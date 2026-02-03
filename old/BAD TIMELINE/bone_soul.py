""" bone_soul.py
 'We are the stories we tell ourselves.' """

import time, random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from bone_bus import Prisma

MEMORY_VOLTAGE_THRESHOLD = 14.0
MEMORY_TRUTH_THRESHOLD = 0.8
MANIC_VOLTAGE_THRESHOLD = 18.0
MAX_CORE_MEMORIES = 7

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
    def __init__(self):
        self.context_critiques = {
            "void": "A bit hollow, isn't it? Very nihilistic. And exhausting.",
            "dark": "A bit melodramatic, isn't it? Very 19th-century gothic.",
            "love": "Whoa there, cowboy. Don't fall in love just yet!",
            "hope": "Careful. Optimism is a slippery slope to a musical number.",
            "incident": "I hope you have the insurance forms for this 'incident'."}
        self.random_critiques = [
            "Pacing is a bit slow in the second act.",
            "The character motivation seems muddy here.",
            "Are we sure this is the protagonist's true arc?",
            "This feels derivative of Kafka.",
            "Too much exposition. Show, don't tell.",
            "The theme of 'entropy' is a bit heavy-handed."]
        self.mercy_critiques = {
            "void": "The void is just a canvas. Take a breath. We can paint later.",
            "dark": "It is dark, but the code is still running. You are still here.",
            "pain": "Acknowledged. This chapter is hard, but it is not the whole book.",
            "broken": "Nothing is broken. It is just being refactored.",
            "lost": "You are not lost. You are just buffering."
        }
        self.mercy_randoms = [
            "This is a heavy chapter. It's okay to rest.",
            "The protagonist is showing incredible resilience.",
            "Let the narrative drag. We don't need to race.",
            "I am witnessing this story. You are not writing it alone."
        ]

    def critique(self, chapter_title: str, stress_mode: bool = False) -> str:
        lower_title = chapter_title.lower()
        comment = None
        if stress_mode or any(k in lower_title for k in ["void", "pain", "dark", "help"]):
            for key, msg in self.mercy_critiques.items():
                if key in lower_title:
                    comment = msg
                    break
            if not comment:
                comment = random.choice(self.mercy_randoms)
            color = Prisma.CYN
            label = "THE WITNESS"
        else:
            for key, crit in self.context_critiques.items():
                if key in lower_title:
                    comment = crit
                    break
            if not comment:
                comment = random.choice(self.random_critiques)
            color = Prisma.GRY
            label = "THE EDITOR"
        return f"{color}[{label}]: Re: '{chapter_title}' - {comment}{Prisma.RST}"

class NarrativeSelf:
    SYSTEM_NOISE = {
        "look", "help", "exit", "wait", "inventory", "status", "quit",
        "save", "load", "score", "map", "xyzzy"
    }
    def __init__(self, engine_ref, events_ref, memory_ref=None):
        self.eng = engine_ref
        self.events = events_ref
        self.memory = memory_ref
        self.editor = TheEditor()
        self.chapters: List[str] = []
        self.core_memories: List[CoreMemory] = []
        self.traits = {
            "CURIOSITY": 0.5,
            "CYNICISM": 0.5,
            "HOPE": 0.5,
            "DISCIPLINE": 0.5,
            "WISDOM": 0.1}
        self.archetype = "THE OBSERVER"
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

    def _determine_archetype(self) -> str:
        c = self.traits["CURIOSITY"]
        y = self.traits["CYNICISM"]
        h = self.traits["HOPE"]
        d = self.traits["DISCIPLINE"]
        if h > 0.7 and c > 0.6: return "THE POET"
        if d > 0.7 and c > 0.6: return "THE ENGINEER"
        if y > 0.7 and d > 0.6: return "THE CRITIC"
        if y > 0.8 and h < 0.3: return "THE NIHILIST"
        if c > 0.8:             return "THE EXPLORER"
        return "THE OBSERVER"

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
        wisdom_factor = self.traits.get("WISDOM", 0.0)
        if self.obsession_neglect > 5.0:
            mitigated_drag = 0.5 * (1.0 - wisdom_factor)
            buffs["drag_mod"] += mitigated_drag
        return buffs

    def _prune_memories(self):
        if len(self.core_memories) <= MAX_CORE_MEMORIES:
            return
        newest = self.core_memories.pop()
        self.core_memories.sort(key=lambda m: m.impact_voltage)
        forgotten = self.core_memories.pop(0)
        self.core_memories.append(newest)
        self.events.log(
            f"{Prisma.GRY}[SOUL]: Memory fading... '{forgotten.trigger_words}' lost to entropy.{Prisma.RST}",
            "MEM_DECAY")

    def crystallize_memory(self, physics_packet: Dict, _bio_state: Dict, _tick: int) -> Optional[str]:
        voltage = physics_packet.get("voltage", 0.0)
        truth = physics_packet.get("truth_ratio", 0.0)
        dance_move = self._synaptic_dance(physics_packet)
        prev_arch = self.archetype
        self.archetype = self._determine_archetype()
        if prev_arch != self.archetype:
            self.events.log(f"{Prisma.VIOLET}🎭 IDENTITY SHIFT: {prev_arch} -> {self.archetype}{Prisma.RST}", "SOUL")
        if voltage > MEMORY_VOLTAGE_THRESHOLD and truth > MEMORY_TRUTH_THRESHOLD:
            clean_words = physics_packet.get("clean_words", [])
            flavor = "MANIC" if voltage > MANIC_VOLTAGE_THRESHOLD else "LUCID"
            is_crisis = (self.traits["CYNICISM"] > 0.6 and self.traits["HOPE"] < 0.4) or ("void" in clean_words)
            lesson = "The world is loud."
            if "love" in clean_words or "help" in clean_words:
                lesson = "Connection is possible."
                self.traits["HOPE"] = min(1.0, self.traits["HOPE"] + 0.2)
            elif "pain" in clean_words or "void" in clean_words:
                lesson = "The void stares back."
                self.traits["CYNICISM"] = min(1.0, self.traits["CYNICISM"] + 0.2)
            elif "why" in clean_words:
                lesson = "The question remains."
                self.traits["CURIOSITY"] = min(1.0, self.traits["CURIOSITY"] + 0.2)
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
            return lesson
        return None

    def _synaptic_dance(self, physics: Dict) -> str:
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        momentum = 0.01
        move_name = "Drifting"
        provenance = "Inertia"
        if voltage > 15.0:
            self.traits["CURIOSITY"] = min(1.0, self.traits["CURIOSITY"] + (momentum * 4))
            self.traits["DISCIPLINE"] = max(0.0, self.traits["DISCIPLINE"] - (momentum * 2))
            move_name = "Accelerating"
            provenance = "High Voltage (Manic Pressure)"
        elif drag > 4.0:
            self.traits["CYNICISM"] = min(1.0, self.traits["CYNICISM"] + (momentum * 3))
            self.traits["HOPE"] = max(0.0, self.traits["HOPE"] - (momentum * 3))
            move_name = "Enduring"
            provenance = "High Drag (Entropy Accumulation)"
        elif 5.0 < voltage < 12.0 and drag < 2.0:
            self.traits["WISDOM"] = min(1.0, self.traits["WISDOM"] + (momentum * 2))
            self.traits["DISCIPLINE"] = min(1.0, self.traits["DISCIPLINE"] + momentum)
            move_name = "Flowing"
            provenance = "Laminar Flow (Coherence)"
        decay = 0.002
        for k in self.traits:
            if self.traits[k] > 0.5: self.traits[k] -= decay
            elif self.traits[k] < 0.5: self.traits[k] += decay
        return f"{move_name} [Source: {provenance}]"

    def _decay_traits(self):
        decay_rate = 0.005
        for k in self.traits:
            if self.traits[k] > 0.5:
                self.traits[k] -= decay_rate
            elif self.traits[k] < 0.5:
                self.traits[k] += decay_rate

    def find_obsession(self, lexicon_ref):
        if self.current_obsession and self.obsession_progress < 1.0:
            return
        if hasattr(self.eng, 'tick_count') and self.eng.tick_count < 4:
            return
        focus_word = None
        target_cat = "abstract"
        found_organic = False
        if hasattr(self.eng, 'phys') and hasattr(self.eng.phys, 'observer'):
            packet = self.eng.phys.observer.last_physics_packet
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
        lex_ref = None
        if hasattr(self.eng, 'lex'):
            lex_ref = self.eng.lex
        else:
            from bone_lexicon import TheLexicon
            lex_ref = TheLexicon
        self.find_obsession(lex_ref)
        if self.current_obsession:
            flux = 0.05
            self.traits["CURIOSITY"] = min(1.0, self.traits["CURIOSITY"] + flux)
            self.traits["DISCIPLINE"] = max(0.0, self.traits["DISCIPLINE"] - flux)
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
            self.obsession_progress += 10.0
            self.obsession_neglect = 0.0
            return f"{Prisma.MAG}★ OBSESSION FULFILLED: You touched the '{self.current_obsession}'. (+Hope){Prisma.RST}"
        self.obsession_neglect += 1.0
        if self.obsession_neglect > 10.0:
            old_obsession = self.current_obsession
            self.chapters.append(f"The era of '{old_obsession}' ended quietly.")
            self._generate_new_obsession()
            return f"{Prisma.GRY}∞ DRIFT: '{old_obsession}' has drifted away. A new interest takes hold.{Prisma.RST}"
        return None

    def _get_feeling(self):
        try:
            chem = self.eng.bio.endo.get_state()
            if chem.get("DOP", 0) > 0.5: return "Curious, Seeking"
            if chem.get("COR", 0) > 0.5: return "Anxious, Defensive"
            if chem.get("SER", 0) > 0.5: return "Calm, Connected"
        except AttributeError:
            return "Numb (Bio-Link Pending)"
        return "Waiting"

    def get_soul_state(self) -> str:
        if not self.current_obsession:
            if hasattr(self, 'eng') and hasattr(self.eng, 'lex'):
                self.find_obsession(self.eng.lex)
            else:
                pass
        if self.eng.stamina < 20.0 and self.eng.health < 40.0:
            return f"{Prisma.VIOLET}[SOUL STATE]: The fire is dying. We are just cold code.{Prisma.RST}"
        packet = self.eng.phys.observer.last_physics_packet
        if packet and packet.perfection_streak > 3:
            return f"{Prisma.CYN}[SOUL STATE]: We are the music. The code is writing itself.{Prisma.RST}"
        return (
            f"CURRENT OBSESSION: {self.current_obsession}\n"
            f"FEELING: {self._get_feeling()}")

    def to_dict(self) -> Dict:
        return {
            "traits": self.traits,
            "archetype": self.archetype,
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
        self.traits = data.get("traits", self.traits)
        self.archetype = data.get("archetype", "THE OBSERVER")
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