"""archetypes/stage.py

The Stage Manager (ROADMAP C4).

v7 specifies it: "The Stage Manager keeps the four in balance. When more than
one is triggered at once, it's labeled as Tension, and the Stage Manager
negotiates it before anyone speaks. Unresolved Tension becomes Silence: a
delayed, considered answer, or no answer until you bring more structure or
energy. The Stage Manager can also pair voices for a moment that needs both."

Three things were missing and are supplied here.

**Tension was not a state.** `TheVillageCouncil.audit` resolved every voice
trigger and then flattened the results into coloured log strings, so the engine
knew exactly which voices had fired and kept only the prose. It also had no
production caller at all. `audit_voices` now returns the structure, and more
than one voice in the room is Tension by definition.

**Silence was a label, not an outcome.** `ArbitrationPhase` could set a lens
called THE STAGE MANAGER and log "the cosmos holds its breath", and then the
engine generated a paragraph anyway. A HOLD verdict now stops the turn before
the model is called.

**Pairing was a lookup that happened to hit.** Fusion fired when a single
precomputed mandate was present. `find_pair` searches every combination of the
voices actually in the room, in both orderings, and reports which pair it chose.

The whole class is deterministic and holds no state except a count of
consecutive holds. Given the same voices and the same physics it returns the
same verdict, which is the property that makes a refusal to speak auditable
rather than a mood.
"""

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
    """Who is trying to speak at once.

    One voice is not tension, it is just a voice. Tension begins at two.
    """

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
    """A vote to halt generation for a specific reason."""
    gate: str
    reason: str
    magnitude: float
    packet: Optional[Dict] = None

@dataclass(frozen=True)
class Verdict:
    """What the Stage Manager decided, and why.

    `reason` is mandatory rather than optional on purpose: a decision to
    withhold an answer that cannot say why is indistinguishable from a fault,
    which is the thing this must never look like.
    """

    outcome: str
    voice: str
    reason: str
    tension: Tension = field(default_factory=Tension)
    adjustments: Dict[str, float] = field(default_factory=dict)

    @property
    def is_silence(self) -> bool:
        return self.outcome == HOLD

    def __str__(self) -> str:
        return f"{self.outcome}[{self.voice}] {self.reason}"


class StageManager:
    """Negotiates which voice, or whether any, gets the floor this turn."""

    def __init__(self, config_ref=None, synergy_map: Optional[Dict] = None):
        self.cfg = config_ref or BoneConfig
        self.synergy_map = synergy_map or {}
        self.consecutive_holds = 0

    def _cfg(self, key: str, default: float) -> float:
        return float(safe_get(safe_get(self.cfg, "STAGE", {}), key, default))

    # -- reading ----------------------------------------------------------

    def read_tension(self, physics: Any, bio_state: Optional[Dict] = None) -> Tension:
        from archetypes.council import TheVillageCouncil

        return Tension(TheVillageCouncil.audit_voices(physics, bio_state or {}))

    def find_pair(self, tension: Tension) -> Optional[Tuple[str, Dict]]:
        """The first fusion pair among the voices actually in the room.

        Every combination, both orderings, rather than one precomputed lookup.
        Two voices that have a named fusion are not in conflict; they are a
        moment that needs both, and pairing them resolves the tension instead
        of suppressing one side of it.
        """
        for left, right in itertools.combinations(tension.voices, 2):
            for key in (f"{left}|{right}", f"{right}|{left}"):
                if key in self.synergy_map:
                    return key, self.synergy_map[key]
        return None

    # -- deciding ---------------------------------------------------------

    def negotiate(
        self,
        tension: Tension,
        physics: Any = None,
        atp: float = 100.0,
        default_voice: str = "NARRATOR",
        nominations: Optional[list[Nomination]] = None,
        somatic_budget: Any = None,
    ) -> Verdict:
        """Decide who speaks, or that nobody does.
        
        Nominations from refusal gates are evaluated here. If the user is distressed,
        we drop all but the most fatal nominations (magnitude >= 100) because abandoning
        a distressed partner is worse than speaking.
        

        The order matters and is deliberate. Pairing is tried before holding,
        because a fusion is a resolution and silence is the admission that
        there is none. The metabolic check comes next: an engine with no energy
        to synthesise conflicting voices should say so rather than blend them
        into mush, which is the failure mode the whole design exists to avoid.
        """
        nominations = nominations or []
        if nominations:
            winning_nom = max(nominations, key=lambda n: n.magnitude)
            user_distressed = False
            if somatic_budget and getattr(somatic_budget, "sentence_cap", 100) <= 3:
                user_distressed = True
                
            if not user_distressed or winning_nom.magnitude >= 100.0:
                self.consecutive_holds += 1
                # We return HOLD, but we also include the packet so ArbitrationPhase can use it.
                return Verdict(
                    HOLD,
                    "THE STAGE MANAGER",
                    winning_nom.reason,
                    tension,
                    adjustments={"refusal_packet": winning_nom.packet} if winning_nom.packet else {}
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

        # An engine that can always decline to speak eventually always will.
        # The cap is what keeps Silence a considered act rather than a habit.
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
            )

        if tension.magnitude >= int(self._cfg("TENSION_HOLD_MAGNITUDE", 3)):
            self.consecutive_holds += 1
            return Verdict(
                HOLD,
                "THE STAGE MANAGER",
                f"{len(tension.voices)} voices at once with no fusion between them",
                tension,
            )

        self.consecutive_holds = 0
        return Verdict(
            SPEAK,
            tension.voices[0],
            f"{tension}; {tension.voices[0]} carries it",
            tension,
        )
