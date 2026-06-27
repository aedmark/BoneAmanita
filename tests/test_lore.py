"""tests/test_lore.py"""

import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import LoreManifest
from tests.base import BoneTestCase


class LoreManifestTests(BoneTestCase):
    def test_singleton_enforcement(self):
        manifest1 = LoreManifest.get_instance()
        manifest2 = LoreManifest.get_instance()
        self.assertIs(
            manifest1,
            manifest2,
            "[FAIL] LoreManifest is not acting as a strict singleton.",
        )

    @patch("core.LoreManifest._load_from_disk")
    def test_cache_miss_loads_from_disk(self, mock_load):
        mock_load.return_value = {"greeting": "Welcome to the Bone Engine"}

        manifest = LoreManifest.get_instance()
        manifest.flush_cache("test_disk_cat")

        result = manifest.get("test_disk_cat", "greeting")
        self.assertEqual(
            result,
            "Welcome to the Bone Engine",
            "[FAIL] LoreManifest failed to retrieve data from disk mock.",
        )
        mock_load.assert_called_once()

        manifest.get("test_disk_cat", "greeting")
        self.assertEqual(
            mock_load.call_count,
            1,
            "[FAIL] LoreManifest did not cache the disk result; read from disk twice.",
        )

    def test_inject_and_merge_data(self):
        manifest = LoreManifest.get_instance()
        manifest.flush_cache("dynamic_cat")

        manifest.inject("dynamic_cat", {"primary_directive": "Survive"})
        self.assertEqual(
            manifest.get("dynamic_cat", "primary_directive"),
            "Survive",
            "[FAIL] Failed to inject and retrieve initial data.",
        )

        manifest.inject("dynamic_cat", {"secondary_directive": "Thrive"})
        self.assertEqual(
            manifest.get("dynamic_cat", "primary_directive"),
            "Survive",
            "[FAIL] Merged injection overwrote existing data.",
        )
        self.assertEqual(
            manifest.get("dynamic_cat", "secondary_directive"),
            "Thrive",
            "[FAIL] Failed to merge new key into existing category.",
        )

    def test_flush_cache(self):
        manifest = LoreManifest.get_instance()
        manifest.inject("flush_cat", {"volatile_data": 42})
        self.assertEqual(manifest.get("flush_cat", "volatile_data"), 42)

        manifest.flush_cache("flush_cat")

        with patch.object(manifest, "_load_from_disk", return_value=None):
            self.assertIsNone(
                manifest.get("flush_cat", "volatile_data"),
                "[FAIL] flush_cache did not clear the dictionary in memory.",
            )

    def test_save_to_disk(self):
        self.lore_patcher.stop()
        try:
            manifest = LoreManifest(data_dir="/dummy/path")
            manifest.inject("save_cat", {"vital_stat": 99.9})

            m_open = mock_open()
            with patch("builtins.open", m_open):
                manifest.save("save_cat")

                m_open.assert_called_once_with(
                    os.path.join("/dummy/path", "save_cat.json"), "w", encoding="utf-8"
                )

                written_content = "".join(
                    call.args[0] for call in m_open().write.call_args_list
                )
                self.assertIn(
                    '"vital_stat": 99.9',
                    written_content,
                    "[FAIL] Saved JSON did not contain the injected data.",
                )
        finally:
            self.lore_patcher.start()


if __name__ == "__main__":
    unittest.main()
