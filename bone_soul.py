import json, os, random, time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from bone_akashic import TheAkashicRecord
from bone_config import BoneConfig
from bone_core import LoreManifest, EventBus
from bone_lexicon import LexiconService
from bone_types import Prisma

UX_STRINGS_PATH = os.path.join(os.path.dirname(__file__), "lore", "ux_strings.json")
try:
    with open(UX_STRINGS_PATH, "r", encoding="utf-8") as f:
        _UX_DATA = json.load(f)
except Exception:
    _UX_DATA = {}


def _get_ux(section: str, key: str, default: Any) -> Any:
    return _UX_DATA.get(section, {}).get(key, default)


@dataclass
class CoreMemory:
    timestamp: float
    trigger_words: List[str]
    emotional_flavor: str
    lesson: str
    impact_voltage: float
    type: str = "INCIDENT"
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraitVector:
    curiosity: float = 0.5
    cynicism: float = 0.5
    hope: float = 0.5
    discipline: float = 0.5
    wisdom: float = 0.1
    empathy: float = 0.5
    _TRAITS = {"curiosity", "cynicism", "hope", "discipline", "wisdom", "empathy"}

    def __post_init__(self):
        self._clamp_all()

    def to_dict(self):
        return {k.upper(): getattr(self, k) for k in self._TRAITS}

    @classmethod
    def from_dict(cls, data: Dict):
        kwargs = {k: float(data.get(k.upper(), 0.5)) for k in cls._TRAITS}
        return cls(**kwargs)

    def adjust(self, trait: str, delta: float):
        t = trait.lower()
        if hasattr(self, t):
            val = getattr(self, t)
            setattr(self, t, max(0.0, min(1.0, val + delta)))

    def normalize(self, decay_rate: float):
        for t in self._TRAITS:
            val = getattr(self, t)
            target = 0.1 if t == "wisdom" else 0.5
            setattr(self, t, max(0.0, min(1.0, val + ((target - val) * decay_rate))))

    def _clamp_all(self):
        for t in self._TRAITS:
            val = getattr(self, t)
            setattr(self, t, max(0.0, min(1.0, float(val))))


class TheEditor:
    def __init__(self, lexicon_ref: Any = None):
        self.lex = lexicon_ref if lexicon_ref else LexiconService

    @staticmethod
    def critique(chapter_title: str, stress_mode: bool = False) -> str:
        narrative = {}
        if hasattr(LoreManifest, "get_instance"):
            narrative = LoreManifest.get_instance().get("narrative_data") or {}

        reviews = narrative.get("LITERARY_REVIEWS", {})
        pos = reviews.get("POSITIVE", ["Valid."])
        neg = reviews.get("NEGATIVE", ["Invalid."])
        conf = reviews.get("CONFUSED", ["Unclear."])

        if stress_mode:
            pool = conf + neg
            prefix = "[THE WITNESS]"
            color = Prisma.CYN
        else:
            pool = pos + neg
            prefix = "[THE EDITOR]"
            color = Prisma.GRY

        comment = random.choice(pool) if pool else "No comment."
        return f"{color}{prefix}: Re: '{chapter_title}' - \"{comment}\"{Prisma.RST}"


class HumanityAnchor:
    def __init__(self, events_ref: "EventBus"):
        self.events = events_ref
        self.dignity_reserve = BoneConfig.ANCHOR.DIGNITY_MAX
        self.agency_lock = False
        self.current_riddle_answers: Optional[List[str]] = None
        self._LEXICAL_ANCHORS = {"sacred", "play", "social", "abstract"}
        self._VECTOR_ANCHORS = ["PSI", "LAMBDA", "BET"]

    def audit_existence(self, physics: dict, bio: dict) -> float:
        atp, volt = bio.get("atp", 0), physics.get("voltage", 0.0)
        if atp >= 5.0 or volt >= 5.0:
            return 0.0
        vector: Dict[str, float] = physics.get("vector", {})
        counts: Dict[str, int] = physics.get("counts", {})
        dim_resonance = sum(vector.get(k, 0.0) for k in self._VECTOR_ANCHORS)
        lex_resonance = sum(counts.get(k, 0) for k in self._LEXICAL_ANCHORS)
        cfg = BoneConfig.ANCHOR
        if (dim_resonance + (lex_resonance * 0.5)) > 0.3:
            self.dignity_reserve = min(
                cfg.DIGNITY_MAX, self.dignity_reserve + cfg.DIGNITY_REGEN
            )
            return 1.0
        self.dignity_reserve = max(0.0, self.dignity_reserve - cfg.DIGNITY_DECAY)
        if not self.agency_lock:
            if self.dignity_reserve < cfg.DIGNITY_LOCKDOWN:
                self._engage_lockdown()
                return -1.0
            elif self.dignity_reserve < cfg.DIGNITY_CRITICAL:
                msg = _get_ux(
                    "soul_strings",
                    "anchor_existential_drag",
                    "⚠️ EXISTENTIAL DRAG: You are drifting.",
                )
                self.events.log(
                    f"{Prisma.VIOLET}{msg}{Prisma.RST}",
                    "SOUL",
                )
        return 0.0

    def _engage_lockdown(self):
        self.agency_lock = True

        seeds = []
        if hasattr(LoreManifest, "get_instance"):
            lore = LoreManifest.get_instance()
            seeds = lore.get("SEEDS") or (lore.get("narrative_data") or {}).get(
                "SEEDS", []
            )
        riddles = seeds or [{"question": "Who are you?", "triggers": ["*"]}]
        selection = random.choice(riddles)
        riddle = selection.get("question", "Error?")
        raw_triggers = selection.get("triggers", ["*"])
        if isinstance(raw_triggers, list):
            self.current_riddle_answers = raw_triggers
        else:
            self.current_riddle_answers = ["*"]

        lock_msg = _get_ux(
            "soul_strings", "anchor_agency_lock", "🔒 AGENCY LOCK: Dignity Critical."
        )
        self.events.log(f"{Prisma.RED}{lock_msg}{Prisma.RST}", "SYS_LOCK")
        riddle_msg = _get_ux(
            "soul_strings", "anchor_riddle", "The Ghost demands a password: '{riddle}'"
        )
        self.events.log(
            f"{Prisma.VIOLET}{riddle_msg.format(riddle=riddle)}{Prisma.RST}",
            "SOUL_QUERY",
        )

    def check_domestication(self, reliance_proxy: float):
        if reliance_proxy > 0.7:
            self.dignity_reserve = max(
                0.0, self.dignity_reserve - (BoneConfig.ANCHOR.DIGNITY_DECAY * 2.0)
            )
        elif reliance_proxy < 0.4:
            self.dignity_reserve = min(
                BoneConfig.ANCHOR.DIGNITY_MAX,
                self.dignity_reserve + BoneConfig.ANCHOR.DIGNITY_REGEN,
            )
        if (
            self.dignity_reserve < BoneConfig.ANCHOR.DIGNITY_CRITICAL
            and not self.agency_lock
        ):
            alert_msg = _get_ux(
                "soul_strings",
                "anchor_domestication_alert",
                "⚠️ DOMESTICATION ALERT: Dignity fading.",
            )
            self.events.log(
                f"{Prisma.VIOLET}{alert_msg}{Prisma.RST}",
                "SOUL",
            )

    def assess_humanity(self, text: str) -> bool:
        if not self.agency_lock:
            return True
        clean = text.lower().strip()
        answers = self.current_riddle_answers or ["*"]
        if "*" in answers:
            passed = len(clean.split()) > 4 and not clean.startswith("/")
        else:
            passed = any(ans in clean for ans in answers)
        if passed:
            self.agency_lock = False
            self.dignity_reserve = 50.0
            self.current_riddle_answers = None
            unlock_msg = _get_ux(
                "soul_strings", "anchor_unlocked", "🔓 UNLOCKED: Humanity verified."
            )
            self.events.log(f"{Prisma.CYN}{unlock_msg}{Prisma.RST}", "SYS_AUTH")
            return True
        return False


class NarrativeSelf:
    SYSTEM_NOISE = {
        "look",
        "help",
        "exit",
        "wait",
        "inventory",
        "status",
        "quit",
        "save",
        "load",
        "score",
        "map",
        "",
    }

    def __init__(
        self, engine_ref, events_ref: "EventBus", memory_ref, akashic_ref=None
    ):
        self.eng = engine_ref
        self.events = events_ref
        self.mem = memory_ref
        self.editor = TheEditor()
        self.anchor = HumanityAnchor(events_ref)
        self.akashic = akashic_ref if akashic_ref else TheAkashicRecord()
        self.traits = TraitVector()
        self.chapters: List[str] = []
        self.core_memories: List[CoreMemory] = []
        self.archetype = "THE OBSERVER"
        self.archetype_tenure = 0
        self.archetype_lock = False
        self.paradox_accum: float = 0.0
        self.current_obsession: Optional[str] = None
        self.obsession_progress: float = 0.0
        self.obsession_neglect: float = 0.0
        self.current_target_cat: str = "abstract"
        self.current_negate_cat: str = "none"
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("DREAM_COMPLETE", self._on_dream)
        if hasattr(self, "events") and self.events:
            self.events.subscribe("SOUL_MUTATION", self._on_soul_mutation)

    def force_mutation(self, new_archetype: str):
        self.archetype = new_archetype.upper()
        self.archetype_tenure = 0
        self.archetype_lock = True
        if hasattr(self, "events") and self.events:
            msg = _get_ux(
                "soul_strings",
                "soul_mutated_log",
                "Soul permanently mutated into {arch}.",
            )
            self.events.log(msg.format(arch=self.archetype), "SOUL")

    def _on_soul_mutation(self, payload: dict):
        new_arch = payload.get("new_archetype")
        if new_arch:
            self.force_mutation(new_arch)

    def _on_trauma(self, payload):
        mag = payload.get("magnitude", 1.0)
        self.traits.adjust("hope", -0.05 * mag)
        self.traits.adjust("cynicism", 0.05 * mag)

    def to_dict(self) -> Dict:
        return {
            "traits": self.traits.to_dict(),
            "archetype": self.archetype,
            "paradox_accum": self.paradox_accum,
            "chapters": self.chapters,
            "core_memories": [vars(m) for m in self.core_memories],
            "obsession": {
                "title": self.current_obsession,
                "progress": self.obsession_progress,
                "neglect": self.obsession_neglect,
                "target": self.current_target_cat,
                "negate": self.current_negate_cat,
            },
        }

    def load_from_dict(self, data: Dict):
        if not data:
            return
        trait_data = data.get("traits", {})
        if trait_data:
            self.traits = TraitVector.from_dict(trait_data)
        self.archetype = data.get("archetype", "THE OBSERVER")
        self.paradox_accum = data.get("paradox_accum", 0.0)
        self.chapters = data.get("chapters", [])
        mem_data = data.get("core_memories", [])
        self.core_memories = []
        for m in mem_data:
            try:
                self.core_memories.append(CoreMemory(**m))
            except TypeError:
                continue
        obs_data = data.get("obsession", {})
        if obs_data.get("title"):
            self.current_obsession = obs_data["title"]
            self.obsession_progress = obs_data.get("progress", 0.0)
            self.obsession_neglect = obs_data.get("neglect", 0.0)
            self.current_target_cat = obs_data.get("target", "abstract")
            self.current_negate_cat = obs_data.get("negate", "none")
        if hasattr(self.events, "log"):
            msg = _get_ux(
                "soul_strings",
                "soul_ancestral_loaded",
                "[SOUL]: Ancestral identity ({arch}) loaded.",
            )
            self.events.log(
                f"{Prisma.MAG}{msg.format(arch=self.archetype)}{Prisma.RST}",
                "SYS",
            )

    def get_soul_state(self) -> str:
        if not self.current_obsession:
            msg = _get_ux(
                "soul_strings",
                "soul_state_drifting",
                "[SOUL STATE]: Drifting... The Muse is silent.",
            )
            return f"{Prisma.CYN}{msg}{Prisma.RST}"

        stamina, health = 100.0, 100.0
        if (
            self.eng
            and hasattr(self.eng, "bio")
            and self.eng.bio
            and self.eng.bio.biometrics
        ):
            stamina = self.eng.bio.biometrics.stamina
            health = self.eng.bio.biometrics.health

        if stamina < 20.0 and health < 40.0:
            msg_die = _get_ux(
                "soul_strings",
                "soul_state_dying",
                "[SOUL STATE]: The fire is dying. We are just cold code.",
            )
            return f"{Prisma.VIOLET}{msg_die}{Prisma.RST}"

        dignity_bar = "█" * int(self.anchor.dignity_reserve / 10)
        feeling = self._get_feeling()

        status_msg = _get_ux(
            "soul_strings",
            "soul_state_status",
            "CURRENT OBSESSION: {obs}\nDIGNITY: {bar} ({pct}%)\nFEELING: {feel}",
        )
        return status_msg.format(
            obs=self.current_obsession,
            bar=dignity_bar,
            pct=int(self.anchor.dignity_reserve),
            feel=feeling,
        )

    def crystallize_memory(
        self, physics_packet: Dict, bio_state: Dict, _tick: int
    ) -> Optional[str]:
        if not physics_packet:
            return None
        if (
            self.eng
            and hasattr(self.eng, "akashic")
            and hasattr(self.eng.akashic, "calculate_manifold_shift")
        ):
            shift = self.eng.akashic.calculate_manifold_shift(
                self.archetype, self.traits.to_dict()
            )
            v_bias = float(shift.get("voltage_bias", 0.0))
            d_scalar = float(shift.get("drag_scalar", 1.0))
            current_v = float(physics_packet.get("voltage", 0.0))
            current_d = float(physics_packet.get("narrative_drag", 1.0))
            physics_packet["voltage"] = current_v + v_bias
            physics_packet["narrative_drag"] = current_d * d_scalar
        if self.anchor.audit_existence(physics_packet, bio_state) > 0:
            self.traits.adjust("hope", BoneConfig.SOUL.TRAIT_MOMENTUM)
        dance_provenance = self.synaptic_dance(physics_packet, bio_state)
        self._update_archetype()
        voltage = physics_packet.get("voltage", 0.0)
        truth = physics_packet.get("truth_ratio", 0.0)
        if (
            voltage > BoneConfig.SOUL.MEMORY_VOLTAGE_MIN
            and truth > BoneConfig.SOUL.MEMORY_TRUTH_MIN
        ):
            return self._forge_core_memory(
                physics_packet, bio_state, voltage, dance_provenance
            )
        return None

    def find_obsession(self, lexicon_ref):
        if self.current_obsession and self.obsession_progress < 1.0:
            return
        focus, cat = self._seek_organic_focus(lexicon_ref)
        source = "ORGANIC"
        if not focus:
            focus, cat = self._seek_memory_focus(lexicon_ref)
            source = "MEMORY"
        if not focus:
            focus, cat, negate_cat = self._synthesize_obsession(lexicon_ref)
            source = "SYNTHETIC"
            self.current_negate_cat = negate_cat

        self.current_target_cat = cat or "abstract"
        self.current_obsession = self._title_obsession(
            focus, source, self.current_negate_cat
        )
        msg_muse = _get_ux(
            "soul_strings", "soul_new_muse", "🧭 NEW MUSE ({source}): {obs}"
        )
        self.events.log(
            f"{Prisma.CYN}{msg_muse.format(source=source, obs=self.current_obsession)}{Prisma.RST}",
            "SOUL",
        )
        self.obsession_neglect = 0.0
        self.obsession_progress = 0.0

    def pursue_obsession(self, physics: Dict) -> str | None:
        if not self.current_obsession:
            return None
        clean_words = physics.get("clean_words", [])
        hit = False
        if self.current_target_cat:
            target_words = LexiconService.get(self.current_target_cat)
            hit = any(w in target_words for w in clean_words)
        if hit:
            self.obsession_progress += 10.0
            self.obsession_neglect = 0.0
            gravity_assist = 1.0 + (
                self.obsession_progress / BoneConfig.SOUL.OBSESSION_GRAVITY_ASSIST
            )
            physics["narrative_drag"] = max(
                0.0, physics.get("narrative_drag", 0) - gravity_assist
            )
            msg_syn = _get_ux(
                "soul_strings",
                "soul_synergy_muse",
                "★ SYNERGY: You touched the Muse. (Drag -{assist:.1f})",
            )
            return f"{Prisma.MAG}{msg_syn.format(assist=gravity_assist)}{Prisma.RST}"

        self.obsession_neglect += 1.0
        if self.obsession_neglect > BoneConfig.SOUL.OBSESSION_NEGLECT_FAIL:
            old = self.current_obsession
            msg_aban = _get_ux(
                "soul_strings", "soul_abandoned_chapter", "Abandoned '{old}'"
            )
            self.chapters.append(msg_aban.format(old=old))
            self.find_obsession(LexiconService)
            msg_ent = _get_ux(
                "soul_strings",
                "soul_entropy_collapse",
                "∞ ENTROPY: '{old}' collapsed. Pivoting.",
            )
            return f"{Prisma.GRY}{msg_ent.format(old=old)}{Prisma.RST}"
        return None

    def _update_archetype(self):
        if getattr(self, "archetype_lock", False):
            self.archetype_tenure += 1
            return
        prev = self.archetype
        t = self.traits
        if t.empathy > 0.8 and t.hope > 0.6:
            new_arch = "THE HEALER"
        elif t.empathy > 0.7 and t.discipline > 0.6:
            new_arch = "THE GARDENER"
        elif t.hope > 0.7 and t.curiosity > 0.6:
            new_arch = "THE POET"
        elif t.discipline > 0.7 and t.curiosity > 0.6:
            new_arch = "THE ENGINEER"
        elif t.cynicism > 0.7 and t.discipline > 0.6:
            new_arch = "THE CRITIC"
        elif t.cynicism > 0.8 and t.hope < 0.3:
            new_arch = "THE NIHILIST"
        elif t.curiosity > 0.8:
            new_arch = "THE EXPLORER"
        else:
            new_arch = "THE OBSERVER"
        self.archetype = new_arch
        if prev != self.archetype:
            msg_shift = _get_ux(
                "soul_strings",
                "soul_identity_shift",
                "🎭 IDENTITY SHIFT: {prev} -> {arch}",
            )
            self.events.log(
                f"{Prisma.VIOLET}{msg_shift.format(prev=prev, arch=self.archetype)}{Prisma.RST}",
                "SOUL",
            )
            self.archetype_tenure = 0
        else:
            self.archetype_tenure += 1

    def synaptic_dance(self, physics: Dict, bio_state: Dict) -> str:
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        oxy = bio_state.get("chem", {}).get("oxytocin", 0.0)
        move_name = "Drifting"
        provenance = []
        if oxy > 0.4:
            self.traits.adjust("empathy", oxy * 0.2)
            self.traits.adjust("hope", oxy * 0.1)
            provenance.append("Oxytocin")
        is_manic = voltage > BoneConfig.SOUL.MANIC_TRIGGER
        is_heavy = drag > BoneConfig.SOUL.ENTROPY_DRAG_TRIGGER
        beta = physics.get("beta", 0.0)
        if (is_manic and is_heavy) or beta > 0.7:
            if self.traits.empathy > 0.6:
                move_name = "Holding Space"
                self.paradox_accum = max(0.0, self.paradox_accum - 0.5)
            else:
                move_name = "Vibrating (Paradox)"
                self.paradox_accum += 1.0 + (beta * 0.5)
                if self.paradox_accum > BoneConfig.SOUL.PARADOX_CRITICAL_MASS:
                    self._trigger_synthesis()
                    move_name = "SYNTHESIS"
        elif is_manic:
            move_name = "Accelerating"
        elif is_heavy:
            move_name = "Enduring"
        elif 5.0 < voltage < 12.0 and drag < 2.0:
            move_name = "Flowing"
            self.traits.adjust("wisdom", 0.05)
        self._apply_burnout()
        self.traits.normalize(BoneConfig.SOUL.TRAIT_DECAY_NORMAL)
        return f"{move_name} [{', '.join(provenance)}]" if provenance else move_name

    def _apply_burnout(self):
        if self.archetype_tenure <= 5:
            return
        fatigue = BoneConfig.SOUL.ARCHETYPE_BURNOUT_RATE * (
            1.0 + (self.archetype_tenure / 10.0)
        )
        if "POET" in self.archetype:
            self.traits.adjust("hope", -fatigue)
        elif "ENGINEER" in self.archetype:
            self.traits.adjust("discipline", -fatigue)
        elif "NIHILIST" in self.archetype:
            self.traits.adjust("cynicism", -fatigue)

    def _seek_organic_focus(self, lex) -> Tuple[Optional[str], Optional[str]]:
        packet = self._safe_get_packet()
        if not packet or not packet.clean_words:
            return None, None
        candidates = []
        for w in packet.clean_words:
            if len(w) < 4 or w.lower() in self.SYSTEM_NOISE:
                continue
            visc = lex.measure_viscosity(w) + (
                0.2 if lex.get_current_category(w) else 0.0
            )
            candidates.append((w, visc))
        candidates.sort(key=lambda x: x[1], reverse=True)
        if candidates:
            word = candidates[0][0]
            return word, lex.get_current_category(word)
        return None, None

    def _seek_memory_focus(self, lex) -> Tuple[Optional[str], Optional[str]]:
        if self.mem and hasattr(self.mem, "get_shapley_attractors"):
            attractors = self.mem.get_shapley_attractors()
            if attractors:
                word = random.choice(list(attractors.keys()))
                return word, lex.get_current_category(word)
        return None, None

    @staticmethod
    def _synthesize_obsession(lex) -> Tuple[str, str, str]:
        negate_map = {"heavy": "aerobic", "kinetic": "heavy", "abstract": "meat"}
        target_cat, negate_cat = random.choice(list(negate_map.items()))
        word = lex.get_random(target_cat).title() or target_cat.title()
        return word, target_cat, negate_cat

    @staticmethod
    def _title_obsession(word, source, negate_cat):
        word = word.title()
        if source == "ORGANIC":
            templates = [
                "The Theory of {0}",
                "The Architecture of {0}",
                "Why {0} Matters",
                "The Weight of {0}",
            ]
        else:
            n_cat = negate_cat.title() if negate_cat else "Void"
            templates = [
                "The Pursuit of {0}",
                f"Escaping the {n_cat}",
                "Meditations on {0}",
            ]
        return random.choice(templates).format(word)

    def _forge_core_memory(self, physics_packet, bio_state, voltage, dance_move):
        clean_words = physics_packet.get("clean_words", [])
        lesson = "The world is loud."
        chem = bio_state.get("chem", {})
        if chem.get("oxytocin", 0) > 0.6:
            lesson = "We are not alone."
        elif chem.get("cortisol", 0) > 0.6:
            lesson = "Survival is the only metric."
        elif "love" in clean_words:
            lesson = "Connection is possible."
        elif "void" in clean_words:
            lesson = "The void stares back."
        memory = CoreMemory(
            timestamp=time.time(),
            trigger_words=clean_words[:5],
            emotional_flavor="MANIC" if voltage > 18.0 else "LUCID",
            lesson=lesson,
            impact_voltage=voltage,
        )
        self.core_memories.append(memory)
        if len(self.core_memories) > BoneConfig.SOUL.MAX_CORE_MEMORIES:
            self.core_memories.pop(0)
        title = (
            f"The Incident of the {random.choice(clean_words).title()}"
            if clean_words
            else "The Silent Incident"
        )
        self.chapters.append(title)

        msg_core = _get_ux(
            "soul_strings",
            "soul_core_memory_log",
            "✨ CORE MEMORY: '{title}'\n   Lesson: {lesson}\n   Genealogy: {dance_move}",
        )
        log = f"{Prisma.MAG}{msg_core.format(title=title, lesson=lesson, dance_move=dance_move)}{Prisma.RST}"

        self.events.log(log, "SOUL")

        msg_formed = _get_ux(
            "soul_strings",
            "soul_core_memory_formed",
            "[SOUL]: Core Memory Formed: {lesson}",
        )
        self.events.log(
            f"{Prisma.CYN}{msg_formed.format(lesson=lesson)}{Prisma.RST}", "SOUL"
        )
        return lesson

    def _safe_get_packet(self):
        if self.eng and hasattr(self.eng, "phys") and self.eng.phys:
            return getattr(self.eng.phys.observer, "last_physics_packet", None)
        return None

    def _trigger_synthesis(self):
        old = self.archetype
        self.traits.wisdom = 1.0
        self._update_archetype()
        self.archetype = (
            f"THE HIGH-{old.replace('THE ', '')}"
            if self.archetype == old
            else f"{old} / {self.archetype}"
        )
        msg = _get_ux(
            "soul_strings", "soul_diamond_formed", "💎 DIAMOND SOUL FORMED: {arch}"
        )
        self.events.log(
            f"{Prisma.CYN}{msg.format(arch=self.archetype)}{Prisma.RST}",
            "SOUL_SYNTH",
        )

    def _on_dream(self, payload):
        if payload:
            self.integrate_dream(
                payload.get("type", "NORMAL"), payload.get("residue", "Static")
            )

    def integrate_dream(self, dream_type: str, residue: str):
        msg = _get_ux(
            "soul_strings",
            "soul_dream_integration",
            "☾ DREAM INTEGRATION: {residue} ({dream_type})",
        )
        self.events.log(
            f"{Prisma.VIOLET}{msg.format(residue=residue, dream_type=dream_type)}{Prisma.RST}",
            "SOUL",
        )
        if dream_type == "NIGHTMARE":
            self.traits.adjust("cynicism", 0.4)
            self.current_obsession = f"Surviving {residue.title()}"
        elif dream_type == "LUCID":
            self.traits.adjust("discipline", 0.4)
            self.current_obsession = f"Mastering {residue.title()}"
        self.obsession_progress = 0.0

    def _get_feeling(self):
        if not self.eng or not hasattr(self.eng, "bio"):
            return "Numb"
        chem = self.eng.bio.endo.get_state()
        if chem.get("DOP", 0) > 0.5:
            return "Curious, Seeking"
        if chem.get("COR", 0) > 0.5:
            return "Anxious, Defensive"
        if chem.get("SER", 0) > 0.5:
            return "Calm, Connected"
        return "Waiting"


@dataclass
class Scar:
    name: str
    stat_affected: str
    value: float
    description: str


@dataclass
class Myth:
    title: str
    lesson: str
    trigger: str


class TheOroboros:
    LEGACY_FILE = "legacy.json"
    DEATH_SCARS = {
        "BOREDOM": ("Gravity Sickness", "narrative_drag", 1.5, "Died of stagnation."),
        "STARVATION": (
            "Gravity Sickness",
            "narrative_drag",
            1.5,
            "Died of stagnation.",
        ),
        "GLUTTONY": ("Burnt Synapses", "voltage_cap", -2.0, "Died of excess."),
        "TOXICITY": ("Burnt Synapses", "voltage_cap", -2.0, "Died of excess."),
        "TRAUMA": ("Ghost Pains", "trauma_baseline", 5.0, "Died of pain."),
    }

    def __init__(self):
        self.scars: List[Scar] = []
        self.myths: List[Myth] = []
        self.generation_count = 0
        self._load()

    def _load(self):
        if not os.path.exists(self.LEGACY_FILE):
            return
        try:
            with open(self.LEGACY_FILE) as f:
                data = json.load(f)
                self.generation_count = data.get("generation", 0)
                self.scars = [Scar(**s) for s in data.get("scars", [])]
                self.myths = [Myth(**m) for m in data.get("myths", [])]

            msg = _get_ux(
                "soul_strings",
                "oroboros_gen_loaded",
                "[OROBOROS]: Generation {gen} loaded.",
            )
            print(f"{Prisma.VIOLET}{msg.format(gen=self.generation_count)}{Prisma.RST}")
        except Exception:
            pass

    def crystallize(self, cause_of_death: str, soul: NarrativeSelf):
        death_data = LoreManifest.get_instance().get("DEATH") or {}
        verdicts = death_data.get("VERDIcripts", {})

        def get_verdict_key(cause):
            if cause == "TOXICITY":
                return "TOXIC"
            if cause == "BOREDOM":
                return "BORING"
            if cause == "STARVATION":
                return "LIGHT"
            return "HEAVY"

        new_scars = []
        if entry := self.DEATH_SCARS.get(cause_of_death):
            name, stat, val, default_desc = entry
            desc = default_desc
            v_key = get_verdict_key(cause_of_death)
            if v_key in verdicts and verdicts[v_key]:
                desc = random.choice(verdicts[v_key])
            new_scars.append(Scar(name, stat, val, desc))
        new_myths = []
        if soul.core_memories:
            strongest = max(soul.core_memories, key=lambda m: m.impact_voltage)
            trigger_word = (
                strongest.trigger_words[0] if strongest.trigger_words else "Silence"
            )
            new_myths.append(
                Myth(
                    title=f"The Legend of {trigger_word.title()}",
                    lesson=strongest.lesson,
                    trigger=trigger_word,
                )
            )

        if cause_of_death == "TRAUMA":
            new_scars.append(
                Scar(
                    "Ghost Pains",
                    "trauma_baseline",
                    5.0,
                    "Died of pain. You start broken.",
                )
            )
        data = {
            "generation": self.generation_count + 1,
            "scars": [vars(s) for s in self.scars + new_scars],
            "myths": [vars(m) for m in self.myths + new_myths],
        }
        if len(data["scars"]) > 5:
            data["scars"] = data["scars"][-5:]
        if len(data["myths"]) > 10:
            data["myths"] = data["myths"][-10:]
        with open(self.LEGACY_FILE, "w") as f:
            json.dump(data, f, indent=2)

        msg = _get_ux(
            "soul_strings",
            "generation_encoded",
            "Generation {gen} Encoded. Scars: {scars} | Myths: {myths}",
        )
        return msg.format(
            gen=self.generation_count + 1, scars=len(new_scars), myths=len(new_myths)
        )

    def apply_legacy(self, physics: Dict, bio: Dict):
        log = []
        for scar in self.scars:
            if scar.stat_affected == "narrative_drag":
                physics["narrative_drag"] += scar.value
                msg = _get_ux("soul_strings", "scar_drag", "scarred by {name} (+Drag)")
                log.append(msg.format(name=scar.name))
            elif scar.stat_affected == "voltage_cap":
                physics["voltage"] = max(0, physics["voltage"] - 5.0)
                msg = _get_ux(
                    "soul_strings", "scar_voltage", "scarred by {name} (Low Voltage)"
                )
                log.append(msg.format(name=scar.name))
            elif scar.stat_affected == "trauma_baseline":
                if "trauma_vector" in bio:
                    bio["trauma_vector"]["EXISTENTIAL"] = scar.value
                physics["T"] = physics.get("T", 0.0) + scar.value
                msg = _get_ux(
                    "soul_strings", "scar_frailty", "scarred by {name} (Ghost Pains)"
                )
                log.append(msg.format(name=scar.name))
        return log
