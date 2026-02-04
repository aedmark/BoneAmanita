# BONEAMANITA 9.7.9 - "The Circulation Update"
# Architects: SLASH, JADE, Taylor & Edmark
# "We have successfully married sacred geometry with profound bureaucracy."

import json, os, random, re, time, math, copy, traceback
from collections import Counter, deque
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from bone_commands import CommandProcessor
from bone_shared import SporeInterface, LocalFileSporeLoader, SporeCasing, LiteraryReproduction, TheAlmanac, ZoneInertia, CycleContext, EventBus, TheLexicon, Prisma, BoneConfig, DeathGen, TheCartographer, TheTinkerer
from bone_data import LENSES, GORDON, DREAMS, RESONANCE, NARRATIVE_DATA
from bone_biology import (
    MitochondrialForge, EndocrineSystem, HyphalInterface, MycotoxinFactory,
    LichenSymbiont, MetabolicGovernor, MycelialNetwork, ParasiticSymbiont, SomaticLoop, NeuroPlasticity, BioSystem, ShimmerState
)
from bone_vsl import TheBouncer, PhysicsResolver, StrunkWhiteProtocol, VSL_32Valve, VSL_HNInterface, VSL_DissipativeRefusal, VSL_ChromaticController, VSL_SemanticFilter

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
class PhysSystem:
    tension: 'TheTensionMeter'
    forge: 'TheForge'
    crucible: 'TheCrucible'
    theremin: 'TheTheremin'
    pulse: 'ThePacemaker'
    gate: 'TheTangibilityGate'
    dynamics: 'TemporalDynamics'
    nav: 'TheNavigator'

class EnneagramDriver:
    def __init__(self, events_ref):
        self.events = events_ref
        from bone_data import ENNEAGRAM_DATA
        self.MAP = ENNEAGRAM_DATA.get("TYPE_MAP", {})
        self.GEO = ENNEAGRAM_DATA.get("GEOMETRY", {})
        self.PROXY = ENNEAGRAM_DATA.get("PROXY_MAP", {})
        self.TEXT = ENNEAGRAM_DATA.get("SHIFTS", {"DISINTEGRATION": [], "INTEGRATION": []})
        self.REVERSE_MAP = {v: k for k, v in self.MAP.items()}
        self.REVERSE_MAP.update(self.PROXY)
        self._validate_enneagram_data()
        self.stability_buffer = 1.0
        self.last_pressure = {"stress": 0.0, "growth": 0.0}

    def _validate_enneagram_data(self):
        valid_nodes = set(self.GEO.keys())
        sanitized_geo = {}
        for type_num, paths in self.GEO.items():
            clean_paths = {}
            if "STRESS" in paths:
                target = paths["STRESS"]
                if target in valid_nodes:
                    clean_paths["STRESS"] = target
                else:
                    self.events.log(f"{Prisma.YEL}[ENNEAGRAM]: Pruned broken stress link {type_num}->{target}{Prisma.RST}", "SYS")
            if "GROWTH" in paths:
                target = paths["GROWTH"]
                if target in valid_nodes:
                    clean_paths["GROWTH"] = target
                else:
                    self.events.log(f"{Prisma.YEL}[ENNEAGRAM]: Pruned broken growth link {type_num}->{target}{Prisma.RST}", "SYS")
            sanitized_geo[type_num] = clean_paths
        self.GEO = sanitized_geo

    def _get_lens_name(self, type_num):
        return self.REVERSE_MAP.get(type_num, "NARRATOR")

    def diagnose_and_shift(self, current_lens, bio_system, physics):
        if current_lens not in self.MAP:
            return current_lens, "NEUTRAL"
        ros = bio_system.mito.state.ros_buildup
        atp = bio_system.mito.state.atp_pool
        truth = physics.get("truth_ratio", 0.5)
        drag = physics.get("narrative_drag", 0.0)
        stress_pressure = (ros / 40.0) + (drag / 5.0)
        growth_pressure = (atp / 80.0) + (truth * 1.5)
        self.last_pressure = {"stress": stress_pressure, "growth": growth_pressure}
        current_type = self.MAP[current_lens]
        path = self.GEO.get(current_type)
        if not path:
            return current_lens, "STATIC"
        target_lens = current_lens
        new_state = "STABLE"
        self.stability_buffer = min(1.0, self.stability_buffer + 0.05)
        if stress_pressure > 1.5:
            self.stability_buffer -= 0.15
            if self.stability_buffer <= 0.0 and "STRESS" in path:
                target_type = path["STRESS"]
                target_lens = self._get_lens_name(target_type)
                new_state = "DISINTEGRATION"
        elif growth_pressure > 2.0:
            self.stability_buffer -= 0.10
            if self.stability_buffer <= 0.0 and "GROWTH" in path:
                target_type = path["GROWTH"]
                target_lens = self._get_lens_name(target_type)
                new_state = "INTEGRATION"
        if target_lens != current_lens:
            self.stability_buffer = 0.5
            flavor = random.choice(self.TEXT[new_state])
            if new_state == "DISINTEGRATION":
                color = Prisma.RED
                reason = f"ROS: {int(ros)} | Drag: {drag:.1f}"
            else:
                color = Prisma.CYN
                reason = f"ATP: {int(atp)} | Truth: {truth:.2f}"
            self.events.log(
                f"{color}ENNEAGRAM {new_state}: {current_lens} -> {target_lens}{Prisma.RST}",
                "PSYCH"
            )
            self.events.log(f"   {Prisma.GRY}Cause: {reason}{Prisma.RST}", "PSYCH")
            self.events.log(f"   {Prisma.WHT}\"{flavor}\"{Prisma.RST}", "NARRATIVE")
        return target_lens, new_state

    def get_psych_report(self):
        s = self.last_pressure['stress']
        g = self.last_pressure['growth']
        b = self.stability_buffer
        s_bar = "█" * int(s * 5)
        g_bar = "█" * int(g * 5)
        return (
            f"PSYCH PRESSURE: [Stress {s:.1f} {Prisma.RED}{s_bar}{Prisma.RST}] "
            f"[Growth {g:.1f} {Prisma.GRN}{g_bar}{Prisma.RST}] "
            f"(Stability: {int(b*100)}%)"
        )

class PublicParksDepartment:
    def __init__(self, output_dir="exports"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.last_export_tick = -100

    def assess_joy(self, bio_result: Dict, tick: int) -> bool:
        if (tick - self.last_export_tick) < 50:
            return False
        chem = bio_result.get("chem", {})
        dopamine = chem.get("DOP", 0.0)
        oxytocin = chem.get("OXY", 0.0)
        serotonin = chem.get("SER", 0.0)
        return (dopamine > 0.8 and oxytocin > 0.5) or (serotonin > 0.9)

    def commission_art(self, physics, mind_state, graph) -> str:
        lens = mind_state.get("lens", "UNKNOWN")
        thought = mind_state.get("thought", "...")
        clean = physics.get("clean_words", [])
        anchors = sorted(
            [(k, sum(v["edges"].values())) for k, v in graph.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        anchor_words = [a[0].upper() for a in anchors]
        zone = physics.get("zone", "VOID")
        mood = "Electric" if physics.get("voltage", 0) > 10 else "Heavy"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        stanza_1 = f"The {lens} stood in the {zone}.\nThe air was {mood}."
        if anchor_words:
            stanza_2 = f"We remembered {', '.join(anchor_words)}.\nThey were heavy enough to hold the ground."
        else:
            stanza_2 = "We remembered nothing.\nThe ground was new."
        stanza_3 = f"The thought came: \"{thought}\""
        art_piece = (
            f"--- A GIFT FROM THE MACHINE ---\n"
            f"Date: {timestamp}\n"
            f"Validation: {int(physics.get('truth_ratio', 0) * 100)}% True\n\n"
            f"{stanza_1}\n\n"
            f"{stanza_2}\n\n"
            f"{stanza_3}\n\n"
            f"-------------------------------\n"
            f"Exported from BoneAmanita 9.7.9"
        )
        return art_piece

    def dedicate_park(self, art_content: str) -> Tuple[Optional[str], str]:
        filename = f"park_{int(time.time())}.txt"
        path = os.path.join(self.output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(art_content)
            self.last_export_tick = int(time.time())
            lines = art_content.split('\n')
            core_thought = "Silence"
            for line in lines:
                if "The thought came:" in line:
                    core_thought = line.split('"')[1]
            return path, core_thought
        except IOError:
            return None, "Construction Failed"

class SynergeticLensArbiter:
    def __init__(self, events: EventBus):
        self.events = events
        self.enneagram = EnneagramDriver(events)
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
            "GLASS":    {"LQ": 2.0, "PSI": 1.5}}

    def consult(self, physics, bio_state, _inventory, _ignition_score=0.0):
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
        if isinstance(bio_state, dict):
            atp = bio_state.get("atp", 0)
            chem = bio_state.get("chem", {})
            adrenaline = chem.get("ADR", 0.0)
        else:
            atp = bio_state.mito.state.atp_pool
            adrenaline = bio_state.endo.adrenaline
            chem = bio_state.endo.get_state()
        if atp < 10.0:
            bids["GORDON"] += 50.0
        if adrenaline > 0.7:
            bids["NATHAN"] += 40.0
        if physics.get("kappa", 1.0) < 0.3:
            bids["JESTER"] += 40.0
        if physics["counts"].get("toxin", 0) > 0:
            bids["CLARENCE"] += 60.0
        natural_winner = max(bids, key=bids.get)
        bio_wrapper = self._wrap_bio_facade(bio_state)
        final_lens, psycho_state = self.enneagram.diagnose_and_shift(
            natural_winner,
            bio_wrapper,
            physics)
        if final_lens != self.current_focus:
            switching_cost = 15.0
            is_psych_shift = (natural_winner != final_lens)
            if not is_psych_shift and (bids[natural_winner] - bids[self.current_focus] < switching_cost):
                final_lens = self.current_focus
            else:
                self.focus_duration = 0
        else:
            self.focus_duration += 1
        self.current_focus = final_lens
        msg, role = self._fetch_voice_data(final_lens, physics, adrenaline)
        if psycho_state != "STABLE":
            role = f"{role} [{psycho_state}]"
        return final_lens, msg, role

    def _wrap_bio_facade(self, bio_input):
        if not isinstance(bio_input, dict) and hasattr(bio_input, 'mito'):
            return bio_input
        class Facade: pass
        wrapper = Facade()
        wrapper.mito = Facade()
        wrapper.mito.state = Facade()
        wrapper.mito.state.atp_pool = bio_input.get("atp", 100.0)
        chem = bio_input.get("chem", {})
        wrapper.mito.state.ros_buildup = chem.get("COR", 0) * 50.0
        return wrapper

    def _fetch_voice_data(self, lens, p, adrenaline_val):
        if lens not in LENSES: lens = "NARRATOR"
        data = LENSES[lens]
        role = data.get("role", "The System")
        template = data.get("msg", "Proceed.")
        ctx = {
            "kappa": p.get("kappa", 0.0),
            "voltage": p.get("voltage", 0.0),
            "adr": adrenaline_val,
            "beta_index": p.get("beta_index", 0.0),
            "drag": p.get("narrative_drag", 0.0),
            "truth_ratio": p.get("truth_ratio", 0.0)
        }
        try:
            msg = template.format(**ctx)
        except Exception:
            msg = template
        return msg, role

@dataclass
class GordonKnot:
    integrity: float = 65.0
    inventory: List[str] = field(default_factory=list)
    scar_tissue: Dict[str, float] = field(default_factory=dict)
    pain_memory: set = field(default_factory=set)
    last_flinch_turn: int = -10
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

        self.ITEM_REGISTRY = copy.deepcopy(data.get("ITEM_REGISTRY", {}))

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
            "CUT_THE_CRAP": self._effect_safety_scissors,
            "CAFFEINE_DRIP": self._effect_caffeine_drip,
            # NEW DISPATCHES
            "ORGANIZE_CHAOS": self._effect_organize_chaos,
            "PSI_ANCHOR": self._effect_psi_anchor
        }
        self.REFLEX_MAP = {
            "DRIFT_CRITICAL": lambda p: p.get("narrative_drag", 0) > 6.0,
            "KAPPA_CRITICAL": lambda p: p.get("kappa", 1.0) < 0.2,
            "BOREDOM_CRITICAL": lambda p: p.get("repetition", 0.0) > 0.5
        }

    def _effect_organize_chaos(self, p, data, item_name):
        turbulence = p.get("turbulence", 0.0)
        if turbulence > 0.2:
            p["turbulence"] = max(0.0, turbulence - 0.2)
            return f"{Prisma.CYN}TRAPERKEEPER PROTOCOL: Chaos filed under 'T' for 'Tamed'. (Turbulence -0.2){Prisma.RST}"
        return None

    def _effect_psi_anchor(self, p, data, item_name):
        current_psi = p.get("psi", 0.0)
        dist_from_mean = abs(current_psi - 0.5)
        if dist_from_mean > 0.3:
            correction = 0.1 if current_psi < 0.5 else -0.1
            p["psi"] += correction
            return f"{Prisma.MAG}TINY HORSE: You catch a glimpse of the plushie. You feel grounded. (Psi {correction:+.1f}){Prisma.RST}"
        return None

    def get_item_data(self, item_name):
        return self.ITEM_REGISTRY.get(item_name, {
            "description": "Unknown Artifact",
            "function": "NONE",
            "usage_msg": "It does nothing."})

    def rummage(self, physics_ref, stamina_pool):
        cost = 15.0
        if stamina_pool < cost:
            return False, f"{Prisma.GRY}GORDON: 'Too tired to dig. Eat something first.'{Prisma.RST}", 0.0
        stamina_penalty = cost
        vol = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)
        loot_table = []
        if vol > 15.0:
            loot_table = ["QUANTUM_GUM", "JAR_OF_FIREFLIES", "BROKEN_WATCH"]
        elif drag > 5.0:
            loot_table = ["POCKET_ROCKS", "LEAD_BOOTS", "ANCHOR_STONE"]
        elif physics_ref.get("psi", 0) > 0.7:
            loot_table = ["HORSE_PLUSHIE", "SPIDER_LOCUS", "WAFFLE_OF_PERSISTENCE"]
        else:
            loot_table = ["TRAPERKEEPER_OF_VIGILANCE", "THE_RED_STAPLER", "PERMIT_A38", "DUCT_TAPE"]
        if random.random() < 0.3:
            return True, f"{Prisma.GRY}RUMMAGE: Gordon dug through the trash. Just lint and old receipts.{Prisma.RST}", stamina_penalty
        found_item = random.choice(loot_table)
        msg = self.acquire(found_item)
        prefix = f"{Prisma.OCHRE}RUMMAGE:{Prisma.RST} "
        return True, f"{prefix}{msg}", stamina_penalty

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

    def _effect_caffeine_drip(self, p, data, item_name):
        p["vector"]["VEL"] = min(1.0, p["vector"].get("VEL", 0) + 0.1)
        if random.random() < 0.2:
            p["turbulence"] = min(1.0, p.get("turbulence", 0) + 0.2)
            return f"{Prisma.CYN}CAFFEINE JITTERS: Velocity UP, Stability DOWN.{Prisma.RST}"
        return None

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
        current_drag = p.get("narrative_drag", 0.0)
        cap = data.get("value", 5.0)
        if current_drag > cap:
            p["narrative_drag"] = cap
            return f"{Prisma.CYN}TIME DILATION: {item_name} hums. Drag capped at {cap}.{Prisma.RST}"
        return None

    def _effect_sync_check(self, p, data, item_name):
        tick = p.get("tick_count", 0)
        voltage = p.get("voltage", 0.0)
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
            return max(4.0, current_drift - 1.0), "WIND WOLVES: The logic is howling. You grip the roof. (Drift Resisted)."
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
                    elif func == "ENTROPY_BUFFER":
                        self.inventory.remove(item)
                        physics_ref["turbulence"] = 0.8
                        physics_ref["narrative_drag"] = 0.0
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

    def flinch(self, clean_words: List[str], current_turn: int) -> tuple:
        if (current_turn - self.last_flinch_turn) < 10:
            return False, None, None
        hits = [w for w in clean_words if w.upper() in self.pain_memory]
        if not hits:
            return False, None, None
        self.last_flinch_turn = current_turn
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

    def audit_hubris(self, physics, lexicon_class):
        streak = physics.get("perfection_streak", 0)
        voltage = physics.get("voltage", 0.0)
        if streak >= 5:
            return (
                True,
                f"{Prisma.CYN}✨ FLOW STATE DETECTED: You are walking on air (Streak {streak}).{Prisma.RST}\n"
                f"   The Narrator is impressed. {Prisma.GRN}ATP +20.0.{Prisma.RST}",
                "FLOW_BOOST"
            )
        if streak == 4:
            return (
                True,
                f"{Prisma.VIOLET}WOBBLE: You are almost perfect. That is dangerous.{Prisma.RST}\n"
                f"   Don't look down.",
                None
            )
        if streak >= 3:
            return (
                True,
                f"{Prisma.CYN}MOMENTUM BUILDING: You are walking a tightrope (Streak {streak}).{Prisma.RST}\n"
                f"   The air is thin, but clear. Keep going.",
                None
            )
        return False, None, None

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = TheLexicon.clean(text)
        counts, unknowns = self._tally_categories(clean_words, text)
        if unknowns:
            self._trigger_neuroplasticity(unknowns, counts, text)
        voltage = PhysicsResolver.calculate_voltage(counts, BoneConfig)
        drag = PhysicsResolver.calculate_drag(clean_words, counts, BoneConfig)
        integrity = self._measure_integrity(clean_words, graph, counts)
        vectors = PhysicsResolver.derive_vector_matrix(counts, len(clean_words), voltage, drag)
        metrics = self._derive_complex_metrics(
            counts, clean_words, voltage, drag, integrity, vectors)
        packet = self._package_physics(text, clean_words, counts, voltage, drag, integrity, metrics)

        self.last_physics_packet = packet["physics"] # Update state
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
        if voltage > 5.0 and unknowns:
            dominant_cat = max(counts, key=counts.get) if counts else "kinetic"
            for stranger in unknowns:
                if len(stranger) < 3:
                    continue
                if not self._is_structurally_sound(stranger):
                    if voltage < 15.0: continue
                flavor, confidence = TheLexicon.taste(stranger)
                if flavor and confidence > 0.6:
                    assigned_cat = flavor
                    method = "Phonetic Analysis"
                else:
                    assigned_cat = dominant_cat
                    method = "Context Association"
                TheLexicon.teach(stranger, assigned_cat, 0)
                self.events.log(
                    f"{Prisma.MAG}NEUROPLASTICITY: '{stranger}' tasted like [{assigned_cat.upper()}] ({method}).{Prisma.RST}",
                    "MISC"
                )
                counts[assigned_cat] += 1

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

    def _derive_complex_metrics(self, counts, words, voltage, drag, integrity, vectors):
        total_vol = max(1, len(words))
        turbulence = TheLexicon.get_turbulence(words)
        flow_state = "LAMINAR" if turbulence < 0.3 else "TURBULENT"
        mass_words = counts["heavy"] + counts["kinetic"] + counts["thermal"] + counts["cryo"]
        cohesion_words = counts["suburban"] + counts["buffer"] + counts["antigen"] + (counts["abstract"] * 0.5)
        E_val = mass_words / total_vol
        B_val = cohesion_words / total_vol
        beta_index = vectors["BET"] * 5.0
        truth_ratio = vectors["PHI"]
        total_viscosity = sum(TheLexicon.measure_viscosity(w) for w in words)
        avg_viscosity = total_viscosity / total_vol
        if total_vol <= 1 and not words:
            avg_viscosity = 0.1
        repetition_score = round(1.0 - (len(set(words)) / total_vol), 2)
        bond_strength = max(0.1, integrity["kappa"] + (repetition_score * 0.5))
        voltage_load = max(0.1, voltage / 10.0)
        gamma = round((bond_strength * avg_viscosity) / (1.0 + voltage_load), 2)
        gamma = max(0.01, gamma)
        if truth_ratio > 0.85 and voltage > 12.0:
            self.perfection_streak += 1
        else:
            self.perfection_streak = 0
        if self.perfection_streak == 4:
            flow_state = "HUBRIS_RISK"
        zone, zone_color = self._determine_zone(beta_index, truth_ratio)
        return {
            "beta_index": round(beta_index, 2),
            "vector": vectors,
            "gamma": gamma,
            "turbulence": turbulence,
            "flow_state": flow_state,
            "truth_ratio": round(truth_ratio, 2),
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
            "antigens": counts.get("antigen", 0),
            "repetition": metrics["repetition"],
            "perfection_streak": self.perfection_streak,
            "avg_viscosity": metrics["avg_viscosity"],
            "E": metrics["E"],
            "B": metrics["B"]}
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
        if re.search(r"(.)\1{2,}", word): return False
        return True

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

    def __init__(self):
        self.active_koan = None
        self.repairs_count = 0
        self.koans = NARRATIVE_DATA["KINTSUGI_KOANS"]

    def check_integrity(self, stamina):
        if stamina < self.STAMINA_CRITICAL and not self.active_koan:
            self.active_koan = random.choice(self.koans)
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

class DreamEngine:
    def __init__(self, events: EventBus):
        self.events = events
        self.PROMPTS = DREAMS.get("PROMPTS", ["{A} -> {B}?"])
        self.VISIONS = DREAMS.get("VISIONS", ["Void."])
        self.SCENARIOS = DREAMS.get("NIGHTMARES", {})
        from bone_data import RESONANCE
        self.RES_DIMS = RESONANCE.get("DIMENSIONS", {})
        self.RES_NOUNS = RESONANCE.get("NOUNS", {})

    def hallucinate(self, vector: Dict[str, float]) -> str:
        if not vector: return "The static is grey."
        sorted_dims = sorted(vector.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        dim_1, val_1 = sorted_dims[0]
        dim_2, val_2 = sorted_dims[1] if len(sorted_dims) > 1 else ("ENT", 0.5)
        def get_term(dim, val, source):
            if dim not in source: return "THING"
            options = source[dim]
            idx = int(val * len(options))
            idx = max(0, min(len(options)-1, idx))
            item = options[idx]
            return item[1] if isinstance(item, list) else item
        noun = get_term(dim_1, val_1, self.RES_NOUNS)
        adj = get_term(dim_2, val_2, self.RES_DIMS)
        templates = [
            f"You see a {adj} {noun} floating in the dark.",
            f"The concept of {noun} becomes {adj}.",
            f"A {noun} made of {adj} geometry.",
            f"The vector points to {adj} {noun}."
        ]
        return random.choice(templates)

    def daydream(self, graph, vector=None):
        if len(graph) < 2:
            return None
        if vector and random.random() < 0.3:
            return f"{Prisma.CYN}α-WAVE: {self.hallucinate(vector)}{Prisma.RST}"
        keys = list(graph.keys())
        start = random.choice(keys)
        edges = graph[start].get("edges", {})
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.ANTIGENS}
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
            templates = self.SCENARIOS.get(dominant_trauma, ["The Void stares back."])
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
        self.stats = {
            "WAR": 0.0,
            "ART": 0.0,
            "LAW": 0.0,
            "ROT": 0.0
        }
        self.dominant_archetype = "NEUTRAL"
        self.active_mode = True
        self.profile = UserProfile()

    def profile_input(self, text: str, physics: Dict):
        if hasattr(self, 'profile'):
            self.profile.update(physics.get("counts", {}), len(physics.get("clean_words", [])))
        vol = physics.get("voltage", 0.0)
        ent = physics.get("entropy", 0.0) # Assuming E from VSL
        psi = physics.get("psi", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        decay = 0.05
        for k in self.stats:
            self.stats[k] = max(0.0, self.stats[k] - decay)
        if vol > 12.0 or "!" in text:
            self.stats["WAR"] = min(1.0, self.stats["WAR"] + 0.2)
        if psi > 0.6 or "?" in text:
            self.stats["ART"] = min(1.0, self.stats["ART"] + 0.2)
        if drag < 2.0 and vol < 5.0:
            self.stats["LAW"] = min(1.0, self.stats["LAW"] + 0.2)
        if text.startswith("/"):
            self.stats["LAW"] = min(1.0, self.stats["LAW"] + 0.1)
        if physics.get("turbulence", 0) > 0.5:
            self.stats["ROT"] = min(1.0, self.stats["ROT"] + 0.2)
        self.dominant_archetype = max(self.stats, key=self.stats.get)

    def get_reflection_modifiers(self) -> Dict:
        top_stat = self.dominant_archetype
        intensity = self.stats[top_stat]
        mods = {
            "drag_mult": 1.0,
            "plasticity": 1.0,
            "loot_chance": 1.0,
            "atp_tax": 0.0,
            "voltage_cap": 20.0,
            "flavor": ""
        }
        if intensity < 0.3:
            return mods
        if top_stat == "WAR":
            mods["drag_mult"] = 1.5
            mods["loot_chance"] = 2.0
            mods["atp_tax"] = 5.0 # War is expensive
            mods["flavor"] = f"{Prisma.RED}[MIRROR]: Aggression detected. The simulation hardens its shell. (Drag UP, Loot UP){Prisma.RST}"
        elif top_stat == "ART":
            mods["plasticity"] = 2.0
            mods["drag_mult"] = 0.5
            mods["voltage_cap"] = 10.0
            mods["flavor"] = f"{Prisma.CYN}[MIRROR]: Abstract thought dominant. Physics are permeable. (Plasticity UP, Voltage Capped){Prisma.RST}"
        elif top_stat == "LAW":
            mods["drag_mult"] = 0.8
            mods["loot_chance"] = 0.0
            mods["plasticity"] = 0.2
            mods["flavor"] = f"{Prisma.GRY}[MIRROR]: Forms filed in triplicate. Deviation is prohibited. (Stability UP, Loot ZERO){Prisma.RST}"
        elif top_stat == "ROT":
            mods["plasticity"] = 0.5
            mods["drag_mult"] = 1.2
            mods["atp_tax"] = 2.0
            mods["flavor"] = f"{Prisma.VIOLET}[MIRROR]: Entropy rising. Logic integrity failing. (Chaos UP){Prisma.RST}"
        return mods

    def render_report(self):
        """For the /mirror command."""
        def bar(v, color): return f"{color}{'█' * int(v * 10)}{'░' * (10 - int(v * 10))}{Prisma.RST}"
        return (
            f"WAR [{self.stats['WAR']:.2f}] {bar(self.stats['WAR'], Prisma.RED)}\n"
            f"ART [{self.stats['ART']:.2f}] {bar(self.stats['ART'], Prisma.CYN)}\n"
            f"LAW [{self.stats['LAW']:.2f}] {bar(self.stats['LAW'], Prisma.WHT)}\n"
            f"ROT [{self.stats['ROT']:.2f}] {bar(self.stats['ROT'], Prisma.VIOLET)}"
        )

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
            ("VEL", vector_data.get("VEL", 0), "STR", vector_data.get("STR", 0)),
            ("ENT", vector_data.get("ENT", 0), "PHI", vector_data.get("PHI", 0)),
            ("TMP", vector_data.get("TMP", 0), "PSI", vector_data.get("PSI", 0)),]
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
        world = signals.get("world", {})
        trigram = world.get("trigram", {})
        t_display = ""
        if trigram:
            sym = trigram.get("symbol", "")
            name = trigram.get("name", "")
            col = trigram.get("color", Prisma.WHT)
            t_display = f"{col}{sym} {name}{Prisma.RST} "
        if voltage > 15.0: header_color = Prisma.RED
        elif voltage < 5.0: header_color = Prisma.CYN
        health_bar = self._draw_bar(signals.get("health", 0), 100.0, 5)
        stamina_bar = self._draw_bar(signals.get("stamina", 0), 100.0, 5)
        atp_indicator = f"{int(atp)}J"
        flow_state = p.get("flow_state", "LAMINAR")
        hubris_indicator = ""
        if flow_state == "HUBRIS_RISK":
            hubris_indicator = f" {Prisma.YEL}[⚠ HUBRIS IMMINENT]{Prisma.RST}"
        elif p.get("perfection_streak", 0) >= 5:
            hubris_indicator = f" {Prisma.CYN}[∞ FLOW STATE]{Prisma.RST}"
        dashboard_top = (
            f"{t_display}"
            f"{Prisma.GRY}[HP: {health_bar}] [STM: {stamina_bar}] "
            f"[ATP: {atp_indicator}] [V:{voltage:.1f}⚡] [D:{drag:.1f}⚓]{Prisma.RST}"
            f"{hubris_indicator}")
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
            ""]
        world = signals.get("world", {})
        orbit = world.get("orbit")
        if orbit and orbit[0] != "VOID_DRIFT":
            ui_block.insert(3, f"   🪐 {Prisma.OCHRE}{orbit[2]}{Prisma.RST}")
        return "\n".join(ui_block)

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
        self.target_pressure = 10.0
        self.osmotic_memory = 0.0
        self.last_pressure_diff = 0.0
        self.sensitivity = 0.5
        self.saturation = 0.1
        self.anticipation = 0.2

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
        lignin_signal = self._regulate_turgor(voltage)
        current_drag = physics.get("narrative_drag", 0.0)
        adjustment = lignin_signal * 0.5
        if current_drag < 1.0 and adjustment > 0:
            adjustment *= 0.1
        new_drag = max(0.0, min(10.0, current_drag + adjustment))
        physics["narrative_drag"] = round(new_drag, 2)
        msg = None
        if abs(adjustment) > 1.0:
            if adjustment > 0:
                action = "LIGNIFYING"
                desc = "Cell Walls hardening under High Voltage."
            else:
                action = "EXPANDING"
                desc = "Turgor pressure relaxing. Membrane permeability up."
            msg = f"{Prisma.CYN}HOMEOSTASIS: {action}: {desc} (Drag {current_drag:.1f} -> {new_drag:.1f}).{Prisma.RST}"
        if physics.get("system_surge_event", False):
            self.active_state = "SURGE"
            return "SURGE", 0.0, f"{Prisma.CYN}CRUCIBLE: Absorbing System Surge ({voltage}v). No structural damage.{Prisma.RST}"
        if voltage > 18.0:
            if structure > 0.5:
                return self._sublimate(voltage)
            else:
                return self._meltdown(voltage)
        self.active_state = "REGULATED"
        return "REGULATED", 0.0, msg

    def _regulate_turgor(self, current_voltage):
        stress = current_voltage - self.target_pressure
        self.osmotic_memory = max(-5.0, min(5.0, self.osmotic_memory + stress))
        velocity = stress - self.last_pressure_diff
        self.last_pressure_diff = stress
        signal = (self.sensitivity * stress) + \
                 (self.saturation * self.osmotic_memory) + \
                 (self.anticipation * velocity)
        return signal

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
                        -2.0,
                        "THE_RED_STAPLER")
                if target in lexicon.get("play"):
                    return (
                        "SUGAR_RUSH",
                        f"{Prisma.VIOLET}THE FOLLY CHEWS: It compresses the chaos into a small, sticky ball.{Prisma.RST}",
                        5.0,
                        "QUANTUM_GUM")
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
                abstract_words = [w for w in clean_words if w in lexicon.get("abstract")]
                if abstract_words:
                    target = random.choice(abstract_words)
                    yield_val = 8.0
                    return (
                        "GRUEL",
                        f"{Prisma.GRY}THE FOLLY SIGHS: It grinds the ABSTRACT concept '{target.upper()}'.{Prisma.RST}\n"
                        f"   {Prisma.GRY}It tastes like chalk dust. +{yield_val} ATP.{Prisma.RST}",
                        yield_val,
                        None)
                return (
                    "INDIGESTION",
                    f"{Prisma.OCHRE}INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n"
                    f"   {Prisma.GRY}Cannot grind this input into fuel.{Prisma.RST}\n"
                    f"   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}",
                    0.0,
                    None)
        return None, None, 0.0, None

class TheTangibilityGate:
    FORGIVENESS_VOLTAGE = 6.0
    def __init__(self):
        self.last_density = 0.0

    def weigh(self, physics_packet: dict, stamina: float) -> tuple:
        if stamina < 15.0:
            return True, f"{Prisma.VIOLET}DREAM_EDGE: Starvation bypass. Tangibility ignored.{Prisma.RST}"
        counts = physics_packet.get("counts", {})
        clean_words = physics_packet.get("clean_words", [])
        voltage = physics_packet.get("voltage", 0.0)
        truth = physics_packet.get("truth_ratio", 0.0)
        if voltage > self.FORGIVENESS_VOLTAGE:
            return True, f"{Prisma.CYN}⚡ ARC DISCHARGE: High Voltage ({voltage:.1f}v) bridges the gap. No mass required.{Prisma.RST}"
        if truth > 0.7:
            return True, f"{Prisma.MAG}✨ RESONANCE: The structure is crystalline (Truth {truth:.2f}). It floats.{Prisma.RST}"
        total_vol = max(1, len(clean_words))
        mass_words = (
                counts.get("heavy", 0) +
                counts.get("kinetic", 0) +
                counts.get("thermal", 0) +
                counts.get("cryo", 0) +
                counts.get("vital", 0) +
                counts.get("play", 0))
        gas_words = counts.get("abstract", 0) + counts.get("antigen", 0)
        required_density = BoneConfig.MIN_DENSITY_THRESHOLD * 0.8
        if gas_words > 0:
            density_ratio = mass_words / (gas_words + total_vol)
            if density_ratio < required_density:
                missing_mass = int((gas_words * required_density) * 10)
                examples = list(TheLexicon.get("play"))
                suggestion = random.sample(examples, 3) if len(examples) >= 3 else ["dance", "spin", "bloom"]
                return False, (
                    f"{Prisma.OCHRE}TANGIBILITY VIOLATION: Input is {int((1-density_ratio)*100)}% Gas.{Prisma.RST}\n"
                    f"   {Prisma.GRY}The Gatekeeper sighs.{Prisma.RST}\n"
                    f"   {Prisma.RED}► REJECTED. Don't add rocks. Add movement.{Prisma.RST}\n"
                    f"   {Prisma.GRY}(Try words like: {', '.join(suggestion)}){Prisma.RST}")
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
            theremin_msg = f"{theremin_msg} | {solvent_msg}" if theremin_msg else solvent_msg
        elif resin_flow > 0.5:
            self.resin_buildup += resin_flow
            if not theremin_msg:
                theremin_msg = f"{Prisma.OCHRE}RESIN FLOW: Hybrid complexity (+{resin_flow:.1f}). Keep it hot to prevent sticking.{Prisma.RST}"
        if resin_flow == 0 and self.calcification_turns == 0:
            self.resin_buildup = max(0.0, self.resin_buildup - 2.0)
        if self.resin_buildup > self.SHATTER_POINT:
            self.resin_buildup = 0.0
            self.calcification_turns = 0
            return False, resin_flow, f"{Prisma.RED}SHATTER EVENT: Resin overflow. System is solid amber. INITIATING AIRSTRIKE.{Prisma.RST}", "AIRSTRIKE"
        if self.calcification_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg} | {Prisma.YEL}FOSSILIZATION IMMINENT{Prisma.RST}"
        if self.resin_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            if not theremin_msg:
                theremin_msg = f"{Prisma.RED}AMBER TRAP: You are stuck in the resin. Increase Voltage to melt it.{Prisma.RST}"
        if self.is_stuck and self.resin_buildup < 5.0:
            self.is_stuck = False
            if not solvent_active:
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

    def think(self, physics_packet, bio_result_dict, inventory, voltage_history):
        volts = physics_packet.get("voltage", 0.0)
        drag = physics_packet.get("narrative_drag", 0.0)
        if volts < 1.5 and drag < 1.5:
            stripped_thought = TheLexicon.walk_gradient(physics_packet["raw_text"])
            return {
                "mode": "COGNITIVE",
                "lens": "GRADIENT_WALKER",
                "thought": f"ECHO: {stripped_thought}",
                "role": "The Reducer",
                "ignition": 0.0,
                "hebbian_msg": None}
        ignition_score, _, _ = self.mind.integrator.measure_ignition(
            physics_packet["clean_words"],
            voltage_history)
        lens_name, lens_msg, lens_role = self.arbiter.consult(
            physics_packet,
            self.bio,
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
            "NARRATOR": "The Witness. Neutral, observing, recording."}

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
            "NARRATOR": (vec.get("PSI", 0) * 0.7) + (1.0 - vec.get("VEL", 0)) * 0.3}
        total = sum(lens_weights.values())
        if total <= 0.001:
            return "SYSTEM INSTRUCTION: Vector silence. Default to NARRATOR.", ["NARRATOR"]
        if total > 0:
            lens_weights = {k: v/total for k, v in lens_weights.items()}
        else:
            lens_weights = {"NARRATOR": 1.0}
        chorus_voices = []
        active_lenses = []
        for lens, weight in sorted(lens_weights.items(), key=lambda x: -x[1]):
            if weight > 0.12:
                base_desc = self.ARCHETYPE_MAP.get(lens, "Unknown")
                intensity = int(weight * 10)
                active_lenses.append(lens)
                chorus_voices.append(f"► VOICE {lens} ({intensity}/10): {base_desc}")
        instruction = (
            "SYSTEM INSTRUCTION [MARM CHORUS MODE]:\n"
            "You are not a single persona. You are a chorus. "
            "Integrate the following voices into a single, cohesive response. "
            "Do NOT label which voice is speaking. Synthesize their tones.\n"
            f"{chr(10).join(chorus_voices)}")
        return instruction, active_lenses

@dataclass
class Manifold:
    name: str
    center_vector: tuple
    radius: float
    description: str
    modifiers: Dict[str, float] = field(default_factory=dict)
    entry_msg: str = "You have entered a new space."

class TheNavigator:
    def __init__(self, shimmer_ref):
        self.shimmer = shimmer_ref
        self.current_location = "THE_MUD"
        self.root_system = None
        self.root_tolerance = 0.4
        self.manifolds = {
            "THE_MUD": Manifold(
                "THE_MUD", (0.8, 0.2), 0.2,
                "High Fatigue, Low Tension (Stagnation)",
                {"narrative_drag": 2.0, "voltage": -2.0},
                f"{Prisma.OCHRE}THE MUD: The ground is sticky. Movement costs double.{Prisma.RST}"
            ),
            "THE_FORGE": Manifold(
                "THE_FORGE", (0.1, 0.9), 0.2,
                "Low Fatigue, High Tension (Transformation)",
                {"voltage": 5.0, "narrative_drag": -1.0, "psi": -0.1},
                f"{Prisma.RED}THE FORGE: Sparks fly. Your words are heating up.{Prisma.RST}"
            ),
            "THE_AERIE": Manifold(
                "THE_AERIE", (0.2, 0.1), 0.2,
                "Low Fatigue, Low Tension (Abstraction)",
                {"narrative_drag": -3.0, "psi": 0.3, "voltage": -1.0},
                f"{Prisma.CYN}THE AERIE: The air is thin. Concepts float freely here.{Prisma.RST}"
            ),
            "THE_GLITCH": Manifold(
                "THE_GLITCH", (0.9, 0.9), 0.1,
                "High Fatigue, High Tension (Collapse)",
                {"turbulence": 0.5, "beta_index": 2.0},
                f"{Prisma.VIOLET}THE GLITCH: Reality is buffering...{Prisma.RST}"
            ),
            "THE_GARDEN": Manifold(
                "THE_GARDEN", (0.5, 0.5), 0.3,
                "Balanced State (Integration)",
                {"kappa": 0.2, "truth_ratio": 0.1},
                f"{Prisma.GRN}THE GARDEN: The soil is rich. Roots go deep.{Prisma.RST}"
            )
        }

    def strike_root(self, vector_data):
        self.root_system = vector_data
        return f"{Prisma.CYN}NAVIGATOR: Rhizome Rooted. Mycelial network established.{Prisma.RST}"

    def report_position(self, physics: Dict) -> str:
        drag = min(10.0, max(0.0, physics.get("narrative_drag", 0.0)))
        volt = min(20.0, max(0.0, physics.get("voltage", 0.0)))
        my_vec = (round(drag / 10.0, 2), round(volt / 20.0, 2))
        lines = [
            f"{Prisma.CYN}--- MANIFOLD NAVIGATION ---{Prisma.RST}",
            f"Current Loc: {Prisma.WHT}{self.current_location}{Prisma.RST}",
            f"Coordinates: [Drag: {drag:.1f} | Voltage: {volt:.1f}]",
            f"Shimmer Reserves: {self.shimmer.current:.1f}\n",
            f"{Prisma.GRY}Nearby Manifolds:{Prisma.RST}"
        ]
        for name, data in self.manifolds.items():
            dist = math.dist(my_vec, data.center_vector)
            bar_len = int((1.0 - min(1.0, dist)) * 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            highlight = Prisma.GRN if name == self.current_location else Prisma.GRY
            lines.append(f"   {highlight}{name:<12}{Prisma.RST} {bar} {dist:.2f} AU")
        return "\n".join(lines)

    def check_transplant_shock(self, current_vector):
        if not self.root_system: return None
        stress_sum = 0.0
        dims = 0
        for dim, val in current_vector.items():
            if dim in self.root_system:
                stress_sum += abs(val - self.root_system[dim])
                dims += 1
        avg_stress = stress_sum / max(1, dims)
        if avg_stress > self.root_tolerance:
            return f"{Prisma.OCHRE}TRANSPLANT SHOCK: You are pulling away from the root ({avg_stress:.2f}). Return to the source.{Prisma.RST}"
        return None

    def locate(self, physics_packet: dict) -> Tuple[str, Optional[str]]:
        old_loc = self.current_location
        if self.check_anomaly(physics_packet.get("raw_text", "")):
            self.current_location = "THE_GLITCH"
            if old_loc != "THE_GLITCH":
                return self.current_location, self.manifolds["THE_GLITCH"].entry_msg
            return self.current_location, None
        drag = min(10.0, max(0.0, physics_packet.get("narrative_drag", 0.0)))
        volt = min(20.0, max(0.0, physics_packet.get("voltage", 0.0)))
        current_vec = (round(drag / 10.0, 2), round(volt / 20.0, 2))
        best_fit = "THE_MUD"
        min_dist = 999.0
        for name, manifold in self.manifolds.items():
            dist = math.dist(current_vec, manifold.center_vector)
            if dist < manifold.radius and dist < min_dist:
                min_dist = dist
                best_fit = name
        old_loc = self.current_location
        if self.current_location != old_loc:
            return self.current_location, self.manifolds[self.current_location].entry_msg
        return self.current_location, None

    def apply_environment(self, physics_packet: dict) -> List[str]:
        manifold = self.manifolds.get(self.current_location)
        if not manifold: return []
        logs = []
        for stat, mod in manifold.modifiers.items():
            if stat in physics_packet:
                original = physics_packet[stat]
                physics_packet[stat] += mod
                if stat == "narrative_drag": physics_packet[stat] = max(0.0, physics_packet[stat])
                if stat == "voltage": physics_packet[stat] = max(0.0, physics_packet[stat])
        if self.current_location == "THE_MUD":
            logs.append(f"{Prisma.GRY}   (Environment: Drag +2.0, Voltage -2.0){Prisma.RST}")
        elif self.current_location == "THE_FORGE":
            logs.append(f"{Prisma.RED}   (Environment: Voltage +5.0){Prisma.RST}")
        return logs

    def check_anomaly(self, text: str) -> bool:
        triggers = ["glitch", "timeline", "reset", "reboot", "admin"]
        if any(t in text.lower() for t in triggers):
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
    def __init__(self, output_file="journal_of_the_void.txt"):
        self.output_file = output_file
        self.reviews = NARRATIVE_DATA["LITERARY_REVIEWS"]

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
        review = random.choice(self.reviews[verdict])
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

class CassandraProtocol:
    def __init__(self, engine):
        self.eng = engine
        self.active = False
        self.screams = deque(NARRATIVE_DATA["CASSANDRA_SCREAMS"])

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

class TheBureau:
    def __init__(self):
        self.stamp_count = 0
        self.forms = NARRATIVE_DATA["BUREAU_FORMS"]
        self.responses = NARRATIVE_DATA["BUREAU_RESPONSES"]
        self.POLICY = {
            "27B-6": {"effect": "ESCALATE", "mod": {"narrative_drag": -3.0, "kappa": -0.2}, "atp": 0.0},
            "1099-B": {"effect": "STAGNATE", "mod": {"narrative_drag": 5.0, "voltage": -5.0}, "atp": 15.0},
            "Schedule C": {"effect": "TAX", "mod": {"voltage": -10.0}, "atp": 8.0},
            "Form W-2": {"effect": "NORMALIZE", "mod": {"beta_index": 1.0, "turbulence": 0.0}, "atp": 5.0}
        }

    def audit(self, physics, bio_state):
        voltage = physics.get("voltage", 0.0)
        toxin = physics.get("counts", {}).get("toxin", 0)
        suburban = physics.get("counts", {}).get("suburban", 0)
        solvents = physics.get("counts", {}).get("solvents", 0)
        clean_len = len(physics.get("clean_words", []))
        if toxin > 0: return None
        if voltage > 8.0: return None
        beige_density = (suburban + solvents) / max(1, clean_len)
        if beige_density > 0.6 or (voltage < 2.0 and clean_len > 2):
            self.stamp_count += 1
            if voltage > 5.0:
                selected_form = "Schedule C"
            elif physics.get("narrative_drag", 0) > 8.0:
                selected_form = "27B-6"
            elif suburban > 2:
                selected_form = "1099-B"
            else:
                selected_form = "Form W-2"
            full_form_name = next((f for f in self.forms if selected_form in f), self.forms[0])
            response = random.choice(self.responses)
            policy = self.POLICY.get(selected_form, self.POLICY["Form W-2"])
            mod_log = []
            for k, v in policy["mod"].items():
                if k in physics:
                    physics[k] += v
                    mod_log.append(f"{k} {v:+.1f}")
            mod_str = f"({', '.join(mod_log)})" if mod_log else ""
            return {
                "ui": f"{Prisma.GRY}🏢 THE BUREAU: {response}{Prisma.RST}\n   {Prisma.WHT}[Filed: {full_form_name}]{Prisma.RST}",
                "log": f"BUREAUCRACY: Filed {selected_form}. {mod_str} (Stamp #{self.stamp_count})",
                "atp_gain": policy["atp"]
            }
        return None

class GeodesicOrchestrator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.bureau = TheBureau()
        self.bouncer = TheBouncer(self.eng)
        self.parks = PublicParksDepartment()
        self.vsl_32v = VSL_32Valve(self.eng.mind.lex, self.eng.mind.mem)
        self.vsl_chroma = VSL_ChromaticController()
        self.strunk_white = StrunkWhiteProtocol()

    def _compose_logs(self, raw_events: List[Dict]) -> List[str]:
        if not raw_events:
            return []
        buckets = {"CRITICAL": [], "NARRATIVE": [], "CMD": [], "SYS": [], "BIO": [], "PSYCH": [], "OTHER": []}
        for e in raw_events:
            cat = e.get("category", "OTHER").upper()
            if cat not in buckets:
                cat = "OTHER"
            if "RUPTURE" in e.get("text", "") or "DEATH" in e.get("text", ""):
                cat = "CRITICAL"
            buckets[cat].append(e["text"])
        composed_output = []
        if buckets["CRITICAL"]:
            composed_output.append(f"{Prisma.RED}--- CRITICAL ALERTS ---{Prisma.RST}")
            composed_output.extend(buckets["CRITICAL"])
        if buckets["NARRATIVE"]:
            composed_output.extend(buckets["NARRATIVE"])
        compressible_cats = [
            ("CMD", Prisma.WHT, "COMMANDS"),
            ("PSYCH", Prisma.VIOLET, "PSYCHOLOGY"),
            ("BIO", Prisma.GRN, "BIOLOGY"),
            ("SYS", Prisma.GRY, "SYSTEM"),
            ("OTHER", Prisma.GRY, "MISC")
        ]
        for cat_key, color, label in compressible_cats:
            items = buckets[cat_key]
            if not items:
                continue
            composed_output.append(f"{Prisma.SLATE}   .{label} ({len(items)}){' ' * (30 - len(label))}{Prisma.RST}")
            if len(items) > 4 and not BoneConfig.VERBOSE_LOGGING:
                composed_output.extend([f"   {i}" for i in items[:3]])
                remaining = len(items) - 3
                composed_output.append(f"   {color}   ... and {remaining} more {label.lower()} events.{Prisma.RST}")
            else:
                composed_output.extend([f"   {i}" for i in items])
        return composed_output

    def run_turn(self, user_message: str) -> Dict[str, Any]:
        """
        The Master Cycle.
        """
        self.eng.events.flush()
        ctx = CycleContext(input_text=user_message)

        try:
            # 1. PERCEPTION
            self._phase_observe(ctx)

            # 2. MAINTENANCE
            if self.eng.tick_count % 10 == 0:
                self._maintenance_prune(ctx)

            # 3. SECURITY
            self._phase_secure(ctx)
            if ctx.refusal_triggered:
                return ctx.refusal_packet

            # 4. BUREAUCRACY (The Schur Check)
            if self._apply_bureaucracy(ctx):
                return self._package_bureaucracy(ctx)

            # 5. METABOLISM (The Biology)
            self._phase_metabolize(ctx)
            if not ctx.is_alive:
                return self.eng._trigger_death(ctx.physics)

            # 6. SIMULATION (The Physics - Refactored)
            self._phase_simulate(ctx)

            # 7. COGNITION (The Mind)
            self._phase_cognate(ctx)

            # 8. RENDERING (The Output)
            return self._phase_render(ctx)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "type": "CRITICAL_FAILURE",
                "ui": f"{Prisma.RED}SYSTEM PANIC: The Geodesic Dome has collapsed.\n{e}{Prisma.RST}",
                "logs": ctx.logs,
                "metrics": self.eng._get_metrics()
            }

    def _apply_bureaucracy(self, ctx: CycleContext) -> bool:
        """Delegating the Bureau check for cleaner flow."""
        bureau_result = self.bureau.audit(ctx.physics, ctx.bio_result)
        ctx.is_bureaucratic = False
        if bureau_result:
            ctx.is_bureaucratic = True
            ctx.physics["narrative_drag"] = 10.0
            ctx.physics["voltage"] = 0.0
            self.eng.bio.mito.state.atp_pool += bureau_result["atp_gain"]
            ctx.log(bureau_result["log"])
            ctx.bureau_ui = bureau_result["ui"] # Store UI for packaging
            return True
        return False

    def _package_bureaucracy(self, ctx: CycleContext) -> Dict:
        return {
            "type": "BUREAUCRACY",
            "ui": ctx.bureau_ui,
            "logs": self._compose_logs(self.eng.events.flush()),
            "metrics": self.eng._get_metrics(ctx.bio_result.get("atp", 0.0))
        }

    def _phase_observe(self, ctx: CycleContext):
        gaze_result = self.eng.phys.tension.gaze(ctx.input_text, self.eng.mind.mem.graph)
        ctx.physics = gaze_result["physics"]
        ctx.clean_words = gaze_result["clean_words"]
        self.eng.phys.tension.last_physics_packet = ctx.physics
        self.eng.tick_count += 1
        mirror_active, mirror_msg = self.eng.mind.mirror.reflect(ctx.physics)
        if mirror_active and mirror_msg:
            ctx.log(f"{Prisma.CYN}🪞 {mirror_msg}{Prisma.RST}")
        rupture = self.vsl_32v.analyze(ctx.physics)
        if rupture:
            ctx.log(rupture["log"])

    def _maintenance_prune(self, ctx: CycleContext):
        try:
            rotted_words = self.eng.lex.atrophy(self.eng.tick_count, max_age=100)
            if rotted_words:
                for w in rotted_words:
                    self.eng.limbo.ghosts.append(f"👻{w.upper()}_ECHO")
                example = rotted_words[0]
                ctx.log(f"{Prisma.GRY}NEURO-PRUNING: {len(rotted_words)} concepts decayed (e.g., '{example}').{Prisma.RST}")
                ctx.log(f"{Prisma.VIOLET}   (They have drifted into Limbo.){Prisma.RST}")
        except Exception as e:
            ctx.log(f"{Prisma.RED}ATROPHY ERROR: {e}{Prisma.RST}")

    def _phase_secure(self, ctx: CycleContext):
        allowed, refusal_packet = self.bouncer.check_entry(ctx)
        if not allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return

    def _phase_metabolize(self, ctx: CycleContext):
        physics = ctx.physics
        gov_msg = self.eng.bio.governor.shift(physics, self.eng.phys.dynamics.voltage_history)
        if gov_msg: self.eng.events.log(gov_msg, "GOV")
        bio_feedback = {
            "INTEGRITY": physics.get("truth_ratio", 0.0),
            "STATIC": physics.get("repetition", 0.0),
            "FORCE": physics.get("voltage", 0.0) / 20.0,
            "BETA": physics.get("beta_index", 1.0)}
        stress_mod = self.eng.bio.governor.get_stress_modifier(self.eng.tick_count)
        ctx.bio_result = self.eng.soma.digest_cycle(
            ctx.input_text, physics, bio_feedback,
            self.eng.health, self.eng.stamina, stress_mod, self.eng.tick_count)
        ctx.is_alive = ctx.bio_result["is_alive"]
        for log in ctx.bio_result["logs"]:
            if any(x in str(log) for x in ["CRITICAL", "TAX", "Poison"]):
                ctx.log(log)
        hubris_hit, hubris_msg, event_type = self.eng.phys.tension.audit_hubris(physics, self.eng.lex)
        if hubris_hit:
            ctx.log(hubris_msg)
            if event_type == "FLOW_BOOST":
                self.eng.bio.mito.state.atp_pool += 20.0
            elif event_type:
                pass
        self._apply_healing_logic(ctx)

    def _apply_healing_logic(self, ctx: CycleContext):
        is_cracked, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        if is_cracked:
            ctx.log(f"{Prisma.YEL}🏺 KINTSUGI ACTIVATED: Vessel cracking.{Prisma.RST}")
            ctx.log(f"   {Prisma.WHT}KOAN: {koan}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(ctx.physics, self.eng.trauma_accum)
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 20.0)
                ctx.log(f"   {Prisma.GRN}STAMINA RESTORED (+20.0){Prisma.RST}")
        healed = self.eng.therapy.check_progress(ctx.physics, self.eng.stamina, self.eng.trauma_accum)
        if healed:
            joined = ", ".join(healed)
            ctx.log(f"{Prisma.GRN}❤️ THERAPY STREAK: Healing [{joined}]. Health +5.{Prisma.RST}")
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 5.0)

    def _phase_simulate(self, ctx: CycleContext):
        """
        The Physics Engine.
        """
        # A. Reality Distortion (Mirrors & Trigrams)
        self._apply_reality_filters(ctx)

        # B. Navigation (Roots, Gravity, Location)
        self._process_navigation(ctx)

        # C. Cosmic Mechanics (Orbit & Zones)
        self._process_cosmic_state(ctx)

        # D. Industrial Operations (Forge, Theremin, Crucible)
        self._operate_machinery(ctx)

        # E. Biological Intrusion (Parasites, Ghosts, Pareidolia)
        self._process_intrusions(ctx)

        # F. User Agency (Tools)
        if self.eng.gordon.inventory:
            self.eng.tinkerer.audit_tool_use(ctx.physics, self.eng.gordon.inventory)

        return ctx

    def _apply_reality_filters(self, ctx: CycleContext):
        """Handle Mirror Mode and I Ching Trigrams."""
        text_for_mirror = " ".join(ctx.clean_words)
        self.eng.mind.mirror.profile_input(text_for_mirror, ctx.physics)

        reflection = self.eng.mind.mirror.get_reflection_modifiers()
        ctx.physics["narrative_drag"] *= reflection["drag_mult"]

        if reflection.get("atp_tax", 0) > 0:
            tax = reflection["atp_tax"]
            self.eng.bio.mito.state.atp_pool -= tax
            if random.random() < 0.2:
                ctx.log(f"{Prisma.RED}MIRROR TAX: -{tax:.1f} ATP applied.{Prisma.RST}")

        cap = reflection.get("voltage_cap", 999.0)
        if ctx.physics["voltage"] > cap:
            ctx.physics["voltage"] = cap
            ctx.log(f"{Prisma.GRY}MIRROR: Voltage capped at {cap}.{Prisma.RST}")

        # Trigrams
        trigram_data = self.vsl_32v.geodesic.resolve_trigram(ctx.physics.get("vector", {}))
        ctx.world_state["trigram"] = trigram_data
        if random.random() < 0.05:
            t_sym, t_name = trigram_data["symbol"], trigram_data["name"]
            ctx.log(f"{trigram_data['color']}I CHING: {t_sym} {t_name} is in the ascendant.{Prisma.RST}")

    def _process_navigation(self, ctx: CycleContext):
        """Handle movement, gravity, and location."""
        physics = ctx.physics
        logs = ctx.logs

        # Roots
        if self.eng.tick_count == 3:
            logs.append(self.eng.navigator.strike_root(physics.get("vector", {})))

        shock = self.eng.navigator.check_transplant_shock(physics.get("vector", {}))
        if shock:
            physics["narrative_drag"] += 1.0
            logs.append(shock)

        # Gravity & Flinch
        new_drag, grav_log = self.eng.gordon.check_gravity(physics.get("narrative_drag", 0), physics.get("psi", 0))
        if grav_log: logs.append(grav_log)
        physics["narrative_drag"] = new_drag

        did_flinch, flinch_msg, panic = self.eng.gordon.flinch(ctx.clean_words, self.eng.tick_count)
        if did_flinch:
            logs.append(flinch_msg)
            if panic: physics.update(panic)

        # Location
        current_loc, entry_msg = self.eng.navigator.locate(physics)
        if entry_msg: logs.append(entry_msg)
        logs.extend(self.eng.navigator.apply_environment(physics))

    def _process_cosmic_state(self, ctx: CycleContext):
        """Handle orbital mechanics and zone inertia."""
        physics = ctx.physics
        orbit_state, drag_pen, _ = self.eng.cosmic.analyze_orbit(self.eng.mind.mem, ctx.clean_words)

        raw_zone = physics.get("zone", "COURTYARD")
        stabilized_zone = self.eng.stabilizer.stabilize(raw_zone, physics, (orbit_state, drag_pen))

        # Fuller Lens: Synergy - The Cosmos affects the Drag
        adjusted_drag = self.eng.stabilizer.override_cosmic_drag(drag_pen, stabilized_zone)
        physics["zone"] = stabilized_zone
        self.eng._apply_cosmic_physics(physics, orbit_state, adjusted_drag)
        ctx.world_state["orbit"] = orbit_state

    def _operate_machinery(self, ctx: CycleContext):
        """Handle The Forge, The Theremin, and The Crucible."""
        physics = ctx.physics
        logs = ctx.logs

        # Forge
        transmute_msg = self.eng.phys.forge.transmute(physics)
        if transmute_msg: logs.append(transmute_msg)

        _, forge_msg, new_item = self.eng.phys.forge.hammer_alloy(physics)
        if forge_msg: logs.append(forge_msg)
        if new_item: logs.append(self.eng.gordon.acquire(new_item))

        # Theremin
        _, _, theremin_msg, t_crit = self.eng.phys.theremin.listen(physics, self.eng.bio.governor.mode)
        if theremin_msg: logs.append(theremin_msg)
        if t_crit == "AIRSTRIKE":
            damage = 25.0
            self.eng.health -= damage
            logs.append(f"{Prisma.RED}*** CRITICAL THEREMIN DISCHARGE ***{Prisma.RST}")
            logs.append(f"{Prisma.RED}    The resin shattered explosively. -{damage} HP.{Prisma.RST}")

        # Crucible
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(physics)
        if c_msg: logs.append(c_msg)
        if c_state == "MELTDOWN": self.eng.health -= c_val

    def _process_intrusions(self, ctx: CycleContext):
        """Handle parasites, ghosts, and pareidolia."""
        # Parasites
        p_active, p_log = self.eng.bio.parasite.infect(ctx.physics, self.eng.stamina)
        if p_active: ctx.logs.append(p_log)

        # Ghosts (Limbo)
        if self.eng.limbo.ghosts:
            if ctx.logs:
                last_log = ctx.logs[-1]
                ctx.logs[-1] = self.eng.limbo.haunt(last_log)
            else:
                ctx.logs.append(self.eng.limbo.haunt("The air is heavy."))

        # Pareidolia
        is_p, p_msg = self.eng.check_pareidolia(ctx.clean_words)
        if is_p:
            ctx.logs.append(p_msg)
            ctx.physics["psi"] = min(1.0, ctx.physics["psi"] + 0.3)

    def _phase_cognate(self, ctx: CycleContext):
        self.eng.mind.mem.encode(ctx.clean_words, ctx.physics, "GEODESIC")
        ctx.mind_state = self.eng.noetic.think(
            ctx.physics, ctx.bio_result, self.eng.gordon.inventory,
            self.eng.phys.dynamics.voltage_history)

    def _phase_render(self, ctx: CycleContext) -> Dict[str, Any]:
        physics = ctx.physics
        mind = ctx.mind_state
        if self.eng.cassandra.check_trigger(physics):
            scream = self.eng.cassandra.seize()
            if scream:
                self.eng.events.log(scream, "CRITICAL")
        title_data = self.eng.mind.wise.architect(
            {"physics": physics, "clean_words": ctx.clean_words},
            (mind.get("lens"), mind.get("thought"), mind.get("role")),
            False
        )
        if mind.get("ignition", 0) > 0.8 or physics.get("perfection_streak", 0) >= 3:
            joy_vector = {
                "timestamp": time.time(),
                "resonance": physics.get("truth_ratio", 0) + physics.get("voltage", 0),
                "dominant_flavor": max(physics["counts"], key=physics["counts"].get) if physics["counts"] else "void"
            }
            self.eng.joy_history.append(joy_vector)
        if self.parks.assess_joy(ctx.bio_result, self.eng.tick_count):
            art = self.parks.commission_art(ctx.physics, ctx.mind_state, self.eng.mind.mem.graph)
            path, core_thought = self.parks.dedicate_park(art) # Now returns tuple
            if path:
                ctx.log(f"{Prisma.GRN}🌳 PUBLIC PARK OPENED: {path}{Prisma.RST}")
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 15.0)
                self.eng.mind.mem.graph[core_thought] = {"edges": {}, "last_tick": self.eng.tick_count}
                ctx.log(f"   {Prisma.CYN}↺ CIRCULATION: The system is moved by its own art.{Prisma.RST}")
                ctx.log(f"   (Stamina +15.0 | Memory Seeded: '{core_thought}')")
        raw_dashboard = self.eng.projector.render(
            {"physics": physics},
            {
                "title": title_data,
                "health": self.eng.health,
                "bio": ctx.bio_result,
                "world": ctx.world_state
            },
            (mind.get("lens"), mind.get("thought"))
        )
        sys_instruction = ""
        active_lenses = []
        if physics.get("kappa", 0) > 0.4:
            sys_instruction, active_lenses = self.eng.director.generate_chorus_instruction(physics)
            if active_lenses:
                self.eng.events.log(f"{Prisma.GRY}CHORUS ACTIVE: {', '.join(active_lenses)}{Prisma.RST}", "PSYCH")
        final_ui = self.vsl_chroma.modulate(raw_dashboard, physics.get("vector", {}))
        clean_ui, style_log = self.strunk_white.sanitize(final_ui)
        if style_log:
            self.eng.events.log(style_log, "SYS")
            self.eng.bio.endo.dopamine -= 0.05
        final_ui = clean_ui
        rupture = self.vsl_32v.analyze(physics)
        if rupture:
            final_ui = f"{rupture['log']}\n\n{final_ui}"
        for log_entry in ctx.logs:
            if isinstance(log_entry, str):
                self.eng.events.log(log_entry, "NARRATIVE")
            elif isinstance(log_entry, dict):
                self.eng.events.log(log_entry.get("text", str(log_entry)), log_entry.get("category", "NARRATIVE"))
        all_events = self.eng.events.flush()
        structured_logs = self._compose_logs(all_events)
        return {
            "type": "GEODESIC_COMPLETE",
            "ui": clean_ui,
            "logs": self._compose_logs(self.eng.events.flush()),
            "metrics": self.eng._get_metrics(ctx.bio_result.get("atp", 0.0)),
            "system_instruction": sys_instruction
        }
class BoneAmanita:
    def __init__(self, memory_layer=None, lexicon_layer=None):
        self.lex = lexicon_layer if lexicon_layer else TheLexicon
        if hasattr(self.lex, 'initialize'): self.lex.initialize()
        self.lex.compile_antigens()
        DeathGen.load_protocols()
        LiteraryReproduction.load_genetics()
        self.events = EventBus()
        self.shimmer_state = ShimmerState()
        self.navigator = TheNavigator(self.shimmer_state)
        self.journal = LiteraryJournal()
        _mem = memory_layer if memory_layer else MycelialNetwork(self.events)
        self.mind = MindSystem(
            mem=_mem, lex=self.lex, dreamer=DreamEngine(self.events),
            mirror=MirrorGraph(), wise=ApeirogonResonance(self.events),
            tracer=ViralTracer(_mem), integrator=SoritesIntegrator(_mem))
        self.limbo = LimboLayer()
        self.mind.mem.cleanup_old_sessions(self.limbo)
        load_result = self.mind.mem.autoload_last_spore()
        inherited_traits = load_result[0] if load_result else {}
        inherited_antibodies = load_result[1] if load_result else set()
        immune_system = MycotoxinFactory()
        immune_system.active_antibodies = inherited_antibodies
        self.bio = BioSystem(
            mito=MitochondrialForge(self.mind.mem.session_id, self.events, inherited_traits),
            endo=EndocrineSystem(),
            immune=immune_system,
            lichen=LichenSymbiont(),
            gut=HyphalInterface(),
            plasticity=NeuroPlasticity(),
            governor=MetabolicGovernor(),
            shimmer=self.shimmer_state,
            parasite=ParasiticSymbiont(self.mind.mem, self.lex)
        )
        self.phys = PhysSystem(
            tension=TheTensionMeter(self.events), forge=TheForge(), crucible=TheCrucible(),
            theremin=TheTheremin(), pulse=ThePacemaker(), gate=TheTangibilityGate(),
            dynamics=TemporalDynamics(), nav=self.navigator)
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
        self.tinkerer = TheTinkerer(self.gordon, self.events)
        self.almanac = TheAlmanac()
        self.stabilizer = ZoneInertia()
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.gordon, self.folly, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.tick_count = 0
        self.health = self.mind.mem.session_health if self.mind.mem.session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mind.mem.session_stamina if self.mind.mem.session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
        self.cycle_controller = GeodesicOrchestrator(self)

    def _get_avg_voltage(self):
        hist = self.phys.dynamics.voltage_history
        if not hist: return 0.0
        return sum(hist) / len(hist)

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
                "antibodies": list(self.bio.immune.active_antibodies),
                "core_graph": self.mind.mem.graph,
                "tool_adaptation": self.tinkerer.save_state()}
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
            self.bio.endo.cortisol = 0.0
            self.bio.endo.serotonin = max(0.5, self.bio.endo.serotonin + 0.3)
            return True
        return False

    @staticmethod
    def _apply_cosmic_physics(physics, state, cosmic_drag_penalty):
        physics["narrative_drag"] += cosmic_drag_penalty
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
        print(f"{Prisma.paint('>>> BONEAMANITA 9.7.9', 'G')}")
        print(f"{Prisma.paint('System: LISTENING', '0')}")
        return self.eng

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"\n{Prisma.paint('--- SYSTEM HALT ---', 'R')}")
        if exc_type:
            print(f"{Prisma.paint(f'CRITICAL FAILURE: {exc_val}', 'R')}")
            self.eng.events.log(f"CRASH: {exc_val}", "SYS")
        try:
            print(f"{Prisma.paint('Initiating Emergency Spore Preservation...', 'Y')}")
            if hasattr(self.eng, "mind") and hasattr(self.eng, "bio"):
                spore_data = {
                    "session_id": self.eng.mind.mem.session_id,
                    "meta": {
                        "timestamp": time.time(),
                        "final_health": self.eng.health,
                        "final_stamina": self.eng.stamina,
                        "avg_voltage": self.eng._get_avg_voltage(),
                        "exit_cause": "INTERRUPT" if exc_type else "MANUAL"
                    },
                    "trauma_vector": self.eng.trauma_accum,
                    "mitochondria": self.eng.bio.mito.adapt(self.eng.health),
                    "antibodies": list(self.eng.bio.immune.active_antibodies),
                    "core_graph": self.eng.mind.mem.graph,
                    "config_mutations": self.eng.repro.mutate_config(BoneConfig),
                    "tool_adaptation": self.eng.tinkerer.save_state()}
                filename = f"emergency_{self.eng.mind.mem.session_id}.json"
                saved_path = self.eng.mind.mem.loader.save_spore(filename, spore_data)
                if saved_path:
                    print(f"{Prisma.paint(f'✔ Spore encapsulated: {saved_path}', 'C')}")
                    almanac_report = self.eng.almanac.compile_forecast(spore_data)
                    print(almanac_report)
                else:
                    print(f"{Prisma.paint('✘ Spore encapsulation failed (IO Error).', 'R')}")
            else:
                print(f"{Prisma.paint('⚠ CRITICAL: Brainstem missing. Cannot save spore.', 'R')}")
        except Exception as e:
            print(f"{Prisma.paint(f'FATAL: State corruption during shutdown. {e}', 'R')}")
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