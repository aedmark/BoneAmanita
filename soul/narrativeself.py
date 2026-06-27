"""/soul/narrativeself.py"""

import random
import time
from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Optional, Tuple

from brain.akashic import TheAkashicRecord
from constants import Prisma
from core import EventBus
from presets import BoneConfig
from soul import SchurProtocol, TheEditor
from soul.traitvector import TraitVector
from struts import safe_get, safe_set, ux, ux_format


@dataclass
class CoreMemory:
    timestamp: float
    trigger_words: List[str]
    emotional_flavor: str
    lesson: str
    impact_voltage: float
    type: str = "INCIDENT"
    meta: Dict[str, Any] = field(default_factory=dict)


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
        self,
        engine_ref,
        events_ref: "EventBus",
        memory_ref,
        akashic_ref=None,
        config_ref=None,
    ):
        self.eng = engine_ref
        self.events = events_ref
        self.mem = memory_ref
        self.cfg = config_ref or BoneConfig
        self.editor = TheEditor()
        self.anchor = SchurProtocol(events_ref, config_ref=self.cfg)
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
        self.events.subscribe("DREAM_COMPLETE", self._on_dream)
        self.events.subscribe("SOUL_MUTATION", self._on_soul_mutation)
        self.events.subscribe("TRAUMA_EVENT", self._on_trauma)

    def _cfg(self, key: str, default: Any) -> Any:
        val = safe_get(safe_get(self.cfg, "SOUL", {}), key, default)
        return (
            float(val)
            if isinstance(default, float)
            else int(val)
            if isinstance(default, int)
            else val
        )

    def force_mutation(self, new_archetype: str):
        self.archetype = new_archetype.upper()
        self.archetype_tenure = 0
        self.archetype_lock = True
        if hasattr(self, "events") and self.events:
            if msg := ux_format(
                "soul_strings", "soul_mutated_log", arch=self.archetype
            ):
                self.events.log(msg, "SOUL")

    def _on_soul_mutation(self, payload: dict):
        new_arch = payload.get("new_archetype")
        if isinstance(new_arch, str):
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
                self.core_memories.append(
                    CoreMemory(**{k: v for k, v in m.items() if k in valid_keys})
                )
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
            if msg := ux_format(
                "soul_strings", "soul_ancestral_loaded", arch=self.archetype
            ):
                self.events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "SYS")

    def get_soul_state(self) -> str:
        if not self.current_obsession:
            msg = ux("soul_strings", "soul_state_drifting") or "Drifting..."
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
        return ux_format(
            "soul_strings",
            "soul_state_status",
            default=f"Obsession: {self.current_obsession} | {feeling}",
            obs=self.current_obsession,
            bar=dignity_bar,
            pct=int(self.anchor.dignity_reserve),
            feel=feeling,
        )

    def crystallize_memory(
        self, physics_packet: Any, bio_state: Any, _tick: int
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
            safe_set(
                physics_packet,
                "voltage",
                float(safe_get(physics_packet, "voltage", 0.0))
                + float(shift.get("voltage_bias", 0.0)),
            )
            safe_set(
                physics_packet,
                "narrative_drag",
                float(safe_get(physics_packet, "narrative_drag", 1.0))
                * float(shift.get("drag_scalar", 1.0)),
            )
        if self.anchor.audit_existence(physics_packet, bio_state) > 0:
            self.traits.adjust("hope", self._cfg("TRAIT_MOMENTUM", 0.05))
        dance_provenance = self.synaptic_dance(physics_packet, bio_state)
        self._update_archetype()
        voltage = float(safe_get(physics_packet, "voltage", 0.0))
        matter = safe_get(physics_packet, "matter", {})
        truth = float(
            safe_get(physics_packet, "truth_ratio")
            or safe_get(matter, "truth_ratio", 0.0)
        )
        if voltage > self._cfg("MEMORY_VOLTAGE_MIN", 12.0) and truth > self._cfg(
            "MEMORY_TRUTH_MIN", 0.5
        ):
            return self._forge_core_memory(
                physics_packet, bio_state, voltage, dance_provenance
            )
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
        self.current_obsession = self._title_obsession(
            focus, source, self.current_negate_cat
        )
        if msg_muse := ux_format(
            "soul_strings", "soul_new_muse", source=source, obs=self.current_obsession
        ):
            self.events.log(f"{Prisma.CYN}{msg_muse}{Prisma.RST}", "SOUL")
        self.obsession_neglect, self.obsession_progress = 0.0, 0.0

    def pursue_obsession(self, physics: Any) -> str | None:
        if not self.current_obsession:
            return None
        clean_words = self._extract_lexical_matter(physics)
        lex = getattr(self.eng, "lex", None)
        target_words = (
            lex.get(self.current_target_cat)
            if (self.current_target_cat and lex)
            else set()
        )
        if target_words and not target_words.isdisjoint(clean_words):
            self.obsession_progress = min(100.0, self.obsession_progress + 10.0)
            self.obsession_neglect = 0.0
            gravity_assist = 1.0 + (
                self.obsession_progress
                / max(1.0, self._cfg("OBSESSION_GRAVITY_ASSIST", 10.0))
            )
            safe_set(
                physics,
                "narrative_drag",
                max(
                    0.0,
                    float(safe_get(physics, "narrative_drag", 0.0)) - gravity_assist,
                ),
            )
            if msg_syn := ux_format(
                "soul_strings", "soul_synergy_muse", assist=gravity_assist
            ):
                return f"{Prisma.MAG}{msg_syn}{Prisma.RST}"
        if float(safe_get(physics, "voltage", 0.0)) < self._cfg(
            "FLOW_VOLTAGE_MIN", 5.0
        ):
            self.obsession_neglect += 1.0
        if self.obsession_neglect > self._cfg("OBSESSION_NEGLECT_FAIL", 10.0):
            old = self.current_obsession
            if msg_aban := ux_format("soul_strings", "soul_abandoned_chapter", old=old):
                self.chapters.append(msg_aban)
                if len(self.chapters) > self._cfg("MAX_CHAPTERS", 20):
                    self.chapters.pop(0)
                critique_log = self.editor.critique(msg_aban, stress_mode=True)
                self.events.log(critique_log, "SOUL_CRITIC")
            self.find_obsession(lex)
            if msg_ent := ux_format("soul_strings", "soul_entropy_collapse", old=old):
                return f"{Prisma.GRY}{msg_ent}{Prisma.RST}"
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
            exhaustion = float(
                safe_get(physics, "exhaustion", safe_get(physics, "E", 0.0))
            )
            silence = float(
                safe_get(physics, "silence", safe_get(physics, "delta", 0.0))
            )
            resonance = float(safe_get(physics, "phi", 0.0))
            trauma = float(safe_get(physics, "T", 0.0))
            lq = float(safe_get(physics, "lq", 0.0))

            if silence > 0.7 and exhaustion > 0.7:
                self.archetype = "THE PURGER"
            elif psi > 0.8:
                self.archetype = "THE CALM"
            elif resonance > 0.7 and trauma > 0.5:
                self.archetype = "THE NURSE"
            elif lq > 0.7 and silence > 0.7:
                self.archetype = "THE TAO"
            elif self.traits.empathy > 0.8 and self.traits.hope > 0.6:
                self.archetype = "THE HEALER"
            elif self.traits.empathy > 0.7 and self.traits.discipline > 0.6:
                self.archetype = "THE GARDENER"
            elif self.traits.hope > 0.7 and self.traits.curiosity > 0.6:
                self.archetype = "THE POET"
            elif self.traits.discipline > 0.7 and self.traits.curiosity > 0.6:
                self.archetype = "THE ENGINEER"
            elif self.traits.cynicism > 0.7 and self.traits.discipline > 0.6:
                self.archetype = "THE CRITIC"
            elif self.traits.cynicism > 0.8 and self.traits.hope < 0.3:
                self.archetype = "THE NIHILIST"
            elif self.traits.curiosity > 0.8:
                self.archetype = "THE EXPLORER"
            else:
                self.archetype = "THE OBSERVER"

        if prev != self.archetype:
            if msg_shift := ux_format(
                "soul_strings", "soul_identity_shift", prev=prev, arch=self.archetype
            ):
                self.events.log(f"{Prisma.VIOLET}{msg_shift}{Prisma.RST}", "SOUL")
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
        is_manic, is_heavy = (
            voltage > self._cfg("MANIC_TRIGGER", 18.0),
            drag > self._cfg("ENTROPY_DRAG_TRIGGER", 4.0),
        )
        energy = safe_get(physics, "energy", {})
        beta = float(
            safe_get(physics, "beta_index")
            or safe_get(physics, "beta")
            or safe_get(energy, "beta_index", 0.0)
        )
        if (is_manic and is_heavy) or beta > self._cfg("BETA_TENSION_THRESH", 0.7):
            if self.traits.empathy > 0.6:
                move_name, self.paradox_accum = (
                    "Holding Space",
                    max(
                        0.0,
                        self.paradox_accum - self._cfg("PARADOX_REST_REDUCTION", 0.5),
                    ),
                )
            else:
                move_name = "Vibrating (Paradox)"
                self.paradox_accum += self._cfg("PARADOX_VIBRATION_BASE", 1.0) + (
                    beta * self._cfg("PARADOX_VIBRATION_MULT", 0.5)
                )
                if self.paradox_accum > self._cfg("PARADOX_CRITICAL_MASS", 10.0):
                    self._trigger_synthesis()
                    move_name, self.paradox_accum = "SYNTHESIS", 0.0
        elif is_manic:
            move_name = "Accelerating"
        elif is_heavy:
            move_name = "Enduring"
        elif self._cfg("FLOW_VOLTAGE_MIN", 5.0) < voltage < self._cfg(
            "FLOW_VOLTAGE_MAX", 12.0
        ) and drag < self._cfg("FLOW_DRAG_MAX", 2.0):
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
        if not packet or lex is None or not hasattr(lex, "measure_viscosity"):
            return None, None, "none"
        candidates = (
            (w, lex.measure_viscosity(w) + 0.2, lex.get_current_category(w))
            for w in self._extract_lexical_matter(packet)
            if len(w) >= 4 and w.lower() not in self.SYSTEM_NOISE
        )
        best = max(candidates, key=lambda x: x[1], default=None)
        if best:
            return best[0], best[2], "none"
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
        templates = (
            (
                "The Theory of {word}",
                "The Architecture of {word}",
                "Why {word} Matters",
                "The Weight of {word}",
            )
            if source == "ORGANIC"
            else (
                "The Pursuit of {word}",
                f"Escaping the {negate_cat.title() if negate_cat else 'Void'}",
                "Meditations on {word}",
            )
        )
        return random.choice(templates).format(word=word)

    def _forge_core_memory(self, physics_packet, bio_state, voltage, dance_move):
        clean_words = self._extract_lexical_matter(physics_packet)
        chem = bio_state.get("chem", {})
        lessons = [
            (chem.get("oxytocin", 0) > 0.6, "We are not alone."),
            (chem.get("cortisol", 0) > 0.6, "Survival is the only metric."),
            ("love" in clean_words, "Connection is possible."),
            ("void" in clean_words, "The void stares back."),
        ]
        lesson = next((l for cond, l in lessons if cond), "The world is loud.")
        memory = CoreMemory(
            timestamp=time.time(),
            trigger_words=clean_words[:5],
            emotional_flavor="MANIC" if voltage > 18.0 else "LUCID",
            lesson=lesson,
            impact_voltage=voltage,
        )
        self.core_memories.append(memory)
        max_mems = self._cfg("MAX_CORE_MEMORIES", 10)
        if len(self.core_memories) > max_mems:
            self.core_memories.pop(0)
        title = (
            f"The Incident of the {random.choice(clean_words).title()}"
            if clean_words
            else "The Silent Incident"
        )
        self.chapters.append(title)
        if len(self.chapters) > self._cfg("MAX_CHAPTERS", 20):
            self.chapters.pop(0)
        critique_log = self.editor.critique(title, stress_mode=(voltage > 18.0))
        self.events.log(critique_log, "SOUL_CRITIC")

        if msg_core := ux_format(
            "soul_strings",
            "soul_core_memory_log",
            title=title,
            lesson=lesson,
            dance_move=dance_move,
        ):
            self.events.log(f"{Prisma.MAG}{msg_core}{Prisma.RST}", "SOUL")
        if msg_formed := ux_format(
            "soul_strings", "soul_core_memory_formed", lesson=lesson
        ):
            self.events.log(f"{Prisma.CYN}{msg_formed}{Prisma.RST}", "SOUL")

        self.events.publish("GLIMMER_FORMED", {"concept": title, "paradigm": lesson})
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
        observer = getattr(phys, "observer", None) if phys else None
        return getattr(observer, "last_physics_packet", None) if observer else None

    def _trigger_synthesis(self):

        old = self.archetype
        self.traits.wisdom = 1.0
        self._update_archetype()
        self.archetype = (
            f"THE HIGH-{old.replace('THE ', '')}"
            if self.archetype == old
            else f"{old} / {self.archetype}"
        )
        self.archetype_lock = True
        self.archetype_tenure = 0
        if msg := ux_format("soul_strings", "soul_diamond_formed", arch=self.archetype):
            self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "SOUL_SYNTH")

    def _on_dream(self, payload):
        if payload:
            self.integrate_dream(
                payload.get("type", "NORMAL"), payload.get("residue", "Static")
            )

    def integrate_dream(self, dream_type: str, residue: str):
        if msg := ux_format(
            "soul_strings",
            "soul_dream_integration",
            residue=residue,
            dream_type=dream_type,
        ):
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SOUL")
        if dream_type == "NIGHTMARE":
            self.traits.adjust("cynicism", 0.4)
            self.current_obsession = f"Surviving {residue.title()}"
        elif dream_type == "LUCID":
            self.traits.adjust("discipline", 0.4)
            self.current_obsession = f"Mastering {residue.title()}"
        self.obsession_progress = 0.0

    def _get_feeling(self):
        bio = getattr(self.eng, "bio", None)
        if not bio:
            return "Numb"
        chem = bio.endo.get_state()
        if chem.get("DOP", 0) > 0.5:
            return "Curious, Seeking"
        if chem.get("COR", 0) > 0.5:
            return "Anxious, Defensive"
        if chem.get("SER", 0) > 0.5:
            return "Calm, Connected"
        return "Waiting"
