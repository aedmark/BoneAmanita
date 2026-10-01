import json
import yaml
import os
from mycelium.lexicon import LinguisticAnalyzer
from mycelium.physics import PhysicsPacket
from mycelium.composer import PromptComposer, ResponseValidator
from mycelium.store import HalcyonStore
from mycelium.llm import OllamaInterface

from lichen.inventory import GordonKnot, Item
from lichen.cartographer import Cartographer
from lichen.commands import CommandProcessor

class LichenEngine:
    """
    The Adventure Mode Fruiting Body.
    Wraps Mycelium biological processing with MUD mechanics and live Ollama.
    """
    def __init__(self):
        print("[Lichen] Booting Adventure Mode...")
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
            
        print("[Lichen] Lore loaded. Booting Mycelium Core...")
        
        self.lexicon = LinguisticAnalyzer(lex_data["VOCAB"], lex_data["LINGUISTICS"])
        self.physics = PhysicsPacket.void_state()
        self.physics.energy.stamina = 100.0
        
        self.composer = PromptComposer(system_prompts, self_claims)
        self.validator = ResponseValidator(style_crimes)
        self.store = HalcyonStore("lichen.db")
        self.llm = OllamaInterface(model="mistral-nemo:latest")
        
        print("[Lichen] Booting MUD Mechanics...")
        
        self.inventory = GordonKnot(starters=["Compass", "Flask"])
        self.cartographer = Cartographer()
        self.cmd_processor = CommandProcessor(self.inventory, self.cartographer)
        
        # We start in a void, LLM will generate the first room based on context
        self.context_history = []
        
        print("[Lichen] Stage Manager is Ready.\n")

    def process_input(self, text: str) -> str:
        if text.startswith('/'):
            return self.cmd_processor.execute(text)
            
        # 1. Biological Processing
        vector = self.lexicon.vectorize(text)
        self.physics.apply_vector(vector)
        
        if self.physics.energy.stamina <= 0.0:
            return "[System] You collapse from exhaustion. (ATP = 0)"
            
        # 2. Compose Prompt
        bio_state = {
            "stamina": self.physics.energy.stamina,
            "cortisol": self.physics.energy.cortisol,
            "dopamine": self.physics.energy.dopamine
        }
        
        prompt = self.composer.compose(
            user_query=text, 
            bio_state=bio_state, 
            physics_state=self.physics.to_dict(),
            template_key="ADVENTURE"
        )
        
        # Add map context if a room exists
        if self.cartographer.current_room:
            r = self.cartographer.get_room(self.cartographer.current_room)
            prompt += f"\n[CURRENT ROOM]: {r.name}\n{r.description}\n"
        
        prompt += f"\n[MUD STATE]\n{self.inventory.render_block()}\n"
        
        # Add a hint about the history
        if self.context_history:
            history_str = "\n".join(self.context_history[-3:])
            prompt += f"\n[RECENT HISTORY]\n{history_str}\n"

        prompt += "\nRespond ONLY with the room format."

        # 3. Hit the LLM with Anti-RLHF retries
        max_retries = 3
        attempts = 0
        final_response = "[System] The LLM failed to generate a valid response."
        
        while attempts < max_retries:
            attempts += 1
            raw_response = self.llm.generate(prompt, temperature=0.7)
            if not raw_response:
                return "[System] LLM offline or timed out."
                
            try:
                self.validator.validate(raw_response)
                final_response = raw_response
                break
            except ValueError as e:
                print(f"[Lichen] Firewall Block (Attempt {attempts}/{max_retries}): {e}")
                # Increase cortisol on rejection
                self.physics.energy.cortisol = min(1.0, self.physics.energy.cortisol + 0.1)
                if attempts == max_retries:
                    return f"[FIREWALL REJECTION]: {e}"
                    
        # 4. Spatial Mapping
        parsed_room = self.cartographer.parse_room(final_response)
        if not parsed_room:
            # If it didn't format properly, just return it as a narrative event
            return final_response
            
        self.context_history.append(f"User: {text}")
        self.context_history.append(f"Narrator: Moved to {parsed_room.name}")
        
        return final_response
