"""tests/test_synapse_fallback.py

Two failures on the path where `LLMInterface.generate` gives up on the model.
Both ended in `mock_generation`, whose output is prose, so neither could be seen
from a reply.

Stop sequences and reasoning models. Ollama applies `stop` to a thinking model's
reasoning as well as its reply. The model quotes "Traveler:" while reasoning,
generation ends, content comes back empty, and `generate` used to answer with
mock prose without counting a failure.

Fallback recursion. `mock_generation` asked the dreamer to hallucinate, the
dreamer asked `generate`, and in mock mode or with the circuit open `generate`
went straight back to `mock_generation`: hundreds of nested calls per turn,
ending in a RecursionError the dreamer swallowed.
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from brain.composer import LLMInterface
from tests.base import BoneTestCase


class StopSequencesAndReasoningModels(unittest.TestCase):
    def setUp(self):
        self.events = MagicMock()
        self.llm = LLMInterface(events_ref=self.events, provider="ollama", model="thinker")
        self.sent = []

    def transmit_returning(self, *replies):
        queue = list(replies)

        def fake_transmit(payload, timeout=None):
            self.sent.append(dict(payload))
            return queue.pop(0)

        return patch.object(self.llm, "_transmit", side_effect=fake_transmit)

    def test_an_empty_reply_is_retried_without_stops(self):
        with self.transmit_returning("", "The tide is out."):
            reply = self.llm.generate("prompt", {})
        self.assertEqual(reply, "The tide is out.")
        self.assertIn("stop", self.sent[0])
        self.assertNotIn("stop", self.sent[1])

    def test_once_learned_stops_are_not_sent_again(self):
        with self.transmit_returning("", "first", "second"):
            self.llm.generate("prompt", {})
            self.llm.generate("prompt", {})
        self.assertTrue(self.llm.stops_cut_reasoning)
        self.assertNotIn("stop", self.sent[2])
        self.assertEqual(len(self.sent), 3, "a learned model should not need a retry")

    def test_stops_still_apply_to_the_reply_text(self):
        """Dropping server stops must not let a model write the partner's lines."""
        self.llm.stops_cut_reasoning = True
        with self.transmit_returning("It is late.\nTraveler: and then I said"):
            reply = self.llm.generate("prompt", {})
        self.assertEqual(reply, "It is late.")

    def test_a_model_that_does_not_reason_keeps_its_stops(self):
        with self.transmit_returning("fine", "fine"):
            self.llm.generate("prompt", {})
            self.llm.generate("prompt", {})
        self.assertFalse(self.llm.stops_cut_reasoning)
        self.assertTrue(all("stop" in p for p in self.sent))

    def test_an_empty_reply_is_a_counted_named_failure(self):
        """Not prose, not silence: a warning and a failure the circuit can see."""
        with self.transmit_returning("", ""), patch.object(
            self.llm, "mock_generation", return_value="MOCK"
        ) as mock:
            self.llm.generate("prompt", {})
        self.assertEqual(self.llm.failure_count, 1)
        mock.assert_called_once()
        warned = [c for c in self.events.log.call_args_list if "no content" in str(c.args[0])]
        self.assertTrue(warned, "an empty reply was not reported")
        self.assertEqual(warned[0].args[2], "WARN")

    def test_repeated_empty_replies_open_the_circuit(self):
        replies = [""] * (2 * self.llm.failure_threshold)
        with self.transmit_returning(*replies), patch.object(
            self.llm, "mock_generation", return_value="MOCK"
        ):
            for _ in range(self.llm.failure_threshold):
                self.llm.generate("prompt", {})
        self.assertEqual(self.llm.circuit_state, "OPEN")


class FallbackDoesNotReenterTheSynapse(BoneTestCase):
    """Travels the real engine: its own LLMInterface and its own dreamer."""

    def count_generate_calls(self, llm) -> int:
        calls = []
        real = llm.generate

        def counting(prompt, params):
            calls.append(prompt)
            return real(prompt, params)

        with patch.object(llm, "generate", side_effect=counting):
            reply = llm.generate("a prompt", {})
        self.assertTrue(reply, "the fallback produced nothing at all")
        return len(calls)

    def test_mock_provider_calls_generate_once(self):
        llm = self.engine.cortex.llm
        self.assertIsNotNone(llm.dreamer, "the engine's synapse has no dreamer to test")
        llm.provider = "mock"
        self.assertEqual(self.count_generate_calls(llm), 1)

    def test_an_open_circuit_calls_generate_once(self):
        llm = self.engine.cortex.llm
        llm.circuit_state = "OPEN"
        llm.last_failure_time = time.time()
        self.assertEqual(self.count_generate_calls(llm), 1)

    def test_the_dreamer_still_uses_the_synapse_when_asked_directly(self):
        """The guard belongs to the fallback, not to every hallucination."""
        dreamer = self.engine.cortex.llm.dreamer
        with patch.object(dreamer.llm, "generate", return_value="a door made of rain") as gen:
            dreamer.hallucinate({"chi": 0.9}, trauma_level=0.0)
        gen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
