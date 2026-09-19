import itertools
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from presets import BoneConfig
from struts import safe_get

SPEAK = "SPEAK"
PAIR = "PAIR"
HOLD = "HOLD"


@dataclass(frozen=True)
class Tension:
    voices: Tuple[str, ...] = ()

    @property
    def magnitude(self) -> int:
        return max(0, len(self.voices) - 1)

    @property
    def is_tense(self) -> bool:
        return len(self.voices) > 1

    def __str__(self) -> str:
        if not self.voices:
            return "no voices"
        if not self.is_tense:
            return f"{self.voices[0]} alone"
        return " vs ".join(self.voices)


@dataclass(frozen=True)
class Nomination:
    gate: str
    reason: str
    magnitude: float
    packet: Optional[Dict] = None

@dataclass(frozen=True)
class Verdict:
    outcome: str
    voice: str
    reason: str
    tension: Tension = field(default_factory=Tension)
    adjustments: Dict[str, float] = field(default_factory=dict)
    gate: str = ""

    @property
    def is_silence(self) -> bool:
        return self.outcome == HOLD

    def __str__(self) -> str:
        return f"{self.outcome}[{self.voice}] {self.reason}"


class StageManager:
    def __init__(self, config_ref=None, synergy_map: Optional[Dict] = None):
        self.cfg = config_ref or BoneConfig
        self.synergy_map = synergy_map or {}
        self.consecutive_holds = 0

    def _cfg(self, key: str, default: float) -> float:
        return float(safe_get(safe_get(self.cfg, "STAGE", {}), key, default))

    def read_tension(self, physics: Any, bio_state: Optional[Dict] = None) -> Tension:
        from archetypes.council import TheVillageCouncil

        return Tension(TheVillageCouncil.audit_voices(physics, bio_state or {}))

    def find_pair(self, tension: Tension) -> Optional[Tuple[str, Dict]]:
        for left, right in itertools.combinations(tension.voices, 2):
            for key in (f"{left}|{right}", f"{right}|{left}"):
                if key in self.synergy_map:
                    return key, self.synergy_map[key]
        return None

    def negotiate(
        self,
        tension: Tension,
        physics: Any = None,
        atp: float = 100.0,
        default_voice: str = "NARRATOR",
        nominations: Optional[list[Nomination]] = None,
        somatic_budget: Any = None,
    ) -> Verdict:
        nominations = nominations or []
        if nominations:
            winning_nom = max(nominations, key=lambda n: n.magnitude)
            user_distressed = False
            if somatic_budget and getattr(somatic_budget, "sentence_cap", 100) <= 3:
                user_distressed = True
                
            if not user_distressed or winning_nom.magnitude >= 100.0:
                self.consecutive_holds += 1
                return Verdict(
                    HOLD,
                    "THE STAGE MANAGER",
                    winning_nom.reason,
                    tension,
                    adjustments={"refusal_packet": winning_nom.packet} if winning_nom.packet else {},
                    gate=winning_nom.gate,
                )
            
        if not tension.voices:
            return Verdict(SPEAK, default_voice, "no voice triggered", tension)

        if not tension.is_tense:
            return Verdict(
                SPEAK, tension.voices[0], "one voice, nothing to negotiate", tension
            )

        if paired := self.find_pair(tension):
            key, data = paired
            self.consecutive_holds = 0
            return Verdict(
                PAIR,
                str(data.get("name") or key),
                f"{key.replace('|', ' and ')} fuse; the moment needs both",
                tension,
                dict(data.get("adjustments") or {}),
            )

        max_holds = int(self._cfg("MAX_CONSECUTIVE_HOLDS", 2))
        if self.consecutive_holds >= max_holds:
            self.consecutive_holds = 0
            return Verdict(
                SPEAK,
                tension.voices[0],
                f"held {max_holds} turns already; {tension.voices[0]} takes the floor",
                tension,
            )

        atp_floor = self._cfg("SYNTHESIS_ATP_FLOOR", 25.0)
        if float(atp) < atp_floor:
            self.consecutive_holds += 1
            return Verdict(
                HOLD,
                "THE STAGE MANAGER",
                f"{tension} and only {float(atp):.0f} ATP to reconcile them",
                tension,
                gate="ATP_FLOOR",
            )

        if tension.magnitude >= int(self._cfg("TENSION_HOLD_MAGNITUDE", 3)):
            self.consecutive_holds += 1
            return Verdict(
                HOLD,
                "THE STAGE MANAGER",
                f"{len(tension.voices)} voices at once with no fusion between them",
                tension,
                gate="TENSION_MAGNITUDE",
            )

        self.consecutive_holds = 0
        return Verdict(
            SPEAK,
            tension.voices[0],
            f"{tension}; {tension.voices[0]} carries it",
            tension,
        )
