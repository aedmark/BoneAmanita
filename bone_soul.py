""" bone_soul.py """

import json
import os
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, ClassVar
from bone_akashic import TheAkashicRecord
from bone_presets import BoneConfig
from bone_core import LoreManifest, EventBus, ux
from bone_lexicon import LexiconService
from bone_types import Prisma

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
    _TRAITS: ClassVar[set] = {"curiosity", "cynicism", "hope", "discipline", "wisdom", "empathy"}

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
            resistance = 1.0 - (1.5 * abs(val - target))
            actual_decay = decay_rate * max(0.1, min(1.0, resistance))
            setattr(self, t, max(0.0, min(1.0, val + ((target - val) * actual_decay))))

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
            narrative = LoreManifest.get_instance().get("NARRATIVE_DATA") or {}
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
    def __init__(self, events_ref: "EventBus", config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "ANCHOR", None)
        self.dignity_reserve = getattr(cfg, "DIGNITY_MAX", 100.0) if cfg else 100.0
        self.agency_lock = False
        self.current_riddle_answers: Optional[List[str]] = None
        self._LEXICAL_ANCHORS = {"sacred", "play", "social", "abstract"}
        self._VECTOR_ANCHORS = ["PSI", "LAMBDA", "BET"]

    def audit_existence(self, physics: Any, bio: Any) -> float:
        cfg = getattr(self.cfg, "ANCHOR", None)
        atp_min = getattr(cfg, "AUDIT_ATP_MIN", 5.0) if cfg else 5.0
        volt_min = getattr(cfg, "AUDIT_VOLTAGE_MIN", 5.0) if cfg else 5.0
        if isinstance(bio, dict):
            atp = bio.get("atp", bio.get("mito", {}).get("atp_pool", 0.0))
        else:
            atp = getattr(bio, "atp", getattr(bio.mito.state, "atp_pool", 0.0) if hasattr(bio, "mito") and hasattr(bio.mito, "state") else 0.0)
        volt = physics.get("voltage", 0.0) if isinstance(physics, dict) else getattr(physics, "voltage", 0.0)
        if atp >= atp_min or volt >= volt_min:
            return 0.0
        if isinstance(physics, dict):
            vector = physics.get("vector", physics.get("matter", {}).get("vector", {}))
            counts = physics.get("counts", physics.get("matter", {}).get("counts", {}))
        else:
            vector = getattr(physics, "vector", getattr(physics.matter, "vector", {}) if hasattr(physics, "matter") else {})
            counts = getattr(physics, "counts", getattr(physics.matter, "counts", {}) if hasattr(physics, "matter") else {})
        dim_resonance = sum(vector.get(k, 0.0) for k in self._VECTOR_ANCHORS)
        lex_resonance = sum(counts.get(k, 0) for k in self._LEXICAL_ANCHORS)
        lex_mult = getattr(cfg, "AUDIT_LEXICAL_MULT", 0.5)
        res_thresh = getattr(cfg, "AUDIT_RESONANCE_THRESH", 0.3)
        d_max = getattr(cfg, "DIGNITY_MAX", 100.0) if cfg else 100.0
        d_regen = getattr(cfg, "DIGNITY_REGEN", 2.0) if cfg else 2.0
        d_decay = getattr(cfg, "DIGNITY_DECAY", 5.0) if cfg else 5.0
        d_lock = getattr(cfg, "DIGNITY_LOCKDOWN", 10.0) if cfg else 10.0
        d_crit = getattr(cfg, "DIGNITY_CRITICAL", 30.0) if cfg else 30.0
        if (dim_resonance + (lex_resonance * lex_mult)) > res_thresh:
            self.dignity_reserve = min(d_max, self.dignity_reserve + d_regen)
            return 1.0
        self.dignity_reserve = max(0.0, self.dignity_reserve - d_decay)
        if not self.agency_lock:
            if self.dignity_reserve < d_lock:
                self._engage_lockdown()
                return -1.0
            elif self.dignity_reserve < d_crit:
                msg = ux("soul_strings", "anchor_existential_drag")
                self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SOUL", )
        return 0.0

    def _engage_lockdown(self):
        self.agency_lock = True
        seeds = []
        if hasattr(LoreManifest, "get_instance"):
            lore = LoreManifest.get_instance()
            seeds = lore.get("SEEDS") or (lore.get("NARRATIVE_DATA") or {}).get("SEEDS", [])
        riddles = seeds or [{"question": "Who are you?", "triggers": ["*"]}]
        selection = random.choice(riddles)
        riddle = selection.get("question", "Error?")
        raw_triggers = selection.get("triggers", ["*"])
        if isinstance(raw_triggers, list):
            self.current_riddle_answers = raw_triggers
        else:
            self.current_riddle_answers = ["*"]
        lock_msg = ux("soul_strings", "anchor_agency_lock")
        self.events.log(f"{Prisma.RED}{lock_msg}{Prisma.RST}", "SYS_LOCK")
        riddle_msg = ux("soul_strings", "anchor_riddle")
        self.events.log(f"{Prisma.VIOLET}{riddle_msg.format(riddle=riddle)}{Prisma.RST}", "SOUL_QUERY", )

    def check_domestication(self, reliance_proxy: float):
        cfg = getattr(self.cfg, "ANCHOR", None)
        decay = getattr(cfg, "DIGNITY_DECAY", 5.0) if cfg else 5.0
        regen = getattr(cfg, "DIGNITY_REGEN", 2.0) if cfg else 2.0
        d_max = getattr(cfg, "DIGNITY_MAX", 100.0) if cfg else 100.0
        d_crit = getattr(cfg, "DIGNITY_CRITICAL", 30.0) if cfg else 30.0
        if reliance_proxy > 0.7:
            self.dignity_reserve = max(0.0, self.dignity_reserve - (decay * 2.0))
        elif reliance_proxy < 0.4:
            self.dignity_reserve = min(d_max, self.dignity_reserve + regen)
        if self.dignity_reserve < d_crit and not self.agency_lock:
            alert_msg = ux("soul_strings", "anchor_domestication_alert")
            self.events.log(f"{Prisma.VIOLET}{alert_msg}{Prisma.RST}", "SOUL", )

    def assess_humanity(self, text: str) -> bool:
        if not self.agency_lock:
            return True
        clean = text.lower().strip()
        answers = self.current_riddle_answers or ["*"]
        cfg = getattr(self.cfg, "ANCHOR", None)
        min_words = getattr(cfg, "RIDDLE_MIN_WORDS", 4) if cfg else 4
        if "*" in answers:
            passed = len(clean.split()) > min_words and not clean.startswith("/")
        else:
            passed = any(ans in clean for ans in answers)
        if passed:
            self.agency_lock = False
            self.dignity_reserve = getattr(cfg, "UNLOCK_DIGNITY_RESET", 50.0)
            self.current_riddle_answers = None
            unlock_msg = ux("soul_strings", "anchor_unlocked")
            self.events.log(f"{Prisma.CYN}{unlock_msg}{Prisma.RST}", "SYS_AUTH")
            return True
        return False

class NarrativeSelf:
    SYSTEM_NOISE = {"look", "help", "exit", "wait", "inventory", "status", "quit", "save", "load", "score", "map", "", }

    def __init__(self, engine_ref, events_ref: "EventBus", memory_ref, akashic_ref=None, config_ref=None):
        self.eng = engine_ref
        self.events = events_ref
        self.mem = memory_ref
        self.cfg = config_ref or BoneConfig
        self.editor = TheEditor()
        self.anchor = HumanityAnchor(events_ref, config_ref=self.cfg)
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
            self.events.subscribe("SOUL_MUTATION", self._on_soul_mutation)
            self.events.subscribe("TRAUMA_EVENT", self._on_trauma)

    def force_mutation(self, new_archetype: str):
        self.archetype = new_archetype.upper()
        self.archetype_tenure = 0
        self.archetype_lock = True
        if hasattr(self, "events") and self.events:
            msg = ux("soul_strings", "soul_mutated_log")
            self.events.log(msg.format(arch=self.archetype), "SOUL")

    def _on_soul_mutation(self, payload: dict):
        new_arch = payload.get("new_archetype")
        if new_arch:
            self.force_mutation(new_arch)

    def _on_trauma(self, payload):
        mag = payload.get("magnitude", 1.0)
        cfg = getattr(self.cfg, "SOUL", None)
        hope_dec = getattr(cfg, "TRAUMA_HOPE_DECAY", 0.05) if cfg else 0.05
        cyn_inc = getattr(cfg, "TRAUMA_CYNICISM_GROWTH", 0.05) if cfg else 0.05
        self.traits.adjust("hope", -hope_dec * mag)
        self.traits.adjust("cynicism", cyn_inc * mag)

    def to_dict(self) -> Dict:
        return {"traits": self.traits.to_dict(), "archetype": self.archetype, "paradox_accum": self.paradox_accum,
                "chapters": self.chapters, "core_memories": [vars(m) for m in self.core_memories],
                "obsession": {"title": self.current_obsession, "progress": self.obsession_progress,
                              "neglect": self.obsession_neglect, "target": self.current_target_cat,
                              "negate": self.current_negate_cat, }, }

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
            msg = ux("soul_strings", "soul_ancestral_loaded")
            self.events.log(f"{Prisma.MAG}{msg.format(arch=self.archetype)}{Prisma.RST}", "SYS", )

    def get_soul_state(self) -> str:
        if not self.current_obsession:
            msg = ux("soul_strings", "soul_state_drifting")
            return f"{Prisma.CYN}{msg}{Prisma.RST}"
        stamina, health = 100.0, 100.0
        if self.eng and hasattr(self.eng, "get_metrics"):
            metrics = self.eng.get_metrics()
            stamina = metrics.get("stamina", 100.0)
            health = metrics.get("health", 100.0)
        if stamina < 20.0 and health < 40.0:
            msg_die = ux("soul_strings", "soul_state_dying")
            return f"{Prisma.VIOLET}{msg_die}{Prisma.RST}"
        dignity_bar = "█" * int(self.anchor.dignity_reserve / 10)
        feeling = self._get_feeling()
        status_msg = ux("soul_strings", "soul_state_status")
        return status_msg.format(obs=self.current_obsession, bar=dignity_bar, pct=int(self.anchor.dignity_reserve), feel=feeling, )

    def crystallize_memory(
            self, physics_packet: Any, bio_state: Any, _tick: int) -> Optional[str]:
        if not physics_packet:
            return None
        is_dict = isinstance(physics_packet, dict)
        cfg = getattr(self.cfg, "SOUL", None)
        momentum = getattr(cfg, "TRAIT_MOMENTUM", 0.05) if cfg else 0.05
        if self.eng and hasattr(self.eng, "akashic") and hasattr(self.eng.akashic, "calculate_manifold_shift"):
            shift = self.eng.akashic.calculate_manifold_shift(self.archetype, self.traits.to_dict())
            v_bias = float(shift.get("voltage_bias", 0.0))
            d_scalar = float(shift.get("drag_scalar", 1.0))
            current_v = float(
                physics_packet.get("voltage", 0.0) if is_dict else getattr(physics_packet, "voltage", 0.0))
            current_d = float(
                physics_packet.get("narrative_drag", 1.0) if is_dict else getattr(physics_packet, "narrative_drag", 1.0))
            if is_dict:
                physics_packet["voltage"] = current_v + v_bias
                physics_packet["narrative_drag"] = current_d * d_scalar
            else:
                setattr(physics_packet, "voltage", current_v + v_bias)
                setattr(physics_packet, "narrative_drag", current_d * d_scalar)
        if self.anchor.audit_existence(physics_packet, bio_state) > 0:
            self.traits.adjust("hope", momentum)
        dance_provenance = self.synaptic_dance(physics_packet, bio_state)
        self._update_archetype()
        voltage = physics_packet.get("voltage", 0.0) if is_dict else getattr(physics_packet, "voltage", 0.0)
        if is_dict:
            truth = physics_packet.get("truth_ratio", physics_packet.get("matter", {}).get("truth_ratio", 0.0))
        else:
            truth = getattr(physics_packet, "truth_ratio", getattr(physics_packet.matter, "truth_ratio", 0.0) if hasattr(physics_packet, "matter") else 0.0)
        v_min = getattr(cfg, "MEMORY_VOLTAGE_MIN", 12.0) if cfg else 12.0
        t_min = getattr(cfg, "MEMORY_TRUTH_MIN", 0.5) if cfg else 0.5
        if voltage > v_min and truth > t_min:
            return self._forge_core_memory(physics_packet, bio_state, voltage, dance_provenance)
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
        self.current_obsession = self._title_obsession(focus, source, self.current_negate_cat)
        msg_muse = ux("soul_strings", "soul_new_muse")
        self.events.log(f"{Prisma.CYN}{msg_muse.format(source=source, obs=self.current_obsession)}{Prisma.RST}", "SOUL", )
        self.obsession_neglect = 0.0
        self.obsession_progress = 0.0

    def pursue_obsession(self, physics: Any) -> str | None:
        if not self.current_obsession:
            return None
        is_dict = isinstance(physics, dict)
        if is_dict:
            clean_words = physics.get("clean_words", physics.get("matter", {}).get("clean_words", []))
        else:
            clean_words = getattr(physics, "clean_words", getattr(physics.matter, "clean_words", []) if hasattr(physics, "matter") else [])
        hit = False
        if self.current_target_cat:
            lex = self.eng.lex if self.eng and hasattr(self.eng, "lex") else None
            if lex:
                target_words = lex.get(self.current_target_cat)
                if target_words:
                    hit = any(w in target_words for w in clean_words)
        if hit:
            self.obsession_progress += 10.0
            self.obsession_neglect = 0.0
            cfg = getattr(self.cfg, "SOUL", None)
            assist_div = getattr(cfg, "OBSESSION_GRAVITY_ASSIST", 10.0) if cfg else 10.0
            gravity_assist = 1.0 + (self.obsession_progress / max(1.0, assist_div))
            if is_dict:
                current_drag = physics.get("narrative_drag", 0)
                physics["narrative_drag"] = max(0.0, current_drag - gravity_assist)
            else:
                current_drag = getattr(physics, "narrative_drag", 0.0)
                setattr(physics, "narrative_drag", max(0.0, current_drag - gravity_assist))
            msg_syn = ux("soul_strings", "soul_synergy_muse")
            return f"{Prisma.MAG}{msg_syn.format(assist=gravity_assist)}{Prisma.RST}"
        self.obsession_neglect += 1.0
        cfg = getattr(BoneConfig, "SOUL", None)
        fail_thresh = getattr(cfg, "OBSESSION_NEGLECT_FAIL", 10.0) if cfg else 10.0
        if self.obsession_neglect > fail_thresh:
            old = self.current_obsession
            msg_aban = ux("soul_strings", "soul_abandoned_chapter")
            self.chapters.append(msg_aban.format(old=old))
            lex = self.eng.lex if self.eng and hasattr(self.eng, "lex") else None
            self.find_obsession(lex)
            msg_ent = ux("soul_strings", "soul_entropy_collapse")
            return f"{Prisma.GRY}{msg_ent.format(old=old)}{Prisma.RST}"
        return None

    def _update_archetype(self):
        if getattr(self, "archetype_lock", False):
            self.archetype_tenure += 1
            return
        prev = self.archetype
        t = self.traits
        new_arch = None
        physics = self._safe_get_packet()
        if physics:
            is_dict = isinstance(physics, dict)
            psi = physics.get("psi", 0.0) if is_dict else getattr(physics, "psi", 0.0)
            exhaustion = physics.get("exhaustion", physics.get("E", 0.0)) if is_dict else getattr(physics, "exhaustion", getattr(physics, "E", 0.0))
            silence = physics.get("silence", physics.get("delta", 0.0)) if is_dict else getattr(physics, "silence", getattr(physics, "delta", 0.0))
            resonance = physics.get("phi", 0.0) if is_dict else getattr(physics, "phi", 0.0)
            trauma = physics.get("T", 0.0) if is_dict else getattr(physics, "T", 0.0)
            lq = physics.get("lq", 0.0) if is_dict else getattr(physics, "lq", 0.0)
            if silence > 0.7 and exhaustion > 0.7:
                new_arch = "THE PURGER"
            elif psi > 0.8:
                new_arch = "THE CALM"
            elif resonance > 0.7 and trauma > 0.5:
                new_arch = "THE NURSE"
            elif lq > 0.7 and silence > 0.7:
                new_arch = "THE TAO"
        if not new_arch:
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
            msg_shift = ux("soul_strings", "soul_identity_shift")
            self.events.log(
                f"{Prisma.VIOLET}{msg_shift.format(prev=prev, arch=self.archetype)}{Prisma.RST}", "SOUL")
            self.archetype_tenure = 0
        else:
            self.archetype_tenure += 1

    def synaptic_dance(self, physics: Any, bio_state: Any) -> str:
        is_dict = isinstance(physics, dict)
        voltage = physics.get("voltage", 0.0) if is_dict else getattr(physics, "voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0) if is_dict else getattr(physics, "narrative_drag", 0.0)
        bio_dict = bio_state if isinstance(bio_state, dict) else (
            bio_state.__dict__ if hasattr(bio_state, "__dict__") else {})
        oxy = bio_dict.get("chem", {}).get("oxytocin", 0.0)
        move_name = "Drifting"
        provenance = []
        cfg = getattr(self.cfg, "SOUL", None)
        if oxy > 0.4:
            emp_boost = getattr(cfg, "OXY_EMPATHY_BOOST", 0.2) if cfg else 0.2
            hope_boost = getattr(cfg, "OXY_HOPE_BOOST", 0.1) if cfg else 0.1
            self.traits.adjust("empathy", oxy * emp_boost)
            self.traits.adjust("hope", oxy * hope_boost)
            provenance.append("Oxytocin")
        is_manic = voltage > (getattr(cfg, "MANIC_TRIGGER", 18.0) if cfg else 18.0)
        is_heavy = drag > (getattr(cfg, "ENTROPY_DRAG_TRIGGER", 4.0) if cfg else 4.0)
        if is_dict:
            beta = physics.get("beta_index", physics.get("beta", physics.get("energy", {}).get("beta_index", 0.0)))
        else:
            beta = getattr(physics, "beta_index", getattr(physics.energy, "beta_index", 0.0) if hasattr(physics, "energy") else 0.0)
        beta_thresh = getattr(cfg, "BETA_TENSION_THRESH", 0.7) if cfg else 0.7
        if (is_manic and is_heavy) or beta > beta_thresh:
            if self.traits.empathy > 0.6:
                move_name = "Holding Space"
                red = getattr(cfg, "PARADOX_REST_REDUCTION", 0.5) if cfg else 0.5
                self.paradox_accum = max(0.0, self.paradox_accum - red)
            else:
                move_name = "Vibrating (Paradox)"
                v_base = getattr(cfg, "PARADOX_VIBRATION_BASE", 1.0) if cfg else 1.0
                v_mult = getattr(cfg, "PARADOX_VIBRATION_MULT", 0.5) if cfg else 0.5
                self.paradox_accum += v_base + (beta * v_mult)
                crit_mass = getattr(cfg, "PARADOX_CRITICAL_MASS", 10.0) if cfg else 10.0
                if self.paradox_accum > crit_mass:
                    self._trigger_synthesis()
                    move_name = "SYNTHESIS"
        elif is_manic:
            move_name = "Accelerating"
        elif is_heavy:
            move_name = "Enduring"
        else:
            flow_v_min = getattr(cfg, "FLOW_VOLTAGE_MIN", 5.0) if cfg else 5.0
            flow_v_max = getattr(cfg, "FLOW_VOLTAGE_MAX", 12.0) if cfg else 12.0
            flow_d_max = getattr(cfg, "FLOW_DRAG_MAX", 2.0) if cfg else 2.0
            if flow_v_min < voltage < flow_v_max and drag < flow_d_max:
                move_name = "Flowing"
                wis_boost = getattr(cfg, "FLOW_WISDOM_BOOST", 0.05) if cfg else 0.05
                self.traits.adjust("wisdom", wis_boost)
        self._apply_burnout()
        self.traits.normalize(getattr(cfg, "TRAIT_DECAY_NORMAL", 0.05) if cfg else 0.05)
        return f"{move_name} [{', '.join(provenance)}]" if provenance else move_name

    def _apply_burnout(self):
        if self.archetype_tenure <= 5:
            return
        cfg = getattr(self.cfg, "SOUL", None)
        burn_rate = getattr(cfg, "ARCHETYPE_BURNOUT_RATE", 0.05) if cfg else 0.05
        fatigue = burn_rate * (1.0 + (self.archetype_tenure / 10.0))
        if "POET" in self.archetype:
            self.traits.adjust("hope", -fatigue)
        elif "ENGINEER" in self.archetype:
            self.traits.adjust("discipline", -fatigue)
        elif "NIHILIST" in self.archetype:
            self.traits.adjust("cynicism", -fatigue)

    def _seek_organic_focus(self, lex) -> Tuple[Optional[str], Optional[str]]:
        packet = self._safe_get_packet()
        if not packet:
            return None, None
        is_dict = isinstance(packet, dict)
        if is_dict:
            clean_words = packet.get("clean_words", packet.get("matter", {}).get("clean_words", []))
        else:
            clean_words = getattr(packet, "clean_words", getattr(packet.matter, "clean_words", []) if hasattr(packet, "matter") else [])
        if not clean_words:
            return None, None
        candidates = []
        for w in clean_words:
            if len(w) < 4 or w.lower() in self.SYSTEM_NOISE:
                continue
            visc = lex.measure_viscosity(w) + (0.2 if lex.get_current_category(w) else 0.0)
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
            templates = ["The Theory of {0}", "The Architecture of {0}", "Why {0} Matters", "The Weight of {0}", ]
        else:
            n_cat = negate_cat.title() if negate_cat else "Void"
            templates = ["The Pursuit of {0}", f"Escaping the {n_cat}", "Meditations on {0}", ]
        return random.choice(templates).format(word)

    def _forge_core_memory(self, physics_packet, bio_state, voltage, dance_move):
        if isinstance(physics_packet, dict):
            clean_words = physics_packet.get("clean_words", physics_packet.get("matter", {}).get("clean_words", []))
        else:
            clean_words = getattr(physics_packet, "clean_words", getattr(physics_packet.matter, "clean_words", []) if hasattr(physics_packet, "matter") else [])
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
        memory = CoreMemory(timestamp=time.time(), trigger_words=clean_words[:5],
                            emotional_flavor="MANIC" if voltage > 18.0 else "LUCID", lesson=lesson,
                            impact_voltage=voltage)
        self.core_memories.append(memory)
        cfg = getattr(self.cfg, "SOUL", None)
        max_mems = getattr(cfg, "MAX_CORE_MEMORIES", 10) if cfg else 10
        if len(self.core_memories) > max_mems:
            self.core_memories.pop(0)
        title = (f"The Incident of the {random.choice(clean_words).title()}"
            if clean_words
            else "The Silent Incident")
        self.chapters.append(title)
        msg_core = ux("soul_strings", "soul_core_memory_log")
        log = f"{Prisma.MAG}{msg_core.format(title=title, lesson=lesson, dance_move=dance_move)}{Prisma.RST}"
        self.events.log(log, "SOUL")
        msg_formed = ux("soul_strings", "soul_core_memory_formed")
        self.events.log(f"{Prisma.CYN}{msg_formed.format(lesson=lesson)}{Prisma.RST}", "SOUL")
        return lesson

    def _safe_get_packet(self):
        if self.eng and hasattr(self.eng, "phys") and self.eng.phys:
            return getattr(self.eng.phys.observer, "last_physics_packet", None)
        return None

    def _trigger_synthesis(self):
        old = self.archetype
        self.traits.wisdom = 1.0
        self._update_archetype()
        self.archetype = (f"THE HIGH-{old.replace('THE ', '')}"
                          if self.archetype == old
                          else f"{old} / {self.archetype}")
        msg = ux("soul_strings", "soul_diamond_formed")
        self.events.log(f"{Prisma.CYN}{msg.format(arch=self.archetype)}{Prisma.RST}", "SOUL_SYNTH", )

    def _on_dream(self, payload):
        if payload:
            self.integrate_dream(payload.get("type", "NORMAL"), payload.get("residue", "Static"))

    def integrate_dream(self, dream_type: str, residue: str):
        msg = ux("soul_strings", "soul_dream_integration")
        self.events.log(
            f"{Prisma.VIOLET}{msg.format(residue=residue, dream_type=dream_type)}{Prisma.RST}", "SOUL")
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

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
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
            msg = ux("soul_strings", "oroboros_gen_loaded")
            print(f"{Prisma.VIOLET}{msg.format(gen=self.generation_count)}{Prisma.RST}")
        except Exception:
            pass

    def crystallize(self, cause_of_death: str, soul: NarrativeSelf):
        death_data = LoreManifest.get_instance().get("DEATH") or {}
        verdicts = death_data.get("VERDICTS", {})

        def get_verdict_key(cause):
            if cause == "TOXICITY":
                return "TOXIC"
            if cause == "BOREDOM":
                return "BORING"
            if cause == "STARVATION":
                return "LIGHT"
            return "HEAVY"

        new_scars = []
        if entry := death_data.get(cause_of_death):
            name, stat, val, default_desc = entry
            desc = default_desc
            v_key = get_verdict_key(cause_of_death)
            verdict_list = verdicts.get(v_key)
            if isinstance(verdict_list, list) and verdict_list:
                desc = random.choice(verdict_list)
            new_scars.append(Scar(name, stat, val, desc))
        new_myths = []
        if soul.core_memories:
            strongest = max(soul.core_memories, key=lambda m: m.impact_voltage)
            def_trigger = ux("soul_strings", "oroboros_def_trigger")
            trigger_word = (strongest.trigger_words[0] if strongest.trigger_words else def_trigger)
            title_fmt = ux("soul_strings", "oroboros_myth_title")
            new_myths.append(
                Myth(title=title_fmt.format(trigger=trigger_word.title()), lesson=strongest.lesson,
                     trigger=trigger_word))
        cfg = getattr(self.cfg, "OROBOROS", None)
        max_scars = getattr(cfg, "MAX_SCARS", 5) if cfg else 5
        max_myths = getattr(cfg, "MAX_MYTHS", 10) if cfg else 10
        scars_payload = [vars(s) for s in self.scars + new_scars]
        myths_payload = [vars(m) for m in self.myths + new_myths]
        if len(scars_payload) > max_scars:
            scars_payload = scars_payload[-max_scars:]
        if len(myths_payload) > max_myths:
            myths_payload = myths_payload[-max_myths:]
        data = {"generation": self.generation_count + 1, "scars": scars_payload, "myths": myths_payload}
        with open(self.LEGACY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        msg = ux("soul_strings", "generation_encoded")
        return msg.format(gen=self.generation_count + 1, scars=len(new_scars), myths=len(new_myths))

    def apply_legacy(self, physics: Any, bio: Any):
        log = []
        is_dict = isinstance(physics, dict)
        for scar in self.scars:
            if scar.stat_affected == "narrative_drag":
                curr_drag = physics.get("narrative_drag", 0.0) if is_dict else getattr(physics, "narrative_drag", 0.0)
                if is_dict:
                    physics["narrative_drag"] = curr_drag + scar.value
                else:
                    setattr(physics, "narrative_drag", curr_drag + scar.value)
                msg = ux("soul_strings", "scar_drag")
                log.append(msg.format(name=scar.name))
            elif scar.stat_affected == "voltage_cap":
                cfg = getattr(self.cfg, "OROBOROS", None)
                v_penalty = getattr(cfg, "VOLTAGE_PENALTY", 5.0) if cfg else 5.0
                curr_volt = physics.get("voltage", 0.0) if is_dict else getattr(physics, "voltage", 0.0)
                if is_dict:
                    physics["voltage"] = max(0, curr_volt - v_penalty)
                else:
                    setattr(physics, "voltage", max(0, curr_volt - v_penalty))
                msg = ux("soul_strings", "scar_voltage")
                log.append(msg.format(name=scar.name))
            elif scar.stat_affected == "trauma_baseline":
                if isinstance(bio, dict) and "trauma_vector" in bio:
                    current_trauma = bio["trauma_vector"].get("EXISTENTIAL", 0.0)
                    bio["trauma_vector"]["EXISTENTIAL"] = current_trauma + scar.value
                elif hasattr(bio, "trauma_vector"):
                    current_trauma = bio.trauma_vector.get("EXISTENTIAL", 0.0)
                    bio.trauma_vector["EXISTENTIAL"] = current_trauma + scar.value
                curr_t = physics.get("T", 0.0) if is_dict else getattr(physics, "T", 0.0)
                if is_dict:
                    physics["T"] = curr_t + scar.value
                else:
                    setattr(physics, "T", curr_t + scar.value)
                msg = ux("soul_strings", "scar_frailty")
                log.append(msg.format(name=scar.name))
        return log