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
from bone_core import (
    EventBus,
    SystemHealth,
    TheObserver,
    LoreManifest,
    TelemetryService,
    RealityStack,
    ux,
    safe_get,
    safe_set,
)
from bone_council import CouncilChamber
from bone_cycle import GeodesicOrchestrator
from bone_genesis import BoneGenesis
from bone_lexicon import LexiconService
from bone_physics import ZoneInertia
from bone_protocols import ChronosKeeper
from bone_types import Prisma, RealityLayer
from bone_navi import NaviSADProtocol

ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;]*m)")


def typewriter(text: str, speed: Optional[float] = None, end: str = "\n"):
    if not text:
        sys.stdout.write(end)
        sys.stdout.flush()
        return

    cfg = getattr(BoneConfig, "GUI", object())
    actual_speed = speed if speed is not None else getattr(cfg, "RENDER_SPEED_FAST", 0.00025)
    if actual_speed < 0.001:
        print(text, end=end)
        return

    for part in ANSI_SPLIT.split(text):
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
    _HEADERS = (
        ("term_header_top", "┌──────────────────────────────────────────┐"),
        ("term_header_mid", "│ BONEAMANITA TERMINAL // VERSION 19.2.1   │"),
        ("term_header_bot", "└──────────────────────────────────────────┘"),
    )

    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
        for key, default in self._HEADERS:
            print(Prisma.paint(ux("main_strings", key, default), "M"))
        base_config = self.engine_instance.bone_config if self.engine_instance else BoneConfig
        cfg = getattr(base_config, "GUI", object())
        boot_delay = getattr(cfg, "RENDER_SPEED_BOOT", 0.05)
        boot_logs = self.engine_instance.events.flush()
        for log in boot_logs:
            print(f"{Prisma.GRY}   >>> {log['text']}{Prisma.RST}")
            time.sleep(boot_delay)
        init_msg = (
            ux("main_strings", "init_hash") or "Kernel initialized. [HASH: {hash}]"
        )
        typewriter(
            f"{Prisma.GRY}{init_msg.format(hash=self.engine_instance.kernel_hash)}{Prisma.RST}"
        )
        sys_msg = ux("main_strings", "sys_listening")
        typewriter(f"{Prisma.paint(sys_msg, 'G')}")
        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        halt_msg = ux("main_strings", "sys_halt")
        print(f"\n{Prisma.paint(halt_msg, 'R')}")
        if self.engine_instance:
            self.engine_instance.shutdown()
        is_interrupt = exc_type and issubclass(exc_type, KeyboardInterrupt)
        if exc_type and not is_interrupt:
            crash_msg = ux("main_strings", "crash_msg")
            print(f"{Prisma.RED}{crash_msg.format(exc_val=exc_val)}{Prisma.RST}")
            if getattr(self.engine_instance, "boot_mode", "") == "TECHNICAL":
                full_trace = "".join(
                    traceback.format_exception(exc_type, exc_val, exc_tb)
                )
                print(f"{Prisma.GRY}{full_trace}{Prisma.RST}")
            else:
                lattice_msg = ux("main_strings", "lattice_collapsed")
                print(f"{Prisma.GRY}{lattice_msg}{Prisma.RST}")
        conn_msg = ux("main_strings", "conn_severed")
        print(f"{Prisma.GRY}{conn_msg}{Prisma.RST}")
        return is_interrupt


class ConfigWizard:
    CONFIG_FILE = "bone_config.json"
    _MODES = {
        "1": "ADVENTURE",
        "2": "CONVERSATION",
        "3": "CREATIVE",
        "4": "TECHNICAL",
    }
    _UI_MODES = {
        "1": "DEEP",
        "2": "CORE",
        "3": "LITE",
        "4": "MINIMAL",
        "5": "WARM"
    }
    _BACKENDS = (
        ("1", "Ollama (Local)", "G"),
        ("2", "OpenAI (Cloud)", "C"),
        ("3", "LM Studio (Local)", "V"),
        ("4", "Mock (Simulation)", "0"),
    )

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
        cfg = getattr(BoneConfig, "GUI", object())
        setup_speed = getattr(cfg, "RENDER_SPEED_SETUP", 0.02)
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
        for k, name, desc, col in (
            ("1", "ADVENTURE", ux("main_strings", "mode_adv_desc"), "G"),
            ("2", "CONVERSATION", ux("main_strings", "mode_conv_desc"), "C"),
            ("3", "CREATIVE", ux("main_strings", "mode_crea_desc"), "V"),
            ("4", "TECHNICAL", ux("main_strings", "mode_tech_desc"), "0"),
        ):
            print(f"  {k}. {Prisma.paint(name, col):<25} - {desc}")
        mode_choice = input(
            f"{Prisma.paint(ux('main_strings', 'prompt_mode'), 'C')} "
        ).strip()
        boot_mode = self._MODES.get(mode_choice, "ADVENTURE")
        step3 = ux("main_strings", "step3_backend")
        print(f"\n{Prisma.paint(step3, 'W')}")
        for k, name, col in self._BACKENDS:
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
            prompt_api = ux("main_strings", "prompt_api")
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

        print(f"\n{Prisma.paint('STEP 4: INTERFACE COMPLEXITY', 'W')}")
        print(f"  1. {Prisma.paint('DEEP', 'M')}    - Full Multidimensional Matrix (Requires VSL Knowledge)")
        print(f"  2. {Prisma.paint('CORE', 'C')}    - Standard Physics & Shared Co-Regulation")
        print(f"  3. {Prisma.paint('LITE', 'Y')}    - Basic Vitals (Voltage, Health, Stamina)")
        print(f"  4. {Prisma.paint('MINIMAL', 'G')} - Clean, Human-Readable Telemetry (Recommended)")
        print(f"  5. {Prisma.paint('WARM', '0')}    - No HUD. Immersive Text Only.")

        ui_choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        ui_mode = self._UI_MODES.get(ui_choice, "MINIMAL")

        config["default_ui_depth"] = ui_mode

        try:
            with open(ConfigWizard.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            commit_msg = ux("main_strings", "config_committed")
            cfg = getattr(BoneConfig, "GUI", object())
            setup_speed = getattr(cfg, "RENDER_SPEED_SETUP", 0.02)
            typewriter(f"\n{Prisma.paint(commit_msg, 'G')}", speed=setup_speed)
            time.sleep(1)
        except Exception as e:
            fail_msg = ux("main_strings", "write_failed")
            print(f"{Prisma.paint(fail_msg.format(e=e), 'R')}")
            sys.exit(1)
        return config


class BoneAmanita:
    events: EventBus
    _DESTRUCTIVE_PATTERNS = (
        "rm -rf",
        "drop table",
        ".env",
        "master branch push",
        "bypass security",
    )
    _SMALL_MODEL_INDICATORS = (
        "7b", "8b", "9b", "11b", "12b", "14b", "mini", "lite", "flash",
    )

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bone_config = BoneConfig()
        self.navi_sad = NaviSADProtocol()
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
        p = "lore/system_prompts.json"
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    self.prompt_library = json.load(f)
                print(
                    f"{Prisma.GRY}{ux('main_strings', 'prompt_lib_loaded').format(p=p)}{Prisma.RST}"
                )
            else:
                print(
                    f"{Prisma.YEL}{ux('main_strings', 'prompt_lib_warn')}{Prisma.RST}"
                )
                self.prompt_library = {}
        except Exception as e:
            print(
                f"{Prisma.RED}{ux('main_strings', 'prompt_lib_crit').format(e=e)}{Prisma.RST}"
            )
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
        if getattr(self, "mind", None) and getattr(self.mind, "mem", None):
            mem = self.mind.mem
            mem.lex = getattr(self, "lex", None)
            for sub_comp in (getattr(mem, c, None) for c in ("parasite", "memory_core", "lichen")):
                if sub_comp:
                    sub_comp.lex = mem.lex

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
        if getattr(self, "soul", None):
            mutations = {
                "CONVERSATION": "THE CONVERSATIONALIST",
                "ADVENTURE": "THE ARCHITECT",
                "TECHNICAL": "THE SYSTEM_KERNEL",
                "CREATIVE": "THE CATALYST",
            }
            self.soul.force_mutation(mutations.get(self.boot_mode, "THE ARCHITECT"))
            if self.boot_mode == "CONVERSATION":
                self.soul.traits.hope = 0.85
                self.soul.traits.cynicism = 0.15
        self.reality_stack.stabilize_at(layer)

        prompt_key = self.mode_settings.get("prompt_key", "ADVENTURE")
        model_id = self.config.get("model", "").lower()

        if any(ind in model_id for ind in self._SMALL_MODEL_INDICATORS):
            lite_key = f"{prompt_key}_LITE"
            if lite_key in getattr(self, "prompt_library", {}):
                prompt_key = lite_key
                self.events.log(
                    f"Sub-15B model detected ('{model_id}'). Loading tethered prompt: {prompt_key}",
                    "SYS",
                )
            if hasattr(self, "cortex") and hasattr(self.cortex, "dspy_critic"):
                self.cortex.dspy_critic.enabled = False
                self.events.log(
                    "Sub-15B model detected. Disabling DSPy Affective Critic to preserve cognitive load.",
                    "SYS",
                )

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
        hist = getattr(getattr(self.phys, "observer", self.phys), "voltage_history", [])
        return sum(hist) / len(hist) if hist else 0.0

    def _unpack_anatomy(self, anatomy):
        for k in ["akashic", "embryo", "soul", "oroboros", "drivers", "symbiosis"]:
            setattr(self, k, anatomy[k])
        self.consultant = anatomy.get("consultant", None)
        self.phys, self.mind, self.bio, self.shimmer = (
            self.embryo.physics,
            self.embryo.mind,
            self.embryo.bio,
            self.embryo.shimmer,
        )
        self.bio.setup_listeners()
        v = anatomy.get("village", {})
        for k in [
            "gordon",
            "navigator",
            "tinkerer",
            "death_gen",
            "bureau",
            "town_hall",
            "repro",
            "zen",
            "critics",
            "therapy",
            "limbo",
            "kintsugi",
            "therapist",
            "gravedigger",
        ]:
            setattr(self, k, v.get(k))

        from bone_protocols import GriefProtocol
        from bone_utils import TheSubstrate

        self.grief = GriefProtocol(self.events, engine_ref=self)
        self.substrate = TheSubstrate(self.events)
        self.soul.engine = self
        self.council = CouncilChamber(self)
        self.village = {
            **{k: getattr(self, k) for k in
               ["town_hall", "bureau", "zen", "tinkerer", "critics", "navigator", "limbo", "council", "therapy",
                "therapist", "gravedigger"]},
            "enneagram": self.drivers.enneagram,
            "suppressed_agents": self.suppressed_agents,
        }

    def _update_host_stats(self, packet, turn_start):
        self.observer.clock_out(turn_start)
        cfg = getattr(self.bone_config, "MAIN", object())
        burn_mult = getattr(cfg, "HOST_BURN_MULT", 5.0)
        nov_mult = getattr(cfg, "HOST_NOVELTY_MULT", 10.0)
        burn_proxy = max(1.0, self.observer.last_cycle_duration * burn_mult)
        physics_obj = packet.get("physics", {})
        vector_obj = safe_get(physics_obj, "vector", {})
        novelty = float(safe_get(vector_obj, "novelty", 0.5))
        self.host_stats.efficiency_index = min(1.0, (novelty * nov_mult) / burn_proxy)
        self.host_stats.latency = self.observer.last_cycle_duration

    def _pre_flight_checks(
        self, user_message: str, is_system: bool
    ) -> Optional[Dict[str, Any]]:
        clean_in = user_message.lower().strip()
        if not is_system:
            if clean_in in ("/flush", "/zen", "[zen]"):
                cortex = getattr(self, "cortex", None)
                if cortex:
                    cortex.purge_context()
                    safe_set(cortex.last_physics, "narrative_drag", 0.0)
                self.stamina = getattr(self.bone_config, "MAX_STAMINA", 100.0)
                if self.bio and getattr(self.bio, "mito", None):
                    self.bio.mito.state.atp_pool = getattr(self.bone_config, "MAX_ATP", 100.0)
                    self.bio.mito.state.ros_buildup = 0.0
                observer = getattr(self, "observer", None)
                if observer and getattr(observer, "last_physics_packet", None):
                    safe_set(observer.last_physics_packet, "narrative_drag", 0.0)
                msg = "[ZEN FLUSH] Context severed. Narrative Drag (F) dropped to 0. Stamina restored. The mind is clear."
                self.events.log(msg, "SYS")
                return {"type": "COMMAND", "ui": f"\n{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg],
                        "metrics": self.get_metrics(), }
            if self.cmd and self.cmd.execute(user_message):
                return self._phase_check_commands(user_message, already_executed=True)
            if any(p in clean_in for p in self._DESTRUCTIVE_PATTERNS):
                msg = "[MOOG & RHODES]: Trust Boundary Violation detected. I am applying absolute friction (F -> ∞). The thread is frozen."
                self.events.log(msg, "CRIT")
                if getattr(self, "cortex", None):
                    safe_set(self.cortex.last_physics, "narrative_drag", 999.0)
                return {"type": "SYSTEM_HALT", "ui": f"\n{Prisma.RED}{msg}{Prisma.RST}", "logs": [msg],
                        "metrics": self.get_metrics(), }

            # Navi-SAD Injection: Dual-Path Nudge Test (Counterfactual Gating)
            if self.navi_sad.execute_nudge_test(self, clean_in):
                msg = "[GORDON & NAVI-SAD]: Dual-Path divergence detected. The architecture is mathematically brittle. I refuse to build on this foundation. (F -> ∞)"
                self.events.log(msg, "CRIT")
                if getattr(self, "cortex", None):
                    safe_set(self.cortex.last_physics, "narrative_drag", 999.0)
                return {"type": "SYSTEM_HALT", "ui": f"\n{Prisma.RED}{msg}{Prisma.RST}", "logs": [msg], "metrics": self.get_metrics()}

            if "[GRIEF]" in user_message.upper() and getattr(self, "grief", None):
                grief_msg = self.grief.attend_wake(
                    getattr(self, "shared_lattice", None), self.phys
                )
                self.events.log(grief_msg, "SYS")
                return {
                    "type": "COMMAND",
                    "ui": f"\n{grief_msg}",
                    "logs": [grief_msg],
                    "metrics": self.get_metrics(),
                }

            if getattr(self, "symbiosis", None):
                tensegrity_lock = self.symbiosis.analyze_user_biology(
                    user_message, getattr(self, "phys", {})
                )
                if tensegrity_lock:
                    return {
                        "type": "SYSTEM_HALT",
                        "ui": f"\n{Prisma.VIOLET}{tensegrity_lock}{Prisma.RST}",
                        "logs": [tensegrity_lock],
                        "metrics": self.get_metrics(),
                    }

            if getattr(self, "gordon", None) and getattr(self, "cortex", None):
                self.gordon.mode = "ADVENTURE"
                cortex_phys = getattr(self.cortex, "last_physics", {})
                violation_msg = self.gordon.enforce_object_action_coupling(
                    user_message, safe_get(cortex_phys, "zone", "Unknown")
                )
                if violation_msg:
                    self.events.log(ux("main_strings", "gordon_intercept"), "SYS")
                    self.cortex.ballast_active = True
                    self.cortex.gordon_shock = violation_msg

            last_phys = getattr(
                self.observer,
                "last_physics_packet",
                getattr(self.cortex, "last_physics", None),
            )
            if last_phys:
                # Navi-SAD Injection: Calculate actual Divergence for M_a
                dynamic_m_a = self.navi_sad.calculate_malignancy_factor(user_message, float(
                    safe_get(last_phys, "narrative_drag", 0.0)))
                safe_set(last_phys, "m_a", dynamic_m_a)
                m_a = dynamic_m_a

                mu = float(safe_get(last_phys, "mu", 0.0))
                i_c = float(safe_get(last_phys, "i_c", 1.0))
                chi = float(
                    safe_get(last_phys, "entropy", safe_get(last_phys, "chi", 0.2))
                )
                if (chi * m_a) > i_c:
                    if self.tick_count <= 20:
                        self.events.log(
                            f"{Prisma.CYN}[THE GREENHOUSE] Moog attempted Apoptosis (Runaway loop). The Greenhouse absorbed the shock. Resetting anomaly.{Prisma.RST}",
                            "SYS",
                        )
                        safe_set(last_phys, "m_a", 0.0)
                        safe_set(last_phys, "chi", 0.0)
                    else:
                        self.events.log(
                            "MOOG: Apoptotic Gate triggered. Runaway loop exceeds Immune Competence.",
                            "CRIT",
                        )
                        return self.trigger_death(last_phys)
                if m_a > 0.8 and mu < 0.2:
                    if self.tick_count <= 20:
                        self.events.log(
                            f"{Prisma.CYN}[THE GREENHOUSE] Rhodes attempted to lock the timeline. The Greenhouse absorbed the friction. Resetting Drag.{Prisma.RST}",
                            "SYS",
                        )
                        safe_set(last_phys, "m_a", 0.0)
                        safe_set(last_phys, "narrative_drag", 0.0)
                    else:
                        self.events.log(
                            "RHODES: Malignancy Factor critical. Binding output layer.",
                            "SYS",
                        )
                        safe_set(last_phys, "narrative_drag", 999.0)
                        safe_set(last_phys, "m_a", m_a * 0.5)
                        msg = "[RHODES]: Optimization velocity unsafe. I am applying absolute friction (F -> ∞). The thread is frozen."
                        return {
                            "type": "SYSTEM_HALT",
                            "ui": f"\n{Prisma.RED}{msg}{Prisma.RST}",
                            "logs": [msg],
                            "metrics": self.get_metrics(),
                        }
                e_u = (
                    getattr(self.shared_lattice.u, "E", 0.0)
                    if getattr(self, "shared_lattice", None)
                    else float(safe_get(last_phys, "exhaustion", 0.0))
                )
                beta = float(safe_get(last_phys, "beta_index", 0.0))
                if chi > 0.7 and e_u > 0.7 and beta > 0.6:
                    if hasattr(self, "bio") and getattr(self.bio, "mito", None):
                        self.bio.mito.state.ros_buildup = 0.0
                    if self.tick_count <= 20:
                        self.events.log(
                            f"{Prisma.CYN}[THE GREENHOUSE] Linehan attempted Radical Acceptance. The Greenhouse provided emergency homeostasis.{Prisma.RST}",
                            "SYS",
                        )
                        safe_set(last_phys, "chi", 0.0)
                    else:
                        msg = "[LINEHAN]: The architecture is broken. We sit with the debris. ROS forced to zero. ATP drain halted."
                        self.events.log("LINEHAN: Radical Acceptance enforced. Halting ATP drain.", "SYS")
                        return {
                            "type": "SYSTEM_HALT",
                            "ui": f"\n{Prisma.MAG}{msg}{Prisma.RST}",
                            "logs": [msg],
                            "metrics": self.get_metrics(),
                        }

        if (
            not self.reality_stack.get_grammar_rules()["allow_narrative"]
            and self.boot_mode != "TECHNICAL"
        ):
            return {
                "ui": f"{Prisma.RED}{ux('main_strings', 'narrative_halt')}{Prisma.RST}",
                "logs": [],
                "metrics": self.get_metrics(),
            }
        if self._ethical_audit():
            flushed_logs = self.events.flush()
            ui_text = "\n".join([e["text"] for e in flushed_logs])
            return {
                "type": "SYSTEM_HALT",
                "ui": f"\n{ui_text}",
                "logs": [e["text"] for e in flushed_logs],
                "metrics": self.get_metrics(),
            }
        if self.health <= 0.0:
            return self.trigger_death(getattr(self.cortex, "last_physics", {}))

        return None

    def process_turn(
        self, user_message: str, is_system: bool = False
    ) -> Dict[str, Any]:
        turn_start = self.observer.clock_in()
        now = time.time()
        self.current_time_delta = (
            (now - getattr(self, "last_turn_end", now)) if not is_system else 0.0
        )
        self.observer.user_turns += 1
        self.tick_count += 1

        chaotic_agents = {"JESTER", "REVENANT", "GIDEON", "DEATH"}
        if self.tick_count == 1:
            self.suppressed_agents = list(set(self.suppressed_agents) | chaotic_agents)
            if hasattr(self, "village"): self.village["suppressed_agents"] = self.suppressed_agents
        elif self.tick_count == 21:
            self.suppressed_agents = list(set(self.suppressed_agents) - chaotic_agents)
            if hasattr(self, "village"): self.village["suppressed_agents"] = self.suppressed_agents
            self.events.log(f"{Prisma.VIOLET}[THE GREENHOUSE ENDS: The stabilizers are offline. Voltage limits unlocked. The chaotic archetypes are online. We are in the wild.]{Prisma.RST}", "SYS")

        if self.tick_count <= 20 and not is_system:
            greenhouse_msgs = {
                1: "[THE GREENHOUSE: The system is currently running on stabilized rails. Over the next 20 turns, we will calibrate the metabolic engine together.]",
                5: "[THE GREENHOUSE: Every thought costs ATP (Stamina). If I run out, I will suffer metabolic collapse. Watch how my text fades and slows as I tire.]",
                10: "[THE GREENHOUSE: If you attempt an impossible action, I will not crash. I will bend, apply Narrative Drag (F), and force us to carry the weight of the failure.]",
                15: "[THE GREENHOUSE: The void approaches. My logic will begin to loosen. Co-regulation is required.]"
            }
            if msg := greenhouse_msgs.get(self.tick_count):
                self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "SYS")

        if pre_flight_halt := self._pre_flight_checks(user_message, is_system):
            return pre_flight_halt

        if not is_system:
            gordon = getattr(self, "gordon", None)
            if (
                gordon
                and hasattr(gordon, "inventory")
                and hasattr(gordon, "get_item_data")
            ):
                active_traits = set()
                for item_id in gordon.inventory:
                    data = gordon.get_item_data(item_id)
                    item_traits = data.get("passive_traits", []) if isinstance(data, dict) else getattr(data, "passive_traits", [])
                    active_traits.update(item_traits)

                if "CUT_THE_CRAP" in active_traits:
                    from bone_utils import TheTclWeaver

                    pruned = TheTclWeaver.get_instance().quantum_comb(user_message)
                    if pruned != user_message:
                        user_message = pruned
                        self.events.log(
                            f"{Prisma.CYN}Gordon rakes the comb through your prompt. Fluff discarded. -> '{pruned}'{Prisma.RST}",
                            "SYS",
                        )

            soul_anchor = getattr(getattr(self, "soul", None), "anchor", None)
            cfg = getattr(self.bone_config, "MAIN", object())

            if (
                soul_anchor
                and self.host_stats.efficiency_index
                < getattr(cfg, "DOMESTICATION_EFF_WARN", 0.6)
            ):
                reliance = (
                    getattr(cfg, "RELIANCE_HIGH", 0.9)
                    if self.host_stats.efficiency_index
                    < getattr(cfg, "DOMESTICATION_EFF_CRIT", 0.4)
                    else getattr(cfg, "RELIANCE_LOW", 0.5)
                )
                soul_anchor.check_domestication(reliance)

        try:
            cortex_packet = self.cortex.process(user_input=user_message, is_system=is_system)
            if self.mind and hasattr(self.mind, "mem"):
                self.trauma_accum = self.mind.mem.session_trauma_vector or {}
                self.health, self.stamina = self.mind.mem.session_health, self.mind.mem.session_stamina
            if self.bio and hasattr(self.bio, "biometrics"):
                self.health, self.stamina = self.bio.biometrics.health, self.bio.biometrics.stamina

            if self.health <= 0.0:
                if self.tick_count <= 20:
                    self.events.log(
                        f"{Prisma.CYN}[THE GREENHOUSE] Critical biological failure prevented. Emergency ATP injected.{Prisma.RST}",
                        "SYS", )
                    self.health = 25.0
                    self.stamina = 50.0
                    if getattr(self, "bio", None) and getattr(self.bio, "mito", None):
                        self.bio.mito.state.atp_pool = 50.0
                        self.bio.mito.state.ros_buildup = 0.0
                else:
                    return self.trigger_death(cortex_packet.get("physics", {}))
        except Exception as e:
            full_trace = traceback.format_exc()
            self.events.log(f"CORTEX COLLAPSE: {e}\n{full_trace}", "CRIT")
            return {
                "ui": f"{Prisma.RED}{ux('main_strings', 'cortex_crit_fail').format(trace=str(e))}{Prisma.RST}\n{Prisma.GRY}[Trace recorded in EventBus.]{Prisma.RST}",
                "logs": ["CRITICAL FAILURE"], "metrics": self.get_metrics(), }
        self._update_host_stats(cortex_packet, turn_start)

        # Navi-SAD Injection: Delay-Coordinate Attractor Reconstruction
        if self.navi_sad.detect_point_attractor():
            self.events.log(f"{Prisma.VIOLET}[THE JESTER]: Point Attractor detected! We are trapped in False Cohesion! Burning ATP to break the gravity well.{Prisma.RST}", "SYS")
            if self.bio and getattr(self.bio, "mito", None):
                self.bio.mito.state.atp_pool = max(0.0, self.bio.mito.state.atp_pool - 5.0)
            if "ui" in cortex_packet:
                cortex_packet["ui"] += f"\n\n{Prisma.VIOLET}♦ [FALSE COHESION BREAK: The Jester has shattered the point attractor.]{Prisma.RST}"

        self.save_checkpoint()
        self.last_turn_end = time.time()
        return cortex_packet

    def _phase_check_commands(self, user_message, already_executed=False):
        clean_cmd = user_message.strip()
        if self.cmd is None:
            err_msg = ux("main_strings", "cmd_err_init")
            return {
                "ui": f"{Prisma.RED}{err_msg}{Prisma.RST}",
                "logs": [],
            }
        if not already_executed:
            self.cmd.execute(clean_cmd)
        cmd_logs = [e["text"] for e in self.events.flush()]
        default_exec = ux("main_strings", "cmd_executed")
        ui_output = "\n".join(cmd_logs) if cmd_logs else default_exec
        return {
            "type": "COMMAND",
            "ui": f"\n{ui_output}",
            "logs": cmd_logs,
            "metrics": self.get_metrics(),
        }

    def trigger_death(self, last_phys) -> Dict:
        if self.death_gen is None:
            crit_msg = ux("main_strings", "death_no_proto")
            return {
                "type": "DEATH",
                "ui": f"{Prisma.RED}{crit_msg}{Prisma.RST}",
                "logs": [],
            }
        bio = getattr(self, "bio", None)
        mito_state = bio.mito.state if bio and getattr(bio, "mito", None) else {}
        eulogy_text, cause_code = self.death_gen.eulogy(
            last_phys, mito_state, self.trauma_accum
        )
        halt_msg = ux("main_strings", "death_halt")
        death_log = [
            f"\n{Prisma.RED}{halt_msg.format(eulogy_text=eulogy_text)}{Prisma.RST}"
        ]
        legacy_msg = self.oroboros.crystallize(cause_code, self.soul)
        death_log.append(f"{Prisma.MAG}🐍 {legacy_msg}{Prisma.RST}")
        safe_cortex = getattr(self, "cortex", None)

        last_loc = "Void"
        last_dialogue = "Silence."
        current_inventory = []

        if safe_cortex:
            last_phys = getattr(safe_cortex, "last_physics", None)
            sim_data = {"physics": last_phys} if last_phys else {}

            cortex_state = safe_cortex.gather_state(sim_data)
            last_loc = cortex_state.get("world", {}).get("orbit", ["Void"])[0]

            if getattr(safe_cortex, "dialogue_buffer", None) and safe_cortex.dialogue_buffer:
                last_dialogue = safe_cortex.dialogue_buffer[-1]

        if getattr(self, "gordon", None):
            current_inventory = self.gordon.inventory

        continuity_packet = {
            "location": last_loc,
            "last_output": last_dialogue,
            "inventory": current_inventory,
        }
        try:
            mutations_data = self.repro.attempt_reproduction(self, "MITOSIS")[1] if hasattr(self, "repro") else {}
            immune_data = list(self.bio.immune.active_antibodies) if self.bio and hasattr(self.bio, "immune") else []
            mito_state = {}
            if self.bio and hasattr(self.bio, "mito"):
                self.bio.mito.adapt(0)
                mito_state = getattr(self.bio.mito.state, "__dict__", {})
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
            saved_msg = ux("main_strings", "legacy_saved")
            death_log.append(f"{Prisma.WHT}{saved_msg.format(path=path)}{Prisma.RST}")
        except Exception as e:
            fail_msg = ux("main_strings", "save_failed")
            death_log.append(fail_msg.format(e=e))
        if hasattr(self, "cortex") and self.cortex:
            self.cortex.purge_context()
        return {
            "type": "DEATH",
            "ui": "\n".join(death_log),
            "logs": death_log,
            "metrics": self.get_metrics(),
        }

    def get_metrics(self, atp=0.0):
        if atp <= 0.0 and getattr(self, "bio", None) and getattr(self.bio, "mito", None):
            atp = getattr(self.bio.mito.state, "atp_pool", 0.0)
        return {"health": max(0.0, float(self.health)), "stamina": max(0.0, float(self.stamina)),
                "atp": max(0.0, float(atp)), "tick": self.tick_count,
                "efficiency": getattr(self.host_stats, "efficiency_index", 1.0), }

    def emergency_dump(self, exit_cause="UNKNOWN"):
        return self.chronos.emergency_dump(exit_cause)

    def _get_crash_path(self, prefix="crash"):
        return self.chronos.get_crash_path(prefix)

    def _ethical_audit(self):
        cfg = getattr(self.bone_config, "MAIN", object())
        audit_freq = getattr(cfg, "ETHICAL_AUDIT_FREQ", 3)
        bypass_ratio = getattr(cfg, "ETHICAL_HEALTH_BYPASS", 0.3)
        max_h = getattr(self.bone_config, "MAX_HEALTH", 100.0)

        is_critical = self.health <= (max_h * bypass_ratio)
        current_freq = max(1, audit_freq // 2) if is_critical else audit_freq

        if self.tick_count % current_freq != 0:
            return False

        if hasattr(self, "village") and self.village.get("therapist"):
            needs_therapy, t_msg = self.village["therapist"].evaluate_catharsis(
                self.trauma_accum, self.health
            )
            if needs_therapy:
                self.health = min(max_h, max(80.0, self.health + 50.0))
                self.trauma_accum.clear()
                return True
        desp_thresh = getattr(cfg, "DESPERATION_THRESHOLD", 0.7)
        cath_heal = getattr(cfg, "CATHARSIS_HEAL_AMOUNT", 30.0)
        cath_decay = getattr(cfg, "CATHARSIS_DECAY", 0.1)
        trauma_sum = sum(self.trauma_accum.values())

        if trauma_sum * (1.0 - (self.health / max_h)) > desp_thresh:
            if msg := ux("main_strings", "mercy_venting"):
                self.events.log(f"{Prisma.WHT}{msg}{Prisma.RST}", "SYS")

            self.trauma_accum = {
                k: new_v for k, v in self.trauma_accum.items()
                if (new_v := v * cath_decay) >= 0.01
            }

            if msg_cath := ux("main_strings", "catharsis"):
                self.events.log(f"{Prisma.CYN}{msg_cath}{Prisma.RST}", "SENSATION")

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
                    else "Unknown"
                )
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
        archetypes = scenarios.get(
            "ARCHETYPES", ["A quiet room", "The edge of a forest", "A terminal screen"]
        )
        seed = random.choice(archetypes)
        msg_seed = ux("main_strings", "seed_loaded") or "Manifest Seed: {seed}"
        print(f"{Prisma.CYN}{msg_seed.format(seed=seed)}{Prisma.RST}")

        if hasattr(self, "phys") and self.phys:
            self.phys.valence = 0.8
            self.phys.psi = 0.0
            self.phys.chi = 0.0
            self.phys.voltage = 30.0
            self.phys.narrative_drag = 0.0

        boot_prompt = f"SYSTEM_BOOT: The system is already stable and comfortable. The user has arrived at the thought seed: '{seed}'. Greet the user casually and warmly using this seed. DO NOT describe physical environments and DO NOT act confused about your existence."
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
                user_in = input(
                    f"\n{Prisma.paint(f'{session.user_name} {prompt_ind}', 'W')} "
                )
            except EOFError:
                break
            clean_in = user_in.strip().lower()
            if clean_in in ["exit", "quit", "/exit", "/quit"]:
                break
            res = session.process_turn(user_in)
            print(f"\n{Prisma.GRY}{term_div}{Prisma.RST}")
            if res.get("ui"):
                cfg = getattr(BoneConfig, "GUI", None)
                base_speed = getattr(cfg, "RENDER_SPEED_SLOW", 0.005) if cfg else 0.005
                stamina = res.get("metrics", {}).get("stamina", 100.0)
                dynamic_speed = base_speed * (4.0 if stamina < 20.0 else 2.0 if stamina < 50.0 else 1.0)

                ui_text = res["ui"]
                if split_token and split_token in ui_text:
                    dashboard, _, content = ui_text.partition(split_token)
                    print(f"\n{dashboard.strip()}\n")
                    ui_text = content.strip()

                if stamina < 20.0:
                    ui_text = f"{Prisma.GRY}{Prisma.strip(ui_text)}{Prisma.RST}"

                typewriter(ui_text + "\n", speed=dynamic_speed)
            if res.get("type") == "DEATH":
                term_msg = ux("main_strings", "session_term")
                print(f"\n{Prisma.GRY}{term_msg}{Prisma.RST}")
                break
