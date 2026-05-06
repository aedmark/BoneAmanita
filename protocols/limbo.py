"""protocols/limbo.py
The Limbo Layer handles the narrative consequences of system crashes and terminal failures.
Instead of silently wiping crash logs, the engine 'absorbs' the dead timeline. It extracts
the trauma vectors and heavy mutations that existed right before the crash and converts
them into 'ghosts' (ectoplasm). These ghosts will randomly 'haunt' the user's current
session, ensuring that catastrophic failures leave a permanent, eerie scar on the system's psychology.
"""
import json
import random
from collections import deque
from core import LoreManifest
from typing import Dict, Any
from struts import ux
from presets import BoneConfig
from constants import Prisma


class LimboLayer:
    """
    Manages the persistence of data from failed timelines.
    Maintains a buffer of 'ghosts' (fragments of old memory) and a 'stasis leak'
    variable that governs how frequently these ghosts interrupt normal text output.
    """
    MAX_ECTOPLASM = 50

    def __init__(self, config_ref=None):
        """
        Initializes the Limbo state, setting up the ghost buffer and baseline haunt probabilities.
        """
        self.cfg = config_ref or BoneConfig
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM)
        self.haunt_chance = 0.05
        self.stasis_leak = 0.0
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.stasis_screams = narrative_data.get("CASSANDRA_SCREAMS",
                                                 ["BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT"])

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the ghostly artifacts and leak state for standard saves."""
        return {
            "ghosts": list(self.ghosts),
            "stasis_leak": self.stasis_leak
        }

    def load_state(self, data: Dict[str, Any]):
        """Restores the ghosts and stasis leak from a serialized dictionary."""
        self.ghosts = deque(data.get("ghosts", []), maxlen=self.MAX_ECTOPLASM)
        self.stasis_leak = data.get("stasis_leak", 0.0)

    def absorb_dead_timeline(self, filepath: str) -> None:
        """
        Reads a JSON crash dump (the 'dead timeline') and extracts psychological
        artifacts to haunt the newly rebooted session.
        Args:
            filepath (str): The path to the crash JSON file.
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self._extract_ghosts(data)
        except (IOError, json.JSONDecodeError) as e:
            err_msg = ux("protocol_strings", "limbo_absorb_fail")
            print(f"{Prisma.RED}{err_msg.format(filepath=filepath, e=e)}{Prisma.RST}")

    def _extract_ghosts(self, data: Dict[str, Any]) -> None:
        """
        Sifts through a dead timeline's data to find high-trauma markers and
        heavy mutations, converting them into strings that will haunt the engine.
        """
        if "trauma_vector" in data:
            for k, v in data["trauma_vector"].items():
                if v > 0.3:
                    echo_msg = ux("protocol_strings", "limbo_echo")
                    self.ghosts.append(echo_msg.format(k=k))
        if "mutations" in data and "heavy" in data["mutations"]:
            bones = data["mutations"]["heavy"]
            self.ghosts.extend(random.sample(bones, min(3, len(bones))))

    def trigger_stasis_failure(self, intended_thought):
        """
        Forces a catastrophic stasis leak, usually triggered during extremely
        chaotic prompts or forced overrides. It spikes the leak metric and injects
        a Cassandra scream directly into the engine's active thought process.
        Args:
            intended_thought (str): What the engine was trying to say before failing.
        Returns:
            A heavily formatted UI string displaying the failure and the scream.
        """
        self.stasis_leak = min(100.0, self.stasis_leak + 1.0)
        horror = random.choice(self.STASIS_SCREAMS)
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        err_msg = ux("protocol_strings", "limbo_stasis_err")
        return f"{Prisma.CYN}{err_msg.format(thought=intended_thought, horror=horror)}{Prisma.RST}"

    def haunt(self, text):
        """
        The active interception hook. Runs on outgoing text generation.
        If a stasis leak is active or the RNG hits the haunt chance, it appends
        creepy, disjointed artifacts to the end of the system's normal output.
        Args:
            text (str): The clean, generated text intended for the user.
        Returns:
            The original text, potentially suffixed with ghostly artifacts.
        """
        cfg = getattr(self.cfg, "LIMBO", object())
        l_chance = getattr(cfg, "LEAK_DECAY_CHANCE", 0.2)
        l_amount = getattr(cfg, "LEAK_DECAY_AMOUNT", 0.5)
        if self.stasis_leak > 0:
            if random.random() < l_chance:
                self.stasis_leak = max(0.0, self.stasis_leak - l_amount)
                scream = random.choice(self.STASIS_SCREAMS)
                return f"{text} ...{Prisma.RED}{scream}{Prisma.RST}..."
        if self.ghosts and random.random() < self.haunt_chance:
            spirit = random.choice(self.ghosts)
            return f"{text} ...{Prisma.GRY}{spirit}{Prisma.RST}..."
        return text
