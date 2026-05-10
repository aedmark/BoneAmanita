"""tests/base.py"""

import unittest
import warnings
import sys
import io
from unittest.mock import patch, MagicMock
from core import LoreManifest
from main import BoneAmanita
from constants import Prisma

class BoneTestCase(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        self.lore_patcher = patch('core.LoreManifest.save')
        self.mock_lore_save = self.lore_patcher.start()
        self.telemetry_patcher = patch('core.TelemetryService.get_instance')
        self.mock_telemetry = self.telemetry_patcher.start()
        dummy_telemetry = MagicMock()
        dummy_telemetry.disabled = True
        self.mock_telemetry.return_value = dummy_telemetry
        self.test_config = {"PROVIDER": "ollama", "boot_mode": "DEEP", "MAX_STAMINA": 100.0, "MAX_HEALTH": 100.0, }

        # 1. Globally patch the legacy file so tests never read/write real save data
        self.oroboros_patcher = patch('soul.oroboros.TheOroboros.LEGACY_FILE', 'tests_isolated_legacy_void.json')
        self.oroboros_patcher.start()

        print(f"\n{Prisma.CYN}>>> STARTING TEST: {self.id()}{Prisma.RST}")

        # 2. Suppress engine boot-up noise so the test console stays pristine
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            self.engine = BoneAmanita(config=self.test_config)
        finally:
            sys.stdout = original_stdout

    def tearDown(self):
        print(f"{Prisma.GRN}<<< COMPLETED TEST: {self.id()}{Prisma.RST}\n")

        # Suppress the Lore cache flush noise
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            LoreManifest.get_instance().flush_cache()
        finally:
            sys.stdout = original_stdout

        self.lore_patcher.stop()
        self.telemetry_patcher.stop()
        self.oroboros_patcher.stop()