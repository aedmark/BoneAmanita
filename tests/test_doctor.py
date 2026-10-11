"""tests/test_doctor.py

The doctor names what is wrong with a machine and the one command that fixes it, without a paid request, and the first-run
wizard lists the models Ollama already has. Offline: every server is a function.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine import doctor
from engine.doctor import FAIL, INFO, OK, WARN, run_doctor


def by_name(checks):
    return {c.name: c for c in checks}


def tags(*names):
    return lambda url, timeout=5.0: {"models": [{"name": n} for n in names]}


def answers(text="ok"):
    def post(url, payload, headers=None, timeout=5.0):
        if "embeddings" in url:
            return {"data": [{"embedding": [0.1] * 768}]}
        return {"message": {"content": text}}

    return post


def down(url, timeout=5.0):
    raise ConnectionError("refused")


def never(*a, **k):
    raise AssertionError("a paid or unexpected request was made")


def post_down(url, payload, headers=None, timeout=5.0):
    raise ConnectionError("refused")


def embeddings_only(url, payload, headers=None, timeout=5.0):
    if "embeddings" not in url:
        raise AssertionError(f"a chat request was made to {url}")
    return {"data": [{"embedding": [0.1] * 768}]}


class DoctorCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = {k: v for k, v in os.environ.items() if not k.startswith("BONE_")}
        patcher = patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_it(self, config=None, get=None, post=None, find_spec=None):
        kwargs = {"find_spec": find_spec} if find_spec else {}
        return by_name(run_doctor(config if config is not None else {"provider": "ollama", "model": "gemma4:12b"},
                                  self.root, get or tags("gemma4:12b", "gemma4:e4b", "nomic-embed-text"), post or answers(), **kwargs))


class TheChatModel(DoctorCase):
    def test_a_ready_machine_has_nothing_to_fix(self):
        got = self.run_it()
        self.assertEqual(got["chat server"].status, OK)
        self.assertEqual(got["chat model"].status, OK)
        self.assertEqual(got["critic model"].status, OK)
        self.assertEqual(got["embeddings"].status, OK)

    def test_ollama_not_running_says_how_to_start_it(self):
        got = self.run_it(get=down)
        self.assertEqual(got["chat server"].status, FAIL)
        self.assertIn("ollama serve", got["chat server"].fix)

    def test_a_model_not_pulled_names_the_pull(self):
        got = self.run_it(get=tags("llama3", "nomic-embed-text"))
        self.assertEqual(got["chat model"].status, FAIL)
        self.assertEqual(got["chat model"].fix, "ollama pull gemma4:12b")

    def test_a_model_that_answers_nothing_is_a_warning(self):
        self.assertEqual(self.run_it(post=answers(""))["chat model"].status, WARN)

    def test_a_missing_critic_is_a_warning_with_the_pull(self):
        got = self.run_it(get=tags("gemma4:12b", "nomic-embed-text"))
        self.assertEqual(got["critic model"].status, WARN)
        self.assertIn("ollama pull gemma4:e4b", got["critic model"].fix)

    def test_latest_tag_counts_as_pulled(self):
        got = self.run_it({"provider": "ollama", "model": "mistral-nemo"}, get=tags("mistral-nemo:latest", "gemma4:e4b", "nomic-embed-text"))
        self.assertEqual(got["chat model"].status, OK)

    def test_cloud_without_a_key_fails_and_with_one_makes_no_request(self):
        self.assertEqual(self.run_it({"provider": "anthropic", "model": "m"}, post=embeddings_only)["chat model"].status, FAIL)
        got = self.run_it({"provider": "anthropic", "model": "m", "api_key": "sk-test"}, post=embeddings_only)
        self.assertEqual(got["chat model"].status, OK)
        self.assertNotIn("sk-test", str(got))

    def test_mock_needs_no_model_and_no_embedding_probe(self):
        got = self.run_it({"provider": "mock", "model": "simulation"}, get=never, post=never)
        self.assertEqual(got["chat model"].status, INFO)
        self.assertNotIn("embeddings", got)


class TheEmbeddings(DoctorCase):
    def test_a_missing_embedding_model_says_what_it_costs_and_the_fix(self):
        got = self.run_it(get=tags("gemma4:12b", "gemma4:e4b"))
        self.assertEqual(got["embeddings"].status, WARN)
        self.assertIn("hash coordinates", got["embeddings"].detail)
        self.assertEqual(got["embeddings"].fix, "ollama pull nomic-embed-text")

    def test_no_answer_from_the_embedding_server_is_a_warning(self):
        def post(url, payload, headers=None, timeout=5.0):
            if "embeddings" in url:
                raise ConnectionError("refused")
            return {"message": {"content": "ok"}}

        self.assertEqual(self.run_it(post=post)["embeddings"].status, WARN)

    def test_the_hash_backend_chosen_on_purpose_is_a_fact_not_a_warning(self):
        with patch.dict(os.environ, {"BONE_EMBED_BACKEND": "hash"}):
            self.assertEqual(self.run_it()["embeddings"].status, INFO)


class ThePackagesFoldersAndConfig(DoctorCase):
    def test_a_missing_required_package_fails_and_a_missing_optional_one_warns(self):
        got = self.run_it(find_spec=lambda name: None if name in ("requests", "ordvec") else object())
        self.assertEqual(got["package requests"].status, FAIL)
        self.assertEqual(got["package ordvec"].status, WARN)
        self.assertEqual(got["package numpy"].status, OK)

    def test_a_corrupt_config_fails_with_the_way_out(self):
        (self.root / "config.json").write_text("{not json", encoding="utf-8")
        got = self.run_it()
        self.assertEqual(got["config.json"].status, FAIL)
        self.assertIn("set up again", got["config.json"].fix)

    def test_no_config_is_information_not_a_failure(self):
        self.assertEqual(self.run_it()["config.json"].status, INFO)


class TheReport(DoctorCase):
    def test_every_fix_is_printed_and_the_verdict_counts_failures(self):
        text = doctor.render(run_doctor({"provider": "ollama", "model": "gemma4:12b"}, self.root, down, post_down))
        self.assertIn("fix: ollama serve", text)
        self.assertIn("Not ready: 1 thing(s) to fix first.", text)

    def test_a_clean_report_says_ready(self):
        checks = [c for c in run_doctor({"provider": "ollama", "model": "gemma4:12b"}, self.root,
                                        tags("gemma4:12b", "gemma4:e4b", "nomic-embed-text"), answers())
                  if c.status in (OK, INFO)]
        self.assertTrue(doctor.render(checks).endswith("Ready."))


class TheWizardOffersWhatOllamaHas(unittest.TestCase):
    def choose(self, models, typed):
        from mechanics.setup import ConfigWizard

        with patch("engine.doctor.installed_models", return_value=models), patch("builtins.input", return_value=typed), \
                patch("builtins.print"):
            return ConfigWizard._choose_ollama_model("http://127.0.0.1:11434/v1/chat/completions")

    def test_a_number_picks_that_model(self):
        self.assertEqual(self.choose(["a:1", "b:2"], "2"), "b:2")

    def test_enter_keeps_the_engines_own_model_when_it_is_there(self):
        self.assertEqual(self.choose(["a:1", "gemma4:12b"], ""), "gemma4:12b")

    def test_enter_takes_the_first_model_when_the_default_is_absent(self):
        self.assertEqual(self.choose(["a:1", "b:2"], ""), "a:1")

    def test_a_typed_name_is_kept(self):
        self.assertEqual(self.choose(["a:1"], "mistral-nemo"), "mistral-nemo")

    def test_an_ollama_that_does_not_answer_still_gets_a_default(self):
        self.assertEqual(self.choose(None, ""), "gemma4:12b")


if __name__ == "__main__":
    unittest.main()
