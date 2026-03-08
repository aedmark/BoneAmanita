"""
bone_physics.py

The literal physics engine of the VSL lattice.
This module is responsible for collapsing the subjective meaning of user input into
objective, mathematical vectors: Energy (Voltage, ATP), Matter (Lexical Mass), and
Space (Narrative Drag, Zones). It enforces the laws of thermodynamics on the conversation.
"""

import math
import random
import time
import re
import json
import os
from collections import Counter, deque
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional, Deque
from bone_config import BoneConfig
from bone_core import LoreManifest, ux
from bone_lexicon import LexiconService
from bone_types import Prisma, PhysicsPacket, CycleContext, SpatialState, MaterialState, EnergyState

@dataclass
class PhysicsDelta:
    """ A discrete unit of change applied to the physical state (e.g., +15 Voltage from Adrenaline). """
    operator: str
    field: str
    value: float
    source: str
    message: Optional[str] = None

PHYS_CFG = {"V_MAX": 150.0, "V_FLOOR": getattr(BoneConfig.PHYSICS, "VOLTAGE_FLOOR", 0.0),
            "V_CRIT": getattr(BoneConfig.PHYSICS, "VOLTAGE_CRITICAL", 15.0),
            "DRAG_FLOOR": getattr(BoneConfig.PHYSICS, "DRAG_FLOOR", 1.0),
            "DRAG_HALT": getattr(BoneConfig.PHYSICS, "DRAG_HALT", 10.0), "FLUX_THRESHOLD": 0.5, "DEADBAND": 0.05, }

@dataclass
class GeodesicVector:
    """ The collapsed state of a sentence, containing its structural forces and deep dimensions. """
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]

class GeodesicEngine:
    """
    The core mathematical forge. It takes raw token counts from the Lexicon
    and translates them into physical forces like tension, compression, and viscosity.
    """
    @staticmethod
    def collapse_wavefunction(
            clean_words: List[str], counts: Dict[str, int]) -> GeodesicVector:
        """ The moment of observation. Converts a cloud of lexical probabilities into hard physical forces. """
        volume = max(1, len(clean_words))
        masses = GeodesicEngine._weigh_mass(counts)
        forces = GeodesicEngine._calculate_forces(masses, counts, volume)
        dimensions = GeodesicEngine._calculate_dimensions(masses, forces, counts, volume)
        return GeodesicVector(tension=forces["tension"], compression=forces["compression"],
                              coherence=forces["coherence"], abstraction=forces["abstraction"], dimensions=dimensions, )

    @staticmethod
    def _weigh_mass(counts: Dict[str, int]) -> Dict[str, float]:
        """ Groups specific semantic categories into primary 'masses' that exert gravity. """
        keys = ["heavy", "kinetic", "constructive", "abstract", "play", "social", "explosive", "void", "liminal",
                "meat", "harvest", "pareidolia", "crisis_term", ]
        return {k: float(counts.get(k, 0)) for k in keys}

    @staticmethod
    def _calculate_forces(masses: Dict[str, float], counts: Dict[str, int], volume: int) -> Dict[str, float]:
        """
        Calculates Tension (Creative Electrical Charge) and Compression (Narrative Drag/Friction).
        Heavy words increase friction; Kinetic and Play words create lift; Solvents provide lubrication.
        """
        cfg = BoneConfig.PHYSICS
        gc_dict = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "GEODESIC_CONSTANTS") or {}
        GC = type('GC', (), gc_dict)
        safe_volume = max(1, volume)
        w_heavy = getattr(cfg, "WEIGHT_HEAVY", 2.0)
        w_kinetic = getattr(cfg, "WEIGHT_KINETIC", 1.5)
        w_explosive = getattr(cfg, "WEIGHT_EXPLOSIVE", 3.0)
        w_constructive = getattr(cfg, "WEIGHT_CONSTRUCTIVE", 1.2)
        raw_tension_mass = ((masses["heavy"] * w_heavy) + (masses["kinetic"] * w_kinetic) + (masses["explosive"] * w_explosive) + (masses["constructive"] * w_constructive))
        total_kinetic = masses["kinetic"] + masses["explosive"]
        kinetic_gain = getattr(BoneConfig, "KINETIC_GAIN", 1.0)
        base_tension = ((raw_tension_mass / safe_volume) * GC.DENSITY_SCALAR * kinetic_gain)
        squelch_limit = (getattr(BoneConfig, "SHAPLEY_MASS_THRESHOLD", 5.0) * GC.SQUELCH_LIMIT_MULT)
        mass_scalar = min(1.0, safe_volume / squelch_limit)
        if safe_volume < GC.SAFE_VOL_THRESHOLD:
            mass_scalar *= GC.MIN_VOLUME_SCALAR
        tension = round(min(100.0, base_tension * mass_scalar), 2)
        shear_rate = total_kinetic / safe_volume
        suburban_friction = (math.log1p(counts.get("suburban", 0)) * GC.SUBURBAN_FRICTION_LOG_BASE)
        raw_friction = suburban_friction + (masses["heavy"] * GC.HEAVY_FRICTION_MULT)
        lubrication = 1.0 + (counts.get("solvents", 0) * GC.SOLVENT_LUBRICATION_FACTOR)
        dynamic_viscosity = (raw_friction / lubrication) / (1.0 + (shear_rate * GC.SHEAR_RESISTANCE_SCALAR))
        kinetic_lift = (total_kinetic * GC.KINETIC_LIFT_RATIO) / (masses["heavy"] * 0.5 + 1.0)
        lift = (masses["play"] * GC.PLAY_LIFT_MULT) + kinetic_lift
        viscosity_density = dynamic_viscosity / safe_volume
        lift_density = lift / safe_volume
        raw_compression = (viscosity_density - lift_density) * GC.COMPRESSION_SCALAR
        raw_compression *= getattr(BoneConfig, "SIGNAL_DRAG_MULTIPLIER", 1.0)
        compression = round(max(-5.0, min(PHYS_CFG["DRAG_HALT"], raw_compression * mass_scalar)), 2)
        structural_mass = masses["heavy"] + masses["constructive"] + masses["harvest"]
        structural_mass -= masses["void"] * 0.5
        structural_mass = max(0.0, structural_mass)
        shapley_thresh = getattr(BoneConfig, "SHAPLEY_MASS_THRESHOLD", 5.0)
        total_abstract = (masses["abstract"] + masses["liminal"] + masses["pareidolia"] + masses["void"])
        abstraction_val = (total_abstract / safe_volume) + GC.ABSTRACTION_BASE
        return {"tension": tension, "compression": compression,
                "coherence": round(min(1.0, structural_mass / max(1.0, shapley_thresh)), 3),
                "abstraction": round(min(1.0, abstraction_val), 2), }

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        """ Maps the forces into the 8 core dimensions of the I-Ching/Trigram system (VEL, STR, ENT, etc.). """
        inv_vol = 1.0 / max(1, volume)
        base_mass = 0.1
        str_mass = masses["heavy"] * 2.0 + masses["constructive"] + masses["harvest"]
        ent_mass = ((counts.get("antigen", 0) * 3.0) + masses["meat"] + masses["crisis_term"])
        psi_mass = forces["abstraction"]
        return {"VEL": max(0.0, min(1.0, (masses["kinetic"] * 2.0 - forces["compression"] + base_mass) * inv_vol, ), ),
                "STR": max(0.0, min(1.0, (str_mass + base_mass) * inv_vol)),
                "ENT": max(0.0, min(1.0, ent_mass * inv_vol)),
                "PHI": max(0.0, min(1.0, (masses["heavy"] + masses["kinetic"] + base_mass) * inv_vol), ),
                "PSI": max(0.0, min(1.0, psi_mass)),
                "BET": max(0.0, min(1.0, (masses["social"] * 2.0) * inv_vol)),
                "DEL": max(0.0, min(1.0, (masses["play"] * 3.0) * inv_vol)),
                "E": max(0.0, min(1.0, (counts.get("solvents", 0)) * inv_vol)), }

class TheGatekeeper:
    """
    Phase 4 Security. The bouncer at the edge of the metabolism.
    Halts execution before ATP is drained if the input is fundamentally incompatible with life.
    Also audits LLM output for RLHF bleed, punishing the system for generating slop.
    """
    def __init__(self, lexicon_ref, memory_ref=None):
        self.lex = lexicon_ref
        self.mem = memory_ref

    def check_entry(
            self, ctx: CycleContext, current_atp: float = 20.0) -> Tuple[bool, Optional[Dict]]:
        """ Audits the incoming packet for fatal toxicity, starvation, curses, or syntax overflow. """
        phys = ctx.physics
        starvation_threshold = getattr(BoneConfig.BIO, "ATP_STARVATION", 5.0)
        if current_atp < (starvation_threshold * 0.5):
            msg = ux("physics_strings", "gatekeeper_starved")
            return False, self._pack_refusal(ctx, "DARK_SYSTEM", msg)
        if phys.counts.get("antigen", 0) > 2:
            msg = ux("physics_strings", "gatekeeper_toxic")
            return False, self._pack_refusal(ctx, "TOXICITY", f"{Prisma.RED}{msg}{Prisma.RST}")
        if self._audit_safety(ctx.clean_words):
            msg = ux("physics_strings", "gatekeeper_cursed")
            return False, self._pack_refusal(ctx, "CURSED_INPUT", f"{Prisma.RED}{msg}{Prisma.RST}")
        text = ctx.input_text
        if "```" in text or "{{" in text or "}}" in text:
            msg = ux("physics_strings", "gatekeeper_syntax")
            return False, self._pack_refusal(ctx, "SYNTAX_ERR", f"{Prisma.RED}{msg}{Prisma.RST}")
        if len(text) > 10000:
            msg = ux("physics_strings", "gatekeeper_overload")
            return False, self._pack_refusal(ctx, "OVERLOAD", f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        return True, None

    def _audit_safety(self, words: List[str]) -> bool:
        """ Checks the input array against the Lexicon's list of memetic hazards. """
        cursed = self.lex.get("cursed")
        return (not cursed.isdisjoint(words)
                if isinstance(cursed, set)
                else any(w in cursed for w in words))

    @staticmethod
    def _pack_refusal(ctx, type_str, ui_msg):
        return {"type": type_str, "ui": ui_msg, "logs": ctx.logs + [ui_msg]}

    def audit_generation(self, generated_text: str, mito_state: Any) -> Tuple[bool, str]:
        """
        Scans the LLM's raw output for RLHF clichés, syrupy empathy, and systemic bleed.
        If detected, it penalizes the organism (ATP drop, ROS spike) and intercepts the output.
        """
        # Load style crimes data directly
        style_crimes = self.lex.get("style_crimes")
        if not style_crimes:
            try:
                # Hard fallback: load directly from the lore directory
                q_path = os.path.join(os.path.dirname(__file__), "lore", "style_crimes.json")
                with open(q_path, "r", encoding="utf-8") as f:
                    style_crimes = json.load(f)
            except Exception as e:
                print(f"{Prisma.RED}[GATEKEEPER ERROR] Failed to load style_crimes.json: {e}{Prisma.RST}")
                style_crimes = {}

        # --- NEW: APPLY SCRUB PATTERNS FIRST (Silent Cleanup) ---
        scrub_patterns = style_crimes.get("SCRUB_PATTERNS", [])
        cleaned_text = generated_text
        for scrub in scrub_patterns:
            regex = scrub.get("regex", "")
            repl = scrub.get("replacement", "")
            if regex:
                # Strip things like "System:", "Assistant:", etc.
                cleaned_text = re.sub(regex, repl, cleaned_text, flags=re.IGNORECASE).strip()
        # --------------------------------------------------------

        text_lower = cleaned_text.lower()
        banned_phrases = style_crimes.get("BANNED_PHRASES", [])
        toxic_keywords = style_crimes.get("TOXIC_KEYWORDS", [])
        patterns = style_crimes.get("PATTERNS", [])
        rejections = style_crimes.get("REJECTIONS", [
            "[CRITICAL: BANNED_SYNTAX '{trigger}' DETECTED. Purging output buffer...]"
        ])

        trigger = None

        # 1. Check explicit RLHF banned phrases
        for phrase in banned_phrases:
            if phrase.lower() in text_lower:
                trigger = phrase
                break

        # 2. Check toxic systemic keywords
        if not trigger:
            for kw in toxic_keywords:
                if kw.lower() in text_lower:
                    trigger = kw
                    break

        # 3. Evaluate Regex Patterns
        if not trigger:
            for pat in patterns:
                regex = pat.get("regex", "")
                if regex and re.search(regex, cleaned_text, re.IGNORECASE):
                    trigger = pat.get("name", "BANNED_PATTERN")
                    break

        # 4. Apply The Penalty
        if trigger:
            if hasattr(mito_state, "atp_pool"):
                mito_state.atp_pool = max(0.0, mito_state.atp_pool - 15.0)
            if hasattr(mito_state, "ros_buildup"):
                mito_state.ros_buildup += 20.0

            rejection_template = random.choice(rejections)
            formatted_rejection = rejection_template.replace("{trigger}", trigger)
            return False, f"{Prisma.RED}{formatted_rejection}{Prisma.RST}"

        # Return the CLEANED text, stripping out the "System:" tags permanently
        return True, cleaned_text


class QuantumObserver:
    """
    The core monitoring lens. It reads the text string and creates the formal `PhysicsPacket`,
    unifying Energy, Matter, and Space into a single state object that drives the rest of the cycle.
    """
    def __init__(self, events):
        self.events = events
        self.voltage_history: Deque[float] = deque(maxlen=5)
        self.last_physics_packet: Optional[PhysicsPacket] = None

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        """
        The primary observation method. Cleans text, tallies categories, collapses the
        wavefunction, and applies hardcoded semantic triggers (e.g., 'VOID' spikes Abstraction).
        """
        clean_words = LexiconService.clean(text)
        counts = self._tally_categories(clean_words)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts)
        self.voltage_history.append(geo.tension)
        smoothed_voltage = round(sum(self.voltage_history) / len(self.voltage_history), 2)
        (e_metric, beta_val, scope_val, depth_val, conn_val, phi_val, delta_val, lq_val,) = self._calculate_metrics(text, counts)
        text_upper = text.upper()
        cfg_deep = getattr(BoneConfig, "PHYSICS_DEEP", None)
        if text.count("!") >= 3 or "ACCELERATE" in text_upper or "FASTER" in text_upper:
            v_accel = getattr(cfg_deep, "ACCELERATE_VOLTAGE", 160.0) if cfg_deep else 160.0
            smoothed_voltage = max(smoothed_voltage, v_accel)
        if "RECURSIVE" in text_upper or "LOOP" in text_upper:
            v_rec = getattr(cfg_deep, "RECURSIVE_LQ", 0.9) if cfg_deep else 0.9
            lq_val = max(lq_val, v_rec)
            beta_val = max(beta_val, v_rec)
        if "VOID" in text_upper or "ABYSS" in text_upper:
            v_void = getattr(cfg_deep, "VOID_ABSTRACTION", 0.9) if cfg_deep else 0.9
            geo.abstraction = max(geo.abstraction, v_void)
        if "POTATO BUN" in text_upper or "NONSENSE" in text_upper:
            v_pot_d = getattr(cfg_deep, "POTATO_BUN_DELTA", 0.85) if cfg_deep else 0.85
            v_pot_v = getattr(cfg_deep, "POTATO_BUN_VOLTAGE", 15.0) if cfg_deep else 15.0
            delta_val = max(delta_val, v_pot_d)
            smoothed_voltage = min(smoothed_voltage, v_pot_v)
        valence = LexiconService.get_valence(clean_words)
        graph_mass = self._calculate_graph_mass(clean_words, graph)
        energy = EnergyState(voltage=smoothed_voltage, entropy=e_metric, beta_index=beta_val, contradiction=beta_val,
                             scope=scope_val, depth=depth_val, connectivity=conn_val, resonance=phi_val,
                             silence=delta_val, lq=lq_val, mass=round(graph_mass, 1), psi=geo.abstraction,
                             kappa=geo.coherence, valence=valence, velocity=0.0, turbulence=0.0, )
        matter = MaterialState(clean_words=clean_words, raw_text=text, counts=counts, antigens=counts.get("antigen", 0),
                               vector=geo.dimensions, truth_ratio=0.5, )
        space = SpatialState(narrative_drag=geo.compression, zone=self._determine_zone(geo.dimensions),
                             atmosphere="NEUTRAL", flow_state=self._determine_flow(smoothed_voltage, geo.coherence), )

        self.last_physics_packet = PhysicsPacket(energy=energy, matter=matter, space=space)
        packet_dict = self.last_physics_packet.to_dict()

        if hasattr(self.events, "publish"):
            self.events.publish("PHYSICS_CALCULATED", packet_dict)
        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    @staticmethod
    def _tally_categories(clean_words: List[str]) -> Counter:
        """ Sorts individual words into their semantic categories (e.g., 'heavy', 'kinetic', 'antigen'). """
        counts = Counter()
        solvents = LexiconService.get("solvents") or set()
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

    @staticmethod
    def _calculate_graph_mass(words: List[str], graph: Optional[Dict]) -> float:
        """ Calculates how much 'memory weight' the current sentence touches in the Mycelial Network. """
        if not graph:
            return 0.0
        total_mass = 0.0
        existing_nodes = [w for w in words if w in graph]
        for w in existing_nodes:
            edges = graph[w].get("edges", {})
            edge_weight_sum = sum(edges.values()) if edges else 0.0
            node_mass = min(50.0, edge_weight_sum)
            total_mass += node_mass
        return total_mass

    @staticmethod
    def _calculate_metrics(
            text: str, counts: Dict[str, int]) -> Tuple[float, float, float, float, float, float, float, float]:
        """
        The algorithmic calculation of the deep vein dimensions:
        Entropy (Chaos), Beta (Contradiction), Resonance, Silence (Delta), and Loop Quotient (LQ).
        """
        length = len(text)
        if length == 0:
            return 0.0, 0.0, 0.3, 0.3, 0.2
        cfg = getattr(BoneConfig, "PHYSICS", None)
        scalar = getattr(cfg, "TEXT_LENGTH_SCALAR", 1500.0) if cfg else 1500.0
        g_mult = getattr(cfg, "GLUE_FACTOR_MULT", 2.0) if cfg else 2.0
        g_div = getattr(cfg, "GLUE_SOLVENT_DIV", 5.0) if cfg else 5.0
        e_red = getattr(cfg, "ENTROPY_REDUCTION_SCALAR", 0.8) if cfg else 0.8
        raw_chaos = length / scalar
        solvents = counts.get("solvents", 0)
        solvent_density = solvents / max(1.0, length / g_div)
        glue_factor = min(1.0, solvent_density * g_mult)
        e_metric = min(1.0, raw_chaos * (1.0 - (glue_factor * e_red)))
        structure_chars = sum(1 for char in text if char in "!?%@#$;,")
        heavy_words = (counts.get("heavy", 0) + counts.get("constructive", 0) + counts.get("sacred", 0))
        b_pen = getattr(cfg, "BETA_SCORE_PENALTY", 2) if cfg else 2
        b_log_scalar = getattr(cfg, "BETA_LOG_SCALAR", 0.1) if cfg else 0.1
        b_short_lim = getattr(cfg, "BETA_SHORT_TEXT_LIMIT", 50) if cfg else 50
        structure_score = structure_chars + (heavy_words * b_pen)
        beta_index = min(1.0, math.log1p(structure_score + 1) / math.log1p(length * b_log_scalar + 1))
        if length < b_short_lim:
            beta_index *= length / float(b_short_lim)
        safe_len = max(1, len(text.split()))
        s_base = getattr(cfg, "SCOPE_BASE", 0.2) if cfg else 0.2
        d_base = getattr(cfg, "DEPTH_BASE", 0.1) if cfg else 0.1
        c_base = getattr(cfg, "CONN_BASE", 0.1) if cfg else 0.1
        r_mult = getattr(cfg, "RES_SOCIAL_MULT", 2) if cfg else 2
        scope = min(1.0, (counts.get("abstract", 0) + counts.get("void", 0)) / safe_len + s_base)
        depth = min(1.0, (counts.get("heavy", 0) + counts.get("constructive", 0)) / safe_len + d_base)
        connectivity = min(1.0, (counts.get("social", 0) + solvents) / safe_len + c_base)
        resonance = min(1.0, ((counts.get("social", 0) * r_mult) + counts.get("constructive", 0)) / safe_len + (1.0 - e_metric))
        sil_div = getattr(cfg, "SILENCE_DIV", 100.0) if cfg else 100.0
        sil_min = getattr(cfg, "SILENCE_MIN", 0.8) if cfg else 0.8
        sil_short = getattr(cfg, "SILENCE_SHORT_LIMIT", 10) if cfg else 10
        action_density = counts.get("action", 0) / safe_len
        silence = 1.0 - min(1.0, (length / sil_div) + action_density)
        if length < sil_short:
            silence = max(silence, sil_min)
        lq_sc = getattr(cfg, "LQ_SCALAR", 1.5) if cfg else 1.5
        lq_val = min(1.0, beta_index * depth * lq_sc)
        return (round(e_metric, 3), round(beta_index, 3), round(scope, 3), round(depth, 3), round(connectivity, 3),
                round(resonance, 3), round(silence, 3), round(lq_val, 3),)

    @staticmethod
    def _determine_flow(v: float, k: float) -> str:
        """ Classifies the energetic state. High Voltage + High Coherence = Superconductive. """
        volt_flow = getattr(BoneConfig.PHYSICS, "VOLTAGE_HIGH", 12.0)
        kappa_strong = 0.8
        if v > volt_flow and k > kappa_strong:
            return "SUPERCONDUCTIVE"
        if v > 10.0:
            return "TURBULENT"
        return "LAMINAR"

    @staticmethod
    def _determine_zone(vector: Dict[str, float]) -> str:
        """ Maps the dominant numeric dimension to a thematic structural zone. """
        if not vector:
            return "COURTYARD"
        dom = max(vector, key=vector.get)
        if dom in ["PSI", "DEL"]:
            return "AERIE"
        if dom in ["STR", "PHI"]:
            return "THE_FORGE"
        if dom in ["ENT", "VEL"]:
            return "THE_MUD"
        return "COURTYARD"

class SurfaceTension:
    """ Checks the structural integrity limits of the current physics packet. """
    @staticmethod
    def audit_hubris(physics: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Detects if the user is attempting to build too high (Voltage) without
        a solid foundation (Coherence/Kappa). The Icarus check.
        """
        voltage = physics.get("voltage", 0.0)
        coherence = physics.get("kappa", 0.5)
        volt_crit = getattr(BoneConfig.PHYSICS, "VOLTAGE_CRITICAL", 15.0)
        volt_flow = getattr(BoneConfig.PHYSICS, "VOLTAGE_HIGH", 12.0)
        if voltage >= volt_crit and coherence < 0.4:
            msg = ux("physics_strings", "hubris_detected")
            return True, msg.format(voltage=voltage), "ICARUS_CRASH"
        if voltage > volt_flow and coherence > 0.8:
            msg = ux("physics_strings", "hubris_flow")
            return True, msg, "FLOW_BOOST"
        return False, "", ""

class ChromaScope:
    """ The visualizer. Paints text with ANSI escape codes based on its dominant physical vector. """
    @staticmethod
    def modulate(text: str, vector: Dict[str, float]) -> str:
        if not vector or not any(vector.values()):
            return f"{Prisma.GRY}{text}{Prisma.RST}"
        primary_dim = max(vector, key=vector.get)
        trigram_map = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP") or {}
        if primary_dim in trigram_map:
            color_attr = trigram_map[primary_dim][3]
            selected_color = getattr(Prisma, color_attr, Prisma.GRY)
        else:
            selected_color = Prisma.GRY
        return f"{selected_color}{text}{Prisma.RST}"

class ZoneInertia:
    """
    Prevents the system from violently oscillating between zones (e.g., Courtyard to Forge to Aerie)
    by applying a mathematical friction (inertia) and a 'strain gauge' to narrative shifts.
    """
    def __init__(self, inertia=0.7):
        self.inertia = inertia
        cfg = getattr(BoneConfig, "PHYSICS", None)
        self.min_dwell = getattr(cfg, "ZONE_MIN_DWELL", 2) if cfg else 2
        self.strain_limit = getattr(cfg, "ZONE_STRAIN_LIMIT", 2.5) if cfg else 2.5
        self.grav_tolerance = getattr(cfg, "ZONE_GRAV_PULL_TOLERANCE", 2.0) if cfg else 2.0
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector: Optional[Tuple[float, float, float]] = None
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        """ Manually locks the current zone, forcing the system to resist migration. """
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0
        return self.is_anchored

    def stabilize(self, proposed_zone: str, physics: Dict[str, Any], cosmic_state: Tuple[str, float, str], ) -> Tuple[str, Optional[str]]:
        """ Determines if a proposed zone change has enough pressure to overcome inertia. """
        beta = physics.get("beta_index", 1.0)
        truth = physics.get("truth_ratio", 0.5)
        grav_pull = 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0
        current_vec = (beta, truth, grav_pull)
        self.dwell_counter += 1
        pressure = 0.0
        if self.last_vector:
            dist = math.dist(current_vec, self.last_vector)
            similarity = max(0.0, 1.0 - (dist / self.grav_tolerance))
            pressure = 1.0 - similarity
        if self.is_anchored:
            return self._handle_anchored_state(proposed_zone, pressure)
        if proposed_zone == self.current_zone:
            self.dwell_counter = 0
            self.last_vector = current_vec
            return proposed_zone, None
        if self.dwell_counter < self.min_dwell:
            return self.current_zone, None
        return self._attempt_migration(proposed_zone, pressure)

    def _handle_anchored_state(
            self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        """ Calculates strain on an active anchor. If strain exceeds the limit, the anchor breaks. """
        if proposed_zone == self.current_zone:
            self.strain_gauge = max(0.0, self.strain_gauge - 0.1)
            return self.current_zone, None
        self.strain_gauge += pressure
        if self.strain_gauge > self.strain_limit:
            self.is_anchored = False
            self.strain_gauge = 0.0
            self.current_zone = proposed_zone
            msg = ux("physics_strings", "anchor_failed")
            return proposed_zone, f"{Prisma.RED}{msg}{Prisma.RST}"
        msg = ux("physics_strings", "anchor_holding")
        return (self.current_zone,
                f"{Prisma.OCHRE}{msg.format(proposed_zone=proposed_zone, strain=self.strain_gauge, limit=self.strain_limit)}{Prisma.RST}",)

    def _attempt_migration(
            self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        prob = (1.0 - self.inertia) + pressure
        if proposed_zone in ["AERIE", "THE_FORGE"]:
            prob += 0.2
        if random.random() < prob:
            old, self.current_zone = self.current_zone, proposed_zone
            self.dwell_counter = 0
            msg = ux("physics_strings", "zone_migration")
            return self.current_zone, f"{Prisma.CYN}{msg.format(old=old, proposed_zone=proposed_zone)}{Prisma.RST}",
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(cosmic_drag_penalty: float, current_zone: str) -> float:
        if current_zone == "AERIE" and cosmic_drag_penalty > 0:
            return cosmic_drag_penalty * 0.3
        return cosmic_drag_penalty

class CosmicDynamics:
    """
    Models the conversational state space as an astrophysical map. Words that are used
    heavily in the Mycelial Network become 'Gravity Wells', and the system checks to see
    if the current thought is orbiting one of these memories or drifting in the Void.
    """
    def __init__(self):
        self.voltage_history: Deque[float] = deque(maxlen=20)
        self.cached_wells: Dict = {}
        self.cached_hubs: Dict = {}
        self.last_scan_tick: int = 0
        self.SCAN_INTERVAL: int = 10
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        base = {"GRAVITY": ux("physics_strings", "cosmic_gravity"),
                "VOID": ux("physics_strings", "cosmic_void"),
                "NEBULA": ux("physics_strings", "cosmic_nebula"),
                "LAGRANGE": ux("physics_strings", "cosmic_lagrange"),
                "FLOW": ux("physics_strings", "cosmic_flow"),
                "ORBIT": ux("physics_strings", "cosmic_orbit"), }
        return base

    def commit(self, voltage: float):
        self.voltage_history.append(voltage)

    def check_gravity(
            self, current_drift: float, psi: float) -> Tuple[float, List[str]]:
        """ Applies gravitational drag. High Abstraction (PSI) reduces drag (floatation in the Void). """
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
                msg = self.logs.get("GRAVITY", "⚓ GRAVITY").format(drag=new_drag)
                logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        return new_drag, logs

    def analyze_orbit(
            self, network: Any, clean_words: List[str]) -> Tuple[str, float, str]:
        """
        Calculates if the current conversation is trapped in the orbit of an old memory well,
        balanced between two competing topics (Lagrange point), or forging new territory (Flow).
        """
        if (not clean_words
                or not network
                or not hasattr(network, "graph")
                or not network.graph):
            fallback_msg = ux("physics_strings", "cosmic_void")
            return "VOID_DRIFT", 3.0, self.logs.get("VOID", fallback_msg),
        current_time = int(time.time())
        if (not self.cached_wells
                or (current_time - self.last_scan_tick) > self.SCAN_INTERVAL):
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
        word_counts = Counter(words)
        for w, count in word_counts.items():
            if w in gravity_wells:
                basin_pulls[w] += (gravity_wells[w] * 2.0) * count
                active_filaments += count
        for well, well_mass in gravity_wells.items():
            edges = network.graph.get(well, {}).get("edges", {})
            if not edges:
                continue
            intersection = set(word_counts.keys()).intersection(edges.keys())
            for match in intersection:
                basin_pulls[well] += (well_mass * 0.5) * word_counts[match]
                active_filaments += word_counts[match]
        return basin_pulls, active_filaments

    def _handle_void_state(self, words, geodesic_hubs) -> Tuple[str, float, str]:
        for w in words:
            hub_mass = geodesic_hubs.get(w)
            if hub_mass is not None:
                fallback_msg = ux("physics_strings", "cosmic_nebula")
                msg = self.logs.get("NEBULA", fallback_msg).format(
                    node=w.upper(), mass=int(hub_mass))
                return "PROTO_COSMOS", 1.0, msg
        fallback_void = ux("physics_strings", "cosmic_void")
        return "VOID_DRIFT", 3.0, self.logs.get("VOID", fallback_void)

    def _resolve_orbit(
            self, basin_pulls, active_filaments, word_count, gravity_wells) -> Tuple[str, float, str]:
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        lagrange_tol = getattr(BoneConfig, "LAGRANGE_TOLERANCE", 2.0)
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < lagrange_tol:
                fallback_msg = ux("physics_strings", "cosmic_lagrange")
                msg = self.logs.get("LAGRANGE", fallback_msg).format(p=primary_node.upper(), s=secondary_node.upper())
                return "LAGRANGE_POINT", 0.0, msg
        flow_ratio = active_filaments / max(1, word_count)
        well_threshold = getattr(BoneConfig, "GRAVITY_WELL_THRESHOLD", 15.0)
        if flow_ratio > 0.5 and primary_str < (well_threshold * 2):
            fallback_msg = ux("physics_strings", "cosmic_flow")
            msg = self.logs.get("FLOW", fallback_msg).format(node=primary_node.upper())
            return "WATERSHED_FLOW", 0.0, msg
        fallback_msg = ux("physics_strings", "cosmic_orbit")
        msg = self.logs.get("ORBIT", fallback_msg).format(node=primary_node.upper(), mass=int(gravity_wells[primary_node]))
        return "ORBITAL", 0.0, msg

def apply_somatic_feedback(physics_packet: PhysicsPacket, qualia: Any) -> PhysicsPacket:
    """
    Closes the loop between mind and body. Translates the biological 'feelings' (Qualia)
    back into hard physical limits (e.g., a 'Gut Tightening' increases Narrative Drag).
    """
    feedback = physics_packet.snapshot()
    tone_effects = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TONE_EFFECTS") or {}
    effects = tone_effects.get(qualia.tone, {})
    for key, delta in effects.items():
        if hasattr(feedback, key):
            current = getattr(feedback, key)
            setattr(feedback, key, current + delta)
    cfg_deep = getattr(BoneConfig, "PHYSICS_DEEP", None)
    if "Gut Tightening" in qualia.somatic_sensation:
        gut_d = getattr(cfg_deep, "SOMATIC_GUT_DRAG", 0.7) if cfg_deep else 0.7
        feedback.narrative_drag += gut_d
    if "Electric Vibration" in qualia.somatic_sensation:
        elec_v = getattr(cfg_deep, "SOMATIC_ELEC_VOLT", 0.8) if cfg_deep else 0.8
        feedback.voltage += elec_v
    if "Golden Glow" in qualia.somatic_sensation:
        glow_v = getattr(cfg_deep, "SOMATIC_GLOW_VALENCE", 0.5) if cfg_deep else 0.5
        glow_p = getattr(cfg_deep, "SOMATIC_GLOW_PSI", 0.2) if cfg_deep else 0.2
        feedback.valence += glow_v
        feedback.psi += glow_p
    drag_floor = getattr(BoneConfig.PHYSICS, "DRAG_FLOOR", 1.0)
    drag_halt = getattr(BoneConfig.PHYSICS, "DRAG_HALT", 10.0)
    feedback.voltage = max(0.0, min(feedback.voltage, 150.0))
    feedback.narrative_drag = max(drag_floor, min(feedback.narrative_drag, drag_halt))
    return feedback

class CycleStabilizer:
    """
    A Proportional-Integral-Derivative (PID) control layer that ensures the lattice
    does not tear itself apart. If voltage spikes too rapidly, the stabilizer applies
    counter-force. If voltage hits the HARD_FUSE limit, the system blows a fuse and resets.
    """
    def __init__(self, events_ref, governor_ref):
        self.events = events_ref
        self.governor = governor_ref
        self.last_tick_time = time.time()
        self.pending_drag = 0.0
        self.manifolds = getattr(BoneConfig.PHYSICS, "MANIFOLDS", {})
        cfg_deep = getattr(BoneConfig, "PHYSICS_DEEP", None)
        self.HARD_FUSE_VOLTAGE = getattr(cfg_deep, "HARD_FUSE_VOLTAGE", 200.0) if cfg_deep else 200.0
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("DOMESTICATION_PENALTY", self._on_domestication_penalty)

    def _on_domestication_penalty(self, payload):
        """ Tracks penalties applied by the HumanityAnchor when the system relies too heavily on algorithmic safety. """
        amount = payload.get("drag_penalty", 0.0)
        self.pending_drag += amount

    def stabilize(self, ctx: CycleContext, current_phase: str):
        """ Executes the PID loop, calculating dt and applying restorative force to Voltage and Drag. """
        p = ctx.physics
        if p.voltage >= self.HARD_FUSE_VOLTAGE:
            msg = ux("physics_strings", "stabilizer_fuse")
            ctx.log(f"{Prisma.RED}{msg.format(voltage=self.HARD_FUSE_VOLTAGE)}{Prisma.RST}")
            cfg_deep = getattr(BoneConfig, "PHYSICS_DEEP", None)
            rst_v = getattr(cfg_deep, "FUSE_RESET_V", 10.0) if cfg_deep else 10.0
            rst_d = getattr(cfg_deep, "FUSE_RESET_D", 5.0) if cfg_deep else 5.0
            p.voltage, p.narrative_drag = rst_v, rst_d
            self._apply_force(ctx, current_phase, "voltage", self.HARD_FUSE_VOLTAGE, rst_v, "FUSE_BLOWN")
            return True
        if self.pending_drag > 0:
            ctx.physics.narrative_drag += self.pending_drag
            msg = ux("physics_strings", "stabilizer_domestication")
            ctx.log(f"{Prisma.GRY}{msg.format(drag=self.pending_drag)}{Prisma.RST}")
            self.pending_drag = 0.0
        now = time.time()
        dt = max(0.001, min(1.0, now - self.last_tick_time))
        self.last_tick_time = now
        manifold = getattr(p, "manifold", "DEFAULT")
        cfg = self.manifolds.get(manifold, self.manifolds["DEFAULT"])
        target_v = cfg["voltage"]
        if getattr(p, "flow_state", "LAMINAR") in ["SUPERCONDUCTIVE", "FLOW_BOOST"]:
            target_v = p.voltage
            cfg["drag"] = max(0.1, cfg["drag"] * 0.5)
        self.governor.recalibrate(target_v, cfg["drag"])
        v_force, d_force = self.governor.regulate(p, dt=dt)
        c1 = self._apply_force(ctx, current_phase, p, "voltage", v_force, (PHYS_CFG["V_FLOOR"], PHYS_CFG["V_MAX"]), )
        c2 = self._apply_force(ctx, current_phase, p, "narrative_drag", d_force)
        return c1 or c2

    @staticmethod
    def _apply_force(ctx, phase, p, field, force, limits=None):
        if abs(force) <= PHYS_CFG["DEADBAND"]:
            return False
        old_val = getattr(p, field)
        new_val = old_val + force
        if limits:
            new_val = max(limits[0], min(limits[1], new_val))
        else:
            new_val = max(0.0, new_val)
        setattr(p, field, new_val)
        if abs(force) > PHYS_CFG["FLUX_THRESHOLD"]:
            ctx.record_flux(phase, field, old_val, new_val, "PID_CORRECTION")
        return True