"""tests/test_pragmatics.py"""

from tests.base import BoneTestCase
from mechanics.pragmatics import ThePragmatist
from core import EventBus

class TestPragmatics(BoneTestCase):
    def test_pragmatist_exhaustion_capping(self):
        """
        PINKER'S CONSTRAINT: The system must physically request compression
        when the user is metabolically exhausted and output is bloated.
        """
        pragmatist = ThePragmatist(events_ref=EventBus())

        # Simulate high drag and low stamina
        phys = {"narrative_drag": 9.5}
        stamina = 10.0
        draft = "Word " * 200 # A massive 200-word draft

        result, needs_rewrite = pragmatist.enforce_maxims(draft, "test prompt", phys, stamina)

        self.assertTrue(
            needs_rewrite,
            "[FAIL] Pragmatist failed to trigger a compression rewrite under critical exhaustion."
        )

    def test_syntactic_antigen_rejection(self):
        """
        THE LEXICAL FIREWALL: The system must physically amputate negative
        comparative framing from generated output.
        """
        bus = EventBus()
        pragmatist = ThePragmatist(events_ref=bus)

        # The LLM generates a toxic structural trope
        draft = "It's not just a bug, it's a feature of the system."

        result, needs_rewrite = pragmatist.enforce_maxims(draft, "test prompt", {}, 100.0)
        logs = "\n".join(e["text"] for e in bus.flush())

        self.assertIn("Amputated", logs, "[FAIL] Pragmatist failed to amputate Syntactic Antigen.")
        self.assertIn("TOXICITY_SPIKE", logs, "[FAIL] Antigen failed to trigger toxicity spike.")
        self.assertIn("FIREWALL", result, "[FAIL] Antigen replacement text not found in output.")