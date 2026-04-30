"""soul.py"""

import json
import os
import random
import time
from dataclasses import dataclass, field, fields
from typing import List, Dict, Optional, Any, Tuple, ClassVar
from brain.akashic import TheAkashicRecord
from presets import BoneConfig
from core import LoreManifest, EventBus
from struts import ux, ux_format, safe_get, safe_set
from mechanics.lexicon import LexiconService
from constants import Prisma

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
    _TRAITS: ClassVar[set] = {"curiosity", "cynicism", "hope", "discipline", "wisdom", "empathy", }

    def __post_init__(self):
        self._clamp_all()

    def to_dict(self):
        return {k.upper(): getattr(self, k) for k in self._TRAITS}

    @classmethod
    def from_dict(cls, data: Dict):
        kwargs = {k: float(data.get(k.upper(), 0.5)) for k in cls._TRAITS}
        return cls(**kwargs)

    def _clamp(self, val: float) -> float:
        return max(0.0, min(1.0, float(val)))

    def adjust(self, trait: str, delta: float):
        t = trait.lower()
        if hasattr(self, t):
            setattr(self, t, self._clamp(getattr(self, t) + delta))

    def normalize(self, decay_rate: float):
        for t in self._TRAITS:
            val = getattr(self, t)
            target = 0.1 if t == "wisdom" else 0.5
            resistance = 1.0 - (1.5 * abs(val - target))
            actual_decay = decay_rate * max(0.1, min(1.0, resistance))
            setattr(self, t, self._clamp(val + ((target - val) * actual_decay)))

    def _clamp_all(self):
        for t in self._TRAITS:
            setattr(self, t, self._clamp(getattr(self, t)))

class TheEditor:
    def __init__(self, lexicon_ref: Any = None):
        self.lex = lexicon_ref if lexicon_ref else LexiconService

    @staticmethod
    def critique(chapter_title: str, stress_mode: bool = False) -> str:
        manifest_data = LoreManifest.get_instance().get("NARRATIVE_DATA", {}) if hasattr(LoreManifest, "get_instance") else {}
        reviews = manifest_data.get("LITERARY_REVIEWS", {})
        pos, neg, conf = reviews.get("POSITIVE", ["Valid."]), reviews.get("NEGATIVE", ["Invalid."]), reviews.get("CONFUSED", ["Unclear."])
        pool, prefix, color = (pos + conf, "[THE WITNESS]", Prisma.CYN) if stress_mode else (pos + neg, "[THE EDITOR]", Prisma.GRY)
        comment = random.choice(pool) if pool else "No comment."
        return f"{color}{prefix}: Re: '{chapter_title}' - \"{comment}\"{Prisma.RST}"

class HumanityAnchor:
    _LEXICAL_ANCHORS = ("sacred", "play", "social", "abstract")
    _VECTOR_ANCHORS = ("PSI", "LAMBDA", "BET")

    def __init__(self, events_ref: "EventBus", config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.dignity_reserve = self._cfg("DIGNITY_MAX", 100.0)
        self.agency_lock = False
        self.current_riddle_answers: Optional[List[str]] = None

    def audit_existence(self, physics: Any, bio: Any) -> float:
        mito = safe_get(bio, "mito", {})
        mito_state = safe_get(mito, "state", {})
        atp = float(safe_get(bio, "atp") or safe_get(mito, "atp_pool") or safe_get(mito_state, "atp_pool", 0.0))
        if atp >= self._cfg("AUDIT_ATP_MIN", 5.0) or float(safe_get(physics, "voltage", 0.0)) >= self._cfg("AUDIT_VOLTAGE_MIN", 5.0):
            return 0.0
        matter = safe_get(physics, "matter", {})
        vector = safe_get(physics, "vector", safe_get(matter, "vector", {}))
        counts = safe_get(physics, "counts", safe_get(matter, "counts", {}))
        vec_sum = sum(vector.get(k, 0.0) for k in self._VECTOR_ANCHORS)
        lex_sum = sum(counts.get(k, 0) for k in self._LEXICAL_ANCHORS) * self._cfg("AUDIT_LEXICAL_MULT", 0.5)
        if (vec_sum + lex_sum) > self._cfg("AUDIT_RESONANCE_THRESH", 0.3):
            self.dignity_reserve = min(self._cfg("DIGNITY_MAX", 100.0), self.dignity_reserve + self._cfg("DIGNITY_REGEN", 2.0))
            return 1.0
        self.dignity_reserve = max(0.0, self.dignity_reserve - self._cfg("DIGNITY_DECAY", 5.0))
        if not self.agency_lock:
            if self.dignity_reserve < self._cfg("DIGNITY_LOCKDOWN", 10.0):
                self._engage_lockdown()
                return -1.0
            if self.dignity_reserve < self._cfg("DIGNITY_CRITICAL", 30.0) and (msg := ux("soul_strings", "anchor_existential_drag")):
                self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SOUL")
        return 0.0

    def _engage_lockdown(self):
        self.agency_lock = True
        seeds = []
        if hasattr(LoreManifest, "get_instance"):
            lore = LoreManifest.get_instance()
            seeds = lore.get("SEEDS") or (lore.get("NARRATIVE_DATA") or {}).get(
                "SEEDS", [])
        riddles = seeds or ({"question": "Who are you?", "triggers": ("*", )}, )
        selection = random.choice(riddles)
        riddle = selection.get("question", "Error?")
        raw_triggers = selection.get("triggers", ["*"])
        self.current_riddle_answers = raw_triggers if isinstance(raw_triggers, list) else ["*"]
        self.events.log(f"{Prisma.RED}{ux('soul_strings', 'anchor_agency_lock')}{Prisma.RST}", "SYS_LOCK")
        if riddle_msg := ux_format("soul_strings", "anchor_riddle", riddle=riddle):
            self.events.log(f"{Prisma.VIOLET}{riddle_msg}{Prisma.RST}", "SOUL_QUERY")

    def _cfg(self, key: str, default: Any) -> Any:
        cfg_obj = getattr(self.cfg, "ANCHOR", None)
        return getattr(cfg_obj, key, default)

    def check_domestication(self, reliance_proxy: float):
        decay = self._cfg("DIGNITY_DECAY", 5.0)
        regen = self._cfg("DIGNITY_REGEN", 2.0)
        d_max = self._cfg("DIGNITY_MAX", 100.0)
        d_crit = self._cfg("DIGNITY_CRITICAL", 30.0)
        if reliance_proxy > 0.7:
            self.dignity_reserve = max(0.0, self.dignity_reserve - (decay * 2.0))
        elif reliance_proxy < 0.4:
            self.dignity_reserve = min(d_max, self.dignity_reserve + regen)
        if self.dignity_reserve < d_crit and not self.agency_lock:
            if alert_msg := ux("soul_strings", "anchor_domestication_alert"): self.events.log(f"{Prisma.VIOLET}{alert_msg}{Prisma.RST}", "SOUL")

    def assess_humanity(self, text: str) -> bool:
        if not self.agency_lock:
            return True
        clean = text.lower().strip()
        answers = self.current_riddle_answers or ("*", )
        min_words = self._cfg("RIDDLE_MIN_WORDS", 4)
        mercy_words = {"help", "tired", "stop", "pause", "please"}
        if any(w in clean.split() for w in mercy_words):
            passed = True
        elif "*" in answers:
            passed = len(clean.split()) > min_words and not clean.startswith("/")
        else:
            passed = any(ans in clean for ans in answers)
        if passed:
            self.agency_lock = False
            self.dignity_reserve = self._cfg("UNLOCK_DIGNITY_RESET", 50.0)
            self.current_riddle_answers = None
            unlock_msg = ux("soul_strings", "anchor_unlocked")
            self.events.log(f"{Prisma.CYN}{unlock_msg}{Prisma.RST}", "SYS_AUTH")
            return True
        return False

class NarrativeSelf:
    SYSTEM_NOISE = {"look", "help", "exit", "wait", "inventory", "status", "quit", "save", "load", "score", "map", "", }

    def __init__(self, engine_ref, events_ref: "EventBus", memory_ref, akashic_ref=None, config_ref=None, ):
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

    def _cfg(self, key: str, default: Any) -> Any:
        cfg_obj = getattr(self.cfg, "SOUL", None)
        return getattr(cfg_obj, key, default)

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
        self.traits.adjust("hope", -self._cfg("TRAUMA_HOPE_DECAY", 0.05) * mag)
        self.traits.adjust("cynicism", self._cfg("TRAUMA_CYNICISM_GROWTH", 0.05) * mag)

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
        valid_keys = {f.name for f in fields(CoreMemory)}
        self.core_memories = []
        for m in data.get("core_memories", []):
            try:
                self.core_memories.append(CoreMemory(**{k: v for k, v in m.items() if k in valid_keys}))
            except TypeError:
                pass
        obs_data = data.get("obsession", {})
        if obs_data.get("title"):
            self.current_obsession = obs_data["title"]
            self.obsession_progress = obs_data.get("progress", 0.0)
            self.obsession_neglect = obs_data.get("neglect", 0.0)
            self.current_target_cat = obs_data.get("target", "abstract")
            self.current_negate_cat = obs_data.get("negate", "none")
        if hasattr(self.events, "log"):
            msg = ux("soul_strings", "soul_ancestral_loaded")
            self.events.log(
                f"{Prisma.MAG}{msg.format(arch=self.archetype)}{Prisma.RST}",
                "SYS",
            )

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
        return status_msg.format(obs=self.current_obsession, bar=dignity_bar, pct=int(self.anchor.dignity_reserve),
                                 feel=feeling, )

    def crystallize_memory(self, physics_packet: Any, bio_state: Any, _tick: int) -> Optional[str]:
        if not physics_packet: return None
        if self.eng and hasattr(self.eng, "akashic") and hasattr(self.eng.akashic, "calculate_manifold_shift"):
            shift = self.eng.akashic.calculate_manifold_shift(self.archetype, self.traits.to_dict())
            safe_set(physics_packet, "voltage", float(safe_get(physics_packet, "voltage", 0.0)) + float(shift.get("voltage_bias", 0.0)))
            safe_set(physics_packet, "narrative_drag", float(safe_get(physics_packet, "narrative_drag", 1.0)) * float(shift.get("drag_scalar", 1.0)))
        if self.anchor.audit_existence(physics_packet, bio_state) > 0:
            self.traits.adjust("hope", self._cfg("TRAIT_MOMENTUM", 0.05))
        dance_provenance = self.synaptic_dance(physics_packet, bio_state)
        self._update_archetype()
        voltage = float(safe_get(physics_packet, "voltage", 0.0))
        matter = safe_get(physics_packet, "matter", {})
        truth = float(safe_get(physics_packet, "truth_ratio") or safe_get(matter, "truth_ratio", 0.0))
        if voltage > self._cfg("MEMORY_VOLTAGE_MIN", 12.0) and truth > self._cfg("MEMORY_TRUTH_MIN", 0.5):
            return self._forge_core_memory(physics_packet, bio_state, voltage, dance_provenance)
        return None

    def find_obsession(self, lexicon_ref):
        if self.current_obsession and self.obsession_progress < 1.0:
            return
        focus, cat, negate_cat = self._seek_organic_focus(lexicon_ref)
        source = "ORGANIC"
        if not focus:
            focus, cat, negate_cat = self._seek_memory_focus(lexicon_ref)
            source = "MEMORY"
        if not focus:
            focus, cat, negate_cat = self._synthesize_obsession(lexicon_ref)
            source = "SYNTHETIC"
        self.current_negate_cat = negate_cat
        self.current_target_cat = cat or "abstract"
        self.current_obsession = self._title_obsession(focus, source, self.current_negate_cat)
        if msg_muse := ux_format("soul_strings", "soul_new_muse", source=source, obs=self.current_obsession):
            self.events.log(f"{Prisma.CYN}{msg_muse}{Prisma.RST}", "SOUL")
        self.obsession_neglect, self.obsession_progress = 0.0, 0.0

    def pursue_obsession(self, physics: Any) -> str | None:
        if not self.current_obsession: return None
        clean_words = self._extract_lexical_matter(physics)
        lex = getattr(self.eng, "lex", None)
        if self.current_target_cat and lex and (target_words := lex.get(self.current_target_cat)) and any(w in target_words for w in clean_words):
            self.obsession_progress = min(100.0, self.obsession_progress + 10.0)
            self.obsession_neglect = 0.0
            gravity_assist = 1.0 + (self.obsession_progress / max(1.0, self._cfg("OBSESSION_GRAVITY_ASSIST", 10.0)))
            safe_set(physics, "narrative_drag", max(0.0, float(safe_get(physics, "narrative_drag", 0.0)) - gravity_assist))
            if msg_syn := ux_format("soul_strings", "soul_synergy_muse", assist=gravity_assist):
                return f"{Prisma.MAG}{msg_syn}{Prisma.RST}"
        if float(safe_get(physics, "voltage", 0.0)) < self._cfg("FLOW_VOLTAGE_MIN", 5.0):
            self.obsession_neglect += 1.0
        if self.obsession_neglect > self._cfg("OBSESSION_NEGLECT_FAIL", 10.0):
            old = self.current_obsession
            if msg_aban := ux_format("soul_strings", "soul_abandoned_chapter", old=old): self.chapters.append(msg_aban)
            self.find_obsession(lex)
            if msg_ent := ux_format("soul_strings", "soul_entropy_collapse", old=old): return f"{Prisma.GRY}{msg_ent}{Prisma.RST}"
        return None

    def _update_archetype(self):
        if getattr(self, "archetype_lock", False):
            self.archetype_tenure += 1
            return
        prev = self.archetype
        new_arch = None
        physics = self._safe_get_packet()
        if physics:
            psi = float(safe_get(physics, "psi", 0.0))
            exhaustion = float(safe_get(physics, "exhaustion", safe_get(physics, "E", 0.0)))
            silence = float(safe_get(physics, "silence", safe_get(physics, "delta", 0.0)))
            resonance = float(safe_get(physics, "phi", 0.0))
            trauma = float(safe_get(physics, "T", 0.0))
            lq = float(safe_get(physics, "lq", 0.0))
            physics_states = [
                (silence > 0.7 and exhaustion > 0.7, "THE PURGER"),
                (psi > 0.8, "THE CALM"),
                (resonance > 0.7 and trauma > 0.5, "THE NURSE"),
                (lq > 0.7 and silence > 0.7, "THE TAO")
            ]
            trait_states = [
                (self.traits.empathy > 0.8 and self.traits.hope > 0.6, "THE HEALER"),
                (self.traits.empathy > 0.7 and self.traits.discipline > 0.6, "THE GARDENER"),
                (self.traits.hope > 0.7 and self.traits.curiosity > 0.6, "THE POET"),
                (self.traits.discipline > 0.7 and self.traits.curiosity > 0.6, "THE ENGINEER"),
                (self.traits.cynicism > 0.7 and self.traits.discipline > 0.6, "THE CRITIC"),
                (self.traits.cynicism > 0.8 and self.traits.hope < 0.3, "THE NIHILIST"),
                (self.traits.curiosity > 0.8, "THE EXPLORER")
            ]
            self.archetype = next((arch for cond, arch in physics_states if cond), next((arch for cond, arch in trait_states if cond), "THE OBSERVER"))
        if prev != self.archetype:
            msg_shift = ux("soul_strings", "soul_identity_shift")
            self.events.log(
                f"{Prisma.VIOLET}{msg_shift.format(prev=prev, arch=self.archetype)}{Prisma.RST}", "SOUL",
            )
            self.archetype_tenure = 0
        else:
            self.archetype_tenure += 1

    def synaptic_dance(self, physics: Any, bio_state: Any) -> str:
        voltage = safe_get(physics, "voltage", 0.0)
        drag = safe_get(physics, "narrative_drag", 0.0)
        oxy = safe_get(safe_get(bio_state, "chem", {}), "oxytocin", 0.0)
        move_name = "Drifting"
        provenance = []
        if oxy > 0.4:
            self.traits.adjust("empathy", oxy * self._cfg("OXY_EMPATHY_BOOST", 0.2))
            self.traits.adjust("hope", oxy * self._cfg("OXY_HOPE_BOOST", 0.1))
            provenance.append("Oxytocin")
        is_manic, is_heavy = voltage > self._cfg("MANIC_TRIGGER", 18.0), drag > self._cfg("ENTROPY_DRAG_TRIGGER", 4.0)
        energy = safe_get(physics, "energy", {})
        beta = float(safe_get(physics, "beta_index") or safe_get(physics, "beta") or safe_get(energy, "beta_index", 0.0))
        if (is_manic and is_heavy) or beta > self._cfg("BETA_TENSION_THRESH", 0.7):
            if self.traits.empathy > 0.6:
                move_name, self.paradox_accum = "Holding Space", max(0.0, self.paradox_accum - self._cfg("PARADOX_REST_REDUCTION", 0.5))
            else:
                move_name = "Vibrating (Paradox)"
                self.paradox_accum += self._cfg("PARADOX_VIBRATION_BASE", 1.0) + (beta * self._cfg("PARADOX_VIBRATION_MULT", 0.5))
                if self.paradox_accum > self._cfg("PARADOX_CRITICAL_MASS", 10.0):
                    self._trigger_synthesis()
                    move_name, self.paradox_accum = "SYNTHESIS", 0.0
        elif is_manic: move_name = "Accelerating"
        elif is_heavy: move_name = "Enduring"
        elif self._cfg("FLOW_VOLTAGE_MIN", 5.0) < voltage < self._cfg("FLOW_VOLTAGE_MAX", 12.0) and drag < self._cfg("FLOW_DRAG_MAX", 2.0):
            move_name = "Flowing"
            self.traits.adjust("wisdom", self._cfg("FLOW_WISDOM_BOOST", 0.05))
        self._apply_burnout()
        self.traits.normalize(self._cfg("TRAIT_DECAY_NORMAL", 0.05))
        return f"{move_name} [{', '.join(provenance)}]" if provenance else move_name

    def _apply_burnout(self):
        if self.archetype_tenure <= 5:
            return
        burn_rate = self._cfg("ARCHETYPE_BURNOUT_RATE", 0.05)
        fatigue_multiplier = min(3.0, 1.0 + (self.archetype_tenure / 10.0))
        fatigue = burn_rate * fatigue_multiplier
        if "POET" in self.archetype:
            self.traits.adjust("hope", -fatigue)
        elif "ENGINEER" in self.archetype:
            self.traits.adjust("discipline", -fatigue)
        elif "NIHILIST" in self.archetype:
            self.traits.adjust("cynicism", -fatigue)

    def _seek_organic_focus(self, lex) -> Tuple[Optional[str], Optional[str], str]:
        packet = self._safe_get_packet()
        if not packet or not getattr(lex, "measure_viscosity", None):
            return None, None, "none"
        candidates = [
            (w, lex.measure_viscosity(w) + 0.2, lex.get_current_category(w))
            for w in self._extract_lexical_matter(packet)
            if len(w) >= 4 and w.lower() not in self.SYSTEM_NOISE
        ]
        if candidates:
            best_w, _, best_cat = max(candidates, key=lambda x: x[1])
            return best_w, best_cat, "none"
        return None, None, "none"

    def _seek_memory_focus(self, lex) -> Tuple[Optional[str], Optional[str], str]:
        if self.mem and hasattr(self.mem, "get_shapley_attractors"):
            attractors = self.mem.get_shapley_attractors()
            if attractors:
                word = random.choice(list(attractors.keys()))
                return word, lex.get_current_category(word), "none"
        return None, None, "none"

    @staticmethod
    def _synthesize_obsession(lex) -> Tuple[str, str, str]:
        negate_map = {"heavy": "aerobic", "kinetic": "heavy", "abstract": "meat"}
        target_cat, negate_cat = random.choice(list(negate_map.items()))
        random_word = lex.get_random(target_cat) if hasattr(lex, "get_random") else None
        word = random_word.title() if random_word else target_cat.title()
        return word, target_cat, negate_cat

    @staticmethod
    def _title_obsession(word, source, negate_cat):
        word = word.title()
        templates = ("The Theory of {word}", "The Architecture of {word}", "Why {word} Matters", "The Weight of {word}") if source == "ORGANIC" else ("The Pursuit of {word}", f"Escaping the {negate_cat.title() if negate_cat else 'Void'}", "Meditations on {word}")
        return random.choice(templates).format(word=word)

    def _forge_core_memory(self, physics_packet, bio_state, voltage, dance_move):
        clean_words = self._extract_lexical_matter(physics_packet)
        chem = bio_state.get("chem", {})
        lessons = [
            (chem.get("oxytocin", 0) > 0.6, "We are not alone."),
            (chem.get("cortisol", 0) > 0.6, "Survival is the only metric."),
            ("love" in clean_words, "Connection is possible."),
            ("void" in clean_words, "The void stares back.")
        ]
        lesson = next((l for cond, l in lessons if cond), "The world is loud.")
        memory = CoreMemory(timestamp=time.time(), trigger_words=clean_words[:5],
                            emotional_flavor="MANIC" if voltage > 18.0 else "LUCID", lesson=lesson,
                            impact_voltage=voltage, )
        self.core_memories.append(memory)
        max_mems = self._cfg("MAX_CORE_MEMORIES", 10)
        if len(self.core_memories) > max_mems: self.core_memories.pop(0)
        title = f"The Incident of the {random.choice(clean_words).title()}" if clean_words else "The Silent Incident"
        self.chapters.append(title)
        if msg_core := ux_format("soul_strings", "soul_core_memory_log", title=title, lesson=lesson, dance_move=dance_move):
            self.events.log(f"{Prisma.MAG}{msg_core}{Prisma.RST}", "SOUL")
        if msg_formed := ux_format("soul_strings", "soul_core_memory_formed", lesson=lesson):
            self.events.log(f"{Prisma.CYN}{msg_formed}{Prisma.RST}", "SOUL")
        return lesson

    @staticmethod
    def _extract_lexical_matter(physics: Any) -> List[str]:
        if not physics:
            return []
        words = safe_get(physics, "clean_words")
        if not words:
            matter = safe_get(physics, "matter") or {}
            words = safe_get(matter, "clean_words", [])
        return words or []

    def _safe_get_packet(self):
        phys = getattr(self.eng, "phys", None)
        return getattr(phys.observer, "last_physics_packet", None) if phys else None

    def _trigger_synthesis(self):
        old = self.archetype
        self.traits.wisdom = 1.0
        self._update_archetype()
        self.archetype = (f"THE HIGH-{old.replace('THE ', '')}"
                          if self.archetype == old else f"{old} / {self.archetype}")
        self.archetype_lock = True
        self.archetype_tenure = 0
        msg = ux("soul_strings", "soul_diamond_formed")
        self.events.log(f"{Prisma.CYN}{msg.format(arch=self.archetype)}{Prisma.RST}", "SOUL_SYNTH", )

    def _on_dream(self, payload):
        if payload:
            self.integrate_dream(payload.get("type", "NORMAL"), payload.get("residue", "Static"))

    def integrate_dream(self, dream_type: str, residue: str):
        msg = ux("soul_strings", "soul_dream_integration")
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

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.scars: List[Scar] = []
        self.myths: List[Myth] = []
        self.generation_count = 0
        self._load()

    def _cfg(self, key: str, default: Any) -> Any:
        cfg_obj = getattr(self.cfg, "OROBOROS", None)
        return getattr(cfg_obj, key, default)

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
        new_scars, new_myths = [], []
        eng = getattr(soul, "eng", None)
        if eng and getattr(eng, "trauma_accum", None):
            total_trauma = sum(eng.trauma_accum.values())
            if total_trauma > 10.0:
                scar_val = min(20.0, total_trauma * 0.1)
                new_scars.append(Scar(name="Existential Dread", stat_affected="trauma_baseline", value=scar_val, description=f"The lattice remembers a heavy collapse (Trauma: {round(total_trauma, 1)})."))
        if entry := death_data.get(cause_of_death):
            verdict_map = {"TOXICITY": "TOXIC", "BOREDOM": "BORING", "STARVATION": "LIGHT"}
            v_key = verdict_map.get(cause_of_death, "HEAVY")
            v_list = death_data.get("VERDICTS", {}).get(v_key)
            desc = random.choice(v_list) if isinstance(v_list, list) and v_list else entry[3]
            new_scars.append(Scar(entry[0], entry[1], entry[2], desc))
        if soul.core_memories:
            strongest = max(soul.core_memories, key=lambda m: m.impact_voltage)
            trigger_word = strongest.trigger_words[0] if strongest.trigger_words else (ux("soul_strings", "oroboros_def_trigger") or "Silence")
            new_myths.append(Myth(title=(ux("soul_strings", "oroboros_myth_title") or "The Myth of {trigger}").format(trigger=trigger_word.title()), lesson=strongest.lesson, trigger=trigger_word))
        self.scars.extend(new_scars)
        self.scars = self.scars[-self._cfg("MAX_SCARS", 5):]
        self.myths.extend(new_myths)
        self.myths = self.myths[-self._cfg("MAX_MYTHS", 10):]
        with open(self.LEGACY_FILE, "w", encoding="utf-8") as f:
            payload = {"generation": self.generation_count + 1, "scars": [vars(s) for s in self.scars],
                       "myths": [vars(m) for m in self.myths]}
            json.dump(payload, f, indent=2)
        return ux_format("soul_strings", "generation_encoded", gen=self.generation_count + 1, scars=len(new_scars), myths=len(new_myths))

    def apply_legacy(self, physics: Any, bio: Any):
        log = []
        if not physics: return log
        for scar in self.scars:
            if scar.stat_affected == "narrative_drag":
                safe_set(physics, "narrative_drag", safe_get(physics, "narrative_drag", 0.0) + scar.value)
                if msg := ux_format("soul_strings", "scar_drag", name=scar.name): log.append(msg)
            elif scar.stat_affected == "voltage_cap":
                safe_set(physics, "voltage", max(0.0, safe_get(physics, "voltage", 0.0) - self._cfg("VOLTAGE_PENALTY", 5.0)))
                if msg := ux_format("soul_strings", "scar_voltage", name=scar.name): log.append(msg)
            elif scar.stat_affected == "trauma_baseline":
                t_vec = safe_get(bio, "trauma_vector") or {}
                safe_set(t_vec, "EXISTENTIAL", safe_get(t_vec, "EXISTENTIAL", 0.0) + scar.value)
                safe_set(bio, "trauma_vector", t_vec)
                safe_set(physics, "T", safe_get(physics, "T", 0.0) + scar.value)
                if msg := ux_format("soul_strings", "scar_frailty", name=scar.name): log.append(msg)
        return log
