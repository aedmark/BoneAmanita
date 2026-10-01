import os
import yaml
from typing import Dict, Any, List

class SelfClaimPrism:
    """
    Evaluates idempotent self-claims from a YAML file against the current biological 
    and physical state of the engine, projecting the active subset of the persona.
    """
    def __init__(self, filepath: str = "lore/self_claims.yaml"):
        self.filepath = filepath
        self.claims: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    self.claims = data.get("claims", [])
        except Exception as e:
            # Fails loudly as per the engine standards, or we can just print?
            # Since this is initialization, failure is a misconfigured yaml.
            raise RuntimeError(f"Failed to load self_claims.yaml: {e}")

    def get_active_claims(self, bio_state: Dict[str, Any], physics_state: Dict[str, Any]) -> List[str]:
        active_texts = []
        
        chem = bio_state.get("chem", {})
        
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
            if "cortisol_min" in conditions and float(chem.get("cortisol", 0.0)) < conditions["cortisol_min"]:
                passes = False
            if "cortisol_max" in conditions and float(chem.get("cortisol", 0.0)) > conditions["cortisol_max"]:
                passes = False
                
            # Evaluate Dopamine
            if "dopamine_min" in conditions and float(chem.get("dopamine", 0.0)) < conditions["dopamine_min"]:
                passes = False
            if "dopamine_max" in conditions and float(chem.get("dopamine", 0.0)) > conditions["dopamine_max"]:
                passes = False
                
            # Evaluate Serotonin
            if "serotonin_min" in conditions and float(chem.get("serotonin", 0.0)) < conditions["serotonin_min"]:
                passes = False
            if "serotonin_max" in conditions and float(chem.get("serotonin", 0.0)) > conditions["serotonin_max"]:
                passes = False
                
            # Evaluate Oxytocin
            if "oxytocin_min" in conditions and float(chem.get("oxytocin", 0.0)) < conditions["oxytocin_min"]:
                passes = False
            if "oxytocin_max" in conditions and float(chem.get("oxytocin", 0.0)) > conditions["oxytocin_max"]:
                passes = False

            # Evaluate Voltage
            if "voltage_min" in conditions and float(physics_state.get("voltage", 0.0)) < conditions["voltage_min"]:
                passes = False
            if "voltage_max" in conditions and float(physics_state.get("voltage", 0.0)) > conditions["voltage_max"]:
                passes = False
                
            # Evaluate Resonance
            if "resonance_min" in conditions and float(physics_state.get("resonance", 0.0)) < conditions["resonance_min"]:
                passes = False
            if "resonance_max" in conditions and float(physics_state.get("resonance", 0.0)) > conditions["resonance_max"]:
                passes = False

            if passes:
                active_texts.append(text)
                
        return active_texts
