"""protocols/bureau.py"""

import random
import re
from typing import Any, Dict, Optional, Tuple

from constants import Prisma
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class TheBureau:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.stamp_count = 0
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.forms = narrative_data.get("BUREAU_FORMS", ["Form 27B-6", "Form 404"])
        self.responses = narrative_data.get("BUREAU_RESPONSES", ["Processing..."])
        lex_data = LoreManifest.get_instance().get("LEXICON") or {}
        raw_buzz = lex_data.get("bureau_buzzwords") or []
        self.buzzwords = (
            set(raw_buzz)
            if raw_buzz
            else {"synergy", "paradigm", "leverage", "utilize"}
        )
        self.crimes = []
        self.crime_data = LoreManifest.get_instance().get("STYLE_CRIMES") or {}
        if "PATTERNS" in self.crime_data:
            for p in self.crime_data["PATTERNS"]:
                try:
                    self.crimes.append(
                        {
                            "name": p.get("name", "Unknown Violation"),
                            "regex": re.compile(p["regex"], re.IGNORECASE),
                            "msg": p.get("error_msg", "Style Violation Detected."),
                            "tax": float(p.get("tax", 5.0)),
                            "action": p.get("action", None),
                        }
                    )
                except re.error as e:
                    err_msg = ux("protocol_strings", "bureau_compile_fail")
                    print(
                        f"{Prisma.RED}{err_msg.format(name=p.get('name'), e=e)}{Prisma.RST}"
                    )
        stylecrimes = LoreManifest.get_instance().get("style_crimes") or {}
        self.cliches = {str(c).lower() for c in stylecrimes.get("BANNED_CLICHES", [])}

    def to_dict(self) -> Dict[str, Any]:
        return {"stamp_count": self.stamp_count}

    def load_state(self, data: Dict[str, Any]):
        self.stamp_count = data.get("stamp_count", 0)

    def audit(self, physics, bio_state, _context=None, origin="USER") -> Optional[Dict]:
        vol = float(safe_get(physics, "voltage", 0.0))
        clean_words = safe_get(physics, "clean_words", [])
        raw_text = str(safe_get(physics, "raw_text", ""))
        truth = float(safe_get(physics, "truth_ratio", 0.0))
        word_count = len(raw_text.split())
        cfg_bureau = safe_get(self.cfg, "BUREAU", {})
        min_words = int(safe_get(cfg_bureau, "MIN_WORD_COUNT", 4))
        if raw_text.startswith("/") or word_count < min_words:
            return None
        selected_form = None
        evidence = []
        tax = 0.0
        tax_std = float(safe_get(cfg_bureau, "TAX_STANDARD", 5.0))
        tax_hvy = float(safe_get(cfg_bureau, "TAX_HEAVY", 10.0))
        chi = float(safe_get(physics, "chi", safe_get(physics, "entropy", 0.0)))
        chaos_thresh = float(safe_get(cfg_bureau, "CHAOS_TAX_THRESHOLD", 0.6))
        if raw_text and (
            crime := next((c for c in self.crimes if c["regex"].search(raw_text)), None)
        ):
            selected_form, tax = f"VIOLATION: {crime['name']}", tax + crime["tax"]
            evidence.append(crime["msg"])
        elif vol > float(safe_get(cfg_bureau, "HIGH_VOLTAGE_TRIGGER", 18.0)):
            if truth < float(safe_get(cfg_bureau, "LOW_TRUTH_TRIGGER", 0.4)):
                selected_form = ux("protocol_strings", "bureau_form_zoning")
                evidence = [
                    ux("protocol_strings", "bureau_ev_voltage"),
                    ux("protocol_strings", "bureau_ev_fiction"),
                ]
                tax = tax_hvy
            else:
                selected_form = ux("protocol_strings", "bureau_form_202a")
                tax = tax_std
        elif chi > chaos_thresh:
            selected_form = ux("protocol_strings", "bureau_form_666")
            evidence = [
                ux("protocol_strings", "bureau_ev_chaos").format(thresh=chaos_thresh),
                ux("protocol_strings", "bureau_ev_level").format(level=chi),
            ]
            tax = float(safe_get(cfg_bureau, "TAX_CHAOS", 12.0))
        else:
            buzz_hits = [w for w in clean_words if w in self.buzzwords]
            cliche_hits = [c for c in self.cliches if c in raw_text.lower()]
            if buzz_hits:
                selected_form, evidence, tax = (
                    random.choice(self.forms),
                    buzz_hits,
                    tax_std,
                )
            elif cliche_hits:
                selected_form, evidence, tax = (
                    ux("protocol_strings", "bureau_form_101"),
                    cliche_hits,
                    tax_hvy,
                )
        if not selected_form:
            return None
        if float(safe_get(bio_state, "health", 100.0)) < 20.0:
            return {
                "status": "WAIVED",
                "ui": f"{Prisma.CYN}Audit waived due to critical systemic instability.{Prisma.RST}",
                "log": "Audit waived.",
                "atp_gain": 0.0,
            }
        self.stamp_count += 1
        bureau_resp = random.choice(self.responses)
        prefix_str = ux("protocol_strings", "bureau_prefix_normal")
        prefix = f"{Prisma.GRY}{prefix_str}"
        if origin == "SYSTEM":
            int_prefix_str = ux("protocol_strings", "bureau_prefix_internal")
            prefix = f"{Prisma.RED}{int_prefix_str}"
            bureau_resp = ux("protocol_strings", "bureau_sys_violation")
        filed_msg = ux_format(
            "protocol_strings", "bureau_filed", form=selected_form, origin=origin
        )
        ui_msg = f"{prefix}: {bureau_resp}{Prisma.RST}\n   {Prisma.WHT}{filed_msg}{Prisma.RST}"
        if evidence:
            ev_msg = ux_format(
                "protocol_strings", "bureau_evidence", evidence=", ".join(evidence)
            )
            ui_msg += f"\n   {Prisma.RED}{ev_msg}{Prisma.RST}"
        log_msg = ux_format(
            "protocol_strings", "bureau_log", form=selected_form, origin=origin, tax=tax
        )
        return {
            "status": "AUDITED",
            "ui": ui_msg,
            "log": log_msg,
            "atp_gain": -tax,
        }

    @staticmethod
    def _apply_correction(text: str, crime: Dict, match: re.Match) -> str:
        action = crime.get("action")
        if not action:
            return text
        if action == "KEEP_TAIL":
            idx = match.lastindex
            if idx is not None:
                seg = match.group(idx)
                if seg:
                    return seg.strip()
        elif action == "STRIP_PREFIX" and len(match.groups()) >= 3:
            prefix = match.group(1) or ""
            suffix = match.group(3) or ""
            if not prefix.strip() and suffix:
                suffix = suffix[0].upper() + suffix[1:]
            return f"{prefix}{suffix}".strip()
        return text

    def sanitize(self, text: str) -> Tuple[str, Optional[str]]:
        for crime in self.crimes:
            match = crime["regex"].search(text)
            if match and crime.get("action"):
                corrected_text = self._apply_correction(text, crime, match)
                corr_msg = ux("protocol_strings", "bureau_correction")
                log_msg = corr_msg.format(msg=crime["msg"])
                return corrected_text, log_msg
        dummy_physics = {"voltage": 0.0, "raw_text": text, "clean_words": text.split()}
        dummy_bio = {"health": 100.0}
        result = self.audit(dummy_physics, dummy_bio, origin="SYSTEM")
        if result:
            return text, result.get("log")
        return text, None
