"""physics/dynamics.py"""

import math
import random
import time
from collections import Counter, deque
from typing import Dict, List, Any, Tuple, Optional, Deque

from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma

class SurfaceTension:
    """
    Monitors the system's structural integrity against its own output energy.
    Think of this as the logic's outer membrane; if the system generates too much
    voltage without the capacity (kappa) to hold it, the membrane ruptures.
    """

    @staticmethod
    def audit_hubris(physics: Any, config_ref=None) -> Tuple[bool, str, str]:
        """
        Evaluates if the system is flying too close to the sun.

        Returns:
            Tuple[bool, str, str]: (Is_Triggered, Message, State_Flag)
        """
        cfg = getattr(config_ref or BoneConfig, "PHYSICS", BoneConfig.PHYSICS)
        energy_state = safe_get(physics, "energy", physics)

        # Voltage represents active processing heat; Kappa represents structural capacity to hold it.
        current_voltage = float(safe_get(energy_state, "voltage", 0.0))
        current_kappa = float(safe_get(energy_state, "kappa", 0.0))

        # Condition 1: The Icarus Crash. High energy, low capacity. The system is overloading.
        if current_voltage >= getattr(cfg, "VOLTAGE_CRITICAL", 15.0) and current_kappa < 0.4:
            return True, (ux("physics_strings", "hubris_detected") or "").format(voltage=current_voltage), "ICARUS_CRASH"

        # Condition 2: The Flow State. High energy, high capacity. The system is humming perfectly.
        if current_voltage > getattr(cfg, "VOLTAGE_HIGH", 12.0) and current_kappa > 0.8:
            return True, ux("physics_strings", "hubris_flow") or "", "FLOW_BOOST"

        # Baseline: System is operating within normal metabolic parameters.
        return False, "", ""

class ChromaScope:
    """
    Handles terminal UI coloring by translating mathematical energy vectors
    into visual output. Decouples the raw logic from the presentation layer.
    """

    # Class-level cache to prevent querying the LoreManifest on every single print statement.
    _CACHED_MAP = None

    @staticmethod
    def modulate(text: str, vector: Dict[str, float]) -> str:
        """
        Applies a terminal color to a string based on the dominant trait in a given vector.
        """
        from core import LoreManifest

        # If there is no energetic vector, default to a neutral, low-stimulus grey.
        if not vector or not any(vector.values()):
            return f"{Prisma.GRY}{text}{Prisma.RST}"

        # Lazy load and cache the Trigram Map (which maps vectors to colors).
        if ChromaScope._CACHED_MAP is None:
            ChromaScope._CACHED_MAP = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP") or {}

        t_map = ChromaScope._CACHED_MAP

        # Identify the strongest signal in the vector to determine the output color.
        primary = max(vector, key=vector.get)
        color = getattr(Prisma, t_map[primary][3], Prisma.GRY) if primary in t_map else Prisma.GRY

        return f"{color}{text}{Prisma.RST}"

class ZoneInertia:
    """
    Provides friction against rapid, erratic semantic context-switching.
    If the system is currently dwelling in one 'zone', it requires sustained semantic
    pressure (strain) to migrate to a new zone. This creates smooth narrative transitions.
    """

    def __init__(self, inertia=0.7, config_ref=None):
        self.inertia = inertia
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "PHYSICS", None)

        # Minimum turns the system must remain in a zone before being allowed to leave.
        self.min_dwell = getattr(cfg, "ZONE_MIN_DWELL", 2)
        # How much pressure is required to break an active anchor lock.
        self.strain_limit = getattr(cfg, "ZONE_STRAIN_LIMIT", 2.5)
        # The tolerance for geometric distance before we consider the topic to have "moved".
        self.grav_tolerance = getattr(cfg, "ZONE_GRAV_PULL_TOLERANCE", 2.0)

        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector: Optional[Tuple[float, float, float]] = None

        # When anchored, the system actively resists migrating zones.
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        """Manually locks or unlocks the system to its current semantic zone."""
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0  # Reset strain when toggling the lock
        return self.is_anchored

    def stabilize(self, proposed_zone: str, physics: Any, cosmic_state: Tuple[str, float, str]) -> Tuple[str, Optional[str]]:
        """
        The core feedback loop for zone transitions. Evaluates whether the proposed
        new zone has enough gravitational pull to overcome the system's current inertia.
        """
        energy = getattr(physics, "energy", physics)
        matter = getattr(physics, "matter", physics)

        # Extract the current coordinates of the thought process.
        beta = safe_get(energy, "beta_index", 1.0)
        truth = safe_get(matter, "truth_ratio", 0.5)

        # If drifting in the void, the z-axis collapses to 0 to simulate weightlessness.
        current_vec = (beta, truth, 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0)

        self.dwell_counter += 1

        # Calculate the actual physical distance the topic has drifted since the last turn.
        pressure = min(1.0, math.dist(current_vec, self.last_vector) / self.grav_tolerance) if self.last_vector else 0.0

        if self.is_anchored:
            result = self._handle_anchored_state(proposed_zone, pressure)
            self.last_vector = current_vec
            return result

        # If the topic hasn't changed, reset the dwell counter.
        if proposed_zone == self.current_zone:
            self.dwell_counter = 0
            self.last_vector = current_vec
            return proposed_zone, None

        # Prevent jitter: don't allow a zone jump if we just arrived here.
        if self.dwell_counter < self.min_dwell:
            self.last_vector = current_vec
            return self.current_zone, None

        result = self._attempt_migration(proposed_zone, pressure)
        self.last_vector = current_vec
        return result

    def _handle_anchored_state(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        """Handles the logic when the system is deliberately fighting a zone change."""
        if proposed_zone == self.current_zone:
            # The topic aligns with the anchor. Slowly relieve the built-up strain.
            self.strain_gauge = max(0.0, self.strain_gauge - 0.1)
            return self.current_zone, None

        # The topic is pulling away from the anchor. Build up strain.
        self.strain_gauge += pressure

        # If the pull is too strong, the anchor snaps and the system migrates.
        if self.strain_gauge > self.strain_limit:
            self.is_anchored = False
            self.strain_gauge = 0.0
            self.current_zone = proposed_zone
            msg = ux("physics_strings", "anchor_failed")
            return proposed_zone, f"{Prisma.RED}{msg}{Prisma.RST}"

        # The anchor holds, but we warn the user of the building tension.
        msg = ux("physics_strings", "anchor_holding")
        return (self.current_zone,
            f"{Prisma.OCHRE}{msg.format(proposed_zone=proposed_zone, strain=self.strain_gauge, limit=self.strain_limit)}{Prisma.RST}",)

    def _attempt_migration(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        """Probabilistically determines if the topic shift is strong enough to trigger a zone change."""
        # Base probability is derived from inertia, modified by the calculated pressure.
        # Certain high-energy zones (AERIE, THE_FORGE) exert a slightly stronger gravitational pull (+0.2).
        prob = min(0.85, (1.0 - self.inertia) + pressure + (0.2 if proposed_zone in ["AERIE", "THE_FORGE"] else 0.0))

        if random.random() < prob:
            old, self.current_zone = self.current_zone, proposed_zone
            self.dwell_counter = 0
            msg = ux("physics_strings", "zone_migration")
            return self.current_zone, f"{Prisma.CYN}{msg.format(old=old, proposed_zone=proposed_zone)}{Prisma.RST}"

        # The pull wasn't strong enough. The system remains in the current zone.
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(cosmic_drag_penalty: float, current_zone: str) -> float:
        """Special environmental rule: Being high up in the AERIE mitigates cosmic drag."""
        if current_zone == "AERIE" and cosmic_drag_penalty > 0:
            return cosmic_drag_penalty * 0.3
        return cosmic_drag_penalty

class CosmicDynamics:
    """
    The macro-level semantic gravity engine.
    Evaluates the user's active words against the total conceptual network to determine
    what concept the conversation is "orbiting". Handles large-scale systemic states
    like being lost in the void, or getting caught in a gravitational well.
    """

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.voltage_history: Deque[float] = deque(maxlen=20) # Sliding window of recent energy states
        self.cached_wells: Dict = {}
        self.cached_hubs: Dict = {}
        self.last_scan_tick: int = 0
        self.SCAN_INTERVAL: int = 10 # Only rescan the total network mass every 10 ticks to save compute
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        """Pre-loads the narrative strings for various orbital states."""
        keys = ["GRAVITY", "VOID", "NEBULA", "LAGRANGE", "FLOW", "ORBIT"]
        return {k: ux("physics_strings", f"cosmic_{k.lower()}") for k in keys}

    def commit(self, voltage: float):
        """Records the voltage of the current turn into the sliding window."""
        self.voltage_history.append(voltage)

    def check_gravity(self, current_drift: float, psi: float) -> Tuple[float, List[str]]:
        """
        A stabilizing feedback loop. If the conversation drifts too far (high drag),
        gravity steps in to physically pull it back down to a manageable state.
        """
        logs = []
        new_drag = current_drift
        drag_floor = getattr(self.cfg.PHYSICS, "DRAG_FLOOR", 1.0)
        CRITICAL_DRIFT = getattr(self.cfg.PHYSICS, "DRAG_CRITICAL", 8.0)

        # High 'psi' (void/silence) actively dissipates drag.
        if psi > 0.5:
            reduction = (psi - 0.5) * 0.2
            new_drag -= reduction

        # If drift hits critical mass, the system's gravity forcibly corrects it.
        if new_drag > CRITICAL_DRIFT:
            if random.random() < 0.3:
                msg = self.logs.get("GRAVITY", "⚓ GRAVITY").format(drag=new_drag)
                logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
            # Pull the drag back towards the critical line
            pull_strength = (new_drag - CRITICAL_DRIFT) * 0.5
            new_drag -= pull_strength

        # Ensure we never drop below the physical floor of the system
        new_drag = max(drag_floor, new_drag)

        return new_drag, logs

    def analyze_orbit(self, network: Any, clean_words: List[str]) -> Tuple[str, float, str]:
        """
        Calculates the gravitational pull of the current conversation (clean_words)
        against the known massive concepts in the network to determine our orbital state.
        """
        # If we have no words or no map, we are drifting.
        if not (clean_words and network and getattr(network, "graph", None)):
            return "VOID_DRIFT", 3.0, self.logs.get("VOID") or "Drifting in the Void."

        now = int(time.time())

        # Periodically rescan the network to identify where the "heavy" concepts are.
        if not self.cached_wells or (now - self.last_scan_tick) > self.SCAN_INTERVAL:
            self.cached_wells, self.cached_hubs = self._scan_network_mass(network, self.cfg)
            self.last_scan_tick = now

        # Calculate how strongly the current conversation is pulling towards known massive nodes.
        basin_pulls, active_filaments = self._calculate_pull(clean_words, network, self.cached_wells)

        # If we aren't being pulled by anything massive, handle void/nebula states.
        if not any(basin_pulls.values()):
            return self._handle_void_state(clean_words, self.cached_hubs)

        # Resolve which node we are orbiting, or if we are stuck between two.
        return self._resolve_orbit(basin_pulls, active_filaments, len(clean_words), self.cached_wells, self.cfg)

    @staticmethod
    def _scan_network_mass(network, config_ref=None) -> Tuple[Dict, Dict]:
        """Iterates over the entire semantic network to identify the heaviest structural nodes."""
        target_cfg = config_ref or BoneConfig
        gravity_wells = {}
        geodesic_hubs = {}
        well_threshold = getattr(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0)
        geo_strength = getattr(target_cfg, "GEODESIC_STRENGTH", 10.0)

        for node in network.graph:
            mass = network.calculate_mass(node)
            if mass >= well_threshold:
                gravity_wells[node] = mass
            elif mass >= geo_strength:
                geodesic_hubs[node] = mass

        return gravity_wells, geodesic_hubs

    @staticmethod
    def _calculate_pull(words, network, gravity_wells) -> Tuple[Dict, int]:
        """
        Maps the raw frequency of the user's current words against the known gravity wells
        to determine absolute directional pull.
        """
        basin_pulls = {k: 0.0 for k in gravity_wells}
        active_filaments = 0
        word_counts = Counter(words)
        unique_words = set(word_counts.keys())

        for well, well_mass in gravity_wells.items():
            # Direct hits: User explicitly mentions a massive concept.
            if direct_hits := word_counts.get(well, 0):
                basin_pulls[well] += (well_mass * 2.0) * direct_hits
                active_filaments += direct_hits

            # Overlap hits: User mentions concepts connected to the massive concept.
            if overlaps := unique_words & set(network.graph.get(well, {}).get("edges", {})):
                overlap_count = sum(word_counts[w] for w in overlaps)
                basin_pulls[well] += (well_mass * 0.5) * overlap_count
                active_filaments += overlap_count

        return basin_pulls, active_filaments

    def _handle_void_state(self, words, geodesic_hubs) -> Tuple[str, float, str]:
        """Determines if we are totally lost (VOID) or approaching something new (NEBULA)."""
        if hubs_in_void := set(words).intersection(geodesic_hubs.keys()):
            best_hub = max(hubs_in_void, key=lambda w: geodesic_hubs[w])
            msg = (self.logs.get("NEBULA") or "Approaching {node} ({mass})").format(node=best_hub.upper(), mass=int(geodesic_hubs[best_hub]))
            return "PROTO_COSMOS", 1.0, msg

        return "VOID_DRIFT", 3.0, self.logs.get("VOID") or "Drifting in the Void."

    def _resolve_orbit(
        self, basin_pulls, active_filaments, word_count, gravity_wells, config_ref=None) -> Tuple[str, float, str]:
        """
        Final calculation state. Determines if we are cleanly orbiting one concept,
        stuck between two (Lagrange), or being swept away in a watershed flow.
        """
        target_cfg = config_ref or BoneConfig

        # Sort the wells by the strength of their pull on the current prompt.
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        lagrange_tol = getattr(target_cfg, "LAGRANGE_TOLERANCE", 2.0)

        # Check for Lagrange Point (Caught equally between two massive concepts)
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < lagrange_tol:
                msg = (self.logs.get("LAGRANGE") or "Lagrange equilibrium between {p} and {s}").format(p=primary_node.upper(), s=secondary_node.upper())
                return "LAGRANGE_POINT", 0.0, msg

        flow_ratio = active_filaments / max(1, word_count)
        well_threshold = getattr(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0)

        # Check for Watershed Flow (Moving rapidly through connected concepts, but not locked in deep orbit)
        if flow_ratio > 0.5 and primary_str < (well_threshold * 2):
            msg = (self.logs.get("FLOW") or "Caught in the flow of {node}").format(node=primary_node.upper())
            return "WATERSHED_FLOW", 0.0, msg

        # Default State: A stable orbit around a primary concept.
        msg = (self.logs.get("ORBIT") or "Orbiting {node} ({mass})").format(node=primary_node.upper(), mass=int(gravity_wells[primary_node]))
        return "ORBITAL", 0.0, msg