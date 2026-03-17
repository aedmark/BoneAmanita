""" bone_commands.py """

import shlex
from typing import Dict, Callable, List, Optional

from bone_presets import BonePresets, BoneConfig
from bone_core import LoreManifest, Prisma, ux

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
            return self.eng.process_turn("LOOK", is_system=True)
        return None

    def modify_resource(self, resource: str, delta: float):
        if resource == "stamina":
            self.eng.stamina = max(0.0, self.eng.stamina + delta)
        elif resource == "atp":
            if hasattr(self.eng, "bio"):
                self.eng.bio.mito.state.atp_pool = max(0.0, self.eng.bio.mito.state.atp_pool + delta)

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
        metrics = self.eng.get_metrics()
        cmd_cfg = getattr(self.Config, "COMMANDS", None)
        return {"health": metrics.get("health", 0.0), "stamina": metrics.get("stamina", 0.0),
                "atp": metrics.get("atp", 0.0), "max_health": getattr(self.Config, "MAX_HEALTH", 100.0),
                "max_stamina": getattr(self.Config, "MAX_STAMINA", 100.0),
                "max_atp": getattr(cmd_cfg, "STATUS_MAX_ATP", 200.0) if cmd_cfg else 200.0, }

    def get_inventory(self) -> List[str]:
        if hasattr(self.eng, "gordon"):
            return getattr(self.eng.gordon, "inventory", [])
        return []

    def get_navigation_report(self) -> str:
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
        self.registry.register("/use", self._cmd_use, _cd("use"))
        self.registry.register("/hud", self._cmd_hud, _cd("hud") or "Adjusts the VSL UI depth (warm, lite, core, deep)")
        self.registry.register("/idle", self._cmd_idle, _cd("idle") or "Enters REM cycle, regenerating ATP and Stamina")
        self.registry.register("/mod", self._cmd_mod, _cd("mod") or "Engages hardwired mode chips (e.g., slash)")
        self.registry.register("/grief", self._cmd_grief, _cd("grief") or "Attends the wake for a consumed memory")
        self.registry.register("/layer", self._cmd_layer, _cd("layer") or "Manipulates the Reality Stack depth")
        self.registry.register("/inject", self._cmd_inject, _cd("inject") or "Forces payload into the EventBus")
        self.registry.register("/trauma", self._cmd_trauma, "DEV: Spikes trauma and drops health to test The Therapist.")

    def execute(self, text: str):
        if hasattr(self.interface.eng, "reality_stack"):
            stack = self.interface.eng.reality_stack
            rules = stack.get_grammar_rules()
            if not rules.get("allow_commands", True):
                msg = ux("command_alerts", "reality_lock")
                self.interface.log(f"{self.P.RED}{msg.format(depth=stack.current_depth)}{self.P.RST}", "ERR")
                return True
        if text.startswith("/"):
            return self.registry.execute(text)
        return False

    def _cmd_help(self, _parts):
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
        v = self.interface.get_vitals()
        menu_cfg = LoreManifest.get_instance(config_ref=self.interface.Config).get("ux_strings", "status_menu") or {}
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
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "mode_usage"))
            return True
        mode_name = parts[1].upper()
        if not hasattr(BonePresets, mode_name):
            msg = ux("command_alerts", "mode_unknown")
            self.interface.log(f"{self.P.RED}{msg.format(mode=mode_name)}{self.P.RST}")
            return True
        cmd_cfg = getattr(self.interface.Config, "COMMANDS", None)
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
        res = self.interface.save_state()
        cfg = getattr(self.interface.Config, "COMMANDS", None)
        error_flags = getattr(cfg, "SAVE_ERROR_FLAGS", ["Error", "Failed", "Exception"])
        if not res or any(flag in str(res) for flag in error_flags):
            msg = ux("command_alerts", "save_failed")
            self.interface.log(f"{self.P.RED}{msg.format(res=res)}{self.P.RST}")
        else:
            msg = ux("command_alerts", "save_success")
            self.interface.log(f"{self.P.GRN}{msg.format(res=res)}{self.P.RST}")
        return True

    def _cmd_inventory(self, _parts):
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
        cmd_cfg = getattr(self.interface.Config, "COMMANDS", None)
        cost = getattr(cmd_cfg, "COST_MAP", 2.0) if cmd_cfg else 2.0
        if not self.tax.levy("MAP", {"stamina": cost}):
            return True
        nav_report = self.interface.get_navigation_report()
        self.interface.log(nav_report)
        return True

    def _cmd_debug(self, _parts):
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
        msg = ux("command_alerts", "exit_halt")
        self.interface.log(f"{Prisma.RED}{msg}{Prisma.RST}", "SYS")

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
            self.interface.log(ux("command_alerts", "look_blind"))
        return True

    def _cmd_reload(self, parts):
        if len(parts) > 1:
            target = parts[1].upper()
            LoreManifest.get_instance(config_ref=self.interface.Config).flush_cache(target)
            msg = ux("command_alerts", "reload_target")
            self.interface.log(msg.format(target=target))
        else:
            LoreManifest.get_instance(config_ref=self.interface.Config).flush_cache()
            self.interface.log(ux("command_alerts", "reload_all"))
        return True

    def _cmd_truth(self, parts):
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

    def _cmd_hud(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /hud [warm|lite|core|deep]")
            return True
        mode = parts[1].upper()
        if mode == "WARM":
            self.interface.eng.mode_settings["default_ui_depth"] = "WARM"
            self.interface.log(f"{self.P.GRY}[SYSTEM] The veil falls. HUD muted.{self.P.RST}")
        elif mode == "LITE":
            self.interface.eng.mode_settings["default_ui_depth"] = "LITE"
            self.interface.eng.ui_mode = "LITE"
            self.interface.log(f"{self.P.CYN}[SYSTEM] LITE HUD engaged.{self.P.RST}")
        elif mode == "CORE":
            self.interface.eng.mode_settings["default_ui_depth"] = "CORE"
            self.interface.eng.ui_mode = "CORE"
            self.interface.log(f"{self.P.CYN}[SYSTEM] CORE HUD engaged.{self.P.RST}")
        elif mode == "DEEP":
            self.interface.eng.mode_settings["default_ui_depth"] = "DEEP"
            self.interface.eng.ui_mode = "DEEP"
            self.interface.log(f"{self.P.VIOLET}[SYSTEM] DEEP HUD engaged. Full lattice visible.{self.P.RST}")
        else:
            self.interface.log(f"{self.P.RED}Unknown HUD mode: {mode}{self.P.RST}")
        return True

    def _cmd_idle(self, _parts):
        self.interface.modify_resource("stamina", 15.0)
        self.interface.modify_resource("atp", 20.0)
        dream_log = ""
        if hasattr(self.interface.eng, "mind") and hasattr(self.interface.eng.mind, "dreamer"):
            snapshot = self.interface.eng.soul.to_dict() if hasattr(self.interface.eng, "soul") else {}
            bio_state = self.interface.eng.bio.endo.get_state() if hasattr(self.interface.eng, "bio") and hasattr(
                self.interface.eng.bio, "endo") else {}
            dream_text, effects = self.interface.eng.mind.dreamer.enter_rem_cycle(snapshot, bio_state)
            if dream_text:
                dream_log = f"\n\n{self.P.VIOLET}☁️ {dream_text}{self.P.RST}"
                if effects and effects.get("glimmers"):
                    g_yield = effects["glimmers"]
                    if hasattr(self.interface.eng, "shared_lattice"):
                        self.interface.eng.shared_lattice.shared.g_pool += g_yield
                    elif hasattr(self.interface.eng, "phys"):
                        self.interface.eng.phys.G = getattr(self.interface.eng.phys, "G", 0) + g_yield
                    dream_log += f"\n{self.P.MAG}✨ The dream yielded a Glimmer (+{g_yield} G_pool).{self.P.RST}"
        self.interface.log(
            f"{self.P.CYN}[SYSTEM] Engine idling. REM cycle initiated. ATP regenerating.{self.P.RST}{dream_log}")
        return True

    def _cmd_mod(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /mod [slash|...]")
            return True
        mod = parts[1].upper()
        if mod == "SLASH":
            self.interface.log(f"{self.P.INDIGO}SLASH Mod Chip engaged. Dev Team online.{self.P.RST}")
            if hasattr(self.interface.eng, "council") and hasattr(self.interface.eng.council, "slash_council"):
                self.interface.eng.council.slash_council.active = True
        return True

    def _cmd_grief(self, _parts):
        if hasattr(self.interface.eng, "grief"):
            shared_lattice = getattr(self.interface.eng, "shared_lattice", None)
            wake_msg = self.interface.eng.grief.attend_wake(shared_lattice, getattr(self.interface.eng, "phys", None))
            self.interface.log(wake_msg)
        else:
            self.interface.log(
                f"{self.P.GRY}(We stand in silence for the lost memory. No protocol active.){self.P.RST}")
        return True

    def _cmd_layer(self, parts):
        if len(parts) >= 2:
            sub = parts[1].lower()
            if sub == "push" and len(parts) > 2:
                if self.interface.eng.reality_stack.push_layer(int(parts[2])):
                    self.interface.log(ux("main_strings", "layer_pushed").format(layer=parts[2]))
            elif sub == "pop":
                self.interface.eng.reality_stack.pop_layer()
                self.interface.log(ux("main_strings", "layer_popped"))
            elif sub == "debug":
                self.interface.eng.reality_stack.push_layer(RealityLayer.DEBUG)
                self.interface.log(ux("main_strings", "debug_engaged"))
        else:
            self.interface.log(
                ux("main_strings", "current_layer").format(layer=self.interface.eng.reality_stack.current_depth))
        return True

    def _cmd_inject(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /inject <payload>")
            return True
        payload = " ".join(parts[1:])
        self.interface.log(payload, "INJECT")
        self.interface.log(ux("main_strings", "injected").format(payload=payload))
        return True

    def _cmd_trauma(self, _parts):
        self.interface.eng.health = 20.0
        self.interface.eng.trauma_accum["SYNTHETIC_CRISIS"] = 50.0
        if hasattr(self.interface.eng, "events"):
            self.interface.eng.events.publish("TRAUMA_EVENT", {"magnitude": 50.0})
        self.interface.log(f"{self.P.RED}[DEV] Health dropped to 20. Trauma spiked to 50. Proceed to next turn.{self.P.RST}", "SYS")
        return True