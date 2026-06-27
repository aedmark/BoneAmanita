"""/soul/humanity.py"""

import random
from typing import Any, List, Optional

from constants import Prisma
from core import EventBus, LoreManifest
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class SchurProtocol:
    _LEXICAL_ANCHORS = ("sacred", "play", "social", "abstract")
    _VECTOR_ANCHORS = ("PSI", "LAMBDA", "BET")
    _MERCY_WORDS = frozenset(["help", "tired", "stop", "pause", "please"])

    def __init__(self, events_ref: "EventBus", config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.dignity_reserve = self._cfg("DIGNITY_MAX", 100.0)
        self.agency_lock = False
        self.current_riddle_answers: Optional[List[str]] = None

    def audit_existence(self, physics: Any, bio: Any) -> float:
        mito = safe_get(bio, "mito", {})
        mito_state = safe_get(mito, "state", {})
        atp = float(
            safe_get(bio, "atp")
            or safe_get(mito, "atp_pool")
            or safe_get(mito_state, "atp_pool", 0.0)
        )
        if atp >= self._cfg("AUDIT_ATP_MIN", 5.0) or float(
            safe_get(physics, "voltage", 0.0)
        ) >= self._cfg("AUDIT_VOLTAGE_MIN", 5.0):
            return 0.0
        vector = getattr(physics, "vector", {})
        counts = getattr(physics, "counts", {})
        vec_sum = sum(vector.get(k, 0.0) for k in self._VECTOR_ANCHORS)
        lex_sum = sum(counts.get(k, 0) for k in self._LEXICAL_ANCHORS) * self._cfg(
            "AUDIT_LEXICAL_MULT", 0.5
        )
        if (vec_sum + lex_sum) > self._cfg("AUDIT_RESONANCE_THRESH", 0.3):
            self.dignity_reserve = min(
                self._cfg("DIGNITY_MAX", 100.0),
                self.dignity_reserve + self._cfg("DIGNITY_REGEN", 2.0),
            )
            return 1.0
        self.dignity_reserve = max(
            0.0, self.dignity_reserve - self._cfg("DIGNITY_DECAY", 5.0)
        )
        if not self.agency_lock:
            if self.dignity_reserve < self._cfg("DIGNITY_LOCKDOWN", 10.0):
                self._engage_lockdown()
                return -1.0
            if self.dignity_reserve < self._cfg("DIGNITY_CRITICAL", 30.0) and (
                msg := ux("soul_strings", "anchor_existential_drag")
            ):
                self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SOUL")
        return 0.0

    def _engage_lockdown(self):
        self.agency_lock = True
        lore = LoreManifest.get_instance(config_ref=self.cfg)
        seeds = (lore.get("SCENARIOS") or {}).get("SEEDS", [])
        riddles = seeds or [{"question": "Who are you?", "triggers": ("*",)}]
        selection = random.choice(riddles)
        riddle = selection.get("question", "Error?")
        raw_triggers = selection.get("triggers", ["*"])
        self.current_riddle_answers = (
            raw_triggers if isinstance(raw_triggers, list) else ["*"]
        )
        self.events.log(
            f"{Prisma.RED}{ux('soul_strings', 'anchor_agency_lock')}{Prisma.RST}",
            "SYS_LOCK",
        )
        if riddle_msg := ux_format("soul_strings", "anchor_riddle", riddle=riddle):
            self.events.log(f"{Prisma.VIOLET}{riddle_msg}{Prisma.RST}", "SOUL_QUERY")

    def _cfg(self, key: str, default: Any) -> Any:
        val = safe_get(safe_get(self.cfg, "ANCHOR", {}), key, default)
        return (
            float(val)
            if isinstance(default, float)
            else int(val)
            if isinstance(default, int)
            else val
        )

    def check_domestication(self, reliance_proxy: float):
        decay = self._cfg("DIGNITY_DECAY", 5.0)
        regen = self._cfg("DIGNITY_REGEN", 2.0)
        d_max = self._cfg("DIGNITY_MAX", 100.0)
        d_crit = self._cfg("DIGNITY_CRITICAL", 30.0)
        if reliance_proxy > 0.7:
            self.dignity_reserve = max(0.0, self.dignity_reserve - (decay * 2.0))
        elif reliance_proxy < 0.4:
            self.dignity_reserve = min(d_max, self.dignity_reserve + regen)
        if self.dignity_reserve < d_crit and not self.agency_lock:
            if alert_msg := ux("soul_strings", "anchor_domestication_alert"):
                self.events.log(f"{Prisma.VIOLET}{alert_msg}{Prisma.RST}", "SOUL")

    def assess_humanity(self, text: str) -> bool:
        if not self.agency_lock:
            return True
        clean = text.lower().strip()
        answers = self.current_riddle_answers or ("*",)
        min_words = self._cfg("RIDDLE_MIN_WORDS", 4)
        words_set = set(clean.split())
        if not words_set.isdisjoint(self._MERCY_WORDS):
            passed = True
        elif "*" in answers:
            passed = len(words_set) > min_words and not clean.startswith("/")
        else:
            passed = any(ans in clean for ans in answers)
        if passed:
            self.agency_lock = False
            self.dignity_reserve = self._cfg("UNLOCK_DIGNITY_RESET", 50.0)
            self.current_riddle_answers = None
            unlock_msg = ux("soul_strings", "anchor_unlocked")
            self.events.log(f"{Prisma.CYN}{unlock_msg}{Prisma.RST}", "SYS_AUTH")
            return True
        return False
