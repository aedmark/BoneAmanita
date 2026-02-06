""" bone_commands.py - 'The snake spits out its tail. The circle becomes a line.' """

import shlex
from typing import Dict, Callable, List, Any, Tuple, Optional
from dataclasses import dataclass
from bone_core import BonePresets, TheLore

class CommandStateInterface:
    def __init__(self, engine_ref, prisma_ref, config_ref):
        self.eng = engine_ref
        self.P = prisma_ref
        self.Config = config_ref

    def log(self, text: str, category: str = "CMD"):
        if hasattr(self.eng, "events"):
            self.eng.events.log(text, category)
        else:
            print(f"[{category}] {text}")

    def trigger_visual_cortex(self) -> Optional[Dict]:
        if hasattr(self.eng, "process_turn"):
            return self.eng.process_turn("LOOK")
        return None

    def modify_resource(self, resource: str, delta: float):
        if resource == "stamina":
            self.eng.stamina = max(0.0, self.eng.stamina + delta)
        elif resource == "atp":
            if hasattr(self.eng, "bio"):
                self.eng.bio.mito.state.atp_pool = max(0.0, self.eng.bio.mito.state.atp_pool + delta)

    def get_resource(self, resource: str) -> float:
        if resource == "stamina": return self.eng.stamina
        if resource == "atp": return self.eng.bio.mito.state.atp_pool
        if resource == "health": return self.eng.health
        return 0.0

    def save_state(self) -> str:
        if hasattr(self.eng, "mind") and hasattr(self.eng.mind, "mem"):
            return self.eng.mind.mem.save(health=self.eng.health, stamina=self.eng.stamina)
        return "Error: Memory system not found."

    def get_vitals(self) -> Dict[str, float]:
        return {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "atp": self.eng.bio.mito.state.atp_pool,
            "max_health": getattr(self.Config, "MAX_HEALTH", 100.0),
            "max_stamina": getattr(self.Config, "MAX_STAMINA", 100.0)}

    def get_inventory(self) -> List[str]:
        if hasattr(self.eng, "gordon"):
            return getattr(self.eng.gordon, "inventory", [])
        return []

    def get_navigation_report(self) -> str:
        if not hasattr(self.eng, "town_hall") or not hasattr(self.eng, "phys"):
            return "Navigation Offline."
        nav = getattr(self.eng.town_hall, "Navigator", None)
        packet = self.eng.phys.tension.last_physics_packet

        if nav and packet:
            return nav.report_position(packet)
        return "Navigation Systems Unresponsive."

    def get_soul_status(self) -> Optional[str]:
        soul = getattr(self.eng, "soul", None)
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
    def __init__(self, engine, prisma_ref, lexicon_ref=None, config_ref=None, cartographer_ref=None):
        real_config = config_ref if config_ref else getattr(engine, "config", None)
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
        self.registry.register("/reload", self._cmd_reload, "Hot-reload Lore")

    def execute(self, text: str):
        if hasattr(self.interface.eng, "reality_stack"):
            stack = self.interface.eng.reality_stack
            rules = stack.get_grammar_rules()
            if not rules.get("allow_commands", True):
                if hasattr(self.interface, 'log'):
                    self.interface.log(
                        f"{self.P.RED}COMMAND REJECTED: Reality Depth {stack.current_depth} prohibits administrative override.{self.P.RST}",
                        "ERR")
                return True
        return self.registry.execute(text)

    def _cmd_help(self, _parts):
        lines = [
            f"\n{self.P.CYN}/// BONEAMANITA 14.5.0 TERMINAL ///{self.P.RST}",
            f"{self.P.GRY}Operating Phase: {self.interface.get_soul_status() or 'EXTANT'}{self.P.RST}\n"]
        structure = {
            "SURVIVAL":    ["/status", "/inventory", "/look"],
            "PROTOCOL":    ["/save", "/mode", "/exit", "/help"],
            "MYSTICISM":   ["/soul", "/map"],
            "MAINTENANCE": ["/debug", "/reload"]}
        buckets = {k: [] for k in structure.keys()}
        buckets["UNCATEGORIZED"] = []
        for cmd, desc in self.registry.help_text.items():
            found = False
            for cat, members in structure.items():
                if cmd in members:
                    buckets[cat].append((cmd, desc))
                    found = True
                    break
            if not found:
                buckets["UNCATEGORIZED"].append((cmd, desc))
        for cat, cmds in buckets.items():
            if not cmds: continue
            lines.append(f"{self.P.WHT}[{cat}]{self.P.RST}")
            for cmd, desc in cmds:
                lines.append(f"  {self.P.CYN}{cmd:<12}{self.P.RST} {desc}")
            lines.append("")
        lines.append(f"{self.P.GRY}>> Use wisely. Entropy is watching.{self.P.RST}")
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

    def _cmd_mode(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /mode [ZEN_GARDEN | THUNDERDOME | SANCTUARY]")
            return True
        mode_name = parts[1].upper()
        if not hasattr(BonePresets, mode_name):
            self.interface.log(f"{self.P.RED}Unknown mode: {mode_name}.{self.P.RST}")
            return True
        if self.tax.levy("MODE_SWITCH", {"stamina": 10.0}):
            preset = getattr(BonePresets, mode_name)
            logs = self.interface.Config.load_preset(preset)
            for log in logs:
                self.interface.log(log)
            phys_packet = None
            if hasattr(self.interface.eng, "phys") and hasattr(self.interface.eng.phys, "tension"):
                phys_packet = getattr(self.interface.eng.phys.tension, "last_physics_packet", None)
            if phys_packet:
                self.interface.Config.reconcile_state(phys_packet)
                self.interface.log(f"{self.P.CYN}State reconciled to {mode_name} parameters.{self.P.RST}")
            self.interface.log(f"Switched to {mode_name}.")
        return True

    def _cmd_save(self, _parts):
        res = self.interface.save_state()
        if "Error" in res or "Failed" in res:
            self.interface.log(f"{self.P.RED}SAVE FAILED: {res}{self.P.RST}")
        else:
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
        result = self.interface.trigger_visual_cortex()
        if result and result.get("ui"):
            self.interface.log(result["ui"])
        else:
            self.interface.log("Blindness. The engine cannot see.")
        return True

    def _cmd_reload(self, parts):
        if len(parts) > 1:
            target = parts[1].upper()
            TheLore.flush_cache(target)
            self.interface.log(f"Reloaded {target}.")
        else:
            TheLore.flush_cache()
            self.interface.log("Reloaded all Lore.")
        return True