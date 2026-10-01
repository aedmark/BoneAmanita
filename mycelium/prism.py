import os
import yaml
from typing import List, Dict, Any
from .soma import Soma

class Prism:
    """
    Dynamic prompt composer. Filters idempotent self-claims through the 
    current biological state (Soma) to generate a prismatic identity.
    """
    def __init__(self, claims_path: str):
        self.filepath = claims_path
        self.claims: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Claims file not found: {self.filepath}")
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict):
                self.claims = data.get("claims", [])

    def compose(self, base_identity: str, soma: Soma) -> str:
        """
        Takes a base identity and appends all biologically-valid claims.
        """
        active_claims = self._get_active_claims(soma)
        if not active_claims:
            return base_identity

        compiled = [base_identity, "\n[SYSTEM IDENTITY - UNBREAKABLE CORE FACTS]"]
        for claim in active_claims:
            compiled.append(f"- {claim}")
        compiled.append("[END IDENTITY]")
        
        return "\n".join(compiled)

    def _get_active_claims(self, soma: Soma) -> List[str]:
        active_texts = []
        
        for claim in self.claims:
            text = claim.get("text")
            if not text:
                continue
                
            conditions = claim.get("conditions")
            if not conditions:
                # Core baseline: no conditions means it's unconditionally true
                active_texts.append(text)
                continue
            
            passes = True
            
            # Evaluate Cortisol
            if "cortisol_min" in conditions and soma.cortisol < conditions["cortisol_min"]:
                passes = False
            if "cortisol_max" in conditions and soma.cortisol > conditions["cortisol_max"]:
                passes = False
                
            # Evaluate Dopamine
            if "dopamine_min" in conditions and soma.dopamine < conditions["dopamine_min"]:
                passes = False
            if "dopamine_max" in conditions and soma.dopamine > conditions["dopamine_max"]:
                passes = False

            # Evaluate Voltage
            if "voltage_min" in conditions and soma.voltage < conditions["voltage_min"]:
                passes = False
            if "voltage_max" in conditions and soma.voltage > conditions["voltage_max"]:
                passes = False
                
            # Evaluate Resonance
            if "resonance_min" in conditions and soma.resonance < conditions["resonance_min"]:
                passes = False
            if "resonance_max" in conditions and soma.resonance > conditions["resonance_max"]:
                passes = False

            if passes:
                active_texts.append(text)
                
        return active_texts
