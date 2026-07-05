"""mechanics/terminal.py"""

import os
import re
import subprocess
import sys
import time
import traceback
from typing import Optional

from core import Prisma
from presets import BoneConfig
from struts import ux

ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;]*m)")


def typewriter(text: str, speed: Optional[float] = None, end: str = "\n"):
    if not text:
        print(end=end, flush=True)
        return
    from struts import safe_get

    cfg = safe_get(BoneConfig, "GUI", {})
    actual_speed = (
        speed
        if speed is not None
        else float(safe_get(cfg, "RENDER_SPEED_FAST", 0.00025))
    )
    if actual_speed < 0.001:
        print(text, end=end, flush=True)
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
    print(end=end, flush=True)


class SessionGuardian:
    _HEADERS = (
        ("term_header_top", "┌──────────────────────────────────────────┐"),
        ("term_header_mid", "│ BONEAMANITA TERMINAL // VERSION 20.7.0   │"),
        ("term_header_bot", "└──────────────────────────────────────────┘"),
    )

    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
        for key, default in self._HEADERS:
            print(Prisma.paint(ux("main_strings", key, default), "M"))
        from struts import safe_get

        base_config = (
            self.engine_instance.config if self.engine_instance else BoneConfig
        )
        cfg = safe_get(base_config, "GUI", {})
        boot_delay = float(safe_get(cfg, "RENDER_SPEED_BOOT", 0.05))
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
            crash_msg = (
                ux("main_strings", "crash_msg") or "CRITICAL SYSTEM FAILURE: {exc_val}"
            )
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
