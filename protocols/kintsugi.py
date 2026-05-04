"""protocols/kintsugi.py

The Kintsugi Protocol (named after the Japanese art of repairing broken pottery with gold)
is a trauma-resolution mechanic. When the system's stamina drops dangerously low,
it triggers a 'koan' (a reflective prompt). If the user responds with high-voltage,
creative, or 'whimsical' language, the protocol repairs accumulated systemic trauma
and rewards the engine with either Wisdom or a massive ATP (energy) refund.
"""

import random
from typing import Dict, Any

from constants import Prisma
from presets import BoneConfig
from struts import ux, safe_get
from core import LoreManifest

class KintsugiProtocol:
    """
    Evaluates systemic trauma and offers pathways to heal it.
    The depth of the healing depends on the user's linguistic engagement.
    """

    # The three tiers of trauma resolution:
    PATH_SCAR = "SCAR"  # Bare minimum repair; leaves a heavy mark.
    PATH_INTEGRATION = "KINTSUGI"  # Beautiful repair; grants Wisdom to the Soul.
    PATH_ALCHEMY = "ALCHEMY"  # Perfect transmutation; converts trauma into raw ATP.

    def __init__(self, config_ref=None):
        """
        Initializes the Kintsugi state and loads the reflective koans.
        """
        self.cfg = config_ref or BoneConfig
        self.active_koan = None

        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        # Koans act as the reflective prompt presented to the user when stamina fails.
        self.koans = narrative_data.get("KINTSUGI_KOANS", ["The crack is where the light enters."])

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Kintsugi state to preserve an active koan across reboots."""
        return {"active_koan": self.active_koan}

    def load_state(self, data: Dict[str, Any]):
        """Restores the Kintsugi state from a serialized dictionary."""
        self.active_koan = data.get("active_koan", None)

    def check_integrity(self, stamina):
        """
        Monitors the engine's baseline stamina. If the system is exhausted
        and no koan is currently active, it triggers the Kintsugi state.

        Args:
            stamina: The current ATP/energy level of the system.

        Returns:
            A tuple of (Boolean triggered_state, Optional koan_string)
        """
        cfg = getattr(self.cfg, "KINTSUGI", object())
        s_trig = getattr(cfg, "STAMINA_TRIGGER", 15.0)

        if stamina < s_trig and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan

        return False, None

    def attempt_repair(self, phys, trauma_accum, soul_ref=None, _qualia=None, lexicon_ref=None):
        """
        Evaluates the user's input (physics and vocabulary) to determine
        how effectively the system can heal its accumulated trauma.

        Returns:
            A dictionary containing the success state, UI messages, and applied healing.
        """
        # Healing cannot occur if the protocol hasn't been triggered
        if not self.active_koan:
            return {"success": False, "msg": "No active koan.", "healed": []}

        # Extract physical metrics from the prompt
        energy = safe_get(phys, "energy", {}) or {}
        matter = safe_get(phys, "matter", {}) or {}
        vol = float(safe_get(phys, "voltage", safe_get(energy, "voltage", 0.0)))
        raw_text = str(safe_get(phys, "raw_text", safe_get(matter, "raw_text", "")))

        # Calculate the "Whimsy Score" by cross-referencing the input against the lexicon
        if lexicon_ref:
            clean = lexicon_ref.sanitize(raw_text)
            play_set = lexicon_ref.get("play") or []
            abstract_set = lexicon_ref.get("abstract") or []
            # Count how many abstract or playful words the user employed
            play_count = sum(1 for w in clean if w in play_set or w in abstract_set)
        else:
            clean = raw_text.split()
            play_count = 0

        # Whimsy is the ratio of creative words to total words
        whimsy_score = play_count / max(1, len(clean))

        # Default to the lowest healing tier
        pathway = self.PATH_SCAR
        cfg = getattr(self.cfg, "KINTSUGI", object())

        # Thresholds for higher-tier healing
        al_v = getattr(cfg, "ALCHEMY_VOLTAGE", 15.0)
        al_w = getattr(cfg, "ALCHEMY_WHIMSY", 0.4)
        in_v = getattr(cfg, "INTEGRATION_VOLTAGE", 8.0)
        in_w = getattr(cfg, "INTEGRATION_WHIMSY", 0.2)

        # Determine the repair pathway based on voltage (effort) and whimsy (creativity)
        if vol > al_v and whimsy_score > al_w:
            pathway = self.PATH_ALCHEMY
        elif vol > in_v and whimsy_score > in_w:
            pathway = self.PATH_INTEGRATION

        # Execute the chosen pathway to modify the system's trauma dictionary
        return self._execute_pathway(pathway, trauma_accum, soul_ref)

    def _execute_pathway(self, pathway, trauma_accum, soul_ref):
        """
        Applies the mathematical reduction to the system's trauma and
        dispenses the appropriate rewards (ATP, Wisdom) based on the pathway.
        """
        # If there's no trauma to heal, abort cleanly
        if not trauma_accum:
            return {
                "success": False,
                "msg": ux("protocol_strings", "kintsugi_no_fissures"),
            }

        # Target the subsystem currently suffering the highest trauma
        target = max(trauma_accum, key=trauma_accum.get)
        severity = trauma_accum[target]
        healed_log = []
        cfg = getattr(self.cfg, "KINTSUGI", object())
        atp_gain = 0.0

        # --- TIER 3: ALCHEMY ---
        # The user's profound input completely transmutes the trauma into useable energy.
        if pathway == self.PATH_ALCHEMY:
            r_alc = getattr(cfg, "REDUCTION_ALCHEMY_FACTOR", 0.8) # Heals 80% of the target trauma
            reduction = severity * r_alc
            atp_gain = reduction * getattr(cfg, "ALCHEMY_ATP_FACTOR", 15.0) # Converts reduced trauma to ATP

            msg_raw = ux("protocol_strings", "kintsugi_alchemy")
            msg = f"{Prisma.VIOLET}{msg_raw.format(target=target, boost=atp_gain)}{Prisma.RST}"
            log_alc = ux("protocol_strings", "kintsugi_log_alchemy")
            if log_alc: healed_log.append(log_alc.format(target=target))

        # --- TIER 2: INTEGRATION ---
        # The user successfully navigated the koan. Trauma is reduced, and the Soul gains Wisdom.
        elif pathway == self.PATH_INTEGRATION:
            reduction = getattr(cfg, "REDUCTION_INTEGRATION", 2.0) # Flat trauma reduction

            if soul_ref:
                soul_ref.traits.adjust("WISDOM", 0.1) # Grant permanent epigenetic growth
                log_wis = ux("protocol_strings", "kintsugi_log_wisdom")
                if log_wis: healed_log.append(log_wis)

            msg_raw = ux("protocol_strings", "kintsugi_mercy")
            msg = f"{Prisma.OCHRE}{msg_raw.format(target=target)}{Prisma.RST}"
            log_int = ux("protocol_strings", "kintsugi_log_integration")
            if log_int: healed_log.append(log_int.format(target=target))

        # --- TIER 1: SCAR ---
        # The user bypassed the koan or lacked creativity. Minimal healing, no rewards.
        else:
            reduction = getattr(cfg, "REDUCTION_SCAR", 0.5) # Negligible trauma reduction
            msg_raw = ux("protocol_strings", "kintsugi_scar")
            msg = f"{Prisma.GRY}{msg_raw}{Prisma.RST}"
            log_scar = ux("protocol_strings", "kintsugi_log_scar")
            if log_scar: healed_log.append(log_scar.format(target=target))

        # Apply the mathematical reduction, ensuring trauma never drops below 0
        trauma_accum[target] = max(0.0, severity - reduction)

        # Package the results for the UI and event bus
        result = {"success": True, "msg": msg, "healed": healed_log}
        if atp_gain > 0:
            result["atp_gain"] = atp_gain

        return result