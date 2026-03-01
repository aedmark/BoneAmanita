import os, json
import shlex
from typing import Dict, Callable, List, Any, Optional
from bone_core import LoreManifest, Prisma
from bone_config import BonePresets, BoneConfig

UX_STRINGS_PATH = os.path.join(os.path.dirname(__file__), "lore", "ux_strings.json")
try:
    with open(UX_STRINGS_PATH, "r", encoding="utf-8") as f:
        _UX_DATA = json.load(f)
except Exception:
    _UX_DATA = {}


def _get_ux(section: str, key: str, default: Any) -> Any:
    return _UX_DATA.get(section, {}).get(key, default)


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
                self.eng.bio.mito.state.atp_pool = max(
                    0.0, self.eng.bio.mito.state.atp_pool + delta
                )

    def get_resource(self, resource: str) -> float:
        if resource == "stamina":
            return self.eng.stamina
        if resource == "atp":
            return self.eng.bio.mito.state.atp_pool
        if resource == "health":
            return self.eng.health
        return 0.0

    def save_state(self) -> str:
        if not hasattr(self.eng, "mind") or not hasattr(self.eng.mind, "mem"):
            return _get_ux(
                "command_state", "mem_error", "Error: Memory system not found."
            )
        loc = _get_ux("command_state", "default_loc", "Unknown")
        last_out = _get_ux("command_state", "default_out", "Silence.")
        inv = []
        if hasattr(self.eng, "cortex"):
            state = self.eng.cortex.gather_state(
                getattr(self.eng.cortex, "last_physics", {})
            )
            def_orbit = _get_ux("command_state", "default_orbit", "Void")
            loc = state.get("world", {}).get("orbit", [def_orbit])[0]
            if self.eng.cortex.dialogue_buffer:
                last_out = self.eng.cortex.dialogue_buffer[-1]
        if hasattr(self.eng, "gordon"):
            inv = getattr(self.eng.gordon, "inventory", [])
        continuity_packet = {
            "location": loc,
            "last_output": last_out,
            "inventory": inv,
        }
        atlas_data = None
        if hasattr(self.eng, "navigator") and self.eng.navigator:
            atlas_data = self.eng.navigator.export_atlas()
        mito_traits = {}
        antibodies = None
        if hasattr(self.eng, "bio"):
            if hasattr(self.eng.bio, "mito") and hasattr(self.eng.bio.mito, "state"):
                mito_traits = self.eng.bio.mito.state.__dict__
            if hasattr(self.eng.bio, "immune"):
                antibodies = list(self.eng.bio.immune.active_antibodies)
            return self.eng.mind.mem.save(
                health=self.eng.health,
                stamina=self.eng.stamina,
                mutations={},
                trauma_accum=getattr(self.eng, "trauma_accum", {}),
                joy_history=[],
                mitochondria_traits=mito_traits,
                antibodies=antibodies,
                soul_data=(
                    self.eng.soul.to_dict() if hasattr(self.eng, "soul") else None
                ),
                continuity=continuity_packet,
                world_atlas=atlas_data,
                village_data=None,
            )
        return _get_ux(
            "command_state", "unreachable_error", "Error: Memory system unreachable."
        )

    def get_vitals(self) -> Dict[str, float]:
        metrics = self.eng.get_metrics()
        return {
            "health": metrics.get("health", 0.0),
            "stamina": metrics.get("stamina", 0.0),
            "atp": metrics.get("atp", 0.0),
            "max_health": getattr(self.Config, "MAX_HEALTH", 100.0),
            "max_stamina": getattr(self.Config, "MAX_STAMINA", 100.0),
        }

    def get_inventory(self) -> List[str]:
        if hasattr(self.eng, "gordon"):
            return getattr(self.eng.gordon, "inventory", [])
        return []

    def get_navigation_report(self) -> str:
        if not hasattr(self.eng, "navigator") or not hasattr(self.eng, "phys"):
            return _get_ux("command_state", "nav_offline", "Navigation Offline.")
        nav = self.eng.navigator
        packet = None
        if hasattr(self.eng.phys, "observer"):
            packet = getattr(self.eng.phys.observer, "last_physics_packet", None)

        if nav and packet:
            return nav.report_position(packet)
        return _get_ux(
            "command_state", "nav_unresponsive", "Navigation Systems Unresponsive."
        )

    def get_soul_status(self) -> Optional[str]:
        soul = getattr(self.eng, "soul", None)
        if soul:
            return soul.get_soul_state()
        return None


class ResourceTax:
    def __init__(self, state: CommandStateInterface):
        self.state = state

    def levy(self, _context: str, costs: Dict[str, float]) -> bool:
        stamina_cost = costs.get("stamina", 0.0)
        atp_cost = costs.get("atp", 0.0)

        msg_exh = _get_ux(
            "resource_tax", "exhausted", "🛑 EXHAUSTED: Requires {cost} Stamina."
        )
        msg_starv = _get_ux(
            "resource_tax", "starving", "🛑 STARVING: Requires {cost} ATP."
        )

        if self.state.get_resource("stamina") < stamina_cost:
            self.state.log(
                f"{self.state.P.RED}{msg_exh.format(cost=stamina_cost)}{self.state.P.RST}"
            )
            return False
        if self.state.get_resource("atp") < atp_cost:
            self.state.log(
                f"{self.state.P.RED}{msg_starv.format(cost=atp_cost)}{self.state.P.RST}"
            )
            return False
        if stamina_cost > 0:
            self.state.modify_resource("stamina", -stamina_cost)
        if atp_cost > 0:
            self.state.modify_resource("atp", -atp_cost)
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
        if not text.startswith("/"):
            return False
        try:
            parts = shlex.split(text)
        except ValueError:
            self.state.log(
                _get_ux("command_registry", "syntax_error", "Syntax Error."), "CMD"
            )
            return True
        cmd = parts[0].lower()
        if cmd in self.commands:
            return self.commands[cmd](parts)
        else:
            msg = _get_ux(
                "command_registry",
                "unknown_command",
                "Unknown command '{cmd}'. Try /help.",
            )
            self.state.log(msg.format(cmd=cmd), "CMD")
            return True


class CommandProcessor:
    def __init__(
        self,
        engine,
        prisma_ref,
        _lexicon_ref=None,
        config_ref=None,
        _cartographer_ref=None,
    ):
        real_config = config_ref if config_ref else BoneConfig
        self.interface = CommandStateInterface(engine, prisma_ref, real_config)
        self.tax = ResourceTax(self.interface)
        self.registry = CommandRegistry(self.interface)
        self.P = prisma_ref

        def _cd(key, default):
            return _get_ux("command_descriptions", key, default)

        self.registry.register("/help", self._cmd_help, _cd("help", "Show this menu"))
        self.registry.register(
            "/status", self._cmd_status, _cd("status", "Check vitals")
        )
        self.registry.register("/save", self._cmd_save, _cd("save", "Persist state"))
        self.registry.register(
            "/inventory", self._cmd_inventory, _cd("inventory", "Check pockets")
        )
        self.registry.register("/map", self._cmd_map, _cd("map", "Navigation check"))
        self.registry.register(
            "/mode", self._cmd_mode, _cd("mode", "Switch operational mode")
        )
        self.registry.register(
            "/debug", self._cmd_debug, _cd("debug", "Toggle verbose logs")
        )
        self.registry.register("/exit", self._cmd_exit, _cd("exit", "Shutdown"))
        self.registry.register("/soul", self._cmd_soul, _cd("soul", "Introspection"))
        self.registry.register(
            "/look", self._cmd_look, _cd("look", "Observe environment")
        )
        self.registry.register(
            "/reload", self._cmd_reload, _cd("reload", "Hot-reload Lore")
        )
        self.registry.register(
            "/truth", self._cmd_truth, _cd("truth", "Adjust Reality Ambiguity [0-3]")
        )
        self.registry.register(
            "/soothe", self._cmd_soothe, _cd("soothe", "Burn ATP to quell memory guilt")
        )
        self.registry.register("/use", self._cmd_use, _cd("use", "Use/Consume an item"))

    def execute(self, text: str):
        if hasattr(self.interface.eng, "reality_stack"):
            stack = self.interface.eng.reality_stack
            rules = stack.get_grammar_rules()
            if not rules.get("allow_commands", True):
                msg = _get_ux(
                    "command_alerts",
                    "reality_lock",
                    "COMMAND REJECTED: Reality Depth {depth} prohibits administrative override.",
                )
                self.interface.log(
                    f"{self.P.RED}{msg.format(depth=stack.current_depth)}{self.P.RST}",
                    "ERR",
                )
                return True

        text_upper = text.upper()

        def _vn(key, default):
            return _get_ux("vsl_notifications", key, default)

        if "[VSL_LITE]" in text_upper:
            self.interface.eng.ui_mode = "LITE"
            self.interface.log(
                f"{self.P.CYN}{_vn('lite', '[VSL_LITE]: Simple energy meter engaged.')}{self.P.RST}"
            )
        elif "[VSL_CORE]" in text_upper:
            self.interface.eng.ui_mode = "CORE"
            self.interface.log(
                f"{self.P.CYN}{_vn('core', '[VSL_CORE]: 5-Coordinate display engaged.')}{self.P.RST}"
            )
        elif "[VSL_DEEP]" in text_upper:
            self.interface.eng.ui_mode = "DEEP"
            self.interface.log(
                f"{self.P.MAG}{_vn('deep', '[VSL_DEEP]: Full 15-vector lattice exposed.')}{self.P.RST}"
            )

        if "[MOD:CODING]" in text_upper or "[SLASH]" in text_upper:
            self.interface.log(
                f"{self.P.INDIGO}{_vn('coding', 'SLASH Mod Chip Engaged.')}{self.P.RST}"
            )
            if hasattr(self.interface.eng, "council") and hasattr(
                self.interface.eng.council, "slash_council"
            ):
                self.interface.eng.council.slash_council.active = True

        if "[VSL_IDLE]" in text_upper:
            self.interface.log(
                f"{self.P.VIOLET}{_vn('idle', '[VSL_IDLE]: Zero ATP burn. Village dormant.')}{self.P.RST}"
            )
            self.interface.eng.mode_settings = {"atp_drain_enabled": False}
        elif "[VSL_RECOVER]" in text_upper:
            self.interface.log(
                f"{self.P.GRN}{_vn('recover', '[VSL_RECOVER]: Zen mode. Stamina regenerating.')}{self.P.RST}"
            )
            self.interface.modify_resource("stamina", 20.0)

        if text.startswith("/"):
            return self.registry.execute(text)

        return False

    def _cmd_soothe(self, _parts):
        cost = 25.0
        current_stamina = self.interface.get_resource("stamina")
        if current_stamina < cost:
            msg = _get_ux(
                "command_alerts",
                "soothe_weak",
                "Too weak to mourn. (Req: {cost} Stamina)",
            )
            self.interface.log(f"{self.P.RED}{msg.format(cost=cost)}{self.P.RST}")
            return True
        if (
            not hasattr(self.interface.eng, "mind")
            or not hasattr(self.interface.eng.mind, "mem")
            or not hasattr(self.interface.eng.mind.mem, "soothe_conscience")
        ):
            msg = _get_ux(
                "command_alerts",
                "soothe_missing_mem",
                "The subconscious is not installed.",
            )
            self.interface.log(f"{self.P.YEL}{msg}{self.P.RST}")
            return True
        self.interface.modify_resource("stamina", -cost)
        result_msg = self.interface.eng.mind.mem.soothe_conscience()
        msg = _get_ux("command_alerts", "soothe_success", "🏺 {msg} (-{cost} Stamina)")
        self.interface.log(
            f"{self.P.OCHRE}{msg.format(msg=result_msg, cost=cost)}{self.P.RST}"
        )
        return True

    def _cmd_help(self, _parts):
        header = _get_ux("help_menu", "header", "/// BONEAMANITA 16.2.0 TERMINAL ///")
        phase_pfx = _get_ux("help_menu", "phase_prefix", "Operating Phase: ")
        def_phase = _get_ux("help_menu", "default_phase", "EXTANT")
        footer = _get_ux("help_menu", "footer", ">> Use wisely. Entropy is watching.")
        uncat = _get_ux("help_menu", "uncategorized", "UNCATEGORIZED")

        default_structure = {
            "SURVIVAL": ["/status", "/inventory", "/look"],
            "PROTOCOL": ["/save", "/mode", "/exit", "/help"],
            "MYSTICISM": ["/soul", "/map", "/truth"],
            "MAINTENANCE": ["/debug", "/reload"],
        }
        structure = _get_ux("help_menu", "structure", default_structure)

        lines = [
            f"\n{self.P.CYN}{header}{self.P.RST}",
            f"{self.P.GRY}{phase_pfx}{self.interface.get_soul_status() or def_phase}{self.P.RST}\n",
        ]

        buckets = {k: [] for k in structure.keys()}
        buckets[uncat] = []
        cmd_to_cat = {cmd: cat for cat, cmds in structure.items() for cmd in cmds}

        for cmd, desc in self.registry.help_text.items():
            cat = cmd_to_cat.get(cmd, uncat)
            if cat not in buckets:
                buckets[cat] = []
            buckets[cat].append((cmd, desc))

        for cat, cmds in buckets.items():
            if not cmds:
                continue
            lines.append(f"{self.P.WHT}[{cat}]{self.P.RST}")
            for cmd, desc in cmds:
                lines.append(f"  {self.P.CYN}{cmd:<12}{self.P.RST} {desc}")
            lines.append("")

        lines.append(f"{self.P.GRY}{footer}{self.P.RST}")
        self.interface.log("\n".join(lines))
        return True

    def _cmd_status(self, _parts):
        v = self.interface.get_vitals()

        def bar(curr, max_v, col):
            max_v = max(1.0, max_v)
            filled = int(max(0.0, min(1.0, curr / max_v)) * 10)
            return f"{col}{'█'*filled}{'░'*(10-filled)}{self.P.RST}"

        self.interface.log(
            f"Health:  {bar(v['health'], v['max_health'], self.P.RED)} {v['health']:.0f}\n"
            f"Stamina: {bar(v['stamina'], v['max_stamina'], self.P.GRN)} {v['stamina']:.0f}\n"
            f"Energy:  {bar(v['atp'], 200, self.P.YEL)} {v['atp']:.0f}"
        )
        return True

    def _cmd_mode(self, parts):
        if len(parts) < 2:
            self.interface.log(
                _get_ux(
                    "command_alerts",
                    "mode_usage",
                    "Usage: /mode [ZEN_GARDEN | THUNDERDOME | SANCTUARY]",
                )
            )
            return True
        mode_name = parts[1].upper()
        if not hasattr(BonePresets, mode_name):
            msg = _get_ux("command_alerts", "mode_unknown", "Unknown mode: {mode}.")
            self.interface.log(f"{self.P.RED}{msg.format(mode=mode_name)}{self.P.RST}")
            return True
        if self.tax.levy("MODE_SWITCH", {"stamina": 10.0}):
            preset = getattr(BonePresets, mode_name)
            logs = self.interface.Config.load_preset(preset)
            for log in logs:
                self.interface.log(log)
            phys_packet = None
            if hasattr(self.interface.eng, "phys") and hasattr(
                self.interface.eng.phys, "observer"
            ):
                phys_packet = getattr(
                    self.interface.eng.phys.observer, "last_physics_packet", None
                )
            if phys_packet:
                self.interface.Config.reconcile_state(phys_packet)
                msg = _get_ux(
                    "command_alerts",
                    "mode_reconciled",
                    "State reconciled to {mode} parameters.",
                )
                self.interface.log(
                    f"{self.P.CYN}{msg.format(mode=mode_name)}{self.P.RST}"
                )
            msg = _get_ux("command_alerts", "mode_switched", "Switched to {mode}.")
            self.interface.log(msg.format(mode=mode_name))
        return True

    def _cmd_save(self, _parts):
        res = self.interface.save_state()
        if "Error" in res or "Failed" in res:
            msg = _get_ux("command_alerts", "save_failed", "SAVE FAILED: {res}")
            self.interface.log(f"{self.P.RED}{msg.format(res=res)}{self.P.RST}")
        else:
            msg = _get_ux("command_alerts", "save_success", "SAVED: {res}")
            self.interface.log(f"{self.P.GRN}{msg.format(res=res)}{self.P.RST}")
        return True

    def _cmd_inventory(self, _parts):
        items = self.interface.get_inventory()
        P = self.interface.P

        header = _get_ux("inventory_strings", "header", "/// GORDON KNOT STORAGE ///")
        empty = _get_ux("inventory_strings", "empty", "   [POCKETS EMPTY]")
        slots_str = _get_ux("inventory_strings", "slots", "Slots")

        self.interface.log(f"{P.WHT}{header}{P.RST}")
        if not items:
            self.interface.log(f"{P.GRY}{empty}{P.RST}")
            return True
        for i, item in enumerate(items):
            self.interface.log(f" {P.GRY}{i + 1}.{P.RST} {P.CYN}{item.upper()}{P.RST}")
        self.interface.log(
            f"{P.GRY}   ({len(items)}/{self.interface.Config.INVENTORY.MAX_SLOTS} {slots_str}){P.RST}"
        )
        return True

    def _cmd_map(self, _parts):
        if not self.tax.levy("MAP", {"stamina": 2.0}):
            return True
        nav_report = self.interface.get_navigation_report()
        self.interface.log(nav_report)
        return True

    def _cmd_debug(self, _parts):
        self.interface.Config.VERBOSE_LOGGING = (
            not self.interface.Config.VERBOSE_LOGGING
        )
        msg = _get_ux("command_alerts", "debug_mode", "Debug Mode: {state}")
        self.interface.log(msg.format(state=self.interface.Config.VERBOSE_LOGGING))
        return True

    def _cmd_exit(self, _parts):
        import sys

        msg = _get_ux("command_alerts", "exit_halt", "System Halt Initiated.")
        self.interface.log(f"{Prisma.RED}{msg}{Prisma.RST}", "SYS")
        if "streamlit" in sys.modules:
            try:
                import streamlit as st

                st.stop()
            except Exception:
                pass
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
            self.interface.log(
                _get_ux(
                    "command_alerts", "look_blind", "Blindness. The engine cannot see."
                )
            )
        return True

    def _cmd_reload(self, parts):
        if len(parts) > 1:
            target = parts[1].upper()
            LoreManifest.get_instance().flush_cache(target)
            msg = _get_ux("command_alerts", "reload_target", "Reloaded {target}.")
            self.interface.log(msg.format(target=target))
        else:
            LoreManifest.get_instance().flush_cache()
            self.interface.log(
                _get_ux("command_alerts", "reload_all", "Reloaded all Lore.")
            )
        return True

    def _cmd_truth(self, parts):
        if len(parts) < 2:
            self.interface.log(
                _get_ux(
                    "command_alerts",
                    "truth_usage",
                    "Usage: /truth [0=Boardroom, 1=Workshop, 2=RedTeam, 3=Palimpsest]",
                )
            )
            return True
        from bone_gui import TruthRenderer

        try:
            mode = int(parts[1])
            if not (0 <= mode <= 3):
                raise ValueError
            orchestrator = getattr(self.interface.eng, "orchestrator", None)
            if not orchestrator:
                self.interface.log(
                    _get_ux(
                        "command_alerts",
                        "truth_no_orch",
                        "Error: Orchestrator not found.",
                    )
                )
                return True
            reporter = getattr(orchestrator, "reporter", None)
            if not reporter:
                self.interface.log(
                    _get_ux(
                        "command_alerts",
                        "truth_no_reporter",
                        "Error: CycleReporter not found.",
                    )
                )
                return True
            if not hasattr(reporter.renderer, "dial_setting"):
                msg = _get_ux(
                    "command_alerts",
                    "truth_transplant",
                    "[SYS] Transplanting TruthRenderer into active cycle...",
                )
                self.interface.log(f"{self.P.YEL}{msg}{self.P.RST}")
                new_renderer = TruthRenderer(self.interface.eng)
                reporter.renderer = new_renderer
                reporter.renderers["STANDARD"] = new_renderer
            reporter.renderer.dial_setting = mode
            modes = ["BOARDROOM", "WORKSHOP", "RED TEAM", "PALIMPSEST"]
            msg = _get_ux(
                "command_alerts", "truth_dial_set", "Ambiguity Dial set to: {mode}"
            )
            self.interface.log(
                f"{self.P.CYN}{msg.format(mode=modes[mode])}{self.P.RST}"
            )
        except ValueError:
            self.interface.log(
                _get_ux("command_alerts", "truth_invalid", "Invalid mode. Use 0-3.")
            )
        except Exception as e:
            msg = _get_ux(
                "command_alerts", "truth_failure", "Truth Dial Failure: {error}"
            )
            self.interface.log(msg.format(error=e))
        return True

    def _cmd_use(self, parts):
        if len(parts) < 2:
            self.interface.log(
                _get_ux("command_alerts", "use_usage", "Usage: /use [ITEM_NAME]")
            )
            return True
        item_name = parts[1].upper()
        gordon = getattr(self.interface.eng, "gordon", None)
        if not gordon:
            msg = _get_ux("command_alerts", "use_no_inv", "Inventory system offline.")
            self.interface.log(f"{self.P.RED}{msg}{self.P.RST}")
            return True
        success, msg = gordon.consume(item_name)
        color = self.P.GRN if success else self.P.OCHRE
        self.interface.log(f"{color}{msg}{self.P.RST}")
        return True
