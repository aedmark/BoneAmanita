"""tests/test_lore.py"""

import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Guarantee test runners discover the Base class correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.base import BoneTestCase
from core import LoreManifest


class LoreManifestTests(BoneTestCase):

    def test_singleton_enforcement(self):
        manifest1 = LoreManifest.get_instance()
        manifest2 = LoreManifest.get_instance()
        self.assertIs(manifest1, manifest2, "[FAIL] LoreManifest is not acting as a strict singleton.")

    @patch('core.LoreManifest._load_from_disk')
    def test_cache_miss_loads_from_disk(self, mock_load):
        # Mock the disk loading behavior so we don't rely on literal JSON files during unit tests
        mock_load.return_value = {"greeting": "Welcome to the Bone Engine"}

        manifest = LoreManifest.get_instance()
        manifest.flush_cache("test_disk_cat")  # Ensure clean slate

        # The first get() should trigger a cache miss and load from disk
        result = manifest.get("test_disk_cat", "greeting")
        self.assertEqual(result, "Welcome to the Bone Engine", "[FAIL] LoreManifest failed to retrieve data from disk mock.")
        mock_load.assert_called_once()

        # The second get() should hit the memory cache, NOT the disk
        manifest.get("test_disk_cat", "greeting")
        self.assertEqual(mock_load.call_count, 1, "[FAIL] LoreManifest did not cache the disk result; read from disk twice.")

    def test_inject_and_merge_data(self):
        manifest = LoreManifest.get_instance()
        manifest.flush_cache("dynamic_cat")

        # Initial inject
        manifest.inject("dynamic_cat", {"primary_directive": "Survive"})
        self.assertEqual(manifest.get("dynamic_cat", "primary_directive"), "Survive", "[FAIL] Failed to inject and retrieve initial data.")

        # Merge inject - adding new keys should not wipe out the old ones
        manifest.inject("dynamic_cat", {"secondary_directive": "Thrive"})
        self.assertEqual(manifest.get("dynamic_cat", "primary_directive"), "Survive", "[FAIL] Merged injection overwrote existing data.")
        self.assertEqual(manifest.get("dynamic_cat", "secondary_directive"), "Thrive", "[FAIL] Failed to merge new key into existing category.")

    def test_flush_cache(self):
        manifest = LoreManifest.get_instance()
        manifest.inject("flush_cat", {"volatile_data": 42})
        self.assertEqual(manifest.get("flush_cat", "volatile_data"), 42)

        # Wipe the specific category
        manifest.flush_cache("flush_cat")

        # Ensure a subsequent fetch attempts to look at the disk (which we mock to return None here)
        with patch.object(manifest, '_load_from_disk', return_value=None):
            self.assertIsNone(manifest.get("flush_cat", "volatile_data"), "[FAIL] flush_cache did not clear the dictionary in memory.")

    def test_save_to_disk(self):
        # Because BoneTestCase mocks LoreManifest.save globally in setUp() to intercept writes,
        # we must temporarily halt the patch to test the actual save mechanism natively.
        self.lore_patcher.stop()
        try:
            # Bypass singleton for an isolated filesystem test
            manifest = LoreManifest(data_dir="/dummy/path")
            manifest.inject("save_cat", {"vital_stat": 99.9})

            m_open = mock_open()
            with patch('builtins.open', m_open):
                manifest.save("save_cat")

                # Check that the file was written to the correct destination folder
                m_open.assert_called_once_with(os.path.join("/dummy/path", "save_cat.json"), "w", encoding="utf-8")

                # Intercept the exact string written to the mocked file
                written_content = "".join(call.args[0] for call in m_open().write.call_args_list)
                self.assertIn('"vital_stat": 99.9', written_content, "[FAIL] Saved JSON did not contain the injected data.")
        finally:
            # Re-engage the patch so tearDown() proceeds safely
            self.lore_patcher.start()


if __name__ == '__main__':
    unittest.main()