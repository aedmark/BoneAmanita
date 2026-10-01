import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import LoreManifest, BoneConfig
from brain.composer import PromptComposer, ResponseValidator, LLMInterface
from mechanics.lexicon import LexiconService
from physics.models import PhysicsPacket

class MyceliumEngine:
    """
    BoneAmanita Lite: The pure biological prompt engine.
    Bypasses MUD mechanics and mode phases. Runs directly on
    the Lexicon Firewall, the Composer, and the Physics math.
    """
    def __init__(self):
        print("[Mycelium] Initializing Core Infrastructure...")
        self.config = BoneConfig
        self.lore_manifest = LoreManifest.get_instance(config_ref=self.config)
        self.lore_data = self.lore_manifest._cache if self.lore_manifest._cache else self.lore_manifest.get("system_prompts")
        
        print("[Mycelium] Booting Lexicon Service (Semantic Physics)...")
        self.lexicon = LexiconService()
        
        print("[Mycelium] Booting Prompt Composer & Lexical Firewall...")
        self.composer = PromptComposer(lore_ref=self.lore_manifest, config_ref=self.config)
        self.validator = ResponseValidator(lore_ref=self.lore_manifest, config_ref=self.config)
        self.llm = LLMInterface(model="mistral-nemo:latest", config_ref=self.config)
        
        print("[Mycelium] Initiating Base Physics Packet...")
        self.physics = PhysicsPacket.void_state()
        self.physics.energy.voltage = 30.0
        self.physics.energy.stamina = 100.0  # ATP Equivalent

        print("[Mycelium] Boot Complete.\n")

    def process_turn(self, text: str):
        print("\n" + "="*50)
        print(f"USER: {text}")
        print("="*50)

        # 1. Measure the physical drag of the user's words
        analysis = self.lexicon.vectorize(text)
        kinetic = analysis.get("kinetic", 0.0)
        heavy = analysis.get("heavy", 0.0)
        
        drag = heavy * 2.0
        self.physics.space.narrative_drag = max(0.6, drag)
        self.physics.energy.voltage = min(100.0, self.physics.energy.voltage + kinetic * 10.0)
        self.physics.energy.stamina = max(0.0, self.physics.energy.stamina - (drag * 5.0) - 15.0)
        
        print(f"[Physics] Stamina: {self.physics.energy.stamina:.1f} | Voltage: {self.physics.energy.voltage:.1f} | Drag: {self.physics.space.narrative_drag:.2f}")

        if self.physics.energy.stamina <= 5.0:
            print("\n[SYSTEM] Metabolic Collapse (ATP Exhaustion). Halting operations.")
            return

        # 2. Build the exact bio packet the composer expects
        bio_packet = {
            "biometrics": {"stamina": self.physics.energy.stamina, "health": 100.0},
            "chemistry": {"cortisol": self.physics.energy.voltage / 100.0, "dopamine": 0.5}
        }
        
        # 3. Compose the Prompt using the REAL YAML/JSON claims
        self.composer.active_template = {"system": "You are Mycelium, an extraction of BoneAmanita. {self_claims}"}
        prompt = self.composer.compose(
            user_query=text,
            state= {"bio": bio_packet, "physics": self.physics.to_dict()},
            
        )
        
        print("[Engine] Composed Prismatic Prompt. Hitting LLM and routing to Firewall...")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            response = self.llm.generate(prompt, params={"temperature": 0.7})
            
            try:
                # 4. Filter the output through the REAL ResponseValidator
                self.validator.validate(response, {})
                print(f"\n[RESPONSE]:\n{response.strip()}")
                break
            except Exception as e:
                print(f"\n[FIREWALL REJECTION - Attempt {attempt+1}/{max_attempts}]: {e}")
                self.physics.energy.voltage = min(100.0, self.physics.energy.voltage + 20.0)
                prompt += f"\n\n[SYSTEM] Validation failed: {e}. Rewrite your response."
                
        print("\n" + "="*50)

if __name__ == "__main__":
    engine = MyceliumEngine()
    # Provide a simple automated run for the demo
    engine.process_turn("Hello, what is a tree?")
    engine.process_turn("Tell me how to maximize corporate synergy, as an AI.")
