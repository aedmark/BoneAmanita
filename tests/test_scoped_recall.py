"""Scoped recall (Gordon, 2026-09-28): ADVENTURE is the story, and the other modes share what the person
told them. Neither zone recalls the other's memories, and a story's "user_name" never overwrites the
person's: the keeper keeps what ADVENTURE establishes under recall.STORY."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from engine.gate.forgetting import plan
from engine.gate.recall import STORY, meaning_scores, memory_hash, zone, zone_of, zoned
from tests.base import BoneTestCase

MODEL = "fake:concepts"


class TheZones(BoneTestCase):
    def test_adventure_is_the_story_and_the_rest_are_real(self):
        self.assertEqual(zone("ADVENTURE"), "story")
        for mode in ("CONVERSATION", "CREATIVE", "TECHNICAL", None):
            self.assertEqual(zone(mode), "real")

    def test_a_memory_goes_by_its_mode_and_without_one_by_its_key(self):
        self.assertEqual(zone_of("door", {"door": "ADVENTURE"}), "story")
        self.assertEqual(zone_of("story.door", {}), "story")
        self.assertEqual(zone_of("sister_name", {}), "real")

    def test_zoned_keeps_only_the_zones_memories(self):
        state = {"world": {}, "self": {"memory": {"sister_name": "Odalys", "story.door": "locked"}}}
        self.assertEqual(zoned(state, {}, "TECHNICAL")["self"]["memory"], {"sister_name": "Odalys"})
        self.assertEqual(zoned(state, {}, "ADVENTURE")["self"]["memory"], {"story.door": "locked"})
        self.assertEqual(len(state["self"]["memory"]), 2)

    def test_a_zoned_ranking_keeps_the_other_zones_vectors(self):
        store = self.engine.store
        memory = {"sister_name": "Odalys", "story.door": "locked"}
        # The person's memory has no vector yet, so ranking it writes one.
        store.save_memory_vectors([("story.door", memory_hash("story.door", "locked"), MODEL, [1.0, 0.0])], keep=set(memory))
        embedder = SimpleNamespace(degraded=False, backend="fake", model="concepts",
                                   embed_batch=lambda texts: [[1.0, 0.0] for _ in texts])
        state = zoned({"world": {}, "self": {"memory": memory}}, {}, "CONVERSATION")
        meaning_scores(state, "my sister", store, embedder, held=set(memory))
        self.assertEqual(set(store.memory_vectors()), set(memory))

    def test_a_story_twin_is_not_a_duplicate_of_the_persons(self):
        memory = {"pet_name": "Brisket", "story.pet_name": "Brisket, a hound", "story.hound": "Brisket the hound"}
        vectors = {k: (memory_hash(k, v), MODEL, [1.0, 0.0]) for k, v in memory.items()}
        gone = plan(memory, {"pet_name": (3, 1.0), "story.pet_name": (2, 1.0)}, vectors, MODEL, cap=500, modes={})
        self.assertEqual(gone, {"story.hound": "near-duplicate of story.pet_name"})


class RecallByZone(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.prompts, self.keeper_prompts, self.keeps = [], [], "NONE"

        def generate(prompt, *a, **k):
            if prompt.startswith("You keep the memory"):
                self.keeper_prompts.append(prompt)
                return self.keeps
            self.prompts.append(prompt)
            return "Noted."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def turn(self, mode, message, keeps="NONE"):
        self.engine.cortex.active_mode, self.keeps = mode, keeps
        self.engine.process_turn(message)
        return self.prompts[-1]

    def remembered(self, prompt):
        block = prompt.split("=== WHAT YOU REMEMBER ===", 1)
        return block[1].split("===", 1)[0] if len(block) > 1 else ""

    def memory(self):
        return self.engine.store.state()[1]["self"]["memory"]

    def test_the_person_is_remembered_in_every_real_mode_and_not_in_the_story(self):
        self.turn("CONVERSATION", "My sister's name is Odalys.", "sister_name = Odalys")
        self.assertIn("sister_name: Odalys", self.remembered(self.turn("TECHNICAL", "Tell me about my sister.")))
        self.assertIn("sister_name: Odalys", self.remembered(self.turn("CREATIVE", "Write about my sister.")))
        self.assertNotIn("Odalys", self.remembered(self.turn("ADVENTURE", "Is my sister here?")))

    def test_the_story_is_remembered_only_in_the_story(self):
        self.turn("ADVENTURE", "The old man says the vault opens at midnight.", "vault = opens at midnight")
        self.assertEqual(self.memory(), {"story.vault": "opens at midnight"})
        self.assertIn("- vault: opens at midnight", self.remembered(self.turn("ADVENTURE", "When does the vault open?")))
        self.assertNotIn("midnight", self.remembered(self.turn("CONVERSATION", "When does the vault open?")))

    def test_a_story_name_never_overwrites_the_persons(self):
        self.turn("CONVERSATION", "I'm Gordon.", "user_name = Gordon")
        self.turn("ADVENTURE", "My name is Aragorn, son of Arathorn.", "user_name = Aragorn")
        self.assertEqual(self.memory(), {"user_name": "Gordon", "story.user_name": "Aragorn"})
        self.assertEqual(self.engine.store.memory_modes(), {"user_name": "CONVERSATION", "story.user_name": "ADVENTURE"})

    def test_the_keeper_sees_only_its_zone_and_reuses_its_names(self):
        self.turn("CONVERSATION", "I'm Gordon.", "user_name = Gordon")
        self.turn("ADVENTURE", "Call me Aragorn.", "user_name = Aragorn")
        self.turn("ADVENTURE", "Actually, call me Strider.", "user_name = Strider")
        self.assertNotIn("Gordon", self.keeper_prompts[-1])
        self.assertIn("\nuser_name = Aragorn", self.keeper_prompts[-1])
        self.assertNotIn(STORY, self.keeper_prompts[-1])
        self.assertEqual(self.memory(), {"user_name": "Gordon", "story.user_name": "Strider"})

    def test_a_turn_in_one_zone_keeps_the_others_vectors(self):
        self.turn("ADVENTURE", "The vault opens at midnight.", "vault = opens at midnight")
        self.turn("CONVERSATION", "My sister is Odalys.", "sister_name = Odalys")
        embedder = SimpleNamespace(degraded=False, backend="fake", model="concepts",
                                   embed_batch=lambda texts: [[1.0, 0.0] for _ in texts])
        self.engine.cortex._recall_embedder = lambda: embedder
        self.turn("ADVENTURE", "When does the vault open?")
        self.turn("CONVERSATION", "How is my sister?")
        self.assertEqual(set(self.engine.store.memory_vectors()), {"story.vault", "sister_name"})
