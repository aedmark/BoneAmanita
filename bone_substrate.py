"""bone_substrate.py"""

import os
import threading
from typing import List, Dict, Tuple
from bone_types import Prisma

class TheSubstrate:
    def __init__(self, events_ref):
        self.events = events_ref
        self.pending_writes: List[Dict[str, str]] = []

    def queue_write(self, path: str, content: str):
        self.pending_writes.append({"path": path, "content": content})

    def execute_writes(self, stamina_pool: float) -> Tuple[List[str], float]:
        logs = []
        cost = 0.0
        if not self.pending_writes:
            return logs, cost
        os.makedirs("output", exist_ok=True)
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
        def _async_tts_task(path, events):
            try:
                from bone_audio import TheVocalCords
                cords = TheVocalCords(events)
                cords.synthesize_podcast(path)
                if events:
                    events.log(f"{Prisma.VIOLET}SUBSTRATE: TTS synthesis complete for {path}.{Prisma.RST}")
            except Exception as e:
                if events:
                    events.log(f"{Prisma.RED}SUBSTRATE FAULT: TTS failed - {e}{Prisma.RST}", "CRIT")
        thread = threading.Thread(target=_async_tts_task, args=(safe_path, self.events))
        thread.daemon = True
        thread.start()