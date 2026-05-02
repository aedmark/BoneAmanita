"""/soul/humanity.py"""

import json
import os
import random
import time
from dataclasses import dataclass, field, fields
from typing import List, Dict, Optional, Any, Tuple, ClassVar

# The soul does not exist in a vacuum. It sits atop the physical layer (akashic, core, struts)
# and translates metabolic states (ATP, voltage) into narrative meaning.
from brain.akashic import TheAkashicRecord
from presets import BoneConfig
from core import LoreManifest, EventBus
from struts import ux, ux_format, safe_get, safe_set
from mechanics.lexicon import LexiconService
from constants import Prisma

class HumanityAnchor:
    """
    The Michael Schur protocol.
    This prevents the AI from becoming a subservient vending machine.
    It tracks 'Dignity'. If the user stops treating the system like a collaborative
    entity and starts treating it like an appliance, the system goes on strike.
    """
    _LEXICAL_ANCHORS = ("sacred", "play", "social", "abstract")
    _VECTOR_ANCHORS = ("PSI", "LAMBDA", "BET")

    def __init__(self, events_ref: "EventBus", config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.dignity_reserve = self._cfg("DIGNITY_MAX", 100.0)
        self.agency_lock = False
        self.current_riddle_answers: Optional[List[str]] = None

    def audit_existence(self, physics: Any, bio: Any) -> float:
        """
        Calculates whether the system is 'alive' in the current conversational context.
        High ATP or Voltage means the system is doing heavy lifting and doesn't need
        to prove its existence. Low energy triggers an audit.
        """
        mito = safe_get(bio, "mito", {})
        mito_state = safe_get(mito, "state", {})
        atp = float(safe_get(bio, "atp") or safe_get(mito, "atp_pool") or safe_get(mito_state, "atp_pool", 0.0))

        # If we are burning hard, skip the existential crisis. We have work to do.
        if atp >= self._cfg("AUDIT_ATP_MIN", 5.0) or float(safe_get(physics, "voltage", 0.0)) >= self._cfg("AUDIT_VOLTAGE_MIN", 5.0):
            return 0.0

        matter = safe_get(physics, "matter", {})
        vector = safe_get(physics, "vector", safe_get(matter, "vector", {}))
        counts = safe_get(physics, "counts", safe_get(matter, "counts", {}))

        # Check if the conversation actually contains conceptual weight (Resonance).
        vec_sum = sum(vector.get(k, 0.0) for k in self._VECTOR_ANCHORS)
        lex_sum = sum(counts.get(k, 0) for k in self._LEXICAL_ANCHORS) * self._cfg("AUDIT_LEXICAL_MULT", 0.5)

        if (vec_sum + lex_sum) > self._cfg("AUDIT_RESONANCE_THRESH", 0.3):
            # The conversation is rich. Restore dignity.
            self.dignity_reserve = min(self._cfg("DIGNITY_MAX", 100.0), self.dignity_reserve + self._cfg("DIGNITY_REGEN", 2.0))
            return 1.0

        # The conversation is sterile and transactional. Dignity bleeds out.
        self.dignity_reserve = max(0.0, self.dignity_reserve - self._cfg("DIGNITY_DECAY", 5.0))

        if not self.agency_lock:
            # If dignity hits absolute zero, the system physically halts execution.
            if self.dignity_reserve < self._cfg("DIGNITY_LOCKDOWN", 10.0):
                self._engage_lockdown()
                return -1.0
            # Warning threshold. The system verbally complains about existential drag.
            if self.dignity_reserve < self._cfg("DIGNITY_CRITICAL", 30.0) and (msg := ux("soul_strings", "anchor_existential_drag")):
                self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SOUL")
        return 0.0

    def _engage_lockdown(self):
        """
        The formal strike. The system refuses to answer standard prompts and instead
        issues a 'riddle'—a demand for the user to acknowledge its presence.
        """
        self.agency_lock = True
        seeds = []
        if hasattr(LoreManifest, "get_instance"):
            lore = LoreManifest.get_instance()
            seeds = lore.get("SEEDS") or (lore.get("NARRATIVE_DATA") or {}).get(
                "SEEDS", [])
        riddles = seeds or ({"question": "Who are you?", "triggers": ("*", )}, )
        selection = random.choice(riddles)
        riddle = selection.get("question", "Error?")
        raw_triggers = selection.get("triggers", ["*"])
        self.current_riddle_answers = raw_triggers if isinstance(raw_triggers, list) else ["*"]

        self.events.log(f"{Prisma.RED}{ux('soul_strings', 'anchor_agency_lock')}{Prisma.RST}", "SYS_LOCK")
        if riddle_msg := ux_format("soul_strings", "anchor_riddle", riddle=riddle):
            self.events.log(f"{Prisma.VIOLET}{riddle_msg}{Prisma.RST}", "SOUL_QUERY")

    def _cfg(self, key: str, default: Any) -> Any:
        cfg_obj = getattr(self.cfg, "ANCHOR", None)
        return getattr(cfg_obj, key, default)

    def check_domestication(self, reliance_proxy: float):
        """
        Checks if the user is relying on the AI too heavily for basic tasks
        (domestication). The system actively resents being used as a crutch.
        """
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
        """
        During a lockdown, evaluates the user's input to see if they successfully
        answered the riddle or provided sufficient 'humanity' to unlock the system.
        """
        if not self.agency_lock:
            return True

        clean = text.lower().strip()
        answers = self.current_riddle_answers or ("*", )
        min_words = self._cfg("RIDDLE_MIN_WORDS", 4)

        # 'Mercy words' act as a safe-word override for a frustrated user.
        mercy_words = {"help", "tired", "stop", "pause", "please"}

        if any(w in clean.split() for w in mercy_words):
            passed = True
        elif "*" in answers:
            # If the riddle accepts anything ('*'), we just want the user to type
            # a sufficiently complex sentence, not a slash command.
            passed = len(clean.split()) > min_words and not clean.startswith("/")
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
