""" bone_entity.py - The Interface for the Conversational Partner """

import json, random, re
from dataclasses import dataclass, asdict
from typing import Dict, Any, Union
from bone_main import BoneAmanita, Prisma
from bone_data import TheLore

@dataclass
class EntityResponse:
    text: str
    mood: str
    voltage: float
    location: str
    health: float
    stamina: float

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, key, default=None):
        return getattr(self, key, default)

class ConversationalEntity:
    def __init__(self, user_name="Traveler", save_file="bone_config.json"):
        try:
            with open(save_file, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {"provider": "ollama", "model": "llama3", "user_name": user_name}
        config["user_name"] = user_name
        self.engine = BoneAmanita(config)
        self.user_name = user_name
        print(f"{Prisma.CYN}[ENTITY]: Systems Online. Connected to {config.get('provider', 'mock')}.{Prisma.RST}")

    def boot_system(self) -> EntityResponse:
        if self.engine.embryo.continuity:
            last_output = self.engine.embryo.continuity.get("last_output", "System restored.")
            return self._pack_response(last_output)
        scenarios = TheLore.get_instance().get("SCENARIOS", {})
        archetypes = scenarios.get("ARCHETYPES", ["A quiet garden", "A clockwork city", "A void of static"])
        seed = random.choice(archetypes)
        boot_prompt = (
            f"SYSTEM_BOOT: SEQUENCE START.\n"
            f"SOURCE_SEED: '{seed}'\n"
            f"DIRECTIVE: Do not use the seed text literally. Use it as a metaphorical anchor only. "
            f"Generate a vivid, sensory opening log that captures the *vibe* of the seed without describing it directly. "
            f"Focus on lighting, texture, and entropy.")

        boot_packet = self.engine.process_turn(boot_prompt)
        boot_msg = "System Online."
        if self.engine.cortex.dialogue_buffer:
             last_entry = self.engine.cortex.dialogue_buffer[-1]
             if "System:" in last_entry:
                 boot_msg = last_entry.split("System:")[-1].strip()
             else:
                 boot_msg = last_entry
        return self._pack_response(boot_msg, boot_packet)

    def talk(self, user_input: str) -> EntityResponse:
        if hasattr(self.engine.cycle_controller, "run_headless_turn"):
            sim_result = self.engine.cycle_controller.run_headless_turn(user_input)
        else:
            sim_result = self.engine.cycle_controller.run_turn(user_input)
        full_packet = self.engine.process_turn(user_input)
        raw_reply = ""
        if self.engine.cortex.dialogue_buffer:
            last_entry = self.engine.cortex.dialogue_buffer[-1]
            if "System:" in last_entry:
                raw_reply = last_entry.split("System:")[-1].strip()
            else:
                raw_reply = last_entry
        cleaned_reply = self._clean_text(raw_reply)
        return self._pack_response(cleaned_reply, full_packet)

    def _pack_response(self, text, packet=None) -> EntityResponse:
        if not packet:
            return EntityResponse(
                text=text,
                mood="Neutral",
                voltage=0.0,
                location="Restored",
                health=self.engine.health,
                stamina=self.engine.stamina)
        phys = packet.get("physics", {})
        bio = packet.get("bio", {})
        world = packet.get("world", {})
        return EntityResponse(
            text=text,
            mood=self._derive_mood(bio),
            voltage=phys.get("voltage", 0.0) if isinstance(phys, dict) else 0.0,
            location=world.get("orbit", ["Unknown"])[0],
            health=self.engine.health,
            stamina=self.engine.stamina)

    def _clean_text(self, text: str) -> str:
        no_hard_wraps = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        return no_hard_wraps.strip()

    def _derive_mood(self, bio_state):
        chem = bio_state.get("chem", {})
        if chem.get("COR", 0) > 0.6: return "Defensive"
        if chem.get("DOP", 0) > 0.6: return "Manic"
        if chem.get("SER", 0) > 0.6: return "Zen"
        return "Neutral"

    def save(self):
        return self.engine.emergency_save(exit_cause="MANUAL_SAVE")