""" BONEAMANITA 12.5.1 'THE SURGICAL STRIKE'
 Architects: SLASH, KISHO, The BonePoke Gods Humans: Taylor & Edmark """

import os, time, json, uuid, urllib.request, urllib.error, random
from dataclasses import dataclass
from typing import Dict, Any, Optional
from bone_bus import EventBus, Prisma, BoneConfig, SystemHealth, TheObserver, BonePresets
from bone_commands import CommandProcessor
from bone_data import TheAkashicRecord, TheLore
from bone_village import TownHall, DeathGen, TheNavigator, ZenGarden, TheTinkerer
from bone_lexicon import TheLexicon
from bone_inventory import GordonKnot
from bone_telemetry import TelemetryService
from bone_personality import TheFolly, ChorusDriver, KintsugiProtocol, TherapyProtocol, TheBureau
from bone_physics import CosmicDynamics, ZoneInertia
from bone_body import SomaticLoop
from bone_brain import TheCortex, LLMInterface, NoeticLoop
from bone_soul import NarrativeSelf
from bone_architect import BoneArchitect
from bone_cycle import GeodesicOrchestrator
from bone_viewer import Projector, GeodesicRenderer
from bone_translation import SomaticInterface
from bone_council import CouncilChamber
from bone_spores import LiteraryReproduction

@dataclass
class HostStats:
    latency: float
    efficiency_index: float

def bootstrap_systems():
    print(f"{Prisma.GRY}...Bootstrapping Sub-Systems...{Prisma.RST}")
    TheLore.get_instance()

class SessionGuardian:
    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        print(f"{Prisma.paint('>>> BONEAMANITA 12.5.1', 'G')}")
        print(f"{Prisma.paint('System: LISTENING', '0')}")
        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"\n{Prisma.paint('--- SYSTEM HALT ---', 'R')}")
        if exc_type:
            print(f"{Prisma.paint(f'CRITICAL FAILURE: {exc_val}', 'R')}")
            if self.engine_instance and hasattr(self.engine_instance, "events"):
                try:
                    self.engine_instance.events.log(f"CRASH: {exc_val}", "SYS")
                except Exception as e:
                    print(f"{Prisma.paint(f'LOGGING SYSTEM FAILED: {e}', 'R')}")
        try:
            print(f"{Prisma.paint('Initiating Emergency Spore Preservation...', 'Y')}")
            if self.engine_instance:
                exit_cause = "INTERRUPT" if exc_type else "MANUAL"
                result_msg = self.engine_instance.emergency_save(exit_cause=exit_cause)
                color = 'C' if '✔' in result_msg else 'R'
                print(f"{Prisma.paint(result_msg, color)}")
        except Exception as e:
            print(f"FATAL: State corruption during shutdown. {e}")
        print(f"{Prisma.paint('Disconnected.', '0')}")
        return exc_type is KeyboardInterrupt

class ConfigWizard:
    CONFIG_FILE = "bone_config.json"

    @staticmethod
    def load_or_create():
        if os.path.exists(ConfigWizard.CONFIG_FILE):
            try:
                with open(ConfigWizard.CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                print(f"{Prisma.RED}Config corrupt. Re-initializing.{Prisma.RST}")
        return ConfigWizard._run_setup()

    @staticmethod
    def _run_setup():
        print(f"\n{Prisma.CYN}=== BONEAMANITA COLD BOOT SETUP ==={Prisma.RST}")
        print("1. Local (Ollama/LM Studio) [Default]")
        print("2. OpenAI / Cloud")
        print("3. Mock Mode (Simulation)")
        choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        config = {"provider": "mock", "model": "local-model", "user_name": "TRAVELER"}
        if choice == "2":
            config["provider"] = "openai"
            config["api_key"] = input("API Key: ").strip()
            config["model"] = input("Model (e.g., gpt-4): ").strip() or "gpt-4"
        elif choice != "3":
            config["provider"] = "ollama"
            config["base_url"] = "http://127.0.0.1:11434/v1/chat/completions"
            print(f"{Prisma.GRY}(Assuming Ollama on default port){Prisma.RST}")
            config["model"] = input("Model Name (e.g., llama3): ").strip() or "llama3"
        config["user_name"] = input("Designation (User Name): ").strip() or "TRAVELER"
        with open(ConfigWizard.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return config

class BoneAmanita:
    def __init__(self, config: Dict[str, Any]):
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.config = config
        self.user_name = config.get("user_name", "TRAVELER")
        self._initialize_core(None)
        self._initialize_embryo()
        self._initialize_identity()
        self._initialize_village()
        self._initialize_cognition()
        self._validate_state()

    def _initialize_core(self, lexicon_layer):
        print(f"{Prisma.GRY}...Bootstrapping Core Systems...{Prisma.RST}")
        self.lex = lexicon_layer if lexicon_layer else TheLexicon
        self._load_resource_safely(
            lambda: self.lex.initialize() if hasattr(self.lex, 'initialize') else None,
            "Lexicon Init")
        if hasattr(self.lex, 'get_store'):
            try:
                store = self.lex.get_store()
                if store and getattr(store, 'hive_loaded', False):
                    BoneConfig.STAMINA_REGEN *= 1.1
                    print(f"{Prisma.GRN}[GENETICS]: Ancestral knowledge detected. Stamina Regen boosted.{Prisma.RST}")
            except Exception as e:
                print(f"{Prisma.GRY}[INIT]: Ancestral check skipped ({e}).{Prisma.RST}")
        self.lex.compile_antigens()
        self._load_resource_safely(DeathGen.load_protocols, "Death Protocols")
        self._load_resource_safely(LiteraryReproduction.load_genetics, "Genetics")
        self.akashic = TheAkashicRecord()
        print(f"{Prisma.CYN}[SLASH]: The Akashic Record is open for writing.{Prisma.RST}")
        self.events = EventBus()
        if hasattr(self.akashic, 'setup_listeners'):
            self.akashic.setup_listeners(self.events)
        self.telemetry = TelemetryService.initialize(f"session_{int(time.time())}")
        self.events.log(f"{Prisma.CYN}[SLASH]: Telemetry Uplink Established.{Prisma.RST}", "BOOT")
        self.system_health = SystemHealth()
        self.observer = TheObserver()
        self.system_health.link_observer(self.observer)

    def _initialize_embryo(self):
        self.embryo = BoneArchitect.incubate(self.events, self.lex)
        self.embryo = BoneArchitect.awaken(self.embryo)
        self.gordon = GordonKnot()
        self.soul_legacy_data = self.embryo.soul_legacy

    def _initialize_identity(self):
        self.soul = NarrativeSelf(self, self.events, memory_ref=self.mind.mem)
        if self.soul_legacy_data:
            self.soul.load_from_dict(self.soul_legacy_data)

    def _initialize_village(self):
        self.town_hall = TownHall(self.gordon, self.events, self.embryo.shimmer)
        self.village = {
            "town_hall": self.town_hall,
            "council": CouncilChamber(),
            "repro": LiteraryReproduction(),
            "projector": Projector(),
            "kintsugi": KintsugiProtocol(),
            "therapy": TherapyProtocol(),
            "folly": TheFolly(),
            "stabilizer": ZoneInertia(),
            "director": ChorusDriver(),
            "bureau": TheBureau(),
            "cosmic": CosmicDynamics(),
            "navigator": TheNavigator(self.embryo.shimmer),
            "zen": ZenGarden(self.events),
            "tinkerer": TheTinkerer(self.gordon, self.events) }
        self.cmd = CommandProcessor(self, Prisma, self.lex, BoneConfig)

    def _initialize_cognition(self):
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.folly, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.cycle_controller = GeodesicOrchestrator(self)
        client = LLMInterface(
            events_ref=self.events,
            provider=self.config.get("provider"),
            base_url=self.config.get("base_url"),
            api_key=self.config.get("api_key"),
            model=self.config.get("model"))
        self.cortex = TheCortex(self, llm_client=client)
        self.somatic = SomaticInterface(self)

    def __getattr__(self, name):
        if name == 'phys':
            if hasattr(self, 'embryo') and self.embryo:
                return self.embryo.physics
            raise AttributeError("'BoneAmanita' has no embryo to retrieve 'phys' from.")
        if hasattr(self, 'embryo') and self.embryo and hasattr(self.embryo, name):
            return getattr(self.embryo, name)
        if hasattr(self, 'town_hall') and self.town_hall and hasattr(self.town_hall, name):
            return getattr(self.town_hall, name)
        if hasattr(self, 'village') and name in self.village:
            return self.village[name]
        if hasattr(self, 'embryo') and self.embryo and hasattr(self.embryo, 'physics'):
            if hasattr(self.embryo.physics, name):
                return getattr(self.embryo.physics, name) 
        raise AttributeError(f"'BoneAmanita' object has no attribute '{name}'")

    def _validate_state(self):
        BoneConfig.load_preset(BonePresets.ZEN_GARDEN)
        self.tick_count = 0
        self.health = self.mind.mem.session_health if self.mind.mem.session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mind.mem.session_stamina if self.mind.mem.session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = self.mind.mem.session_trauma_vector if hasattr(self.mind.mem, 'session_trauma_vector') and self.mind.mem.session_trauma_vector else BoneConfig.TRAUMA_VECTOR.copy()

    def _load_resource_safely(self, loader_func, resource_name):
        try:
            loader_func()
        except Exception as e:
            self.events.log(f"{Prisma.RED}[INIT]: {resource_name} failed to load: {e}{Prisma.RST}", "BOOT_ERR")
            print(f"{Prisma.RED}   > {resource_name} skipped (Error: {e}){Prisma.RST}")

    def get_avg_voltage(self):
        hist = self.phys.dynamics.voltage_history
        if not hist: return 0.0
        return sum(hist) / len(hist)

    def process_turn(self, user_message: str) -> Dict[str, Any]:
        turn_start = self.observer.clock_in()
        self.observer.user_turns += 1
        if not user_message: user_message = ""
        cmd_response = self._phase_check_commands(user_message)
        if cmd_response:
            return cmd_response
        if self._ethical_audit():
            self.events.log(f"{Prisma.WHT}MERCY SIGNAL: Trauma boards wiped.{Prisma.RST}", "SYS")
        try:
            cortex_packet = self.cortex.process(user_input=user_message)
        except Exception as e:
            self.events.log(f"CYCLE CRITICAL FAILURE: {e}", "ERR")
            import traceback
            traceback.print_exc()
            return {
                "ui": f"{Prisma.RED}REALITY FRACTURE: {e}{Prisma.RST}",
                "logs": ["CRITICAL FAILURE"],
                "metrics": self.get_metrics()}
        duration = self.observer.clock_out(turn_start, "cycle")
        avg_cycle = self.observer.get_report().get("avg_cycle_sec", 0.0)
        reporter = self.cycle_controller.reporter
        if avg_cycle > 2.0 and reporter.current_mode != "PERFORMANCE":
            self.events.log(f"{Prisma.OCHRE}⚠️ HIGH LATENCY ({avg_cycle:.2f}s). Engaging Performance Mode.{Prisma.RST}", "SYS")
            reporter.switch_renderer("PERFORMANCE")
        elif avg_cycle < 0.5 and reporter.current_mode == "PERFORMANCE":
            self.events.log(f"{Prisma.GRN}⚡ LATENCY NOMINAL ({avg_cycle:.2f}s). Restoring High-Fidelity.{Prisma.RST}", "SYS")
            reporter.switch_renderer("STANDARD")
        if hasattr(self.mind, 'mem') and hasattr(self.mind.mem, 'session_trauma_vector'):
            self.mind.mem.session_trauma_vector = self.trauma_accum.copy()
        return cortex_packet

    def _phase_check_commands(self, user_message):
        if user_message.strip().startswith("/"):
            self.cmd.execute(user_message)
            cmd_logs = [e['text'] for e in self.events.flush()]
            ui_output = "\n".join(cmd_logs) if cmd_logs else "Command Executed."
            return {
                "type": "COMMAND",
                "ui": f"\n{ui_output}",
                "logs": cmd_logs,
                "metrics": self.get_metrics()}
        return None

    def trigger_death(self, last_phys) -> Dict:
        eulogy = DeathGen.eulogy(last_phys, self.bio.mito.state)
        death_log = [f"\n{Prisma.RED}SYSTEM HALT: {eulogy}{Prisma.RST}"]
        try:
            path = self.mind.mem.save(
                health=0,
                stamina=self.stamina,
                mutations=self.repro.attempt_reproduction(self, "MITOSIS")[1],
                trauma_accum=self.trauma_accum,
                joy_history=[],
                mitochondria_traits=self.bio.mito.adapt(0),
                antibodies=list(self.bio.immune.active_antibodies),
                soul_data=self.soul.to_dict())
            death_log.append(f"{Prisma.WHT}   [LEGACY SAVED: {path}]{Prisma.RST}")
        except Exception as e:
            death_log.append(f"Save Failed: {e}")
        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self.get_metrics(0.0)}

    def get_metrics(self, atp=0.0):
        return {"health": self.health, "stamina": self.stamina, "atp": atp, "tick": self.tick_count}

    def _get_crash_path(self, prefix="crash"):
        folder = "crashes"
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError:
                folder = "."
        try:
            files = sorted([f for f in os.listdir(folder) if f.startswith(prefix)])
            while len(files) >= 5:
                oldest = files.pop(0)
                os.remove(os.path.join(folder, oldest))
        except Exception:
            pass
        return os.path.join(folder, f"{prefix}_{int(time.time())}.json")

    def emergency_save(self, exit_cause: str = "UNKNOWN") -> str:
        try:
            sess_id = self.mind.mem.session_id
        except AttributeError:
            sess_id = f"corrupted_{int(time.time())}"
        spore_data = {
            "session_id": sess_id,
            "meta": {
                "timestamp": time.time(),
                "final_health": getattr(self, "health", 0),
                "final_stamina": getattr(self, "stamina", 0),
                "exit_cause": str(exit_cause)},
            "core_graph": getattr(self.mind.mem, "graph", {}) if hasattr(self, "mind") else {},
            "trauma_vector": getattr(self, "trauma_accum", {})}
        try:
            if hasattr(self, "mind") and hasattr(self.mind.mem, "loader"):
                path = self.mind.mem.loader.save_spore(f"emergency_{sess_id}.json", spore_data)
            else:
                fname = self._get_crash_path("spore_emergency")
                with open(fname, 'w') as spore_file:
                    json.dump(spore_data, spore_file, default=str)
                path = fname
            return f"✔ Spore encapsulated: {path}"
        except Exception as e:
            try:
                fname = self._get_crash_path("panic_dump")
                with open(fname, 'w') as panic_file:
                    json.dump({"error": str(e), "data": str(spore_data)}, panic_file)
                return f"✘ Encapsulation Failed. Panic dump written to {fname}"
            except:
                return f"✘ TOTAL SYSTEM FAILURE: {e}"

    def _ethical_audit(self):
        DESPERATION_THRESHOLD = 0.7
        CATHARSIS_HEAL_AMOUNT = 30.0
        CATHARSIS_DECAY = 0.1
        MAX_HEALTH_CAP = 100.0
        trauma_sum = sum(self.trauma_accum.values())
        health_ratio = self.health / BoneConfig.MAX_HEALTH
        desperation = trauma_sum * (1.0 - health_ratio)
        if desperation > DESPERATION_THRESHOLD:
            self.events.log(f"{Prisma.WHT}ETHICAL RELEASE: Desperation Index ({desperation:.2f}) critical.{Prisma.RST}", "SYS")
            for k in self.trauma_accum:
                self.trauma_accum[k] *= CATHARSIS_DECAY
            self.events.log(f"{Prisma.CYN}*** CATHARSIS *** Trauma stocks reduced by {int((1-CATHARSIS_DECAY)*100)}%. Ghost remains.{Prisma.RST}", "SYS")
            self.health = min(self.health + CATHARSIS_HEAL_AMOUNT, MAX_HEALTH_CAP)
            if hasattr(self.bio, 'endo'):
                self.bio.endo.cortisol *= 0.2
                self.bio.endo.serotonin = max(0.5, self.bio.endo.serotonin + 0.3)
            return True
        return False

    @staticmethod
    def apply_cosmic_physics(physics, state, cosmic_drag_penalty):
        physics["narrative_drag"] += cosmic_drag_penalty
        if state == "VOID_DRIFT": physics["voltage"] = max(0.0, physics["voltage"] - 0.5)
        elif state == "LAGRANGE_POINT": physics["narrative_drag"] = max(0.1, physics["narrative_drag"] - 2.0)
        elif state == "WATERSHED_FLOW": physics["voltage"] += 0.5

    @staticmethod
    def check_pareidolia(words):
        return BoneConfig.check_pareidolia(words)

    def engage_cold_boot(self):
        if self.tick_count > 0:
            return
        print(f"{Prisma.GRY}...Synthesizing Initial Reality...{Prisma.RST}")
        scenarios = TheLore.get_instance().get("SCENARIOS", {})
        archetypes = scenarios.get("ARCHETYPES", ["A quiet void"])
        seed = random.choice(archetypes)
        boot_prompt = (
            f"SYSTEM_BOOT_SEQUENCE. User: {self.user_name}. "
            f"SEED: {seed}. "
            "DIRECTIVE: Generate the opening scene for a text-based simulation. "
            "Be vivid, atmospheric, and specific. Describe the immediate surroundings. "
            "Do not ask 'What do you do?'. Just set the scene."
        )
        cold_result = self.process_turn(f"SYSTEM_BOOT: {boot_prompt}")
        if cold_result.get("ui"):
            print(cold_result["ui"])

if __name__ == "__main__":
    print("\n" + "="*40)
    print(f"{Prisma.paint('♦ BONEAMANITA 12.5.1', 'M')}")
    print("="*40 + "\n")
    sys_config = ConfigWizard.load_or_create()
    engine_instance = BoneAmanita(config=sys_config)
    with SessionGuardian(engine_instance) as session_engine:
        session_engine.engage_cold_boot()
        while True:
            try:
                user_input = input(f"{Prisma.paint(f'{session_engine.user_name} >', 'W')} ")
            except EOFError:
                break
            if user_input.lower() in ["exit", "quit", "/exit"]:
                break
            result = session_engine.process_turn(user_input)
            if result.get("ui"):
                print(result["ui"])
            if result.get("logs") and BoneConfig.VERBOSE_LOGGING:
                for entry in result["logs"]:
                    print(entry)