"""protocols/bureau.py
The Bureau acts as the system's administrative and stylistic auditor.
It monitors the generative output and user inputs for structural anomalies,
stylistic 'crimes' (like cliches or corporate buzzwords), and excessive chaos.
When a violation is detected, it 'files a form' and levies an ATP (stamina) tax
against the system to physically discourage lazy or overly chaotic processing.
"""
import random
import re
from typing import Dict, Tuple, Optional, Any
from core import LoreManifest
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma


class TheBureau:
    """
    A bureaucratic governor that enforces syntactic and systemic discipline.
    It penalizes high-chaos, low-truth states, and actively strips out banned
    lexical patterns using regex-based 'style crimes'.
    """

    def __init__(self, config_ref=None):
        """
        Initializes the Bureau, loading its rigid ruleset from the LoreManifest.
        """
        self.cfg = config_ref or BoneConfig
        self.stamp_count = 0
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.forms = narrative_data.get("BUREAU_FORMS", ["Form 27B-6", "Form 404"])
        self.responses = narrative_data.get("BUREAU_RESPONSES", ["Processing..."])
        lex_data = LoreManifest.get_instance().get("LEXICON") or {}
        raw_buzz = lex_data.get("bureau_buzzwords") or []
        self.buzzwords = (set(raw_buzz) if raw_buzz else {"synergy", "paradigm", "leverage", "utilize"})
        self.crimes = []
        self.crime_data = LoreManifest.get_instance().get("STYLE_CRIMES") or {}
        if "PATTERNS" in self.crime_data:
            for p in self.crime_data["PATTERNS"]:
                try:
                    self.crimes.append({
                        "name": p.get("name", "Unknown Violation"),
                        "regex": re.compile(p["regex"], re.IGNORECASE),
                        "msg": p.get("error_msg", "Style Violation Detected."),
                        "tax": float(p.get("tax", 5.0)),
                        "action": p.get("action", None),
                    })
                except re.error as e:
                    err_msg = ux("protocol_strings", "bureau_compile_fail")
                    print(f"{Prisma.RED}{err_msg.format(name=p.get('name'), e=e)}{Prisma.RST}")
        stylecrimes = LoreManifest.get_instance().get("style_crimes") or {}
        self.cliches = {str(c).lower() for c in stylecrimes.get("BANNED_CLICHES", [])}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Bureau's state for persistence across sessions."""
        return {"stamp_count": self.stamp_count}

    def load_state(self, data: Dict[str, Any]):
        """Restores the Bureau's state from a serialized dictionary."""
        self.stamp_count = data.get("stamp_count", 0)

    def audit(self, physics, bio_state, _context=None, origin="USER") -> Optional[Dict]:
        """
        Evaluates the current physical dimensions of a prompt or generation to determine
        if an administrative penalty (tax) is required.
        Args:
            physics: The dimensional state of the text (voltage, truth_ratio, chi, word count).
            bio_state: The biological health/stamina of the system.
            origin: "USER" or "SYSTEM", determining who is committing the infraction.
        Returns:
            A dictionary containing UI alerts, logs, and ATP tax values if an audit was triggered,
            or None if the text passes inspection.
        """
        vol = float(safe_get(physics, "voltage", 0.0))
        clean_words = safe_get(physics, "clean_words", [])
        raw_text = str(safe_get(physics, "raw_text", ""))
        truth = float(safe_get(physics, "truth_ratio", 0.0))
        word_count = len(raw_text.split())
        if raw_text.startswith("/") or word_count < self.cfg.BUREAU.MIN_WORD_COUNT:
            return None
        selected_form = None
        evidence = []
        tax = 0.0
        cfg_bureau = getattr(self.cfg, "BUREAU", object())
        tax_std = getattr(cfg_bureau, "TAX_STANDARD", 5.0)
        tax_hvy = getattr(cfg_bureau, "TAX_HEAVY", 10.0)
        chi = float(safe_get(physics, "chi", safe_get(physics, "entropy", 0.0)))
        chaos_thresh = getattr(cfg_bureau, "CHAOS_TAX_THRESHOLD", 0.6)
        if raw_text and (crime := next((c for c in self.crimes if c["regex"].search(raw_text)), None)):
            selected_form, tax = f"VIOLATION: {crime['name']}", tax + crime["tax"]
            evidence.append(crime["msg"])
        elif vol > getattr(cfg_bureau, "HIGH_VOLTAGE_TRIGGER", 18.0):
            if truth < getattr(cfg_bureau, "LOW_TRUTH_TRIGGER", 0.4):
                selected_form = ux("protocol_strings", "bureau_form_zoning")
                evidence = [ux("protocol_strings", "bureau_ev_voltage"), ux("protocol_strings", "bureau_ev_fiction")]
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
            tax = getattr(cfg_bureau, "TAX_CHAOS", 12.0)
        else:
            buzz_hits = [w for w in clean_words if w in self.buzzwords]
            cliche_hits = [c for c in self.cliches if c in raw_text.lower()]
            if buzz_hits:
                selected_form, evidence, tax = random.choice(self.forms), buzz_hits, tax_std
            elif cliche_hits:
                selected_form, evidence, tax = ux("protocol_strings", "bureau_form_101"), cliche_hits, tax_hvy
        if not selected_form:
            return None
        if bio_state.get("health", 100.0) < 20.0:
            return {
                "status": "WAIVED",
                "ui": f"{Prisma.CYN}[BUREAU]: Audit waived due to critical systemic instability.{Prisma.RST}",
                "log": "Audit waived (Mercy).",
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
        filed_msg = ux("protocol_strings", "bureau_filed")
        ui_msg = f"{prefix}: {bureau_resp}{Prisma.RST}\n   {Prisma.WHT}{filed_msg.format(form=selected_form, origin=origin)}{Prisma.RST}"
        if evidence:
            ev_msg = ux("protocol_strings", "bureau_evidence")
            ui_msg += f"\n   {Prisma.RED}{ev_msg.format(evidence=', '.join(evidence))}{Prisma.RST}"
        log_msg = ux("protocol_strings", "bureau_log")
        return {
            "status": "AUDITED",
            "ui": ui_msg,
            "log": log_msg.format(form=selected_form, origin=origin, tax=tax),
            "atp_gain": -tax,
        }

    @staticmethod
    def _apply_correction(text: str, crime: Dict, match: re.Match) -> str:
        """
        Physically alters the input string based on predefined regex group actions.
        This is how the system enforces structural syntax limits.
        """
        action = crime.get("action")
        if not action:
            return text
        if action == "KEEP_TAIL":
            idx = match.lastindex
            if idx is not None:
                seg = match.group(idx)
                if isinstance(seg, str):
                    return seg.strip()
        elif action == "STRIP_PREFIX" and len(match.groups()) >= 3:
            prefix = match.group(1) if isinstance(match.group(1), str) else ""
            suffix = match.group(3) if isinstance(match.group(3), str) else ""
            if not prefix.strip() and suffix:
                suffix = suffix[0].upper() + suffix[1:]
            return f"{prefix}{suffix}".strip()
        return text

    def sanitize(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Scans a string against all style crimes and applies physical corrections if defined.
        If no correction logic is defined but the string still triggers an audit, it processes
        the audit as a System violation.
        Returns:
            A tuple containing the cleaned text, and the log message (if any action was taken).
        """
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
