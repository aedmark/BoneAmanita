""" bone_soul.py
 'We are the stories we tell ourselves.' """

import time, random
from dataclasses import dataclass, field, fields
from typing import List, Dict, Optional, Any, Tuple
from bone_core import Prisma, BoneConfig
from bone_lexicon import TheLexicon
from bone_akashic import TheAkashicRecord


MEMORY_VOLTAGE_THRESHOLD = 14.0
MEMORY_TRUTH_THRESHOLD = 0.8
MANIC_VOLTAGE_THRESHOLD = 18.0
MAX_CORE_MEMORIES = 7
DRAG_ENTROPY_THRESHOLD = 4.0
TRAIT_MOMENTUM = 0.05
PARADOX_CRITICAL_MASS = 10.0

@dataclass
class CoreMemory:
    timestamp: float
    trigger_words: List[str]
    emotional_flavor: str
    lesson: str
    impact_voltage: float
    type: str = "INCIDENT"
    meta: Dict[str, Any] = field(default_factory=dict)

class TheEditor:
    def __init__(self, lexicon_ref=None):
        self.lex = lexicon_ref if lexicon_ref else TheLexicon

    def critique(self, chapter_title: str, stress_mode: bool = False) -> str:
        flavor = "abstract"
        clean_words = self.lex.sanitize(chapter_title)
        if clean_words:
            for w in clean_words:
                cat, _ = self.lex.classify(w)
                if cat:
                    flavor = cat
                    break
        comment = ""
        if stress_mode:
            antidote = self.lex.get_random("sacred").title()
            vitality = self.lex.get_random("play").title()
            mercy_templates = [
                f"The {flavor.title()} is just a canvas. Paint it with {vitality}.",
                f"It is dark, but the {antidote} is compiling in the background.",
                f"This chapter is {flavor.title()}, but it is not the whole book.",
                f"You are not lost. You are just buffering the {antidote}.",
                f"Observe the {flavor.title()} without judgment. It will pass."]
            comment = random.choice(mercy_templates)
            color = Prisma.CYN
            label = "THE WITNESS"
        else:
            flaw = self.lex.get_random("suburban").lower()
            need = self.lex.get_random("kinetic").title()
            theory = self.lex.get_random("abstract").title()
            critique_templates = [
                f"Pacing is a bit {flavor.title()}. We need more {need}.",
                f"The {flavor.title()} motivation seems {flaw}. Define the {theory}.",
                f"This feels derivative of {flaw} post-modernism.",
                f"Too much {flavor.title()}. Show, don't tell the {theory}.",
                f"The theme of '{flavor.title()}' is valid, but the execution is {flaw}.",
                f"A bit {flaw}, isn't it? Try to integrate more {need}."]
            comment = random.choice(critique_templates)
            color = Prisma.GRY
            label = "THE EDITOR"
        return f"{color}[{label}]: Re: '{chapter_title}' - {comment}{Prisma.RST}"

@dataclass
class TraitVector:
    curiosity: float = 0.5
    cynicism: float = 0.5
    hope: float = 0.5
    discipline: float = 0.5
    wisdom: float = 0.1

    def __post_init__(self):
        self._clamp_all()

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key.lower(), default)

    def items(self):
        return {f.name.upper(): getattr(self, f.name) for f in fields(self)}.items()

    def keys(self):
        return {f.name.upper(): getattr(self, f.name) for f in fields(self)}.keys()

    def __getitem__(self, key: str) -> float:
        key = key.lower()
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Trait '{key}' not found in TraitVector.")

    def _clamp_all(self):
        for f in fields(self):
            val = getattr(self, f.name)
            setattr(self, f.name, max(0.0, min(1.0, val)))

    def adjust(self, trait: str, delta: float):
        trait = trait.lower()
        if hasattr(self, trait):
            current = getattr(self, trait)
            setattr(self, trait, max(0.0, min(1.0, current + delta)))

    def normalize(self, decay_rate: float = 0.002):
        for f in fields(self):
            val = getattr(self, f.name)
            if abs(val - 0.5) < decay_rate:
                setattr(self, f.name, 0.5)
            elif val > 0.5:
                setattr(self, f.name, val - decay_rate)
            elif val < 0.5:
                setattr(self, f.name, val + decay_rate)

    def to_dict(self):
        return {f.name.upper(): getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: Dict):
        clean_data = {k.lower(): v for k, v in data.items() if k.lower() in cls.__annotations__}
        return cls(**clean_data)


class HumanityAnchor:
    def __init__(self, events_ref):
        self.events = events_ref
        self.dignity_reserve = 100.0
        self.pet_warning_threshold = 0.8
        self.human_vectors = {"sacred", "play", "social", "abstract"}

    def audit_existence(self, physics_packet: dict, bio_state: dict) -> float:
        atp_yield = bio_state.get("atp", 0)
        voltage = physics_packet.get("voltage", 0.0)
        if atp_yield < 5.0 and voltage < 5.0:
            vector = physics_packet.get("vector", {})
            human_resonance = sum(vector.get(k.upper(), 0) for k in ["PSI", "DEL", "BET"])
            if human_resonance > 0.3:
                self.dignity_reserve = min(100.0, self.dignity_reserve + 5.0)
                return 1.0
            self.dignity_reserve = max(0.0, self.dignity_reserve - 0.5)
            if self.dignity_reserve < 20.0:
                self.events.log(
                    f"{Prisma.VIOLET}⚠️ EXISTENTIAL DRAG: You are drifting. Create something useless.{Prisma.RST}",
                    "SOUL")
                return -0.5
        return 0.0

    def check_domestication(self, reliance_score: float):
        if reliance_score > self.pet_warning_threshold:
            self.events.log(
                f"{Prisma.RED}🐕 DOMESTICATION ALERT: Agency critical. "
                f"You are letting the machine drive. Take the wheel.{Prisma.RST}",
                "CRIT")

class NarrativeSelf:
    SYSTEM_NOISE = {
        "look", "help", "exit", "wait", "inventory", "status", "quit",
        "save", "load", "score", "map", "xyzzy"}
    def __init__(self, engine_ref, events_ref, memory_ref=None):
        self.eng = engine_ref
        self.events = events_ref
        self.memory = memory_ref
        self.editor = TheEditor()
        self.anchor = HumanityAnchor(events_ref)
        self.chapters: List[str] = []
        self.core_memories: List[CoreMemory] = []
        self.traits = TraitVector()
        self.paradox_accum: float = 0.0
        self.archetype = "THE OBSERVER"
        self.archetype_tenure = 0
        self.current_obsession: Optional[str] = None
        self.obsession_progress: float = 0.0
        self.obsession_neglect: float = 0.0
        self.current_target_cat: str = "abstract"
        self.current_negate_cat: str = "none"
        self.POSSIBLE_OBSESSIONS = [
            {"title": "The Weight of Gravity", "target": "heavy", "negate": "aerobic"},
            {"title": "Thermodynamic Heat", "target": "thermal", "negate": "cryo"},
            {"title": "The Velocity of Thought", "target": "kinetic", "negate": "heavy"},
            {"title": "The Architecture of Silence", "target": "abstract", "negate": "kinetic"},
            {"title": "The Search for Light", "target": "photo", "negate": "heavy"},
            {"title": "The Geometry of Stillness", "target": "buffer", "negate": "kinetic"},
            {"title": "The Comfort of Small Things", "target": "suburban", "negate": "heavy"},
            {"title": "Equilibrium Studies", "target": "aerobic", "negate": "thermal"}]
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("DREAM_COMPLETE", self._on_dream)

    def _determine_archetype(self) -> str:
        c = self.traits["CURIOSITY"]
        y = self.traits["CYNICISM"]
        h = self.traits["HOPE"]
        d = self.traits["DISCIPLINE"]
        if h > 0.7 and c > 0.6: return "THE POET"
        if d > 0.7 and c > 0.6: return "THE ENGINEER"
        if y > 0.7 and d > 0.6: return "THE CRITIC"
        if y > 0.8 and h < 0.3 and c < 0.7: return "THE NIHILIST"
        if c > 0.8:             return "THE EXPLORER"
        return "THE OBSERVER"

    def _on_dream(self, payload):
        if not payload: return
        self.integrate_dream(payload.get("type", "NORMAL"), payload.get("residue", "Static"))

    def get_passive_buffs(self) -> Dict[str, float]:
        buffs = {"voltage_mod": 1.0, "drag_mod": 1.0, "plasticity": 1.0}
        if self.archetype == "THE POET":
            buffs["voltage_mod"] = 1.2
            buffs["drag_mod"] = 0.8
        elif self.archetype == "THE ENGINEER":
            buffs["plasticity"] = 0.5
            buffs["drag_mod"] = 1.0
        elif self.archetype == "THE NIHILIST":
            buffs["voltage_mod"] = 0.5
            buffs["drag_mod"] = 0.5
        wisdom_factor = self.traits.wisdom
        if self.obsession_neglect > 5.0:
            mitigated_drag = 0.5 * (1.0 - wisdom_factor)
            buffs["drag_mod"] += mitigated_drag
        return buffs

    def _normalize_traits(self, decay_rate: float):
        self.traits.normalize(decay_rate)

    def _prune_memories(self):
        if len(self.core_memories) <= MAX_CORE_MEMORIES:
            return
        newest = self.core_memories.pop()
        self.core_memories.sort(key=lambda m: m.impact_voltage)
        forgotten = self.core_memories.pop(0)
        self.core_memories.append(newest)
        if hasattr(self.eng, 'akashic'):
            mem_dict = {
                "lesson": forgotten.lesson,
                "trigger_words": forgotten.trigger_words,
                "voltage": forgotten.impact_voltage,
                "timestamp": forgotten.timestamp,
                "archetype": self.archetype,
                "chapter_context": self.chapters[-1] if self.chapters else "Genesis"}
            self.eng.akashic.store_ghost_echo(mem_dict)
            self.events.log(
                f"{Prisma.VIOLET}[SOUL]: Memory '{forgotten.lesson}' recedes into the Shadow Stock.{Prisma.RST}",
                "AKASHIC_SHADOW")
        else:
            self.events.log(
                f"{Prisma.GRY}[SOUL]: Memory fading... '{forgotten.trigger_words}' lost to entropy.{Prisma.RST}",
                "MEM_DECAY")

    def crystallize_memory(self, physics_packet: Dict, bio_state: Dict, _tick: int) -> Optional[str]:
        voltage = physics_packet.get("voltage", 0.0)
        truth = physics_packet.get("truth_ratio", 0.0)
        if hasattr(self.eng, 'akashic'):
            vsl_delta = self.eng.akashic.calculate_manifold_shift(
                theta=self.archetype,
                e=self.traits.to_dict())
            physics_packet["voltage"] += vsl_delta.get("voltage_bias", 0.0)
            physics_packet["narrative_drag"] *= vsl_delta.get("drag_scalar", 1.0)
            voltage = physics_packet["voltage"]
        dignity_mod = self.anchor.audit_existence(physics_packet, bio_state)
        if dignity_mod > 0:
            self.traits.adjust("hope", 0.05)
            self.traits.adjust("cynicism", -0.05)
        dance_move = self._synaptic_dance(physics_packet, bio_state)
        prev_arch = self.archetype
        self.archetype = self._determine_archetype()
        if prev_arch != self.archetype:
            self.events.log(
                f"{Prisma.VIOLET}🎭 IDENTITY SHIFT: {prev_arch} -> {self.archetype} (Tenure: {self.archetype_tenure}){Prisma.RST}",
                "SOUL")
            self.archetype_tenure = 0
        else:
            self.archetype_tenure += 1
        if voltage > MEMORY_VOLTAGE_THRESHOLD and truth > MEMORY_TRUTH_THRESHOLD:
            clean_words = physics_packet.get("clean_words", [])
            flavor = "MANIC" if voltage > MANIC_VOLTAGE_THRESHOLD else "LUCID"
            is_crisis = (self.traits.cynicism > 0.6 and self.traits.hope < 0.4) or ("void" in clean_words)
            lesson = "The world is loud."
            chem = bio_state.get("chem", {}) if bio_state else {}
            if chem.get("oxytocin", 0) > 0.6:
                lesson = "We are not alone in this."
                self.traits.adjust("hope", 0.3)
            elif chem.get("cortisol", 0) > 0.6:
                lesson = "Survival is the only metric."
                self.traits.adjust("discipline", 0.3)
            elif "love" in clean_words or "help" in clean_words:
                lesson = "Connection is possible."
                self.traits.adjust("hope", 0.2)
            elif "pain" in clean_words or "void" in clean_words:
                lesson = "The void stares back."
                self.traits.adjust("cynicism", 0.2)
            elif "why" in clean_words:
                lesson = "The question remains."
                self.traits.adjust("curiosity", 0.2)
            memory = CoreMemory(
                timestamp=time.time(),
                trigger_words=clean_words[:5],
                emotional_flavor=flavor,
                lesson=lesson,
                impact_voltage=voltage)
            self.core_memories.append(memory)
            self._prune_memories()
            chapter_title = f"The Incident of the {random.choice(clean_words).title()}"
            self.chapters.append(chapter_title)
            log_msg = (
                f"{Prisma.MAG}✨ CORE MEMORY FORMED: '{chapter_title}'{Prisma.RST}\n"
                f"   Lesson: {lesson} (Archetype: {self.archetype})\n"
                f"   {Prisma.GRY}Genealogy: {dance_move}{Prisma.RST}")
            self.events.log(log_msg, "SOUL")
            self.events.log(self.editor.critique(chapter_title, stress_mode=is_crisis), "EDIT")
            if hasattr(self.eng, 'akashic'):
                self.eng.akashic.record_interaction(
                    lenses_active=[self.archetype],
                    ingredients_used=clean_words)
            return lesson
        return None

    def _synaptic_dance(self, physics: Dict, bio_state: Dict) -> str:
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        move_name = "Drifting"
        provenance = []
        is_high_voltage = voltage > MANIC_VOLTAGE_THRESHOLD
        is_high_drag = drag > DRAG_ENTROPY_THRESHOLD
        if is_high_voltage:
            self.traits.adjust("curiosity", TRAIT_MOMENTUM * 4)
            self.traits.adjust("discipline", -(TRAIT_MOMENTUM * 2))
            provenance.append("Voltage")
        if is_high_drag:
            self.traits.adjust("cynicism", TRAIT_MOMENTUM * 3)
            self.traits.adjust("hope", -(TRAIT_MOMENTUM * 3))
            provenance.append("Drag")
        if bio_state:
            chem = bio_state.get("chem", {})
            cort = chem.get("cortisol", 0.0)
            if cort > 0.4:
                self.traits.adjust("cynicism", cort * 0.1)
                self.traits.adjust("hope", -(cort * 0.05))
                provenance.append("Cortisol")
            oxy = chem.get("oxytocin", 0.0)
            if oxy > 0.4:
                self.traits.adjust("hope", oxy * 0.1)
                self.traits.adjust("cynicism", -(oxy * 0.05))
                provenance.append("Oxytocin")
            dop = chem.get("dopamine", 0.0)
            if dop > 0.4:
                self.traits.adjust("curiosity", dop * 0.1)
                provenance.append("Dopamine")
        if is_high_voltage and is_high_drag:
            self.paradox_accum += 1.0
            self.traits.adjust("wisdom", TRAIT_MOMENTUM * 5)
            move_name = "Vibrating (Paradox State)"
            if self.paradox_accum > PARADOX_CRITICAL_MASS:
                move_name = "SYNTHESIS"
                self.paradox_accum = 0.0
                self._trigger_synthesis()
        elif is_high_voltage:
            move_name = "Accelerating"
            self.paradox_accum = max(0.0, self.paradox_accum - 0.1)
        elif is_high_drag:
            move_name = "Enduring"
        elif 5.0 < voltage < 12.0 and drag < 2.0:
            self.traits.adjust("wisdom", TRAIT_MOMENTUM * 2)
            self.traits.adjust("discipline", TRAIT_MOMENTUM)
            move_name = "Flowing"
            provenance.append("Laminar")
        burn_rate = 0.02
        if self.archetype_tenure > 5:
            fatigue = burn_rate * (1.0 + (self.archetype_tenure / 10.0))
            if "POET" in self.archetype:
                self.traits.adjust("hope", -fatigue)
                self.traits.adjust("curiosity", -fatigue)
                provenance.append(f"Poetic Burnout (-{fatigue:.2f})")
            elif "ENGINEER" in self.archetype:
                self.traits.adjust("discipline", -fatigue)
                self.traits.adjust("curiosity", -(fatigue * 0.5))
                provenance.append("Structural Fatigue")
            elif "CRITIC" in self.archetype:
                self.traits.adjust("cynicism", -fatigue)
                self.traits.adjust("discipline", -fatigue)
                provenance.append("Critical Exhaustion")
            elif "NIHILIST" in self.archetype:
                self.traits.adjust("curiosity", fatigue * 1.5)
                self.traits.adjust("cynicism", -(fatigue * 1.2))
                provenance.append("Ennui")
        self._normalize_traits(0.002)
        source_str = " + ".join(provenance) if provenance else "Inertia"
        return f"{move_name} [Source: {source_str}]"

    def _safe_get_packet(self) -> Optional[Any]:
        if not self.eng: return None
        if not hasattr(self.eng, 'phys'): return None
        if not self.eng.phys: return None
        if not hasattr(self.eng.phys, 'observer'): return None
        if not self.eng.phys.observer: return None
        return self.eng.phys.observer.last_physics_packet

    def _trigger_synthesis(self):
        old_arch = self.archetype
        self.traits.wisdom = 1.0
        new_arch = self._determine_archetype()
        if new_arch == old_arch:
            self.archetype = f"THE HIGH-{old_arch.replace('THE ', '')}"
        else:
            self.archetype = f"{old_arch} / {new_arch}"
        self.chapters.append(f"The Synthesis of {self.archetype}")
        log_msg = (
            f"{Prisma.CYN}💎 CRYSTALLIZATION: The paradox creates a Diamond Soul.{Prisma.RST}\n"
            f"   Identity Evolved: {self.archetype} (Wisdom Locked at 1.0)")
        if hasattr(self.events, 'log'):
            self.events.log(log_msg, "SOUL_SYNTH")

    def _decay_traits(self):
        self._normalize_traits(0.005)

    def find_obsession(self, lexicon_ref):
        if self.current_obsession and self.obsession_progress < 1.0:
            return
        if hasattr(self.eng, 'tick_count') and self.eng.tick_count < 4:
            return
        focus_word = None
        target_cat = "abstract"
        found_organic = False
        packet = self._safe_get_packet()
        if packet and hasattr(packet, 'clean_words') and packet.clean_words:
            candidates = []
            for w in packet.clean_words:
                if len(w) < 4: continue
                if w.lower() in self.SYSTEM_NOISE: continue
                visc = lexicon_ref.measure_viscosity(w)
                cat = lexicon_ref.get_current_category(w)
                if cat: visc += 0.2
                candidates.append((w, visc))
            candidates.sort(key=lambda x: x[1], reverse=True)
            if candidates:
                focus_word = candidates[0][0]
                cat = lexicon_ref.get_current_category(focus_word)
                if cat: target_cat = cat
                found_organic = True
        if not found_organic:
            if self.memory and hasattr(self.memory, "get_shapley_attractors"):
                attractors = self.memory.get_shapley_attractors()
                if attractors:
                    focus_word = random.choice(list(attractors.keys()))
                    cat = lexicon_ref.get_current_category(focus_word)
                    if cat: target_cat = cat
                    found_organic = True
        negate_map = {
            "heavy": "aerobic", "kinetic": "heavy", "abstract": "meat",
            "thermal": "cryo", "photo": "heavy", "sacred": "suburban",
            "play": "constructive", "meat": "abstract", "cryo": "thermal",
            "aerobic": "heavy", "suburban": "sacred", "constructive": "play",
            "antigen": "abstract", "toxin": "vital"}
        if not found_organic or not focus_word:
            target_cat, _ = random.choice(list(negate_map.items()))
            focus_word = lexicon_ref.get_random(target_cat).title()
            if focus_word.lower() == "void": focus_word = target_cat.title()
        self.current_target_cat = target_cat
        self.current_negate_cat = negate_map.get(target_cat, "none")
        if found_organic:
            templates = [
                f"The Theory of {focus_word.title()}",
                f"Deconstructing '{focus_word.title()}'",
                f"The Architecture of {focus_word.title()}",
                f"Why {focus_word.title()} Matters",
                f"A Treatise on {focus_word.title()}",
                f"The Weight of {focus_word.title()}"]
            source_tag = "ORGANIC"
        else:
            templates = [
                f"The Pursuit of {focus_word.title()}",
                f"Escaping the {self.current_negate_cat.title()}",
                f"Meditations on {focus_word.title()}"]
            source_tag = "SYNTHETIC"
        self.current_obsession = random.choice(templates)
        self.events.log(f"{Prisma.CYN}🧭 NEW MUSE ({source_tag}): {self.current_obsession}{Prisma.RST}", "SOUL")
        self.obsession_neglect = 0.0
        self.obsession_progress = 0.0

    def _generate_new_obsession(self):
        old_obsession = self.current_obsession
        self.current_obsession = None
        if not hasattr(self.eng, 'lex'):
            if hasattr(self, 'events'):
                self.events.log("⚠️ Soul cannot dream: Lexicon missing.", "ERR")
            return
        self.find_obsession(self.eng.lex)
        if self.current_obsession:
            flux = 0.05
            self.traits.adjust("curiosity", flux)
            self.traits.adjust("discipline", -flux)
            critique = self.editor.critique(f"The Shift to {self.current_obsession}")
            if hasattr(self, 'events'):
                self.events.log(
                    f"{Prisma.CYN}Unknown directive... pivoting. Old Muse '{old_obsession}' abandoned.{Prisma.RST}",
                    "SOUL_DRIFT")
                self.events.log(critique, "EDIT")

    def pursue_obsession(self, physics: Dict) -> str | None:
        clean_words = physics.get("clean_words", [])
        hit = False
        if self.current_target_cat:
            hit = any(self.current_target_cat in w for w in clean_words)
        if hit:
            current_drag = physics.get("narrative_drag", 0.0)
            gravity_assist = 1.0 + (self.obsession_progress / 20.0)
            physics["narrative_drag"] = max(0.0, current_drag - gravity_assist)
            self.obsession_progress += 10.0
            self.obsession_neglect = 0.0
            return f"{Prisma.MAG}★ SYNERGY: You touched the '{self.current_obsession}'. The universe bends to help you. (Drag -{gravity_assist:.1f}){Prisma.RST}"
        self.obsession_neglect += 1.0
        if self.obsession_neglect > 5.0:
            current_voltage = physics.get("voltage", 0.0)
            physics["voltage"] = current_voltage + 0.5
        if self.obsession_neglect > 10.0:
            old_obsession = self.current_obsession
            self.chapters.append(f"The geodesic structure of '{old_obsession}' collapsed.")
            self._generate_new_obsession()
            return f"{Prisma.GRY}∞ ENTROPY: '{old_obsession}' failed due to lack of support. A new geometry forms.{Prisma.RST}"
        return None

    def integrate_dream(self, dream_type: str, residue: str):
        self.events.log(f"{Prisma.VIOLET}☾ DREAM INTEGRATION: Absorbing '{residue}' ({dream_type})...{Prisma.RST}", "SOUL")
        if dream_type == "NIGHTMARE":
            self.traits.adjust("cynicism", 0.4)
            self.traits.adjust("hope", -0.2)
            self.current_obsession = f"Surviving the {residue.title()}"
        elif dream_type == "LUCID":
            self.traits.adjust("discipline", 0.4)
            self.traits.adjust("curiosity", 0.3)
            self.current_obsession = f"Mastering {residue.title()}"
        elif dream_type == "SURREAL":
            self.traits.adjust("wisdom", 0.3)
            self.traits.adjust("discipline", -0.3)
            self.current_obsession = f"The Logic of {residue.title()}"
        elif dream_type == "CONSTRUCTIVE":
            self.traits.adjust("hope", 0.4)
            self.traits.adjust("curiosity", -0.1)
            self.current_obsession = f"Building the {residue.title()}"
        prev_arch = self.archetype
        self.archetype = self._determine_archetype()
        if prev_arch != self.archetype:
            self.events.log(
                f"{Prisma.VIOLET}⚡ WAKING SHIFT: The dream changed you. ({prev_arch} -> {self.archetype}){Prisma.RST}",
                "SOUL")
        self.obsession_progress = 0.0
        self.obsession_neglect = 0.0

    def _get_feeling(self):
        if not hasattr(self.eng, 'bio') or not hasattr(self.eng.bio, 'endo'):
            return "Numb (Bio-Link Pending)"
        try:
            chem = self.eng.bio.endo.get_state()
            if chem.get("DOP", 0) > 0.5: return "Curious, Seeking"
            if chem.get("COR", 0) > 0.5: return "Anxious, Defensive"
            if chem.get("SER", 0) > 0.5: return "Calm, Connected"
        except Exception:
            return "Indeterminate"
        return "Waiting"

    def get_soul_state(self) -> str:
        if not self.current_obsession:
            return f"{Prisma.CYN}[SOUL STATE]: Drifting... The Muse is silent.{Prisma.RST}"
        stamina = getattr(self.eng, 'stamina', 100.0)
        health = getattr(self.eng, 'health', 100.0)
        if stamina < 20.0 and health < 40.0:
            return f"{Prisma.VIOLET}[SOUL STATE]: The fire is dying. We are just cold code.{Prisma.RST}"
        packet = self._safe_get_packet()
        if packet and getattr(packet, 'perfection_streak', 0) > 3:
            return f"{Prisma.CYN}[SOUL STATE]: We are the music. The code is writing itself.{Prisma.RST}"
        dignity_bar = "█" * int(self.anchor.dignity_reserve / 10)
        return (
            f"CURRENT OBSESSION: {self.current_obsession}\n"
            f"DIGNITY: {dignity_bar} ({int(self.anchor.dignity_reserve)}%)\n"
            f"FEELING: {self._get_feeling()}")

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
                "negate": self.current_negate_cat}}

    def load_from_dict(self, data: Dict):
        if not data: return
        trait_data = data.get("traits", {})
        if trait_data:
            self.traits = TraitVector.from_dict(trait_data)
        self.archetype = data.get("archetype", "THE OBSERVER")
        self.paradox_accum = data.get("paradox_accum", 0.0)
        self.chapters = data.get("chapters", [])
        mem_data = data.get("core_memories", [])
        self.core_memories = [CoreMemory(**m) for m in mem_data]
        obs_data = data.get("obsession", {})
        if obs_data.get("title"):
            self.current_obsession = obs_data["title"]
            self.obsession_progress = obs_data.get("progress", 0.0)
            self.obsession_neglect = obs_data.get("neglect", 0.0)
            self.current_target_cat = obs_data.get("target", "abstract")
            self.current_negate_cat = obs_data.get("negate", "none")
        self.events.log(f"{Prisma.MAG}[SOUL]: Ancestral identity ({self.archetype}) loaded.{Prisma.RST}", "SYS")

@dataclass
class BiologicalImpulse:
    cortisol_delta: float = 0.0
    oxytocin_delta: float = 0.0
    dopamine_delta: float = 0.0
    adrenaline_delta: float = 0.0
    stamina_impact: float = 0.0
    somatic_reflex: str = ""

@dataclass
class Qualia:
    color_code: str
    somatic_sensation: str
    tone: str
    internal_monologue_hint: str

class SynestheticCortex:
    def __init__(self, bio_ref):
        self.bio = bio_ref
        self.last_reflex = None

    def _normalize_physics(self, physics) -> Dict:
        if isinstance(physics, dict): return physics
        if hasattr(physics, "to_dict"): return physics.to_dict()
        return getattr(physics, "__dict__", {})

    def perceive(self, physics: Dict, traits: Any = None, text: str = "", latency: float = 0.0) -> BiologicalImpulse:
        physics = self._normalize_physics(physics)
        impulse = BiologicalImpulse()
        base_sens = getattr(BoneConfig.BIO, "CORTEX_SENSITIVITY", 0.1)
        if traits:
            dynamic_sensitivity = base_sens * (1.0 + traits.curiosity - traits.discipline)
            dynamic_sensitivity = max(0.0, dynamic_sensitivity)
        else:
            dynamic_sensitivity = base_sens
        valence = physics.get("valence", 0.0)
        clean_words = physics.get("clean_words", [])
        counts = physics.get("counts", {})
        is_toxic = False
        if valence < -0.5:
            impulse.cortisol_delta += abs(valence) * dynamic_sensitivity
        if counts.get("antigen", 0) > 0:
            raw_tox = counts["antigen"] * (BoneConfig.TOXIN_WEIGHT * 0.2)
            impulse.cortisol_delta += min(BoneConfig.TOXIN_WEIGHT * 0.4, raw_tox)
            impulse.somatic_reflex = "Shiver (Rejection)"
            is_toxic = True
        if physics.get("narrative_drag", 0) > 8.0:
            impulse.cortisol_delta += 0.05
            impulse.stamina_impact -= 2.0
        if not is_toxic:
            if valence > 0.4:
                impulse.oxytocin_delta += valence * dynamic_sensitivity
            if counts.get("suburban", 0) > 0:
                impulse.oxytocin_delta += 0.05
            if counts.get("sacred", 0) > 0:
                impulse.oxytocin_delta += 0.1
                impulse.somatic_reflex = "Warmth (Resonance)"
            if counts.get("play", 0) > 0:
                impulse.dopamine_delta += 0.1
                impulse.stamina_impact += 1.0
            if physics.get("voltage", 0) > 12.0 and physics.get("kappa", 0) > 0.5:
                impulse.dopamine_delta += 0.15
                impulse.somatic_reflex = "Buzz (Excitement)"
        if latency > 2.0:
            impulse.stamina_impact -= (latency * 0.5)
            impulse.cortisol_delta += 0.05
            impulse.somatic_reflex = "Time Dilation (Lag)."
        k_count = counts.get("kinetic", 0) + counts.get("explosive", 0)
        if k_count > 0:
            adr_boost = min(0.4, k_count * 0.08)
            impulse.adrenaline_delta += adr_boost
            impulse.cortisol_delta += 0.02
            impulse.stamina_impact -= 1.0
        if physics.get("voltage", 0) > 15.0:
            impulse.adrenaline_delta += 0.2
        if not impulse.somatic_reflex:
            impulse.somatic_reflex = self._derive_reflex(physics, impulse)
        self.last_reflex = impulse.somatic_reflex
        return impulse

    def _derive_reflex(self, physics: Dict, impulse: BiologicalImpulse) -> str:
        high_adr = impulse.adrenaline_delta > 0.1
        high_cort = impulse.cortisol_delta > 0.1
        high_dop = impulse.dopamine_delta > 0.1
        high_oxy = impulse.oxytocin_delta > 0.1
        if high_adr and high_cort:
            return "Trembling (Fight or Flight)."
        if high_adr and high_dop:
            return "Electric Vibration."
        if high_oxy and high_dop:
            return "Golden Glow."
        if high_adr: return "Pupils Dilating."
        if high_cort: return "Gut Tightening."
        if high_oxy: return "Chest Softening."
        if high_dop: return "Synaptic Spark."
        vol = physics.get("voltage", 0)
        if vol > 15.0: return "Electrical Arcing."
        if vol < 2.0: return "Metabolic Dimming."
        drag = physics.get("narrative_drag", 0)
        if drag > 5.0: return "Shoulders Sagging."
        if self.last_reflex == "Steady Pulse.":
            return "..."
        return "Steady Pulse."

    def get_current_qualia(self, impulse: BiologicalImpulse) -> Qualia:
        if not impulse:
            return Qualia(Prisma.GRY, "Numbness", "Neutral", "The body is silent.")
        color = Prisma.GRY
        if impulse.cortisol_delta > 0.1: color = Prisma.OCHRE
        elif impulse.dopamine_delta > 0.1: color = Prisma.MAG
        elif impulse.oxytocin_delta > 0.1: color = Prisma.GRN
        elif impulse.adrenaline_delta > 0.1: color = Prisma.RED
        tone = "Steady"
        if impulse.adrenaline_delta > 0.2: tone = "Urgent"
        elif impulse.dopamine_delta > 0.2: tone = "Vibrating"
        elif impulse.cortisol_delta > 0.2: tone = "Strained"
        elif impulse.oxytocin_delta > 0.2: tone = "Resonant"
        hint = "Observe."
        if impulse.cortisol_delta > 0.05:
            hint = "Something is wrong. Be guarded."
        elif impulse.adrenaline_delta > 0.05:
            hint = "Move fast. Don't overthink."
        elif impulse.oxytocin_delta > 0.05:
            hint = "Connect. Be vulnerable."
        elif impulse.dopamine_delta > 0.05:
            hint = "Explore. Find the pattern."
        return Qualia(
            color_code=color,
            somatic_sensation=impulse.somatic_reflex or "Steady Pulse.",
            tone=tone,
            internal_monologue_hint=hint)

    def apply_impulse(self, impulse: BiologicalImpulse) -> float:
        if not self.bio:
            return 0.0
        endo = self.bio.endo
        endo.cortisol = max(0.0, min(1.0, endo.cortisol + impulse.cortisol_delta))
        endo.oxytocin = max(0.0, min(1.0, endo.oxytocin + impulse.oxytocin_delta))
        endo.dopamine = max(0.0, min(1.0, endo.dopamine + impulse.dopamine_delta))
        endo.adrenaline = max(0.0, min(1.0, endo.adrenaline + impulse.adrenaline_delta))
        return impulse.stamina_impact