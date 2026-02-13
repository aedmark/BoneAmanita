""" BONEAMANITA 15.2.1
 Architects: SLASH, KISHO, Taylor & Edmark
 Refactored by: THE TORVALDS & THE BEZALEL
 "The metabolic engine that drives the session."
"""

import os
import time
import json
import uuid
import random
import traceback
import sys
import re
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from bone_chronos import ChronosKeeper
from bone_core import EventBus, SystemHealth, TheObserver, TheLore, TelemetryService, RealityStack
from bone_types import Prisma, RealityLayer
from bone_config import BoneConfig, BonePresets
from bone_genesis import BoneGenesis
from bone_village import DeathGen
from bone_lexicon import TheLexicon
from bone_physics import CosmicDynamics, ZoneInertia
from bone_body import SomaticLoop
from bone_brain import TheCortex, LLMInterface, NoeticLoop
from bone_cycle import GeodesicOrchestrator
from bone_council import CouncilChamber

def typewriter(text: str, speed: float = 0.005, end: str = "\n"):
    tokens = re.split(r'(\x1b\[[0-9;]*m)', text)
    for token in tokens:
        if token.startswith('\x1b['):
            sys.stdout.write(token)
            sys.stdout.flush()
        else:
            for char in token:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(speed)
    sys.stdout.write(end)

@dataclass
class HostStats:
    latency: float
    efficiency_index: float

class SessionGuardian:
    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Prisma.paint('┌──────────────────────────────────────────┐', 'M')}")
        print(f"{Prisma.paint('│ BONEAMANITA TERMINAL // VERSION 15.2.1   │', 'M')}")
        print(f"{Prisma.paint('└──────────────────────────────────────────┘', 'M')}")
        boot_logs = self.engine_instance.events.flush()
        for log in boot_logs:
            print(f"{Prisma.GRY}   >>> {log['text']}{Prisma.RST}")
            time.sleep(0.05)
        typewriter(f"{Prisma.GRY}...Initializing KernelHash: {self.engine_instance.kernel_hash}...{Prisma.RST}")
        typewriter(f"{Prisma.paint('>>> SYSTEM: LISTENING', 'G')}")
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
                print(f"{Prisma.GRY}{full_trace}{Prisma.RST}")
        print(f"{Prisma.paint('Connection Severed.')}")
        return exc_type is KeyboardInterrupt

class ConfigWizard:
    CONFIG_FILE = "bone_config.json"

    @staticmethod
    def load_or_create():
        if os.path.exists(ConfigWizard.CONFIG_FILE):
            try:
                with open(ConfigWizard.CONFIG_FILE, encoding='utf-8') as f:
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
            print(f"{Prisma.YEL}   >>> Corrupt Config backed up to: {backup_name}{Prisma.RST}")
        except:
            pass

    @staticmethod
    def _run_setup():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Prisma.CYN}/// SYSTEM INITIALIZATION SEQUENCE ///{Prisma.RST}")
        typewriter("No configuration detected. Initiating manual override...", speed=0.02)
        print("------------------------------------------------")
        print(f"\n{Prisma.WHT}[STEP 1]: IDENTITY{Prisma.RST}")
        user_name = input(f"{Prisma.GRY}Identify yourself (Default: TRAVELER): {Prisma.RST}").strip() or "TRAVELER"
        print(f"\n{Prisma.WHT}[STEP 2]: REALITY MODE{Prisma.RST}")
        print(f"1. {Prisma.GRN}Adventure{Prisma.RST}    - [Survival, Inventory, Map]")
        print(f"2. {Prisma.CYN}Conversation{Prisma.RST} - [Pure Dialogue, No Mechanics]")
        print(f"3. {Prisma.VIOLET}Creative{Prisma.RST}     - [High Voltage, Hallucination]")
        print(f"4. {Prisma.GRY}Technical{Prisma.RST}    - [Debug, Raw Data]")
        mode_choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        mode_map = {"1": "ADVENTURE", "2": "CONVERSATION", "3": "CREATIVE", "4": "TECHNICAL"}
        boot_mode = mode_map.get(mode_choice, "ADVENTURE")

        print(f"\n{Prisma.WHT}[STEP 3]: CORTEX BACKEND{Prisma.RST}")
        print(f"1. {Prisma.GRN}Ollama (Local){Prisma.RST}")
        print(f"2. {Prisma.CYN}OpenAI (Cloud){Prisma.RST}")
        print(f"3. {Prisma.VIOLET}LM Studio (Local){Prisma.RST}")
        print(f"4. {Prisma.GRY}Mock (Simulation){Prisma.RST}")
        choice = input(f"{Prisma.paint('>', 'C')} ").strip()

        config = {"user_name": user_name, "boot_mode": boot_mode}

        if choice == "2":
            config["provider"] = "openai"
            config["base_url"] = "https://api.openai.com/v1/chat/completions"
            config["model"] = input(f"Model ID [gpt-4]: ").strip() or "gpt-4"
            api_key = input(f"{Prisma.RED}Enter API Key: {Prisma.RST}").strip()
            config["api_key"] = api_key
        elif choice == "3":
            config["provider"] = "lm_studio"
            config["base_url"] = "http://127.0.0.1:1234/v1/chat/completions"
            config["model"] = "local-model"
        elif choice == "4":
            config["provider"] = "mock"
            config["model"] = "simulation"
        else:
            config["provider"] = "ollama"
            config["base_url"] = "http://127.0.0.1:11434/v1/chat/completions"
            config["model"] = input(f"Model ID [llama3]: ").strip() or "llama3"

        try:
            with open(ConfigWizard.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            typewriter(f"\n{Prisma.GRN}✔ CONFIGURATION COMMITTED.{Prisma.RST}", speed=0.02)
            time.sleep(1)
        except Exception as e:
            print(f"{Prisma.RED}Write Failed: {e}{Prisma.RST}")
            sys.exit(1)
        return config

class BoneAmanita:
    events: EventBus

    def __init__(self, config: Dict[str, Any]):
        self.cmd = None
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.config = config
        self.user_name = config.get("user_name", "TRAVELER")
        self.chronos = ChronosKeeper(self)
        self.boot_mode = config.get("boot_mode", "ADVENTURE").upper()
        if self.boot_mode not in BonePresets.MODES:
            self.boot_mode = "ADVENTURE"
        self.mode_settings = BonePresets.MODES[self.boot_mode]
        self.suppressed_agents = self.mode_settings.get("village_suppression", [])
        self.config["mode_settings"] = self.mode_settings
        self.health = BoneConfig.MAX_HEALTH
        self.stamina = BoneConfig.MAX_STAMINA
        self.trauma_accum = {}
        self.tick_count = 0
        self.events = EventBus()
        self.events.log("...Bootstrapping Core...", "BOOT")
        self.lex = TheLexicon
        self.lex.initialize()
        self.lex.compile_antigens()
        anatomy = BoneGenesis.ignite(self.config, self.lex, events_ref=self.events)
        self.akashic = anatomy["akashic"]
        self.embryo = anatomy["embryo"]
        self.soul = anatomy["soul"]
        self.oroboros = anatomy["oroboros"]
        self.drivers = anatomy["drivers"]
        self.symbiosis = anatomy["symbiosis"]
        self.phys = self.embryo.physics
        self.mind = self.embryo.mind
        self.bio = self.embryo.bio
        self.shimmer = self.embryo.shimmer
        self.bio.setup_listeners()
        v = anatomy["village"]
        self.gordon = v["gordon"]
        self.navigator = v["navigator"]
        self.tinkerer = v["tinkerer"]
        self.death_gen = v["death_gen"]
        self.bureau = v["bureau"]
        self.town_hall = v["town_hall"]
        self.repro = v["repro"]
        self.zen = v["zen"]
        self.critics = v["critics"]
        self.therapy = v["therapy"]
        self.limbo = v["limbo"]
        self.kintsugi = v["kintsugi"]
        self.soul.engine = self
        self.council = CouncilChamber(self)
        self.village = {
            "town_hall": self.town_hall,
            "bureau": self.bureau,
            "zen": self.zen,
            "tinkerer": self.tinkerer,
            "critics": self.critics,
            "navigator": self.navigator,
            "limbo": self.limbo,
            "council": self.council,
            "therapy": self.therapy,
            "enneagram": self.drivers.enneagram
        }
        if self.phys:
            self.phys.dynamics = CosmicDynamics()
            self.cosmic = self.phys.dynamics
            self.stabilizer = ZoneInertia()
        self.telemetry = TelemetryService.get_instance()
        self.system_health = SystemHealth()
        self.observer = TheObserver()
        self.system_health.link_observer(self.observer)
        self.reality_stack = RealityStack()
        self._load_system_prompts()
        self._initialize_cognition()
        self.host_stats = HostStats(latency=0.0, efficiency_index=1.0)
        self._validate_state()
        self._apply_boot_mode()

    def _load_system_prompts(self):
        try:
            paths = ["lore/system_prompts.json", "dev/lore/system_prompts.json"]
            loaded = False
            for p in paths:
                if os.path.exists(p):
                    with open(p, encoding='utf-8') as f:
                        self.prompt_library = json.load(f)
                    print(f"{Prisma.GRY}...Prompt Library Loaded from {p}...{Prisma.RST}")
                    loaded = True
                    break
            if not loaded:
                print(f"{Prisma.YEL}WARNING: system_prompts.json not found. Using defaults.{Prisma.RST}")
                self.prompt_library = {}
        except Exception as e:
            print(f"{Prisma.RED}CRITICAL: Could not load prompts: {e}{Prisma.RST}")
            self.prompt_library = {}

    def _initialize_cognition(self):
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.gordon, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.cycle_controller = GeodesicOrchestrator(self)

        llm_args = {
            k: v for k, v in self.config.items()
            if k in ["provider", "base_url", "api_key", "model"]}

        client = LLMInterface(events_ref=self.events, **llm_args)
        self.cortex = TheCortex.from_engine(self, llm_client=client)

    def _validate_state(self):
        tuning_key = self.mode_settings.get("tuning", "STANDARD")
        if hasattr(BonePresets, tuning_key):
            BoneConfig.load_preset(getattr(BonePresets, tuning_key))

        if self.mind.mem.session_health:
            self.health = self.mind.mem.session_health
            self.stamina = self.mind.mem.session_stamina
            self.trauma_accum = self.mind.mem.session_trauma_vector or {}
        if self.tick_count == 0 and self.bio.mito:
            self.bio.mito.state.atp_pool = BoneConfig.BIO.STARTING_ATP

    def _apply_boot_mode(self):
        self.events.log(f"Engaging Mode: {self.boot_mode}")

        layer = self.mode_settings.get("ui_layer", RealityLayer.SIMULATION)
        self.reality_stack.stabilize_at(layer)

        prompt_key = self.mode_settings.get("prompt_key", "ADVENTURE")
        if self.prompt_library and prompt_key in self.prompt_library:
            if self.cortex and self.cortex.composer:
                self.cortex.composer.load_template(self.prompt_library[prompt_key])
                self.events.log(f"Neural Pathway Re-aligned: {prompt_key}", "CORTEX")
        else:
            self.events.log(f"Prompt Template '{prompt_key}' not found.", "WARN")

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
            mercy_logs = [e['text'] for e in self.events.get_recent_logs(2) if "CATHARSIS" in e['text']]
            if mercy_logs:
                return {
                    "ui": f"\n\n{mercy_logs[-1]}",
                    "logs": mercy_logs,
                    "metrics": self.get_metrics()
                }

        if self.health <= 0.0:
            last_phys = getattr(self.cortex, "last_physics", {})
            return self.trigger_death(last_phys)

        if not is_system and hasattr(self, 'soul') and hasattr(self.soul, 'anchor'):
            if self.host_stats.efficiency_index < 0.6:
                reliance_proxy = 0.9 if self.host_stats.efficiency_index < 0.4 else 0.5
                self.soul.anchor.check_domestication(reliance_proxy)

        try:
            cortex_packet = self.cortex.process(user_input=user_message, is_system=is_system)

            if self.gordon and "GORDON" not in self.suppressed_agents:
                loot_candidate = self.gordon.parse_loot(user_message, cortex_packet.get("ui", ""))
                if loot_candidate:
                    acquire_msg = self.gordon.acquire(loot_candidate)
                    cortex_packet["logs"].append(acquire_msg)
                    cortex_packet["ui"] += f"\n\n> {acquire_msg}"

            if hasattr(self.cortex, "last_physics") and self.cortex.last_physics:
                world_state = self.cortex.gather_state(self.cortex.last_physics).get("world", {})
                orbit_state = world_state.get("orbit", ["Unknown"])[0]
                if "physics" in cortex_packet and isinstance(cortex_packet["physics"], dict):
                    cosmic_drag = 0.5 if orbit_state == "VOID_DRIFT" else 0.0
                    BoneAmanita.apply_cosmic_physics(
                        cortex_packet["physics"],
                        orbit_state,
                        cosmic_drag)

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
            if "BUREAU" not in self.suppressed_agents:
                real_phys = cortex_packet.get("physics", {})
                if hasattr(real_phys, "to_dict"):
                    real_phys = real_phys.to_dict()
                if not real_phys:
                    real_phys = {"raw_text": cortex_packet.get("ui", ""), "voltage": 1.0, "truth_ratio": 1.0}

                audit = self.bureau.audit(real_phys, {"health": self.health}, origin="SYSTEM")
                if audit and "ui" in audit:
                    cortex_packet["ui"] += f"\n\n{audit['ui']}"

        self.observer.clock_out(turn_start)
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
        meta_parts = text.strip().split()
        cmd = meta_parts[0].lower()
        ui_msg = ""
        if cmd == "//layer":
            if len(meta_parts) >= 2:
                sub = meta_parts[1].lower()
                if sub == "push" and len(meta_parts) > 2:
                    if self.reality_stack.push_layer(int(meta_parts[2])):
                        ui_msg = f"Layer Pushed: {meta_parts[2]}"
                elif sub == "pop":
                    self.reality_stack.pop_layer()
                    ui_msg = "Layer Popped."
                elif sub == "debug":
                    self.reality_stack.push_layer(RealityLayer.DEBUG)
                    ui_msg = "Debug Mode Engaged."
            else:
                ui_msg = f"Current Layer: {self.reality_stack.current_depth}"
        elif cmd == "//inject":
            payload = " ".join(meta_parts[1:])
            self.events.log(payload, "INJECT")
            ui_msg = f"Injected: {payload}"
        else:
            ui_msg = f"Unknown Meta-Command: {cmd}"
        return {"ui": f"{Prisma.GRY}[META] {ui_msg}{Prisma.RST}", "logs": [], "metrics": self.get_metrics()}

    def trigger_death(self, last_phys) -> Dict:
        if self.death_gen is None:
             return {"type": "DEATH", "ui": f"{Prisma.RED}*** CRITICAL FAILURE (NO DEATH PROTOCOL) ***{Prisma.RST}", "logs": []}

        eulogy_text, cause_code = DeathGen.eulogy(last_phys, self.bio.mito.state, self.trauma_accum)
        death_log = [f"\n{Prisma.RED}SYSTEM HALT: {eulogy_text}{Prisma.RST}"]

        legacy_msg = self.oroboros.crystallize(cause_code, self.soul)
        death_log.append(f"{Prisma.MAG}🐍 {legacy_msg}{Prisma.RST}")

        continuity_packet = {
            "location": self.cortex.gather_state(self.cortex.last_physics or {}).get("world", {}).get("orbit", ["Void"])[0],
            "last_output": self.cortex.dialogue_buffer[-1] if self.cortex.dialogue_buffer else "Silence.",
            "inventory": self.gordon.inventory if self.gordon else []}

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

        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self.get_metrics()}

    def get_metrics(self, atp=0.0):
        real_atp = atp
        if real_atp <= 0.0 and hasattr(self, 'bio') and hasattr(self.bio, 'mito'):
             try:
                 if hasattr(self.bio.mito, 'state'):
                     real_atp = getattr(self.bio.mito.state, 'atp_pool', 0.0)
             except Exception:
                 pass
        return {"health": self.health, "stamina": self.stamina, "atp": real_atp, "tick": self.tick_count}

    def emergency_save(self, exit_cause="UNKNOWN"):
        return self.chronos.emergency_dump(exit_cause)

    def _get_crash_path(self, prefix="crash"):
        return self.chronos.get_crash_path(prefix)

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
        return cold_result

    def save_checkpoint(self, history: list = None) -> str:
        return self.chronos.save_checkpoint(history)

    def resume_checkpoint(self) -> Tuple[bool, list]:
        return self.chronos.resume_checkpoint()

    def shutdown(self):
        self.chronos.perform_shutdown()

if __name__ == "__main__":
    sys_config = ConfigWizard.load_or_create()
    engine = BoneAmanita(config=sys_config)
    with SessionGuardian(engine) as session:
        boot_packet = session.engage_cold_boot()
        if boot_packet and boot_packet.get("ui"):
            typewriter(boot_packet["ui"])
        while True:
            try:
                user_in = input(f"{Prisma.paint(f'{session.user_name} >', 'W')} ")
            except EOFError:
                break
            if user_in.lower() in ["exit", "quit", "/exit"]:
                break
            res = session.process_turn(user_in)
            if res.get("ui"):
                if "──────" in res["ui"]:
                    parts = res["ui"].split("──────")
                    dashboard = parts[0] + "────────────────────────────────────────────────────────────"
                    content = parts[-1].strip()
                    print(dashboard)
                    typewriter("\n" + content)
                else:
                    typewriter(res["ui"])