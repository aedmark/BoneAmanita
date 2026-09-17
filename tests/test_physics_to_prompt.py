"""tests/test_physics_to_prompt.py

ROADMAP A4. The contract of the whole engine, asserted end to end.

BoneAmanita's entire claim is that a measured state changes what the model is
told. Everything else (the lexicon, the physics formulas, the memory, the
Creative Determinant) exists to produce numbers, and those numbers are only
worth anything if they reach the prompt. That step was untested: the suite knew
`compose()` returned a string, not that a high contradiction put a paradox
directive in it.

These tests read their thresholds from `BoneConfig` rather than hardcoding them,
so retuning a constant moves the tests with it. A test that pins 0.6 would go
green against a threshold nobody is using any more, which is the same illness as
a subsystem wired to nothing.

Every positive assertion is paired with a negative one. A directive that is
always present tells you nothing, and would pass a test that only checks for its
presence under load.
"""

import unittest

from brain.composer import PromptComposer
from presets import BoneConfig
from tests.base import BoneTestCase

PARADOX_REST = "SYSTEM OVERRIDE: PARADOX REST"
ORTHOGONAL = "SYSTEM OVERRIDE: ORTHOGONAL ATTENTION"
EXHAUSTION = "You must conclude your thought in 3 sentences or less"


class PhysicsToPromptCase(BoneTestCase):
    """Shared rig: a real composer over the engine's real prompt library."""

    def setUp(self):
        super().setUp()
        self.cortex_cfg = BoneConfig().CORTEX
        self.composer = PromptComposer(
            {"system_prompts": self.engine.prompt_library, "lenses": {}}
        )

    def compose_with(
        self,
        physics: dict,
        mode: str = "CONVERSATION",
        mood_override: str = "",
        **state_over,
    ) -> str:
        """Compose a prompt from a physics packet and nothing else unusual.

        `mood_override` is an argument of `compose()`, not a key in the state
        dict. An earlier version of this helper accepted it into `state_over`,
        where the composer never looked for it, and the precedence test below
        passed against a deliberately broken composer. Anything the composer
        takes as a parameter has to be passed as one.
        """
        self.engine.cortex.active_mode = mode
        state = self.engine.cortex.gather_state({"physics": dict(physics)})
        state.setdefault("meta", {})["active_mode"] = mode
        for key, value in state_over.items():
            state[key] = value
        return self.composer.compose(
            state,
            "the thing I am saying",
            modifiers={"include_inventory": False},
            mood_override=mood_override,
        )

    def over(self, threshold: float) -> float:
        return min(1.0, threshold + 0.15)

    def under(self, threshold: float) -> float:
        return max(0.0, threshold - 0.15)


class TestContradictionDirectives(PhysicsToPromptCase):
    """High contradiction must change the instructions, not just the numbers."""

    def test_paradox_rest_appears_when_both_gates_open(self):
        chi = self.over(self.cortex_cfg.PARADOX_CHI)
        beta = self.over(self.cortex_cfg.PARADOX_BETA)
        prompt = self.compose_with({"chi": chi, "contradiction": beta})
        self.assertIn(
            PARADOX_REST,
            prompt,
            f"chi={chi} and contradiction={beta} are both above their thresholds "
            f"({self.cortex_cfg.PARADOX_CHI}, {self.cortex_cfg.PARADOX_BETA}) and the "
            "paradox directive did not reach the model.",
        )

    def test_paradox_rest_is_absent_in_a_calm_state(self):
        """The half that proves it is a gate rather than boilerplate."""
        prompt = self.compose_with(
            {
                "chi": self.under(self.cortex_cfg.PARADOX_CHI),
                "contradiction": self.under(self.cortex_cfg.PARADOX_BETA),
            }
        )
        self.assertNotIn(PARADOX_REST, prompt)
        self.assertNotIn(ORTHOGONAL, prompt)

    def test_chi_alone_does_not_open_the_paradox_gate(self):
        """Both conditions are required, and the `and` has to stay an `and`."""
        prompt = self.compose_with(
            {
                "chi": self.over(self.cortex_cfg.PARADOX_CHI),
                "contradiction": self.under(self.cortex_cfg.PARADOX_BETA),
            }
        )
        self.assertNotIn(PARADOX_REST, prompt)

    def test_orthogonal_attention_covers_contradiction_without_chaos(self):
        beta = self.over(self.cortex_cfg.ORTHOGONAL_BETA)
        prompt = self.compose_with(
            {"chi": self.under(self.cortex_cfg.PARADOX_CHI), "contradiction": beta}
        )
        self.assertIn(ORTHOGONAL, prompt)
        self.assertNotIn(PARADOX_REST, prompt)

    def test_the_two_directives_never_ship_together(self):
        """They are mutually exclusive by construction (`if`/`elif`).

        Sending both would tell the model to rest in the paradox and to evaluate
        it from two perspectives at once, which is an instruction to do two
        different things about the same state.
        """
        prompt = self.compose_with(
            {
                "chi": self.over(self.cortex_cfg.PARADOX_CHI),
                "contradiction": self.over(self.cortex_cfg.ORTHOGONAL_BETA),
            }
        )
        self.assertIn(PARADOX_REST, prompt)
        self.assertNotIn(ORTHOGONAL, prompt)

    def test_adventure_mode_suppresses_both(self):
        """A real contract, and a surprising one, so it is pinned here.

        `compose()` blanks `system_injection` entirely in ADVENTURE. If that is
        ever changed it should be changed deliberately, not discovered.
        """
        prompt = self.compose_with(
            {
                "chi": self.over(self.cortex_cfg.PARADOX_CHI),
                "contradiction": self.over(self.cortex_cfg.ORTHOGONAL_BETA),
            },
            mode="ADVENTURE",
        )
        self.assertNotIn(PARADOX_REST, prompt)
        self.assertNotIn(ORTHOGONAL, prompt)


class TestExhaustionReachesThePrompt(PhysicsToPromptCase):
    """Spent energy has to shorten the output, or the metabolism is decorative."""

    THRESHOLD = 0.8

    def test_exhaustion_shortens_the_instruction(self):
        prompt = self.compose_with({"exhaustion": self.THRESHOLD + 0.15})
        self.assertIn(EXHAUSTION, prompt)

    def test_a_rested_engine_is_not_told_to_hurry(self):
        prompt = self.compose_with({"exhaustion": self.THRESHOLD - 0.3})
        self.assertNotIn(EXHAUSTION, prompt)


class TestSomaticCues(PhysicsToPromptCase):
    """Each affective dimension has its own cue and its own threshold."""

    CUES = (
        ("psi", "SOMATIC_PSI", "Adrenaline Spike"),
        ("chi", "SOMATIC_CHI", "Cortisol Spike"),
        ("contradiction", "SOMATIC_BETA", "Paradox Strain"),
        ("valence", "SOMATIC_VALENCE", "Oxytocin Surge"),
    )

    def test_each_cue_fires_on_its_own_dimension(self):
        for field, cfg_key, cue in self.CUES:
            with self.subTest(cue=cue):
                threshold = float(getattr(self.cortex_cfg, cfg_key))
                prompt = self.compose_with({field: self.over(threshold)})
                self.assertIn(
                    cue,
                    prompt,
                    f"{field} above {cfg_key}={threshold} did not produce {cue!r}.",
                )

    def test_no_cue_fires_in_a_neutral_state(self):
        neutral = {
            field: self.under(float(getattr(self.cortex_cfg, cfg_key)))
            for field, cfg_key, _ in self.CUES
        }
        prompt = self.compose_with(neutral)
        for _, _, cue in self.CUES:
            with self.subTest(cue=cue):
                self.assertNotIn(cue, prompt)

    def test_a_cue_does_not_fire_on_a_neighbouring_dimension(self):
        """Crosstalk here would make every affective reading interchangeable."""
        threshold = float(self.cortex_cfg.SOMATIC_PSI)
        prompt = self.compose_with(
            {
                "psi": self.over(threshold),
                "chi": self.under(float(self.cortex_cfg.SOMATIC_CHI)),
                "valence": self.under(float(self.cortex_cfg.SOMATIC_VALENCE)),
                "contradiction": self.under(float(self.cortex_cfg.SOMATIC_BETA)),
            }
        )
        self.assertIn("Adrenaline Spike", prompt)
        self.assertNotIn("Cortisol Spike", prompt)
        self.assertNotIn("Oxytocin Surge", prompt)


class TestMetricsSurviveTheJourney(PhysicsToPromptCase):
    """The numeric readout the model is told to consume, not print."""

    def test_the_measured_values_are_the_ones_rendered(self):
        prompt = self.compose_with(
            {"voltage": 71.0, "exhaustion": 0.42, "contradiction": 0.33, "psi": 0.27}
        )
        self.assertIn("Voltage=71.0", prompt)
        self.assertIn("Exhaustion=0.42", prompt)
        self.assertIn("Contradiction=0.33", prompt)
        self.assertIn("Void=0.27", prompt)

    def test_the_readout_is_marked_internal(self):
        """If this framing is lost the model starts printing UI bars at the user."""
        prompt = self.compose_with({"voltage": 50.0})
        self.assertIn("DO NOT RENDER OR PRINT THIS TO THE USER", prompt)


class TestMetabolicStateReachesThePrompt(PhysicsToPromptCase):
    """The starvation half of A4: spent metabolism must change the instruction.

    The chain is `raw_cost > BIO.ANAEROBIC_THRESHOLD` in `body/metabolism.py`,
    which sets a respiration status that `body/system.py` packages into the bio
    block, which `_build_persona_block` turns into a prose directive. Three
    modules and no single place where the whole path is visible, which is why it
    is asserted end to end here rather than trusted.
    """

    ANAEROBIC = "ANAEROBIC STATE. Raw, breathless, efficient prose."

    def test_anaerobic_respiration_degrades_the_prose_instruction(self):
        prompt = self.compose_with({"voltage": 30.0}, bio={"respiration": "ANAEROBIC"})
        self.assertIn(self.ANAEROBIC, prompt)

    def test_normal_respiration_does_not(self):
        prompt = self.compose_with({"voltage": 30.0}, bio={"respiration": "RESPIRING"})
        self.assertNotIn(self.ANAEROBIC, prompt)

    def test_anaerobic_outranks_an_explicit_mood(self):
        """A real precedence rule: the body overrules the mood, not the reverse.

        `_build_persona_block` checks respiration first and `mood_override`
        second. If that order ever flips, an engine with no metabolic headroom
        would keep writing in whatever voice it was asked for, which is the one
        state where the constraint is supposed to bind hardest.
        """
        prompt = self.compose_with(
            {"voltage": 30.0},
            bio={"respiration": "ANAEROBIC"},
            mood_override="Current Biology: EXUBERANT",
        )
        self.assertIn(self.ANAEROBIC, prompt)
        self.assertNotIn("EXUBERANT", prompt)

    def test_the_atp_pool_reaches_the_readout(self):
        prompt = self.compose_with(
            {"voltage": 30.0}, bio={"mito": {"atp_pool": 12.5, "ros_buildup": 88.0}}
        )
        self.assertIn("P:12.5", prompt)
        self.assertIn("ROS:88.0", prompt)


class TestExhaustionIsTheUsersNotTheEngines(PhysicsToPromptCase):
    """A naming trap, pinned so the next reader does not fall into it.

    `ctx.physics.exhaustion` is assigned from `ctx.user_state` in `cycle.py`,
    which is the engine's inference about how tired the PERSON is. It is not the
    engine's own ATP pool, despite sitting in the same metrics line as it and
    reading like a property of the machine.

    Both are real signals and both reach the prompt; they just reach it by
    different routes and mean different things. The engine's own depletion
    arrives as respiration (see above), not as `exhaustion`.
    """

    def test_a_drained_engine_is_not_automatically_exhausted(self):
        prompt = self.compose_with(
            {"voltage": 30.0, "exhaustion": 0.1},
            bio={"mito": {"atp_pool": 0.0, "ros_buildup": 100.0}},
        )
        self.assertIn("P:0.0", prompt)
        self.assertNotIn(
            EXHAUSTION,
            prompt,
            "An empty ATP pool produced the exhaustion directive. If that link "
            "was added deliberately, update this test and ROADMAP A4; if not, "
            "`exhaustion` has been rewired to something other than user state.",
        )

    def test_a_tired_user_shortens_a_healthy_engine(self):
        prompt = self.compose_with(
            {"voltage": 30.0, "exhaustion": 0.95},
            bio={"mito": {"atp_pool": 100.0, "ros_buildup": 0.0}},
        )
        self.assertIn("P:100.0", prompt)
        self.assertIn(EXHAUSTION, prompt)


class TestVoltageSwitchesTheDirectiveSet(PhysicsToPromptCase):
    """Above 60 volts the composer swaps which block of directives it uses."""

    def test_high_and_low_voltage_produce_different_instructions(self):
        low = self.compose_with({"voltage": 20.0})
        high = self.compose_with({"voltage": 90.0})
        self.assertNotEqual(
            low,
            high,
            "Voltage crossed the 60 threshold and the prompt did not change at all.",
        )
