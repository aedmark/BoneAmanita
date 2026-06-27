"""protocols/kintsugi.py"""

import random
from typing import Any, Dict

from constants import Prisma
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class KintsugiProtocol:
    PATH_SCAR = "SCAR"
    PATH_INTEGRATION = "KINTSUGI"
    PATH_ALCHEMY = "ALCHEMY"

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.active_koan = None
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.koans = narrative_data.get(
            "KINTSUGI_KOANS", ["The crack is where the light enters."]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"active_koan": self.active_koan}

    def load_state(self, data: Dict[str, Any]):
        self.active_koan = data.get("active_koan", None)

    def check_integrity(self, stamina):
        cfg = safe_get(self.cfg, "KINTSUGI", {})
        s_trig = float(safe_get(cfg, "STAMINA_TRIGGER", 15.0))
        if stamina < s_trig and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan
        return False, None

    def attempt_repair(
        self, phys, trauma_accum, soul_ref=None, _qualia=None, lexicon_ref=None
    ):
        if not self.active_koan:
            return {"success": False, "msg": "No active koan.", "healed": []}
        vol = float(safe_get(phys, "voltage", 0.0))
        raw_text = str(safe_get(phys, "raw_text", ""))
        whimsy_score = 0.0
        if lexicon_ref:
            clean = lexicon_ref.sanitize(raw_text)
            target_sets = set(lexicon_ref.get("play") or []) | set(
                lexicon_ref.get("abstract") or []
            )
            play_count = sum(1 for w in clean if w in target_sets)
            whimsy_score = play_count / max(1, len(clean))
        pathway = self.PATH_SCAR
        cfg = safe_get(self.cfg, "KINTSUGI", {})
        al_v = float(safe_get(cfg, "ALCHEMY_VOLTAGE", 15.0))
        al_w = float(safe_get(cfg, "ALCHEMY_WHIMSY", 0.4))
        in_v = float(safe_get(cfg, "INTEGRATION_VOLTAGE", 8.0))
        in_w = float(safe_get(cfg, "INTEGRATION_WHIMSY", 0.2))
        if vol > al_v and whimsy_score > al_w:
            pathway = self.PATH_ALCHEMY
        elif vol > in_v and whimsy_score > in_w:
            pathway = self.PATH_INTEGRATION
        return self._execute_pathway(pathway, trauma_accum, soul_ref)

    def _execute_pathway(self, pathway, trauma_accum, soul_ref):
        if not trauma_accum:
            return {
                "success": False,
                "msg": ux("protocol_strings", "kintsugi_no_fissures"),
            }
        target = max(trauma_accum, key=lambda k: float(trauma_accum[k]))
        severity = float(trauma_accum[target])
        healed_log = []
        cfg = safe_get(self.cfg, "KINTSUGI", {})
        atp_gain = 0.0
        if pathway == self.PATH_ALCHEMY:
            r_alc = float(safe_get(cfg, "REDUCTION_ALCHEMY_FACTOR", 0.8))
            reduction = severity * r_alc
            atp_gain = reduction * float(safe_get(cfg, "ALCHEMY_ATP_FACTOR", 15.0))
            msg = f"{Prisma.VIOLET}{ux_format('protocol_strings', 'kintsugi_alchemy', target=target, boost=atp_gain)}{Prisma.RST}"
            if log_alc := ux_format(
                "protocol_strings", "kintsugi_log_alchemy", target=target
            ):
                healed_log.append(log_alc)
        elif pathway == self.PATH_INTEGRATION:
            reduction = float(safe_get(cfg, "REDUCTION_INTEGRATION", 2.0))
            if soul_ref:
                soul_ref.traits.adjust("WISDOM", 0.1)
                if log_wis := ux("protocol_strings", "kintsugi_log_wisdom"):
                    healed_log.append(log_wis)
            msg = f"{Prisma.OCHRE}{ux_format('protocol_strings', 'kintsugi_mercy', target=target)}{Prisma.RST}"
            if log_int := ux_format(
                "protocol_strings", "kintsugi_log_integration", target=target
            ):
                healed_log.append(log_int)
        else:
            reduction = float(safe_get(cfg, "REDUCTION_SCAR", 0.5))
            msg = f"{Prisma.GRY}{ux('protocol_strings', 'kintsugi_scar')}{Prisma.RST}"
            if log_scar := ux_format(
                "protocol_strings", "kintsugi_log_scar", target=target
            ):
                healed_log.append(log_scar)
        trauma_accum[target] = max(0.0, severity - reduction)
        result: Dict[str, Any] = {"success": True, "msg": msg, "healed": healed_log}
        if atp_gain > 0:
            result["atp_gain"] = atp_gain
        return result
