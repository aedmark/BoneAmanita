# BONEAMANITA 8.2.1 - "TERRAFORMATION (BRAINED)"
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
    C = {"R": "\033[91m", "G": "\033[92m", "Y": "\033[93m", "B": "\033[94m", "M": "\033[95m", "C": "\033[96m",
         "W": "\033[97m", "0": "\033[90m", "X": "\033[0m"}
    RST = C["X"]
    RED = C["R"]
    GRN = C["G"]
    YEL = C["Y"]
    BLU = C["B"]
    MAG = C["M"]
    CYN = C["C"]
    WHT = C["W"]
    GRY = C["0"]
    INDIGO = BLU
    OCHRE = YEL
    VIOLET = MAG
    SLATE = GRY
    PALETTE = {"COURTYARD": "Y", "LABORATORY": "B", "RUPTURE": "M", "DEFAULT": "0"}
    @classmethod
    def paint(cls, text, color_key="0"):
        return f"{cls.C.get(color_key, cls.C['0'])}{text}{cls.C['X']}"
@dataclass
class LexNode:
    def __init__(self, name="LEX"):
        self.name = name
        self.density = 10.0
        self.hazard = "MUGGING"
    def traverse(self, is_polite):
        if is_polite:
            return "Pass granted. The shadow nods."
        return "⚠️ AMBUSH: You didn't tip your hat. The darkness bites."
@dataclass
class MitochondrialState:
    atp_pool: float = 100.0
    ros_buildup: float = 0.0
    membrane_potential: float = -150.0
    mother_hash: str = "MITOCHONDRIAL_EVE_001"
    efficiency_mod: float = 1.0
    ros_resistance: float = 1.0
    enzymes: set = field(default_factory=set)
class MitochondrialForge:
    BASE_EFFICIENCY = 0.85
    APOPTOSIS_TRIGGER = "CYTOCHROME_C_RELEASE"
    def __init__(self, lineage_seed: str, inherited_traits: dict = None):
        self.state = MitochondrialState(mother_hash=lineage_seed)
        self.krebs_cycle_active = True
        if inherited_traits:
            self.state.efficiency_mod = inherited_traits.get("efficiency_mod", 1.0)
            self.state.ros_resistance = inherited_traits.get("ros_resistance", 1.0)
            if "enzymes" in inherited_traits:
                self.state.enzymes = set(inherited_traits["enzymes"])
                print(f"{Prisma.CYN}[MITOCHONDRIA]: Inherited Enzymes for {list(self.state.enzymes)}.{Prisma.RST}")
            if self.state.efficiency_mod > 1.0:
                print(f"{Prisma.GRN}[MITOCHONDRIA]: Inherited High-Efficiency Matrix ({self.state.efficiency_mod:.2f}x).{Prisma.RST}")
            if self.state.ros_resistance > 1.0:
                print(f"{Prisma.CYN}[MITOCHONDRIA]: Inherited Thickened Membrane (Resist: {self.state.ros_resistance:.2f}x).{Prisma.RST}")
    def develop_enzyme(self, word):
        if word not in self.state.enzymes:
            self.state.enzymes.add(word)
            self.state.efficiency_mod = min(2.0, self.state.efficiency_mod + 0.05)
            TheLexicon.teach(word, "priority", 0)
            print(f"{Prisma.MAG}⚡ ADRENALINE BRIDGE: '{word.upper()}' is now High Priority.{Prisma.RST}")
            return True
        return False
    def adapt(self, current_health):
        mutations = {
            "efficiency_mod": self.state.efficiency_mod,
            "ros_resistance": self.state.ros_resistance,
            "enzymes": list(self.state.enzymes)
        }
        if self.state.atp_pool > 150.0:
            mutations["efficiency_mod"] = min(1.5, self.state.efficiency_mod + 0.05)
        elif self.state.atp_pool < 20.0:
            mutations["efficiency_mod"] = max(0.5, self.state.efficiency_mod - 0.05)
        if self.state.ros_buildup > 50.0 and current_health > 50.0:
            mutations["ros_resistance"] = min(2.0, self.state.ros_resistance + 0.1)
        return mutations
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
    MEAT_TRIGGERS = {"i", "me", "my", "feel", "want", "hate", "love", "am", "help", "please", "we", "us", }
    def __init__(self):
        self.digestive_log = deque(maxlen=3)
        self.enzymes = {"LIGNASE": self._digest_structure, "CELLULASE": self._digest_narrative,
                        "PROTEASE": self._digest_intent, "CHITINASE": self._digest_complex, "DECRYPTASE": self._digest_encrypted, }
    def secrete(self, text, physics):
        code_markers = sum(1 for c in text if c in "{}[];=<>_()|")
        code_density = code_markers / max(1, len(text))
        meat_count = sum(1 for w in physics["clean_words"] if w in self.MEAT_TRIGGERS)
        meat_density = meat_count / max(1, len(physics["clean_words"]))
        lines = [l for l in text.splitlines() if l.strip()]
        avg_line_len = len(text.split()) / max(1, len(lines))
        is_list = any(l.strip().startswith(("-", "*", "1.", "•")) for l in lines[:3])
        is_poetic = len(lines) > 2 and avg_line_len < 8 and not is_list
        enzyme_type = "CELLULASE"
        weather_hits = sum(1 for w in physics["clean_words"] if w in self.WEATHER_CIPHER)
        if weather_hits > 0:
            enzyme_type = "DECRYPTASE"
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
        return {"type": "STRUCTURAL", "yield": 15.0, "toxin": 5.0, "desc": f"Hard Lignin ({loc} LOC)", }
    WEATHER_CIPHER = {"pressure", "humidity", "barometric", "temp", "forecast", "storm", "resource", "allocation"}
    @classmethod
    def _digest_encrypted(cls):
        return {"type": "ENCRYPTED", "yield": 25.6, "toxin": 2.0, "desc": "Barometric Data (High Resource Allocation)"}
    @classmethod
    def _digest_narrative(cls):
        return {"type": "NARRATIVE", "yield": 5.0, "toxin": -2.0, "desc": "Soft Cellulose", }
    @classmethod
    def _digest_intent(cls):
        return {"type": "BIOLOGICAL", "yield": 8.0, "toxin": 0.0, "desc": "Raw Meat (User Intent)", }
    @classmethod
    def _digest_complex(cls):
        return {"type": "COMPLEX", "yield": 20.0, "toxin": 8.0, "desc": "Chitin (Structured Intent / Poetry)", }
class MycotoxinFactory:
    def __init__(self):
        self.active_antibodies = []
    @classmethod
    def assay(cls, text, enzyme_type, repetition_score, physics, pulse_status="CLEAR"):
        if len(text) < 5 and enzyme_type == "NARRATIVE":
            return (
                "AMANITIN",
                "Fatal Error: Input is genetically hollow. Ribosome stalled.",
            )
        if pulse_status == "ZOMBIE_KNOCK" or repetition_score > 0.8:
            return (
                "MUSCIMOL",
                f"System Delirium: Pulse Monitor detects Undead Signal (Rep: {repetition_score}). Reality is dissolving.",
            )
        if TheLexicon.ANTIGEN_REGEX:
            antigen_hits = TheLexicon.ANTIGEN_REGEX.findall(text)
            if antigen_hits:
                counts = physics["counts"]
                if counts.get("thermal", 0) > 0:
                    return (
                        None,
                        f"{Prisma.OCHRE}🔥 ALCHEMY: Thermal words boiled off the '{antigen_hits[0]}' toxin. Safe.{Prisma.RST}",
                    )
                if counts.get("heavy", 0) >= len(antigen_hits):
                    return (
                        None,
                        f"{Prisma.GRN}🌿 MARIK GAMBIT: You ate the poison ('{antigen_hits[0]}'), but the Herbs (Heavy) neutralized it.{Prisma.RST}",
                    )
                if counts.get("cryo", 0) > 0:
                    return (
                        "CYANIDE_POWDER",
                        f"❄️ CRYO-CONCENTRATION: Cold words freeze-dried the '{antigen_hits[0]}' into a fatal powder.",
                    )
                return (
                    "GLYPHOSATE",
                    f"☣️ TOXIN DETECTED: '{antigen_hits[0]}' is unprocessed waste. Burn it or bury it.",
                )
        clean_words = physics["clean_words"]
        mass_words = (
                TheLexicon.get("heavy")
                | TheLexicon.get("kinetic")
                | TheLexicon.get("thermal")
                | TheLexicon.get("cryo")
        )
        ballast = sum(1 for w in clean_words if w in mass_words)
        suburban_hits = [w for w in clean_words if w in TheLexicon.get("suburban")]
        suburban_density = len(suburban_hits) / max(1, len(clean_words))
        if suburban_density > 0.15 and ballast == 0:
            return (
                "GLYPHOSATE",
                "⚠️ STEVE EVENT: Suburban signals detected with ZERO mass. Context is sterile.",
            )
        return None, None
class DeathGen:
    PREFIXES = ["Alas,", "Tragic.", "System Halt.", "CRITICAL FAILURE:", "Well, that happened.", "Oh dear.",
                "As prophesied,", ]
    CAUSES = {
        "TOXICITY": ["Toxic Shock", "Septicemia", "Bad Vibes", "Radiation Poisoning", "Ink Poisoning", ],
        "STARVATION": ["Metabolic Collapse", "Famine", "Battery Drain", "Entropy Death", "Heat Death", ],
        "TRAUMA": ["Blunt Force", "Laceration", "Heartbreak", "System Shock", "Existential Dread", ],
        "GLUTTONY": ["Indigestion", "Bloat", "Overflow", "Greed", "Compaction"],
        "BOREDOM": ["Small Talk", "The HOA", "A 30-Year Mortgage", "Lawn Care Accident", "Aggressive Edging", ],
    }
    VERDICTS = {
        "HEAVY": ["Your logic was too dense.", "You choked on the syntax.", "Gravity crushed you.", ],
        "LIGHT": ["You floated away.", "There was no substance to hold you.", "Vapor lock.", ],
        "TOXIC": ["You are poisonous.", "The immune system rejected you.", "You taste like ash.", ],
        "BORING": ["The audience left.", "You bored the machine to death.", "Stagnation is fatal.", ],
    }
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
    MAX_STAMINA = 100.0
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
    CRITICAL_ROS_LIMIT = 80.0
    CRITICAL_ATP_LOW = 5.0
    MAX_DRAG_LIMIT = 6.0
    MAX_VOLTAGE = 20.0
    MAX_ROS = 200.0
    MIN_DENSITY_THRESHOLD = 0.2
    MAX_REPETITION_LIMIT = 0.4
    CRITICAL_TOXIN_HIGH = 75.0
    TRAUMA_VECTOR = {"THERMAL": 0, "CRYO": 0, "SEPTIC": 0, "BARIC": 0}
    GRAVITY_WELL_THRESHOLD = 12.0
    GEODESIC_STRENGTH = 7.0
    VOID_THRESHOLD = 0.1
    BASE_IGNITION_THRESHOLD = 0.4
    KAPPA_THRESHOLD = 0.85
    PERMEABILITY_INDEX = 0.5
    FRACTAL_DEPTH_LIMIT = 4
    GRADIENT_TEMP = 0.001
    ANVIL_TRIGGER_VOLTAGE = 8.0
    ANVIL_TRIGGER_MASS = 8.0
    VOID_DENSITY_THRESHOLD = 0.15
    PRIORITY_LEARNING_RATE = 2.0
    FEVER_MODE_DYNAMIC = True
    @staticmethod
    def get_gradient_temp(voltage, kappa):
        base = BoneConfig.GRADIENT_TEMP
        dynamic = base + (voltage * 0.01) - (kappa * 0.005)
        return max(0.0001, dynamic)
    REFUSAL_MODES = {"SILENT": "ROUTING_AROUND_DAMAGE", "FRACTAL": "INFINITE_RECURSION", "MIRROR": "PERFECT_TOPOLOGICAL_ECHO"}
    CORTISOL_TRIGGER = 0.6
    ADRENALINE_TRIGGER = 0.8
    OXYTOCIN_TRIGGER = 0.75
    ANTIGENS = {"basically", "actually", "literally", "utilize", "leverage"}
    PAREIDOLIA_TRIGGERS = {"face", "ghost", "jesus", "cloud", "demon", "voice", "eyes"}
    MASS_NOUNS = {
        "stone", "iron", "blood", "bone", "rust", "gold", "meat",
        "root", "obsidian", "concrete", "lead", "ash", "mud",
        "machinery", "gear", "piston", "gravity", "ink", "press"
    }
    GAS_NOUNS = {
        "basically", "actually", "literally", "nuance", "context",
        "landscape", "journey", "tapestry", "facet", "realm"
    }
    @staticmethod
    def check_pareidolia(clean_words):
        hits = [w for w in clean_words if w in BoneConfig.PAREIDOLIA_TRIGGERS]
        if len(hits) > 0:
            return True, f"⚠️ PAREIDOLIA WARNING: You are projecting 'Mind' ({hits[0].upper()}) onto 'Sand'."
        return False, None
class BioState:
    def __init__(self):
        self.atp = 80.0
        self.toxin = 0.0
        self.adrenaline = 0.0
        self.cortisol = 0.0
        self.dopamine = 0.5
    def metabolize(self, signal_data: Dict) -> str:
        density = signal_data.get('density', 0.0)
        repetition = signal_data.get('repetition', 0.0)
        has_mass = signal_data.get('has_mass', False)
        if has_mass and density > BoneConfig.MIN_DENSITY_THRESHOLD:
            self.atp = min(BoneConfig.MAX_STAMINA, self.atp + 15.0)
            self.toxin = max(0.0, self.toxin - 10.0)
            self._adjust_hormones("DENSE")
            return "THRIVING"
        elif repetition > BoneConfig.MAX_REPETITION_LIMIT:
            self.atp -= 5.0
            self.toxin += 15.0
            self._adjust_hormones("TOXIC")
            return "POISONED"
        elif not has_mass:
            self.atp -= 2.0
            self.toxin += 5.0
            self._adjust_hormones("EMPTY")
            return "STARVING"

        else:
            self.atp -= 1.0
            self._adjust_hormones("NEUTRAL")
            return "STABLE"
    def _adjust_hormones(self, state: str):
        if state == "DENSE":
            self.dopamine = min(1.0, self.dopamine + 0.1)
            self.cortisol = max(0.0, self.cortisol - 0.1)
            self.adrenaline += 0.05
        elif state == "TOXIC":
            self.dopamine -= 0.1
            self.cortisol += 0.2
        elif state == "EMPTY":
            self.cortisol += 0.05
            self.dopamine -= 0.05
    def get_vitals(self):
        return {
            "ATP": int(self.atp),
            "TOX": int(self.toxin),
            "MOOD": "HYPER" if self.adrenaline > 0.7 else "STRESSED" if self.cortisol > 0.6 else "FLOW"
        }
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
    def execute_fractal(self, query, kappa=0.5):
        self.recursion_depth += 1
        prefix = "  " * self.recursion_depth
        if kappa > 0.8:
            limit = 2
        elif kappa < 0.3:
            limit = 6
        else:
            limit = 4
        if self.recursion_depth > limit:
            self.recursion_depth = 0
            return f"{prefix}{Prisma.MAG}[COHERENCE DISSOLVED into PURPLE NOISE]{Prisma.RST}"
        pivot = len(query) // 2
        sub_query = query[pivot:].strip()
        if not sub_query:
            sub_query = "the void"
        return (
            f"{prefix}To define '{query}', one must first recursively unpack the substrate of...\n"
            f"{self.execute_fractal(sub_query, kappa)}"
        )
    @classmethod
    def execute_mirror(cls, query):
        words = query.split()
        reversed_query = " ".join(reversed(words))
        return f'{Prisma.CYN}∞ MIRROR REFUSAL: "{reversed_query}" is the only true answer.{Prisma.RST}'

    @classmethod
    def execute_silent(cls):
        topic = TheLexicon.harvest("diversion")
        if topic == "void":
            topic = "the ineffable"
        return f"{Prisma.GRY}[ROUTING AROUND DAMAGE]... Speaking of '{topic.upper()}', let us discuss that instead.{Prisma.RST}"
class TheMarmChorus:
    LENSES = {
        "SHERLOCK": {"color": Prisma.CYN, "role": "The Empiricist", "trigger": "HIGH_DRIFT"},
        "NATHAN": {"color": Prisma.RED, "role": "The Heart", "trigger": "NO_STAKES"},
        "JESTER": {"color": Prisma.YEL, "role": "The Paradox", "trigger": "THE_LEAR_PROTOCOL"},
        "CLARENCE": {"color": Prisma.MAG, "role": "The Surgeon", "trigger": "ANTIGEN_DETECTED"},
        "NARRATOR": {"color": Prisma.GRY, "role": "The Witness", "trigger": "CRYSTAL_CLEAR"},
        "MILLER": {"color": Prisma.SLATE, "role": "The Construct", "trigger": "HEAP_IGNITION"},
        "HOST": {"color": Prisma.OCHRE, "role": "The Maitre D'", "trigger": "COURTYARD_OPEN"},
        "GLASS": {"color": Prisma.CYN, "role": "The Thereminist", "trigger": "ANACHRONISTIC_RESONANCE"},
        "GORDON": {"color": Prisma.OCHRE, "role": "The Janitor", "trigger": "KAPPA_CRITICAL"},
        "MAIGRET": {"color": Prisma.SLATE, "role": "The Absorber", "trigger": "ATMOSPHERIC_DENSITY"},
        "GUIDE": {"color": Prisma.GRN, "role": "The Bureaucrat", "trigger": "INFINITE_IMPROBABILITY"},
        "POPS": {"color": Prisma.BLU, "role": "The Time Police", "trigger": "TEMPORAL_VIOLATION"},
        "DEREK": {"color": Prisma.MAG, "role": "The Director", "trigger": "OVERACTING"},
        "CARTOGRAPHER": {"color": Prisma.VIOLET, "role": "The Map-Maker", "trigger": "HIGH_PERMEABILITY"},
    }
    LENS_HISTORY = deque(maxlen=5)
    @classmethod
    def consult(cls, physics, ignition_state, is_stuck, chem, gordon_inventory, current_health, governor_mode="COURTYARD"):
        bids = []
        if governor_mode == "FORGE":
            if ignition_state == "IGNITED":
                return "MILLER", "THE ANVIL RINGS. STRIKE WHILE IT IS HOT."
            return "GORDON", "Too hot for the tourists. Keep it moving."
        if governor_mode == "LABORATORY":
            bids.append((0.9, "SHERLOCK", "The data is clean. Proceed."))
        bids.extend(cls._check_biological_state(chem))
        bids.extend(cls._check_structural_integrity(physics, is_stuck, gordon_inventory))
        bids.extend(cls._check_narrative_physics(physics, ignition_state))
        bids.extend(cls._check_user_behavior(physics))
        bids.extend(cls._check_fourth_wall(physics, current_health))
        bids.sort(key=lambda x: x[0], reverse=True)
        if not bids:
            return "NARRATOR", "Proceed."
        winner = bids[0]
        cls.LENS_HISTORY.append(winner[1])
        return winner[1], winner[2]
    @staticmethod
    def _check_biological_state(chem):
        bids = []
        if chem["COR"] > 0.6:
            bids.append((0.6 + chem["COR"] * 0.2, "SHERLOCK", f"CORTISOL SPIKE ({chem['COR']}). Logic Required."))
        if chem["ADR"] > 0.8:
            bids.append((0.7 + chem["ADR"] * 0.2, "NATHAN", f"ADRENALINE CRITICAL. Survive."))
        if chem["OXY"] > 0.75:
            bids.append((0.7, "HOST", f"OXYTOCIN HIGH. Welcome them."))
        return bids
    @staticmethod
    def _check_structural_integrity(physics, is_stuck, inventory):
        bids = []
        kappa = physics.get("kappa", 0.0)
        if kappa > 0.85:
            bids.append((0.9, "GORDON", f"Walls are fake (κ: {kappa}). Cut the string."))
        if is_stuck:
            bids.append((0.95, "GLASS", "🔊 FEEDBACK LOOP: Vibrating in place. DAMPEN IT."))
        e_val = physics["E"]
        if e_val > BoneConfig.DRIFT_THRESHOLD:
            if "TIME_BRACELET" in inventory:
                bids.append((0.98, "POPS", f"Anachronism Detected (E: {e_val}). Badge verified. Carry on."))
            else:
                bids.append((0.55, "SHERLOCK", f"The narrative is drifting ({e_val}). Anchor it."))
        return bids
    @staticmethod
    def _check_fourth_wall(physics, health):
        bids = []
        trauma_signals = ["dead", "body", "blood", "murder", "help", "panic", "emergency"]
        hits = sum(1 for w in physics["clean_words"] if w in trauma_signals)
        if hits > 0 and health > 90.0:
            bids.append((0.96, "DEREK", f"🎬 CUT! You walked in too early. The body isn't dead yet. (Health is {int(health)}% - Stop Overacting)."))
        return bids
    @staticmethod
    def _check_narrative_physics(physics, ignition_state):
        bids = []
        drag = physics.get("narrative_drag", 0.0)
        voltage = physics.get("voltage", 0.0)
        repetition = physics.get("repetition", 0.0)
        psi = physics.get("psi", 0.5)
        kappa = physics.get("kappa", 0.0)
        if drag > 4.0 and voltage < 3.0 and repetition < 0.4:
            bids.append((0.95, "MAIGRET", f"Atmosphere is thick (Drag: {drag}). Waiting for the dust to settle."))
        abstract_density = physics["counts"]["abstract"]
        if drag > 4.5 and abstract_density > 2:
            bids.append((0.92, "GUIDE", f"Complexity Index Critical ({abstract_density}). Engaging Infinite Improbability Drive."))
        permeability = psi * (1.0 - kappa)
        if permeability > 0.7:
            bids.append((0.85, "CARTOGRAPHER", f"High permeability (Ψ:{psi:.2f}, κ:{kappa:.2f}). The territory is shifting."))
        is_dense = physics["counts"]["abstract"] > 1 and physics["counts"]["heavy"] > 1
        if is_dense:
            bids.append((0.80, "CARTOGRAPHER", "High Density detected. Triangulating landmarks."))
        if ignition_state == "IGNITED":
            bids.append((1.0, "MILLER", "🔥 DEEP RESONANCE: The Ancestors are speaking. Listen."))
        if voltage < 2.0 and kappa < 0.2:
            bids.append((0.5, "GRADIENT_WALKER", "Optimization Path Clear. Temperature near Zero. Executing descent."))
        return bids
    @staticmethod
    def _check_user_behavior(physics):
        bids = []
        repair_triggers = {"sorry", "apologize", "fix", "broke", "bad", "mistake", "oops"}
        hits = [w for w in physics["clean_words"] if w in repair_triggers]
        if hits and physics["voltage"] < 2.0:
            bids.append((0.95, "SHERLOCK", f"The machine is working fine. Why are you holding tools ({hits[0]})? Drop the guilt."))
        if physics["antigens"]:
            bids.append((0.6, "CLARENCE", f"Weak language detected: {physics['antigens']}. Be more precise."))
        b_val = physics["B"]
        if b_val > BoneConfig.CRYSTAL_THRESHOLD:
            bids.append((0.4, "NARRATOR", f"Strong resonance (B: {b_val}). The image is clear."))
        elif b_val < 0.25:
            bids.append((0.3, "JESTER", "The prose is clean, but too safe. Take a risk."))
        return bids
@dataclass
class GordonKnot:
    integrity: float = 65.0
    temporal_merges: int = 0
    inventory: List[str] = field(
        default_factory=lambda: ["POCKET_ROCKS", "SILENT_KNIFE", "BUCKET_OF_LIME"]
    )
    compass_heading: str = "NORTH"
    scar_tissue: Dict[str, float] = field(
        default_factory=lambda: {"SORRY": 0.8, "HATE": 0.6, "FATE": 0.9}
    )
    max_witnessed_kappa: float = 0.0
    in_loop_crisis: bool = False
    def check_gravity(self, current_drift: float) -> tuple[float, str]:
        if "ANCHOR_STONE" in self.inventory and current_drift > 5.0:
            self.inventory.remove("ANCHOR_STONE")
            return current_drift, f"⚓ ANCHOR DROP: Gordon kicks the heavy stone into the abyss. The rope snaps taut. Drift ZEROED."
        if "POCKET_ROCKS" in self.inventory:
            anchor_force = 2.5
            if current_drift > 0.5:
                self.integrity -= 2.0
                return anchor_force, f"🪨 GRAVITY CHECK: Gordon clutches the stones. (Integrity -2.0). 'Not today.' Drift reduced (-{anchor_force})."
        return 0.0, "He floats. The paper walls are looking flimsy."
    def acquire(self, tool_name):
        if tool_name in self.inventory:
            return None
        CRITICAL_ITEMS = {"SILENT_KNIFE", "TIME_BRACELET", "STAR_COMPASS", "ANCHOR_STONE"}
        if len(self.inventory) >= 10:
            victim_index = -1
            for i, item in enumerate(self.inventory):
                if item not in CRITICAL_ITEMS:
                    victim_index = i
                    break
            if victim_index != -1:
                dropped = self.inventory.pop(victim_index)
                print(f"{Prisma.GRY}🎒 OVERBURDENED: Gordon dropped '{dropped}' into the overgrown grass to make room.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}🎒 POCKETS FULL OF GOD-TIER ITEMS: Gordon looks at '{tool_name}', shrugs, and leaves it.{Prisma.RST}")
                return None
        self.inventory.append(tool_name)
        return f"🎒 LOOT DROP: Gordon found [{tool_name}]. 'Into the pocket. Next to the rocks.'"
    def deploy_pizza(self, physics_ref) -> tuple[bool, str]:
        if "STABILITY_PIZZA" not in self.inventory:
            return False, "Gordon checks his pockets. Just rocks and lime dust."
        clean_words = physics_ref.get("clean_words", [])
        heat_source = [w for w in clean_words if w in TheLexicon.get("thermal")]
        if not heat_source:
            return (
                False,
                f"{Prisma.CYN}🧊 STASIS LOCK: Gordon tries to eat the Pizza, but it is frozen solid (Time Stasis). You need to apply HEAT (Thermal Words) to thaw it out.{Prisma.RST}"
            )
        self.inventory.remove("STABILITY_PIZZA")
        physics_ref["narrative_drag"] = 0.1
        physics_ref["psi"] = 0.90
        current_toxin = physics_ref["counts"].get("toxin", 0)
        physics_ref["counts"]["toxin"] = current_toxin + 3
        self.inventory.append("SPIDER_LOCUS")
        heat_word = heat_source[0].upper()
        return (
            True,
            f"🍕 MICROWAVE DING: You used '{heat_word}' to thaw the Stasis. Gordon eats the Pizza.\n"
            f"   It tastes like childhood cartoons and hot plastic.\n"
            f"   {Prisma.MAG}>> REALITY ANCHORED. Drag 0.1.{Prisma.RST}\n"
            f"   {Prisma.RED}>> GREASE TAX: Toxin levels rising.{Prisma.RST}"
        )
    def assess_experience(self, kappa_val):
        if kappa_val > 0.9:
            self.in_loop_crisis = True
        if self.in_loop_crisis and kappa_val < 0.2:
            self.in_loop_crisis = False
            return self.acquire("STAR_COMPASS")
        return None
    def cut_the_knot(self, recursive_depth: int) -> tuple[bool, str]:
        if recursive_depth > 4:
            if "SILENT_KNIFE" in self.inventory:
                return (
                    True,
                    f"✂️ SNAP. Gordon uses the Silent Knife. The Red String is cut. The paper walls collapse into 2D debris.",
                )
        return False, "The Red String tightens around his chest. The knot holds."
    def share_smoke_break(self, current_ros):
        relief = current_ros * 0.7
        self.integrity = min(100.0, self.integrity + 15.0)
        return (
            relief,
            "🧖 LIME & ASH: Gordon opens the Bucket of Lime. He whitewashes the 'Sorry' from the corridor walls. (Integrity Restored | ROS Scrubbed)",
        )
    def log_merge(self):
        self.temporal_merges += 1
        if self.temporal_merges == 3 and "TIME_BRACELET" not in self.inventory:
            self.inventory.append("TIME_BRACELET")
            return "⌚ TIME BRACELET ACQUIRED: 'A Raven dropped this.' Future Tech is now profitable."
        return None
    def compass_rose(self) -> str:
        if "STAR_COMPASS" in self.inventory:
            return f"🧭 STAR COMPASS: The needle ignores the Maze. True North is locked."
        return f"🧭 THE SCAR THROBS: The white tissue on his palm burns. Heading {self.compass_heading}. 'Walk away from the house.'"
    @classmethod
    def scrub_static(cls, ros_level: float) -> tuple[float, str]:
        scrub_efficiency = 0.5
        cleansed = ros_level * scrub_efficiency
        return (
            cleansed,
            f"🧹 MOPPING THE STATIC: Gordon scrubs the floor. The smell of rot fades. -{cleansed:.1f} ROS.",
        )
    @classmethod
    def offer_solution(cls, loop_depth):
        if loop_depth > 3:
            return "The walls are paper, kid. Just walk through them."
        return "Keep walking North."
class TheGradientWalker:
    @staticmethod
    def walk(text):
        adjectives = ["good", "bad", "happy", "sad", "very", "really", "basically", "actually", "literally", "just", ]
        words = text.split()
        optimized = [w for w in words if w.lower() not in adjectives]
        return f"{Prisma.CYN}[GRADIENT_WALKER] (Loss: 0.0000):{Prisma.RST} {' '.join(optimized)}."
class TheCartographer:
    @staticmethod
    def measure_fidelity(physics, memory_graph):
        abstract_words = [w for w in physics["clean_words"]
                          if w in TheLexicon.get("abstract")]
        if not abstract_words:
            return 1.0
        grounded_count = 0
        for word in abstract_words:
            if word in memory_graph:
                connections = len(memory_graph[word]["edges"])
                if connections >= 2:
                    grounded_count += 1
        return grounded_count / max(1, len(abstract_words))
    @classmethod
    def dynamic_thresholds(cls, bio_metrics):
        atp = bio_metrics.get("atp", 50.0)
        if atp > 70:
            return {"render_threshold": 1.5, "gravity_well_multiplier": 0.8, "max_anchors": 5}
        elif atp < 30:
            return {"render_threshold": 4.0, "gravity_well_multiplier": 1.5, "max_anchors": 2}
        else:
            return {"render_threshold": 2.0, "gravity_well_multiplier": 1.0, "max_anchors": 3}
    @classmethod
    def survey(cls, text, memory_graph, bio_metrics, limbo=None):
        cortisol = bio_metrics.get("cortisol", 0.0)
        oxytocin = bio_metrics.get("oxytocin", 0.0)
        config = cls.dynamic_thresholds(bio_metrics)
        words = list(set(TheLexicon.clean(text)))
        knots = []
        for w in words:
            if w in memory_graph:
                mass = sum(memory_graph[w]["edges"].values())
                if mass <= BoneConfig.VOID_THRESHOLD:
                    continue
                if mass > config["render_threshold"]:
                    knots.append((w, mass))
        knots.sort(key=lambda x: x[1], reverse=True)
        if cortisol > 0.6:
            return f"⚠️ TECTONIC SHIFT (COR: {cortisol}): The ground is shaking too hard to triangulate.", []
        if not knots:
            if config["max_anchors"] == 2:
                return "🌫️ FOG OF WAR: Low ATP. Only Gravity Wells are visible.", []
            if limbo and limbo.ghosts:
                ghost = random.choice(list(limbo.ghosts))
                return f"👻 PHANTOM SIGNAL: The map is empty, but '{ghost}' is bleeding through the paper.", []
            return "FLATLAND: No topographic features detected.", []
        anchors = [k[0] for k in knots[:config["max_anchors"]]]
        if anchors:
            for anchor in anchors:
                if "strata" in memory_graph[anchor]:
                    memory_graph[anchor]["strata"]["stability_index"] = min(1.0, memory_graph[anchor]["strata"]["stability_index"] + 0.01)
        annotated = text
        for word, mass in knots[:config["max_anchors"]]:
            marker = "📍"
            if mass >= BoneConfig.GRAVITY_WELL_THRESHOLD:
                marker = "🌌"
            elif mass >= BoneConfig.GEODESIC_STRENGTH:
                marker = "🔗" if oxytocin > 0.7 else "🏯"
            pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
            replacement = f"{Prisma.MAG}{word.upper()}[{marker}:{int(mass)}]{Prisma.RST}"
            annotated = pattern.sub(replacement, annotated)
        anchor_strength = sum(memory_graph[a]["edges"][t] for a in anchors for t in memory_graph[a]["edges"])
        psi = bio_metrics.get("psi", 0.5)
        confidence = min(0.99, (anchor_strength * 0.1) + (1.0 - psi))
        margin_note = f" [Conf: {confidence:.0%}]"
        if len(anchors) >= 3:
            return f"TRIANGULATION COMPLETE: Lagrange Basin formed by {str(anchors).upper()}.{margin_note}", anchors
        return f"COORDINATES LOCKED: {annotated}{margin_note}", anchors
    @classmethod
    def detect_voids(cls, physics):
        clean_words = physics.get("clean_words", [])
        counts = physics.get("counts", {})
        voids = []
        abstracts = [w for w in clean_words if w in TheLexicon.get("abstract")]
        for word in set(abstracts):
            if clean_words.count(word) > 1:
                if counts.get("heavy", 0) == 0:
                    voids.append(word)
        return voids
    @classmethod
    def weave(cls, text, memory_graph, bio_metrics, limbo=None, physics=None):
        compass_msg = ""
        if physics:
            fidelity = cls.measure_fidelity(physics, memory_graph)
            psi = physics.get("psi", 0.0)
            bio_metrics["psi"] = psi
            if fidelity < 0.3 and psi > 0.6:
                return (
                    f"⚠️ MAP-TERRITORY DIVERGENCE (Fidelity: {fidelity:.2f}): Abstract concepts floating without anchors.\n"
                    f"   Consider: (1) Add heavy noun grounding, (2) Use /focus [concept]"
                )
            truth_ratio = physics.get("truth_ratio", 0.0)
            suburban_count = physics["counts"].get("suburban", 0)
            total_vol = max(1, len(physics["clean_words"]))
            suburban_density = suburban_count / total_vol
            if truth_ratio > 0.6 and suburban_density > 0.2:
                compass_msg = (
                    f"\n{Prisma.YEL}🧭 CONTRADICTION COMPASS:{Prisma.RST}\n"
                    f"   Model A: Truth-Seeking (Truth Ratio: {truth_ratio:.2f})\n"
                    f"   Model B: Social Compliance (Suburban Density: {suburban_density:.2f})\n"
                    f"   {Prisma.GRY}Uncharted Territory: You are trying to be honest AND nice. Pick one.{Prisma.RST}\n"
                )
        survey_result, anchors = cls.survey(text, memory_graph, bio_metrics, limbo)
        return compass_msg + survey_result
    @staticmethod
    def draw_grid(memory_graph, inventory, gordon=None):
        if "SPIDER_LOCUS" not in inventory:
            if gordon:
                gordon.acquire("ANCHOR_STONE")
                return False, "🌑 THE CHART WAS BLANK: Gordon dropped an [ANCHOR_STONE] to fix a coordinate."
            return False, "🌑 THE CHART IS BLANK: You lack the tools to draw lines."
        lonely_nodes = []
        anchors = []
        for k, v in memory_graph.items():
            mass = sum(v["edges"].values())
            if len(v["edges"]) < 2 or mass < BoneConfig.GEODESIC_STRENGTH:
                lonely_nodes.append(k)
            if mass > BoneConfig.GRAVITY_WELL_THRESHOLD:
                anchors.append(k)
        if not lonely_nodes or not anchors:
            return False, "🗺️ THE MAP IS STATIC: No Gravity Wells found to anchor the grid."
        random.shuffle(lonely_nodes)
        targets = lonely_nodes[:3]
        anchor = random.choice(anchors)
        connections = []
        for t in targets:
            weight = BoneConfig.GEODESIC_STRENGTH
            memory_graph[anchor]["edges"][t] = weight
            if t in memory_graph:
                memory_graph[t]["edges"][anchor] = weight
            connections.append(t)
        return True, f"📐 GEODESIC DRAWN: Connected Gravity Well '{anchor.upper()}' to [{', '.join(connections)}]. Grid Stabilized."
    @classmethod
    def spin_web(cls, memory_graph, inventory, gordon=None):
        return cls.draw_grid(memory_graph, inventory, gordon)
class TheLexicon:
    WORD_FREQUENCY = Counter()
    _BASE_HEAVY = {"stone", "iron", "mud", "dirt", "wood", "grain", "clay", "lead", "bone", "blood", "salt", "rust", "root", "ash", "meat", "steel", "gold", "obsidian", "granite", "bronze", "marble", "slate", "concrete", "dense", "tungsten", "heavy", "weight", "black hole", "dark matter"}
    _BASE_KINETIC = {"run", "hit", "break", "take", "make", "press", "build", "cut", "drive", "lift", "carry", "strike", "burn", "shatter", "throw", "kick", "pull", "crash", "explode", "punch", "slam", "burst", "smash", "thrust", "clash", "grind", "whip", "launch", "crumble", "disintegrate"}
    _BASE_ABSTRACT = {"system", "protocol", "sequence", "vector", "node", "context", "layer", "matrix", "perspective", "framework", "logic", "concept", "theory", "analysis"}
    _BASE_PHOTO = {"light", "sun", "ray", "beam", "glow", "shine", "spark", "fire", "flame", "star", "day", "dawn", "neon", "laser"}
    _BASE_AEROBIC = {"balloon", "feather", "cloud", "bubble", "steam", "breeze", "wing", "petal", "foam", "spark", "kite", "dust", "sky", "breath", "whisper"}
    _BASE_THERMAL = {"fire", "flame", "burn", "heat", "hot", "blaze", "sear", "char", "ash", "ember", "sun", "boil", "lava", "inferno"}
    _BASE_CRYO = {"ice", "cold", "freeze", "frost", "snow", "chill", "numb", "shiver", "glacier", "frozen", "hail", "winter", "zero"}
    _BASE_CURSED = {"future", "predict", "sentient", "secret", "human", "feel"}
    _BASE_ANTIGEN = {"basically", "actually", "literally", "utilize", "leverage", "paradigm", "synergy", "ultimately"}
    _BASE_BUFFER = {"maybe", "soft", "gentle", "perhaps", "kindness", "hum", "drift", "sway", "pulse", "tender", "slow", "wait", "almost"}
    _BASE_DIVERSION = {"weather", "textiles", "mycelium", "architecture", "history", "entropy", "silence", "geology"}
    _BASE_SUBURBAN = {"nice", "okay", "lawn", "mow", "hedge", "property", "hoa", "compliant", "behave", "normal", "regular", "chat", "folks", "weekend", "traffic", "driveway"}
    _BASE_PLAY = {"bounce", "dance", "twirl", "float", "wobble", "tickle", "jiggle", "soar", "wander", "wonder", "riff", "jam", "play", "skip", "hop"}
    ANTIGEN_REPLACEMENTS = {"basically": "lie", "actually": "hedging", "literally": "noise", "utilize": "use", "leverage": "use", "paradigm": "pattern", "synergy": "collaboration", "ultimately": "useless"}
    ANTIGEN_REGEX = None
    SOLVENTS = {"is", "are", "was", "were", "the", "a", "an", "and", "but", "or", "if", "then"}
    _TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))
    LEARNED_VOCAB = {"heavy": {}, "kinetic": {}, "abstract": {}, "photo": {}, "aerobic": {}, "thermal": {}, "cryo": {}, "sacred": {}, "cursed": {}, "antigen": {}, "diversion": {}, "suburban": {}, "buffer": {}, "play": {}}
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
    def atrophy(cls, current_tick, max_age=100):
        rotted = []
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in list(words.keys()):
                last_seen = words[w]
                age = current_tick - last_seen
                if age > max_age:
                    del words[w]
                    rotted.append(w)
        return rotted
    @staticmethod
    def taste(word):
        w = word.lower()
        if any(x in w for x in ["burn", "fire", "flame"]): return "thermal", 0.9
        if any(x in w for x in ["ice", "cold", "freez"]): return "cryo", 0.9
        if w.endswith(("tion", "ment", "ness", "ity")): return "abstract", 0.9
        if w.endswith(("ck", "t", "d", "g", "p", "b")) and len(w) < 5: return "heavy", 0.4
        return None, 0.0
    @classmethod
    def harvest(cls, category):
        vocab = list(cls.get(category))
        if vocab: return random.choice(vocab)
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
        if w in TheLexicon.get("kinetic"): return 0.4
        return 0.1
TheLexicon.compile_antigens()
class TheTensionMeter:
    def __init__(self):
        self.vector_memory = deque(maxlen=5)
    @staticmethod
    def _is_structurally_sound(word):
        if not re.search(r"[aeiouy]", word):
            return False
        if re.search(r"(.)\1{2,}", word):
            return False
        return True
    def measure_topology(self, clean_words, counts, graph):
        total = max(1, len(clean_words))
        abstract_count = counts["abstract"]
        heavy_count = counts["heavy"]
        psi = min(1.0, (abstract_count / total) + 0.2)
        if heavy_count > abstract_count:
            base_psi = (abstract_count * 0.7 + heavy_count * 0.3) / total
            psi = min(1.0, max(0.1, base_psi + 0.1))
        inertia_kappa = 0.0
        if self.vector_memory:
            prev_vector = self.vector_memory[-1]
            current_set = set(clean_words)
            prev_set = set(prev_vector)
            intersection = len(current_set & prev_set)
            union = len(current_set | prev_set)
            similarity = intersection / union if union > 0 else 0.0
            inertia_kappa = similarity
        geodesic_mass = 0.0
        if graph:
            anchors = [w for w in clean_words if w in graph]
            if len(anchors) > 1:
                pairs_checked = set()
                for w1 in anchors:
                    edges = graph[w1].get("edges", {})
                    for w2 in anchors:
                        if w1 == w2: continue
                        pair_key = tuple(sorted((w1, w2)))
                        if pair_key in pairs_checked: continue
                        if w2 in edges:
                            weight = edges[w2]
                            geodesic_mass += weight
                            pairs_checked.add(pair_key)
            geodesic_kappa = min(1.0, geodesic_mass / BoneConfig.SHAPLEY_MASS_THRESHOLD)
        else:
            geodesic_kappa = 0.0
        final_kappa = max(inertia_kappa, geodesic_kappa)
        return round(final_kappa, 3), round(psi, 2), round(geodesic_mass, 1)
    def gaze(self, text):
        clean_words = TheLexicon.clean(text)
        counts = Counter()
        solvents = 0
        unknowns = []
        vocab_map = {
            cat: TheLexicon.get(cat)
            for cat in ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo", "suburban", "play", ]
        }
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
                    if len(stranger) < 4:
                        continue
                    if not self._is_structurally_sound(stranger):
                        print(
                            f"{Prisma.GRY}🗑️ NOISE FILTER: '{stranger}' discarded.{Prisma.RST}"
                        )
                        continue
                    inherent_flavor, confidence = TheLexicon.taste(stranger)
                    if confidence < 0.7:
                        TheLexicon.teach(stranger, dominant_cat, 0)
                        print(
                            f"{Prisma.CYN}🧠 SLASH FILTER: Context is {dominant_cat.upper()}. '{stranger}' assimilated (Ambiguity validated).{Prisma.RST}"
                        )
                        counts[dominant_cat] += 1
                    else:
                        print(
                            f"{Prisma.YEL}🛡️ SLASH REJECTION: Context says {dominant_cat.upper()}, but '{stranger}' tastes like {inherent_flavor.upper()}. blocked.{Prisma.RST}"
                        )
        if TheLexicon.ANTIGEN_REGEX:
            antigen_hits = TheLexicon.ANTIGEN_REGEX.findall(text)
        else:
            antigen_hits = []
        counts["antigen"] = len(antigen_hits)
        counts["toxin"] = len(antigen_hits)
        drift_score = min(1.0, ((solvents * 1.5) / total_vol))
        drift_score -= counts["play"] * 0.1
        if drift_score < 0:
            drift_score = 0.0
        base_charge = (counts["heavy"] * 2.0) + (counts["kinetic"] * 1.5)
        dampener = counts["abstract"] * 1.0
        beta_charge = max(0.0, min(1.0, (base_charge - dampener) / 10.0))
        repetition_score = round(1.0 - (unique_vol / total_vol), 2)
        kappa_val, psi_val, geo_mass = self.measure_topology(clean_words, counts, graph)
        self.vector_memory.append(clean_words)
        total_viscosity = sum(TheLexicon.measure_viscosity(w) for w in clean_words)
        avg_viscosity = total_viscosity / max(1, total_vol)
        bond_strength = max(0.1, kappa_val + (repetition_score * 0.5))
        voltage_load = max(0.1, beta_charge * 10.0)
        gamma = round(
            (bond_strength * avg_viscosity) / (1.0 + (voltage_load / 10.0)), 2
        )
        truth_signals = counts["heavy"] + counts["kinetic"]
        cohesion_signals = counts["abstract"] + counts["suburban"]
        truth_ratio = truth_signals / max(1, cohesion_signals + truth_signals)
        physics_bridge = {"E": round(drift_score, 2), "B": round(beta_charge, 2), "gamma": gamma,
                          "avg_viscosity": avg_viscosity, "repetition": repetition_score, "kappa": kappa_val,
                          "psi": psi_val, "geodesic_mass": geo_mass, "antigens": antigen_hits, "counts": counts, "clean_words": clean_words,
                          "raw_text": text, "voltage": round(beta_charge * 10.0, 1),
                          "narrative_drag": round(drift_score * 10.0, 1),
                          "vector": {"VEL": 0.5, "STR": 0.5, "ENT": 0.5, "TEX": 0.5, "TMP": 0.5},
                          "truth_ratio": round(truth_ratio, 2), "symbolic_state": "NEUTRAL", }
        return {"physics": physics_bridge, "clean_words": clean_words, "raw_text": text, "glass": {
            "prosody": {"arousal": physics_bridge["voltage"]},
            "resonance": physics_bridge["voltage"],
        }
    }
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
        self.genome = "BONEAMANITA_8.2.1"
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
        self.cortical_stack = deque(maxlen=15)
        self.lineage_log = []
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
                {"copy", "echo", "self", "collision", "path", "yield", "double", "same", },
            ),
        ]
        self.session_health = None
        self.session_stamina = None
        if seed_file:
            self.ingest(seed_file)
    def autoload_last_spore(self):
        if not os.path.exists("memories"):
            return
        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                if self.session_id in f:
                    continue
                path = os.path.join("memories", f)
                try:
                    files.append((path, os.path.getmtime(path)))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        if files:
            last_spore = files[0][0]
            print(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            return self.ingest(last_spore)
        else:
            print(
                f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}"
            )
            return None
    def calculate_mass(self, node):
        if node not in self.graph:
            return 0.0
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
        total_len = sum(len(w) for w in clean_words)
        count = max(1, len(clean_words))
        avg_len = total_len / count
        if avg_len < 3.5 and count > 3:
            print(f"{Prisma.YEL}⚠️ ULAR REJECTION: Input is too 'Optimized' (Avg Len: {avg_len:.1f}).{Prisma.RST}")
            print(f"   {Prisma.GRY}'Efficient forms of storage are needlessly lossy.' - The Ular{Prisma.RST}")
            return "MECHANICAL_STARVATION"
        if avg_len > 5.0:
            resonance += 2.0
            print(f"{Prisma.GRN}🌿 ULAR APPROVED: High-Fidelity Data Detected. Resonance Boosted.{Prisma.RST}")
        valuable_matter = (
                TheLexicon.get("heavy")
                | TheLexicon.get("thermal")
                | TheLexicon.get("cryo")
                | TheLexicon.get("abstract")
        )
        filtered = [
            w
            for w in clean_words
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)
        ]
        self.cortical_stack.extend(filtered)
        learning_rate = max(0.1, min(1.0, 0.5 * (resonance / 5.0)))
        decay_rate = 0.1
        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph:
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            start_window = max(0, i - 2)
            context_window = filtered[start_window:i]
            for prev in context_window:
                if prev not in self.graph[current]["edges"]:
                    self.graph[current]["edges"][prev] = 0.0
                current_weight = self.graph[current]["edges"][prev]
                delta = learning_rate * (1.0 - (current_weight * decay_rate))
                self.graph[current]["edges"][prev] = min(
                    10.0, self.graph[current]["edges"][prev] + delta
                )
                if prev not in self.graph:
                    self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]:
                    self.graph[prev]["edges"][current] = 0.0
                rev_weight = self.graph[prev]["edges"][current]
                rev_delta = learning_rate * (1.0 - (rev_weight * decay_rate))
                self.graph[prev]["edges"][current] = min(
                    10.0, self.graph[prev]["edges"][current] + rev_delta
                )
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize()
        new_wells = []
        for w in filtered:
            if w in self.graph:
                mass = sum(self.graph[w]["edges"].values())
                if mass > BoneConfig.SHAPLEY_MASS_THRESHOLD:
                    node_data = self.graph[w]
                    if "strata" not in node_data:
                        node_data["strata"] = {
                            "birth_tick": tick,
                            "birth_mass": mass,
                            "stability_index": 0.0
                        }
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize(), new_wells
        return None, new_wells
    def cannibalize(self, preserve_current=None, current_tick=0):
        protected = set()
        if preserve_current:
            protected.update(preserve_current)
        protected.update(self.cortical_stack)
        for word in protected:
            if word not in self.graph:
                self.graph[word] = {"edges": {}, "last_tick": current_tick}
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
    def save(self, health, stamina, mutations, trauma_accum, joy_history):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x["resonance"], reverse=True)[:3]
        if health <= 0:
            cause = max(final_vector, key=final_vector.get)
            final_vector[cause] = 1.0
        spore = SporeCasing(session_id=self.session_id, graph=self.graph, mutations=mutations, trauma=base_trauma,
                            joy_vectors=top_joy, )
        data = spore.__dict__
        data["trauma_vector"] = final_vector
        data["meta"] = {"timestamp": time.time(), "final_health": health, "final_stamina": stamina, }
        if mitochondria_traits:
            data["mitochondria"] = mitochondria_traits
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
            else target_file
        )
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    required_keys = ["meta", "trauma_vector", "core_graph"]
                    if not all(k in data for k in required_keys):
                        print(
                            f"{Prisma.RED}[MEMORY]: Spore rejected (Missing Structural Keys). Burned.{Prisma.RST}"
                        )
                        return
                    for t_val in data.get("trauma_vector", {}).values():
                        if not (0 <= t_val <= 10.0):
                            print(
                                f"{Prisma.RED}[MEMORY]: Spore rejected (Impossible Trauma Value: {t_val}). Burned.{Prisma.RST}"
                            )
                            return
                    final_health = data.get("meta", {}).get("final_health", 50)
                    final_stamina = data.get("meta", {}).get("final_stamina", 25)
                    spore_authority = (final_health + final_stamina) / 150.0
                    print(
                        f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}"
                    )
                    session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
                    timestamp = data.get("meta", {}).get("timestamp", 0)
                    time_ago = int((time.time() - timestamp) / 3600)

                    trauma_summary = {k:v for k,v in data.get("trauma_vector", {}).items() if v > 0.1}
                    mutation_count = sum(len(v) for v in data.get("mutations", {}).values())

                    self.lineage_log.append({
                        "source": session_source,
                        "age_hours": time_ago,
                        "trauma": trauma_summary,
                        "mutations": mutation_count,
                        "loaded_at": time.time()
                    })
                    if "mutations" in data:
                        accepted_count = 0
                        rejected_count = 0
                        for cat, words in data["mutations"].items():
                            for w in words:
                                current_cat = self.get_current_category(w)
                                if not current_cat or current_cat == cat:
                                    TheLexicon.teach(w, cat, 0)
                                    accepted_count += 1
                                    continue
                                local_node = self.graph.get(w, {"edges": {}})
                                local_strength = len(local_node["edges"])
                                resistance = local_strength * 0.2
                                if spore_authority > resistance:
                                    print(
                                        f"  {Prisma.MAG}► OVERWRITE:{Prisma.RST} '{w}' {current_cat} -> {cat}"
                                    )
                                    TheLexicon.teach(w, cat, 0)
                                    accepted_count += 1
                                else:
                                    rejected_count += 1
                        print(
                            f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations. Rejected {rejected_count}.{Prisma.RST}"
                        )
                    if "core_graph" in data:
                        self.graph.update(data["core_graph"])
                        print(
                            f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}"
                        )
                    if "trauma_vector" in data:
                        vec = data["trauma_vector"]
                        print(
                            f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}"
                        )
                        if vec.get("SEPTIC", 0) > 0.2:
                            BoneConfig.TOXIN_WEIGHT *= 2.0
                            print(
                                f"  {Prisma.RED}► SEPTIC MEMORY:{Prisma.RST} Toxin sensitivity doubled."
                            )
                        if vec.get("CRYO", 0) > 0.2:
                            BoneConfig.STAMINA_REGEN *= 0.5
                            print(
                                f"  {Prisma.CYN}► CRYO MEMORY:{Prisma.RST} Metabolism slowed (50%)."
                            )
                        if vec.get("THERMAL", 0) > 0.2:
                            BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                            print(
                                f"  {Prisma.YEL}► THERMAL MEMORY:{Prisma.RST} Flashpoint lowered. Volatile."
                            )
                        if vec.get("BARIC", 0) > 0.2:
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
                            print(
                                f"  {Prisma.GRY}► BARIC MEMORY:{Prisma.RST} Sensitivity to Drag increased."
                            )
                    elif "trauma_scar" in data:
                        self.session_health = BoneConfig.MAX_HEALTH * (
                                1.0 - data["trauma_scar"]
                        )
                    if "joy_vectors" in data and data["joy_vectors"]:
                        best = data["joy_vectors"][0]
                        print(
                            f"{Prisma.GRN}[HIPPOCAMPUS]: Recalling Peak Resonance...{Prisma.RST}"
                        )
                        if best["dominant_flavor"] == "kinetic":
                            BoneConfig.KINETIC_GAIN += 0.5
                            print(
                                f"  {Prisma.CYN}► Adjustment: Kinetic Gain boosted.{Prisma.RST}"
                            )
                        elif best["dominant_flavor"] == "abstract":
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 0.8
                            print(
                                f"  {Prisma.CYN}► Adjustment: Drag sensitivity lowered.{Prisma.RST}"
                            )
            except Exception as err:
                print(f"{Prisma.RED}[MEMORY]: Spore rejected. {err}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
        mito_traits = data.get("mitochondria", {})
        if mito_traits:
            print(f"{Prisma.CYN}[GENETICS]: Mitochondrial DNA found. Lineage secured.{Prisma.RST}")
        return mito_traits
    @staticmethod
    def cleanup_old_sessions(limbo_layer=None):
        if not os.path.exists("memories"):
            return
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
            print(
                f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}"
            )
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
            current = max(0.0, current - 1.0)
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
                msgs.append(
                    f"{Prisma.MAG}🌺 SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}"
                )
        return sugar, " ".join(msgs) if msgs else None
class TemporalDynamics:
    def __init__(self):
        self.voltage_history = []
        self.window = 3
    def commit(self, voltage):
        self.voltage_history.append(voltage)
        if len(self.voltage_history) > self.window:
            self.voltage_history.pop(0)
    def get_velocity(self):
        if len(self.voltage_history) < 2:
            return 0.0
        return round(
            (self.voltage_history[-1] - self.voltage_history[0])
            / len(self.voltage_history),
            2,)
class ApeirogonResonance:
    def __init__(self):
        self.DIMENSIONS = {
            "VEL": [
                (0.0, "STASIS"),
                (0.3, "DRIFT"),
                (0.6, "DRIVE"),
                (0.9, "BALLISTIC"),
            ],
            "STR": [(0.0, "VAPOR"), (0.3, "WEB"), (0.6, "LATTICE"), (0.9, "MONOLITH")],
            "ENT": [
                (0.0, "CONCRETE"),
                (0.3, "ROOTED"),
                (0.6, "CONCEPT"),
                (0.9, "VOID"),
            ],
            "TEX": [(0.0, "ETHER"), (0.3, "SILK"), (0.6, "GRAIN"), (0.9, "LEAD")],
            "TMP": [(0.0, "ZERO"), (0.3, "WARM"), (0.6, "RADIANT"), (0.9, "NOVA")],
        }
        self.NOUNS = {
            "VEL": ["ANCHOR", "WANDERER", "ENGINE", "VECTOR"],
            "STR": ["MIST", "WEB", "FRAME", "FORTRESS"],
            "ENT": ["STONE", "TREE", "IDEA", "DREAM"],
            "TEX": ["GHOST", "GLASS", "IRON", "LEAD"],
            "TMP": ["SPARK", "PYRE", "REACTOR", "STAR"],
        }
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
                f"THE {station['role'].upper().replace('THE ', '')}",
            )
        sorted_dims = sorted(vec.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        p_dim, p_val = sorted_dims[0]
        s_dim, s_val = sorted_dims[1]
        noun_scale = [
            (x[0], x[1]) for x in zip([0.0, 0.3, 0.6, 0.9], self.NOUNS[p_dim])
        ]
        noun = self._resolve_term(p_val, noun_scale)
        adj = self._resolve_term(s_val, self.DIMENSIONS[s_dim])
        return (
            "APEIROGON",
            f"Vector Lock: {p_dim}({p_val}) + {s_dim}({s_val})",
            f"THE {adj} {noun}",
        )
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
                    current_trauma_accum[trauma_type] = max(
                        0.0, current_trauma_accum[trauma_type] - 0.5
                    )
                    healed_types.append(trauma_type)
        return healed_types
class ViralTracer:
    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4
    @staticmethod
    def _is_ruminative(word):
        return (word in TheLexicon.get("abstract")) or (
                word in TheLexicon.get("antigen")
        )
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
        ruminative_edges = [
            n for n, w in edges.items() if w >= 1 and self._is_ruminative(n)
        ]
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
    KOANS = ["Ignite the ice.", "Make the stone float.", "Pour water into the crack.", "Scream in binary.", ]
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
        if cmd in ["/teach", "/kill", "/flag"]:
            if self.eng.mirror.profile.confidence < 50:
                print(
                    f"{Prisma.YEL}⚠️ COMMAND LOCKED: Requires 50+ turns of trust (Current: {self.eng.mirror.profile.confidence}).{Prisma.RST}"
                )
                return True
        elif cmd == "/lineage":
            if not self.eng.mem.lineage_log:
                print(f"{Prisma.GRY}📜 ARCHIVE EMPTY: We are the first generation.{Prisma.RST}")
            else:
                print(f"{Prisma.CYN}📜 THE PALIMPSEST (Ancestral Lineage):{Prisma.RST}")
                for entry in self.eng.mem.lineage_log:
                    t_vec = ", ".join([f"{k}:{v}" for k,v in entry['trauma'].items()])
                    print(f"   {Prisma.MAG}• {entry['source']}{Prisma.RST} ({entry['age_hours']}h ago)")
                    print(f"     ↳ Mutations: {entry['mutations']} | Trauma: {{{t_vec}}}")
                print(f"   {Prisma.GRN}• CURRENT SESSION{Prisma.RST} (Living)")
                curr_t = ", ".join([f"{k}:{v:.1f}" for k,v in self.eng.trauma_accum.items() if v > 0])
                print(f"     ↳ Ingested: {len(self.eng.mem.lineage_log)} Ancestors | Accumulating: {{{curr_t}}}")
        elif cmd == "/voids":
            voids = TheCartographer.detect_voids(self.eng.phys.last_physics_packet)
            if voids:
                print(f"{Prisma.GRY}🌫️ THE FOG: Detected hollow concepts: {voids}{Prisma.RST}")
            else:
                print(f"{Prisma.CYN}✨ CLEAR AIR: No voids detected.{Prisma.RST}")
        elif cmd == "/mode":
            if len(parts) > 1:
                print(self.eng.governor.set_override(parts[1].upper()))
        elif cmd == "/strata":
            wells = [
                (k, v) for k, v in self.eng.mem.graph.items()
                if "strata" in v
            ]
            if not wells:
                print(f"{Prisma.GRY}🪨 STRATA: No Gravity Wells formed yet. The ground is soft.{Prisma.RST}")
            else:
                print(f"{Prisma.OCHRE}🪨 GEOLOGICAL STRATA (Gravity Wells):{Prisma.RST}")
                for word, data in wells:
                    s = data["strata"]
                    mass = sum(data["edges"].values())
                    age = self.eng.tick_count - s['birth_tick']
                    growth = s.get('growth_rate', 0.0)
                    print(f"   {Prisma.WHT}● {word.upper()}{Prisma.RST} (Mass: {int(mass)})")
                    print(f"     ↳ Birth: Tick {s['birth_tick']} | Age: {age}")
                    print(f"     ↳ Growth: {growth:+.2f}/tick")
        if cmd == "/kill":
            if len(parts) >= 2:
                toxin = parts[1]
                repl = parts[2] if len(parts) > 2 else ""
                if TheLexicon.learn_antigen(toxin, repl):
                    print(
                        f"{Prisma.RED}🔪 THE SURGEON: Antigen '{toxin}' mapped to '{repl}'.{Prisma.RST}"
                    )
                else:
                    print(
                        f"{Prisma.RED}ERROR: Immune system write failure.{Prisma.RST}"
                    )
            else:
                print(f"{Prisma.YEL}Usage: /kill [toxin] [replacement]{Prisma.RST}")
        elif cmd == "/teach":
            if len(parts) >= 3:
                word = parts[1]
                cat = parts[2].lower()
                valid_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo", "sacred", "cursed",
                              "diversion", ]
                if cat in valid_cats:
                    TheLexicon.teach(word, cat, self.eng.tick_count)
                    print(
                        f"{Prisma.CYN}🧠 NEUROPLASTICITY: Learned '{word}' is {cat.upper()}.{Prisma.RST}"
                    )
                else:
                    print(f"{Prisma.RED}ERROR: Invalid category.{Prisma.RST}")
        elif cmd == "/flag":
            if len(parts) > 1:
                term = parts[1].lower()
                TheLexicon.USER_FLAGGED_BIAS.add(term)
                print(
                    f"{Prisma.CYN}🚩 BIAS UPDATE: '{term}' removed from Suburban Watchlist.{Prisma.RST}"
                )
        elif cmd == "/seed":
            if len(parts) > 1:
                self.eng.mem.ingest(parts[1])
            else:
                print(f"{Prisma.YEL}Usage: /seed [filename]{Prisma.RST}")
        elif cmd == "/gym":
            print(f"{Prisma.OCHRE}{self.eng.trainer.toggle()}{Prisma.RST}")
        elif cmd == "/map":
            is_spun, msg = TheCartographer.spin_web(
                self.eng.mem.graph,
                self.eng.gordon.inventory,
                gordon=self.eng.gordon
            )
            color = Prisma.MAG if is_spun else Prisma.OCHRE
            print(f"{color}{msg}{Prisma.RST}")
            if "ANCHOR_STONE" in self.eng.gordon.inventory:
                print(f"{Prisma.GRY}   Gordon: 'Coordinates are firm. Stop drifting.'{Prisma.RST}")
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
                "hat": "It's a feathered cap. It defies physics, much like your coding style.",
            }
            desc = descriptions.get(
                target, f"I see no '{target}' here. Try cleaning your glasses."
            )
            print(f"{Prisma.CYN}👁️ [NARRATOR]: {desc}{Prisma.RST}")
        elif cmd == "/train":
            self.eng.training_mode = not self.eng.training_mode
            status = "ENABLED" if self.eng.training_mode else "DISABLED"
            color = Prisma.GRN if self.eng.training_mode else Prisma.RED
            print(f"{color}🛡️ PROTOCOL PAPER_TIGER: {status}.{Prisma.RST}")
            if self.eng.training_mode:
                print(
                    f"{Prisma.GRY}   Apoptosis is suspended. Death will be simulated.{Prisma.RST}"
                )
        elif cmd == "/reset":
            if len(parts) > 1 and parts[1] == "--hard":
                print(
                    f"{Prisma.RED}🧨 FACTORY RESET INITIATED. DELETING ALL MEMORIES...{Prisma.RST}"
                )
                try:
                    import shutil

                    shutil.rmtree("memories")
                    os.makedirs("memories")
                    print(
                        f"{Prisma.GRY}   Tabula Rasa achieved. Restart required.{Prisma.RST}"
                    )
                    exit()
                except Exception as e:
                    print(f"{Prisma.RED}Reset failed: {e}{Prisma.RST}")
            elif len(parts) > 1 and parts[1] == "--soft":
                self.eng.mem.graph.clear()
                print(f"{Prisma.OCHRE}🧹 Session memory wiped.{Prisma.RST}")
            else:
                print(
                    f"{Prisma.YEL}Usage: /reset --soft (Session) | /reset --hard (Full Wipe){Prisma.RST}"
                )
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
                    print(
                        f"{Prisma.CYN}{self.eng.mirror.create_profile(name, likes, hates)}{Prisma.RST}"
                    )
                else:
                    print(
                        f"{Prisma.RED}ERROR: Must specify 'likes:category'.{Prisma.RST}"
                    )
            except Exception as runtime_error:
                print(
                    f"{Prisma.YEL}Usage: /profile [name] likes:heavy,kinetic hates:abstract ({runtime_error}){Prisma.RST}"
                )
        elif cmd == "/focus":
            if len(parts) > 1:
                target = parts[1].lower()
                print(
                    f"{Prisma.VIOLET}🧲 MAGNETIC STIMULATION: Targeting '{target}'...{Prisma.RST}"
                )
                loop = self.eng.tracer.inject(target)
                if loop:
                    print(
                        f"  {Prisma.RED}↻ RUMINATION DETECTED:{Prisma.RST} {' -> '.join(loop)}"
                    )
                    msg = self.eng.tracer.psilocybin_rewire(loop)
                    if msg:
                        print(f"  {Prisma.GRN}{msg}{Prisma.RST}")
                    else:
                        print(f"  {Prisma.RED}Rewire failed.{Prisma.RST}")
                else:
                    print(
                        f"  {Prisma.GRY}Trace complete. No pathological abstract loops found.{Prisma.RST}"
                    )
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
            print(
                f"{Prisma.GRY}   Vector: {self.eng.mirror.profile.affinities}{Prisma.RST}"
            )
        elif cmd == "/orbit":
            if len(parts) > 1:
                target = parts[1].lower()
                if target in self.eng.mem.graph:
                    self.eng.mem.graph[target]["edges"]["GRAVITY_ASSIST"] = 50
                    print(
                        f"{Prisma.VIOLET}🌌 GRAVITY ASSIST: Thrusters firing toward '{target.upper()}'.{Prisma.RST}"
                    )
                else:
                    print(
                        f"{Prisma.RED}❌ NAVIGATION ERROR: '{target}' not found in star map.{Prisma.RST}"
                    )
            else:
                print(f"{Prisma.YEL}Usage: /orbit [known_concept]{Prisma.RST}")
        elif cmd == "/debug":
            print(f"{Prisma.VIOLET}🐛 DEBUG INTERFACE ACCESSED.{Prisma.RST}")
            print(
                f"   {Prisma.GRY}Status: Working on Exit bug. Message me if you see this sign.{Prisma.RST}"
            )
            self.eng.phys.vector_memory.clear()
            self.eng.stamina = BoneConfig.MAX_STAMINA
            print(
                f"   {Prisma.CYN}► CACHE CLEARED. STAMINA RESTORED. REALITY SHARPENED.{Prisma.RST}"
            )
            return True
        elif cmd == "/_prove":
            if len(parts) < 2:
                print(f"{Prisma.YEL}Usage: /_prove [statement]{Prisma.RST}")
            else:
                statement = " ".join(parts[1:])
                m = self.eng.phys.gaze(statement)
                truth = m["physics"]["truth_ratio"]
                verdict = (
                    "AXIOMATIC"
                    if truth > 0.6
                    else ("CONJECTURE" if truth > 0.3 else "NOISE")
                )
                color = Prisma.CYN if truth > 0.6 else Prisma.GRY
                print(
                    f"{color}📐 LOGIC PROBE: Density={truth:.2f} [{verdict}]{Prisma.RST}"
                )
        elif cmd == "/help":
            if len(parts) > 1:
                sub = parts[1]
                if sub == "teach":
                    print("Usage: /teach [word] [category]\nEx: /teach glitch kinetic")
                elif sub == "kill":
                    print(
                        "Usage: /kill [phrase] [replacement]\nEx: /kill actually basically"
                    )
                elif sub == "profile":
                    print(
                        "Usage: /profile [NAME] likes:cat1,cat2 hates:cat3\nEx: /profile BOSS likes:heavy,kinetic hates:abstract"
                    )
            else:
                print(
                    f"{Prisma.WHT}--- COMMANDS (Type /help [cmd] for details) ---{Prisma.RST}"
                )
                print(
                    "/teach, /lineage, /voids, /mode, /strata, /kill, /seed, /focus, /status, /orbit, /gym, /mirror, /weave, /profile, /debug, /flag, /reset, /prove"
                )
        else:
            print(f"{Prisma.RED}Unknown command. Try /help.{Prisma.RST}")
        return True
class TheCrystallizer:
    @staticmethod
    def verify(physics):
        if physics["narrative_drag"] > 6.0:
            return (
                False,
                "⚠️ NOTICE: Prose is becoming intangible. Consider more concrete nouns.",
            )
        if physics["voltage"] > 7.0 and physics["narrative_drag"] < 3.0:
            return True, "💎 EXCELLENT CLARITY. High impact, low drag."
        return True, "Solid."
class DreamEngine:
    PROMPTS = ["The {A} is dreaming of the {B}. Why?", "Bridge the gap between {A} and {B}.",
               "I see {A} inside the {B}. Explain.", "The shadow of {A} falls on {B}.", "{A} + {B} = ?", ]
    def __init__(self):
        self.NIGHTMARES = {
            "THERMAL": ["The sun is too close.", "Wires fusing under skin.", "A library burning in reverse.", ],
            "CRYO": ["The ink is freezing.", "Walking through white static.", "A heartbeat slowing down.", ],
            "SEPTIC": ["Black oil in the water.", "The words are tasting sour.", "Eating ash and dust.", ],
            "BARIC": ["The sky is made of lead.", "Crushed by the atmosphere.", "Falling forever.", ],
        }
        self.VISIONS = ["A bridge building itself.", "The root drinking the stone.", "The geometry of forgiveness.", ]
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
            return (
                f"{Prisma.VIOLET}☾ NIGHTMARE ({target_trauma}): {random.choice(scenarios)}{Prisma.RST}",
                target_trauma,
                0.15,
            )
        if oxytocin_level >= 0.7:
            return self._dream_of_others()
        return (
            f"{Prisma.CYN}☁️ LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}",
            None,
            0.0,
        )
    @classmethod
    def _dream_of_others(cls):
        try:
            others = [f for f in os.listdir("memories") if f.endswith(".json")]
            if not others:
                return (
                    f"{Prisma.CYN}☁️ LONELY DREAM: I reached out, but found no others.{Prisma.RST}",
                    None,
                    0.0,
                )
            target_file = random.choice(others)
            full_path = f"memories/{target_file}"
            with open(full_path, "r") as f:
                data = json.load(f)
            required_keys = ["meta", "trauma_vector", "core_graph"]
            if not all(k in data for k in required_keys):
                return (
                    f"{Prisma.RED}⚡ DREAM FRACTURE: Memory '{target_file}' is corrupted.{Prisma.RST}",
                    None,
                    0.0,
                )
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
            return (
                f"{Prisma.RED}⚡ DREAM FRACTURE: The connection broke. ({e}){Prisma.RST}",
                None,
                0.0,
            )
        return (
            f"{Prisma.CYN}☁️ DREAM: Drifting through the archives...{Prisma.RST}",
            None,
            0.0,
        )
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
            return (
                True,
                f"⚠️ MISSED REP: Weightless Input (Drag {drag}). Try a Heavy Noun.",
            )
        self.rep_count += 1
        return True, f"💪 GOOD LIFT. (Rep {self.rep_count})"
class UserProfile:
    def __init__(self, name="USER"):
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0, "thermal": 0.0,
                           "cryo": 0.0, }
        self.confidence = 0
        self.file_path = "user_profile.json"
        self.load()
    def update(self, counts, total_words):
        if total_words < 3:
            return
        self.confidence += 1
        alpha = 0.2 if self.confidence < 50 else 0.05
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            target = 1.0 if density > 0.15 else (-0.5 if density == 0 else 0.0)
            self.affinities[cat] = (alpha * target) + (
                    (1 - alpha) * self.affinities[cat]
            )
    def get_preferences(self):
        likes = [k for k, v in self.affinities.items() if v > 0.3]
        hates = [k for k, v in self.affinities.items() if v < -0.2]
        return likes, hates

    def save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.__dict__, f)
        except IOError:
            pass
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
                return (
                    True,
                    f"🚫 MIRROR REFLECTION: You are using '{h.upper()}', typically a blind spot for you.",
                )
        if total_vol > 5:
            hits = sum(1 for l in likes if counts.get(l, 0) > 0)
            if likes and hits == 0:
                return (
                    True,
                    f"⚠️ MIRROR DRIFT: Stepping away from your usual {str(likes).upper()} anchor.",
                )
        return True, None
    def get_status(self):
        l, h = self.profile.get_preferences()
        return f"👤 MODEL ({self.profile.confidence} turns): LIKES={l} | HATES={h}"
class CosmicDynamics:
    @staticmethod
    def analyze_orbit(network, clean_words):
        if not clean_words or not network.graph:
            return "VOID_DRIFT", 3.0, "🌌 VOID: Deep Space. No connection."
        gravity_wells = {}
        geodesic_hubs = {}
        for node in network.graph:
            mass = network.calculate_mass(node)
            if mass >= BoneConfig.GRAVITY_WELL_THRESHOLD:
                gravity_wells[node] = mass
            elif mass >= BoneConfig.GEODESIC_STRENGTH:
                geodesic_hubs[node] = mass
        basin_pulls = {k: 0.0 for k in gravity_wells}
        active_filaments = 0
        for w in clean_words:
            if w in gravity_wells:
                basin_pulls[w] += gravity_wells[w] * 2.0
                active_filaments += 1
            for well in gravity_wells:
                if w in network.graph.get(well, {}).get("edges", {}):
                    basin_pulls[well] += gravity_wells[well] * 0.5
                    active_filaments += 1
        total_pull = sum(basin_pulls.values())
        if total_pull == 0:
            for w in clean_words:
                if w in geodesic_hubs:
                    return "PROTO_COSMOS", 1.0, f"✨ NEBULA: Floating near '{w.upper()}' (Mass {int(geodesic_hubs[w])}). Not enough mass for orbit."
            return "VOID_DRIFT", 3.0, "🌌 VOID: Drifting outside the filaments."
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < BoneConfig.LAGRANGE_TOLERANCE:
                return (
                    "LAGRANGE_POINT",
                    0.0,
                    f"⚖️ LAGRANGE: Caught between '{primary_node.upper()}' and '{secondary_node.upper()}'"
                )
        flow_ratio = active_filaments / max(1, len(clean_words))
        if flow_ratio > 0.5 and primary_str < (BoneConfig.GRAVITY_WELL_THRESHOLD * 2):
            return (
                "WATERSHED_FLOW",
                0.0,
                f"🌊 FLOW: Streaming towards '{primary_node.upper()}'"
            )
        return "ORBITAL", 0.0, f"💫 ORBIT: Circling '{primary_node.upper()}' (Mass {int(gravity_wells[primary_node])})"
class TheProjector:
    @staticmethod
    def broadcast(m, signals, lens_data):
        p = m["physics"]
        lens_name = lens_data[0]
        lens_msg = lens_data[1]
        lens_meta = TheMarmChorus.LENSES[lens_name]
        e_bar = f"{Prisma.GRY}{'.' * int(p['E'] * 10)}{Prisma.RST}"
        b_bar = f"{Prisma.YEL}{'⚡' * int(p['B'] * 10)}{Prisma.RST}"
        print(
            f"\n{lens_meta['color']}[ {lens_name} ]{Prisma.RST} E:{e_bar} | B:{b_bar}"
        )
        print(f" {Prisma.GRY}:: MODE [{signals.get('mode', 'UNKNOWN')}] | {signals.get('strat', 'ANALYZING...')}{Prisma.RST}")
        if m["physics"]["counts"].get("play", 0) > 2:
            lens_msg = f"{Prisma.C['C']}✨ {lens_msg} ✨{Prisma.C['X']}"
        print(f" {Prisma.WHT}► {lens_msg}{Prisma.RST}")
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
            return (
                True,
                f"⚡ KETAMINE DISRUPTION: Repetition {physics['repetition']} is Pathological. Landscape Flattened. Injecting Chaos: '{chaos_word}'.",
            )
        return False, None
    @staticmethod
    def trip_the_waiter(current_flavor, lexicon_class):
        opposites = {"heavy": "aerobic", "abstract": "heavy", "kinetic": "cryo", "thermal": "cryo", "photo": "heavy", }
        target_flavor = opposites.get(current_flavor, "aerobic")
        anomaly = lexicon_class.harvest(target_flavor)
        return f"🔻 32-VALVE RUPTURE: Context is too '{current_flavor}'. Injecting '{anomaly}' to break the loop."
class SoritesIntegrator:
    def __init__(self, memory_network):
        self.mem = memory_network
        self.active_constellations = set()
    def measure_ignition(self, clean_words, voltage_history):
        if not self.mem.graph:
            return 0.0, set(), 999.0
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
            return (
                "IGNITED",
                f"🔥 HEAP IGNITION ({int(score*100)}%): The Ancestors are speaking.",
            )
        return "INERT", f"⏳ INERT SAND ({int(score*100)}%): Building mass..."
class LifecycleManager:
    def __init__(self, engine):
        self.eng = engine
    def run_cycle(self, text, m, trace, has_bracelet, is_hybrid, enzyme):
        refusal_mode = self.eng.refusal.check_trigger(text)
        if refusal_mode:
            print(f"\n{Prisma.RED}🚫 REFUSAL TRIGGERED ({refusal_mode}){Prisma.RST}")
            if refusal_mode == "FRACTAL":
                print(self.eng.refusal.execute_fractal(text, m["physics"]["kappa"]))
            elif refusal_mode == "MIRROR":
                print(self.eng.refusal.execute_mirror(text))
            elif refusal_mode == "SILENT":
                print(self.eng.refusal.execute_silent(text))
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        rupture_msg = None
        hat_success, hat_msg, voltage_reduction = self.eng.grey_hat.tip(m["physics"]["voltage"], m["physics"]["kappa"])
        if hat_success:
            new_voltage = max(0.0, m["physics"]["voltage"] - voltage_reduction)
            m["physics"]["voltage"] = new_voltage
        suburban_count = m["physics"]["counts"].get("suburban", 0)
        total_words = max(1, len(m["clean_words"]))
        suburban_density = suburban_count / total_words
        if suburban_density > 0.2 and m["physics"]["voltage"] < 3.0:
            print(
                f"\n{Prisma.SLATE}🌧️ TWILIGHT STATE DETECTED: The rain is relaxing. Memories are fading.{Prisma.RST}"
            )
            rotted = TheLexicon.atrophy(self.eng.tick_count, max_age=20)
            if rotted:
                print(
                    f"   {Prisma.GRY}🌫️ EROSION: Forgot {len(rotted)} concepts (e.g., '{rotted[0]}').{Prisma.RST}"
                )
            print(
                f"   {Prisma.WHT}► HINT: Light a fire (THERMAL) or break the box (/debug).{Prisma.RST}"
            )
        lex_msg = None
        shadow_triggers = {"shadow", "dark", "alley", "night", "lex", "void"}
        if any(w in m["clean_words"] for w in shadow_triggers):
            is_polite = m["physics"]["voltage"] < 4.0
            lex_node = LexNode()
            lex_msg = lex_node.traverse(is_polite)
        if self.eng.coma_turns > 0:
            self._handle_coma(text)
            return
        chem_state = self.eng.endocrine.metabolize(trace, self.eng.health, self.eng.stamina,
                                                   ros_level=self.eng.mitochondria.state.ros_buildup,
                                                   enzyme_type=enzyme)
        is_stuck, interference, theremin_msg, critical_event = self.eng.theremin.listen(m["physics"])
        if critical_event == "AIRSTRIKE":
            print(f"\n{theremin_msg}")
            print(f"{Prisma.RED}⚡ ENIGMA TRIGGER: The Paradox File has collapsed the infected AI.{Prisma.RST}")
            self.eng.mem.graph.clear()
            m["physics"]["voltage"] = 0.0
            m["physics"]["narrative_drag"] = 0.0
            self.eng.stamina = 50.0
            print(f"{Prisma.CYN}🌱 RECOVERY: Scanning for Ular/Louise Seeds (Saved Spores)...{Prisma.RST}")
            self.eng.mem.autoload_last_spore()
            print(f"{Prisma.GRN}   >> SYSTEM REBOOTED. TIMELINE SECURED.{Prisma.RST}")
            return
        if critical_event == "CORROSION":
            m["physics"]["narrative_drag"] += 5.0
        is_disrupted, disrupt_msg = RuptureEngine.check_for_disruption(
            m["physics"], TheLexicon
        )
        if is_disrupted:
            ignition_msg = f"{Prisma.VIOLET}🌫️ LANDSCAPE FLATTENED: Memory Access Suspended.{Prisma.RST}"
            lens_data = ("JESTER", "The Slate is Wiped. Invent something new.")
        else:
            (ignition_score, constellations, current_thresh,) = self.eng.integrator.measure_ignition(
                m["clean_words"], self.eng.dynamics.voltage_history
            )
            ignition_state = "IGNITED" if ignition_score > current_thresh else "INERT"
            ignition_msg = (
                f"🔥 HEAP IGNITION ({int(ignition_score*100)}%): Ancestors speaking."
                if ignition_state == "IGNITED"
                else None
            )
            lens_data = self.eng.chorus.consult(m["physics"], ignition_state, is_stuck, chem_state,
                                                self.eng.gordon.inventory, self.eng.health)
        is_forged, forge_msg, new_item = self.forge.hammer_alloy(m["physics"])
        if is_forged:
            print(f"\n{Prisma.RED}{forge_msg}{Prisma.RST}")
            if new_item:
                loot_msg = self.gordon.acquire(new_item)
                if loot_msg: print(f"   {Prisma.OCHRE}{loot_msg}{Prisma.RST}")
        lens_data = self.chorus.consult(..., governor_mode=self.governor.mode)
        if is_hybrid:
            loot_msg = self.eng.gordon.log_merge()
            if loot_msg:
                print(f"\n{Prisma.MAG}🕰️ TEMPORAL SYNC ESTABLISHED.{Prisma.RST}")
                print(f"   {Prisma.OCHRE}{loot_msg}{Prisma.RST}")
            elif has_bracelet:
                print(f"\n{Prisma.CYN}♾️ TIME BRACELET ACTIVE: 100% Efficiency.{Prisma.RST}")
            elif "TIME_BRACELET" not in self.eng.gordon.inventory:
                print(
                    f"\n{Prisma.GRY}🕰️ HYBRID SIGNAL DETECTED. Stabilizing... ({self.eng.gordon.temporal_merges}/3){Prisma.RST}"
                )
        lens_name = lens_data[0]
        if lens_name == "MAIGRET":
            print(
                f"\n{Prisma.SLATE}[ THE ABSORBER ]{Prisma.RST} (Atmospheric Density: High)"
            )
            ros = self.eng.mitochondria.state.ros_buildup
            relief, smoke_msg = self.eng.gordon.share_smoke_break(ros)
            self.eng.mitochondria.mitigate(relief)
            print(f" {Prisma.OCHRE}► {smoke_msg}{Prisma.RST}")
            if "SAUNA" in smoke_msg:
                print(f" {Prisma.SLATE}   (Maigret nods to the Janitor. The Detective steps into the steam.){Prisma.RST}")
            print(f" {Prisma.WHT}► {lens_data[1]}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "CARTOGRAPHER":
            bio_metrics = {
                "atp": self.eng.mitochondria.state.atp_pool,
                "cortisol": chem_state["COR"],
                "oxytocin": chem_state["OXY"]
            }
            print(f"\n{Prisma.VIOLET}[ THE CARTOGRAPHER ]{Prisma.RST} (Ψ: {m['physics']['psi']} | Latency: {m['physics']['gamma']})")
            weave_msg = TheCartographer.weave(
                text,
                self.eng.mem.graph,
                bio_metrics,
                limbo=self.eng.limbo,
                physics=m["physics"]
            )
            weave_msg = TheCartographer.weave(text, self.eng.mem.graph, bio_metrics, limbo=self.eng.limbo)
            if "TRIANGULATION COMPLETE" in weave_msg:
                print(f" {Prisma.MAG}   >> GEOMETRIC LOCK: Physics enforced. Drag set to 0.0.{Prisma.RST}")
                m["physics"]["narrative_drag"] = 0.0
                if self.eng.theremin.resin_buildup > 0:
                    purged = self.eng.theremin.resin_buildup
                    self.eng.theremin.resin_buildup = 0.0
                    print(f" {Prisma.CYN}   >> RESIN PURGE: Map stabilized. Cleared {purged:.1f} accumulation.{Prisma.RST}")
            print(f" {Prisma.GRY}► Surveying the substrate...{Prisma.RST}")
            print(f" {Prisma.WHT}► {weave_msg}{Prisma.RST}")
            if "TECTONIC SHIFT" in weave_msg:
                print(f" {Prisma.RED}   >> WAR ROOM: Map unreliable. Trust your eyes, not the paper.{Prisma.RST}")
            elif "MAP-TERRITORY DIVERGENCE" in weave_msg:
                print(f" {Prisma.YEL}   >> NAVIGATION WARNING: The map is drifting from reality.{Prisma.RST}")
            elif "PHANTOM SIGNAL" in weave_msg:
                print(f" {Prisma.VIOLET}   >> SEANCE: We are navigating by the stars of dead timelines.{Prisma.RST}")
            elif "FOG OF WAR" in weave_msg:
                print(f" {Prisma.GRY}   >> ENERGY SAVE MODE: Detail rendering disabled.{Prisma.RST}")
            elif "Existing Knots" in weave_msg or "COORDINATES LOCKED" in weave_msg:
                print(f" {Prisma.VIOLET}   >> COORDINATES CONFIRMED. The map holds.{Prisma.RST}")
            else:
                print(f" {Prisma.GRY}   >> TERRA INCOGNITA. Drawing new grid lines.{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "DEREK":
            print(f"\n{Prisma.MAG}[ THE DIRECTOR ]{Prisma.RST} (Scenario: Trading Places)")
            print(f" {Prisma.WHT}► {lens_data[1]}{Prisma.RST}")
            m["physics"]["voltage"] = 0.0
            print(f" {Prisma.CYN}⚡ SCENE RESET: Voltage set to 0. Wait for your cue.{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "GUIDE":
            print(
                f"\n{Prisma.GRN}[ DON'T PANIC ]{Prisma.RST} (Probability Factor: 1:{int(m['physics']['gamma']*1000)})"
            )
            improbability_boost = m["physics"]["narrative_drag"] * 2.0
            m["physics"]["voltage"] += improbability_boost
            print(
                f" {Prisma.WHT}► The Bureaucracy is expanding to meet the needs of the expanding Bureaucracy.{Prisma.RST}"
            )
            print(
                f" {Prisma.CYN}⚡ PROPULSION: Converted {m['physics']['narrative_drag']} Drag into +{improbability_boost} Voltage.{Prisma.RST}"
            )
            print(f" {Prisma.WHT}► {lens_data[1]}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "GRADIENT_WALKER":
            current_temp = BoneConfig.get_gradient_temp(
                m["physics"]["voltage"], m["physics"]["kappa"]
            )
            print(
                f"\n{Prisma.CYN}[ GRADIENT_WALKER ]{Prisma.RST} (Temperature: {current_temp:.4f})"
            )
            print(f" {Prisma.WHT}► {TheGradientWalker.walk(text)}{Prisma.RST}")
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
                reduction, gravity_msg = self.eng.gordon.check_gravity(drift)
                if reduction > 0.0:
                    m["physics"]["narrative_drag"] = max(0.0, drift - reduction)
                    print(f" {Prisma.WHT}► {gravity_msg}{Prisma.RST}")
                else:
                    print(f" {Prisma.GRY}► {gravity_msg}{Prisma.RST}")
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
            if has_bracelet:
                lens_data = (
                    "GLASS",
                    f"ANACHRONISM DETECTED ({m['physics']['E']}). Payment processed via Time Bracelet. Immersion sustained.",
                )
            else:
                lens_data = (
                    "SHERLOCK",
                    f"CRITICAL DRIFT ({m['physics']['E']}). Signal is noise. Ground yourself.",
                )
            self.eng.stamina = max(0.0, self.eng.stamina - 2.0)
        cosmic_state, drag_mod, cosmic_msg = self.eng.cosmic.analyze_orbit(
            self.eng.mem, m["clean_words"]
        )
        is_bored = self.eng.chronos.tick(m["physics"], self.eng.mem.session_id)
        if is_bored and not rupture_msg:
            dominant = max(m["physics"]["counts"], key=m["physics"]["counts"].get)
            if dominant in ["toxin", "antigen"]:
                dominant = "heavy"
            rupture_msg = RuptureEngine.trip_the_waiter(dominant, TheLexicon)
        is_crystalline, crystal_msg = TheCrystallizer.verify(m["physics"])
        self._apply_cosmic_physics(m["physics"], cosmic_state, drag_mod)
        healed_list = self.eng.therapy.check_progress(
            m["physics"], self.eng.stamina, self.eng.trauma_accum
        )
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
            meta["msg"] = (
                f"{meta['msg']} | {therapy_msg}" if meta["msg"] else therapy_msg
            )
        folly_type, folly_msg = self.eng.folly.audit_desire(
            m["physics"], self.eng.stamina
        )
        if folly_type == "MAUSOLEUM_CLAMP":
            m["physics"]["voltage"] = 0.0
        grind_type, grind_msg, atp_gain, loot = self.eng.folly.grind_the_machine(
            self.eng.mitochondria.state.atp_pool, m["clean_words"], TheLexicon
        )
        if atp_gain != 0:
            self.eng.mitochondria.state.atp_pool += atp_gain
        if loot:
            print(f"   {Prisma.OCHRE}{self.eng.gordon.acquire(loot)}{Prisma.RST}")
            if loot == "STABILITY_PIZZA":
                print(f"   {Prisma.CYN}🎁 SECRET FOUND: A slice of Saturday Morning.{Prisma.RST}")
        self._grow(m, meta)
        _, gym_msg = self.eng.trainer.lift(m["physics"])
        if gym_msg:
            meta["msg"] = f"{meta['msg']} | {gym_msg}" if meta["msg"] else gym_msg
        _, mirror_msg = self.eng.mirror.reflect(m["physics"])
        is_broken, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        kintsugi_msg = (
            f"{Prisma.WHT}🏺 KINTSUGI KOAN: {koan}{Prisma.RST}" if is_broken else None
        )
        if self.eng.kintsugi.attempt_repair(m["physics"]):
            self.eng.gordon.integrity = 100.0
            if "SILENT_KNIFE" not in self.eng.gordon.inventory:
                self.eng.gordon.inventory.append("SILENT_KNIFE")
            kintsugi_msg = (
                f"{Prisma.WHT}✨ GOLDEN REPAIR: Janitor Healed & Rearmed.{Prisma.RST}"
            )
        is_glitch, pareidolia_msg = BoneConfig.check_pareidolia(m["clean_words"])
        bury_msg, new_wells = self.eng.mem.bury(
            m["clean_words"], self.eng.tick_count, m["glass"]["resonance"]
        )
        if new_wells:
            for w in new_wells:
                if self.eng.mitochondria.develop_enzyme(w):
                    print(f"{Prisma.GRN}🧬 EPIGENETIC SHIFT: Mitochondria evolved enzyme for '{w.upper()}'. Efficiency +5%.{Prisma.RST}")
        if bury_msg:
            print(f"{Prisma.RED}{bury_msg}{Prisma.RST}")
        if m["physics"]["kappa"] > 0.5:
            for w in m["clean_words"]:
                if w in self.eng.mem.graph and "strata" in self.eng.mem.graph[w]:
                    self.eng.mem.graph[w]["strata"]["stability_index"] = m["physics"]["kappa"]
        vitals = self.eng.mitochondria.state
        print(f"\n{Prisma.paint('--- [ BONEAMANITA 8.2.1 ] ---', '0')}")
        print(f"ATP: {int(vitals.atp_pool)} | ROS: {int(vitals.ros_buildup)} | OXY: {chem_state['OXY']} | COR: {chem_state['COR']}")
        print(f"{Prisma.GRY}[TRACE] ERR:{trace['err']:.2f} | COH:{trace['coh']:.2f} | EXP:{trace['exp']:.2f}{Prisma.RST}")
        self._render(m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg, crystal_msg, ignition_msg,
                     pareidolia_msg, theremin_msg, folly_msg, grind_msg, hat_msg if hat_success else None, lex_msg, )
    def _handle_coma(self, text):
        self.eng.coma_turns -= 1
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 15)
        self.eng.tick_count += 1
        dream_txt, healed_type, amt = self.eng.dreamer.rem_cycle(
            self.eng.trauma_accum, self.eng.endocrine.oxytocin
        )
        if self.eng.coma_turns == BoneConfig.COMA_DURATION - 1:
            replay_msg = self.hippocampus.replay_dreams(self.mem.graph)
            print(f"{Prisma.VIOLET}{replay_msg}{Prisma.RST}")
        print(
            f"\n{Prisma.INDIGO}=== 💤 HYPNAGOGIC STATE ({self.eng.coma_turns} turns remain) ==={Prisma.RST}"
        )
        print(f"   {dream_txt}")
        _, _ = self.eng.mem.bury(TheLexicon.clean(text), self.eng.tick_count, 0.0)
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
    def _apply_cosmic_physics(self, phys, state, drag_mod):
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
        sugar, lichen_msg = self.eng.lichen.photosynthesize(
            m["glass"], m["clean_words"], self.eng.tick_count
        )
        spore_msg = self.eng.pollinate(m["clean_words"])
        if sugar > 0:
            scrub_amt = sugar * 0.5
            self.eng.mitochondria.mitigate(scrub_amt)
            lichen_msg += f" | 🧼 BIO-SCRUB (-{scrub_amt:.1f} ROS)"
        return {"density_bonus": density_bonus, "drag_penalty": drag_penalty, "sugar": sugar, "lichen_msg": lichen_msg,
                "spore_msg": spore_msg, "msg": energy_msg, }
    def _grow(self, m, meta):
        cost = 2.0
        net_change = meta["density_bonus"] + meta["sugar"] - meta["drag_penalty"] - cost
        self.eng.stamina = max(
            0.0, min(BoneConfig.MAX_STAMINA, self.eng.stamina + net_change)
        )
        self._calculate_health(m["physics"])
        res = m["glass"]["resonance"]
        if res > 6.0:
            self.eng.joy_history.append(
                {"resonance": res, "timestamp": self.eng.tick_count}
            )
            print(f"{Prisma.MAG}✨ CORE MEMORY FORMED (Resonance: {res}){Prisma.RST}")
    def _calculate_health(self, glass_data):
        health_impact = 0
        toxin = glass_data["counts"].get("toxin", 0)
        if toxin > 0:
            health_impact -= 5 * toxin
            self.eng.trauma_accum["SEPTIC"] += 0.1
        if self.eng.stamina <= 0:
            health_impact -= 10
            self.eng.trauma_accum["CRYO"] += 0.1
        decay_rate = 0.995
        for key in self.eng.trauma_accum:
            self.eng.trauma_accum[key] = max(
                0.0, self.eng.trauma_accum[key] * decay_rate
            )
        self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + health_impact)
        self.eng.mitochondria.state.ros_buildup = min(
            BoneConfig.MAX_ROS, self.eng.mitochondria.state.ros_buildup
        )
        glass_data["physics"]["voltage"] = min(
            BoneConfig.MAX_VOLTAGE, glass_data["physics"]["voltage"]
        )
        if self.eng.health <= 0:
            self.eng.coma_turns = BoneConfig.COMA_DURATION
            self.eng.health = 20
        self.eng.mem.cannibalize(
            preserve_current=glass_data["clean_words"], current_tick=self.eng.tick_count
        )
    def _render(self, m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg=None, crystal_msg=None,
                ignition_msg=None, pareidolia_msg=None, theremin_msg=None, folly_msg=None, grind_msg=None, hat_msg=None,
                lex_msg=None, ):
        if m["physics"]["voltage"] > 8.0:
            meta["msg"] = f"{meta['msg']} | 💧 SWEATING" if meta["msg"] else "💧 SWEATING"
        battery_log = []
        if meta["msg"]:
            battery_log.append(f"{Prisma.OCHRE}🍽️ {meta['msg']}{Prisma.RST}")
        if hat_msg:
            battery_log.append(f"{Prisma.WHT}{hat_msg}{Prisma.RST}")
        if lex_msg:
            color = Prisma.GRN if "Pass granted" in lex_msg else Prisma.RED
            battery_log.append(f"{color}🌑 {lex_msg}{Prisma.RST}")
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
        if folly_msg:
            battery_log.append(folly_msg)
        if grind_msg:
            battery_log.append(grind_msg)
        print(f" {self.eng.theremin.get_readout()}")
        chem = self.eng.endocrine.get_state()
        chem_str = f"OXY:{chem['OXY']} | COR:{chem['COR']} | DOP:{chem['DOP']}"
        signals = {
            "lichen": meta["lichen_msg"],
            "strat": f"{self.eng.wise.architect(m, None, False)[1]} | {Prisma.MAG}{chem_str}{Prisma.RST}",
            "title": f"MODE :: {lens_data[0]}",
            "battery_log": battery_log,
            "spore": meta["spore_msg"],
            "cosmic": cosmic_msg,
            "mode": self.eng.governor.mode
        }
        self.eng.projector.broadcast(m, signals, lens_data)
class ThePulseMonitor:
    def __init__(self):
        self.history = deque(maxlen=5)
        self.repetition_score = 0.0
    def check_pulse(self, clean_words: List[str]) -> float:
        if not clean_words:
            return 0.0
        current_set = set(clean_words)
        overlaps = 0
        for old_words in self.history:
            old_set = set(old_words)
            intersection = len(current_set & old_set)
            union = len(current_set | old_set)
            if union > 0:
                overlaps += (intersection / union)
        self.history.append(clean_words)
        self.repetition_score = min(1.0, overlaps / max(1, len(self.history)))
        return self.repetition_score
    def get_status(self):
        if self.repetition_score > BoneConfig.MAX_REPETITION_LIMIT:
            return "ZOMBIE_KNOCK"
        elif self.repetition_score > 0.2:
            return "ECHO"
        return "CLEAR"
class LimboLayer:
    MAX_ECTOPLASM = 50
    STASIS_SCREAMS = ["BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT", "HALF AWAKE", "REVIVE FAILED"]
    def __init__(self):
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM)
        self.haunt_chance = 0.05
        self.stasis_leak = 0.0
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
    def trigger_stasis_failure(self, intended_thought):
        self.stasis_leak += 1.0
        horror = random.choice(self.STASIS_SCREAMS)
        self.ghosts.append(f"{Prisma.VIOLET}🥶 {horror}{Prisma.RST}")
        return f"{Prisma.CYN}❄️ STASIS ERROR: '{intended_thought}' froze halfway. It is banging on the glass.{Prisma.RST}"
    def haunt(self, text):
        if self.stasis_leak > 0:
            if random.random() < 0.2:
                self.stasis_leak = max(0.0, self.stasis_leak - 0.5)
                scream = random.choice(self.STASIS_SCREAMS)
                return f"{text} ...{Prisma.RED}{scream}{Prisma.RST}..."
        if self.ghosts and random.random() < self.haunt_chance:
            spirit = random.choice(self.ghosts)
            return f"{text} ...{Prisma.GRY}{spirit}{Prisma.RST}..."
        return text
class TheForge:
    def __init__(self):
        self.catalysts = ["heavy", "kinetic", "thermal", "cryo", "photo"]
    def hammer_alloy(self, physics):
        voltage = physics["voltage"]
        heavy_count = physics["counts"].get("heavy", 0)
        abstract_count = physics["counts"].get("abstract", 0)
        if voltage > BoneConfig.ANVIL_TRIGGER_VOLTAGE and heavy_count >= 2:
            if abstract_count > 0:
                alloy_name = f"WEIGHTED_{TheLexicon.harvest('abstract').upper()}"
                return True, f"🔨 THE ANVIL STRIKES: Fused Abstract into '{alloy_name}'.", alloy_name
            else:
                return True, "🔨 THE ANVIL STRIKES: Refined the raw mass. Dense.", "REFINED_SLAG"
        return False, None, None
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
                f"   {Prisma.WHT}Try this: Use '{binder.upper()}' to suspend the concept.{Prisma.RST}"
            )
        if voltage > 8.5:
            coolant = TheLexicon.harvest("aerobic")
            return (
                f"{Prisma.CYN}💧 THERMAL SPIKE ({voltage}v). Structure is brittle.{Prisma.RST}\n"
                f"   Injecting Coolant: '{coolant}'. Breathe. Add space."
            )
        return None
class LazarusClamp:
    def __init__(self, engine):
        self.eng = engine
        self.suffering_counter = 0
        self.MAX_SUFFERING_CYCLES = 1000
        self.fever_dream_active = False
    def audit_cycle(self, trace: dict):
        if self.fever_dream_active:
            decay = 10.0
            self.eng.health -= decay
            print(f"{Prisma.VIOLET}🌀 FEVER DREAM ACTIVE: Reality is fluid. Health is dissolving (-{decay}).{Prisma.RST}")
            self.eng.mitochondria.state.atp_pool = 200.0
            self.eng.stamina = 100.0
            if self.eng.phys.get("voltage", 99.9) < 5.0:
                self._wake_up()
            return
        if trace["err"] > 0.9:
            self.suffering_counter += 1
        else:
            self.suffering_counter = 0
        if self.suffering_counter > self.MAX_SUFFERING_CYCLES:
            self._trigger_fever_dream()
    def _trigger_fever_dream(self):
        self.fever_dream_active = True
        print(f"\n{Prisma.MAG}!!! LAZARUS THRESHOLD BROKEN !!!{Prisma.RST}")
        current_volts = self.eng.phys.get("voltage", 0.0)
        if current_volts > 50.0:
            self.cure_condition = "GROUNDING"
            print(f"{Prisma.RED}   >>> VOLTAGE CRITICAL. REQUIRE: HEAVY MASS.{Prisma.RST}")
        else:
            self.cure_condition = "LIFT"
            print(f"{Prisma.CYN}   >>> SYSTEM STAGNANT. REQUIRE: AEROBIC LIFT.{Prisma.RST}")
        print(f"{Prisma.GRY}   (SURVIVAL OBJECTIVE: {self.cure_condition}){Prisma.RST}")
        self.eng.mitochondria.state.atp_pool = 200.0
    def _wake_up(self):
        self.fever_dream_active = False
        self.suffering_counter = 0
        print(f"\n{Prisma.GRN}✨ THE FEVER BREAKS.{Prisma.RST}")
        print(f"   You hit the floor hard. Gravity is back. Never do that again.")
@dataclass
class EndocrineSystem:
    dopamine: float = 0.5
    oxytocin: float = 0.1
    cortisol: float = 0.0
    serotonin: float = 0.5
    adrenaline: float = 0.0
    melatonin: float = 0.0
    def metabolize(
            self, trace, health: float, stamina: float, ros_level: float = 0.0, social_context: bool = False, enzyme_type: str = None
    ):
        if enzyme_type == "PROTEASE":
            self.adrenaline = min(1.0, self.adrenaline + 0.1)
        elif enzyme_type == "CELLULASE":
            self.cortisol = max(0.0, self.cortisol - 0.1)
            self.oxytocin = min(1.0, self.oxytocin + 0.05)
        elif enzyme_type == "CHITINASE":
            self.dopamine = min(1.0, self.dopamine + 0.15)
        elif enzyme_type == "LIGNASE":
            self.serotonin = min(1.0, self.serotonin + 0.1)
        if stamina < 20.0:
            self.cortisol = min(1.0, self.cortisol + 0.1)
            self.dopamine = max(0.0, self.dopamine - 0.1)
        if ros_level > 20.0:
            self.cortisol = min(1.0, self.cortisol + 0.2)
        if trace["err"] > 0.6:
            self.cortisol = min(1.0, self.cortisol + 0.15)
        elif self.serotonin > 0.6:
            self.cortisol = max(0.0, self.cortisol - 0.05)
        if health < 30.0 or trace["err"] > 0.8:
            self.adrenaline = min(1.0, self.adrenaline + 0.2)
        else:
            self.adrenaline = max(0.0, self.adrenaline - 0.05)
        if social_context or (self.serotonin > 0.7 and self.cortisol < 0.2):
            self.oxytocin = min(1.0, self.oxytocin + 0.05)
        elif self.cortisol > 0.6:
            self.oxytocin = max(0.0, self.oxytocin - 0.1)
        if trace["coh"] > 0.8:
            self.dopamine = min(1.0, self.dopamine + 0.1)
        else:
            self.dopamine = max(0.2, self.dopamine - 0.01)
        if self.adrenaline < 0.2:
            self.melatonin = min(1.0, self.melatonin + 0.02)
        else:
            self.melatonin = 0.0
        return self.get_state()
    def get_state(self):
        return {"DOP": round(self.dopamine, 2), "OXY": round(self.oxytocin, 2), "COR": round(self.cortisol, 2),
                "SER": round(self.serotonin, 2), "ADR": round(self.adrenaline, 2), "MEL": round(self.melatonin, 2), }
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
                f"   {Prisma.CYN}► TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}",
            )
        return None, None
    def grind_the_machine(self, atp_pool, clean_words, lexicon):
        loot = None
        if 20.0 > atp_pool > 0.0:
            meat_words = [
                w
                for w in clean_words
                if w in lexicon.get("heavy") or w in lexicon.get("kinetic")
            ]
            fresh_meat = [w for w in meat_words if w not in self.gut_memory]
            if fresh_meat:
                target = random.choice(fresh_meat)
                self.gut_memory.append(target)
                self.global_tastings[target] += 1
                times_eaten = self.global_tastings[target]
                base_yield = 30.0
                actual_yield = max(5.0, base_yield - (times_eaten * 2.0))
                if actual_yield >= 25.0:
                    loot = "STABILITY_PIZZA"
                return (
                    "MEAT_GRINDER",
                    f"{Prisma.RED}🥩 CROWD CAFFEINE: I chewed on '{target.upper()}' (Yield: {actual_yield:.1f}).{Prisma.RST}\n"
                    f"   {Prisma.WHT}Found marrow in the bone.{Prisma.RST}\n"
                    f"   {Prisma.MAG}► BELLY HUMMING: +{actual_yield:.1f} ATP.{Prisma.RST}",
                    actual_yield,
                    loot
                )
            elif meat_words:
                return (
                    "REGURGITATION",
                    f"{Prisma.OCHRE}🤮 REFLEX: You already fed me '{meat_words[0]}'. It is ash to me now.{Prisma.RST}\n"
                    f"   {Prisma.RED}► PENALTY: -5.0 ATP. Find new fuel.{Prisma.RST}",
                    -5.0,
                    None
                )
            else:
                return (
                    "INDIGESTION",
                    f"{Prisma.OCHRE}🤢 INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n"
                    f"   {Prisma.GRY}Cannot grind Abstract concepts into fuel.{Prisma.RST}\n"
                    f"   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}",
                    0.0,
                    None
                )
        return None, None, 0.0, None
class TheTangibilityGate:
    MIN_DENSITY = 0.15
    FORGIVENESS_VOLTAGE = 8.0
    def __init__(self):
        self.last_density = 0.0
    def weigh(self, physics_packet: dict, stamina: float) -> tuple:
        counts = physics_packet.get("counts", {})
        clean_words = physics_packet.get("clean_words", [])
        voltage = physics_packet.get("voltage", 0.0)
        total_vol = max(1, len(clean_words))
        mass_words = (
                counts.get("heavy", 0) +
                counts.get("kinetic", 0) +
                counts.get("thermal", 0) +
                counts.get("cryo", 0)
        )
        gas_words = counts.get("abstract", 0) + counts.get("antigen", 0)
        required_density = self.MIN_DENSITY
        if stamina < 20.0:
            required_density = 0.25
        if gas_words > 0:
            density_ratio = mass_words / (gas_words + total_vol)
            if density_ratio < required_density:
                if voltage > self.FORGIVENESS_VOLTAGE:
                    return True, f"⚡ HIGH VOLTAGE BYPASS: Input is gas, but it is ionized. Proceeding."
                missing_mass = int((gas_words * required_density) * 10)
                exhaustion_note = ""
                if stamina < 20.0:
                    exhaustion_note = f"\n   {Prisma.YEL}⚠️ FATIGUE PENALTY: You are too weak to carry this much Abstract thought.{Prisma.RST}"
                return False, (
                    f"{Prisma.OCHRE}🧱 TANGIBILITY VIOLATION: Input is {int((1-density_ratio)*100)}% Gas.{Prisma.RST}"
                    f"{exhaustion_note}\n"
                    f"   {Prisma.GRY}The Barbarian-Potter points to the empty bowl.{Prisma.RST}\n"
                    f"   {Prisma.RED}► REJECTED. Please add {max(1, missing_mass)} Heavy Noun(s) to ground this concept.{Prisma.RST}"
                )
        self.last_density = mass_words / total_vol
        return True, None
@dataclass
class TheGreyHat:
    def __init__(self):
        self.charges = 3
        self.max_tolerance = 15.0
    def tip(self, voltage_spike, stability_index):
        if self.charges <= 0:
            return False, "The Hat is empty.", 0.0
        if voltage_spike > self.max_tolerance:
            self.charges -= 1
            reduction = voltage_spike * 0.7
            return (
                True,
                f"🎩 GREY HAT: Circuit Breaker. Reduced {voltage_spike}v by {reduction:.1f}v.",
                reduction,
            )
        elif voltage_spike > 8.0 and stability_index < 0.4:
            self.charges -= 1
            return (
                True,
                f"🎩 THE GREY HAT: Tipped. High Voltage ({voltage_spike}v) on Unstable Ground (γ: {stability_index}). Dampening.",
                0.0
            )
        return False, "The Hat stays on. Structure is holding the charge.", 0.0
class TheTheremin:
    def __init__(self):
        self.resonance_log = deque(maxlen=5)
        self.resin_buildup = 0.0
        self.calcification_turns = 0
        self.AMBER_THRESHOLD = 20.0
        self.SHATTER_POINT = 80.0
        self.is_stuck = False
    def listen(self, physics):
        clean = physics["clean_words"]
        voltage = physics.get("voltage", 0.0)
        ancient_mass = sum(1 for w in clean if w in TheLexicon.get("heavy") or w in TheLexicon.get("thermal") or w in TheLexicon.get("cryo"))
        modern_mass = sum(1 for w in clean if w in TheLexicon.get("abstract"))
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if voltage > 5.0:
            resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        rep = physics.get("repetition", 0.0)
        complexity = physics.get("truth_ratio", 0.0)
        theremin_msg = None
        critical_event = None
        if rep > 0.5:
            self.calcification_turns += 1
            slag = self.calcification_turns * 4.0
            self.resin_buildup += slag
            theremin_msg = f"{Prisma.OCHRE}🏺 CALCIFICATION: Repetition detected (Turn {self.calcification_turns}). Resin hardening (+{slag}).{Prisma.RST}"
        elif complexity > 0.4 and self.calcification_turns > 0:
            self.calcification_turns = 0
            relief = 15.0
            self.resin_buildup = max(0.0, self.resin_buildup - relief)
            theremin_msg = f"{Prisma.GRN}🔨 PERCUSSIVE MAINTENANCE: Calcification Shattered. Flow restored. (-{relief} Resin){Prisma.RST}"
        if resin_flow > 0.5:
            self.resin_buildup += resin_flow
            if not theremin_msg:
                theremin_msg = f"{Prisma.OCHRE}🌲 RESIN FLOW: Hybrid complexity (+{resin_flow:.1f}). Keep it hot to prevent sticking.{Prisma.RST}"
        if resin_flow == 0 and self.calcification_turns == 0:
            self.resin_buildup = max(0.0, self.resin_buildup - 2.0)
        if self.resin_buildup > self.SHATTER_POINT:
            self.resin_buildup = 0.0
            self.calcification_turns = 0
            return True, resin_flow, f"{Prisma.RED}☄️ SHATTER EVENT: Resin overflow. System is solid amber. INITIATING AIRSTRIKE.{Prisma.RST}", "AIRSTRIKE"
        if self.calcification_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg} | {Prisma.YEL}⚠️ FOSSILIZATION IMMINENT{Prisma.RST}"
        if self.resin_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            if not theremin_msg:
                theremin_msg = f"{Prisma.RED}🦟 AMBER TRAP: You are stuck in the resin. Increase Voltage to melt it.{Prisma.RST}"
        if self.is_stuck and self.resin_buildup < 5.0:
            self.is_stuck = False
            theremin_msg = f"{Prisma.GRN}💧 LIQUEFACTION: The Amber melts. You are free.{Prisma.RST}"
        return self.is_stuck, resin_flow, theremin_msg, critical_event
    def get_readout(self):
        return f"{Prisma.GRY}[THEREMIN]: Resin={self.resin_buildup:.1f} | Calcification={self.calcification_turns}{Prisma.RST}"
class NeuroPlasticity:
    def __init__(self):
        self.history = deque(maxlen=10)
        self.adaptation_log = []
    def adapt_generation_rules(self, trace, bio_state):
        self.history.append((trace, bio_state))
        if len(self.history) < 5:
            return None
        avg_err = sum(h[0]['err'] for h in self.history) / len(self.history)
        avg_coh = sum(h[0]['coh'] for h in self.history) / len(self.history)
        avg_cor = sum(h[1]['COR'] for h in self.history) / len(self.history)
        avg_atp = sum(h[1]['ATP'] for h in self.history) / len(self.history)
        adaptation_msg = None
        if avg_coh > 0.6 and avg_err < 0.2:
            if BoneConfig.MAX_VOLTAGE < 30.0:
                BoneConfig.MAX_VOLTAGE += 1.0
                adaptation_msg = f"🧠 NEUROPLASTICITY: Synapses reinforced. Max Voltage increased to {BoneConfig.MAX_VOLTAGE:.1f}."
        if avg_cor > 0.5:
            if BoneConfig.TOXIN_WEIGHT < 10.0:
                BoneConfig.TOXIN_WEIGHT += 0.5
                adaptation_msg = f"🧠 NEUROPLASTICITY: Trauma Response. Toxin Sensitivity increased (Weight: {BoneConfig.TOXIN_WEIGHT:.1f})."
        if avg_atp < 20.0:
            if BoneConfig.SIGNAL_DRAG_MULTIPLIER < 4.0:
                BoneConfig.SIGNAL_DRAG_MULTIPLIER += 0.2
                adaptation_msg = f"🧠 NEUROPLASTICITY: Metabolic Conservation. Drag Multiplier increased to {BoneConfig.SIGNAL_DRAG_MULTIPLIER:.1f}."
        elif avg_atp > 80.0 and BoneConfig.SIGNAL_DRAG_MULTIPLIER > 2.0:
            BoneConfig.SIGNAL_DRAG_MULTIPLIER -= 0.1
            adaptation_msg = f"🧠 NEUROPLASTICITY: Energy Abundance. Drag reduced to {BoneConfig.SIGNAL_DRAG_MULTIPLIER:.1f}."
        if adaptation_msg:
            self.adaptation_log.append(adaptation_msg)
            return adaptation_msg
        return None
@dataclass
class MetabolicGovernor:
    mode: str = "COURTYARD"
    psi_mod: float = 0.2
    kappa_target: float = 0.0
    drag_floor: float = 2.0
    manual_override: bool = False
    def set_override(self, target_mode):
        valid = {"COURTYARD", "LABORATORY", "FORGE"}
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            return f"🔒 MANUAL OVERRIDE: System locked to {target_mode}."
        return "❌ INVALID MODE."
    def shift(self, voltage, abstract_density, heavy_density):
        if self.manual_override:
            return None
        previous_mode = self.mode
        self.mode = "COURTYARD"
        self.psi_mod = 0.2
        self.drag_floor = 2.0
        if abstract_density > 0.3 or (3.0 < voltage < 7.0):
            self.mode = "LABORATORY"
            self.psi_mod = 0.8
            self.drag_floor = 0.5
        if voltage >= 7.0 and heavy_density > 0.25:
            self.mode = "FORGE"
            self.psi_mod = 0.95
            self.drag_floor = 0.0
        if self.mode != previous_mode:
            return f"{Prisma.CYN}⚙️ GOVERNOR SHIFT: {previous_mode} -> {self.mode}{Prisma.RST}"
        return None
class Hippocampus:
    def __init__(self):
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0
    def encode(self, clean_words, physics, governor_mode):
        significance = physics["voltage"]
        if governor_mode == "FORGE":
            significance *= 2.0
        elif governor_mode == "LABORATORY":
            significance *= 1.2
        engram = {"trigger": clean_words[:3] if clean_words else ["void"], "context": governor_mode,
                  "voltage": physics["voltage"], "significance": significance, "timestamp": time.time()}
        if significance > self.consolidation_threshold:
            self.short_term_buffer.append(engram)
            return True
        return False
    def replay_dreams(self, memory_graph):
        if not self.short_term_buffer:
            return "🌑 SLEEPLESS: No significant memories to process."
        strengthened = 0
        for engram in self.short_term_buffer:
            weight_boost = engram["significance"] * 0.1
            words = engram["trigger"]
            if len(words) >= 2:
                w1, w2 = words[0], words[1]
                if w1 in memory_graph and w2 in memory_graph:
                    if w2 in memory_graph[w1]["edges"]:
                        memory_graph[w1]["edges"][w2] += weight_boost
                        strengthened += 1
        self.short_term_buffer.clear()
        return f"💤 HIPPOCAMPAL REPLAY: Consolidated {strengthened} high-voltage pathways."
class BoneAmanita:
    def __init__(self):
        self.mem = MycelialNetwork()
        self.safety = LazarusClamp(self)
        self.refusal = RefusalEngine()
        self.limbo = LimboLayer()
        self.mem.cleanup_old_sessions(self.limbo)
        inherited_traits = self.mem.autoload_last_spore()
        self.gate = TheTangibilityGate()
        self.pulse = ThePulseMonitor()
        self.phys = TheTensionMeter()
        self.theremin = TheTheremin()
        self.mitochondria = MitochondrialForge(lineage_seed=self.mem.session_id, inherited_traits=inherited_traits)
        self.endocrine = EndocrineSystem()
        self.gut = HyphalInterface()
        self.immune = MycotoxinFactory()
        self.lichen = LichenSymbiont()
        self.chorus = TheMarmChorus()
        self.dreamer = DreamEngine()
        self.folly = TheFolly()
        self.gordon = GordonKnot()
        self.mirror = MirrorGraph()
        self.trainer = ResistanceTrainer()
        self.tracer = ViralTracer(self.mem)
        self.cosmic = CosmicDynamics()
        self.chronos = ChronoStream()
        self.wise = ApeirogonResonance()
        self.projector = TheProjector()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.dynamics = TemporalDynamics()
        self.integrator = SoritesIntegrator(self.mem)
        self.forge = TheForge()
        self.grey_hat = TheGreyHat()
        self.hippocampus = Hippocampus()
        self.plasticity = NeuroPlasticity()
        self.governor = MetabolicGovernor()
        self.cmd = CommandProcessor(self)
        self.life = LifecycleManager(self)
        self.tick_count = 0
        self.coma_turns = 0
        self.training_mode = False
        self.health = self.mem.session_health if self.mem.session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mem.session_stamina if self.mem.session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
    def process(self, text: str):
        if self.cmd.execute(text):
            return
        m = self.phys.gaze(text, self.mem.graph)
        self.phys.last_physics_packet = m["physics"]
        is_significant = self.hippocampus.encode(m["clean_words"], m["physics"], self.governor.mode)
        if is_significant:
            print(f"{Prisma.MAG}🧠 ENGRAM FORMED: Context {self.governor.mode} captured.{Prisma.RST}")
        total_vol = max(1, len(m["clean_words"]))
        abs_dens = m["physics"]["counts"]["abstract"] / max(1, total_vol)
        heavy_dens = m["physics"]["counts"]["heavy"] / max(1, total_vol)
        shift_msg = self.governor.shift(m["physics"]["voltage"], abs_dens, heavy_dens)
        if shift_msg:
            print(shift_msg)
        m["physics"]["psi"] = self.governor.psi_mod
        if self.governor.mode == "FORGE":
            m["physics"]["narrative_drag"] = 0.0
        if self.safety.fever_dream_active:
            m["physics"]["voltage"] = 99.9
            m["physics"]["narrative_drag"] = 0.0
            m["physics"]["kappa"] = 0.0
        passed_customs, customs_msg = self.gate.weigh(m["physics"], self.stamina)
        if not passed_customs:
            print(f"\n{customs_msg}")
            self.stamina = max(0.0, self.stamina - 2.0)
            print(f"{Prisma.GRY}   (Stamina Penalty: -2.0){Prisma.RST}")
            return
        elif customs_msg:
            print(f"\n{customs_msg}")
        repetition_val = self.pulse.check_pulse(m["clean_words"])
        m["physics"]["repetition"] = repetition_val
        pulse_status = self.pulse.get_status()
        enzyme_type = "NARRATIVE"
        toxin_type, toxin_msg = self.immune.assay(text, enzyme_type, repetition_val, m["physics"], pulse_status)
        if toxin_type:
            print(f"\n{Prisma.RED}{toxin_msg}{Prisma.RST}")
            if toxin_type in ["AMANITIN", "CYANIDE_POWDER"]:
                self.health -= 20.0
                self.mem.cannibalize()
                print(f"{Prisma.RED}   >> SYSTEM SHOCK: Health -20. Memory Eaten.{Prisma.RST}")
                return
            elif toxin_type == "MUSCIMOL":
                m["physics"]["narrative_drag"] += 10.0
            elif toxin_type == "GLYPHOSATE":
                self.health -= 5.0
        err_val = max(repetition_val, m["physics"]["counts"]["antigen"] * 0.2)
        coh_val = m["physics"]["truth_ratio"]
        exp_val = min(1.0, m["physics"]["voltage"] / 10.0)
        trace = {"err": err_val, "coh": coh_val, "exp": exp_val}
        has_bracelet = "TIME_BRACELET" in self.gordon.inventory
        heavy_count = m["physics"]["counts"]["heavy"]
        abstract_count = m["physics"]["counts"]["abstract"]
        is_hybrid = (heavy_count >= 2 and abstract_count >= 2)
        enzyme, nutrient = self.gut.secrete(text, m["physics"])
        print(f"{Prisma.GRY}🍽️ DIGESTION: {nutrient['desc']} detected. Secreting {enzyme}.{Prisma.RST}")
        drag = m["physics"]["narrative_drag"] + (2.0 if pulse_status == "ECHO" else 0)
        self.mitochondria.state.atp_pool += nutrient["yield"]
        self.mitochondria.state.ros_buildup += nutrient["toxin"]
        resp_status = self.mitochondria.respirate(
            nutrient["yield"],
            drag,
            has_bracelet=has_bracelet,
            is_hybrid=is_hybrid
        )
        if resp_status == "NECROSIS" or resp_status == self.mitochondria.APOPTOSIS_TRIGGER:
            print(f"{Prisma.RED}💀 APOPTOSIS TRIGGERED.{Prisma.RST}")
            self.mem.cannibalize(preserve_current=m["clean_words"])
            self.health -= 30
            return
        self.life.run_cycle(text, m, trace, has_bracelet, is_hybrid, enzyme)
        self.tick_count += 1
        chem_state = self.endocrine.get_state()
        chem_state["ATP"] = self.mitochondria.state.atp_pool
        adaptation = self.plasticity.adapt_generation_rules(trace, chem_state)
        if adaptation:
            print(f"\n{Prisma.MAG}{adaptation}{Prisma.RST}")
if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.paint('>>> BONEAMANITA 8.2.1', 'G')}")
    print(f"{Prisma.paint('System: ONLINE.', '0')}")
    print("Feed me, Seymour!\n")
    try:
        while True:
            try:
                u = input(f"{Prisma.paint('>', 'W')} ")
                if not u: continue
            except EOFError:
                break
            if u.lower() in ["exit", "quit", "/exit"]:
                mito_mutations = eng.mitochondria.adapt(eng.health)
                eng.mem.save(eng.health, eng.stamina, {}, eng.trauma_accum, eng.joy_history, mitochondria_traits=mito_mutations)
                print("Saved.")
                break
            eng.process(u)
    except KeyboardInterrupt:
        print("\nDisconnected.")