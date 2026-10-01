import json
import yaml
import os
from mycelium.lexicon import LinguisticAnalyzer
from mycelium.physics import PhysicsPacket
from mycelium.composer import PromptComposer, ResponseValidator
from mycelium.store import HalcyonStore

class SporeEngine:
    """
    The Technical Mode Fruiting Body.
    Wraps Mycelium biological processing with strict lexical validation,
    low drag for code structures, and zero conversational fluff.
    """
    def __init__(self, db_path="spore.db"):
        print("[Spore] Booting Technical Kernel...")
        self.lore_dir = os.path.join(os.path.dirname(__file__), "lore")
        
        # Load Localized Lore
        with open(os.path.join(self.lore_dir, "style_crimes.json")) as f:
            style_crimes = json.load(f)
        with open(os.path.join(self.lore_dir, "system_prompts.json")) as f:
            system_prompts = json.load(f)
        with open(os.path.join(self.lore_dir, "self_claims.yaml")) as f:
            self_claims = yaml.safe_load(f)
        with open(os.path.join(self.lore_dir, "lexicon.json")) as f:
            lex_data = json.load(f)
            
        print("[Spore] Lore loaded. Booting Mycelium Core...")
        
        # Initialize Mycelium Core dependencies
        self.lexicon = LinguisticAnalyzer(lex_data["VOCAB"], lex_data["LINGUISTICS"])
        self.physics = PhysicsPacket.void_state()
        
        # Technical Mode operates on cold efficiency (low baseline dopamine, low cortisol)
        self.physics.energy.stamina = 100.0
        self.physics.energy.dopamine = 0.1 
        self.physics.energy.cortisol = 0.1
        
        self.composer = PromptComposer(system_prompts, self_claims)
        self.validator = ResponseValidator(style_crimes)
        self.store = HalcyonStore(db_path)
        
        print("[Spore] Kernel Active. Ready for input.\n")

    def process_input(self, text: str, mock_llm_response: str) -> str:
        # 1. Biological Processing via Mycelium
        vector = self.lexicon.vectorize(text)
        self.physics.apply_vector(vector)
        
        if self.physics.energy.stamina <= 0.0:
            return "[System] Kernel Panic: Exhaustion. (ATP = 0)"
            
        # 2. Compose Prompt via Mycelium
        bio_state = {
            "stamina": self.physics.energy.stamina,
            "cortisol": self.physics.energy.cortisol,
            "dopamine": self.physics.energy.dopamine
        }
        
        prompt = self.composer.compose(
            user_query=text, 
            bio_state=bio_state, 
            physics_state=self.physics.to_dict(),
            template_key="TECHNICAL"
        )
        
        # 3. Anti-RLHF Firewall via Mycelium
        max_retries = 3
        attempts = 0
        
        while attempts < max_retries:
            attempts += 1
            try:
                # In a real loop, we generate from the LLM here. We use the mock.
                # If it passes, we break and return.
                self.validator.validate(mock_llm_response)
                return mock_llm_response
            except ValueError as e:
                print(f"[Spore] Attempt {attempts}/{max_retries} Failed: {e}. Retrying...")
                # We just reject and try again (mocking a "better" response on retry)
                if attempts < max_retries:
                    mock_llm_response = "def optimized_function():\n    return True"
                else:
                    return f"[FIREWALL REJECTION]: Maximum retries exceeded. Final error: {e}"
            
        return mock_llm_response
