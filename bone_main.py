""" BONEAMANITA 14.9.5
 Architects: SLASH, KISHO, Taylor & Edmark """

import os, time, json, uuid, random, traceback
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from bone_core import EventBus, SystemHealth, TheObserver, TheLore, TelemetryService, RealityStack
from bone_types import Prisma, RealityLayer, LoreCategory
from bone_config import BoneConfig, BonePresets
from bone_commands import CommandProcessor
from bone_symbiosis import SymbiosisManager
from bone_village import TownHall, DeathGen, TheCartographer, TheTinkerer, Limbo
from bone_lexicon import TheLexicon
from bone_inventory import GordonKnot
from bone_protocols import KintsugiProtocol, TherapyProtocol, TheBureau, ZenGarden, TheCriticsCircle
from bone_physics import CosmicDynamics, ZoneInertia
from bone_body import SomaticLoop
from bone_brain import TheCortex, LLMInterface, NoeticLoop
from bone_soul import NarrativeSelf
from bone_architect import BoneArchitect
from bone_cycle import GeodesicOrchestrator
from bone_council import CouncilChamber
from bone_spores import LiteraryReproduction
from bone_akashic import TheAkashicRecord

@dataclass
class HostStats:
    latency: float
    efficiency_index: float

class SessionGuardian:
    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        print(f"{Prisma.paint('>>> BONEAMANITA 14.9.5', 'G')}")
        print(f"{Prisma.paint('System: LISTENING', '0')}")
        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"\n{Prisma.paint('--- SYSTEM HALT ---', 'R')}")
        if self.engine_instance:
            self.engine_instance.shutdown()

        if exc_type:
            is_interrupt = issubclass(exc_type, KeyboardInterrupt)
            if not is_interrupt:
                full_trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(f"{Prisma.RED}CRASH: {exc_val}{Prisma.RST}")

        print(f"{Prisma.paint('Disconnected.', '0')}")
        return exc_type is KeyboardInterrupt

class ConfigWizard:
    CONFIG_FILE = "bone_config.json"

    @staticmethod
    def load_or_create():
        if os.path.exists(ConfigWizard.CONFIG_FILE):
            try:
                with open(ConfigWizard.CONFIG_FILE, "r", encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{Prisma.RED}[CONFIG]: Load Error: {e}{Prisma.RST}")
                ConfigWizard._backup_corrupt_file()
        return ConfigWizard._run_setup()

    @staticmethod
    def _backup_corrupt_file():
        backup_name = f"{ConfigWizard.CONFIG_FILE}.{int(time.time())}.bak"
        try:
            os.rename(ConfigWizard.CONFIG_FILE, backup_name)
            print(f"{Prisma.YEL}   >>> Config backed up to: {backup_name}{Prisma.RST}")
        except:
            pass

    @staticmethod
    def _run_setup():
        print(f"\n{Prisma.CYN}=== BONEAMANITA SETUP ==={Prisma.RST}")
        config = {"provider": "mock", "model": "local", "user_name": "TRAVELER"}
        print("1. Local (Ollama) [Default]")
        print("2. Mock (Simulation)")
        choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        if choice != "2":
            config["provider"] = "ollama"
            config["base_url"] = "http://127.0.0.1:11434/v1/chat/completions"
            config["model"] = "llama3"
        config["user_name"] = input("User Name [TRAVELER]: ").strip() or "TRAVELER"
        with open(ConfigWizard.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return config


class BoneAmanita:
    events: EventBus
    def __init__(self, config: Dict[str, Any]):
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.config = config
        self.user_name = config.get("user_name", "TRAVELER")
        self.health = BoneConfig.MAX_HEALTH
        self.stamina = BoneConfig.MAX_STAMINA
        self.trauma_accum = {}
        self.tick_count = 0
        self._initialize_core(TheLexicon)
        self._initialize_embryo()
        self._initialize_identity()
        self._initialize_village()
        self._initialize_cognition()
        self.host_stats = HostStats(latency=0.0, efficiency_index=1.0)
        self._validate_state()

    def _initialize_core(self, lexicon_layer):
        print(f"{Prisma.GRY}...Bootstrapping Core...{Prisma.RST}")
        self.lex = lexicon_layer
        self.lex.initialize()
        self.lex.compile_antigens()
        DeathGen.load_protocols()
        LiteraryReproduction.load_genetics()
        self.akashic = TheAkashicRecord()
        self.events = EventBus()
        self.akashic.setup_listeners(self.events)
        self.telemetry = TelemetryService.get_instance()
        self.system_health = SystemHealth()
        self.observer = TheObserver()
        self.system_health.link_observer(self.observer)
        self.reality_stack = RealityStack()

    def _initialize_embryo(self):
        self.embryo = BoneArchitect.incubate(self.events, self.lex)
        self.embryo = BoneArchitect.awaken(self.embryo)
        self.phys = self.embryo.physics
        self.mind = self.embryo.mind
        self.bio = self.embryo.bio
        self.shimmer = self.embryo.shimmer
        self.bio.setup_listeners()
        self.gordon = GordonKnot(events=self.events)
        self.soul_legacy_data = self.embryo.soul_legacy

    def _initialize_identity(self):
        self.soul = NarrativeSelf(
            self, self.events, memory_ref=self.mind.mem, akashic_ref=self.akashic)
        if self.soul_legacy_data:
            self.soul.load_from_dict(self.soul_legacy_data)

    def _initialize_village(self):
        self.navigator = TheCartographer(self.embryo.shimmer)
        self.town_hall = TownHall(self.gordon, self.events, self.embryo.shimmer, self.akashic, self.navigator)
        self.bureau = TheBureau()
        self.repro = LiteraryReproduction()
        self.zen = ZenGarden(self.events)
        self.tinkerer = TheTinkerer(self.gordon, self.events, self.akashic)
        self.critics = TheCriticsCircle(self.events)
        self.therapy = TherapyProtocol()
        self.stabilizer = ZoneInertia()
        self.limbo = Limbo()
        self.kintsugi = KintsugiProtocol()
        self.council = CouncilChamber(self)
        self.symbiosis = SymbiosisManager(self.events)

        from bone_drivers import EnneagramDriver

        @dataclass
        class DriverCluster:
            enneagram: Any
        self.drivers = DriverCluster(
            enneagram=EnneagramDriver(self.events))
        if self.phys:
            self.phys.dynamics = CosmicDynamics()
            self.cosmic = self.phys.dynamics
        self.village = {
            "town_hall": self.town_hall,
            "bureau": self.bureau,
            "zen": self.zen,
            "tinkerer": self.tinkerer,
            "critics": self.critics,
            "navigator": self.navigator,
            "limbo": self.limbo,
            "council": self.council,
            "therapy": self.therapy}
        self.cmd = CommandProcessor(self, Prisma, self.lex, BoneConfig)

    def _initialize_cognition(self):
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.gordon, None, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.cycle_controller = GeodesicOrchestrator(self)
        llm_args = {
            k: v for k, v in self.config.items()
            if k in ["provider", "base_url", "api_key", "model"]}
        client = LLMInterface(events_ref=self.events, **llm_args)
        self.cortex = TheCortex.from_engine(self, llm_client=client)

    def _validate_state(self):
        BoneConfig.load_preset(BonePresets.ZEN_GARDEN)
        if self.mind.mem.session_health:
            self.health = self.mind.mem.session_health
            self.stamina = self.mind.mem.session_stamina
            self.trauma_accum = self.mind.mem.session_trauma_vector or {}

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
        self.tick_count += 1
        if user_message.strip().startswith(("/", "//")):
            return self._phase_check_commands(user_message) or self.get_metrics()
        rules = self.reality_stack.get_grammar_rules()
        if not rules["allow_narrative"]:
            return {"ui": f"{Prisma.RED}NARRATIVE HALT{Prisma.RST}", "logs": [], "metrics": self.get_metrics()}
        if self._ethical_audit():
            pass
        if self.health <= 0.0:
            last_phys = getattr(self.cortex, "last_physics", {})
            return self.trigger_death(last_phys)
        if not is_system and hasattr(self, 'soul') and hasattr(self.soul, 'anchor'):
            if self.host_stats.efficiency_index < 0.6:
                reliance_proxy = 0.9 if self.host_stats.efficiency_index < 0.4 else 0.5
                self.soul.anchor.check_domestication(reliance_proxy)
        try:
            cortex_packet = self.cortex.process(user_input=user_message, is_system=is_system)
            if hasattr(self.mind, 'mem'):
                self.health = self.mind.mem.session_health
                self.stamina = self.mind.mem.session_stamina
                self.trauma_accum = self.mind.mem.session_trauma_vector or {}
            if self.health <= 0.0:
                return self.trigger_death(cortex_packet.get("physics", {}))
        except Exception as e:
            traceback.print_exc()
            return {"ui": f"CORTEX ERROR: {e}", "logs": [], "metrics": self.get_metrics()}
        if self.bureau and not is_system and random.random() < 0.15:
            phys = {"raw_text": cortex_packet.get("ui", ""), "voltage": 1.0, "truth_ratio": 1.0}
            audit = self.bureau.audit(phys, {"health": self.health}, origin="SYSTEM")
            if audit and "ui" in audit:
                cortex_packet["ui"] += f"\n\n{audit['ui']}"
        self.observer.clock_out(turn_start, "cycle")
        self.host_stats.latency = self.observer.last_cycle_duration
        return cortex_packet

    def _phase_check_commands(self, user_message):
        clean_cmd = user_message.strip()
        if clean_cmd.startswith("//"):
            return self._handle_meta_command(clean_cmd)
        self.cmd.execute(clean_cmd)
        cmd_logs = [e['text'] for e in self.events.flush()]
        ui_output = "\n".join(cmd_logs) if cmd_logs else "Command Executed."
        return {
            "type": "COMMAND",
            "ui": f"\n{ui_output}",
            "logs": cmd_logs,
            "metrics": self.get_metrics()}

    def _handle_meta_command(self, text: str) -> Dict[str, Any]:
        parts = text.strip().split()
        cmd = parts[0].lower()
        ui_msg = ""
        if cmd == "//layer":
            if len(parts) >= 2:
                sub = parts[1].lower()
                if sub == "push" and len(parts) > 2:
                    if self.reality_stack.push_layer(int(parts[2])):
                        ui_msg = f"Layer Pushed: {parts[2]}"
                elif sub == "pop":
                    self.reality_stack.pop_layer()
                    ui_msg = "Layer Popped."
                elif sub == "debug":
                    self.reality_stack.push_layer(RealityLayer.DEBUG)
                    ui_msg = "Debug Mode Engaged."
            else:
                ui_msg = f"Current Layer: {self.reality_stack.current_depth}"
        elif cmd == "//inject":
            payload = " ".join(parts[1:])
            self.events.log(payload, "INJECT")
            ui_msg = f"Injected: {payload}"
        else:
            ui_msg = f"Unknown Meta-Command: {cmd}"
        return {"ui": f"{Prisma.GRY}[META] {ui_msg}{Prisma.RST}", "logs": [], "metrics": self.get_metrics()}

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

    def emergency_save(self, exit_cause="UNKNOWN"):
        return f"✔ Emergency Dump: {exit_cause}"

    def _ethical_audit(self):
        if self.tick_count % 3 != 0 and self.health > (BoneConfig.MAX_HEALTH * 0.3):
            return False
        DESPERATION_THRESHOLD = 0.7
        CATHARSIS_HEAL_AMOUNT = 30.0
        CATHARSIS_DECAY = 0.1
        MAX_HEALTH_CAP = 100.0
        trauma_sum = sum(self.trauma_accum.values())
        health_ratio = self.health / BoneConfig.MAX_HEALTH
        desperation = trauma_sum * (1.0 - health_ratio)
        if desperation > DESPERATION_THRESHOLD:
            self.events.log(f"{Prisma.WHT}MERCY SIGNAL: Pressure Critical. Venting...{Prisma.RST}", "SYS")
            for k in self.trauma_accum:
                self.trauma_accum[k] *= CATHARSIS_DECAY
            self.events.log(
                f"{Prisma.CYN}*** CATHARSIS *** The fever breaks. Logic cools.{Prisma.RST}",
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
        if self.tick_count > 0: return None
        if os.path.exists("saves/quicksave.json"):
            print(f"{Prisma.GRY}...Detected Stasis Pod...{Prisma.RST}")
            success, history = self.resume_checkpoint()
            if success:
                if self.cortex:
                    self.cortex.restore_context(history)
                loc = self.embryo.continuity.get("location", "Unknown") if self.embryo.continuity else "Unknown"
                last_scene = self.embryo.continuity.get("last_output", "") if self.embryo.continuity else "Silence."
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
                state[name] = component.to_dict()
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
            last_phys = getattr(self.cortex, "last_physics", None) or {}
            world_data = self.cortex.gather_state(last_phys).get("world", {})
            loc = world_data.get("orbit", ["Void"])[0]
            last_speech = "Silence."
            if self.cortex.dialogue_buffer:
                last_speech = self.cortex.dialogue_buffer[-1]
            continuity_packet = {
                "location": loc,
                "last_output": last_speech,
                "inventory": self.gordon.inventory}
            start_history = history if history is not None else self.cortex.dialogue_buffer
            state_data = {
                "health": self.health,
                "stamina": self.stamina,
                "trauma_accum": self.trauma_accum,
                "soul_data": self.soul.to_dict(),
                "village_data": self._gather_village_state(),
                "continuity": continuity_packet,
                "timestamp": time.time(),
                "chat_history": start_history}
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
        print(f"{Prisma.GRY}...System Halt...{Prisma.RST}")
        self.events.publish("SYSTEM_HALT", {"tick": self.tick_count})
        last_phys = getattr(self.cortex, "last_physics", {})
        world_data = self.cortex.gather_state(last_phys).get("world", {})
        continuity_packet = {
            "location": world_data.get("orbit", ["Void"])[0],
            "last_output": self.cortex.dialogue_buffer[-1] if self.cortex.dialogue_buffer else "Silence.",
            "inventory": self.gordon.inventory}
        try:
            print(f"{Prisma.GRY}[MEMORY]: Freezing State...{Prisma.RST}")
            mito_traits = {}
            if hasattr(self.bio.mito, 'state_ref'):
                mito_traits = self.bio.mito.state_ref.__dict__
            else:
                mito_traits = self.bio.mito.adapt(0)
            self.mind.mem.save(
                health=self.health,
                stamina=self.stamina,
                mutations={},
                trauma_accum=self.trauma_accum,
                joy_history=[],
                mitochondria_traits=mito_traits,
                antibodies=list(self.bio.immune.active_antibodies),
                soul_data=self.soul.to_dict(),
                village_data=self._gather_village_state(),
                continuity=continuity_packet,
                world_atlas=self.phys.nav.export_atlas() if hasattr(self.phys, "nav") else {})
        except Exception as e:
            print(f"{Prisma.RED}[MEMORY]: Save Failed: {e}{Prisma.RST}")
        subsystems = [
            ("LEXICON", self.lex, "save"),
            ("AKASHIC", self.akashic, "save_all")]
        for name, sys, method in subsystems:
            if hasattr(sys, method):
                try:
                    print(f"{Prisma.GRY}[{name}]: Persisting...{Prisma.RST}")
                    getattr(sys, method)()
                except Exception as e:
                    print(f"{Prisma.RED}[{name}]: Failed: {e}{Prisma.RST}")


if __name__ == "__main__":
    print(f"\n{Prisma.paint('♦ BONEAMANITA 14.9.5', 'M')}")
    sys_config = ConfigWizard.load_or_create()
    engine = BoneAmanita(config=sys_config)
    with SessionGuardian(engine) as session:
        session.engage_cold_boot()
        while True:
            try:
                user_in = input(f"{Prisma.paint(f'{session.user_name} >', 'W')} ")
            except EOFError:
                break
            if user_in.lower() in ["exit", "quit", "/exit"]:
                break
            res = session.process_turn(user_in)
            if res.get("ui"): print(res["ui"])