"""tests/test_cortex.py"""

import unittest
from unittest.mock import MagicMock

from brain.akashic import TheAkashicRecord
from brain.cortex import CortexServices, TheCortex
from spores.network import MycelialNetwork
from engine.presets import BoneConfig


def _drag_over_limit() -> float:
    """A narrative_drag value guaranteed to trip the cortex toxicity gates.

    `narrative_drag` runs from DRAG_FLOOR to DRAG_HALT, not 0..1, and the gates
    compare it against CORTEX.DRAG_STRESS_THRESHOLD. Deriving the fixture from
    that constant means retuning the threshold moves the test with it, instead
    of leaving a literal that once cleared a limit nobody uses any more.
    """
    from engine.presets import BoneConfig
    from engine.struts import safe_get

    return float(safe_get(safe_get(BoneConfig(), "CORTEX", {}), "DRAG_STRESS_THRESHOLD", 8.0)) + 1.0



try:
    from tests.base import BoneTestCase
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tests.base import BoneTestCase


class CortexArchitectTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()

        self.mock_services = CortexServices(
            events=MagicMock(),
            lore={},
            lexicon=MagicMock(),
            inventory=MagicMock(),
            consultant=MagicMock(),
            orchestrator=MagicMock(),
            symbiosis=MagicMock(),
            # Spec'd, so a call to a method the real class lacks fails here too.
            # An unspecced mock accepted `mind_memory.record_scar` for as long
            # as production crashed on it.
            mind_memory=MagicMock(spec=MycelialNetwork),
            bio=MagicMock(),
            config_ref=self.config,
            akashic=MagicMock(spec=TheAkashicRecord),
        )

        mock_eng = self.mock_services.orchestrator.eng
        mock_eng.navi_sad.calculate_semantic_dimension.return_value = 1.0
        mock_eng.shared_lattice.u.E = 0.5
        mock_eng.governor.calculate_coupling.return_value = 1.0

        self.cortex = TheCortex(self.mock_services, llm_client=MagicMock())

    def test_apply_boot_overlay_adventure(self):
        state = {"mind": {}}
        self.cortex.active_mode = "ADVENTURE"
        self.cortex._apply_boot_overlay(state, "SYSTEM_BOOT: A dark forest")

        self.assertIn(
            "world", state, "[FAIL] Boot overlay failed to initialize world state."
        )
        self.assertIn(
            "A dark forest",
            state["world"].get("orbit", []),
            "[FAIL] Thought seed not injected into orbit.",
        )
        self.assertEqual(
            state["mind"].get("role"),
            "The Architect",
            "[FAIL] Incorrect role mapped for ADVENTURE mode.",
        )

    def test_evaluate_toxicity_system_halt(self):
        # Above CORTEX.DRAG_STRESS_THRESHOLD, read rather than hardcoded. The
        # literal 2.5 here cleared a limit of 1.5 that sat near the floor of the
        # real drag range and had never fired in production, because the
        # serialized physics packet did not carry `narrative_drag` at all.
        phys_state = {
            "narrative_drag": _drag_over_limit(),
            "chi": 0.5,
            "m_a": 0.5,
        }
        sim_result = {"ui": "Standard interface output."}

        from engine.core import CycleContext, PhysicsPacket
        ctx = CycleContext(input_text="test", clean_words="test")
        ctx.physics = PhysicsPacket()
        ctx.physics.narrative_drag = phys_state.get("narrative_drag", 1.0)
        ctx.physics.chi = phys_state.get("chi", 0.0)
        ctx.physics.m_a = phys_state.get("m_a", 0.0)
        ctx.physics.delta_atp = phys_state.get("delta_atp", 0.0)
        ctx.physics.delta_ros = phys_state.get("delta_ros", 0.0)
        self.mock_services.bio.mito.state.ros_buildup = 0.0
        self.cortex.nominate_toxicity(ctx)
        
        self.assertEqual(len(ctx.nominations), 1)
        nom = ctx.nominations[0]
        self.assertEqual(
            nom.packet.get("type"),
            "SYSTEM_HALT",
            "[FAIL] Expected SYSTEM_HALT for high friction.",
        )
        self.assertIn(
            "Tensegrity Anchor engaged",
            nom.packet.get("ui", ""),
            "[FAIL] Missing Gordon anchor warning.",
        )

    def test_evaluate_toxicity_counterfactual_rejection(self):
        phys_state = {"narrative_drag": 1.5, "chi": 0.8, "m_a": 1.0}
        sim_result = {"ui": ""}
        self.mock_services.bio.mito.state.ros_buildup = 0.0

        from engine.core import CycleContext, PhysicsPacket
        ctx = CycleContext(input_text="test", clean_words="test")
        ctx.physics = PhysicsPacket()
        ctx.physics.narrative_drag = phys_state.get("narrative_drag", 1.0)
        ctx.physics.chi = phys_state.get("chi", 0.0)
        ctx.physics.m_a = phys_state.get("m_a", 0.0)
        ctx.physics.delta_atp = phys_state.get("delta_atp", 0.0)
        ctx.physics.delta_ros = phys_state.get("delta_ros", 0.0)
        self.mock_services.bio.mito.state.ros_buildup = 0.0
        self.cortex.nominate_toxicity(ctx)
        
        self.assertEqual(len(ctx.nominations), 1)
        nom = ctx.nominations[0]
        self.assertEqual(
            nom.packet.get("type"),
            "COUNTERFACTUAL_REJECTION",
            "[FAIL] Failed to trigger Counterfactual Rejection.",
        )
        self.assertIn(
            "[PINKER]: strain",
            nom.packet.get("ui", ""),
            "[FAIL] Missing Pinker gate rejection log.",
        )
        # PINKER no longer records a scar (20.7.4.36).
        self.mock_services.akashic.record_scar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
