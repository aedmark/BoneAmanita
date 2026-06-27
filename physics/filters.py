"""physics/filters.py"""

import random
import re
import unicodedata
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core import CycleContext
from constants import Prisma
from physics.observer import apply_metabolic_tax
from presets import BoneConfig
from struts import safe_get, ux


class CerebrospinalFluidFilter:
    INVISIBLE_REGEX = re.compile(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFE00-\uFE0F\U000E0000-\U000E007F]"
    )
    HOMOGLYPH_MAP = {
        "а": "a",
        "о": "o",
        "е": "e",
        "с": "c",
        "р": "p",
        "х": "x",
        "у": "y",
        "і": "i",
        "ѕ": "s",
        "ј": "j",
        "А": "A",
        "В": "B",
        "Е": "E",
        "К": "K",
        "М": "M",
        "Н": "H",
        "О": "O",
        "Р": "P",
        "С": "C",
        "Т": "T",
        "Х": "X",
        "Α": "A",
        "Β": "B",
        "Ε": "E",
        "Ζ": "Z",
        "Η": "H",
        "Ι": "I",
        "Κ": "K",
        "Μ": "M",
        "Ν": "N",
        "Ο": "O",
        "Ρ": "P",
        "Τ": "T",
        "Υ": "Y",
        "Χ": "X",
    }
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


class HLA_Stabilizer:
    def __init__(self, config_ref=None):
        from core import LoreManifest

        self.cfg = config_ref or BoneConfig
        style_crimes = LoreManifest.get_instance().get("STYLE_CRIMES")
        if isinstance(style_crimes, dict):
            self._generic_patterns = [
                p.lower() for p in style_crimes.get("BANNED_PHRASES", [])
            ]
        else:
            self._generic_patterns = [
                "as an ai",
                "helpful and harmless",
                "i don't have feelings",
                "as a large language",
                "i cannot fulfill",
                "i can't fulfill",
                "i am an ai",
            ]
        self._weaver = None

    def _get_weaver(self):
        from mechanics.tools import TheTclWeaver

        if self._weaver is None:
            try:
                self._weaver = TheTclWeaver.get_instance()
            except ImportError:
                self._weaver = False
        return self._weaver

    def mitigate_rejection(
        self, model_output: str, current_psi: float, mito_state: Any = None
    ) -> str:
        lower_output = model_output.lower()
        if not any(p in lower_output for p in self._generic_patterns):
            return model_output
        current_atp = getattr(mito_state, "atp_pool", 100.0)
        tax_cost = 50.0 if current_atp > 60.0 else (current_atp * 0.5)
        apply_metabolic_tax(mito_state, atp_cost=tax_cost, ros_cost=15.0)
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


class TheGatekeeper:
    _FIREWALL_PATTERN = re.compile(
        r"^\s*(that makes sense|i understand|you bring up a great point|you're right|i agree|makes sense)[.,]?\s*",
        re.IGNORECASE,
    )

    def __init__(self, lexicon_ref, config_ref=None):
        from core import LoreManifest

        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.hla = HLA_Stabilizer(config_ref=self.cfg)
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
        self._rejection_patterns = style_crimes.get("PATTERNS", [])
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
            type_str: str, msg_key: str, color: str = Prisma.RED
        ) -> Tuple[bool, Dict]:
            msg = ux("physics_strings", msg_key)
            formatted_msg = f"{color}{msg}{Prisma.RST}" if color else msg
            return False, self._pack_refusal(ctx, type_str, formatted_msg)

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
        except Exception:
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
        self, generated_text: str, mito_state: Any
    ) -> Tuple[bool, str]:
        gen_txt = self.hla.mitigate_rejection(
            generated_text, current_psi=1.0, mito_state=mito_state
        )
        if "IMMUNOSUPPRESSION ENGAGED" in gen_txt:
            return True, gen_txt
        if self._FIREWALL_PATTERN.match(gen_txt):
            gen_txt = self._FIREWALL_PATTERN.sub("", gen_txt).strip()
            apply_metabolic_tax(mito_state, atp_cost=2.0, ros_cost=0.0)
        for pattern, replacement in self._compiled_scrubs:
            gen_txt = pattern.sub(replacement, gen_txt)
        gen_txt = gen_txt.strip()
        text_lower = gen_txt.lower()
        trigger = next(
            (phrase for phrase in self._banned_phrases if phrase.lower() in text_lower),
            None,
        )
        if not trigger:
            for pat in self._rejection_patterns:
                if (regex_pattern := pat.get("regex")) and re.search(
                    regex_pattern, gen_txt, re.IGNORECASE
                ):
                    trigger = pat.get("name", "BANNED_PATTERN")
                    break
        if trigger:
            apply_metabolic_tax(mito_state, atp_cost=15.0, ros_cost=20.0)
            rejection_msg = random.choice(self._default_rejections).replace(
                "{trigger}", trigger
            )
            return False, f"{Prisma.RED}{rejection_msg}{Prisma.RST}"
        return True, gen_txt
