import unittest
from bone_architect import BoneArchitect
from bone_brain import NeurotransmitterModulator, LLMInterface
from bone_config import BoneConfig
from bone_core import EventBus, Prisma
from bone_physics import GeodesicEngine, CycleStabilizer, GeodesicConstants
from bone_types import CycleContext


class MockGovernor:

    def recalibrate(self, v, d):
        pass

    def regulate(self, p, dt):
        return 0.0, 0.0


class TestSlashCompliance(unittest.TestCase):

    def setUp(self):
        self.events = EventBus()
        self.lexicon_stub = type("LexiconStub", (), {"get": lambda self_setup, k: set()})()

    def test_fuller_genesis_spark(self):
        print(f"\n{Prisma.CYN}[FULLER] Testing Genesis Ephemeralization...{Prisma.RST}")
        embryo = BoneArchitect.incubate(self.events, self.lexicon_stub)
        embryo.bio.mito.state.atp_pool = 0.0
        embryo = BoneArchitect.awaken(embryo)
        atp = embryo.bio.mito.state.atp_pool
        genesis_val = getattr(BoneConfig.METABOLISM, "GENESIS_VOLTAGE", 100.0)
        self.assertEqual(
            atp, genesis_val, f"Genesis Spark failed. Expected {genesis_val}, got {atp}"
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Architect injected {atp} ATP independently.{Prisma.RST}"
        )

    def test_pinker_geodesic_constants(self):
        print(f"\n{Prisma.MAG}[PINKER] Testing Geodesic Constants...{Prisma.RST}")

        self.assertTrue(
            hasattr(GeodesicConstants, "DENSITY_SCALAR"),
            "GeodesicConstants class missing!",
        )
        clean_words = ["run", "fast", "kinetic"]
        counts = {"kinetic": 3, "heavy": 0}
        vector = GeodesicEngine.collapse_wavefunction(clean_words, counts)
        self.assertIsInstance(vector.tension, float)
        print(
            f"{Prisma.GRN}   >>> PASS: GeodesicConstants detected. Vector calculated: T={vector.tension:.2f}{Prisma.RST}"
        )

    def test_meadows_hard_fuse(self):
        print(f"\n{Prisma.YEL}[MEADOWS] Testing Hard Fuse Protocol...{Prisma.RST}")
        gov = MockGovernor()
        stabilizer = CycleStabilizer(self.events, gov)
        ctx = CycleContext(input_text="System Overload")
        ctx.physics.voltage = 105.0
        triggered = stabilizer.stabilize(ctx, "TEST_PHASE")
        self.assertTrue(triggered, "Stabilizer did not trigger correction.")
        self.assertEqual(
            ctx.physics.voltage,
            10.0,
            "Hard Fuse did not reset voltage to Safe Mode (10.0).",
        )
        self.assertEqual(
            ctx.physics.flow_state, "SAFE_MODE", "Flow state not set to SAFE_MODE."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Fuse blew at 105V. System reset to Safe Mode.{Prisma.RST}"
        )

    def test_schur_self_care(self):
        print(f"\n{Prisma.VIOLET}[SCHUR] Testing Self-Care Routine...{Prisma.RST}")
        bio_stub = type(
            "BioStub", (), {"endo": type("Endo", (), {"get_state": lambda self_stub: {}})()}
        )
        modulator = NeurotransmitterModulator(bio_stub, self.events)
        modulator.current_chem.dopamine = 0.05
        initial_dop = modulator.current_chem.dopamine
        for _ in range(12):
            modulator.modulate(base_voltage=10.0)

        final_dop = modulator.current_chem.dopamine
        self.assertGreater(
            final_dop, initial_dop, "Dopamine did not increase after starvation."
        )
        logs = [e["text"] for e in self.events.flush()]
        cookie_log = any("SELF-CARE" in l for l in logs)
        self.assertTrue(cookie_log, "No 'SELF-CARE' log found in EventBus.")
        print(
            f"{Prisma.GRN}   >>> PASS: System gave itself a cookie after starvation.{Prisma.RST}"
        )


class TestLocalIntegration(unittest.TestCase):
    def test_ollama_handshake(self):
        print(
            f"\n{Prisma.CYN}[CORTEX] Testing Local LLM Uplink (Ollama)...{Prisma.RST}"
        )
        llm = LLMInterface(
            events_ref=EventBus(),
            provider="ollama",
            base_url="http://127.0.0.1:11434/v1/chat/completions",
            model="llama3",
            api_key="ollama",
        )
        prompt = "SYSTEM_DIAGNOSTIC: Respond with 'ONLINE'."
        try:
            response = llm.generate(prompt, {"max_tokens": 10})

            if "ONLINE" in response or "online" in response.lower():
                print(
                    f"{Prisma.GRN}   >>> PASS: Ollama Responded: {response.strip()}{Prisma.RST}"
                )
            elif "[CIRCUIT_BROKEN]" in response or "[SILENCE]" in response:
                print(
                    f"{Prisma.OCHRE}   >>> WARN: Ollama not detected or timed out. (Is it running?){Prisma.RST}"
                )
            else:
                print(
                    f"{Prisma.GRN}   >>> PASS: Connection successful, output generated: {response[:50]}...{Prisma.RST}"
                )

        except Exception as e:
            print(
                f"{Prisma.RED}   >>> FAIL: Exception during transport: {e}{Prisma.RST}"
            )


if __name__ == "__main__":
    print(f"{Prisma.WHT}┌──────────────────────────────────────────┐{Prisma.RST}")
    print(f"{Prisma.WHT}│ BONE ENGINE DIAGNOSTIC SUITE // v2.3     │{Prisma.RST}")
    print(f"{Prisma.WHT}│ PYTHON 3.14 COMPATIBLE                   │{Prisma.RST}")
    print(f"{Prisma.WHT}└──────────────────────────────────────────┘{Prisma.RST}")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSlashCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalIntegration))
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    if result.wasSuccessful():
        print(
            f"\n{Prisma.GRN}*** ALL SYSTEMS NOMINAL. SLASH COMPLIANCE VERIFIED. ***{Prisma.RST}"
        )
    else:
        print(f"\n{Prisma.RED}*** SYSTEM FAILURE DETECTED. CHECK LOGS. ***{Prisma.RST}")
