"""tests/base.py"""

import unittest
import warnings
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
        print(f"\n{Prisma.CYN}>>> STARTING TEST: {self.id()}{Prisma.RST}")
        self.engine = BoneAmanita(config=self.test_config)

    def tearDown(self):
        print(f"{Prisma.GRN}<<< COMPLETED TEST: {self.id()}{Prisma.RST}\n")
        LoreManifest.get_instance().flush_cache()
        self.lore_patcher.stop()
        self.telemetry_patcher.stop()