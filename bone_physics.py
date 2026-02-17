""" bone_physics.py - 'Gravity is just a habit that space-time hasn't been able to break.' """

import math, random, time
from typing import Dict, List, Any, Tuple, Optional, Deque
from collections import Counter, deque
from dataclasses import dataclass
from bone_types import Prisma, PhysicsPacket, CycleContext, SpatialState, MaterialState, EnergyState
from bone_lexicon import LexiconService
from bone_config import BoneConfig

@dataclass
class PhysicsDelta:
    operator: str
    field: str
    value: float
    source: str
    message: Optional[str] = None

TRIGRAM_MAP: Dict[str, Tuple[str, str, str, str]] = {
    "VEL": ("☳", "ZHEN",  "Thunder",  Prisma.GRN),
    "STR": ("☶", "GEN",   "Mountain", Prisma.SLATE),
    "ENT": ("☵", "KAN",   "Water",    Prisma.BLU),
    "PHI": ("☲", "LI",    "Fire",     Prisma.RED),
    "PSI": ("☰", "QIAN",  "Heaven",   Prisma.WHT),
    "BET": ("☴", "XUN",   "Wind",     Prisma.CYN),
    "E":   ("☷", "KUN",   "Earth",    Prisma.OCHRE),
    "DEL": ("☱", "DUI",   "Lake",     Prisma.MAG)}

@dataclass
class GeodesicVector:
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]

class GeodesicConstants:
    DENSITY_SCALAR = 20.0
    SQUELCH_LIMIT_MULT = 3.0
    MIN_VOLUME_SCALAR = 0.5
    SUBURBAN_FRICTION_LOG_BASE = 5.0
    HEAVY_FRICTION_MULT = 2.5
    SOLVENT_LUBRICATION_FACTOR = 0.05
    SHEAR_RESISTANCE_SCALAR = 2.0
    KINETIC_LIFT_RATIO = 0.5
    PLAY_LIFT_MULT = 2.5
    COMPRESSION_SCALAR = 10.0
    ABSTRACTION_BASE = 0.2
    MAX_VISCOSITY_DENSITY = 2.0
    MAX_LIFT_DENSITY = 2.0
    SAFE_VOL_THRESHOLD = 3

class GeodesicEngine:
    @staticmethod
    def collapse_wavefunction(clean_words: List[str], counts: Dict[str, int]) -> GeodesicVector:
        volume = max(1, len(clean_words))
        masses = GeodesicEngine._weigh_mass(counts)
        forces = GeodesicEngine._calculate_forces(masses, counts, volume)
        dimensions = GeodesicEngine._calculate_dimensions(masses, forces, counts, volume)
        return GeodesicVector(
            tension=forces['tension'],
            compression=forces['compression'],
            coherence=forces['coherence'],
            abstraction=forces['abstraction'],
            dimensions=dimensions)

    @staticmethod
    def _weigh_mass(counts: Dict[str, int]) -> Dict[str, float]:
        return {k: float(counts.get(k, 0)) for k in [
            "heavy", "kinetic", "constructive", "abstract",
            "play", "social", "explosive"]}

    @staticmethod
    def _calculate_forces(masses: Dict[str, float], counts: Dict[str, int], volume: int) -> Dict[str, float]:
        cfg = BoneConfig.PHYSICS
        GC = GeodesicConstants
        safe_volume = max(1, volume)
        total_kinetic = masses["kinetic"] + masses["explosive"]
        raw_tension_mass = ((masses["heavy"] * cfg.WEIGHT_HEAVY) + (total_kinetic * cfg.WEIGHT_EXPLOSIVE) + (masses["constructive"] * cfg.WEIGHT_CONSTRUCTIVE))
        density = raw_tension_mass / safe_volume
        kinetic_gain = getattr(BoneConfig, "KINETIC_GAIN", 1.0)
        base_tension = density * GC.DENSITY_SCALAR * kinetic_gain
        squelch_limit = getattr(BoneConfig, "SHAPLEY_MASS_THRESHOLD", 5.0) * GC.SQUELCH_LIMIT_MULT
        mass_scalar = min(1.0, safe_volume / squelch_limit)
        if safe_volume < GC.SAFE_VOL_THRESHOLD:
            mass_scalar *= GC.MIN_VOLUME_SCALAR
        tension = round(min(100.0, base_tension * mass_scalar), 2)
        shear_rate = total_kinetic / safe_volume
        suburban_count = counts.get("suburban", 0)
        suburban_friction = math.log1p(suburban_count) * GC.SUBURBAN_FRICTION_LOG_BASE
        raw_friction = (suburban_friction + (masses["heavy"] * GC.HEAVY_FRICTION_MULT))
        solvent_count = counts.get("solvents", 0)
        lubrication = 1.0 + (solvent_count * GC.SOLVENT_LUBRICATION_FACTOR)
        dynamic_viscosity = (raw_friction / lubrication) / (1.0 + (shear_rate * GC.SHEAR_RESISTANCE_SCALAR))
        kinetic_lift = total_kinetic * GC.KINETIC_LIFT_RATIO
        if masses["heavy"] > 0:
            kinetic_lift /= (masses["heavy"] * 0.5 + 1.0)
        lift = (masses["play"] * GC.PLAY_LIFT_MULT) + kinetic_lift
        viscosity_density = min(GC.MAX_VISCOSITY_DENSITY, dynamic_viscosity / safe_volume)
        lift_density = min(GC.MAX_LIFT_DENSITY, lift / safe_volume)
        raw_compression = (viscosity_density * GC.COMPRESSION_SCALAR) - (lift_density * GC.COMPRESSION_SCALAR)
        signal_drag_mult = getattr(BoneConfig, "SIGNAL_DRAG_MULTIPLIER", 1.0)
        raw_compression *= signal_drag_mult
        drag_halt = getattr(cfg, "DRAG_HALT", 10.0)
        compression = round(max(-5.0, min(drag_halt, raw_compression * mass_scalar)), 2)
        structural_mass = masses["heavy"] + masses["constructive"]
        shapley_threshold = getattr(BoneConfig, "SHAPLEY_MASS_THRESHOLD", 5.0)
        coherence = min(1.0, structural_mass / max(1.0, shapley_threshold))
        abstraction = min(1.0, (masses["abstract"] / safe_volume) + GC.ABSTRACTION_BASE)
        return {
            "tension": tension,
            "compression": compression,
            "coherence": round(coherence, 3),
            "abstraction": round(abstraction, 2)}

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        inv_vol = 1.0 / max(1, volume)
        base_mass = 0.1
        return {
            "VEL": min(1.0, (masses["kinetic"] * 2.0 - forces['compression'] + base_mass) * inv_vol),
            "STR": min(1.0, (masses["heavy"] * 2.0 + masses["constructive"] + base_mass) * inv_vol),
            "ENT": min(1.0, (counts.get("antigen", 0) * 3.0) * inv_vol),
            "PHI": min(1.0, (masses["heavy"] + masses["kinetic"] + base_mass) * inv_vol),
            "PSI": forces['abstraction'],
            "BET": min(1.0, (masses["social"] * 2.0) * inv_vol),
            "DEL": min(1.0, (masses["play"] * 3.0) * inv_vol),
            "E": min(1.0, (counts.get("solvents", 0)) * inv_vol)}

class TheGatekeeper:
    def __init__(self, lexicon_ref, memory_ref=None):
        self.lex = lexicon_ref
        self.mem = memory_ref

    def check_entry(self, ctx: CycleContext, current_atp: float = 20.0) -> Tuple[bool, Optional[Dict]]:
        phys = ctx.physics
        starvation_threshold = getattr(BoneConfig.BIO, "ATP_STARVATION", 5.0)
        if current_atp < (starvation_threshold * 0.5):
            return False, self._pack_refusal(ctx, "DARK_SYSTEM", "Energy critical. The inputs dissolve into the void.")
        if phys.counts.get("antigen", 0) > 2:
            return False, self._pack_refusal(ctx, "TOXICITY", f"{Prisma.RED}IMMUNE REACTION: Input rejected as pathogenic.{Prisma.RST}")
        text = ctx.input_text
        if "```" in text or "{{" in text or "}}" in text:
            return False, self._pack_refusal(ctx, "SYNTAX_ERR", f"{Prisma.RED}The mechanism jams. Syntax anomaly detected.{Prisma.RST}")
        if len(text) > 10000:
            return False, self._pack_refusal(ctx, "OVERLOAD", f"{Prisma.OCHRE}Input too long. Compress your thought.{Prisma.RST}")
        return True, None

    def _audit_safety(self, words: List[str]) -> bool:
        cursed = self.lex.get("cursed")
        return not cursed.isdisjoint(words) if isinstance(cursed, set) else any(w in cursed for w in words)

    def _pack_refusal(self, ctx, type_str, ui_msg):
        return {
            "type": type_str,
            "ui": ui_msg,
            "logs": ctx.logs + [ui_msg]}

class QuantumObserver:
    def __init__(self, events):
        self.events = events
        self.voltage_history: Deque[float] = deque(maxlen=5)
        self.last_physics_packet: Optional[PhysicsPacket] = None

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = LexiconService.clean(text)
        counts = self._tally_categories(clean_words)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts)
        self.voltage_history.append(geo.tension)
        smoothed_voltage = round(sum(self.voltage_history) / len(self.voltage_history), 2)
        e_metric, beta_val = self._calculate_metrics(text, counts)
        valence = LexiconService.get_valence(clean_words)
        graph_mass = self._calculate_graph_mass(clean_words, graph)
        energy = EnergyState(
            voltage=smoothed_voltage,
            entropy=e_metric,
            beta_index=beta_val,
            mass=round(graph_mass, 1),
            psi=geo.abstraction,
            kappa=geo.coherence,
            valence=valence,
            velocity=0.0,
            turbulence=0.0)
        matter = MaterialState(
            clean_words=clean_words,
            raw_text=text,
            counts=counts,
            antigens=counts.get("antigen", 0),
            vector=geo.dimensions,
            truth_ratio=0.5)
        space = SpatialState(
            narrative_drag=geo.compression,
            zone=self._determine_zone(geo.dimensions),
            atmosphere="NEUTRAL",
            flow_state=self._determine_flow(smoothed_voltage, geo.coherence))
        self.last_physics_packet = PhysicsPacket(energy=energy, matter=matter, space=space)
        packet_dict = self.last_physics_packet.to_dict()
        if hasattr(self.events, "publish"):
            self.events.publish("PHYSICS_CALCULATED", packet_dict)
        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    def _tally_categories(self, clean_words: List[str]) -> Counter:
        counts = Counter()
        solvents = LexiconService.SOLVENTS if hasattr(LexiconService, 'SOLVENTS') else set()
        for w in clean_words:
            if w in solvents:
                counts["solvents"] += 1
                continue
            cats = LexiconService.get_categories_for_word(w)
            if cats:
                counts.update(cats)
            else:
                flavor, conf = LexiconService.taste(w)
                if flavor and conf > 0.5:
                    counts[flavor] += 1
        return counts

    def _calculate_graph_mass(self, words: List[str], graph: Optional[Dict]) -> float:
        if not graph: return 0.0
        total_mass = 0.0
        existing_nodes = [w for w in words if w in graph]
        for w in existing_nodes:
            edges = graph[w].get("edges", {})
            node_mass = min(50.0, len(edges) * 1.5)
            total_mass += node_mass
        return total_mass

    def _calculate_metrics(self, text: str, counts: Dict[str, int]) -> Tuple[float, float]:
        length = len(text)
        if length == 0: return 0.0, 0.0
        scalar = getattr(BoneConfig.PHYSICS, "TEXT_LENGTH_SCALAR", 1500.0)
        raw_chaos = (length / scalar)
        solvents = counts.get("solvents", 0)
        solvent_density = solvents / max(1.0, length / 5.0)
        glue_factor = min(1.0, solvent_density * 2.0)
        e_metric = min(1.0, raw_chaos * (1.0 - (glue_factor * 0.8)))
        structure_chars = sum(1 for char in text if char in '!?%@#$;,')
        heavy_words = counts.get("heavy", 0) + counts.get("constructive", 0) + counts.get("sacred", 0)
        structure_score = structure_chars + (heavy_words * 2)
        beta_index = min(1.0, math.log1p(structure_score + 1) / math.log1p(length * 0.1 + 1))
        if length < 50:
            beta_index *= (length / 50.0)
        return round(e_metric, 3), round(beta_index, 3)

    def _determine_flow(self, v: float, k: float) -> str:
        volt_flow = getattr(BoneConfig.PHYSICS, "VOLTAGE_HIGH", 12.0)
        kappa_strong = 0.8
        if v > volt_flow and k > kappa_strong:
            return "SUPERCONDUCTIVE"
        if v > 10.0:
            return "TURBULENT"
        return "LAMINAR"

    def _determine_zone(self, vector: Dict[str, float]) -> str:
        if not vector: return "COURTYARD"
        dom = max(vector, key=vector.get)
        if dom in ["PSI", "DEL"]: return "AERIE"
        if dom in ["STR", "PHI"]: return "THE_FORGE"
        if dom in ["ENT", "VEL"]: return "THE_MUD"
        return "COURTYARD"

class SurfaceTension:
    def __init__(self):
        pass

    def audit_hubris(self, physics: Dict[str, Any]) -> Tuple[bool, str, str]:
        voltage = physics.get("voltage", 0.0)
        coherence = physics.get("kappa", 0.5)
        volt_crit = getattr(BoneConfig.PHYSICS, "VOLTAGE_CRITICAL", 15.0)
        volt_flow = getattr(BoneConfig.PHYSICS, "VOLTAGE_HIGH", 12.0)
        if voltage > (volt_crit + 5.0) and coherence < 0.4:
            return True, f"⚠️ HUBRIS DETECTED: Voltage ({voltage:.1f}v) exceeds structural integrity. Wings melting.", "ICARUS_CRASH"
        if voltage > volt_flow and coherence > 0.8:
            return True, "🌊 SURFACE TENSION OPTIMAL: Entering Flow State.", "FLOW_BOOST"
        return False, "", ""

class ChromaScope:
    def modulate(self, text: str, vector: Dict[str, float]) -> str:
        if not vector: return f"{Prisma.GRY}{text}{Prisma.RST}"
        sorted_vecs = sorted(vector.items(), key=lambda x: x[1], reverse=True)
        if not sorted_vecs: return f"{Prisma.GRY}{text}{Prisma.RST}"
        primary_dim = sorted_vecs[0][0]
        if primary_dim in TRIGRAM_MAP:
            selected_color = TRIGRAM_MAP[primary_dim][3]
        else:
            selected_color = Prisma.GRY
        return f"{selected_color}{text}{Prisma.RST}"

class ZoneInertia:
    def __init__(self, inertia=0.7):
        self.inertia = inertia
        self.min_dwell = getattr(BoneConfig.PHYSICS, "ZONE_MIN_DWELL", 2)
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector: Optional[Tuple[float, float, float]] = None
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0
        return self.is_anchored

    def stabilize(self, proposed_zone: str, physics: Dict[str, Any], cosmic_state: Tuple[str, float, str]) -> Tuple[str, Optional[str]]:
        beta = physics.get("beta_index", 1.0)
        truth = physics.get("truth_ratio", 0.5)
        grav_pull = 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0
        current_vec = (beta, truth, grav_pull)
        self.dwell_counter += 1
        pressure = 0.0
        if self.last_vector:
            a1, a2, a3 = current_vec
            b1, b2, b3 = self.last_vector
            dist = math.sqrt((a1-b1)**2 + (a2-b2)**2 + (a3-b3)**2)
            similarity = max(0.0, 1.0 - (dist / 2.0))
            pressure = (1.0 - similarity)
        if self.is_anchored:
            return self._handle_anchored_state(proposed_zone, pressure)
        if proposed_zone == self.current_zone:
            self.dwell_counter = 0
            self.last_vector = current_vec
            return proposed_zone, None
        if self.dwell_counter < self.min_dwell:
            return self.current_zone, None
        return self._attempt_migration(proposed_zone, pressure)

    def _handle_anchored_state(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        if proposed_zone == self.current_zone:
            self.strain_gauge = max(0.0, self.strain_gauge - 0.1)
            return self.current_zone, None
        self.strain_gauge += pressure
        limit = 2.5
        if self.strain_gauge > limit:
            self.is_anchored = False
            self.strain_gauge = 0.0
            self.current_zone = proposed_zone
            return proposed_zone, f"{Prisma.RED}⚡ SNAP! The narrative current was too strong. Anchor failed.{Prisma.RST}"
        return self.current_zone, f"{Prisma.OCHRE}⚓ ANCHORED: Resisting drift to '{proposed_zone}' (Strain {self.strain_gauge:.1f}/{limit}){Prisma.RST}"

    def _attempt_migration(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        change_probability = (1.0 - self.inertia) + pressure
        if proposed_zone in ["AERIE", "THE_FORGE"]: change_probability += 0.2
        if random.random() < change_probability:
            old_zone = self.current_zone
            self.current_zone = proposed_zone
            self.dwell_counter = 0
            return self.current_zone, f"{Prisma.CYN}>>> MIGRATION: {old_zone} -> {proposed_zone}.{Prisma.RST}"
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(cosmic_drag_penalty: float, current_zone: str) -> float:
        if current_zone == "AERIE" and cosmic_drag_penalty > 0:
            return cosmic_drag_penalty * 0.3
        return cosmic_drag_penalty

class CosmicDynamics:
    def __init__(self):
        self.voltage_history: Deque[float] = deque(maxlen=20)
        self.cached_wells: Dict = {}
        self.cached_hubs: Dict = {}
        self.last_scan_tick: int = 0
        self.SCAN_INTERVAL: int = 10

    def commit(self, voltage: float):
        self.voltage_history.append(voltage)

    def check_gravity(self, current_drift: float, psi: float) -> Tuple[float, List[str]]:
        logs = []
        new_drag = current_drift
        drag_floor = getattr(BoneConfig.PHYSICS, "DRAG_FLOOR", 1.0)
        if new_drag < drag_floor:
            new_drag += 0.05
        if psi > 0.5:
            reduction = (psi - 0.5) * 0.2
            new_drag = max(0.0, new_drag - reduction)
        CRITICAL_DRIFT = getattr(BoneConfig.PHYSICS, "DRAG_CRITICAL", 8.0)
        if new_drag > CRITICAL_DRIFT:
            if random.random() < 0.3:
                logs.append(f"{Prisma.GRY}⚓ GRAVITY: The narrative is heavy. (Drag {new_drag:.1f}){Prisma.RST}")
        return new_drag, logs

    def analyze_orbit(self, network: Any, clean_words: List[str]) -> Tuple[str, float, str]:
        if not clean_words or not network or not hasattr(network, 'graph') or not network.graph:
            return "VOID_DRIFT", 3.0, "VOID: Deep Space. No connection."
        current_time = int(time.time())
        if not self.cached_wells or (current_time - self.last_scan_tick) > self.SCAN_INTERVAL:
            gravity_wells, geodesic_hubs = self._scan_network_mass(network)
            self.cached_wells = gravity_wells
            self.cached_hubs = geodesic_hubs
            self.last_scan_tick = current_time
        else:
            gravity_wells = self.cached_wells
            geodesic_hubs = self.cached_hubs
        basin_pulls, active_filaments = self._calculate_pull(clean_words, network, gravity_wells)
        if sum(basin_pulls.values()) == 0:
            return self._handle_void_state(clean_words, geodesic_hubs)
        return self._resolve_orbit(basin_pulls, active_filaments, len(clean_words), gravity_wells)

    @staticmethod
    def _scan_network_mass(network) -> Tuple[Dict, Dict]:
        gravity_wells = {}
        geodesic_hubs = {}
        well_threshold = getattr(BoneConfig, "GRAVITY_WELL_THRESHOLD", 15.0)
        geo_strength = getattr(BoneConfig, "GEODESIC_STRENGTH", 10.0)
        for node in network.graph:
            mass = network.calculate_mass(node)
            if mass >= well_threshold:
                gravity_wells[node] = mass
            elif mass >= geo_strength:
                geodesic_hubs[node] = mass
        return gravity_wells, geodesic_hubs

    @staticmethod
    def _calculate_pull(words, network, gravity_wells) -> Tuple[Dict, int]:
        basin_pulls = {k: 0.0 for k in gravity_wells}
        active_filaments = 0
        for w in words:
            if w in gravity_wells:
                basin_pulls[w] += gravity_wells[w] * 2.0
                active_filaments += 1
            for well in gravity_wells:
                if w in network.graph.get(well, {}).get("edges", {}):
                    basin_pulls[well] += gravity_wells[well] * 0.5
                    active_filaments += 1
        return basin_pulls, active_filaments

    @staticmethod
    def _handle_void_state(words, geodesic_hubs) -> Tuple[str, float, str]:
        for w in words:
            if w in geodesic_hubs:
                return "PROTO_COSMOS", 1.0, f"NEBULA: Floating near '{w.upper()}' (Mass {int(geodesic_hubs[w])}). Not enough mass for orbit."
        return "VOID_DRIFT", 3.0, "VOID: Drifting outside the filaments."

    @staticmethod
    def _resolve_orbit(basin_pulls, active_filaments, word_count, gravity_wells) -> Tuple[str, float, str]:
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        lagrange_tol = getattr(BoneConfig, "LAGRANGE_TOLERANCE", 2.0)
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < lagrange_tol:
                return "LAGRANGE_POINT", 0.0, f"LAGRANGE: Caught between '{primary_node.upper()}' and '{secondary_node.upper()}'"
        flow_ratio = active_filaments / max(1, word_count)
        well_threshold = getattr(BoneConfig, "GRAVITY_WELL_THRESHOLD", 15.0)
        if flow_ratio > 0.5 and primary_str < (well_threshold * 2):
            return "WATERSHED_FLOW", 0.0, f"FLOW: Streaming towards '{primary_node.upper()}'"
        return "ORBITAL", 0.0, f"ORBIT: Circling '{primary_node.upper()}' (Mass {int(gravity_wells[primary_node])})"

def apply_somatic_feedback(physics_packet: PhysicsPacket, qualia: Any) -> PhysicsPacket:
    feedback = physics_packet.snapshot()
    tone_effects = {"Urgent": {"velocity": 0.3, "narrative_drag": -0.5, "voltage": 0.5},
        "Strained": {"narrative_drag": 1.2, "voltage": -0.3, "kappa": -0.1},
        "Vibrating": {"entropy": 0.2, "voltage": 0.2, "psi": 0.1},
        "Resonant": {"valence": 0.3, "beta_index": 0.1, "kappa": 0.2},
        "Steady": {}}
    effects = tone_effects.get(qualia.tone, {})
    for key, delta in effects.items():
        if hasattr(feedback, key):
            current = getattr(feedback, key)
            setattr(feedback, key, current + delta)
    if "Gut Tightening" in qualia.somatic_sensation:
        feedback.narrative_drag += 0.7
    if "Electric Vibration" in qualia.somatic_sensation:
        feedback.voltage += 0.8
    if "Golden Glow" in qualia.somatic_sensation:
        feedback.valence += 0.5
        feedback.psi += 0.2
    volt_crit = getattr(BoneConfig.PHYSICS, "VOLTAGE_CRITICAL", 15.0)
    drag_floor = getattr(BoneConfig.PHYSICS, "DRAG_FLOOR", 1.0)
    drag_halt = getattr(BoneConfig.PHYSICS, "DRAG_HALT", 10.0)
    feedback.voltage = max(0.0, min(feedback.voltage, volt_crit * 1.5))
    feedback.narrative_drag = max(drag_floor, min(feedback.narrative_drag, drag_halt))
    return feedback

class CycleStabilizer:
    def __init__(self, events_ref, governor_ref):
        self.events = events_ref
        self.governor = governor_ref
        self.last_tick_time = time.time()
        self.pending_drag = 0.0
        self.manifolds = getattr(BoneConfig.PHYSICS, "MANIFOLDS", {})
        self.HARD_FUSE_VOLTAGE = 100.0
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("DOMESTICATION_PENALTY", self._on_domestication_penalty)

    def _on_domestication_penalty(self, payload):
        amount = payload.get("drag_penalty", 0.0)
        self.pending_drag += amount

    def stabilize(self, ctx: CycleContext, current_phase: str):
        p = ctx.physics
        if p.voltage >= self.HARD_FUSE_VOLTAGE:
            ctx.log(f"{Prisma.RED}⚡ FUSE BLOWN: Voltage exceeded {self.HARD_FUSE_VOLTAGE}V. Hard Reset Initiated.{Prisma.RST}")
            p.voltage = 10.0
            p.narrative_drag = 5.0
            p.flow_state = "SAFE_MODE"
            ctx.record_flux(current_phase, "voltage", self.HARD_FUSE_VOLTAGE, 10.0, "FUSE_BLOWN")
            return True
        if self.pending_drag > 0:
            if isinstance(ctx.physics, dict):
                ctx.physics["narrative_drag"] = ctx.physics.get("narrative_drag", 0.0) + self.pending_drag
            else:
                ctx.physics.narrative_drag += self.pending_drag
            ctx.log(
                f"{Prisma.GRY}⚖️ DOMESTICATION: The collar feels heavy. (Drag +{self.pending_drag:.1f}){Prisma.RST}")
            self.pending_drag = 0.0
        now = time.time()
        dt = max(0.001, min(1.0, now - self.last_tick_time))
        self.last_tick_time = now
        manifold = getattr(p, "manifold", "DEFAULT")
        if manifold not in self.manifolds:
            manifold = "DEFAULT"
        cfg = self.manifolds[manifold]
        target_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        flow_state = getattr(p, "flow_state", "LAMINAR")
        if flow_state in ["SUPERCONDUCTIVE", "FLOW_BOOST"]:
            target_v = p.voltage
            cfg["drag"] = max(0.1, cfg["drag"] * 0.5)
        else:
            target_v = cfg["voltage"]
        self.governor.recalibrate(target_v, cfg["drag"])
        v_force, d_force = self.governor.regulate(p, dt=dt)
        corrections = False
        if abs(v_force) > 0.01:
            p.voltage = max(0.0, min(getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0), p.voltage + v_force))
            if abs(v_force) > 0.5:
                ctx.record_flux(current_phase, "voltage", p.voltage - v_force, p.voltage, "PID_CORRECTION")
            corrections = True
            DRAG_DEADBAND = 0.05
            if abs(d_force) > DRAG_DEADBAND:
                p.narrative_drag = max(0.0, p.narrative_drag + d_force)
            if abs(d_force) > 0.5:
                ctx.record_flux(current_phase, "narrative_drag", p.narrative_drag - d_force, p.narrative_drag, "PID_CORRECTION")
            corrections = True
        return corrections