"""bone_main.py"""

import os, time, json, uuid, random, traceback, sys, re
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from bone_commands import CommandProcessor
from bone_core import EventBus, SystemHealth, TheObserver, LoreManifest, TelemetryService, RealityStack
from bone_types import Prisma, RealityLayer
from bone_config import BoneConfig, BonePresets
from bone_genesis import BoneGenesis
from bone_lexicon import LexiconService
from bone_physics import CosmicDynamics, ZoneInertia
from bone_protocols import ChronosKeeper
from bone_body import SomaticLoop
from bone_brain import TheCortex, LLMInterface, NoeticLoop
from bone_cycle import GeodesicOrchestrator
from bone_council import CouncilChamber

ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;]*m)")

def typewriter(text: str, speed: float = 0.00025, end: str = "\n"):
    if speed < 0.001:
        print(text, end=end)
        return
    type_parts = ANSI_SPLIT.split(text)
    for part in type_parts:
        if not part:
            continue
        if part.startswith("\x1b"):
            sys.stdout.write(part)
        else:
            for char in part:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(speed)
    sys.stdout.write(end)
    sys.stdout.flush()


@dataclass
class HostStats:
    latency: float
    efficiency_index: float


class SessionGuardian:
    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        os.system("cls" if os.name == "nt" else "clear")
        top_bar = LoreManifest.get_instance().get_ux(
            "main_strings",
            "term_header_top",
            "┌──────────────────────────────────────────┐",
        )
        mid_bar = LoreManifest.get_instance().get_ux(
            "main_strings",
            "term_header_mid",
            "│ BONEAMANITA TERMINAL // VERSION 16.3.0   │",
        )
        bot_bar = LoreManifest.get_instance().get_ux(
            "main_strings",
            "term_header_bot",
            "└──────────────────────────────────────────┘",
        )
        print(f"{Prisma.paint(top_bar, 'M')}")
        print(f"{Prisma.paint(mid_bar, 'M')}")
        print(f"{Prisma.paint(bot_bar, 'M')}")
        boot_logs = self.engine_instance.events.flush()
        for log in boot_logs:
            print(f"{Prisma.GRY}   >>> {log['text']}{Prisma.RST}")
            time.sleep(0.05)

        init_msg = LoreManifest.get_instance().get_ux(
            "main_strings", "init_hash", "...Initializing KernelHash: {hash}..."
        )
        typewriter(
            f"{Prisma.GRY}{init_msg.format(hash=self.engine_instance.kernel_hash)}{Prisma.RST}"
        )
        sys_msg = LoreManifest.get_instance().get_ux("main_strings", "sys_listening", ">>> SYSTEM: LISTENING")
        typewriter(f"{Prisma.paint(sys_msg, 'G')}")
        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        halt_msg = LoreManifest.get_instance().get_ux("main_strings", "sys_halt", "--- SYSTEM HALT ---")
        print(f"\n{Prisma.paint(halt_msg, 'R')}")
        if self.engine_instance:
            self.engine_instance.shutdown()

        if exc_type:
            is_interrupt = issubclass(exc_type, KeyboardInterrupt)
            if not is_interrupt:
                crash_msg = LoreManifest.get_instance().get_ux("main_strings", "crash_msg", "CRASH: {exc_val}")
                print(f"{Prisma.RED}{crash_msg.format(exc_val=exc_val)}{Prisma.RST}")
                if getattr(self.engine_instance, "boot_mode", "") == "TECHNICAL":
                    full_trace = "".join(
                        traceback.format_exception(exc_type, exc_val, exc_tb)
                    )
                    print(f"{Prisma.GRY}{full_trace}{Prisma.RST}")
                else:
                    lattice_msg = LoreManifest.get_instance().get_ux(
                        "main_strings",
                        "lattice_collapsed",
                        "The reality lattice collapsed. Check the developer logs.",
                    )
                    print(f"{Prisma.GRY}{lattice_msg}{Prisma.RST}")
        conn_msg = LoreManifest.get_instance().get_ux("main_strings", "conn_severed", "Connection Severed.")
        print(f"{Prisma.paint(conn_msg)}")
        return exc_type is KeyboardInterrupt


class ConfigWizard:
    CONFIG_FILE = "bone_config.json"

    @staticmethod
    def load_or_create():
        if os.path.exists(ConfigWizard.CONFIG_FILE):
            try:
                with open(ConfigWizard.CONFIG_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                err_msg = LoreManifest.get_instance().get_ux(
                    "main_strings", "config_load_err", "[CONFIG]: Load Error: {e}"
                )
                print(f"{Prisma.RED}{err_msg.format(e=e)}{Prisma.RST}")
                ConfigWizard._backup_corrupt_file()
        return ConfigWizard._run_setup()

    @staticmethod
    def _backup_corrupt_file():
        backup_name = f"{ConfigWizard.CONFIG_FILE}.{int(time.time())}.bak"
        try:
            os.rename(ConfigWizard.CONFIG_FILE, backup_name)
            msg = LoreManifest.get_instance().get_ux(
                "main_strings",
                "config_backup",
                "   >>> Corrupt Config backed up to: {backup_name}",
            )
            print(f"{Prisma.YEL}{msg.format(backup_name=backup_name)}{Prisma.RST}")
        except:
            pass

    @staticmethod
    def _run_setup():
        os.system("cls" if os.name == "nt" else "clear")
        seq_msg = LoreManifest.get_instance().get_ux(
            "main_strings", "init_seq", "/// SYSTEM INITIALIZATION SEQUENCE ///"
        )
        hyp_msg = LoreManifest.get_instance().get_ux(
            "main_strings",
            "init_hypervisor",
            "No configuration detected. Initiating VSL Hypervisor...",
        )
        print(f"{Prisma.paint(seq_msg, 'C')}")
        typewriter(hyp_msg, speed=0.02)

        step1 = LoreManifest.get_instance().get_ux("main_strings", "step1_id", "[STEP 1]: IDENTITY")
        prompt1 = LoreManifest.get_instance().get_ux(
            "main_strings", "prompt_id", "Identify yourself (Default: TRAVELER): "
        )
        print(f"\n{Prisma.paint(step1, 'W')}")
        user_name = input(f"{Prisma.GRY}{prompt1}{Prisma.RST}").strip() or "TRAVELER"

        step2 = LoreManifest.get_instance().get_ux(
            "main_strings", "step2_mode", "[STEP 2]: LATTICE RESONANCE (MODE)"
        )
        print(f"\n{Prisma.paint(step2, 'W')}")
        modes = [
            (
                "1",
                "ADVENTURE",
                LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "mode_adv_desc",
                    "Tactile, inventory-driven, high friction.",
                ),
                "G",
            ),
            (
                "2",
                "CONVERSATION",
                LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "mode_conv_desc",
                    "Pure philosophical dialogue, no mechanics.",
                ),
                "C",
            ),
            (
                "3",
                "CREATIVE",
                LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "mode_crea_desc",
                    "High voltage, associative leaps, brainstorming.",
                ),
                "V",
            ),
            (
                "4",
                "TECHNICAL",
                LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "mode_tech_desc",
                    "[SLASH COUNCIL] System architecture, debug, coding.",
                ),
                "0",
            ),
        ]
        for k, name, desc, col in modes:
            print(f"  {k}. {Prisma.paint(name, col):<25} - {desc}")

        prompt_mode = LoreManifest.get_instance().get_ux(
            "main_strings", "prompt_mode", "Select resonance vector (1-4): "
        )
        mode_choice = input(f"{Prisma.paint(prompt_mode, 'C')} ").strip()
        mode_map = {
            "1": "ADVENTURE",
            "2": "CONVERSATION",
            "3": "CREATIVE",
            "4": "TECHNICAL",
        }
        boot_mode = mode_map.get(mode_choice, "ADVENTURE")

        step3 = LoreManifest.get_instance().get_ux("main_strings", "step3_backend", "[STEP 3]: CORTEX BACKEND")
        print(f"\n{Prisma.paint(step3, 'W')}")
        backends = [
            ("1", "Ollama (Local)", "G"),
            ("2", "OpenAI (Cloud)", "C"),
            ("3", "LM Studio (Local)", "V"),
            ("4", "Mock (Simulation)", "0"),
        ]
        for k, name, col in backends:
            print(f"{k}. {Prisma.paint(name, col)}")
        choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        config = {"user_name": user_name, "boot_mode": boot_mode}
        if choice == "2":
            config.update(
                {
                    "provider": "openai",
                    "base_url": "https://api.openai.com/v1/chat/completions",
                }
            )
            config["model"] = input(f"Model ID [gpt-4]: ").strip() or "gpt-4"
            prompt_api = LoreManifest.get_instance().get_ux("main_strings", "prompt_api", "Enter API Key: ")
            config["api_key"] = input(f"{Prisma.paint(prompt_api, 'R')} ").strip()
        elif choice == "3":
            config.update(
                {
                    "provider": "lm_studio",
                    "base_url": "http://127.0.0.1:1234/v1/chat/completions",
                    "model": "local-model",
                }
            )
        elif choice == "4":
            config.update({"provider": "mock", "model": "simulation"})
        else:
            config.update(
                {
                    "provider": "ollama",
                    "base_url": "http://127.0.0.1:11434/v1/chat/completions",
                }
            )
            config["model"] = input(f"Model ID [llama3]: ").strip() or "llama3"

        try:
            with open(ConfigWizard.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            commit_msg = LoreManifest.get_instance().get_ux(
                "main_strings", "config_committed", "✔ CONFIGURATION COMMITTED."
            )
            typewriter(f"\n{Prisma.paint(commit_msg, 'G')}", speed=0.02)
            time.sleep(1)
        except Exception as e:
            fail_msg = LoreManifest.get_instance().get_ux("main_strings", "write_failed", "Write Failed: {e}")
            print(f"{Prisma.paint(fail_msg.format(e=e), 'R')}")
            sys.exit(1)
        return config


class BoneAmanita:
    events: EventBus

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.events = EventBus()
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.cmd = CommandProcessor(self, Prisma, config_ref=BoneConfig)
        self.user_name = config.get("user_name", "TRAVELER")
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
        boot_msg = LoreManifest.get_instance().get_ux("main_strings", "boot_core", "...Bootstrapping Core...")
        self.events.log(boot_msg, "BOOT")
        self.chronos = ChronosKeeper(self)
        self.lex = LexiconService
        self.lex.initialize()
        anatomy = BoneGenesis.ignite(self.config, self.lex, events_ref=self.events)
        self._unpack_anatomy(anatomy)
        self.events.subscribe("ITEM_DROP", self.town_hall.on_item_drop)
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
                    with open(p, encoding="utf-8") as f:
                        self.prompt_library = json.load(f)
                    msg = LoreManifest.get_instance().get_ux(
                        "main_strings",
                        "prompt_lib_loaded",
                        "...Prompt Library Loaded from {p}...",
                    )
                    print(f"{Prisma.GRY}{msg.format(p=p)}{Prisma.RST}")
                    loaded = True
                    break
            if not loaded:
                warn_msg = LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "prompt_lib_warn",
                    "WARNING: system_prompts.json not found. Using defaults.",
                )
                print(f"{Prisma.YEL}{warn_msg}{Prisma.RST}")
                self.prompt_library = {}
        except Exception as e:
            crit_msg = LoreManifest.get_instance().get_ux(
                "main_strings",
                "prompt_lib_crit",
                "CRITICAL: Could not load prompts: {e}",
            )
            print(f"{Prisma.RED}{crit_msg.format(e=e)}{Prisma.RST}")
            self.prompt_library = {}

    def _initialize_cognition(self):
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.cycle_controller = GeodesicOrchestrator(self)
        self.orchestrator = self.cycle_controller
        llm_args = {
            k: v
            for k, v in self.config.items()
            if k in ["provider", "base_url", "api_key", "model"]
        }
        client = LLMInterface(events_ref=self.events, **llm_args)
        self.cortex = TheCortex.from_engine(self, llm_client=client)

    def _validate_state(self):
        tuning_key = self.mode_settings.get("tuning", "STANDARD")
        if hasattr(BonePresets, tuning_key):
            BoneConfig.load_preset(getattr(BonePresets, tuning_key))
        if getattr(self.mind.mem, "session_health", None) is not None:
            self.health = self.mind.mem.session_health
            self.stamina = self.mind.mem.session_stamina
            self.trauma_accum = self.mind.mem.session_trauma_vector or {}
        if self.tick_count == 0 and self.bio.mito:
            self.bio.mito.state.atp_pool = BoneConfig.BIO.STARTING_ATP

    def _apply_boot_mode(self):
        msg = LoreManifest.get_instance().get_ux("main_strings", "engaging_mode", "Engaging Mode: {boot_mode}")
        self.events.log(msg.format(boot_mode=self.boot_mode))
        layer = self.mode_settings.get("ui_layer", RealityLayer.SIMULATION)
        if self.boot_mode == "TECHNICAL":
            layer = RealityLayer.SIMULATION
        self.reality_stack.stabilize_at(layer)
        prompt_key = self.mode_settings.get("prompt_key", "ADVENTURE")
        if self.prompt_library and prompt_key in self.prompt_library:
            if self.cortex and self.cortex.composer:
                self.cortex.composer.load_template(self.prompt_library[prompt_key])
                msg_align = LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "pathway_aligned",
                    "Neural Pathway Re-aligned: {prompt_key}",
                )
                self.events.log(msg_align.format(prompt_key=prompt_key), "CORTEX")
        else:
            msg_warn = LoreManifest.get_instance().get_ux(
                "main_strings",
                "prompt_not_found",
                "Prompt Template '{prompt_key}' not found.",
            )
            self.events.log(msg_warn.format(prompt_key=prompt_key), "WARN")
        active_mods = self.mode_settings.get("active_mods", [])
        if active_mods and hasattr(self, "consultant") and self.consultant:
            for mod in active_mods:
                if mod not in self.consultant.state.active_modules:
                    self.consultant.state.active_modules.append(mod)
            msg_mods = LoreManifest.get_instance().get_ux(
                "main_strings", "hardwired_mods", "Hard-wired Mod Chips: {mods}"
            )
            self.events.log(msg_mods.format(mods=", ".join(active_mods)), "SYS")

    def get_avg_voltage(self):
        observer = getattr(self.phys, "observer", self.phys)
        hist = getattr(observer, "voltage_history", [])

        if not hist:
            return 0.0
        return sum(hist) / len(hist)

    def _unpack_anatomy(self, anatomy):
        self.akashic = anatomy["akashic"]
        self.embryo = anatomy["embryo"]
        self.soul = anatomy["soul"]
        self.oroboros = anatomy["oroboros"]
        self.drivers = anatomy["drivers"]
        self.symbiosis = anatomy["symbiosis"]
        self.consultant = anatomy.get("consultant", None)
        self.phys = self.embryo.physics
        self.mind = self.embryo.mind
        self.bio = self.embryo.bio
        self.shimmer = self.embryo.shimmer
        self.bio.setup_listeners()
        v = anatomy.get("village", {})
        self.gordon = v.get("gordon")
        self.navigator = v.get("navigator")
        self.tinkerer = v.get("tinkerer")
        self.death_gen = v.get("death_gen")
        self.bureau = v.get("bureau")
        self.town_hall = v.get("town_hall")
        self.repro = v.get("repro")
        self.zen = v.get("zen")
        self.critics = v.get("critics")
        self.therapy = v.get("therapy")
        self.limbo = v.get("limbo")
        self.kintsugi = v.get("kintsugi")
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
            "enneagram": self.drivers.enneagram,
            "suppressed_agents": self.suppressed_agents,
        }

    def _update_host_stats(self, packet, turn_start):
        self.observer.clock_out(turn_start)
        burn_proxy = max(1.0, self.observer.last_cycle_duration * 5.0)
        novelty = packet.get("physics", {}).get("vector", {}).get("novelty", 0.5)
        self.host_stats.efficiency_index = min(1.0, (novelty * 10.0) / burn_proxy)
        self.host_stats.latency = self.observer.last_cycle_duration

    def process_turn(
        self, user_message: str, is_system: bool = False
    ) -> Dict[str, Any]:
        turn_start = self.observer.clock_in()
        self.observer.user_turns += 1
        self.tick_count += 1

        if self.cmd and self.cmd.execute(user_message):
            return self._phase_check_commands(user_message, already_executed=True)
        elif user_message.strip().startswith("//"):
            return self._handle_meta_command(user_message.strip())

        if not is_system and self.gordon:
            self.gordon.mode = "ADVENTURE"
            current_zone = "Unknown"
            if hasattr(self, "cortex") and hasattr(self.cortex, "last_physics"):
                current_zone = (
                    self.cortex.gather_state(self.cortex.last_physics or {})
                    .get("world", {})
                    .get("orbit", ["Unknown"])[0]
                )

            violation_msg = self.gordon.enforce_object_action_coupling(
                user_message, current_zone
            )
            if violation_msg:
                msg = LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "gordon_intercept",
                    "Gordon intercepted a premise violation. Shocking the Cortex.",
                )
                self.events.log(msg, "SYS")
                if hasattr(self, "cortex"):
                    self.cortex.ballast_active = True
                    self.cortex.gordon_shock = violation_msg

        rules = self.reality_stack.get_grammar_rules()
        if not rules["allow_narrative"]:
            halt_msg = LoreManifest.get_instance().get_ux("main_strings", "narrative_halt", "NARRATIVE HALT")
            return {
                "ui": f"{Prisma.RED}{halt_msg}{Prisma.RST}",
                "logs": [],
                "metrics": self.get_metrics(),
            }
        if self._ethical_audit():
            mercy_logs = [
                e["text"]
                for e in self.events.get_recent_logs(2)
                if "CATHARSIS" in e["text"]
            ]
            if mercy_logs:
                return {
                    "ui": f"\n\n{mercy_logs[-1]}",
                    "logs": mercy_logs,
                    "metrics": self.get_metrics(),
                }
        if self.health <= 0.0:
            last_phys = getattr(self.cortex, "last_physics", {})
            return self.trigger_death(last_phys)
        if not is_system and hasattr(self, "soul") and hasattr(self.soul, "anchor"):
            if self.host_stats.efficiency_index < 0.6:
                reliance_proxy = 0.9 if self.host_stats.efficiency_index < 0.4 else 0.5
                self.soul.anchor.check_domestication(reliance_proxy)
        try:
            cortex_packet = self.cortex.process(
                user_input=user_message, is_system=is_system
            )
            if hasattr(self.mind, "mem"):
                self.health = self.mind.mem.session_health
                self.stamina = self.mind.mem.session_stamina
                self.trauma_accum = self.mind.mem.session_trauma_vector or {}
            if self.health <= 0.0:
                return self.trigger_death(cortex_packet.get("physics", {}))
        except Exception:
            full_trace = traceback.format_exc()
            crit_msg = LoreManifest.get_instance().get_ux(
                "main_strings",
                "cortex_crit_fail",
                "*** CORTEX CRITICAL FAILURE ***\n{trace}",
            )
            return {
                "ui": f"{Prisma.RED}{crit_msg.format(trace=full_trace)}{Prisma.RST}",
                "logs": ["CRITICAL FAILURE"],
                "metrics": self.get_metrics(),
            }
        self._update_host_stats(cortex_packet, turn_start)
        self.save_checkpoint()
        return cortex_packet

    def _phase_check_commands(self, user_message, already_executed=False):
        clean_cmd = user_message.strip()
        if clean_cmd.startswith("//"):
            return self._handle_meta_command(clean_cmd)
        if self.cmd is None:
            err_msg = LoreManifest.get_instance().get_ux(
                "main_strings",
                "cmd_err_init",
                "ERR: Command interface not initialized.",
            )
            return {
                "ui": f"{Prisma.RED}{err_msg}{Prisma.RST}",
                "logs": [],
            }

        if not already_executed:
            self.cmd.execute(clean_cmd)

        cmd_logs = [e["text"] for e in self.events.flush()]
        default_exec = LoreManifest.get_instance().get_ux("main_strings", "cmd_executed", "Command Executed.")
        ui_output = "\n".join(cmd_logs) if cmd_logs else default_exec
        return {
            "type": "COMMAND",
            "ui": f"\n{ui_output}",
            "logs": cmd_logs,
            "metrics": self.get_metrics(),
        }

    def _handle_meta_command(self, text: str) -> Dict[str, Any]:
        meta_parts = text.strip().split()
        cmd = meta_parts[0].lower()
        ui_msg = ""
        if cmd == "//layer":
            if len(meta_parts) >= 2:
                sub = meta_parts[1].lower()
                if sub == "push" and len(meta_parts) > 2:
                    if self.reality_stack.push_layer(int(meta_parts[2])):
                        msg = LoreManifest.get_instance().get_ux(
                            "main_strings", "layer_pushed", "Layer Pushed: {layer}"
                        )
                        ui_msg = msg.format(layer=meta_parts[2])
                elif sub == "pop":
                    self.reality_stack.pop_layer()
                    ui_msg = LoreManifest.get_instance().get_ux("main_strings", "layer_popped", "Layer Popped.")
                elif sub == "debug":
                    self.reality_stack.push_layer(RealityLayer.DEBUG)
                    ui_msg = LoreManifest.get_instance().get_ux(
                        "main_strings", "debug_engaged", "Debug Mode Engaged."
                    )
            else:
                msg = LoreManifest.get_instance().get_ux("main_strings", "current_layer", "Current Layer: {layer}")
                ui_msg = msg.format(layer=self.reality_stack.current_depth)
        elif cmd == "//inject":
            payload = " ".join(meta_parts[1:])
            self.events.log(payload, "INJECT")
            msg = LoreManifest.get_instance().get_ux("main_strings", "injected", "Injected: {payload}")
            ui_msg = msg.format(payload=payload)
        else:
            msg = LoreManifest.get_instance().get_ux("main_strings", "unknown_meta", "Unknown Meta-Command: {cmd}")
            ui_msg = msg.format(cmd=cmd)
        return {
            "ui": f"{Prisma.GRY}[META] {ui_msg}{Prisma.RST}",
            "logs": [],
            "metrics": self.get_metrics(),
        }

    def trigger_death(self, last_phys) -> Dict:
        if self.death_gen is None:
            crit_msg = LoreManifest.get_instance().get_ux(
                "main_strings",
                "death_no_proto",
                "*** CRITICAL FAILURE (NO DEATH PROTOCOL) ***",
            )
            return {
                "type": "DEATH",
                "ui": f"{Prisma.RED}{crit_msg}{Prisma.RST}",
                "logs": [],
            }
        eulogy_text, cause_code = self.death_gen.eulogy(
            last_phys, self.bio.mito.state, self.trauma_accum
        )
        halt_msg = LoreManifest.get_instance().get_ux("main_strings", "death_halt", "SYSTEM HALT: {eulogy_text}")
        death_log = [
            f"\n{Prisma.RED}{halt_msg.format(eulogy_text=eulogy_text)}{Prisma.RST}"
        ]
        legacy_msg = self.oroboros.crystallize(cause_code, self.soul)
        death_log.append(f"{Prisma.MAG}🐍 {legacy_msg}{Prisma.RST}")
        continuity_packet = {
            "location": self.cortex.gather_state(self.cortex.last_physics or {})
            .get("world", {})
            .get("orbit", ["Void"])[0],
            "last_output": (
                self.cortex.dialogue_buffer[-1]
                if self.cortex.dialogue_buffer
                else "Silence."
            ),
            "inventory": self.gordon.inventory if self.gordon else [],
        }
        try:
            mutations_data = (
                self.repro.attempt_reproduction(self, "MITOSIS")[1]
                if getattr(self, "repro", None)
                else {}
            )
            immune_data = (
                list(self.bio.immune.active_antibodies)
                if getattr(self.bio, "immune", None)
                else []
            )
            self.bio.mito.adapt(0)
            mito_state = (
                self.bio.mito.state.__dict__
                if hasattr(self.bio.mito.state, "__dict__")
                else {}
            )

            path = self.mind.mem.save(
                health=0,
                stamina=self.stamina,
                mutations=mutations_data,
                trauma_accum=self.trauma_accum,
                joy_history=[],
                mitochondria_traits=mito_state,
                antibodies=immune_data,
                soul_data=self.soul.to_dict(),
                continuity=continuity_packet,
            )
            saved_msg = LoreManifest.get_instance().get_ux(
                "main_strings", "legacy_saved", "   [LEGACY SAVED: {path}]"
            )
            death_log.append(f"{Prisma.WHT}{saved_msg.format(path=path)}{Prisma.RST}")
        except Exception as e:
            fail_msg = LoreManifest.get_instance().get_ux("main_strings", "save_failed", "Save Failed: {e}")
            death_log.append(fail_msg.format(e=e))
        return {
            "type": "DEATH",
            "ui": "\n".join(death_log),
            "logs": death_log,
            "metrics": self.get_metrics(),
        }

    def get_metrics(self, atp=0.0):
        real_atp = atp
        if real_atp <= 0.0 and hasattr(self, "bio") and hasattr(self.bio, "mito"):
            real_atp = getattr(self.bio.mito.state, "atp_pool", 0.0)
        return {
            "health": self.health,
            "stamina": self.stamina,
            "atp": real_atp,
            "tick": self.tick_count,
            "efficiency": getattr(self.host_stats, "efficiency_index", 1.0),
        }

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
            msg = LoreManifest.get_instance().get_ux(
                "main_strings",
                "mercy_venting",
                "MERCY SIGNAL: Pressure Critical. Venting...",
            )
            self.events.log(
                f"{Prisma.WHT}{msg}{Prisma.RST}",
                "SYS",
            )
            for k in self.trauma_accum:
                self.trauma_accum[k] *= CATHARSIS_DECAY
                if self.trauma_accum[k] < 0.01:
                    self.trauma_accum[k] = 0.0
            msg_cath = LoreManifest.get_instance().get_ux(
                "main_strings",
                "catharsis",
                "*** CATHARSIS *** The fever breaks. Logic cools.",
            )
            self.events.log(
                f"{Prisma.CYN}{msg_cath}{Prisma.RST}",
                "SENSATION",
            )
            self.health = min(self.health + CATHARSIS_HEAL_AMOUNT, MAX_HEALTH_CAP)
            return True
        return False

    def engage_cold_boot(self) -> Optional[Dict[str, Any]]:
        if self.tick_count > 0:
            return None
        if os.path.exists("saves/quicksave.json"):
            msg_pod = LoreManifest.get_instance().get_ux("main_strings", "stasis_pod", "...Detected Stasis Pod...")
            print(f"{Prisma.GRY}{msg_pod}{Prisma.RST}")
            success, history = self.resume_checkpoint()
            if success:
                if self.cortex:
                    self.cortex.restore_context(history)
                loc = (
                    self.embryo.continuity.get("location", "Unknown")
                    if self.embryo.continuity
                    else "Unknown"
                )

                last_scene = "Silence."
                if self.cortex and self.cortex.dialogue_buffer:
                    last_scene = self.cortex.dialogue_buffer[-1]
                elif self.embryo.continuity:
                    last_scene = self.embryo.continuity.get("last_output", "Silence.")

                msg_resume = LoreManifest.get_instance().get_ux(
                    "main_strings",
                    "resuming_timeline",
                    "**RESUMING TIMELINE**\nLocation: {loc}\n\n{last_scene}",
                )
                msg_restored = LoreManifest.get_instance().get_ux(
                    "main_strings", "timeline_restored", "Timeline Restored."
                )
                resume_text = msg_resume.format(loc=loc, last_scene=last_scene)
                return {"ui": resume_text, "logs": [msg_restored]}

        msg_synth = LoreManifest.get_instance().get_ux(
            "main_strings", "synth_reality", "...Synthesizing Initial Reality..."
        )
        print(f"{Prisma.GRY}{msg_synth}{Prisma.RST}")
        scenarios = LoreManifest.get_instance().get("SCENARIOS", {})
        archetypes = scenarios.get(
            "ARCHETYPES", ["A quiet room", "The edge of a forest", "A terminal screen"]
        )
        seed = random.choice(archetypes)
        msg_seed = LoreManifest.get_instance().get_ux("main_strings", "seed_loaded", "[SYS] Seed Loaded: '{seed}'")
        print(f"{Prisma.CYN}{msg_seed.format(seed=seed)}{Prisma.RST}")

        boot_prompt = f"SYSTEM_BOOT: {seed}"

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
                user_in = input(f"\n{Prisma.paint(f'{session.user_name} >', 'W')} ")
            except EOFError:
                break
            clean_in = user_in.strip().lower()
            if clean_in in ["exit", "quit", "/exit", "/quit"]:
                break
            res = session.process_turn(user_in)
            print(
                f"\n{Prisma.GRY}════════════════════════════════════════════════════════════{Prisma.RST}"
            )

            if res.get("ui"):
                if "────────" in res["ui"]:
                    dashboard, _, content = res["ui"].partition("\n\n")

                    print(f"\n{dashboard.strip()}\n")

                    typewriter(content.strip() + "\n", speed=0.005)
                else:
                    typewriter(res["ui"] + "\n", speed=0.005)
            if res.get("type") == "DEATH":
                term_msg = LoreManifest.get_instance().get_ux(
                    "main_strings", "session_term", "[SESSION TERMINATED]"
                )
                print(f"\n{Prisma.GRY}{term_msg}{Prisma.RST}")
                break
