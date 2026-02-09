""" BONEAMANITA 14.6.4
 Architects: SLASH, KISHO, Taylor & Edmark """

import os, time, json, uuid, urllib.request, urllib.error, random, traceback
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from bone_core import EventBus, Prisma, BoneConfig, RealityLayer, SystemHealth, TheObserver, BonePresets, TheLore, LoreCategory, TelemetryService, RealityStack
from bone_commands import CommandProcessor
from bone_village import TownHall, DeathGen, TheCartographer, TheTinkerer, Limbo
from bone_lexicon import TheLexicon, SomaticInterface
from bone_inventory import GordonKnot
from bone_protocols import TheFolly, KintsugiProtocol, TherapyProtocol, TheBureau, ZenGarden, TheCriticsCircle
from bone_drivers import ChorusDriver, SynergeticLensArbiter, BoneConsultant
from bone_physics import CosmicDynamics, ZoneInertia
from bone_body import SomaticLoop
from bone_brain import TheCortex, LLMInterface, NoeticLoop
from bone_soul import NarrativeSelf
from bone_architect import BoneArchitect
from bone_cycle import GeodesicOrchestrator
from bone_gui import Projector, GeodesicRenderer
from bone_council import CouncilChamber
from bone_spores import LiteraryReproduction
from bone_akashic import TheAkashicRecord

@dataclass
class HostStats:
    latency: float
    efficiency_index: float

def bootstrap_systems():
    print(f"{Prisma.GRY}...Bootstrapping Sub-Systems...{Prisma.RST}")
    lore = TheLore.get_instance()
    critical_files = [LoreCategory.LEXICON, LoreCategory.SCENARIOS]
    for cat in critical_files:
        if lore.get(cat.value) is None:
            print(f"{Prisma.RED}[CRITICAL]: '{cat.name}' data missing! System may be unstable.{Prisma.RST}")
        else:
            print(f"{Prisma.GRY}[SYS] Checked {cat.name}... OK.{Prisma.RST}")


class SessionGuardian:
    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        print(f"{Prisma.paint('>>> BONEAMANITA 14.6.4', 'G')}")
        print(f"{Prisma.paint('System: LISTENING', '0')}")
        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"\n{Prisma.paint('--- SYSTEM HALT ---', 'R')}")
        if self.engine_instance:
            try:
                self.engine_instance.shutdown()
            except Exception as e:
                print(f"{Prisma.RED}Error during graceful shutdown: {e}{Prisma.RST}")
                self._safe_log(f"SHUTDOWN_ERROR: {e}", "SYS_ERR")
        if self.engine_instance and hasattr(self.engine_instance, "telemetry"):
            try:
                print(self.engine_instance.telemetry.generate_session_summary())
            except Exception as e:
                print(f"{Prisma.GRY}[Telemetry Summary Failed]: {e}{Prisma.RST}")
        if exc_type:
            is_interrupt = issubclass(exc_type, KeyboardInterrupt)
            err_color = 'Y' if is_interrupt else 'R'
            print(f"{Prisma.paint(f'EXIT CAUSE: {exc_val}', err_color)}")
            if not is_interrupt:
                full_trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                self._safe_log(f"CRITICAL CRASH: {exc_val}\n{full_trace}", "CRIT")
        try:
            print(f"{Prisma.paint('Initiating Emergency Spore Preservation...', 'Y')}")
            if self.engine_instance:
                exit_cause = "INTERRUPT" if exc_type else "MANUAL"
                result_msg = self.engine_instance.emergency_save(exit_cause=exit_cause)
                color = 'C' if '✔' in result_msg else 'R'
                print(f"{Prisma.paint(result_msg, color)}")
        except Exception as e:
            print(f"{Prisma.RED}FATAL: State corruption during Spore creation. {e}{Prisma.RST}")
        print(f"{Prisma.paint('Disconnected.', '0')}")
        return exc_type is KeyboardInterrupt

    def _safe_log(self, msg, cat):
        if self.engine_instance and hasattr(self.engine_instance, "events"):
            try:
                self.engine_instance.events.log(msg, cat)
            except:
                pass

class ConfigWizard:
    CONFIG_FILE = "bone_config.json"

    @staticmethod
    def load_or_create():
        if os.path.exists(ConfigWizard.CONFIG_FILE):
            try:
                with open(ConfigWizard.CONFIG_FILE, "r", encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"{Prisma.RED}[CONFIG]: JSON Corruption detected: {e}{Prisma.RST}")
                ConfigWizard._backup_corrupt_file()
            except IOError as e:
                print(f"{Prisma.RED}[CONFIG]: Read Error: {e}{Prisma.RST}")
            except Exception as e:
                print(f"{Prisma.RED}[CONFIG]: Unexpected Load Failure: {e}{Prisma.RST}")
        return ConfigWizard._run_setup()

    @staticmethod
    def _backup_corrupt_file():
        try:
            timestamp = int(time.time())
            backup_name = f"{ConfigWizard.CONFIG_FILE}.{timestamp}.bak"
            os.rename(ConfigWizard.CONFIG_FILE, backup_name)
            print(f"{Prisma.YEL}   >>> Corrupt config backed up to: {backup_name}{Prisma.RST}")
            print(f"{Prisma.YEL}   >>> Re-initializing Setup...{Prisma.RST}")
        except Exception as e:
            print(f"{Prisma.RED}   >>> FATAL: Could not backup config: {e}{Prisma.RST}")

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
            default_url = "http://127.0.0.1:11434/v1/chat/completions"
            user_url = input(f"Base URL [{default_url}]: ").strip()
            config["base_url"] = user_url if user_url else default_url
            config["model"] = input("Model Name (e.g., llama3): ").strip() or "llama3"
        config["user_name"] = input("Designation (User Name): ").strip() or "TRAVELER"
        with open(ConfigWizard.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return config

class BoneAmanita:
    events: EventBus
    def __init__(self, config: Dict[str, Any]):
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.config = config
        self.user_name = config.get("user_name", "TRAVELER")
        self.health: float = BoneConfig.MAX_HEALTH
        self.stamina: float = BoneConfig.MAX_STAMINA
        self.trauma_accum: Dict[str, float] = {}
        self.tick_count: int = 0
        self._initialize_core(None)
        self._initialize_embryo()
        self._initialize_identity()
        self._initialize_village()
        self._initialize_cognition()
        self.host_stats = HostStats(latency=0.0, efficiency_index=1.0)
        self._validate_state()

    @property
    def phys(self):
        return self.embryo.physics if self.embryo else None

    @property
    def mind(self):
        return self.embryo.mind if self.embryo else None

    @property
    def bio(self):
        return self.embryo.bio if self.embryo else None

    @property
    def shimmer(self):
        return self.embryo.shimmer if self.embryo else None

    def _initialize_core(self, lexicon_layer):
        print(f"{Prisma.GRY}...Bootstrapping Core Systems...{Prisma.RST}")
        self.lex = lexicon_layer if lexicon_layer else TheLexicon
        lore_instance = TheLore.get_instance()
        lex_data = lore_instance.get("LEXICON")
        if not lex_data or len(lex_data) < 5:
            print(f"{Prisma.RED}[WARN] bone_data.LEXICON appears empty! Check imports.{Prisma.RST}")
        else:
            print(f"{Prisma.GRY}[SYS] Lore Manifest connected ({len(lex_data)} categories found).{Prisma.RST}")
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
        self.telemetry = TelemetryService.get_instance()
        self.events.log(f"{Prisma.CYN}[SLASH]: Telemetry Uplink Established.{Prisma.RST}", "BOOT")
        self.system_health = SystemHealth()
        self.observer = TheObserver()
        self.system_health.link_observer(self.observer)
        self.reality_stack = RealityStack()
        self.soil_fertility = 0.0

    def _initialize_embryo(self):
        self.embryo = BoneArchitect.incubate(self.events, self.lex)
        self.embryo = BoneArchitect.awaken(self.embryo)
        if hasattr(self.embryo, 'bio') and hasattr(self.embryo.bio, 'setup_listeners'):
            self.embryo.bio.setup_listeners()
        self.gordon = GordonKnot(events=self.events)
        self.soul_legacy_data = self.embryo.soul_legacy

    def _initialize_identity(self):
        self.soul = NarrativeSelf(
            self,
            self.events,
            memory_ref=self.mind.mem,
            akashic_ref=self.akashic)
        if self.soul_legacy_data:
            self.soul.load_from_dict(self.soul_legacy_data)

    def _initialize_village(self):
        self.navigator = TheCartographer(self.embryo.shimmer)
        self.town_hall = TownHall(self.gordon, self.events, self.embryo.shimmer, self.akashic, self.navigator)
        self.drivers = SynergeticLensArbiter(self.events)
        self.consultant = BoneConsultant()
        self.limbo = Limbo()
        self.council = CouncilChamber(self)
        self.repro = LiteraryReproduction()
        self.projector = Projector()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.folly = TheFolly()
        self.stabilizer = ZoneInertia()
        self.director = ChorusDriver()
        self.bureau = TheBureau()
        self.cosmic = CosmicDynamics()
        self.zen = ZenGarden(self.events)
        self.tinkerer = TheTinkerer(self.gordon, self.events, self.akashic)
        self.critics = TheCriticsCircle(self.events)
        self.village = {
            "town_hall": self.town_hall,
            "critics": self.critics,
            "council": self.council,
            "repro": self.repro,
            "projector": self.projector,
            "kintsugi": self.kintsugi,
            "therapy": self.therapy,
            "folly": self.folly,
            "stabilizer": self.stabilizer,
            "director": self.director,
            "bureau": self.bureau,
            "cosmic": self.cosmic,
            "navigator": self.navigator,
            "zen": self.zen,
            "tinkerer": self.tinkerer}
        self.cmd = CommandProcessor(self, Prisma, self.lex, BoneConfig)
        if self.phys:
            self.phys.dynamics = self.cosmic

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
            print(f"{Prisma.RED}   > {resource_name} CRITICAL FAILURE:{Prisma.RST}")
            traceback.print_exc()

    def get_avg_voltage(self):
        hist = self.phys.observer.voltage_history
        if not hist: return 0.0
        return sum(hist) / len(hist)

    def process_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        turn_start = self.observer.clock_in()
        self.observer.user_turns += 1
        if not user_message: user_message = ""
        if user_message.startswith("//"):
            return self._handle_meta_command(user_message)
        rules = self.reality_stack.get_grammar_rules()
        if rules["allow_commands"]:
            cmd_response = self._phase_check_commands(user_message)
            if cmd_response:
                return cmd_response
        if not rules["allow_narrative"]:
            return {
                "ui": f"{Prisma.paint('REALITY HALT', 'R')}: Narrative engine suppressed by current depth ({self.reality_stack.current_depth}).",
                "logs": [], "metrics": self.get_metrics()}
        if self._ethical_audit():
            self.events.log(f"{Prisma.WHT}MERCY SIGNAL: Trauma boards wiped.{Prisma.RST}", "SYS")
        try:
            cortex_packet = self.cortex.process(user_input=user_message, is_system=is_system)
            if self.bureau and not is_system:
                sys_text = cortex_packet.get("ui", "")
                current_voltage = 0.0
                if self.cortex and getattr(self.cortex, "last_physics", None):
                    current_voltage = self.cortex.last_physics.get("voltage", 0.0)
                sys_phys = {
                    "raw_text": sys_text,
                    "clean_words": self.lex.clean(sys_text) if hasattr(self, 'lex') else [],
                    "voltage": current_voltage,
                    "truth_ratio": 1.0}
                sys_bio = {"health": self.health}
                audit_result = self.bureau.audit(sys_phys, sys_bio, origin="SYSTEM")
                if audit_result:
                    if "atp_gain" in audit_result and hasattr(self, 'bio') and self.bio.mito:
                        self.bio.mito.adjust_atp(audit_result["atp_gain"], "System Style Violation")
                    if "ui" in audit_result:
                        cortex_packet["ui"] += f"\n\n{audit_result['ui']}"
                    if "log" in audit_result:
                        self.events.log(audit_result["log"], "BUREAU")
            if rules["system_override"] and "ui" in cortex_packet:
                debug_footer = f"\n{Prisma.paint(f'--- DEBUG: {self.get_metrics()} ---', '0')}"
                cortex_packet["ui"] += debug_footer
        except Exception as e:
            self.events.log(f"CYCLE CRITICAL FAILURE: {e}", "ERR")
            import traceback
            traceback.print_exc()
            return {
                "ui": f"{Prisma.RED}REALITY FRACTURE: {e}{Prisma.RST}",
                "logs": ["CRITICAL FAILURE"],
                "metrics": self.get_metrics()}
        self.observer.clock_out(turn_start, "cycle")
        self.host_stats.latency = self.observer.last_cycle_duration
        self.host_stats.efficiency_index = self.observer.calculate_efficiency(self.health, self.stamina)
        if self.host_stats.efficiency_index < 50.0:
            self.events.log(
                f"{Prisma.OCHRE}[LAG]: System viscosity high. Efficiency: {self.host_stats.efficiency_index:.1f}{Prisma.RST}",
                "PERF")
        avg_cycle = self.observer.get_report().get("avg_cycle_sec", 0.0)
        reporter = self.cycle_controller.reporter
        if avg_cycle > 2.0 and reporter.current_mode != "PERFORMANCE":
            self.events.log(f"{Prisma.OCHRE}The simulation blurs to maintain velocity. (Performance Mode Engaged){Prisma.RST}", "SENSATION")
            reporter.switch_renderer("PERFORMANCE")
        elif avg_cycle < 0.5 and reporter.current_mode == "PERFORMANCE":
            self.events.log(f"{Prisma.GRN}The details snap back into focus. (High-Fidelity Restored){Prisma.RST}", "SENSATION")
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
        eulogy = DeathGen.eulogy(last_phys, self.bio.mito.state, self.trauma_accum)
        death_log = [f"\n{Prisma.RED}SYSTEM HALT: {eulogy}{Prisma.RST}"]
        continuity_packet = {
            "location": self.cortex.gather_state(self.cortex.last_physics or {}).get("world", {}).get("orbit", ["Void"])[0],
            "last_output": self.cortex.dialogue_buffer[-1] if self.cortex.dialogue_buffer else "Silence.",
            "inventory": self.gordon.inventory}
        try:
            path = self.mind.mem.save(
                health=0,
                stamina=self.stamina,
                mutations=self.repro.attempt_reproduction(self, "MITOSIS")[1],
                trauma_accum=self.trauma_accum,
                joy_history=[],
                mitochondria_traits=self.bio.mito.adapt(0),
                antibodies=list(self.bio.immune.active_antibodies),
                soul_data=self.soul.to_dict(),
                continuity=continuity_packet)
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
        sess_id = "unknown_session"
        if hasattr(self, "mind") and hasattr(self.mind, "mem"):
            sess_id = getattr(self.mind.mem, "session_id", f"crash_{int(time.time())}")
        spore_data = {
            "session_id": sess_id,
            "meta": {
                "timestamp": time.time(),
                "final_health": getattr(self, "health", 0),
                "exit_cause": str(exit_cause),
                "kernel_hash": getattr(self, "kernel_hash", "UNKNOWN")},
            "trauma_vector": getattr(self, "trauma_accum", {})}
        try:
            if hasattr(self.mind.mem, "loader"):
                path = self.mind.mem.loader.save_spore(f"emergency_{sess_id}.json", spore_data)
                return f"✔ Spore encapsulated via Loader: {path}"
            fname = self._get_crash_path(f"spore_{sess_id}")
            with open(fname, 'w', encoding='utf-8') as spore_file:
                json.dump(spore_data, spore_file, default=str, indent=2)
            return f"✔ Spore encapsulated via RAW DUMP: {fname}"
        except (OSError, IOError) as disk_err:
            self.events.log(f"EMERGENCY SAVE DISK ERROR: {disk_err}", "CRIT")
            return f"✘ Disk Failure during spore creation: {disk_err}"
        except Exception as e:
            self.events.log(f"UNEXPECTED ENCAPSULATION FAILURE: {e}", "CRIT")
            return f"✘ Total System Failure: {e}"

    def _ethical_audit(self):
        DESPERATION_THRESHOLD = 0.7
        CATHARSIS_HEAL_AMOUNT = 30.0
        CATHARSIS_DECAY = 0.1
        MAX_HEALTH_CAP = 100.0
        trauma_sum = sum(self.trauma_accum.values())
        health_ratio = self.health / BoneConfig.MAX_HEALTH
        desperation = trauma_sum * (1.0 - health_ratio)
        if desperation > DESPERATION_THRESHOLD:
            self.events.log(f"{Prisma.WHT}MERCY SIGNAL: The pressure is too high. Venting...{Prisma.RST}", "SYS")
            for k in self.trauma_accum:
                self.trauma_accum[k] *= CATHARSIS_DECAY
            self.events.log(
                f"{Prisma.CYN}*** CATHARSIS *** You take a deep breath. A weight lifts from your chest.{Prisma.RST}",
                "SENSATION")
            self.health = min(self.health + CATHARSIS_HEAL_AMOUNT, MAX_HEALTH_CAP)
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

    def engage_cold_boot(self) -> Optional[Dict[str, Any]]:
        if self.tick_count > 0:
            return None
        if self.embryo.continuity:
            print(f"{Prisma.GRY}...Resuming Timeline...{Prisma.RST}")
            loc = self.embryo.continuity.get("location", "Unknown")
            last_scene = self.embryo.continuity.get("last_output", "")
            saved_inv = self.embryo.continuity.get("inventory", [])
            if saved_inv:
                self.gordon.inventory = saved_inv
            resume_text = f"**RESUMING TIMELINE**\nLocation: {loc}\n\n{last_scene}"
            return {"ui": resume_text, "logs": ["Timeline Restored."]}
        print(f"{Prisma.GRY}...Synthesizing Initial Reality...{Prisma.RST}")
        scenarios = TheLore.get_instance().get("SCENARIOS", {})
        archetypes = scenarios.get("ARCHETYPES", ["A quiet garden"])
        seed = random.choice(archetypes)
        print(f"{Prisma.CYN}[SYS] Seed Loaded: '{seed}'{Prisma.RST}")
        boot_prompt = (
            f"SYSTEM_BOOT: SEQUENCE START.\n"
            f"SOURCE_SEED: '{seed}'\n"
            f"DIRECTIVE: Do not use the seed text literally. Use it as a metaphorical anchor only. "
            f"Generate a vivid, sensory opening log that captures the *vibe* of the seed without describing it directly. "
            f"Focus on lighting, texture, and entropy.")
        cold_result = self.process_turn(boot_prompt, is_system=True)
        if cold_result.get("ui"):
            print(cold_result["ui"])
        return cold_result

    def _gather_village_state(self) -> Dict[str, Any]:
        state = {}
        for name, component in self.village.items():
            if hasattr(component, 'to_dict'):
                try:
                    state[name] = component.to_dict()
                except Exception as e:
                    self.events.log(f"Serialization failed for {name}: {e}", "ERR")
        return state

    def _restore_village_state(self, state_data: Dict[str, Any]):
        if not state_data: return
        for name, data in state_data.items():
            if name in self.village and hasattr(self.village[name], 'load_state'):
                try:
                    self.village[name].load_state(data)
                except Exception as e:
                    print(f"{Prisma.RED}[RESUME]: Failed to hydrate {name}: {e}{Prisma.RST}")

    def save_checkpoint(self, history: list = None) -> str:
        try:
            folder = "saves"
            if not os.path.exists(folder):
                os.makedirs(folder)
            last_phys = getattr(self.cortex, "last_physics", {})
            world_data = self.cortex.gather_state(last_phys).get("world", {})
            loc = world_data.get("orbit", ["Void"])[0]
            last_speech = "Silence."
            if self.cortex.dialogue_buffer:
                last_speech = self.cortex.dialogue_buffer[-1]
            continuity_packet = {
                "location": loc,
                "last_output": last_speech,
                "inventory": self.gordon.inventory}
            state_data = {
                "health": self.health,
                "stamina": self.stamina,
                "trauma_accum": self.trauma_accum,
                "soul_data": self.soul.to_dict(),
                "village_data": self._gather_village_state(),
                "continuity": continuity_packet,
                "timestamp": time.time(),
                "chat_history": history if history else []}
            path = os.path.join(folder, "quicksave.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, default=str)
            return f"✔ Checkpoint Saved: {path}"
        except Exception as e:
            self.events.log(f"SAVE FAILED: {e}", "SYS_ERR")
            return f"❌ Save Failed: {e}"

    def resume_checkpoint(self) -> Tuple[bool, list]:
        path = "saves/quicksave.json"
        if not os.path.exists(path):
            print(f"{Prisma.GRY}[RESUME]: No quicksave found. Starting fresh.{Prisma.RST}")
            return False, []
        try:
            print(f"{Prisma.CYN}[RESUME]: Hydrating from {path}...{Prisma.RST}")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.health = data.get("health", 100.0)
            self.stamina = data.get("stamina", 100.0)
            self.trauma_accum = data.get("trauma_accum", {})
            if "soul_data" in data and hasattr(self, "soul"):
                self.soul.load_from_dict(data["soul_data"])
            if "village_data" in data:
                 self._restore_village_state(data["village_data"])
            if "continuity" in data:
                self.embryo.continuity = data["continuity"]
                if "inventory" in data["continuity"]:
                    self.gordon.inventory = data["continuity"]["inventory"]
            restored_history = data.get("chat_history", [])
            print(f"{Prisma.GRN}[RESUME]: System State & Logs Restored.{Prisma.RST}")
            return True, restored_history
        except Exception as e:
            print(f"{Prisma.RED}[RESUME]: Failed to hydrate: {e}{Prisma.RST}")
            return False, []

    def shutdown(self):
        print(f"{Prisma.GRY}...Broadcasting SYSTEM_HALT...{Prisma.RST}")
        self.events.publish("SYSTEM_HALT", {"tick": self.tick_count})
        if hasattr(self, 'mind') and hasattr(self.mind, 'mem'):
            try:
                print(f"{Prisma.GRY}[MEMORY]: Committing Session State...{Prisma.RST}")
                last_phys = getattr(self.cortex, "last_physics", {})
                world_data = self.cortex.gather_state(last_phys).get("world", {})
                loc = world_data.get("orbit", ["Void"])[0]
                last_speech = "Silence."
                if self.cortex.dialogue_buffer:
                    last_speech = self.cortex.dialogue_buffer[-1]
                continuity_packet = {
                    "location": loc,
                    "last_output": last_speech,
                    "inventory": self.gordon.inventory}
                atlas_data = {}
                if hasattr(self.phys, "nav") and hasattr(self.phys.nav, "export_atlas"):
                    atlas_data = self.phys.nav.export_atlas()
                save_path = self.mind.mem.save(
                    health=self.health,
                    stamina=self.stamina,
                    mutations={},
                    trauma_accum=self.trauma_accum,
                    joy_history=[],
                    mitochondria_traits=self.bio.mito.adapt(0),
                    antibodies=list(self.bio.immune.active_antibodies),
                    soul_data=self.soul.to_dict(),
                    village_data=self._gather_village_state(),
                    continuity=continuity_packet,
                    world_atlas=atlas_data)
                print(f"{Prisma.GRN}[MEMORY]: State preserved at {save_path}{Prisma.RST}")
            except Exception as e:
                print(f"{Prisma.RED}[MEMORY]: Save Failed: {e}{Prisma.RST}")
                self.events.log(f"SHUTDOWN_SAVE_FAILURE: {traceback.format_exc()}", "ERR")
        time.sleep(0.1)
        if hasattr(self, 'lex') and hasattr(self.lex, 'save'):
            print(f"{Prisma.GRY}[LEXICON]: Preserving Hive Mind...{Prisma.RST}")
            self.lex.save()
        if hasattr(self, 'akashic') and hasattr(self.akashic, 'save_all'):
            self.akashic.save_all()
        elif hasattr(self, 'akashic') and hasattr(self.akashic, '_save_to_disk'):
            try:
                print(f"{Prisma.GRY}[AKASHIC]: Force-saving...{Prisma.RST}")
                self.akashic.save_to_disk("manifest", {})
            except Exception as e:
                print(f"{Prisma.RED}[AKASHIC]: Save failed: {e}{Prisma.RST}")
        for system_name, system in [("LEXICON", self.lex), ("AKASHIC", self.akashic)]:
            if hasattr(system, 'save') or hasattr(system, 'save_all'):
                try:
                    print(f"{Prisma.GRY}[{system_name}]: Preserving...{Prisma.RST}")
                    if hasattr(system, 'save'):
                        system.save()
                    else:
                        system.save_all()
                except Exception as e:
                    print(f"{Prisma.RED}[{system_name}]: Save failed: {e}{Prisma.RST}")

    def _handle_meta_command(self, text: str) -> Dict[str, Any]:
        parts = text.strip().split()
        cmd = parts[0].lower()
        logs = []
        ui_msg = ""
        if cmd == "//layer":
            if len(parts) < 2:
                ui_msg = f"Current Layer: {self.reality_stack.current_depth}"
            else:
                sub = parts[1].lower()
                from bone_core import RealityLayer
                if sub == "push" and len(parts) > 2:
                    val = int(parts[2])
                    if self.reality_stack.push_layer(val):
                        ui_msg = f"Stack Pushed: Now at {val}"
                    else:
                        ui_msg = "Stack Push Failed (Locked?)"
                elif sub == "pop":
                    prev = self.reality_stack.pop_layer()
                    ui_msg = f"Stack Popped. Returned to {self.reality_stack.current_depth}"
                elif sub == "debug":
                    self.reality_stack.push_layer(RealityLayer.DEBUG)
                    ui_msg = f"{Prisma.paint('DEBUG MODE ENGAGED', 'M')}"
                elif sub == "sim":
                    self.reality_stack.stabilize_at(RealityLayer.SIMULATION)
                    ui_msg = f"{Prisma.paint('SIMULATION RESTORED', 'C')}"
        elif cmd == "//inject":
            payload = " ".join(parts[1:])
            self.events.log(payload, "INJECT")
            ui_msg = f"Injected: '{payload}'"
        else:
            ui_msg = f"Unknown Meta-Command: {cmd}"
        return {"ui": f"{Prisma.GRY}[META] {ui_msg}{Prisma.RST}", "logs": logs, "metrics": self.get_metrics()}

if __name__ == "__main__":
    print("\n" + "="*40)
    print(f"{Prisma.paint('♦ BONEAMANITA 14.6.4', 'M')}")
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