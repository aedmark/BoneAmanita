import re
from typing import Dict, Any, Optional

class ResponseValidator:
    """The Lexical Firewall. Validates LLM output against style crimes."""
    def __init__(self, style_crimes: Dict[str, Any]):
        self.banned_phrases = style_crimes.get("BANNED_PHRASES", [])
        if self.banned_phrases:
            escaped = [re.escape(str(p)) for p in self.banned_phrases]
            joined = "|".join(escaped)
            self.banned_regex = re.compile(rf"(?i)\b({joined})\b")
        else:
            self.banned_regex = None

    def validate(self, response: str) -> None:
        if not response:
            raise ValueError("Empty response received.")
            
        if self.banned_regex:
            match = self.banned_regex.search(response)
            if match:
                raise ValueError(f"Lexical Firewall Violation: Detected banned phrase '{match.group(1)}'")

class PromptComposer:
    """Biological Prompt Builder."""
    def __init__(self, system_prompts: Dict[str, Any], self_claims: Optional[Dict[str, Any]] = None):
        self.system_prompts = system_prompts
        self.self_claims = self_claims or {}

    def _compile_claims(self, bio_state: Dict[str, Any]) -> str:
        """Filters self_claims.yaml based on bio state."""
        claims = self.self_claims.get("claims", [])
        active_claims = []
        cortisol = bio_state.get("cortisol", 0.0)
        dopamine = bio_state.get("dopamine", 0.0)
        
        for claim in claims:
            conditions = claim.get("conditions", {})
            valid = True
            if "cortisol_min" in conditions and cortisol < conditions["cortisol_min"]: valid = False
            if "cortisol_max" in conditions and cortisol > conditions["cortisol_max"]: valid = False
            if "dopamine_min" in conditions and dopamine < conditions["dopamine_min"]: valid = False
            
            if valid:
                active_claims.append(f"- {claim['text']}")
                
        return "\n".join(active_claims)

    def compose(self, user_query: str, bio_state: Dict[str, Any], physics_state: Dict[str, Any], template_key: str = "DEFAULT") -> str:
        template = self.system_prompts.get(template_key, "You are Mycelium.\n{self_claims}")
        claims_text = self._compile_claims(bio_state)
        
        # Inject context
        system_block = template.replace("{self_claims}", claims_text)
        
        prompt = f"{system_block}\n\n"
        prompt += f"[BIOLOGY] Stamina: {bio_state.get('stamina', 100):.1f} | Cortisol: {bio_state.get('cortisol', 0.1):.2f}\n"
        prompt += f"[PHYSICS] Drag: {physics_state.get('narrative_drag', 0.6):.2f}\n\n"
        prompt += f"USER: {user_query}\n"
        
        return prompt
