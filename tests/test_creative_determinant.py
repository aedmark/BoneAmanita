"""tests/test_creative_determinant.py

The governor's regime gate, and what is left of the Creative Determinant.

This file used to test a graph Laplacian and a Picard iteration. Both are gone.
Instrumented on our own code with the real 768d embedder and a 23-node subgraph
seeded at 17% edge density, denser than a real session:

    Phi^T L Phi / Phi^T Phi  : +0.006149
    b_mean                   : +0.408239
    reported lambda_1        : -0.402089
    graph share of |lambda_1|:  1.53%

and lambda_1 came back byte-identical at voltage 15, 25, 30, 35, 45, 60 and 90.
The topology contributed one and a half percent and the voltage contributed
nothing; what remained was the mean ordvec similarity computed the expensive
way. Nelson Spence predicted the magnitude before we measured it, having found
the same collapse at 207,695 nodes, and recommended the replacement tested here.

What survives of his mathematics is in `physics/maths.py`:
`calculate_viability`, `update_coherence_debt` and `execute_metabolic_tick`
still drive the ATP and ROS economy, and that is genuinely his equation with the
debt closure attached.
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from brain.composer import LLMInterface, PromptComposer
from engine.core import CyberneticGovernor, InsufficientCorpus
from engine.presets import BoneConfig
from tests.base import BoneTestCase


class _FakeBitmap:
    """Stands in for ordvec's SignBitmap so the gate is testable offline.

    The real one cannot be used here: `SignBitmap` requires a dimension that is
    a multiple of 64 and the suite is pinned to the 8-dim hash backend, so the
    whole ordvec path is unreachable under test. That is worth knowing on its
    own, and it is why these tests drive the arithmetic directly.
    """

    def __init__(self, scores):
        self._scores = np.asarray(scores, dtype=np.float64)

    def score_all(self, _q):
        return self._scores


def _governor_over(scores):
    gov = CyberneticGovernor()
    gov.memory_bitmap = _FakeBitmap(scores)
    gov.cached_nodes = list(range(len(scores)))
    gov._sync_ordvec_indices = lambda _core: True
    gov._cached_vectorizer = lambda _text: [0.0] * 8
    return gov


class RegimeSignal(unittest.TestCase):
    """z_top10 is how far the neighbourhood stands above the corpus null."""

    PHYSICS = {"voltage": 30.0, "narrative_drag": 0.6}

    def test_a_flat_corpus_has_no_regime_to_report(self):
        """Every memory scoring alike means there is no null to measure against."""
        gov = _governor_over([384.0] * 64)
        with self.assertRaises(InsufficientCorpus):
            gov._bitmap_regulation(self.PHYSICS, 1.0, object(), "anything", None)

    def test_too_few_memories_declines_rather_than_guesses(self):
        """navi-fractal's rule, applied to the governor."""
        floor = int(BoneConfig().GATE.MIN_CORPUS)
        gov = _governor_over(np.random.default_rng(0).normal(384, 14, floor - 1))
        with self.assertRaises(InsufficientCorpus):
            gov._bitmap_regulation(self.PHYSICS, 1.0, object(), "anything", None)

    def test_a_standout_neighbourhood_reads_high(self):
        scores = np.full(200, 384.0)
        scores[:10] = 470.0          # ten memories far above the null
        scores[10:] += np.random.default_rng(1).normal(0, 14, 190)
        gov = _governor_over(scores)
        gov._bitmap_regulation(self.PHYSICS, 1.0, object(), "anything", None)
        self.assertGreater(gov.last_z, 0.5)
        self.assertEqual(gov.last_sol, "coherent")

    def test_a_random_corpus_reads_as_no_neighbourhood_at_any_size(self):
        """The bug that gating on raw z would have shipped.

        A pure-noise corpus has no neighbourhood by construction, but its
        top-10 mean still drifts upward with size: 2.05 sigma at n=200, 2.65 at
        n=1000, 3.55 at n=20000. A fixed threshold on raw z would have read
        every one of these as coherent once the memory got big enough, and it
        would have done so gradually, as the engine was used.
        """
        for n in (64, 200, 1000, 4000):
            with self.subTest(corpus=n):
                scores = np.random.default_rng(n).normal(384, 14, n)
                gov = _governor_over(scores)
                gov._bitmap_regulation(self.PHYSICS, 1.0, object(), "anything", None)
                self.assertLess(
                    gov.last_z, 0.5,
                    f"a random corpus of {n} read as coherent "
                    f"(raw z was {gov.last_z_raw:.2f})",
                )
                self.assertEqual(gov.last_sol, "diffuse")

    def test_the_null_baseline_tracks_corpus_size(self):
        from engine.core import CyberneticGovernor as G

        self.assertLess(G._null_z(32), G._null_z(1000))
        self.assertLess(G._null_z(1000), G._null_z(20000))
        self.assertAlmostEqual(G._null_z(1000), 2.62, delta=0.1)

    def test_z_is_scale_free(self):
        """The same shape at a different offset and spread reads the same.

        This is the property that makes the pivot calibratable once rather than
        per corpus, and it is why a sign-agreement z is a better signal than the
        raw similarity it replaced.
        """
        base = np.concatenate([np.full(10, 3.0), np.zeros(190)])
        a = _governor_over(384 + 14 * base)
        b = _governor_over(100 + 3 * base)
        for gov in (a, b):
            gov._bitmap_regulation(self.PHYSICS, 1.0, object(), "x", None)
        self.assertAlmostEqual(a.last_z, b.last_z, places=6)


class GateTemperature(unittest.TestCase):
    def setUp(self):
        from engine.core import CyberneticGovernor
        from engine.presets import BoneConfig
        self.gov = CyberneticGovernor()
        self.gate = BoneConfig().GATE

    def test_never_measured_leaves_the_band_alone(self):
        self.assertIsNone(self.gov.last_z)
        self.assertIsNone(self.gov.gate_openness())

    def test_a_diffuse_neighbourhood_keeps_the_lower_share_not_zero(self):
        """It used to lock the band to (0, 0), which sent temperature 0 on every measured turn."""
        self.gov.last_z = float(self.gate.Z_PIVOT) - 0.5
        self.assertAlmostEqual(self.gov.gate_openness(), float(self.gate.DIFFUSE_SHARE))

    def test_openness_climbs_with_z_and_is_capped_at_the_pivot(self):
        self.gov.last_z = float(self.gate.Z_PIVOT) / 2
        half = self.gov.gate_openness()
        self.assertGreater(half, float(self.gate.DIFFUSE_SHARE))
        self.gov.last_z = float(self.gate.Z_PIVOT)
        self.assertAlmostEqual(self.gov.gate_openness(), 1.0)
        self.gov.last_z = float(self.gate.Z_PIVOT) + 500.0
        self.assertAlmostEqual(self.gov.gate_openness(), 1.0)

    def test_the_modulator_narrows_the_somatic_band_and_chemistry_still_moves(self):
        from body.somatic_budget import SomaticBudget
        from brain.mind import NeurotransmitterModulator

        from unittest.mock import MagicMock

        budget = SomaticBudget.evaluate({}, {})
        mod = NeurotransmitterModulator(bio_ref=MagicMock())
        temps = set()
        for dopamine in (0.0, 1.0):
            mod.current_chem.dopamine = dopamine
            for openness in (float(self.gate.DIFFUSE_SHARE), 1.0):
                params = mod.modulate(base_voltage=30.0, physics_state={"thermal_openness": openness},
                                      somatic_budget=budget)
                lo, hi = params["temperature_band"]
                self.assertGreater(lo, 0.0)
                self.assertLessEqual(lo, params["temperature"])
                self.assertLessEqual(params["temperature"], hi)
                temps.add(params["temperature"])
        self.assertGreater(len(temps), 1, "chemistry and openness should move the temperature")

    def test_policy_follows_the_same_threshold(self):
        self.gov.last_z = float(self.gate.Z_PIVOT) + 0.1
        self.assertEqual(self.gov.get_policy_shift(), "CO_REGULATION")
        self.gov.last_z = float(self.gate.Z_PIVOT) - 0.1
        self.assertEqual(self.gov.get_policy_shift(), "EFFICIENCY")

    def test_an_unmeasured_regime_does_not_claim_co_regulation(self):
        self.gov.last_z = None
        self.gov.order = 1
        self.assertEqual(self.gov.get_policy_shift(), "EFFICIENCY")


class DeclineIsNotFailure(BoneTestCase):
    """A declined measurement must read differently from a broken one."""

    def test_declining_files_an_honest_receipt_and_falls_back(self):
        from engine.receipts import ReceiptLedger

        gov = self.engine.governor
        gov._sync_ordvec_indices = lambda _c: True
        gov.memory_bitmap = _FakeBitmap([384.0] * 4)
        gov._cached_vectorizer = lambda _t: [0.0] * 8
        ledger = ReceiptLedger.get_instance()
        gov.regulate(
            {"voltage": 30.0, "narrative_drag": 0.6}, 1.0,
            memory_core=object(), user_text="something",
        )
        receipts = ledger.for_subsystem("governor.bitmap_gate")
        self.assertTrue(receipts, "the governor declined and said nothing")
        latest = receipts[-1]
        self.assertFalse(
            latest.degraded,
            "declining to measure is not a degraded path; it is the correct one",
        )
        self.assertIn("declined", latest.effect)
        self.assertIsNone(gov.last_z, "a declined turn must not leave a stale z")
        self.assertEqual(gov.last_sol, "not_measured")




class ThermalGateConsumer(unittest.TestCase):
    def setUp(self):
        self.llm = LLMInterface(events_ref=MagicMock(), provider="mock")

    def _generate(self, prompt, params):
        with patch.object(self.llm, "mock_generation", return_value="ok") as mock:
            self.llm.generate(prompt, params)
        return mock.call_args[0][0]

    def test_the_tag_sets_the_temperature_verbatim(self):
        params = {"temperature": 0.5}
        self._generate("body\n<thermal_gate>1.1000</thermal_gate>", params)
        self.assertAlmostEqual(params["temperature"], 1.1, places=6)
        self.assertEqual(params["top_p"], 0.95)

    def test_a_closed_gate_locks_sampling(self):
        params = {"temperature": 0.9}
        self._generate("body\n<thermal_gate>0.0000</thermal_gate>", params)
        self.assertEqual(params["temperature"], 0.0)
        self.assertEqual(params["top_p"], 0.1)

    def test_the_tag_never_reaches_the_model(self):
        sent = self._generate("body\n<thermal_gate>0.8000</thermal_gate>", {})
        self.assertNotIn("thermal_gate", sent)
        self.assertIn("body", sent)

    def test_an_absent_tag_leaves_sampling_alone(self):
        params = {"temperature": 0.42}
        self._generate("body with no tag at all", params)
        self.assertEqual(params["temperature"], 0.42)


class WhatSurvivesOfTheDeterminant(unittest.TestCase):
    """The metabolic economy is still solving Spence's equation."""

    def test_viability_carries_the_debt_closure(self):
        from physics.maths import CreativeDeterminantEngine

        engine = CreativeDeterminantEngine()
        rested = engine.calculate_viability(kappa=0.8, gamma=0.8, mu=0.4)
        engine.coherence_debt = 2.0
        indebted = engine.calculate_viability(kappa=0.8, gamma=0.8, mu=0.4)
        self.assertLess(
            indebted, rested, "lambda_eff = lambda_0 * (1 + D) is not being applied"
        )

    def test_positive_viability_feeds_the_organism(self):
        from physics.maths import CreativeDeterminantEngine

        atp, ros = CreativeDeterminantEngine().execute_metabolic_tick(0.5)
        self.assertGreater(atp, 0.0)
        self.assertLess(ros, 0.0)

    def test_negative_viability_costs_it(self):
        from physics.maths import CreativeDeterminantEngine

        atp, ros = CreativeDeterminantEngine().execute_metabolic_tick(-0.5)
        self.assertLess(atp, 0.0)
        self.assertGreater(ros, 0.0)
