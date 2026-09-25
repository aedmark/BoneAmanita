"""/mode switches the experience mode mid-session, as the README promises; /preset keeps tuning-only switches.

/mode used to accept only tuning presets (ZEN_GARDEN, THUNDERDOME, ...) and rejected CONVERSATION
as unknown, so the prompt's mode was fixed at boot. Gordon's call: /mode switches the whole
experience and keeps the conversation; the presets move to /preset.
"""

from unittest.mock import MagicMock

from tests.base import BoneTestCase


class ModeSwitch(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.bio.mito.state.atp_pool = 100.0
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="Start with the tire story.")
        self.log = self.engine.cmd.interface.log = MagicMock()

    def turn_prompt(self, message: str) -> str:
        self.engine.cortex.llm.generate.reset_mock()
        self.engine.process_turn(message)
        return [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list
                if "=== PARTNER INPUT ===" in c.args[0]][-1]

    def test_switching_to_conversation_changes_the_prompt_and_keeps_the_conversation(self):
        self.assertEqual(self.engine.boot_mode, "ADVENTURE")
        self.engine.process_turn("I look around the room.")
        person = self.engine.shared_lattice.u
        person.distress_u = 0.3
        history = list(self.engine.cortex.dialogue_buffer)

        self.engine.cmd.execute("/mode conversation")

        self.assertEqual((self.engine.boot_mode, self.engine.cortex.active_mode), ("CONVERSATION", "CONVERSATION"))
        self.assertIs(self.engine.shared_lattice.u, person)
        self.assertEqual(list(self.engine.cortex.dialogue_buffer)[:len(history)], history)
        self.assertIsNone(self.engine.village.gordon, "CONVERSATION suppresses Gordon")
        self.assertIsNone(self.engine.cortex.svc.inventory)
        prompt = self.turn_prompt("I found one good memory for the toast.")
        self.assertIn("[MODE: CONVERSATION]", prompt)
        self.assertIn("RESPOND, DO NOT NARRATE", prompt)
        self.assertNotIn("INFOCOM", prompt)

    def test_a_round_trip_keeps_gordons_items_and_rewires_his_dependents(self):
        gordon = self.engine.village.gordon
        gordon.inventory.append("BRASS_KEY")
        self.engine.cmd.execute("/mode CONVERSATION")
        self.engine.cmd.execute("/mode ADVENTURE")
        self.assertIs(self.engine.village.gordon, gordon)
        self.assertIn("BRASS_KEY", self.engine.village.gordon.inventory)
        self.assertIs(self.engine.cortex.svc.inventory, gordon)
        town_hall = self.engine.village.town_hall
        self.assertIn(town_hall.on_item_drop, self.engine.events.subscribers.get("ITEM_DROP", ()))
        self.assertIn("INFOCOM", self.turn_prompt("I look around the room."))

    def test_unknown_names_are_refused_and_presets_live_on_preset(self):
        for bad in ("/mode ZEN_GARDEN", "/mode GATE", "/mode FOO"):
            self.engine.cmd.execute(bad)
            self.assertEqual(self.engine.boot_mode, "ADVENTURE", bad)
        self.log.reset_mock()
        self.engine.cmd.execute("/preset ZEN_GARDEN")
        self.assertIn("Loaded preset ZEN_GARDEN", " ".join(str(c.args[0]) for c in self.log.call_args_list))
        self.assertEqual(self.engine.boot_mode, "ADVENTURE", "a preset is tuning only")
        for bad in ("/preset GATE", "/preset CONVERSATION"):
            self.log.reset_mock()
            self.engine.cmd.execute(bad)
            self.assertIn("Unknown preset", " ".join(str(c.args[0]) for c in self.log.call_args_list), bad)

    def test_booting_in_conversation_then_switching_builds_a_working_adventure(self):
        """Gordon never existed; the members built holding him must be rebuilt around the new one."""
        from main import BoneAmanita

        engine = BoneAmanita(config=dict(self.test_config, boot_mode="CONVERSATION"))
        self.addCleanup(self._shutdown_engine, engine)
        self.assertIsNone(engine.village.gordon)
        engine.bio.mito.state.atp_pool = 100.0
        engine.cmd.interface.log = MagicMock()
        engine.cmd.execute("/mode ADVENTURE")
        gordon = engine.village.gordon
        self.assertIsNotNone(gordon)
        self.assertIs(engine.village.tinkerer.gordon, gordon)
        self.assertIs(engine.village.town_hall.gordon, gordon)
        self.assertIs(engine.village.gravedigger.inventory, gordon)
        self.assertIs(engine.cortex.svc.inventory, gordon)
