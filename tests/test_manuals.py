import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_PY = ROOT / "tools" / "manual.py"
SPEC = importlib.util.spec_from_file_location("manual", MANUAL_PY)
manual = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(manual)


class ManualSetTests(unittest.TestCase):
    def test_system_manual_validates_and_builds(self):
        source_path = ROOT / "docs" / "manual" / "system.manual.json"
        self.assertTrue(source_path.is_file(), f"missing {source_path}")
        data = json.loads(source_path.read_text(encoding="utf-8"))
        expanded = manual.expand_placeholders(copy.deepcopy(data), data)
        errors, warnings = manual.validate(expanded)
        self.assertEqual(errors, [], f"system manual errors: {errors}")
        self.assertEqual(warnings, [], f"system manual warnings: {warnings}")
        output = manual.build_html(expanded)
        self.assertIn("BoneAmanita System Manual", output)
        self.assertIn("The prompt engine contract", output)
        self.assertIn("reference.html", output)

    def test_reference_manual_validates_and_builds(self):
        source_path = ROOT / "docs" / "manual" / "reference.manual.json"
        self.assertTrue(source_path.is_file(), f"missing {source_path}")
        data = json.loads(source_path.read_text(encoding="utf-8"))
        expanded = manual.expand_placeholders(copy.deepcopy(data), data)
        errors, warnings = manual.validate(expanded)
        self.assertEqual(errors, [], f"reference manual errors: {errors}")
        self.assertEqual(warnings, [], f"reference manual warnings: {warnings}")
        output = manual.build_html(expanded)
        self.assertIn("BoneAmanita Reference Manual", output)
        self.assertIn("In-Session Slash Commands", output)
        self.assertIn("index.html", output)


if __name__ == "__main__":
    unittest.main()
