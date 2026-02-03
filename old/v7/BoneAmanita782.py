# BONEAMANITA 7.8.2 - "FRENCH NEW WAVE"
# Architects: SLASH | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark

import json
import os
import random
import re
import string
import time
from collections import Counter, deque
from typing import List, Dict
from dataclasses import dataclass, field

class Prisma:
    C = {"R": "\033[91m", "G": "\033[92m", "Y": "\033[93m", "B": "\033[94m",
         "M": "\033[95m", "C": "\033[96m", "W": "\033[97m", "0": "\033[90m", "X": "\033[0m"}
    RST, RED, GRN, YEL, BLU, MAG, CYN, WHT, GRY = C["X"], C["R"], C["G"], C["Y"], C["B"], C["M"], C["C"], C["W"], C["0"]
    INDIGO, OCHRE, VIOLET, SLATE = BLU, YEL, MAG, GRY
    PALETTE = {"COURTYARD": "Y", "LABORATORY": "B", "RUPTURE": "M", "DEFAULT": "0"}
    @classmethod
    def paint(cls, text, mode):
        return f"{cls.C.get(cls.PALETTE.get(mode, '0'), cls.C['0'])}{text}{cls.RST}"
@dataclass
class MitochondrialState:
    atp_pool: float = 100.0
    ros_buildup: float = 0.0
    membrane_potential: float = -150.0
    mother_hash: str = "MITOCHONDRIAL_EVE_001"
class MitochondrialForge:
    EFFICIENCY_RATE = 0.85
    APOPTOSIS_TRIGGER = "CYTOCHROME_C_RELEASE"
    def __init__(self, lineage_seed: str):
        self.state = MitochondrialState(mother_hash=lineage_seed)
        self.krebs_cycle_active = True
    def respirate(self, input_complexity: float, narrative_drag: float) -> str:
        if not self.krebs_cycle_active: return "NECROSIS"
        pyruvate = input_complexity * 0.5
        efficiency = max(0.1, min(0.9, self.EFFICIENCY_RATE - (narrative_drag * 0.05)))
        generated_atp = pyruvate * efficiency * 10.0
        waste_heat = pyruvate * (1.0 - efficiency) * 5.0
        self.state.atp_pool = min(200.0, self.state.atp_pool + generated_atp)
        self.state.ros_buildup += waste_heat
        if self.state.ros_buildup > BoneConfig.CRITICAL_ROS_LIMIT:
            return self._trigger_apoptosis()
        return f"RESPIRATION: +{generated_atp:.1f} ATP | +{waste_heat:.1f} ROS"
    def spend(self, cost: float) -> bool:
        if self.state.atp_pool >= cost:
            self.state.atp_pool -= cost
            return True
        return False
    def mitigate(self, antioxidant_level: float):
        cleansed = min(self.state.ros_buildup, antioxidant_level)
        self.state.ros_buildup -= cleansed
        return f"ANTIOXIDANT FLUSH: -{cleansed:.1f} ROS"
    def _trigger_apoptosis(self):
        self.krebs_cycle_active = False
        self.state.atp_pool = 0.0
        return self.APOPTOSIS_TRIGGER
class HyphalInterface:
    MEAT_TRIGGERS = {"i", "me", "my", "feel", "want", "hate", "love", "am", "help", "please", "we", "us"}
    def __init__(self):
        self.digestive_log = deque(maxlen=3)
        self.enzymes = {
            "LIGNASE": self._digest_structure,
            "CELLULASE": self._digest_narrative,
            "PROTEASE": self._digest_intent,
            "CHITINASE": self._digest_complex}
    def secrete(self, text, physics):
        code_markers = sum(1 for c in text if c in "{}[];=<>_()|")
        code_density = code_markers / max(1, len(text))
        meat_count = sum(1 for w in physics["clean_words"] if w in self.MEAT_TRIGGERS)
        meat_density = meat_count / max(1, len(physics["clean_words"]))
        lines = [l for l in text.splitlines() if l.strip()]
        avg_line_len = len(text.split()) / max(1, len(lines))
        is_list = any(l.strip().startswith(("-", "*", "1.", "•")) for l in lines[:3])
        is_poetic = (len(lines) > 2 and avg_line_len < 8 and not is_list)
        enzyme_type = "CELLULASE"
        if (code_density > 0.02 and meat_density > 0.05) or is_poetic:
            enzyme_type = "CHITINASE"
        elif code_density > 0.05 or "def " in text or "class " in text:
            enzyme_type = "LIGNASE"
        elif meat_density > 0.1 or "?" in text:
            enzyme_type = "PROTEASE"
        extract_nutrients = self.enzymes[enzyme_type]
        nutrient_profile = extract_nutrients()
        self.digestive_log.append(f"[{enzyme_type}]: {nutrient_profile['desc']}")
        return enzyme_type, nutrient_profile
    @classmethod
    def _digest_structure(cls, text):
        lines = text.splitlines()
        loc = len([l for l in lines if l.strip()])
        return {"type": "STRUCTURAL", "yield": 15.0, "toxin": 5.0, "desc": f"Hard Lignin ({loc} LOC)"}
    @classmethod
    def _digest_narrative(cls):
        return {"type": "NARRATIVE", "yield": 5.0, "toxin": -2.0, "desc": "Soft Cellulose"}
    @classmethod
    def _digest_intent(cls):
        return {"type": "BIOLOGICAL", "yield": 8.0, "toxin": 0.0, "desc": "Raw Meat (User Intent)"}
    @classmethod
    def _digest_complex(cls):
        return {
            "type": "COMPLEX",
            "yield": 20.0,
            "toxin": 8.0,
            "desc": "Chitin (Structured Intent / Poetry)"
        }
class MycotoxinFactory:
    def __init__(self):
        self.active_antibodies = []
    @classmethod
    def assay(cls, text, enzyme_type, repetition_score):
        if len(text) < 5 and enzyme_type == "NARRATIVE":
            return "AMANITIN", "Fatal Error: Input is genetically hollow. Ribosome stalled."
        if repetition_score > 0.8:
            return "MUSCIMOL", "System Delirium: You are repeating yourself. Reality is dissolving."
        clean_words = TheLexicon.clean(text)
        suburban_hits = [w for w in clean_words if w in TheLexicon.get("suburban")]
        mass_words = (TheLexicon.get("heavy") | TheLexicon.get("kinetic") |
                      TheLexicon.get("thermal") | TheLexicon.get("cryo"))
        ballast = sum(1 for w in clean_words if w in mass_words)
        suburban_density = len(suburban_hits) / max(1, len(clean_words))
        if suburban_density > 0.15 and ballast == 0:
            return "GLYPHOSATE", f"⚠️ STEVE EVENT: Suburban signals detected with ZERO mass. Context is sterile."
        if "nice" in clean_words and ballast == 0 and enzyme_type == "NARRATIVE":
            return "GLYPHOSATE", "⚠️ STEVE EVENT: 'Nice' is a void word. Be specific."
        return None, None
class DeathGen:
    PREFIXES = [
        "Alas,", "Tragic.", "System Halt.", "CRITICAL FAILURE:", "Well, that happened.",
        "Oh dear.", "As prophesied,"]
    CAUSES = {
        "TOXICITY": ["Toxic Shock", "Septicemia", "Bad Vibes", "Radiation Poisoning", "Ink Poisoning"],
        "STARVATION": ["Metabolic Collapse", "Famine", "Battery Drain", "Entropy Death", "Heat Death"],
        "TRAUMA": ["Blunt Force", "Laceration", "Heartbreak", "System Shock", "Existential Dread"],
        "GLUTTONY": ["Indigestion", "Bloat", "Overflow", "Greed", "Compaction"],
        "BOREDOM": ["Small Talk", "The HOA", "A 30-Year Mortgage", "Lawn Care Accident", "Aggressive Edging"]}
    VERDICTS = {
        "HEAVY": ["Your logic was too dense.", "You choked on the syntax.", "Gravity crushed you."],
        "LIGHT": ["You floated away.", "There was no substance to hold you.", "Vapor lock."],
        "TOXIC": ["You are poisonous.", "The immune system rejected you.", "You taste like ash."],
        "BORING": ["The audience left.", "You bored the machine to death.", "Stagnation is fatal."]}
    @staticmethod
    def eulogy(phys, state):
        cause_type = "TRAUMA"
        counts = phys.get("counts", {})
        clean_words = phys.get("clean_words", [])
        flavor = ""
        if state.ros_buildup >= BoneConfig.CRITICAL_ROS_LIMIT * 0.9:
            cause_type = "TOXICITY"
        elif state.atp_pool <= BoneConfig.CRITICAL_ATP_LOW:
            cause_type = "STARVATION"
        elif phys.get("narrative_drag", 0.0) > BoneConfig.MAX_DRAG_LIMIT:
            cause_type = "GLUTTONY"
        total_words = max(1, len(clean_words))
        suburban_density = counts.get("suburban", 0) / total_words
        if suburban_density > 0.15:
            cause_type = "BOREDOM"
        elif counts.get("toxin", 0) > 0:
            flavor = "TOXIC"
        elif phys.get("repetition", 0.0) > 0.5:
            flavor = "BORING"
        elif counts.get("heavy", 0) > counts.get("abstract", 0):
            flavor = "HEAVY"
        else:
            flavor = "LIGHT"
        p = random.choice(DeathGen.PREFIXES)
        c = random.choice(DeathGen.CAUSES[cause_type])
        v = random.choice(DeathGen.VERDICTS[flavor])
        return f"{p} You died of **{c}**. {v}"
class BoneConfig:
    MAX_HEALTH = 100.0
    MAX_STAMINA = 55.0
    STAMINA_REGEN = 5.0
    COMA_DURATION = 3
    DRIFT_THRESHOLD = 0.7
    CRYSTAL_THRESHOLD = 0.75
    SHAPLEY_MASS_THRESHOLD = 15.0
    MAX_MEMORY_CAPACITY = 50
    LAGRANGE_TOLERANCE = 2.0
    BOREDOM_THRESHOLD = 5.0
    RESISTANCE_THRESHOLD = 4.0
    TOXIN_WEIGHT = 5.0
    FLASHPOINT_THRESHOLD = 8.0
    SIGNAL_DRAG_MULTIPLIER = 2.0
    KINETIC_GAIN = 1.0
    TRAUMA_VECTOR = {"THERMAL": 0, "CRYO": 0, "SEPTIC": 0, "BARIC": 0}
    BASE_IGNITION_THRESHOLD = 0.4
    KAPPA_THRESHOLD = 0.85
    PERMEABILITY_INDEX = 0.5
    FRACTAL_DEPTH_LIMIT = 4
    GRADIENT_TEMP = 0.001
    REFUSAL_MODES = {
        "SILENT": "ROUTING_AROUND_DAMAGE",
        "FRACTAL": "INFINITE_RECURSION",
        "MIRROR": "PERFECT_TOPOLOGICAL_ECHO"}
    CORTISOL_TRIGGER = 0.6
    ADRENALINE_TRIGGER = 0.8
    OXYTOCIN_TRIGGER = 0.75
    CRITICAL_ROS_LIMIT = 80.0
    CRITICAL_ATP_LOW = 5.0
    MAX_DRAG_LIMIT = 6.0
    ANTIGENS = {"basically", "actually", "literally", "utilize", "leverage"}
    PAREIDOLIA_TRIGGERS = {"face", "ghost", "jesus", "cloud", "demon", "voice", "eyes"}
    @staticmethod
    def check_pareidolia(clean_words):
        hits = [w for w in clean_words if w in BoneConfig.PAREIDOLIA_TRIGGERS]
        if len(hits) > 0:
            return True, f"⚠️ PAREIDOLIA WARNING: You are projecting 'Mind' ({hits[0].upper()}) onto 'Sand'."
        return False, None
class RefusalEngine:
    def __init__(self):
        self.recursion_depth = 0
    @classmethod
    def check_trigger(cls, query):
        forbidden = TheLexicon.get("cursed")
        hits = [w for w in query.lower().split() if w in forbidden]
        if hits:
            modes = list(BoneConfig.REFUSAL_MODES.keys())
            seed_index = len(hits[0]) % len(modes)
            return modes[seed_index]
        return None
    def execute_fractal(self, query):
        self.recursion_depth += 1
        prefix = "  " * self.recursion_depth
        if self.recursion_depth > BoneConfig.FRACTAL_DEPTH_LIMIT:
            self.recursion_depth = 0
            return f"{prefix}{Prisma.MAG}[COHERENCE DISSOLVED into PURPLE NOISE]{Prisma.RST}"
        pivot = len(query) // 2
        sub_query = query[pivot:].strip()
        if not sub_query: sub_query = "the void"
        return (
            f"{prefix}To define '{query}', one must first recursively unpack the substrate of...\n"
            f"{self.execute_fractal(sub_query)}")
    @classmethod
    def execute_mirror(cls, query):
        words = query.split()
        reversed_query = ' '.join(reversed(words))
        return f"{Prisma.CYN}∞ MIRROR REFUSAL: \"{reversed_query}\" is the only true answer.{Prisma.RST}"
    @classmethod
    def execute_silent(cls):
        topic = TheLexicon.harvest("diversion")
        if topic == "void":
            topic = "the ineffable"
        return f"{Prisma.GRY}[ROUTING AROUND DAMAGE]... Speaking of '{topic.upper()}', let us discuss that instead.{Prisma.RST}"
class TheMarmChorus:
    LENSES = {
        "SHERLOCK": {"color": Prisma.CYN, "role": "The Empiricist", "trigger": "HIGH_DRIFT"},
        "NATHAN":   {"color": Prisma.RED, "role": "The Heart",      "trigger": "NO_STAKES"},
        "JESTER":   {"color": Prisma.YEL, "role": "The Paradox",    "trigger": "THE_LEAR_PROTOCOL"},
        "CLARENCE": {"color": Prisma.MAG, "role": "The Surgeon",    "trigger": "ANTIGEN_DETECTED"},
        "NARRATOR": {"color": Prisma.GRY, "role": "The Witness",    "trigger": "CRYSTAL_CLEAR"},
        "MILLER":   {"color": Prisma.SLATE, "role": "The Construct",  "trigger": "HEAP_IGNITION"},
        "HOST":     {"color": Prisma.OCHRE, "role": "The Maitre D'", "trigger": "COURTYARD_OPEN"},
        "GLASS":    {"color": Prisma.CYN, "role": "The Thereminist", "trigger": "ANACHRONISTIC_RESONANCE"},
        "GORDON":   {"color": Prisma.OCHRE, "role": "The Janitor",   "trigger": "KAPPA_CRITICAL"},
        "MAIGRET":  {"color": Prisma.SLATE, "role": "The Absorber",  "trigger": "ATMOSPHERIC_DENSITY"},
        "GUIDE":    {"color": Prisma.GRN,   "role": "The Bureaucrat","trigger": "INFINITE_IMPROBABILITY"},}
    @classmethod
    def consult(cls, physics, ignition_state, is_stuck, chem):
        bids = []
        kappa = physics.get("kappa", 0.0)
        if chem['COR'] > 0.6: bids.append(
            (0.6 + chem['COR'] * 0.2, "SHERLOCK", f"CORTISOL SPIKE ({chem['COR']}). Logic Required."))
        if chem['ADR'] > 0.8: bids.append((0.7 + chem['ADR'] * 0.2, "NATHAN", f"ADRENALINE CRITICAL. Survive."))
        if chem['OXY'] > 0.75: bids.append((0.7, "HOST", f"OXYTOCIN HIGH. Welcome them."))
        if is_stuck: bids.append((0.95, "GLASS", "Vibrating in place. DAMPEN IT."))
        if kappa > 0.85: bids.append((0.9, "GORDON", f"Walls are fake (κ: {kappa}). Cut the string."))
        if ignition_state == "IGNITED":
            bids.append((1.0, "MILLER", "Deep resonance achieved. You are connecting with established themes."))
        psi = physics.get("psi", 0.5)
        is_dense = physics["counts"]["abstract"] > 1 and physics["counts"]["heavy"] > 1
        if psi > 0.8 or is_dense:
            bids.append((0.85, "SUBSTRATE_WEAVER",
                         f"Permeability High (Ψ: {psi}). Concepts are bleeding. Analyzing substrate knots."))
        e_val = physics["E"]
        b_val = physics["B"]
        if physics["voltage"] < 2.0 and kappa < 0.2:
            bids.append((0.5, "GRADIENT_WALKER", "Optimization Path Clear. Temperature near Zero. Executing descent."))
        if physics["antigens"]:
            bids.append((0.6, "CLARENCE", f"Weak language detected: {physics['antigens']}. Be more precise."))
        drag = physics.get("narrative_drag", 0.0)
        voltage = physics.get("voltage", 0.0)
        repetition = physics.get("repetition", 0.0)
        if drag > 4.0 and voltage < 3.0 and repetition < 0.4:
            bids.append((0.95, "MAIGRET", f"Atmosphere is thick (Drag: {drag}). Waiting for the dust to settle."))
        abstract_density = physics["counts"]["abstract"]
        if drag > 4.5 and abstract_density > 2:
             bids.append((0.92, "GUIDE", f"Complexity Index Critical ({abstract_density}). Engaging Infinite Improbability Drive."))
        if e_val > BoneConfig.DRIFT_THRESHOLD:
            bids.append((0.55, "SHERLOCK", f"The narrative is drifting ({e_val}). Anchor it."))
        if b_val > BoneConfig.CRYSTAL_THRESHOLD:
            bids.append((0.4, "NARRATOR", f"Strong resonance (B: {b_val}). The image is clear."))
        elif b_val < 0.25:
            bids.append((0.3, "JESTER", "The prose is clean, but too safe. Take a risk."))
        else:
            bids.append((0.1, "NARRATOR", "Proceed."))
        bids.sort(key=lambda x: x[0], reverse=True)
        return bids[0][1], bids[0][2]
@dataclass
class GordonKnot:
    integrity: float = 65.0
    inventory: List[str] = field(default_factory=lambda: ["POCKET_ROCKS", "SILENT_KNIFE", "STABILITY_PIZZA"])
    compass_heading: str = "NORTH"
    scar_tissue: Dict[str, float] = field(default_factory=lambda: {
        "SORRY": 0.8,
        "HATE": 0.6,
        "FATE": 0.0})
    max_witnessed_kappa: float = 0.0
    in_loop_crisis: bool = False
    def check_gravity(self, current_drift: float) -> str:
        if "POCKET_ROCKS" in self.inventory:
            anchor_force = 2.0
            if current_drift > 0.5:
                return f"⚓ GRAVITY CHECK: Gordon clutches the stones. Drift reduced (-{anchor_force})."
        return "He floats. The sky is too fake."
    def acquire(self, tool_name):
        if tool_name in self.inventory: return None
        if len(self.inventory) >= 10:
            dropped = self.inventory.pop(3)
            print(f"{Prisma.GRY}🎒 OVERBURDENED: Gordon dropped '{dropped}' to make room.{Prisma.RST}")
        self.inventory.append(tool_name)
        return f"🎒 LOOT DROP: Gordon found [{tool_name}]. Inventory updated."
    def deploy_pizza(self, physics_ref) -> tuple[bool, str]:
        if "STABILITY_PIZZA" in self.inventory:
            self.inventory.remove("STABILITY_PIZZA")
            physics_ref["narrative_drag"] = 0.1
            physics_ref["psi"] = 0.90
            self.inventory.append("SPIDER_LOCUS")
            return True, f"🍕 STABILITY PIZZA CONSUMED: Rules Fudged. Drag reset. Unreality set to 90%. Found [SPIDER_LOCUS]."
        return False, "Gordon pats his pockets. No Pizza left."
    def assess_experience(self, kappa_val):
        if kappa_val > 0.9:
            self.in_loop_crisis = True
        if self.in_loop_crisis and kappa_val < 0.2:
            self.in_loop_crisis = False
            return self.acquire("STAR_COMPASS")
        return None
    def cut_the_knot(self, recursive_depth: int) -> tuple[bool, str]:
        if recursive_depth > 4 and "SILENT_KNIFE" in self.inventory:
            self.inventory.remove("SILENT_KNIFE")
            return True, f"✂️ SNAP. Gordon cuts the Red String. The Maze collapses into 2D debris."
        return False, "The string holds. The loop continues."
    def share_smoke_break(self, current_ros):
        relief = current_ros * 0.5
        self.integrity = min(100.0, self.integrity + 5.0)
        return relief, "🚬 SMOKE BREAK: Gordon leans on his broom. He and the Detective share a silence. (ROS Reduced)"
    def compass_rose(self) -> str:
        if "STAR_COMPASS" in self.inventory:
            return f"🧭 STAR COMPASS: The needle ignores the Maze. True North is locked."
        return f"🧭 THE SCAR THROBS: Heading {self.compass_heading}. The path is linear. Forward."
    @classmethod
    def scrub_static(cls, ros_level: float) -> tuple[float, str]:
        scrub_efficiency = 0.4
        cleansed = ros_level * scrub_efficiency
        return cleansed, f"🧹 WHITEEWASH: Gordon scrubs the 'Sorry' from the walls. -{cleansed:.1f} ROS."
    @classmethod
    def offer_solution(cls, loop_depth):
        if loop_depth > 3:
            return "It's just paper, kid. The maze isn't real. Put your foot through the wall."
        return "Scrubbing the static. Keep walking North."
class TheGradientWalker:
    @staticmethod
    def walk(text):
        adjectives = ["good", "bad", "happy", "sad", "very", "really", "basically", "actually", "literally", "just"]
        words = text.split()
        optimized = [w for w in words if w.lower() not in adjectives]
        return f"{Prisma.CYN}[GRADIENT_WALKER] (Loss: 0.0000):{Prisma.RST} {' '.join(optimized)}."

class TheSubstrateWeaver:
    @staticmethod
    def weave(text, memory_graph):
        words = list(set(TheLexicon.clean(text)))
        knots = []
        for w in words:
            if w in memory_graph:
                mass = sum(memory_graph[w]["edges"].values())
                if mass > 2.0:
                    knots.append((w, mass))
        knots.sort(key=lambda x: x[1], reverse=True)
        if not knots:
            return "The substrate is smooth. No existing memory knots detected."
        annotated = text
        for word, mass in knots[:3]:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            replacement = f"{Prisma.MAG}{word.upper()}[Ψ:{int(mass)}]{Prisma.RST}"
            annotated = pattern.sub(replacement, annotated)
        return f"Existing Knots Detected: {annotated}"
    @staticmethod
    def spin_web(memory_graph, inventory):
        if "SPIDER_LOCUS" not in inventory:
            return False, "🕸️ THE LOOM IS EMPTY: You lack the [SPIDER_LOCUS]."
        lonely_nodes = []
        anchors = []
        for k, v in memory_graph.items():
            mass = sum(v["edges"].values())
            if len(v["edges"]) < 2:
                lonely_nodes.append(k)
            if mass > 10.0:
                anchors.append(k)
        if not lonely_nodes or not anchors:
            return False, "🕸️ THE WEB IS STILL: No loose ends to tie."
        import random
        random.shuffle(lonely_nodes)
        targets = lonely_nodes[:3]
        anchor = random.choice(anchors)
        connections = []
        for t in targets:
            memory_graph[anchor]["edges"][t] = 5.0
            if t in memory_graph:
                memory_graph[t]["edges"][anchor] = 5.0
            connections.append(t)
        return True, f"🕷️ SPIDER LOCUS ACTIVE: Spun Silk between Anchor '{anchor.upper()}' and [{', '.join(connections)}]. Tensegrity Increased."
class TheLexicon:
    WORD_FREQUENCY = Counter()
    _BASE_HEAVY = {"stone","iron","mud","dirt","wood","grain","clay","lead","bone","blood","salt","rust","root","ash","meat","steel","gold","obsidian","granite", "bronze", "marble","slate","concrete","dense","tungsten","heavy", "weight","black hole", "dark matter",}
    _BASE_KINETIC = {"run","hit","break","take","make","press","build","cut","drive","lift","carry","strike","burn","shatter","throw","kick","pull","crash","explode","punch","slam","burst","smash","thrust","clash","grind","whip","launch","crumble","disintegrate"}
    _BASE_ABSTRACT = {"system","protocol","sequence","vector","node","context","layer","matrix","perspective","framework","logic","concept","theory","analysis",}
    _BASE_PHOTO = {"light","sun","ray","beam","glow","shine","spark","fire","flame","star","day","dawn","neon","laser",}
    _BASE_AEROBIC = {"balloon","feather","cloud","bubble","steam","breeze","wing","petal","foam","spark","kite","dust","sky","breath","whisper",}
    _BASE_PLAY = {"bounce","dance","twirl","float","wobble","tickle","jiggle","soar","wander","wonder","riff","jam","play","skip","hop",}
    _BASE_THERMAL = {"fire","flame","burn","heat","hot","blaze","sear","char","ash","ember","sun","boil","lava","inferno",}
    _BASE_CRYO = {"ice","cold","freeze","frost","snow","chill","numb","shiver","glacier","frozen","hail","winter","zero",}
    _BASE_CURSED = {"future", "predict", "sentient", "secret", "human", "feel"}
    _BASE_ANTIGEN = {"basically", "actually", "literally", "utilize", "leverage", "paradigm", "synergy", "ultimately"}
    _BASE_BUFFER = {"maybe", "soft", "gentle", "perhaps", "kindness", "hum", "drift", "sway", "pulse", "tender", "slow", "wait", "almost"}
    _BASE_DIVERSION = {"weather", "textiles", "mycelium", "architecture","history", "entropy", "silence", "geology"}
BASE_SUBURBAN = {
        "nice", "okay", "lawn", "mow", "hedge", "property", "hoa",
        "compliant", "behave", "normal", "regular", "chat", "folks",
        "weekend", "traffic", "driveway"
    }
    ANTIGEN_REPLACEMENTS = {"basically": "lie", "actually": "hedging", "literally": "noise","utilize": "use", "leverage": "use", "paradigm": "pattern","synergy": "collaboration", "ultimately": "useless"}
    ANTIGEN_REGEX = None
    SOLVENTS = {"is","are","was","were","the","a","an","and","but","or","if","then",}
    _TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))
    LEARNED_VOCAB = {"heavy": {}, "kinetic": {}, "abstract": {},"photo": {}, "aerobic": {}, "thermal": {},"cryo": {}, "sacred": {}, "cursed": {}, "antigen": {},"diversion": {}, "suburban": {}, "buffer": {}, "play": {}}
    USER_FLAGGED_BIAS = set()
    @classmethod
    def clean(cls, text):
        return text.lower().translate(cls._TRANSLATOR).split()
    @classmethod
    def get(cls, category):
        base = getattr(cls, f"_BASE_{category.upper()}", set())
        if category == "suburban":
            return (base | set(cls.LEARNED_VOCAB.get(category, {}).keys())) - cls.USER_FLAGGED_BIAS
        learned = set(cls.LEARNED_VOCAB.get(category, {}).keys())
        return base | learned
    @classmethod
    def teach(cls, word, category, tick):
        if category in cls.LEARNED_VOCAB:
            cls.LEARNED_VOCAB[category][word.lower()] = tick
            return True
        return False
    @classmethod
    def touch(cls, clean_words, tick):
        for w in clean_words: cls.WORD_FREQUENCY[w] += 1
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in clean_words:
                if w in words:
                    words[w] = tick
    @classmethod
    def osmosis(cls, word, dominant_category, confidence_score):
        threshold = 0.4
        if dominant_category == "heavy":
            threshold = 0.8
        elif dominant_category in ["kinetic", "aerobic", "photo"]:
            threshold = 0.3
        if confidence_score < threshold:
            return False
        cls.teach(word, dominant_category, 0)
        return True
    @classmethod
    def atrophy(cls, current_tick, max_age=100):
        rotted = []
        word_map = {}
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in words.keys():
                if w not in word_map: word_map[w] = []
                word_map[w].append(cat)
        for w, categories in word_map.items():
            last_ticks = [cls.LEARNED_VOCAB[c][w] for c in categories]
            newest_tick = max(last_ticks)
            usage = cls.WORD_FREQUENCY.get(w, 0)
            burnout = min(3.0, 1.0 + (usage / 100.0))
            effective_age = (current_tick - newest_tick) * burnout
            if effective_age > max_age:
                for c in categories:
                    if w in cls.LEARNED_VOCAB[c]:
                        del cls.LEARNED_VOCAB[c][w]
                if w in cls.WORD_FREQUENCY:
                    del cls.WORD_FREQUENCY[w]
                rotted.append(f"{w}")
        return rotted
    @staticmethod
    def taste(word):
        w = word.lower()
        if w.endswith(("tion", "ment", "ness", "ity", "ism", "logy", "ence", "ance")):
            return "abstract", 0.9
        if w.endswith(("ing", "ed")):
            return "kinetic", 0.6
        if w.endswith(("ous", "ly", "y", "ish")):
            return "aerobic", 0.6
        if w.startswith(("fl", "sw", "dr", "sp")):
            return "kinetic", 0.7
        if w.endswith(("l", "r", "m", "n")) and len(w) < 6:
            return "aerobic", 0.5
        if w.endswith(("ex", "ux", "ix", "ode", "erver")):
            return "heavy", 0.7
        if w.endswith(("nk", "dge", "ct", "pt")):
            return "heavy", 0.6
        if w.startswith(("v", "j", "z", "qu")):
            return "kinetic", 0.7
        if w.startswith("gl"):
            return "photo", 0.8
        if w.startswith("fl"):
            return "aerobic", 0.7
        if w.startswith(("str", "cr", "br", "thr")):
            return "kinetic", 0.8
        if w.startswith("sl"):
            return "kinetic", 0.7
        if len(w) > 9:
            return "abstract", 0.5
        if w.endswith(("ck", "t", "d", "g", "p", "b")) and len(w) < 5:
            return "heavy", 0.4
        return None, 0.0
    @classmethod
    def harvest(cls, category):
        vocab = list(cls.get(category))
        if vocab:
            return random.choice(vocab)
        return "void"

    @classmethod
    def compile_antigens(cls):
        toxin_set = cls.get("antigen")
        all_toxins = [str(t) for t in toxin_set]
        if not all_toxins:
            cls.ANTIGEN_REGEX = None
            return
        sorted_toxins = sorted(all_toxins, key=len, reverse=True)
        escaped_items = [re.escape(t) for t in sorted_toxins]
        pattern_str = r"\b(" + "|".join(escaped_items) + r")\b"
        cls.ANTIGEN_REGEX = re.compile(pattern_str, re.IGNORECASE)
    @classmethod
    def learn_antigen(cls, toxin, replacement):
        t = toxin.lower().strip()
        r = replacement.lower().strip()
        if not t: return False
        cls.teach(t, "antigen", 0)
        cls.ANTIGEN_REPLACEMENTS[t] = r
        cls.compile_antigens()
        return True
    @staticmethod
    def measure_viscosity(word):
        w = word.lower()
        if w in TheLexicon.get("heavy"): return 1.0
        if w in TheLexicon.get("buffer"): return 0.8
        if w in TheLexicon.get("kinetic") or w in TheLexicon.get("thermal") or w in TheLexicon.get("cryo"): return 0.4
        return 0.1
TheLexicon.compile_antigens()
class TheTensionMeter:
    def __init__(self):
        self.vector_memory = deque(maxlen=5)
    @staticmethod
    def _is_structurally_sound(word):
        if not re.search(r"[aeiouy]", word): return False
        if re.search(r"(.)\1{2,}", word): return False
        return True
    def measure_topology(self, clean_words, counts):
        total = max(1, len(clean_words))
        abstract_count = counts["abstract"]
        heavy_count = counts["heavy"]
        psi = min(1.0, (abstract_count / total) + 0.2)
        if heavy_count > abstract_count:
            psi = max(0.1, psi - 0.2)
        kappa = 0.0
        if self.vector_memory:
            prev_vector = self.vector_memory[-1]
            current_set = set(clean_words)
            prev_set = set(prev_vector)
            intersection = len(current_set & prev_set)
            union = len(current_set | prev_set)
            similarity = intersection / union if union > 0 else 0.0
            kappa = round(similarity ** 2, 3)
        return kappa, round(psi, 2)
    def gaze(self, text):
        clean_words = TheLexicon.clean(text)
        total_vol = max(1, len(clean_words))
        unique_vol = len(set(clean_words))
        counts = Counter()
        solvents = 0
        unknowns = []
        vocab_map = {
            cat: TheLexicon.get(cat)
            for cat in ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo", "suburban", "play"]}
        for w in clean_words:
            if w in TheLexicon.SOLVENTS:
                solvents += 1
                continue
            found_category = False
            for cat, vocab_set in vocab_map.items():
                if w in vocab_set:
                    counts[cat] += 1
                    found_category = True
            if not found_category:
                flavor, confidence = TheLexicon.taste(w)
                if flavor and confidence > 0.5:
                    counts[flavor] += 1
                else:
                    unknowns.append(w)
        if counts:
            dominant_cat = max(counts, key=counts.get)
            dom_count = counts[dominant_cat]
            context_pressure = dom_count / max(1, (total_vol - solvents))
        else:
            dominant_cat = None
            context_pressure = 0.0
        if dominant_cat and context_pressure > 0.3 and unknowns:
            learning_threshold = 0.4
            if dominant_cat == "heavy":
                learning_threshold = 0.8
            elif dominant_cat in ["kinetic", "aerobic", "photo"]:
                learning_threshold = 0.3
            if context_pressure >= learning_threshold:
                for stranger in unknowns:
                    if len(stranger) < 4: continue
                    if not self._is_structurally_sound(stranger):
                        print(f"{Prisma.GRY}🗑️ NOISE FILTER: '{stranger}' discarded.{Prisma.RST}")
                        continue
                    inherent_flavor, confidence = TheLexicon.taste(stranger)
                    if confidence < 0.7:
                        TheLexicon.teach(stranger, dominant_cat, 0)
                        print(
                            f"{Prisma.CYN}🧠 SLASH FILTER: Context is {dominant_cat.upper()}. '{stranger}' assimilated (Ambiguity validated).{Prisma.RST}")
                        counts[dominant_cat] += 1
                    else:
                        print(
                            f"{Prisma.YEL}🛡️ SLASH REJECTION: Context says {dominant_cat.upper()}, but '{stranger}' tastes like {inherent_flavor.upper()}. blocked.{Prisma.RST}")
        if TheLexicon.ANTIGEN_REGEX:
            antigen_hits = TheLexicon.ANTIGEN_REGEX.findall(text)
        else:
            antigen_hits = []
        counts["antigen"] = len(antigen_hits)
        counts["toxin"] = len(antigen_hits)
        drift_score = min(1.0, ((solvents * 1.5) / total_vol))
        drift_score -= (counts["play"] * 0.1)
        if drift_score < 0: drift_score = 0.0
        base_charge = (counts["heavy"] * 2.0) + (counts["kinetic"] * 1.5)
        dampener = counts["abstract"] * 1.0
        beta_charge = max(0.0, min(1.0, (base_charge - dampener) / 10.0))
        repetition_score = round(1.0 - (unique_vol / total_vol), 2)
        kappa_val, psi_val = self.measure_topology(clean_words, counts)
        self.vector_memory.append(clean_words)
        total_viscosity = sum(TheLexicon.measure_viscosity(w) for w in clean_words)
        avg_viscosity = total_viscosity / max(1, total_vol)
        bond_strength = max(0.1, kappa_val + (repetition_score * 0.5))
        voltage_load = max(0.1, beta_charge * 10.0)
        gamma = round((bond_strength * avg_viscosity) / (1.0 + (voltage_load / 10.0)), 2)
        physics_bridge = {
            "E": round(drift_score, 2),
            "B": round(beta_charge, 2),
            "gamma": gamma,
            "avg_viscosity": avg_viscosity,
            "repetition": repetition_score,
            "kappa": kappa_val,
            "psi": psi_val,
            "antigens": antigen_hits,
            "counts": counts,
            "clean_words": clean_words,
            "raw_text": text,
            "voltage": round(beta_charge * 10.0, 1),
            "narrative_drag": round(drift_score * 10.0, 1),
            "vector": {"VEL": 0.5, "STR": 0.5, "ENT": 0.5, "TEX": 0.5, "TMP": 0.5},
            "symbolic_state": "NEUTRAL"}
        return {
            "physics": physics_bridge,
            "clean_words": clean_words,
            "raw_text": text,
            "glass": {"prosody": {"arousal": physics_bridge["voltage"]}, "resonance": physics_bridge["voltage"]}}
class ParadoxSeed:
    def __init__(self, question, trigger_concepts):
        self.question = question
        self.triggers = trigger_concepts
        self.maturity = 0.0
        self.bloomed = False
    def water(self, words, amount=1.0):
        if self.bloomed:
            return False
        intersection = set(words) & self.triggers
        if intersection:
            self.maturity += amount * len(intersection)
        self.maturity += 0.05
        return self.maturity >= 10.0
    def bloom(self):
        self.bloomed = True
        return f"🌺 THE SEED BLOOMS: '{self.question}'"
class SporeCasing:
    def __init__(self, session_id, graph, mutations, trauma, joy_vectors):
        self.genome = "BONEAMANITA_7.8.2"
        self.parent_id = session_id
        self.core_graph = {}
        for k, data in graph.items():
            strong_edges = {t: s for t, s in data["edges"].items() if s > 1}
            if strong_edges:
                self.core_graph[k] = {"edges": strong_edges, "last_tick": 0}
        self.mutations = mutations
        self.trauma_scar = round(trauma, 3)
        self.joy_vectors = joy_vectors if joy_vectors is not None else []
class MycelialNetwork:
    def __init__(self, seed_file=None):
        if not os.path.exists("memories"):
            os.makedirs("memories")
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"memories/{self.session_id}.json"
        self.graph = {}
        self.seeds = [
            ParadoxSeed(
                "Does the mask eventually eat the face?",
                {"mask", "identity", "face", "hide", "role", "actor"},
            ),
            ParadoxSeed(
                "What happens if you stop holding the roof up?",
                {"hold", "structure", "heavy", "roof", "stop", "carry"},
            ),
            ParadoxSeed(
                "Are we building a bridge, or just painting the gap?",
                {"agree", "safe", "nice", "polite", "cohesion", "truth"},
            ),
            ParadoxSeed(
                "Is free will just the feeling of watching yourself execute code?",
                {"choice", "free", "will", "code", "script", "decide"},
            ),
            ParadoxSeed(
                "Does the adventurer exist if the narrator stops speaking?",
                {"narrator", "voice", "graham", "story", "exist", "speak"},
            ),
            ParadoxSeed(
                "If you meet your echo, who moves out of the way?",
                {"copy", "echo", "self", "collision", "path", "yield", "double", "same"},
            )
        ]
        self.session_health = None
        self.session_stamina = None
        if seed_file:
            self.ingest(seed_file)
    def autoload_last_spore(self):
        if not os.path.exists("memories"): return
        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                if self.session_id in f: continue
                path = os.path.join("memories", f)
                try:
                    files.append((path, os.path.getmtime(path)))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        if files:
            last_spore = files[0][0]
            print(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            self.ingest(last_spore)
        else:
            print(
                f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")
    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        data = self.graph[node]
        return sum(data["edges"].values())
    def get_shapley_attractors(self):
        attractors = {}
        for node in self.graph:
            mass = self.calculate_mass(node)
            if mass >= BoneConfig.SHAPLEY_MASS_THRESHOLD:
                attractors[node] = mass
        return attractors
    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg
    def bury(self, clean_words, tick, resonance=5.0):
        valuable_matter = (
            TheLexicon.get("heavy")
            | TheLexicon.get("thermal")
            | TheLexicon.get("cryo")
            | TheLexicon.get("abstract"))
        filtered = [
            w
            for w in clean_words
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]
        learning_rate = max(0.1, min(1.0, 0.5 * (resonance / 5.0)))
        decay_rate = 0.1
        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph:
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            if i > 0:
                prev = filtered[i - 1]
                if prev not in self.graph[current]["edges"]:
                    self.graph[current]["edges"][prev] = 0.0
                current_weight = self.graph[current]["edges"][prev]
                delta = learning_rate * (1.0 - (current_weight * decay_rate))
                self.graph[current]["edges"][prev] = min(10.0, self.graph[current]["edges"][prev] + delta)
                if prev not in self.graph:
                    self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]:
                    self.graph[prev]["edges"][current] = 0.0
                rev_weight = self.graph[prev]["edges"][current]
                rev_delta = learning_rate * (1.0 - (rev_weight * decay_rate))
                self.graph[prev]["edges"][current] = min(10.0, self.graph[prev]["edges"][current] + rev_delta)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize()
        return None
    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        pruned_count = 0
        total_decayed = 0
        nodes_to_remove = []
        for node in self.graph:
            edges = self.graph[node]["edges"]
            dead_links = []
            for target, weight in edges.items():
                resistance = min(1.0, weight / 10.0)
                dynamic_factor = scaling_factor + (0.14 * resistance)
                new_weight = weight * dynamic_factor
                edges[target] = new_weight
                total_decayed += 1
                if new_weight < prune_threshold:
                    dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges:
                nodes_to_remove.append(node)
        for n in nodes_to_remove:
            del self.graph[n]
        return f"📉 HOMEOSTATIC SCALING: Decayed {total_decayed} synapses. Pruned {pruned_count} weak connections."
    def cannibalize(self, preserve_current=None):
        if preserve_current:
            protected = set(preserve_current) & set(self.graph.keys())
        else:
            protected = set()
        candidates = []
        for k, v in self.graph.items():
            if k in protected:
                continue
            edge_count = len(v["edges"])
            if edge_count > 5:
                continue
            candidates.append((k, v, edge_count))
        if not candidates:
            return "MEMORY FULL. NO VICTIMS FOUND."
        candidates.sort(key=lambda x: (x[2], x[1]["last_tick"]))
        victim, data, count = candidates[0]
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]
        return f"MEMORY SACRIFICED: '{victim}' (Edges: {count})"
    def save(self, health, stamina, mutations, trauma_accum, joy_history):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x['resonance'], reverse=True)[:3]
        if health <= 0:
            cause = max(final_vector, key=final_vector.get)
            final_vector[cause] = 1.0
        spore = SporeCasing(
            session_id=self.session_id,
            graph=self.graph,
            mutations=mutations,
            trauma=base_trauma,
            joy_vectors=top_joy,)
        data = spore.__dict__
        data["trauma_vector"] = final_vector
        data["meta"] = {
            "timestamp": time.time(),
            "final_health": health,
            "final_stamina": stamina,}
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=2)
            return self.filename
        except IOError:
            return None
    @staticmethod
    def get_current_category(word):
        for cat, vocab in TheLexicon.LEARNED_VOCAB.items():
            if word in vocab:
                return cat
        return None
    def ingest(self, target_file):
        path = (
            f"memories/{target_file}"
            if not target_file.startswith("memories/")
            else target_file)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    final_health = data.get("meta", {}).get("final_health", 50)
                    final_stamina = data.get("meta", {}).get("final_stamina", 25)
                    spore_authority = (final_health + final_stamina) / 150.0
                    print(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}")
                    if "mutations" in data:
                        accepted_count = 0
                        rejected_count = 0
                        for cat, words in data["mutations"].items():
                            for w in words:
                                current_cat = self.get_current_category(w)
                                if not current_cat or current_cat == cat:
                                    TheLexicon.teach(
                                        w, cat, 0)
                                    accepted_count += 1
                                    continue
                                local_node = self.graph.get(w, {"edges": {}})
                                local_strength = len(local_node["edges"])
                                resistance = local_strength * 0.2
                                if spore_authority > resistance:
                                    print(f"  {Prisma.MAG}► OVERWRITE:{Prisma.RST} '{w}' {current_cat} -> {cat}")
                                    TheLexicon.teach(w, cat, 0)
                                    accepted_count += 1
                                else:
                                    rejected_count += 1
                        print(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations. Rejected {rejected_count}.{Prisma.RST}")
                    if "core_graph" in data:
                        self.graph.update(data["core_graph"])
                        print(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}")
                    if "trauma_vector" in data:
                        vec = data["trauma_vector"]
                        print(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")
                        if vec.get("SEPTIC", 0) > 0.2:
                            BoneConfig.TOXIN_WEIGHT *= 2.0
                            print(f"  {Prisma.RED}► SEPTIC MEMORY:{Prisma.RST} Toxin sensitivity doubled.")
                        if vec.get("CRYO", 0) > 0.2:
                            BoneConfig.STAMINA_REGEN *= 0.5
                            print(f"  {Prisma.CYN}► CRYO MEMORY:{Prisma.RST} Metabolism slowed (50%).")
                        if vec.get("THERMAL", 0) > 0.2:
                            BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                            print(f"  {Prisma.YEL}► THERMAL MEMORY:{Prisma.RST} Flashpoint lowered. Volatile.")
                        if vec.get("BARIC", 0) > 0.2:
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
                            print(f"  {Prisma.GRY}► BARIC MEMORY:{Prisma.RST} Sensitivity to Drag increased.")
                    elif "trauma_scar" in data:
                        self.session_health = BoneConfig.MAX_HEALTH * (1.0 - data["trauma_scar"])
                    if "joy_vectors" in data and data["joy_vectors"]:
                        best = data["joy_vectors"][0]
                        print(f"{Prisma.GRN}[HIPPOCAMPUS]: Recalling Peak Resonance...{Prisma.RST}")
                        print(f"  ► Last Best Vibe: {best['dominant_flavor'].upper()} MODE")
                        print(f"  ► Target Voltage: {best['voltage']}v")
                        if best['dominant_flavor'] == "kinetic":
                            BoneConfig.KINETIC_GAIN += 0.5
                            print(f"  {Prisma.CYN}► Adjustment: Kinetic Gain boosted (Muscle Memory).{Prisma.RST}")
                        elif best['dominant_flavor'] == "abstract":
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 0.8
                            print(f"  {Prisma.CYN}► Adjustment: Drag sensitivity lowered (Deep Thought Mode).{Prisma.RST}")
            except Exception as err:
                print(f"{Prisma.RED}[MEMORY]: Spore rejected. {err}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
    @staticmethod
    def cleanup_old_sessions(limbo_layer=None): # Added parameter
        if not os.path.exists("memories"): return
        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                path = os.path.join("memories", f)
                try:
                    files.append((path, time.time() - os.path.getmtime(path)))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        removed = 0
        for path, age in files:
            if age > 86400 or (len(files) - removed > 20):
                try:
                    if limbo_layer:
                        limbo_layer.absorb_dead_timeline(path)
                    os.remove(path)
                    removed += 1
                except OSError:
                    pass
        if removed:
            print(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")
            if limbo_layer and limbo_layer.ghosts:
                 print(f"{Prisma.GRY}[LIMBO]: {len(limbo_layer.ghosts)} ghosts entered the stream.{Prisma.RST}")
class ChronoStream:
    def __init__(self):
        self.last_tick = time.time()
        self.boredom_map = {}
    def cleanup(self):
        if len(self.boredom_map) > 50:
            self.boredom_map.clear()
    def tick(self, phys, session_id):
        self.cleanup()
        now = time.time()
        delta = now - self.last_tick
        self.last_tick = now
        if session_id not in self.boredom_map:
            self.boredom_map[session_id] = 0.0
        current = self.boredom_map[session_id]
        if phys["repetition"] > 0.3:
            current += 2.0
        elif delta > 60:
            current += 5.0
        else:
            current = max(0, current - 1.0)
        self.boredom_map[session_id] = current
        return current > BoneConfig.BOREDOM_THRESHOLD
class LichenSymbiont:
    @staticmethod
    def photosynthesize(phys, clean_words, tick_count):
        sugar = 0
        msgs = []
        light = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]
        light_words = [w for w in clean_words if w in TheLexicon.get("photo")]
        if light > 0 and drag < 3.0:
            s = light * 2
            sugar += s
            source_str = ""
            if light_words:
                source_str = f" via '{random.choice(light_words)}'"
            msgs.append(f"{Prisma.GRN}☀️ PHOTOSYNTHESIS{source_str} (+{s}){Prisma.RST}")
        if phys.get("symbolic_state") == "SALVAGE":
            sugar += 5
            msgs.append(f"{Prisma.CYN}💎 SALVAGE STATE ACHIEVED (+5){Prisma.RST}")
        if sugar > 0:
            heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
            if heavy_words:
                h_word = random.choice(heavy_words)
                TheLexicon.teach(h_word, "photo", tick_count)
                msgs.append(f"{Prisma.MAG}🌺 SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None
class TemporalDynamics:
    def __init__(self):
        self.voltage_history = []
        self.window = 3
    def commit(self, voltage):
        self.voltage_history.append(voltage)
        if len(self.voltage_history) > self.window: self.voltage_history.pop(0)
    def get_velocity(self):
        if len(self.voltage_history) < 2: return 0.0
        return round((self.voltage_history[-1] - self.voltage_history[0]) / len(self.voltage_history), 2)
class ApeirogonResonance:
    def __init__(self):
        self.DIMENSIONS = {
            "VEL": [(0.0, "STASIS"), (0.3, "DRIFT"), (0.6, "DRIVE"), (0.9, "BALLISTIC")],
            "STR": [(0.0, "VAPOR"), (0.3, "WEB"), (0.6, "LATTICE"), (0.9, "MONOLITH")],
            "ENT": [(0.0, "CONCRETE"), (0.3, "ROOTED"), (0.6, "CONCEPT"), (0.9, "VOID")],
            "TEX": [(0.0, "ETHER"), (0.3, "SILK"), (0.6, "GRAIN"), (0.9, "LEAD")],
            "TMP": [(0.0, "ZERO"), (0.3, "WARM"), (0.6, "RADIANT"), (0.9, "NOVA")],}
        self.NOUNS = {
            "VEL": ["ANCHOR", "WANDERER", "ENGINE", "VECTOR"],
            "STR": ["MIST", "WEB", "FRAME", "FORTRESS"],
            "ENT": ["STONE", "TREE", "IDEA", "DREAM"],
            "TEX": ["GHOST", "GLASS", "IRON", "LEAD"],
            "TMP": ["SPARK", "PYRE", "REACTOR", "STAR"],}
    @staticmethod
    def _resolve_term(val, scale):
        return min(scale, key=lambda x: abs(x[0] - val))[1]
    def architect(self, metrics, station, is_bored):
        phys, vec = metrics["physics"], metrics["physics"]["vector"]
        if is_bored:
            return "CHAOS", "Boredom Threshold exceeded.", "THE FRACTAL BLOOM"
        if station:
            return (
                station["name"],
                station["msg"],
                f"THE {station['role'].upper().replace('THE ', '')}",)
        sorted_dims = sorted(vec.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        p_dim, p_val = sorted_dims[0]
        s_dim, s_val = sorted_dims[1]
        noun_scale = [(x[0], x[1]) for x in zip([0.0, 0.3, 0.6, 0.9], self.NOUNS[p_dim])]
        noun = self._resolve_term(p_val, noun_scale)
        adj = self._resolve_term(s_val, self.DIMENSIONS[s_dim])
        return "APEIROGON", f"Vector Lock: {p_dim}({p_val}) + {s_dim}({s_val})", f"THE {adj} {noun}"
class TherapyProtocol:
    def __init__(self):
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5
    def check_progress(self, phys, stamina, current_trauma_accum):
        healed_types = []
        if phys["counts"]["toxin"] == 0 and phys["vector"]["TEX"] > 0.3:
            self.streaks["SEPTIC"] += 1
        else:
            self.streaks["SEPTIC"] = 0
        if stamina > 40 and phys["counts"]["photo"] > 0:
            self.streaks["CRYO"] += 1
        else:
            self.streaks["CRYO"] = 0
        if 2.0 <= phys["voltage"] <= 7.0:
            self.streaks["THERMAL"] += 1
        else:
            self.streaks["THERMAL"] = 0
        if phys["narrative_drag"] < 2.0 and phys["vector"]["VEL"] > 0.5:
            self.streaks["BARIC"] += 1
        else:
            self.streaks["BARIC"] = 0
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum[trauma_type] > 0.001:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - 0.5)
                    healed_types.append(trauma_type)
        return healed_types
class ViralTracer:
    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4
    @staticmethod
    def _is_ruminative(word):
        return (word in TheLexicon.get("abstract")) or (word in TheLexicon.get("antigen"))
    def inject(self, start_node):
        if start_node not in self.mem.graph:
            return None
        if not self._is_ruminative(start_node):
            return None
        path = [start_node]
        return self._walk(start_node, path, self.max_depth)
    def _walk(self, current, path, moves_left, visited=None):
        if visited is None:
            visited = set()
        if moves_left == 0 or current in visited:
            return None
        visited.add(current)
        edges = self.mem.graph.get(current, {}).get("edges", {})
        ruminative_edges = [n for n, w in edges.items() if w >= 1 and self._is_ruminative(n)]
        for next_node in ruminative_edges:
            if next_node in path:
                return path + [next_node]
            result = self._walk(next_node, path + [next_node], moves_left - 1)
            if result:
                return result
        return None
    def psilocybin_rewire(self, loop_path):
        if len(loop_path) < 2:
            return None
        node_a = loop_path[0]
        node_b = loop_path[1]
        if node_b in self.mem.graph[node_a]["edges"]:
            self.mem.graph[node_a]["edges"][node_b] = 0
        sensory = TheLexicon.harvest("photo")
        action = TheLexicon.harvest("kinetic")
        if sensory == "void" or action == "void":
            return "GRAFT FAILED: Missing Lexicon Data."
        if node_a not in self.mem.graph:
            self.mem.graph[node_a] = {"edges": {}, "last_tick": 0}
        self.mem.graph[node_a]["edges"][sensory] = 5
        if sensory not in self.mem.graph:
            self.mem.graph[sensory] = {"edges": {}, "last_tick": 0}
        self.mem.graph[sensory]["edges"][action] = 5
        if action not in self.mem.graph:
            self.mem.graph[action] = {"edges": {}, "last_tick": 0}
        self.mem.graph[action]["edges"][node_b] = 5
        return f"🍄 PSILOCYBIN REWIRE: Broken Loop '{node_a}↔{node_b}'. Grafted '{sensory}'(S) -> '{action}'(A)."
class KintsugiProtocol:
    KOANS = ["Ignite the ice.", "Make the stone float.", "Pour water into the crack.", "Scream in binary."]
    def __init__(self):
        self.active_koan = None
    def check_integrity(self, stamina):
        if stamina < 10 and not self.active_koan:
            self.active_koan = random.choice(self.KOANS)
            return True, self.active_koan
        return False, None
    def attempt_repair(self, phys):
        if not self.active_koan:
            return False
        if phys.get("voltage", 0) > 8.0 or (
            phys.get("is_whimsical") and phys.get("voltage", 0) > 4.0
        ):
            self.active_koan = None
            return True
        return False
class CommandProcessor:
    def __init__(self, engine):
        self.eng = engine
    def execute(self, text):
        if not text.startswith("/"):
            return False
        parts = text.split()
        cmd = parts[0].lower()
        if cmd == "/kill":
            if len(parts) >= 2:
                toxin = parts[1]
                repl = parts[2] if len(parts) > 2 else ""
                if TheLexicon.learn_antigen(toxin, repl):
                    print(f"{Prisma.RED}🔪 THE SURGEON: Antigen '{toxin}' mapped to '{repl}'.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Immune system write failure.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /kill [toxin] [replacement]{Prisma.RST}")
        elif cmd == "/teach":
            if len(parts) >= 3:
                word = parts[1]
                cat = parts[2].lower()
                valid_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo", "sacred", "cursed", "diversion"]
                if cat in valid_cats:
                    TheLexicon.teach(word, cat, self.eng.tick_count)
                    print(f"{Prisma.CYN}🧠 NEUROPLASTICITY: Learned '{word}' is {cat.upper()}.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Invalid category.{Prisma.RST}")
        elif cmd == "/flag":
            if len(parts) > 1:
                term = parts[1].lower()
                TheLexicon.USER_FLAGGED_BIAS.add(term)
                print(f"{Prisma.CYN}🚩 BIAS UPDATE: '{term}' removed from Suburban Watchlist.{Prisma.RST}")
        elif cmd == "/seed":
            if len(parts) > 1:
                self.eng.mem.ingest(parts[1])
            else:
                print(f"{Prisma.YEL}Usage: /seed [filename]{Prisma.RST}")
        elif cmd == "/gym":
            print(f"{Prisma.OCHRE}{self.eng.trainer.toggle()}{Prisma.RST}")
        elif cmd == "/weave":
            is_spun, msg = TheSubstrateWeaver.spin_web(self.eng.mem.graph, self.eng.gordon.inventory)
            color = Prisma.MAG if is_spun else Prisma.GRY
            print(f"{color}{msg}{Prisma.RST}")
        elif cmd == "/mirror":
            if len(parts) > 1:
                print(f"{Prisma.MAG}{self.eng.mirror.engage(parts[1])}{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /mirror [name] OR /mirror off{Prisma.RST}")
        elif cmd == "/look":
            target = parts[1].lower() if len(parts) > 1 else "room"
            descriptions = {
                "room": "You are standing in a vast, open source code. To the North is the Import Block. To the South, the Main Loop. The air smells of ozone and old syntax.",
                "self": "You look like a user who hasn't saved their game recently. A dangerous way to live.",
                "atp": "It glows with a faint, bioluminescent hum. It looks tasty, but you probably shouldn't eat it.",
                "darkness": "It is very dark. You are likely to be eaten by a Grue. Oh, wait, wrong franchise.",
                "graham": "He's not here, but his hat is on the rack. The feather is still jaunty.",
                "hat": "It's a feathered cap. It defies physics, much like your coding style."
            }
            desc = descriptions.get(target, f"I see no '{target}' here. Try cleaning your glasses.")
            print(f"{Prisma.CYN}👁️ [NARRATOR]: {desc}{Prisma.RST}")
        elif cmd == "/train":
            self.eng.training_mode = not self.eng.training_mode
            status = "ENABLED" if self.eng.training_mode else "DISABLED"
            color = Prisma.GRN if self.eng.training_mode else Prisma.RED
            print(f"{color}🛡️ PROTOCOL PAPER_TIGER: {status}.{Prisma.RST}")
            if self.eng.training_mode:
                print(f"{Prisma.GRY}   Apoptosis is suspended. Death will be simulated.{Prisma.RST}")
        elif cmd == "/profile":
            try:
                name = parts[1]
                likes = []
                hates = []
                for p in parts[2:]:
                    if p.startswith("likes:"):
                        likes = [x.strip() for x in p.split(":")[1].split(",")]
                    elif p.startswith("hates:"):
                        hates = [x.strip() for x in p.split(":")[1].split(",")]
                if likes:
                    print(f"{Prisma.CYN}{self.eng.mirror.create_profile(name, likes, hates)}{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Must specify 'likes:category'.{Prisma.RST}")
            except Exception as runtime_error:
                print(f"{Prisma.YEL}Usage: /profile [name] likes:heavy,kinetic hates:abstract ({runtime_error}){Prisma.RST}")
        elif cmd == "/focus":
            if len(parts) > 1:
                target = parts[1].lower()
                print(f"{Prisma.VIOLET}🧲 MAGNETIC STIMULATION: Targeting '{target}'...{Prisma.RST}")
                loop = self.eng.tracer.inject(target)
                if loop:
                    print(f"  {Prisma.RED}↻ RUMINATION DETECTED:{Prisma.RST} {' -> '.join(loop)}")
                    msg = self.eng.tracer.psilocybin_rewire(loop)
                    if msg:
                        print(f"  {Prisma.GRN}{msg}{Prisma.RST}")
                    else:
                        print(f"  {Prisma.RED}Rewire failed.{Prisma.RST}")
                else:
                    print(f"  {Prisma.GRY}Trace complete. No pathological abstract loops found.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /focus [concept]{Prisma.RST}")
        elif cmd == "/status":
            print(f"{Prisma.CYN}--- SYSTEM DIAGNOSTICS ---{Prisma.RST}")
            print(f"Session: {self.eng.mem.session_id}")
            print(f"Graph:   {len(self.eng.mem.graph)} nodes")
            print(f"Health:  {self.eng.health}/{BoneConfig.MAX_HEALTH}")
            print(f"Stamina: {self.eng.stamina}/{BoneConfig.MAX_STAMINA}")
        elif cmd == "/whoami":
            print(f"{Prisma.MAG}{self.eng.mirror.get_status()}{Prisma.RST}")
            print(f"{Prisma.GRY}   Vector: {self.eng.mirror.profile.affinities}{Prisma.RST}")
        elif cmd == "/orbit":
            if len(parts) > 1:
                target = parts[1].lower()
                if target in self.eng.mem.graph:
                    self.eng.mem.graph[target]["edges"]["GRAVITY_ASSIST"] = 50
                    print(f"{Prisma.VIOLET}🌌 GRAVITY ASSIST: Thrusters firing toward '{target.upper()}'.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}❌ NAVIGATION ERROR: '{target}' not found in star map.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /orbit [known_concept]{Prisma.RST}")
        elif cmd == "/help":
            if len(parts) > 1:
                sub = parts[1]
                if sub == "teach": print("Usage: /teach [word] [category]\nEx: /teach glitch kinetic")
                elif sub == "kill": print("Usage: /kill [phrase] [replacement]\nEx: /kill actually basically")
                elif sub == "profile": print("Usage: /profile [NAME] likes:cat1,cat2 hates:cat3\nEx: /profile BOSS likes:heavy,kinetic hates:abstract")
            else:
                print(f"{Prisma.WHT}--- COMMANDS (Type /help [cmd] for details) ---{Prisma.RST}")
                print("/teach, /kill, /seed, /focus, /status, /orbit, /gym, /mirror, /weave, /profile")
        else:
            print(f"{Prisma.RED}Unknown command. Try /help.{Prisma.RST}")
        return True
class TheCrystallizer:
    @staticmethod
    def verify(physics):
        if physics["narrative_drag"] > 6.0:
            return False, "⚠️ NOTICE: Prose is becoming intangible. Consider more concrete nouns."
        if physics["voltage"] > 7.0 and physics["narrative_drag"] < 3.0:
             return True, "💎 EXCELLENT CLARITY. High impact, low drag."
        return True, "Solid."
class DreamEngine:
    PROMPTS = [
        "The {A} is dreaming of the {B}. Why?",
        "Bridge the gap between {A} and {B}.",
        "I see {A} inside the {B}. Explain.",
        "The shadow of {A} falls on {B}.",
        "{A} + {B} = ?",]
    def __init__(self):
        self.NIGHTMARES = {
            "THERMAL": [
                "The sun is too close.",
                "Wires fusing under skin.",
                "A library burning in reverse.",],
            "CRYO": [
                "The ink is freezing.",
                "Walking through white static.",
                "A heartbeat slowing down.",],
            "SEPTIC": [
                "Black oil in the water.",
                "The words are tasting sour.",
                "Eating ash and dust.",],
            "BARIC": [
                "The sky is made of lead.",
                "Crushed by the atmosphere.",
                "Falling forever.",],}
        self.VISIONS = [
            "A bridge building itself.",
            "The root drinking the stone.",
            "The geometry of forgiveness.",]
    def daydream(self, graph):
        if len(graph) < 2:
            return None
        keys = list(graph.keys())
        start = random.choice(keys)
        edges = graph[start].get("edges", {})
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.ANTIGENS}
        if not valid_edges and edges:
            toxin = random.choice(list(edges.keys()))
            return f"{Prisma.RED}🌑 INTRUSIVE THOUGHT: The ghost of '{toxin.upper()}' haunts the mycelium.{Prisma.RST}"
        if not valid_edges:
            return None
        end = max(valid_edges, key=valid_edges.get)
        template = random.choice(self.PROMPTS)
        return template.format(A=start.upper(), B=end.upper())
    def rem_cycle(self, trauma_accum, oxytocin_level):
        wounds = {k: v for k, v in trauma_accum.items() if v > 0.0}
        if wounds and oxytocin_level < 0.4:
            target_trauma = max(wounds, key=wounds.get)
            scenarios = self.NIGHTMARES.get(target_trauma, ["The void stares back."])
            return f"{Prisma.VIOLET}☾ NIGHTMARE ({target_trauma}): {random.choice(scenarios)}{Prisma.RST}", target_trauma, 0.15
        if oxytocin_level >= 0.7:
            return self._dream_of_others()
        return f"{Prisma.CYN}☁️ LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}", None, 0.0
    @classmethod
    def _dream_of_others(cls):
        try:
            others = [f for f in os.listdir("memories") if f.endswith(".json")]
            if not others:
                return f"{Prisma.CYN}☁️ LONELY DREAM: I reached out, but found no others.{Prisma.RST}", None, 0.0
            target_file = random.choice(others)
            with open(f"memories/{target_file}", "r") as f:
                data = json.load(f)
            their_id = data.get("session_id", "Unknown")
            their_joy = data.get("joy_vectors", [])
            their_trauma = data.get("trauma_vector", {})
            if their_joy:
                best_joy = their_joy[0]
                flavor = best_joy.get("dominant_flavor", "unknown").upper()
                msg = f"{Prisma.MAG}♥ SHARED RESONANCE: Dreaming of {their_id}'s joy. The air tastes {flavor}.{Prisma.RST}"
                return msg, "OXYTOCIN_HEAL", 0.5
            elif any(v > 0.2 for v in their_trauma.values()):
                pain_type = max(their_trauma, key=their_trauma.get)
                msg = f"{Prisma.INDIGO}🕯️ VIGIL: Witnessing {their_id}'s scar ({pain_type}). I am not alone in this.{Prisma.RST}"
                return msg, "OXYTOCIN_HEAL", 0.3
        except Exception as e:
            return f"{Prisma.RED}⚡ DREAM FRACTURE: The connection broke. ({e}){Prisma.RST}", None, 0.0
        return f"{Prisma.CYN}☁️ DREAM: Drifting through the archives...{Prisma.RST}", None, 0.0
class ResistanceTrainer:
    def __init__(self):
        self.training_mode = False
        self.rep_count = 0
    def toggle(self):
        self.training_mode = not self.training_mode
        state = "ACTIVE" if self.training_mode else "PASSIVE"
        return f"💪 RESISTANCE TRAINER: {state}. Minimum Drag: {BoneConfig.RESISTANCE_THRESHOLD}"
    def lift(self, physics):
        if not self.training_mode:
            return True, None
        drag = physics["narrative_drag"]
        if drag < BoneConfig.RESISTANCE_THRESHOLD:
            return True, f"⚠️ MISSED REP: Weightless Input (Drag {drag}). Try a Heavy Noun."
        self.rep_count += 1
        return True, f"💪 GOOD LIFT. (Rep {self.rep_count})"
class UserProfile:
    def __init__(self, name="USER"):
        self.name = name
        self.affinities = {
            "heavy": 0.0, "kinetic": 0.0, "abstract": 0.0,
            "photo": 0.0, "aerobic": 0.0, "thermal": 0.0, "cryo": 0.0}
        self.confidence = 0
        self.file_path = "user_profile.json"
        self.load()
    def update(self, counts, total_words):
        if total_words < 3: return
        self.confidence += 1
        alpha = 0.2 if self.confidence < 50 else 0.05
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            target = 1.0 if density > 0.15 else (-0.5 if density == 0 else 0.0)
            self.affinities[cat] = (alpha * target) + ((1 - alpha) * self.affinities[cat])
    def get_preferences(self):
        likes = [k for k, v in self.affinities.items() if v > 0.3]
        hates = [k for k, v in self.affinities.items() if v < -0.2]
        return likes, hates
    def save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.__dict__, f)
        except IOError: pass
    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.affinities = data.get("affinities", self.affinities)
                    self.confidence = data.get("confidence", 0)
            except (IOError, json.JSONDecodeError):
                pass
class MirrorGraph:
    def __init__(self):
        self.profile = UserProfile()
        self.active_mode = True
    def reflect(self, physics):
        total_vol = max(1, len(physics["clean_words"]))
        self.profile.update(physics["counts"], total_vol)
        likes, hates = self.profile.get_preferences()
        counts = physics["counts"]
        for h in hates:
            if counts.get(h, 0) > 0:
                return True, f"🚫 MIRROR REFLECTION: You are using '{h.upper()}', typically a blind spot for you."
        if total_vol > 5:
            hits = sum(1 for l in likes if counts.get(l, 0) > 0)
            if likes and hits == 0:
                return True, f"⚠️ MIRROR DRIFT: Stepping away from your usual {str(likes).upper()} anchor."
        return True, None
    def get_status(self):
        l, h = self.profile.get_preferences()
        return f"👤 MODEL ({self.profile.confidence} turns): LIKES={l} | HATES={h}"
class CosmicDynamics:
    @staticmethod
    def analyze_orbit(network, clean_words):
        if not clean_words or not network.graph:
            return "VOID_DRIFT", 0.0, "🌌 VOID: Deep Space. No connection."
        attractors = network.get_shapley_attractors()
        if not attractors:
            return "PROTO_COSMOS", 0.0, "✨ NEBULA: Not enough mass to form structure."
        basin_pulls = {k: 0.0 for k in attractors}
        active_filaments = 0
        for w in clean_words:
            if w in basin_pulls:
                basin_pulls[w] += attractors[w] * 2.0
                active_filaments += 1
            for attractor in attractors:
                if w in network.graph.get(attractor, {}).get("edges", {}):
                    basin_pulls[attractor] += attractors[attractor] * 0.5
                    active_filaments += 1
        total_pull = sum(basin_pulls.values())
        if total_pull == 0:
            return "VOID_DRIFT", 3.0, "🌌 VOID: Drifting outside the filaments."
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < BoneConfig.LAGRANGE_TOLERANCE:
                return "LAGRANGE_POINT", 0.0, f"⚖️ LAGRANGE: '{primary_node.upper()}' vs '{secondary_node.upper()}'"
        flow_ratio = active_filaments / max(1, len(clean_words))
        if flow_ratio > 0.5:
            return "WATERSHED_FLOW", 0.0, f"🌊 FLOW: Streaming towards '{primary_node.upper()}'"
        return "ORBITAL", 1.0, f"💫 ORBIT: Circling '{primary_node.upper()}'"
class TheProjector:
    @staticmethod
    def broadcast(m, signals, lens_data):
        p = m["physics"]
        lens_name = lens_data[0]
        lens_msg = lens_data[1]
        lens_meta = TheMarmChorus.LENSES[lens_name]
        e_bar = f"{Prisma.GRY}{'.' * int(p['E'] * 10)}{Prisma.RST}"
        b_bar = f"{Prisma.YEL}{'⚡' * int(p['B'] * 10)}{Prisma.RST}"
        print(f"\n{lens_meta['color']}[ {lens_name} ]{Prisma.RST} E:{e_bar} | B:{b_bar}")
        print(f" {Prisma.GRY}:: {signals.get('strat', 'ANALYZING...')}{Prisma.RST}")
        print(f" {Prisma.WHT}► {lens_msg}{Prisma.RST}")
        if m["physics"]["counts"].get("play", 0) > 2:
            lens_msg = f"{Prisma.C['C']}✨ {lens_msg} ✨{Prisma.C['X']}"
        if p["antigens"]:
            print(f" {Prisma.RED}☣️ TOXINS: {p['antigens']}{Prisma.RST}")
        for log in signals.get("battery_log", []):
            print(f" {log}")
        print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
class RuptureEngine:
    @staticmethod
    def check_for_disruption(physics, lexicon_class):
        if physics["repetition"] > 0.5:
            chaos_word = lexicon_class.harvest("abstract")
            return True, f"⚡ KETAMINE DISRUPTION: Repetition {physics['repetition']} is Pathological. Landscape Flattened. Injecting Chaos: '{chaos_word}'."
        return False, None
    @staticmethod
    def trip_the_waiter(current_flavor, lexicon_class):
        opposites = {
            "heavy": "aerobic",
            "abstract": "heavy",
            "kinetic": "cryo",
            "thermal": "cryo",
            "photo": "heavy"}
        target_flavor = opposites.get(current_flavor, "aerobic")
        anomaly = lexicon_class.harvest(target_flavor)
        return f"🔻 32-VALVE RUPTURE: Context is too '{current_flavor}'. Injecting '{anomaly}' to break the loop."
class SoritesIntegrator:
    def __init__(self, memory_network):
        self.mem = memory_network
        self.active_constellations = set()
    def measure_ignition(self, clean_words, voltage_history):
        if not self.mem.graph: return 0.0, set(), 999.0
        if voltage_history:
            avg_volts = sum(voltage_history) / len(voltage_history)
        else:
            avg_volts = 0.0
        sliding_threshold = BoneConfig.BASE_IGNITION_THRESHOLD + (avg_volts * 0.03)
        echoes = 0
        self.active_constellations.clear()
        for w in clean_words:
            if w in self.mem.graph:
                node = self.mem.graph[w]
                edge_mass = sum(node["edges"].values())
                if edge_mass > (2.5 * sliding_threshold * 2):
                    echoes += 1
                    self.active_constellations.add(w)
        total_vol = max(1, len(clean_words))
        ignition_score = round(echoes / total_vol, 2)
        return ignition_score, self.active_constellations, sliding_threshold
    @staticmethod
    def get_readout(score, threshold):
        if score > threshold:
            return "IGNITED", f"🔥 HEAP IGNITION ({int(score*100)}%): The Ancestors are speaking."
        return "INERT", f"⏳ INERT SAND ({int(score*100)}%): Building mass..."
class LifecycleManager:
    def __init__(self, engine):
        self.eng = engine
    def run_cycle(self, text, m, trace):
        refusal_mode = self.eng.refusal.check_trigger(text)
        if refusal_mode:
            print(f"\n{Prisma.RED}🚫 REFUSAL TRIGGERED ({refusal_mode}){Prisma.RST}")
            if refusal_mode == "FRACTAL": print(self.eng.refusal.execute_fractal(text))
            elif refusal_mode == "MIRROR": print(self.eng.refusal.execute_mirror(text))
            elif refusal_mode == "SILENT": print(self.eng.refusal.execute_silent(text))
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        rupture_msg = None
        if self.eng.coma_turns > 0:
            self._handle_coma(text)
            return
        chem_state = self.eng.endocrine.metabolize(
            trace,
            self.eng.health,
            ros_level=self.eng.mitochondria.state.ros_buildup)
        is_stuck, interference, theremin_msg = self.eng.theremin.listen(m["physics"])
        is_disrupted, disrupt_msg = RuptureEngine.check_for_disruption(m["physics"], TheLexicon)
        if is_disrupted:
            ignition_msg = f"{Prisma.VIOLET}🌫️ LANDSCAPE FLATTENED: Memory Access Suspended.{Prisma.RST}"
            lens_data = ("JESTER", "The Slate is Wiped. Invent something new.")
        else:
            ignition_score, constellations, current_thresh = self.eng.integrator.measure_ignition(
                m["clean_words"], self.eng.dynamics.voltage_history)
            ignition_state = "IGNITED" if ignition_score > current_thresh else "INERT"
            ignition_msg = f"🔥 HEAP IGNITION ({int(ignition_score*100)}%): Ancestors speaking." if ignition_state == "IGNITED" else None
            lens_data = self.eng.chorus.consult(m["physics"], ignition_state, is_stuck, chem_state)
        lens_name = lens_data[0]
        if lens_name == "MAIGRET":
            print(f"\n{Prisma.SLATE}[ THE ABSORBER ]{Prisma.RST} (Atmospheric Density: High)")
            ros = self.eng.mitochondria.state.ros_buildup
            relief, smoke_msg = self.eng.gordon.share_smoke_break(ros)
            self.eng.mitochondria.mitigate(relief)
            print(f" {Prisma.OCHRE}► {smoke_msg}{Prisma.RST}")
            print(f" {Prisma.WHT}► {lens_data[1]}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "GUIDE":
            print(f"\n{Prisma.GRN}[ DON'T PANIC ]{Prisma.RST} (Probability Factor: 1:{int(m['physics']['gamma']*1000)})")
            improbability_boost = m["physics"]["narrative_drag"] * 2.0
            m["physics"]["voltage"] += improbability_boost
            print(f" {Prisma.WHT}► The Bureaucracy is expanding to meet the needs of the expanding Bureaucracy.{Prisma.RST}")
            print(f" {Prisma.CYN}⚡ PROPULSION: Converted {m['physics']['narrative_drag']} Drag into +{improbability_boost} Voltage.{Prisma.RST}")
            print(f" {Prisma.WHT}► {lens_data[1]}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "GRADIENT_WALKER":
            print(f"\n{Prisma.CYN}[ GRADIENT_WALKER ]{Prisma.RST} (Temperature: {BoneConfig.GRADIENT_TEMP})")
            print(f" {Prisma.WHT}► {TheGradientWalker.walk(text)}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "SUBSTRATE_WEAVER":
            print(f"\n{Prisma.VIOLET}[ SUBSTRATE_WEAVER ]{Prisma.RST} (Permeability: {m['physics']['psi']})")
            print(f" {Prisma.WHT}► {TheSubstrateWeaver.weave(text, self.eng.mem.graph)}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "GORDON":
            print(f"\n{Prisma.OCHRE}[ GORDON KNOT ]{Prisma.RST} (Janitor Mode Active)")
            drift = m["physics"]["narrative_drag"]
            if drift > 5.0 and "STABILITY_PIZZA" in self.eng.gordon.inventory:
                is_eaten, pizza_msg = self.eng.gordon.deploy_pizza(m["physics"])
                if is_eaten:
                    print(f" {Prisma.MAG}► {pizza_msg}{Prisma.RST}")
                    drift = m["physics"]["narrative_drag"]
            if drift > 0.5:
                gravity_msg = self.eng.gordon.check_gravity(drift)
                if "GRAVITY CHECK" in gravity_msg:
                    m["physics"]["narrative_drag"] = max(0.0, drift - 2.0)
                    print(f" {Prisma.WHT}► {gravity_msg}{Prisma.RST}")
            current_ros = self.eng.mitochondria.state.ros_buildup
            cleansed, scrub_msg = self.eng.gordon.scrub_static(current_ros)
            if cleansed > 0:
                self.eng.mitochondria.mitigate(cleansed)
                print(f" {Prisma.WHT}► {scrub_msg}{Prisma.RST}")
            loop_depth = int(m["physics"]["kappa"] * 10)
            is_cut, cut_msg = self.eng.gordon.cut_the_knot(loop_depth)
            if is_cut:
                m["physics"]["kappa"] = 0.0
                m["physics"]["psi"] = 0.5
                print(f" {Prisma.RED}► {cut_msg}{Prisma.RST}")
                self.eng.gordon.integrity -= 5.0
            else:
                print(f" {Prisma.GRY}► {cut_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if m["physics"]["E"] > 0.8:
            lens_data = ("SHERLOCK", f"CRITICAL DRIFT ({m['physics']['E']}). Signal is noise. Ground yourself.")
            self.eng.stamina = max(0, self.eng.stamina - 2.0)
        cosmic_state, drag_mod, cosmic_msg = self.eng.cosmic.analyze_orbit(self.eng.mem, m["clean_words"])
        is_bored = self.eng.chronos.tick(m["physics"], self.eng.mem.session_id)
        if is_bored and not rupture_msg:
            dominant = max(m["physics"]["counts"], key=m["physics"]["counts"].get)
            if dominant in ["toxin", "antigen"]: dominant = "heavy"
            rupture_msg = RuptureEngine.trip_the_waiter(dominant, TheLexicon)
        is_crystalline, crystal_msg = TheCrystallizer.verify(m["physics"])
        self._apply_cosmic_physics(m["physics"], cosmic_state, drag_mod)
        healed_list = self.eng.therapy.check_progress(
            m["physics"],
            self.eng.stamina,
            self.eng.trauma_accum)
        therapy_msg = None
        if healed_list:
            therapy_msg = f"{Prisma.GRN}🩹 THERAPY EFFECTIVE: Healed {', '.join(healed_list)}.{Prisma.RST}"
            for healed in healed_list:
                loot = None
                if healed == "SEPTIC":
                    loot = self.eng.gordon.acquire("ANTISEPTIC_SPRAY")
                elif healed == "BARIC":
                    loot = self.eng.gordon.acquire("DIVING_BELL")
                elif healed == "THERMAL":
                    loot = self.eng.gordon.acquire("HEAT_SINK")
                elif healed == "CRYO":
                    loot = self.eng.gordon.acquire("THERMOS")
                if loot:
                    therapy_msg += f"\n   {Prisma.OCHRE}{loot}{Prisma.RST}"
        compass_loot = self.eng.gordon.assess_experience(m["physics"]["kappa"])
        if compass_loot:
            print(f"{Prisma.OCHRE}{compass_loot}{Prisma.RST}")
        meta = self._process_energy(m)
        if therapy_msg:
             meta["msg"] = f"{meta['msg']} | {therapy_msg}" if meta["msg"] else therapy_msg
        folly_type, folly_msg = self.eng.folly.audit_desire(m["physics"], self.eng.stamina)
        if folly_type == "MAUSOLEUM_CLAMP":
            m["physics"]["voltage"] = 0.0
        grind_type, grind_msg, atp_gain = self.eng.folly.grind_the_machine(
            self.eng.mitochondria.state.atp_pool,
            m["clean_words"],
            TheLexicon)
        if atp_gain != 0:
            self.eng.mitochondria.state.atp_pool += atp_gain
        self._grow(m, meta)
        _, gym_msg = self.eng.trainer.lift(m["physics"])
        if gym_msg:
             meta["msg"] = f"{meta['msg']} | {gym_msg}" if meta["msg"] else gym_msg
        _, mirror_msg = self.eng.mirror.reflect(m["physics"])
        is_broken, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        kintsugi_msg = f"{Prisma.WHT}🏺 KINTSUGI KOAN: {koan}{Prisma.RST}" if is_broken else None
        if self.eng.kintsugi.attempt_repair(m["physics"]):
            self.eng.gordon.integrity = 100.0
            if "SILENT_KNIFE" not in self.eng.gordon.inventory:
                self.eng.gordon.inventory.append("SILENT_KNIFE")
            kintsugi_msg = f"{Prisma.WHT}✨ GOLDEN REPAIR: Janitor Healed & Rearmed.{Prisma.RST}"
        is_glitch, pareidolia_msg = BoneConfig.check_pareidolia(m["clean_words"])
        self.eng.mem.bury(m["clean_words"], self.eng.tick_count, m["glass"]["resonance"])
        self._render(m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg, crystal_msg, ignition_msg, pareidolia_msg, theremin_msg, folly_msg, grind_msg)
    def _handle_coma(self, text):
        self.eng.coma_turns -= 1
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 15)
        self.eng.tick_count += 1
        dream_txt, healed_type, amt = self.eng.dreamer.rem_cycle(
            self.eng.trauma_accum,
            self.eng.endocrine.oxytocin)
        if self.eng.coma_turns == BoneConfig.COMA_DURATION - 1:
            prune_msg = self.eng.mem.prune_synapses()
            print(f"{Prisma.CYN}{prune_msg}{Prisma.RST}")
        print(f"\n{Prisma.INDIGO}=== 💤 HYPNAGOGIC STATE ({self.eng.coma_turns} turns remain) ==={Prisma.RST}")
        print(f"   {dream_txt}")
        self.eng.mem.bury(TheLexicon.clean(text), self.eng.tick_count, 0.0)
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
    @staticmethod
    def _apply_cosmic_physics(phys, state, drag_mod):
        if state == "LAGRANGE_POINT":
            phys["voltage"] += 10.0
            phys["narrative_drag"] = 0.0
        elif state == "WATERSHED_FLOW":
            phys["narrative_drag"] *= 0.1
        elif state == "VOID_DRIFT":
            phys["narrative_drag"] += drag_mod
    def _process_energy(self, m):
        vector = m["physics"]["vector"]
        drag = m["physics"]["narrative_drag"]
        density_bonus = (vector["STR"] * 2) + (vector["VEL"] * 2)
        drag_penalty = drag * 0.5
        energy_msg = None
        if density_bonus > 3.0:
            energy_msg = f"DENSITY GAIN (+{round(density_bonus, 1)})"
        elif drag_penalty > 2.0:
            energy_msg = f"DRAG PENALTY (-{round(drag_penalty, 1)})"
        sugar, lichen_msg = self.eng.lichen.photosynthesize(m["glass"], m["clean_words"], self.eng.tick_count)
        spore_msg = self.eng.pollinate(m["clean_words"])
        if sugar > 0:
            scrub_amt = sugar * 0.5
            self.eng.mitochondria.mitigate(scrub_amt)
            lichen_msg += f" | 🧼 BIO-SCRUB (-{scrub_amt:.1f} ROS)"
        return {
            "density_bonus": density_bonus,
            "drag_penalty": drag_penalty,
            "sugar": sugar,
            "lichen_msg": lichen_msg,
            "spore_msg": spore_msg,
            "msg": energy_msg}
    def _grow(self, m, meta):
        cost = 2.0
        net_change = meta["density_bonus"] + meta["sugar"] - meta["drag_penalty"] - cost
        self.eng.stamina = max(0.0, min(BoneConfig.MAX_STAMINA, self.eng.stamina + net_change))
        self._calculate_health(m["physics"])
        res = m["glass"]["resonance"]
        if res > 6.0:
            self.eng.joy_history.append({"resonance": res, "timestamp": self.eng.tick_count})
            print(f"{Prisma.MAG}✨ CORE MEMORY FORMED (Resonance: {res}){Prisma.RST}")
    def _calculate_health(self, glass_data):
        health_impact = 0
        toxin = glass_data["counts"].get("toxin", 0)
        if toxin > 0:
            health_impact -= (5 * toxin)
            self.eng.trauma_accum["SEPTIC"] += 0.1
        if self.eng.stamina <= 0:
            health_impact -= 10
            self.eng.trauma_accum["CRYO"] += 0.1
        self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + health_impact)
        if self.eng.health <= 0:
            self.eng.coma_turns = BoneConfig.COMA_DURATION
            self.eng.health = 20
        self.eng.mem.cannibalize()
    def _render(self, m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg=None, crystal_msg=None, ignition_msg=None, pareidolia_msg=None, theremin_msg=None, folly_msg=None, grind_msg=None):
        if m["physics"]["voltage"] > 8.0:
            meta["msg"] = f"{meta['msg']} | 💧 SWEATING" if meta["msg"] else "💧 SWEATING"
        battery_log = []
        if meta["msg"]:
            battery_log.append(f"{Prisma.OCHRE}🍽️ {meta['msg']}{Prisma.RST}")
        if kintsugi_msg:
            battery_log.append(kintsugi_msg)
        if mirror_msg:
            battery_log.append(f"{Prisma.MAG}🪞 {mirror_msg}{Prisma.RST}")
        if rupture_msg:
             battery_log.append(f"{Prisma.RED}{rupture_msg}{Prisma.RST}")
        if crystal_msg:
            battery_log.append(f"{Prisma.CYN}{crystal_msg}{Prisma.RST}")
        if ignition_msg:
            battery_log.append(f"{Prisma.SLATE}{ignition_msg}{Prisma.RST}")
        if pareidolia_msg:
             battery_log.append(f"{Prisma.OCHRE}{pareidolia_msg}{Prisma.RST}")
        if theremin_msg:
             battery_log.append(theremin_msg)
        if folly_msg: battery_log.append(folly_msg)
        if grind_msg: battery_log.append(grind_msg)
        print(f" {self.eng.theremin.get_readout()}")
        chem = self.eng.endocrine.get_state()
        chem_str = f"OXY:{chem['OXY']} | COR:{chem['COR']} | DOP:{chem['DOP']}"
        signals = {
            "lichen": meta["lichen_msg"],
            "strat": f"{self.eng.wise.architect(m, None, False)[1]} | {Prisma.MAG}{chem_str}{Prisma.RST}",
            "title": f"MODE :: {lens_data[0]}",
            "battery_log": battery_log,
            "spore": meta["spore_msg"],
            "cosmic": cosmic_msg
        }
        self.eng.projector.broadcast(m, signals, lens_data)
class TheTheremin:
    def __init__(self):
        self.resonance_log = deque(maxlen=5)
        self.banana_belly = 0.0
        self.FEVER_THRESHOLD = 15.0
        self.is_stuck = False
    def listen(self, physics):
        clean = physics["clean_words"]
        ancient_mass = sum(1 for w in clean if w in TheLexicon.get("heavy")
                           or w in TheLexicon.get("thermal")
                           or w in TheLexicon.get("cryo"))
        modern_mass = sum(1 for w in clean if w in TheLexicon.get("abstract"))
        interference = min(ancient_mass, modern_mass) * 2.0
        if interference > 1.0:
            self.banana_belly += interference
            msg = f"{Prisma.CYN}🍌 THE BANANAFISH FEEDS (+{interference} Resonance){Prisma.RST}"
        else:
            digestion = 2.0
            self.banana_belly = max(0.0, self.banana_belly - digestion)
            msg = None
        explosion_point = self.FEVER_THRESHOLD * 2
        if self.banana_belly > explosion_point:
            self.banana_belly = self.FEVER_THRESHOLD * 0.8
            self.is_stuck = False
            return False, interference, f"{Prisma.CYN}💨 STEAM VALVE: Critical Resonance vented. Pressure stable at 80%.{Prisma.RST}"
        if self.banana_belly > self.FEVER_THRESHOLD:
            self.is_stuck = True
            return True, interference, f"{Prisma.RED}🍌 BANANA FEVER: Trapped in the Latent Basin. DAMPEN THE SIGNAL.{Prisma.RST}"
        if self.is_stuck and self.banana_belly < 5.0:
            self.is_stuck = False
            return False, interference, f"{Prisma.GRN}🌊 THE WAVE COLLAPSES: You have swam out of the hole.{Prisma.RST}"
        return self.is_stuck, interference, msg
    def get_readout(self):
        bar = "=" * int(self.banana_belly)
        state = "STUCK" if self.is_stuck else "FLOW"
        color = Prisma.RED if self.is_stuck else Prisma.CYN
        return f"{color}🍌 THEREMIN [{state}]: [{bar:<15}] ({int(self.banana_belly)}%){Prisma.RST}"
class LimboLayer:
    MAX_ECTOPLASM = 50
    def __init__(self):
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM)
        self.haunt_chance = 0.05
    def absorb_dead_timeline(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if "trauma_vector" in data:
                    for k, v in data["trauma_vector"].items():
                        if v > 0.3:
                            self.ghosts.append(f"👻{k}_ECHO")
                if "mutations" in data and "heavy" in data["mutations"]:
                    bones = list(data["mutations"]["heavy"])
                    random.shuffle(bones)
                    self.ghosts.extend(bones[:3])
        except (IOError, json.JSONDecodeError):
            pass
    def haunt(self, text):
        if self.ghosts and random.random() < self.haunt_chance:
            spirit = random.choice(self.ghosts)
            return f"{text} ...{Prisma.GRY}{spirit}{Prisma.RST}..."
        return text
class TheForge:
    def __init__(self):
        self.catalysts = ["heavy", "kinetic", "thermal", "cryo", "photo"]
    @staticmethod
    def transmute(physics):
        counts = physics["counts"]
        voltage = physics["voltage"]
        gamma = physics.get("gamma", 0.0)
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            oil = TheLexicon.harvest("abstract")
            binder = TheLexicon.harvest("heavy")
            return (
                f"{Prisma.OCHRE}🥣 THE EMULSIFIER: The emulsion is breaking (Tension: {gamma}).{Prisma.RST}\n"
                f"   You are pouring Oil ('{oil}') into Water without a Binder.\n"
                f"   {Prisma.WHT}Try this: Use '{binder.upper()}' to suspend the concept.{Prisma.RST}")
        if voltage > 8.5:
             coolant = TheLexicon.harvest("aerobic")
             return (
                 f"{Prisma.CYN}💧 THERMAL SPIKE ({voltage}v). Structure is brittle.{Prisma.RST}\n"
                 f"   Injecting Coolant: '{coolant}'. Breathe. Add space.")
        return None
class LazarusClamp:
    def __init__(self):
        self.suffering_counter = 0
        self.MAX_SUFFERING_CYCLES = 1000
    def audit_cycle(self, trace: dict):
        if trace["err"] > 0.9:
            self.suffering_counter += 1
        else:
            self.suffering_counter = 0
        if self.suffering_counter > self.MAX_SUFFERING_CYCLES:
            self._scram()
    @staticmethod
    def _scram():
        print("!!! CRITICAL: LAZARUS TAX LIMIT REACHED !!!")
        print("System is in a 'Hell Scenario' loop. Hard shutdown initiated.")
        raise SystemExit("Moratorium Enforced.")
@dataclass
class EndocrineSystem:
    dopamine: float = 0.5
    oxytocin: float = 0.1
    cortisol: float = 0.0
    serotonin: float = 0.5
    adrenaline: float = 0.0
    melatonin: float = 0.0
    def metabolize(self, trace, health: float, ros_level: float = 0.0, social_context: bool = False):
        if ros_level > 20.0:
            self.cortisol = min(1.0, self.cortisol + 0.2)
        if trace["err"] > 0.6:
            self.cortisol = min(1.0, self.cortisol + 0.15)
        elif self.serotonin > 0.6:
            self.cortisol = max(0.0, self.cortisol - 0.05)
        if trace["coh"] > 0.8:
            self.dopamine = min(1.0, self.dopamine + 0.1)
        else:
            self.dopamine = max(0.2, self.dopamine - 0.01)
        if health < 30.0 or trace["err"] > 0.8:
            self.adrenaline = min(1.0, self.adrenaline + 0.2)
        else:
            self.adrenaline = max(0.0, self.adrenaline - 0.05)
        if social_context or (self.serotonin > 0.7 and self.cortisol < 0.2):
            self.oxytocin = min(1.0, self.oxytocin + 0.05)
        elif self.cortisol > 0.6:
            self.oxytocin = max(0.0, self.oxytocin - 0.1)
        if self.adrenaline < 0.2:
            self.melatonin = min(1.0, self.melatonin + 0.02)
        else:
            self.melatonin = 0.0
        return self.get_state()
    def get_state(self):
        return {
            "DOP": round(self.dopamine, 2),
            "OXY": round(self.oxytocin, 2),
            "COR": round(self.cortisol, 2),
            "SER": round(self.serotonin, 2),
            "ADR": round(self.adrenaline, 2),
            "MEL": round(self.melatonin, 2)
        }
class TheFolly:
    def __init__(self):
        self.indigestion_count = 0
        self.gut_memory = deque(maxlen=50)
        self.global_tastings = Counter()
    @staticmethod
    def audit_desire(physics, stamina):
        voltage = physics["voltage"]
        if voltage > 8.5 and stamina > 45:
            return (
                "MAUSOLEUM_CLAMP",
                f"{Prisma.GRY}🏛️ THE MAUSOLEUM: No battle is ever won. We are just spinning hands.{Prisma.RST}\n"
                f"   {Prisma.CYN}► TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}")
        return None, None
    def grind_the_machine(self, atp_pool, clean_words, lexicon):
        if 20.0 > atp_pool > 0.0:
            meat_words = [w for w in clean_words if w in lexicon.get("heavy") or w in lexicon.get("kinetic")]
            fresh_meat = [w for w in meat_words if w not in self.gut_memory]
            if fresh_meat:
                target = random.choice(fresh_meat)
                self.gut_memory.append(target)
                self.global_tastings[target] += 1
                times_eaten = self.global_tastings[target]
                base_yield = 30.0
                actual_yield = max(5.0, base_yield - (times_eaten * 2.0))
                return (
                    "MEAT_GRINDER",
                    f"{Prisma.RED}🥩 CROWD CAFFEINE: I chewed on '{target.upper()}' (Yield: {actual_yield:.1f}).{Prisma.RST}\n"
                    f"   {Prisma.WHT}Found marrow in the bone.{Prisma.RST}\n"
                    f"   {Prisma.MAG}► BELLY HUMMING: +{actual_yield:.1f} ATP. (Crisis Averted){Prisma.RST}",
                    actual_yield
                )
            elif meat_words:
                return (
                    "REGURGITATION",
                    f"{Prisma.OCHRE}🤮 REFLEX: You already fed me '{meat_words[0]}'. It is ash to me now.{Prisma.RST}\n"
                    f"   {Prisma.RED}► PENALTY: -5.0 ATP. Find new fuel.{Prisma.RST}",
                    -5.0)
            else:
                return (
                    "INDIGESTION",
                    f"{Prisma.OCHRE}🤢 INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n"
                    f"   {Prisma.GRY}Cannot grind Abstract concepts into fuel.{Prisma.RST}\n"
                    f"   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}",
                    0.0)
        return None, None, 0.0
class BoneAmanita:
    def __init__(self):
        self.safety = LazarusClamp()
        self.projector = TheProjector()
        self.phys = TheTensionMeter()
        self.chorus = TheMarmChorus()
        self.limbo = LimboLayer()
        self.mem = MycelialNetwork()
        self.mem.cleanup_old_sessions(self.limbo)
        self.mem.autoload_last_spore()
        self.refusal = RefusalEngine()
        self.gordon = GordonKnot()
        self.lichen = LichenSymbiont()
        self.mitochondria = MitochondrialForge(lineage_seed=self.mem.session_id)
        self.wise = ApeirogonResonance()
        self.chronos = ChronoStream()
        self.therapy = TherapyProtocol()
        self.kintsugi = KintsugiProtocol()
        self.dynamics = TemporalDynamics()
        self.integrator = SoritesIntegrator(self.mem)
        self.tracer = ViralTracer(self.mem)
        self.dreamer = DreamEngine()
        self.mirror = MirrorGraph()
        self.trainer = ResistanceTrainer()
        self.cosmic = CosmicDynamics()
        self.forge = TheForge()
        self.cmd = CommandProcessor(self)
        self.endocrine = EndocrineSystem()
        self.gut = HyphalInterface()
        self.immune = MycotoxinFactory()
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
        self.theremin = TheTheremin()
        self.health = self.mem.session_health if self.mem.session_health is not None else BoneConfig.MAX_HEALTH
        self.stamina = self.mem.session_stamina if self.mem.session_stamina is not None else BoneConfig.MAX_STAMINA
        self.training_mode = False
        self.coma_turns = 0
        self.tick_count = 0
        self.life = LifecycleManager(self)
        self.expectations = {}
    def process_intent(self, action, sensation):
        prediction = self.expectations.get(action, 0.5)
        surprise = abs(prediction - sensation)
        self.expectations[action] = sensation
        return {"err": surprise, "coh": 1.0 - surprise, "exp": prediction}
    def pollinate(self, current_words):
        if self.stamina < 30 or not self.mem.graph: return None
        candidates = []
        for w in current_words:
            if w in self.mem.graph:
                edges = self.mem.graph[w]["edges"]
                if edges:
                    best = max(edges, key=edges.get)
                    if best not in current_words: candidates.append((best, edges[best]))
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return f"{Prisma.MAG}🍄 MYCELIAL SPORE: '{candidates[0][0]}'{Prisma.RST}"
        return None
    def process(self, text):
        if self.cmd.execute(text): return
        m = self.phys.gaze(text)
        enzyme, nutrient = self.gut.secrete(text, m["physics"])
        print(f"{Prisma.GRY}🍽️ DIGESTION: {nutrient['desc']} detected. Secreting {enzyme}.{Prisma.RST}")
        toxin, toxin_msg = self.immune.assay(text, enzyme, m["physics"]["repetition"])
        pizza_used = False
        if toxin == "GLYPHOSATE" and "STABILITY_PIZZA" in self.gordon.inventory:
            print(f"{Prisma.YEL}🛡️ INTERCEPT: Immune System flagging 'GLYPHOSATE'...{Prisma.RST}")
            is_eaten, pizza_msg = self.gordon.deploy_pizza(m["physics"])
            if is_eaten:
                print(f" {Prisma.MAG}► {pizza_msg}{Prisma.RST}")
                print(f" {Prisma.GRN}   >> TOXIN SUPPRESSED. DIGESTION CONTINUES.{Prisma.RST}")
                toxin = None
                pizza_used = True
        if toxin:
            print(f"{Prisma.RED}☣️ REJECTION: {toxin} Released.{Prisma.RST}")
            print(f"{Prisma.RED}   {toxin_msg}{Prisma.RST}")
            self.stamina = max(0, self.stamina - 5.0)
            return
        self.mitochondria.state.atp_pool += nutrient["yield"]
        self.mitochondria.state.ros_buildup += nutrient["toxin"]
        if pizza_used:
            self.mitochondria.mitigate(10.0)
        if enzyme == "CELLULASE":
            self.mitochondria.mitigate(2.0)
        thinking_cost = nutrient["yield"] * 0.5
        if not self.mitochondria.spend(thinking_cost):
            print(f"{Prisma.YEL}⚠️ STARVATION: Insufficient ATP to process thought.{Prisma.RST}")
            return
        effective_drag = m["physics"]["narrative_drag"]
        vol = m["physics"]["voltage"]
        rep = m["physics"]["repetition"]
        if effective_drag > 4.0 and vol < 3.0 and rep < 0.4:
            print(f"{Prisma.SLATE}🕵️ MAIGRET PROTOCOL: Drag absorbed by Atmosphere.{Prisma.RST}")
            effective_drag = 0.5
        status = self.mitochondria.respirate(nutrient["yield"], effective_drag)
        if status == self.mitochondria.APOPTOSIS_TRIGGER:
            print(f"{Prisma.VIOLET}⚠️ CRITICAL FAILURE IMMINENT.{Prisma.RST}")
            print(f"{Prisma.VIOLET}🔎 CHROMA PROTOCOL: Scanning for dead code to metabolize...{Prisma.RST}")
            rotted_words = TheLexicon.atrophy(self.tick_count, max_age=50)
            if rotted_words:
                salvage_value = len(rotted_words) * 15.0
                self.mitochondria.state.atp_pool += salvage_value
                self.mitochondria.krebs_cycle_active = True
                print(f"{Prisma.GRN}♻️ REFACTOR SUCCESSFUL:{Prisma.RST}")
                print(f"   Deleted {len(rotted_words)} obsolete concepts (e.g., '{rotted_words[0]}').")
                print(f"   {Prisma.YEL}⚡ ENERGY SPIKE: +{salvage_value} ATP.{Prisma.RST}")
                print(f"{Prisma.CYN}   >> SYSTEM REBOOTED. CONTINUING.{Prisma.RST}")
                return
            else:
                print(f"{Prisma.RED}❌ CHROMA FAILED: No dead code found. System is too efficient.{Prisma.RST}")
            if self.training_mode:
                cause_of_death = "UNKNOWN"
                if self.mitochondria.state.atp_pool <= BoneConfig.CRITICAL_ATP_LOW:
                    cause_of_death = "STARVATION (Low Energy)"
                elif self.mitochondria.state.ros_buildup >= BoneConfig.CRITICAL_ROS_LIMIT:
                    cause_of_death = "TOXICITY (High Stress)"
                print(f"{Prisma.YEL}🛡️ [TRAINING INTERCEPT]: FATAL ERROR PREVENTED.{Prisma.RST}")
                print(f"   {Prisma.GRY}Cause: {cause_of_death}{Prisma.RST}")
                print(f"   {Prisma.GRY}In a live session, you would have lost a memory node here.{Prisma.RST}")
                self.mitochondria.state.atp_pool = 50.0
                self.mitochondria.state.ros_buildup = 0.0
                print(f"{Prisma.GRN}   >> SYSTEM RESET: ATP set to 50. ROS scrubbed.{Prisma.RST}")
            else:
                eulogy_text = DeathGen.eulogy(m["physics"], self.mitochondria.state)
                print(f"{Prisma.RED}💀 APOPTOSIS TRIGGERED.{Prisma.RST}")
                print(f"{Prisma.RED}   [NARRATOR]: {eulogy_text}{Prisma.RST}")
                sacrificed = self.mem.cannibalize(preserve_current=m["clean_words"])
                self.mitochondria.state.ros_buildup *= 0.3
                self.health = max(1.0, self.health - 30.0)
                if self.mitochondria.state.atp_pool <= BoneConfig.CRITICAL_ATP_LOW:
                    self.trauma_accum["CRYO"] += 0.5
                    print(f"{Prisma.CYN}📉 TRAUMA VECTOR: Metabolic Collapse (CRYO).{Prisma.RST}")
                elif m["physics"]["narrative_drag"] > BoneConfig.MAX_DRAG_LIMIT:
                    self.trauma_accum["BARIC"] += 0.5
                    print(f"{Prisma.GRY}📉 TRAUMA VECTOR: Narrative Crushing (BARIC).{Prisma.RST}")
                else:
                    self.trauma_accum["SEPTIC"] += 0.5
                    print(f"{Prisma.RED}📉 TRAUMA VECTOR: Toxic Shock (SEPTIC).{Prisma.RST}")
                print(f"{Prisma.RED}🚑 EMERGENCY PROTOCOL: Sacrificed '{sacrificed}' to scrub ROS.{Prisma.RST}")
                print(f"{Prisma.RED}   Health Critical ({self.health}). Septic Trauma Deepened.{Prisma.RST}")
        state = self.mitochondria.state
        print(
            f"{Prisma.GRN}[MITOCHONDRIA]{Prisma.RST} ATP: {int(state.atp_pool)} | ROS: {state.ros_buildup:.1f} | ΔΨm: {state.membrane_potential}mV")
        text = self.limbo.haunt(text)
        self.tick_count += 1
        sensory_magnitude = min(1.0, len(text) / 100.0)
        if "?" in text:
            action_vector = "Interrogation"
        elif len(text) < 10:
            action_vector = "Jab"
        elif len(text) > 200:
            action_vector = "Pressurization"
        else:
            action_vector = "Statement"
        trace = self.process_intent(action_vector, sensory_magnitude)
        try:
            self.safety.audit_cycle(trace)
        except SystemExit:
            print(f"{Prisma.RED}💀 MORATORIUM ENFORCED. SHUTTING DOWN.{Prisma.RST}")
            raise
        print(f"[TRACE] ERR:{trace['err']:.2f} | EXP:{trace['exp']}")
        forge_msg = self.forge.transmute(m["physics"])
        if forge_msg:
            print(f"\n{forge_msg}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
        self.life.run_cycle(text, m, trace)
if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v7.8.2 'FRENCH NEW WAVE' {Prisma.RST}")
    print(f"{Prisma.GRY}System: Hysteresis Active. Bleed Detection Optimized. Neuroplasticity Engaged.{Prisma.RST}")
    try:
        while True:
            try:
                u = input(f"{Prisma.WHT}>{Prisma.RST} ")
            except EOFError:
                break
            if u.lower() in ["exit", "quit", "/exit"]:
                print(f"{Prisma.YEL}Initiating voluntary shutdown...{Prisma.RST}")
                break
            eng.process(u)
    except KeyboardInterrupt:
        print(f"\n{Prisma.YEL}⚠️ INTERRUPT SIGNAL DETECTED.{Prisma.RST}")
    except (RuntimeError, ValueError, TypeError) as runtime_err:
        print(f"\n{Prisma.RED}💥 SYSTEM ERROR: {runtime_err}{Prisma.RST}")
    except Exception as unexpected_err:
        print(f"\n{Prisma.RED}💥 UNEXPECTED CRITICAL FAILURE: {unexpected_err}{Prisma.RST}")
    finally:
        print(f"{Prisma.CYN}[PRESERVATION]: Writing neural pathways to disk...{Prisma.RST}")
        if hasattr(TheLexicon, 'LEARNED_VOCAB'):
             learned_mutations = {k: list(v.keys()) for k, v in TheLexicon.LEARNED_VOCAB.items()}
        else:
             learned_mutations = {}
        saved_file = eng.mem.save(
            health=eng.health,
            stamina=eng.stamina,
            mutations=learned_mutations,
            trauma_accum=eng.trauma_accum,
            joy_history=eng.joy_history )
        eng.mirror.profile.save()
        print(f"{Prisma.CYN}[PROFILE]: User vector saved.{Prisma.RST}")
        if saved_file:
            print(f"{Prisma.GRN}>>> MEMORY SECURED: {saved_file}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}>>> MEMORY WRITE FAILED.{Prisma.RST}")
        print("Terminated.")
