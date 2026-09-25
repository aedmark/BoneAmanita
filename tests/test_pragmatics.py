"""tests/test_pragmatics.py"""

from engine.core import EventBus
from mechanics.pragmatics import ThePragmatist
from tests.base import BoneTestCase


class TestPragmatics(BoneTestCase):
    def test_the_pragmatist_leaves_negative_comparisons_to_the_gatekeeper(self):
        """It used to replace the whole draft on sight, and a mangled regex made that any "didn't"."""
        pragmatist = ThePragmatist(events_ref=EventBus())
        for draft in ("It's not just a bug, it's a feature of the system.", "He didn't say much, but you knew."):
            result, needs_rewrite = pragmatist.enforce_maxims(draft, "test prompt", {}, 100.0)
            self.assertEqual((result, needs_rewrite), (draft, False))
