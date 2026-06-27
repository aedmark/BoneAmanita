"""tests/base.py"""

import io
import json
import os
import sys
import time
import unittest
import warnings
from unittest.mock import MagicMock, patch

from constants import Prisma
from core import LoreManifest, TelemetryService
from main import BoneAmanita


class AppendLogger:
    """Funneled logger to ensure mock outputs append without overwriting."""

    def __init__(self, filename):
        self.filename = filename
        os.makedirs(
            os.path.dirname(filename) if os.path.dirname(filename) else ".",
            exist_ok=True,
        )

    def log(self, test_id, category, *args, **kwargs):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"\n[{category}] TEST: {test_id}\n")
            if args:
                f.write(f"Args: {args}\n")
            if kwargs:
                f.write(f"Kwargs: {json.dumps(kwargs, default=str)}\n")


class TeeOutput:
    """Multiplexes stdout to both the console and a file, stripping ANSI for the file."""

    def __init__(self, stream, filename):
        self.stream = stream
        self.file = open(filename, "a", encoding="utf-8")

    def write(self, data):
        self.stream.write(data)
        self.file.write(Prisma.strip(data) if data else "")

    def flush(self):
        self.stream.flush()
        self.file.flush()

    def close(self):
        self.file.close()


class BoneTestCase(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        self.original_stdout = sys.stdout
        self.tee = TeeOutput(sys.stdout, "test_output_full.log")
        sys.stdout = self.tee
        print(f"\n{Prisma.CYN}>>> STARTING TEST: {self.id()}{Prisma.RST}")
        self.lore_logger = AppendLogger("test_saves.log")
        self.lore_patcher = patch("core.LoreManifest.save")
        self.mock_lore_save = self.lore_patcher.start()
        self.mock_lore_save.side_effect = lambda *a, **k: self.lore_logger.log(
            self.id(), "LORE SAVE", *a, **k
        )

        self.chronos_patcher = patch("protocols.chronos.ChronosKeeper.save_checkpoint")
        self.mock_chronos_save = self.chronos_patcher.start()

        def _hooked_chronos_save(*args, **kwargs):
            self.lore_logger.log(
                self.id(), "CHRONOS QUICKSAVE", args=args, kwargs=kwargs
            )
            return "quicksave.json"

        self.mock_chronos_save.side_effect = _hooked_chronos_save

        self.memory_logger = AppendLogger("test_memories.log")
        self.spore_patcher = patch("spores.io.LocalFileSporeLoader.save_spore")
        self.mock_spore_save = self.spore_patcher.start()
        self.mock_spore_save.side_effect = lambda filename, data: (
            self.memory_logger.log(self.id(), f"SPORE SAVE: {filename}", data=data)
        )

        self.telemetry_logger = AppendLogger("test_telemetry.log")
        self.telemetry_patcher = patch("core.TelemetryService.get_instance")
        self.mock_telemetry_get = self.telemetry_patcher.start()
        self.test_telemetry_dir = "test_telemetry_logs"
        self.real_telemetry = TelemetryService()
        self.real_telemetry.log_dir = self.test_telemetry_dir
        self.real_telemetry.current_trace_file = os.path.join(
            self.test_telemetry_dir, f"trace_test_{int(time.time())}.jsonl"
        )
        os.makedirs(self.test_telemetry_dir, exist_ok=True)
        original_record = self.real_telemetry.record_event

        def hooked_record(event_dict):
            self.telemetry_logger.log(self.id(), "TELEMETRY RECORD", event=event_dict)
            original_record(event_dict)

        self.real_telemetry.record_event = hooked_record
        self.mock_telemetry_get.return_value = self.real_telemetry
        self.test_config = {
            "PROVIDER": "ollama",
            "boot_mode": "DEEP",
            "MAX_STAMINA": 100.0,
            "MAX_HEALTH": 100.0,
            "CORE": {"TELEMETRY_LOG_DIR": self.test_telemetry_dir},
        }
        self.oroboros_file = f"tests_isolated_legacy_{self.id().split('.')[-1]}.json"
        self.oroboros_patcher = patch(
            "soul.oroboros.TheOroboros.LEGACY_FILE", self.oroboros_file
        )
        self.oroboros_patcher.start()
        try:
            self.engine = BoneAmanita(config=self.test_config)
        except Exception as e:
            print(
                f"{Prisma.RED}Test Engine Initialization Failed! Captured Output is preserved in test_output_full.log{Prisma.RST}"
            )
            raise

    def tearDown(self):
        print(f"{Prisma.GRN}<<< COMPLETED TEST: {self.id()}{Prisma.RST}\n")
        try:
            if hasattr(self, "real_telemetry"):
                self.real_telemetry.flush_to_disk()
                if self.real_telemetry._executor:
                    self.real_telemetry._executor.shutdown(wait=True)
            LoreManifest.get_instance().flush_cache()
        finally:
            sys.stdout = self.original_stdout
            self.tee.close()
        self.lore_patcher.stop()
        self.chronos_patcher.stop()
        self.spore_patcher.stop()
        self.telemetry_patcher.stop()
        self.oroboros_patcher.stop()
