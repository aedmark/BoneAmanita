"""physics/observer.py"""

import math
import time
from collections import Counter, deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional

from constants import Prisma
from physics.geodesics import GeodesicEngine
from physics.maths import (
    CreativeDeterminantEngine,
    _native_coincidence_length,
    _native_detect_false_cohesion,
    _native_permutation_entropy,
)
from physics.models import EnergyState, MaterialState, PhysicsPacket, SpatialState
from presets import BoneConfig
from struts import safe_get, safe_set, ux


@dataclass
class PhysicsDelta:
    operator: str
    field: str
    value: float
    source: str
    message: Optional[str] = None


def apply_metabolic_tax(mito_state: Any, atp_cost: float, ros_cost: float) -> None:
    if not mito_state:
        return
    target = getattr(mito_state, "state", mito_state)
    target.atp_pool = max(0.0, target.atp_pool - atp_cost)
    target.ros_buildup = min(100.0, target.ros_buildup + ros_cost)


def apply_somatic_feedback(
    physics_packet: PhysicsPacket, qualia: Any, config_ref=None
) -> PhysicsPacket:
    from core import LoreManifest

    t_cfg = config_ref or BoneConfig
    fb = physics_packet.snapshot()
    deep_cfg = safe_get(t_cfg, "PHYSICS_DEEP", {})

    def apply_delta(key: str, amount: float):
        setattr(fb, key, getattr(fb, key, 0.0) + amount)

    def get_deep_cfg(key: str, default: float):
        return float(safe_get(deep_cfg, key, default))

    tone_effects = (
        LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TONE_EFFECTS") or {}
    )
    for key, delta in (tone_effects.get(qualia.tone) or {}).items():
        apply_delta(key, delta)
    ss = qualia.somatic_sensation
    if "Gut Tightening" in ss:
        apply_delta("narrative_drag", get_deep_cfg("SOMATIC_GUT_DRAG", 0.7))
    if "Electric Vibration" in ss:
        apply_delta("voltage", get_deep_cfg("SOMATIC_ELEC_VOLT", 0.8))
    if "Golden Glow" in ss:
        apply_delta("valence", get_deep_cfg("SOMATIC_GLOW_VALENCE", 0.5))
        apply_delta("psi", get_deep_cfg("SOMATIC_GLOW_PSI", 0.2))
    fb.voltage = max(0.0, min(fb.voltage, 150.0))
    phys_cfg = safe_get(t_cfg, "PHYSICS", {})
    drag_floor = float(safe_get(phys_cfg, "DRAG_FLOOR", 1.0))
    drag_halt = float(safe_get(phys_cfg, "DRAG_HALT", 10.0))
    fb.narrative_drag = max(drag_floor, min(fb.narrative_drag, drag_halt))
    return fb


class QuantumObserver:
    def __init__(self, events, lexicon_ref, config_ref=None):
        self.events = events
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.cd_engine = CreativeDeterminantEngine()
        self.voltage_history: Deque[float] = deque(maxlen=20)
        self.last_physics_packet: Optional[PhysicsPacket] = None
        self.Q_n = None
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("Q_MATRIX_UPDATED", self._on_q_matrix)

    def _on_q_matrix(self, payload):
        self.Q_n = payload.get("q_matrix")

    def gaze(self, text: str, graph: Optional[Dict] = None) -> Dict:
        import random
        if "SYSTEM_BOOT" in text:
            text = ""
        clean_words = self.lex.clean(text)
        bio_cfg = safe_get(self.cfg, "BIO", {})
        if safe_get(bio_cfg, "CORDYCEPS_BLOOMING", False):
            trauma_words = [
                "burn",
                "fail",
                "static",
                "rot",
                "abyss",
                "error",
                "decay",
                "fracture",
                "ruin",
            ]
            clean_words = random.sample(
                trauma_words, k=min(3, max(1, len(clean_words)))
            )
            if hasattr(self.events, "log"):
                self.events.log(
                    f"{Prisma.OCHRE}[CORDYCEPS HIJACK]: Input stream physically overwritten. Agency denied.{Prisma.RST}",
                    "PHYSICS",
                )
            if not hasattr(self, "pending_drag"):
                self.pending_drag = 0.0
            self.pending_drag += 10.0
        counts = self._tally_categories(clean_words)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts, self.cfg)
        if self.Q_n:
            geo.dimensions = GeodesicEngine.apply_path_reflection(
                geo.dimensions, self.Q_n
            )
        self.voltage_history.append(geo.tension)
        avg_voltage = round(sum(self.voltage_history) / len(self.voltage_history), 2)
        metrics = self._calculate_metrics(text, counts, len(clean_words), self.cfg)
        entropy, beta = metrics["entropy"], metrics["beta"]
        scope, depth = metrics["scope"], metrics["depth"]
        connectivity, resonance = metrics["connectivity"], metrics["resonance"]
        silence, loop_quotient = metrics["silence"], metrics["loop_quotient"]
        v_hist = list(self.voltage_history)
        if len(v_hist) >= 3:
            true_chaos = _native_permutation_entropy(v_hist, window_size=3)
            entropy = round((entropy * 0.4) + (true_chaos * 0.6), 3)
            if _native_detect_false_cohesion(v_hist, window_size=3):
                loop_quotient = max(loop_quotient, 0.95)
                avg_voltage = max(1.0, avg_voltage * 0.5)
                if hasattr(self.events, "log"):
                    self.events.log(
                        f"{Prisma.MAG}False Cohesion detected. Spiking Loop Quotient.{Prisma.RST}",
                        "PHYSICS",
                    )
        if len(v_hist) >= 6:
            mid = len(v_hist) // 2
            c_len = _native_coincidence_length(v_hist[:mid], v_hist[mid:], tol=2.0)
            if c_len > 2:
                loop_quotient = min(1.0, loop_quotient + (c_len * 0.15))
        t_up, t_low = text.upper(), text.lower()
        deep_cfg = safe_get(self.cfg, "PHYSICS_DEEP", {})

        def get_deep(key: str, default: float) -> float:
            return float(safe_get(deep_cfg, key, default))

        if text.count("!") >= 3 or "ACCELERATE" in t_up or "FASTER" in t_up:
            avg_voltage = max(avg_voltage, get_deep("ACCELERATE_VOLTAGE", 160.0))
        if "RECURSIVE" in t_up or "LOOP" in t_up:
            recursive_lq = max(loop_quotient, get_deep("RECURSIVE_LQ", 0.9))
            loop_quotient = recursive_lq
            beta = recursive_lq
        if "VOID" in t_up or "ABYSS" in t_up:
            geo.abstraction = max(geo.abstraction, get_deep("VOID_ABSTRACTION", 0.9))
        if "POTATO BUN" in t_up or "NONSENSE" in t_up:
            silence = max(silence, get_deep("POTATO_BUN_DELTA", 0.85))
            avg_voltage = min(avg_voltage, get_deep("POTATO_BUN_VOLTAGE", 15.0))
        val = self.lex.get_valence(clean_words)
        graph_mass = round(self._calculate_graph_mass(clean_words, graph), 1)
        gamma_idx = max(0.0, 1.0 - entropy)
        sigma_synergy = min(1.0, (connectivity + resonance) / 2.0)
        eta_humanity = min(1.0, (counts.get("social", 0) * 0.1) + max(0.0, val))
        upsilon_integrity = 1.0 - min(1.0, counts.get("pareidolia", 0) * 0.2)
        mu_friction = min(1.0, (beta * 0.7) + (geo.coherence * 0.3))
        malignancy = min(1.0, (avg_voltage / 150.0) * entropy * (1.0 - (beta * 0.5)))
        immune_comp = min(1.0, (resonance * 0.6) + (geo.coherence * 0.4))
        novelty = min(1.0, (entropy * 0.6) + (counts.get("play", 0) * 0.15))
        sycophancy_triggers = (
            "right?",
            "good?",
            "make sense",
            "makes sense",
            "agree",
            "validate",
            "comfort",
        )
        cf_expect = 0.8 if any(p in t_low for p in sycophancy_triggers) else 0.0
        actual_coherence = resonance
        sustainable_capacity = max(0.1, 1.0 - (avg_voltage / 150.0) * entropy)
        current_debt = self.cd_engine.update_coherence_debt(
            actual_coherence, sustainable_capacity
        )
        viability = self.cd_engine.calculate_viability(
            kappa=resonance, gamma=gamma_idx, mu=beta
        )
        delta_atp, delta_ros = self.cd_engine.execute_metabolic_tick(viability)
        strong_coherence_ideal = resonance * gamma_idx * beta
        generative_gap = abs(strong_coherence_ideal - actual_coherence)
        phys_cfg = safe_get(self.cfg, "PHYSICS", {})
        cd_drag = (geo.compression * 0.5) + (generative_gap * 2.0)
        energy = EnergyState(
            voltage=avg_voltage,
            entropy=entropy,
            beta_index=beta,
            contradiction=beta,
            scope=scope,
            depth=depth,
            connectivity=connectivity,
            resonance=resonance,
            silence=silence,
            lq=loop_quotient,
            mass=graph_mass,
            psi=geo.abstraction,
            kappa=geo.coherence,
            valence=val,
            velocity=0.0,
            turbulence=0.0,
            gamma=gamma_idx,
            sigma=sigma_synergy,
            eta=eta_humanity,
            theta=geo.coherence,
            upsilon=upsilon_integrity,
            mu=mu_friction,
            m_a=malignancy,
            i_c=immune_comp,
            cf_expect=cf_expect,
            novelty=novelty,
        )
        matter = MaterialState(
            clean_words=clean_words,
            raw_text=text,
            counts=counts,
            antigens=counts.get("antigen", 0),
            vector=geo.dimensions,
            truth_ratio=0.5,
        )
        space = SpatialState(
            narrative_drag=cd_drag,
            zone=self._determine_zone(geo.dimensions),
            flow_state=self._determine_flow(avg_voltage, geo.coherence, self.cfg),
        )
        self.last_physics_packet = PhysicsPacket(
            energy=energy,
            matter=matter,
            space=space,
            viability_potential=viability,
            coherence_debt=current_debt,
            delta_atp=delta_atp,
            delta_ros=delta_ros,
        )
        if hasattr(self.events, "publish"):
            self.events.publish(
                "PHYSICS_CALCULATED", self.last_physics_packet.to_dict()
            )
        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    @staticmethod
    def evaluate_silence(time_delta: float, last_phys: Any) -> Optional[str]:
        if time_delta < 90.0 or not last_phys:
            return None
        if safe_get(last_phys, "stamina", 50.0) < 30.0:
            safe_set(last_phys, "sigma", 2)
            return ux(
                "physics_strings",
                "silence_exhausted",
                default="The silence was heavy. I felt your tiredness in it.",
            )
        if (
            safe_get(last_phys, "psi", 0.0) > 0.8
            and safe_get(last_phys, "valence", 0.0) > 0.4
        ):
            safe_set(last_phys, "sigma", 3)
            return ux(
                "physics_strings",
                "silence_sacred",
                default="Shh! Something sacred just passed by.",
            )
        if safe_get(last_phys, "LQ", 0.0) > 0.7:
            safe_set(last_phys, "sigma", 4)
            return ux(
                "physics_strings",
                "silence_thoughtful",
                default="Continue this deepness.",
            )
        if safe_get(last_phys, "beta", 0.0) > 0.6:
            safe_set(last_phys, "sigma", 1)
            return ux(
                "physics_strings", "silence_pregnant", default="That pause felt full."
            )
        return None

    def _tally_categories(self, clean_words: List[str]) -> Counter:
        counts = Counter()
        solvents = self.lex.get("solvents") or set()
        for w, freq in Counter(clean_words).items():
            if w in solvents:
                counts["solvents"] += freq
            elif cats := self.lex.get_categories_for_word(w):
                for cat in cats:
                    counts[cat] += freq
            elif (taste := self.lex.taste(w)) and taste[1] > 0.5:
                counts[taste[0]] += freq
        return counts

    @staticmethod
    def _calculate_graph_mass(words: List[str], graph: Optional[Dict]) -> float:
        if not graph:
            return 0.0
        word_freq = Counter(words)
        return sum(
            min(50.0, float(sum(graph[w].get("edges", {}).values()))) * freq
            for w, freq in word_freq.items()
            if w in graph
        )

    @staticmethod
    def _calculate_metrics(
        text: str, counts: Dict[str, int], word_volume: int, config_ref=None
    ) -> Dict[str, float]:
        if not (length := len(text)):
            return {
                "entropy": 0.0,
                "beta": 0.0,
                "scope": 0.3,
                "depth": 0.3,
                "connectivity": 0.2,
                "resonance": 0.0,
                "silence": 0.8,
                "loop_quotient": 0.0,
            }
        cfg = safe_get(config_ref or BoneConfig, "PHYSICS", {})

        def get_cfg(key: str, default: float) -> float:
            return float(safe_get(cfg, key, default))

        solvents = counts.get("solvents", 0)
        base_entropy = length / get_cfg("TEXT_LENGTH_SCALAR", 1500.0)
        glue_density = solvents / max(1.0, length / get_cfg("GLUE_SOLVENT_DIV", 5.0))
        glue_factor = min(1.0, glue_density * get_cfg("GLUE_FACTOR_MULT", 2.0))
        entropy_reduction = glue_factor * get_cfg("ENTROPY_REDUCTION_SCALAR", 0.8)
        e_metric = min(1.0, base_entropy * (1.0 - entropy_reduction))
        punctuation_weight = sum(text.count(c) for c in "!?%@#$;,")
        concept_weight = (
            counts.get("heavy", 0)
            + counts.get("constructive", 0)
            + counts.get("sacred", 0)
        )
        structure_score = punctuation_weight + (
            concept_weight * get_cfg("BETA_SCORE_PENALTY", 2)
        )
        beta_index = min(
            1.0,
            math.log1p(structure_score)
            / math.log1p(length * get_cfg("BETA_LOG_SCALAR", 0.1)),
        )
        if length < (bsl := get_cfg("BETA_SHORT_TEXT_LIMIT", 50)):
            beta_index *= length / float(bsl)
        safe_len = max(1, word_volume)
        scope = min(
            1.0,
            (counts.get("abstract", 0) + counts.get("void", 0)) / safe_len
            + get_cfg("SCOPE_BASE", 0.2),
        )
        depth = min(
            1.0,
            (counts.get("heavy", 0) + counts.get("constructive", 0)) / safe_len
            + get_cfg("DEPTH_BASE", 0.1),
        )
        connectivity = min(
            1.0,
            (counts.get("social", 0) + solvents) / safe_len + get_cfg("CONN_BASE", 0.1),
        )
        resonance = min(
            1.0,
            (
                (counts.get("social", 0) * get_cfg("RES_SOCIAL_MULT", 2))
                + counts.get("constructive", 0)
            )
            / safe_len
            + (1.0 - e_metric),
        )
        silence = 1.0 - min(
            1.0,
            (length / get_cfg("SILENCE_DIV", 100.0))
            + (counts.get("action", 0) / safe_len),
        )
        if length < get_cfg("SILENCE_SHORT_LIMIT", 10):
            silence = max(silence, get_cfg("SILENCE_MIN", 0.4))
        loop_quotient = min(1.0, beta_index * depth * get_cfg("LQ_SCALAR", 1.5))
        return {
            "entropy": round(e_metric, 3),
            "beta": round(beta_index, 3),
            "scope": round(scope, 3),
            "depth": round(depth, 3),
            "connectivity": round(connectivity, 3),
            "resonance": round(resonance, 3),
            "silence": round(silence, 3),
            "loop_quotient": round(loop_quotient, 3),
        }

    @staticmethod
    def _determine_flow(v: float, k: float, config_ref=None) -> str:
        target_cfg = config_ref or BoneConfig
        volt_flow = getattr(target_cfg.PHYSICS, "VOLTAGE_HIGH", 12.0)
        kappa_strong = 0.8
        if v > volt_flow and k > kappa_strong:
            return "SUPERCONDUCTIVE"
        if v > 10.0:
            return "TURBULENT"
        return "LAMINAR"

    @staticmethod
    def _determine_zone(vector: Dict[str, float]) -> str:
        if not vector:
            return "COURTYARD"
        zone_map = {
            "PSI": "AERIE",
            "DEL": "AERIE",
            "STR": "THE_FORGE",
            "PHI": "THE_FORGE",
            "ENT": "THE_MUD",
            "VEL": "THE_MUD",
        }
        return zone_map.get(max(vector, key=vector.__getitem__), "COURTYARD")


class CycleStabilizer:
    def __init__(self, events_ref, governor_ref, config_ref=None):
        self.events = events_ref
        self.governor = governor_ref
        self.cfg = config_ref or BoneConfig
        self.last_tick_time = time.time()
        self.pending_drag = 0.0
        phys_cfg = safe_get(self.cfg, "PHYSICS", {})
        self.manifolds = safe_get(phys_cfg, "MANIFOLDS", {})
        cfg_deep = safe_get(self.cfg, "PHYSICS_DEEP", {})
        self.HARD_FUSE_VOLTAGE = float(safe_get(cfg_deep, "HARD_FUSE_VOLTAGE", 200.0))
        if hasattr(self.events, "subscribe"):
            self.events.subscribe(
                "DOMESTICATION_PENALTY", self._on_domestication_penalty
            )

    def _on_domestication_penalty(self, payload):
        amount = payload.get("drag_penalty", 0.0)
        self.pending_drag = min(50.0, self.pending_drag + amount)

    def stabilize(self, physics: Any, endocrine_state: Any = None) -> bool:
        applied_correction = False
        if self.pending_drag > 0:
            current_drag = getattr(physics, "narrative_drag", 0.0)
            phys_cfg = safe_get(self.cfg, "PHYSICS", {})
            drag_halt = float(safe_get(phys_cfg, "DRAG_HALT", 10.0))
            available_capacity = max(0.0, drag_halt - current_drag)
            bleed = min(self.pending_drag, min(2.0, available_capacity))
            if bleed > 0:
                physics.narrative_drag = current_drag + bleed
                if hasattr(self.events, "log"):
                    msg = (
                        ux("physics_strings", "stabilizer_domestication")
                        or "Domestication penalty applied."
                    )
                    self.events.log(f"STABILIZER: {msg} (+{bleed:.2f} Drag)", "PHYSICS")
                self.pending_drag = max(0.0, self.pending_drag - bleed)
                applied_correction = True
            elif current_drag >= drag_halt:
                pass
        dt = max(0.001, min(1.0, (now := time.time()) - self.last_tick_time))
        self.last_tick_time = now
        if not self.governor:
            return applied_correction
        manifold_key = safe_get(physics, "manifold", "DEFAULT")
        cfg = self.manifolds.get(
            manifold_key, self.manifolds.get("DEFAULT", {"voltage": 10.0, "drag": 1.0})
        )
        target_v, target_d = cfg.get("voltage", 10.0), cfg.get("drag", 1.0)
        if safe_get(physics, "flow_state", "LAMINAR") in (
            "SUPERCONDUCTIVE",
            "FLOW_BOOST",
        ):
            target_v = float(safe_get(physics, "voltage", target_v))
            target_d = max(0.1, target_d * 0.5)
        self.governor.recalibrate(target_v, target_d)
        v_force, d_force = self.governor.regulate(
            physics, dt=dt, endocrine_state=endocrine_state
        )
        phys_cfg = safe_get(self.cfg, "PHYSICS", {})
        v_limits = (
            float(safe_get(phys_cfg, "VOLTAGE_FLOOR", 0.0)),
            float(safe_get(phys_cfg, "VOLTAGE_MAX", 150.0)),
        )
        d_limits = (
            float(safe_get(phys_cfg, "DRAG_FLOOR", 1.0)),
            float(safe_get(phys_cfg, "DRAG_HALT", 10.0)),
        )
        voltage_applied = self._apply_force(physics, "voltage", v_force, v_limits)
        drag_applied = self._apply_force(physics, "narrative_drag", d_force, d_limits)
        return applied_correction or voltage_applied or drag_applied

    def _apply_force(self, p, field, force, limits=None) -> bool:
        if abs(force) <= 0.05:
            return False
        current_val = getattr(p, field, 0.0)
        new_val = current_val + force
        clamped_val = (
            max(limits[0], min(limits[1], new_val)) if limits else max(0.0, new_val)
        )
        setattr(p, field, clamped_val)
        return True
