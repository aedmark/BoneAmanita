"""
unified_diagnostic.py - BoneAmanita Master Test Suite
"Trust, but verify. Then verify the verification."
"""

from bone_drivers import EnneagramDriver, SoulDriver, BoneConsultant, LiminalModule, SyntaxModule
import time, os, unittest
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from unittest.mock import MagicMock, patch
from bone_body import SemanticEndocrinologist, EndocrineSystem, SemanticSignal
from bone_brain import NeurotransmitterModulator
from bone_core import EventBus, Prisma, LoreManifest
from bone_machine import TheCrucible, TheTheremin, PanicRoom
from bone_physics import GeodesicEngine, GeodesicConstants, CycleStabilizer, ZoneInertia, TRIGRAM_MAP
from bone_spores import ImmuneMycelium, BioLichen, BioParasite, MemoryCore
from bone_types import PhysicsPacket
from bone_brain import LLMInterface
from bone_akashic import TheAkashicRecord
from bone_village import TheTinkerer, TheCartographer, MirrorGraph,DeathGen
from bone_soul import TraitVector, HumanityAnchor, NarrativeSelf, TheOroboros
from bone_inventory import GordonKnot, Item
from bone_lexicon import LexiconStore, LinguisticAnalyzer, SemanticField
from bone_protocols import ZenGarden, TheBureau, TheFolly, KintsugiProtocol, LimboLayer
from bone_config import BoneConfig


@dataclass
class MockLexicon:
    @staticmethod
    def sanitize(text: str) -> List[str]:
        return text.split()

    @staticmethod
    def classify(word: str) -> Tuple[Optional[str], float]:
        if word in ["void", "chaos"]:
            return "abstract", 0.9
        return "neutral", 0.1

    @staticmethod
    def get_random(_cat: str) -> str:
        return "test_word"

    @staticmethod
    def measure_viscosity(word: str) -> float:
        return 0.8 if word == "void" else 0.2


@dataclass
class MockAkashic:

    @staticmethod
    def calculate_manifold_shift(
        _archetype: str, _traits: Dict
    ) -> Dict:
        return {"shift": 0.5}

    @staticmethod
    def forge_new_item(_vector: Dict) -> Tuple[str, Dict]:
        return "QUANTUM_SPHERE", {
            "description": "A dense ball of mock data.",
            "passive_traits": ["HEAVY"],
        }


class MockLore:
    @staticmethod
    def get_lenses():
        return {
            "JESTER": {
                "role": "The Paradox",
                "directives": ["Break the fourth wall.", "Celebrate entropy."],
            }
        }

    @staticmethod
    def get_item_gen():
        return {
            "PREFIXES": {"kinetic": ["Fast"], "heavy": ["Heavy"]},
            "BASES": {"TOOL": ["Wrench"], "ARTIFACT": ["Orb"]},
            "SUFFIXES": {"kinetic": ["of Speed"], "heavy": ["of Weight"]},
        }


class MockGovernor:
    def recalibrate(self, _v, _d):
        pass

    @staticmethod
    def regulate(_p, _dt):
        return 0.0, 0.0


class TestBedrockIntegrity(unittest.TestCase):
    def test_lore_manifest_loading(self):
        print(f"\n{Prisma.CYN}[PROBE] Testing LoreManifest Integrity...{Prisma.RST}")
        manifest = LoreManifest.get_instance()
        narrative = manifest.get("narrative_data")
        self.assertIsNotNone(narrative, "CRITICAL: narrative_data.json failed to load.")
        seeds = narrative.get("SEEDS", [])
        self.assertGreater(len(seeds), 0, "No seeds found in narrative_data.")
        lenses = narrative.get("lenses", {})
        self.assertIn(
            "SHERLOCK", lenses, "Core 'SHERLOCK' lens missing from narrative_data."
        )
        print(f"{Prisma.GRN}   >>> PASS: Bedrock data loaded successfully.{Prisma.RST}")


class TestSomaticPhysics(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()
        self.lex_stub = MagicMock()

    def test_pinker_geodesic_constants(self):
        print(
            f"\n{Prisma.MAG}[PINKER] Testing Geodesic Constants & Logarithmic Friction...{Prisma.RST}"
        )
        self.assertTrue(
            hasattr(GeodesicConstants, "DENSITY_SCALAR"),
            "GeodesicConstants class missing!",
        )
        counts = {"suburban": 500, "heavy": 0}
        clean_words = ["the"] * 500
        vector = GeodesicEngine.collapse_wavefunction(clean_words, counts)
        self.assertLess(
            vector.compression,
            50.0,
            f"Friction Explosion! Drag: {vector.compression:.1f}",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Logarithmic Friction Active (Drag: {vector.compression:.1f}){Prisma.RST}"
        )

    def test_meadows_hard_fuse_and_starvation(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Hard Fuses and Starvation Clamps...{Prisma.RST}"
        )
        gov = MockGovernor()
        stabilizer = CycleStabilizer(self.events, gov)

        class MockCtx:

            class MockPhys:
                voltage = 105.0
                flow_state = "CRITICAL"

            physics = MockPhys()
            input_text = "System Overload"

            def log(self, msg):
                pass

            def record_flux(self, phase, field, old_val, new_val, reason):
                pass

        ctx = MockCtx()
        triggered = stabilizer.stabilize(ctx, "TEST_PHASE")
        self.assertTrue(triggered, "Stabilizer did not trigger correction.")
        self.assertEqual(ctx.physics.voltage, 10.0, "Hard Fuse did not reset voltage.")
        print(
            f"{Prisma.GRN}   >>> PASS: Hard Fuse Blew successfully at 105V.{Prisma.RST}"
        )


class TestCognitionAndInventory(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()
        self.lore_mock = MagicMock()
        self.lore_mock.get.side_effect = lambda k: (
            MockLore.get_lenses() if k == "LENSES" else {}
        )

    def test_schur_self_care(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Cognitive Self-Care Routine...{Prisma.RST}"
        )
        bio_stub = type(
            "BioStub",
            (),
            {"endo": type("Endo", (), {"get_state": lambda self_stub: {}})()},
        )
        modulator = NeurotransmitterModulator(bio_stub, self.events)
        modulator.current_chem.dopamine = 0.05
        initial_dop = modulator.current_chem.dopamine
        for _ in range(12):
            modulator.modulate(base_voltage=10.0)
        self.assertGreater(
            modulator.current_chem.dopamine,
            initial_dop,
            "Dopamine did not increase after starvation.",
        )
        print(f"{Prisma.GRN}   >>> PASS: System administered self-care.{Prisma.RST}")

    def test_fuller_inventory_stacking_and_reflexes(self):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Inventory Reflexes & Diminishing Returns...{Prisma.RST}"
        )
        gordon = GordonKnot(self.events)

        anchor = Item(
            name="ANCHOR_STONE",
            description="Heavy.",
            function="ANCHOR",
            reflex_trigger="DRIFT_CRITICAL",
        )
        gordon.registry["ANCHOR_STONE"] = anchor
        gordon.inventory.append("ANCHOR_STONE")
        phys = {"narrative_drag": 8.0, "voltage": 10.0}
        triggered, msg = gordon.emergency_reflex(phys)
        self.assertTrue(triggered, "Anchor Stone failed to trigger.")
        self.assertEqual(
            phys["narrative_drag"], 0.0, "Anchor Stone failed to zero out drag."
        )
        self.assertNotIn(
            "ANCHOR_STONE", gordon.inventory, "Anchor Stone was not consumed."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Anchor Stone deployed. Drag neutralized.{Prisma.RST}"
        )


class TestLiveFireIntegration(unittest.TestCase):
    def test_ollama_handshake(self):
        if not LLMInterface:
            print(
                f"\n{Prisma.OCHRE}[LIVE FIRE] LLMInterface not imported. Skipping.{Prisma.RST}"
            )
            self.skipTest("LLMInterface missing")
        print(
            f"\n{Prisma.CYN}[LIVE FIRE] Testing Local LLM Uplink (Ollama)...{Prisma.RST}"
        )
        llm = LLMInterface(
            events_ref=EventBus(),
            provider="ollama",
            base_url="http://127.0.0.1:11434/v1/chat/completions",
            model="mistral-nemo",
        )
        try:
            start_t = time.time()
            response = llm.generate(
                "System check. Reply with the single word: ONLINE.", {"max_tokens": 10}
            )
            duration = time.time() - start_t
            self.assertIsNotNone(response)
            self.assertGreater(len(response), 0)
            if "ONLINE" in response.upper():
                print(
                    f"{Prisma.GRN}   >>> PASS: LLM Responded strictly in {duration:.2f}s.{Prisma.RST}"
                )
            else:
                print(
                    f"{Prisma.OCHRE}   >>> WARN: LLM Drifted: {response.strip()}{Prisma.RST}"
                )
        except Exception as e:
            self.fail(f"LLM Connection Failed: {e}")


class TestSemanticEndocrine(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()
        self.lex_stub = MockLexicon()
        self.akashic_stub = MockAkashic()

    def test_cortisol_spike_on_void_exposure(self):
        print(f"\n{Prisma.RED}[MEADOWS] Testing Somatic Stress Response...{Prisma.RST}")
        endo = EndocrineSystem()
        initial_cortisol = endo.cortisol
        stress_signal = SemanticSignal(
            novelty=0.9, resonance=0.1, valence=-0.8, coherence=0.2
        )
        endo._apply_semantic_pressure(stress_signal)
        self.assertGreater(
            endo.cortisol,
            initial_cortisol,
            "Cortisol failed to spike under negative semantic pressure.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Negative valence triggered Cortisol rise (from {initial_cortisol:.2f} to {endo.cortisol:.2f}).{Prisma.RST}"
        )

    def test_semantic_signal_generation(self):
        print(
            f"\n{Prisma.VIOLET}[PINKER] Testing Lexical-to-Chemical Translation...{Prisma.RST}"
        )
        mem_stub = type(
            "MemStub", (), {"check_for_resurrection": lambda self_stub, w, v: None}
        )()
        endocrinologist = SemanticEndocrinologist(
            memory_ref=mem_stub, lexicon_ref=self.lex_stub
        )
        phys = PhysicsPacket(voltage=20.0, narrative_drag=5.0)
        signal = endocrinologist.assess(["void", "chaos", "void"], phys)
        self.assertIsInstance(
            signal,
            SemanticSignal,
            "Endocrinologist did not return a valid SemanticSignal.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Semantic signal generated successfully.{Prisma.RST}"
        )

    def test_akashic_handshake(self):
        print(
            f"\n{Prisma.YEL}[FULLER] Testing Akashic-to-Inventory Handshake...{Prisma.RST}"
        )
        gordon = GordonKnot(self.events)
        vector = {"PHI": 0.9, "ENT": 0.1}
        name, data = self.akashic_stub.forge_new_item(vector)
        gordon.register_dynamic_item(name, data)
        retrieved = gordon.get_item_data(name)
        self.assertIsNotNone(retrieved, "Gordon failed to register the forged item.")
        self.assertEqual(
            retrieved.name, "QUANTUM_SPHERE", "Gordon registered the wrong item data."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Akashic Forge created '{name}', Gordon successfully caught it.{Prisma.RST}"
        )


class TestMechanicalSystems(unittest.TestCase):

    def test_crucible_dampening_and_meltdown(self):
        print(
            f"\n{Prisma.RED}[FULLER] Testing Crucible Load Bearing & Meltdowns...{Prisma.RST}"
        )
        crucible = TheCrucible()
        initial_charges = crucible.dampener_charges
        success, msg, reduction = crucible.dampen(
            voltage_spike=18.0, stability_index=1.0
        )
        self.assertTrue(success, "Crucible failed to dampen a spike above tolerance.")
        self.assertEqual(
            crucible.dampener_charges,
            initial_charges - 1,
            "Dampener charge not consumed.",
        )
        self.assertGreater(reduction, 0.0, "Voltage reduction was 0.")
        crucible.dampen(18.0, 1.0)
        crucible.dampen(18.0, 1.0)
        fail_success, fail_msg, fail_red = crucible.dampen(18.0, 1.0)
        self.assertFalse(fail_success, "Crucible dampened without charges.")
        self.assertIn("EMPTY", fail_msg, "Crucible did not warn of empty dampener.")
        phys_meltdown = {"voltage": 19.0, "kappa": 0.2}
        state, effect, msg = crucible.audit_fire(phys_meltdown)
        self.assertEqual(
            state, "MELTDOWN", "Low structure high voltage did not cause Meltdown."
        )
        phys_ritual = {"voltage": 19.0, "kappa": 0.8}
        state_r, effect_r, msg_r = crucible.audit_fire(phys_ritual)
        self.assertEqual(
            state_r, "RITUAL", "High structure high voltage did not trigger Ritual."
        )
        self.assertGreater(
            crucible.max_voltage_cap,
            20.0,
            "Ritual failed to increase max voltage capacity.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Crucible safely exhausted charges and routed voltage to Ritual/Meltdown based on structure.{Prisma.RST}"
        )

    def test_theremin_accumulation_and_airstrike(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Theremin Resin Accumulation & Airstrike...{Prisma.RST}"
        )
        theremin = TheTheremin()
        phys_rep = {
            "voltage": 4.0,
            "repetition": 0.8,
            "counts": {"heavy": 1, "abstract": 1},
        }
        msg = ""
        for _ in range(3):
            is_stuck, flow, msg, crit = theremin.listen(phys_rep)
        self.assertGreater(
            theremin.decoherence_buildup, 0.0, "Theremin failed to accumulate Resin."
        )
        self.assertIn("CALCIFICATION", msg, "Theremin did not log Calcification.")
        theremin.decoherence_buildup = 99.0
        phys_strike = {
            "voltage": 10.0,
            "narrative_drag": 2.0,
            "counts": {"abstract": 10, "heavy": 10},
        }
        is_stuck, flow, msg, crit = theremin.listen(phys_strike)
        self.assertEqual(
            crit,
            "AIRSTRIKE",
            "Theremin breached 100 Resin but did not trigger AIRSTRIKE.",
        )
        self.assertEqual(
            theremin.decoherence_buildup, 0.0, "Resin did not reset after AIRSTRIKE."
        )
        self.assertEqual(
            phys_strike["voltage"], 0.0, "AIRSTRIKE did not zero out voltage."
        )
        self.assertGreaterEqual(
            phys_strike["narrative_drag"],
            20.0,
            "AIRSTRIKE did not apply massive narrative drag penalty.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Theremin accumulated stock and correctly blew the Airstrike pressure valve.{Prisma.RST}"
        )

    def test_theremin_relief_valves(self):
        print(
            f"\n{Prisma.CYN}[MEADOWS] Testing Theremin Thermal/Turbulence Relief...{Prisma.RST}"
        )
        theremin = TheTheremin()
        theremin.decoherence_buildup = 50.0
        phys_turb = {"turbulence": 0.8, "voltage": 2.0}
        theremin.listen(phys_turb)
        self.assertLess(
            theremin.decoherence_buildup,
            50.0,
            "Turbulence failed to reduce Resin buildup.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Turbulence successfully drained the Resin stock.{Prisma.RST}"
        )

    def test_panic_room_fallbacks(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Panic Room Graceful Degradation...{Prisma.RST}"
        )
        safe_phys = PanicRoom.get_safe_physics()
        self.assertEqual(
            safe_phys.flow_state, "SAFE_MODE", "Panic physics not in SAFE_MODE."
        )
        self.assertEqual(
            safe_phys.zone, "PANIC_ROOM", "Panic physics zone is incorrect."
        )
        safe_bio = PanicRoom.get_safe_bio()
        self.assertTrue(
            safe_bio["is_alive"], "Panic bio killed the system instead of saving it."
        )
        self.assertEqual(
            safe_bio["respiration"],
            "NECROSIS",
            "Panic bio respiration not set to fallback.",
        )
        safe_mind = PanicRoom.get_safe_mind()
        self.assertEqual(safe_mind["lens"], "NARRATOR", "Panic mind lens not reset.")

        print(
            f"{Prisma.GRN}   >>> PASS: Panic Room successfully generated safe fallback states.{Prisma.RST}"
        )


class TestMycelialEcosystem(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()

    def test_pinker_immune_response(self):
        print(
            f"\n{Prisma.MAG}[PINKER] Testing Phonetic Immune Rejection...{Prisma.RST}"
        )
        immune = ImmuneMycelium()
        status_smooth, msg_smooth = immune.assay("flow", None, None, None, None)
        self.assertIsNone(status_smooth, "Immune system rejected a smooth word.")
        status_toxic, msg_toxic = immune.assay("kbdgpt", None, None, None, None)
        self.assertEqual(
            status_toxic,
            "TOXIN_HEAVY",
            "Immune system failed to detect phonetic toxicity.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Phonetic density correctly triggered immune response.{Prisma.RST}"
        )

    @patch("bone_spores.LexiconService.get")
    @patch("bone_spores.LexiconService.teach")
    def test_schur_lichen_photosynthesis(self, _mock_teach, mock_get):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Lichen Sugar Generation...{Prisma.RST}"
        )
        lichen = BioLichen()
        mock_get.return_value = {"rock"}
        class MockPhysLichen:
            counts = {"photo": 3}
            narrative_drag = 1.0
        sugar, msg = lichen.photosynthesize(
            MockPhysLichen(), ["solar", "bloom", "rock"], tick_count=1
        )
        self.assertGreater(
            sugar, 0.0, "Lichen failed to generate sugar from photo-words."
        )
        self.assertIn("PHOTOSYNTHESIS", msg, "Lichen did not log photosynthesis event.")
        self.assertIn("SUBLIMATION", msg, "Lichen did not sublimate the heavy word.")
        print(
            f"{Prisma.GRN}   >>> PASS: Lichen successfully converted light into {sugar} ATP/Sugar.{Prisma.RST}"
        )

    def test_fuller_parasitic_bridging(self):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Parasitic Synapse Forcing...{Prisma.RST}"
        )
        mock_mem = type(
            "MockMem",
            (),
            {
                "graph": {
                    "rock": {"edges": {}, "last_tick": 0},
                    "void": {"edges": {}, "last_tick": 0},
                }
            },
        )()
        mock_lex = type(
            "MockLex",
            (),
            {"get": lambda self, cat: {"rock"} if cat == "heavy" else {"void"}},
        )()
        parasite = BioParasite(mock_mem, mock_lex)
        infected, msg = parasite.infect({"psi": 0.8}, stamina=50.0)
        self.assertTrue(infected, "Parasite failed to infect the graph.")
        self.assertIn(
            "void",
            mock_mem.graph["rock"]["edges"],
            "Parasite failed to bridge rock -> void.",
        )
        self.assertEqual(
            mock_mem.graph["rock"]["edges"]["void"],
            8.88,
            "Parasitic edge weight incorrect.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Parasite successfully bridged Heavy and Abstract nodes.{Prisma.RST}"
        )

    def test_meadows_memory_cannibalization(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Memory Cannibalization (Stock Limits)...{Prisma.RST}"
        )
        mock_strata = type("MockStrata", (), {"bury": lambda self, data: True})()
        core = MemoryCore(self.events, mock_strata)
        core.graph["old_node"] = {
            "edges": {"x": 1.0},
            "last_tick": 5,
        }
        core.graph["new_node"] = {
            "edges": {"x": 1.0, "y": 1.0},
            "last_tick": 10,
        }
        victim, msg = core.cannibalize(current_tick=12)
        self.assertEqual(victim, "old_node", "Cannibalize selected the wrong node.")
        self.assertNotIn(
            "old_node", core.graph, "Victim node was not removed from graph."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: System properly repressed the weakest memory to protect the limit.{Prisma.RST}"
        )


class TestSoulDynamics(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()

    def test_pinker_trait_normalization(self):
        print(f"\n{Prisma.MAG}[PINKER] Testing Trait Math & Decay...{Prisma.RST}")
        traits = TraitVector(hope=1.8, cynicism=-0.5, wisdom=0.9)
        self.assertEqual(traits.hope, 1.0, "TraitVector failed to clamp upper bound.")
        self.assertEqual(
            traits.cynicism, 0.0, "TraitVector failed to clamp lower bound."
        )
        traits.normalize(decay_rate=0.2)
        self.assertLess(traits.hope, 1.0, "Hope did not decay downward.")
        self.assertGreater(traits.cynicism, 0.0, "Cynicism did not decay upward.")
        print(
            f"{Prisma.GRN}   >>> PASS: Personality traits correctly clamped and decayed to baseline.{Prisma.RST}"
        )

    @patch("bone_core.LoreManifest.get_instance")
    def test_meadows_humanity_anchor_lockdown(self, mock_lore):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Existential Lockdown & Riddle...{Prisma.RST}"
        )
        mock_lore.return_value.get.return_value = [
            {"question": "Who goes there?", "triggers": ["friend"]}
        ]
        anchor = HumanityAnchor(self.events)
        anchor.dignity_reserve = 0.0
        anchor.audit_existence(physics={"voltage": 1.0, "vector": {}}, bio={"atp": 1.0})
        self.assertTrue(
            anchor.agency_lock,
            "Anchor failed to engage lockdown when dignity reached 0.",
        )
        unlocked_fail = anchor.assess_humanity("enemy")
        self.assertFalse(unlocked_fail, "Anchor unlocked with incorrect riddle answer.")
        self.assertTrue(anchor.agency_lock, "Agency lock incorrectly released.")
        unlocked_pass = anchor.assess_humanity("i am a friend")
        self.assertTrue(
            unlocked_pass, "Anchor failed to unlock with correct riddle answer."
        )
        self.assertFalse(
            anchor.agency_lock, "Agency lock remained active after correct answer."
        )
        self.assertEqual(
            anchor.dignity_reserve, 50.0, "Dignity not restored after unlock."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Anchor successfully locked the system and yielded to the correct password.{Prisma.RST}"
        )

    def test_schur_archetype_shifting(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Identity/Archetype Shifts...{Prisma.RST}"
        )
        soul = NarrativeSelf(
            engine_ref=MagicMock(), events_ref=self.events, memory_ref=MagicMock()
        )
        soul.traits.empathy = 0.9
        soul.traits.hope = 0.9
        soul._update_archetype()
        self.assertEqual(
            soul.archetype, "THE HEALER", "Soul failed to recognize Healer traits."
        )
        soul.traits.empathy = 0.1
        soul.traits.cynicism = 0.9
        soul.traits.hope = 0.2
        soul._update_archetype()
        self.assertEqual(
            soul.archetype, "THE NIHILIST", "Soul failed to recognize Nihilist traits."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: The Soul dynamically shifted its archetype based on mathematical traits.{Prisma.RST}"
        )

    @patch("bone_lexicon.LexiconService.get")
    def test_fuller_obsession_pursuit(self, mock_lex_get):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Obsession Pursuit & Gravity Assist...{Prisma.RST}"
        )
        mock_lex_get.return_value = {"star", "sky"}
        soul = NarrativeSelf(
            engine_ref=MagicMock(), events_ref=self.events, memory_ref=MagicMock()
        )
        soul.current_obsession = "The Pursuit of Stars"
        soul.current_target_cat = "astronomy"
        phys_packet = {"clean_words": ["star", "dust"], "narrative_drag": 5.0}
        msg = soul.pursue_obsession(phys_packet)
        self.assertIsNotNone(msg, "Muse did not trigger.")
        self.assertGreater(
            soul.obsession_progress, 0.0, "Obsession progress did not advance."
        )
        self.assertLess(
            phys_packet["narrative_drag"],
            5.0,
            "Gravity Assist failed to reduce narrative drag.",
        )
        self.assertIn("SYNERGY", msg, "Did not log synergy.")
        print(
            f"{Prisma.GRN}   >>> PASS: Hitting obsession keywords granted Gravity Assist (reduced drag).{Prisma.RST}"
        )

    def test_oroboros_reincarnation_scars(self):
        print(
            f"\n{Prisma.RED}[FULLER] Testing Oroboros Death & Reincarnation Scars...{Prisma.RST}"
        )
        original_legacy_file = TheOroboros.LEGACY_FILE
        TheOroboros.LEGACY_FILE = "test_legacy.json"
        try:
            if os.path.exists("test_legacy.json"):
                os.remove("test_legacy.json")
            oro = TheOroboros()
            oro.scars = []
            oro.myths = []
            oro.generation_count = 0
            mock_soul = MagicMock()
            mock_soul.core_memories = []
            oro.crystallize(cause_of_death="TOXICITY", soul=mock_soul)
            reborn_oro = TheOroboros()
            self.assertTrue(
                any(s.name == "Burnt Synapses" for s in reborn_oro.scars),
                "Oroboros did not apply Toxicity scar upon rebirth.",
            )
            phys = {"voltage": 15.0, "narrative_drag": 0.0}
            bio = {}
            log = reborn_oro.apply_legacy(phys, bio)
            self.assertEqual(
                phys["voltage"],
                10.0,
                "Burnt Synapses failed to penalize voltage capacity.",
            )
            self.assertTrue(
                any("Burnt Synapses" in l for l in log),
                "Legacy log missing scar application.",
            )
            print(
                f"{Prisma.GRN}   >>> PASS: Oroboros successfully crystallized death and scarred the next generation.{Prisma.RST}"
            )
        finally:
            TheOroboros.LEGACY_FILE = original_legacy_file
            if os.path.exists("test_legacy.json"):
                os.remove("test_legacy.json")


class TestSlashAkashic(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()
        self.mock_lore = MagicMock()
        self.mock_lore.get.side_effect = self._mock_lore_get
        self.captured_events = []

        def capture(payload):
            self.captured_events.append(payload)
        self.events.subscribe("RESONANCE_ACHIEVED", capture)
        self.akashic = TheAkashicRecord(
            lore_manifest=self.mock_lore, events_ref=self.events
        )

    @staticmethod
    def _mock_lore_get(key):
        if key == "LENSES":
            return {
                "THE POET": {"weights": {"voltage": 5.0, "drag": 1.0}},
                "THE ENGINEER": {"weights": {"voltage": 1.0, "drag": 5.0}},
                "_META_RESONANCE_": [
                    {
                        "trigram": "ZHEN",
                        "lens": "MANIC",
                        "result": "STORM_CHASER",
                        "msg": "Thunder resonates.",
                    }
                ],
            }
        elif key == "GORDON":
            return {"ITEM_REGISTRY": {}}
        return None

    def test_fuller_lens_hybridization(self):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Emergent Lens Hybridization...{Prisma.RST}"
        )
        for _ in range(self.akashic.HYBRID_LENS_THRESHOLD):
            self.akashic.record_interaction(["THE POET", "THE ENGINEER"])
        self.mock_lore.inject.assert_called()
        args, kwargs = self.mock_lore.inject.call_args
        target_dict, injected_data = args
        self.assertEqual(
            target_dict, "LENSES", "Akashic did not target LENSES for injection."
        )
        self.assertIn(
            "THE ENGINEER-POET",
            injected_data,
            "Akashic did not create the correctly named hybrid lens.",
        )
        new_weights = injected_data["THE ENGINEER-POET"]["weights"]
        self.assertEqual(new_weights["voltage"], 3.0, "Hybrid voltage math incorrect.")
        self.assertEqual(new_weights["drag"], 3.0, "Hybrid drag math incorrect.")
        print(
            f"{Prisma.GRN}   >>> PASS: Akashic Record successfully fused two lenses into a new paradigm.{Prisma.RST}"
        )

    def test_meadows_meta_resonance(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Meta-Resonance (Physics to Event)...{Prisma.RST}"
        )
        payload = {"lens": "MANIC", "physics": {"vector": {"VEL": 0.9, "STR": 0.1}}}
        self.akashic._on_mythology_update(payload)
        self.assertTrue(
            len(self.captured_events) > 0,
            "Akashic failed to fire RESONANCE_ACHIEVED event.",
        )
        self.assertEqual(
            self.captured_events[0]["result"],
            "STORM_CHASER",
            "Akashic fired the wrong resonance.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Physics vector correctly aligned with trigram to trigger Meta-Resonance.{Prisma.RST}"
        )

    def test_pinker_artifact_forging(self):
        print(
            f"\n{Prisma.MAG}[PINKER] Testing Akashic Artifact Generation...{Prisma.RST}"
        )
        vector = {"PHI": 0.8, "ENT": 0.2}
        name, data = self.akashic.forge_new_item(vector)
        self.assertTrue(
            name.startswith("SOLAR_ARTIFACT_8_"),
            "Artifact prefix did not match dominant force.",
        )
        self.assertIn(
            "CONDUCTIVE_HAZARD",
            data["passive_traits"],
            "High PHI did not grant conductive hazard trait.",
        )
        self.mock_lore.inject.assert_called()
        args, _ = self.mock_lore.inject.call_args
        self.assertEqual(
            args[0], "GORDON", "Akashic did not inject artifact into GORDON registry."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Akashic successfully generated and registered a new artifact based on physics.{Prisma.RST}"
        )

class TestVillageEcosystem(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()
        DeathGen.load_protocols()

    def test_meadows_tinkerer_passives(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Tinkerer Inventory Physics...{Prisma.RST}"
        )
        tinkerer = TheTinkerer(
            gordon_ref=MagicMock(), events_ref=self.events, akashic_ref=MagicMock()
        )
        inventory_data = [
            {"name": "Lead Boots", "passive_traits": ["HEAVY_LOAD"]},
            {"name": "Pocket Watch", "passive_traits": ["TIME_DILATION"]},
        ]
        deltas = tinkerer.calculate_passive_deltas(inventory_data)
        heavy_delta = next((d for d in deltas if d.message == "Heavy Load"), None)
        self.assertIsNotNone(heavy_delta, "Tinkerer missed HEAVY_LOAD trait.")
        self.assertEqual(heavy_delta.operator, "ADD", "Heavy Load should ADD drag.")
        self.assertGreater(heavy_delta.value, 0.0, "Heavy Load drag value is 0.")
        time_delta = next((d for d in deltas if d.message == "Time Dilation"), None)
        self.assertIsNotNone(time_delta, "Tinkerer missed TIME_DILATION trait.")
        self.assertEqual(
            time_delta.operator, "MULT", "Time Dilation should MULTIPLY drag."
        )
        self.assertLess(
            time_delta.value,
            1.0,
            "Time Dilation failed to reduce drag multiplier below 1.0.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Tinkerer correctly translated item traits into PhysicsDeltas.{Prisma.RST}"
        )

    def test_fuller_cartographer_navigation(self):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Cartographer Geography & Environment...{Prisma.RST}"
        )
        cartographer = TheCartographer(shimmer_ref=MagicMock())

        packet = PhysicsPacket(
            vector={"STR": 0.9, "VEL": 0.8}, voltage=5.0, narrative_drag=1.0
        )
        loc_name, msg = cartographer.locate(packet)
        self.assertIsNotNone(loc_name)
        self.assertIn(
            "STR9-VEL8",
            cartographer.world_graph,
            "Cartographer failed to hash and store the new coordinates.",
        )
        current_node = cartographer.world_graph[cartographer.current_node_id]
        current_node.atmosphere = "It is very heavy here."
        logs = cartographer.apply_environment(packet)
        self.assertGreater(
            packet.narrative_drag,
            1.0,
            "Heavy atmosphere failed to apply narrative drag.",
        )
        self.assertTrue(
            any("heavy" in log.lower() for log in logs), "Environment log missing."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Cartographer mapped vector to location and applied environmental physics.{Prisma.RST}"
        )

    def test_pinker_mirror_graph_reflection(self):
        print(
            f"\n{Prisma.MAG}[PINKER] Testing Mirror Graph Punctuation Analysis...{Prisma.RST}"
        )
        mirror = MirrorGraph(events_ref=self.events)
        packet_art = PhysicsPacket(
            raw_text="What is this place?", voltage=5.0, narrative_drag=1.0
        )
        mirror.reflect(packet_art)
        packet_war = PhysicsPacket(
            raw_text="Watch out!", voltage=50.0, narrative_drag=1.0
        )
        mirror.reflect(packet_war)
        self.assertGreater(
            mirror.stats["ART"], 0.0, "Mirror failed to register ART (?)"
        )
        self.assertGreater(
            mirror.stats["WAR"], 0.0, "Mirror failed to register WAR (!)"
        )
        modifiers = mirror.get_reflection_modifiers()
        self.assertIn(
            "WAR",
            modifiers["flavor"],
            "Mirror failed to identify the dominant reflection.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Mirror Graph accurately reflected punctuation and voltage into disposition.{Prisma.RST}"
        )

    def test_schur_death_generator(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Death Generation Diagnostics...{Prisma.RST}"
        )
        gluttony_packet = PhysicsPacket(voltage=999.0, narrative_drag=0.0)
        _, cause_g = DeathGen.eulogy(gluttony_packet, mito_state={"atp": 50.0})
        self.assertEqual(
            cause_g,
            "GLUTTONY",
            "DeathGen failed to diagnose Gluttony from high voltage.",
        )
        starve_packet = PhysicsPacket(voltage=5.0, narrative_drag=0.0)
        _, cause_s = DeathGen.eulogy(starve_packet, mito_state={"atp": 0.0})
        self.assertEqual(
            cause_s, "STARVATION", "DeathGen failed to diagnose Starvation from 0 ATP."
        )
        bored_packet = PhysicsPacket(voltage=5.0, narrative_drag=99.0)
        _, cause_b = DeathGen.eulogy(bored_packet, mito_state={"atp": 50.0})
        self.assertEqual(
            cause_b, "BOREDOM", "DeathGen failed to diagnose Boredom from high drag."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Death Generator correctly diagnosed causes of system termination.{Prisma.RST}"
        )


class TestGordonInventory(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()

    @patch("bone_core.LoreManifest.get_instance")
    def test_pinker_natural_language_parsing(self, mock_lore):
        print(f"\n{Prisma.MAG}[PINKER] Testing Organic Loot Parsing...{Prisma.RST}")
        mock_lore.return_value.get.return_value = {}
        gordon = GordonKnot(self.events)
        user_in = "I carefully"
        sys_out = "picked up a silver key from the table."
        found = gordon.parse_loot(user_in, sys_out)
        self.assertEqual(
            found, "silver key", "Gordon failed to extract the organic item."
        )
        sys_out_refusal = "I try, but I cannot pick up the heavy anvil."
        found_refused = gordon.parse_loot(user_in, sys_out_refusal)
        self.assertIsNone(
            found_refused,
            "Gordon ignored the 'cannot' refusal marker and looted anyway.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Natural language extraction respects syntax and refusal bounds.{Prisma.RST}"
        )

    @patch("bone_core.LoreManifest.get_instance")
    def test_schur_explicit_tag_processing(self, mock_lore):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing [[LOOT]] / [[LOST]] Tag Extraction...{Prisma.RST}"
        )
        mock_lore.return_value.get.return_value = {}
        gordon = GordonKnot(self.events)
        gordon.inventory = ["OLD_RATIONS"]
        text = "You open the chest. [[LOOT: Magic Sword]] [[LOST: Old Rations]]"
        user_in = "I take the contents."
        clean_text, logs = gordon.process_loot_tags(text, user_in)
        self.assertNotIn("[[LOOT:", clean_text, "Loot tag was not stripped from text.")
        self.assertIn(
            "MAGIC_SWORD", gordon.inventory, "Gordon failed to add tagged loot."
        )
        self.assertNotIn(
            "OLD_RATIONS", gordon.inventory, "Gordon failed to remove tagged lost item."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Explicit tags successfully parsed and applied to inventory.{Prisma.RST}"
        )

    @patch("bone_core.LoreManifest.get_instance")
    def test_meadows_fifo_capacity_limits(self, mock_lore):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Inventory Stock Limits (FIFO)...{Prisma.RST}"
        )
        mock_lore.return_value.get.return_value = {}
        gordon = GordonKnot(self.events)
        gordon.max_slots = 3
        gordon.acquire("ITEM_1")
        gordon.acquire("ITEM_2")
        gordon.acquire("ITEM_3")
        gordon.acquire("ITEM_4")
        self.assertEqual(len(gordon.inventory), 3, "Inventory exceeded max slots.")
        self.assertNotIn("ITEM_1", gordon.inventory, "Oldest item was not dropped.")
        self.assertIn("ITEM_4", gordon.inventory, "Newest item was not added.")
        print(
            f"{Prisma.GRN}   >>> PASS: Inventory safely dropped oldest item when capacity breached.{Prisma.RST}"
        )

    @patch("bone_core.LoreManifest.get_instance")
    def test_fuller_stamina_rummaging(self, mock_lore):
        print(f"\n{Prisma.CYN}[FULLER] Testing Rummage Stamina Tax...{Prisma.RST}")
        mock_lore.return_value.get.return_value = {}
        gordon = GordonKnot(self.events)
        gordon.registry["POCKET_LINT"] = Item(
            "POCKET_LINT", "Dust.", "MISC", spawn_context="COMMON"
        )
        success_fail, msg, cost = gordon.rummage(
            physics_ref={}, stamina_pool=5.0
        )
        self.assertFalse(success_fail, "Gordon rummaged without enough stamina.")
        success_pass, msg, cost = gordon.rummage(physics_ref={}, stamina_pool=50.0)
        self.assertTrue(
            success_pass, "Gordon failed to rummage despite having stamina."
        )
        self.assertEqual(cost, 15.0, "Rummage returned incorrect stamina cost.")
        self.assertIn(
            "POCKET_LINT", gordon.inventory, "Gordon did not acquire the rummaged item."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Rummaging correctly checked ATP/Stamina bounds before yielding loot.{Prisma.RST}"
        )


class TestLexicalSystems(unittest.TestCase):
    def setUp(self):
        self.store = LexiconStore()
        self.store.VOCAB["sentiment_pos"] = {"good", "joy", "bright"}
        self.store.VOCAB["sentiment_neg"] = {"bad", "pain", "dark"}
        self.store.VOCAB["sentiment_negators"] = {"not", "never", "no"}
        self.store.VOCAB["heavy"] = {"lead", "iron", "rock"}
        self.store.VOCAB["kinetic"] = {"dash", "run", "speed"}
        self.store.SOLVENTS = {"the", "a", "an", "is"}
        for cat, words in self.store.VOCAB.items():
            for w in words:
                self.store._index_word(w, cat)
        self.analyzer = LinguisticAnalyzer(self.store)

    def test_pinker_viscosity_and_turbulence(self):
        print(
            f"\n{Prisma.MAG}[PINKER] Testing Phonetic Viscosity & Turbulence...{Prisma.RST}"
        )
        visc_plosive = self.analyzer.measure_viscosity("kbdgpt")
        visc_liquid = self.analyzer.measure_viscosity("flowery")
        self.assertGreater(visc_plosive, 0.0, "Plosive viscosity failed to calculate.")
        self.assertGreater(visc_liquid, 0.0, "Liquid viscosity failed to calculate.")
        turb_low = self.analyzer.get_turbulence(
            ["cat", "dog", "bat"]
        )
        turb_high = self.analyzer.get_turbulence(
            ["a", "hippopotamus", "is", "large"]
        )
        self.assertEqual(
            turb_low, 0.0, "Turbulence should be 0 for words of equal length."
        )
        self.assertGreater(
            turb_high, 0.0, "Turbulence failed to detect length variance."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Phonetic viscosity and length-variance turbulence mathematically sound.{Prisma.RST}"
        )

    def test_schur_valence_and_negation(self):
        print(f"\n{Prisma.VIOLET}[SCHUR] Testing Sentiment & Negation...{Prisma.RST}")
        val_pos = self.analyzer.measure_valence(["good", "joy"])
        self.assertGreater(val_pos, 0.0, "Failed to detect positive valence.")
        val_neg = self.analyzer.measure_valence(["bad", "pain"])
        self.assertLess(val_neg, 0.0, "Failed to detect negative valence.")
        val_negated = self.analyzer.measure_valence(["not", "good"])
        self.assertLess(
            val_negated, 0.0, "Negator failed to invert positive sentiment."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Valence logic correctly handled baseline and negated sentiments.{Prisma.RST}"
        )

    def test_fuller_vector_mapping(self):
        print(f"\n{Prisma.CYN}[FULLER] Testing Lexical Vectorization...{Prisma.RST}")
        vector = self.analyzer.vectorize("lead run lead")
        self.assertIn("STR", vector, "Vector failed to map 'heavy' to STR.")
        self.assertIn("VEL", vector, "Vector failed to map 'kinetic' to VEL.")
        self.assertGreater(
            vector["STR"], vector["VEL"], "Proportional vector mapping failed."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Words successfully mapped to dimensional vectors (STR, VEL).{Prisma.RST}"
        )

    def test_meadows_semantic_field_flux(self):
        print(f"\n{Prisma.YEL}[MEADOWS] Testing Semantic Field Momentum...{Prisma.RST}")
        field = SemanticField(self.analyzer)
        field.update("lead iron rock")
        self.assertEqual(field.momentum, 0.0, "Initial momentum should be 0.")
        field.update("dash run speed")
        self.assertGreater(
            field.momentum, 0.0, "Semantic shift failed to generate momentum."
        )
        atmosphere = field.get_atmosphere()
        self.assertTrue(
            "Volatile" in atmosphere or "Stable" in atmosphere,
            "Failed to generate atmosphere string.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Semantic Field correctly accumulated flux momentum across turns.{Prisma.RST}"
        )

    def test_pinker_hive_learning(self):
        print(f"\n{Prisma.MAG}[PINKER] Testing Hive Vocabulary Learning...{Prisma.RST}")
        taught = self.store.teach("neologism", "abstract", tick=1)
        self.assertTrue(taught, "Store refused to learn a new word.")
        abstract_words = self.store.get_raw("abstract")
        self.assertIn(
            "neologism",
            abstract_words,
            "Learned word not returned in category raw fetch.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Hive memory successfully integrated and retrieved new vocabulary.{Prisma.RST}"
        )


class TestDriversAndPersonas(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()

    def test_meadows_enneagram_hysteresis(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Enneagram Persona Hysteresis...{Prisma.RST}"
        )
        driver = EnneagramDriver(self.events)
        phys_clarence = {"narrative_drag": 10.0, "kappa": 0.9, "voltage": 1.0}
        persona, state, reason = driver.decide_persona(phys_clarence)
        self.assertEqual(
            driver.pending_persona, "CLARENCE", "Clarence not set as pending."
        )
        self.assertEqual(
            driver.current_persona,
            "NARRATOR",
            "Persona shifted without hysteresis delay.",
        )
        for _ in range(driver.HYSTERESIS_THRESHOLD):
            persona, state, reason = driver.decide_persona(phys_clarence)
        self.assertEqual(
            driver.current_persona,
            "CLARENCE",
            "Persona failed to shift after hysteresis met.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Persona shifting correctly delayed by hysteresis threshold.{Prisma.RST}"
        )

    def test_pinker_soul_driver_influence(self):
        print(f"\n{Prisma.MAG}[PINKER] Testing Soul Archetype Influence...{Prisma.RST}")
        mock_soul = MagicMock()
        mock_soul.archetype = "THE POET"
        mock_soul.paradox_accum = 0.0
        mock_soul.anchor.dignity_reserve = 100.0
        sd = SoulDriver(mock_soul)
        influence = sd.get_influence()
        self.assertGreater(
            influence.get("NATHAN", 0.0), 0.5, "Poet failed to influence Nathan."
        )
        self.assertGreater(
            influence.get("JESTER", 0.0), 0.2, "Poet failed to influence Jester."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Soul Archetype successfully injected weighted influence into persona pool.{Prisma.RST}"
        )

    @patch("bone_lexicon.LexiconService.get")
    def test_fuller_liminal_and_syntax_analysis(self, mock_lex_get):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Liminal & Syntax Module Calculus...{Prisma.RST}"
        )
        mock_lex_get.side_effect = lambda cat: (
            {"void"} if cat == "liminal" else {"bureaucratic"}
        )
        lim_mod = LiminalModule()
        syn_mod = SyntaxModule()
        lambda_val = lim_mod.analyze("staring into the void", {"PSI": 1.0})
        self.assertGreater(
            lambda_val, 0.0, "Liminal module failed to detect 'void' and PSI."
        )
        omega_val = syn_mod.analyze("bureaucratic establishment", narrative_drag=10.0)
        self.assertGreater(
            omega_val,
            0.8,
            "Syntax module failed to increase Omega under high drag and length.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Modifiers correctly calculated Lambda (Liminal) and Omega (Syntax) values.{Prisma.RST}"
        )

    @patch("bone_drivers.LexiconService.get")
    def test_schur_vsl_consultant_prompt_injection(self, mock_lex_get):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing VSL Hypervisor Prompt Injection...{Prisma.RST}"
        )
        mock_lex_get.return_value = set()
        consultant_coding = BoneConsultant()
        consultant_coding.update_coordinates("[MOD:CODING]")
        prompt_coding = consultant_coding.get_system_prompt()
        self.assertIn(
            "SLASH_COUNCIL",
            prompt_coding,
            "System prompt missing SLASH_COUNCIL directive.",
        )
        consultant_liminal = BoneConsultant()
        consultant_liminal.update_coordinates("[VSL_LIMINAL]")
        prompt_liminal = consultant_liminal.get_system_prompt()
        self.assertIn(
            "THE REVENANT", prompt_liminal, "System prompt missing Revenant archetype."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: VSL Hypervisor successfully prioritized and injected specific mode prompts.{Prisma.RST}"
        )


class TestDeepLexicon(unittest.TestCase):
    def setUp(self):
        self.store = LexiconStore()
        self.store.VOCAB["heavy"] = {"lead", "iron", "stone"}
        self.store.VOCAB["kinetic"] = {"dash", "bolt", "rush"}
        self.store.VOCAB["sentiment_pos"] = {"joy", "bright"}
        self.store.VOCAB["sentiment_neg"] = {"dark", "pain"}
        self.store.VOCAB["sentiment_negators"] = {"not", "never"}
        for cat, words in self.store.VOCAB.items():
            for w in words:
                self.store._index_word(w, cat)

        self.analyzer = LinguisticAnalyzer(self.store)

    def test_pinker_viscosity_calculus(self):
        print(f"\n{Prisma.MAG}[PINKER] Testing Viscosity Calculus...{Prisma.RST}")
        visc_iron = self.analyzer.measure_viscosity("iron")
        visc_plosive = self.analyzer.measure_viscosity("btkp")
        self.assertGreater(
            visc_plosive,
            visc_iron,
            "Phonetic plosives should be more viscous than liquids.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Phonetic viscosity correctly weighted plosives over liquids.{Prisma.RST}"
        )

    def test_schur_valence_negation_complex(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Complex Valence Negation...{Prisma.RST}"
        )
        valence = self.analyzer.measure_valence(["not", "joy"])
        self.assertLess(valence, 0.0, "Negator failed to invert positive valence.")
        self.assertEqual(valence, -0.5, "Negation attenuation math failed.")
        print(
            f"{Prisma.GRN}   >>> PASS: Valence logic correctly handled the 'not joy' inversion.{Prisma.RST}"
        )

    def test_meadows_semantic_field_dynamics(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Semantic Field Momentum & Flux...{Prisma.RST}"
        )
        field = SemanticField(self.analyzer)
        field.update("lead iron stone")
        initial_vec = field.current_vector.copy()
        self.assertIn("STR", initial_vec, "Failed to establish initial STR vector.")
        field.update("dash bolt rush")
        self.assertGreater(
            field.momentum, 0.0, "Semantic shift failed to generate momentum."
        )
        self.assertIn("VEL", field.current_vector, "Vector failed to shift to VEL.")
        self.assertGreater(
            field.current_vector["STR"],
            0.0,
            "Blended vector lost all previous state too quickly.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Semantic Field correctly blended states and tracked momentum flux.{Prisma.RST}"
        )

    def test_fuller_phonetic_classification(self):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Phonetic Auto-Classification...{Prisma.RST}"
        )
        cat, score = self.analyzer.classify_word("kbdgpt")
        self.assertEqual(
            cat, "heavy", "Dense plosive string failed to auto-classify as 'heavy'."
        )
        cat_v, score_v = self.analyzer.classify_word("lalala")
        self.assertEqual(
            cat_v, "play", "Vowel-rich string failed to auto-classify as 'play'."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Phonetic density correctly categorized unknown words.{Prisma.RST}"
        )


class TestLexicalSubstrate(unittest.TestCase):
    def setUp(self):
        self.store = LexiconStore()
        self.store.VOCAB["heavy"] = {"stone", "iron", "lead"}
        self.store.VOCAB["play"] = {"dance", "sing", "jump"}
        self.store.VOCAB["sentiment_pos"] = {"joy", "bright"}
        self.store.VOCAB["sentiment_negators"] = {"not"}
        self.store.SOLVENTS = {"the", "a"}
        for cat, words in self.store.VOCAB.items():
            for w in words:
                self.store._index_word(w, cat)
        self.analyzer = LinguisticAnalyzer(self.store)

    def test_pinker_viscosity_math(self):
        print(
            f"\n{Prisma.MAG}[PINKER] Testing Viscosity & Phonetic Density...{Prisma.RST}"
        )
        v_heavy = self.analyzer.measure_viscosity("ironstone")
        v_light = self.analyzer.measure_viscosity("a")
        self.assertGreater(v_heavy, v_light, "Phonetic viscosity calculation failed.")
        cat, score = self.analyzer.classify_word("kbdgpt")
        self.assertEqual(
            cat, "heavy", f"Phonetic density failed to classify 'heavy'. Got: {cat}"
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Phonetic math correctly mapped sound to viscosity.{Prisma.RST}"
        )

    def test_schur_valence_negation(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Sentiment Look-behind Negation...{Prisma.RST}"
        )
        val_pure = self.analyzer.measure_valence(["joy"])
        val_neg = self.analyzer.measure_valence(["not", "joy"])
        self.assertGreater(val_pure, 0.0)
        self.assertLess(val_neg, 0.0, "Negator failed to invert sentiment.")
        self.assertEqual(val_neg, -0.5, "Negation attenuation factor incorrect.")
        print(
            f"{Prisma.GRN}   >>> PASS: Valence engine correctly parsed 'not joy' as negative.{Prisma.RST}"
        )

    def test_meadows_field_flux(self):
        print(f"\n{Prisma.YEL}[MEADOWS] Testing Semantic Field Momentum...{Prisma.RST}")
        field = SemanticField(self.analyzer)
        field.update("stone iron lead")
        field.update("dance sing jump")
        field.update("stone iron lead")
        field.update(
            "dance sing jump"
        )
        self.assertGreater(
            field.momentum,
            0.5,
            f"Momentum ({field.momentum:.2f}) failed to breach threshold.",
        )
        self.assertIn(
            "Volatile", field.get_atmosphere(), "Field failed to reach Volatile state."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Semantic Field correctly accumulated momentum across turns.{Prisma.RST}"
        )

    def test_fuller_hive_indexing(self):
        print(
            f"\n{Prisma.CYN}[FULLER] Testing Hive Learning & Reverse Indexing...{Prisma.RST}"
        )
        self.store.teach("neologism", "abstract", tick=1)
        harvested = self.store.harvest("A strange neologism.")
        self.assertIn("abstract", harvested)
        self.assertIn("neologism", harvested["abstract"])
        cats = self.store.get_categories_for_word("neologism")
        self.assertIn("abstract", cats)
        print(
            f"{Prisma.GRN}   >>> PASS: The Hive successfully learned and indexed new vocabulary.{Prisma.RST}"
        )


class TestCosmicPhysics(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()

    def test_pinker_trigram_mapping(self):
        print(f"\n{Prisma.MAG}[PINKER] Testing Trigram & Color Mapping...{Prisma.RST}")
        for dim in ["VEL", "STR", "ENT", "PHI", "PSI", "BET", "E", "DEL"]:
            self.assertIn(dim, TRIGRAM_MAP, f"Missing Trigram mapping for {dim}")
            icon, name, label, color = TRIGRAM_MAP[dim]
            self.assertIsNotNone(icon)
            self.assertIsNotNone(color)
        print(
            f"{Prisma.GRN}   >>> PASS: Core Trigram mapping is complete and color-coded.{Prisma.RST}"
        )

    def test_meadows_zone_inertia(self):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing Zone Inertia & Migration...{Prisma.RST}"
        )
        inertia = ZoneInertia(inertia=0.9)
        physics = {"beta_index": 1.0, "truth_ratio": 0.5}
        cosmic_state = ("STABLE_ORBIT", 0.0, "Orbiting")
        zone, msg = inertia.stabilize("AERIE", physics, cosmic_state)
        self.assertEqual(
            zone, "COURTYARD", "Inertia failed to resist immediate migration."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: ZoneInertia successfully resisted narrative drift.{Prisma.RST}"
        )

    def test_fuller_cosmic_dynamics_manifolds(self):
        print(f"\n{Prisma.CYN}[FULLER] Testing Manifold Field Dynamics...{Prisma.RST}")
        mock_gov = MagicMock()
        mock_gov.regulate.return_value = (0.0, 0.0)
        stabilizer = CycleStabilizer(self.events, mock_gov)

        class MockCtx:
            class MockPhys:
                manifold = "DEFAULT"
                voltage = 18.0
                flow_state = "SUPERCONDUCTIVE"
            physics = MockPhys()

            def log(self, m):
                pass

            def record_flux(self, *args):
                pass

        stabilizer.stabilize(MockCtx(), "TEST_PHASE")
        mock_gov.recalibrate.assert_called()
        args, _ = mock_gov.recalibrate.call_args
        self.assertEqual(
            args[0],
            18.0,
            "Stabilizer failed to apply Superconductive voltage override.",
        )
        print(
            f"{Prisma.GRN}   >>> PASS: CycleStabilizer correctly handled flow-state manifold overrides.{Prisma.RST}"
        )


class TestVillageSocialLogic(unittest.TestCase):
    def setUp(self):
        self.events = EventBus()

    def test_schur_zen_garden_stillness(self):
        print(
            f"\n{Prisma.VIOLET}[SCHUR] Testing Zen Garden Stillness Streaks...{Prisma.RST}"
        )
        garden = ZenGarden(self.events)
        class StablePhys:
            voltage = 5.0
            narrative_drag = 1.0
        for i in range(5):
            boost, msg = garden.raking_the_sand(StablePhys(), {})
        self.assertEqual(garden.stillness_streak, 5, "Zen streak failed to increment.")
        self.assertEqual(
            garden.pebbles_collected, 1, "Failed to collect pebble on streak 5."
        )
        self.assertIsNotNone(msg, "Koan message missing on streak milestone.")

        class UnstablePhys:
            voltage = 25.0
            narrative_drag = 1.0

        garden.raking_the_sand(UnstablePhys(), {})
        self.assertEqual(
            garden.stillness_streak, 0, "Zen streak failed to reset on turbulence."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Zen Garden correctly rewarded poise and reset on chaos.{Prisma.RST}"
        )

    @patch("bone_core.LoreManifest.get_instance")
    def test_fuller_bureau_auditing(self, mock_lore):
        print(f"\n{Prisma.CYN}[FULLER] Testing Bureau Style Audits...{Prisma.RST}")
        mock_lore.return_value.get.return_value = {
            "PATTERNS": [
                {
                    "name": "EXCESSIVE_DOTS",
                    "regex": r"\.\.\.\.",
                    "error_msg": "Too many dots.",
                    "tax": 10.0,
                }
            ]
        }
        with patch("bone_config.BoneConfig.BUREAU") as mock_cfg:
            mock_cfg.MIN_WORD_COUNT = 3  # Ensure 4+ words always pass
            mock_cfg.MIN_HEALTH_TO_AUDIT = 20
            bureau = TheBureau()
            class CriminalPhys:
                voltage = 5.0
                raw_text = "Wait for the dots...."
                clean_words = ["wait", "for", "the", "dots"]
            result = bureau.audit(CriminalPhys(), {"health": 100.0})
            self.assertIsNotNone(
                result,
                "Bureau failed to detect a Style Violation (Check word count/config).",
            )
            self.assertEqual(
                result["atp_gain"], -10.0, "Bureau failed to levy the correct tax."
            )
            self.assertIn(
                "EXCESSIVE_DOTS", result["ui"], "Violation name missing from UI report."
            )
        print(
            f"{Prisma.GRN}   >>> PASS: The Bureau successfully identified a style crime and levied a tax.{Prisma.RST}"
        )

    @patch("bone_lexicon.LexiconService.get")
    def test_meadows_folly_digestion(self, mock_lex_get):
        print(
            f"\n{Prisma.YEL}[MEADOWS] Testing The Folly (ATP Metabolism)...{Prisma.RST}"
        )
        mock_lex_get.side_effect = lambda cat: {"iron"} if cat == "heavy" else set()
        folly = TheFolly()
        mode, msg, yield_atp, loot = folly.grind_the_machine(10.0, ["iron"], {})
        self.assertEqual(
            mode, "MEAT_GRINDER", "Folly failed to identify heavy word as meat."
        )
        self.assertGreater(yield_atp, 0.0, "Folly generated no ATP from meat.")
        mode_2, msg_2, yield_2, loot_2 = folly.grind_the_machine(10.0, ["iron"], {})
        self.assertEqual(
            mode_2, "REGURGITATION", "Folly failed to detect repeated word."
        )
        self.assertLess(yield_2, 0.0, "Folly failed to penalize repetition.")
        print(
            f"{Prisma.GRN}   >>> PASS: The Folly enforced linguistic variety via metabolic penalties.{Prisma.RST}"
        )

    def test_fuller_kintsugi_restoration(self):
        print(f"\n{Prisma.MAG}[FULLER] Testing Kintsugi Repair Pathways...{Prisma.RST}")
        kintsugi = KintsugiProtocol()
        kintsugi.active_koan = "The crack lets the light in."
        trauma = {"SEPTIC": 5.0}
        class AlchemicalPhys:
            voltage = 20.0
            raw_text = "dance jump bright"
        with patch(
            "bone_lexicon.LexiconService.sanitize",
            return_value=["dance", "jump", "bright"],
        ), patch(
            "bone_lexicon.LexiconService.get", return_value={"dance", "jump", "bright"}
        ):
            result = kintsugi.attempt_repair(AlchemicalPhys(), trauma)
            self.assertTrue(result["success"])
            self.assertIn(
                "ALCHEMY", result["msg"], "Failed to trigger Alchemy pathway."
            )
            self.assertLess(trauma["SEPTIC"], 5.0, "Trauma was not reduced by repair.")
            self.assertGreater(
                result.get("atp_gain", 0), 0, "Alchemy did not grant ATP boost."
            )
        print(
            f"{Prisma.GRN}   >>> PASS: Kintsugi transmuted trauma into fuel via the Alchemy pathway.{Prisma.RST}"
        )

    def test_hauntings_in_limbo(self):
        print(f"\n{Prisma.GRY}[MEADOWS] Testing Limbo Ghost Integration...{Prisma.RST}")
        limbo = LimboLayer()
        limbo.ghosts.append("👻SEPTIC_ECHO")
        limbo.haunt_chance = 1.0
        text = "I am walking."
        haunted_text = limbo.haunt(text)
        self.assertIn(
            "👻SEPTIC_ECHO", haunted_text, "Limbo failed to inject a ghost echo."
        )
        print(
            f"{Prisma.GRN}   >>> PASS: Limbo successfully haunted the narrative string.{Prisma.RST}"
        )


if __name__ == "__main__":
    print(f"{Prisma.WHT}┌──────────────────────────────────────────┐{Prisma.RST}")
    print(f"{Prisma.WHT}│ BONEAMANITA UNIFIED DIAGNOSTIC SUITE     │{Prisma.RST}")
    print(f"{Prisma.WHT}│ AUDITING: LORE, PHYSICS, MIND, INVENTORY │{Prisma.RST}")
    print(f"{Prisma.WHT}└──────────────────────────────────────────┘{Prisma.RST}")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestBedrockIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestSomaticPhysics))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitionAndInventory))
    suite.addTests(loader.loadTestsFromTestCase(TestLiveFireIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticEndocrine))
    suite.addTests(loader.loadTestsFromTestCase(TestMechanicalSystems))
    suite.addTests(loader.loadTestsFromTestCase(TestMycelialEcosystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSoulDynamics))
    suite.addTests(loader.loadTestsFromTestCase(TestSlashAkashic))
    suite.addTests(loader.loadTestsFromTestCase(TestVillageEcosystem))
    suite.addTests(loader.loadTestsFromTestCase(TestGordonInventory))
    suite.addTests(loader.loadTestsFromTestCase(TestLexicalSystems))
    suite.addTests(loader.loadTestsFromTestCase(TestDriversAndPersonas))
    suite.addTests(loader.loadTestsFromTestCase(TestDeepLexicon))
    suite.addTests(loader.loadTestsFromTestCase(TestLexicalSubstrate))
    suite.addTests(loader.loadTestsFromTestCase(TestCosmicPhysics))
    suite.addTests(loader.loadTestsFromTestCase(TestVillageSocialLogic))
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    if result.wasSuccessful():
        print(
            f"\n{Prisma.GRN}*** ALL SYSTEMS NOMINAL. SLASH COMPLIANCE VERIFIED. ***{Prisma.RST}"
        )
    else:
        print(
            f"\n{Prisma.RED}*** SYSTEM FAILURE DETECTED. CHECK STACK TRACE. ***{Prisma.RST}"
        )
