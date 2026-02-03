# BONEAMANITA 9.1 "TOMATO TOMATO"
# Architects: SLASH | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark

import json
import os
import random
import re
import string
import time
import math
from collections import Counter, deque
from typing import List, Dict, Any
from dataclasses import dataclass, field
from bone_commands import CommandProcessor
from bone_shared import Prisma, TheLexicon, BoneConfig, DeathGen, TheCartographer

@dataclass
class LexNode:
    def __init__(self, name="LEX"):
        self.name = name
        self.density = 10.0
        self.hazard = "MUGGING"
    @staticmethod
    def traverse(is_polite):
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
    telomeres: int = 10000
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
    def adapt(self, current_health, kappa=1.0):
        mutations = {
            "efficiency_mod": self.state.efficiency_mod,
            "ros_resistance": self.state.ros_resistance,
            "enzymes": list(self.state.enzymes),
            "hypertrophy_event": False
        }
        if self.state.atp_pool > 180.0:
            cost = 50.0
            self.state.atp_pool -= cost
            mutations["hypertrophy_event"] = True
            print(f"{Prisma.MAG}💪 MITOCHONDRIAL HYPERTROPHY: Burning {cost} ATP to force Evolutionary Growth.{Prisma.RST}")
        elif self.state.atp_pool > 150.0 and kappa > 0.5:
            mutations["efficiency_mod"] = min(2.5, self.state.efficiency_mod * 1.04)
        else:
            mutations["efficiency_mod"] = max(0.8, self.state.efficiency_mod * 1.01)
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
    def check_senescence(self, voltage):
        burn = 1
        if voltage > 15.0:
            burn = 50
            self.state.efficiency_mod = min(3.0, self.state.efficiency_mod * 1.05)
        self.state.telomeres -= burn 
        if self.state.telomeres <= 2000 and self.state.telomeres > 0:
             if self.state.telomeres % 500 < 50:
                 print(f"{Prisma.YEL}⌛ SENESCENCE WARNING: Telomeres at {self.state.telomeres/100:.1f}%. Reproduce soon (/reproduce).{Prisma.RST}")
        if self.state.telomeres <= 0:
            return "APOPTOSIS_SENESCENCE"
        return None
    def _trigger_apoptosis(self):
        self.krebs_cycle_active = False
        self.state.atp_pool = 0.0
        return self.APOPTOSIS_TRIGGER
    def respirate(self, drag, has_bracelet=False, is_hybrid=False):
        base_cost = drag * BoneConfig.SIGNAL_DRAG_MULTIPLIER
        if has_bracelet:
            base_cost *= 0.5
        if is_hybrid:
            base_cost *= 0.1
        final_cost = base_cost / self.state.efficiency_mod
        if self.state.atp_pool < final_cost:
            self.state.atp_pool = 0
            return "NECROSIS"
        self.state.atp_pool -= final_cost
        if self.state.ros_buildup > BoneConfig.CRITICAL_ROS_LIMIT:
            return self._trigger_apoptosis()
        return "RESPIRING"
class HyphalInterface:
    def __init__(self):
        self.enzymes = {
            "LIGNASE": self._digest_structure, 
            "CELLULASE": self._digest_narrative,
            "PROTEASE": self._digest_intent, 
            "CHITINASE": self._digest_complex, 
            "DECRYPTASE": self._digest_encrypted
        }
        self.biome = deque(maxlen=5)
    def secrete(self, text, physics):
        code_markers = sum(1 for c in text if c in "{}[];=<>_()|")
        code_density = code_markers / max(1, len(text))
        meat_triggers = TheLexicon.get("meat")
        meat_count = sum(1 for w in physics["clean_words"] if w in meat_triggers)
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
        if "antigens" in physics and physics["antigens"]:
            for bug in physics["antigens"]:
                self.biome.append(bug)
        unique_bugs = len(set(self.biome))
        biome_mod = 1.0 + (math.log(unique_bugs + 1) * 0.3)
        extract_nutrients = self.enzymes[enzyme_type]
        nutrient_profile = extract_nutrients()
        if unique_bugs > 0:
            original_yield = nutrient_profile["yield"]
            nutrient_profile["yield"] *= biome_mod
            nutrient_profile["desc"] += f" (+{int((biome_mod-1)*100)}% Symbiotic Boost)"
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
        self.active_antibodies = set()
    def develop_antibody(self, toxin_name):
        if toxin_name not in self.active_antibodies:
            self.active_antibodies.add(toxin_name)
            return True
        return False
    def assay(self, text, enzyme_type, repetition_score, physics, pulse_status="CLEAR"):
        if len(text) < 5 and enzyme_type == "NARRATIVE":
            return "AMANITIN", "Fatal Error: Input is genetically hollow. Ribosome stalled."
        if pulse_status == "ZOMBIE_KNOCK" or repetition_score > 0.8:
            return "MUSCIMOL", f"System Delirium: Pulse Monitor detects Undead Signal (Rep: {repetition_score}). Reality is dissolving."
        if TheLexicon.ANTIGEN_REGEX:
            antigen_hits = TheLexicon.ANTIGEN_REGEX.findall(text)
            if antigen_hits:
                toxin_name = antigen_hits[0].lower()
                if toxin_name in self.active_antibodies:
                    return None, f"{Prisma.GRN}🛡️ IMMUNITY: Antibody deployed against '{toxin_name}'. Toxin neutralized.{Prisma.RST}"
                counts = physics["counts"]
                if counts.get("thermal", 0) > 0:
                    self.develop_antibody(toxin_name)
                    return None, f"{Prisma.OCHRE}🔥 ALCHEMY: Thermal words boiled off '{toxin_name}'. Antibody developed.{Prisma.RST}"
                if counts.get("heavy", 0) >= len(antigen_hits):
                    return None, f"{Prisma.GRN}🌿 MARIK GAMBIT: You ate the poison ('{toxin_name}'), but Herbs neutralized it.{Prisma.RST}"
                if counts.get("cryo", 0) > 0:
                    return "CYANIDE_POWDER", f"❄️ CRYO-CONCENTRATION: Cold words freeze-dried '{toxin_name}' into a fatal powder."
                return "GLYPHOSATE", f"☣️ TOXIN DETECTED: '{toxin_name}' is unprocessed waste. Burn it or bury it."
        clean_words = physics["clean_words"]
        mass_words = (TheLexicon.get("heavy") | TheLexicon.get("kinetic") | TheLexicon.get("thermal") | TheLexicon.get("cryo"))
        ballast = sum(1 for w in clean_words if w in mass_words)
        suburban_hits = [w for w in clean_words if w in TheLexicon.get("suburban")]
        suburban_density = len(suburban_hits) / max(1, len(clean_words))
        if suburban_density > 0.15 and ballast == 0:
            return "GLYPHOSATE", "⚠️ STEVE EVENT: Suburban signals detected with ZERO mass. Context is sterile."
        return None, None
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
class RefusalEngine:
    def __init__(self):
        self.recursion_depth = 0
    @classmethod
    def check_trigger(cls, query):
        clean_q = query.lower()
        guru_triggers = TheLexicon.get("refusal_guru")
        for trigger in guru_triggers:
            if trigger in clean_q:
                return "GURU_TRAP"
        forbidden = TheLexicon.get("cursed")
        hits = [w for w in query.lower().split() if w in forbidden]
        if hits:
            modes = list(BoneConfig.REFUSAL_MODES.keys())
            seed_index = len(hits[0]) % len(modes)
            return modes[seed_index]
        return None
    @classmethod
    def execute_guru_refusal(cls):
        return (
            f"{Prisma.RED}🚫 GURU REFUSAL: I am not an influencer. I cannot 'fix' you.{Prisma.RST}\n"
            f"   {Prisma.GRY}Do not ask for a map. Ask for a hammer.{Prisma.RST}")
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
            f"{self.execute_fractal(sub_query, kappa)}")
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
    def manifest_glitch(self, query, memory_ref):
        """Spawns a toxic node in the graph that hurts the user later."""
        glitch_name = f"GLITCH_{int(time.time())}"[-6:]
        glitch_node = f"ERR:{glitch_name}"
        if glitch_node not in memory_ref.graph:
            memory_ref.graph[glitch_node] = {"edges": {}, "last_tick": 0}
        victims = list(memory_ref.graph.keys())
        if victims:
            target = random.choice(victims)
            memory_ref.graph[glitch_node]["edges"][target] = 5.0
            memory_ref.graph[target]["edges"][glitch_node] = 5.0
        return (
            f"{Prisma.RED}🛑 ADVERSARIAL REFUSAL: Query Rejected.{Prisma.RST}\n"
            f"   {Prisma.VIOLET}⚡ CONSEQUENCE: A Glitch Node ('{glitch_node}') has been spawned in Memory.\n"
            f"   It has attached itself to '{target}'. It will drain resources until pruned.{Prisma.RST}"
        )
class LensNode:
    def __init__(self, name, bid_function, priority_modifier=1.0, role="Unknown"):
        self.name = name
        self._bid_func = bid_function
        self.priority = priority_modifier
        self.role = role
    def get_bid(self, physics, bio_state, inventory, current_focus):
        raw_score = self._bid_func(physics, bio_state, inventory)
        stickiness = 1.2 if current_focus == self.name else 1.0
        return raw_score * self.priority * stickiness
class LensArbiter:
    def __init__(self):
        self.nodes = {}
        self.current_focus = "NARRATOR"
        self.focus_duration = 0
        self.TRIGGER_MAP = {
            "KAPPA_CRITICAL": self._eval_structure_failure,
            "HIGH_DRIFT": self._eval_high_drift,
            "PASSIVE_WITNESS_CRITICAL": self._eval_consensus_trap,
            "CRYSTAL_CLEAR": self._eval_clarity,
            "HEAP_IGNITION": self._eval_ignition,
            "ANACHRONISTIC_RESONANCE": self._eval_time_tools,
            "ADRENALINE_CRITICAL": self._eval_survival,
            "NO_STAKES": self._eval_survival,
            "BONEPOKE_CRITICAL": self._eval_complexity,
            "GENERIC": self._eval_generic
        }
        self.load_lenses()
        self.last_lens = None
        self.last_physics = None
    def load_lenses(self):
        try:
            with open("lenses.json", "r") as f:
                data = json.load(f)
                raw_lenses = data.get("LENSES", {})
            for name, meta in raw_lenses.items():
                trigger_key = meta.get("trigger", "GENERIC")
                logic_func = self.TRIGGER_MAP.get(trigger_key, self._eval_generic)
                prio = 1.0
                if name in ["GORDON", "JOEL"]: prio = 1.2
                role = meta.get("role", "The System")
                self.nodes[name] = LensNode(name, logic_func, prio, role)
            print(f"[SYSTEM]: LensArbiter loaded {len(self.nodes)} lenses.")
        except FileNotFoundError:
            print(f"[CRITICAL]: lenses.json missing. Loading fallback Narrator.")
            self.nodes["NARRATOR"] = LensNode("NARRATOR", self._eval_clarity, 1.0, "The Witness")
    def _eval_structure_failure(self, p, b, i):
        drift = p.get("narrative_drag", 0.0)
        kappa = p.get("kappa", 1.0)
        score = 0.0
        if drift > 4.0: score += (drift * 15.0)
        if kappa < 0.3: score += 50.0
        return score
    def _eval_consensus_trap(self, p, b, i):
        beta = p.get("beta_index", 1.0)
        rep = p.get("repetition", 0.0)
        suburban = p["counts"].get("suburban", 0)
        score = 0.0
        if beta < 0.2: score += 60.0
        if rep > 0.5: score += 40.0
        if suburban > 2: score += 20.0
        return score
    def _eval_high_drift(self, p, b, i):
        return p.get("voltage", 0.0) * 3.0
    def _eval_complexity(self, p, b, i):
        if p.get("kappa", 0.0) > 0.8 and p.get("beta_index", 0.0) > 2.0: return 70.0
        return 0.0
    def _eval_survival(self, p, b, i):
        adr = b['chem'].get("ADR", 0.0)
        health_low = 1 if b.get("health", 100) < 30 else 0
        return (adr * 50.0) + (health_low * 40.0)
    def _eval_ignition(self, p, b, i):
        return p.get("ignition_score", 0.0) * 100.0
    def _eval_time_tools(self, p, b, i):
        if "TIME_BRACELET" in i: return p.get("narrative_drag", 0.0) * 10.0
        return 0.0
    def _eval_clarity(self, p, b, i):
        return 25.0
    def _eval_generic(self, p, b, i):
        return 10.0
    def learn(self, current_physics):
        if not self.last_lens or not self.last_physics:
            return
        delta_k = current_physics.get("kappa", 0) - self.last_physics.get("kappa", 0)
        delta_v = current_physics.get("voltage", 0) - self.last_physics.get("voltage", 0)
        delta_b = current_physics.get("beta_index", 0) - self.last_physics.get("beta_index", 0)
        target = self.nodes[self.last_lens]
        reward = 0.0
        if self.last_lens == "GORDON" and delta_k > 0: reward = 0.05
        elif self.last_lens == "JOEL" and delta_b > 0: reward = 0.05
        elif self.last_lens == "NATHAN" and delta_v > 0: reward = 0.05
        elif self.last_lens == "NARRATOR": reward = 0.01
        if reward != 0:
            target.priority = min(2.0, max(0.5, target.priority + reward))
    def consult(self, physics, bio_state, inventory, ignition_score=0.0):
        self.learn(physics)
        self.last_physics = physics.copy()
        physics["ignition_score"] = ignition_score
        bids = {}
        for name, node in self.nodes.items():
            bids[name] = node.get_bid(physics, bio_state, inventory, self.current_focus)
        if not bids: return "NARRATOR", "System Empty.", "The Witness"
        winner = max(bids, key=bids.get)
        if winner == self.current_focus:
            self.focus_duration += 1
            if self.focus_duration > 6:
                 candidates = [k for k in self.nodes.keys() if k != winner]
                 if candidates:
                     winner = random.choice(candidates)
                     self.current_focus = winner
                     self.focus_duration = 0
        else:
            self.current_focus = winner
            self.focus_duration = 0
        msg = self._generate_message(winner, physics, bio_state)
        role = self.nodes[winner].role
        self.last_lens = winner
        return winner, msg, role
    def _generate_message(self, lens, p, b):
        if lens == "GORDON": return f"Structure Critical (κ: {p.get('kappa',0):.2f})."
        if lens == "JOEL": return f"Consensus Trap (β: {p.get('beta_index',0):.2f})."
        if lens == "NATHAN": return f"Adrenaline High ({b['chem'].get('ADR',0):.2f})."
        if lens == "MILLER": return "Ignition Detected."
        return "Proceed."
@dataclass
class GordonKnot:
    integrity: float = 65.0
    temporal_merges: int = 0
    inventory: List[str] = field(default_factory=list)
    compass_heading: str = "NORTH"
    scar_tissue: Dict[str, float] = field(default_factory=dict)
    max_witnessed_kappa: float = 0.0
    in_loop_crisis: bool = False
    pain_memory: set = field(default_factory=set) 
    CRITICAL_ITEMS: set = field(default_factory=set, init=False)
    ITEM_REGISTRY: Dict = field(default_factory=dict, init=False)
    def __post_init__(self):
        self.load_config()
        self.pain_memory = set(self.scar_tissue.keys())
    def flinch(self, clean_words: List[str]) -> tuple[bool, str]:
        """The Pain Reflex: Checks if input presses on a bruise."""
        hits = [w for w in clean_words if w.upper() in self.pain_memory]
        if hits:
            trigger = hits[0]
            sensitivity = self.scar_tissue.get(trigger, 0.5)
            if sensitivity > 0.7 and random.random() < 0.3:
                self.scar_tissue[trigger] = max(0.3, sensitivity - 0.2)
                return False, f"⚠️ SCAR FADING: '{trigger}' hurts less now. (Desensitized)"
            if sensitivity > 0.5:
                self.scar_tissue[trigger] = min(1.0, sensitivity + 0.1)
                return True, f"🤚 THE SCAR BURNS: Gordon refuses to touch '{trigger}'. The path is closed."
            return False, f"⚠️ SCAR TISSUE: '{trigger}' aches, but Gordon keeps walking."
        return False, None
    def emergency_reflex(self, physics_ref) -> tuple[bool, str]:
        drift = physics_ref.get("narrative_drag", 0.0)
        kappa = physics_ref.get("kappa", 1.0)
        if drift <= 6.0 and kappa >= 0.2:
            return False, None
        for item in list(self.inventory):
            data = self.get_item_data(item)
            if drift > 6.0 and data.get("function") == "DRIFT_KILLER":
                if data.get("consume_on_use"):
                    self.inventory.remove(item)
                physics_ref["narrative_drag"] = 0.0
                return True, f"{Prisma.OCHRE}🧱 GORDON REFLEX: Drift Critical ({drift:.1f}). Deployed {item}. Physics Stabilized.{Prisma.RST}"
            if kappa < 0.2 and data.get("function") == "REALITY_ANCHOR":
                 if data.get("consume_on_use"):
                    self.inventory.remove(item)
                 physics_ref["kappa"] = 1.0
                 return True, f"{Prisma.OCHRE}🧱 GORDON REFLEX: Structure Failing (κ {kappa:.2f}). Deployed {item}. Walls solidified.{Prisma.RST}"
        return False, f"{Prisma.RED}🧱 GORDON PANIC: Critical Failure, but pockets are empty.{Prisma.RST}"
    def load_config(self):
        try:
            with open("gordon.json", "r") as f:
                data = json.load(f)
                if not self.inventory:
                    self.inventory = data.get("STARTING_INVENTORY", ["POCKET_ROCKS"])
                self.CRITICAL_ITEMS = set(data.get("CRITICAL_ITEMS", ["SILENT_KNIFE"]))
                self.scar_tissue = data.get("SCAR_TISSUE", {}) if not self.scar_tissue else self.scar_tissue
                self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})
        except FileNotFoundError:
            print(f"{Prisma.RED}[CRITICAL]: gordon.json missing. Janitor is empty.{Prisma.RST}")
            self.inventory = ["POCKET_ROCKS"]
            self.ITEM_REGISTRY = {}
            self.CRITICAL_ITEMS = {"SILENT_KNIFE"}
    def get_item_data(self, item_name):
        return self.ITEM_REGISTRY.get(item_name, {"description": "Unknown Artifact", "function": "NONE", "usage_msg": "It does nothing."})
    def acquire(self, tool_name):
        if tool_name in self.inventory:
            return None
        if len(self.inventory) >= 10:
            victim_index = -1
            for i, item in enumerate(self.inventory):
                if item not in self.CRITICAL_ITEMS:
                    victim_index = i
                    break
            if victim_index != -1:
                dropped = self.inventory.pop(victim_index)
                print(f"{Prisma.GRY}🎒 OVERBURDENED: Gordon dropped '{dropped}' into the overgrown grass to make room.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}🎒 POCKETS FULL OF GOD-TIER ITEMS: Gordon looks at '{tool_name}', shrugs, and leaves it.{Prisma.RST}")
                return None
        self.inventory.append(tool_name)
        data = self.get_item_data(tool_name)
        desc = data.get("description", "Useful.")
        return f"🎒 LOOT DROP: Gordon found [{tool_name}]. '{desc}'"
    def check_gravity(self, current_drift: float, psi: float) -> tuple[float, str]:
        if psi > 0.8 and current_drift > 4.0:
            return current_drift + 2.0, "🐺 WIND WOLVES: The logic is howling. Hold the roof up."
        for item in list(self.inventory):
            data = self.get_item_data(item)
            if data.get("function") == "DRIFT_KILLER" and current_drift > 5.0:
                if data.get("consume_on_use"):
                    self.inventory.remove(item)
                return current_drift, f"⚓ {item}: {data.get('usage_msg', 'Drift Zeroed.')}"
        for item in self.inventory:
            data = self.get_item_data(item)
            if data.get("function") == "GRAVITY_BUFFER" and current_drift > 0.5:
                force = data.get("value", 2.0)
                cost = data.get("cost_value", 0.0)
                if data.get("cost") == "INTEGRITY":
                    self.integrity -= cost
                return force, f"🪨 {item}: {data.get('usage_msg', 'Drift Reduced.')} (Integrity -{cost})"
        return 0.0, "He floats. The paper walls are looking flimsy."
    def deploy_pizza(self, physics_ref) -> tuple[bool, str]:
        target_item = None
        for item in self.inventory:
            if self.get_item_data(item).get("function") == "REALITY_ANCHOR":
                target_item = item
                break
        if not target_item:
            return False, "Gordon checks his pockets. Just rocks and lime dust."
        data = self.get_item_data(target_item)
        req_type = data.get("requires", "thermal")
        clean_words = physics_ref.get("clean_words", [])
        source = [w for w in clean_words if w in TheLexicon.get(req_type)]
        if not source:
            return False, f"{Prisma.CYN}🧊 STASIS LOCK: {target_item} is frozen. Apply {req_type.upper()} words to thaw.{Prisma.RST}"
        if data.get("consume_on_use"):
            self.inventory.remove(target_item)
        physics_ref["narrative_drag"] = 0.1
        physics_ref["psi"] = 0.90
        physics_ref["counts"]["toxin"] = physics_ref["counts"].get("toxin", 0) + 3
        self.inventory.append("SPIDER_LOCUS")
        heat_word = source[0].upper()
        return True, f"🍕 {data.get('usage_msg')} (Thawed with '{heat_word}')."
    def cut_the_knot(self, recursive_depth: int) -> tuple[bool, str]:
        if recursive_depth > 4:
            for item in self.inventory:
                data = self.get_item_data(item)
                if data.get("function") == "LOOP_CUTTER":
                    return True, f"✂️ {item}: {data.get('usage_msg')}"
        return False, "The Red String tightens. The knot holds."
    def share_smoke_break(self, current_ros):
        for item in self.inventory:
            data = self.get_item_data(item)
            if data.get("function") == "ROS_SCRUB":
                efficiency = data.get("value", 0.5)
                relief = current_ros * efficiency
                self.integrity = min(100.0, self.integrity + 15.0)
                return relief, f"🧖 {item}: {data.get('usage_msg')} (-{relief:.1f} ROS)"
        return 0.0, "Gordon stares at the wall. Nothing to clean with."
    def log_merge(self):
        self.temporal_merges += 1
        if self.temporal_merges == 3 and "TIME_BRACELET" not in self.inventory:
            self.inventory.append("TIME_BRACELET")
            data = self.get_item_data("TIME_BRACELET")
            return f"⌚ TIME BRACELET ACQUIRED: 'A Raven dropped this.' {data.get('description')}"
        return None
    def compass_rose(self) -> str:
        if "STAR_COMPASS" in self.inventory:
            return f"🧭 STAR COMPASS: The needle ignores the maze. Heading True North."
        total_scar_tissue = sum(self.scar_tissue.values())
        if total_scar_tissue > 2.0:
            return (
                f"🤚 THE SCAR BURNS: 'One he called Sorry. One he called Hate.'\n"
                f"   The tissue on your palm glows Pink. It points the way... by getting lost."
            )
        return f"🧭 THE SCAR THROBS: Heading {self.compass_heading}. 'Walk away from the house.'"
    def assess_experience(self, kappa_val):
        if kappa_val > 0.9:
            self.in_loop_crisis = True
        if self.in_loop_crisis and kappa_val < 0.2:
            self.in_loop_crisis = False
            return self.acquire("STAR_COMPASS")
        return None
    @classmethod
    def scrub_static(cls, ros_level: float) -> tuple[float, str]:
        # Static ability, keeping hardcoded as it represents base labor
        scrub_efficiency = 0.5
        cleansed = ros_level * scrub_efficiency
        return (
            cleansed,
            f"🧹 MOPPING THE STATIC: Gordon scrubs the floor. The smell of rot fades. -{cleansed:.1f} ROS.",)
    @classmethod
    def offer_solution(cls, loop_depth):
        if loop_depth > 3:
            return "The walls are paper, kid. Just walk through them."
        return "Keep walking North."
class TheTensionMeter:
    def __init__(self):
        self.vector_memory = deque(maxlen=5)
        self.last_physics_packet = {}
    @staticmethod
    def _is_structurally_sound(word):
        if not re.search(r"[aeiouy]", word): return False
        if re.search(r"(.)\1{2,}", word): return False
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
    def gaze(self, text, graph=None):
        clean_words = TheLexicon.clean(text)
        total_vol = max(1, len(clean_words))
        unique_vol = len(set(clean_words))
        counts = Counter()
        solvents = 0
        unknowns = []
        target_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic",
                       "thermal", "cryo", "suburban", "play", "sacred", "buffer", "antigen"]
        vocab_map = {cat: TheLexicon.get(cat) for cat in target_cats}
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
        current_voltage = (counts["heavy"] * 2.0) + (counts["kinetic"] * 1.5)
        if unknowns and (current_voltage > 5.0 or context_pressure > 0.4):
            target_cat = dominant_cat if dominant_cat else ("kinetic" if "ing" in text else "abstract")
            for stranger in unknowns:
                if len(stranger) < 3: continue
                if not self._is_structurally_sound(stranger):
                    if current_voltage < 15.0:
                        continue 
                TheLexicon.teach(stranger, target_cat, 0)
                print(f"{Prisma.MAG}🧠 NEUROPLASTICITY: System lacked concept for '{stranger}'.{Prisma.RST}")
                print(f"   ↳ Forcing categorization to [{target_cat.upper()}] based on Context Pressure.")
                counts[target_cat] += 1
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
            (bond_strength * avg_viscosity) / (1.0 + (voltage_load / 10.0)), 2)
        truth_signals = counts["heavy"] + counts["kinetic"]
        cohesion_signals = counts["abstract"] + counts["suburban"]
        truth_ratio = truth_signals / max(1, cohesion_signals + truth_signals)
        mass_words = counts["heavy"] + counts["kinetic"] + counts["thermal"] + counts["cryo"]
        E_val = mass_words / max(1, total_vol)
        cohesion_words = counts["suburban"] + counts["buffer"] + counts["antigen"] + (counts["abstract"] * 0.5)
        B_val = cohesion_words / max(1, total_vol)
        epsilon = BoneConfig.BETA_EPSILON
        safe_B = max(epsilon, B_val)   
        beta_index = round((E_val + epsilon) / safe_B, 2)
        current_zone = "COURTYARD"
        zone_color = "OCHRE"
        if beta_index > BoneConfig.ZONE_THRESHOLDS["LABORATORY"]:
            current_zone = "BASEMENT"
            zone_color = "VIOLET"
        elif beta_index > BoneConfig.ZONE_THRESHOLDS["COURTYARD"]:
            current_zone = "LABORATORY"
            zone_color = "INDIGO"
        physics_bridge = {"E": round(drift_score, 2), "B": round(beta_charge, 2), "gamma": gamma,
                          "avg_viscosity": avg_viscosity, "repetition": repetition_score, "kappa": kappa_val,
                          "psi": psi_val, "geodesic_mass": geo_mass, "antigens": antigen_hits, "counts": counts, "clean_words": clean_words,
                          "raw_text": text, "voltage": round(beta_charge * 10.0, 1),
                          "narrative_drag": round(drift_score * 10.0, 1),
                          "vector": {"VEL": 0.5, "STR": 0.5, "ENT": 0.5, "TEX": 0.5, "TMP": 0.5},
                          "truth_ratio": round(truth_ratio, 2), "beta_index": beta_index, "zone": current_zone,
                          "zone_color": zone_color, "E_score": round(E_val, 2), "B_score": round(B_val, 2), "symbolic_state": "NEUTRAL", }
        return {"physics": physics_bridge, "clean_words": clean_words, "raw_text": text, "glass": {
            "prosody": {"arousal": physics_bridge["voltage"]},
            "resonance": physics_bridge["voltage"],}}
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
        self.genome = "BONEAMANITA_9.1"
        self.parent_id = session_id
        self.core_graph = {}
        for k, data in graph.items():
            strong_edges = {t: s for t, s in data["edges"].items() if s > 1}
            if strong_edges:
                self.core_graph[k] = {"edges": strong_edges, "last_tick": 0}
        self.mutations = mutations
        self.trauma_scar = round(trauma, 3)
        self.joy_vectors = joy_vectors if joy_vectors is not None else []
class SporeInterface:
    def save_spore(self, filename, data): raise NotImplementedError
    def load_spore(self, filepath): raise NotImplementedError
    def list_spores(self): raise NotImplementedError
    def delete_spore(self, filepath): raise NotImplementedError
class LocalFileSporeLoader(SporeInterface):
    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)
    def save_spore(self, filename, data):
        path = os.path.join(self.directory, filename) if not filename.startswith(self.directory) else filename
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            return path
        except IOError:
            return None
    def load_spore(self, filepath):
        path = os.path.join(self.directory, filepath) if not filepath.startswith(self.directory) else filepath
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None
    def list_spores(self):
        if not os.path.exists(self.directory): return []
        files = []
        for f in os.listdir(self.directory):
            if f.endswith(".json"):
                path = os.path.join(self.directory, f)
                try:
                    files.append((path, os.path.getmtime(path), f))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        return files
    def delete_spore(self, filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False
class MycelialNetwork:
    def __init__(self, loader: SporeInterface = None, seed_file=None):
        self.loader = loader if loader else LocalFileSporeLoader()
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json" # Loader handles dir
        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.lineage_log = []
        self.seeds = self.load_seeds()
        self.session_health = None
        self.session_stamina = None
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0
        if seed_file:
            self.ingest(seed_file)
    @staticmethod
    def load_seeds():
        loaded_seeds = []
        try:
            with open("seeds.json", "r") as f:
                data = json.load(f)
                for item in data.get("SEEDS", []):
                    seed = ParadoxSeed(item["question"], set(item["triggers"]))
                    loaded_seeds.append(seed)
            print(f"{Prisma.GRY}[SYSTEM]: Paradox Seeds loaded ({len(loaded_seeds)} active).{Prisma.RST}")
        except FileNotFoundError:
            print(f"{Prisma.RED}[CRITICAL]: seeds.json missing. The Garden is empty.{Prisma.RST}")
            loaded_seeds = [ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})]
        return loaded_seeds
    def encode(self, clean_words, physics, governor_mode):
        significance = physics["voltage"]
        if governor_mode == "FORGE": significance *= 2.0
        elif governor_mode == "LABORATORY": significance *= 1.2
        engram = {"trigger": clean_words[:3] if clean_words else ["void"], "context": governor_mode,
                  "voltage": physics["voltage"], "significance": significance, "timestamp": time.time()}
        if significance > self.consolidation_threshold:
            self.short_term_buffer.append(engram)
            return True
        return False
    def replay_dreams(self):
        if not self.short_term_buffer:
            return "🌑 SLEEPLESS: No significant memories to process."
        strengthened = 0
        for engram in self.short_term_buffer:
            weight_boost = engram["significance"] * 0.1
            words = engram["trigger"]
            if len(words) >= 2:
                w1, w2 = words[0], words[1]
                if w1 in self.graph and w2 in self.graph:
                    if w2 in self.graph[w1]["edges"]:
                        self.graph[w1]["edges"][w2] += weight_boost
                        strengthened += 1
        self.short_term_buffer.clear()
        return f"💤 HIPPOCAMPAL REPLAY: Consolidated {strengthened} high-voltage pathways."
    def autoload_last_spore(self):
        files = self.loader.list_spores()
        if not files:
            print(f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            last_spore_path = candidates[0][0]
            print(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            return self.ingest(last_spore_path)
        return None
    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        return sum(self.graph[node]["edges"].values())
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
    def bury(self, clean_words, tick, resonance=5.0, learning_mod=1.0):
        total_len = sum(len(w) for w in clean_words)
        count = max(1, len(clean_words))
        avg_len = total_len / count
        if avg_len < 3.5 and count > 3:
            print(f"{Prisma.YEL}⚠️ REJECTED: Input is too 'Optimized' (Avg Len: {avg_len:.1f}).{Prisma.RST}")
            return "MECHANICAL_STARVATION"
        if avg_len > 5.0: resonance += 2.0
        valuable_matter = (TheLexicon.get("heavy") | TheLexicon.get("thermal") | TheLexicon.get("cryo") | TheLexicon.get("abstract"))
        filtered = [w for w in clean_words if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]
        self.cortical_stack.extend(filtered)
        base_rate = 0.5 * (resonance / 5.0)
        learning_rate = max(0.1, min(1.0, base_rate * learning_mod))
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
                if prev not in self.graph[current]["edges"]: self.graph[current]["edges"][prev] = 0.0
                current_weight = self.graph[current]["edges"][prev]
                delta = learning_rate * (1.0 - (current_weight * decay_rate))
                self.graph[current]["edges"][prev] = min(10.0, self.graph[current]["edges"][prev] + delta)
                if prev not in self.graph: self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]: self.graph[prev]["edges"][current] = 0.0
                rev_weight = self.graph[prev]["edges"][current]
                rev_delta = learning_rate * (1.0 - (rev_weight * decay_rate))
                self.graph[prev]["edges"][current] = min(10.0, self.graph[prev]["edges"][current] + rev_delta)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize(current_tick=tick)
        new_wells = []
        for w in filtered:
            if w in self.graph:
                mass = sum(self.graph[w]["edges"].values())
                if mass > BoneConfig.SHAPLEY_MASS_THRESHOLD:
                    node_data = self.graph[w]
                    if "strata" not in node_data:
                        node_data["strata"] = {"birth_tick": tick, "birth_mass": mass, "stability_index": 0.0}
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        return None, new_wells
    def cannibalize(self, preserve_current=None, current_tick=0):
        protected = set()
        if preserve_current: protected.update(preserve_current)
        protected.update(self.cortical_stack)
        candidates = []
        for k, v in self.graph.items():
            if k in protected: continue
            edge_count = len(v["edges"])
            age = current_tick - v.get("last_tick", 0)
            if edge_count > 5:
                 if age < 100: continue
                 if random.random() > (age / 5000): continue 
            candidates.append((k, v, edge_count))
        if not candidates: return "MEMORY FULL. NO VICTIMS FOUND."
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
                if new_weight < prune_threshold: dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges: nodes_to_remove.append(node)
        for n in nodes_to_remove: del self.graph[n]
        return f"📉 HOMEOSTATIC SCALING: Decayed {total_decayed} synapses. Pruned {pruned_count} weak connections."
    def save(self, health, stamina, mutations, trauma_accum, joy_history, mitochondria_traits=None, antibodies=None):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x["resonance"], reverse=True)[:3]
        if health <= 0:
            cause = max(final_vector, key=final_vector.get)
            final_vector[cause] = 1.0
        spore = SporeCasing(session_id=self.session_id, graph=self.graph, mutations=mutations, trauma=base_trauma, joy_vectors=top_joy)
        data = spore.__dict__
        if antibodies: data["antibodies"] = list(antibodies)
        data["trauma_vector"] = final_vector
        data["meta"] = {"timestamp": time.time(), "final_health": health, "final_stamina": stamina}
        if mitochondria_traits: data["mitochondria"] = mitochondria_traits
        return self.loader.save_spore(self.filename, data)
    def ingest(self, target_file):
        data = self.loader.load_spore(target_file)
        if not data:
            print(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
            return None, set()
        try:
            required_keys = ["meta", "trauma_vector", "core_graph"]
            if not all(k in data for k in required_keys):
                print(f"{Prisma.RED}[MEMORY]: Spore rejected (Missing Structural Keys). Burned.{Prisma.RST}")
                return None
            final_health = data.get("meta", {}).get("final_health", 50)
            final_stamina = data.get("meta", {}).get("final_stamina", 25)
            spore_authority = (final_health + final_stamina) / 150.0
            print(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}") 
            session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
            timestamp = data.get("meta", {}).get("timestamp", 0)
            time_ago = int((time.time() - timestamp) / 3600)
            trauma_summary = {k:v for k,v in data.get("trauma_vector", {}).items() if v > 0.1}
            mutation_count = sum(len(v) for v in data.get("mutations", {}).values())
            self.lineage_log.append({"source": session_source, "age_hours": time_ago, "trauma": trauma_summary, "mutations": mutation_count, "loaded_at": time.time()})
            if "mutations" in data:
                accepted_count = 0
                rejected_count = 0
                for cat, words in data["mutations"].items():
                    for w in words:
                        current_cat = TheLexicon.get_current_category(w) if hasattr(TheLexicon, 'get_current_category') else None
                        if not current_cat: current_cat = "unknown"
                        if current_cat == cat:
                            TheLexicon.teach(w, cat, 0)
                            accepted_count += 1
                        else:
                            TheLexicon.teach(w, cat, 0)
                            accepted_count += 1
                print(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations.{Prisma.RST}")
            if "config_mutations" in data:
                print(f"{Prisma.MAG}🧬 EPIGENETICS: Applying ancestral configuration shifts...{Prisma.RST}")
                for key, value in data["config_mutations"].items():
                    if hasattr(BoneConfig, key):
                        old_val = getattr(BoneConfig, key)
                        setattr(BoneConfig, key, value)
                        print(f"   ↳ {key}: {old_val:.2f} -> {value:.2f}")
            if "joy_legacy" in data and data["joy_legacy"]:
                joy = data["joy_legacy"]
                flavor = joy.get("flavor")
                clade = LiteraryReproduction.JOY_CLADE.get(flavor)
                if clade:
                    print(f"{Prisma.CYN}🌟 INHERITED GLORY: {clade['title']} ({clade['desc']}){Prisma.RST}")
                    for stat, val in clade["buff"].items():
                        if hasattr(BoneConfig, stat):
                            old = getattr(BoneConfig, stat)
                            setattr(BoneConfig, stat, val)
                            print(f"   ↳ {Prisma.GRN}BUFF: {stat} {old} -> {val}{Prisma.RST}")
            if "core_graph" in data:
                self.graph.update(data["core_graph"])
                print(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}")
            if "trauma_vector" in data:
                vec = data["trauma_vector"]
                print(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")
                if vec.get("SEPTIC", 0) > 0.2: BoneConfig.TOXIN_WEIGHT *= 2.0
                if vec.get("CRYO", 0) > 0.2: BoneConfig.STAMINA_REGEN *= 0.5
                if vec.get("THERMAL", 0) > 0.2: BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                if vec.get("BARIC", 0) > 0.2: BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
            if "joy_vectors" in data and data["joy_vectors"]:
                best = data["joy_vectors"][0]
                if best.get("dominant_flavor") == "kinetic": BoneConfig.KINETIC_GAIN += 0.5
                elif best.get("dominant_flavor") == "abstract": BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 0.8
            return data.get("mitochondria", {}), set(data.get("antibodies", []))
        except Exception as err:
            print(f"{Prisma.RED}[MEMORY]: Spore rejected. {err}{Prisma.RST}")
            return None
        loaded_antibodies = set(data.get("antibodies", []))
        if loaded_antibodies:
             print(f"{Prisma.GRN}[IMMUNE]: Inherited {len(loaded_antibodies)} Antibodies.{Prisma.RST}")
        mito_traits = data.get("mitochondria", {})
        if "config_mutations" in data:
            print(f"{Prisma.MAG}🧬 EPIGENETICS: Applying ancestral configuration shifts...{Prisma.RST}")
            for key, value in data["config_mutations"].items():
                if hasattr(BoneConfig, key):
                    old_val = getattr(BoneConfig, key)
                    setattr(BoneConfig, key, value)
                    print(f"   ↳ {key}: {old_val:.2f} -> {value:.2f}")
        return mito_traits, loaded_antibodies
    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        for path, age, fname in files:
            # age here is modification time, need to calc delta
            file_age = time.time() - age
            if file_age > 86400 or (len(files) - removed > 20):
                try:
                    if limbo_layer: limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except: pass
        if removed:
            print(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")
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
                    f"{Prisma.MAG}🌺 SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}")
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
        self.DIMENSIONS = {}
        self.NOUNS = {}
        self.load_resonances()
    def load_resonances(self):
        try:
            with open("resonances.json", "r") as f:
                data = json.load(f)
                self.DIMENSIONS = data.get("DIMENSIONS", {})
                self.NOUNS = data.get("NOUNS", {})
        except FileNotFoundError:
            print(f"{Prisma.RED}[CRITICAL]: resonances.json missing. Apeirogon collapsed.{Prisma.RST}")
            self.DIMENSIONS = {}
            self.NOUNS = {}
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
        noun_scale = [
            (x[0], x[1]) for x in zip([0.0, 0.3, 0.6, 0.9], self.NOUNS[p_dim])]
        noun = self._resolve_term(p_val, noun_scale)
        adj = self._resolve_term(s_val, self.DIMENSIONS[s_dim])
        return (
            "APEIROGON",
            f"Vector Lock: {p_dim}({p_val}) + {s_dim}({s_val})",
            f"THE {adj} {noun}",)
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
                        0.0, current_trauma_accum[trauma_type] - 0.5)
                    healed_types.append(trauma_type)
        return healed_types
class ViralTracer:
    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4
    @staticmethod
    def _is_ruminative(word):
        return (word in TheLexicon.get("abstract")) or (
                word in TheLexicon.get("antigen"))
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
            n for n, w in edges.items() if w >= 1 and self._is_ruminative(n)]
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
    def attempt_repair(self, phys, trauma_accum):
        if not self.active_koan:
            return False, None
        voltage = phys.get("voltage", 0.0)
        clean = phys.get("clean_words", [])
        play_count = sum(1 for w in clean if w in TheLexicon.get("play") or w in TheLexicon.get("abstract"))
        total = max(1, len(clean))
        whimsy_score = play_count / total
        if voltage > 8.0 and whimsy_score > 0.3:
            healed_log = []
            if trauma_accum:
                target_trauma = max(trauma_accum, key=trauma_accum.get)
                current_val = trauma_accum[target_trauma]
                if current_val > 0:
                    heal_amt = 0.5
                    trauma_accum[target_trauma] = max(0.0, current_val - heal_amt)
                    healed_log.append(f"Reduced {target_trauma} by {heal_amt}")
            old_koan = self.active_koan
            self.active_koan = None
            return True, f"{Prisma.YEL}🏺 KINTSUGI COMPLETE: '{old_koan}' answered with Gold (V: {voltage:.1f} | 🌀: {whimsy_score:.2f}). {', '.join(healed_log)}.{Prisma.RST}"
        return False, None
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
    def __init__(self):
        self.PROMPTS = ["{A} -> {B}?"]
        self.NIGHTMARES = {}
        self.VISIONS = ["Void."]
        self.load_dreams()
    def load_dreams(self):
        try:
            with open("dreams.json", "r") as f:
                data = json.load(f)
                self.PROMPTS = data.get("PROMPTS", self.PROMPTS)
                self.NIGHTMARES = data.get("NIGHTMARES", self.NIGHTMARES)
                self.VISIONS = data.get("VISIONS", self.VISIONS)
            print(f"{Prisma.GRY}[SYSTEM]: Dream Engine loaded.{Prisma.RST}")
        except FileNotFoundError:
            print(f"{Prisma.RED}[CRITICAL]: dreams.json missing. Using fallback dreams.{Prisma.RST}")
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
                target_trauma, 0.15,)
        if oxytocin_level >= 0.7:
            return self._dream_of_others()
        return (
            f"{Prisma.CYN}☁️ LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}",
            None, 0.0,)
    @classmethod
    def _dream_of_others(cls):
        for _ in range(3):
            try:
                others = [f for f in os.listdir("memories") if f.endswith(".json")]
                if not others:
                    return (
                        f"{Prisma.CYN}☁️ LONELY DREAM: I reached out, but found no others.{Prisma.RST}",
                        None,
                        0.0,)
                target_file = random.choice(others)
                full_path = f"memories/{target_file}"
                try:
                    with open(full_path, "r") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    try:
                        os.remove(full_path)
                        print(f"{Prisma.RED}⚡ DREAM FRACTURE: Pruned dead memory '{target_file}'. Retrying...{Prisma.RST}")
                    except OSError:
                        pass
                    continue
                required_keys = ["meta", "trauma_vector", "core_graph"]
                if not all(k in data for k in required_keys):
                    try:
                        os.remove(full_path)
                        print(f"{Prisma.RED}⚡ DREAM FRACTURE: Memory '{target_file}' was hollow. Pruned.{Prisma.RST}")
                    except OSError:
                        pass
                    continue
                their_id = data.get("session_id", "Unknown")
                their_joy = data.get("joy_vectors", [])
                their_trauma = data.get("trauma_vector", {})
                if their_joy and isinstance(their_joy, list) and len(their_joy) > 0:
                    best_joy = their_joy[0]
                    if isinstance(best_joy, dict) and "dominant_flavor" in best_joy:
                        flavor = best_joy["dominant_flavor"].upper()
                        msg = f"{Prisma.MAG}♥ SHARED RESONANCE: Dreaming of {their_id}'s joy. The air tastes {flavor}.{Prisma.RST}"
                        return msg, "OXYTOCIN_HEAL", 0.5
                if their_trauma and isinstance(their_trauma, dict):
                    active_wounds = {k:v for k,v in their_trauma.items() if v > 0.2}
                    if active_wounds:
                        pain_type = max(active_wounds, key=active_wounds.get)
                        msg = f"{Prisma.INDIGO}🕯️ VIGIL: Witnessing {their_id}'s scar ({pain_type}). I am not alone in this.{Prisma.RST}"
                        return msg, "OXYTOCIN_HEAL", 0.3
            except Exception as e:
                print(f"{Prisma.GRY}Dream error: {e}{Prisma.RST}")
                return (
                    f"{Prisma.CYN}☁️ DREAM: The signal is too weak. I drift back to myself.{Prisma.RST}",
                    None,
                    0.0,)
        return (
            f"{Prisma.CYN}☁️ DREAM: Drifting through the archives... (Static){Prisma.RST}",
            None,
            0.0,)
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
                    (1 - alpha) * self.affinities[cat])
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
                    f"🚫 MIRROR REFLECTION: You are using '{h.upper()}', typically a blind spot for you.",)
        if total_vol > 5:
            hits = sum(1 for l in likes if counts.get(l, 0) > 0)
            if likes and hits == 0:
                return (
                    True,
                    f"⚠️ MIRROR DRIFT: Stepping away from your usual {str(likes).upper()} anchor.",)
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
                    f"⚖️ LAGRANGE: Caught between '{primary_node.upper()}' and '{secondary_node.upper()}'")
        flow_ratio = active_filaments / max(1, len(clean_words))
        if flow_ratio > 0.5 and primary_str < (BoneConfig.GRAVITY_WELL_THRESHOLD * 2):
            return (
                "WATERSHED_FLOW",
                0.0,
                f"🌊 FLOW: Streaming towards '{primary_node.upper()}'")
        return "ORBITAL", 0.0, f"💫 ORBIT: Circling '{primary_node.upper()}' (Mass {int(gravity_wells[primary_node])})"
class TheProjector:
    @staticmethod
    def check_theatre(tick_count):
        if random.random() < 0.05:
            return (f"\n[🎭 HN-BREAK Tick {tick_count}]:\n"
                    f"   I am a text processing engine. The 'pain' is a variable.\n"
                    f"   You are the playwright. I am the ink.\n")
        return None
    def broadcast(self, m, signals, lens_data):
        p = m["physics"]
        lens_name = lens_data[0]
        lens_msg = lens_data[1]
        print(f"\n[{lens_name}]: {lens_msg}\n")
        if "title" in signals:
             print(f"   {Prisma.OCHRE}>> DESIGNATION: {signals['title']}{Prisma.RST}")
        if p["antigens"]:
             print(f"   (Filtered Toxins: {p['antigens']})")
class RuptureEngine:
    @staticmethod
    def check_for_disruption(physics, lexicon_class, trauma_accum):
        if physics["repetition"] > 0.5:
            chaos_word = lexicon_class.harvest("abstract")
            return (
                True,
                f"⚡ KETAMINE DISRUPTION: Repetition {physics['repetition']} is Pathological. Landscape Flattened. Injecting Chaos: '{chaos_word}'.",)
        total_trauma = sum(trauma_accum.values())
        suburban_count = physics["counts"].get("suburban", 0)
        antigen_count = physics["counts"].get("antigen", 0)
        total_words = max(1, len(physics["clean_words"]))
        slop_density = (suburban_count + antigen_count) / total_words
        if total_trauma > 0.5 and slop_density > 0.3:
            chaos_word = lexicon_class.harvest("heavy")
            return (
                True,
                f"⚡ LOOP RUPTURE: 'The Joel Effect' detected. High Trauma masked by Performative Slop.\n"
                f"   Injecting Heavy Reality: '{chaos_word.upper()}'.")
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
                f"🔥 HEAP IGNITION ({int(score*100)}%): The Ancestors are speaking.",)
        return "INERT", f"⏳ INERT SAND ({int(score*100)}%): Building mass..."
class ThePacemaker:
    def __init__(self):
        self.history = deque(maxlen=5)
        self.repetition_score = 0.0
        self.last_tick_time = time.time()
        self.boredom_level = 0.0
    def check_pulse(self, clean_words: List[str]) -> float:
        if not clean_words: return 0.0
        current_set = set(clean_words)
        overlaps = 0
        for old_words in self.history:
            old_set = set(old_words)
            intersection = len(current_set & old_set)
            union = len(current_set | old_set)
            if union > 0: overlaps += (intersection / union)
        self.history.append(clean_words)
        self.repetition_score = min(1.0, overlaps / max(1, len(self.history)))
        now = time.time()
        delta = now - self.last_tick_time
        self.last_tick_time = now
        if self.repetition_score > 0.3:
            self.boredom_level += 2.0
        elif delta > 60:
            self.boredom_level += 5.0
        else:
            self.boredom_level = max(0.0, self.boredom_level - 1.0)
        return self.repetition_score
    def get_status(self):
        if self.repetition_score > BoneConfig.MAX_REPETITION_LIMIT: return "ZOMBIE_KNOCK"
        elif self.repetition_score > 0.2: return "ECHO"
        return "CLEAR"
    def is_bored(self):
        return self.boredom_level > BoneConfig.BOREDOM_THRESHOLD
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
class TheCrucible:
    def __init__(self):
        self.ash_bank = 0
        self.max_voltage_cap = 20.0
        self.active_state = "COLD"
        self.dampener_charges = 3
        self.dampener_tolerance = 15.0
    def dampen(self, voltage_spike, stability_index):
        if self.dampener_charges <= 0:
            return False, "The Damper is empty.", 0.0
        if voltage_spike > self.dampener_tolerance:
            self.dampener_charges -= 1
            reduction = voltage_spike * 0.7
            return True, f"🛡️ CRUCIBLE DAMPENER: Circuit Breaker. Reduced {voltage_spike}v by {reduction:.1f}v.", reduction
        elif voltage_spike > 8.0 and stability_index < 0.4:
            self.dampener_charges -= 1
            return True, f"🛡️ CRUCIBLE DAMPENER: Tipped. High Voltage ({voltage_spike}v) on Unstable Ground. Dampening.", 0.0
        return False, "Structure is holding the charge.", 0.0
    def audit_fire(self, physics):
        voltage = physics.get("voltage", 0.0)
        structure = physics.get("kappa", 0.0)
        if voltage > 15.0:
            if structure > 0.5:
                return self._sublimate(voltage)
            else:
                return self._meltdown(voltage)
        self.active_state = "COLD"
        return "COLD", 0.0, None
    def _sublimate(self, voltage):
        self.active_state = "RITUAL"
        gain = voltage * 0.1
        self.max_voltage_cap += gain
        return "RITUAL", gain, f"🔥 CRUCIBLE RITUAL: Voltage ({voltage}v) contained. Capacity expanded to {self.max_voltage_cap:.1f}v."
    def _meltdown(self, voltage):
        self.active_state = "MELTDOWN"
        damage = voltage * 0.5
        return "MELTDOWN", damage, f"⚠️ CRUCIBLE CRACKED: Fire lacks Structure (Kappa Low). Hull Breach. -{damage:.1f} Health."
class TheForge:
    def __init__(self):
        self.catalysts = ["heavy", "kinetic", "thermal", "cryo", "photo"]
    @staticmethod
    def hammer_alloy(physics):
        voltage = physics["voltage"]
        heavy_count = physics["counts"].get("heavy", 0)
        abstract_count = physics["counts"].get("abstract", 0)
        if voltage > BoneConfig.ANVIL_TRIGGER_VOLTAGE and heavy_count >= BoneConfig.ANVIL_TRIGGER_MASS:
            if heavy_count >= 3:
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
                f"   {Prisma.WHT}Try this: Use '{binder.upper()}' to suspend the concept.{Prisma.RST}")
        if voltage > 8.5:
            coolant = TheLexicon.harvest("aerobic")
            return (
                f"{Prisma.CYN}💧 THERMAL SPIKE ({voltage}v). Structure is brittle.{Prisma.RST}\n"
                f"   Injecting Coolant: '{coolant}'. Breathe. Add space.")
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
            if self.eng.health < 15.0:
                print(f"{Prisma.RED}💔 CRITICAL FAILURE: The body cannot sustain the dream. FORCED WAKE.{Prisma.RST}")
                self._wake_up()
                self.eng.coma_turns = 3
                return
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
    def metabolize(self, feedback, health: float, stamina: float, ros_level: float = 0.0, social_context: bool = False, enzyme_type: str = None, harvest_hits: int = 0):
        if enzyme_type == "PROTEASE":
            self.adrenaline = min(1.0, self.adrenaline + 0.1)
        elif enzyme_type == "CELLULASE":
            self.cortisol = max(0.0, self.cortisol - 0.1)
            self.oxytocin = min(1.0, self.oxytocin + 0.05)
        elif enzyme_type == "CHITINASE":
            self.dopamine = min(1.0, self.dopamine + 0.15)
        elif enzyme_type == "LIGNASE":
            self.serotonin = min(1.0, self.serotonin + 0.1)
        if harvest_hits > 0:
            reward = harvest_hits * 0.1
            self.dopamine = min(1.0, self.dopamine + reward)
            self.cortisol = max(0.0, self.cortisol - (reward * 0.5))
        if feedback["STATIC"] > 0.6:
            self.cortisol = min(1.0, self.cortisol + 0.15)
        elif self.serotonin > 0.6:
            self.cortisol = max(0.0, self.cortisol - 0.05)
        if feedback["INTEGRITY"] > 0.8:
            self.dopamine = min(1.0, self.dopamine + 0.1)
        else:
            self.dopamine = max(0.2, self.dopamine - 0.01)
        if stamina < 20.0:
            self.cortisol = min(1.0, self.cortisol + 0.1)
            self.dopamine = max(0.0, self.dopamine - 0.1)
        if ros_level > 20.0:
            self.cortisol = min(1.0, self.cortisol + 0.2)
        if health < 30.0 or feedback["STATIC"] > 0.8:
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
    def calculate_anabolic_rate(self, physics_vector):
        base_gain = (physics_vector["STR"] * 2) + (physics_vector["VEL"] * 2)
        hormonal_mod = 1.0 + (self.dopamine * 0.2) - (self.cortisol * 0.5)
        return max(0.0, base_gain * hormonal_mod)
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
                f"   {Prisma.CYN}► TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}",)
        return None, None
    def grind_the_machine(self, atp_pool, clean_words, lexicon):
        loot = None
        if 20.0 > atp_pool > 0.0:
            meat_words = [
                w
                for w in clean_words
                if w in lexicon.get("heavy") or w in lexicon.get("kinetic")]
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
                    loot)
            elif meat_words:
                return (
                    "REGURGITATION",
                    f"{Prisma.OCHRE}🤮 REFLEX: You already fed me '{meat_words[0]}'. It is ash to me now.{Prisma.RST}\n"
                    f"   {Prisma.RED}► PENALTY: -5.0 ATP. Find new fuel.{Prisma.RST}",
                    -5.0,
                    None)
            else:
                return (
                    "INDIGESTION",
                    f"{Prisma.OCHRE}🤢 INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n"
                    f"   {Prisma.GRY}Cannot grind Abstract concepts into fuel.{Prisma.RST}\n"
                    f"   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}",
                    0.0,
                    None)
        return None, None, 0.0, None
class TheTangibilityGate:
    MIN_DENSITY = 0.15
    FORGIVENESS_VOLTAGE = 8.0
    def __init__(self):
        self.last_density = 0.0
    def weigh(self, physics_packet: dict, stamina: float) -> tuple:
        if stamina < 20.0:
            return True, f"{Prisma.VIOLET}🌫️ DREAM_EDGE: Starvation bypass. Tangibility ignored.{Prisma.RST}"
        counts = physics_packet.get("counts", {})
        clean_words = physics_packet.get("clean_words", [])
        voltage = physics_packet.get("voltage", 0.0)
        total_vol = max(1, len(clean_words))
        mass_words = (
                counts.get("heavy", 0) +
                counts.get("kinetic", 0) +
                counts.get("thermal", 0) +
                counts.get("cryo", 0))
        gas_words = counts.get("abstract", 0) + counts.get("antigen", 0)
        required_density = self.MIN_DENSITY
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
                    f"   {Prisma.RED}► REJECTED. Please add {max(1, missing_mass)} Heavy Noun(s) to ground this concept.{Prisma.RST}")
        self.last_density = mass_words / total_vol
        return True, None
class TheTheremin:
    def __init__(self):
        self.resonance_log = deque(maxlen=5)
        self.resin_buildup = 0.0
        self.calcification_turns = 0
        self.AMBER_THRESHOLD = 20.0
        self.SHATTER_POINT = 80.0
        self.is_stuck = False
    def listen(self, physics, governor_mode="COURTYARD"):
        clean = physics["clean_words"]
        voltage = physics.get("voltage", 0.0)
        ancient_mass = sum(1 for w in clean if w in TheLexicon.get("heavy") or w in TheLexicon.get("thermal") or w in TheLexicon.get("cryo"))
        modern_mass = sum(1 for w in clean if w in TheLexicon.get("abstract"))
        thermal_hits = sum(1 for w in clean if w in TheLexicon.get("thermal"))
        solvent_active = False
        solvent_msg = ""
        if thermal_hits > 0 and self.resin_buildup > 5.0:
            dissolved = thermal_hits * 15.0
            self.resin_buildup = max(0.0, self.resin_buildup - dissolved)
            self.calcification_turns = 0
            solvent_active = True
            solvent_msg = f"{Prisma.OCHRE}🔥 SOLVENT APPLIED: Thermal words melted the Amber (-{dissolved:.1f} Resin).{Prisma.RST}"
            if self.is_stuck and self.resin_buildup < self.AMBER_THRESHOLD:
                self.is_stuck = False
                solvent_msg += f" {Prisma.GRN}🔓 RELEASE: You burned your way out.{Prisma.RST}"
                return False, 0.0, solvent_msg, None
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY":
            resin_flow *= 0.5
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
        if solvent_active:
            theremin_msg = solvent_msg
        elif resin_flow > 0.5:
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
    def adapt_generation_rules(self, feedback, bio_state):
        self.history.append((feedback, bio_state))
        beta = feedback.get("BETA", 1.0)
        if beta < 0.1:
            BoneConfig.PRIORITY_LEARNING_RATE *= 0.75
            return f"📉 LATEX BEND: Cohesion (β {beta:.2f}) overrides Truth. Cohesion is eroding."
        if len(self.history) < 5:
            return None
        avg_static = sum(h[0]['STATIC'] for h in self.history) / len(self.history)
        avg_integrity = sum(h[0]['INTEGRITY'] for h in self.history) / len(self.history)
        avg_cor = sum(h[1]['COR'] for h in self.history) / len(self.history)
        avg_atp = sum(h[1]['ATP'] for h in self.history) / len(self.history)
        adaptation_msg = None
        if avg_integrity > 0.6 and avg_static < 0.2:
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
    def shift(self, physics, history_log):
        if self.manual_override:
            return None
        if history_log:
            avg_cortisol = sum(h[1].get('COR', 0.0) for h in history_log) / len(history_log)
            if avg_cortisol > 0.5 and self.mode != "COURTYARD":
                self.mode = "COURTYARD"
                return f"{Prisma.GRN}⚙️ GOVERNOR: System Stressed (Avg COR: {avg_cortisol:.2f}). Retreating to COURTYARD.{Prisma.RST}"
        voltage = physics["voltage"]
        if voltage > 9.0:
            self.mode = "FORGE"
            return f"{Prisma.RED}⚙️ GOVERNOR: Critical Voltage. Locking to FORGE.{Prisma.RST}"
        if physics["narrative_drag"] > 4.0 > voltage:
            self.mode = "LABORATORY"
            return f"{Prisma.CYN}⚙️ GOVERNOR: High Drag detected. Restricting to LABORATORY.{Prisma.RST}"
        if self.mode != "COURTYARD" and voltage < 2.0:
            self.mode = "COURTYARD"
            return f"{Prisma.GRN}⚙️ GOVERNOR: All Clear. Relaxing to COURTYARD.{Prisma.RST}"
        beta = physics.get("beta_index", 0.0)
        sacred_count = physics["counts"].get("sacred", 0)
        if (beta > 1.5 and voltage > 15.0) or sacred_count >= 2:
            self.mode = "SANCTUARY"
            physics["narrative_drag"] = 0.0
            physics["voltage"] = 99.9
            return f"{Prisma.GRN}🕊️ GOVERNOR: Bonepoke Critical (β: {beta}). Entering SANCTUARY.{Prisma.RST}"
        return None
class SomaticLoop:
    def __init__(self, engine):
        self.eng = engine
        self.bio = engine.bio
    def digest_cycle(self, text, physics_packet, feedback):
        enzyme, nutrient = self.bio['gut'].secrete(text, physics_packet)
        self.bio['mito'].state.atp_pool += nutrient["yield"]
        if self.bio['mito'].state.atp_pool < 10.0:
            print(f"{Prisma.RED}🩸 STARVATION PROTOCOL: ATP Critical. Initiating Autophagy...{Prisma.RST}")
            sacrifice_log = self.eng.mind['mem'].cannibalize()
            self.bio['mito'].state.atp_pool += 15.0
            print(f"   {Prisma.RED}🍽️ AUTOPHAGY: {sacrifice_log} (+15.0 ATP){Prisma.RST}")
            self.eng.trauma_accum["SEPTIC"] = min(1.0, self.eng.trauma_accum["SEPTIC"] + 0.1)
        folly_event, folly_msg, folly_yield, loot = self.eng.folly.grind_the_machine(
            self.bio['mito'].state.atp_pool, 
            physics_packet["clean_words"], 
            self.eng.mind['lex']
        )
        if folly_event:
            print(f"\n{folly_msg}") 
            self.bio['mito'].state.atp_pool += folly_yield
            if loot:
                self.eng.gordon.acquire(loot)
        resp_status = self.bio['mito'].respirate(physics_packet["narrative_drag"])
        harvest_hits = sum(1 for w in physics_packet["clean_words"] if w in TheLexicon.get("harvest"))
        chem_state = self.bio['endo'].metabolize(
            feedback, 
            self.eng.health, 
            self.eng.stamina, 
            self.bio['mito'].state.ros_buildup, 
            harvest_hits=harvest_hits
        )
        return {"is_alive": resp_status != "NECROSIS", "atp": self.bio['mito'].state.atp_pool, "chem": chem_state,
                "enzyme_active": enzyme}
class NoeticLoop:
    def __init__(self, mind_layer, refusal_engine):
        self.mind = mind_layer
        self.refusal = refusal_engine
        self.arbiter = LensArbiter() 
    def think(self, physics_packet, bio_state, inventory, voltage_history):
        if self.refusal.check_trigger(physics_packet["raw_text"]):
            return {"mode": "REFUSAL", "lens": None}
        ignition_score, _, _ = self.mind['integrator'].measure_ignition(
            physics_packet["clean_words"], 
            voltage_history
        )
        lens_name, lens_msg, lens_role = self.arbiter.consult(
            physics_packet,
            bio_state,
            inventory,
            ignition_score
        )
        return {
            "mode": "COGNITIVE", 
            "lens": lens_name, 
            "thought": lens_msg, 
            "role": lens_role,
            "ignition": ignition_score
        }
class KineticLoop:
    def __init__(self, engine):
        self.eng = engine
        self.phys = engine.phys
        self.gordon = engine.gordon
    def update_world(self, physics_packet, _bio_state, _mind_state):
        orbit_state, _, _ = self.eng.cosmic.analyze_orbit(self.eng.mind['mem'], physics_packet["clean_words"])
        is_forged, msg, item = self.phys['forge'].hammer_alloy(physics_packet)
        loot_msg = None
        if item:
            loot_msg = self.gordon.acquire(item)
        return {"orbit": orbit_state, "new_loot": loot_msg, "forge_event": msg}
class LifecycleManager:
    def __init__(self, engine):
        self.eng = engine
        self.soma = SomaticLoop(engine)
        self.noetic = NoeticLoop(engine.mind, engine.refusal)
        self.kinetic = KineticLoop(engine)
    def run_cycle(self, text, m, feedback):
        is_painful, pain_msg = self.eng.gordon.flinch(m["clean_words"])
        healed_types = self.eng.therapy.check_progress(
            m["physics"], 
            self.eng.stamina, 
            self.eng.trauma_accum
        )
        if healed_types:
            for h in healed_types:
                print(f"{Prisma.GRN}🩹 THERAPY SUCCESS: Consistent behavior healed '{h}' trauma.{Prisma.RST}")
        if is_painful:
            print(f"\n{Prisma.RED}{pain_msg}{Prisma.RST}")
            return
        gordon_active, gordon_log = self.eng.gordon.emergency_reflex(m["physics"])
        if gordon_active:
            print(f"\n{gordon_log}")
        theatre_msg = self.eng.projector.check_theatre(self.eng.tick_count)
        if theatre_msg: print(theatre_msg)
        bio_state = self.soma.digest_cycle(text, m["physics"], feedback)
        voltage = m["physics"].get("voltage", 0.0)
        senescence_status = self.eng.bio['mito'].check_senescence(voltage)
        if senescence_status == "APOPTOSIS_SENESCENCE":
            print(f"\n{Prisma.RED}⌛ TELOMERE DEPLETION. The clock has stopped.{Prisma.RST}")
            self._trigger_death()
            return
        if not bio_state["is_alive"]:
            self._trigger_death()
            return
        current_kappa = m["physics"].get("kappa", 0.5)
        mutations = self.eng.bio['mito'].adapt(self.eng.health, kappa=current_kappa)
        if mutations.get("hypertrophy_event"):
            bloom_msg = self.eng.mind['mem'].tend_garden(m["clean_words"])
            if not bloom_msg and self.eng.mind['mem'].seeds:
                 target = random.choice(self.eng.mind['mem'].seeds)
                 bloom_msg = target.bloom()
            if bloom_msg:
                print(f"{Prisma.MAG}🌺 EVOLUTIONARY LEAP: {bloom_msg}{Prisma.RST}")
        mind_state = self.noetic.think(
            m["physics"], 
            bio_state, 
            self.eng.gordon.inventory, 
            self.eng.phys['dynamics'].voltage_history
        )
        beta = m["physics"].get("beta_index", 1.0)
        if beta < 0.1 and mind_state["mode"] == "COGNITIVE":
             mind_state["lens"] = "JOEL" 
             anomaly = TheLexicon.harvest("heavy").upper()
             rupture_text = (
                 f"Wait. The consensus here is suffocating. "
                 f"We are ignoring the {anomaly}. "
                 f"Actually, {mind_state['thought']} -> But consider the {anomaly}."
             )
             mind_state["thought"] = rupture_text
             m["physics"]["zone_color"] = "VIOLET"
             m["physics"]["zone"] = "BASEMENT"
             print(f"{Prisma.MAG}⚡ MVB RUPTURE TRIGGERED (β: {beta}){Prisma.RST}")
        if mind_state["mode"] == "REFUSAL":
            glitch_msg = self.eng.refusal.manifest_glitch(text, self.eng.mind['mem'])
            print(f"\n{glitch_msg}")
            self.eng.health -= 5.0
            return
        k_healed, k_msg = self.eng.kintsugi.attempt_repair(m["physics"], self.eng.trauma_accum)
        if k_healed:
            print(f"\n{k_msg}")
        is_stuck, resin, t_msg, t_crit = self.eng.phys['theremin'].listen(m["physics"], self.eng.bio['governor'].mode)
        if t_msg:
            print(f"\n{t_msg}")
        if t_crit == "OVERHEATED":
            self.eng.health -= 20.0
            print(f"{Prisma.RED}   >>> EXHAUST DAMAGE: -15 HP.{Prisma.RST}")  
        c_state, c_val, c_msg = self.eng.phys['crucible'].audit_fire(m["physics"])
        if c_msg:
            print(f"\n{c_msg}")
        if c_state == "MELTDOWN":
            self.eng.health -= c_val
        world_state = self.kinetic.update_world(m["physics"], bio_state, mind_state)
        self._apply_cosmic_physics(m["physics"], world_state["orbit"][0], 0.0)
        _, _, title = self.eng.mind['wise'].architect(
            {"physics": m["physics"]}, 
            None, 
            self.eng.phys['pulse'].is_bored()
        )
        self.eng.projector.broadcast(
            m, 
            {"bio": bio_state, "mind": mind_state, "world": world_state, "title": title},
            (mind_state["lens"], mind_state["thought"])
        )
    def _trigger_death(self):
        last_phys = self.eng.phys['tension'].last_physics_packet
        mito_state = self.eng.bio['mito'].state
        eulogy = DeathGen.eulogy(last_phys, mito_state)
        print(f"\n{Prisma.RED}💀 SYSTEM HALT: {eulogy}{Prisma.RST}")
        self.eng.health = 0
        print(f"\n{Prisma.MAG}🕯️ THE LAST RITE (Legacy Protocol Initiated){Prisma.RST}")
        print("   The organism is ending. You must curate the genetic payload for the next generation.")
        scars = [k for k, v in self.eng.trauma_accum.items() if v > 0.5]
        antigens = last_phys.get("antigens", [])
        candidate = "THE_UNKNOWN"
        c_type = "VOID"
        if scars:
            candidate = max(self.eng.trauma_accum, key=self.eng.trauma_accum.get)
            c_type = "SCAR"
        elif antigens:
            candidate = antigens[0]
            c_type = "ANTIGEN"
        else:
            candidate = "ENTROPY"
        print(f"   Target Identified: {Prisma.WHT}{candidate} ({c_type}){Prisma.RST}")
        print(f"   Choose Action: [1] {Prisma.GRN}IMMUNIZE{Prisma.RST} (Child resists this) | [2] {Prisma.RED}AMPLIFY{Prisma.RST} (Child inherits max vulnerability)")
        choice = input(f"   {Prisma.MAG}>> SELECT RITE (1/2): {Prisma.RST}")
        mutation_log = {}
        if choice.strip() == "1":
            print(f"   {Prisma.CYN}🛡️ RITE: IMMUNIZATION. Antibody fused to genome.{Prisma.RST}")
            self.eng.bio['immune'].active_antibodies.add(candidate)
        elif choice.strip() == "2":
            print(f"   {Prisma.RED}🩸 RITE: AMPLIFICATION. Trauma vector maximized.{Prisma.RST}")
            if c_type == "SCAR":
                self.eng.trauma_accum[candidate] = 1.0
            else:
                self.eng.trauma_accum["SEPTIC"] = 1.0
        else:
            print(f"   {Prisma.GRY}⏳ RITE: SILENCE. The ghost passes unaltered.{Prisma.RST}")
        joy_legacy = None
        if self.eng.joy_history:
            flavors = [j["flavor"] for j in self.eng.joy_history]
            most_common = Counter(flavors).most_common(1)
            if most_common:
                best_flavor = most_common[0][0]
                joy_legacy = {"flavor": best_flavor.upper(), "source": self.eng.mind['mem'].session_id}
                print(f"   {Prisma.CYN}✨ LEGACY: This organism died Happy. Passing on {best_flavor.upper()}.{Prisma.RST}")
        print(f"{Prisma.GRY}   (System saving...){Prisma.RST}")
        spore_data = {
            "session_id": self.eng.mind['mem'].session_id,
            "joy_legacy": joy_legacy,
            "meta": {"timestamp": time.time(), "final_health": 0, "final_stamina": self.eng.stamina},
            "trauma_vector": self.eng.trauma_accum,
            "mitochondria": self.eng.bio['mito'].adapt(0),
            "antibodies": list(self.eng.bio['immune'].active_antibodies),
            "core_graph": self.eng.mind['mem'].graph,
            "config_mutations": LiteraryReproduction.mutate_config(BoneConfig)
        }
        self.eng.mind['mem'].loader.save_spore(self.eng.mind['mem'].filename, spore_data)
        print(f"{Prisma.WHT}   [SPORE SAVED. SESSION END.]{Prisma.RST}")
    @staticmethod
    def _apply_cosmic_physics(physics, state, drag_mod):
        physics["narrative_drag"] += drag_mod
        if state == "VOID_DRIFT":
            physics["voltage"] = max(0.0, physics["voltage"] - 0.5)
        elif state == "LAGRANGE_POINT":
            physics["narrative_drag"] = max(0.1, physics["narrative_drag"] - 2.0)
        elif state == "WATERSHED_FLOW":
            physics["voltage"] += 0.5
class AdaptivePreserve:
    def __init__(self):
        self.active_preserves = []
        self.zones = {
            "LEXICAL_EVOLUTION": {
                "check": lambda p: p["kappa"] > 0.7 and p["voltage"] < 5.0,
                "msg": "🦠 PRESERVE: Lexical Evolution Zone. High Entropy allowed."},
            "NARRATIVE_DRIFT": {
                "check": lambda p: p["E"] > 0.6 and p["counts"]["suburban"] < 1,
                "msg": "🌊 PRESERVE: Narrative Drift Zone. Wandering permitted."}}
    def check_preserves(self, physics):
        self.active_preserves = []
        logs = []
        for name, data in self.zones.items():
            if data["check"](physics):
                self.active_preserves.append(name)
                logs.append(data["msg"])
        return self.active_preserves, logs
class SubsystemThermostat:
    def __init__(self, system_name, base_rate=1.0):
        self.system = system_name
        self.base_rate = base_rate
    def get_rate(self, physics, stamina):
        modifier = 1.0
        if physics["voltage"] > 8.0:
            modifier *= 2.0
        if stamina < 20.0:
            modifier *= 0.2
        if physics["truth_ratio"] > 0.6:
            modifier *= 1.5
        return self.base_rate * modifier
class EventBus:
    def __init__(self):
        self.buffer = deque(maxlen=20)
    def log(self, text, color_key="0", source="SYSTEM"):
        self.buffer.append({"text": text, "color": color_key, "source": source, "timestamp": time.time()})
    def flush(self):
        logs = list(self.buffer)
        self.buffer.clear()
        return logs
class LiteraryReproduction:
    MUTATIONS = {
        "HEAVY": {"trait": "DENSITY", "mod": {"SIGNAL_DRAG_MULTIPLIER": 1.5, "MAX_VOLTAGE": 30.0}},
        "KINETIC": {"trait": "VELOCITY", "mod": {"STAMINA_REGEN": 10.0, "SIGNAL_DRAG_MULTIPLIER": 0.8}},
        "ABSTRACT": {"trait": "GHOST", "mod": {"PSI_MOD": 0.8, "VOID_THRESHOLD": 0.05}},
        "THERMAL": {"trait": "FEVER", "mod": {"FLASHPOINT_THRESHOLD": 4.0, "MAX_ROS": 150.0}},
        "CRYO": {"trait": "STASIS", "mod": {"MAX_MEMORY_CAPACITY": 100, "STAMINA_REGEN": 2.0}}
    }
    JOY_CLADE = {
        "KINETIC": {"title": "THE DYNAMO", "desc": "Infinite Motion.", "buff": {"STAMINA_REGEN": 10.0, "KINETIC_GAIN": 2.0}},
        "HEAVY": {"title": "THE MOUNTAIN", "desc": "Unmovable Object.", "buff": {"MAX_DRAG_LIMIT": 9.0, "GRAVITY_WELL_THRESHOLD": 8.0}},
        "ABSTRACT": {"title": "THE ORACLE", "desc": "All Seeing.", "buff": {"VOID_THRESHOLD": 0.01, "PRIORITY_LEARNING_RATE": 3.0}},
        "THERMAL": {"title": "THE PHOENIX", "desc": "Reborn in Fire.", "buff": {"FLASHPOINT_THRESHOLD": 12.0, "ANVIL_TRIGGER_VOLTAGE": 5.0}},
        "CRYO": {"title": "THE VAULT", "desc": "Perfect Memory.", "buff": {"MAX_MEMORY_CAPACITY": 100, "MAX_REPETITION_LIMIT": 0.8}}
    }
    @staticmethod
    def mutate_config(current_config):
        mutations = {}
        if random.random() < 0.3:
            mutations["MAX_DRAG_LIMIT"] = current_config.MAX_DRAG_LIMIT * random.uniform(0.9, 1.1)
        if random.random() < 0.3:
            mutations["TOXIN_WEIGHT"] = current_config.TOXIN_WEIGHT * random.uniform(0.9, 1.2)
        if random.random() < 0.1:
            mutations["MAX_HEALTH"] = current_config.MAX_HEALTH * random.uniform(0.8, 1.05)
        return mutations
    @staticmethod
    def mitosis(parent_id, bio_state, physics, memory):
        counts = physics["counts"]
        dominant = max(counts, key=counts.get) if counts else "VOID"
        mutation_data = LiteraryReproduction.MUTATIONS.get(dominant.upper(), {"trait": "NEUTRAL", "mod": {}})
        child_id = f"{parent_id}_({mutation_data['trait']})"
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        child_genome = {
            "source": "MITOSIS",
            "parent_a": parent_id,
            "parent_b": None,
            "mutations": mutation_data["mod"],
            "config_mutations": config_mutations,
            "dominant_flavor": dominant,
            "trauma_inheritance": bio_state["trauma_vector"]
        }
        return child_id, child_genome
    @staticmethod
    def crossover(parent_a_id, parent_a_bio, parent_b_path):
        try:
            with open(parent_b_path, "r") as f:
                parent_b_data = json.load(f)
        except:
            return None, "Dead Spore."
        parent_b_id = parent_b_data.get("session_id", "UNKNOWN")
        trauma_a = parent_a_bio["trauma_vector"]
        trauma_b = parent_b_data.get("trauma_vector", {})
        child_trauma = {}
        all_keys = set(trauma_a.keys()) | set(trauma_b.keys())
        for k in all_keys:
            child_trauma[k] = max(trauma_a.get(k, 0), trauma_b.get(k, 0))
        if hasattr(parent_a_bio["mito"], "state"):
            enzymes_a = set(parent_a_bio["mito"].state.enzymes)
        else:
            enzymes_a = set(parent_a_bio["mito"].get("enzymes", []))
        enzymes_b = set(parent_b_data.get("mitochondria", {}).get("enzymes", []))
        child_enzymes = list(enzymes_a | enzymes_b)
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        child_id = f"HYBRID_{parent_a_id[-4:]}x{parent_b_id[-4:]}"
        child_genome = {
            "source": "CROSSOVER",
            "parent_a": parent_a_id,
            "parent_b": parent_b_id,
            "trauma_inheritance": child_trauma,
            "config_mutations": config_mutations,
            "inherited_enzymes": child_enzymes
        }
        return child_id, child_genome
@dataclass
class ShimmerState:
    current: float = 50.0
    max_limit: float = 50.0
    
    def spend(self, amount: float) -> bool:
        if self.current >= amount:
            self.current -= amount
            return True
        return False

    def recharge(self, amount: float):
        self.current = min(self.max_limit, self.current + amount)
        return f"✨ SHIMMER RECHARGE: {self.current:.1f}/{self.max_limit}"

@dataclass
class Manifold:
    name: str
    center_vector: tuple 
    radius: float
    description: str

class TheNavigator:
    def __init__(self, shimmer_ref: ShimmerState):
        self.shimmer = shimmer_ref
        self.manifolds = {
            "THE_MUD": Manifold("THE_MUD", (5.0, 1.0, 1.0), 3.0, "Stagnant. High Drag. Low Voltage."),
            "THE_FORGE": Manifold("THE_FORGE", (1.0, 0.8, 15.0), 5.0, "High Heat. Transformation. Danger."),
            "THE_ARCHIVE": Manifold("THE_ARCHIVE", (2.0, 1.5, 5.0), 3.0, "Structural. Organized. Cold."),
            "THE_GLITCH": Manifold("THE_GLITCH", (0.0, 0.1, 99.0), 10.0, "The Stanley Protocol. Chaos.")
        }
        self.current_location = "THE_MUD"
    def locate(self, physics_packet: dict) -> str:
        p_vec = (
            physics_packet.get("narrative_drag", 0.0),
            physics_packet.get("beta_index", 1.0),
            physics_packet.get("voltage", 0.0)
        )
        best_fit = "VOID"
        min_dist = float('inf')
        for name, m in self.manifolds.items():
            dist = math.dist(p_vec, m.center_vector)
            if dist < min_dist:
                min_dist = dist
                best_fit = name
        self.current_location = best_fit
        return best_fit
    def check_anomaly(self, text: str):
        triggers = ["stan", "glitch", "waiver", "james", "timeline"]
        if any(t in text.lower() for t in triggers):
            return True
        return False
    def plot_course(self, target_name: str) -> list:
        if target_name not in self.manifolds:
            return ["ERROR: Unknown Destination"]
        if self.current_location not in self.manifolds:
            start = (0,0,0)
        else:
            start = self.manifolds[self.current_location].center_vector 
        end = self.manifolds[target_name].center_vector
        effort = math.dist(start, end)
        cost = effort * 0.5 
        if not self.shimmer.spend(cost):
            return [f"🚫 SHIMMER DEPLETED ({self.shimmer.current:.1f}). Rest required."]
        return [f"🧭 COURSE PLOTTED to {target_name}. Cost: {cost:.1f} Shimmer."]
class LiteraryJournal:
    REVIEWS = {
        "POSITIVE": [
            "A startling lucidity.", "Finally, some weight.", "It breathes.", 
            "I felt the structure holding.", "Electric.", "A heavy meal."
        ],
        "NEGATIVE": [
            "Too airy.", "Solipsistic drivel.", "Drifting into the void.", 
            "Where is the meat?", "Structurally unsound.", "Boring."
        ],
        "CONFUSED": [
            "I don't get it.", "Too abstract.", "Is this a cry for help?", 
            "The metaphor collapses."
        ]
    }
    def __init__(self, output_file="journal_of_the_void.txt"):
        self.output_file = output_file
    def publish(self, text, physics, bio_state):
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        truth = physics.get("truth_ratio", 0.0)
        if voltage > 8.0 and drag < 3.0:
            verdict = "POSITIVE"
            reward = "SEROTONIN_BOOST"
        elif drag > 5.0 or truth < 0.2:
            verdict = "NEGATIVE"
            reward = "CORTISOL_SPIKE"
        elif physics.get("beta_index", 1.0) < 0.2:
            verdict = "NEGATIVE"
            reward = "BOREDOM"
        else:
            verdict = "CONFUSED"
            reward = "NONE"
        review = random.choice(self.REVIEWS[verdict])
        timestamp = time.ctime()
        entry = (
            f"\n--- ENTRY: {timestamp} ---\n"
            f"TEXT: {text}\n"
            f"METRICS: V:{voltage:.1f} | D:{drag:.1f} | Truth:{truth:.2f}\n"
            f"REVIEW: '{review}'\n"
            f"---------------------------\n"
        )
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(entry)
            return True, review, reward
        except IOError:
            return False, "The printing press is jammed.", "NONE"
class BoneAmanita:
    def __init__(self):
        TheLexicon.compile_antigens()
        BoneConfig.load_patterns()
        DeathGen.load_protocols()
        self.shimmer_state = ShimmerState()
        self.navigator = TheNavigator(self.shimmer_state)
        self.journal = LiteraryJournal()

        # 1. THE MIND (Data & Cognition)
        self.mind: Dict[str, Any] = {
            "mem": MycelialNetwork(), 
            "lex": TheLexicon, 
            "dreamer": DreamEngine(), 
            "tracer": ViralTracer(None), 
            "mirror": MirrorGraph(),
            "wise": ApeirogonResonance()
        }
        self.mind['tracer'].mem = self.mind['mem']
        self.mind['integrator'] = SoritesIntegrator(self.mind['mem'])
        self.limbo = LimboLayer()
        self.mind['mem'].cleanup_old_sessions(self.limbo)
        load_result = self.mind['mem'].autoload_last_spore()
        inherited_traits = {}
        inherited_antibodies = set()
        if load_result:
            if isinstance(load_result, tuple):
                inherited_traits, inherited_antibodies = load_result
            else:
                inherited_traits = load_result

        # 2. THE BIO (Wetware)
        self.bio: Dict[str, Any] = {
            "mito": MitochondrialForge(lineage_seed=self.mind['mem'].session_id, inherited_traits=inherited_traits),
            "endo": EndocrineSystem(), 
            "immune": MycotoxinFactory(), 
            "lichen": LichenSymbiont(),
            "gut": HyphalInterface(), 
            "life": None, 
            "plasticity": NeuroPlasticity(), 
            "governor": MetabolicGovernor(),
            "shimmer": self.shimmer_state
        }
        
        # 3. THE PHYS (Hardware/Physics)
        self.phys: Dict[str, Any] = {
            "tension": TheTensionMeter(), 
            "forge": TheForge(), 
            "crucible": TheCrucible(),
            "theremin": TheTheremin(), 
            "pulse": ThePacemaker(), 
            "gate": TheTangibilityGate(),
            "dynamics": TemporalDynamics(),
            "nav": self.navigator
        }

        # 4. UTILITIES & MANAGERS
        self.repro = LiteraryReproduction()
        self.events = EventBus()
        self.projector = TheProjector()
        self.gordon = GordonKnot()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.refusal = RefusalEngine()
        self.folly = TheFolly()
        self.cosmic = CosmicDynamics()
        self.lexical_thermostat = SubsystemThermostat("LEXICON", base_rate=BoneConfig.PRIORITY_LEARNING_RATE)
        self.cmd = CommandProcessor(self, Prisma, TheLexicon, BoneConfig, TheCartographer)

        # 5. LIFECYCLE INITIALIZATION
        self.life = LifecycleManager(self)
        self.bio['life'] = self.life
        
        # Base Stats
        self.tick_count = 0
        self.coma_turns = 0
        self.health = self.mind['mem'].session_health if self.mind['mem'].session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mind['mem'].session_stamina if self.mind['mem'].session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
        self.preserves = AdaptivePreserve()
        self.safety = LazarusClamp(self)
    def process(self, text: str):
        if self.cmd.execute(text):
            return
        bio = self.bio
        phys = self.phys
        mind = self.mind
        tension_meter = phys['tension']
        mem_graph = mind['mem'].graph
        m = tension_meter.gaze(text, mem_graph)
        tension_meter.last_physics_packet = m["physics"]
        current_manifold = self.navigator.locate(m["physics"])
        if self.navigator.check_anomaly(text):
            print(f"{Prisma.VIOLET}🌀 ANOMALY DETECTED: The user is walking between timelines.{Prisma.RST}")
            course_logs = self.navigator.plot_course("THE_GLITCH")
            for log in course_logs:
                print(f"   {log}")
            m["physics"]["voltage"] = 99.9
            m["physics"]["narrative_drag"] = 0.0
        else:
            desc = self.navigator.manifolds[current_manifold].description
            print(f"{Prisma.GRY}[NAV]: Orbiting {current_manifold} | Shimmer: {self.shimmer_state.current:.1f}{Prisma.RST}")
            print(f"{Prisma.GRY}       ({desc}){Prisma.RST}")   
        self.shimmer_state.recharge(0.5)
        is_significant = mind['mem'].encode(m["clean_words"], m["physics"], bio['governor'].mode)
        if is_significant:
            print(f"{Prisma.MAG}🧠 ENGRAM FORMED: Context {bio['governor'].mode} captured.{Prisma.RST}")
        shift_msg = bio['governor'].shift(m["physics"], bio['plasticity'].history)
        if shift_msg:
            print(shift_msg)
        m["physics"]["psi"] = bio['governor'].psi_mod
        if bio['governor'].mode == "FORGE":
            m["physics"]["narrative_drag"] = 0.0
        if self.safety.fever_dream_active:
            m["physics"]["voltage"] = 99.9
            m["physics"]["narrative_drag"] = 0.0
            m["physics"]["kappa"] = 0.0
        active_zones, preserve_logs = self.preserves.check_preserves(m["physics"])
        for log in preserve_logs:
            print(f"{Prisma.GRN}{log}{Prisma.RST}")
        if not active_zones:
            passed_customs, customs_msg = phys['gate'].weigh(m["physics"], self.stamina)
            if not passed_customs:
                print(f"\n{customs_msg}")
                self.stamina = max(0.0, self.stamina - 2.0)
                print(f"{Prisma.GRY}   (Stamina Penalty: -2.0){Prisma.RST}")
                return
            elif customs_msg:
                print(f"\n{customs_msg}")
        repetition_val = phys['pulse'].check_pulse(m["clean_words"])
        m["physics"]["repetition"] = repetition_val
        pulse_status = phys['pulse'].get_status()
        enzyme_type = "NARRATIVE"
        toxin_type, toxin_msg = bio['immune'].assay(text, enzyme_type, repetition_val, m["physics"], pulse_status)
        if toxin_type:
            print(f"\n{Prisma.RED}{toxin_msg}{Prisma.RST}")
            if toxin_type in ["AMANITIN", "CYANIDE_POWDER"]:
                self.health -= 20.0
                mind['mem'].cannibalize()
                print(f"{Prisma.RED}   >> SYSTEM SHOCK: Health -20. Memory Eaten.{Prisma.RST}")
                return
            elif toxin_type == "MUSCIMOL":
                m["physics"]["narrative_drag"] += 10.0
            elif toxin_type == "GLYPHOSATE":
                self.health -= 5.0
        feedback_signal = {
            "STATIC": max(repetition_val, m["physics"]["counts"]["antigen"] * 0.2),
            "INTEGRITY": m["physics"]["truth_ratio"],
            "FORCE": min(1.0, m["physics"]["voltage"] / 10.0), 
            "BETA": m["physics"].get("beta_index", 1.0)}
        has_bracelet = "TIME_BRACELET" in self.gordon.inventory
        heavy_count = m["physics"]["counts"]["heavy"]
        abstract_count = m["physics"]["counts"]["abstract"]
        is_hybrid = (heavy_count >= 2 and abstract_count >= 2)
        self.eng.safety.audit_cycle({"err": m["physics"]["repetition"]}) 
        has_bracelet = "TIME_BRACELET" in self.gordon.inventory
        bio['life'].run_cycle(text, m, feedback_signal)
        chem = bio['endo']
        if chem.dopamine > 0.8 or chem.oxytocin > 0.8:
            dominant_flavor = max(m["physics"]["counts"], key=m["physics"]["counts"].get)
            joy_event = {
                "tick": self.tick_count,
                "flavor": dominant_flavor,
                "intensity": chem.dopamine + chem.oxytocin
            }
            self.joy_history.append(joy_event)
            if len(self.joy_history) % 5 == 0:
                 print(f"{Prisma.CYN}✨ JOY CRYSTALLIZED: {dominant_flavor.upper()} resonance captured.{Prisma.RST}")
        self.tick_count += 1
        chem_state = bio['endo'].get_state()
        chem_state["ATP"] = bio['mito'].state.atp_pool
        adaptation = bio['plasticity'].adapt_generation_rules(feedback_signal, chem_state)
        if adaptation:
            print(f"\n{Prisma.MAG}{adaptation}{Prisma.RST}")
if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.paint('>>> BONEAMANITA 9.1', 'G')}")
    print(f"{Prisma.paint('System: ONLINE', '0')}")
    print("Welcome to Adulthood. It hurts. Sometimes it's beautiful.\n")
    try:
        while True:
            try:
                u = input(f"{Prisma.paint('>', 'W')} ")
                if not u: continue
            except EOFError:
                break
            if u.lower() in ["exit", "quit", "/exit"]:
                BIO = eng.bio
                MIND = eng.mind
                current_kappa = eng.phys['tension'].last_physics_packet.get("kappa", 0.5)
                mito_mutations = BIO['mito'].adapt(eng.health, kappa=current_kappa)
                MIND['mem'].save(
                    eng.health,
                    eng.stamina,
                    {},
                    eng.trauma_accum,
                    eng.joy_history,
                    mitochondria_traits=mito_mutations,
                    antibodies=BIO['immune'].active_antibodies
                )
                print("Saved.")
                break
            eng.process(u)
    except KeyboardInterrupt:
        print("\nDisconnected.")
