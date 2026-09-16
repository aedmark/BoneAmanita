"""tests/test_creative_determinant.py

The Creative Determinant coupling, end to end.

Project Navi's CD framework (Apache 2.0) already drove ATP/ROS through
physics/observer.py, but the principal eigenvalue lambda_1 was computed only in
a test and the <cd_lambda_1> thermal lock in LLMInterface.generate had no
producer at all. These tests pin the whole chain: observer fields -> cycle ->
physics dict -> composed prompt -> generation parameters.
"""

import re
import unittest
from unittest.mock import MagicMock, patch

from brain.composer import LLMInterface
from physics.models import PhysicsPacket, principal_eigenvalue
from tests.base import BoneTestCase

TAG = re.compile(r"<cd_lambda_1>([-\d.]+)</cd_lambda_1>")


class EigenvalueMath(unittest.TestCase):
    """Theorem 3.16 reduced: coherent configurations exist iff b > 0."""

    def test_lambda_1_is_negated_viability(self):
        self.assertAlmostEqual(
            principal_eigenvalue(kappa=0.8, gamma=0.8, mu=0.5, lambda_val=0.5),
            -((0.8 * 0.8) - (0.5 * 0.5)),
            places=6,
        )

    def test_sign_condition_matches_the_theorem(self):
        """lambda_1 < 0 exactly when viability is positive."""
        coherent = principal_eigenvalue(kappa=0.9, gamma=0.9, mu=0.2, lambda_val=0.5)
        dissolving = principal_eigenvalue(kappa=0.2, gamma=0.3, mu=0.9, lambda_val=0.5)
        self.assertLess(coherent, 0.0)
        self.assertGreater(dissolving, 0.0)

    def test_beta_scales_magnitude_not_sign(self):
        args = dict(kappa=0.9, gamma=0.9, mu=0.2, lambda_val=0.5)
        weak = principal_eigenvalue(beta=0.5, **args)
        strong = principal_eigenvalue(beta=2.0, **args)
        self.assertLess(strong, weak)
        self.assertLess(strong, 0.0)
        self.assertAlmostEqual(strong, 4.0 * weak, places=6)

    def test_coherent_regime_is_reachable_at_the_shipped_lambda(self):
        """Regression: the old (pi/L)^2 term with L=pi pinned lambda_1 >= 0 for
        every state the engine could actually produce, so the generative branch
        was dead under all inputs."""
        packet = PhysicsPacket()
        packet.kappa, packet.gamma, packet.mu = 0.6, 0.97, 0.88
        packet.lambda_val = 0.5
        self.assertGreater(packet.get_viability_potential(), 0.0)
        self.assertLess(packet.get_principal_eigenvalue(), 0.0)

    def test_lambda_val_is_used_as_given(self):
        """Zero means contradiction is free. It must not be overridden with 1.0."""
        packet = PhysicsPacket()
        packet.kappa, packet.gamma, packet.mu = 0.5, 0.5, 1.0
        packet.lambda_val = 0.0
        self.assertAlmostEqual(packet.get_viability_potential(), 0.25, places=6)


class ThermalLockProducer(BoneTestCase):
    """The half that had no coverage: something must actually emit the tag."""

    def test_cortex_attaches_lambda_from_nested_energy(self):
        phys = {"energy": {"kappa": 0.9, "gamma": 0.9, "mu": 0.2, "lambda_val": 0.5}}
        self.engine.cortex._attach_principal_eigenvalue(phys)
        self.assertIn("cd_lambda_1", phys)
        self.assertAlmostEqual(phys["cd_lambda_1"], -((0.81) - (0.1)), places=6)

    def test_attach_is_inert_without_an_energy_block(self):
        phys = {}
        self.engine.cortex._attach_principal_eigenvalue(phys)
        self.assertNotIn("cd_lambda_1", phys)

    def test_composed_prompt_carries_the_tag(self):
        composer = self.engine.cortex.composer
        state = {
            "meta": {"active_mode": "CONVERSATION", "mode_settings": {}},
            "mind": {}, "bio": {}, "world": {}, "soul": {},
            "physics": {"cd_lambda_1": -0.42},
            "dialogue_history": [],
        }
        prompt = composer.compose(state, "a test utterance")
        found = TAG.search(prompt)
        self.assertIsNotNone(found, "[FAIL] compose() emitted no <cd_lambda_1> tag.")
        self.assertAlmostEqual(float(found.group(1)), -0.42, places=4)

    def test_no_tag_emitted_when_physics_is_absent(self):
        composer = self.engine.cortex.composer
        state = {
            "meta": {"active_mode": "CONVERSATION", "mode_settings": {}},
            "mind": {}, "bio": {}, "world": {}, "soul": {},
            "physics": {},
            "dialogue_history": [],
        }
        self.assertIsNone(TAG.search(composer.compose(state, "a test utterance")))


class EigenvalueProvenance(BoneTestCase):
    """Two eigenvalues exist and they are not equally good.

    The governor solves the nonlinear elliptic BVP by Picard iteration over the
    Laplacian of a memory subgraph and takes lambda_1 as a Rayleigh quotient.
    That is the real one. The scalar -beta*(kappa*gamma - lambda*mu) states the
    same sign condition over three per-turn scalars and cannot see memory
    structure at all; it is the cold-start fallback.
    """

    def test_solved_eigenvalue_is_preferred(self):
        phys = {
            "energy": {
                "kappa": 0.6, "gamma": 0.97, "mu": 0.88,
                "lambda_val": 0.5, "lam1": -0.4196,
            }
        }
        self.engine.cortex._attach_principal_eigenvalue(phys)
        self.assertAlmostEqual(phys["cd_lambda_1"], -0.4196, places=4)
        self.assertEqual(phys["cd_lambda_1_source"], "graph_laplacian")

    def test_scalar_fallback_before_any_solve(self):
        phys = {
            "energy": {
                "kappa": 0.6, "gamma": 0.97, "mu": 0.88,
                "lambda_val": 0.5, "lam1": 0.0,
            }
        }
        self.engine.cortex._attach_principal_eigenvalue(phys)
        self.assertEqual(phys["cd_lambda_1_source"], "scalar_fallback")
        self.assertNotEqual(phys["cd_lambda_1"], 0.0)

    def test_the_two_can_disagree_and_the_solve_wins(self):
        """Regression: the scalar shipped to the thermal lock while the governor
        computed a better value that only ever reached the post-turn snapshot,
        which is after the prompt has been composed."""
        energy = {"kappa": 0.9, "gamma": 0.9, "mu": 0.1, "lambda_val": 0.5}
        scalar_only = {"energy": dict(energy, lam1=0.0)}
        solved = {"energy": dict(energy, lam1=0.25)}
        self.engine.cortex._attach_principal_eigenvalue(scalar_only)
        self.engine.cortex._attach_principal_eigenvalue(solved)
        self.assertLess(scalar_only["cd_lambda_1"], 0.0)
        self.assertGreater(solved["cd_lambda_1"], 0.0)

    def test_packet_carries_the_field(self):
        from physics.models import PhysicsPacket

        packet = PhysicsPacket()
        self.assertEqual(packet.lam1, 0.0)
        packet.lam1 = -0.3
        self.assertIn("lam1", packet.to_dict().get("energy", packet.to_dict()))


class ThermalLockConsumer(unittest.TestCase):
    """generate() must act on the tag and must never forward it to the model."""

    def setUp(self):
        self.llm = LLMInterface(events_ref=MagicMock(), provider="mock")

    def test_tag_is_stripped_before_transmission(self):
        sent = {}

        def fake_transmit(payload, timeout=None):
            sent["prompt"] = payload["messages"][0]["content"]
            return "ok"

        llm = LLMInterface(events_ref=MagicMock(), provider="ollama")
        with patch.object(llm, "_transmit", side_effect=fake_transmit):
            llm.generate("Real content <cd_lambda_1>-0.3</cd_lambda_1>", {})
        self.assertNotIn("cd_lambda_1", sent["prompt"])
        self.assertIn("Real content", sent["prompt"])

    def test_coherent_state_opens_heat_proportional_to_magnitude(self):
        near, far = {}, {}
        self.llm.generate("p <cd_lambda_1>-0.1</cd_lambda_1>", near)
        self.llm.generate("p <cd_lambda_1>-0.4</cd_lambda_1>", far)
        self.assertGreater(far["temperature"], near["temperature"])
        self.assertLessEqual(far["temperature"], 1.2)

    def test_dissolving_state_collapses_to_determinism(self):
        params = {}
        self.llm.generate("p <cd_lambda_1>0.25</cd_lambda_1>", params)
        self.assertEqual(params.get("temperature"), 0.0)
        self.assertEqual(params.get("top_p"), 0.1)


class EndToEnd(BoneTestCase):
    def test_a_real_turn_produces_a_tag_and_sets_temperature(self):
        seen = []
        original = LLMInterface.generate

        def spy(inner_self, prompt, params):
            if match := TAG.search(prompt):
                seen.append((float(match.group(1)), dict(params)))
            return original(inner_self, prompt, params)

        with patch.object(LLMInterface, "generate", spy):
            self.engine.process_turn(
                "the greenhouse smelled like warm tomatoes and rust"
            )
            self.engine.orchestrator.shutdown()

        self.assertTrue(
            seen, "[FAIL] A full turn emitted no <cd_lambda_1> tag; the lock is dead."
        )
        lam, params = seen[0]
        if lam < 0:
            self.assertGreater(params.get("temperature", 0.0), 0.7)
        else:
            self.assertEqual(params.get("temperature"), 0.0)

    def test_observer_populates_all_three_cd_fields(self):
        """Regression: gamma and mu were computed and then dropped, because only
        `kappa` was listed in ObservationPhase._SYNC_KEYS."""
        packet = self.engine.phys.observer.gaze(
            "the greenhouse smelled like warm tomatoes and rust",
            self.engine.mind.mem.graph,
        )["physics"]
        self.assertGreater(packet.kappa, 0.0)
        self.assertGreater(packet.gamma, 0.0)
        self.assertGreater(packet.mu, 0.0)
        self.assertGreater(packet.lambda_val, 0.0)


if __name__ == "__main__":
    unittest.main()
