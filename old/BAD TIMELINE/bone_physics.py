""" bone_physics.py
 'Gravity is just a habit that space-time hasn't been able to break.' """

import math, re, random
from typing import Dict, List, Any, Tuple, Optional, Union
from collections import Counter, deque
from dataclasses import dataclass, field
from bone_lexicon import TheLexicon
from bone_bus import Prisma, BoneConfig, PhysicsPacket, CycleContext

def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    intersection = set(vec_a.keys()) & set(vec_b.keys())
    numerator = sum(vec_a[k] * vec_b[k] for k in intersection)
    sum1 = sum(vec_a[k] ** 2 for k in vec_a.keys())
    sum2 = sum(vec_b[k] ** 2 for k in vec_b.keys())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator: return 0.0
    return numerator / denominator

SOLVENT_WORDS = {'i', 'you', 'said', 'the', 'and', 'was', 'a', 'is', 'it'}
MAX_SOLVENT_TOLERANCE = 40.0
TEXT_LENGTH_SCALAR = 1500.0

class TheGatekeeper:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.lex = engine_ref.mind.lex
        self.mem = engine_ref.mind.mem
        self.bureaucracy_active = False

    def check_entry(self, ctx: CycleContext) -> Tuple[bool, Optional[Dict]]:
        phys = ctx.physics
        if not self._check_thermodynamics(ctx):
            return False, self._pack_refusal(ctx, "DARK_SYSTEM", "Energy critical. The inputs dissolve into the void.")
        if self._audit_bureaucracy(phys):
            return False, self._pack_refusal(ctx, "VOGON_HOLD", self._get_bureaucracy_msg(ctx.input_text))
        if not self._audit_tangibility(phys):
            return False, self._pack_refusal(ctx, "TANGIBILITY_FAIL", self._get_tangibility_msg(phys))
        if phys.counts.get("antigen", 0) > 2:
            return False, self._pack_refusal(ctx, "TOXICITY", f"{Prisma.RED}IMMUNE REACTION: Input rejected as pathogenic.{Prisma.RST}")
        if self._audit_safety(ctx.clean_words):
            return False, self._pack_refusal(ctx, "SAFETY_LOCK", f"{Prisma.GRY}The mechanism jams. Forbidden glyphs detected.{Prisma.RST}")
        return True, None

    def _check_thermodynamics(self, ctx):
        return getattr(self.eng.bio.mito.state, "atp_pool", 10.0) > 1.0

    def _audit_bureaucracy(self, phys):
        return phys.voltage < 5.0 and random.randint(1, 50) == 42

    def _audit_tangibility(self, phys):
        if phys.truth_ratio > 0.8: return True
        density = (phys.counts.get("heavy", 0) + phys.counts.get("kinetic", 0)) / max(1, len(phys.clean_words))
        required = 0.15 if self.eng.stamina > 15.0 else 0.05
        return density >= required

    def _audit_safety(self, words):
        cursed = self.lex.get("cursed")
        return any(w in cursed for w in words)

    def _pack_refusal(self, ctx, type_str, ui_msg):
        return {
            "type": type_str,
            "ui": ui_msg,
            "logs": ctx.logs + [ui_msg],
            "metrics": self.eng.get_metrics()}

    def _get_bureaucracy_msg(self, text):
        return (f"{Prisma.OCHRE}🛑 BUREAUCRATIC HALT (Form 27B/6 Missing){Prisma.RST}\n"
                f"   Processing of '{text}' suspended pending review.")

    def _get_tangibility_msg(self, phys):
        suggestion = random.choice(["stone", "iron", "bone", "mud"])
        return (f"{Prisma.OCHRE}TANGIBILITY VIOLATION: Concepts too airy.{Prisma.RST}\n"
                f"   {Prisma.GRY}Anchor them with mass (e.g., {suggestion}).{Prisma.RST}")

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

@dataclass
class GeodesicVector:
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]

class GeodesicEngine:
    @staticmethod
    def collapse_wavefunction(clean_words: List[str], counts: Dict[str, int], config) -> GeodesicVector:
        volume = max(1, len(clean_words))
        mass_heavy = counts.get("heavy", 0)
        mass_kinetic = counts.get("explosive", 0) + counts.get("kinetic", 0)
        mass_constructive = counts.get("constructive", 0)
        mass_abstract = counts.get("abstract", 0)
        mass_play = counts.get("play", 0)
        mass_social = counts.get("suburban", 0) + counts.get("solvents", 0)
        raw_tension_mass = (
                (mass_heavy * config.PHYSICS.WEIGHT_HEAVY) +
                (mass_kinetic * config.PHYSICS.WEIGHT_EXPLOSIVE) +
                (mass_constructive * config.PHYSICS.WEIGHT_CONSTRUCTIVE))
        tension = round(((raw_tension_mass / volume) * 25.0) * config.KINETIC_GAIN, 2)
        raw_friction = (counts.get("solvents", 0) * 0.2) + (counts.get("suburban", 0) * 2.0)
        lift = (mass_play * 1.5) + (mass_kinetic * 0.5)
        raw_compression = ((raw_friction / volume) * 10.0) - ((lift / volume) * 10.0)
        compression = round(max(-5.0, min(config.PHYSICS.DRAG_HALT, raw_compression * config.SIGNAL_DRAG_MULTIPLIER)), 2)
        structural_mass = mass_heavy + mass_constructive
        coherence = min(1.0, structural_mass / max(1, config.SHAPLEY_MASS_THRESHOLD))
        abstraction = min(1.0, (mass_abstract / volume) + 0.2)

        def norm(val): return min(1.0, val / volume)
        dimensions = {
            "VEL": norm(mass_kinetic * 2.0 - compression),
            "STR": norm(mass_heavy * 2.0 + mass_constructive),
            "ENT": norm(counts.get("antigen", 0) * 3.0),
            "PHI": norm(mass_heavy + mass_kinetic),
            "PSI": abstraction,
            "BET": norm(mass_social * 2.0),
            "DEL": norm(mass_play * 3.0),
            "E":   norm(counts.get("solvents", 0))}
        return GeodesicVector(tension, compression, round(coherence, 3), round(abstraction, 2), dimensions)

class Tension:
    def audit_hubris(self, physics) -> Tuple[bool, Optional[str], Optional[str]]:
        voltage = physics.voltage
        if voltage > 20.0:
            return True, f"{Prisma.RED}⚡ ICARUS EVENT: Voltage ({voltage:.1f}v) exceeds structural limits. Wings melting.{Prisma.RST}", "ICARUS_CRASH"
        if physics.flow_state == "SUPERCONDUCTIVE":
            return True, f"{Prisma.CYN}🌊 SUPERCONDUCTIVE: Resistance is zero. The words are flying.{Prisma.RST}", "FLOW_BOOST"
        if physics.narrative_drag > 8.0 and voltage > 10.0:
            return True, f"{Prisma.OCHRE}⚙️ GRINDING: High Velocity + High Drag = Heat.{Prisma.RST}", "FRICTION_WARNING"
        return False, None, None

class QuantumObserver:
    def __init__(self, events):
        self.events = events
        self.voltage_history = deque(maxlen=5)
        self.semantic_field = TheLexicon.create_field()
        self.last_physics_packet: Optional[PhysicsPacket] = None

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = TheLexicon.clean(text)
        counts, unknowns = self._tally_categories(clean_words)
        if unknowns:
            self._trigger_learning(unknowns, counts)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts, BoneConfig)
        raw_voltage = geo.tension
        self.voltage_history.append(raw_voltage)
        voltage = round(sum(self.voltage_history) / len(self.voltage_history), 2)
        graph_mass = 0.0
        if graph:
            anchors = [w for w in clean_words if w in graph]
            if anchors:
                graph_mass = sum(sum(graph[w]["edges"].values()) for w in anchors)
        packet_data = {
            "voltage": voltage,
            "narrative_drag": geo.compression,
            "mass": round(graph_mass, 1),
            "coherence": geo.coherence,
            "abstraction": geo.abstraction,
            "valence": TheLexicon.get_valence(clean_words),
            "counts": counts,
            "vector": geo.dimensions,
            "clean_words": clean_words,
            "raw_text": text,
            "flow_state": self._determine_flow(voltage, geo.coherence),
            "zone": self._determine_zone(geo.dimensions)}
        self.last_physics_packet = PhysicsPacket(**packet_data)
        if hasattr(self.events, "publish"):
            self.events.publish("PHYSICS_CALCULATED", packet_data)

        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    def _tally_categories(self, clean_words):
        counts = Counter()
        unknowns = []
        target_cats = ["heavy", "explosive", "constructive", "abstract", "play", "suburban", "antigen"]
        solvents = {"the", "is", "a", "and", "of"}

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
                flavor, conf = TheLexicon.taste(w)
                if flavor and conf > 0.5:
                    counts[flavor] += 1
                else:
                    unknowns.append(w)
        return counts, unknowns

    def _trigger_learning(self, unknowns, counts):
        energy = (counts["heavy"] * 2) + (counts["explosive"] * 2)
        if energy > 5:
            for w in unknowns:
                if len(w) > 3:
                    TheLexicon.teach(w, "kinetic", 0)
                    if hasattr(self.events, "log"):
                        self.events.log(f"{Prisma.MAG}NEUROPLASTICITY: Learned '{w}'.{Prisma.RST}", "SYS")

    def _determine_flow(self, v, k):
        if v > 15.0 and k > 0.8: return "SUPERCONDUCTIVE"
        if v > 10.0: return "TURBULENT"
        return "LAMINAR"

    def _determine_zone(self, vector):
        dom = max(vector, key=vector.get) if vector else "E"
        if dom in ["PSI", "DEL"]: return "AERIE"
        if dom in ["STR", "PHI"]: return "THE_FORGE"
        if dom in ["ENT", "VEL"]: return "THE_MUD"
        return "COURTYARD"

class Humility:
    def __init__(self):
        self.BOUNDARIES = {
            "FUTURE": ["predict", "future", "tomorrow", "will happen", "forecast"],
            "SOUL": ["soul", "spirit", "afterlife", "heaven", "hell"],
            "ABSOLUTE": ["always", "never", "everyone", "nobody", "proven"]}
        self.HUMBLE_PHRASES = [
            "Based on the available data...",
            "As I understand the current coordinates...",
            "From a structural perspective...",
            "This is a probabilistic estimation...",
            "I could be misinterpreting the vector..."]

    def check_boundary(self, text, voltage):
        text_lower = text.lower()
        violation = None
        for category, triggers in self.BOUNDARIES.items():
            if any(t in text_lower for t in triggers):
                violation = category
                break
        if violation or (voltage > 15.0):
            prefix = random.choice(self.HUMBLE_PHRASES)
            new_text = f"{Prisma.CYN}{prefix}{Prisma.RST} {text}"
            reason = f"Voltage ({voltage:.1f}v) > 15.0" if voltage > 15.0 else f"Boundary Violation ({violation})"
            log_msg = f"HUMILITY INTERVENTION: Text modified. Reason: {reason}."
            return True, new_text, log_msg
        return False, text, None

class GeodesicDome:
    def __init__(self):
        self.TRIGRAM_MAP = {
            "VEL": ("☳", "ZHEN",  "Thunder",  Prisma.GRN),
            "STR": ("☶", "GEN",   "Mountain", Prisma.SLATE),
            "ENT": ("☵", "KAN",   "Water",    Prisma.BLU),
            "PHI": ("☲", "LI",    "Fire",     Prisma.RED),
            "PSI": ("☰", "QIAN",  "Heaven",   Prisma.WHT),
            "BET": ("☴", "XUN",   "Wind",     Prisma.CYN),
            "E":   ("☷", "KUN",   "Earth",    Prisma.OCHRE),
            "DEL": ("☱", "DUI",   "Lake",     Prisma.MAG)}
        self.TRIGRAM_MAP["TMP"] = self.TRIGRAM_MAP["PHI"]
        self.TRIGRAM_MAP["TEX"] = self.TRIGRAM_MAP["STR"]
        self.TRIGRAM_MAP["XI"]  = self.TRIGRAM_MAP["BET"]
        self.TRIGRAM_MAP["LQ"]  = self.TRIGRAM_MAP["DEL"]

    @staticmethod
    def calculate_metrics(text: str, counts: Dict[str, int] = None) -> Tuple[float, float]:
        length = len(text)
        if length == 0: return 0.0, 0.0
        text_lower = text.lower()
        solvent_hits = sum(text_lower.count(w) for w in SOLVENT_WORDS)
        solvent_density = solvent_hits / max(1.0, (length / 5.0))
        raw_chaos = (length / TEXT_LENGTH_SCALAR)
        glue_factor = min(1.0, solvent_density * 2.0)
        e_metric = min(1.0, raw_chaos * (1.0 - (glue_factor * 0.8)))
        c_count = sum(1 for char in text if char in '!?%@#$;,')
        heavy_words = 0
        if counts:
            heavy_words = counts.get("heavy", 0) + counts.get("constructive", 0) + counts.get("sacred", 0)
        structure_score = c_count + (heavy_words * 2)
        base_b = min(1.0, math.log1p(structure_score + 1) / math.log1p(length * 0.1 + 1))
        if length < 50:
            base_b *= (length / 50.0)
        return round(e_metric, 3), round(base_b, 3)

    def resolve_trigram(self, vector: Dict[str, float]) -> Dict[str, Any]:
        if not vector:
            return {"symbol": "☷", "name": "KUN", "color": Prisma.OCHRE, "vector": "E"}
        dominant_vec = max(vector, key=vector.get)
        if vector[dominant_vec] < 0.2:
            dominant_vec = "E"
        symbol, name, concept, color = self.TRIGRAM_MAP.get(dominant_vec, self.TRIGRAM_MAP["E"])
        return {
            "symbol": symbol,
            "name": name,
            "concept": concept,
            "color": color,
            "vector": dominant_vec}

class ChromaScope:
    PALETTE = {
        "INDIGO": (Prisma.INDIGO, "STR", "PHI"),
        "OCHRE":  (Prisma.OCHRE,  "TMP", "E"),
        "VIOLET": (Prisma.VIOLET, "DEL", "LQ"),
        "EMERALD":(Prisma.GRN,    "XI",  "BET"),
        "CRIMSON":(Prisma.RED,    "VEL", "ENT")}
    def modulate(self, text, vector):
        sorted_vecs = sorted(vector.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        primary_dim = sorted_vecs[0][0]
        selected_color = Prisma.GRY
        for color_name, (code, d1, d2) in self.PALETTE.items():
            if primary_dim == d1 or primary_dim == d2:
                selected_color = code
                break
        if "sorry" in text.lower():
            return f"{Prisma.OCHRE}{text}{Prisma.RST}"
        return f"{selected_color}{text}{Prisma.RST}"

class ZoneInertia:
    def __init__(self, inertia=0.7, min_dwell=2):
        self.inertia = inertia
        self.min_dwell = min_dwell
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector = None
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0
        return self.is_anchored

    def stabilize(self, proposed_zone, physics, cosmic_state) -> Tuple[str, Optional[str]]:
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
            if proposed_zone != self.current_zone:
                self.strain_gauge += pressure
                if self.strain_gauge > 2.5:
                    self.is_anchored = False
                    self.strain_gauge = 0.0
                    self.current_zone = proposed_zone
                    return proposed_zone, f"{Prisma.RED}⚡ SNAP! The narrative current was too strong. Anchor failed.{Prisma.RST}"
                return self.current_zone, f"{Prisma.OCHRE}⚓ ANCHORED: Resisting drift to '{proposed_zone}' (Strain {self.strain_gauge:.1f}/2.5){Prisma.RST}"
            else:
                self.strain_gauge = max(0.0, self.strain_gauge - 0.1)
                return self.current_zone, None
        if proposed_zone == self.current_zone:
            self.dwell_counter = 0
            self.last_vector = current_vec
            return proposed_zone, None
        if self.dwell_counter < self.min_dwell:
            return self.current_zone, None
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
    def override_cosmic_drag(cosmic_drag_penalty, current_zone):
        aerie_flow_coefficient = 0.3
        if current_zone == "AERIE":
            if cosmic_drag_penalty > 0:
                return cosmic_drag_penalty * aerie_flow_coefficient
        return cosmic_drag_penalty

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