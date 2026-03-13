"""bone_substrate.py"""
import os
from typing import List, Dict
from bone_types import Prisma

class TheSubstrate:
    """
    The Physical Hands of the machine.
    Allows the system to write files directly to the host OS.
    """
    def __init__(self, events_ref):
        self.events = events_ref
        self.pending_writes: List[Dict[str, str]] = []

    def queue_write(self, path: str, content: str):
        self.pending_writes.append({"path": path, "content": content})

    def execute_writes(self, stamina_pool: float) -> tuple[List[str], float]:
        logs = []
        cost = 0.0
        if not self.pending_writes:
            return logs, cost
        if not os.path.exists("output"):
            os.makedirs("output")
        for write in self.pending_writes:
            safe_name = os.path.basename(write["path"])
            safe_path = os.path.join("output", safe_name)
            content = write["content"]
            size = len(content)
            write_cost = size * 0.02
            if stamina_pool - cost < write_cost:
                logs.append(f"{Prisma.RED}SUBSTRATE FAULT: Insufficient stamina to forge {safe_name}.{Prisma.RST}")
                continue
            try:
                with open(safe_path, "w", encoding="utf-8") as f:
                    f.write(content)
                cost += write_cost
                logs.append(f"{Prisma.GRN}SUBSTRATE: Physically forged {safe_path} ({size} bytes).{Prisma.RST}")
                if "podcast_script" in safe_name:
                    self._trigger_tts(safe_path)
            except Exception as e:
                logs.append(f"{Prisma.RED}SUBSTRATE FAULT: Write failed - {e}{Prisma.RST}")
        self.pending_writes.clear()
        return logs, cost

    def _trigger_tts(self, safe_path: str):
        import threading
        try:
            from bone_audio import TheVocalCords
            cords = TheVocalCords(self.events)
            thread = threading.Thread(target=cords.synthesize_podcast, args=(safe_path,))
            thread.start()
            if self.events:
                self.events.log(f"{Prisma.VIOLET}🎙️ Routing script to Vocal Cords (TTS generation in background)...{Prisma.RST}", "SYS")
        except ImportError:
            pass