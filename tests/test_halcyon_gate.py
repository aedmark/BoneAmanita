"""The Halcyon gate as BoneAmanita runs it: one NOMINATE line per reply, adjudicated from the model's
own draft, committed to the SQLite store, never shown to the person."""

import copy
from unittest.mock import MagicMock, patch

from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

PROSE = "The river runs east past the mill."
REMEMBER = "NOMINATE what=self/memory/river verb=remember args=key:river; value:runs east past the mill"


class TestHalcyonGate(BoneTestCase):
    def turn(self, draft, message="Tell me about the river."):
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=draft)
        return self.engine.process_turn(message)

    def gate_receipts(self):
        return ReceiptLedger.get_instance().for_subsystem("halcyon.gate")

    def test_gate_initialization(self):
        engine = self.engine
        for attr in ("store", "boundary", "gate_tools", "gate_invariants"):
            self.assertTrue(hasattr(engine, attr), attr)
        seq, state = engine.store.state()
        self.assertEqual(seq, 0)
        self.assertIn("world", state)
        self.assertIn("self", state)

    def test_the_gate_accepts_a_well_formed_nomination(self):
        from engine.gate.kernel import Gate

        seq, state = self.engine.store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        receipt = gate.adjudicate("This is my thought process.\nNOMINATE what=world/nodes verb=create args=name:TestNode;type:concept")
        self.assertEqual(receipt["decision"], "ACCEPT")
        self.engine.store.commit_cycle("test-trace", gate.state, seq, receipt, "raw")
        seq2, state2 = self.engine.store.state()
        self.assertEqual(seq2, seq + 1)
        self.assertIn("entity:testnode", state2["world"]["nodes"])

    def test_the_prompt_carries_the_declared_grammar(self):
        # It read a meta key nothing set, so the model saw "args=..." and never the real arg names.
        self.turn(PROSE)
        prompt = self.engine.cortex.llm.generate.call_args[0][0]
        self.assertIn("verb=relate (writes world/) args=subject:<str>; relation:<str>; object:<str>", prompt)
        self.assertIn("verb=remember (writes self/memory/) args=key:<str>; value:<str>", prompt)
        self.assertNotIn("args=...", prompt)

    def test_the_gate_block_comes_before_the_person_and_gives_the_reason(self):
        # After the reply cue, the model read it as part of its own turn.
        self.turn(PROSE)
        prompt = self.engine.cortex.llm.generate.call_args[0][0]
        self.assertLess(prompt.index("=== HALCYON GATE GOVERNANCE ==="), prompt.index("=== PARTNER INPUT ==="))
        self.assertIn("You have a memory that lasts between sessions", prompt)

    def test_the_limits_come_from_the_boundary(self):
        # build_invariants was handed the limits dict and looked for "limits" inside it: the caps fell to 10000.
        breach = self.engine.gate_invariants["self_within_budget"]
        state = {"self": {"memory": {f"k{i}": "v" for i in range(501)}}, "world": {}}
        self.assertIsNotNone(breach(state))
        state["self"]["memory"].pop("k0")
        self.assertIsNone(breach(state))

    def test_a_nomination_never_reaches_the_person(self):
        result = self.turn(f"{PROSE}\n{REMEMBER}")
        self.assertIn(PROSE, result.get("ui", ""))
        self.assertNotIn("NOMINATE", result.get("ui", ""))
        self.assertNotIn("NOMINATE", self.engine.cortex.dialogue_buffer[-1])

    def test_the_gate_commits_what_the_draft_nominated(self):
        self.turn(f"{PROSE}\n{REMEMBER}")
        _, state = self.engine.store.state()
        self.assertEqual(state["self"]["memory"].get("river"), "runs east past the mill")
        receipt = self.gate_receipts()[-1]
        self.assertEqual((receipt.effect, receipt.result_count), ("ACCEPT", 1))

    def test_the_gate_reads_the_draft_not_the_screen(self):
        # It adjudicated the rendered UI, so the "verbatim rationale" was log bullets.
        from engine.gate.kernel import Gate

        seen = []
        real = Gate.adjudicate

        def spy(gate, text):
            seen.append(text)
            return real(gate, text)

        with patch.object(Gate, "adjudicate", spy):
            self.turn(f"{PROSE}\n{REMEMBER}")
        self.assertEqual(seen, [f"{PROSE}\n{REMEMBER}"])

    def test_a_turn_without_a_nomination_is_receipted_as_noop(self):
        self.turn(PROSE)
        receipt = self.gate_receipts()[-1]
        self.assertEqual((receipt.effect, receipt.result_count), ("NOOP", 0))
        self.assertEqual(self.engine.store.state()[0], 0)

    def test_an_out_of_scope_nomination_is_denied_and_nothing_changes(self):
        self.turn(f"{PROSE}\nNOMINATE what=self/identity verb=remember args=key:name; value:Iris")
        self.assertEqual(self.gate_receipts()[-1].effect, "DENY")
        self.assertEqual(self.engine.store.state()[0], 0)

    def test_the_store_does_not_replace_the_engines_own_state(self):
        # The turn loaded world and self into world_state and mind_state, which the engine uses for its own data.
        self.turn(f"{PROSE}\n{REMEMBER}")
        captured = []
        sim = self.engine.orchestrator.simulator
        real = sim.run_simulation

        def spy(ctx):
            captured.append((dict(ctx.halcyon_state), dict(ctx.mind_state), dict(ctx.world_state)))
            return real(ctx)

        with patch.object(sim, "run_simulation", spy):
            self.turn(PROSE, "And the mill?")
        halcyon, mind, world = captured[0]
        self.assertEqual(halcyon["self"]["memory"]["river"], "runs east past the mill")
        self.assertNotIn("memory", mind)
        self.assertNotIn("nodes", world)


class TheAuditTrail(BoneTestCase):
    """commit_cycle updated canonical state only; the receipts, proposals, gate decisions and mutations
    tables stayed empty, so nothing the gate decided was kept."""

    turn = TestHalcyonGate.turn

    def test_an_accepted_nomination_leaves_its_whole_trail(self):
        self.turn(f"{PROSE}\n{REMEMBER}")
        store = self.engine.store
        (receipt,) = store.audit("receipts")
        self.assertEqual((receipt["decision"], receipt["outcome"]), ("ACCEPT", "committed"))
        self.assertEqual(receipt["rationale"], f"{PROSE}\n{REMEMBER}")
        self.assertTrue(receipt["boundary_hash"].startswith("sha256:"))
        (proposal,) = store.audit("proposals")
        self.assertEqual((proposal["verb"], proposal["parse_status"]), ("remember", "valid"))
        (decision,) = store.audit("gate_decisions")
        self.assertEqual((decision["admission"], decision["persistence"]), ("admitted", "committed"))
        (mutation,) = store.audit("mutations")
        self.assertEqual((mutation["state_sequence_before"], mutation["state_sequence_after"]), (0, 1))
        roles = sorted(m["role"] for m in store.audit("messages"))
        self.assertEqual(roles, ["assistant", "user"])
        assistant = next(m for m in store.audit("messages") if m["role"] == "assistant")
        self.assertNotIn("NOMINATE", assistant["display_content"])
        db = store.connect()
        try:
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            db.close()

    def test_a_plain_turn_is_receipted_without_a_proposal_or_mutation(self):
        self.turn(PROSE)
        store = self.engine.store
        self.assertEqual([r["decision"] for r in store.audit("receipts")], ["NOOP"])
        self.assertEqual(store.audit("proposals"), [])
        self.assertEqual(store.audit("mutations"), [])

    def test_a_malformed_nomination_is_kept_in_the_audit_and_off_the_screen(self):
        result = self.turn(f"{PROSE}\nNOMINATE remember that the river runs east")
        self.assertNotIn("NOMINATE", result.get("ui", ""))
        (proposal,) = self.engine.store.audit("proposals")
        self.assertEqual(proposal["parse_status"], "malformed")

    def test_turns_of_one_session_share_a_conversation(self):
        self.turn(PROSE)
        self.turn(PROSE, "And the mill?")
        turns = self.engine.store.audit("turns")
        self.assertEqual(len({t["conversation_id"] for t in turns}), 1)
        self.assertEqual(sorted(t["ordinal"] for t in turns), [1, 2])


class DenialsShowOnlyWhereAsked(BoneTestCase):
    """Gordon: the player doesn't need to see a denial unless in TECHNICAL mode or on the DEEP HUD."""

    turn = TestHalcyonGate.turn
    OUT_OF_SCOPE = f"{PROSE}\nNOMINATE what=self/identity verb=remember args=key:name; value:Iris"

    def test_hidden_in_conversation(self):
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.ui_mode = "WARM"
        self.assertNotIn("the gate refused", self.turn(self.OUT_OF_SCOPE).get("ui", ""))
        self.assertEqual(self.engine.store.audit("receipts")[0]["decision"], "DENY")

    def test_shown_in_technical_and_on_the_deep_hud(self):
        for mode, depth in (("TECHNICAL", "WARM"), ("CONVERSATION", "DEEP")):
            with self.subTest(mode=mode, depth=depth):
                self.engine.cortex.active_mode = mode
                self.engine.ui_mode = depth
                self.assertIn("the gate refused remember self/identity: 'self/identity' is outside the declared state scope",
                              self.turn(self.OUT_OF_SCOPE).get("ui", ""))


class TheModelGetsItsMemoriesBack(BoneTestCase):
    """What the model keeps through the gate is handed back in the next prompt."""

    turn = TestHalcyonGate.turn

    def prompt(self):
        return self.engine.cortex.llm.generate.call_args[0][0]

    def test_a_kept_memory_comes_back_next_turn(self):
        self.turn(f"{PROSE}\n{REMEMBER}")
        self.turn("The mill is quiet.", "Which way does the river run?")
        self.assertIn("=== WHAT YOU REMEMBER ===", self.prompt())
        self.assertIn("- river: runs east past the mill", self.prompt())
        receipt = ReceiptLedger.get_instance().for_subsystem("halcyon.recall")[-1]
        self.assertEqual(receipt.result_count, 1)

    def test_an_old_memory_says_when_it_was_kept(self):
        # A kept state ("barely sleeping this week") read a month on as current.
        self.turn(f"{PROSE}\n{REMEMBER}")
        self.turn("The mill is quiet.", "Which way does the river run?")
        self.assertIn("- river: runs east past the mill\n", self.prompt())
        db = self.engine.store.connect()
        try:
            db.execute("UPDATE memory_meta SET kept_at = kept_at - 21 * 86400 WHERE key='river'")
        finally:
            db.close()
        self.turn("The mill is quiet.", "Which way does the river run?")
        self.assertIn("- river: runs east past the mill (kept 3 weeks ago)", self.prompt())

    def test_ages_read_plainly(self):
        from brain.composer import PromptComposer

        now = 1_000_000_000
        ago = lambda days: PromptComposer._kept_ago(now - days * 86400, now)
        self.assertEqual([ago(0.5), ago(1.5), ago(3), ago(7), ago(15), ago(40), ago(800)],
                         ["", " (kept yesterday)", " (kept 3 days ago)", " (kept a week ago)", " (kept 2 weeks ago)",
                          " (kept a month ago)", " (kept 2 years ago)"])
        self.assertEqual(PromptComposer._kept_ago(None, now), "")

    def test_the_keeper_is_asked_how_they_are_doing(self):
        from engine.gate.keeper import PROMPT

        # Six live runs never kept "haven't slept in a week"; asked, it kept 12 of 12 states.
        self.assertIn("how they are doing lately", PROMPT)
        self.assertIn("sleep = barely sleeping this week", PROMPT)

    def test_a_new_fact_of_the_same_kind_gets_its_own_name(self):
        from engine.gate.keeper import PROMPT

        # CREATIVE's plot_point was overwritten five times; live, new facts got their own name 6 of 12 times,
        # 12 of 12 with this rule, and changes still reused theirs 9 of 9.
        self.assertIn("A new fact of the same kind is not a change", PROMPT)

    def test_every_mode_knows_it_remembers(self):
        # A bare model has no memory; this one does, and two of three live answers denied it.
        for mode in ("ADVENTURE", "CONVERSATION", "CREATIVE", "TECHNICAL"):
            with self.subTest(mode=mode):
                self.engine.cortex.active_mode = mode
                self.turn(PROSE)
                self.assertIn("MEMORY: You have a working memory.", self.prompt())
                self.assertIn("Never say you have no memory", self.prompt())

    def test_adventure_answers_a_question_before_the_room(self):
        # The probe: ADVENTURE had the key's hiding place in its prompt and still only described the room.
        self.assertEqual(self.engine.boot_mode, "ADVENTURE")
        self.turn(f"{PROSE}\n{REMEMBER}")
        self.turn("The mill is quiet.", "Where does the river run?")
        self.assertIn("7. QUESTIONS: If the user asks a question", self.prompt())
        self.assertIn("answer it plainly first", self.prompt())

    def test_nothing_kept_means_no_block(self):
        self.turn(PROSE)
        self.assertNotIn("=== WHAT YOU REMEMBER ===", self.prompt())
        receipt = ReceiptLedger.get_instance().for_subsystem("halcyon.recall")[-1]
        self.assertEqual((receipt.result_count, receipt.detail), (0, "nothing kept yet"))

    def test_the_turn_decides_what_comes_back_first(self):
        from engine.gate.recall import recall

        # The lantern is the oldest memory, so only relevance can put it first.
        memory = {"lantern": "the brass lantern hangs by the north door"}
        memory.update({f"note{i}": f"an ordinary detail number {i}" for i in range(20)})
        state = {"self": {"memory": memory}, "world": {"nodes": {}, "edges": [], "constraints": []}}
        found = recall(state, "Where did I leave the lantern?", max_memories=3)
        self.assertEqual(found["memories"][0][0], "lantern")
        self.assertEqual(len(found["memories"]), 3)
        self.assertEqual(found["held"]["memories"], 21)

    def test_world_facts_about_what_the_turn_names_come_first(self):
        from engine.gate.kernel import Gate

        _, state = self.engine.store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        for line in ("NOMINATE what=world/edge verb=relate args=subject:Riverhold; relation:sits on; object:the Long River",
                     "NOMINATE what=world/edge verb=relate args=subject:Ashford; relation:trades with; object:the coast"):
            gate.adjudicate(f"Noted.\n{line}")
        from engine.gate.recall import recall

        found = recall(gate.state, "Tell me about Riverhold.", max_facts=1)
        self.assertEqual(found["facts"], ["Riverhold sits on the Long River"])


class ConceptEmbedder:
    """A stand-in with a real notion of meaning: each dimension is a concept, scored by its words."""

    CONCEPTS = (
        {"lantern", "lamp", "light", "dark", "see"},
        {"river", "water", "stream", "bridge"},
        {"bread", "oven", "hungry", "eat"},
    )

    def __init__(self, backend="fake", model="concepts"):
        self.backend, self.model, self.degraded, self.batches = backend, model, False, []

    def embed_batch(self, texts):
        self.batches.append(list(texts))
        words = [set(str(t).lower().replace(":", " ").replace("?", " ").split()) for t in texts]
        return [[float(len(w & c)) for c in self.CONCEPTS] + [0.01] for w in words]


class MemoriesRankedByMeaning(BoneTestCase):
    """Memory phase 2: memories come back by what they mean, embedded once each; word overlap stays the
    fallback when the embedder is on its hash fallback."""

    MEMORY = {
        "lantern": "the brass lamp hangs by the north door",
        **{f"note{i}": f"an ordinary detail number {i}" for i in range(6)},
    }
    ASK = "Where can I find something to see by?"

    def state(self, memory=None):
        return {"self": {"memory": dict(memory or self.MEMORY)}, "world": {"nodes": {}, "edges": [], "constraints": []}}

    def test_meaning_finds_what_shares_no_words(self):
        from engine.gate.recall import meaning_scores, recall

        state = self.state()
        by_words = recall(state, self.ASK, max_memories=1)
        self.assertNotEqual(by_words["memories"][0][0], "lantern")
        scores = meaning_scores(state, self.ASK, self.engine.store, ConceptEmbedder())
        by_meaning = recall(state, self.ASK, max_memories=1, scores=scores)
        self.assertEqual((by_meaning["memories"][0][0], by_meaning["ranked_by"]), ("lantern", "meaning"))

    def test_each_memory_is_embedded_once(self):
        from engine.gate.recall import meaning_scores

        embedder, store = ConceptEmbedder(), self.engine.store
        meaning_scores(self.state(), self.ASK, store, embedder)
        self.assertEqual(len(embedder.batches[-1]), 1 + len(self.MEMORY))
        meaning_scores(self.state(), "And the river?", store, embedder)
        self.assertEqual(embedder.batches[-1], ["And the river?"])

        changed = dict(self.MEMORY, lantern="the lamp went out")
        changed.pop("note0")
        meaning_scores(self.state(changed), self.ASK, store, embedder)
        self.assertEqual(embedder.batches[-1], [self.ASK, "lantern: the lamp went out"])
        self.assertNotIn("note0", store.memory_vectors())

    def test_a_new_embedding_model_re_embeds(self):
        from engine.gate.recall import meaning_scores

        meaning_scores(self.state(), self.ASK, self.engine.store, ConceptEmbedder())
        other = ConceptEmbedder(model="concepts-v2")
        meaning_scores(self.state(), self.ASK, self.engine.store, other)
        self.assertEqual(len(other.batches[-1]), 1 + len(self.MEMORY))

    def test_hash_vectors_never_rank(self):
        from engine.gate.recall import meaning_scores

        degraded = ConceptEmbedder()
        degraded.degraded = True
        self.assertIsNone(meaning_scores(self.state(), self.ASK, self.engine.store, degraded))
        self.assertEqual(degraded.batches, [])

        failing = ConceptEmbedder()
        failing.embed_batch = lambda texts: (setattr(failing, "degraded", True), [[0.0]] * len(texts))[1]
        self.assertIsNone(meaning_scores(self.state(), self.ASK, self.engine.store, failing))
        self.assertEqual(self.engine.store.memory_vectors(), {})

    def remember_and_ask(self, embedder):
        for key, value in self.MEMORY.items():
            TestHalcyonGate.turn(self, f"Noted.\nNOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}", "Noted?")
        with patch.object(type(self.engine.cortex), "_recall_embedder", return_value=embedder):
            TestHalcyonGate.turn(self, "Let me think.", self.ASK)
        prompt = self.engine.cortex.llm.generate.call_args[0][0]
        return prompt, ReceiptLedger.get_instance().for_subsystem("halcyon.recall")[-1]

    def test_a_turn_hands_back_memories_by_meaning(self):
        prompt, receipt = self.remember_and_ask(ConceptEmbedder())
        # The lantern is the oldest memory and shares no word with the question, so only meaning puts it first.
        block = prompt.split("=== WHAT YOU REMEMBER ===", 1)[1]
        first = next(line for line in block.splitlines() if line.startswith("- "))
        self.assertEqual(first, "- lantern: the brass lamp hangs by the north door")
        self.assertEqual((receipt.inputs["ranked_by"], receipt.degraded), ("meaning", False))

    def test_a_degraded_embedder_falls_back_to_words_and_says_so(self):
        degraded = ConceptEmbedder()
        degraded.degraded = True
        _, receipt = self.remember_and_ask(degraded)
        self.assertEqual((receipt.inputs["ranked_by"], receipt.degraded), ("words", True))
        self.assertIn("hash fallback", receipt.detail)



class TheMemoryKeeper(BoneTestCase):
    """Memory phase 3: the chat model almost never wrote its own NOMINATE line, so after the reply a
    short keeper call says what the person told it worth keeping, and the engine nominates that."""

    SISTER = "By the way, my sister's name is Odalys."

    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"  # a sister's name is the person's, not the story's
        self.keeper_prompts = []

    def respond(self, reply="That's a lovely name.", keeps="sister_name = Odalys"):
        def generate(prompt, *a, **k):
            if prompt.startswith("You keep the memory"):
                self.keeper_prompts.append(prompt)
                if isinstance(keeps, Exception):
                    raise keeps
                return keeps
            return reply

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def receipt(self):
        return ReceiptLedger.get_instance().for_subsystem("halcyon.keeper")[-1]

    def test_what_the_person_says_is_kept_through_the_gate(self):
        self.respond()
        result = self.engine.process_turn(self.SISTER)
        self.assertEqual(self.engine.store.state()[1]["self"]["memory"].get("sister_name"), "Odalys")
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("halcyon.gate")[-1].effect, "ACCEPT")
        self.assertEqual(self.receipt().effect, "PROPOSED")
        self.assertNotIn("NOMINATE", result.get("ui", ""))
        (proposal,) = self.engine.store.audit("proposals")
        self.assertIn("self/memory/sister_name", proposal["raw_line"])

    def test_small_talk_keeps_nothing(self):
        self.respond(keeps="NONE")
        self.engine.process_turn("Anyway, work has been a lot lately.")
        self.assertEqual(self.engine.store.state()[0], 0)
        self.assertEqual((self.receipt().effect, self.receipt().result_count), ("NONE", 0))

    def test_a_draft_that_nominates_itself_still_gets_the_keeper(self):
        """The keeper was skipped when the draft nominated; what the person said that turn was lost (2026-10-05)."""
        self.respond(reply=f"{PROSE}\n{REMEMBER}")
        self.engine.process_turn(self.SISTER)
        self.assertEqual(len(self.keeper_prompts), 1)
        self.assertEqual(self.engine.store.state()[1]["self"]["memory"],
                         {"river": "runs east past the mill", "sister_name": "Odalys"})

    def test_it_sees_what_is_already_kept(self):
        self.respond()
        self.engine.process_turn(self.SISTER)
        self.respond(keeps="NONE")
        self.engine.process_turn("She's staying for a week.")
        self.assertIn("\nsister_name = Odalys\n", self.keeper_prompts[-1])
        self.assertIn('The person\'s latest message, the only one to keep or update from: "She\'s staying for a week."',
                      self.keeper_prompts[-1])

        # The draft is still adjudicated and audited.
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("halcyon.gate")[-1].effect, "NOOP")

    def test_the_usage_of_the_reply_is_kept(self):
        from engine.gate.keeper import MemoryKeeper

        # The census reads the reply's token usage after the turn; the keeper call must not replace it.
        llm = MagicMock(last_usage={"prompt_tokens": 1234})
        llm.generate = MagicMock(side_effect=lambda *a: setattr(llm, "last_usage", {"prompt_tokens": 90}) or "NONE")
        keeper = MemoryKeeper(llm)
        keeper.propose(self.SISTER, {})
        self.assertEqual(keeper.llm.last_usage, {"prompt_tokens": 1234})

    def test_the_line_is_always_well_formed(self):
        from engine.gate.keeper import MemoryKeeper

        line = MemoryKeeper(None).line_for
        self.assertEqual(line("sister_name = Odalys"),
                         "NOMINATE what=self/memory/sister_name verb=remember args=key:sister_name; value:Odalys")
        self.assertEqual(line("- `Dog Name` = Brisket; hates the vacuum"),
                         "NOMINATE what=self/memory/dog_name verb=remember args=key:dog_name; value:Brisket, hates the vacuum")
        # The probe's second turn: with a memory shown, the model answered in the template's own words.
        self.assertEqual(line("key = dog_name: Brisket (hates vacuum)"),
                         "NOMINATE what=self/memory/dog_name verb=remember args=key:dog_name; value:Brisket (hates vacuum)")
        for answer in ("NONE", "None.", "NONE of this = worth keeping", "I think the sister matters.", "", "= no key",
                       "key = Brisket", "key = name: Brisket"):
            self.assertIsNone(line(answer), answer)

    def test_the_keeper_is_on_unless_configured_off(self):
        from main import BoneAmanita

        config = {k: v for k, v in self.test_config.items() if k != "CORTEX"}
        engine = BoneAmanita(config=config)
        self.addCleanup(self._shutdown_engine, engine)
        self.assertTrue(engine.memory_keeper.enabled)
        off = BoneAmanita(config=self.test_config)
        self.addCleanup(self._shutdown_engine, off)
        self.assertFalse(off.memory_keeper.enabled)


class AHeldTurnHasNoDraft(BoneTestCase):
    """The probe found a Stage Manager hold left the previous turn's draft in last_model_raw, so the gate
    adjudicated and audited it again as this turn's reply."""

    def hold(self, message):
        from archetypes.stage import HOLD, StageManager, Tension, Verdict

        verdict = Verdict(HOLD, "THE STAGE MANAGER", "held for the test", Tension(("MOIRA", "CASSANDRA")), gate="ATP_FLOOR")
        with patch.object(StageManager, "negotiate", return_value=verdict):
            return self.engine.process_turn(message)

    def gate_receipts(self):
        return ReceiptLedger.get_instance().for_subsystem("halcyon.gate")

    def test_the_previous_draft_is_not_adjudicated_again(self):
        TestHalcyonGate.turn(self, f"{PROSE}\n{REMEMBER}")
        before = len(self.gate_receipts())
        result = self.hold("say something about all this")
        self.assertEqual(result.get("type"), "SILENCE")
        self.assertEqual(len(self.gate_receipts()), before)
        self.assertEqual(len(self.engine.store.audit("turns")), 1)

    def test_what_the_person_said_is_still_kept(self):
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.active_mode = "TECHNICAL"
        self.engine.cortex.llm.generate = MagicMock(return_value="deploy_window = Thursdays at 2pm")
        self.hold("Our deploy window is Thursdays at 2pm.")
        self.assertEqual(self.engine.store.state()[1]["self"]["memory"].get("deploy_window"), "Thursdays at 2pm")
        (receipt,) = self.engine.store.audit("receipts")
        self.assertTrue(receipt["rationale"].startswith("(No reply this turn: the Stage Manager held the floor."))
        assistant = next(m for m in self.engine.store.audit("messages") if m["role"] == "assistant")
        self.assertEqual(assistant["display_content"], "")

    def test_a_held_turn_with_nothing_to_keep_records_nothing(self):
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.llm.generate = MagicMock(return_value="NONE")
        self.hold("hm")
        self.assertEqual(self.gate_receipts(), [])
        self.assertEqual(self.engine.store.audit("turns"), [])
