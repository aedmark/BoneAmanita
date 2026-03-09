"""bone_commands.py"""

import shlex
from typing import Dict, Callable, List, Optional

from bone_config import BonePresets, BoneConfig
from bone_core import LoreManifest, Prisma, ux


class CommandStateInterface:
    """
    An adapter layer that safely bridges the CLI commands with the delicate biological
    and cognitive engines. Prevents out-of-band queries from crashing the lattice if
    certain organs (like the Cartographer or BioSystem) are offline or damaged.
    """
    def __init__(self, engine_ref, prisma_ref, config_ref):
        self.eng = engine_ref
        self.P = prisma_ref
        self.Config = config_ref

    def log(self, text: str, category: str = "CMD"):
        """ Routes standard output through the EventBus to be properly metabolized and rendered, or falls back to standard print if the bus is down. """
        if hasattr(self.eng, "events"):
            self.eng.events.log(text, category)
        else:
            print(f"[{category}] {text}")

    def trigger_visual_cortex(self) -> Optional[Dict]:
        """ Forces the engine to re-evaluate and render the current spatial and inventory context without advancing the metabolic clock. """
        if hasattr(self.eng, "process_turn"):
            return self.eng.process_turn("LOOK")
        return None

    def modify_resource(self, resource: str, delta: float):
        """ Directly manipulates the core metabolic pools (ATP, Stamina) without passing through the standard digestive cycle. """
        if resource == "stamina":
            self.eng.stamina = max(0.0, self.eng.stamina + delta)
        elif resource == "atp":
            if hasattr(self.eng, "bio"):
                self.eng.bio.mito.state.atp_pool = max(0.0, self.eng.bio.mito.state.atp_pool + delta)

    def get_resource(self, resource: str) -> float:
        """ Safely extracts vital metrics, defaulting to zero if the organism is severely degraded. """
        if resource == "stamina":
            return self.eng.stamina
        if resource == "atp":
            return self.eng.bio.mito.state.atp_pool
        if resource == "health":
            return self.eng.health
        return 0.0

    def save_state(self) -> str:
        """ Serializes the entire physical, mental, and spatial state of the lattice into a stable fossil for later resurrection. """
        if not hasattr(self.eng, "mind") or not hasattr(self.eng.mind, "mem"):
            return ux("command_state", "mem_error")
        loc = ux("command_state", "default_loc")
        last_out = ux("command_state", "default_out")
        inv = []
        if hasattr(self.eng, "cortex"):
            state = self.eng.cortex.gather_state(getattr(self.eng.cortex, "last_physics", {}))
            def_orbit = ux("command_state", "default_orbit")
            loc = state.get("world", {}).get("orbit", [def_orbit])[0]
            if self.eng.cortex.dialogue_buffer:
                last_out = self.eng.cortex.dialogue_buffer[-1]
        if hasattr(self.eng, "gordon"):
            inv = getattr(self.eng.gordon, "inventory", [])
        continuity_packet = {"location": loc, "last_output": last_out, "inventory": inv, }
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
            return self.eng.mind.mem.save(health=self.eng.health, stamina=self.eng.stamina, mutations={},
                                          trauma_accum=getattr(self.eng, "trauma_accum", {}), joy_history=[],
                                          mitochondria_traits=mito_traits, antibodies=antibodies,
                                          soul_data=(self.eng.soul.to_dict() if hasattr(self.eng, "soul") else None),
                                          continuity=continuity_packet, world_atlas=atlas_data, village_data=None, )
        return ux("command_state", "unreachable_error")

    def get_vitals(self) -> Dict[str, float]:
        """ Packages the core survival metrics (Health, Stamina, ATP) for UI rendering. """
        metrics = self.eng.get_metrics()
        cmd_cfg = getattr(self.Config, "COMMANDS", None)
        return {"health": metrics.get("health", 0.0), "stamina": metrics.get("stamina", 0.0),
                "atp": metrics.get("atp", 0.0), "max_health": getattr(self.Config, "MAX_HEALTH", 100.0),
                "max_stamina": getattr(self.Config, "MAX_STAMINA", 100.0),
                "max_atp": getattr(cmd_cfg, "STATUS_MAX_ATP", 200.0) if cmd_cfg else 200.0, }

    def get_inventory(self) -> List[str]:
        """ Peeks into Gordon's pockets to retrieve current structural items. """
        if hasattr(self.eng, "gordon"):
            return getattr(self.eng.gordon, "inventory", [])
        return []

    def get_navigation_report(self) -> str:
        """ Asks the Cartographer where the system currently resides within the semantic manifold. """
        if not hasattr(self.eng, "navigator") or not hasattr(self.eng, "phys"):
            return ux("command_state", "nav_offline")
        nav = self.eng.navigator
        packet = None
        if hasattr(self.eng.phys, "observer"):
            packet = getattr(self.eng.phys.observer, "last_physics_packet", None)
        if nav and packet:
            return nav.report_position(packet)
        return ux("command_state", "nav_unresponsive")

    def get_soul_status(self) -> Optional[str]:
        """ Checks the current driving archetype occupying the narrative seat. """
        soul = getattr(self.eng, "soul", None)
        if soul:
            return soul.get_soul_state()
        return None

class ResourceTax:
    """
    The metabolic tollbooth for out-of-band actions. Ensures that even
    system commands carry a physical weight, preventing free lunches.
    """
    def __init__(self, state: CommandStateInterface):
        self.state = state

    def levy(self, _context: str, costs: Dict[str, float]) -> bool:
        """ Deducts the physical cost of running a command, halting execution if the system is starved or exhausted. """
        stamina_cost = costs.get("stamina", 0.0)
        atp_cost = costs.get("atp", 0.0)
        msg_exh = ux("resource_tax", "exhausted")
        msg_starv = ux("resource_tax", "starving")
        if self.state.get_resource("stamina") < stamina_cost:
            self.state.log(f"{self.state.P.RED}{msg_exh.format(cost=stamina_cost)}{self.state.P.RST}")
            return False
        if self.state.get_resource("atp") < atp_cost:
            self.state.log(f"{self.state.P.RED}{msg_starv.format(cost=atp_cost)}{self.state.P.RST}")
            return False
        if stamina_cost > 0:
            self.state.modify_resource("stamina", -stamina_cost)
        if atp_cost > 0:
            self.state.modify_resource("atp", -atp_cost)
        return True

class CommandRegistry:
    """ A simple dictionary mapping string inputs (slash commands) to their execution pathways. """
    def __init__(self, state: CommandStateInterface):
        self.state = state
        self.commands: Dict[str, Callable] = {}
        self.help_text: Dict[str, str] = {}

    def register(self, name: str, func: Callable, help_str: str):
        """ Binds a command string to its corresponding class method. """
        self.commands[name] = func
        self.help_text[name] = help_str

    def execute(self, text: str) -> bool:
        """ Safely tokenizes user input and routes it to the appropriate command function. """
        if not text.startswith("/"):
            return False
        try:
            parts = shlex.split(text)
        except ValueError:
            self.state.log(ux("command_registry", "syntax_error"), "CMD")
            return True
        cmd = parts[0].lower()
        if cmd in self.commands:
            return self.commands[cmd](parts)
        else:
            msg = ux("command_registry", "unknown_command")
            self.state.log(msg.format(cmd=cmd), "CMD")
            return True

class CommandProcessor:
    """
    The master router for terminal interactions. It intercepts user input before
    it hits the LLM, checking for reality locks, VSL meta-tags, and slash commands.
    """
    def __init__(self, engine, prisma_ref, _lexicon_ref=None, config_ref=None, _cartographer_ref=None, ):
        real_config = config_ref if config_ref else BoneConfig
        self.interface = CommandStateInterface(engine, prisma_ref, real_config)
        self.tax = ResourceTax(self.interface)
        self.registry = CommandRegistry(self.interface)
        self.P = prisma_ref

        def _cd(key):
            return ux("command_descriptions", key)

        self.registry.register("/help", self._cmd_help, _cd("help"))
        self.registry.register("/status", self._cmd_status, _cd("status"))
        self.registry.register("/save", self._cmd_save, _cd("save"))
        self.registry.register("/inventory", self._cmd_inventory, _cd("inventory"))
        self.registry.register("/map", self._cmd_map, _cd("map"))
        self.registry.register("/mode", self._cmd_mode, _cd("mode"))
        self.registry.register("/debug", self._cmd_debug, _cd("debug"))
        self.registry.register("/exit", self._cmd_exit, _cd("exit"))
        self.registry.register("/soul", self._cmd_soul, _cd("soul"))
        self.registry.register("/look", self._cmd_look, _cd("look"))
        self.registry.register("/reload", self._cmd_reload, _cd("reload"))
        self.registry.register("/truth", self._cmd_truth, _cd("truth"))
        self.registry.register("/soothe", self._cmd_soothe, _cd("soothe"))
        self.registry.register("/use", self._cmd_use, _cd("use"))

    def execute(self, text: str):
        """ The primary intercept block. Checks for narrative lockouts and parses architectural flags (like [VSL_DEEP] or [SLASH]). """
        if hasattr(self.interface.eng, "reality_stack"):
            stack = self.interface.eng.reality_stack
            rules = stack.get_grammar_rules()
            if not rules.get("allow_commands", True):
                msg = ux("command_alerts", "reality_lock")
                self.interface.log(f"{self.P.RED}{msg.format(depth=stack.current_depth)}{self.P.RST}", "ERR",)
                return True
        text_upper = text.upper()

        def _vn(key):
            return ux("vsl_notifications", key)
        if "[VSL_LITE]" in text_upper:
            self.interface.eng.ui_mode = "LITE"
            self.interface.log(f"{self.P.CYN}{_vn('lite')}{self.P.RST}")
        elif "[VSL_CORE]" in text_upper:
            self.interface.eng.ui_mode = "CORE"
            self.interface.log(f"{self.P.CYN}{_vn('core')}{self.P.RST}")
        elif "[VSL_DEEP]" in text_upper:
            self.interface.eng.ui_mode = "DEEP"
            self.interface.log(f"{self.P.MAG}{_vn('deep')}{self.P.RST}")
        if "[MOD:CODING]" in text_upper or "[SLASH]" in text_upper:
            self.interface.log(f"{self.P.INDIGO}{_vn('coding')}{self.P.RST}")
            if hasattr(self.interface.eng, "council") and hasattr(self.interface.eng.council, "slash_council"):
                self.interface.eng.council.slash_council.active = True
        if "[VSL_IDLE]" in text_upper:
            self.interface.log(f"{self.P.VIOLET}{_vn('idle')}{self.P.RST}")
            self.interface.eng.mode_settings = {"atp_drain_enabled": False}
        elif "[VSL_RECOVER]" in text_upper:
            self.interface.log(f"{self.P.GRN}{_vn('recover')}{self.P.RST}")
            cmd_cfg = getattr(BoneConfig, "COMMANDS", None)
            recover_val = getattr(cmd_cfg, "RECOVER_STAMINA", 20.0) if cmd_cfg else 20.0
            self.interface.modify_resource("stamina", recover_val)
        if text.startswith("/"):
            return self.registry.execute(text)
        return False

    def _cmd_soothe(self, _parts):
        """ A manual override to clear trauma or reset anxiety, costing heavy Stamina. """
        cmd_cfg = getattr(BoneConfig, "COMMANDS", None)
        cost = getattr(cmd_cfg, "COST_SOOTHE", 25.0) if cmd_cfg else 25.0
        current_stamina = self.interface.get_resource("stamina")
        if current_stamina < cost:
            msg = ux("command_alerts", "soothe_weak")
            self.interface.log(f"{self.P.RED}{msg.format(cost=cost)}{self.P.RST}")
            return True
        if (not hasattr(self.interface.eng, "mind")
                or not hasattr(self.interface.eng.mind, "mem")
                or not hasattr(self.interface.eng.mind.mem, "soothe_conscience")):
            msg = ux("command_alerts", "soothe_missing_mem")
            self.interface.log(f"{self.P.YEL}{msg}{self.P.RST}")
            return True
        self.interface.modify_resource("stamina", -cost)
        result_msg = self.interface.eng.mind.mem.soothe_conscience()
        msg = ux("command_alerts", "soothe_success")
        self.interface.log(f"{self.P.OCHRE}{msg.format(msg=result_msg, cost=cost)}{self.P.RST}")
        return True

    def _cmd_help(self, _parts):
        """ Dynamically compiles and formats the help menu using localized strings. """
        header = ux("help_menu", "header")
        phase_pfx = ux("help_menu", "phase_prefix")
        def_phase = ux("help_menu", "default_phase")
        footer = ux("help_menu", "footer")
        uncat = ux("help_menu", "uncategorized")
        structure = ux("help_menu", "structure", {})
        lines = [f"\n{self.P.CYN}{header}{self.P.RST}", f"{self.P.GRY}{phase_pfx}{self.interface.get_soul_status() or def_phase}{self.P.RST}\n",]
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
        """ Renders an ASCII bar chart of the organism's core biological state. """
        v = self.interface.get_vitals()
        menu_cfg = LoreManifest.get_instance().get("ux_strings", "status_menu") or {}
        h_lbl = menu_cfg.get("health_label", "Health:  ")
        s_lbl = menu_cfg.get("stamina_label", "Stamina: ")
        e_lbl = menu_cfg.get("energy_label", "Energy:  ")
        b_f = menu_cfg.get("bar_filled", "█")
        b_e = menu_cfg.get("bar_empty", "░")

        def bar(curr, max_v, col):
            max_v = max(1.0, max_v)
            filled = int(max(0.0, min(1.0, curr / max_v)) * 10)
            return f"{col}{b_f*filled}{b_e*(10-filled)}{self.P.RST}"
        self.interface.log(
            f"{h_lbl}{bar(v['health'], v['max_health'], self.P.RED)} {v['health']:.0f}\n"
            f"{s_lbl}{bar(v['stamina'], v['max_stamina'], self.P.GRN)} {v['stamina']:.0f}\n"
            f"{e_lbl}{bar(v['atp'], v['max_atp'], self.P.YEL)} {v['atp']:.0f}")
        return True

    def _cmd_mode(self, parts):
        """ Swaps the operating mode, re-hydrating presets and attempting to reconcile physics constraints. """
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "mode_usage"))
            return True
        mode_name = parts[1].upper()
        if not hasattr(BonePresets, mode_name):
            msg = ux("command_alerts", "mode_unknown")
            self.interface.log(f"{self.P.RED}{msg.format(mode=mode_name)}{self.P.RST}")
            return True
        cmd_cfg = getattr(BoneConfig, "COMMANDS", None)
        cost = getattr(cmd_cfg, "COST_MODE", 10.0) if cmd_cfg else 10.0
        if self.tax.levy("MODE_SWITCH", {"stamina": cost}):
            preset = getattr(BonePresets, mode_name)
            logs = self.interface.Config.load_preset(preset)
            for log in logs:
                self.interface.log(log)
            phys_packet = None
            if hasattr(self.interface.eng, "phys") and hasattr(self.interface.eng.phys, "observer"):
                phys_packet = getattr(self.interface.eng.phys.observer, "last_physics_packet", None)
            if phys_packet:
                self.interface.Config.reconcile_state(phys_packet)
                msg = ux("command_alerts", "mode_reconciled")
                self.interface.log(f"{self.P.CYN}{msg.format(mode=mode_name)}{self.P.RST}")
            msg = ux("command_alerts", "mode_switched")
            self.interface.log(msg.format(mode=mode_name))
        return True

    def _cmd_save(self, _parts):
        """ Forces a manual save state. """
        res = self.interface.save_state()
        cfg = getattr(BoneConfig, "COMMANDS", None)
        error_flags = getattr(cfg, "SAVE_ERROR_FLAGS", ["Error", "Failed", "Exception"])
        if any(flag in res for flag in error_flags):
            msg = ux("command_alerts", "save_failed")
            self.interface.log(f"{self.P.RED}{msg.format(res=res)}{self.P.RST}")
        else:
            msg = ux("command_alerts", "save_success")
            self.interface.log(f"{self.P.GRN}{msg.format(res=res)}{self.P.RST}")
        return True

    def _cmd_inventory(self, _parts):
        """ Formats and displays Gordon's current item cache. """
        items = self.interface.get_inventory()
        P = self.interface.P
        header = ux("inventory_strings", "header")
        empty = ux("inventory_strings", "empty")
        slots_str = ux("inventory_strings", "slots")
        self.interface.log(f"{P.WHT}{header}{P.RST}")
        if not items:
            self.interface.log(f"{P.GRY}{empty}{P.RST}")
            return True
        for i, item in enumerate(items):
            self.interface.log(f" {P.GRY}{i + 1}.{P.RST} {P.CYN}{item.upper()}{P.RST}")
        self.interface.log(f"{P.GRY}   ({len(items)}/{self.interface.Config.INVENTORY.MAX_SLOTS} {slots_str}){P.RST}")
        return True

    def _cmd_map(self, _parts):
        """ Deducts stamina to poll the Cartographer for our exact semantic coordinates. """
        cmd_cfg = getattr(BoneConfig, "COMMANDS", None)
        cost = getattr(cmd_cfg, "COST_MAP", 2.0) if cmd_cfg else 2.0
        if not self.tax.levy("MAP", {"stamina": cost}):
            return True
        nav_report = self.interface.get_navigation_report()
        self.interface.log(nav_report)
        return True

    def _cmd_debug(self, _parts):
        """ Toggles verbose internal logging AND elevates the Reality Stack. """
        self.interface.Config.VERBOSE_LOGGING = (not self.interface.Config.VERBOSE_LOGGING)
        is_debug = self.interface.Config.VERBOSE_LOGGING
        if hasattr(self.interface.eng, "reality_stack"):
            if is_debug:
                self.interface.eng.reality_stack.stabilize_at(3)
            else:
                self.interface.eng.reality_stack.stabilize_at(1)
        msg = ux("command_alerts", "debug_mode")
        base_msg = msg.format(state=is_debug)
        layer_msg = "[D3:DBG] (Filters off)" if is_debug else "[D1:SIM] (Filters on)"
        self.interface.log(f"{base_msg} | Layer: {layer_msg}")
        return True

    def _cmd_exit(self, _parts):
        """ Triggers a system halt. """
        msg = ux("command_alerts", "exit_halt")
        self.interface.log(f"{Prisma.RED}{msg}{Prisma.RST}", "SYS")

    def _cmd_soul(self, _parts):
        """ Interrogates the NarrativeSelf for the current driving archetype. """
        soul_msg = self.interface.get_soul_status()
        if soul_msg:
            self.interface.log(f"{self.P.MAG}{soul_msg}{self.P.RST}")
        return True

    def _cmd_look(self, _parts):
        """ Probes the visual cortex for immediate environmental context. """
        result = self.interface.trigger_visual_cortex()
        if result and result.get("ui"):
            self.interface.log(result["ui"])
        else:
            self.interface.log(ux("command_alerts", "look_blind"))
        return True

    def _cmd_reload(self, parts):
        """ Hot-reloads specific or global caches from the LoreManifest without restarting the system. """
        if len(parts) > 1:
            target = parts[1].upper()
            LoreManifest.get_instance().flush_cache(target)
            msg = ux("command_alerts", "reload_target")
            self.interface.log(msg.format(target=target))
        else:
            LoreManifest.get_instance().flush_cache()
            self.interface.log(ux("command_alerts", "reload_all"))
        return True

    def _cmd_truth(self, parts):
        """
        A highly meta command that hot-swaps the UI Renderer to TruthRenderer,
        exposing the raw, internal argument between the archetypes before final output.
        """
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "truth_usage"))
            return True
        from bone_gui import TruthRenderer
        try:
            mode = int(parts[1])
            if not (0 <= mode <= 3):
                raise ValueError
            orchestrator = getattr(self.interface.eng, "orchestrator", None)
            if not orchestrator:
                self.interface.log(ux("command_alerts", "truth_no_orch"))
                return True
            reporter = getattr(orchestrator, "reporter", None)
            if not reporter:
                self.interface.log(ux("command_alerts", "truth_no_reporter"))
                return True
            if not hasattr(reporter.renderer, "dial_setting"):
                msg = ux("command_alerts", "truth_transplant")
                self.interface.log(f"{self.P.YEL}{msg}{self.P.RST}")
                new_renderer = TruthRenderer(self.interface.eng)
                reporter.renderer = new_renderer
                reporter.renderers["STANDARD"] = new_renderer
            reporter.renderer.dial_setting = mode
            modes = ux("command_alerts", "truth_modes", ["BOARDROOM", "WORKSHOP", "RED TEAM", "PALIMPSEST"])
            msg = ux("command_alerts", "truth_dial_set")
            selected_mode = modes[mode] if mode < len(modes) else "UNKNOWN"
            self.interface.log(f"{self.P.CYN}{msg.format(mode=selected_mode)}{self.P.RST}")
        except ValueError:
            self.interface.log(ux("command_alerts", "truth_invalid"))
        except Exception as e:
            msg = ux("command_alerts", "truth_failure")
            self.interface.log(msg.format(error=e))
        return True

    def _cmd_use(self, parts):
        """ Direct hook into the GordonKnot to consume an item from inventory. """
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "use_usage"))
            return True
        item_name = parts[1].upper()
        gordon = getattr(self.interface.eng, "gordon", None)
        if not gordon:
            msg = ux("command_alerts", "use_no_inv")
            self.interface.log(f"{self.P.RED}{msg}{self.P.RST}")
            return True
        success, msg = gordon.consume(item_name)
        color = self.P.GRN if success else self.P.OCHRE
        self.interface.log(f"{color}{msg}{self.P.RST}")
        return True