"""physics/models.py"""

import dataclasses
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DragProfile:
    semantic: float = 0.0
    emotional: float = 0.0
    structural: float = 0.0
    metabolic: float = 0.0
    trauma: float = 0.0

    def total(self) -> float:
        return (
            self.semantic
            + self.emotional
            + self.structural
            + self.metabolic
            + self.trauma
        )


@dataclass
class EnergyState:
    voltage: float = 30.0
    health: float = 100.0
    stamina: float = 100.0
    trauma: float = 0.0
    ros: float = 0.0
    glimmers: int = 0
    exhaustion: float = 0.2
    contradiction: float = 0.4
    scope: float = 0.3
    depth: float = 0.3
    connectivity: float = 0.2

    psi: float = 0.2
    chi: float = 0.2
    valence: float = 0.0

    gamma: float = 0.0
    sigma: float = 0.0
    eta: float = 0.0
    theta: float = 0.0
    upsilon: float = 0.0
    mu: float = 0.0
    m_a: float = 0.0
    i_c: float = 1.0
    h_s: float = 1.0
    omega_r: float = 1.0
    delta_t: float = 12.0
    s_y: float = 0.5
    r_a: float = 0.0

    entropy: float = 0.2
    mass: float = 0.0
    velocity: float = 0.0
    beta_index: float = 0.4
    turbulence: float = 0.0
    kappa: float = 0.0
    epsilon: float = 0.0
    xi: float = 0.0
    lambda_val: float = 0.0
    omega: float = 0.0

    resonance: float = 0.0
    silence: float = 0.0
    lq: float = 0.0
    perfection_streak: int = 0
    cf_expect: float = 0.0
    novelty: float = 0.0


@dataclass
class MaterialState:
    clean_words: List[str] = field(default_factory=list)
    raw_text: str = ""
    counts: Dict[str, int] = field(default_factory=dict)
    antigens: int = 0
    vector: Dict[str, float] = field(default_factory=dict)
    truth_ratio: float = 0.0
    repetition: float = 0.0


@dataclass
class SpatialState:
    zone: str = "COURTYARD"
    manifold: str = "DEFAULT"
    narrative_drag: float = 0.6
    friction: float = 0.6
    atmosphere: str = "NEUTRAL"
    flow_state: str = "LAMINAR"
    godel_scar: Optional[tuple] = None


@dataclass
class PhysicsPacket:
    energy: EnergyState = field(default_factory=EnergyState)
    matter: MaterialState = field(default_factory=MaterialState)
    space: SpatialState = field(default_factory=SpatialState)
    macro_policy: str = "UNKNOWN"

    _CORE_DOMAINS = ("energy", "space", "matter")
    _BASE_FIELDS = frozenset(
        {"energy", "matter", "space", "drag_profile", "macro_policy"}
    )

    _ALIAS_MAP = {
        "E": [("energy", "exhaustion")],
        "beta": [("energy", "beta_index"), ("energy", "contradiction")],
        "S": [("energy", "scope")],
        "D": [("energy", "depth")],
        "C": [("energy", "connectivity")],
        "V": [("energy", "voltage")],
        "F": [("space", "narrative_drag"), ("space", "friction")],
        "narrative_drag": [("space", "narrative_drag"), ("space", "friction")],
        "H": [("energy", "health")],
        "P": [("energy", "stamina")],
        "ROS": [("energy", "ros")],
        "G": [("energy", "glimmers")],
        "PHI_RES": [("energy", "resonance")],
        "DELTA": [("energy", "silence")],
        "LQ": [("energy", "lq")],
        "chi": [("energy", "entropy"), ("energy", "chi")],
        "entropy": [("energy", "entropy"), ("energy", "chi")],
    }

    _DOMAIN_MAP = {
        **{k: "energy" for k in EnergyState.__dataclass_fields__},
        **{k: "matter" for k in MaterialState.__dataclass_fields__},
        **{k: "space" for k in SpatialState.__dataclass_fields__},
    }

    @staticmethod
    def _safe_init(cls: Any, data: Any) -> Any:
        if isinstance(data, cls):
            return data
        if not data:
            return cls()
        valid_keys = getattr(cls, "_valid_keys_cache", None)
        if valid_keys is None:
            valid_keys = {f.name for f in dataclasses.fields(cls)}
            cls._valid_keys_cache = valid_keys
        if isinstance(data, dict):
            return cls(
                **{k: v for k, v in data.items() if k in valid_keys and v is not None}
            )
        return cls(
            **{
                k: getattr(data, k)
                for k in valid_keys
                if getattr(data, k, None) is not None
            }
        )

    def __init__(
        self,
        energy: Optional[Any] = None,
        matter: Optional[Any] = None,
        space: Optional[Any] = None,
        **kwargs,
    ):
        self.energy = self._safe_init(EnergyState, energy)
        self.matter = self._safe_init(MaterialState, matter)
        self.space = self._safe_init(SpatialState, space)
        self.drag_profile = self._safe_init(
            DragProfile, kwargs.pop("drag_profile", None)
        )
        for k, v in kwargs.items():
            setattr(self, k, v)

    def sync_drag(self):
        if hasattr(self, "drag_profile") and self.drag_profile is not None:
            total = self.drag_profile.total()
            setattr(self, "narrative_drag", max(0.6, total))

    def get_creative_drive(self) -> float:
        """a(x) = κγμ. Project Navi, Apache 2.0"""
        return float(self.kappa) * float(self.gamma) * float(self.mu)

    def get_viability_potential(self) -> float:
        """b = κγ - λμ. Project Navi, Apache 2.0"""
        lam = float(self.lambda_val) if self.lambda_val > 0 else 1.0
        return (float(self.kappa) * float(self.gamma)) - (lam * float(self.mu))

    def get_principal_eigenvalue(self, L: float = 3.14159, beta: float = 1.0) -> float:
        """λ₁ = (π/L)² - βb. If λ₁ < 0, nontrivial presence emerges. Project Navi, Apache 2.0"""
        b = self.get_viability_potential()
        return ((math.pi / L) ** 2) - (beta * b)

    def enforce_saturation_limit(self, c: float = 1.5, p: float = 2.0) -> float:
        """Applies the Navi PDE saturation penalty: -c * Φ^p. Caps runway voltage/drag."""
        phi = float(self.get("voltage", 0.0)) / 100.0
        penalty = c * (max(0.0, phi) ** p)
        self.energy.voltage = max(
            0.0, float(self.get("voltage", 0.0)) - (penalty * 15.0)
        )
        return penalty

    @classmethod
    def void_state(cls):
        p = cls()
        p.space.atmosphere = "VOID"
        p.space.zone = "VOID"
        p.space.flow_state = "LAMINAR"
        return p

    def snapshot(self) -> "PhysicsPacket":
        return PhysicsPacket(**self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for k, v in self.__dict__.items():
            if k not in data and not k.startswith("_"):
                data[k] = v
        return data

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )
        if key in self._ALIAS_MAP:
            domain, t_key = self._ALIAS_MAP[key][0]
            return getattr(getattr(self, domain), t_key)
        domain = self._DOMAIN_MAP.get(key)
        if isinstance(domain, str):
            return getattr(getattr(self, domain), key)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{key}'"
        )

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("voltage", "narrative_drag", "psi", "chi", "ros", "V", "F"):
            value = max(0.0, float(value))
        if key in self._BASE_FIELDS:
            if key == "energy":
                value = self._safe_init(EnergyState, value)
            elif key == "matter":
                value = self._safe_init(MaterialState, value)
            elif key == "space":
                value = self._safe_init(SpatialState, value)
            elif key == "drag_profile" and value is not None:
                value = self._safe_init(DragProfile, value)
            super().__setattr__(key, value)
            return
        if key in self._ALIAS_MAP:
            for domain, t_key in self._ALIAS_MAP[key]:
                setattr(getattr(self, domain), t_key, value)
            return
        domain = self._DOMAIN_MAP.get(key)
        if isinstance(domain, str):
            setattr(getattr(self, domain), key, value)
            return
        super().__setattr__(key, value)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"'{key}' not found in PhysicsPacket or its sub-states.")

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return (
            key in self._BASE_FIELDS
            or key in self._ALIAS_MAP
            or key in self._DOMAIN_MAP
        )


@dataclass
class UserInferredState:
    E_u: float = 0.5
    beta_u: float = 0.5
    S_u: float = 0.5
    D_u: float = 0.3
    C_u: float = 0.3
    V_u: float = 50.0
    F_u: float = 0.6
    H_u: float = 100.0
    P_u: float = 100.0
    T_u: float = 0.0
    ROS_u: float = 0.0
    G_u: int = 0
    psi_u: float = 0.3
    chi_u: float = 0.2
    valence_u: float = 0.0

    def __getattr__(self, key: str) -> Any:
        u_key = f"{key}_u"
        if u_key in {f.name for f in dataclasses.fields(self)}:
            return getattr(self, u_key)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{key}'"
        )

    def __setattr__(self, key: str, value: Any) -> None:
        u_key = f"{key}_u"
        field_names = {f.name for f in dataclasses.fields(self)}
        if u_key in field_names and key not in field_names:
            super().__setattr__(u_key, value)
        else:
            super().__setattr__(key, value)

    def snapshot(self) -> "UserInferredState":
        return UserInferredState(**asdict(self))


@dataclass
class SharedDynamics:
    phi: float = 0.5
    delta: float = 0.0
    lq: float = 0.0
    null_coord: float = 0.0
    nabla: float = 0.0
    presence: float = 0.0
    g_pool: int = 0
    p_transfer: float = 0.0
    sigma_silence: int = 0
    lambda_silence: float = 0.2

    def snapshot(self) -> "SharedDynamics":
        return SharedDynamics(**asdict(self))
