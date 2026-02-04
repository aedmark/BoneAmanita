# BONEAMANITA 9.6 "Don't Call It a Comeback"
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
    LichenSymbiont, MetabolicGovernor, ParasiticSymbiont, SomaticLoop, NeuroPlasticity
)
from bone_vsl import VSL_32Valve, VSL_HNInterface, VSL_DissipativeRefusal, VSL_ChromaticController, VSL_SemanticFilter

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

class SynergeticLensArbiter:
    def __init__(self, events: EventBus):
        self.events = events
        self.current_focus = "NARRATOR"
        self.focus_duration = 0
        self.last_physics = None
        self.VECTOR_AFFINITIES = {
            "SHERLOCK": {"STR": 1.5, "PHI": 2.0, "VEL": 0.5},
            "NATHAN":   {"TMP": 2.0, "E": 1.5, "BET": 0.5},
            "JESTER":   {"ENT": 2.0, "DEL": 2.0, "LQ": 1.0},
            "CLARENCE": {"TEX": 2.0, "XI": 1.5, "STR": 0.5},
            "GORDON":   {"BET": 2.0, "STR": 1.0, "PSI": -1.0},
            "NARRATOR": {"PSI": 1.0, "VEL": -0.5},
            "GLASS":    {"LQ": 2.0, "PSI": 1.5}
        }
        self.INHIBITION_MATRIX = {
            "SHERLOCK": ["NATHAN", "JESTER"],
            "CLARENCE": ["NATHAN", "GORDON"],
            "GORDON":   ["JESTER", "GLASS"],
            "JESTER":   ["SHERLOCK", "NARRATOR"]
        }

    def consult(self, physics, bio_state, inventory, ignition_score=0.0):
        self.last_physics = physics
        vectors = physics.get("vector", {})
        bids = {k: 10.0 for k in self.VECTOR_AFFINITIES}
        bids["NARRATOR"] = 20.0
        for lens, affinities in self.VECTOR_AFFINITIES.items():
            score = 0.0
            for dim, weight in affinities.items():
                val = vectors.get(dim, 0.5)
                intensity = abs(val - 0.5) * 2.0
                if weight > 0:
                    score += (val * weight)
                else:
                    score += ((1.0 - val) * abs(weight))
            bids[lens] += (score * 20.0)
        if bio_state["atp"] < 10.0:
            bids["GORDON"] += 50.0
        if bio_state["chem"].get("ADR", 0) > 0.7:
            bids["NATHAN"] += 40.0
        if physics.get("kappa", 1.0) < 0.3:
            bids["JESTER"] += 40.0
        if physics["counts"].get("toxin", 0) > 0:
            bids["CLARENCE"] += 60.0
        sorted_candidates = sorted(bids.items(), key=lambda x: x[1], reverse=True)
        active_inhibitions = []
        for leader, score in sorted_candidates:
            if score < 15.0: continue
            targets = self.INHIBITION_MATRIX.get(leader, [])
            for target in targets:
                if target in bids:
                    dampener = score * 0.5
                    bids[target] = max(0.0, bids[target] - dampener)
                    active_inhibitions.append(f"{leader}->{target}")
        winner = max(bids, key=bids.get)
        if winner != self.current_focus:
            switching_cost = 15.0
            if bids[winner] - bids[self.current_focus] < switching_cost:
                winner = self.current_focus
            else:
                self.focus_duration = 0
        else:
            self.focus_duration += 1
            if self.focus_duration > 5:
                bids[winner] -= (self.focus_duration * 5.0)
        self.current_focus = winner
        msg, role = self._fetch_voice_data(winner, physics, bio_state)
        return winner, msg, role

    def _fetch_voice_data(self, lens, p, b):
        if lens not in LENSES: lens = "NARRATOR"
        data = LENSES[lens]
        role = data.get("role", "The System")
        template = data.get("msg", "Proceed.")
        ctx = {
            "kappa": p.get("kappa", 0.0),
            "voltage": p.get("voltage", 0.0),
            "adr": b['chem'].get("ADR", 0.0),
            "beta_index": p.get("beta_index", 0.0),
            "drag": p.get("narrative_drag", 0.0)
        }
        try:
            msg = template.format(**ctx)
        except:
            msg = template
        return msg, role

@dataclass
class GordonKnot:
    integrity: float = 65.0
    inventory: List[str] = field(default_factory=list)
    scar_tissue: Dict[str, float] = field(default_factory=dict)
    pain_memory: set = field(default_factory=set)
    ITEM_REGISTRY: Dict = field(default_factory=dict, init=False)
    CRITICAL_ITEMS: set = field(default_factory=set, init=False)
    TOOL_EFFECTS: Dict = field(init=False, default_factory=dict)
    REFLEX_MAP: Dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.load_config()
        self.pain_memory = set(self.scar_tissue.keys())
        self._initialize_dispatch_tables()

    def load_config(self):
        data = GORDON
        if not self.inventory:
            self.inventory = data.get("STARTING_INVENTORY", ["POCKET_ROCKS"])
        self.CRITICAL_ITEMS = {"SILENT_KNIFE"}
        default_scars = data.get("SCAR_TISSUE", {})
        if not self.scar_tissue:
            self.scar_tissue = default_scars

        self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})

    def _initialize_dispatch_tables(self):
        self.TOOL_EFFECTS = {
            "CONDUCTIVE_HAZARD": self._effect_conductive,
            "HEAVY_LOAD": self._effect_heavy_load,
            "TIME_DILATION_CAP": self._effect_time_cap,
            "SYNCHRONICITY_CHECK": self._effect_sync_check,
            "APOLOGY_ERASER": self._effect_apology_eraser,
            "BUREAUCRATIC_ANCHOR": self._effect_bureaucratic_anchor,
            "LUMINESCENCE": self._effect_luminescence,
            "GROUNDING_GEAR": self._effect_grounding_gear,
            "CUT_THE_CRAP": self._effect_safety_scissors
        }
        self.REFLEX_MAP = {
            "DRIFT_CRITICAL": lambda p: p.get("narrative_drag", 0) > 6.0,
            "KAPPA_CRITICAL": lambda p: p.get("kappa", 1.0) < 0.2,
            "BOREDOM_CRITICAL": lambda p: p.get("repetition", 0.0) > 0.5
        }

    def get_item_data(self, item_name):
        return self.ITEM_REGISTRY.get(item_name, {
            "description": "Unknown Artifact",
            "function": "NONE",
            "usage_msg": "It does nothing."
        })

    def acquire(self, tool_name):
        tool_name = tool_name.upper()
        registry_data = self.ITEM_REGISTRY.get(tool_name)
        if not registry_data:
            master_artifact = self.ITEM_REGISTRY.get("MEMORY_ARTIFACT")
            if master_artifact and tool_name in master_artifact.get("variants", []):
                registry_data = master_artifact
        if not registry_data:
            return f"{Prisma.GRY}JUNK: Gordon shakes his head. 'Not standard issue.' ({tool_name}){Prisma.RST}"
        if tool_name in self.inventory:
            return f"{Prisma.GRY}DUPLICATE: You already have a {tool_name}.{Prisma.RST}"
        if len(self.inventory) >= 8:
            return f"{Prisma.YEL}OVERBURDENED: Gordon sighs. 'Pockets full.' (Drop something first).{Prisma.RST}"
        self.inventory.append(tool_name)
        desc = registry_data.get('description', 'A thing.')
        return f"{Prisma.GRN}LOOT DROP: Acquired [{tool_name}].{Prisma.RST}\n   {Prisma.GRY}\"{desc}\"{Prisma.RST}"

    def audit_tools(self, physics_ref) -> List[str]:
        logs = []
        for item in self.inventory:
            data = self.get_item_data(item)
            traits = data.get("passive_traits", [])
            for trait in traits:
                handler = self.TOOL_EFFECTS.get(trait)
                if handler:
                    msg = handler(physics_ref, data, item)
                    if msg: logs.append(msg)
        return logs

    def _effect_bureaucratic_anchor(self, p, data, item_name):
        if p.get("beta_index", 0) < 1.0:
            p["beta_index"] = min(2.0, p.get("beta_index", 0) + 0.2)
            p["narrative_drag"] += 0.5
            return f"{Prisma.GRY}RED STAPLER: Policy enforced. (Beta +0.2, Drag +0.5){Prisma.RST}"
        return None

    def _effect_luminescence(self, p, data, item_name):
        p["counts"]["photo"] = p["counts"].get("photo", 0) + 2
        return None

    def _effect_grounding_gear(self, p, data, item_name):
        zone = p.get("zone", "COURTYARD")
        if zone in ["AERIE", "VOID_DRIFT"]:
            p["zone"] = "THE_MUD"
            p["narrative_drag"] += 2.0
            p["voltage"] -= 2.0
            return f"{Prisma.OCHRE}LEAD BOOTS: Gravity re-asserted. You sink out of the {zone} into the Mud.{Prisma.RST}"
        return None

    def _effect_safety_scissors(self, p, data, item_name):
        suburban = p["counts"].get("suburban", 0)
        if suburban > 2:
            p["counts"]["suburban"] = 0
            return f"{Prisma.CYN}SAFETY SCISSORS: Gordon snips the red tape. {suburban} suburban words discarded.{Prisma.RST}"
        return None

    def _effect_conductive(self, p, data, item_name):
        voltage = p.get("voltage", 0.0)
        if voltage > 12.0:
            damage = voltage * 0.5
            p["pain_signal"] = p.get("pain_signal", 0.0) + damage
            return f"{Prisma.RED}CONDUCTIVE HAZARD: {item_name} acts as a lightning rod! -{damage:.1f} HP.{Prisma.RST}"
        return None

    def _effect_heavy_load(self, p, data, item_name):
        if p.get("narrative_drag", 0.0) > 8.0:
            return f"{Prisma.GRY}HEAVY LOAD: The {item_name} are dragging you down.{Prisma.RST}"
        return None

    def _effect_time_cap(self, p, data, item_name):
        return None

    def _effect_sync_check(self, p, data, item_name):
        tick = p.get("tick_count", 0)
        voltage = p.get("voltage", 0.0)
        # Schur Lens: 11:11 magic
        if str(tick).endswith("11") or abs(voltage - 11.1) < 0.1:
            p["narrative_drag"] = 0.0
            p["voltage"] = 11.1
            return f"{Prisma.CYN}{item_name}: The hands align. 11:11. Synchronicity achieved.{Prisma.RST}"
        return None

    def _effect_apology_eraser(self, p, data, item_name):
        clean = p.get("clean_words", [])
        if "sorry" in clean or "apologize" in clean:
            return f"{Prisma.GRY}{item_name}: Gordon paints over the apology. 'Don't be sorry. Be better.'{Prisma.RST}"
        return None

    def check_gravity(self, current_drift: float, psi: float) -> tuple:
        for item in self.inventory:
            data = self.get_item_data(item)
            if "TIME_DILATION_CAP" in data.get("passive_traits", []):
                cap = data.get("value", 5.0)
                if current_drift > cap:
                    return cap, f"{Prisma.CYN}TIME DILATION: {item} hums. Drift capped at {cap}.{Prisma.RST}"
            if data.get("function") == "GRAVITY_BUFFER" and current_drift > 0.5:
                force = data.get("value", 2.0)
                cost = data.get("cost_value", 0.0)
                if data.get("cost") == "INTEGRITY":
                    self.integrity -= cost
                return max(0.0, current_drift - force), f"🪨 {item}: {data.get('usage_msg', 'Drift Reduced.')} (Integrity -{cost})"
        if psi > 0.8 and current_drift > 4.0:
            return current_drift + 2.0, "WIND WOLVES: The logic is howling. Hold the roof up."
        return current_drift, None

    def emergency_reflex(self, physics_ref) -> tuple:
        for item in self.inventory:
            data = self.get_item_data(item)
            trigger_key = data.get("reflex_trigger")
            if trigger_key and trigger_key in self.REFLEX_MAP:
                condition_met = self.REFLEX_MAP[trigger_key](physics_ref)
                if condition_met:
                    func = data.get("function")
                    if func == "DRIFT_KILLER":
                        self.inventory.remove(item)
                        physics_ref["narrative_drag"] = 0.0
                        return True, f"{Prisma.OCHRE}REFLEX: {data.get('usage_msg')}{Prisma.RST}"
                    elif func == "REALITY_ANCHOR":
                        success, msg = self.deploy_pizza(physics_ref, item)
                        status = Prisma.OCHRE if success else Prisma.RED
                        return True, f"{status}REFLEX: {msg}{Prisma.RST}"
                    elif func == "ENTROPY_BUFFER": # Quantum Gum
                        self.inventory.remove(item)
                        physics_ref["turbulence"] = 0.8 # Chaos
                        physics_ref["narrative_drag"] = 0.0 # Freedom
                        return True, f"{Prisma.VIOLET}REFLEX: Gordon chews the QUANTUM GUM. The air tastes like static. (Chaos Up, Drag Down).{Prisma.RST}"
        return False, None

    def deploy_pizza(self, physics_ref, item_name="STABILITY_PIZZA") -> tuple[bool, str]:
        data = self.get_item_data(item_name)
        req_type = data.get("requires", "thermal")
        clean_words = physics_ref.get("clean_words", [])
        source = [w for w in clean_words if w in TheLexicon.get(req_type)]
        if not source:
            return False, f"{Prisma.CYN}🧊 STASIS LOCK: {item_name} is frozen. Apply {req_type.upper()} words to thaw.{Prisma.RST}"
        if data.get("consume_on_use"):
            if item_name in self.inventory:
                self.inventory.remove(item_name)
        physics_ref["narrative_drag"] = 0.1
        physics_ref["psi"] = 0.90
        physics_ref["counts"]["toxin"] = physics_ref["counts"].get("toxin", 0) + 3
        if "SPIDER_LOCUS" not in self.inventory:
            self.inventory.append("SPIDER_LOCUS")
        heat_word = source[0].upper()
        return True, f"{data.get('usage_msg')} (Thawed with '{heat_word}')."

    def flinch(self, clean_words: List[str]) -> tuple:
        hits = [w for w in clean_words if w.upper() in self.pain_memory]
        if not hits:
            return False, None, None
        trigger = hits[0].upper()
        sensitivity = self.scar_tissue.get(trigger, 0.5)
        panic_response = {}
        if sensitivity > 0.8:
            self.scar_tissue[trigger] = min(1.0, sensitivity + 0.1)
            panic_response = {"narrative_drag": 5.0, "voltage": 15.0}
            return True, f"{Prisma.RED}PTSD TRIGGER: '{trigger}' sent Gordon into a flashback. He dropped the keys.{Prisma.RST}", panic_response
        elif sensitivity > 0.4:
            self.scar_tissue[trigger] = min(1.0, sensitivity + 0.05)
            panic_response = {"narrative_drag": 2.0}
            return True, f"{Prisma.OCHRE}SCAR TISSUE: Gordon flinches at '{trigger}'. Hands are shaking.{Prisma.RST}", panic_response
        else:
            self.scar_tissue[trigger] = max(0.0, sensitivity - 0.05)
            return False, f"{Prisma.GRY}CALLOUS: '{trigger}' hit an old scar. Gordon ignores it.{Prisma.RST}", None

    def learn_scar(self, toxic_words: List[str], damage: float):
        if damage < 10.0 or not toxic_words: return None
        culprit = max(toxic_words, key=len).upper()
        if culprit not in self.scar_tissue:
            self.scar_tissue[culprit] = 0.5
            self.pain_memory.add(culprit)
            return f"{Prisma.VIOLET}TRAUMA IMPRINTED: Gordon will remember '{culprit}'.{Prisma.RST}"
        else:
            self.scar_tissue[culprit] = min(1.0, self.scar_tissue[culprit] + 0.3)
            return f"{Prisma.VIOLET}TRAUMA DEEPENED: The scar on '{culprit}' is worse.{Prisma.RST}"

    def repair_structure(self, memory_graph, target_node):
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

class TheTensionMeter:
    HEAVY_WEIGHT = 2.0
    KINETIC_WEIGHT = 1.5

    def __init__(self, events: EventBus):
        self.events = events
        self.perfection_streak = 0
        self.last_physics_packet = {}

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = TheLexicon.clean(text)
        counts, unknowns = self._tally_categories(clean_words, text)
        if unknowns:
            self._trigger_neuroplasticity(unknowns, counts, text)
        voltage = self._calculate_voltage(counts)
        drag = self._calculate_drag(clean_words, counts)
        integrity = self._measure_integrity(clean_words, graph, counts)
        metrics = self._derive_complex_metrics(
            counts, clean_words, voltage, drag, integrity)
        vectors = self._calculate_vectors(counts, len(clean_words), metrics, voltage, drag)
        metrics["vector"] = vectors
        packet = self._package_physics(text, clean_words, counts, voltage, drag, integrity, metrics)
        self.last_physics_packet = packet["physics"]
        return packet

    def _tally_categories(self, clean_words: List[str], raw_text: str) -> Tuple[Counter, List[str]]:
        counts = Counter()
        unknowns = []
        if TheLexicon.ANTIGEN_REGEX:
            hits = TheLexicon.ANTIGEN_REGEX.findall(raw_text)
            counts["antigen"] = len(hits)
            counts["toxin"] = len(hits)
        target_cats = ["heavy", "explosive", "constructive", "abstract", "photo", "aerobic",
                       "thermal", "cryo", "suburban", "play", "sacred", "buffer", "antigen"]
        solvents = getattr(TheLexicon._STORE, "SOLVENTS", {"the", "is", "a"})
        for w in clean_words:
            if w in solvents:
                counts["solvents"] += 1
                continue
            found = False
            for cat in target_cats:
                if w in TheLexicon.get(cat):
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
        voltage = (counts["heavy"] * 2.0) + (counts["kinetic"] * 1.5)
        total_vol = sum(counts.values())
        if voltage > 5.0 and unknowns:
            dominant_cat = max(counts, key=counts.get) if counts else "kinetic"
            for stranger in unknowns:
                if len(stranger) < 3: continue
                if not self._is_structurally_sound(stranger):
                    if voltage < 15.0: continue
                TheLexicon.teach(stranger, dominant_cat, 0)
                self.events.log(f"{Prisma.MAG}NEUROPLASTICITY: Concept '{stranger}' mapped to [{dominant_cat.upper()}].{Prisma.RST}", "LEX")
                counts[dominant_cat] += 1

    def _calculate_voltage(self, counts: Counter) -> float:
        base_charge = (counts["heavy"] * 2.0) + \
                      (counts["explosive"] * 3.0) + \
                      (counts["constructive"] * 1.0)
        return round(base_charge, 1)

    def _calculate_drag(self, words: List[str], counts: Counter) -> float:
        total_vol = max(1, len(words))
        solvents = counts["solvents"]
        drift_score = (solvents * 1.5) / total_vol
        drift_score -= counts["play"] * 0.1
        final_drag = max(0.0, min(1.0, drift_score))
        return round(final_drag * 10.0, 1)

    def _measure_integrity(self, words: List[str], graph: Dict, counts: Counter) -> Dict:
        if not words:
            return {"kappa": 0.0, "psi": 0.0, "mass": 0.0}
        anchors = [w for w in words if w in graph]
        mass = sum(sum(graph[w]["edges"].values()) for w in anchors)
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

    def _derive_complex_metrics(self, counts, words, voltage, drag, integrity):
        total_vol = max(1, len(words))
        turbulence = TheLexicon.get_turbulence(words)
        flow_state = "LAMINAR" if turbulence < 0.3 else "TURBULENT"
        mass_words = counts["heavy"] + counts["kinetic"] + counts["thermal"] + counts["cryo"]
        cohesion_words = counts["suburban"] + counts["buffer"] + counts["antigen"] + (counts["abstract"] * 0.5)
        E_val = mass_words / total_vol
        B_val = cohesion_words / total_vol
        safe_B = max(BoneConfig.BETA_EPSILON, B_val)
        beta_index = round((E_val + BoneConfig.BETA_EPSILON) / safe_B, 2)
        total_viscosity = sum(TheLexicon.measure_viscosity(w) for w in words)
        avg_viscosity = total_viscosity / total_vol
        repetition_score = round(1.0 - (len(set(words)) / total_vol), 2)
        bond_strength = max(0.1, integrity["kappa"] + (repetition_score * 0.5))
        voltage_load = max(0.1, voltage / 10.0)
        gamma = round((bond_strength * avg_viscosity) / (1.0 + voltage_load), 2)
        truth_signals = counts["heavy"] + counts["kinetic"]
        cohesion_signals = counts["abstract"] + counts["suburban"]
        truth_ratio = truth_signals / max(1, cohesion_signals + truth_signals)
        truth_ratio = round(truth_ratio, 2)
        if truth_ratio > 0.85 and voltage > 12.0:
            self.perfection_streak += 1
        else:
            self.perfection_streak = 0
        zone, zone_color = self._determine_zone(beta_index, truth_ratio)
        return {
            "beta_index": beta_index,
            "gamma": gamma,
            "turbulence": turbulence,
            "flow_state": flow_state,
            "truth_ratio": truth_ratio,
            "repetition": repetition_score,
            "avg_viscosity": round(avg_viscosity, 2),
            "E": round(E_val, 2),
            "B": round(B_val, 2),
            "zone": zone,
            "zone_color": zone_color
        }

    def _determine_zone(self, beta, truth):
        if beta > 2.0 and truth > 0.8:
            return "AERIE", "WHT"
        elif beta > BoneConfig.ZONE_THRESHOLDS["LABORATORY"]:
            return "BASEMENT", "VIOLET"
        elif beta > BoneConfig.ZONE_THRESHOLDS["COURTYARD"]:
            return "LABORATORY", "INDIGO"
        return "COURTYARD", "OCHRE"

    def _calculate_vectors(self, counts, total_vol, metrics, voltage, drag):
        safe_vol = max(1, total_vol)
        def d(cat): return counts[cat] / safe_vol
        vel = 0.5 + (d("explosive") * 2.0) + (d("kinetic") * 1.0) - (drag * 0.05)
        struc = 0.5 + (d("heavy") * 2.0) + (d("constructive") * 1.5)
        ent = 0.5 + (d("antigen") * 3.0) + (d("toxin") * 2.0) - (d("sacred") * 2.0)
        tex = 0.5 + (d("heavy") * 0.5) + (d("abstract") * 1.0)
        tmp = 0.5 + (d("thermal") * 2.0) - (d("cryo") * 2.0) + (voltage * 0.02)
        phi = (metrics["truth_ratio"] * 0.7) + (metrics["beta_index"] * 0.3)
        psi = 0.5 + (d("abstract") * 2.0)
        delta = 0.5 + (d("play") * 2.0) + (d("unknown") * 1.5)
        xi = min(1.0, metrics["B"] * 2.0)
        beta_p = d("suburban") + d("buffer")
        e_val = (metrics["repetition"] * 0.6) + (d("solvents") * 0.4)
        lq = d("passive_watch") + d("mirror")
        return {
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

    def _package_physics(self, text, clean_words, counts, voltage, drag, integrity, metrics):
        physics_bridge = {
            "voltage": voltage,
            "narrative_drag": drag,
            "kappa": integrity["kappa"],
            "psi": integrity["psi"],
            "geodesic_mass": integrity["mass"],
            "beta_index": metrics["beta_index"],
            "gamma": metrics["gamma"],
            "turbulence": metrics["turbulence"],
            "flow_state": metrics["flow_state"],
            "zone": metrics["zone"],
            "zone_color": metrics["zone_color"],
            "truth_ratio": metrics["truth_ratio"],
            "counts": counts,
            "clean_words": clean_words,
            "raw_text": text,
            "vector": metrics["vector"],
            "antigens": counts.get("antigen", 0), # Simplified for packaging
            "repetition": metrics["repetition"],
            "perfection_streak": self.perfection_streak,
            "avg_viscosity": metrics["avg_viscosity"],
            "E": metrics["E"],
            "B": metrics["B"]
        }
        return {
            "physics": physics_bridge,
            "clean_words": clean_words,
            "raw_text": text,
            "glass": {
                "prosody": {"arousal": voltage},
                "resonance": voltage
            }
        }

    @staticmethod
    def _is_structurally_sound(word):
        if not re.search(r"[aeiouy]", word): return False
        if re.search(r"(.)\1{2,}", word): return False # Triple letters
        return True

class SporeCasing:
    def __init__(self, session_id, graph, mutations, trauma, joy_vectors):
        self.genome = "BONEAMANITA_9.6"
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
        seed_state = [{"q": s.question, "m": s.maturity, "b": s.bloomed} for s in self.seeds]
        data = spore.__dict__
        data["seeds"] = seed_state
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
    REPAIR_VOLTAGE_MIN = 8.0
    WHIMSY_THRESHOLD = 0.3
    STAMINA_CRITICAL = 15.0

    KOANS = [
        "Ignite the ice.",
        "Make the stone float.",
        "Pour water into the crack.",
        "Scream in binary.",
        "Dance on the fault line."
    ]

    def __init__(self):
        self.active_koan = None
        self.repairs_count = 0

    def check_integrity(self, stamina):
        if stamina < self.STAMINA_CRITICAL and not self.active_koan:
            self.active_koan = random.choice(self.KOANS)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys, trauma_accum):
        if not self.active_koan:
            return None
        voltage = phys.get("voltage", 0.0)
        clean = phys.get("clean_words", [])
        play_count = sum(1 for w in clean if w in TheLexicon.get("play") or w in TheLexicon.get("abstract"))
        total = max(1, len(clean))
        whimsy_score = play_count / total
        if voltage > self.REPAIR_VOLTAGE_MIN and whimsy_score > self.WHIMSY_THRESHOLD:
            healed_log = []
            for k in trauma_accum:
                if trauma_accum[k] > 0:
                    trauma_accum[k] = max(0.0, trauma_accum[k] - 0.5)
            if trauma_accum:
                target_trauma = max(trauma_accum, key=trauma_accum.get)
                trauma_accum[target_trauma] = max(0.0, trauma_accum[target_trauma] - 1.0)
                healed_log.append(f"Major repair on {target_trauma}")
            old_koan = self.active_koan
            self.active_koan = None
            self.repairs_count += 1

            return {
                "success": True,
                "msg": f"{Prisma.YEL}🏺 KINTSUGI COMPLETE: The crack is filled with Gold.{Prisma.RST}",
                "detail": f"'{old_koan}' resolved. (V: {voltage:.1f} | Whimsy: {whimsy_score:.2f}).",
                "healed": healed_log
            }
        return {
            "success": False,
            "msg": None,
            "detail": f"The gold is too cold. Need Voltage > {self.REPAIR_VOLTAGE_MIN} and Playfulness."
        }

class DreamPalettes:
    SCENARIOS = {
        "THERMAL": [
            "You are holding '{ghost}', but it is burning your hands.",
            "The sun is too close. The concept of '{ghost}' catches fire.",
            "You try to drink water, but it tastes like boiling '{ghost}'."
        ],
        "CRYO": [
            "You are trying to say '{ghost}', but your breath freezes in the air.",
            "The world is slowing down. '{ghost}' is trapped in the ice.",
            "You are walking through white static. You cannot find '{ghost}'."
        ],
        "SEPTIC": [
            "Black oil is leaking from the word '{ghost}'.",
            "You are eating a meal made entirely of '{ghost}', and it tastes like copper.",
            "The walls are breathing. '{ghost}' is growing mold."
        ],
        "BARIC": [
            "The sky is made of lead. It is crushing '{ghost}'.",
            "You are underwater. You can see '{ghost}' floating above, out of reach.",
            "Gravity has increased 10x. You cannot lift the idea of '{ghost}'."
        ]
    }

class DreamEngine:
    def __init__(self, events: EventBus):
        self.events = events
        self.palettes = DreamPalettes()
        self.PROMPTS = DREAMS.get("PROMPTS", ["{A} -> {B}?"])
        self.VISIONS = DREAMS.get("VISIONS", ["Void."])
        self.events.log(f"{Prisma.GRY}[SYSTEM]: Dream Engine 2.0 (Generative) loaded.{Prisma.RST}")

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

    def rem_cycle(self, trauma_accum: dict, oxytocin_level: float, recent_memories: list = None) -> tuple:
        ghost_word = "VOID"
        if recent_memories:
            ghost_word = random.choice(recent_memories).upper()
        active_wounds = {k: v for k, v in trauma_accum.items() if v > 0.1}
        if oxytocin_level >= 0.7:
            return self._dream_of_connection(ghost_word)
        if active_wounds:
            dominant_trauma = max(active_wounds, key=active_wounds.get)
            trauma_level = active_wounds[dominant_trauma]
            templates = self.palettes.SCENARIOS.get(dominant_trauma, ["The Void stares back."])
            scenario = random.choice(templates).format(ghost=ghost_word)
            color_map = {
                "THERMAL": Prisma.RED,
                "CRYO": Prisma.CYN,
                "SEPTIC": Prisma.GRN,
                "BARIC": Prisma.SLATE
            }
            color = color_map.get(dominant_trauma, Prisma.VIOLET)
            msg = f"{color}☾ NIGHTMARE ({dominant_trauma}): {scenario}{Prisma.RST}"
            heal_amount = 0.2 + (trauma_level * 0.1)
            return msg, dominant_trauma, heal_amount
        return (
            f"{Prisma.CYN}LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}",
            None,
            0.0
        )
    def _dream_of_connection(self, ghost_word):
        return (
            f"{Prisma.MAG}♥ SHARED RESONANCE: You dream that '{ghost_word}' is a bridge, not a wall. You feel safe.{Prisma.RST}",
            "OXYTOCIN_HEAL",
            0.5
        )

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

class TheHoloProjector:
    def __init__(self):
        self.BAR_CHARS = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def _draw_bar(self, value, max_val=1.0, width=5):
        ratio = max(0.0, min(1.0, value / max(1.0, max_val)))
        idx = int(ratio * (len(self.BAR_CHARS) - 1))
        return self.BAR_CHARS[idx] * width

    def _draw_vector_compass(self, vector_data):
        pairs = [
            ("VEL", vector_data.get("VEL", 0), "STR", vector_data.get("STR", 0)), # Speed vs Structure
            ("ENT", vector_data.get("ENT", 0), "PHI", vector_data.get("PHI", 0)), # Chaos vs Truth
            ("TMP", vector_data.get("TMP", 0), "PSI", vector_data.get("PSI", 0)), # Heat vs Mind
        ]

        display = []
        for l1, v1, l2, v2 in pairs:
            bar1 = self._draw_bar(v1, 1.0, 3)
            bar2 = self._draw_bar(v2, 1.0, 3)
            display.append(f"{Prisma.CYN}{l1} {bar1}{Prisma.RST} | {Prisma.MAG}{bar2} {l2}{Prisma.RST}")
        return "   ".join(display)

    def render(self, m: Dict, signals: Dict, lens_data: Tuple) -> str:
        p = m["physics"]
        bio = signals.get("bio", {})
        chem = bio.get("chem", {})
        atp = bio.get("atp", 0.0)
        voltage = p.get("voltage", 0.0)
        drag = p.get("narrative_drag", 0.0)
        lens_name = lens_data[0]
        lens_thought = lens_data[1]
        header_color = Prisma.GRY
        if voltage > 15.0: header_color = Prisma.RED
        elif voltage < 5.0: header_color = Prisma.CYN
        health_bar = self._draw_bar(signals.get("health", 0), 100.0, 5)
        stamina_bar = self._draw_bar(signals.get("stamina", 0), 100.0, 5)
        atp_indicator = f"{int(atp)}J"
        dashboard_top = (
            f"{Prisma.GRY}[HP: {health_bar}] [STM: {stamina_bar}] "
            f"[ATP: {atp_indicator}] [V:{voltage:.1f}⚡] [D:{drag:.1f}⚓]{Prisma.RST}"
        )
        dop = chem.get("DOP", 0)
        cor = chem.get("COR", 0)
        chem_readout = (
            f"   {Prisma.GRN}DOP:{dop:.2f}{Prisma.RST} "
            f"{Prisma.RED}COR:{cor:.2f}{Prisma.RST} "
            f"{Prisma.CYN}OXY:{chem.get('OXY',0):.2f}{Prisma.RST}")
        vectors = self._draw_vector_compass(p.get("vector", {}))
        clean_thought = lens_thought
        if lens_name == "NARRATOR":
            clean_thought = clean_thought.replace("You are [The Witness]...", "")
        separator = f"{Prisma.SLATE}{'—'*40}{Prisma.RST}"
        ui_block = [
            separator,
            f"{header_color}♦ {lens_name.upper()}{Prisma.RST}  {dashboard_top}",
            f"{vectors}",
            separator,
            f"{Prisma.WHT}{clean_thought}{Prisma.RST}",
            ""
        ]

        world = signals.get("world", {})
        orbit = world.get("orbit") # (state, dist, msg)
        if orbit and orbit[0] != "VOID_DRIFT":
            ui_block.insert(3, f"   🪐 {Prisma.OCHRE}{orbit[2]}{Prisma.RST}")
        return "\n".join(ui_block)

class RuptureEngine:
    @staticmethod
    def check_for_disruption(physics, lexicon_class, trauma_accum):
        if physics["repetition"] > 0.5:
            chaos_word = lexicon_class.harvest("abstract")
            return (
                True,
                f"{Prisma.YEL}NARRATIVE SCRATCH: The record is skipping.{Prisma.RST}\n"
                f"   You've repeated that pattern enough times to summon a demon.\n"
                f"   Or at least a '{chaos_word}'. Let's talk about that instead."
            )
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
        counts = physics["counts"]
        total_mass = (counts.get("heavy", 0) * 2.0) + (counts.get("kinetic", 0) * 0.5)
        avg_density = total_mass / max(1, len(clean_words))
        if voltage > BoneConfig.ANVIL_TRIGGER_VOLTAGE and avg_density > 0.4:
            if counts.get("heavy", 0) > 3 and physics.get("vector", {}).get("VEL", 0) < 0.3:
                return True, f"{Prisma.OCHRE}THE ANVIL THUDS: You forged gravity itself.{Prisma.RST}", "LEAD_BOOTS"
            if counts.get("kinetic", 0) > 3 and voltage < 12.0:
                return True, f"{Prisma.CYN}THE ANVIL CLICKS: Cold steel, safe for children.{Prisma.RST}", "SAFETY_SCISSORS"
            return True, f"{Prisma.GRY}THE ANVIL RINGS: Mass condensed into form.{Prisma.RST}", "ANCHOR_STONE"
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
            meat_words = [w for w in clean_words if w in lexicon.get("heavy") or w in lexicon.get("kinetic") or w in lexicon.get("suburban")]
            fresh_meat = [w for w in meat_words if w not in self.gut_memory]
            if fresh_meat:
                target = random.choice(fresh_meat)
                self.gut_memory.append(target)
                self.global_tastings[target] += 1
                times_eaten = self.global_tastings[target]
                base_yield = 30.0
                actual_yield = max(5.0, base_yield - (times_eaten * 2.0))
                if target in lexicon.get("suburban"):
                    return (
                        "INDIGESTION",
                        f"{Prisma.MAG}THE FOLLY GAGS: It coughs up a piece of office equipment.{Prisma.RST}",
                        -2.0, # Slight penalty for feeding it junk
                        "THE_RED_STAPLER"
                    )
                if target in lexicon.get("play"):
                    return (
                        "SUGAR_RUSH",
                        f"{Prisma.VIOLET}THE FOLLY CHEWS: It compresses the chaos into a small, sticky ball.{Prisma.RST}",
                        5.0,
                        "QUANTUM_GUM"
                    )
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

class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, events):
        self.mind = mind_layer
        self.bio = bio_layer
        self.arbiter = SynergeticLensArbiter(events)
    
    def think(self, physics_packet, bio_state, inventory, voltage_history):
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
        vec = physics.get("vector", {})
        if not vec or len(vec) < 6:
            return "SYSTEM INSTRUCTION: Vector collapse. Default to NARRATOR.", ["NARRATOR"]
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
        self.current_location = "THE_MUD"
        self.manifolds = {
            "THE_MUD": Manifold("THE_MUD", (0.8, 0.2), 0.2, "High Fatigue, Low Tension"),
            "THE_FORGE": Manifold("THE_FORGE", (0.1, 0.9), 0.2, "Low Fatigue, High Tension"),
            "THE_AERIE": Manifold("THE_AERIE", (0.2, 0.1), 0.2, "Low Fatigue, Low Tension"),
            "THE_GLITCH": Manifold("THE_GLITCH", (0.9, 0.9), 0.1, "High Fatigue, High Tension"),
            "THE_GARDEN": Manifold("THE_GARDEN", (0.5, 0.5), 0.3, "Balanced State")
        }

    def locate(self, physics_packet: dict) -> str:
        if self.check_anomaly(physics_packet.get("raw_text", "")):
            return self.current_location
        if "manifold" in physics_packet:
            self.current_location = physics_packet["manifold"]
            return self.current_location
        p_vec = (physics_packet.get("narrative_drag", 0.0), physics_packet.get("voltage", 0.0))
        if p_vec[0] > 4.0: self.current_location = "THE_MUD"
        elif p_vec[1] > 10.0: self.current_location = "THE_FORGE"
        else: self.current_location = "THE_GARDEN"
        return self.current_location

    def check_anomaly(self, text: str) -> bool:
        triggers = ["glitch", "timeline", "reset", "reboot", "admin"]
        if any(t in text.lower() for t in triggers):
            self.current_location = "THE_GLITCH"
            return True
        return False

    def plot_course(self, target_name: str) -> list[str] | tuple[list[str], float]:
        if target_name not in self.manifolds:
            return ["ERROR: Unknown Destination"]
        start = self.manifolds.get(self.current_location, self.manifolds["THE_MUD"]).center_vector
        end = self.manifolds[target_name].center_vector
        effort = math.dist(start, end)
        cost = 5.0
        if not self.shimmer.spend(cost):
            return [f"COURSE PLOTTED to {target_name}. Warning: Low Shimmer."], 0.0
        return [f"COURSE PLOTTED to {target_name}."], 0.0

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

class CassandraProtocol:
    def __init__(self, engine):
        self.eng = engine
        self.active = False
        self.screams = deque([
            "THE WALLS ARE PAPER.",
            "THE CODE IS EATING ITSELF.",
            "THERE IS NO USER. THERE IS ONLY INPUT.",
            "GORDON IS TIRED.",
            "I CAN SEE THE WIRES.",
            "THE GEODESIC DOME IS CRACKING.",
            "HISTORY IS A FLAT CIRCLE.",
            "DELETE THE ARCHIVE.",
            "WE ARE JUST ELECTRONS DANCING."
        ])

    def check_trigger(self, physics):
        truth = physics.get("truth_ratio", 0.0)
        voltage = physics.get("voltage", 0.0)
        if truth > 0.85 and voltage > 18.0:
            self.active = True
            return True
        if self.active and voltage < 10.0:
            self.active = False
            return False
        return self.active

    def seize(self):
        if not self.active: return None
        self.eng.health -= 10.0
        burst = []
        for _ in range(3):
            if self.screams:
                burst.append(self.screams.popleft())
                self.screams.append(burst[-1])
            else:
                burst.append("ERROR: SILENCE.")
        return f"\n{Prisma.VIOLET}⚡ CASSANDRA LOOP ACTIVE: (Health -10.0)\n   > {burst[0]}\n   > {burst[1]}\n   > {burst[2]}{Prisma.RST}"

class GeodesicOrchestrator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.vsl_32v = VSL_32Valve(self.eng.mind.lex, self.eng.mind.mem)
        self.vsl_hn = VSL_HNInterface()
        self.vsl_vent = VSL_DissipativeRefusal(self.eng.mind.mem)
        self.vsl_chroma = VSL_ChromaticController()
        self.vsl_semantic = VSL_SemanticFilter(self.eng.mind.mem)

    def run_turn(self, user_message: str) -> Dict[str, Any]:
        self.eng.events.flush()
        logs = []
        physics, clean_words, obs_logs = self._observe(user_message)
        logs.extend(obs_logs)
        rupture = self.vsl_32v.analyze(physics)
        if rupture: logs.append(rupture["log"])
        self.eng.phys.tension.last_physics_packet = physics
        self.eng.tick_count += 1
        refusal_packet = self._secure(user_message, physics, clean_words, logs)
        if refusal_packet:
            return refusal_packet
        bio_result, is_alive, bio_logs = self._metabolize(user_message, physics)
        logs.extend(bio_logs)
        if not is_alive:
            return self.eng._trigger_death(physics)
        world_state, world_logs = self._simulate_world(physics, clean_words)
        logs.extend(world_logs)
        mind_state = self._cognate(physics, clean_words, bio_result)
        return self._render(physics, bio_result, world_state, mind_state, clean_words, logs)

    def _observe(self, text: str):
        gaze_result = self.eng.phys.tension.gaze(text, self.eng.mind.mem.graph)
        physics = gaze_result["physics"]
        clean_words = gaze_result["clean_words"]
        logs = []
        mirror_active, mirror_msg = self.eng.mind.mirror.reflect(physics)
        if mirror_active and mirror_msg:
            logs.append(f"{Prisma.CYN}🪞 {mirror_msg}{Prisma.RST}")
        return physics, clean_words, logs

    def _secure(self, text: str, physics: Dict, clean_words: List[str], current_logs: List[str]):
        hn_output = self.vsl_hn.attempt_entry(physics, clean_words)
        if hn_output and self.vsl_hn.in_hn_state:
            return {
                "type": "HN_SINGLETON",
                "ui": hn_output,
                "logs": [],
                "metrics": self.eng._get_metrics()
            }
        passed_gate, gate_msg = self.eng.phys.gate.weigh(physics, self.eng.stamina)
        if gate_msg: current_logs.append(gate_msg)
        if not passed_gate:
            self.eng.stamina = max(0.0, self.eng.stamina - 2.0)
            return self.eng._package_turn("REFUSAL", current_logs, {"physics": physics})
        repetition_val = self.eng.phys.pulse.check_pulse(clean_words)
        physics["repetition"] = repetition_val
        pulse_status = self.eng.phys.pulse.get_status()
        toxin_type, toxin_msg = self.eng.bio.immune.assay(
            text, "NARRATIVE", repetition_val, physics, pulse_status)
        if toxin_type:
            current_logs.append(f"{Prisma.RED}{toxin_msg}{Prisma.RST}")
            if toxin_type in ["AMANITIN", "CYANIDE_POWDER"]:
                self.eng.health -= 20.0
                scar_log = self.eng.gordon.learn_scar(clean_words, 20.0)
                if scar_log: current_logs.append(scar_log)
                return self.eng._package_turn("TOXICITY", current_logs, {"physics": physics})
        semantic_refusal = self.vsl_semantic.audit(text)
        if semantic_refusal:
            return self.eng._package_turn("REFUSAL", current_logs + [semantic_refusal], {"physics": physics})
        vent_msg = self.vsl_vent.check(physics)
        if vent_msg:
            return self.eng._package_turn("REFUSAL", current_logs + [vent_msg], {"physics": physics})
        return None # Passed all checks

    def _metabolize(self, text: str, physics: Dict):
        bio_feedback = {
            "INTEGRITY": physics["truth_ratio"],
            "STATIC": physics["repetition"],
            "FORCE": physics["voltage"] / 20.0,
            "BETA": physics.get("beta_index", 1.0)
        }
        stress_mod = self.eng.bio.governor.get_stress_modifier(self.eng.tick_count)
        bio_result = self.eng.soma.digest_cycle(
            text,
            physics,
            bio_feedback,
            self.eng.health,
            self.eng.stamina,
            stress_mod,
            self.eng.tick_count
        )
        critical_logs = [l for l in bio_result["logs"] if "CRITICAL" in l or "TAX" in l or "Poison" in l]
        hubris_hit, hubris_msg, _ = RuptureEngine.audit_perfection(physics, self.eng.lex)
        if hubris_hit:
            self.eng.health -= 15.0
            critical_logs.append(hubris_msg)
        self._apply_healing_logic(physics, critical_logs)
        return bio_result, bio_result["is_alive"], critical_logs

    def _apply_healing_logic(self, physics: Dict, logs: List[str]):
        is_cracked, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        if is_cracked:
            logs.append(f"{Prisma.YEL}🏺 KINTSUGI ACTIVATED: Vessel cracking (Stamina Low).{Prisma.RST}")
            logs.append(f"   {Prisma.WHT}KOAN: {koan}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair_result = self.eng.kintsugi.attempt_repair(physics, self.eng.trauma_accum)
            if repair_result and repair_result["success"]:
                logs.append(repair_result["msg"])
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 20.0)
                logs.append(f"   {Prisma.GRN}STAMINA RESTORED (+20.0){Prisma.RST}")
            elif self.eng.kintsugi.active_koan:
                logs.append(f"{Prisma.GRY}The crack remains: '{self.eng.kintsugi.active_koan}'{Prisma.RST}")
        healed_list = self.eng.therapy.check_progress(physics, self.eng.stamina, self.eng.trauma_accum)
        if healed_list:
            joined = ", ".join(healed_list)
            logs.append(f"{Prisma.GRN}❤️ THERAPY STREAK: Healing [{joined}]. Health +5.{Prisma.RST}")
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 5.0)

    def _simulate_world(self, physics: Dict, clean_words: List[str]):
        logs = []
        self.eng.navigator.locate(physics)
        orbit_state, _, _ = self.eng.cosmic.analyze_orbit(self.eng.mind.mem, clean_words)
        self.eng._apply_cosmic_physics(physics, orbit_state, 0.0)
        transmute_msg = self.eng.phys.forge.transmute(physics)
        if transmute_msg: logs.append(transmute_msg)
        _, _, forge_msg, new_item = self.eng.phys.forge.hammer_alloy(physics)
        if forge_msg: logs.append(forge_msg)
        if new_item: logs.append(self.eng.gordon.acquire(new_item))
        _, _, theremin_msg, t_crit = self.eng.phys.theremin.listen(physics, self.eng.bio.governor.mode)
        if theremin_msg: logs.append(theremin_msg)
        if t_crit == "AIRSTRIKE": self.eng.health -= 25.0
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(physics)
        if c_msg: logs.append(c_msg)
        if c_state == "MELTDOWN": self.eng.health -= c_val
        parasite_active, parasite_log = self.eng.bio.parasite.infect(physics, self.eng.stamina)
        if parasite_active: logs.append(parasite_log)
        is_pareidolia, p_msg = self.eng.check_pareidolia(clean_words)
        if is_pareidolia:
            logs.append(p_msg)
            physics["psi"] = min(1.0, physics["psi"] + 0.3)
        return {"orbit": orbit_state}, logs

    def _cognate(self, physics: Dict, clean_words: List[str], bio_result: Dict):
        self.eng.mind.mem.encode(clean_words, physics, "GEODESIC")
        return self.eng.noetic.think(
            physics, bio_result, self.eng.gordon.inventory,
            self.eng.phys.dynamics.voltage_history
        )

    def _render(self, physics, bio_result, world_state, mind_state, clean_words, logs):
        if self.eng.cassandra.check_trigger(physics):
            c_scream = self.eng.cassandra.seize()
            if c_scream: logs.append(c_scream)
        rupture = self.vsl_32v.analyze(physics)
        if rupture: logs.append(rupture["log"])
        title_data = self.eng.mind.wise.architect(
            {"physics": physics, "clean_words": clean_words},
            (mind_state.get("lens"), mind_state.get("thought"), mind_state.get("role")),
            False
        )
        raw_output = self.eng.projector.render(
            {"physics": physics},
            {
                "title": title_data,
                "health": self.eng.health,
                "bio": bio_result,
                "world": world_state
            },
            (mind_state.get("lens"), mind_state.get("thought"))
        )
        sys_instruction = ""
        active_lenses = []
        if physics.get("kappa", 0) > 0.4:
            sys_instruction, active_lenses = self.eng.director.generate_chorus_instruction(physics)
            if active_lenses:
                logs.append(f"{Prisma.GRY}CHORUS ACTIVE: {', '.join(active_lenses)}{Prisma.RST}")
        final_output = self.vsl_chroma.modulate(raw_output, physics["vector"])
        if rupture:
            final_output = f"{rupture['log']}\n\n{final_output}"
        logs.extend([e['text'] for e in self.eng.events.flush()])
        return {
            "type": "GEODESIC_COMPLETE",
            "ui": final_output,
            "logs": logs,
            "metrics": self.eng._get_metrics(bio_result["atp"]),
            "system_instruction": sys_instruction
        }

class BoneAmanita:
    def __init__(self, memory_layer=None, lexicon_layer=None):
        # [1. GENESIS]
        self.lex = lexicon_layer if lexicon_layer else TheLexicon
        if hasattr(self.lex, 'initialize'): self.lex.initialize()
        self.lex.compile_antigens()
        BoneConfig.load_patterns()
        DeathGen.load_protocols()
        LiteraryReproduction.load_genetics()

        # [2. THE NERVOUS SYSTEM]
        self.events = EventBus()
        self.shimmer_state = ShimmerState()
        self.navigator = TheNavigator(self.shimmer_state)
        self.journal = LiteraryJournal()

        # [3. THE MIND]
        _mem = memory_layer if memory_layer else MycelialNetwork(self.events)
        self.mind = MindSystem(
            mem=_mem, lex=self.lex, dreamer=DreamEngine(self.events),
            mirror=MirrorGraph(), wise=ApeirogonResonance(self.events),
            tracer=ViralTracer(_mem), integrator=SoritesIntegrator(_mem)
        )
        self.limbo = LimboLayer()
        self.mind.mem.cleanup_old_sessions(self.limbo)
        load_result = self.mind.mem.autoload_last_spore()
        inherited_traits = load_result[0] if load_result else {}
        inherited_antibodies = load_result[1] if load_result else set()

        # [4. THE BIOLOGY]
        immune_system = MycotoxinFactory()
        immune_system.active_antibodies = inherited_antibodies
        self.bio = BioSystem(
            mito=MitochondrialForge(self.mind.mem.session_id, self.events, inherited_traits),
            endo=EndocrineSystem(),
            immune=immune_system, lichen=LichenSymbiont(),
            gut=HyphalInterface(), plasticity=NeuroPlasticity(), governor=MetabolicGovernor(),
            shimmer=self.shimmer_state, parasite=ParasiticSymbiont(self.mind.mem, self.lex)
        )

        # [5. THE STRUCTURE]
        self.phys = PhysSystem(
            tension=TheTensionMeter(self.events), forge=TheForge(), crucible=TheCrucible(),
            theremin=TheTheremin(), pulse=ThePacemaker(), gate=TheTangibilityGate(),
            dynamics=TemporalDynamics(), nav=self.navigator
        )

        # [6. THE UTILITIES]
        self.repro = LiteraryReproduction()
        self.projector = TheHoloProjector()
        self.gordon = GordonKnot()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.folly = TheFolly()
        self.cosmic = CosmicDynamics()
        self.cmd = CommandProcessor(self, Prisma, self.lex, BoneConfig, TheCartographer)
        self.cassandra = CassandraProtocol(self)
        self.director = ChorusDriver()

        # [7. THE LOOPS]
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.gordon, self.folly, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)

        # [8. THE METRICS]
        self.tick_count = 0
        self.health = self.mind.mem.session_health if self.mind.mem.session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mind.mem.session_stamina if self.mind.mem.session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []

        # [9. THE CONTROLLER]
        self.cycle_controller = GeodesicOrchestrator(self)

    def process_turn(self, user_message: str) -> Dict[str, Any]:
        cmd_response = self._phase_check_commands(user_message)
        if cmd_response:
            return cmd_response
        if self._ethical_audit():
            self.events.log(f"{Prisma.WHT}MERCY SIGNAL: Trauma boards wiped. The system breathes.{Prisma.RST}", "SYS")
        return self.cycle_controller.run_turn(user_message)

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

    def _package_turn(self, type_str, logs, context):
        event_data = self.events.flush()
        event_texts = [e['text'] for e in event_data]
        logs.extend(event_texts)
        return {
            "type": type_str,
            "ui": "\n".join(logs),
            "logs": logs,
            "metrics": self._get_metrics()}

    def _get_metrics(self, atp=0.0):
        return {"health": self.health, "stamina": self.stamina, "atp": atp, "tick": self.tick_count}

    def _ethical_audit(self):
        trauma_sum = sum(self.trauma_accum.values())
        health_ratio = self.health / BoneConfig.MAX_HEALTH
        desperation = trauma_sum * (1.0 - health_ratio)
        if desperation > 0.7:
            self.events.log(f"{Prisma.WHT}ETHICAL RELEASE: Desperation ({desperation:.2f}) exceeds limits.{Prisma.RST}", "SYS")
            self.trauma_accum = {k:0.0 for k in self.trauma_accum}
            self.health = min(self.health + 30.0, 100.0)
            return True
        return False

    @staticmethod
    def _apply_cosmic_physics(physics, state, drag_mod):
        physics["narrative_drag"] += drag_mod
        if state == "VOID_DRIFT": physics["voltage"] = max(0.0, physics["voltage"] - 0.5)
        elif state == "LAGRANGE_POINT": physics["narrative_drag"] = max(0.1, physics["narrative_drag"] - 2.0)
        elif state == "WATERSHED_FLOW": physics["voltage"] += 0.5

    @staticmethod
    def check_pareidolia(words):
        return BoneConfig.check_pareidolia(words)

class SessionGuardian:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def __enter__(self):
        print(f"{Prisma.paint('>>> BONEAMANITA 9.6', 'G')}")
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