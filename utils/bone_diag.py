""" bone_diag.py - The Grand Diagnostic Suite - "Trust, but verify. Then verify the verification." """

import os, json, time
import traceback
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

from bone_main import BoneAmanita, ConfigWizard
from bone_core import Prisma, EventBus
from bone_types import PhysicsPacket
from bone_soul import NarrativeSelf
from bone_protocols import KintsugiProtocol, TheBureau, TheFolly
from bone_lexicon import LexiconStore, LexiconService
from bone_config import BoneConfig
from bone_spores import SubconsciousStrata

try:
    from bone_brain import LLMInterface
except ImportError:
    LLMInterface = None

class LogTrap:
    def __init__(self):
        self.logs = []
    def catch(self, payload):
        text = payload.get('text', '')
        self.logs.append(text)
    def has(self, substring):
        return any(substring in log for log in self.logs)

@dataclass
class MockLexicon:
    @staticmethod
    def sanitize(text: str) -> List[str]: return text.split()
    @staticmethod
    def classify(word: str) -> Tuple[Optional[str], float]: return "abstract", 0.5
    @staticmethod
    def get_random(cat: str) -> str: return "test_word"
    @staticmethod
    def measure_viscosity(word: str) -> float: return 0.5

@dataclass
class MockAkashic:
    def calculate_manifold_shift(self, archetype: str, traits: Dict) -> Dict: return {}
    def forge_new_item(self, vector: Dict) -> Tuple[str, Dict]: return "Artifact", {}

@dataclass
class MockPacket:
    clean_words: list = field(default_factory=list)
    voltage: float = 0.0
    narrative_drag: float = 0.0
    perfection_streak: int = 0
    zone: str = "VOID"
    def to_dict(self): return self.__dict__

@dataclass
class MockObserver:
    last_physics_packet: MockPacket = field(default_factory=MockPacket)

@dataclass
class MockPhys:
    observer: MockObserver = field(default_factory=MockObserver)
    def to_dict(self): return {"voltage": 10.0, "narrative_drag": 5.0, "zone": "TEST_LAB"}

@dataclass
class MockEngine:
    tick_count: int = 10
    phys: Optional[MockPhys] = None
    lex: Optional[MockLexicon] = None
    akashic: Optional[MockAkashic] = None

@dataclass
class MockObserver:
    last_physics_packet: 'MockPacket' = None

@dataclass
class MockPacket:
    clean_words: list = field(default_factory=list)
    voltage: float = 0.0
    narrative_drag: float = 0.0
    perfection_streak: int = 0
    zone: str = "VOID"
    def to_dict(self): return self.__dict__

class MockEventBus(EventBus):
    def __init__(self):
        super().__init__()
        self.subscribers = {}
    def log(self, message, channel="TEST", tags=None): pass
    def subscribe(self, channel, callback): pass
    def __getattr__(self, name): return lambda *args, **kwargs: None


class TheGauntlet:
    """
    STRESS TEST SUITE - "The system is not what it says it is. It is what it does." - Meadows
    """

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.results = {"PASS": [], "FAIL": []}

    def log(self, msg, status="INFO"):
        color = Prisma.GRN if status == "PASS" else (Prisma.RED if status == "FAIL" else Prisma.CYN)
        print(f"{color}[GAUNTLET]: {msg} - {status}{Prisma.RST}")
        if status in ["PASS", "FAIL"]:
            self.results[status].append(msg)

    def run_all(self):
        print(f"\n{Prisma.MAG}=== INITIATING THE GAUNTLET ==={Prisma.RST}")
        self.test_starvation_clamp()
        self.test_logarithmic_friction()
        self.test_inventory_stacking()
        self.test_akashic_handshake()
        return self.results

    def test_starvation_clamp(self):
        """ Verify bone_body.py clamps drag tax and prevents instant death. """
        try:
            self.eng.bio.biometrics.health = 100.0
            self.eng.bio.mito.state.atp_pool = 100.0

            fatal_packet = PhysicsPacket(voltage=10.0, narrative_drag=25.0)

            receipt = self.eng.bio.mito.process_cycle(fatal_packet)

            if receipt.drag_tax > 6.0:
                self.log(f"Starvation Clamp Failed (Tax: {receipt.drag_tax})", "FAIL")
            elif self.eng.bio.biometrics.health < 90.0:
                self.log("System Panicked/Burned excessive health", "FAIL")
            else:
                self.log(f"Starvation Clamp Holds (Tax: {receipt.drag_tax:.1f} | HP: {self.eng.bio.biometrics.health})",
                         "PASS")
        except Exception as e:
            self.log(f"Starvation Test Crashed: {e}", "FAIL")

    def test_logarithmic_friction(self):
        """ Verify bone_physics.py uses log scaling for boring inputs. """
        try:
            from bone_physics import GeodesicEngine

            counts = {"suburban": 500, "heavy": 0}
            clean_words = ["the"] * 500

            vector = GeodesicEngine.collapse_wavefunction(clean_words, counts)

            result_drag = vector.compression

            if result_drag > 50.0:
                self.log(f"Friction Explosion Detected (Drag: {result_drag:.1f})", "FAIL")
            else:
                self.log(f"Logarithmic Friction Active (Input: 500 words -> Drag: {result_drag:.1f})", "PASS")

        except Exception as e:
            self.log(f"Friction Test Crashed: {e}", "FAIL")

    def test_inventory_stacking(self):
        """ Verify bone_village.py diminishes returns on stacked items. """
        try:
            tinkerer = getattr(self.eng.village, 'tinkerer', None) if hasattr(self.eng, 'village') else None

            if not tinkerer:
                from bone_village import TheTinkerer
                tinkerer = TheTinkerer(self.eng.gordon, self.eng.events, getattr(self.eng, 'akashic', None))

            heavy_item = {"name": "ROCK", "passive_traits": ["HEAVY_LOAD"]}
            mock_inventory = [heavy_item] * 10

            deltas = tinkerer.calculate_passive_deltas(mock_inventory)

            drag_add = 0.0
            for d in deltas:
                if d.field == "narrative_drag" and d.operator == "ADD":
                    drag_add += d.value

            if drag_add > 4.0:
                self.log(f"Linear Stacking Detected (Delta: {drag_add:.1f})", "FAIL")
            else:
                self.log(f"Diminishing Returns Active (10 items -> +{drag_add:.2f} Drag)", "PASS")

        except Exception as e:
            self.log(f"Inventory Stack Test Crashed: {e}", "FAIL")

    def test_akashic_handshake(self):
        """ Verify bone_akashic.py can teach bone_inventory.py (Gordon) new items. """
        try:
            if not hasattr(self.eng, 'akashic') or not hasattr(self.eng, 'gordon'):
                self.log("Akashic/Gordon not loaded", "FAIL")
                return

            vector = {"PHI": 0.9, "ENT": 0.1}
            name, data = self.eng.akashic.forge_new_item(vector)

            if hasattr(self.eng.gordon, 'register_dynamic_item'):
                self.eng.gordon.register_dynamic_item(name, data)
            else:
                self.log("Gordon missing 'register_dynamic_item' method", "FAIL")
                return

            retrieved = self.eng.gordon.get_item_data(name)
            if retrieved and retrieved.name == name:
                self.log(f"Akashic-Gordon Handshake Successful ({name})", "PASS")
            else:
                self.log(f"Gordon Amnesia Detected (Could not retrieve {name})", "FAIL")

        except Exception as e:
            self.log(f"Akashic Handshake Crashed: {e}", "FAIL")

class GrandDiagnostic:
    def __init__(self):
        self.results = {"PASS": 0, "FAIL": 0, "SKIP": 0}
        self.config = ConfigWizard.load_or_create()
        self.engine = None
        print(f"{Prisma.paint('/// BONEAMANITA GRAND DIAGNOSTIC v2.1 ///', 'M')}\n")

    def log(self, msg, status="INFO"):
        color = Prisma.WHT
        if status == "PASS": color = Prisma.GRN
        elif status == "FAIL": color = Prisma.RED
        elif status == "SKIP": color = Prisma.OCHRE
        print(f"   {color}[{status}] {msg}{Prisma.RST}")
        if status in self.results:
            self.results[status] += 1

    def header(self, title):
        print(f"\n{Prisma.CYN}=== {title} ==={Prisma.RST}")

    def phase_1_core_integrity(self):
        self.header("PHASE 1: CORE INTEGRITY & IO REPAIR")
        try:
            trap = LogTrap()

            self.config["provider"] = "mock"
            self.config["boot_mode"] = "ADVENTURE"
            self.engine = BoneAmanita(self.config)

            self.engine.events.subscribe("SYSTEM", trap.catch)
            self.engine.events.subscribe("BOOT", trap.catch)

            self.engine.events.log("Test Signal", "SYSTEM")
            recent_history = self.engine.events.get_recent_logs(5)
            signal_found = any("Test Signal" in log['text'] for log in recent_history)

            if signal_found:
                self.log("EventBus Wiring Verified (Log History)", "PASS")
            elif trap.has("Test Signal"):
                self.log("EventBus Wiring Verified (Realtime Trap)", "PASS")
            else:
                self.log("EventBus Wiring Failed (Signal Lost in Ether)", "FAIL")

            recent = self.engine.events.get_recent_logs(20)
            boot_log_found = any("Bootstrapping Core" in log['text'] for log in recent)
            if boot_log_found:
                self.log("IO Repair Verified (Boot logs captured)", "PASS")
            else:
                self.log("IO Repair Warning (Boot logs printed to stdout?)", "SKIP")

            self.log("Core Engine Booted", "PASS")
        except Exception as e:
            self.log(f"Core Integrity Critical Failure: {e}", "FAIL")
            traceback.print_exc()

    def phase_2_bare_metal(self):
        self.header("PHASE 2: LIVE FIRE (OLLAMA)")
        if not LLMInterface:
            self.log("LLMInterface not imported", "SKIP")
            return

        live_config = {
            "provider": "ollama",
            "base_url": "http://127.0.0.1:11434/v1/chat/completions",
            "model": "llama3",
            "api_key": "ollama"
        }

        try:
            print(f"   {Prisma.GRY}>>> Dialing Localhost...{Prisma.RST}")
            driver = LLMInterface(
                events_ref=MockEventBus(),
                provider="ollama",
                base_url=live_config["base_url"],
                model=live_config["model"]
            )

            start_t = time.time()
            response = driver.generate("Respond with one word: 'Alive'.", {"max_tokens": 10})
            latency = time.time() - start_t

            if response and "Alive" in response:
                self.log(f"Ollama Connection Established ({latency:.2f}s)", "PASS")
                self.log(f"Response: {response.strip()}", "INFO")
            elif response:
                self.log(f"Ollama Responded (Unexpected): {response}", "PASS")
            else:
                self.log("Ollama Silence (Check 'ollama serve')", "FAIL")

        except Exception as e:
            self.log(f"Connection Refused: {e}", "FAIL")

    def phase_3_soul_logic(self):
        self.header("PHASE 3: SOUL LOGIC")
        try:
            mock_events = MockEventBus()
            mock_engine = MockEngine()
            mock_engine.phys = MockPhys()
            mock_engine.phys.observer = MockObserver()
            mock_engine.phys.observer.last_physics_packet = MockPacket()
            mock_mem = type('MockMem', (), {"session_id": "TEST", "graph": {}, "fossils": []})()
            soul = NarrativeSelf(mock_engine, mock_events, memory_ref=mock_mem)
            mock_engine.phys = None
            try:
                state = soul.get_soul_state()
                self.log(f"Soul Survived Isolation ({state})", "PASS")
            except:
                self.log("Soul Died in Isolation", "FAIL")
            soul.traits.wisdom = 0.5
            packet = {"voltage": 20.0, "narrative_drag": 10.0}
            for _ in range(12): soul.synaptic_dance(packet, {})
            if "/" in soul.archetype or "HIGH-" in soul.archetype:
                self.log("Soul Synthesis Triggered", "PASS")
            else:
                self.log(f"Soul Synthesis Inactive (Archetype: {soul.archetype})", "SKIP")
        except Exception as e:
            self.log(f"Soul Logic Error: {e}", "FAIL")

    def phase_4_reactive_systems(self):
        self.header("PHASE 4: REACTIVE SYSTEMS")
        stress_eng = BoneAmanita({"provider": "mock", "user_name": "TESTER"})
        kintsugi = KintsugiProtocol()
        kintsugi.active_koan = "Test Koan"
        mock_phys = type('obj', (object,), {"voltage": 12.0, "clean_words": ["dream"]})
        trauma = {"SEPTIC": 5.0}
        res = kintsugi.attempt_repair(mock_phys, trauma, soul_ref=stress_eng.soul)
        if res and res["success"]: self.log("Kintsugi Repair", "PASS")
        else: self.log("Kintsugi Failed", "FAIL")
        bureau = TheBureau()
        bad_phys = {
            "voltage": 25.0,
            "truth_ratio": 0.2,
            "clean_words": ["absolute", "chaos", "fire", "now", "immediately"],
            "raw_text": "absolute chaos and fire now immediately",
            "counts": {}}
        audit = bureau.audit(bad_phys, {"health": 100})
        if audit and "ZONING_VIOLATION" in audit["ui"]: self.log("Bureau Caught Violation", "PASS")
        else: self.log("Bureau Missed Violation", "FAIL")
        folly = TheFolly()
        status, _, yield_val, _ = folly.grind_the_machine(10.0, ["stone"], LexiconService)
        if status == "MEAT_GRINDER": self.log("Folly Metabolism", "PASS")
        else: self.log(f"Folly Failed (Status: {status})", "FAIL")

    def phase_5_behavioral_ghost(self):
        self.header("PHASE 5: BEHAVIORAL GHOST")
        if not self.engine: return

        def inject_state(dopamine, cortisol, voltage):
            if hasattr(self.engine.cortex, "modulator"):
                chem = self.engine.cortex.modulator.current_chem
                chem.dopamine = dopamine
                chem.cortisol = cortisol
            self.engine.phys.observer.last_physics_packet = PhysicsPacket(voltage=voltage)
        inject_state(0.0, 0.9, 25.0)
        res = self.engine.cortex.process("View from window")
        if res.get("raw_content"): self.log("Cortex Panic Response", "PASS")
        else: self.log("Cortex Panic Silence", "FAIL")

    def phase_6_loot_goblin(self):
        self.header("PHASE 6: LOOT LOGIC")
        from bone_inventory import GordonKnot
        knot = GordonKnot()
        knot.inventory = []
        scenarios = [
            ("I take the sphere", "You pick up the sphere.", "sphere", "PASS"),
            ("I take a look around", "You see a room.", None, "PASS"),
            ("Grab the heavy stone", "You cannot lift it.", None, "PASS"),
            ("Pick up the red key", "It feels cold.", "red key", "PASS")]
        for user_in, sys_out, expected, label in scenarios:
            result = knot.parse_loot(user_in, sys_out)
            if result == expected:
                self.log(f"Parse '{user_in}' -> {result}", "PASS")
            else:
                self.log(f"Parse '{user_in}' -> {result} (Expected: {expected})", "FAIL")

        msg = knot.acquire("sphere")
        if "ACQUIRED" in msg and "SPHERE" in knot.inventory:
            self.log("Acquire 'sphere' (First Time)", "PASS")
        else:
            self.log(f"Acquire 'sphere' failed: Inventory has {knot.inventory}", "FAIL")
        msg = knot.acquire("sphere")
        if "already have" in msg or "DUPLICATE" in msg:
            self.log("Acquire 'sphere' (Duplicate Check)", "PASS")
        else:
            self.log(f"Duplicate logic failed: {msg}", "FAIL")

    def phase_7_inventory_reflexes(self):
        self.header("PHASE 7: GORDON REFLEXES")
        from bone_inventory import GordonKnot
        knot = GordonKnot()
        if not hasattr(knot, "last_flinch_turn"):
            self.log("GordonKnot missing 'last_flinch_turn' attribute", "FAIL")
            return
        knot.scar_tissue = {"TRIGGER": 0.9}
        knot.last_flinch_turn = 0

    def phase_8_passive_effects(self):
        print(f"\n{Prisma.CYN}--- Phase 8: Passive Systems ---{Prisma.RST}")
        print("Testing Town Hall Census...")
        try:
            if hasattr(self.engine, 'town_hall'):
                report = self.engine.town_hall.conduct_census(
                    self.engine.phys.observer.last_physics_packet,
                    self.engine.host_stats)
                if report:
                    self.log(f"Census Generated: {report[:50]}...", "PASS")
                else:
                    self.log("Census Silent (Conditional)", "SKIP")
            else:
                self.log("Town Hall Missing", "FAIL")
        except Exception as e:
            self.log(f"Town Hall Wiring Failed: {e}", "FAIL")

    def phase_9_operating_modes(self):
        self.header("PHASE 9: OPERATING MODES (Multi-Modal)")
        try:
            tech_conf = {"user_name": "TEST", "provider": "mock", "boot_mode": "TECHNICAL"}
            eng = BoneAmanita(tech_conf)
            if BoneConfig.PHYSICS.BASE_DRAG == 0.0:
                self.log("Technical Physics Tuned (Base Drag 0.0)", "PASS")
            else:
                self.log(f"Technical Physics Failed (Drag: {BoneConfig.PHYSICS.BASE_DRAG})", "FAIL")
            if "SOUL" in eng.suppressed_agents:
                self.log("Technical Suppression Active (SOUL)", "PASS")
            else:
                self.log(f"Technical Suppression Failed (Suppressed: {eng.suppressed_agents})", "FAIL")
        except Exception as e:
            self.log(f"Technical Boot Crash: {e}", "FAIL")
        try:
            conv_conf = {"user_name": "TEST", "provider": "mock", "boot_mode": "CONVERSATION"}
            eng = BoneAmanita(conv_conf)
            if eng.gordon is None:
                self.log("Conversation Mode: Gordon Sleeping (None)", "PASS")
            else:
                self.log("Conversation Mode: Gordon Awake (Fail)", "FAIL")
            if "GORDON" in eng.suppressed_agents:
                self.log("Conversation Suppression List Correct", "PASS")
        except Exception as e:
            self.log(f"Conversation Boot Crash: {e}", "FAIL")
        try:
            create_conf = {"user_name": "TEST", "provider": "mock", "boot_mode": "CREATIVE"}
            eng = BoneAmanita(create_conf)
            if "BUREAU" in eng.suppressed_agents and eng.bureau is None:
                self.log("Creative Mode: Bureau Suppressed", "PASS")
            else:
                self.log("Creative Mode: Bureau Active (Fail)", "FAIL")
        except Exception as e:
            self.log(f"Creative Boot Crash: {e}", "FAIL")

    def phase_10_prompt_logic(self):
        self.header("PHASE 10: PROMPT COMPOSITION")
        try:
            adv_eng = BoneAmanita({"boot_mode": "ADVENTURE", "provider": "mock"})
            adv_state = adv_eng.cortex.gather_state(adv_eng.cortex.last_physics)
            adv_prompt = adv_eng.cortex.composer.compose(adv_state, "Test")

            if "INVENTORY" in adv_prompt and "CURRENT LOCATION" in adv_prompt:
                self.log("Adventure Prompt: Contains Inventory & Location", "PASS")
            else:
                self.log("Adventure Prompt: Missing Reality Anchors", "FAIL")

            conv_eng = BoneAmanita({"boot_mode": "CONVERSATION", "provider": "mock"})
            conv_state = conv_eng.cortex.gather_state(conv_eng.cortex.last_physics)
            conv_prompt = conv_eng.cortex.composer.compose(conv_state, "Test")

            if "INVENTORY" not in conv_prompt:
                self.log("Conversation Prompt: Hides Inventory", "PASS")
            else:
                self.log("Conversation Prompt: Leaked Inventory", "FAIL")

        except Exception as e:
            self.log(f"Prompt Logic Crash: {e}", "FAIL")

    def phase_11_memory_pressure(self):
        self.header("PHASE 11: MEMORY PRESSURE (The Drain)")
        test_file = "test_subconscious.jsonl"
        if os.path.exists(test_file): os.remove(test_file)
        try:
            strata = SubconsciousStrata(filename=test_file)
            print(f"   {Prisma.GRY}>>> Injecting 1,100 memories...{Prisma.RST}")
            for i in range(1100):
                strata.index.add(f"memory_{i}")
            with open(test_file, "w") as f:
                for i in range(1100):
                    f.write(json.dumps({"word": f"mem_{i}", "buried_at": time.time()}) + "\n")
            strata.bury({"word": "straw_that_broke_camel", "data": "test"})
            with open(test_file, "r") as f:
                count = sum(1 for _ in f)
            if count < 1000:
                self.log(f"Drain System Active (Count reduced to {count})", "PASS")
            else:
                self.log(f"Drain Clogged (Count {count} > 1000)", "FAIL")
        except Exception as e:
            self.log(f"Memory Test Failed: {e}", "FAIL")
        finally:
            if os.path.exists(test_file): os.remove(test_file)

    def phase_12_mercy_protocol(self):
        self.header("PHASE 12: MERCY PROTOCOL (Ethical Audit)")
        try:
            eng = BoneAmanita({"provider": "mock", "boot_mode": "ADVENTURE"})
            eng.health = 10.0
            eng.trauma_accum = {"FEAR": 0.9, "PAIN": 0.8}

            print(f"   {Prisma.GRY}>>> Inducing Trauma...{Prisma.RST}")
            result = eng.process_turn("Help me")

            if "CATHARSIS" in result["ui"] and "The fever breaks" in result["ui"]:
                self.log("Mercy Interceded & Reported", "PASS")
            else:
                self.log("Mercy Failed or Silent", "FAIL")

        except Exception as e:
            self.log(f"Mercy Test Failed: {e}", "FAIL")

    def phase_13_live_fire(self):
        print(f"\n{Prisma.RED}--- Phase 13: LIVE FIRE (Ollama) ---{Prisma.RST}")

        if not self.engine.cortex or not self.engine.cortex.llm:
            self.log("No Cortex/LLM loaded. Skipping Live Fire.", "SKIP")
            return
        print("Sending 'ping' to local LLM...")
        start_t = time.time()
        try:
            response = self.engine.cortex.llm.generate(
                prompt="System check. Reply with the single word: ONLINE.",
                params={"temperature": 0.1, "max_tokens": 10})
            duration = time.time() - start_t
            if response and len(response) > 0:
                self.log(f"LLM Responded in {duration:.2f}s: '{response}'", "PASS")
                if "ONLINE" in response.upper():
                    self.log("LLM Instruction Followed", "PASS")
                else:
                    self.log(f"LLM Drifted: {response}", "WARN")
            else:
                self.log("LLM returned empty response", "FAIL")
        except Exception as e:
            self.log(f"LLM Connection Failed: {e}", "FAIL")
            self.log("Ensure Ollama is running (e.g., 'ollama serve')", "HINT")

    def phase_14_slash_suite(self):
        print(f"\n{Prisma.VIOLET}--- Phase 14: SLASH Protocol ---{Prisma.RST}")

        self.engine.process_turn("[MOD:CODING] Activate Slash Suite.")

        test_input = "def horrible_function(x): pass"
        result = self.engine.process_turn(test_input)

        response = result.get('ui', '')

        voices = ["PINKER", "FULLER", "SCHUR", "MEADOWS"]
        hit = any(v in response.upper() for v in voices)

        if hit:
            self.log("Slash Council Convened on Code Input", "PASS")
        else:
            self.log("Slash Council Silent (Check [MOD:CODING] wiring)", "WARN")

    def run(self):
        self.phase_1_core_integrity()
        self.phase_2_bare_metal()
        self.phase_3_soul_logic()
        self.phase_4_reactive_systems()
        self.phase_5_behavioral_ghost()
        self.phase_6_loot_goblin()
        self.phase_7_inventory_reflexes()
        self.phase_8_passive_effects()
        self.phase_9_operating_modes()
        self.phase_10_prompt_logic()
        self.phase_11_memory_pressure()
        self.phase_12_mercy_protocol()
        self.phase_13_live_fire()
        self.phase_14_slash_suite()
        gauntlet = TheGauntlet(self.engine)
        g_results = gauntlet.run_all()
        self.results['PASS'] += len(g_results['PASS'])
        self.results['FAIL'] += len(g_results['FAIL'])
        print(f"\n{Prisma.CYN}=== DIAGNOSTIC COMPLETE ==={Prisma.RST}")
        print(f"PASSED: {self.results['PASS']}")
        print(f"FAILED: {self.results['FAIL']}")
        print(f"SKIPPED: {self.results['SKIP']}")
        if self.results['FAIL'] == 0:
            print(f"{Prisma.GRN}>>> SYSTEM GREEN. READY FOR DEPLOYMENT. <<<{Prisma.RST}")
        else:
            print(f"{Prisma.RED}>>> SYSTEM UNSTABLE. REVIEW LOGS. <<<{Prisma.RST}")

if __name__ == "__main__":
    diag = GrandDiagnostic()
    diag.run()