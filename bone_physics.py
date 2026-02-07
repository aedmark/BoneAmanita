""" bone_physics.py
 'Gravity is just a habit that space-time hasn't been able to break.' """

import math
import random
from typing import Dict, List, Any, Tuple, Optional, Deque
from collections import Counter, deque
from dataclasses import dataclass, field
from bone_lexicon import TheLexicon
from bone_core import Prisma, BoneConfig, PhysicsPacket, CycleContext


class PhysicsConstants:
    VOLT_CRITICAL = 20.0
    VOLT_MANIC = 12.0
    VOLT_FLOW = 15.0
    DRAG_HALT = 10.0
    DRAG_HEAVY = 6.0
    DRAG_FLOOR = 0.1
    KAPPA_STRONG = 0.8
    KAPPA_WEAK = 0.4
    WEIGHT_HEAVY = 2.0
    WEIGHT_EXPLOSIVE = 3.0
    WEIGHT_CONSTRUCTIVE = 1.5
    KINETIC_GAIN = 1.0
    SIGNAL_DRAG_MULTIPLIER = 1.0
    SHAPLEY_MASS_THRESHOLD = 5.0
    MAX_SOLVENT_TOLERANCE = 40.0
    TEXT_LENGTH_SCALAR = 1500.0
    ATP_STARVATION = 5.0
    ZONE_INERTIA_DEFAULT = 0.7
    ZONE_MIN_DWELL = 2
    ANCHOR_STRAIN_LIMIT = 2.5
    GRAVITY_WELL_THRESHOLD = 10.0
    GEODESIC_STRENGTH = 5.0
    LAGRANGE_TOLERANCE = 2.0

TRIGRAM_MAP: Dict[str, Tuple[str, str, str, str]] = {
    "VEL": ("☳", "ZHEN",  "Thunder",  Prisma.GRN),
    "STR": ("☶", "GEN",   "Mountain", Prisma.SLATE),
    "ENT": ("☵", "KAN",   "Water",    Prisma.BLU),
    "PHI": ("☲", "LI",    "Fire",     Prisma.RED),
    "PSI": ("☰", "QIAN",  "Heaven",   Prisma.WHT),
    "BET": ("☴", "XUN",   "Wind",     Prisma.CYN),
    "E":   ("☷", "KUN",   "Earth",    Prisma.OCHRE),
    "DEL": ("☱", "DUI",   "Lake",     Prisma.MAG)}

def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    intersection = set(vec_a.keys()) & set(vec_b.keys())
    numerator = sum(vec_a[k] * vec_b[k] for k in intersection)
    sum1 = sum(vec_a[k] ** 2 for k in vec_a.keys())
    sum2 = sum(vec_b[k] ** 2 for k in vec_b.keys())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator: return 0.0
    return numerator / denominator

def resolve_trigram(vector: Dict[str, float]) -> Dict[str, Any]:
    if not vector:
        return {"symbol": "☷", "name": "KUN", "color": Prisma.OCHRE, "vector": "E"}
    dominant_vec = max(vector, key=vector.get)
    if vector[dominant_vec] < 0.2:
        dominant_vec = "E"
    symbol, name, concept, color = TRIGRAM_MAP.get(dominant_vec, TRIGRAM_MAP["E"])
    return {
        "symbol": symbol,
        "name": name,
        "concept": concept,
        "color": color,
        "vector": dominant_vec}

@dataclass
class GeodesicVector:
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]

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
        return {
            "heavy": float(counts.get("heavy", 0)),
            "kinetic": float(counts.get("kinetic", 0)),
            "constructive": float(counts.get("constructive", 0)),
            "abstract": float(counts.get("abstract", 0)),
            "play": float(counts.get("play", 0)),
            "social": float(counts.get("social", 0)),
            "explosive": float(counts.get("explosive", 0))}

    @staticmethod
    def _calculate_forces(masses: Dict[str, float], counts: Dict[str, int], volume: int) -> Dict[str, float]:
        pc = PhysicsConstants
        total_kinetic = masses["kinetic"] + masses["explosive"]
        raw_tension_mass = (
                (masses["heavy"] * pc.WEIGHT_HEAVY) +
                (total_kinetic * pc.WEIGHT_EXPLOSIVE) +
                (masses["constructive"] * pc.WEIGHT_CONSTRUCTIVE))
        tension = round(((raw_tension_mass / volume) * 25.0) * pc.KINETIC_GAIN, 2)
        shear_rate = total_kinetic / volume
        raw_friction = (
                (counts.get("solvents", 0) * 0.2) +
                (counts.get("suburban", 0) * 2.0) +
                (masses["heavy"] * 2.5))
        dynamic_viscosity = raw_friction / (1.0 + (shear_rate * 2.0))
        kinetic_lift = total_kinetic * 0.5
        if masses["heavy"] > 0:
            kinetic_lift /= (masses["heavy"] * 0.5 + 1.0)
        lift = (masses["play"] * 2.5) + kinetic_lift
        raw_compression = ((dynamic_viscosity / volume) * 10.0) - ((lift / volume) * 10.0)
        compression = round(max(-5.0, min(pc.DRAG_HALT, raw_compression * pc.SIGNAL_DRAG_MULTIPLIER)), 2)
        structural_mass = masses["heavy"] + masses["constructive"]
        coherence = min(1.0, structural_mass / max(1, pc.SHAPLEY_MASS_THRESHOLD))
        abstraction = min(1.0, (masses["abstract"] / volume) + 0.2)

        return {
            "tension": tension,
            "compression": compression,
            "coherence": round(coherence, 3),
            "abstraction": round(abstraction, 2)}

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        def norm(val): return min(1.0, val / volume)
        return {
            "VEL": norm(masses["kinetic"] * 2.0 - forces['compression']),
            "STR": norm(masses["heavy"] * 2.0 + masses["constructive"]),
            "ENT": norm(counts.get("antigen", 0) * 3.0),
            "PHI": norm(masses["heavy"] + masses["kinetic"]),
            "PSI": forces['abstraction'],
            "BET": norm(masses["social"] * 2.0),
            "DEL": norm(masses["play"] * 3.0),
            "E":   norm(counts.get("solvents", 0))}

class TheGatekeeper:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.lex = engine_ref.mind.lex
        self.mem = engine_ref.mind.mem

    def check_entry(self, ctx: CycleContext) -> Tuple[bool, Optional[Dict]]:
        phys = ctx.physics
        if not self._check_thermodynamics(ctx):
            return False, self._pack_refusal(ctx, "DARK_SYSTEM", "Energy critical. The inputs dissolve into the void.")
        if not self._audit_tangibility(phys):
            return False, self._pack_refusal(ctx, "TANGIBILITY_FAIL", self._get_tangibility_msg())
        if phys.counts.get("antigen", 0) > 2:
            return False, self._pack_refusal(ctx, "TOXICITY", f"{Prisma.RED}IMMUNE REACTION: Input rejected as pathogenic.{Prisma.RST}")
        text = ctx.input_text
        if "```" in text or "{{" in text or "}}" in text:
            return False, self._pack_refusal(ctx, "SYNTAX_ERR", f"{Prisma.RED}The mechanism jams. Syntax anomaly detected.{Prisma.RST}")
        if len(text) > 1000:
            return False, self._pack_refusal(ctx, "OVERLOAD", f"{Prisma.OCHRE}Input too long. Compress your thought.{Prisma.RST}")
        return True, None

    def _check_thermodynamics(self, ctx) -> bool:
        threshold = PhysicsConstants.ATP_STARVATION * 0.5
        if hasattr(ctx, "bio_snapshot") and ctx.bio_snapshot:
            return ctx.bio_snapshot.get("atp", 10.0) > threshold
        if hasattr(self.eng, "bio") and hasattr(self.eng.bio, "mito"):
            return self.eng.bio.mito.state.atp_pool > threshold
        return True

    def _audit_tangibility(self, phys: PhysicsPacket) -> bool:
        if phys.truth_ratio > 0.8: return True
        mass_score = (
                phys.counts.get("heavy", 0) +
                phys.counts.get("kinetic", 0) +
                phys.counts.get("constructive", 0) +
                (phys.counts.get("play", 0) * 0.5))
        ether_score = phys.counts.get("abstract", 0) + phys.counts.get("sacred", 0)
        if ether_score > 2 and phys.kappa > 0.6:
            return True
        density = mass_score / max(1, len(phys.clean_words))
        required = 0.15 if self.eng.stamina > 15.0 else 0.05
        return density >= required

    def _audit_safety(self, words: List[str]) -> bool:
        cursed = self.lex.get("cursed")
        return any(w in cursed for w in words)

    def _pack_refusal(self, ctx, type_str, ui_msg):
        return {
            "type": type_str,
            "ui": ui_msg,
            "logs": ctx.logs + [ui_msg],
            "metrics": self.eng.get_metrics()}

    def _get_tangibility_msg(self):
        suggestion = random.choice(["stone", "iron", "bone", "mud"])
        return (f"{Prisma.OCHRE}TANGIBILITY VIOLATION: Concepts too airy.{Prisma.RST}\n"
                f"   {Prisma.GRY}Anchor them with mass (e.g., {suggestion}).{Prisma.RST}")

class QuantumObserver:
    def __init__(self, events):
        self.events = events
        self.voltage_history: Deque[float] = deque(maxlen=5)
        self.last_physics_packet: Optional[PhysicsPacket] = None

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = TheLexicon.clean(text)
        counts = self._tally_categories(clean_words)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts)
        self.voltage_history.append(geo.tension)
        smoothed_voltage = round(sum(self.voltage_history) / len(self.voltage_history), 2)
        e_metric, beta_val = self._calculate_metrics(text, counts)
        valence = TheLexicon.get_valence(clean_words)
        graph_mass = self._calculate_graph_mass(clean_words, graph)
        packet_data = {
            "voltage": smoothed_voltage,
            "narrative_drag": geo.compression,
            "valence": valence,
            "repetition": 0.0,
            "atmosphere": "NEUTRAL",
            "clean_words": clean_words,
            "counts": counts,
            "vector": geo.dimensions,
            "flow_state": self._determine_flow(smoothed_voltage, geo.coherence),
            "zone": self._determine_zone(geo.dimensions),
            "truth_ratio": 0.5,
            "raw_text": text,
            "antigens": counts.get("antigen", 0),
            "perfection_streak": 0,
            "turbulence": 0.0,
            "entropy": e_metric,
            "beta_index": beta_val,
            "mass": round(graph_mass, 1),
            "velocity": 0.0,
            "psi": geo.abstraction,
            "kappa": geo.coherence}
        self.last_physics_packet = PhysicsPacket(**packet_data)
        if hasattr(self.events, "publish"):
            self.events.publish("PHYSICS_CALCULATED", packet_data)
        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    def _tally_categories(self, clean_words: List[str]) -> Counter:
        counts = Counter()
        solvents = TheLexicon.SOLVENTS if hasattr(TheLexicon, 'SOLVENTS') else set()
        for w in clean_words:
            if w in solvents:
                counts["solvents"] += 1
                continue
            cats = TheLexicon.get_categories_for_word(w)
            if cats:
                counts.update(cats)
            else:
                flavor, conf = TheLexicon.taste(w)
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
        pc = PhysicsConstants
        raw_chaos = (length / pc.TEXT_LENGTH_SCALAR)
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
        if v > PhysicsConstants.VOLT_FLOW and k > PhysicsConstants.KAPPA_STRONG:
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
        self.HUMBLE_PHRASES = [
            "Based on the available data...",
            "As I understand the current coordinates...",
            "From a structural perspective...",
            "This is a probabilistic estimation...",
            "I could be misinterpreting the vector..."]

    def audit_hubris(self, physics: Dict[str, Any]) -> Tuple[bool, str, str]:
        voltage = physics.get("voltage", 0.0)
        coherence = physics.get("kappa", 0.5)
        pc = PhysicsConstants
        if voltage > (pc.VOLT_CRITICAL + 5.0) and coherence < pc.KAPPA_WEAK:
            return True, f"⚠️ HUBRIS DETECTED: Voltage ({voltage:.1f}v) exceeds structural integrity. Wings melting.", "ICARUS_CRASH"
        if voltage > pc.VOLT_FLOW and coherence > pc.KAPPA_STRONG:
            return True, "🌊 SURFACE TENSION OPTIMAL: Entering Flow State.", "FLOW_BOOST"
        return False, "", ""

    def check_boundary(self, text: str, voltage: float) -> Tuple[bool, str, Optional[str]]:
        if voltage > PhysicsConstants.VOLT_CRITICAL and random.random() < 0.3:
            prefix = random.choice(self.HUMBLE_PHRASES)
            return True, f"{prefix} {text}", "VOLTAGE_DAMPENER"
        return False, text, None

class ChromaScope:
    def modulate(self, text: str, vector: Dict[str, float]) -> str:
        if not vector:
            return f"{Prisma.GRY}{text}{Prisma.RST}"

        sorted_vecs = sorted(vector.items(), key=lambda x: x[1], reverse=True)
        if not sorted_vecs:
            return f"{Prisma.GRY}{text}{Prisma.RST}"
        primary_dim = sorted_vecs[0][0]
        if primary_dim in TRIGRAM_MAP:
            selected_color = TRIGRAM_MAP[primary_dim][3]
        else:
            selected_color = Prisma.GRY
        if "sorry" in text.lower():
            return f"{Prisma.OCHRE}{text}{Prisma.RST}"
        return f"{selected_color}{text}{Prisma.RST}"

class ZoneInertia:
    def __init__(self, inertia=0.7):
        self.inertia = inertia
        self.min_dwell = PhysicsConstants.ZONE_MIN_DWELL
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
            dist = sum((a - b) ** 2 for a, b in zip(current_vec, self.last_vector)) ** 0.5
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
        limit = PhysicsConstants.ANCHOR_STRAIN_LIMIT
        if self.strain_gauge > limit:
            self.is_anchored = False
            self.strain_gauge = 0.0
            self.current_zone = proposed_zone
            return proposed_zone, f"{Prisma.RED}⚡ SNAP! The narrative current was too strong. Anchor failed.{Prisma.RST}"
        return self.current_zone, f"{Prisma.OCHRE}⚓ ANCHORED: Resisting drift to '{proposed_zone}' (Strain {self.strain_gauge:.1f}/{limit}){Prisma.RST}"

    def _attempt_migration(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        change_probability = (1.0 - self.inertia) + pressure

        if proposed_zone in ["AERIE", "THE_FORGE"]:
            change_probability += 0.2
        if random.random() < change_probability:
            old_zone = self.current_zone
            self.current_zone = proposed_zone
            self.dwell_counter = 0
            return self.current_zone, f"{Prisma.CYN}>>> MIGRATION: {old_zone} -> {proposed_zone}.{Prisma.RST}"
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(cosmic_drag_penalty: float, current_zone: str) -> float:
        aerie_flow_coefficient = 0.3
        if current_zone == "AERIE":
            if cosmic_drag_penalty > 0:
                return cosmic_drag_penalty * aerie_flow_coefficient
        return cosmic_drag_penalty

class CosmicDynamics:
    def __init__(self):
        self.voltage_history: Deque[float] = deque(maxlen=20)

    def commit(self, voltage: float):
        self.voltage_history.append(voltage)

    @staticmethod
    def analyze_orbit(network: Any, clean_words: List[str]) -> Tuple[str, float, str]:
        if not clean_words or not network.graph:
            return "VOID_DRIFT", 3.0, "VOID: Deep Space. No connection."
        gravity_wells, geodesic_hubs = CosmicDynamics._scan_network_mass(network)
        basin_pulls, active_filaments = CosmicDynamics._calculate_pull(clean_words, network, gravity_wells)
        if sum(basin_pulls.values()) == 0:
            return CosmicDynamics._handle_void_state(clean_words, geodesic_hubs)
        return CosmicDynamics._resolve_orbit(basin_pulls, active_filaments, len(clean_words), gravity_wells)

    @staticmethod
    def _scan_network_mass(network) -> Tuple[Dict, Dict]:
        gravity_wells = {}
        geodesic_hubs = {}
        for node in network.graph:
            mass = network.calculate_mass(node)
            if mass >= PhysicsConstants.GRAVITY_WELL_THRESHOLD:
                gravity_wells[node] = mass
            elif mass >= PhysicsConstants.GEODESIC_STRENGTH:
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
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < PhysicsConstants.LAGRANGE_TOLERANCE:
                return (
                    "LAGRANGE_POINT",
                    0.0,
                    f"LAGRANGE: Caught between '{primary_node.upper()}' and '{secondary_node.upper()}'")
        flow_ratio = active_filaments / max(1, word_count)
        if flow_ratio > 0.5 and primary_str < (PhysicsConstants.GRAVITY_WELL_THRESHOLD * 2):
            return (
                "WATERSHED_FLOW",
                0.0,
                f"FLOW: Streaming towards '{primary_node.upper()}'")
        return "ORBITAL", 0.0, f"ORBIT: Circling '{primary_node.upper()}' (Mass {int(gravity_wells[primary_node])})"

def apply_somatic_feedback(physics_packet: PhysicsPacket, qualia: Any) -> PhysicsPacket:
    feedback = physics_packet.snapshot()
    tone_effects = {
        "Urgent": {"velocity": 0.3, "narrative_drag": -0.5, "voltage": 0.5},
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
    pc = PhysicsConstants
    feedback.voltage = max(0.0, min(feedback.voltage, pc.VOLT_CRITICAL * 1.5))
    feedback.narrative_drag = max(pc.DRAG_FLOOR, min(feedback.narrative_drag, pc.DRAG_HALT))
    return feedback