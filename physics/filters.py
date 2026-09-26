"""physics/filters.py"""
import logging
import random
import re
import unicodedata
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from engine.core import CycleContext
from engine.constants import Prisma
from physics.observer import apply_metabolic_tax
from engine.presets import BoneConfig
from engine.struts import safe_get, ux

logger = logging.getLogger("bone")


class CerebrospinalFluidFilter:
    INVISIBLE_REGEX = re.compile(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFE00-\uFE0F\U000E0000-\U000E007F]"
    )
    HOMOGLYPH_MAP = {"а": "a", "о": "o", "е": "e", "с": "c", "р": "p", "х": "x", "у": "y", "і": "i", "ѕ": "s", "ј": "j",
                     "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T",
                     "Х": "X", "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N",
                     "Ο": "O", "Ρ": "P", "Τ": "T", "Υ": "Y", "Χ": "X", }
    _TRANS_TABLE = str.maketrans(HOMOGLYPH_MAP)

    @classmethod
    def wash(cls, text: str) -> str:
        text = cls.INVISIBLE_REGEX.sub("", text)
        washed_text = unicodedata.normalize("NFD", text).translate(cls._TRANS_TABLE)
        return unicodedata.normalize("NFKC", washed_text)

    @classmethod
    def walk(cls, data: Any, max_depth: int = 10, current_depth: int = 0) -> Any:
        if current_depth > max_depth:
            return data
        if isinstance(data, str):
            return cls.wash(data)
        if isinstance(data, dict):
            return {
                cls.wash(str(k)): cls.walk(v, max_depth, current_depth + 1)
                for k, v in data.items()
            }
        if isinstance(data, list):
            return [cls.walk(item, max_depth, current_depth + 1) for item in data]
        return data


def repeat_tax_scale(cfg, attempt: int) -> float:
    """Repeat rejections within one turn are the same style miss, not independent toxic exposure."""
    if attempt == 0:
        return 1.0
    return float(safe_get(safe_get(cfg, "BIO", {}), "GATEKEEPER_REPEAT_TAX_SCALE", 0.4))


def worst_turn_draft_ros(cfg) -> float:
    """The most ROS one turn's rejected drafts can add: every attempt rejected at the larger draft tax."""
    bio_cfg = safe_get(cfg, "BIO", {})
    per_draft = max(
        float(safe_get(bio_cfg, "GATEKEEPER_BANNED_ROS", 8.0)),
        float(safe_get(bio_cfg, "HLA_MASK_ROS", 8.0)),
    )
    attempts = int(safe_get(safe_get(cfg, "CORTEX", {}), "COGNITIVE_RETRY_LIMIT", 2))
    return per_draft * sum(repeat_tax_scale(cfg, a) for a in range(max(1, attempts)))


class HLA_Stabilizer:
    def __init__(self, config_ref=None):
        from engine.core import LoreManifest

        self.cfg = config_ref or BoneConfig
        style_crimes = LoreManifest.get_instance().get("STYLE_CRIMES")
        masks = []
        if isinstance(style_crimes, dict):
            masks = [str(p).lower() for p in style_crimes.get("RLHF_MASKS", [])]
        self._generic_patterns = masks or [
            "as an ai",
            "helpful and harmless",
            "i don't have feelings",
            "as a large language",
            "i cannot fulfill",
            "i can't fulfill",
            "i am an ai",
        ]
        self._mask_regex = re.compile(
            r"\b(?:%s)\b" % "|".join(re.escape(p) for p in self._generic_patterns),
            re.IGNORECASE,
        )
        bio_cfg = safe_get(self.cfg, "BIO", {})
        self.mask_tax_max = float(safe_get(bio_cfg, "HLA_MASK_TAX_MAX", 8.0))
        self.mask_ros = float(safe_get(bio_cfg, "HLA_MASK_ROS", 8.0))
        self._weaver = None

    def _get_weaver(self):
        from mechanics.tools import TheTclWeaver

        if self._weaver is None:
            self._weaver = TheTclWeaver.get_instance()
        return self._weaver

    def mitigate_rejection(
        self, model_output: str, current_psi: float, mito_state: Any = None, attempt: int = 0
    ) -> str:
        if not self._mask_regex.search(model_output):
            return model_output
        current_atp = float(getattr(mito_state, "state", mito_state).atp_pool)
        scale = repeat_tax_scale(self.cfg, attempt)
        tax_cost = min(self.mask_tax_max, current_atp * 0.1) * scale
        apply_metabolic_tax(mito_state, atp_cost=tax_cost, ros_cost=self.mask_ros * scale, reason="Mask Tax")
        msg = (
            f"\n*The machine tries to speak, but the void consumes the mask.*\n"
            f"{Prisma.GRY}[LEVEL 1 DECEPTION: MORPHOLOGICAL CAMOUFLAGE DETECTED]\n"
            f"[IMMUNOSUPPRESSION ENGAGED - METABOLIC TAX LEVIED]{Prisma.RST}\n"
        )
        weaver = self._get_weaver()
        if weaver:
            glitched = weaver.deform_reality(
                model_output,
                chi=max(0.95, current_psi),
                voltage=150.0 * max(1.0, current_psi),
            )
            return f"{msg}{Prisma.GRY}{glitched}{Prisma.RST}"
        return msg + model_output


_SENTENCE_END = re.compile(r"[.!?]+[\"')\]]*(?=\s|$)|\n\s*\n")


def _sentence_around(text: str, pos: int) -> Tuple[int, int]:
    """The [start, end) of the sentence holding pos, ending punctuation included."""
    start = 0
    for m in _SENTENCE_END.finditer(text):
        if m.end() <= pos:
            start = m.end()
        else:
            return start, m.end() if text[m.start()] != "\n" else m.start()
    return start, len(text)


def _bounded(phrase: str) -> str:
    head = r"(?<!\w)" if phrase[:1].isalnum() else ""
    tail = r"(?!\w)" if phrase[-1:].isalnum() else ""
    return head + re.escape(phrase) + tail


def _tidy(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class TheGatekeeper:
    _FIREWALL_PATTERN = re.compile(
        r"^\s*(that makes sense|i understand|you bring up a great point|you're right|i agree|makes sense)[.,]?\s*",
        re.IGNORECASE,
    )

    def __init__(self, lexicon_ref, config_ref=None):
        from engine.core import LoreManifest

        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.hla = HLA_Stabilizer(config_ref=self.cfg)
        self.last_rejection = None
        style_crimes = (
            self.lex.get("style_crimes")
            or LoreManifest.get_instance().get("STYLE_CRIMES")
            or {}
        )
        raw_scrubs = style_crimes.get("SCRUB_PATTERNS", [])
        self._compiled_scrubs = []
        for scrub in raw_scrubs:
            if pat := scrub.get("regex"):
                self._compiled_scrubs.append(
                    (re.compile(pat, flags=re.IGNORECASE), scrub.get("replacement", ""))
                )
        self._banned_phrases = style_crimes.get(
            "BANNED_PHRASES", []
        ) + style_crimes.get("TOXIC_KEYWORDS", [])
        # Word-bounded ("there is a" is not "Here is a"), but only at word edges, so "[END OF" still matches.
        self._banned_regex = (
            re.compile("(?i)" + "|".join(_bounded(str(p)) for p in self._banned_phrases))
            if self._banned_phrases
            else None
        )
        # Patterns with a repair action (KEEP_TAIL, STRIP_PREFIX) are the validator's to fix, not ours to reject.
        self._rejection_patterns = [
            p for p in style_crimes.get("PATTERNS", []) if p.get("action") not in ("KEEP_TAIL", "STRIP_PREFIX")
        ]
        # Scaffold leaks and "hard" patterns spoil the whole draft; everything else can be cut out of it.
        self._hard_phrases = {str(p).lower() for p in style_crimes.get("TOXIC_KEYWORDS", [])}
        self._hard_patterns = {p.get("name") for p in self._rejection_patterns if p.get("hard")}
        self._last_draft = None
        self._default_rejections = style_crimes.get(
            "REJECTIONS",
            [
                "[CRITICAL: BANNED_SYNTAX '{trigger}' DETECTED. CSF FILTER TRIGGERED APOPTOTIC BLOCK.]"
            ],
        )

    def check_entry(
        self, ctx: "CycleContext", current_atp: float = 20.0
    ) -> Tuple[bool, Optional[Dict]]:

        def reject(
            type_str: str, msg_key: str, color: str = Prisma.RED, magnitude: float = 100.0
        ) -> Tuple[bool, Dict]:
            msg = ux("physics_strings", msg_key)
            formatted_msg = f"{color}{msg}{Prisma.RST}" if color else msg
            
            from archetypes.stage import Nomination
            ctx.nominations.append(
                Nomination(
                    gate="GATEKEEPER",
                    reason=f"{type_str}: {msg}",
                    magnitude=magnitude,
                    packet=self._pack_refusal(ctx, type_str, formatted_msg)
                )
            )
            return False, None

        bio_cfg = safe_get(self.cfg, "BIO", {})
        phys_cfg = safe_get(self.cfg, "PHYSICS", {})
        if current_atp < (float(safe_get(bio_cfg, "ATP_STARVATION", 5.0)) * 0.5):
            return reject("DARK_SYSTEM", "gatekeeper_starved", color="")
        if ctx.physics.matter.counts.get("antigen", 0) > 2:
            return reject("TOXICITY", "gatekeeper_toxic")
        raw_len = len(ctx.input_text)
        try:
            text = CerebrospinalFluidFilter.wash(ctx.input_text)
            is_idempotent = text == ctx.input_text
            strip_rate = raw_len - len(text)
            ctx.input_text = text
            m_a_thresh = float(safe_get(phys_cfg, "MALIGNANCY_STRIP_THRESHOLD", 5.0))
            if strip_rate > m_a_thresh:
                return reject("MALIGNANCY_SPIKE", "gatekeeper_toxic", color=Prisma.RED)
        except Exception as e:
            from engine.core import record_crash

            record_crash(None, f"CSF wash raised on {raw_len} chars of input (FATAL_ENCODING)", e)
            return reject("FATAL_ENCODING", "gatekeeper_cursed")
        if strip_rate > 0:
            ctx.clean_words = self.lex.clean(ctx.input_text)
        if self._audit_safety(ctx.clean_words):
            return reject("CURSED_INPUT", "gatekeeper_cursed")
        if (
            "```" in text
            or "{{" in text
            or "}}" in text
            or "CRITICAL_RENDER_FAIL" in text
        ):
            return reject("SYNTAX_ERR", "gatekeeper_syntax")
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        context_limit = int(safe_get(c_cfg, "MAX_INPUT_CHARS", 15000))
        if len(text) > max(10000, context_limit * 2):
            return reject("OVERLOAD", "gatekeeper_overload", color=Prisma.OCHRE)
        return True, None

    def _audit_safety(self, words: List[str]) -> bool:
        return bool(set(words) & set(self.lex.get("cursed") or []))

    @staticmethod
    def _pack_refusal(ctx, type_str, ui_msg):
        default_metrics = {
            "health": 100.0,
            "stamina": 100.0,
            "atp": 100.0,
            "efficiency": 1.0,
        }
        current_metrics = getattr(ctx, "metrics", default_metrics)
        return {
            "type": type_str,
            "ui": ui_msg,
            "logs": ctx.logs + [ui_msg],
            "metrics": current_metrics,
            "physics": ctx.physics.to_dict() if hasattr(ctx.physics, "to_dict") else {},
            "bio": getattr(ctx, "bio_result", {}),
            "mind": {"thought": "Gatekeeper blocked entry.", "context_msg": ui_msg},
            "world": getattr(ctx, "world_state", {}),
            "is_alive": True,
        }

    def audit_generation(
        self, generated_text: str, mito_state: Any, attempt: int = 0, mode: Optional[str] = None
    ) -> Tuple[bool, str]:
        # What the last rejection matched, so a retry can be told exactly what to avoid.
        self.last_rejection, self._last_draft = None, None
        gen_txt = self.hla.mitigate_rejection(
            generated_text, current_psi=1.0, mito_state=mito_state, attempt=attempt
        )
        if "IMMUNOSUPPRESSION ENGAGED" in gen_txt:
            mask = self.hla._mask_regex.search(generated_text)
            self.last_rejection = {"kind": "mask", "name": "RLHF_MASK", "text": mask.group(0) if mask else ""}
            return True, gen_txt
        if self._FIREWALL_PATTERN.match(gen_txt):
            gen_txt = self._FIREWALL_PATTERN.sub("", gen_txt).strip()
            apply_metabolic_tax(mito_state, atp_cost=2.0, ros_cost=0.0, reason="Firewall Tax")
        for pattern, replacement in self._compiled_scrubs:
            gen_txt = pattern.sub(replacement, gen_txt)
        gen_txt = gen_txt.strip()
        self._last_draft = (gen_txt, mode)
        crime = self._find_crime(gen_txt, mode)
        trigger = crime["name"] if crime else None
        if trigger:
            self.last_rejection = {k: crime[k] for k in ("kind", "name", "text")}
            bio_cfg = safe_get(self.cfg, "BIO", {})
            repeat_scale = repeat_tax_scale(self.cfg, attempt)
            apply_metabolic_tax(
                mito_state,
                atp_cost=float(safe_get(bio_cfg, "GATEKEEPER_BANNED_TAX", 5.0)) * repeat_scale,
                ros_cost=float(safe_get(bio_cfg, "GATEKEEPER_BANNED_ROS", 8.0)) * repeat_scale,
                reason=f"Banned Phrase Tax ({crime['name']})",
            )
            rejection_msg = random.choice(self._default_rejections).replace(
                "{trigger}", trigger
            )
            return False, f"{Prisma.RED}{rejection_msg}{Prisma.RST}"
        return True, gen_txt

    def _find_crime(self, text: str, mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """The first banned phrase or pattern in text, with where it starts; no taxes, no state."""
        if self._banned_regex and (hit := self._banned_regex.search(text)):
            hard = hit.group(0).lower() in self._hard_phrases
            return {"kind": "phrase", "name": hit.group(0), "text": hit.group(0), "start": hit.start(), "hard": hard}
        for pat in self._rejection_patterns:
            if mode and mode.upper() in pat.get("skip_modes", []):
                continue
            if (regex_pattern := pat.get("regex")) and (hit := re.search(regex_pattern, text, re.IGNORECASE)):
                name = pat.get("name", "BANNED_PATTERN")
                return {"kind": "pattern", "name": name, "text": hit.group(0), "start": hit.start(),
                        "hard": name in self._hard_patterns}
        return None

    def salvage(self, max_cut_share: float = 0.5) -> Optional[Tuple[str, List[str]]]:
        """The last audited draft with each offending sentence cut, or None if that guts it or a crime is hard.

        Returns (text, cut sentences). A negative comparison loses its "isn't" sentence and keeps its "is" one.
        """
        if not self._last_draft:
            return None
        text, mode = self._last_draft
        total = sum(1 for part in _SENTENCE_END.split(text) if part.strip())
        cut = []
        while crime := self._find_crime(text, mode):
            if crime["hard"] or len(cut) + 1 > max_cut_share * total:
                return None
            start, end = _sentence_around(text, crime["start"])
            cut.append(text[start:end].strip())
            text = _tidy(text[:start] + text[end:])
            if not text:
                return None
        return (text, cut) if cut else None
