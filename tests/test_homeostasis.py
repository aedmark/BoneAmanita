"""Homeostasis (Gordon, 2026-09-29: the original intent). In every recorded run the chemistry pinned within
five turns (dopamine and oxytocin at 1.0, cortisol at 0), so every state read the same. A rise now uses only
the headroom left, and each hormone moves BIO.DECAY_RATE of the way back to rest every turn."""

from body.endocrine import REST, EndocrineSystem
from tests.base import BoneTestCase

WARM = dict(feedback={"VALENCE": 0.7, "INTEGRITY": 0.9}, social_context=True)
NEUTRAL = dict(feedback={}, social_context=False)
STRESS = dict(feedback={"STATIC": 0.9, "CHI": 0.8, "VALENCE": -0.7})


def turns(endo, kind, n):
    for _ in range(n):
        endo.metabolize(health=100.0, stamina=100.0, **kind)
    return endo


class Homeostasis(BoneTestCase):
    def test_sustained_warmth_levels_off_below_the_ceiling(self):
        endo = turns(EndocrineSystem(), WARM, 15)
        self.assertLess(endo.oxytocin, 0.8)
        self.assertLess(endo.dopamine, 0.8)
        self.assertGreater(endo.oxytocin, REST["oxytocin"] + 0.3)  # still clearly warm

    def test_quiet_turns_bring_it_back_to_rest(self):
        endo = turns(turns(EndocrineSystem(), WARM, 8), NEUTRAL, 10)
        self.assertLess(abs(endo.oxytocin - REST["oxytocin"]), 0.12)
        self.assertLess(abs(endo.serotonin - REST["serotonin"]), 0.08)

    def test_stress_is_a_state_of_its_own(self):
        endo = turns(EndocrineSystem(), STRESS, 3)
        self.assertGreater(endo.cortisol, 0.5)
        self.assertLess(endo.dopamine, REST["dopamine"] - 0.2)

    def test_a_rise_uses_only_the_headroom_left(self):
        high, low = EndocrineSystem(), EndocrineSystem()
        high.cfg = low.cfg = {"BIO": {"DECAY_RATE": 0.0}}
        high.oxytocin, low.oxytocin = 0.8, 0.2
        for endo in (high, low):
            endo.metabolize(health=100.0, stamina=100.0, **WARM)
        self.assertLess(high.oxytocin - 0.8, (low.oxytocin - 0.2) / 2)

    def test_a_decay_rate_of_zero_freezes_the_chemistry(self):
        endo = EndocrineSystem()
        endo.cfg = {"BIO": {"DECAY_RATE": 0.0}}  # LABORATORY
        endo.oxytocin = 0.6
        turns(endo, NEUTRAL, 5)
        self.assertAlmostEqual(endo.oxytocin, 0.6, places=6)
