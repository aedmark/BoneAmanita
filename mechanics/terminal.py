"""mechanics/terminal.py"""

import os
import sys
import time
import traceback
import subprocess
import re
from typing import Optional
from core import Prisma
from struts import ux
from presets import BoneConfig

# Matches standard ANSI escape sequences (used for terminal colors).
# This is critical for the typewriter effect to prevent it from slowly typing out hidden formatting codes.
ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;]*m)")

def typewriter(text: str, speed: Optional[float] = None, end: str = "\n"):
    """
    Prints text to the console character-by-character to simulate mechanical output.
    Intelligently ignores ANSI color codes so formatting is applied instantly without disrupting the visual pacing.
    """
    if not text:
        print(end=end, flush=True)
        return

    cfg = getattr(BoneConfig, "GUI", object())
    actual_speed = speed if speed is not None else getattr(cfg, "RENDER_SPEED_FAST", 0.00025)

    # If the speed is effectively zero, bypass the typewriter loop entirely for efficiency.
    if actual_speed < 0.001:
        print(text, end=end, flush=True)
        return

    # Split the text into alternating chunks of plain text and ANSI color codes.
    for part in ANSI_SPLIT.split(text):
        if not part:
            continue

        if part.startswith("\x1b"):
            # This is an invisible formatting code. Apply it immediately to the terminal.
            sys.stdout.write(part)
        else:
            # This is visible text. Print it one character at a time with the specified delay.
            for char in part:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(actual_speed)

    print(end=end, flush=True)

class SessionGuardian:
    """
    A context manager that wraps the entire application runtime.
    Ensures the terminal is properly initialized on boot, and gracefully handles
    shutdowns, user interruptions (Ctrl+C), and fatal crashes without leaving the terminal in a broken state.
    """
    _HEADERS = (
        ("term_header_top", "┌──────────────────────────────────────────┐"),
        ("term_header_mid", "│ BONEAMANITA TERMINAL // VERSION 19.8.3   │"),
        ("term_header_bot", "└──────────────────────────────────────────┘"),
    )

    def __init__(self, engine_ref):
        self.engine_instance = engine_ref

    def __enter__(self):
        """
        The Boot Sequence. Clears the screen, prints the headers, and slowly
        flushes the engine's startup logs to establish the pacing of the session.
        """
        subprocess.run("cls" if os.name == "nt" else "clear", shell=True)

        for key, default in self._HEADERS:
            print(Prisma.paint(ux("main_strings", key, default), "M"))

        base_config = self.engine_instance.config if self.engine_instance else BoneConfig
        cfg = getattr(base_config, "GUI", object())
        boot_delay = getattr(cfg, "RENDER_SPEED_BOOT", 0.05)

        # Flush the logs that were generated during the silent boot phase
        boot_logs = self.engine_instance.events.flush()
        for log in boot_logs:
            print(f"{Prisma.GRY}   >>> {log['text']}{Prisma.RST}")
            time.sleep(boot_delay)

        init_msg = ux("main_strings", "init_hash") or "Kernel initialized. [HASH: {hash}]"
        typewriter(f"{Prisma.GRY}{init_msg.format(hash=self.engine_instance.kernel_hash)}{Prisma.RST}")

        sys_msg = ux("main_strings", "sys_listening")
        typewriter(f"{Prisma.paint(sys_msg, 'G')}")

        return self.engine_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        The Teardown Sequence. Executes regardless of whether the program ended naturally,
        was interrupted by the user, or suffered a fatal Python exception.
        """
        halt_msg = ux("main_strings", "sys_halt")
        print(f"\n{Prisma.paint(halt_msg, 'R')}")

        # Guarantee that the engine's internal shutdown hooks are fired to save state
        if self.engine_instance:
            self.engine_instance.shutdown()

        # Check if the exit was caused by the user hitting Ctrl+C
        is_interrupt = exc_type and issubclass(exc_type, KeyboardInterrupt)

        # Handle actual fatal crashes (not standard interruptions)
        if exc_type and not is_interrupt:
            # Prevent AttributeError from masking the original exception if UX localization fails
            crash_msg = ux("main_strings", "crash_msg") or "CRITICAL SYSTEM FAILURE: {exc_val}"
            print(f"{Prisma.RED}{crash_msg.format(exc_val=exc_val)}{Prisma.RST}")

            # Conditional Error Reporting based on User Intent
            if getattr(self.engine_instance, "boot_mode", "") == "TECHNICAL":
                # The user is a developer. Show them the ugly stack trace so they can debug.
                full_trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(f"{Prisma.GRY}{full_trace}{Prisma.RST}")
            else:
                # The user is a player/writer. Hide the stack trace to preserve narrative immersion.
                lattice_msg = ux("main_strings", "lattice_collapsed")
                print(f"{Prisma.GRY}{lattice_msg}{Prisma.RST}")

        conn_msg = ux("main_strings", "conn_severed")
        print(f"{Prisma.GRY}{conn_msg}{Prisma.RST}")

        # Returning True suppresses the KeyboardInterrupt exception from flooding the terminal
        return is_interrupt