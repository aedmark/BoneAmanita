import json
import yaml
import os
from mycelium.lexicon import LinguisticAnalyzer
from mycelium.physics import PhysicsPacket
from mycelium.composer import PromptComposer, ResponseValidator
from mycelium.store import HalcyonStore

from lichen.inventory import GordonKnot, Item
from lichen.cartographer import Cartographer
from lichen.commands import CommandProcessor

class LichenEngine:
    """
    The Adventure Mode Fruiting Body.
    Wraps Mycelium biological processing with MUD mechanics.
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
        
        # Initialize Mycelium Core dependencies
        self.lexicon = LinguisticAnalyzer(lex_data["VOCAB"], lex_data["LINGUISTICS"])
        self.physics = PhysicsPacket.void_state()
        self.physics.energy.stamina = 100.0
        
        self.composer = PromptComposer(system_prompts, self_claims)
        self.validator = ResponseValidator(style_crimes)
        self.store = HalcyonStore("lichen.db")
        
        print("[Lichen] Booting MUD Mechanics...")
        
        # Initialize Lichen Mechanics
        self.inventory = GordonKnot(starters=["Compass", "Flask"])
        self.cartographer = Cartographer()
        self.cmd_processor = CommandProcessor(self.inventory, self.cartographer)
        
        print("[Lichen] Stage Manager is Ready.\n")

    def process_input(self, text: str) -> str:
        # Check if it's a slash command
        if text.startswith('/'):
            return self.cmd_processor.execute(text)
            
        # 1. Biological Processing via Mycelium
        vector = self.lexicon.vectorize(text)
        self.physics.apply_vector(vector)
        
        if self.physics.energy.stamina <= 0.0:
            return "[System] You collapse from exhaustion. (ATP = 0)"
            
        # 2. Compose Prompt via Mycelium
        bio_state = {
            "stamina": self.physics.energy.stamina,
            "cortisol": self.physics.energy.cortisol,
            "dopamine": self.physics.energy.dopamine
        }
        
        # Append inventory rendering to the prompt
        prompt = self.composer.compose(
            user_query=text, 
            bio_state=bio_state, 
            physics_state=self.physics.to_dict(),
            template_key="ADVENTURE"
        )
        prompt += f"\n\n[MUD STATE]\n{self.inventory.render_block()}\n"
        
        # In a real GUI/backend, we would now hit the LLM. 
        # For this engine wrapper demo, we simulate the LLM's spatial response
        # so the Cartographer can map it.
        mock_llm_response = f"**[The Dark Woods]**\nYou step into the woods. The air is heavy.\n**Points of Interest:**\n- A shiny rock\n**Exits:**\n- North to [Crystal Cave]"
        
        # 3. Anti-RLHF Firewall via Mycelium
        try:
            self.validator.validate(mock_llm_response)
        except ValueError as e:
            return f"[FIREWALL REJECTION]: {e}"
            
        # 4. Spatial Mapping via Lichen
        self.cartographer.parse_room(mock_llm_response)
        
        return mock_llm_response
