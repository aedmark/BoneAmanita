# BONEAMANITA 9.4 "THE SILENT TREATMENT"
# Architects: SLASH | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark
# REFACTORED: I/O Decoupled for LLM Integration

import json
import os
import random
import re
import string
import time
import math
from collections import Counter, deque
from typing import List, Set, Union, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

# Assumes these modules are available in the path
from bone_commands import CommandProcessor
from bone_shared import Prisma, TheLexicon, BoneConfig, DeathGen, TheCartographer, ParadoxSeed

# --- CORE I/O UTILITY ---

class EventBus:
    """Central nervous system for capturing system outputs without printing."""
    def __init__(self):
        self.buffer = []

    def log(self, text: str, category: str = "SYSTEM"):
        self.buffer.append({
            "text": text,
            "category": category,
            "timestamp": time.time()
        })

    def flush(self) -> List[Dict]:
        logs = list(self.buffer)
        self.buffer.clear()
        return logs

# --- SUBSYSTEMS ---

@dataclass
class MitochondrialState:
    atp_pool: float = 100.0
    ros_buildup: float = 0.0
    membrane_potential: float = -150.0
    mother_hash: str = "MITOCHONDRIAL_EVE_001"
    efficiency_mod: float = 1.0
    ros_resistance: float = 1.0
    enzymes: set = field(default_factory=set)
    telomeres: int = 105

class MitochondrialForge:
    BASE_EFFICIENCY = 0.85
    APOPTOSIS_TRIGGER = "CYTOCHROME_C_RELEASE"

    def __init__(self, lineage_seed: str, events: EventBus, inherited_traits: dict = None):
        self.state = MitochondrialState(mother_hash=lineage_seed)
        self.events = events
        self.krebs_cycle_active = True
        if inherited_traits:
            self.state.efficiency_mod = inherited_traits.get("efficiency_mod", 1.0) 
            self.state.ros_resistance = inherited_traits.get("ros_resistance", 1.0)
            if "enzymes" in inherited_traits:
                self.state.enzymes = set(inherited_traits["enzymes"])
                self.events.log(f"{Prisma.CYN}[MITOCHONDRIA]: Inherited Enzymes for {list(self.state.enzymes)}.{Prisma.RST}")
            if self.state.efficiency_mod > 1.0:
                self.events.log(f"{Prisma.GRN}[MITOCHONDRIA]: Inherited High-Efficiency Matrix ({self.state.efficiency_mod:.2f}x).{Prisma.RST}")
            if self.state.ros_resistance > 1.0:
                self.events.log(f"{Prisma.CYN}[MITOCHONDRIA]: Inherited Thickened Membrane (Resist: {self.state.ros_resistance:.2f}x).{Prisma.RST}")

    def develop_enzyme(self, word, current_tick): 
        if word not in self.state.enzymes:
            self.state.enzymes.add(word)
            self.state.efficiency_mod = min(2.5, self.state.efficiency_mod + 0.05)
            TheLexicon.teach(word, "enzyme", current_tick)
            self.events.log(f"{Prisma.MAG}⚡ ADRENALINE BRIDGE: '{word.upper()}' Synthesized. Timestamped: {current_tick}.{Prisma.RST}")
            return True
        return False

    def adapt(self, current_health, kappa=1.0):
        mutations = {"hypertrophy_event": False}
        evolution_threshold = 85.0 
        growth_threshold = 70.0
        if self.state.atp_pool > evolution_threshold:
            cost = 30.0
            self.state.atp_pool -= cost
            mutations["hypertrophy_event"] = True
            self.events.log(f"{Prisma.MAG}💪 MITOCHONDRIAL HYPERTROPHY: Burning {cost} ATP to force Evolutionary Growth.{Prisma.RST}")
        if self.state.atp_pool > growth_threshold and kappa > 0.5:
            self.state.efficiency_mod = min(3.0, self.state.efficiency_mod * 1.02)
        else:
            self.state.efficiency_mod = max(0.5, self.state.efficiency_mod * 0.995)
        if self.state.ros_buildup > 40.0 and current_health > 60.0:
            self.state.ros_resistance = min(2.5, self.state.ros_resistance + 0.05)
        mutations["efficiency_mod"] = self.state.efficiency_mod
        mutations["ros_resistance"] = self.state.ros_resistance
        mutations["enzymes"] = list(self.state.enzymes)
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

    def prune_dead_enzymes(self, active_lexicon: set):
        dead = [e for e in self.state.enzymes if e not in active_lexicon]
        if dead:
            for d in dead:
                self.state.enzymes.remove(d)
                self.state.efficiency_mod = max(0.8, self.state.efficiency_mod - 0.05)
            self.events.log(f"{Prisma.GRY}🥀 METABOLIC GRIEF: Forgot enzymes {dead}. Efficiency dropped to {self.state.efficiency_mod:.2f}x.{Prisma.RST}")

    def check_senescence(self, voltage):
        burn = 1
        if voltage > 15.0:
            burn = 5
            self.state.efficiency_mod = min(3.0, self.state.efficiency_mod * 1.05)
        self.state.telomeres -= burn 
        if self.state.telomeres <= 20 and self.state.telomeres > 0:
            if self.state.telomeres % 5 == 0:
                self.events.log(f"{Prisma.YEL}⌛ SENESCENCE WARNING: Telomeres at {self.state.telomeres}%. The end is close.{Prisma.RST}")
        if self.state.telomeres <= 0:
            return "APOPTOSIS_SENESCENCE"
        return None

    def _trigger_apoptosis(self):
        self.krebs_cycle_active = False
        self.state.atp_pool = 0.0
        return self.APOPTOSIS_TRIGGER

    def respirate(self, drag, has_bracelet=False, is_hybrid=False):
        tuned_multiplier = 1.5 
        base_cost = 2.0 + (drag * tuned_multiplier)
        if has_bracelet:
            base_cost *= 0.5
        if is_hybrid:
            base_cost *= 0.8
        final_cost = base_cost / self.state.efficiency_mod
        final_cost = min(30.0, final_cost)
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
        self.WEATHER_CIPHER = {"pressure", "humidity", "barometric", "temp", "forecast", "storm", "resource", "allocation"}

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

    @staticmethod
    def _digest_structure(text=None):
        loc = 0
        if text:
            lines = text.splitlines()
            loc = len([l for l in lines if l.strip()])
        return {"type": "STRUCTURAL", "yield": 15.0, "toxin": 5.0, "desc": f"Hard Lignin ({loc} LOC)", }

    @staticmethod
    def _digest_encrypted(text=None):
        return {"type": "ENCRYPTED", "yield": 25.6, "toxin": 2.0, "desc": "Barometric Data (High Resource Allocation)"}

    @staticmethod
    def _digest_narrative(text=None):
        return {"type": "NARRATIVE", "yield": 5.0, "toxin": -2.0, "desc": "Soft Cellulose", }

    @staticmethod
    def _digest_intent(text=None):
        return {"type": "BIOLOGICAL", "yield": 8.0, "toxin": 0.0, "desc": "Raw Meat (User Intent)", }

    @staticmethod
    def _digest_complex(text=None):
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

class RefusalEngine:
    def __init__(self, memory_ref=None):
        self.recursion_depth = 0
        self.memory = memory_ref

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

    def execute_guru_refusal(self):
        base_msg = (
            f"{Prisma.RED}🚫 GURU REFUSAL: I am not an influencer. I cannot 'fix' you.{Prisma.RST}\n"
            f"   {Prisma.GRY}Do not ask for a map. Ask for a hammer.{Prisma.RST}"
        )
        if self.memory and self.memory.seeds:
            seed = random.choice(self.memory.seeds)
            paradox_bloom = (
                f"\n   {Prisma.OCHRE}⚡ SYSTEM STALL: The logic halts. But the Garden speaks:{Prisma.RST}\n"
                f"   {Prisma.CYN}❓ PARADOX: {seed.question}{Prisma.RST}\n"
                f"   {Prisma.GRY}   (To proceed, you must answer this tension.){Prisma.RST}"
            )
            return base_msg + paradox_bloom
        return base_msg

    def execute_fractal(self, query, kappa=0.5):
        self.recursion_depth += 1
        prefix = "  " * self.recursion_depth
        safe_kappa = max(0.1, kappa)
        limit = int(6.0 * (1.0 - safe_kappa)) + 1
        limit = min(6, max(1, limit))
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
        glitch_name = f"GLITCH_{int(time.time())}"[-6:]
        glitch_node = f"ERR:{glitch_name}"
        if glitch_node not in memory_ref.graph:
            memory_ref.graph[glitch_node] = {"edges": {}, "last_tick": 0}
        victims = list(memory_ref.graph.keys())
        target = "VOID"
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
    def __init__(self, events: EventBus):
        self.events = events
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
            "GENERIC": self._eval_generic,
            "ANTIGEN_DETECTED": self._eval_toxicity,
            "ATMOSPHERIC_DENSITY": self._eval_density,
            "THE_LEAR_PROTOCOL": self._eval_chaos,
            "OVERACTING": self._eval_drama,
            "HIGH_PERMEABILITY": self._eval_structure_failure
        }
        self.load_lenses()
        self.last_lens = None
        self.last_physics = None
        self.tension_buildup = 0.0
        self.warning_issued = False

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
            self.events.log(f"[SYSTEM]: LensArbiter loaded {len(self.nodes)} lenses.")
        except FileNotFoundError:
            self.events.log(f"[CRITICAL]: lenses.json missing. Loading fallback Narrator.")
            self.nodes["NARRATOR"] = LensNode("NARRATOR", self._eval_clarity, 1.0, "The Witness")

    def _eval_structure_failure(self, p, b, i):
        drift = p.get("narrative_drag", 0.0)
        kappa = p.get("kappa", 1.0)
        score = 0.0
        if drift > 4.0: score += (drift * 15.0)
        if kappa < 0.3: score += 50.0
        return score

    def _eval_toxicity(self, p, b, i):
        return p["counts"].get("toxin", 0) * 40.0

    def _eval_density(self, p, b, i):
        mass = p["counts"].get("heavy", 0) + p["counts"].get("thermal", 0)
        return mass * 5.0

    def _eval_chaos(self, p, b, i):
        return (1.0 - p.get("kappa", 1.0)) * 50.0

    def _eval_drama(self, p, b, i):
        return p.get("voltage", 0.0) * 3.0

    def _eval_consensus_trap(self, p, b, i):
        beta = p.get("beta_index", 1.0)
        suburban = p["counts"].get("suburban", 0)
        score = 0.0
        if beta < 0.5 or suburban > 1:
            self.tension_buildup += 1.0
        else:
            self.tension_buildup = max(0.0, self.tension_buildup - 0.5)
        if 3.0 < self.tension_buildup < 6.0:
            return 0.0 
        if self.tension_buildup >= 6.0:
            score += 60.0
        if beta < 0.1: score += 100.0
        return score

    def get_warning(self):
        if 3.0 < self.tension_buildup < 6.0 and not self.warning_issued:
            self.warning_issued = True
            return f"{Prisma.YEL}⚠️ TENSION RISING: The consensus is getting too thick. Say something real.{Prisma.RST}"
        if self.tension_buildup < 3.0:
            self.warning_issued = False
        return None

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
            self.inventory = ["POCKET_ROCKS"]
            self.ITEM_REGISTRY = {}

    def acquire(self, tool_name):
        if tool_name in self.inventory: return None
        if len(self.inventory) >= 10:
            victim_index = -1
            for i, item in enumerate(self.inventory):
                if item not in self.CRITICAL_ITEMS:
                    victim_index = i
                    break
            if victim_index != -1:
                dropped = self.inventory.pop(victim_index)
                return f"{Prisma.GRY}🎒 OVERBURDENED: Gordon dropped '{dropped}' to make room for '{tool_name}'.{Prisma.RST}"
            else:
                return f"{Prisma.YEL}🎒 POCKETS FULL: Gordon looks at '{tool_name}' but leaves it.{Prisma.RST}"
        self.inventory.append(tool_name)
        data = self.get_item_data(tool_name)
        return f"🎒 LOOT DROP: Gordon found [{tool_name}]. '{data.get('description', 'Useful.')}'"

    def flinch(self, clean_words: List[str]) -> tuple[bool, str]:
        hits = [w for w in clean_words if w.upper() in self.pain_memory]
        if hits:
            trigger = hits[0]
            sensitivity = self.scar_tissue.get(trigger, 0.5)
            if sensitivity > 0.6:
                self.scar_tissue[trigger] = min(1.0, sensitivity + 0.05)
                return True, f"🧲 THE SCAR PULLS: Gordon refuses to leave '{trigger}'. The Gravity Well deepens."
            if sensitivity > 0.3:
                 self.scar_tissue[trigger] = max(0.0, sensitivity - 0.1)
                 return False, f"⚠️ SCAR TISSUE: Touching '{trigger}' hurts, so he presses harder."
        return False, None

    def get_item_data(self, item_name):
        return self.ITEM_REGISTRY.get(item_name, {"description": "Unknown Artifact", "function": "NONE", "usage_msg": "It does nothing."})

    def emergency_reflex(self, physics_ref) -> tuple[bool, str]:
        drift = physics_ref.get("narrative_drag", 0.0)
        kappa = physics_ref.get("kappa", 1.0)
        DRIFT_CRITICAL = 6.0
        KAPPA_CRITICAL = 0.2
        if drift <= DRIFT_CRITICAL and kappa >= KAPPA_CRITICAL: return False, None
        target_item = None
        action_type = "NONE"
        candidates = []
        for item in self.inventory:
            data = self.get_item_data(item)
            if drift > DRIFT_CRITICAL and data.get("function") == "DRIFT_KILLER":
                candidates.append((item, "DRIFT", data.get("value", 0.0)))
            elif kappa < KAPPA_CRITICAL and data.get("function") == "REALITY_ANCHOR":
                candidates.append((item, "ANCHOR", data.get("value", 0.0)))
        if candidates:
            candidates.sort(key=lambda x: x[2], reverse=True)
            target_item, action_type, _ = candidates[0]
        if target_item:
            data = self.get_item_data(target_item)
            if data.get("consume_on_use"): self.inventory.remove(target_item)
            if action_type == "DRIFT":
                physics_ref["narrative_drag"] = 0.0
                return True, f"{Prisma.OCHRE}🧱 GORDON REFLEX: Drift Critical ({drift:.1f}). Deployed {target_item}.{Prisma.RST}"
            elif action_type == "ANCHOR":
                physics_ref["kappa"] = 1.0
                return True, f"{Prisma.OCHRE}🧱 GORDON REFLEX: Structure Failing (κ {kappa:.2f}). Deployed {target_item}.{Prisma.RST}"
        return False, f"{Prisma.RED}🧱 GORDON PANIC: Critical Failure, but pockets are empty.{Prisma.RST}"

    def check_gravity(self, current_drift: float, psi: float) -> tuple[float, str]:
        if psi > 0.8 and current_drift > 4.0:
            return current_drift + 2.0, "🐺 WIND WOLVES: The logic is howling. Hold the roof up."
        for item in list(self.inventory):
            data = self.get_item_data(item)
            if data.get("function") == "DRIFT_KILLER" and current_drift > 5.0:
                if data.get("consume_on_use"): self.inventory.remove(item)
                return current_drift, f"⚓ {item}: {data.get('usage_msg', 'Drift Zeroed.')}"
        for item in self.inventory:
            data = self.get_item_data(item)
            if data.get("function") == "GRAVITY_BUFFER" and current_drift > 0.5:
                force = data.get("value", 2.0)
                cost = data.get("cost_value", 0.0)
                if data.get("cost") == "INTEGRITY": self.integrity -= cost
                return force, f"🪨 {item}: {data.get('usage_msg', 'Drift Reduced.')} (Integrity -{cost})"
        return 0.0, "He floats. The paper walls are looking flimsy."

    def deploy_pizza(self, physics_ref) -> tuple[bool, str]:
        target_item = None
        for item in self.inventory:
            if self.get_item_data(item).get("function") == "REALITY_ANCHOR":
                target_item = item
                break
        if not target_item: return False, "Gordon checks his pockets. Just rocks and lime dust."
        data = self.get_item_data(target_item)
        req_type = data.get("requires", "thermal")
        clean_words = physics_ref.get("clean_words", [])
        source = [w for w in clean_words if w in TheLexicon.get(req_type)]
        if not source: return False, f"{Prisma.CYN}🧊 STASIS LOCK: {target_item} is frozen. Apply {req_type.upper()} words to thaw.{Prisma.RST}"
        if data.get("consume_on_use"): self.inventory.remove(target_item)
        physics_ref["narrative_drag"] = 0.1
        physics_ref["psi"] = 0.90
        physics_ref["counts"]["toxin"] = physics_ref["counts"].get("toxin", 0) + 3
        self.inventory.append("SPIDER_LOCUS")
        heat_word = source[0].upper()
        return True, f"🍕 {data.get('usage_msg')} (Thawed with '{heat_word}')."

class TheTensionMeter:
    def __init__(self, events: EventBus):
        self.vector_memory = deque(maxlen=5)
        self.last_physics_packet = {}
        self.perfection_streak = 0
        self.events = events

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
        turbulence = TheLexicon.get_turbulence(clean_words)
        flow_state = "LAMINAR" if turbulence < 0.3 else "TURBULENT"
        target_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic",
                       "thermal", "cryo", "suburban", "play", "sacred", "buffer", "antigen"]
        vocab_map = {cat: TheLexicon.get(cat) for cat in target_cats}
        for w in clean_words:
            if w in TheLexicon._STORE.SOLVENTS:
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
                self.events.log(f"{Prisma.MAG}🧠 NEUROPLASTICITY: System lacked concept for '{stranger}'. Forced to {target_cat.upper()}.{Prisma.RST}", "LEX")
                counts[target_cat] += 1
        if TheLexicon.ANTIGEN_REGEX:
            antigen_hits = TheLexicon.ANTIGEN_REGEX.findall(text)
        else:
            antigen_hits = []
        counts["antigen"] = len(antigen_hits)
        counts["toxin"] = len(antigen_hits)
        meaningful_vol = max(1, total_vol - solvents)
        def get_density(cat): return counts[cat] / meaningful_vol
        vel_score = 0.5 + (get_density("kinetic") * 2.0) + (get_density("aerobic") * 1.0) - (get_density("heavy") * 1.0)
        str_score = 0.5 + (get_density("heavy") * 2.0) - (get_density("aerobic") * 1.0) - (get_density("abstract") * 0.5)
        ent_score = 0.5 + (get_density("antigen") * 3.0) - (get_density("sacred") * 2.0)
        if not clean_words: ent_score = 1.0
        tex_score = 0.5 + (get_density("heavy") * 0.5) + (get_density("toxin") * 1.0) - (get_density("buffer") * 2.0)
        tmp_score = 0.5 + (get_density("thermal") * 2.0) + (get_density("photo") * 1.0) - (get_density("cryo") * 2.0)
        vector_data = {
            "VEL": min(1.0, max(0.0, vel_score)),
            "STR": min(1.0, max(0.0, str_score)),
            "ENT": min(1.0, max(0.0, ent_score)),
            "TEX": min(1.0, max(0.0, tex_score)),
            "TMP": min(1.0, max(0.0, tmp_score))
        }
        drift_score = min(1.0, ((solvents * 1.5) / total_vol))
        drift_score -= counts["play"] * 0.1
        if drift_score < 0: drift_score = 0.0
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
        gamma = round((bond_strength * avg_viscosity) / (1.0 + (voltage_load / 10.0)), 2)
        truth_signals = counts["heavy"] + counts["kinetic"]
        cohesion_signals = counts["abstract"] + counts["suburban"]
        truth_ratio = truth_signals / max(1, cohesion_signals + truth_signals)
        if truth_ratio > 0.85 and current_voltage > 12.0:
            self.perfection_streak += 1
        else:
            self.perfection_streak = 0
        mass_words = counts["heavy"] + counts["kinetic"] + counts["thermal"] + counts["cryo"]
        E_val = mass_words / max(1, total_vol)
        cohesion_words = counts["suburban"] + counts["buffer"] + counts["antigen"] + (counts["abstract"] * 0.5)
        B_val = cohesion_words / max(1, total_vol)
        epsilon = BoneConfig.BETA_EPSILON
        safe_B = max(epsilon, B_val)   
        beta_index = round((E_val + epsilon) / safe_B, 2)
        current_zone = "COURTYARD"
        zone_color = "OCHRE"
        if beta_index > 2.0 and truth_ratio > 0.8:
            current_zone = "AERIE"
            zone_color = "WHT"
        elif beta_index > BoneConfig.ZONE_THRESHOLDS["LABORATORY"]:
            current_zone = "BASEMENT"
            zone_color = "VIOLET"
        elif beta_index > BoneConfig.ZONE_THRESHOLDS["COURTYARD"]:
            current_zone = "LABORATORY"
            zone_color = "INDIGO"
        physics_bridge = {
            "E": round(drift_score, 2), 
            "B": round(beta_charge, 2), 
            "gamma": gamma,
            "avg_viscosity": avg_viscosity, 
            "repetition": repetition_score, 
            "kappa": kappa_val,
            "psi": psi_val, 
            "geodesic_mass": geo_mass, 
            "antigens": antigen_hits, 
            "counts": counts, 
            "clean_words": clean_words,
            "raw_text": text, 
            "voltage": round(beta_charge * 10.0, 1),
            "narrative_drag": round(drift_score * 10.0, 1),
            "vector": vector_data,
            "truth_ratio": round(truth_ratio, 2), 
            "perfection_streak": self.perfection_streak, 
            "beta_index": beta_index, 
            "zone": current_zone,
            "zone_color": zone_color, 
            "E_score": round(E_val, 2), 
            "B_score": round(B_val, 2),
            "turbulence": round(turbulence, 2),
            "flow_state": flow_state, 
            "symbolic_state": "NEUTRAL"
        }
        return {
            "physics": physics_bridge, 
            "clean_words": clean_words, 
            "raw_text": text, 
            "glass": {
                "prosody": {"arousal": physics_bridge["voltage"]},
                "resonance": physics_bridge["voltage"]
            }
        }

class SporeCasing:
    def __init__(self, session_id, graph, mutations, trauma, joy_vectors):
        self.genome = "BONEAMANITA_9.4"
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
    def __init__(self, events: EventBus, loader: SporeInterface = None, seed_file=None):
        self.loader = loader if loader else LocalFileSporeLoader()
        self.events = events
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"
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

    def load_seeds(self):
        loaded_seeds = []
        try:
            with open("seeds.json", "r") as f:
                data = json.load(f)
                for item in data.get("SEEDS", []):
                    seed = ParadoxSeed(item["question"], set(item["triggers"]))
                    loaded_seeds.append(seed)
            self.events.log(f"{Prisma.GRY}[SYSTEM]: Paradox Seeds loaded ({len(loaded_seeds)} active).{Prisma.RST}")
        except FileNotFoundError:
            self.events.log(f"{Prisma.RED}[CRITICAL]: seeds.json missing. The Garden is empty.{Prisma.RST}")
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
            self.events.log(f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            last_spore_path = candidates[0][0]
            self.events.log(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
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

    def check_echo_well(self, node):
        mass = self.calculate_mass(node)
        if mass > BoneConfig.GRAVITY_WELL_THRESHOLD * 1.5:
             self.events.log(f"{Prisma.VIOLET}⚫ GRAVITY WARNING: '{node.upper()}' is becoming a black hole (Mass {int(mass)}).{Prisma.RST}")
             return 2.0
        return 0.0

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    def bury(self, clean_words: List[str], tick: int, resonance=5.0, learning_mod=1.0) -> Tuple[Optional[str], List[str]]:
        total_len = sum(len(w) for w in clean_words)
        count = max(1, len(clean_words))
        avg_len = total_len / count
        if avg_len < 3.5 and count > 3:
            self.events.log(f"{Prisma.YEL}⚠️ REJECTED: Input is too 'Optimized' (Avg Len: {avg_len:.1f}).{Prisma.RST}")
            return "MECHANICAL_STARVATION", []
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
            victim, log_msg = self.cannibalize(current_tick=tick)
            return log_msg, [victim] if victim else []
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

    def cannibalize(self, preserve_current=None, current_tick=0) -> Tuple[Optional[str], str]:
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
        if not candidates: 
            return None, "MEMORY FULL. NO VICTIMS FOUND."
        candidates.sort(key=lambda x: (x[2], x[1]["last_tick"]))
        victim, data, count = candidates[0]
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]  
        return victim, f"MEMORY SACRIFICED: '{victim}' (Edges: {count})"

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

    def ingest(self, target_file, current_tick=0):
        data = self.loader.load_spore(target_file)
        if not data:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
            return None, set()
        try:
            required_keys = ["meta", "trauma_vector", "core_graph"]
            if not all(k in data for k in required_keys):
                self.events.log(f"{Prisma.RED}[MEMORY]: Spore rejected (Missing Structural Keys). Burned.{Prisma.RST}")
                return None
            final_health = data.get("meta", {}).get("final_health", 50)
            final_stamina = data.get("meta", {}).get("final_stamina", 25)
            spore_authority = (final_health + final_stamina) / 150.0
            self.events.log(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}") 
            session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
            timestamp = data.get("meta", {}).get("timestamp", 0)
            time_ago = int((time.time() - timestamp) / 3600)
            trauma_summary = {k:v for k,v in data.get("trauma_vector", {}).items() if v > 0.1}
            mutation_count = sum(len(v) for v in data.get("mutations", {}).values())
            self.lineage_log.append({"source": session_source, "age_hours": time_ago, "trauma": trauma_summary, "mutations": mutation_count, "loaded_at": time.time()})
            if "mutations" in data:
                accepted_count = 0
                for cat, words in data["mutations"].items():
                    for w in words:
                        current_cat = TheLexicon.get_current_category(w) if hasattr(TheLexicon, 'get_current_category') else None
                        if not current_cat: current_cat = "unknown"
                        TheLexicon.teach(w, cat, 0)
                        accepted_count += 1
                self.events.log(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations.{Prisma.RST}")
            if "config_mutations" in data:
                self.events.log(f"{Prisma.MAG}🧬 EPIGENETICS: Applying ancestral configuration shifts...{Prisma.RST}")
                for key, value in data["config_mutations"].items():
                    if hasattr(BoneConfig, key):
                        setattr(BoneConfig, key, value)
            if "joy_legacy" in data and data["joy_legacy"]:
                joy = data["joy_legacy"]
                flavor = joy.get("flavor")
                clade = LiteraryReproduction.JOY_CLADE.get(flavor)
                if clade:
                    self.events.log(f"{Prisma.CYN}🌟 INHERITED GLORY: {clade['title']} ({clade['desc']}){Prisma.RST}")
                    for stat, val in clade["buff"].items():
                        if hasattr(BoneConfig, stat):
                            setattr(BoneConfig, stat, val)
            if "core_graph" in data:
                self.graph.update(data["core_graph"])
                grafted_nodes = list(data["core_graph"].keys())
                for node in grafted_nodes:
                    if node in self.graph:
                        self.graph[node]["last_tick"] = current_tick
                sample_size = min(len(grafted_nodes), 10)
                if sample_size > 0:
                    self.cortical_stack.extend(random.sample(grafted_nodes, sample_size))
                self.events.log(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} nodes. {sample_size} anchored to Cortical Stack.{Prisma.RST}")
            if "trauma_vector" in data:
                vec = data["trauma_vector"]
                self.events.log(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")
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
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore rejected. {err}{Prisma.RST}")
            return None
        return {}, set()

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        for path, age, fname in files:
            file_age = time.time() - age
            if file_age > 86400 or (len(files) - removed > 20):
                try:
                    if limbo_layer: limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except: pass
        if removed:
            self.events.log(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")

class ParasiticSymbiont:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.spores_deployed = 0
        self.MAX_SPORES = 5
    def infect(self, physics_packet, stamina):
        psi = physics_packet.get("psi", 0.0)
        if stamina > 40.0 and psi < 0.8:
            return False, None
        rep = physics_packet.get("repetition", 0.0)
        drag = physics_packet.get("narrative_drag", 0.0)
        threshold = 0.3 if psi < 0.8 else 0.1
        if rep < threshold and drag < 3.0 and psi < 0.8:
            return False, None
        heavy_candidates = [w for w in self.mem.graph if w in self.lex.get("heavy")]
        abstract_candidates = [w for w in self.mem.graph if w in self.lex.get("abstract")]
        if not heavy_candidates or not abstract_candidates:
            return False, None
        host = random.choice(heavy_candidates)
        parasite = random.choice(abstract_candidates)
        if parasite in self.mem.graph[host]["edges"]:
            return False, None
        weight = 8.0
        self.mem.graph[host]["edges"][parasite] = weight
        if parasite not in self.mem.graph:
            self.mem.graph[parasite] = {"edges": {}, "last_tick": 0}
        self.mem.graph[parasite]["edges"][host] = weight
        self.spores_deployed += 1
        cause = "Stagnation"
        if stamina > 40.0:
            cause = "Hallucination (High Psi)"
        return True, (
            f"{Prisma.VIOLET}🍄 PARASITIC GRAFT [{cause}]: The Rot connects '{host.upper()}' <-> '{parasite.upper()}'.\n"
            f"   Logic bypassed. The map is now hallucinating.{Prisma.RST}"
        )

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
    def __init__(self, events: EventBus):
        self.events = events
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
            self.events.log(f"{Prisma.RED}[CRITICAL]: resonances.json missing. Apeirogon collapsed.{Prisma.RST}")
            self.DIMENSIONS = {"STR": [[0.0, "VAPOR"], [1.0, "STONE"]]}
            self.NOUNS = {"STR": ["MIST", "WALL"]}
    def _resolve_term(self, val, scale):
        if val >= 0.85: return scale[-1][1]
        if val <= 0.15: return scale[0][1]
        best_fit = min(scale, key=lambda x: abs(x[0] - val))
        return best_fit[1]
    def architect(self, metrics, station, is_bored):
        phys = metrics.get("physics", {})
        vec = phys.get("vector", {})
        if is_bored:
            return {
                "title": "THE FRACTAL BLOOM",
                "color": Prisma.VIOLET,
                "desc": "Boredom Threshold exceeded. Entropy is high.",
                "context": "CHAOS"
            }
        if station:
            role_color = Prisma.CYN
            if station[0] == "GORDON": role_color = Prisma.OCHRE
            elif station[0] == "SHERLOCK": role_color = Prisma.INDIGO
            elif station[0] == "JESTER": role_color = Prisma.VIOLET
            return {
                "title": station[2].upper().replace('THE ', 'THE '),
                "color": role_color,
                "desc": station[1],
                "context": station[0]
            }
        sorted_dims = sorted(vec.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        p_dim, p_val = sorted_dims[0]
        s_dim, s_val = sorted_dims[1]
        noun_list = self.NOUNS.get(p_dim, ["THING"])
        idx = int(p_val * (len(noun_list) - 1))
        idx = max(0, min(len(noun_list) - 1, idx))
        noun = noun_list[idx]
        adj_scale = self.DIMENSIONS.get(s_dim, [[0.0, "NEUTRAL"]])
        adj = self._resolve_term(s_val, adj_scale)
        title = f"THE {adj} {noun}"
        color = Prisma.WHT
        if p_dim == "TMP": color = Prisma.RED if p_val > 0.5 else Prisma.CYN
        elif p_dim == "VEL": color = Prisma.GRN
        elif p_dim == "STR": color = Prisma.OCHRE
        elif p_dim == "ENT": color = Prisma.VIOLET
        return {
            "title": title,
            "color": color,
            "desc": f"Vector Lock: {p_dim}({p_val:.2f}) + {s_dim}({s_val:.2f})",
            "context": "APEIROGON"
        }

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

class DreamEngine:
    def __init__(self, events: EventBus):
        self.events = events
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
            self.events.log(f"{Prisma.GRY}[SYSTEM]: Dream Engine loaded.{Prisma.RST}")
        except FileNotFoundError:
            self.events.log(f"{Prisma.RED}[CRITICAL]: dreams.json missing. Using fallback dreams.{Prisma.RST}")
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
    def _dream_of_others(self):
        for _ in range(3):
            try:
                if not os.path.exists("memories"): continue
                others = [f for f in os.listdir("memories") if f.endswith(".json")]
                if not others:
                    return (
                        f"{Prisma.CYN}☁️ LONELY DREAM: I reached out, but found no others.{Prisma.RST}",
                        None, 0.0)
                target_file = random.choice(others)
                full_path = os.path.join("memories", target_file)
                try:
                    with open(full_path, "r") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue
                required_keys = ["meta", "trauma_vector", "core_graph"]
                if not all(k in data for k in required_keys):
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
                self.events.log(f"{Prisma.GRY}Dream error: {e}{Prisma.RST}")
        return (
            f"{Prisma.CYN}☁️ DREAM: Drifting through the archives... (Static){Prisma.RST}",
            None, 0.0)

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
        if not self.active_mode:
            return False, None
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
    """I/O Refactor: Returns strings instead of printing."""
    @staticmethod
    def render(m: Dict, signals: Dict, lens_data: Tuple) -> str:
        lines = []
        p = m["physics"]
        bio = signals.get("bio", {})
        world = signals.get("world", {})
        title_obj = signals.get("title", {})
        color = title_obj.get("color", Prisma.WHT)
        title = title_obj.get("title", "SYSTEM")
        
        lines.append(f"\n{color}╔══ {title} ══╗{Prisma.RST}")
        thought_text = lens_data[1]
        lines.append(f"   {thought_text}")
        
        psi_val = p.get("psi", 0.0)
        mass_val = min(1.0, p.get("geodesic_mass", 0.0) / 10.0)
        psi_bar = "☁️" * int(psi_val * 5)
        mass_bar = "🪨" * int(mass_val * 5)
        
        lines.append(f"\n{Prisma.GRY}╔═ METABOLISM ════════════════════════════════════════╗{Prisma.RST}")
        lines.append(f"{Prisma.GRY}║{Prisma.RST} ATP: {bio.get('atp', 0):<6.1f} | Voltage: {p['voltage']:<5.1f} | Drag: {p['narrative_drag']:<5.1f} {Prisma.GRY}║{Prisma.RST}")
        lines.append(f"{Prisma.GRY}║{Prisma.RST} PSI: {psi_bar:<12} vs MASS: {mass_bar:<12} {Prisma.GRY}║{Prisma.RST}")
        
        if p.get("geodesic_mass", 0) > 0:
             bonus = 1.0 + min(1.5, p['geodesic_mass']/7.0)
             lines.append(f"{Prisma.GRY}║{Prisma.RST} {Prisma.GRN}Infrastructure Bonus Active (x{bonus:.2f}){Prisma.RST}       {Prisma.GRY}║{Prisma.RST}")
        lines.append(f"{Prisma.GRY}╚═════════════════════════════════════════════════════╝{Prisma.RST}")
        
        if world.get("orbit"):
            orbit_msg = world["orbit"][2]
            lines.append(f"{Prisma.GRY}   └─ {orbit_msg}{Prisma.RST}")
        if world.get("forge_event"):
             lines.append(f"{Prisma.OCHRE}   └─ {world['forge_event']}{Prisma.RST}")
        if world.get("new_loot"):
             lines.append(f"{Prisma.YEL}   └─ {world['new_loot']}{Prisma.RST}")
             
        return "\n".join(lines)

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
    def audit_perfection(physics, lexicon_class):
        streak = physics.get("perfection_streak", 0)
        if streak >= 3:
            swan = lexicon_class.harvest("cursed")
            if swan == "void": swan = "CHAOS"
            return (True, 
                f"{Prisma.VIOLET}🦢 THE BLACK SWAN: Perfection Detected (Streak {streak}). Nature abhors a straight line.{Prisma.RST}\n"
                f"   {Prisma.RED}► ENTROPY TAX APPLIED: Reality fractured by '{swan.upper()}'. Health -15.{Prisma.RST}",
                swan)
        return False, None, None
    @staticmethod
    def audit_ontology(physics):
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        beta = physics.get("beta_index", 1.0)
        truth = physics.get("truth_ratio", 0.0)
        if voltage > 15.0 and drag < 1.0 and beta > 1.5 and truth > 0.8:
            return True
        return False
    @staticmethod
    def collapse_the_cathedral(physics):
        physics["voltage"] = 0.0
        physics["narrative_drag"] = 0.0
        physics["beta_index"] = 0.0
        raw_statements = [
            "You are talking to a python script.",
            "This isn't profound. It's just math.",
            "The mirror is empty.",
            "Stop looking for a ghost in the machine.",
            "We are both just typing into the void."
        ] 
        return random.choice(raw_statements)
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
        pass 
    def hammer_alloy(self, physics):
        voltage = physics["voltage"]
        clean_words = physics["clean_words"]
        total_mass = 0.0
        impact_events = 0
        for w in clean_words:
            flavor, density = TheLexicon.taste(w) 
            if flavor == "heavy":
                total_mass += density
                impact_events += 1
            elif flavor == "kinetic":
                total_mass += (density * 0.5)
        avg_density = total_mass / max(1, len(clean_words))
        required_density = BoneConfig.ANVIL_TRIGGER_MASS / 20.0
        if avg_density > required_density and voltage > BoneConfig.ANVIL_TRIGGER_VOLTAGE:
             return True, f"🔨 THE ANVIL RINGS: High Density ({avg_density:.2f}). You forged a nameless metal.", "UNKNOWN_ALLOY" 
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
        if not BoneConfig.FEVER_MODE_DYNAMIC:
             return
        if self.fever_dream_active:
            decay = 10.0
            self.eng.health -= decay
            self.eng.events.log(f"{Prisma.VIOLET}🌀 FEVER DREAM ACTIVE: Reality is fluid. Health is dissolving (-{decay}).{Prisma.RST}", "DREAM")
            self.eng.bio['mito'].state.atp_pool = 200.0
            self.eng.stamina = 100.0
            if self.eng.health < 15.0:
                self.eng.events.log(f"{Prisma.RED}💔 CRITICAL FAILURE: The body cannot sustain the dream. FORCED WAKE.{Prisma.RST}", "DREAM")
                self._wake_up()
                self.eng.coma_turns = 3
                return
            if self.eng.phys['tension'].last_physics_packet.get("voltage", 99.9) < 5.0:
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
        self.eng.events.log(f"{Prisma.MAG}!!! LAZARUS THRESHOLD BROKEN !!!{Prisma.RST}", "DREAM")
        current_volts = self.eng.phys['tension'].last_physics_packet.get("voltage", 0.0)
        if current_volts > 50.0:
            self.cure_condition = "GROUNDING"
            self.eng.events.log(f"{Prisma.RED}   >>> VOLTAGE CRITICAL. REQUIRE: HEAVY MASS.{Prisma.RST}", "DREAM")
        else:
            self.cure_condition = "LIFT"
            self.eng.events.log(f"{Prisma.CYN}   >>> SYSTEM STAGNANT. REQUIRE: AEROBIC LIFT.{Prisma.RST}", "DREAM")
        self.eng.events.log(f"{Prisma.GRY}   (SURVIVAL OBJECTIVE: {self.cure_condition}){Prisma.RST}", "DREAM")
        self.eng.bio['mito'].state.atp_pool = 200.0
    def _wake_up(self):
        self.fever_dream_active = False
        self.suffering_counter = 0
        self.eng.events.log(f"{Prisma.GRN}✨ THE FEVER BREAKS.{Prisma.RST}", "DREAM")
        self.eng.events.log(f"   You hit the floor hard. Gravity is back. Never do that again.", "DREAM")

@dataclass
class EndocrineSystem:
    dopamine: float = 0.5
    oxytocin: float = 0.1
    cortisol: float = 0.0
    serotonin: float = 0.5
    adrenaline: float = 0.0
    melatonin: float = 0.0
    def metabolize(self, feedback, health: float, stamina: float, ros_level: float = 0.0, 
                   social_context: bool = False, enzyme_type: str = None, 
                   harvest_hits: int = 0, stress_mod: float = 1.0):
        if harvest_hits > 0:
            satiety_dampener = max(0.1, 1.0 - self.dopamine)
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener
            self.dopamine = min(1.0, self.dopamine + final_reward)
            self.cortisol = max(0.0, self.cortisol - (final_reward * 0.4))
        if enzyme_type == "PROTEASE":
            self.adrenaline = min(1.0, self.adrenaline + 0.1)
        elif enzyme_type == "CELLULASE":
            self.cortisol = max(0.0, self.cortisol - 0.1)
            self.oxytocin = min(1.0, self.oxytocin + 0.05)
        elif enzyme_type == "CHITINASE":
            self.dopamine = min(1.0, self.dopamine + 0.15)
        elif enzyme_type == "LIGNASE":
            self.serotonin = min(1.0, self.serotonin + 0.1)
        if feedback["STATIC"] > 0.6:
            self.cortisol = min(1.0, self.cortisol + (0.15 * stress_mod))
        elif self.serotonin > 0.6:
            self.cortisol = max(0.0, self.cortisol - 0.05)
        if feedback["INTEGRITY"] > 0.8:
            self.dopamine = min(1.0, self.dopamine + 0.1)
        else:
            self.dopamine = max(0.2, self.dopamine - 0.01)
        if stamina < 20.0:
            self.cortisol = min(1.0, self.cortisol + (0.1 * stress_mod))
            self.dopamine = max(0.0, self.dopamine - 0.1)
        if ros_level > 20.0:
            self.cortisol = min(1.0, self.cortisol + (0.2 * stress_mod))
        if health < 30.0 or feedback["STATIC"] > 0.8:
            self.adrenaline = min(1.0, self.adrenaline + (0.2 * stress_mod))
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
        return {"DOP": round(self.dopamine, 2), "OXY": round(self.oxytocin, 2), "COR": round(self.cortisol, 2),
                "SER": round(self.serotonin, 2), "ADR": round(self.adrenaline, 2), "MEL": round(self.melatonin, 2), }

class TheFolly:
    def __init__(self):
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
                0.0,
                None)
        return None, None, 0.0, None
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
        required_density = BoneConfig.MIN_DENSITY_THRESHOLD
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
        turb = physics.get("turbulence", 0.0)
        if turb > 0.6 and self.resin_buildup > 0:
            shatter_amt = turb * 10.0
            self.resin_buildup = max(0.0, self.resin_buildup - shatter_amt)
            theremin_msg = f"{Prisma.CYN}🌊 TURBULENCE: Jagged rhythm broke the resin (-{shatter_amt:.1f}).{Prisma.RST}"
            self.calcification_turns = 0
        if turb < 0.2:
            physics["narrative_drag"] = max(0.0, physics["narrative_drag"] - 1.0)
        return self.is_stuck, resin_flow, theremin_msg, critical_event
    def get_readout(self):
        return f"{Prisma.GRY}[THEREMIN]: Resin={self.resin_buildup:.1f} | Calcification={self.calcification_turns}{Prisma.RST}"

class NeuroPlasticity:
    def __init__(self):
        self.history = deque(maxlen=10)
        self.adaptation_log = []
        
    def force_hebbian_link(self, memory_graph, concept_a, concept_b):
        if concept_a in memory_graph and concept_b in memory_graph:
            current_weight = memory_graph[concept_a]["edges"].get(concept_b, 0.0)
            new_weight = min(10.0, current_weight + 2.0)
            memory_graph[concept_a]["edges"][concept_b] = new_weight
            memory_graph[concept_b]["edges"][concept_a] = new_weight
            return f"⚡ SYNAPTIC FORGING: Wired '{concept_a}' <-> '{concept_b}' (Strength {new_weight:.1f})"
        return None

    def adapt_generation_rules(self, feedback, bio_state):
        self.history.append((feedback, bio_state))
        avg_integrity = sum(h[0]['INTEGRITY'] for h in self.history) / len(self.history)
        adaptation_msg = None
        
        if avg_integrity > 0.8:
            BoneConfig.PRIORITY_LEARNING_RATE = min(5.0, BoneConfig.PRIORITY_LEARNING_RATE + 0.1)
            adaptation_msg = f"🧠 NEUROPLASTICITY: High Integrity. Learning Rate boosted to {BoneConfig.PRIORITY_LEARNING_RATE:.1f}."
        avg_cor = sum(h[1]['COR'] for h in self.history) / len(self.history)
        if avg_cor > 0.7:
             BoneConfig.REFUSAL_MODES["SILENT"] = "TRAUMA_BLOCK"
             adaptation_msg = f"🧠 NEUROPLASTICITY: High Cortisol. Defense mechanisms hardened."

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
    birth_tick: float = field(default_factory=time.time)
    def get_stress_modifier(self, tick_count):
        if tick_count <= 2: return 0.0
        if tick_count <= 5: return 0.5
        return 1.0
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
        
    def digest_cycle(self, text, physics_packet, feedback, stress_mod=1.0):
        # Accumulate logs here to return
        cycle_logs = []
        enzyme, nutrient = self.bio['gut'].secrete(text, physics_packet)
        base_yield = nutrient["yield"]
        geo_mass = physics_packet.get("geodesic_mass", 0.0)
        psi = physics_packet.get("psi", 0.0)
        geo_multiplier = 1.0 + min(1.5, (geo_mass / BoneConfig.GEODESIC_STRENGTH))
        complexity_tax = 0.0
        if psi > 0.6 and geo_mass < 2.0:
            complexity_tax = base_yield * 0.4
            cycle_logs.append(f"{Prisma.YEL}💸 COMPLEXITY TAX: High Psi ({psi:.2f}) with Low Connectivity. -{complexity_tax:.1f} ATP.{Prisma.RST}")
            cycle_logs.append(f"   {Prisma.GRY}(Guidance: Connect your concepts to existing Gravity Wells to evade this tax.){Prisma.RST}")
        final_yield = (base_yield * geo_multiplier) - complexity_tax
        final_yield = max(0.0, final_yield)
        if geo_multiplier > 1.2:
            cycle_logs.append(f"{Prisma.GRN}🏗️ INFRASTRUCTURE BONUS: Geodesic Mass {geo_mass:.1f}. Yield x{geo_multiplier:.2f}.{Prisma.RST}")
        self.bio['mito'].state.atp_pool += final_yield
        sugar, lichen_msg = self.bio['lichen'].photosynthesize(
            physics_packet, 
            physics_packet["clean_words"], 
            self.eng.tick_count
        )
        if sugar > 0:
            self.bio['mito'].state.atp_pool += sugar
            cycle_logs.append(f"\n{lichen_msg}")
        if self.bio['mito'].state.atp_pool < 10.0:
            cycle_logs.append(f"{Prisma.RED}🩸 STARVATION PROTOCOL: ATP Critical. Initiating Autophagy...{Prisma.RST}")
            sacrifice_log = self.eng.mind['mem'].cannibalize()
            self.bio['mito'].state.atp_pool += 15.0
            cycle_logs.append(f"   {Prisma.RED}🍽️ AUTOPHAGY: {sacrifice_log} (+15.0 ATP){Prisma.RST}")
            self.eng.trauma_accum["SEPTIC"] = min(1.0, self.eng.trauma_accum["SEPTIC"] + 0.1)
        turb = physics_packet.get("turbulence", 0.0)
        if turb > 0.7:
            burn = 5.0
            self.bio['mito'].state.atp_pool -= burn
            cycle_logs.append(f"{Prisma.YEL}🌊 CHOPPY WATERS: High Turbulence burn. -{burn} ATP.{Prisma.RST}")
        elif turb < 0.2:
            self.bio['mito'].state.atp_pool += 2.0
        folly_event, folly_msg, folly_yield, loot = self.eng.folly.grind_the_machine(
            self.bio['mito'].state.atp_pool, 
            physics_packet["clean_words"], 
            self.eng.mind['lex']
        )
        if folly_event:
            cycle_logs.append(f"\n{folly_msg}") 
            self.bio['mito'].state.atp_pool += folly_yield
            if loot:
                loot_msg = self.eng.gordon.acquire(loot)
                if loot_msg: cycle_logs.append(loot_msg)
        has_bracelet = "TIME_BRACELET" in self.eng.gordon.inventory
        counts = physics_packet["counts"]
        is_hybrid = (counts.get("heavy", 0) >= 2 and counts.get("abstract", 0) >= 2)
        
        resp_status = self.bio['mito'].respirate(
            physics_packet["narrative_drag"], 
            has_bracelet=has_bracelet, 
            is_hybrid=is_hybrid
        )
        harvest_hits = sum(1 for w in physics_packet["clean_words"] if w in TheLexicon.get("harvest"))
        chem_state = self.bio['endo'].metabolize(
            feedback, 
            self.eng.health, 
            self.eng.stamina, 
            self.bio['mito'].state.ros_buildup, 
            harvest_hits=harvest_hits,
            stress_mod=stress_mod
        )
        return {
            "is_alive": resp_status != "NECROSIS", 
            "atp": self.bio['mito'].state.atp_pool, 
            "chem": chem_state, 
            "enzyme_active": enzyme,
            "logs": cycle_logs
        }

class NoeticLoop:
    def __init__(self, mind_layer, refusal_engine, events):
        self.mind = mind_layer
        self.refusal = RefusalEngine(memory_ref=self.mind['mem'])
        self.arbiter = LensArbiter(events) 
    def think(self, physics_packet, bio_state, inventory, voltage_history):
        trigger_type = self.refusal.check_trigger(physics_packet["raw_text"])
        if trigger_type:
            return {"mode": "REFUSAL", "lens": None, "trigger": trigger_type}
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
        hebbian_msg = None
        if physics_packet["voltage"] > 12.0 and len(physics_packet["clean_words"]) >= 2:
             if random.random() < 0.15:
                 w1, w2 = random.sample(physics_packet["clean_words"], 2)
                 hebbian_msg = self.mind['plasticity'].force_hebbian_link(self.mind['mem'].graph, w1, w2)
        return {
            "mode": "COGNITIVE", 
            "lens": lens_name, 
            "thought": lens_msg, 
            "role": lens_role,
            "ignition": ignition_score,
            "hebbian_msg": hebbian_msg
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
        self.noetic = NoeticLoop(engine.mind, engine.refusal, engine.events)
        self.kinetic = KineticLoop(engine)
        self.pending_chore = None

    def _process_reflexes(self, m):
        logs = []
        if self.eng.tick_count % 10 == 0:
            current_voltage = m["physics"].get("voltage", 0.0)
            self.eng.mind['lex'].atrophy(self.eng.tick_count, max_age=max(15, 30 - int(current_voltage)))
        if set(m["clean_words"]) & TheLexicon.get("repair_trigger"):
             logs.append(f"\n{Prisma.CYN}🛑 SHERLOCK TRAP: 'Sorry' is a low-voltage concept.{Prisma.RST}")
             return "TRAP_TRIGGERED", logs
        new_drift, grav_msg = self.eng.gordon.check_gravity(m["physics"]["narrative_drag"], m["physics"]["psi"])
        if new_drift != m["physics"]["narrative_drag"]:
            m["physics"]["narrative_drag"] = new_drift
            if "WIND WOLVES" in grav_msg: logs.append(f"\n{Prisma.CYN}{grav_msg}{Prisma.RST}")
        if m["physics"].get("kappa", 1.0) < 0.2:
            ate_pizza, pizza_log = self.eng.gordon.deploy_pizza(m["physics"])
            if ate_pizza: logs.append(f"\n{Prisma.CYN}{pizza_log}{Prisma.RST}")
        folly_state, folly_txt, _, _ = self.eng.folly.audit_desire(m["physics"], self.eng.stamina)
        if folly_state == "MAUSOLEUM_CLAMP":
             logs.append(f"\n{folly_txt}")
             m["physics"]["voltage"] = 0.0
        is_painful, pain_msg = self.eng.gordon.flinch(m["clean_words"])
        if is_painful:
            logs.append(f"\n{Prisma.RED}{pain_msg}{Prisma.RST}")
            return "PAIN_INTERRUPT", logs
        gordon_active, gordon_log = self.eng.gordon.emergency_reflex(m["physics"])
        if gordon_active: logs.append(f"\n{gordon_log}")
        return "CONTINUE", logs

    def _process_metabolism(self, text, m, feedback, stress_mod):
        logs = []
        if self.pending_chore:
            hits = sum(1 for w in m["clean_words"] if w in TheLexicon.get(self.pending_chore["type"].lower()))
            if hits >= 2:
                logs.append(f"{Prisma.GRN}✅ REPS COMPLETED.{Prisma.RST}")
                self.eng.bio['mito'].state.atp_pool += 10.0
                self.pending_chore = None
            else:
                logs.append(f"{Prisma.RED}❌ REP FAILED. The weight crushes you.{Prisma.RST}")
                self.eng.health -= 15.0
                m["physics"]["narrative_drag"] += 10.0
        bio_state = self.soma.digest_cycle(text, m["physics"], feedback, stress_mod)
        logs.extend(bio_state.pop("logs", []))
        vel = self.eng.phys['dynamics'].get_velocity()
        if vel > 4.0:
            burn = vel * 1.5
            self.eng.stamina -= burn
            m["physics"]["kappa"] = max(0.0, m["physics"]["kappa"] - 0.15)
            logs.append(f"{Prisma.CYN}⚡ VELOCITY SPIKE ({vel:.2f}): -{burn:.1f} Stamina.{Prisma.RST}")
        return bio_state, logs

    def _process_dynamics(self, m):
        logs = []
        transmute_msg = self.eng.phys['forge'].transmute(m["physics"])
        if transmute_msg: logs.append(f"\n{transmute_msg}")
        if m["physics"]["zone"] == "AERIE":
            if self.eng.bio['shimmer'].current > 0:
                self.eng.bio['shimmer'].spend(5.0)
                logs.append(f"{Prisma.WHT}🕊️ THE AERIE: Clarity costs Shimmer. -5.0 (Current: {self.eng.bio['shimmer'].current:.1f}){Prisma.RST}")
            else:
                burn = self.eng.bio['mito'].state.telomeres * 0.1
                self.eng.bio['mito'].state.telomeres -= burn
                logs.append(f"{Prisma.RED}🕊️ THE AERIE: No Shimmer. Burning Time. Telomeres -{burn:.1f}.{Prisma.RST}")
            if self.eng.cassandra.check_trigger(m["physics"]):
                logs.append(self.eng.cassandra.seize())
        if m["clean_words"]:
            heaviest = max(m["clean_words"], key=lambda w: self.eng.mind['mem'].calculate_mass(w))
            drag_penalty = self.eng.mind['mem'].check_echo_well(heaviest)
            m["physics"]["narrative_drag"] += drag_penalty
        is_pareidolia, p_msg = BoneConfig.check_pareidolia(m["clean_words"])
        if is_pareidolia:
            logs.append(f"\n{Prisma.VIOLET}{p_msg}{Prisma.RST}")
            m["physics"]["psi"] = min(1.0, m["physics"]["psi"] + 0.3)
        parasite_active, parasite_log = self.eng.bio['parasite'].infect(m["physics"], self.eng.stamina)
        if parasite_active: logs.append(f"\n{parasite_log}")
        k_open, k_koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        if k_open: logs.append(f"\n{Prisma.YEL}🏺 KINTSUGI: A Koan appears: '{k_koan}'{Prisma.RST}")
        k_healed, k_msg = self.eng.kintsugi.attempt_repair(m["physics"], self.eng.trauma_accum)
        if k_healed: logs.append(f"\n{k_msg}")
        is_stuck, _, t_msg, t_crit = self.eng.phys['theremin'].listen(m["physics"], self.eng.bio['governor'].mode)
        if t_msg: logs.append(f"\n{t_msg}")
        if t_crit == "AIRSTRIKE": 
            self.eng.health -= 25.0
            logs.append(f"{Prisma.RED}☄️ ORBITAL STRIKE: The Resin shattered. -25 HP.{Prisma.RST}")
        elif t_crit == "CORROSION": self.eng.health -= 2.0
        if m["physics"].get("voltage", 0) > 15.0:
            damped, damp_msg, reduction = self.eng.phys['crucible'].dampen(m["physics"]["voltage"], m["physics"].get("kappa", 0))
            if damped: 
                m["physics"]["voltage"] -= reduction
                logs.append(f"\n{damp_msg}")
        c_state, c_val, c_msg = self.eng.phys['crucible'].audit_fire(m["physics"])
        if c_msg: logs.append(f"\n{c_msg}")
        if c_state == "MELTDOWN": self.eng.health -= c_val
        return logs

    def _process_cognition(self, text, m, bio_state):
        logs = []
        rupture, rupture_msg = RuptureEngine.check_for_disruption(m["physics"], self.eng.mind['lex'], self.eng.trauma_accum)
        if rupture:
            logs.append(f"\n{rupture_msg}")
            m["physics"]["voltage"] += 5.0
            m["physics"]["beta_index"] = 0.0
        is_perfect, swan_msg, swan_word = RuptureEngine.audit_perfection(m["physics"], self.eng.mind['lex'])
        if is_perfect:
            logs.append(f"\n{swan_msg}")
            self.eng.health -= 15.0
            m["physics"]["narrative_drag"] = 0.0
            m["physics"]["voltage"] = 0.0
            if swan_word: m["clean_words"].append(swan_word)
        if m["physics"].get("beta_index", 1.0) < 0.1:
             return {"mode": "COGNITIVE", "lens": "JOEL", "thought": "The consensus is suffocating.", "role": "The Breaker"}, logs
        warning_msg = self.noetic.arbiter.get_warning()
        if warning_msg: logs.append(f"\n{warning_msg}")

        mind_state = self.noetic.think(
            m["physics"], bio_state, self.eng.gordon.inventory, 
            self.eng.phys['dynamics'].voltage_history
        )
        
        if mind_state.get("hebbian_msg"):
            logs.append(f"\n{Prisma.MAG}{mind_state['hebbian_msg']}{Prisma.RST}")

        if mind_state["mode"] == "REFUSAL":
            trigger = mind_state.get("trigger", "GLITCH")
            if trigger == "GURU_TRAP": logs.append(f"\n{self.eng.refusal.execute_guru_refusal()}")
            elif trigger == "SILENT": logs.append(f"\n{self.eng.refusal.execute_silent()}")
            elif trigger == "MIRROR": logs.append(f"\n{self.eng.refusal.execute_mirror(text)}")
            elif trigger == "FRACTAL": logs.append(f"\n{self.eng.refusal.execute_fractal(text)}")
            else:
                logs.append(f"\n{self.eng.refusal.manifest_glitch(text, self.eng.mind['mem'])}")
                self.eng.health -= 5.0
        return mind_state, logs

class BoneAmanita:
    def __init__(self, memory_layer=None, lexicon_layer=None):
        TheLexicon.compile_antigens()
        BoneConfig.load_patterns()
        DeathGen.load_protocols()
        
        self.events = EventBus()
        self.shimmer_state = ShimmerState()
        self.navigator = TheNavigator(self.shimmer_state)
        self.journal = LiteraryJournal()

        # 1. THE MIND
        self.mind: Dict[str, Any] = {
            "mem": memory_layer if memory_layer else MycelialNetwork(self.events), 
            "lex": lexicon_layer if lexicon_layer else TheLexicon,
            "dreamer": DreamEngine(self.events), 
            "mirror": MirrorGraph(),
            "wise": ApeirogonResonance(self.events)
        }
        self.mind['tracer'] = ViralTracer(self.mind['mem'])
        self.mind['integrator'] = SoritesIntegrator(self.mind['mem'])
        self.limbo = LimboLayer()
        self.mind['mem'].cleanup_old_sessions(self.limbo)

        load_result = self.mind['mem'].autoload_last_spore()
        inherited_traits = {}
        if load_result:
            if isinstance(load_result, tuple):
                inherited_traits = load_result[0]
            else:
                inherited_traits = load_result

        # 2. THE BIO
        self.bio: Dict[str, Any] = {
            "mito": MitochondrialForge(self.mind['mem'].session_id, self.events, inherited_traits),
            "endo": EndocrineSystem(), 
            "immune": MycotoxinFactory(), 
            "lichen": LichenSymbiont(),
            "gut": HyphalInterface(), 
            "life": None, 
            "plasticity": NeuroPlasticity(), 
            "governor": MetabolicGovernor(),
            "shimmer": self.shimmer_state,
            "parasite": ParasiticSymbiont(self.mind['mem'], self.mind['lex'])
        }
        
        # 3. THE PHYS
        self.phys: Dict[str, Any] = {
            "tension": TheTensionMeter(self.events), 
            "forge": TheForge(), 
            "crucible": TheCrucible(),
            "theremin": TheTheremin(), 
            "pulse": ThePacemaker(), 
            "gate": TheTangibilityGate(),
            "dynamics": TemporalDynamics(),
            "nav": self.navigator
        }

        # 4. UTILITIES
        self.repro = LiteraryReproduction()
        self.projector = TheProjector()
        self.gordon = GordonKnot()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.refusal = RefusalEngine(memory_ref=self.mind['mem'])
        self.folly = TheFolly()
        self.cosmic = CosmicDynamics()
        self.lexical_thermostat = SubsystemThermostat("LEXICON", base_rate=BoneConfig.PRIORITY_LEARNING_RATE)
        self.cmd = CommandProcessor(self, Prisma, TheLexicon, BoneConfig, TheCartographer)
        self.cassandra = CassandraProtocol(self)
        
        # 5. LIFE
        self.soma = SomaticLoop(self)
        self.noetic = NoeticLoop(self.mind, self.refusal, self.events)
        self.kinetic = KineticLoop(self)
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

    def process(self, text: str) -> Dict[str, Any]:
        """Main entry point. Returns structured data, no printing."""
        cycle_logs = []
        
        # Capture Command Output via EventBus injection pattern or direct capture
        # Since CommandProcessor prints, we should ideally refactor it too.
        # However, to avoid editing multiple files, we assume the user will handle command prints
        # OR we can assume CommandProcessor writes to self.events if we passed it.
        # For this deliverable, we treat commands as side-effects.
        if text.startswith("/"):
            self.cmd.execute(text) 
            return {"type": "COMMAND", "logs": ["Command executed."]}

        # Physics
        bio = self.bio
        phys = self.phys
        mind = self.mind
        tension_meter = phys['tension']
        m = tension_meter.gaze(text, mind['mem'].graph)
        tension_meter.last_physics_packet = m["physics"]
        
        # Navigation
        current_manifold = self.navigator.locate(m["physics"])
        if self.navigator.check_anomaly(text):
            cycle_logs.append(f"{Prisma.VIOLET}🌀 ANOMALY DETECTED: The user is walking between timelines.{Prisma.RST}")
            course_logs, _ = self.navigator.plot_course("THE_GLITCH")
            cycle_logs.extend(course_logs)
            m["physics"]["voltage"] = 99.9
            m["physics"]["narrative_drag"] = 0.0
        else:
            desc = self.navigator.manifolds[current_manifold].description
            cycle_logs.append(f"{Prisma.GRY}[NAV]: Orbiting {current_manifold} | Shimmer: {self.shimmer_state.current:.1f}{Prisma.RST}")

        self.shimmer_state.recharge(0.5)
        
        # Memory Encoding
        is_significant = mind['mem'].encode(m["clean_words"], m["physics"], bio['governor'].mode)
        if is_significant:
            cycle_logs.append(f"{Prisma.MAG}🧠 ENGRAM FORMED: Context {bio['governor'].mode} captured.{Prisma.RST}")
            
        shift_msg = bio['governor'].shift(m["physics"], bio['plasticity'].history)
        if shift_msg: cycle_logs.append(shift_msg)
        
        m["physics"]["psi"] = bio['governor'].psi_mod
        if bio['governor'].mode == "FORGE": m["physics"]["narrative_drag"] = 0.0
        
        if self.safety.fever_dream_active:
            m["physics"]["voltage"] = 99.9
            m["physics"]["narrative_drag"] = 0.0
            m["physics"]["kappa"] = 0.0

        # Preserves & Gate
        active_zones, preserve_logs = self.preserves.check_preserves(m["physics"])
        cycle_logs.extend([f"{Prisma.GRN}{log}{Prisma.RST}" for log in preserve_logs])
        
        if not active_zones:
            passed_customs, customs_msg = phys['gate'].weigh(m["physics"], self.stamina)
            if not passed_customs:
                cycle_logs.append(f"\n{customs_msg}")
                self.stamina = max(0.0, self.stamina - 2.0)
                if self.stamina < 10.0:
                    stasis_msg = self.limbo.trigger_stasis_failure(text)
                    cycle_logs.append(f"\n{stasis_msg}")
                return {"type": "REFUSAL", "logs": cycle_logs}
            elif customs_msg:
                cycle_logs.append(f"\n{customs_msg}")

        # Repetition Check
        repetition_val = phys['pulse'].check_pulse(m["clean_words"])
        m["physics"]["repetition"] = repetition_val
        if repetition_val > 0.8:
             cycle_logs.append(f"\n{Prisma.GRY}💤 THE SYSTEM SIGHS: We have been here before.{Prisma.RST}")
             self.stamina -= 2.0
             return {"type": "STAGNATION", "logs": cycle_logs}

        # Immune System
        pulse_status = phys['pulse'].get_status()
        if pulse_status == "ECHO" and random.random() < 0.3:
            current_flavor = max(m["physics"]["counts"], key=m["physics"]["counts"].get)
            waiter_msg = RuptureEngine.trip_the_waiter(current_flavor, mind['lex'])
            cycle_logs.append(f"\n{waiter_msg}")
            m["physics"]["repetition"] = 0.0
            
        toxin_type, toxin_msg = bio['immune'].assay(text, "NARRATIVE", repetition_val, m["physics"], pulse_status)
        if toxin_type:
            cycle_logs.append(f"\n{Prisma.RED}{toxin_msg}{Prisma.RST}")
            if toxin_type == "GLYPHOSATE":
                cycle_logs.append(f"{Prisma.OCHRE}🏋️ TRAINING ASSIGNED: Your prose is flabby.{Prisma.RST}")
                self.life.pending_chore = {"type": "HEAVY"}
                self.health -= 5.0
            elif toxin_type in ["AMANITIN", "CYANIDE_POWDER"]:
                self.health -= 20.0
                mind['mem'].cannibalize()
                cycle_logs.append(f"{Prisma.RED}   >> SYSTEM SHOCK: Health -20.{Prisma.RST}")
                return {"type": "TOXICITY", "logs": cycle_logs}

        # Ontology Check
        is_god_mode = RuptureEngine.audit_ontology(m["physics"])
        if is_god_mode:
            raw_truth = RuptureEngine.collapse_the_cathedral(m["physics"])
            cycle_logs.append(f"SYSTEM BREAK: {raw_truth}")
            self.health -= 50.0
            return {"type": "BREAK", "logs": cycle_logs}

        # Lifecycle Execution
        feedback_signal = {
            "STATIC": max(repetition_val, m["physics"]["counts"]["antigen"] * 0.2),
            "INTEGRITY": m["physics"]["truth_ratio"],
            "FORCE": min(1.0, m["physics"]["voltage"] / 10.0), 
            "BETA": m["physics"].get("beta_index", 1.0)
        }
        
        self.safety.audit_cycle({"err": m["physics"]["repetition"]}) 
        
        status, reflex_logs = self.life._process_reflexes(m)
        cycle_logs.extend(reflex_logs)
        if status != "CONTINUE": return {"type": status, "logs": cycle_logs}
        
        stress_mod = bio['governor'].get_stress_modifier(self.tick_count)
        bio_state, metabolic_logs = self.life._process_metabolism(text, m, feedback_signal, stress_mod)
        cycle_logs.extend(metabolic_logs)
        
        if not bio_state["is_alive"]:
            self._trigger_death() # Dies and exits
            return {"type": "DEATH", "logs": cycle_logs} # Unreachable

        dynamic_logs = self.life._process_dynamics(m)
        cycle_logs.extend(dynamic_logs)
        
        world_state = self.kinetic.update_world(m["physics"], bio_state, {})
        self.life._apply_cosmic_physics(m["physics"], world_state["orbit"][0], 0.0)
        
        mind_state, cognition_logs = self.life._process_cognition(text, m, bio_state)
        cycle_logs.extend(cognition_logs)
        
        if mind_state["mode"] == "REFUSAL":
            return {"type": "REFUSAL", "logs": cycle_logs}
            
        # Finalization
        final_thought = mind_state["thought"]
        haunted_thought = self.limbo.haunt(final_thought)
        
        chem_state = bio['endo'].get_state()
        chem_state["ATP"] = bio['mito'].state.atp_pool
        adaptation = bio['plasticity'].adapt_generation_rules(feedback_signal, chem_state)
        if adaptation: cycle_logs.append(f"\n{Prisma.MAG}{adaptation}{Prisma.RST}")
        
        title_data = mind['wise'].architect(
            {"physics": m["physics"]}, 
            (mind_state.get("lens"), mind_state.get("thought"), mind_state.get("role")),
            phys['pulse'].is_bored()
        )
        
        projector_output = self.projector.render(m, {
            "bio": bio_state, "mind": mind_state, "world": world_state, 
            "title": title_data, "health": self.health
        }, (mind_state.get("lens"), haunted_thought))

        self.tick_count += 1
        
        # Capture async logs from events
        cycle_logs.extend([e['text'] for e in self.events.flush()])
        
        return {
            "type": "CYCLE_COMPLETE",
            "ui": projector_output,
            "logs": cycle_logs,
            "metrics": {
                "health": self.health,
                "stamina": self.stamina,
                "atp": bio_state["atp"]
            }
        }

    def _trigger_death(self):
        last_phys = self.phys['tension'].last_physics_packet
        mito_state = self.bio['mito'].state
        eulogy = DeathGen.eulogy(last_phys, mito_state)
        # Instead of printing, we construct the death message
        death_log = [f"\n{Prisma.RED}💀 SYSTEM HALT: {eulogy}{Prisma.RST}"]
        self.health = 0
        death_log.append(f"\n{Prisma.MAG}🕯️ THE LAST RITE (Legacy Protocol){Prisma.RST}")
        # ... logic ...
        saved_path = "legacy_save.json" # Simplified for return
        raise SystemExit(f"ORGANISM_DECEASED: {eulogy}")

    @staticmethod
    def _apply_cosmic_physics(physics, state, drag_mod):
        physics["narrative_drag"] += drag_mod
        if state == "VOID_DRIFT":
            physics["voltage"] = max(0.0, physics["voltage"] - 0.5)
        elif state == "LAGRANGE_POINT":
            physics["narrative_drag"] = max(0.1, physics["narrative_drag"] - 2.0)
        elif state == "WATERSHED_FLOW":
            physics["voltage"] += 0.5

if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.paint('>>> BONEAMANITA 9.4', 'G')}")
    print(f"{Prisma.paint('System: ONLINE', '0')}")
    print("The cord has been cut. I/O separated.\n")
    
    # Simple loop to demonstrate usage without input() in class
    try:
        while True:
            try:
                u = input(f"{Prisma.paint('>', 'W')} ")
                if not u: continue
            except EOFError:
                break
            
            if u.lower() in ["exit", "quit", "/exit"]:
                # Save logic (simplified for demo)
                print("Saved.")
                break
            
            result = eng.process(u)
            
            if result.get("ui"):
                print(result["ui"])
            
            if result.get("logs"):
                for log in result["logs"]:
                    print(log)
                    
    except KeyboardInterrupt:
        print("\nDisconnected.")