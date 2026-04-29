"""tests/base.py"""

import unittest
import warnings
from core import LoreManifest
from main import BoneAmanita

class BoneTestCase(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        self.test_config = {"PROVIDER": "mock", "boot_mode": "ADVENTURE", "MAX_STAMINA": 100.0, "MAX_HEALTH": 100.0, }
        self.engine = BoneAmanita(config=self.test_config)

    def tearDown(self):
        LoreManifest.get_instance().flush_cache()