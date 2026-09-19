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
from constants import Prisma
from presets import BoneConfig
from tests.base import BoneTestCase

PARADOX_REST = "SYSTEM OVERRIDE: PARADOX REST"
ORTHOGONAL = "SYSTEM OVERRIDE: ORTHOGONAL ATTENTION"
_FLAGGING_CAP = int(BoneConfig().SOMATIC_BUDGET.SENTENCE_CAP_FLAGGING)
EXHAUSTION = f"Your partner is running low. Answer in at most {_FLAGGING_CAP} sentences."


class PhysicsToPromptCase(BoneTestCase):
    """Shared rig: a real composer over the engine's real prompt library."""

    def setUp(self):
        super().setUp()
        self.cortex_cfg = BoneConfig().CORTEX
        self.somatic_cfg = BoneConfig().SOMATIC_BUDGET
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
            
        if not state.get("somatic_budget"):
            from body.somatic_budget import SomaticBudget
            # Translate test physics properties into a budget for the composer
            e_u = physics.get("exhaustion", physics.get("E", 0.0))
            atp = physics.get("p", 100.0)
            ros = physics.get("ros", 0.0)
            respiration = state.get("bio", {}).get("respiration", "RESPIRING")
            state["somatic_budget"] = SomaticBudget.evaluate(
                {"exhaustion": e_u, "effort": 100.0},
                {"atp_pool": atp, "ros": ros, "respiration": respiration}
            )
            
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

    @property
    def THRESHOLD(self) -> float:
        """Read from config: the gate moved from 0.8 to 0.5 after the census
        showed a flagging partner never reaches 0.8 (ROADMAP D0)."""
        return float(self.cortex_cfg.EXHAUSTION_GATE)

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

    @property
    def ANAEROBIC(self) -> str:
        cap = int(self.somatic_cfg.SENTENCE_CAP_ANAEROBIC)
        return f"Your partner is running low. Answer in at most {cap} sentences."

    def test_anaerobic_respiration_degrades_the_prose_instruction(self):
        prompt = self.compose_with({"voltage": 30.0}, bio={"respiration": "ANAEROBIC"})
        self.assertIn(self.ANAEROBIC, prompt)

    def test_normal_respiration_does_not(self):
        prompt = self.compose_with({"voltage": 30.0}, bio={"respiration": "RESPIRING"})
        self.assertNotIn(self.ANAEROBIC, prompt)

    # def test_anaerobic_outranks_an_explicit_mood(self):
    #     """A real precedence rule: the body overrules the mood, not the reverse."""
    #     pass

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
            {"voltage": 30.0, "exhaustion": 0.05},
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


class TestSomaticBudgetReachesThePrompt(PhysicsToPromptCase):
    """ROADMAP D1: one budget object, read by the composer's text.

    The tests above exercise the budget indirectly, through the helper's own
    translation of raw physics into a budget. These construct a `SomaticBudget`
    directly and pass it through `state_over`, so each field's effect on the
    rendered text is pinned on its own rather than through that translation.
    """

    def _budget(self, **overrides) -> "SomaticBudget":
        from body.somatic_budget import SomaticBudget

        defaults = dict(
            word_cap=200,
            sentence_cap=10,
            closing_question_allowed=True,
            offer_to_carry_load=False,
            retry_allowance=3,
            temperature_band=(0.6, 0.9),
            forbid_body_narration=True,
            reason="Nominal",
        )
        defaults.update(overrides)
        return SomaticBudget(**defaults)

    def test_a_low_sentence_cap_asks_the_partner_directly(self):
        prompt = self.compose_with({}, somatic_budget=self._budget(sentence_cap=3))
        self.assertIn("Your partner is running low. Answer in at most 3 sentences.", prompt)

    def test_a_generous_sentence_cap_is_stated_as_a_number_only(self):
        prompt = self.compose_with({}, somatic_budget=self._budget(sentence_cap=10))
        self.assertIn("Sentence cap: 10 sentences.", prompt)
        self.assertNotIn("running low", prompt)

    def test_forbidding_narration_states_it(self):
        prompt = self.compose_with(
            {}, somatic_budget=self._budget(forbid_body_narration=True)
        )
        self.assertIn(
            "CRITICAL: Do not narrate your body, breath, lungs, or physical exhaustion.",
            prompt,
        )

    def test_adventure_mode_permits_narration(self):
        """ADVENTURE's room template needs `**Header**`/`(via X)` exits, which the
        ban can't tell apart from narration (body/somatic_budget.py)."""
        prompt = self.compose_with(
            {}, mode="ADVENTURE", somatic_budget=self._budget(forbid_body_narration=False)
        )
        self.assertNotIn("Do not narrate your body", prompt)

    def test_no_closing_question_is_stated_when_disallowed(self):
        prompt = self.compose_with(
            {}, somatic_budget=self._budget(closing_question_allowed=False)
        )
        self.assertIn("Do not ask a closing question.", prompt)

    def test_a_closing_question_is_not_forbidden_by_default(self):
        prompt = self.compose_with(
            {}, somatic_budget=self._budget(closing_question_allowed=True)
        )
        self.assertNotIn("Do not ask a closing question.", prompt)

    def test_offering_to_carry_the_load_is_stated_when_flagged(self):
        prompt = self.compose_with(
            {}, somatic_budget=self._budget(offer_to_carry_load=True)
        )
        self.assertIn(
            "Your partner is carrying a heavy load. Offer to carry part of the burden.",
            prompt,
        )

    def test_no_offer_is_made_when_effort_is_not_critical(self):
        prompt = self.compose_with(
            {}, somatic_budget=self._budget(offer_to_carry_load=False)
        )
        self.assertNotIn("Offer to carry part of the burden.", prompt)


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


class TestTheSerializationBoundary(PhysicsToPromptCase):
    """The gap every other test in this file steps over.

    The classes above build a flat physics dict and hand it to `compose()`, so
    they prove the composer's gates are correct. They do NOT prove the measured
    values ever arrive, because a real turn does not hand the composer a
    hand-built dict: it hands it `dump_state(ctx.physics)`.

    `PhysicsPacket` routes attribute access through an alias map, so
    `packet.exhaustion` resolves into `energy.exhaustion`. `asdict` knows
    nothing about that routing, so the serialized form carried only the nested
    shape while every consumer read flat. Sixteen measured fields never arrived
    and every gate above read a hardcoded default: a turn measuring
    contradiction 1.0 composed a prompt saying Contradiction=0.40.

    These tests sit on that boundary specifically.
    """

    # Every flat key a composer gate reads. If one stops surviving to_dict(),
    # the directive it feeds goes quietly back to reading its default.
    COMPOSER_READS = (
        "exhaustion",
        "contradiction",
        "beta_index",
        "psi",
        "chi",
        "entropy",
        "valence",
        "voltage",
        "narrative_drag",
        "scope",
        "depth",
        "connectivity",
        "lq",
        "gamma",
        "sigma",
        "eta",
        "theta",
        "upsilon",
    )

    def test_every_field_a_gate_reads_survives_serialization(self):
        from physics.models import PhysicsPacket

        packet = PhysicsPacket.void_state()
        data = packet.to_dict()
        missing = [k for k in self.COMPOSER_READS if k not in data]
        self.assertEqual(
            missing,
            [],
            f"to_dict() dropped {missing}. Attribute access still works, so "
            "nothing else will fail; the directives gated on these will simply "
            "read their defaults forever.",
        )

    def test_the_nested_shape_is_preserved_alongside_the_flat_one(self):
        """Readers of `data["energy"]["exhaustion"]` must keep working."""
        from physics.models import PhysicsPacket

        packet = PhysicsPacket.void_state()
        packet.exhaustion = 0.77
        data = packet.to_dict()
        self.assertEqual(data["exhaustion"], 0.77)
        self.assertEqual(data["energy"]["exhaustion"], 0.77)

    def test_matter_is_not_flattened(self):
        """`matter` holds mutable containers and must stay nested.

        `CognitivePhase` writes every key of the serialized dict back onto a
        packet with `setattr`. Round-tripping `matter.counts` (a Counter)
        through that rewraps its keys one tuple deeper every turn, until the
        word tally driving the entire physics layer reads
        `Counter({((('play', 1), 1), 1): 1})` and measures nothing.
        """
        from physics.models import PhysicsPacket

        data = PhysicsPacket.void_state().to_dict()
        self.assertIn("matter", data)
        for mutable_field in ("counts", "clean_words", "vector", "raw_text"):
            self.assertNotIn(
                mutable_field,
                data,
                f"`matter.{mutable_field}` was projected flat. It will be fed "
                "back through setattr every turn and degrade.",
            )

    def test_a_measured_value_reaches_the_prompt_through_a_real_turn(self):
        """End to end, with no hand-built dict anywhere in the path."""
        from brain.composer import PromptComposer

        seen = {}
        original = PromptComposer.compose

        def spy(composer, state, *args, **kwargs):
            seen["physics"] = dict(state.get("physics") or {})
            return original(composer, state, *args, **kwargs)

        PromptComposer.compose = spy
        try:
            self.engine.process_turn("a sentence with some genuine weight to it")
        finally:
            PromptComposer.compose = original

        physics = seen.get("physics")
        self.assertIsNotNone(physics, "the composer was never reached")
        absent = [k for k in self.COMPOSER_READS if k not in physics]
        self.assertEqual(
            absent,
            [],
            f"A real turn handed the composer a physics dict missing {absent}.",
        )


class TestCoRegulationReachesThePrompt(PhysicsToPromptCase):
    """ROADMAP C3. The engine's model of the USER changing what it is told.

    `SharedLatticeDriver` infers `E_u`, how tired the person is, and `cycle.py`
    carries it onto the packet as `exhaustion`. It was computed correctly on
    every turn and never arrived: a lattice reading `E_u = 1.00` composed a
    prompt saying `Exhaustion=0.20`, the composer's hardcoded fallback. The
    whole co-regulation goal rested on a value that stopped at serialization.
    """

    def _compose_with_user_state(self, exhaustion: float, stamina: float) -> str:
        from brain.composer import PromptComposer

        lattice = self.engine.shared_lattice
        lattice.u.E_u, lattice.u.P_u = exhaustion, stamina
        seen = {}
        original = PromptComposer.compose

        def spy(composer, state, *args, **kwargs):
            out = original(composer, state, *args, **kwargs)
            seen["prompt"] = out
            return out

        PromptComposer.compose = spy
        try:
            self.engine.process_turn("what do you make of all this")
        finally:
            PromptComposer.compose = original
        return seen.get("prompt", "")

    def test_a_tired_user_shortens_the_engine(self):
        prompt = self._compose_with_user_state(exhaustion=0.95, stamina=5.0)
        self.assertIn(
            EXHAUSTION,
            prompt,
            "The lattice read the user as exhausted and the engine was not told.",
        )

    def test_a_fresh_user_does_not(self):
        prompt = self._compose_with_user_state(exhaustion=0.0, stamina=100.0)
        self.assertNotIn(EXHAUSTION, prompt)


class TestUserModelIsFirstClass(PhysicsToPromptCase):
    """ROADMAP C3: tracked, logged, and visible, the same as PhysicsPacket.

    The inference already existed and worked. What it lacked was every property
    that makes a model inspectable: it never survived a session, never appeared
    in any readout, and never filed a receipt. An engine that had spent an hour
    learning you were running low woke up assuming you were fresh.
    """

    def test_the_user_model_survives_a_save_and_reload(self):
        lattice = self.engine.shared_lattice
        lattice.u.E_u, lattice.u.P_u, lattice.u.T_u = 0.82, 17.0, 3.5

        payload = self.engine.chronos._gather_user_model()
        self.assertEqual(payload["E_u"], 0.82)
        self.assertEqual(payload["P_u"], 17.0)

        lattice.u.E_u, lattice.u.P_u, lattice.u.T_u = 0.0, 100.0, 0.0
        self.engine.chronos._restore_user_model(payload)
        self.assertEqual(lattice.u.E_u, 0.82)
        self.assertEqual(lattice.u.P_u, 17.0)
        self.assertEqual(lattice.u.T_u, 3.5)

    def test_restore_ignores_fields_the_model_does_not_have(self):
        """A save from an older build must not inject junk onto the dataclass."""
        lattice = self.engine.shared_lattice
        self.engine.chronos._restore_user_model({"E_u": 0.4, "not_a_field": 99})
        self.assertEqual(lattice.u.E_u, 0.4)
        self.assertFalse(hasattr(lattice.u, "not_a_field"))

    def test_status_reports_what_the_engine_believes_about_you(self):
        lattice = self.engine.shared_lattice
        lattice.u.E_u, lattice.u.P_u = 0.85, 12.0
        rendered = Prisma.strip(self.engine.cmd._render_user_model())
        self.assertIn("flagging", rendered)
        self.assertIn("0.85", rendered)

        lattice.u.E_u, lattice.u.P_u = 0.05, 95.0
        rendered = Prisma.strip(self.engine.cmd._render_user_model())
        self.assertIn("steady", rendered)

    def test_the_lattice_files_a_receipt(self):
        from receipts import CORE_SUBSYSTEMS, ReceiptLedger

        self.assertIn("lattice.infer_and_couple", CORE_SUBSYSTEMS)
        ledger = ReceiptLedger.get_instance()
        self.engine.process_turn("something worth saying about all of this")
        receipts = ledger.for_subsystem("lattice.infer_and_couple")
        self.assertTrue(receipts, "the lattice coupled and reported nothing")
        self.assertIn("E_u", receipts[-1].inputs)
        self.assertIn("phi", receipts[-1].inputs)


class TestTirednessMeansWithdrawal(unittest.TestCase):
    """ROADMAP C3: what the engine reads as "this person is running low".

    The original model was "typing is work": every word drained the user's
    stamina, and exhaustion rose only once that stamina hit a floor. So writing
    three searching paragraphs about something hard was the thing that made the
    engine read you as exhausted and start cutting its replies to three
    sentences, while "ok. sure. fine." restored you to full. That is backwards
    for an engine whose stated purpose is supporting the first person.

    Two signals now, deliberately separate. `P_u` is effort spent and long
    messages still drain it, because low `P_u` is what makes the engine offer to
    carry part of the load. `E_u` is disengagement, measured against this
    person's own recent baseline rather than an absolute length.
    """

    def setUp(self):
        from drivers.lattice import SharedLatticeDriver

        self.lattice = SharedLatticeDriver()

    def _learn(self, *messages):
        for message in messages:
            self.lattice._length_baseline.append(len(message.split()))
            self._remember(message)

    def _remember(self, message):
        self.lattice._recent_texts.append(message.strip())

    SEARCHING = (
        "I keep circling the same question about whether the thing I built does what I say",
        "there is a gap between the story I tell about this and what the code does",
        "maybe the honest version is that I wanted it to be true before I checked",
    )

    def test_searching_prose_reads_as_engagement(self):
        for message in self.SEARCHING:
            with self.subTest(message=message[:32]):
                self.assertLess(
                    self.lattice.read_disengagement(message),
                    0.3,
                    "Long searching prose was read as withdrawal. This is the "
                    "exact inversion C3 was about.",
                )
            self._learn(message)

    def test_going_blunt_after_writing_at_length_reads_as_withdrawal(self):
        self._learn(*self.SEARCHING)
        for message in ("fix it", "no", "wrong"):
            with self.subTest(message=message):
                self.assertGreater(self.lattice.read_disengagement(message), 0.6)

    def test_someone_who_always_writes_tersely_is_not_tired(self):
        """The reason this is a baseline and not an absolute length.

        A person whose messages are always four words has a style, not a mood.
        Reading them as permanently exhausted would make the engine useless to
        them.
        """
        self._learn("ok sounds good", "yes do that", "sure go ahead")
        self.assertLess(
            self.lattice.read_disengagement("right lets try"),
            0.3,
            "A consistently terse writer was mistaken for someone withdrawing.",
        )

    def test_repetition_reads_as_withdrawal_whatever_the_length(self):
        self._learn(*self.SEARCHING)
        self.assertGreater(
            self.lattice.read_disengagement("the same the same the same the same"),
            0.6,
        )

    def test_an_empty_message_is_maximal_withdrawal(self):
        self.assertEqual(self.lattice.read_disengagement("   "), 1.0)


class TestUserStaminaCeiling(unittest.TestCase):
    """`P_u` had no ceiling and climbed to 172 from a starting 100.

    Every other pool in the engine clamps. The ceiling is also the one number
    here that can honestly say "this conversation is costing you more than
    usual", so it moves with resonance and accumulated trauma rather than
    sitting flat.
    """

    def setUp(self):
        from drivers.lattice import SharedLatticeDriver

        self.lattice = SharedLatticeDriver()
        self.base = self.lattice._user_cfg("STAMINA_MAX", 100.0)

    def test_a_neutral_conversation_sits_at_the_configured_maximum(self):
        self.lattice.shared.phi = 0.5
        self.lattice.u.T_u = 0.0
        self.assertAlmostEqual(self.lattice.stamina_ceiling(), self.base, places=5)

    def test_resonance_buys_headroom(self):
        self.lattice.shared.phi, self.lattice.u.T_u = 1.0, 0.0
        self.assertGreater(self.lattice.stamina_ceiling(), self.base)

    def test_accumulated_trauma_spends_it(self):
        self.lattice.shared.phi, self.lattice.u.T_u = 0.5, 6.0
        self.assertLess(self.lattice.stamina_ceiling(), self.base)

    def test_the_ceiling_never_collapses(self):
        self.lattice.shared.phi, self.lattice.u.T_u = 0.0, 500.0
        floor = self.base * self.lattice._user_cfg("STAMINA_FLOOR_FRACTION", 0.5)
        self.assertGreaterEqual(self.lattice.stamina_ceiling(), floor)

    def test_the_ceiling_is_never_exceeded_however_long_the_rest(self):
        from physics.models import PhysicsPacket

        self.lattice.u.P_u = 50.0
        for _ in range(40):
            self.lattice.infer_and_couple(
                text="ok", sys_phys=PhysicsPacket.void_state(), input_phys={}, atp_pool=100.0
            )
            self.assertLessEqual(
                self.lattice.u.P_u,
                self.lattice.stamina_ceiling() + 1e-6,
                "User stamina climbed past its ceiling.",
            )


class TestTheUserModelIsSingular(unittest.TestCase):
    """There used to be two, and they disagreed.

    `SymbiosisManager` built its own `UserInferredState` and wrote exhaustion
    into it from a raw character count, while `SharedLatticeDriver` kept a
    separate one. Only the lattice's ever reached the prompt, so every reading
    Symbiosis made was computed and discarded, and it wrote `beth`, `phi` and
    `beta_index` onto the physics packet from a model nothing else agreed with.
    """

    def test_symbiosis_shares_the_lattice_model_once_attached(self):
        from archetypes.symbiosis import SymbiosisManager
        from drivers.lattice import SharedLatticeDriver
        from unittest.mock import MagicMock

        lattice = SharedLatticeDriver()
        symbiosis = SymbiosisManager(MagicMock())
        self.assertIsNot(symbiosis.u, lattice.u)

        symbiosis.attach_lattice(lattice)
        self.assertIs(symbiosis.u, lattice.u)
        self.assertIs(symbiosis.shared, lattice.shared)

        lattice.u.E_u = 0.66
        self.assertEqual(symbiosis.u.E_u, 0.66)
