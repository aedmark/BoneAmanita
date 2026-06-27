"""mechanics/setup.py"""

import json
import os
import subprocess
import sys
import time

from core import Prisma
from mechanics.terminal import typewriter
from presets import BoneConfig
from struts import ux


class ConfigWizard:
    CONFIG_FILE = "config.json"
    _MODES = {"1": "ADVENTURE", "2": "CONVERSATION", "3": "CREATIVE", "4": "TECHNICAL"}
    _UI_MODES = {"1": "DEEP", "2": "CORE", "3": "LITE", "4": "MINIMAL", "5": "WARM"}
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
        except Exception as e:
            print(
                f"{Prisma.YEL}[WIZARD] Non-fatal issue archiving config: {e}{Prisma.RST}"
            )

    @staticmethod
    def _run_setup():

        cfg_obj = BoneConfig
        cfg = (
            cfg_obj.get("GUI", {})
            if isinstance(cfg_obj, dict)
            else getattr(cfg_obj, "GUI", {})
        )
        is_cfg_dict = isinstance(cfg, dict)
        setup_speed = float(
            cfg.get("RENDER_SPEED_SETUP", 0.02)
            if is_cfg_dict
            else getattr(cfg, "RENDER_SPEED_SETUP", 0.02)
        )
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
        boot_mode = ConfigWizard._MODES.get(mode_choice, "ADVENTURE")
        step3 = ux("main_strings", "step3_backend")
        print(f"\n{Prisma.paint(step3, 'W')}")
        for k, name, col in ConfigWizard._BACKENDS:
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
            config["model"] = input("Model ID [gpt-4]: ").strip() or "gpt-4"
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
            config["model"] = input("Model ID [llama3]: ").strip() or "llama3"

        print(f"\n{Prisma.paint('STEP 4: COMPUTE PROFILE (METABOLIC TUNING)', 'W')}")
        for k, name, col, desc in [
            ("1", "EDGE / APU", "Y", "Aggressive throttling. (Low VRAM / Laptops / Pi)"),
            ("2", "DISCRETE GPU", "G", "Balanced limits. (Local models <= 8B)"),
            ("3", "HEAVY COMPUTE", "M", "Unrestricted. (Cloud API / Massive VRAM / Models > 8B)"),
        ]:
            print(f"  {k}. {Prisma.paint(name, col):<15} - {desc}")
        compute_choice = input(f"{Prisma.paint('>', 'C')} ").strip()

        if compute_choice == "1":
            config["CORTEX"] = {"TOPOLOGY_FREQ": 10, "WLS_FREQ": 10, "COGNITIVE_RETRY_LIMIT": 1}
        elif compute_choice == "3":
            config["CORTEX"] = {"TOPOLOGY_FREQ": 3, "WLS_FREQ": 3, "COGNITIVE_RETRY_LIMIT": 3}
        else:
            config["CORTEX"] = {"TOPOLOGY_FREQ": 5, "WLS_FREQ": 5, "COGNITIVE_RETRY_LIMIT": 2}

        print(f"\n{Prisma.paint('STEP 5: INTERFACE COMPLEXITY', 'W')}")
        for k, name, col, desc in [
            ("1", "DEEP", "M", "Full Multidimensional Matrix (Requires VSL Knowledge)"),
            ("2", "CORE", "C", "Standard Physics & Shared Co-Regulation"),
            ("3", "LITE", "Y", "Basic Vitals (Voltage, Health, Stamina)"),
            ("4", "MINIMAL", "G", "Clean, Human-Readable Telemetry (Recommended)"),
            ("5", "WARM", "0", "No HUD. Immersive Text Only."),
        ]:
            print(f"  {k}. {Prisma.paint(name, col):<15} - {desc}")
        ui_choice = input(f"{Prisma.paint('>', 'C')} ").strip()
        ui_mode = ConfigWizard._UI_MODES.get(ui_choice, "MINIMAL")
        config["default_ui_depth"] = ui_mode
        try:
            with open(ConfigWizard.CONFIG_FILE, "w", encoding="utf-8") as f:
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
