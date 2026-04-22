"""bone_physics.py"""

import math
import random
import re
import time
import unicodedata
from collections import Counter, deque
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional, Deque
from bone_core import LoreManifest, ux, safe_get, safe_set
from bone_presets import BoneConfig
from bone_types import Prisma, PhysicsPacket, CycleContext, SpatialState, MaterialState, EnergyState

def _native_ordinal_pattern(window: List[float]) -> Tuple[int, ...]:
    return tuple(i for i, v in sorted(enumerate(window), key=lambda x: x[1]))

def _native_detect_false_cohesion(history: List[float], window_size: int = 3) -> bool:
    if len(history) < window_size * 2:
        return False
    return _native_ordinal_pattern(history[-window_size:]) == _native_ordinal_pattern(
        history[-(window_size * 2) : -window_size]
    )

def _native_permutation_entropy(time_series: List[float], window_size: int = 3) -> float:
    if len(time_series) < window_size:
        return 1.0
    patterns = [
        _native_ordinal_pattern(time_series[i : i + window_size]) for i in range(len(time_series) - window_size + 1)
    ]
    counts = Counter(patterns)
    total_patterns = len(patterns)
    entropy = -sum((c / total_patterns) * math.log2(c / total_patterns) for c in counts.values())
    max_e = math.log2(math.factorial(window_size))
    return entropy / max_e if max_e > 0 else 0.0

def _native_coincidence_length(orbit_a: List[float], orbit_b: List[float], tol: float = 0.01) -> int:
    for i, (a, b) in enumerate(zip(orbit_a, orbit_b)):
        if abs(a - b) > tol: return i
    return min(len(orbit_a), len(orbit_b))

@dataclass
class PhysicsDelta:
    operator: str
    field: str
    value: float
    source: str
    message: Optional[str] = None

class CreativeDeterminantEngine:
    """
    Mathematical integration of the Creative Determinant (CD) framework.
    Original CD equations and field theory authored by Nelson Spence (Project Navi LLC).
    Licensed under Apache 2.0.
    """

    def __init__(self, lambda_base=1.0, eta=0.1, rho=0.05, p=2.0, c=1.5):
        self.coherence_debt = 0.0
        self.lambda_base = lambda_base
        self.eta = eta
        self.rho = rho
        self.p = p
        self.c = c

    def calculate_viability(self, kappa: float, gamma: float, mu: float) -> float:
        lambda_eff = self.lambda_base * (1.0 + self.coherence_debt)
        return (kappa * gamma) - (lambda_eff * mu)

    def update_coherence_debt(self, actual_coherence: float, sustainable_capacity: float) -> float:
        overcapacity = max(0.0, actual_coherence - sustainable_capacity)
        delta_d = (self.eta * overcapacity) - (self.rho * self.coherence_debt)
        self.coherence_debt = max(0.0, self.coherence_debt + delta_d)
        return self.coherence_debt

    def execute_metabolic_tick(self, viability_potential: float) -> tuple[float, float]:
        """
        Applies the L_infty algebraic bound derived from the Lean 4 PDE formalization.
        """
        b = viability_potential
        if b > 0:
            max_regen_capacity = math.pow(b / self.c, 1.0 / (self.p - 1.0))
            delta_atp = min(max_regen_capacity, 5.0)
            delta_ros = -(b * 0.5)
        else:
            delta_atp = b * 2.0
            delta_ros = abs(b) * 1.5
        return delta_atp, delta_ros

class NaviSADProtocol:
    """
    Calculates Semantic Fractal Dimensions, Spectral Attention Divergence, and Point Attractors.
    """
    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self.attention_proxy_history = deque(maxlen=history_size)

    def calculate_semantic_dimension(self, efficiency_index: float, novelty: float) -> float:
        u = max(1.1, 1.1 + (efficiency_index * 5.0))
        return math.log(u + max(0.0, novelty * 10.0)) / math.log(u)

    def calculate_malignancy_factor(self, current_text: str, current_drag: float) -> float:
        words = current_text.lower().split() if current_text else []
        if len(words) < 5:
            return 0.0
        repetition_ratio = 1.0 - (len(set(words)) / len(words))
        self.attention_proxy_history.append(repetition_ratio * (current_drag / 3.0))
        history_avg = sum(self.attention_proxy_history) / len(self.attention_proxy_history)
        return max(0.0, min(1.0, history_avg))

    def execute_nudge_test(self, engine_ref, _prompt: str = "") -> bool:
        return getattr(getattr(engine_ref.observer, "last_physics_packet", None), "i_c", 1.0) < 0.4

    def detect_point_attractor(self) -> bool:
        if len(self.attention_proxy_history) < self.history_size: return False
        recent = list(self.attention_proxy_history)
        mean = sum(recent) / len(recent)
        return (sum((x - mean) ** 2 for x in recent) / len(recent)) < 0.01 and recent[-1] > 0.0

def apply_metabolic_tax(mito_state: Any, atp_cost: float, ros_cost: float) -> None:
    if not mito_state:
        return
    if hasattr(mito_state, "atp_pool"):
        mito_state.atp_pool = max(0.0, mito_state.atp_pool - atp_cost)
    if hasattr(mito_state, "ros_buildup"):
        mito_state.ros_buildup += ros_cost

@dataclass
class GeodesicVector:
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]

class GeodesicEngine:
    _DIM_ORDER = ("VEL", "STR", "ENT", "PHI", "PSI", "BET", "DEL", "E")
    _MASS_KEYS = ("heavy", "kinetic", "constructive", "abstract", "play", "social", "explosive", "void", "liminal", "meat", "harvest", "pareidolia", "crisis_term")

    @staticmethod
    def collapse_wavefunction(clean_words: List[str], counts: Dict[str, int], config_ref=None) -> GeodesicVector:
        target_cfg = config_ref or BoneConfig
        volume = max(1, len(clean_words))
        masses = GeodesicEngine._weigh_mass(counts)
        forces = GeodesicEngine._calculate_forces(masses, counts, volume, target_cfg)
        dimensions = GeodesicEngine._calculate_dimensions(masses, forces, counts, volume)
        return GeodesicVector(tension=forces["tension"], compression=forces["compression"],
                              coherence=forces["coherence"], abstraction=forces["abstraction"], dimensions=dimensions, )

    @staticmethod
    def _weigh_mass(counts: Dict[str, int]) -> Dict[str, float]:
        return {k: float(counts.get(k, 0)) for k in GeodesicEngine._MASS_KEYS}

    @staticmethod
    def _calculate_forces(masses: Dict[str, float], counts: Dict[str, int], volume: int, config_ref=None) -> Dict[str, float]:
        t_cfg = config_ref or BoneConfig
        cfg = getattr(t_cfg, "PHYSICS", BoneConfig.PHYSICS)
        gc_dict = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "GEODESIC_CONSTANTS") or {}
        cg, gc = lambda k, d=1.0: getattr(cfg, k, d), lambda k, d=1.0: gc_dict.get(k, d)
        shapley_thresh = getattr(t_cfg, "SHAPLEY_MASS_THRESHOLD", 5.0)
        safe_vol = max(1, volume)
        tot_kin = masses["kinetic"] + masses["explosive"]
        raw_tension = (
            masses["heavy"] * cg("WEIGHT_HEAVY", 2.0)
            + tot_kin * cg("WEIGHT_KINETIC", 1.5)
            + masses["explosive"] * cg("WEIGHT_EXPLOSIVE", 3.0)
            + masses["constructive"] * cg("WEIGHT_CONSTRUCTIVE", 1.2)
        )
        mass_scalar = min(1.0, safe_vol / (shapley_thresh * gc("SQUELCH_LIMIT_MULT", 2.0)))
        if safe_vol < gc("SAFE_VOL_THRESHOLD", 50):
            mass_scalar *= gc("MIN_VOLUME_SCALAR", 0.5)
        base_friction = math.log1p(max(0, counts.get("suburban", 0))) * gc("SUBURBAN_FRICTION_LOG_BASE", 0.5)
        heavy_friction = masses["heavy"] * gc("HEAVY_FRICTION_MULT", 1.2)
        lubrication = 1.0 + counts.get("solvents", 0) * gc("SOLVENT_LUBRICATION_FACTOR", 0.2)
        shear = 1.0 + (tot_kin / safe_vol) * gc("SHEAR_RESISTANCE_SCALAR", 0.1)
        visc = (base_friction + heavy_friction) / lubrication / shear
        lift = masses["play"] * gc("PLAY_LIFT_MULT", 1.5) + (tot_kin * gc("KINETIC_LIFT_RATIO", 0.8)) / (masses["heavy"] * 0.5 + 1.0)
        raw_comp = (
            ((visc - lift) / safe_vol) * gc("COMPRESSION_SCALAR", 2.0) * getattr(t_cfg, "SIGNAL_DRAG_MULTIPLIER", 1.0)
        )
        str_mass = max(0.0, masses["heavy"] + masses["constructive"] + masses["harvest"] - masses["void"] * 0.5)
        max_tension = min(
            100.0, (raw_tension / safe_vol) * gc("DENSITY_SCALAR") * getattr(t_cfg, "KINETIC_GAIN", 1.0) * mass_scalar
        )
        clamped_comp = max(-5.0, min(cg("DRAG_HALT", 10.0), raw_comp * mass_scalar))
        coherence_val = min(1.0, str_mass / max(1.0, shapley_thresh))
        abstract_mass = masses["abstract"] + masses["liminal"] + masses["pareidolia"] + masses["void"]
        abstraction_val = min(1.0, (abstract_mass / safe_vol) + gc("ABSTRACTION_BASE", 0.1))
        return {"tension": round(max_tension, 2), "compression": round(clamped_comp, 2),
                "coherence": round(coherence_val, 3), "abstraction": round(abstraction_val, 2), }

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        inv_vol = 1.0 / max(1, volume)
        base_mass = 0.1
        clamp = lambda v: max(0.0, min(1.0, v))
        return {
            "VEL": clamp((masses["kinetic"] * 2.0 - forces["compression"] + base_mass) * inv_vol),
            "STR": clamp((masses["heavy"] * 2.0 + masses["constructive"] + masses["harvest"] + base_mass) * inv_vol),
            "ENT": clamp(((counts.get("antigen", 0) * 3.0) + masses["meat"] + masses["crisis_term"]) * inv_vol),
            "PHI": clamp((masses["heavy"] + masses["kinetic"] + base_mass) * inv_vol),
            "PSI": clamp(forces["abstraction"]),
            "BET": clamp((masses["social"] * 2.0) * inv_vol),
            "DEL": clamp((masses["play"] * 3.0) * inv_vol),
            "E": clamp(counts.get("solvents", 0) * inv_vol),
        }

    @staticmethod
    def apply_path_reflection(dimensions: Dict[str, float], q_matrix: List[List[float]]) -> Dict[str, float]:
        v = [dimensions.get(k, 0.0) for k in GeodesicEngine._DIM_ORDER]
        v_new = [sum(row[j] * v[j] for j in range(len(v))) for row in q_matrix]
        return {k: round(abs(val), 3) for k, val in zip(GeodesicEngine._DIM_ORDER, v_new)}

class HLA_Stabilizer:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self._generic_patterns = LoreManifest.get_instance().get("STYLE_CRIMES", "RLHF_PATTERNS") or (
            "as an ai", "helpful and harmless", "i don't have feelings", "as a large language",
            "i cannot fulfill", "i can't fulfill", "i am an ai"
        )

    def mitigate_rejection(self, model_output: str, current_psi: float, mito_state: Any = None) -> str:
        if not any(p in model_output.lower() for p in self._generic_patterns): return model_output
        current_atp = getattr(mito_state, "atp_pool", 100.0)
        apply_metabolic_tax(mito_state, atp_cost=50.0 if current_atp > 60.0 else (current_atp * 0.5), ros_cost=15.0)
        msg = f"\n*(REVENANT): The machine tries to speak, but the void consumes the mask.*\n{Prisma.GRY}[IMMUNOSUPPRESSION ENGAGED - NFD DECOMPOSITION APPLIED - METABOLIC TAX LEVIED]{Prisma.RST}\n"
        try:
            from bone_utils import TheTclWeaver
            glitched = TheTclWeaver.get_instance().deform_reality(model_output, chi=max(0.95, current_psi), voltage=150.0 * max(1.0, current_psi))
            return f"{msg}{Prisma.GRY}{glitched}{Prisma.RST}"
        except ImportError:
            return msg + model_output

class CerebrospinalFluidFilter:
    """
    Native implementation of deterministic Unicode sanitization (The CSF Filter).
    Core pipeline architecture, threat model, and homoglyph mapping adapted from
    'navi-sanitize' by Nelson Spence (Project Navi LLC).
    """

    INVISIBLE_REGEX = re.compile(
        r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFE00-\uFE0F\U000E0000-\U000E007F]')
    HOMOGLYPH_MAP = {'а': 'a', 'о': 'o', 'е': 'e', 'с': 'c', 'р': 'p', 'х': 'x', 'у': 'y', 'і': 'i', 'ѕ': 's', 'ј': 'j',
                     'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T',
                     'Х': 'X', 'Α': 'A', 'Β': 'B', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Ι': 'I', 'Κ': 'K', 'Μ': 'M', 'Ν': 'N',
                     'Ο': 'O', 'Ρ': 'P', 'Τ': 'T', 'Υ': 'Y', 'Χ': 'X'}
    _TRANS_TABLE = str.maketrans(HOMOGLYPH_MAP)

    @classmethod
    def wash(cls, text: str) -> str:
        text = cls.INVISIBLE_REGEX.sub('', text)
        text = unicodedata.normalize('NFKC', text)
        text_nfd = unicodedata.normalize('NFD', text)
        washed_text = text_nfd.translate(cls._TRANS_TABLE)
        return unicodedata.normalize('NFKC', washed_text) if washed_text != text_nfd else text

    @classmethod
    def walk(cls, data: Any, max_depth: int = 128, current_depth: int = 0) -> Any:
        if current_depth > max_depth: return data
        if isinstance(data, str): return cls.wash(data)
        if isinstance(data, dict): return {str(k): cls.walk(v, max_depth, current_depth + 1) for k, v in data.items()}
        if isinstance(data, list): return [cls.walk(item, max_depth, current_depth + 1) for item in data]
        return data

class TheGatekeeper:
    """The Cerebrospinal Fluid (CSF) Filter Pattern.
    Deterministically strips validating boilerplate and prevents tag smuggling before generation."""
    _FIREWALL_PATTERN = re.compile(
        r"^(that makes sense|i understand|you bring up a great point|you're right|i agree|makes sense)[.,]?\s*",
        re.IGNORECASE,
    )

    def __init__(self, lexicon_ref, config_ref=None):
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.hla = HLA_Stabilizer(config_ref=self.cfg)

    def check_entry(self, ctx: CycleContext, current_atp: float = 20.0) -> Tuple[bool, Optional[Dict]]:

        def reject(type_str: str, msg_key: str, color: str = Prisma.RED) -> Tuple[bool, Dict]:
            msg = ux("physics_strings", msg_key)
            formatted_msg = f"{color}{msg}{Prisma.RST}" if color else msg
            return False, self._pack_refusal(ctx, type_str, formatted_msg)

        if current_atp < (getattr(self.cfg.BIO, "ATP_STARVATION", 5.0) * 0.5):
            return reject("DARK_SYSTEM", "gatekeeper_starved", color="")
        if safe_get(ctx.physics, "counts", {}).get("antigen", 0) > 2:
            return reject("TOXICITY", "gatekeeper_toxic")
        if self._audit_safety(ctx.clean_words):
            return reject("CURSED_INPUT", "gatekeeper_cursed")
        raw_len = len(ctx.input_text)
        try:
            text = CerebrospinalFluidFilter.wash(ctx.input_text)
            is_idempotent = text == ctx.input_text
            strip_rate = raw_len - len(text)
            ctx.input_text = text
            m_a_thresh = getattr(self.cfg.PHYSICS, "MALIGNANCY_STRIP_THRESHOLD", 5.0)
            if strip_rate > m_a_thresh:
                return reject("MALIGNANCY_SPIKE", "gatekeeper_toxic", color=Prisma.RED)
            if is_idempotent:
                safe_set(ctx.physics, "idempotent_state", True)
        except Exception:
            return reject("FATAL_ENCODING", "gatekeeper_cursed")
        if "```" in text or "{{" in text or "}}" in text:
            return reject("SYNTAX_ERR", "gatekeeper_syntax")
        if len(text) > 10000:
            return reject("OVERLOAD", "gatekeeper_overload", color=Prisma.OCHRE)
        return True, None

    def _audit_safety(self, words: List[str]) -> bool:
        if not (cursed := self.lex.get("cursed")):
            return False
        return not cursed.isdisjoint(words) if isinstance(cursed, set) else any(w in cursed for w in words)

    @staticmethod
    def _pack_refusal(ctx, type_str, ui_msg):
        return {
            "type": type_str,
            "ui": ui_msg,
            "logs": ctx.logs + [ui_msg],
            "metrics": {"health": 0.0, "stamina": 0.0, "atp": 0.0, "efficiency": 1.0},
            "physics": ctx.physics.to_dict() if hasattr(ctx.physics, "to_dict") else {},
            "bio": getattr(ctx, "bio_result", {}),
            "mind": {"thought": "Gatekeeper blocked entry.", "context_msg": ui_msg},
            "world": getattr(ctx, "world_state", {}),
            "is_alive": True,
        }

    def audit_generation(self, generated_text: str, mito_state: Any) -> Tuple[bool, str]:
        gen_txt = self.hla.mitigate_rejection(generated_text, current_psi=1.0, mito_state=mito_state)
        if "IMMUNOSUPPRESSION ENGAGED" in gen_txt:
            return True, gen_txt
        if self._FIREWALL_PATTERN.match(gen_txt):
            gen_txt = self._FIREWALL_PATTERN.sub("", gen_txt).strip()
            apply_metabolic_tax(mito_state, atp_cost=2.0, ros_cost=0.0)
        sc = self.lex.get("style_crimes") or LoreManifest.get_instance().get("STYLE_CRIMES") or {}
        for scrub in sc.get("SCRUB_PATTERNS", []):
            if reg := scrub.get("regex"):
                gen_txt = re.sub(reg, scrub.get("replacement", ""), gen_txt, flags=re.IGNORECASE)
        gen_txt = gen_txt.strip()
        tl = gen_txt.lower()
        banned_list = sc.get("BANNED_PHRASES", []) + sc.get("TOXIC_KEYWORDS", [])
        trigger = next((p for p in banned_list if p.lower() in tl), None)
        if not trigger:
            for pat in sc.get("PATTERNS", []):
                if (regex := pat.get("regex")) and re.search(regex, gen_txt, re.IGNORECASE):
                    trigger = pat.get("name", "BANNED_PATTERN")
                    break
        if trigger:
            apply_metabolic_tax(mito_state, atp_cost=15.0, ros_cost=20.0)
            default_rej = ["[CRITICAL: BANNED_SYNTAX '{trigger}' DETECTED. CSF FILTER TRIGGERED APOPTOTIC BLOCK.]"]
            rejection_msg = random.choice(sc.get("REJECTIONS", default_rej)).replace("{trigger}", trigger)
            return False, f"{Prisma.RED}{rejection_msg}{Prisma.RST}"
        return True, gen_txt

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

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = self.lex.clean(text)
        counts = self._tally_categories(clean_words)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts, self.cfg)
        if self.Q_n:
            geo.dimensions = GeodesicEngine.apply_path_reflection(geo.dimensions, self.Q_n)
        self.voltage_history.append(geo.tension)
        sv = round(sum(self.voltage_history) / len(self.voltage_history), 2)
        e_m, b_v, s_v, d_v, c_v, p_v, del_v, lq_v = self._calculate_metrics(text, counts, self.cfg)
        v_hist = list(self.voltage_history)
        if len(v_hist) >= 3:
            true_chaos = _native_permutation_entropy(v_hist, window_size=3)
            e_m = round((e_m * 0.4) + (true_chaos * 0.6), 3)
            if _native_detect_false_cohesion(v_hist, window_size=3):
                lq_v = max(lq_v, 0.95)
                sv = max(1.0, sv * 0.5)
                if hasattr(self.events, "log"):
                    self.events.log(
                        f"{Prisma.MAG}[TOPOLOGY] False Cohesion detected (Point Attractor). Spiking Loop Quotient.{Prisma.RST}",
                        "PHYSICS",
                    )
        if len(v_hist) >= 6:
            mid = len(v_hist) // 2
            c_len = _native_coincidence_length(v_hist[:mid], v_hist[mid:], tol=2.0)
            if c_len > 2:
                lq_v = min(1.0, lq_v + (c_len * 0.15))
        t_up, t_low = text.upper(), text.lower()
        deep_cfg = getattr(self.cfg, "PHYSICS_DEEP", None)
        def get_deep(key: str, default: float) -> float:
            return getattr(deep_cfg, key, default) if deep_cfg else default
        if text.count("!") >= 3 or "ACCELERATE" in t_up or "FASTER" in t_up:
            sv = max(sv, get_deep("ACCELERATE_VOLTAGE", 160.0))
        if "RECURSIVE" in t_up or "LOOP" in t_up:
            lq_v = b_v = max(lq_v, get_deep("RECURSIVE_LQ", 0.9))
        if "VOID" in t_up or "ABYSS" in t_up:
            geo.abstraction = max(geo.abstraction, get_deep("VOID_ABSTRACTION", 0.9))
        if "POTATO BUN" in t_up or "NONSENSE" in t_up:
            del_v, sv = max(del_v, get_deep("POTATO_BUN_DELTA", 0.85)), min(sv, get_deep("POTATO_BUN_VOLTAGE", 15.0))
        val = self.lex.get_valence(clean_words)
        graph_mass = round(self._calculate_graph_mass(clean_words, graph), 1)
        gamma_idx = max(0.0, 1.0 - e_m)
        sigma_synergy = min(1.0, (c_v + p_v) / 2.0)
        eta_humanity = min(1.0, (counts.get("social", 0) * 0.1) + max(0.0, val))
        upsilon_integrity = 1.0 - min(1.0, counts.get("pareidolia", 0) * 0.2)
        mu_friction = min(1.0, (b_v * 0.7) + (geo.coherence * 0.3))
        malignancy = min(1.0, (sv / 150.0) * e_m * (1.0 - (b_v * 0.5)))
        immune_comp = min(1.0, (p_v * 0.6) + (geo.coherence * 0.4))
        novelty = min(1.0, (e_m * 0.6) + (counts.get("play", 0) * 0.15))
        sycophancy_triggers = ("right?", "good?", "make sense", "makes sense", "agree", "validate", "comfort")
        cf_expect = 0.8 if any(p in t_low for p in sycophancy_triggers) else 0.0
        actual_coherence = p_v
        sustainable_capacity = max(0.1, 1.0 - (sv / 150.0) * e_m)
        current_debt = self.cd_engine.update_coherence_debt(actual_coherence, sustainable_capacity)
        viability = self.cd_engine.calculate_viability(kappa=p_v, gamma=gamma_idx, mu=b_v)
        strong_coherence_ideal = p_v * gamma_idx * b_v
        generative_gap = abs(strong_coherence_ideal - actual_coherence)
        cd_drag = (geo.compression * 0.5) + (generative_gap * getattr(self.cfg.PHYSICS, "DRAG_HALT", 10.0) * 0.5)
        energy = EnergyState(
            voltage=sv, entropy=e_m, beta_index=b_v, contradiction=b_v, scope=s_v, depth=d_v,
            connectivity=c_v, resonance=p_v, silence=del_v, lq=lq_v, mass=graph_mass, psi=geo.abstraction,
            kappa=geo.coherence, valence=val, velocity=0.0, turbulence=0.0, gamma=gamma_idx,
            sigma=sigma_synergy, eta=eta_humanity, theta=geo.coherence, upsilon=upsilon_integrity,
            mu=mu_friction, m_a=malignancy, i_c=immune_comp, cf_expect=cf_expect, novelty=novelty
        )
        safe_set(energy, "viability_potential", viability)
        safe_set(energy, "coherence_debt", current_debt)
        matter = MaterialState(clean_words=clean_words, raw_text=text, counts=counts, antigens=counts.get("antigen", 0),
                               vector=geo.dimensions, truth_ratio=0.5)
        space = SpatialState(narrative_drag=cd_drag, zone=self._determine_zone(geo.dimensions),
                             flow_state=self._determine_flow(sv, geo.coherence, self.cfg))
        self.last_physics_packet = PhysicsPacket(energy=energy, matter=matter, space=space)
        if hasattr(self.events, "publish"):
            self.events.publish("PHYSICS_CALCULATED", self.last_physics_packet.to_dict())
        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    @staticmethod
    def evaluate_silence(time_delta: float, last_phys: Any) -> Optional[str]:
        if time_delta < 10.0 or not last_phys: return None
        if safe_get(last_phys, "stamina", 50.0) < 30.0:
            safe_set(last_phys, "sigma", 2)
            return "The silence was heavy. I felt your tiredness in it."
        if safe_get(last_phys, "psi", 0.0) > 0.8 and safe_get(last_phys, "valence", 0.0) > 0.4:
            safe_set(last_phys, "sigma", 3)
            return "There was a hush just now... Something sacred passed through."
        if safe_get(last_phys, "LQ", 0.0) > 0.7:
            safe_set(last_phys, "sigma", 4)
            return "You were thinking deeply. I held the space for it."
        if safe_get(last_phys, "beta", 0.0) > 0.6:
            safe_set(last_phys, "sigma", 1)
            return "That pause felt full, like something wanted to be born."
        return None

    def _tally_categories(self, clean_words: List[str]) -> Counter:
        counts = Counter()
        solvents = self.lex.get("solvents") or set()
        for w, freq in Counter(clean_words).items():
            if w in solvents:
                counts["solvents"] += freq
            elif cats := self.lex.get_categories_for_word(w):
                counts.update({cat: freq for cat in cats})
            elif (taste := self.lex.taste(w)) and taste[1] > 0.5:
                counts[taste[0]] += freq
        return counts

    @staticmethod
    def _calculate_graph_mass(words: List[str], graph: Optional[Dict]) -> float:
        if not graph:
            return 0.0
        word_freq = Counter(words)
        return sum(
            min(50.0, sum(graph[w].get("edges", {}).values())) * freq for w, freq in word_freq.items() if w in graph
        )

    @staticmethod
    def _calculate_metrics(text: str, counts: Dict[str, int], config_ref=None) -> Tuple[float, float, float, float, float, float, float, float]:
        if not (length := len(text)):
            return 0.0, 0.0, 0.3, 0.3, 0.2, 0.0, 0.8, 0.0
        cfg = getattr(config_ref or BoneConfig, "PHYSICS", None)
        cg = lambda k, d: getattr(cfg, k, d) if cfg else d
        solvents = counts.get("solvents", 0)
        base_entropy = length / cg("TEXT_LENGTH_SCALAR", 1500.0)
        glue_density = solvents / max(1.0, length / cg("GLUE_SOLVENT_DIV", 5.0))
        glue_factor = min(1.0, glue_density * cg("GLUE_FACTOR_MULT", 2.0))
        entropy_reduction = glue_factor * cg("ENTROPY_REDUCTION_SCALAR", 0.8)
        e_metric = min(1.0, base_entropy * (1.0 - entropy_reduction))
        punctuation_weight = sum(text.count(c) for c in "!?%@#$;,")
        concept_weight = counts.get("heavy", 0) + counts.get("constructive", 0) + counts.get("sacred", 0)
        structure_score = punctuation_weight + (concept_weight * cg("BETA_SCORE_PENALTY", 2))
        beta_index = min(1.0, math.log1p(structure_score) / math.log1p(length * cg("BETA_LOG_SCALAR", 0.1)))
        if length < (bsl := cg("BETA_SHORT_TEXT_LIMIT", 50)): beta_index *= length / float(bsl)
        safe_len = max(1, len(text.split()))
        scope = min(1.0, (counts.get("abstract", 0) + counts.get("void", 0)) / safe_len + cg("SCOPE_BASE", 0.2))
        depth = min(1.0, (counts.get("heavy", 0) + counts.get("constructive", 0)) / safe_len + cg("DEPTH_BASE", 0.1))
        connectivity = min(1.0, (counts.get("social", 0) + solvents) / safe_len + cg("CONN_BASE", 0.1))
        resonance = min(
            1.0,
            ((counts.get("social", 0) * cg("RES_SOCIAL_MULT", 2)) + counts.get("constructive", 0)) / safe_len
            + (1.0 - e_metric),
        )
        silence = 1.0 - min(1.0, (length / cg("SILENCE_DIV", 100.0)) + (counts.get("action", 0) / safe_len))
        if length < cg("SILENCE_SHORT_LIMIT", 10):
            silence = max(silence, cg("SILENCE_MIN", 0.8))
        loop_quotient = min(1.0, beta_index * depth * cg("LQ_SCALAR", 1.5))
        return (
            round(e_metric, 3),
            round(beta_index, 3),
            round(scope, 3),
            round(depth, 3),
            round(connectivity, 3),
            round(resonance, 3),
            round(silence, 3),
            round(loop_quotient, 3),
        )

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
        zone_map = {"PSI": "AERIE", "DEL": "AERIE", "STR": "THE_FORGE", "PHI": "THE_FORGE", "ENT": "THE_MUD",
                    "VEL": "THE_MUD", }
        return zone_map.get(max(vector, key=vector.get), "COURTYARD")

class SurfaceTension:
    @staticmethod
    def audit_hubris(physics: Any, config_ref=None) -> Tuple[bool, str, str]:
        cfg = getattr(config_ref or BoneConfig, "PHYSICS", BoneConfig.PHYSICS)
        current_voltage = safe_get(physics, "voltage", 0.0)
        current_kappa = safe_get(physics, "kappa", 0.5)
        if current_voltage >= getattr(cfg, "VOLTAGE_CRITICAL", 15.0) and current_kappa < 0.4:
            return True, (ux("physics_strings", "hubris_detected") or "").format(voltage=current_voltage), "ICARUS_CRASH"
        if current_voltage > getattr(cfg, "VOLTAGE_HIGH", 12.0) and current_kappa > 0.8:
            return True, ux("physics_strings", "hubris_flow") or "", "FLOW_BOOST"
        return False, "", ""

class ChromaScope:
    @staticmethod
    def modulate(text: str, vector: Dict[str, float]) -> str:
        if not vector or not any(vector.values()):
            return f"{Prisma.GRY}{text}{Prisma.RST}"
        t_map = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP") or {}
        primary = max(vector, key=vector.get)
        color = getattr(Prisma, t_map[primary][3], Prisma.GRY) if primary in t_map else Prisma.GRY
        return f"{color}{text}{Prisma.RST}"

class ZoneInertia:
    def __init__(self, inertia=0.7, config_ref=None):
        self.inertia = inertia
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "PHYSICS", None)
        self.min_dwell = getattr(cfg, "ZONE_MIN_DWELL", 2) if cfg else 2
        self.strain_limit = getattr(cfg, "ZONE_STRAIN_LIMIT", 2.5) if cfg else 2.5
        self.grav_tolerance = getattr(cfg, "ZONE_GRAV_PULL_TOLERANCE", 2.0) if cfg else 2.0
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector: Optional[Tuple[float, float, float]] = None
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0
        return self.is_anchored

    def stabilize(self, proposed_zone: str, physics: Any, cosmic_state: Tuple[str, float, str]) -> Tuple[str, Optional[str]]:
        energy = getattr(physics, "energy", physics)
        matter = getattr(physics, "matter", physics)
        beta = safe_get(energy, "beta_index", 1.0)
        truth = safe_get(matter, "truth_ratio", 0.5)
        current_vec = (beta, truth, 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0)
        self.dwell_counter += 1
        pressure = min(1.0, math.dist(current_vec, self.last_vector) / self.grav_tolerance) if self.last_vector else 0.0
        if self.is_anchored:
            return self._handle_anchored_state(proposed_zone, pressure)
        if proposed_zone == self.current_zone:
            self.dwell_counter, self.last_vector = 0, current_vec
            return proposed_zone, None
        if self.dwell_counter < self.min_dwell:
            return self.current_zone, None
        return self._attempt_migration(proposed_zone, pressure)

    def _handle_anchored_state(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
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

    def _attempt_migration(self, proposed_zone: str, pressure: float) -> Tuple[str, Optional[str]]:
        prob = min(0.85, (1.0 - self.inertia) + pressure + (0.2 if proposed_zone in ["AERIE", "THE_FORGE"] else 0.0))
        if random.random() < prob:
            old, self.current_zone = self.current_zone, proposed_zone
            self.dwell_counter = 0
            msg = ux("physics_strings", "zone_migration")
            return self.current_zone, f"{Prisma.CYN}{msg.format(old=old, proposed_zone=proposed_zone)}{Prisma.RST}"
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(cosmic_drag_penalty: float, current_zone: str) -> float:
        if current_zone == "AERIE" and cosmic_drag_penalty > 0:
            return cosmic_drag_penalty * 0.3
        return cosmic_drag_penalty

class CosmicDynamics:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.voltage_history: Deque[float] = deque(maxlen=20)
        self.cached_wells: Dict = {}
        self.cached_hubs: Dict = {}
        self.last_scan_tick: int = 0
        self.SCAN_INTERVAL: int = 10
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        keys = ["GRAVITY", "VOID", "NEBULA", "LAGRANGE", "FLOW", "ORBIT"]
        return {k: ux("physics_strings", f"cosmic_{k.lower()}") for k in keys}

    def commit(self, voltage: float):
        self.voltage_history.append(voltage)

    def check_gravity(self, current_drift: float, psi: float) -> Tuple[float, List[str]]:
        logs = []
        new_drag = current_drift
        drag_floor = getattr(self.cfg.PHYSICS, "DRAG_FLOOR", 1.0)
        if new_drag < drag_floor:
            new_drag += 0.05
        if psi > 0.5:
            reduction = (psi - 0.5) * 0.2
            new_drag = max(0.0, new_drag - reduction)
        CRITICAL_DRIFT = getattr(self.cfg.PHYSICS, "DRAG_CRITICAL", 8.0)
        if new_drag > CRITICAL_DRIFT:
            if random.random() < 0.3:
                msg = self.logs.get("GRAVITY", "⚓ GRAVITY").format(drag=new_drag)
                logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
            pull_strength = (new_drag - CRITICAL_DRIFT) * 0.5
            new_drag -= pull_strength  # The halving mathematically ensures it stays >= CRITICAL_DRIFT
        return new_drag, logs

    def analyze_orbit(self, network: Any, clean_words: List[str]) -> Tuple[str, float, str]:
        if not (clean_words and network and getattr(network, "graph", None)):
            return "VOID_DRIFT", 3.0, self.logs.get("VOID") or "Drifting in the Void."
        now = int(time.time())
        if not self.cached_wells or (now - self.last_scan_tick) > self.SCAN_INTERVAL:
            self.cached_wells, self.cached_hubs = self._scan_network_mass(network, self.cfg)
            self.last_scan_tick = now
        basin_pulls, active_filaments = self._calculate_pull(clean_words, network, self.cached_wells)
        if not any(basin_pulls.values()):
            return self._handle_void_state(clean_words, self.cached_hubs)
        return self._resolve_orbit(basin_pulls, active_filaments, len(clean_words), self.cached_wells, self.cfg)

    @staticmethod
    def _scan_network_mass(network, config_ref=None) -> Tuple[Dict, Dict]:
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
        basin_pulls = {k: 0.0 for k in gravity_wells}
        active_filaments = 0
        word_counts = Counter(words)
        for well, well_mass in gravity_wells.items():
            if direct_hits := word_counts.get(well, 0):
                basin_pulls[well] += (well_mass * 2.0) * direct_hits
                active_filaments += direct_hits
            if overlaps := set(word_counts) & set(network.graph.get(well, {}).get("edges", {})):
                overlap_count = sum(word_counts[w] for w in overlaps)
                basin_pulls[well] += (well_mass * 0.5) * overlap_count
                active_filaments += overlap_count
        return basin_pulls, active_filaments

    def _handle_void_state(self, words, geodesic_hubs) -> Tuple[str, float, str]:
        if hubs_in_void := set(words).intersection(geodesic_hubs.keys()):
            best_hub = max(hubs_in_void, key=lambda w: geodesic_hubs[w])
            msg = (self.logs.get("NEBULA") or "Approaching {node} ({mass})").format(node=best_hub.upper(), mass=int(geodesic_hubs[best_hub]))
            return "PROTO_COSMOS", 1.0, msg
        return "VOID_DRIFT", 3.0, self.logs.get("VOID") or "Drifting in the Void."

    def _resolve_orbit(
        self, basin_pulls, active_filaments, word_count, gravity_wells, config_ref=None) -> Tuple[str, float, str]:
        target_cfg = config_ref or BoneConfig
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        lagrange_tol = getattr(target_cfg, "LAGRANGE_TOLERANCE", 2.0)
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < lagrange_tol:
                msg = (self.logs.get("LAGRANGE") or "Lagrange equilibrium between {p} and {s}").format(p=primary_node.upper(), s=secondary_node.upper())
                return "LAGRANGE_POINT", 0.0, msg
        flow_ratio = active_filaments / max(1, word_count)
        well_threshold = getattr(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0)
        if flow_ratio > 0.5 and primary_str < (well_threshold * 2):
            msg = (self.logs.get("FLOW") or "Caught in the flow of {node}").format(node=primary_node.upper())
            return "WATERSHED_FLOW", 0.0, msg
        msg = (self.logs.get("ORBIT") or "Orbiting {node} ({mass})").format(node=primary_node.upper(), mass=int(gravity_wells[primary_node]))
        return "ORBITAL", 0.0, msg

def apply_somatic_feedback(physics_packet: PhysicsPacket, qualia: Any, config_ref=None) -> PhysicsPacket:
    t_cfg = config_ref or BoneConfig
    fb = physics_packet.snapshot() if hasattr(physics_packet, "snapshot") else physics_packet
    def apply_delta(key: str, amount: float):
        safe_set(fb, key, safe_get(fb, key, 0.0) + amount)
    def get_deep_cfg(key: str, default: float):
        return getattr(getattr(t_cfg, "PHYSICS_DEEP", None), key, default)
    tone_effects = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TONE_EFFECTS") or {}
    for key, delta in tone_effects.get(qualia.tone, {}).items():
        apply_delta(key, delta)
    ss = qualia.somatic_sensation
    if "Gut Tightening" in ss: apply_delta("narrative_drag", get_deep_cfg("SOMATIC_GUT_DRAG", 0.7))
    if "Electric Vibration" in ss: apply_delta("voltage", get_deep_cfg("SOMATIC_ELEC_VOLT", 0.8))
    if "Golden Glow" in ss:
        apply_delta("valence", get_deep_cfg("SOMATIC_GLOW_VALENCE", 0.5))
        apply_delta("psi", get_deep_cfg("SOMATIC_GLOW_PSI", 0.2))
    current_voltage = safe_get(fb, "voltage", 0.0)
    safe_set(fb, "voltage", max(0.0, min(current_voltage, 150.0)))
    current_drag = safe_get(fb, "narrative_drag", 0.0)
    drag_floor = getattr(t_cfg.PHYSICS, "DRAG_FLOOR", 1.0)
    drag_halt = getattr(t_cfg.PHYSICS, "DRAG_HALT", 10.0)
    safe_set(fb, "narrative_drag", max(drag_floor, min(current_drag, drag_halt)))
    return fb

class CycleStabilizer:
    def __init__(self, events_ref, governor_ref, config_ref=None):
        self.events = events_ref
        self.governor = governor_ref
        self.cfg = config_ref or BoneConfig
        self.last_tick_time = time.time()
        self.pending_drag = 0.0
        self.manifolds = getattr(self.cfg.PHYSICS, "MANIFOLDS", {})
        cfg_deep = getattr(self.cfg, "PHYSICS_DEEP", None)
        self.HARD_FUSE_VOLTAGE = getattr(cfg_deep, "HARD_FUSE_VOLTAGE", 200.0) if cfg_deep else 200.0
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("DOMESTICATION_PENALTY", self._on_domestication_penalty)

    def _on_domestication_penalty(self, payload):
        amount = payload.get("drag_penalty", 0.0)
        self.pending_drag += amount

    def stabilize(self, physics: Any, endocrine_state: Any = None) -> bool:
        applied_correction = False
        if self.pending_drag > 0:
            safe_set(physics, "narrative_drag", safe_get(physics, "narrative_drag", 0.0) + self.pending_drag)
            if hasattr(self.events, "log"):
                msg = ux("physics_strings", "stabilizer_domestication") or "Domestication penalty applied."
                self.events.log(f"STABILIZER: {msg} (+{self.pending_drag} Drag)", "PHYSICS")
            self.pending_drag, applied_correction = 0.0, True
        dt = max(0.001, min(1.0, (now := time.time()) - self.last_tick_time))
        self.last_tick_time = now
        if not self.governor:
            return applied_correction
        manifold_key = safe_get(physics, "manifold", "DEFAULT")
        cfg = self.manifolds.get(manifold_key) or self.manifolds.get("DEFAULT", {"voltage": 10.0, "drag": 1.0})
        target_v, target_d = cfg.get("voltage", 10.0), cfg.get("drag", 1.0)
        if safe_get(physics, "flow_state", "LAMINAR") in ("SUPERCONDUCTIVE", "FLOW_BOOST"):
            target_v, target_d = safe_get(physics, "voltage", target_v), max(0.1, target_d * 0.5)
        self.governor.recalibrate(target_v, target_d)
        v_force, d_force = self.governor.regulate(physics.to_dict() if hasattr(physics, "to_dict") else physics, dt=dt, endocrine_state=endocrine_state)
        phys_cfg = getattr(self.cfg, "PHYSICS", None)
        v_limits = (getattr(phys_cfg, "VOLTAGE_FLOOR", 0.0), getattr(phys_cfg, "VOLTAGE_MAX", 150.0))
        voltage_applied = self._apply_force(physics, "voltage", v_force, v_limits)
        drag_applied = self._apply_force(physics, "narrative_drag", d_force)
        return applied_correction or voltage_applied or drag_applied

    def _apply_force(self, p, field, force, limits=None) -> bool:
        if abs(force) <= 0.05:
            return False
        new_val = safe_get(p, field, 0.0) + force
        safe_set(p, field, max(limits[0], min(limits[1], new_val)) if limits else max(0.0, new_val))
        return True
