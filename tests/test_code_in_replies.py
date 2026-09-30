"""Code in a reply is the answer, not prose to police (2026-09-29). The end-to-end run: the validator refused
any code block (it demanded <write_file>, which no prompt mentions, against the persona's "Markdown code blocks
when necessary"), and the gatekeeper, matching case-blind, read "# This pattern handles..." as a Title Case
header; "How do I fix the regex?" shipped "Let's take a moment with that."."""

from types import SimpleNamespace

from body.somatic_metrics import trim_to_sentence_cap
from engine.prose import close_gaps, mask_code
from physics.filters import TheGatekeeper
from tests.base import BoneTestCase

REGEX_ANSWER = (
    "The quotes around the user agent are optional, so make them optional in the pattern.\n\n"
    "```python\n"
    "# This pattern handles optional quotes around the user agent\n"
    'UA = re.compile(r\'"?(?P<ua>[^"]*)"?$\')\n'
    "```\n\n"
    "Lines without quotes now parse too."
)
JS_ANSWER = "Compare with strict equality.\n\n```js\nif (a === b) { return true; }\n```"


class CodeIsNotProse(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.validator = self.engine.cortex.validator
        self.gk = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)

    def validate(self, text, mode="TECHNICAL"):
        return self.validator.validate(text, {"meta": {"active_mode": mode}})

    def test_a_code_block_is_an_answer(self):
        result = self.validate(REGEX_ANSWER)
        self.assertTrue(result["valid"], result.get("feedback_instruction"))
        self.assertIn("(?P<ua>", result["content"])

    def test_a_comment_in_code_is_not_a_header(self):
        self.assertIsNone(self.gk._find_crime(REGEX_ANSWER, "TECHNICAL"))

    def test_a_title_case_header_in_prose_still_is(self):
        crime = self.gk._find_crime("# Parsing Logic\n\nSplit on spaces.", "TECHNICAL")
        self.assertEqual(crime and crime["name"], "TITLE_CASE_HEADERS")
        self.assertIsNone(self.gk._find_crime("# parsing logic here\n\nSplit on spaces.", "TECHNICAL"))

    def test_code_that_looks_like_a_scaffold_leak_is_kept(self):
        self.assertIsNone(self.gk._find_crime(JS_ANSWER, "TECHNICAL"))
        self.assertIsNotNone(self.gk._find_crime("=== SYSTEM ===\nHello.", "TECHNICAL"))
        result = self.validate("Set the limit once.\n\n```python\nMAX = 10\n```")
        self.assertIn("MAX = 10", result["content"])

    def test_asterisks_and_question_marks_in_code_are_not_prose(self):
        # A live probe after the first fix: `[^"]*"|[^ ]+` read as a stage direction, twice.
        budget = SimpleNamespace(closing_question_allowed=False, forbid_body_narration=True, sentence_cap=0)
        reply = 'Match either form: `(?:"[^"]*"|[^ ]+)`\n\n```python\nUA = re.compile(r\'"?([^"]*)"?\')\n```'
        result = self.validator.validate(reply, {"meta": {"active_mode": "TECHNICAL"}, "somatic_budget": budget})
        self.assertTrue(result["valid"], result.get("feedback_instruction"))
        acted = self.validator.validate("*sighs* Use a Counter.", {"meta": {"active_mode": "TECHNICAL"}, "somatic_budget": budget})
        self.assertFalse(acted["valid"])

    def test_a_repair_keeps_the_rest_of_the_reply(self):
        result = self.validate("While that works, a Counter is simpler.\n\nIt counts in one pass.", "CONVERSATION")
        self.assertEqual(result["content"], "A Counter is simpler.\n\nIt counts in one pass.")

    def test_a_lifted_file_leaves_no_gap(self):
        reply = 'Here it is.\n\n<write_file path="a.py">x = 1</write_file>\n\n\nIt is frozen, so nothing changes it.'
        result = self.validate(reply)
        self.assertNotIn("\n\n\n", result["content"])
        self.assertTrue(any(l.startswith("[SUBSTRATE_QUEUE] a.py") for l in result["meta_logs"]))


class Helpers(BoneTestCase):
    def test_masking_keeps_length_and_lines(self):
        masked = mask_code(REGEX_ANSWER)
        self.assertEqual(len(masked), len(REGEX_ANSWER))
        self.assertEqual(masked.count("\n"), REGEX_ANSWER.count("\n"))
        self.assertNotIn("pattern handles", masked)

    def test_code_keeps_its_blank_lines(self):
        code = "```python\ndef a():\n    pass\n\n\ndef b():\n    pass\n```"
        self.assertIn("\n\n\n", close_gaps("Two functions.\n\n\n\n" + code))
        self.assertTrue(close_gaps("Two functions.\n\n\n\n" + code).startswith("Two functions.\n\n```"))

    def test_the_sentence_cap_never_cuts_inside_code(self):
        reply = "Use a Counter.\n\n```python\nfrom collections import Counter\nc = Counter(paths)\nc.most_common(10)\n```\n\nThat is all. More here. And more."
        cut = trim_to_sentence_cap(reply, 2)
        self.assertEqual(cut.count("```"), 2)
        self.assertIn("c.most_common(10)", cut)
        self.assertNotIn("More here", cut)
