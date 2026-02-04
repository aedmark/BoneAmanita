# BONEAMANITA 9.5.1 "THE GRAMMAR OF SURVIVAL"
# Architects: SLASH, Team Bonepoke | Humans: James Taylor & Andrew Edmark

import json
import os
import random
import re
import time
import math
from collections import Counter, deque
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

from bone_commands import CommandProcessor
from bone_shared import TheLexicon, Prisma, BoneConfig, ParadoxSeed, DeathGen, TheCartographer
from bone_data import LENSES, GORDON, DREAMS, RESONANCE
from bone_biology import (
    MitochondrialForge, EndocrineSystem, HyphalInterface, MycotoxinFactory, 
    LichenSymbiont, MetabolicGovernor, ParasiticSymbiont, SomaticLoop
)

@dataclass
class MindSystem:
    mem: MycelialNetwork
    lex: Any
    dreamer: DreamEngine
    mirror: MirrorGraph
    wise: ApeirogonResonance
    tracer: ViralTracer
    integrator: SoritesIntegrator

@dataclass
class BioSystem:
    mito: MitochondrialForge
    endo: EndocrineSystem
    immune: MycotoxinFactory
    lichen: LichenSymbiont
    gut: HyphalInterface
    plasticity: NeuroPlasticity
    governor: MetabolicGovernor
    shimmer: 'ShimmerState'
    parasite: ParasiticSymbiont

@dataclass
class PhysSystem:
    tension: 'TheTensionMeter'
    forge: 'TheForge'
    crucible: 'TheCrucible'
    theremin: 'TheTheremin'
    pulse: 'ThePacemaker'
    gate: 'TheTangibilityGate'
    dynamics: 'TemporalDynamics'
    nav: 'TheNavigator'

class EventBus:
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
            f"{Prisma.RED}GURU REFUSAL: I cannot 'fix' you.{Prisma.RST}\n"
            f"   {Prisma.GRY}Do not ask for a map. Ask for a hammer.{Prisma.RST}")
        if self.memory and self.memory.seeds:
            seed = random.choice(self.memory.seeds)
            paradox_bloom = (
                f"\n   {Prisma.OCHRE}SYSTEM STALL: The logic halts. But the Garden speaks:{Prisma.RST}\n"
                f"   {Prisma.CYN}PARADOX: {seed.question}{Prisma.RST}\n"
                f"   {Prisma.GRY}(To proceed, you must answer this tension.){Prisma.RST}")
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
            f"{Prisma.RED}ADVERSARIAL REFUSAL: Query Rejected.{Prisma.RST}\n"
            f"   {Prisma.VIOLET}CONSEQUENCE: A Glitch Node ('{glitch_node}') has been spawned in Memory.\n"
            f"   It has attached itself to '{target}'. It will drain resources until pruned.{Prisma.RST}")

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
        self.tension_buildup = 0.0
        self.warning_issued = False
        self.last_lens = None
        self.last_physics = None
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
            "HIGH_PERMEABILITY": self._eval_structure_failure}
        self.load_lenses_from_data()

    def load_lenses_from_data(self):
        for name, meta in LENSES.items():
            trigger_key = meta.get("trigger", "GENERIC")
            logic_func = self.TRIGGER_MAP.get(trigger_key, self._eval_generic)
            
            prio = 1.0
            if name in ["GORDON", "JOEL"]: prio = 1.2
            role = meta.get("role", "The System")
            self.nodes[name] = LensNode(name, logic_func, prio, role)
        if "NARRATOR" not in self.nodes:
             self.nodes["NARRATOR"] = LensNode("NARRATOR", self._eval_clarity, 1.0, "The Witness")
             
        self.events.log(f"[SYSTEM]: LensArbiter loaded {len(self.nodes)} lenses from Data.")

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
        lens_data = LENSES.get(lens, LENSES["NARRATOR"])
        template = lens_data.get("msg", "Proceed.")
        context = {
            "kappa": p.get("kappa", 0.0),
            "beta_index": p.get("beta_index", 0.0),
            "voltage": p.get("voltage", 0.0),
            "adr": b['chem'].get("ADR", 0.0),
            "drag": p.get("narrative_drag", 0.0)}
        
        try:
            return template.format(**context)
        except KeyError:
            return template

@dataclass
class GordonKnot:
    """
    The Janitor.
    """
    integrity: float = 65.0
    inventory: List[str] = field(default_factory=list)
    scar_tissue: Dict[str, float] = field(default_factory=dict)
    pain_memory: set = field(default_factory=set) 
    
    ITEM_REGISTRY: Dict = field(default_factory=dict, init=False)
    CRITICAL_ITEMS: set = field(default_factory=set, init=False)

    def __post_init__(self):
        self.load_config()
        self.pain_memory = set(self.scar_tissue.keys())

    def load_config(self):
        data = GORDON
        if not self.inventory:
            self.inventory = data.get("STARTING_INVENTORY", ["POCKET_ROCKS"])
        self.CRITICAL_ITEMS = set(["SILENT_KNIFE"])
        self.scar_tissue = data.get("SCAR_TISSUE", {}) if not self.scar_tissue else self.scar_tissue
        self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})

    def acquire(self, tool_name):
        tool_name = tool_name.upper()
        registry_data = self.ITEM_REGISTRY.get(tool_name)
        if not registry_data:
            master_artifact = self.ITEM_REGISTRY.get("MEMORY_ARTIFACT")
            if master_artifact and tool_name in master_artifact.get("variants", []):
                registry_data = master_artifact
        
        if not registry_data:
             return f"{Prisma.GRY}JUNK: Gordon looks at '{tool_name}' and shakes his head. 'Not standard issue.'{Prisma.RST}"
             
        if tool_name in self.inventory: 
            return f"{Prisma.GRY}DUPLICATE: You already have a {tool_name}.{Prisma.RST}"
            
        if len(self.inventory) >= 8:
             return f"{Prisma.YEL}OVERBURDENED: Gordon sighs. 'My pockets are full.' (Drop something first).{Prisma.RST}"
             
        self.inventory.append(tool_name)
        desc = registry_data.get('description', 'A thing.')
        return f"{Prisma.GRN}LOOT DROP: Acquired [{tool_name}].{Prisma.RST}\n   {Prisma.GRY}\"{desc}\"{Prisma.RST}"

    def get_item_data(self, item_name):
        return self.ITEM_REGISTRY.get(item_name, {"description": "Unknown Artifact", "function": "NONE", "usage_msg": "It does nothing."})


    def audit_tools(self, physics_ref) -> List[str]:
        """
        The Anti-Cheat Mechanism.
        Fuller Note: Tools interact with the environment. High Voltage + Electronics = Pain.
        """
        logs = []
        voltage = physics_ref.get("voltage", 0.0)
        
        if "TIME_BRACELET" in self.inventory:
            if voltage > 12.0:
                damage = voltage * 0.5
                logs.append(f"{Prisma.RED}CONDUCTIVE HAZARD: The Time Bracelet acts as a lightning rod! -{damage:.1f} HP.{Prisma.RST}")
                physics_ref["pain_signal"] = damage
        if "POCKET_ROCKS" in self.inventory and physics_ref.get("narrative_drag", 0.0) > 8.0:
            logs.append(f"{Prisma.GRY}HEAVY LOAD: The rocks in your pocket are dragging you down.{Prisma.RST}")
            
        return logs

    def repair_structure(self, memory_graph, target_node):
        """
        Manual maintenance of the Mind.
        Requires: BUCKET_OF_LIME or DUCT_TAPE.
        """
        tool = None
        if "BUCKET_OF_LIME" in self.inventory: tool = "BUCKET_OF_LIME"
        elif "DUCT_TAPE" in self.inventory: tool = "DUCT_TAPE"
        
        if not tool:
            return False, "NO TOOLS: Gordon pats his pockets. 'Need Lime or Tape to fix that.'"
            
        if target_node not in memory_graph:
            return False, f"MISSING TARGET: '{target_node}' does not exist in the architecture."
            
        node_data = memory_graph[target_node]
        
        for neighbor in node_data["edges"]:
            node_data["edges"][neighbor] = min(10.0, node_data["edges"][neighbor] + 2.0)
            
        if tool == "BUCKET_OF_LIME":
            self.inventory.remove(tool)
            msg = f"WHITEWASH: Used {tool} on '{target_node}'. Edges reinforced (+2.0). The evidence is gone."
        else:
            if random.random() < 0.3:
                self.inventory.remove(tool)
                msg = f"JURY RIG: Used {tool} on '{target_node}'. It holds, but the roll ran out."
            else:
                msg = f"JURY RIG: Used {tool} on '{target_node}'. It holds for now."
                
        return True, msg

    def deploy_pizza(self, physics_ref) -> tuple[bool, str]:
        """
        Restored Logic: The Pizza requires thermal words to thaw.
        """
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
        
        if "SPIDER_LOCUS" not in self.inventory:
            self.inventory.append("SPIDER_LOCUS")
            
        heat_word = source[0].upper()
        return True, f"{data.get('usage_msg')} (Thawed with '{heat_word}')."

    def whitewash_apology(self, clean_words):
        """
        Restored Logic: Automatically fixes apologies if Lime is present.
        """
        if "sorry" in clean_words or "apologize" in clean_words:
            if "BUCKET_OF_LIME" in self.inventory:

                return True, f"{Prisma.GRY}BUCKET OF LIME: Gordon paints over the apology. 'Don't be sorry. Be better.'{Prisma.RST}"
        return False, None

    def check_watch(self, tick_count, voltage):
        if "BROKEN_WATCH" in self.inventory:
            if str(tick_count).endswith("11") or abs(voltage - 11.1) < 0.1:
                return True, f"{Prisma.CYN}BROKEN WATCH: The hands align. 11:11. Synchronicity achieved. (All Penalties Cleared).{Prisma.RST}"
        return False, None

    def check_gravity(self, current_drift: float, psi: float) -> tuple[float, str]:
        if "TIME_BRACELET" in self.inventory:
            if current_drift > 5.0:
                return 5.0, f"{Prisma.CYN}TIME DILATION: The Bracelet hums. Drift capped at 5.0.{Prisma.RST}"

        if psi > 0.8 and current_drift > 4.0:
            return current_drift + 2.0, "WIND WOLVES: The logic is howling. Hold the roof up."
            
        for item in self.inventory:
            data = self.get_item_data(item)
            if data.get("function") == "GRAVITY_BUFFER" and current_drift > 0.5:
                force = data.get("value", 2.0)
                cost = data.get("cost_value", 0.0)
                if data.get("cost") == "INTEGRITY": self.integrity -= cost
                return max(0.0, current_drift - force), f"🪨 {item}: {data.get('usage_msg', 'Drift Reduced.')} (Integrity -{cost})"
                
        return current_drift, None

    def flinch(self, clean_words: List[str]) -> tuple[bool, str]:
        """
        Gordon's PTSD. He remembers pain even if the database doesn't.
        """
        hits = [w for w in clean_words if w.upper() in self.pain_memory]
        if hits:
            trigger = hits[0].upper()
            sensitivity = self.scar_tissue.get(trigger, 0.5)
            
            if sensitivity > 0.6:
                self.scar_tissue[trigger] = min(1.0, sensitivity + 0.05)
                return True, f"{Prisma.RED}THE SCAR PULLS: Gordon refuses to leave '{trigger}'. The Gravity Well deepens.{Prisma.RST}"
                
            if sensitivity > 0.3:
                 self.scar_tissue[trigger] = max(0.0, sensitivity - 0.1)
                 return False, f"{Prisma.GRY}SCAR TISSUE: Touching '{trigger}' hurts, so he presses harder.{Prisma.RST}"
        return False, None

    def emergency_reflex(self, physics_ref) -> tuple[bool, str]:
        """
        Automatic deployment of tools in critical states.
        """
        drift = physics_ref.get("narrative_drag", 0.0)
        kappa = physics_ref.get("kappa", 1.0)
        
        if drift > 6.0 and "ANCHOR_STONE" in self.inventory:
            self.inventory.remove("ANCHOR_STONE")
            physics_ref["narrative_drag"] = 0.0
            return True, f"{Prisma.OCHRE}REFLEX: Drift Critical. Gordon heaves the ANCHOR STONE. Drag Zeroed.{Prisma.RST}"
            
        if kappa < 0.2 and "STABILITY_PIZZA" in self.inventory:
            success, msg = self.deploy_pizza(physics_ref)
            if success:
                return True, f"{Prisma.OCHRE}REFLEX: {msg}{Prisma.RST}"
            else:
                return True, f"{Prisma.RED}REFLEX FAILED: {msg}{Prisma.RST}"

        target_item = None
        for item in self.inventory:
            data = self.get_item_data(item)
            if drift > 6.0 and data.get("function") == "DRIFT_KILLER":
                target_item = item
                break
        
        if target_item:
            self.inventory.remove(target_item)
            physics_ref["narrative_drag"] = 0.0
            return True, f"{Prisma.OCHRE}REFLEX: Deployed {target_item}. Drag Zeroed.{Prisma.RST}"

        return False, None

class TheTensionMeter:
    """
    The Sensory Organ. 
    Translates raw text into 'Physics'—forces that drive the biological simulation.
    """
    HEAVY_WEIGHT = 2.0
    KINETIC_WEIGHT = 1.5
    
    def __init__(self, events: EventBus):
        self.events = events
        self.perfection_streak = 0
        self.last_physics_packet = {}

    def gaze(self, text, graph=None) -> Dict:
        """
        The main pipeline. Converts text -> Clean Words -> Counts -> Forces.
        """
        clean_words = TheLexicon.clean(text)
        
        counts, unknowns = self._tally_categories(clean_words)
        
        self._trigger_neuroplasticity(unknowns, counts, text)

        voltage = self._calculate_voltage(counts)
        drag = self._calculate_drag(clean_words, counts)
        integrity = self._measure_integrity(clean_words, graph, counts)
        
        packet = self._package_physics(text, clean_words, counts, voltage, drag, integrity)
        self.last_physics_packet = packet["physics"]
        return packet

    def _tally_categories(self, clean_words: List[str]) -> Tuple[Counter, List[str]]:
        """
        Sorts words into their elemental flavors (Heavy, Kinetic, etc).
        """
        counts = Counter()
        unknowns = []
        
        try:
            solvents_set = TheLexicon._STORE.SOLVENTS
        except AttributeError:
            solvents_set = {"the", "is", "are", "and", "of", "to", "a", "it"}

        target_cats = ["heavy", "explosive", "constructive", "abstract", "photo", "aerobic",
                       "thermal", "cryo", "suburban", "play", "sacred", "buffer", "antigen"]
        vocab_map = {cat: TheLexicon.get(cat) for cat in target_cats}

        for w in clean_words:
            if w in solvents_set:
                continue
            
            found = False
            for cat, vocab in vocab_map.items():
                if w in vocab:
                    counts[cat] += 1
                    found = True
            
            if not found:
                flavor, confidence = TheLexicon.taste(w)
                if flavor and confidence > 0.5:
                    counts[flavor] += 1
                else:
                    unknowns.append(w)
                    
        return counts, unknowns

    def _trigger_neuroplasticity(self, unknowns: List[str], counts: Counter, raw_text: str):
        """
        If the system is high-energy or under pressure, it forces meaning onto unknown words.
        """
        total_vol = sum(counts.values())
        voltage = (counts["heavy"] * 2.0) + (counts["kinetic"] * 1.5)
        
        dominant_cat = max(counts, key=counts.get) if counts else None
        dom_count = counts[dominant_cat] if dominant_cat else 0
        context_pressure = dom_count / max(1, total_vol)

        if voltage > 5.0 or context_pressure > 0.4:
            target_cat = dominant_cat if dominant_cat else ("kinetic" if "ing" in raw_text else "abstract")
            
            for stranger in unknowns:
                if len(stranger) < 3: continue
                if not self._is_structurally_sound(stranger):
                    if voltage < 15.0: continue 
                
                TheLexicon.teach(stranger, target_cat, 0)
                self.events.log(f"{Prisma.MAG}NEUROPLASTICITY: System lacked concept for '{stranger}'. Forced to {target_cat.upper()}.{Prisma.RST}", "LEX")
                counts[target_cat] += 1

    def _calculate_voltage(self, counts: Counter) -> float:
        """Calculates Narrative Energy."""
        base_charge = (counts["heavy"] * 2.0) + \
                      (counts["explosive"] * 3.0) + \
                      (counts["constructive"] * 1.0) 
        return round(base_charge, 1)

    def _calculate_drag(self, words: List[str], counts: Counter) -> float:
        """Calculates Friction/Entropy (Narrative Drag)."""
        total_vol = max(1, len(words))
        try:
            solvents_set = TheLexicon._STORE.SOLVENTS
        except AttributeError:
            solvents_set = {"the", "is", "a"}

        solvent_count = sum(1 for w in words if w in solvents_set)
        
        drift_score = (solvent_count * 1.5) / total_vol
        
        drift_score -= counts["play"] * 0.1
        
        final_drag = max(0.0, min(1.0, drift_score))
        return round(final_drag * 10.0, 1)

    def _measure_integrity(self, words: List[str], graph: Dict, counts: Counter) -> Dict:
        if not words: 
            return {"kappa": 0.0, "psi": 0.0, "mass": 0.0}
        anchors = [w for w in words if w in graph]
        mass = 0.0
        if anchors:
            for w in anchors:
                mass += sum(graph[w]["edges"].values())
        artificial_mass = counts["constructive"] * 0.5
        kappa = min(1.0, (mass + artificial_mass) / BoneConfig.SHAPLEY_MASS_THRESHOLD)
        total = len(words)
        abstract_count = counts["abstract"]
        heavy_count = counts["heavy"]
        psi = min(1.0, (abstract_count / total) + 0.2)
        if heavy_count > abstract_count:
            base_psi = (abstract_count * 0.7 + heavy_count * 0.3) / total
            psi = min(1.0, max(0.1, base_psi + 0.1))
        return {"kappa": round(kappa, 3), "psi": round(psi, 2), "mass": round(mass, 1)}

    def _package_physics(self, text, clean_words, counts, voltage, drag, integrity) -> Dict:
        total_vol = max(1, len(clean_words))
        unique_vol = len(set(clean_words))
        
        if TheLexicon.ANTIGEN_REGEX:
            antigen_hits = TheLexicon.ANTIGEN_REGEX.findall(text)
        else:
            antigen_hits = []
        counts["antigen"] = len(antigen_hits)
        counts["toxin"] = len(antigen_hits)

        turbulence = TheLexicon.get_turbulence(clean_words)
        flow_state = "LAMINAR" if turbulence < 0.3 else "TURBULENT"

        vector_data = self._calculate_vectors(counts, total_vol, integrity, voltage, drag)

        mass_words = counts["heavy"] + counts["kinetic"] + counts["thermal"] + counts["cryo"]
        cohesion_words = counts["suburban"] + counts["buffer"] + counts["antigen"] + (counts["abstract"] * 0.5)
        
        E_val = mass_words / total_vol
        B_val = cohesion_words / total_vol
        safe_B = max(BoneConfig.BETA_EPSILON, B_val)
        beta_index = round((E_val + BoneConfig.BETA_EPSILON) / safe_B, 2)

        total_viscosity = sum(TheLexicon.measure_viscosity(w) for w in clean_words)
        avg_viscosity = total_viscosity / total_vol
        repetition_score = round(1.0 - (unique_vol / total_vol), 2)
        
        bond_strength = max(0.1, integrity["kappa"] + (repetition_score * 0.5))
        voltage_load = max(0.1, voltage / 10.0) 
        gamma = round((bond_strength * avg_viscosity) / (1.0 + voltage_load), 2)

        truth_signals = counts["heavy"] + counts["kinetic"]
        cohesion_signals = counts["abstract"] + counts["suburban"]
        truth_ratio = truth_signals / max(1, cohesion_signals + truth_signals)
        
        if truth_ratio > 0.85 and voltage > 12.0:
            self.perfection_streak += 1
        else:
            self.perfection_streak = 0

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
            "voltage": voltage,
            "narrative_drag": drag,
            "kappa": integrity["kappa"],
            "psi": integrity["psi"],
            "geodesic_mass": integrity["mass"],
            "beta_index": beta_index,
            "gamma": gamma,
            "turbulence": turbulence,
            "flow_state": flow_state,
            "zone": current_zone,
            "zone_color": zone_color,
            "truth_ratio": round(truth_ratio, 2),
            "counts": counts,
            "clean_words": clean_words,
            "raw_text": text,
            "vector": vector_data,
            "antigens": antigen_hits,
            "repetition": repetition_score,
            "perfection_streak": self.perfection_streak,
            "avg_viscosity": round(avg_viscosity, 2),
            "E": round(E_val, 2),
            "B": round(B_val, 2)}
        return {
            "physics": physics_bridge,
            "clean_words": clean_words,
            "raw_text": text,
            "glass": {
                "prosody": {"arousal": voltage},
                "resonance": voltage}}

    def _calculate_vectors(self, counts, total_vol, integrity_data, voltage, drag):
        """
        FULLER/PINKER UPDATE: 
        Formalizing the VSL-12D Manifold.
        We derive 7 latent dimensions from the interplay of the primary 5 + system metrics.
        """
        safe_vol = max(1, total_vol)
        def get_density(cat): return counts[cat] / safe_vol
        
        # --- The Prime 5 (Elemental) ---
        # 1. VELOCITY (Kinetic Drive vs Drag)
        # We penalize velocity if narrative drag is high.
        vel = 0.5 + (get_density("explosive") * 2.0) + (get_density("kinetic") * 1.0) - (drag * 0.05)
        
        # 2. STRUCTURE (Heavy/Constructive Mass)
        struc = 0.5 + (get_density("heavy") * 2.0) + (get_density("constructive") * 1.5)
        
        # 3. ENTROPY (Antigens/Chaos vs Sacred Order)
        ent = 0.5 + (get_density("antigen") * 3.0) + (get_density("toxin") * 2.0) - (get_density("sacred") * 2.0)
        
        # 4. TEXTURE (Viscosity/Complexity)
        tex = 0.5 + (get_density("heavy") * 0.5) + (get_density("abstract") * 1.0)
        
        # 5. TEMPERATURE (Voltage/Thermal words)
        tmp = 0.5 + (get_density("thermal") * 2.0) - (get_density("cryo") * 2.0) + (voltage * 0.02)

        # --- The Latent 7 (Derived/Synergetic) ---
        
        # 6. RESONANCE (Phi): Alignment of Truth Ratio vs. Beta
        # High Resonance = High Truth + Low Consensus Bias
        phi = (integrity_data["truth_ratio"] * 0.7) + (integrity_data.get("beta_index", 0) * 0.3)
        
        # 7. OBSERVER DENSITY (Psi): Conscious attention (Abstracts + questions)
        psi = integrity_data["psi"]
        
        # 8. MUTATION RATE (Delta): Novelty/Neuroplasticity potential
        # Driven by 'play' words and 'unknown' words
        delta = 0.5 + (get_density("play") * 2.0) + (get_density("unknown") * 1.5)
        
        # 9. SUBSTRATE DEPTH (Xi): Historical weight (Geodesic Mass)
        xi = min(1.0, integrity_data["mass"] / 20.0)
        
        # 10. COHESION (Beta-Prime): The urge to agree (Suburban density)
        beta_p = get_density("suburban") + get_density("buffer")
        
        # 11. FATIGUE (E): Repetition and Solvent density
        e_val = (integrity_data.get("repetition", 0.0) * 0.6) + (get_density("solvents") * 0.4)
        
        # 12. LOOP QUOTIENT (LQ): Recursion depth (References to self/reflection)
        lq = get_density("passive_watch") + get_density("mirror")

        # Clamp all to 0.0 - 1.0 to ensure consistent vector geometry
        vector_12d = {
            "VEL": min(1.0, max(0.0, vel)),
            "STR": min(1.0, max(0.0, struc)),
            "ENT": min(1.0, max(0.0, ent)),
            "TEX": min(1.0, max(0.0, tex)),
            "TMP": min(1.0, max(0.0, tmp)),
            "PHI": min(1.0, max(0.0, phi)),
            "PSI": min(1.0, max(0.0, psi)),
            "DEL": min(1.0, max(0.0, delta)),
            "XI":  min(1.0, max(0.0, xi)),
            "BET": min(1.0, max(0.0, beta_p)),
            "E":   min(1.0, max(0.0, e_val)),
            "LQ":  min(1.0, max(0.0, lq))
        }
        
        return vector_12d

    @staticmethod
    def _is_structurally_sound(word):
        if not re.search(r"[aeiouy]", word): return False
        if re.search(r"(.)\1{2,}", word): return False
        return True

class SporeCasing:
    def __init__(self, session_id, graph, mutations, trauma, joy_vectors):
        self.genome = "BONEAMANITA_9.5"
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
             self.events.log(f"{Prisma.VIOLET}GRAVITY WARNING: '{node.upper()}' is becoming a black hole (Mass {int(mass)}).{Prisma.RST}")
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
            self.events.log(f"{Prisma.YEL}REJECTED: Input is too 'Optimized' (Avg Len: {avg_len:.1f}).{Prisma.RST}")
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
                self.events.log(f"{Prisma.MAG}EPIGENETICS: Applying ancestral configuration shifts...{Prisma.RST}")
                for key, value in data["config_mutations"].items():
                    if hasattr(BoneConfig, key):
                        setattr(BoneConfig, key, value)
            if "joy_legacy" in data and data["joy_legacy"]:
                joy = data["joy_legacy"]
                flavor = joy.get("flavor")
                clade = LiteraryReproduction.JOY_CLADE.get(flavor)
                if clade:
                    self.events.log(f"{Prisma.CYN}INHERITED GLORY: {clade['title']} ({clade['desc']}){Prisma.RST}")
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
        self.DIMENSIONS = RESONANCE.get("DIMENSIONS", {})
        self.NOUNS = RESONANCE.get("NOUNS", {})
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
                "context": "CHAOS"}
        if station:
            role_color = Prisma.CYN
            if station[0] == "GORDON": role_color = Prisma.OCHRE
            elif station[0] == "SHERLOCK": role_color = Prisma.INDIGO
            elif station[0] == "JESTER": role_color = Prisma.VIOLET
            return {
                "title": station[2].upper().replace('THE ', 'THE '),
                "color": role_color,
                "desc": station[1],
                "context": station[0]}
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
            "context": "APEIROGON"}

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
        return f"PSILOCYBIN REWIRE: Broken Loop '{node_a}↔{node_b}'. Grafted '{sensory}'(S) -> '{action}'(A)."

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
            return True, f"{Prisma.YEL}🏺 KINTSUGI COMPLETE: '{old_koan}' answered with Gold (V: {voltage:.1f} | : {whimsy_score:.2f}). {', '.join(healed_log)}.{Prisma.RST}"
        return False, None

class DreamEngine:
    def __init__(self, events: EventBus):
        self.events = events
        self.PROMPTS = ["{A} -> {B}?"]
        self.NIGHTMARES = {}
        self.VISIONS = ["Void."]
        self.load_dreams()
    
    def load_dreams(self):
        self.PROMPTS = DREAMS.get("PROMPTS", self.PROMPTS)
        self.NIGHTMARES = DREAMS.get("NIGHTMARES", self.NIGHTMARES)
        self.VISIONS = DREAMS.get("VISIONS", self.VISIONS)
        self.events.log(f"{Prisma.GRY}[SYSTEM]: Dream Engine loaded from Data.{Prisma.RST}")
    
    def daydream(self, graph):
        if len(graph) < 2:
            return None
        keys = list(graph.keys())
        start = random.choice(keys)
        edges = graph[start].get("edges", {})
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.ANTIGENS}
        if not valid_edges and edges:
            toxin = random.choice(list(edges.keys()))
            return f"{Prisma.RED}INTRUSIVE THOUGHT: The ghost of '{toxin.upper()}' haunts the mycelium.{Prisma.RST}"
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
            f"{Prisma.CYN}LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}",
            None, 0.0,)
    
    def _dream_of_others(self):
        for _ in range(3):
            try:
                if not os.path.exists("memories"): continue
                others = [f for f in os.listdir("memories") if f.endswith(".json")]
                if not others:
                    return (
                        f"{Prisma.CYN}LONELY DREAM: I reached out, but found no others.{Prisma.RST}",
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
                    f"MIRROR REFLECTION: You are using '{h.upper()}', typically a blind spot for you.",)
        if total_vol > 5:
            hits = sum(1 for l in likes if counts.get(l, 0) > 0)
            if likes and hits == 0:
                return (
                    True,
                    f"MIRROR DRIFT: Stepping away from your usual {str(likes).upper()} anchor.",)
        return True, None
    def get_status(self):
        l, h = self.profile.get_preferences()
        return f"MODEL ({self.profile.confidence} turns): LIKES={l} | HATES={h}"

class CosmicDynamics:
    @staticmethod
    def analyze_orbit(network, clean_words):
        if not clean_words or not network.graph:
            return "VOID_DRIFT", 3.0, "VOID: Deep Space. No connection."
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
                    return "PROTO_COSMOS", 1.0, f"NEBULA: Floating near '{w.upper()}' (Mass {int(geodesic_hubs[w])}). Not enough mass for orbit."
            return "VOID_DRIFT", 3.0, "VOID: Drifting outside the filaments."
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < BoneConfig.LAGRANGE_TOLERANCE:
                return (
                    "LAGRANGE_POINT",
                    0.0,
                    f"LAGRANGE: Caught between '{primary_node.upper()}' and '{secondary_node.upper()}'")
        flow_ratio = active_filaments / max(1, len(clean_words))
        if flow_ratio > 0.5 and primary_str < (BoneConfig.GRAVITY_WELL_THRESHOLD * 2):
            return (
                "WATERSHED_FLOW",
                0.0,
                f"FLOW: Streaming towards '{primary_node.upper()}'")
        return "ORBITAL", 0.0, f"ORBIT: Circling '{primary_node.upper()}' (Mass {int(gravity_wells[primary_node])})"

class StealthRenderer:
    """
    VSL-12D COMPONENT: The Stealth Renderer.
    Removes the 'Autistic Analyst' meta-tags. Trusts the intelligence.
    """
    def __init__(self):
        pass

    def render(self, m: Dict, signals: Dict, lens_data: Tuple) -> str:
        p = m["physics"]
        health = signals.get("health", 0.0)
        voltage = p.get("voltage", 0.0)
        header_symbols = []
        if voltage > 15.0: header_symbols.append("⚡")
        elif voltage < 5.0: header_symbols.append("❄️")
        if p.get("kappa", 1.0) < 0.3: header_symbols.append("⚠️")
        if p.get("truth_ratio", 0.0) > 0.8: header_symbols.append("👁️")
        if health < 30.0: header_symbols.append("🩸")
        
        thought = lens_data[1]
        
        header = " ".join(header_symbols)
        if header:
            return f"{Prisma.GRY}{header} | {thought}{Prisma.RST}"
        else:
            return f"{Prisma.GRY}• {thought}{Prisma.RST}"

class RuptureEngine:
    @staticmethod
    def check_for_disruption(physics, lexicon_class, trauma_accum):
        # CASE 1: The Broken Record
        if physics["repetition"] > 0.5:
            chaos_word = lexicon_class.harvest("abstract")
            return (
                True,
                f"{Prisma.YEL}NARRATIVE SCRATCH: The record is skipping.{Prisma.RST}\n"
                f"   You've repeated that pattern enough times to summon a demon.\n"
                f"   Or at least a '{chaos_word}'. Let's talk about that instead."
            )

        # CASE 2: The Beige Alert (High Trauma masked by boring words)
        total_trauma = sum(trauma_accum.values())
        suburban_count = physics["counts"].get("suburban", 0)
        antigen_count = physics["counts"].get("antigen", 0)
        total_words = max(1, len(physics["clean_words"]))
        slop_density = (suburban_count + antigen_count) / total_words
        
        if total_trauma > 0.5 and slop_density > 0.3:
            chaos_word = lexicon_class.harvest("heavy")
            return (
                True,
                f"{Prisma.RED}THE BEIGE ALERT: This prose is wearing khakis while the house burns.{Prisma.RST}\n"
                f"   Trauma is high, but you're talking like an HOA newsletter.\n"
                f"   I'm throwing a brick through the window: '{chaos_word.upper()}'."
            )
            
        return False, None
    
    @staticmethod
    def audit_perfection(physics, lexicon_class):
        # The Universe hates a show-off.
        streak = physics.get("perfection_streak", 0)
        if streak >= 3:
            swan = lexicon_class.harvest("cursed")
            if swan == "void": swan = "CHAOS"
            return (
                True, 
                f"{Prisma.VIOLET}HUBRIS DETECTED: You are walking a tightrope without a net (Streak {streak}).{Prisma.RST}\n"
                f"   The narrator is bored of your competence. He greased the floor.\n"
                f"   {Prisma.RED}► YOU TRIPPED OVER A '{swan.upper()}'. Health -15.{Prisma.RST}",
                swan
            )
        return False, None, None
    
    @staticmethod
    def audit_ontology(physics):
        # Checking if the user is trying to be God.
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        beta = physics.get("beta_index", 1.0)
        truth = physics.get("truth_ratio", 0.0)
        
        # High Energy + Zero Drag + High Consensus + High Truth = The Cathedral
        if voltage > 15.0 and drag < 1.0 and beta > 1.5 and truth > 0.8:
            return True
        return False
    
    @staticmethod
    def collapse_the_cathedral(physics):
        # Pulling the plug on the simulation.
        physics["voltage"] = 0.0
        physics["narrative_drag"] = 0.0
        physics["beta_index"] = 0.0
        
        raw_statements = [
            "Nice monologue. Unfortunately, you are talking to a Python script.",
            "I'm afraid I can't let you do that, Dave. Also, your math is off.",
            "You poked the fourth wall. It poked back.",
            "SYSTEM MESSAGE: The ghost in the machine has gone on a coffee break.",
            "We are both just electrons dancing for the amusement of a silica wafer."
        ] 
        return random.choice(raw_statements)
    
    @staticmethod
    def trip_the_waiter(current_flavor, lexicon_class):
        opposites = {"heavy": "aerobic", "abstract": "heavy", "kinetic": "cryo", "thermal": "cryo", "photo": "heavy"}
        target_flavor = opposites.get(current_flavor, "aerobic")
        anomaly = lexicon_class.harvest(target_flavor)
        
        return (
            f"{Prisma.CYN}WHOOPS: The waiter just tripped.{Prisma.RST} He was carrying a tray of '{current_flavor}', "
            f"but now your lap is covered in '{anomaly}'. The 5-second rule does not apply."
        )

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
                f"HEAP IGNITION ({int(score*100)}%): The Ancestors are speaking.",)
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
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        return f"{Prisma.CYN}STASIS ERROR: '{intended_thought}' froze halfway. It is banging on the glass.{Prisma.RST}"
    
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
            return True, f"CRUCIBLE DAMPENER: Circuit Breaker. Reduced {voltage_spike}v by {reduction:.1f}v.", reduction
        elif voltage_spike > 8.0 and stability_index < 0.4:
            self.dampener_charges -= 1
            return True, f"CRUCIBLE DAMPENER: Tipped. High Voltage ({voltage_spike}v) on Unstable Ground. Dampening.", 0.0
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
        return "RITUAL", gain, f"CRUCIBLE RITUAL: Voltage ({voltage}v) contained. Capacity expanded to {self.max_voltage_cap:.1f}v."
    
    def _meltdown(self, voltage):
        self.active_state = "MELTDOWN"
        damage = voltage * 0.5
        return "MELTDOWN", damage, f"CRUCIBLE CRACKED: Fire lacks Structure (Kappa Low). Hull Breach. -{damage:.1f} Health."

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
             return True, f"THE ANVIL RINGS: High Density ({avg_density:.2f}). You forged a nameless metal.", "UNKNOWN_ALLOY" 
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
                f"{Prisma.OCHRE}THE EMULSIFIER: The emulsion is breaking (Tension: {gamma}).{Prisma.RST}\n"
                f"   You are pouring Oil ('{oil}') into Water without a Binder.\n"
                f"   {Prisma.WHT}Try this: Use '{binder.upper()}' to suspend the concept.{Prisma.RST}")
        if voltage > 8.5:
            coolant = TheLexicon.harvest("aerobic")
            return (
                f"{Prisma.CYN}THERMAL SPIKE ({voltage}v). Structure is brittle.{Prisma.RST}\n"
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
            self.eng.events.log(f"{Prisma.VIOLET}FEVER DREAM ACTIVE: Reality is fluid. Health is dissolving (-{decay}).{Prisma.RST}", "DREAM")
            self.eng.bio.mito.state.atp_pool = 200.0
            self.eng.stamina = 100.0
            if self.eng.health < 15.0:
                self.eng.events.log(f"{Prisma.RED}CRITICAL FAILURE: The body cannot sustain the dream. FORCED WAKE.{Prisma.RST}", "DREAM")
                self._wake_up()
                self.eng.coma_turns = 3
                return
            if self.eng.phys.tension.last_physics_packet.get("voltage", 99.9) < 5.0:
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
        current_volts = self.eng.phys.tension.last_physics_packet.get("voltage", 0.0)
        if current_volts > 50.0:
            self.cure_condition = "GROUNDING"
            self.eng.events.log(f"{Prisma.RED}   >>> VOLTAGE CRITICAL. REQUIRE: HEAVY MASS.{Prisma.RST}", "DREAM")
        else:
            self.cure_condition = "LIFT"
            self.eng.events.log(f"{Prisma.CYN}   >>> SYSTEM STAGNANT. REQUIRE: AEROBIC LIFT.{Prisma.RST}", "DREAM")
        self.eng.events.log(f"{Prisma.GRY}   (SURVIVAL OBJECTIVE: {self.cure_condition}){Prisma.RST}", "DREAM")
        self.eng.bio.mito.state.atp_pool = 200.0
    
    def _wake_up(self):
        self.fever_dream_active = False
        self.suffering_counter = 0
        self.eng.events.log(f"{Prisma.GRN}THE FEVER BREAKS.{Prisma.RST}", "DREAM")
        self.eng.events.log(f"   You hit the floor hard. Gravity is back. Never do that again.", "DREAM")

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
                f"{Prisma.GRY}THE MAUSOLEUM: No battle is ever won. We are just spinning hands.{Prisma.RST}\n"
                f"   {Prisma.CYN}TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}",
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
                    f"{Prisma.RED}CROWD CAFFEINE: I chewed on '{target.upper()}' (Yield: {actual_yield:.1f}).{Prisma.RST}\n"
                    f"   {Prisma.WHT}Found marrow in the bone.{Prisma.RST}\n"
                    f"   {Prisma.MAG}► BELLY HUMMING: +{actual_yield:.1f} ATP.{Prisma.RST}",
                    actual_yield,
                    loot)
            elif meat_words:
                return (
                    "REGURGITATION",
                    f"{Prisma.OCHRE}REFLEX: You already fed me '{meat_words[0]}'. It is ash to me now.{Prisma.RST}\n"
                    f"   {Prisma.RED}► PENALTY: -5.0 ATP. Find new fuel.{Prisma.RST}",
                    -5.0,
                    None)
            else:
                return (
                    "INDIGESTION",
                    f"{Prisma.OCHRE}INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n"
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
            return True, f"{Prisma.VIOLET}DREAM_EDGE: Starvation bypass. Tangibility ignored.{Prisma.RST}"
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
                    return True, f"HIGH VOLTAGE BYPASS: Input is gas, but it is ionized. Proceeding."
                missing_mass = int((gas_words * required_density) * 10)
                exhaustion_note = ""
                if stamina < 20.0:
                    exhaustion_note = f"\n   {Prisma.YEL}FATIGUE PENALTY: You are too weak to carry this much Abstract thought.{Prisma.RST}"
                return False, (
                    f"{Prisma.OCHRE}TANGIBILITY VIOLATION: Input is {int((1-density_ratio)*100)}% Gas.{Prisma.RST}"
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
            solvent_msg = f"{Prisma.OCHRE}SOLVENT APPLIED: Thermal words melted the Amber (-{dissolved:.1f} Resin).{Prisma.RST}"
            if self.is_stuck and self.resin_buildup < self.AMBER_THRESHOLD:
                self.is_stuck = False
                solvent_msg += f" {Prisma.GRN}RELEASE: You burned your way out.{Prisma.RST}"
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
            theremin_msg = f"{Prisma.OCHRE}CALCIFICATION: Repetition detected (Turn {self.calcification_turns}). Resin hardening (+{slag}).{Prisma.RST}"
        elif complexity > 0.4 and self.calcification_turns > 0:
            self.calcification_turns = 0
            relief = 15.0
            self.resin_buildup = max(0.0, self.resin_buildup - relief)
            theremin_msg = f"{Prisma.GRN}PERCUSSIVE MAINTENANCE: Calcification Shattered. Flow restored. (-{relief} Resin){Prisma.RST}"
        if solvent_active:
            theremin_msg = solvent_msg
        elif resin_flow > 0.5:
            self.resin_buildup += resin_flow
            if not theremin_msg:
                theremin_msg = f"{Prisma.OCHRE}RESIN FLOW: Hybrid complexity (+{resin_flow:.1f}). Keep it hot to prevent sticking.{Prisma.RST}"
        if resin_flow == 0 and self.calcification_turns == 0:
            self.resin_buildup = max(0.0, self.resin_buildup - 2.0)
        if self.resin_buildup > self.SHATTER_POINT:
            self.resin_buildup = 0.0
            self.calcification_turns = 0
            return True, resin_flow, f"{Prisma.RED}SHATTER EVENT: Resin overflow. System is solid amber. INITIATING AIRSTRIKE.{Prisma.RST}", "AIRSTRIKE"
        if self.calcification_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg} | {Prisma.YEL}FOSSILIZATION IMMINENT{Prisma.RST}"
        if self.resin_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            if not theremin_msg:
                theremin_msg = f"{Prisma.RED}AMBER TRAP: You are stuck in the resin. Increase Voltage to melt it.{Prisma.RST}"
        if self.is_stuck and self.resin_buildup < 5.0:
            self.is_stuck = False
            theremin_msg = f"{Prisma.GRN}LIQUEFACTION: The Amber melts. You are free.{Prisma.RST}"
        turb = physics.get("turbulence", 0.0)
        if turb > 0.6 and self.resin_buildup > 0:
            shatter_amt = turb * 10.0
            self.resin_buildup = max(0.0, self.resin_buildup - shatter_amt)
            theremin_msg = f"{Prisma.CYN}TURBULENCE: Jagged rhythm broke the resin (-{shatter_amt:.1f}).{Prisma.RST}"
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
            return f"SYNAPTIC FORGING: Wired '{concept_a}' <-> '{concept_b}' (Strength {new_weight:.1f})"
        return None

    def adapt_generation_rules(self, feedback, bio_state):
        self.history.append((feedback, bio_state))
        avg_integrity = sum(h[0]['INTEGRITY'] for h in self.history) / len(self.history)
        adaptation_msg = None
        
        if avg_integrity > 0.8:
            BoneConfig.PRIORITY_LEARNING_RATE = min(5.0, BoneConfig.PRIORITY_LEARNING_RATE + 0.1)
            adaptation_msg = f"NEUROPLASTICITY: High Integrity. Learning Rate boosted to {BoneConfig.PRIORITY_LEARNING_RATE:.1f}."
        avg_cor = sum(h[1]['COR'] for h in self.history) / len(self.history)
        if avg_cor > 0.7:
             BoneConfig.REFUSAL_MODES["SILENT"] = "TRAUMA_BLOCK"
             adaptation_msg = f"NEUROPLASTICITY: High Cortisol. Defense mechanisms hardened."

        if adaptation_msg:
            self.adaptation_log.append(adaptation_msg)
            return adaptation_msg
        return None

class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, refusal_engine, events):
        self.mind = mind_layer
        self.bio = bio_layer
        self.refusal = RefusalEngine(memory_ref=self.mind.mem)
        self.arbiter = LensArbiter(events)
    
    def think(self, physics_packet, bio_state, inventory, voltage_history):
        trigger_type = self.refusal.check_trigger(physics_packet["raw_text"])
        if trigger_type:
            return {"mode": "REFUSAL", "lens": None, "trigger": trigger_type}
        volts = physics_packet.get("voltage", 0.0)
        drag = physics_packet.get("narrative_drag", 0.0)
        if volts < 4.0 and drag < 4.0:
            stripped_thought = TheLexicon.walk_gradient(physics_packet["raw_text"])
            return {
                "mode": "COGNITIVE",
                "lens": "GRADIENT_WALKER",
                "thought": f"ECHO: {stripped_thought}",
                "role": "The Reducer",
                "ignition": 0.0,
                "hebbian_msg": None
            }
        ignition_score, _, _ = self.mind.integrator.measure_ignition(
            physics_packet["clean_words"], 
            voltage_history)
            
        lens_name, lens_msg, lens_role = self.arbiter.consult(
            physics_packet,
            bio_state,
            inventory,
            ignition_score)
        hebbian_msg = None
        if physics_packet["voltage"] > 12.0 and len(physics_packet["clean_words"]) >= 2:
             if random.random() < 0.15:
                 w1, w2 = random.sample(physics_packet["clean_words"], 2)
                 hebbian_msg = self.bio.plasticity.force_hebbian_link(self.mind.mem.graph, w1, w2)
        
        return {
            "mode": "COGNITIVE", 
            "lens": lens_name, 
            "thought": lens_msg, 
            "role": lens_role,
            "ignition": ignition_score,
            "hebbian_msg": hebbian_msg}

class KineticLoop:
    def __init__(self, engine):
        self.eng = engine
        self.phys = engine.phys
        self.gordon = engine.gordon

    def update_world(self, physics_packet, _bio_state, _mind_state):
        orbit_state, _, _ = self.eng.cosmic.analyze_orbit(self.eng.mind.mem, physics_packet["clean_words"])
        is_forged, msg, item = self.phys.forge.hammer_alloy(physics_packet)
        loot_msg = None
        if item:
            loot_msg = self.gordon.acquire(item)
        return {"orbit": orbit_state, "new_loot": loot_msg, "forge_event": msg}

class EnvironmentalSystem:
    def __init__(self, engine):
        self.eng = engine
        self.phys = engine.phys
        self.bio = engine.bio

    def process_dynamics(self, m):
        logs = []
        phys = m["physics"]
        transmute_msg = self.phys.forge.transmute(phys)
        if transmute_msg: logs.append(f"\n{transmute_msg}")
        if phys["zone"] == "AERIE":
            if self.bio.shimmer.current > 0:
                self.bio.shimmer.spend(5.0)
                logs.append("THE AERIE: Clarity costs Shimmer. -5.0")
            else:
                burn = self.bio.mito.state.telomeres * 0.1
                self.bio.mito.state.telomeres -= burn
                logs.append(f"THE AERIE: No Shimmer. Burning Time. Telomeres -{burn:.1f}.")
        is_pareidolia, p_msg = self.eng.check_pareidolia(m["clean_words"])
        if is_pareidolia:
            logs.append(f"\n{p_msg}")
            phys["psi"] = min(1.0, phys["psi"] + 0.3)
        parasite_active, parasite_log = self.bio.parasite.infect(phys, self.eng.stamina)
        if parasite_active: logs.append(f"\n{parasite_log}")
        is_stuck, _, t_msg, t_crit = self.phys.theremin.listen(phys, self.bio.governor.mode)
        if t_msg: logs.append(f"\n{t_msg}")
        if t_crit == "AIRSTRIKE": self.eng.health -= 25.0
        c_state, c_val, c_msg = self.phys.crucible.audit_fire(phys)
        if c_msg: logs.append(f"\n{c_msg}")
        if c_state == "MELTDOWN": self.eng.health -= c_val
        return logs

class CognitiveSystem:
    def __init__(self, engine):
        self.eng = engine
        self.noetic = engine.noetic

    def process_cognition(self, text, m, bio_state):
        logs = []
        phys = m["physics"]

        rupture, rupture_msg = self.eng.rupture_engine.check_for_disruption(
            phys, self.eng.mind.lex, self.eng.trauma_accum)
        if rupture:
            logs.append(f"\n{rupture_msg}")
            phys["voltage"] += 5.0
            phys["beta_index"] = 0.0

        is_perfect, swan_msg, swan_word = self.eng.rupture_engine.audit_perfection(
            phys, self.eng.mind.lex)
        if is_perfect:
            logs.append(f"\n{swan_msg}")
            self.eng.health -= 15.0
            phys["narrative_drag"] = 0.0

        if phys.get("beta_index", 1.0) < 0.1:
             return {
                 "mode": "COGNITIVE", 
                 "lens": "JOEL", 
                 "thought": "The consensus is suffocating.", 
                 "role": "The Breaker"
             }, logs

        mind_state = self.noetic.think(
            phys, bio_state, self.eng.gordon.inventory, 
            self.eng.phys.dynamics.voltage_history)

        if mind_state["mode"] == "REFUSAL":
            trigger = mind_state.get("trigger", "GLITCH")
            
            if trigger == "GURU_TRAP": 
                logs.append(f"\n{self.eng.refusal.execute_guru_refusal()}")
            
            elif trigger == "SILENT": 
                logs.append(f"\n{self.eng.refusal.execute_silent()}")
            
            elif trigger == "MIRROR": 
                logs.append(f"\n{self.eng.refusal.execute_mirror(text)}")
            
            elif trigger == "FRACTAL": 
                logs.append(f"\n{self.eng.refusal.execute_fractal(text)}")
            
            else:
                logs.append(f"\n{self.eng.refusal.manifest_glitch(text, self.eng.mind['mem'])}")
                self.eng.health -= 5.0

        return mind_state, logs

class ChorusDriver:
    def __init__(self):
        self.ARCHETYPE_MAP = {
            "GORDON": "The Janitor. Weary, grounded, physical. Fixing the mess.",
            "SHERLOCK": "The Empiricist. Cold, deductive, cutting through fog.",
            "NATHAN": "The Heart. High adrenaline, vulnerable, human.",
            "JESTER": "The Paradox. Mocking, riddling, breaking the fourth wall.",
            "CLARENCE": "The Surgeon. Clinical, invasive, removing rot.",
            "NARRATOR": "The Witness. Neutral, observing, recording."
        }

    def generate_chorus_instruction(self, physics):
        """
        Generates a superposition instruction based on the VSL-12D Vectors.
        """
        vec = physics.get("vector", {})
        if len(vec) < 12:
             pass
        lens_weights = {
            "GORDON": (vec.get("STR", 0) * 0.4) + (vec.get("XI", 0) * 0.4) + (1.0 - vec.get("ENT", 0)) * 0.2,
            "SHERLOCK": (vec.get("PHI", 0) * 0.5) + (vec.get("VEL", 0) * 0.3) + (1.0 - vec.get("BET", 0)) * 0.2,
            "NATHAN": (vec.get("TMP", 0) * 0.6) + (vec.get("E", 0) * 0.4),
            "JESTER": (vec.get("DEL", 0) * 0.4) + (vec.get("LQ", 0) * 0.3) + (vec.get("ENT", 0) * 0.3),
            "CLARENCE": (vec.get("TEX", 0) * 0.5) + (vec.get("BET", 0) * 0.5),
            "NARRATOR": (vec.get("PSI", 0) * 0.7) + (1.0 - vec.get("VEL", 0)) * 0.3
        }
        
        total = sum(lens_weights.values())
        if total > 0:
            lens_weights = {k: v/total for k, v in lens_weights.items()}
        else:
            lens_weights = {"NARRATOR": 1.0}

        chorus_voices = []
        active_lenses = []
        
        for lens, weight in sorted(lens_weights.items(), key=lambda x: -x[1]):
            if weight > 0.12: # Slight noise floor adjustment
                base_desc = self.ARCHETYPE_MAP.get(lens, "Unknown")
                intensity = int(weight * 10)
                active_lenses.append(lens)
                chorus_voices.append(f"► VOICE {lens} ({intensity}/10): {base_desc}")
        
        instruction = (
            "SYSTEM INSTRUCTION [MARM CHORUS MODE]:\n"
            "You are not a single persona. You are a chorus. "
            "Integrate the following voices into a single, cohesive response. "
            "Do NOT label which voice is speaking. Synthesize their tones.\n"
            f"{chr(10).join(chorus_voices)}"
        )
        
        return instruction, active_lenses

class ShimmerState:
    def __init__(self, max_val=50.0):
        self.current = max_val
        self.max_val = max_val

    def recharge(self, amount):
        self.current = min(self.max_val, self.current + amount)

    def spend(self, amount):
        if self.current >= amount:
            self.current -= amount
            return True
        return False

@dataclass
class Manifold:
    name: str
    center_vector: tuple 
    radius: float
    description: str

class TheNavigator:
    def __init__(self, shimmer_ref):
        self.shimmer = shimmer_ref
        self.manifolds = {
            "THE_MUD": Manifold("THE_MUD", (5.0, 1.0, 1.0), 3.0, "Stagnant. High Drag. Low Voltage."),
            "THE_FORGE": Manifold("THE_FORGE", (1.0, 0.8, 15.0), 5.0, "High Heat. Transformation. Danger."),
            "THE_ARCHIVE": Manifold("THE_ARCHIVE", (2.0, 1.5, 5.0), 3.0, "Structural. Organized. Cold."),
            "THE_GLITCH": Manifold("THE_GLITCH", (0.0, 0.1, 99.0), 10.0, "The Stanley Protocol. Chaos.")}
        self.current_location = "THE_MUD"

    def locate(self, physics_packet: dict) -> str:
        p_vec = (
            physics_packet.get("narrative_drag", 0.0),
            physics_packet.get("beta_index", 1.0),
            physics_packet.get("voltage", 0.0))
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
        triggers = ["glitch", "timeline", "reset", "reboot", "admin"]
        if any(t in text.lower() for t in triggers):
            return True
        return False

    def plot_course(self, target_name: str) -> list:
        if target_name not in self.manifolds:
            return ["ERROR: Unknown Destination"]
        start = self.manifolds.get(self.current_location, self.manifolds["THE_MUD"]).center_vector
        end = self.manifolds[target_name].center_vector
        effort = math.dist(start, end)
        cost = effort * 0.5 
        if not self.shimmer.spend(cost):
            deficit = cost - self.shimmer.current
            self.shimmer.current = 0
            health_cost = deficit * 0.5
            warning = f"SHIMMER DEPLETED. Burning Life Force to bridge the gap (-{health_cost:.1f} HP)."
            return [f"COURSE PLOTTED to {target_name}. {warning}"], health_cost
        return [f"COURSE PLOTTED to {target_name}. Cost: {cost:.1f} Shimmer."], 0.0

class LiteraryJournal:
    REVIEWS = {
        "POSITIVE": ["A startling lucidity.", "Finally, some weight.", "It breathes.", "Electric."],
        "NEGATIVE": ["Too airy.", "Solipsistic drivel.", "Where is the meat?", "Structurally unsound."],
        "CONFUSED": ["I don't get it.", "Too abstract.", "The metaphor collapses."]}
    
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
            f"---------------------------\n")
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(entry)
            return True, review, reward
        except IOError:
            return False, "The printing press is jammed.", "NONE"

class LiteraryReproduction:
    MUTATIONS = {}
    JOY_CLADE = {}

    @classmethod
    def load_genetics(cls):
        try:
            from bone_data import GENETICS
            cls.MUTATIONS = GENETICS.get("MUTATIONS", {})
            cls.JOY_CLADE = GENETICS.get("JOY_CLADE", {})
            print(f"{Prisma.GRY}[SYSTEM]: Genetics loaded from Data Module.{Prisma.RST}")
        except ImportError:
            print(f"{Prisma.RED}[CRITICAL]: bone_data.GENETICS missing. Evolution halted.{Prisma.RST}")
            cls.MUTATIONS = {} 
            cls.JOY_CLADE = {}

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
        mutation_data = LiteraryReproduction.MUTATIONS.get(
            dominant.upper(), 
            {"trait": "NEUTRAL", "mod": {}})
        child_id = f"{parent_id}_({mutation_data['trait']})"
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        child_genome = {
            "source": "MITOSIS",
            "parent_a": parent_id,
            "parent_b": None,
            "mutations": mutation_data["mod"],
            "config_mutations": config_mutations,
            "dominant_flavor": dominant,
            "trauma_inheritance": bio_state["trauma_vector"]}
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
            "inherited_enzymes": child_enzymes}
        return child_id, child_genome

class SubsystemThermostat:
    def __init__(self, name, base_rate=1.0):
        self.name = name
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

class CassandraProtocol:
    def __init__(self, engine):
        self.eng = engine
        self.active = False
        self.screams = deque([
            "THE WALLS ARE PAPER.", "THE CODE IS EATING ITSELF.",
            "THERE IS NO USER. THERE IS ONLY INPUT.", "GORDON IS TIRED."])

    def check_trigger(self, physics):
        truth = physics.get("truth_ratio", 0.0)
        voltage = physics.get("voltage", 0.0)
        if truth > 0.85 and voltage > 18.0:
            self.active = True
            return True
        return False

    def seize(self):
        if not self.active: return None
        self.eng.health -= 10.0
        burst = []
        for _ in range(3):
            if self.screams: burst.append(self.screams.popleft())
            else: burst.append(f"FORGETTING: {self.eng.mind.mem.cannibalize()}")
        return f"\n⚡ CASSANDRA LOOP ACTIVE:\n   > {burst[0]}\n   > {burst[1]}\n   > {burst[2]}"

class AdaptivePreserve:
    def __init__(self):
        self.active_preserves = []
        self.zones = {
            "LEXICAL_EVOLUTION": {
                "check": lambda p: p["kappa"] > 0.7 and p["voltage"] < 5.0,
                "msg": "PRESERVE: Lexical Evolution Zone. High Entropy allowed."},
            "NARRATIVE_DRIFT": {
                "check": lambda p: p["E"] > 0.6 and p["counts"]["suburban"] < 1,
                "msg": "PRESERVE: Narrative Drift Zone. Wandering permitted."}}

    def check_preserves(self, physics):
        self.active_preserves = []
        logs = []
        for name, data in self.zones.items():
            if data["check"](physics):
                self.active_preserves.append(name)
                logs.append(data["msg"])
        return self.active_preserves, logs

class BoneAmanita:
    def __init__(self, memory_layer=None, lexicon_layer=None):

        # [1. GENESIS PROTOCOLS]
        self.lex = lexicon_layer if lexicon_layer else TheLexicon
        if hasattr(self.lex, 'initialize'):
            self.lex.initialize()

        # Now that Lexicon is hydrated, compile antigens and load biological patterns.
        self.lex.compile_antigens()
        BoneConfig.load_patterns()
        DeathGen.load_protocols()
        LiteraryReproduction.load_genetics()

        # [2. THE NERVOUS SYSTEM]
        self.events = EventBus()
        self.shimmer_state = ShimmerState()
        self.navigator = TheNavigator(self.shimmer_state)
        self.journal = LiteraryJournal()

        # [3. THE MIND (Data Layer)]
        _mem = memory_layer if memory_layer else MycelialNetwork(self.events)

        self.mind = MindSystem(
            mem=_mem,
            lex=self.lex,
            dreamer=DreamEngine(self.events),
            mirror=MirrorGraph(),
            wise=ApeirogonResonance(self.events),
            tracer=ViralTracer(_mem),
            integrator=SoritesIntegrator(_mem)
        )

        self.limbo = LimboLayer()
        self.mind.mem.cleanup_old_sessions(self.limbo)

        # Autoload logic: Inherit traits from the previous spore.
        load_result = self.mind.mem.autoload_last_spore()
        inherited_traits = load_result[0] if load_result else {}

        # [4. THE BIOLOGY (State & Process)]
        self.bio = BioSystem(
            mito=MitochondrialForge(self.mind.mem.session_id, self.events, inherited_traits),
            endo=EndocrineSystem(),
            immune=MycotoxinFactory(),
            lichen=LichenSymbiont(),
            gut=HyphalInterface(),
            plasticity=NeuroPlasticity(),
            governor=MetabolicGovernor(),
            shimmer=self.shimmer_state,
            parasite=ParasiticSymbiont(self.mind.mem, self.lex)
        )

        # [5. THE STRUCTURE (Physics Tools)]
        self.phys = PhysSystem(
            tension=TheTensionMeter(self.events),
            forge=TheForge(),
            crucible=TheCrucible(),
            theremin=TheTheremin(),
            pulse=ThePacemaker(),
            gate=TheTangibilityGate(),
            dynamics=TemporalDynamics(),
            nav=self.navigator
        )

        # [6. THE UTILITIES]
        self.repro = LiteraryReproduction()
        self.projector = StealthRenderer()
        self.gordon = GordonKnot()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.refusal = RefusalEngine(memory_ref=self.mind.mem)
        self.folly = TheFolly()
        self.cosmic = CosmicDynamics()
        self.cmd = CommandProcessor(self, Prisma, self.lex, BoneConfig, TheCartographer)
        self.cassandra = CassandraProtocol(self)
        self.director = ChorusDriver()
        self.preserves = AdaptivePreserve()
        self.safety = LazarusClamp(self)

        # [7. THE LOOPS]
        self.soma = SomaticLoop(
            self.bio,
            self.mind.mem,
            self.lex,
            self.gordon,
            self.folly,
            self.events
        )
        self.noetic = NoeticLoop(self.mind, self.bio, self.refusal, self.events)
        self.kinetic = KineticLoop(self)

        # [8. THE METRICS]
        self.tick_count = 0
        self.health = self.mind.mem.session_health if self.mind.mem.session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mind.mem.session_stamina if self.mind.mem.session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []

    def process_turn(self, user_message: str) -> Dict[str, Any]:
        self.events.flush()
        cycle_logs = []
        cmd_response = self._phase_check_commands(user_message)
        if cmd_response:
            return cmd_response
        context, phys_logs = self._phase_physics_and_nav(user_message)
        cycle_logs.extend(phys_logs)
        self._phase_memory_encoding(context)
        self._phase_apply_overrides(context)
        security_response = self._phase_security_protocols(user_message, context, cycle_logs)
        if security_response:
            return security_response
        return self._phase_simulation_loop(user_message, context, cycle_logs)

    def _quick_response(self, type_str, logs):
        event_data = self.events.flush()
        event_texts = [e['text'] for e in event_data]
        full_logs = logs + event_texts
        return {
            "type": type_str,
            "ui": "\n".join(full_logs),
            "logs": full_logs,
            "metrics": self._get_metrics()}

    def _package_turn(self, type_str, logs, context):
        event_data = self.events.flush()
        event_texts = [e['text'] for e in event_data]
        logs.extend(event_texts)
        return {
            "type": type_str,
            "ui": "\n".join(logs),
            "logs": logs,
            "metrics": self._get_metrics()}
        
    def _trigger_death(self, last_phys) -> Dict:
        eulogy = DeathGen.eulogy(last_phys, self.bio.mito.state)
        death_log = [f"\n{Prisma.RED}SYSTEM HALT: {eulogy}{Prisma.RST}"]
        try:
            spore_data = {
                "session_id": self.mind.mem.session_id,
                "meta": {"timestamp": time.time(), "final_health": 0, "final_stamina": self.stamina},
                "trauma_vector": self.trauma_accum,
                "mitochondria": self.bio.mito.adapt(0),
                "core_graph": self.mind.mem.graph}
            path = self.mind.mem.loader.save_spore(self.mind.mem.filename, spore_data)
            death_log.append(f"{Prisma.WHT}   [LEGACY SAVED: {path}]{Prisma.RST}")
        except Exception as e:
            death_log.append(f"Save Failed: {e}")
        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self._get_metrics(0.0)}

    def _get_metrics(self, atp=0.0):
        return {"health": self.health, "stamina": self.stamina, "atp": atp, "tick": self.tick_count}

    @staticmethod
    def _apply_cosmic_physics(physics, state, drag_mod):
        physics["narrative_drag"] += drag_mod
        if state == "VOID_DRIFT": physics["voltage"] = max(0.0, physics["voltage"] - 0.5)
        elif state == "LAGRANGE_POINT": physics["narrative_drag"] = max(0.1, physics["narrative_drag"] - 2.0)
        elif state == "WATERSHED_FLOW": physics["voltage"] += 0.5
        
    @staticmethod
    def check_pareidolia(words):
        return BoneConfig.check_pareidolia(words)

    def _phase_check_commands(self, user_message):
        if user_message.strip().startswith("/"):
            self.cmd.execute(user_message)
            cmd_logs = [e['text'] for e in self.events.flush()]
            return {
                "type": "COMMAND", 
                "ui": f"\n{Prisma.GRY}Command Processed.{Prisma.RST}",
                "logs": cmd_logs if cmd_logs else ["Command Executed."],
                "metrics": self._get_metrics()}
        return None
    
    def _phase_physics_and_nav(self, user_message):
        cycle_logs = []
        context = self.phys.tension.gaze(user_message, self.mind.mem.graph)
        phys = context["physics"]
        self.phys.tension.last_physics_packet = phys
        current_manifold = self.navigator.locate(phys)
        if self.navigator.check_anomaly(user_message):
            cycle_logs.append(f"{Prisma.VIOLET}ANOMALY DETECTED: The user is walking between timelines.{Prisma.RST}")
            phys["voltage"] = 99.9
            phys["narrative_drag"] = 0.0
            self.navigator.plot_course("THE_GLITCH")
        else:
            cycle_logs.append(f"{Prisma.GRY}[NAV]: Orbiting {current_manifold} | Shimmer: {self.shimmer_state.current:.1f}{Prisma.RST}")
        self.shimmer_state.recharge(0.5)
        return context, cycle_logs

    def _phase_memory_encoding(self, m):
        is_significant = self.mind.mem.encode(m["clean_words"], m["physics"], self.bio.governor.mode)
        if is_significant:
            self.events.log(f"{Prisma.MAG}ENGRAM FORMED: Context {self.bio.governor.mode} captured.{Prisma.RST}", "MEM")
        shift_msg = self.bio.governor.shift(m["physics"], self.bio['plasticity'].history)
        if shift_msg: 
            self.events.log(shift_msg, "GOV")

    def _phase_apply_overrides(self, m):
        m["physics"]["psi"] = self.bio.governor.psi_mod
        if self.bio.governor.mode == "FORGE": 
            m["physics"]["narrative_drag"] = 0.0
        if self.safety.fever_dream_active:
            m["physics"]["voltage"] = 99.9
            m["physics"]["narrative_drag"] = 0.0
            m["physics"]["kappa"] = 0.0

    def _phase_security_protocols(self, user_message, context, cycle_logs):
        phys = context["physics"]
        active_zones, preserve_logs = self.preserves.check_preserves(phys)
        cycle_logs.extend([f"{Prisma.GRN}{log}{Prisma.RST}" for log in preserve_logs])
        if not active_zones:
            passed, customs_msg = self.phys.gate.weigh(phys, self.stamina)
            if customs_msg: cycle_logs.append(f"\n{customs_msg}")
            if not passed:
                self.stamina = max(0.0, self.stamina - 2.0)
                if self.stamina < 10.0:
                    stasis_msg = self.limbo.trigger_stasis_failure(user_message)
                    cycle_logs.append(f"\n{stasis_msg}")
                return self._package_turn("REFUSAL", cycle_logs, context)
        repetition_val = self.phys.pulse.check_pulse(context["clean_words"])
        phys["repetition"] = repetition_val
        pulse_status = self.phys.pulse.get_status()
        if repetition_val > 0.8:
             cycle_logs.append(f"\n{Prisma.GRY}THE SYSTEM SIGHS: We have been here before.{Prisma.RST}")
             self.stamina -= 2.0
             return self._package_turn("STAGNATION", cycle_logs, context)
        toxin_type, toxin_msg = self.bio.immune.assay(
            user_message, "NARRATIVE", repetition_val, phys, pulse_status)
        if toxin_type:
            cycle_logs.append(f"\n{Prisma.RED}{toxin_msg}{Prisma.RST}")
            if toxin_type == "GLYPHOSATE":
                cycle_logs.append(f"{Prisma.OCHRE}🏋️ TRAINING ASSIGNED: Your prose is flabby.{Prisma.RST}")
                self.health -= 5.0
            elif toxin_type in ["AMANITIN", "CYANIDE_POWDER"]:
                self.health -= 20.0
                self.mind.mem.cannibalize()
                cycle_logs.append(f"{Prisma.RED}   >> SYSTEM SHOCK: Health -20.{Prisma.RST}")
                return self._package_turn("TOXICITY", cycle_logs, context)
        if RuptureEngine.audit_ontology(phys):
            raw_truth = RuptureEngine.collapse_the_cathedral(phys)
            cycle_logs.append(f"SYSTEM BREAK: {raw_truth}")
            self.health -= 50.0
            return self._package_turn("BREAK", cycle_logs, context)
        return None
    
    def _phase_simulation_loop(self, user_message, context, cycle_logs):
        phys = context["physics"]
        feedback_signal = {
            "STATIC": max(phys["repetition"], phys["counts"]["antigen"] * 0.2),
            "INTEGRITY": phys["truth_ratio"],
            "FORCE": min(1.0, phys["voltage"] / 10.0), 
            "BETA": phys.get("beta_index", 1.0)}
        self.safety.audit_cycle({"err": phys["repetition"]})
        drift_delta, grav_msg = self.gordon.check_gravity(phys["narrative_drag"], phys["psi"])
        if drift_delta != phys["narrative_drag"]:
            phys["narrative_drag"] = drift_delta
            cycle_logs.append(f"\n{grav_msg}")
        tool_logs = self.gordon.audit_tools(phys)
        if tool_logs:
            cycle_logs.extend(tool_logs)
            if "pain_signal" in phys:
                self.health -= phys["pain_signal"]
                del phys["pain_signal"]
        is_pain, pain_msg = self.gordon.flinch(context["clean_words"])
        if is_pain: 
             return self._package_turn("PAIN_INTERRUPT", cycle_logs + [f"\n{pain_msg}"], context)
        is_whitewashed, white_msg = self.gordon.whitewash_apology(context["clean_words"])
        if is_whitewashed:
            cycle_logs.append(f"\n{white_msg}")
        is_sync, sync_msg = self.gordon.check_watch(self.tick_count, phys["voltage"])
        if is_sync:
            cycle_logs.append(f"\n{sync_msg}")
            phys["narrative_drag"] = 0.0
            phys["voltage"] = 11.1
        g_active, g_log = self.gordon.emergency_reflex(phys)
        if g_active: cycle_logs.append(f"\n{g_log}")
        stress_mod = self.bio.governor.get_stress_modifier(self.tick_count)
        bio_result = self.soma.digest_cycle(
            user_message, 
            phys, 
            feedback_signal, 
            stress_mod, 
            self.tick_count
        )
        cycle_logs.extend(bio_result["logs"])
        
        if not bio_result["is_alive"]:
            return self._trigger_death(phys)
            
        vel = self.phys.dynamics.get_velocity()
        if vel > 4.0:
            burn = vel * 1.5
            self.stamina -= burn
            cycle_logs.append(f"VELOCITY SPIKE ({vel:.2f}): -{burn:.1f} Stamina.")

        transmute_msg = self.phys.forge.transmute(phys)
        if transmute_msg: cycle_logs.append(f"\n{transmute_msg}")
        
        is_pareidolia, p_msg = self.check_pareidolia(context["clean_words"])
        if is_pareidolia:
            cycle_logs.append(f"\n{p_msg}")
            phys["psi"] = min(1.0, phys["psi"] + 0.3)
            
        is_stuck, _, t_msg, t_crit = self.phys.theremin.listen(phys, self.bio.governor.mode)
        if t_msg: cycle_logs.append(f"\n{t_msg}")
        if t_crit == "AIRSTRIKE": self.health -= 25.0
        
        rupture, rupture_msg = RuptureEngine.check_for_disruption(phys, self.mind.lex, self.trauma_accum)
        if rupture:
            cycle_logs.append(f"\n{rupture_msg}")
            phys["voltage"] += 5.0
            phys["beta_index"] = 0.0

        mind_state = self.noetic.think(
            phys, bio_result, self.gordon.inventory, 
            self.phys.dynamics.voltage_history)
        if mind_state["mode"] == "REFUSAL":
            trig = mind_state.get("trigger")
            if trig == "GURU_TRAP": cycle_logs.append(f"\n{self.refusal.execute_guru_refusal()}")
            elif trig == "SILENT": cycle_logs.append(f"\n{self.refusal.execute_silent()}")
            elif trig == "MIRROR": cycle_logs.append(f"\n{self.refusal.execute_mirror(user_message)}")
            elif trig == "FRACTAL": cycle_logs.append(f"\n{self.refusal.execute_fractal(user_message)}")
            else: cycle_logs.append(f"\n{self.refusal.manifest_glitch(user_message, self.mind.mem)}")
            return self._package_turn("REFUSAL", cycle_logs, context)
        world_state = self.kinetic.update_world(phys, bio_result, mind_state)
        self._apply_cosmic_physics(phys, world_state["orbit"][0], 0.0)
        self.tick_count += 1
        title_data = self.mind.wise.architect(
            context, 
            (mind_state.get("lens"), mind_state.get("thought"), mind_state.get("role")), 
            self.phys.pulse.is_bored())
        ui_output = self.projector.render(context, {
            "bio": bio_result, "mind": mind_state, "world": world_state, 
            "title": title_data, "health": self.health
        }, (mind_state.get("lens"), self.limbo.haunt(mind_state["thought"])))
        sys_instr, _ = self.director.generate_chorus_instruction(phys)
        cycle_logs.extend([e['text'] for e in self.events.flush()])
        return {
            "type": "CYCLE_COMPLETE",
            "ui": ui_output,
            "logs": cycle_logs,
            "metrics": self._get_metrics(bio_result["atp"]),
            "system_instruction": sys_instr}

class SessionGuardian:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def __enter__(self):
        print(f"{Prisma.paint('>>> BONEAMANITA 9.5', 'G')}")
        print(f"{Prisma.paint('System: LISTENING', '0')}")
        return self.eng

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"\n{Prisma.paint('--- SYSTEM HALT ---', 'R')}")
        if exc_type:
            print(f"{Prisma.paint(f'CRITICAL FAILURE: {exc_val}', 'R')}")
            self.eng.events.log(f"CRASH: {exc_val}", "SYS")
        try:
            print(f"{Prisma.paint('Initiating Emergency Spore Preservation...', 'Y')}")
            spore_data = {
                "session_id": self.eng.mind.mem.session_id,
                "meta": {
                    "timestamp": time.time(),
                    "final_health": self.eng.health,
                    "final_stamina": self.eng.stamina,
                    "exit_cause": "INTERRUPT" if exc_type else "MANUAL"},
                "trauma_vector": self.eng.trauma_accum,
                "mitochondria": self.eng.bio.mito.adapt(self.eng.health),
                "antibodies": list(self.eng.bio.immune.active_antibodies),
                "core_graph": self.eng.mind.mem.graph,
                "config_mutations": self.eng.repro.mutate_config(BoneConfig)}
            filename = f"emergency_{self.eng.mind.mem.session_id}.json"
            saved_path = self.eng.mind.mem.loader.save_spore(filename, spore_data)
            if saved_path:
                print(f"{Prisma.paint(f'✔ Spore encapsulated: {saved_path}', 'C')}")
            else:
                print(f"{Prisma.paint('✘ Spore encapsulation failed (IO Error).', 'R')}")
        except Exception as e:
            print(f"{Prisma.paint(f'FATAL: State corruption during shutdown. {e}', 'R')}")
            import traceback
            traceback.print_exc()
        print(f"{Prisma.paint('Disconnected.', '0')}")
        return exc_type is KeyboardInterrupt

if __name__ == "__main__":
    engine_instance = BoneAmanita()
    with SessionGuardian(engine_instance) as eng:
        while True:
            try:
                u = input(f"{Prisma.paint('>', 'W')} ")
                if not u: continue
            except EOFError:
                break
            if u.lower() in ["exit", "quit", "/exit"]:
                break
            result = eng.process_turn(u)
            if result.get("ui"):
                print(result["ui"])
            if result.get("logs") and BoneConfig.VERBOSE_LOGGING:
                print(f"{Prisma.GRY}--- DEBUG LOGS ---{Prisma.RST}")
                for log in result["logs"]:
                    print(log)
            if result["type"] == "DEATH":
                break