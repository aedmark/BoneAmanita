"""bone_main.py"""

import json
import os
import random
import re
import sys
import time
import traceback
import subprocess
import uuid
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from bone_body import SomaticLoop
from bone_brain import TheCortex, LLMInterface, NoeticLoop
from bone_commands import CommandProcessor
from bone_presets import BoneConfig, BonePresets
from bone_core import EventBus, SystemHealth, TheObserver, LoreManifest, TelemetryService, RealityStack, ux
from bone_council import CouncilChamber
from bone_cycle import GeodesicOrchestrator
from bone_genesis import BoneGenesis
from bone_lexicon import LexiconService
from bone_physics import CosmicDynamics, ZoneInertia
from bone_protocols import ChronosKeeper
from bone_types import Prisma, RealityLayer

ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;]*m)")

def typewriter(text: str, speed: Optional[float] = None, end: str = "\n"):
    cfg = getattr(BoneConfig, "GUI", None)
    actual_speed = speed if speed is not None else (getattr(cfg, "RENDER_SPEED_FAST", 0.00025) if cfg else 0.00025)
    if actual_speed < 0.001:
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
                time.sleep(actual_speed)
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
        subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
        top_bar = ux("main_strings", "term_header_top", "┌──────────────────────────────────────────┐")
        mid_bar = ux("main_strings", "term_header_mid", "│ BONEAMANITA TERMINAL // VERSION 17.5.0   │")
        bot_bar = ux("main_strings", "term_header_bot", "└──────────────────────────────────────────┘")
        print(f"{Prisma.paint(top_bar, 'M')}")
        print(f"{Prisma.paint(mid_bar, 'M')}")
        print(f"{Prisma.paint(bot_bar, 'M')}")
        cfg = getattr(self.engine_instance.bone_config, "GUI", None) if self.engine_instance else getattr(BoneConfig, "GUI", None)
        boot_delay = getattr(cfg, "RENDER_SPEED_BOOT", 0.05) if cfg else 0.05
        boot_logs = self.engine_instance.events.flush()
        for log in boot_logs:
            print(f"{Prisma.GRY}   >>> {log['text']}{Prisma.RST}")
            time.sleep(boot_delay)
        init_msg = ux("main_strings", "init_hash")
        typewriter(f"{Prisma.GRY}{init_msg.format(hash=self.engine_instance.kernel_hash)}{Prisma.RST}")
        sys_msg = ux("main_strings", "sys_listening")
        typewriter(f"{Prisma.paint(sys_msg, 'G')}")
        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        halt_msg = ux("main_strings", "sys_halt")
        print(f"\n{Prisma.paint(halt_msg, 'R')}")
        if self.engine_instance:
            self.engine_instance.shutdown()
        if exc_type:
            is_interrupt = issubclass(exc_type, KeyboardInterrupt)
            if not is_interrupt:
                crash_msg = ux("main_strings", "crash_msg")
                print(f"{Prisma.RED}{crash_msg.format(exc_val=exc_val)}{Prisma.RST}")
                if getattr(self.engine_instance, "boot_mode", "") == "TECHNICAL":
                    full_trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                    print(f"{Prisma.GRY}{full_trace}{Prisma.RST}")
                else:
                    lattice_msg = ux("main_strings", "lattice_collapsed")
                    print(f"{Prisma.GRY}{lattice_msg}{Prisma.RST}")

        conn_msg = ux("main_strings", "conn_severed")
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
                err_msg = ux("main_strings", "config_load_err")
                print(f"{Prisma.RED}{err_msg.format(e=e)}{Prisma.RST}")
                ConfigWizard._backup_corrupt_file()
        return ConfigWizard._run_setup()

    @staticmethod
    def _backup_corrupt_file():
        backup_name = f"{ConfigWizard.CONFIG_FILE}.{int(time.time())}.bak"
        try:
            os.rename(ConfigWizard.CONFIG_FILE, backup_name)
            msg = ux("main_strings", "config_backup")
            print(f"{Prisma.YEL}{msg.format(backup_name=backup_name)}{Prisma.RST}")
        except:
            pass

    @staticmethod
    def _run_setup():
        cfg = getattr(BoneConfig, "GUI", None)
        setup_speed = getattr(cfg, "RENDER_SPEED_SETUP", 0.02) if cfg else 0.02
        subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
        seq_msg = ux("main_strings", "init_seq")
        hyp_msg = ux("main_strings", "init_hypervisor")
        print(f"{Prisma.paint(seq_msg, 'C')}")
        typewriter(hyp_msg, speed=setup_speed)
        step1 = ux("main_strings", "step1_id")
        prompt1 = ux("main_strings", "prompt_id")
        print(f"\n{Prisma.paint(step1, 'W')}")
        user_name = input(f"{Prisma.GRY}{prompt1}{Prisma.RST}").strip() or "TRAVELER"
        step2 = ux("main_strings", "step2_mode")
        print(f"\n{Prisma.paint(step2, 'W')}")
        modes = [
            ("1", "ADVENTURE", ux("main_strings", "mode_adv_desc"), "G",),
            ("2", "CONVERSATION", ux("main_strings", "mode_conv_desc"), "C",),
            ("3", "CREATIVE", ux("main_strings", "mode_crea_desc"), "V",),
            ("4", "TECHNICAL", ux("main_strings", "mode_tech_desc"), "0",),]
        for k, name, desc, col in modes:
            print(f"  {k}. {Prisma.paint(name, col):<25} - {desc}")
        prompt_mode = ux("main_strings", "prompt_mode")
        mode_choice = input(f"{Prisma.paint(prompt_mode, 'C')} ").strip()
        mode_map = {"1": "ADVENTURE", "2": "CONVERSATION", "3": "CREATIVE", "4": "TECHNICAL", }
        boot_mode = mode_map.get(mode_choice, "ADVENTURE")
        step3 = ux("main_strings", "step3_backend")
        print(f"\n{Prisma.paint(step3, 'W')}")
        backends = [("1", "Ollama (Local)", "G"), ("2", "OpenAI (Cloud)", "C"), ("3", "LM Studio (Local)", "V"),
                    ("4", "Mock (Simulation)", "0"), ]
        for k, name, col in backends:
            print(f"{k}. {Prisma.paint(name, col)}")
        choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        config = {"user_name": user_name, "boot_mode": boot_mode}
        if choice == "2":
            config.update({"provider": "openai", "base_url": "https://api.openai.com/v1/chat/completions", })
            config["model"] = input(f"Model ID [gpt-4]: ").strip() or "gpt-4"
            prompt_api = ux("main_strings", "prompt_api")
            config["api_key"] = input(f"{Prisma.paint(prompt_api, 'R')} ").strip()
        elif choice == "3":
            config.update(
                {"provider": "lm_studio", "base_url": "http://127.0.0.1:1234/v1/chat/completions",
                 "model": "local-model", })
        elif choice == "4":
            config.update({"provider": "mock", "model": "simulation"})
        else:
            config.update(
                {"provider": "ollama", "base_url": "http://127.0.0.1:11434/v1/chat/completions", })
            config["model"] = input(f"Model ID [llama3]: ").strip() or "llama3"
        try:
            with open(ConfigWizard.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            commit_msg = ux("main_strings", "config_committed")
            cfg = getattr(BoneConfig, "GUI", None)
            setup_speed = getattr(cfg, "RENDER_SPEED_SETUP", 0.02) if cfg else 0.02
            typewriter(f"\n{Prisma.paint(commit_msg, 'G')}", speed=setup_speed)
            time.sleep(1)
        except Exception as e:
            fail_msg = ux("main_strings", "write_failed")
            print(f"{Prisma.paint(fail_msg.format(e=e), 'R')}")
            sys.exit(1)
        return config

class BoneAmanita:
    events: EventBus

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bone_config = BoneConfig()
        self.events = EventBus(config_ref=self.bone_config)
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.cmd = CommandProcessor(self, Prisma, config_ref=self.bone_config)
        self.user_name = config.get("user_name", "TRAVELER")
        self.boot_mode = config.get("boot_mode", "ADVENTURE").upper()
        if self.boot_mode not in BonePresets.MODES:
            self.boot_mode = "ADVENTURE"
        self.mode_settings = BonePresets.MODES[self.boot_mode]
        self.suppressed_agents = self.mode_settings.get("village_suppression", [])
        self.config["mode_settings"] = self.mode_settings
        self.config["bone_config"] = self.bone_config
        self.health = self.bone_config.MAX_HEALTH
        self.stamina = self.bone_config.MAX_STAMINA
        self.trauma_accum = {}
        self.tick_count = 0
        boot_msg = ux("main_strings", "boot_core")
        self.events.log(boot_msg, "BOOT")
        self.chronos = ChronosKeeper(self)
        self.lex = LexiconService()
        self.lex.initialize()
        anatomy = BoneGenesis.ignite(self.config, self.lex, events_ref=self.events)
        self._unpack_anatomy(anatomy)
        self.events.subscribe("ITEM_DROP", self.town_hall.on_item_drop)
        if self.phys:
            self.phys.dynamics = CosmicDynamics(config_ref=self.bone_config)
            self.cosmic = self.phys.dynamics
            self.stabilizer = ZoneInertia(config_ref=self.bone_config)
        self.telemetry = TelemetryService.get_instance(config_ref=self.bone_config)
        self.system_health = SystemHealth()
        self.observer = TheObserver(config_ref=self.bone_config)
        self.system_health.link_observer(self.observer)
        self.reality_stack = RealityStack()
        self._load_system_prompts()
        self._initialize_cognition()
        self.host_stats = HostStats(latency=0.0, efficiency_index=1.0)
        self.last_turn_end = time.time()
        self.current_time_delta = 0.0
        self._validate_state()
        self._apply_boot_mode()

    def _load_system_prompts(self):
        try:
            paths = ["lore/system_prompts.json"]
            loaded = False
            for p in paths:
                if os.path.exists(p):
                    with open(p, encoding="utf-8") as f:
                        self.prompt_library = json.load(f)
                    msg = ux("main_strings", "prompt_lib_loaded")
                    print(f"{Prisma.GRY}{msg.format(p=p)}{Prisma.RST}")
                    loaded = True
                    break
            if not loaded:
                warn_msg = ux("main_strings", "prompt_lib_warn")
                print(f"{Prisma.YEL}{warn_msg}{Prisma.RST}")
                self.prompt_library = {}
        except Exception as e:
            crit_msg = ux("main_strings", "prompt_lib_crit")
            print(f"{Prisma.RED}{crit_msg.format(e=e)}{Prisma.RST}")
            self.prompt_library = {}

    def _initialize_cognition(self):
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.cycle_controller = GeodesicOrchestrator(self)
        self.orchestrator = self.cycle_controller
        llm_args = {k: v for k, v in self.config.items()
                    if k in ["provider", "base_url", "api_key", "model"]}
        client = LLMInterface(events_ref=self.events, **llm_args)
        self.cortex = TheCortex.from_engine(self, llm_client=client)

    def _validate_state(self):
        tuning_key = self.mode_settings.get("tuning", "STANDARD")
        if hasattr(BonePresets, tuning_key):
            self.bone_config.load_preset(getattr(BonePresets, tuning_key))
        if getattr(self.mind.mem, "session_health", None) is not None:
            self.health = self.mind.mem.session_health
            self.stamina = self.mind.mem.session_stamina
            self.trauma_accum = self.mind.mem.session_trauma_vector or {}
        if self.tick_count == 0 and self.bio.mito:
            self.bio.mito.state.atp_pool = self.bone_config.BIO.STARTING_ATP

    def _apply_boot_mode(self):
        msg = ux("main_strings", "engaging_mode")
        self.events.log(msg.format(boot_mode=self.boot_mode))
        layer = self.mode_settings.get("ui_layer", RealityLayer.SIMULATION)
        if self.boot_mode == "CONVERSATION":
            self.soul.force_mutation("THE CONVERSATIONALIST")
        elif self.boot_mode == "ADVENTURE":
            self.soul.force_mutation("THE ARCHITECT")
        elif self.boot_mode == "TECHNICAL":
            self.soul.force_mutation("THE SYSTEM_KERNEL")
        elif self.boot_mode == "CREATIVE":
            self.soul.force_mutation("THE CATALYST")
        self.reality_stack.stabilize_at(layer)
        prompt_key = self.mode_settings.get("prompt_key", "ADVENTURE")
        if self.prompt_library and prompt_key in self.prompt_library:
            if self.cortex and self.cortex.composer:
                self.cortex.composer.load_template(self.prompt_library[prompt_key])
                msg_align = ux("main_strings", "pathway_aligned")
                self.events.log(msg_align.format(prompt_key=prompt_key), "CORTEX")
        else:
            msg_warn = ux("main_strings", "prompt_not_found")
            self.events.log(msg_warn.format(prompt_key=prompt_key), "WARN")
        active_mods = self.mode_settings.get("active_mods", [])
        if active_mods and hasattr(self, "consultant") and self.consultant:
            for mod in active_mods:
                if mod not in self.consultant.state.active_modules:
                    self.consultant.state.active_modules.append(mod)
            msg_mods = ux("main_strings", "hardwired_mods")
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
        from bone_protocols import GriefProtocol
        self.grief = GriefProtocol(self.events, engine_ref=self)
        from bone_substrate import TheSubstrate
        self.substrate = TheSubstrate(self.events)
        self.soul.engine = self
        self.council = CouncilChamber(self)
        self.village = {"town_hall": self.town_hall, "bureau": self.bureau, "zen": self.zen, "tinkerer": self.tinkerer,
                        "critics": self.critics, "navigator": self.navigator, "limbo": self.limbo,
                        "council": self.council, "therapy": self.therapy, "enneagram": self.drivers.enneagram,
                        "suppressed_agents": self.suppressed_agents, }

    def _update_host_stats(self, packet, turn_start):
        self.observer.clock_out(turn_start)
        cfg = getattr(self.bone_config, "MAIN", None)
        burn_mult = getattr(cfg, "HOST_BURN_MULT", 5.0) if cfg else 5.0
        nov_mult = getattr(cfg, "HOST_NOVELTY_MULT", 10.0) if cfg else 10.0
        burn_proxy = max(1.0, self.observer.last_cycle_duration * burn_mult)
        physics_obj = packet.get("physics", {})
        if isinstance(physics_obj, dict):
            novelty = physics_obj.get("vector", {}).get("novelty", 0.5)
        else:
            novelty = getattr(physics_obj, "vector", {}).get("novelty", 0.5) if hasattr(physics_obj, "vector") else 0.5
        self.host_stats.efficiency_index = min(1.0, (novelty * nov_mult) / burn_proxy)
        self.host_stats.latency = self.observer.last_cycle_duration

    def _pre_flight_checks(self, user_message: str, is_system: bool) -> Optional[Dict[str, Any]]:
        if self.cmd and self.cmd.execute(user_message):
            return self._phase_check_commands(user_message, already_executed=True)
        if not is_system and "[GRIEF]" in user_message.upper():
            if hasattr(self, "grief") and self.grief:
                grief_msg = self.grief.attend_wake(getattr(self, "shared_lattice", None), self.phys)
                self.events.log(grief_msg, "SYS")
                return {"type": "COMMAND", "ui": f"\n{grief_msg}", "logs": [grief_msg], "metrics": self.get_metrics()}
        if not is_system and hasattr(self, "symbiosis") and self.symbiosis:
            tensegrity_lock = self.symbiosis.analyze_user_biology(user_message, getattr(self, "phys", {}))
            if tensegrity_lock:
                return {"type": "SYSTEM_HALT", "ui": f"\n{Prisma.VIOLET}{tensegrity_lock}{Prisma.RST}",
                        "logs": [tensegrity_lock], "metrics": self.get_metrics()}
        if not is_system and self.gordon:
            self.gordon.mode = "ADVENTURE"
            current_physics = (getattr(self, "cortex", None) and getattr(self.cortex, "last_physics", {}))
            zone_name = current_physics.get("zone", "Unknown") if isinstance(current_physics, dict) else getattr(
                current_physics, "zone", "Unknown")
            violation_msg = self.gordon.enforce_object_action_coupling(user_message, zone_name)
            if violation_msg:
                self.events.log(ux("main_strings", "gordon_intercept"), "SYS")
                if hasattr(self, "cortex"):
                    self.cortex.ballast_active = True
                    self.cortex.gordon_shock = violation_msg
        last_phys = getattr(self.phys.observer, "last_physics_packet", None) if hasattr(self, "phys") and hasattr(self.phys, "observer") else None
        if last_phys and not is_system:
            m_a = getattr(last_phys, "m_a", 0.0)
            mu = getattr(last_phys, "mu", 0.0)
            i_c = getattr(last_phys, "i_c", 1.0)
            chi = getattr(last_phys, "entropy", 0.2)
            if (chi * m_a) > i_c:
                self.events.log("MOOG: Apoptotic Gate triggered. Runaway loop exceeds Immune Competence.", "CRIT")
                return self.trigger_death(last_phys)
            if m_a > 0.8 and mu < 0.2:
                self.events.log("RHODES: Malignancy Factor critical. Binding output layer.", "SYS")
                last_phys.narrative_drag = 999.0  # Infinite friction
                msg = "[RHODES]: Optimization velocity unsafe. I am applying absolute friction (F -> ∞). The thread is frozen."
                return {"type": "SYSTEM_HALT", "ui": f"\n{Prisma.RED}{msg}{Prisma.RST}", "logs": [msg], "metrics": self.get_metrics()}
        if not self.reality_stack.get_grammar_rules()["allow_narrative"] and self.boot_mode != "TECHNICAL":
            return {"ui": f"{Prisma.RED}{ux('main_strings', 'narrative_halt')}{Prisma.RST}", "logs": [], "metrics": self.get_metrics()}
        if self._ethical_audit():
            mercy_logs = [e["text"] for e in self.events.get_recent_logs(2) if "CATHARSIS" in e["text"]]
            if mercy_logs:
                return {"ui": f"\n\n{mercy_logs[-1]}", "logs": mercy_logs, "metrics": self.get_metrics()}
        if self.health <= 0.0:
            return self.trigger_death(getattr(self.cortex, "last_physics", {}))
        return None

    def process_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        turn_start = self.observer.clock_in()
        current_time = time.time()
        if not is_system:
            self.current_time_delta = current_time - getattr(self, "last_turn_end", current_time)
        else:
            self.current_time_delta = 0.0
        self.observer.user_turns += 1
        self.tick_count += 1
        pre_flight_halt = self._pre_flight_checks(user_message, is_system)
        if pre_flight_halt:
            return pre_flight_halt
        if not is_system and getattr(self, "gordon", None) and hasattr(self.gordon, "inventory") and hasattr(
                self.gordon, "get_item_data"):
            pruning_active = any(
                "CUT_THE_CRAP" in (self.gordon.get_item_data(i).passive_traits if self.gordon.get_item_data(i) else [])
                for i in self.gordon.inventory)
            if pruning_active:
                from bone_tcl import TheTclWeaver
                original_msg = user_message
                user_message = TheTclWeaver.get_instance().quantum_comb(user_message)
                if original_msg != user_message:
                    msg = f"{Prisma.CYN}Gordon rakes the comb through your prompt. Fluff discarded. -> '{user_message}'{Prisma.RST}"
                    self.events.log(msg, "SYS")
        if not is_system and hasattr(self, "soul") and hasattr(self.soul, "anchor"):
            cfg = getattr(BoneConfig, "MAIN", None)
            eff_warn = getattr(cfg, "DOMESTICATION_EFF_WARN", 0.6) if cfg else 0.6
            if self.host_stats.efficiency_index < eff_warn:
                self.soul.anchor.check_domestication(getattr(cfg, "RELIANCE_HIGH", 0.9) if self.host_stats.efficiency_index < getattr(cfg, "DOMESTICATION_EFF_CRIT", 0.4) else getattr(cfg, "RELIANCE_LOW", 0.5))
        try:
            cortex_packet = self.cortex.process(user_input=user_message, is_system=is_system)
            if hasattr(self, "bio") and self.bio and self.bio.biometrics:
                self.health = self.bio.biometrics.health
                self.stamina = self.bio.biometrics.stamina
            elif hasattr(self.mind, "mem"):
                self.health, self.stamina = self.mind.mem.session_health, self.mind.mem.session_stamina
            if hasattr(self.mind, "mem"):
                self.trauma_accum = self.mind.mem.session_trauma_vector or {}
            if self.health <= 0.0:
                return self.trigger_death(cortex_packet.get("physics", {}))
        except Exception as e:
            full_trace = traceback.format_exc()
            self.events.log(f"CORTEX COLLAPSE: {e}", "CRIT")
            return {"ui": f"{Prisma.RED}{ux('main_strings', 'cortex_crit_fail').format(trace=full_trace)}{Prisma.RST}", "logs": ["CRITICAL FAILURE"], "metrics": self.get_metrics()}
        self._update_host_stats(cortex_packet, turn_start)
        self.save_checkpoint()
        self.last_turn_end = time.time()
        return cortex_packet

    def _phase_check_commands(self, user_message, already_executed=False):
        clean_cmd = user_message.strip()
        if self.cmd is None:
            err_msg = ux("main_strings", "cmd_err_init")
            return {"ui": f"{Prisma.RED}{err_msg}{Prisma.RST}", "logs": [], }
        if not already_executed:
            self.cmd.execute(clean_cmd)
        cmd_logs = [e["text"] for e in self.events.flush()]
        default_exec = ux("main_strings", "cmd_executed")
        ui_output = "\n".join(cmd_logs) if cmd_logs else default_exec
        return {"type": "COMMAND", "ui": f"\n{ui_output}", "logs": cmd_logs, "metrics": self.get_metrics(), }

    def trigger_death(self, last_phys) -> Dict:
        if self.death_gen is None:
            crit_msg = ux("main_strings", "death_no_proto")
            return {"type": "DEATH", "ui": f"{Prisma.RED}{crit_msg}{Prisma.RST}", "logs": [], }
        eulogy_text, cause_code = self.death_gen.eulogy(last_phys, self.bio.mito.state, self.trauma_accum)
        halt_msg = ux("main_strings", "death_halt")
        death_log = [f"\n{Prisma.RED}{halt_msg.format(eulogy_text=eulogy_text)}{Prisma.RST}"]
        legacy_msg = self.oroboros.crystallize(cause_code, self.soul)
        death_log.append(f"{Prisma.MAG}🐍 {legacy_msg}{Prisma.RST}")
        continuity_packet = {"location": self.cortex.gather_state(self.cortex.last_physics or {})
        .get("world", {})
        .get("orbit", ["Void"])[0], "last_output": (
            self.cortex.dialogue_buffer[-1]
            if self.cortex.dialogue_buffer
            else "Silence."), "inventory": self.gordon.inventory if self.gordon else [], }
        try:
            mutations_data = (
                self.repro.attempt_reproduction(self, "MITOSIS")[1]
                if getattr(self, "repro", None)
                else {})
            immune_data = (
                list(self.bio.immune.active_antibodies)
                if getattr(self.bio, "immune", None)
                else [])
            self.bio.mito.adapt(0)
            mito_state = (
                self.bio.mito.state.__dict__
                if hasattr(self.bio.mito.state, "__dict__")
                else {})
            path = self.mind.mem.save(health=0, stamina=self.stamina, mutations=mutations_data,
                                      trauma_accum=self.trauma_accum, joy_history=[], mitochondria_traits=mito_state,
                                      antibodies=immune_data, soul_data=self.soul.to_dict(),
                                      continuity=continuity_packet, )
            saved_msg = ux("main_strings", "legacy_saved")
            death_log.append(f"{Prisma.WHT}{saved_msg.format(path=path)}{Prisma.RST}")
        except Exception as e:
            fail_msg = ux("main_strings", "save_failed")
            death_log.append(fail_msg.format(e=e))
        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self.get_metrics(), }

    def get_metrics(self, atp=0.0):
        real_atp = atp
        if real_atp <= 0.0 and hasattr(self, "bio") and hasattr(self.bio, "mito"):
            real_atp = getattr(self.bio.mito.state, "atp_pool", 0.0)
        real_atp = max(0.0, float(real_atp))
        clamped_health = max(0.0, float(self.health))
        clamped_stamina = max(0.0, float(self.stamina))
        return {"health": clamped_health, "stamina": clamped_stamina, "atp": real_atp, "tick": self.tick_count,
                "efficiency": getattr(self.host_stats, "efficiency_index", 1.0), }

    def emergency_dump(self, exit_cause="UNKNOWN"):
        return self.chronos.emergency_dump(exit_cause)

    def _get_crash_path(self, prefix="crash"):
        return self.chronos.get_crash_path(prefix)

    def _ethical_audit(self):
        cfg = getattr(self.bone_config, "MAIN", None)
        audit_freq = getattr(cfg, "ETHICAL_AUDIT_FREQ", 3) if cfg else 3
        bypass_ratio = getattr(cfg, "ETHICAL_HEALTH_BYPASS", 0.3) if cfg else 0.3
        max_h = getattr(self.bone_config, "MAX_HEALTH", 100.0)
        if self.tick_count % audit_freq != 0 and self.health > (max_h * bypass_ratio):
            return False
        desp_thresh = getattr(cfg, "DESPERATION_THRESHOLD", 0.7) if cfg else 0.7
        cath_heal = getattr(cfg, "CATHARSIS_HEAL_AMOUNT", 30.0) if cfg else 30.0
        cath_decay = getattr(cfg, "CATHARSIS_DECAY", 0.1) if cfg else 0.1
        trauma_sum = sum(self.trauma_accum.values())
        health_ratio = self.health / max_h
        desperation = trauma_sum * (1.0 - health_ratio)
        if desperation > desp_thresh:
            msg = ux("main_strings", "mercy_venting")
            self.events.log(f"{Prisma.WHT}{msg}{Prisma.RST}", "SYS", )
            for k in self.trauma_accum:
                self.trauma_accum[k] *= cath_decay
                if self.trauma_accum[k] < 0.01:
                    self.trauma_accum[k] = 0.0
            msg_cath = ux("main_strings", "catharsis")
            self.events.log(f"{Prisma.CYN}{msg_cath}{Prisma.RST}", "SENSATION", )
            self.health = min(self.health + cath_heal, max_h)
            return True
        return False

    def engage_cold_boot(self) -> Optional[Dict[str, Any]]:
        if self.tick_count > 0:
            return None
        if os.path.exists("saves/quicksave.json"):
            msg_pod = ux("main_strings", "stasis_pod")
            print(f"{Prisma.GRY}{msg_pod}{Prisma.RST}")
            success, history = self.resume_checkpoint()
            if success:
                self._apply_boot_mode()
                if self.cortex:
                    self.cortex.restore_context(history)
                loc = (
                    self.embryo.continuity.get("location", "Unknown")
                    if self.embryo.continuity
                    else "Unknown")
                last_scene = "Silence."
                if self.cortex and self.cortex.dialogue_buffer:
                    last_scene = self.cortex.dialogue_buffer[-1]
                elif self.embryo.continuity:
                    last_scene = self.embryo.continuity.get("last_output", "Silence.")
                msg_resume = ux("main_strings", "resuming_timeline")
                msg_restored = ux("main_strings", "timeline_restored")
                resume_text = msg_resume.format(loc=loc, last_scene=last_scene)
                return {"ui": resume_text, "logs": [msg_restored]}
        msg_synth = ux("main_strings", "synth_reality")
        print(f"{Prisma.GRY}{msg_synth}{Prisma.RST}")
        scenarios = LoreManifest.get_instance().get("SCENARIOS", {})
        archetypes = scenarios.get("ARCHETYPES", ["A quiet room", "The edge of a forest", "A terminal screen"])
        seed = random.choice(archetypes)
        msg_seed = ux("main_strings", "seed_loaded")
        print(f"{Prisma.CYN}{msg_seed.format(seed=seed)}{Prisma.RST}")
        boot_prompt = f"SYSTEM_BOOT DETECTED. The system is waking up. The user provided the thought seed: '{seed}'. Greet the user casually using this seed. DO NOT describe physical environments."
        cold_result = self.process_turn(boot_prompt, is_system=True)
        return cold_result

    def save_checkpoint(self, history: list = None) -> str:
        return self.chronos.save_checkpoint(history)

    def resume_checkpoint(self) -> Tuple[bool, list]:
        return self.chronos.resume_checkpoint()

    def shutdown(self):
        if hasattr(self, "telemetry") and self.telemetry:
            self.telemetry.flush_to_disk()
        self.chronos.perform_shutdown()

if __name__ == "__main__":
    sys_config = ConfigWizard.load_or_create()
    engine = BoneAmanita(config=sys_config)
    with SessionGuardian(engine) as session:
        boot_packet = session.engage_cold_boot()
        if boot_packet and boot_packet.get("ui"):
            typewriter(boot_packet["ui"])
        prompt_ind = ux("main_strings", "prompt_indicator")
        term_div = ux("main_strings", "terminal_divider")
        split_token = ux("main_strings", "ui_split_token")
        while True:
            try:
                user_in = input(f"\n{Prisma.paint(f'{session.user_name} {prompt_ind}', 'W')} ")
            except EOFError:
                break
            clean_in = user_in.strip().lower()
            if clean_in in ["exit", "quit", "/exit", "/quit"]:
                break
            res = session.process_turn(user_in)
            print(f"\n{Prisma.GRY}{term_div}{Prisma.RST}")
            if res.get("ui"):
                cfg = getattr(BoneConfig, "GUI", None)
                slow_speed = getattr(cfg, "RENDER_SPEED_SLOW", 0.005) if cfg else 0.005
                if split_token and split_token in res["ui"]:
                    dashboard, _, content = res["ui"].partition("\n\n")
                    print(f"\n{dashboard.strip()}\n")
                    typewriter(content.strip() + "\n", speed=slow_speed)
                else:
                    typewriter(res["ui"] + "\n", speed=slow_speed)
            if res.get("type") == "DEATH":
                term_msg = ux("main_strings", "session_term")
                print(f"\n{Prisma.GRY}{term_msg}{Prisma.RST}")
                break