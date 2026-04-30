"""protocols/kintsugi.py"""

import random
from typing import Dict, Any
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma
from core import LoreManifest

NARRATIVE_DATA = LoreManifest.get_instance().get("narrative_data") or {}

class KintsugiProtocol:
    PATH_SCAR = "SCAR"
    PATH_INTEGRATION = "KINTSUGI"
    PATH_ALCHEMY = "ALCHEMY"

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.active_koan = None
        self.koans = NARRATIVE_DATA.get("KINTSUGI_KOANS", ["The crack is where the light enters."])

    def to_dict(self) -> Dict[str, Any]:
        return {"active_koan": self.active_koan}

    def load_state(self, data: Dict[str, Any]):
        self.active_koan = data.get("active_koan", None)

    def check_integrity(self, stamina):
        cfg = getattr(self.cfg, "KINTSUGI", object())
        s_trig = getattr(cfg, "STAMINA_TRIGGER", 15.0)
        if stamina < s_trig and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys, trauma_accum, soul_ref=None, _qualia=None, lexicon_ref=None):
        if not self.active_koan:
            return {"success": False, "msg": "No active koan.", "healed": []}
        energy = safe_get(phys, "energy", {}) or {}
        matter = safe_get(phys, "matter", {}) or {}
        vol = float(safe_get(phys, "voltage", safe_get(energy, "voltage", 0.0)))
        raw_text = str(safe_get(phys, "raw_text", safe_get(matter, "raw_text", "")))
        if lexicon_ref:
            clean = lexicon_ref.sanitize(raw_text)
            play_set = lexicon_ref.get("play") or []
            abstract_set = lexicon_ref.get("abstract") or []
            play_count = sum(1 for w in clean if w in play_set or w in abstract_set)
        else:
            clean = raw_text.split()
            play_count = 0
        whimsy_score = play_count / max(1, len(clean))
        pathway = self.PATH_SCAR
        cfg = getattr(self.cfg, "KINTSUGI", object())
        al_v = getattr(cfg, "ALCHEMY_VOLTAGE", 15.0)
        al_w = getattr(cfg, "ALCHEMY_WHIMSY", 0.4)
        in_v = getattr(cfg, "INTEGRATION_VOLTAGE", 8.0)
        in_w = getattr(cfg, "INTEGRATION_WHIMSY", 0.2)
        if vol > al_v and whimsy_score > al_w:
            pathway = self.PATH_ALCHEMY
        elif vol > in_v and whimsy_score > in_w:
            pathway = self.PATH_INTEGRATION
        return self._execute_pathway(pathway, trauma_accum, soul_ref)

    def _execute_pathway(self, pathway, trauma_accum, soul_ref):
        if not trauma_accum:
            return {"success": False, "msg": ux("protocol_strings", "kintsugi_no_fissures"),}
        target = max(trauma_accum, key=trauma_accum.get)
        severity = trauma_accum[target]
        healed_log = []
        cfg = getattr(self.cfg, "KINTSUGI", object())
        atp_gain = 0.0
        if pathway == self.PATH_ALCHEMY:
            r_alc = getattr(cfg, "REDUCTION_ALCHEMY_FACTOR", 0.8)
            reduction = severity * r_alc
            atp_gain = reduction * getattr(cfg, "ALCHEMY_ATP_FACTOR", 15.0)
            msg_raw = ux("protocol_strings", "kintsugi_alchemy")
            msg = f"{Prisma.VIOLET}{msg_raw.format(target=target, boost=atp_gain)}{Prisma.RST}"
            log_alc = ux("protocol_strings", "kintsugi_log_alchemy")
            if log_alc: healed_log.append(log_alc.format(target=target))
        elif pathway == self.PATH_INTEGRATION:
            reduction = getattr(cfg, "REDUCTION_INTEGRATION", 2.0)
            if soul_ref:
                soul_ref.traits.adjust("WISDOM", 0.1)
                log_wis = ux("protocol_strings", "kintsugi_log_wisdom")
                if log_wis: healed_log.append(log_wis)
            msg_raw = ux("protocol_strings", "kintsugi_mercy")
            msg = f"{Prisma.OCHRE}{msg_raw.format(target=target)}{Prisma.RST}"
            log_int = ux("protocol_strings", "kintsugi_log_integration")
            if log_int: healed_log.append(log_int.format(target=target))
        else:
            reduction = getattr(cfg, "REDUCTION_SCAR", 0.5)
            msg_raw = ux("protocol_strings", "kintsugi_scar")
            msg = f"{Prisma.GRY}{msg_raw}{Prisma.RST}"
            log_scar = ux("protocol_strings", "kintsugi_log_scar")
            if log_scar: healed_log.append(log_scar.format(target=target))
        trauma_accum[target] = max(0.0, severity - reduction)
        result = {"success": True, "msg": msg, "healed": healed_log}
        if atp_gain > 0: result["atp_gain"] = atp_gain
        return result