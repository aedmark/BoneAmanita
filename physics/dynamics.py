"""physics/dynamics.py"""

import heapq
import math
import random
import time
from collections import Counter, deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from constants import Prisma
from presets import BoneConfig
from struts import safe_get, ux


class SurfaceTension:
    @staticmethod
    def audit_hubris(physics: Any, config_ref=None) -> Tuple[bool, str, str]:
        cfg_obj = config_ref or BoneConfig
        cfg = safe_get(cfg_obj, "PHYSICS", {})
        current_voltage = float(getattr(physics, "voltage", 0.0))
        current_kappa = float(getattr(physics, "kappa", 0.0))
        v_crit = float(safe_get(cfg, "VOLTAGE_CRITICAL", 15.0))
        v_high = float(safe_get(cfg, "VOLTAGE_HIGH", 12.0))
        if current_voltage >= v_crit and current_kappa < 0.4:
            return (
                True,
                (ux("physics_strings", "hubris_detected") or "").format(
                    voltage=current_voltage
                ),
                "ICARUS_CRASH",
            )
        if current_voltage > v_high and current_kappa > 0.8:
            return True, ux("physics_strings", "hubris_flow") or "", "FLOW_BOOST"
        return False, "", ""


class ChromaScope:
    _T_MAP_CACHE = None

    @staticmethod
    def modulate(text: str, vector: Dict[str, float]) -> str:
        if ChromaScope._T_MAP_CACHE is None:
            from core import LoreManifest

            ChromaScope._T_MAP_CACHE = (
                LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP")
                or {}
            )
        if not vector or not any(vector.values()):
            return f"{Prisma.GRY}{text}{Prisma.RST}"
        t_map = ChromaScope._T_MAP_CACHE
        primary = max(vector, key=lambda k: float(vector[k]))
        color = (
            getattr(Prisma, t_map[primary][3], Prisma.GRY)
            if primary in t_map
            else Prisma.GRY
        )
        return f"{color}{text}{Prisma.RST}"


class ZoneInertia:
    def __init__(self, inertia=0.7, config_ref=None):
        self.inertia = inertia
        self.cfg = config_ref or BoneConfig
        cfg = safe_get(self.cfg, "PHYSICS", {})
        self.min_dwell = int(safe_get(cfg, "ZONE_MIN_DWELL", 2))
        self.strain_limit = float(safe_get(cfg, "ZONE_STRAIN_LIMIT", 2.5))
        self.grav_tolerance = float(safe_get(cfg, "ZONE_GRAV_PULL_TOLERANCE", 2.0))
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector: Optional[Tuple[float, float, float]] = None
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0
        return self.is_anchored

    def stabilize(
        self, proposed_zone: str, physics: Any, cosmic_state: Tuple[str, float, str]
    ) -> Tuple[str, Optional[str]]:
        beta = float(safe_get(physics, "beta_index", 1.0))
        truth = float(safe_get(physics, "truth_ratio", 0.5))
        current_vec = (beta, truth, 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0)
        self.dwell_counter += 1
        pressure = (
            min(1.0, math.dist(current_vec, self.last_vector) / self.grav_tolerance)
            if self.last_vector
            else 0.0
        )
        if self.is_anchored:
            result = self._handle_anchored_state(proposed_zone, pressure)
        elif proposed_zone == self.current_zone:
            self.dwell_counter = 0
            result = proposed_zone, None
        elif self.dwell_counter < self.min_dwell:
            result = self.current_zone, None
        else:
            result = self._attempt_migration(proposed_zone, pressure)
        self.last_vector = current_vec
        return result

    def _handle_anchored_state(
        self, proposed_zone: str, pressure: float
    ) -> Tuple[str, Optional[str]]:
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
        return (
            self.current_zone,
            f"{Prisma.OCHRE}{msg.format(proposed_zone=proposed_zone, strain=self.strain_gauge, limit=self.strain_limit)}{Prisma.RST}",
        )

    def _attempt_migration(
        self, proposed_zone: str, pressure: float
    ) -> Tuple[str, Optional[str]]:
        prob = min(
            0.85,
            (1.0 - self.inertia)
            + pressure
            + (0.2 if proposed_zone in ["AERIE", "THE_FORGE"] else 0.0),
        )
        if random.random() < prob:
            old, self.current_zone = self.current_zone, proposed_zone
            self.dwell_counter = 0
            msg = ux("physics_strings", "zone_migration")
            return (
                self.current_zone,
                f"{Prisma.CYN}{msg.format(old=old, proposed_zone=proposed_zone)}{Prisma.RST}",
            )
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(
        cosmic_drag_penalty: float, current_zone: str, config_ref=None
    ) -> float:
        low_drag = safe_get(
            safe_get(config_ref or BoneConfig, "PHYSICS", {}),
            "LOW_DRAG_ZONES",
            ["AERIE"],
        )
        return (
            cosmic_drag_penalty * 0.3
            if current_zone in low_drag and cosmic_drag_penalty > 0
            else cosmic_drag_penalty
        )


class CosmicDynamics:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.voltage_history: Deque[float] = deque(maxlen=20)
        self.cached_wells: Dict = {}
        self.cached_hubs: Dict = {}
        self.last_scan_time: int = 0
        self.SCAN_INTERVAL: int = 10
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        keys = ["GRAVITY", "VOID", "NEBULA", "LAGRANGE", "FLOW", "ORBIT"]
        return {k: ux("physics_strings", f"cosmic_{k.lower()}") for k in keys}

    def commit(self, voltage: float):
        self.voltage_history.append(voltage)

    def check_gravity(
        self, current_drift: float, psi: float
    ) -> Tuple[float, List[str]]:
        logs = []
        new_drag = current_drift
        cfg_obj = self.cfg
        phys_cfg = safe_get(cfg_obj, "PHYSICS", {})
        drag_floor = float(safe_get(phys_cfg, "DRAG_FLOOR", 1.0))
        CRITICAL_DRIFT = float(safe_get(phys_cfg, "DRAG_CRITICAL", 8.0))
        if psi > 0.5:
            reduction = (psi - 0.5) * 0.2
            new_drag -= reduction
        if new_drag > CRITICAL_DRIFT:
            new_drag -= (new_drag - CRITICAL_DRIFT) * 0.5
            if random.random() < 0.3 and (msg := self.logs.get("GRAVITY")):
                logs.append(f"{Prisma.GRY}{msg.format(drag=new_drag)}{Prisma.RST}")
        new_drag = max(drag_floor, new_drag)
        return new_drag, logs

    def analyze_orbit(
        self, network: Any, clean_words: List[str]
    ) -> Tuple[str, float, str]:
        if not clean_words or not network or not network.graph:
            return "VOID_DRIFT", 3.0, self.logs.get("VOID") or "Drifting in the Void."
        unique_word_count = len(set(clean_words))
        fractal_density = unique_word_count / max(1, len(clean_words))
        if fractal_density > 0.85 and len(clean_words) > 50:
            return (
                "FRACTAL_OVERLOAD",
                5.0,
                "Context density critical. The water tank is empty. Flush or simplify.",
            )
        now = int(time.time())
        if not self.cached_wells or (now - self.last_scan_time) > self.SCAN_INTERVAL:
            self.cached_wells, self.cached_hubs = self._scan_network_mass(
                network, self.cfg
            )
            self.last_scan_time = now
        basin_pulls, active_filaments = self._calculate_pull(
            clean_words, network, self.cached_wells
        )
        if not any(basin_pulls.values()):
            return self._handle_void_state(clean_words, self.cached_hubs)
        return self._resolve_orbit(
            basin_pulls, active_filaments, len(clean_words), self.cached_wells, self.cfg
        )

    @staticmethod
    def _scan_network_mass(network, config_ref=None) -> Tuple[Dict, Dict]:
        target_cfg = config_ref or BoneConfig
        gravity_wells = {}
        geodesic_hubs = {}
        well_threshold = float(safe_get(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0))
        geo_strength = float(safe_get(target_cfg, "GEODESIC_STRENGTH", 10.0))
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
        unique_words = set(word_counts.keys())
        for well, well_mass in gravity_wells.items():
            if direct_hits := word_counts.get(well, 0):
                basin_pulls[well] += (well_mass * 2.0) * direct_hits
                active_filaments += direct_hits
            if overlaps := unique_words & network.graph[well]["edges"].keys():
                overlap_count = sum(word_counts[w] for w in overlaps)
                basin_pulls[well] += (well_mass * 0.5) * overlap_count
                active_filaments += overlap_count
        return basin_pulls, active_filaments

    def _handle_void_state(self, words, geodesic_hubs) -> Tuple[str, float, str]:
        if hubs_in_void := set(words).intersection(geodesic_hubs.keys()):
            best_hub = max(hubs_in_void, key=lambda w: geodesic_hubs[w])
            msg = (self.logs.get("NEBULA") or "Approaching {node} ({mass})").format(
                node=best_hub.upper(), mass=int(geodesic_hubs[best_hub])
            )
            return "PROTO_COSMOS", 1.0, msg
        return "VOID_DRIFT", 3.0, self.logs.get("VOID") or "Drifting in the Void."

    def _resolve_orbit(
        self, basin_pulls, active_filaments, word_count, gravity_wells, config_ref=None
    ) -> Tuple[str, float, str]:
        target_cfg = config_ref or BoneConfig
        top_basins = heapq.nlargest(2, basin_pulls.items(), key=lambda x: x[1])
        primary_node, primary_str = top_basins[0]
        lagrange_tol = float(safe_get(target_cfg, "LAGRANGE_TOLERANCE", 2.0))
        if len(top_basins) > 1:
            secondary_node, secondary_str = top_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < lagrange_tol:
                msg = (
                    self.logs.get("LAGRANGE")
                    or "Lagrange equilibrium between {p} and {s}"
                ).format(p=primary_node.upper(), s=secondary_node.upper())
                return "LAGRANGE_POINT", 0.0, msg
        flow_ratio = active_filaments / max(1, word_count)
        well_threshold = float(safe_get(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0))
        if flow_ratio > 0.5 and primary_str < (well_threshold * 2):
            msg = (self.logs.get("FLOW") or "Caught in the flow of {node}").format(
                node=primary_node.upper()
            )
            return "WATERSHED_FLOW", 0.0, msg
        msg = (self.logs.get("ORBIT") or "Orbiting {node} ({mass})").format(
            node=primary_node.upper(), mass=int(gravity_wells[primary_node])
        )
        return "ORBITAL", 0.0, msg
