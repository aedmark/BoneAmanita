""" bone_commands.py
 'The snake spits out its tail. The circle becomes a line.' """

import shlex
from typing import Dict, Callable, List, Any, Tuple, Optional
from dataclasses import dataclass


class CommandStateInterface:
    def __init__(self, engine_ref, prisma_ref, config_ref):
        self._eng = engine_ref
        self.P = prisma_ref
        self.Config = config_ref

    def log(self, text: str, category: str = "CMD"):
        if hasattr(self._eng, "events"):
            self._eng.events.log(text, category)
        else:
            print(f"[{category}] {text}")

    def modify_resource(self, resource: str, delta: float):
        if resource == "stamina":
            self._eng.stamina = max(0.0, self._eng.stamina + delta)
        elif resource == "atp":
            if hasattr(self._eng, "bio"):
                self._eng.bio.mito.state.atp_pool = max(0.0, self._eng.bio.mito.state.atp_pool + delta)

    def get_resource(self, resource: str) -> float:
        if resource == "stamina": return self._eng.stamina
        if resource == "atp": return self._eng.bio.mito.state.atp_pool
        if resource == "health": return self._eng.health
        return 0.0

    def save_state(self) -> str:
        if hasattr(self._eng, "mind") and hasattr(self._eng.mind, "mem"):
            return self._eng.mind.mem.save(health=self._eng.health, stamina=self._eng.stamina)
        return "Error: Memory system not found."

    def get_vitals(self) -> Dict[str, float]:
        return {
            "health": self._eng.health,
            "stamina": self._eng.stamina,
            "atp": self._eng.bio.mito.state.atp_pool,
            "max_health": getattr(self.Config, "MAX_HEALTH", 100.0),
            "max_stamina": getattr(self.Config, "MAX_STAMINA", 100.0)}

    def get_inventory(self) -> List[str]:
        if hasattr(self._eng, "gordon"):
            return getattr(self._eng.gordon, "inventory", [])
        return []

    def get_navigation_report(self) -> str:
        if not hasattr(self._eng, "town_hall") or not hasattr(self._eng, "phys"):
            return "Navigation Offline."
        nav = getattr(self._eng.town_hall, "Navigator", None)
        packet = self._eng.phys.tension.last_physics_packet

        if nav and packet:
            return nav.report_position(packet)
        return "Navigation Systems Unresponsive."

    def get_soul_status(self) -> Optional[str]:
        soul = getattr(self._eng, "soul", None)
        if soul:
            return soul.get_soul_state()
        return None

class ResourceTax:
    def __init__(self, state: CommandStateInterface):
        self.state = state

    def levy(self, context: str, costs: Dict[str, float]) -> bool:
        stamina_cost = costs.get("stamina", 0.0)
        atp_cost = costs.get("atp", 0.0)
        if self.state.get_resource("stamina") < stamina_cost:
            self.state.log(f"{self.state.P.RED}🛑 EXHAUSTED: Requires {stamina_cost} Stamina.{self.state.P.RST}")
            return False
        if self.state.get_resource("atp") < atp_cost:
            self.state.log(f"{self.state.P.RED}🛑 STARVING: Requires {atp_cost} ATP.{self.state.P.RST}")
            return False
        if stamina_cost > 0: self.state.modify_resource("stamina", -stamina_cost)
        if atp_cost > 0: self.state.modify_resource("atp", -atp_cost)
        return True

class CommandRegistry:
    def __init__(self, state: CommandStateInterface):
        self.state = state
        self.commands: Dict[str, Callable] = {}
        self.help_text: Dict[str, str] = {}

    def register(self, name: str, func: Callable, help_str: str):
        self.commands[name] = func
        self.help_text[name] = help_str

    def execute(self, text: str) -> bool:
        if not text.startswith("/"): return False
        try:
            parts = shlex.split(text)
        except ValueError:
            self.state.log("Syntax Error.", "CMD")
            return True
        cmd = parts[0].lower()
        if cmd in self.commands:
            return self.commands[cmd](parts)
        else:
            self.state.log(f"Unknown command '{cmd}'. Try /help.", "CMD")
            return True

class CommandProcessor:
    def __init__(self, engine, prisma_ref, lexicon_ref, config_ref, cartographer_ref=None):
        self.interface = CommandStateInterface(engine, prisma_ref, config_ref)
        self.tax = ResourceTax(self.interface)
        self.registry = CommandRegistry(self.interface)
        self.P = prisma_ref
        self.registry.register("/help", self._cmd_help, "Show this menu")
        self.registry.register("/status", self._cmd_status, "Check vitals")
        self.registry.register("/save", self._cmd_save, "Persist state")
        self.registry.register("/inventory", self._cmd_inventory, "Check pockets")
        self.registry.register("/map", self._cmd_map, "Navigation check")
        self.registry.register("/mode", self._cmd_mode, "Switch operational mode")
        self.registry.register("/debug", self._cmd_debug, "Toggle verbose logs")
        self.registry.register("/exit", self._cmd_exit, "Shutdown")
        self.registry.register("/soul", self._cmd_soul, "Introspection")
        self.registry.register("/look", self._cmd_look, "Observe environment")

    def execute(self, text: str):
        return self.registry.execute(text)

    def _cmd_help(self, _parts):
        lines = [f"\n{self.P.CYN}:: BONEAMANITA 11.7.0 ::{self.P.RST}"]
        for cmd, desc in self.registry.help_text.items():
            lines.append(f"{self.P.WHT}{cmd:<12}{self.P.RST} {desc}")
        self.interface.log("\n".join(lines))
        return True

    def _cmd_status(self, _parts):
        v = self.interface.get_vitals()
        def bar(curr, max_v, col):
            filled = int((curr / max_v) * 10)
            return f"{col}{'█'*filled}{'░'*(10-filled)}{self.P.RST}"

        self.interface.log(
            f"Health:  {bar(v['health'], v['max_health'], self.P.RED)} {v['health']:.0f}\n"
            f"Stamina: {bar(v['stamina'], v['max_stamina'], self.P.GRN)} {v['stamina']:.0f}\n"
            f"Energy:  {bar(v['atp'], 200, self.P.YEL)} {v['atp']:.0f}")
        return True

    def _cmd_save(self, _parts):
        res = self.interface.save_state()
        self.interface.log(f"{self.P.GRN}SAVED: {res}{self.P.RST}")
        return True

    def _cmd_inventory(self, _parts):
        inv = self.interface.get_inventory()
        self.interface.log(f"Pocket: {inv if inv else 'Empty'}")
        return True

    def _cmd_map(self, _parts):
        if not self.tax.levy("MAP", {"stamina": 2.0}): return True
        nav_report = self.interface.get_navigation_report()
        self.interface.log(nav_report)
        return True

    def _cmd_mode(self, parts):
        if len(parts) < 2: return True
        if self.tax.levy("MODE_SWITCH", {"stamina": 10.0}):
            self.interface.log(f"Switched to {parts[1].upper()} (Simulated)")
        return True

    def _cmd_debug(self, _parts):
        self.interface.Config.VERBOSE_LOGGING = not self.interface.Config.VERBOSE_LOGGING
        self.interface.log(f"Debug Mode: {self.interface.Config.VERBOSE_LOGGING}")
        return True

    def _cmd_exit(self, _parts):
        self.interface.log("Shutting down...")
        raise KeyboardInterrupt

    def _cmd_soul(self, _parts):
        soul_msg = self.interface.get_soul_status()
        if soul_msg:
            self.interface.log(f"{self.P.MAG}{soul_msg}{self.P.RST}")
        return True

    def _cmd_look(self, _parts):
        self.interface.log("You see the code structure. It is cleaner now.")
        return True