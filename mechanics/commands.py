"""mechanics/commands.py"""

import shlex
import time
from typing import Callable, Dict, List, Optional

from constants import RealityLayer
from core import LoreManifest
from presets import BoneConfig, BonePresets
from struts import safe_get, safe_set, ux, ux_format


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
        vitals = self.get_vitals()
        if resource == "stamina":
            self.eng.stamina = max(0.0, min(self.eng.stamina + delta, vitals.get("max_stamina", 100.0)))
        elif resource == "atp" and hasattr(self.eng, "bio"):
            state = self.eng.bio.mito.state
            state.atp_pool = max(0.0, min(state.atp_pool + delta, vitals.get("max_atp", 200.0)))

    def get_resource(self, resource: str) -> float:
        return self.get_vitals().get(resource, 0.0)

    def save_state(self) -> str:
        mind = getattr(self.eng, "mind", None)
        if not mind or not getattr(mind, "mem", None):
            return ux("command_state", "mem_error")
        loc = ux("command_state", "default_loc")
        last_out = ux("command_state", "default_out")
        if cortex := getattr(self.eng, "cortex", None):
            state = cortex.gather_state({"physics": getattr(cortex, "last_physics", {})})
            orbit = state.get("world", {}).get("orbit")
            loc = orbit[0] if orbit else ux("command_state", "default_orbit")
            if cortex.dialogue_buffer:
                last_out = cortex.dialogue_buffer[-1]
        bio = getattr(self.eng, "bio", None)
        bio_dict = bio.to_dict() if hasattr(bio, "to_dict") else {}
        mito_traits = bio_dict.get("mito", {})
        immune = getattr(bio, "immune", None)
        antibodies = list(immune.active_antibodies) if immune and hasattr(immune, "active_antibodies") else None
        continuity_packet = {"location": loc, "last_output": last_out, "inventory": self.get_inventory()}
        village = getattr(self.eng, "village", None)
        nav = getattr(village, "navigator", None)
        atlas_data = nav.export_atlas() if nav else None
        payload = {"health": self.eng.health, "stamina": self.eng.stamina,
                   "trauma_accum": getattr(self.eng, "trauma_accum", {}), "mitochondria_traits": mito_traits,
                   "antibodies": antibodies,
                   "soul_data": self.eng.soul.to_dict() if hasattr(self.eng, "soul") else None,
                   "continuity": continuity_packet, "world_atlas": atlas_data,"mutations": getattr(self.eng, "mutations", {}), "joy_history": getattr(self.eng, "joy_history", [])}
        try:
            return self.eng.mind.mem.save(**payload)
        except Exception as e:
            self.log(f"{self.P.RED}Save failed at memory core: {e}{self.P.RST}", "ERR")
            return ux("command_state", "unreachable_error")

    def get_vitals(self) -> Dict[str, float]:
        from struts import safe_get
        metrics = self.eng.get_metrics()
        cmd_cfg = safe_get(self.Config, "COMMANDS", {})
        return {"health": metrics.get("health", 0.0), "stamina": metrics.get("stamina", 0.0),
                "atp": metrics.get("atp", 0.0), "max_health": float(safe_get(self.Config, "MAX_HEALTH", 100.0)),
                "max_stamina": float(safe_get(self.Config, "MAX_STAMINA", 100.0)),
                "max_atp": float(safe_get(cmd_cfg, "STATUS_MAX_ATP", 200.0)), }

    def get_inventory(self) -> List[str]:
        village = getattr(self.eng, "village", None)
        gordon = getattr(village, "gordon", None) if village else None
        return getattr(gordon, "inventory", [])

    def get_navigation_report(self) -> str:
        village = getattr(self.eng, "village", None)
        nav = getattr(village, "navigator", None) if village else None
        phys = getattr(self.eng, "phys", None)
        observer = getattr(phys, "observer", None) if phys else None
        packet = getattr(observer, "last_physics_packet", None)
        if nav and packet:
            return nav.report_position(packet)
        return ux("command_state", "nav_offline" if not nav else "nav_unresponsive")

    def get_soul_status(self) -> Optional[str]:
        soul = getattr(self.eng, "soul", None)
        if soul:
            return soul.get_soul_state()
        return None

class ResourceTax:
    def __init__(self, state: CommandStateInterface):
        self.state = state

    def levy(self, _context: str, costs: Dict[str, float]) -> bool:
        limits = {"stamina": "exhausted", "atp": "starving"}
        for res, cost in costs.items():
            if cost > self.state.get_resource(res):
                limit_key = limits.get(res, "depleted")
                msg = ux_format("resource_tax", limit_key, default=f"{res} limit reached: {{cost}}", cost=cost)
                self.state.log(f"{self.state.P.RED}{msg}{self.state.P.RST}")
                return False
        for res, cost in costs.items():
            if cost > 0:
                self.state.modify_resource(res, -cost)
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
        from struts import ux_format
        clean_text = text.strip()
        try:
            parts = shlex.split(clean_text)
        except ValueError:
            parts = clean_text.split()
        if not parts:
            return True
        cmd = parts[0].lower()
        if func := self.commands.get(cmd):
            return func(parts)
        msg = ux_format("command_registry", "unknown_command", default="Unknown command: {cmd}", cmd=cmd)
        self.state.log(msg, "CMD")
        return True

class CommandProcessor:
    DEFAULT_DESCS = {
        "hud": "Adjusts the VSL UI depth (warm, lite, core, deep)",
        "idle": "Enters REM cycle, regenerating ATP and Stamina",
        "mode": "Engages hardwired mode chips (e.g., slash)",
        "grief": "Attends the wake for a consumed memory",
        "hallucinate": "Disengages the thermal lock for a forced lateral paradigm shift",
        "layer": "Manipulates the Reality Stack depth",
        "inject": "Forces payload into the EventBus",
        "trauma": "DEV: Spikes trauma and drops health to test The Therapist.",
        "journal": "Generates a narrative diary entry of the session so far",
        "shuffle": "Explicit intent [ !s ]: The Jester's Gambit. Breaks loops, resets drag, lateral shift."
    }

    def __init__(self, engine, prisma_ref, _lexicon_ref=None, config_ref=None, _cartographer_ref=None):
        from struts import safe_get
        real_config = config_ref if config_ref else BoneConfig
        self.interface = CommandStateInterface(engine, prisma_ref, real_config)
        self.tax = ResourceTax(self.interface)
        self.registry = CommandRegistry(self.interface)
        self.P = prisma_ref
        self.cmd_cfg = safe_get(self.interface.Config, "COMMANDS", {})
        for attr in dir(self):
            if attr.startswith("_cmd_"):
                name = attr[5:]
                desc = ux("command_descriptions", name) or self.DEFAULT_DESCS.get(name, "")
                self.registry.register(f"/{name}", getattr(self, attr), desc)

    def execute(self, text: str):
        if text.strip().lower() == "[zen]":
            text = "/zen"
        if not text.startswith("/"):
            return False
        if hasattr(self.interface.eng, "reality_stack"):
            stack = self.interface.eng.reality_stack
            boot_mode = getattr(self.interface.eng, "boot_mode", "ADVENTURE")
            rules = RealityLayer.get_rules(stack.current_depth, boot_mode=boot_mode)
            if not rules.get("allow_commands", True):
                msg = ux("command_alerts", "reality_lock")
                self.interface.log(f"{self.P.RED}{msg.format(depth=stack.current_depth)}{self.P.RST}", "ERR")
                return True
        return self.registry.execute(text)

    def _cmd_help(self, _parts):
        header = ux("help_menu", "header")
        phase_pfx = ux("help_menu", "phase_prefix")
        def_phase = ux("help_menu", "default_phase")
        footer = ux("help_menu", "footer")
        uncat = ux("help_menu", "uncategorized")
        structure = ux("help_menu", "structure", {})
        lines = [
            f"\n{self.P.CYN}{header}{self.P.RST}",
            f"{self.P.GRY}{phase_pfx}{self.interface.get_soul_status() or def_phase}{self.P.RST}\n",
        ]
        cmd_to_cat = {cmd: cat for cat, cmds in structure.items() for cmd in cmds}
        buckets = {cat: [] for cat in list(structure.keys()) + [uncat]}
        for cmd, desc in self.registry.help_text.items():
            buckets[cmd_to_cat.get(cmd, uncat)].append((cmd, desc))
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
        menu_cfg = LoreManifest.get_instance(config_ref=self.interface.Config).get(
            "ux_strings", "status_menu") or {}
        b_f, b_e = menu_cfg.get("bar_filled", "█"), menu_cfg.get("bar_empty", "░")

        def render(lbl_key, default_lbl, curr, max_v, color):
            lbl = menu_cfg.get(lbl_key, default_lbl)
            ratio = curr / max(1.0, max_v)
            filled = int(max(0.0, min(1.0, ratio)) * 10)
            return f"{lbl}{color}{b_f * filled}{b_e * (10 - filled)}{self.P.RST} {curr:.0f}"

        self.interface.log("\n".join([
            render("health_label", "Health:  ", v['health'], v['max_health'], self.P.RED),
            render("stamina_label", "Stamina: ", v['stamina'], v['max_stamina'], self.P.GRN),
            render("energy_label", "Energy:  ", v['atp'], v['max_atp'], self.P.YEL)
        ]))
        return True

    def _cmd_report(self, _parts):
        try:
            telemetry = getattr(self.interface.eng, "telemetry", None)
            if not telemetry:
                self.interface.log(f"{self.P.RED}Telemetry module offline. Cannot generate report.{self.P.RST}")
                return True
            report_text = telemetry.get_report()
            summary_text = telemetry.generate_session_summary()
            self.interface.log(f"{self.P.CYN}=== SYSTEM REPORT ==={self.P.RST}\n{report_text}")
            self.interface.log(f"{self.P.CYN}=== SESSION SUMMARY ==={self.P.RST}\n{summary_text}")
        except Exception as e:
            self.interface.log(f"{self.P.RED}Failed to generate report: {e}{self.P.RST}")
        return True

    def _cmd_diag(self, _parts):
        try:
            telemetry = getattr(self.interface.eng, "telemetry", None)
            if not telemetry:
                self.interface.log(f"{self.P.RED}Telemetry module offline. Cannot run diagnostics.{self.P.RST}")
                return True
            fatal = telemetry.get_last_fatal_error()
            thoughts = telemetry.get_last_thoughts()
            self.interface.log(f"{self.P.RED}=== LAST FATAL ERROR ==={self.P.RST}\n{fatal}")
            self.interface.log(f"{self.P.YEL}=== LAST THOUGHTS ==={self.P.RST}\n{thoughts}")
        except Exception as e:
            self.interface.log(f"{self.P.RED}Diag failure: {e}{self.P.RST}")
        return True

    def _cmd_mode(self, parts):
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "mode_usage"))
            return True
        mode_name = parts[1].upper()
        if not hasattr(BonePresets, mode_name):
            msg = ux_format("command_alerts", "mode_unknown", default="Unknown mode: {mode}", mode=mode_name)
            self.interface.log(f"{self.P.RED}{msg}{self.P.RST}")
            return True
        cost = float(safe_get(self.cmd_cfg, "COST_MODE", 10.0))
        if self.tax.levy("MODE_SWITCH", {"stamina": cost}):
            preset = getattr(BonePresets, mode_name)
            logs = self.interface.Config.load_preset(preset)
            for log in logs:
                self.interface.log(log)
            phys = getattr(self.interface.eng, "phys", None)
            observer = getattr(phys, "observer", None) if phys else None
            if phys_packet := getattr(observer, "last_physics_packet", None):
                self.interface.Config.reconcile_state(phys_packet)
                msg = ux_format("command_alerts", "mode_reconciled", default="Reconciled state to {mode}",
                                mode=mode_name)
                self.interface.log(f"{self.P.CYN}{msg}{self.P.RST}")
            msg = ux_format("command_alerts", "mode_switched", default="Switched to {mode}", mode=mode_name)
            self.interface.log(msg)
        return True

    def _cmd_save(self, _parts):
        cortex = getattr(self.interface.eng, "cortex", None)
        if cortex and hasattr(cortex, "dialogue_buffer") and cortex.dialogue_buffer:
            last_response = cortex.dialogue_buffer[-1]
            from mechanics.projector import anchor_to_bedrock
            anchor_to_bedrock(self.interface.eng, last_response)

        res = self.interface.save_state()
        error_flags = safe_get(self.cmd_cfg, "SAVE_ERROR_FLAGS", ("Error", "Failed", "Exception"))
        if not res or any(flag in str(res) for flag in error_flags):
            msg = ux_format("command_alerts", "save_failed", default="Save failed: {res}", res=res)
            self.interface.log(f"{self.P.RED}{msg}{self.P.RST}")
        else:
            msg = ux_format("command_alerts", "save_success", default="State saved: {res}", res=res)
            self.interface.log(f"{self.P.GRN}{msg}{self.P.RST}")
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
        cost = float(safe_get(self.cmd_cfg, "COST_MAP", 2.0))
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
        msg = ux("command_alerts", "exit_halt") or "System powering down. Rest well."
        self.interface.log(f"{self.P.VIOLET}{msg}{self.P.RST}", "SYS")
        return False

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
            msg = ux_format("command_alerts", "reload_target", default="Reloaded {target}", target=target)
            self.interface.log(msg)
        else:
            LoreManifest.get_instance(config_ref=self.interface.Config).flush_cache()
            self.interface.log(ux("command_alerts", "reload_all") or "All caches reloaded.")
        return True

    def _cmd_truth(self, parts):
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "truth_usage") or "Usage: /truth [0-3]")
            return True
        try:
            mode = int(parts[1])
            if mode not in (0, 1, 2, 3):
                self.interface.log(ux("command_alerts", "truth_invalid") or "Invalid truth mode.")
                return True
            self.interface.eng.ambiguity_dial = mode
            modes = ux("command_alerts", "truth_modes", ("BOARDROOM", "WORKSHOP", "RED TEAM", "PALIMPSEST"))
            mode_name = modes[mode] if mode < len(modes) else str(mode)
            msg = ux_format('command_alerts', 'truth_dial_set', default="Truth set to {mode}", mode=mode_name)
            self.interface.log(f"{self.P.CYN}{msg}{self.P.RST}")
        except ValueError:
            self.interface.log(ux("command_alerts", "truth_invalid") or "Invalid truth mode.")
        except Exception as e:
            msg = ux_format("command_alerts", "truth_failure", default="Truth failed: {error}", error=e)
            self.interface.log(msg)
        return True

    def _cmd_use(self, parts):
        if len(parts) < 2:
            self.interface.log(ux("command_alerts", "use_usage"))
            return True
        item_name = " ".join(parts[1:]).upper()
        village = getattr(self.interface.eng, "village", None)
        gordon = getattr(village, "gordon", None)
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
        hud_configs = {
            "WARM": f"{self.P.GRY}The veil falls. HUD muted.{self.P.RST}",
            "LITE": f"{self.P.CYN}LITE HUD engaged.{self.P.RST}",
            "CORE": f"{self.P.CYN}CORE HUD engaged.{self.P.RST}",
            "DEEP": f"{self.P.VIOLET}DEEP HUD engaged. Full lattice visible.{self.P.RST}",
        }
        if mode in hud_configs:
            self.interface.eng.mode_settings["default_ui_depth"] = mode
            self.interface.eng.ui_mode = mode
            self.interface.log(hud_configs[mode])
        else:
            self.interface.log(f"{self.P.RED}Unknown HUD mode: {mode}{self.P.RST}")
        return True

    def _cmd_idle(self, _parts):
        vitals = self.interface.get_vitals()
        if vitals["stamina"] >= vitals["max_stamina"] and vitals["atp"] >= vitals["max_atp"]:
            if hasattr(self.interface.eng, "phys"):
                drag = getattr(self.interface.eng.phys, "narrative_drag", 0.0)
                self.interface.eng.phys.narrative_drag = min(10.0, drag + 1.0)
                self.interface.log(f"{self.P.GRY}[SYSTEM] The host is fully rested. Oversleeping induces lethargy. (Drag +1.0){self.P.RST}")
            return True
        self.interface.modify_resource("stamina", 15.0)
        self.interface.modify_resource("atp", 20.0)
        dream_log = ""
        mind = getattr(self.interface.eng, "mind", None)
        dreamer = getattr(mind, "dreamer", None)
        if dreamer:
            soul = getattr(self.interface.eng, "soul", None)
            bio = getattr(self.interface.eng, "bio", None)
            snapshot = soul.to_dict() if soul else {}
            bio_state = {}
            if bio:
                bio_state["chem"] = bio.endo.get_state() if hasattr(bio, "endo") else {}
                if hasattr(bio, "mito"):
                    bio_state["mito"] = {"atp": bio.mito.state.atp_pool, "ros": bio.mito.state.ros_buildup}
            dream_text, effects = dreamer.enter_rem_cycle(snapshot, bio_state)
            if dream_text:
                dream_log = f"\n\n{self.P.VIOLET}☁️ {dream_text}{self.P.RST}"
                if effects and effects.get("glimmers"):
                    g_yield = effects["glimmers"]
                    lattice = getattr(self.interface.eng, "shared_lattice", None)
                    if shared := getattr(lattice, "shared", None):
                        shared.g_pool += g_yield
                    elif phys := getattr(self.interface.eng, "phys", None):
                        phys.G = getattr(phys, "G", 0) + g_yield
                    dream_log += f"\n{self.P.MAG}The dream yielded a Glimmer (+{g_yield} G_pool).{self.P.RST}"
        self.interface.log(
            f"{self.P.CYN}Engine idling. REM cycle initiated. ATP regenerating.{self.P.RST}{dream_log}")
        return True

    def _cmd_sleep(self, parts):
        return self._cmd_idle(parts)

    def _cmd_rest(self, _parts):
        cortex = getattr(self.interface.eng, "cortex", None)
        if cortex:
            cortex.purge_context()
        for p_attr in ("active_physics", "phys"):
            p_obj = getattr(self.interface.eng, p_attr, None)
            if p_obj is not None:
                safe_set(p_obj, "narrative_drag", 0.0)
        vitals = self.interface.get_vitals()
        self.interface.modify_resource("stamina", vitals.get("max_stamina", 100.0))
        self.interface.modify_resource("atp", vitals.get("max_atp", 100.0))
        if state := getattr(self.interface.eng, "_mito_state", None):
            state.ros_buildup = 0.0
        if hasattr(self.interface.eng, "trauma_accum"):
            self.interface.eng.trauma_accum.clear()
        msg = "Context severed. Friction Dropped. Stamina restored. Trauma purged. The mind is clear."
        self.interface.log(f"{self.P.CYN}{msg}{self.P.RST}", "SYS")
        return True

    def _cmd_flush(self, parts):
        return self._cmd_rest(parts)

    def _cmd_zen(self, parts):
        return self._cmd_rest(parts)

    def _cmd_grief(self, _parts):
        grief_ref = getattr(self.interface.eng, "grief", None) or getattr(getattr(self.interface.eng, "village", None), "grief", None)
        if grief_ref:
            shared_lattice = getattr(self.interface.eng, "shared_lattice", None)
            wake_msg = grief_ref.attend_wake(
                shared_lattice, getattr(self.interface.eng, "phys", None))
            self.interface.log(wake_msg)
        else:
            self.interface.log(
                f"{self.P.GRY}We stand in silence for the lost memory. No protocol active.{self.P.RST}")
        return True

    def _cmd_layer(self, parts):
        stack = getattr(self.interface.eng, "reality_stack", None)
        if not stack:
            return True
        if len(parts) < 2:
            self.interface.log(ux_format("main_strings", "current_layer", default="Layer: {layer}", layer=stack.current_depth))
            return True
        sub = parts[1].lower()
        if sub == "push" and len(parts) > 2:
            try:
                layer_val = int(parts[2])
            except ValueError:
                self.interface.log(f"{self.P.RED}Invalid layer index. Must be an integer.{self.P.RST}")
                return True
            try:
                stack.push_layer(layer_val)
                self.interface.log(ux_format("main_strings", "layer_pushed", default="Pushed layer {layer}", layer=layer_val))
            except ValueError as e:
                self.interface.log(f"{self.P.RED}{str(e)}{self.P.RST}")
        elif sub == "pop":
            stack.pop_layer()
            self.interface.log(ux("main_strings", "layer_popped"))
        elif sub == "debug":
            stack.push_layer(RealityLayer.DEBUG)
            self.interface.log(ux("main_strings", "debug_engaged"))
        return True

    def _cmd_inject(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /inject <payload>")
            return True
        payload = " ".join(parts[1:])
        self.interface.log(payload, "INJECT")
        self.interface.log(ux_format("main_strings", "injected", default="Injected: {payload}", payload=payload))
        return True

    def _cmd_trauma(self, _parts):
        self.interface.eng.health = 20.0
        if not hasattr(self.interface.eng, "trauma_accum"):
            self.interface.eng.trauma_accum = {}
        self.interface.eng.trauma_accum["SYNTHETIC_CRISIS"] = 50.0
        if hasattr(self.interface.eng, "events"):
            self.interface.eng.events.publish("TRAUMA_EVENT", {"magnitude": 50.0})
        self.interface.log(
            f"{self.P.RED}Health dropped to 20. Trauma spiked to 50. Proceed to next turn.{self.P.RST}",
            "SYS", )
        return True

    def _execute_substrate_write(self, file_name: str, content: str):
        substrate = getattr(self.interface.eng, "substrate", None)
        if substrate is None:
            from mechanics.tools import TheSubstrate
            substrate = TheSubstrate(getattr(self.interface.eng, "events", None))
            self.interface.eng.substrate = substrate
        substrate.queue_write(file_name, self.P.strip(content))
        stamina = self.interface.get_resource("stamina")
        write_logs, cost = substrate.execute_writes(stamina)
        self.interface.modify_resource("stamina", -cost)
        for log in write_logs:
            self.interface.log(log)

    def _cmd_journal(self, _parts):
        cost = float(safe_get(self.cmd_cfg, "COST_JOURNAL", 15.0))
        if not self.tax.levy("JOURNAL", {"atp": cost}):
            return True
        self.interface.log(f"{self.P.CYN}📖 Compiling narrative journal...{self.P.RST}")
        cortex = getattr(self.interface.eng, "cortex", None)
        llm = getattr(cortex, "llm", None)
        if not llm or not cortex.dialogue_buffer:
            self.interface.log(f"{self.P.RED}Error: Cortex LLM unavailable or memory buffer is empty.{self.P.RST}")
            return True
        try:
            history = "\n".join(cortex.dialogue_buffer)
            prompt = ("SYSTEM_INSTRUCTION: You are the archivist of a surreal journey. "
                      "Read the following recent dialogue history and write a whimsical, reflective, first-person diary entry (1-5 paragraphs) "
                      "summarizing the events and emotional undercurrents so far. Focus on the mood, the strange tension, and the overarching theme. "
                      "DO NOT use AI-isms. Write like a traveler recording a dream.\n\n"
                      f"DIALOGUE HISTORY:\n{history}")
            journal_entry = llm.generate(prompt, {"temperature": 0.85, "max_tokens": 300})
            self.interface.log(f"\n{self.P.WHT}{journal_entry}{self.P.RST}\n")
            file_name = f"journal_entry_{int(time.time())}.txt"
            self._execute_substrate_write(file_name, journal_entry)
        except Exception as e:
            self.interface.log(f"{self.P.RED}Journal generation failed: {e}{self.P.RST}")
        return True

    def _cmd_hallucinate(self, _parts):
        cost = float(safe_get(self.cmd_cfg, "COST_HALLUCINATE", 25.0))
        if not self.tax.levy("HALLUCINATE", {"atp": cost}):
            return True
        for p_attr in ("active_physics", "phys"):
            p_obj = getattr(self.interface.eng, p_attr, None)
            if p_obj is not None:
                safe_set(p_obj, "mu", min(1.0, float(safe_get(p_obj, "mu", 0.0)) + 0.8))
                safe_set(p_obj, "kappa", max(0.5, float(safe_get(p_obj, "kappa", 0.0))))
        cortex = getattr(self.interface.eng, "cortex", None)
        if cortex and hasattr(cortex, "dialogue_buffer"):
            cortex.dialogue_buffer.append(
                "System: [!s] THERMAL LOCK OVERRIDE. The user has explicitly invoked a hallucination. "
                "Abandon linear cohesion. Connect two wildly unrelated concepts from the active memory graph. "
                "Maximize structural polyphony. Generate a fever dream of lateral paradigm shifts. Let The Jester speak."
            )
        self.interface.log(f"{self.P.MAG}[VOID] Thermal lock disengaged. Tension spiked. The next turn will be a forced hallucination.{self.P.RST}", "SYS")
        return True

    def _cmd_shuffle(self, _parts):
        """The emergency release valve. Burns ATP to physically reset structural/narrative loops."""
        cost = float(safe_get(self.cmd_cfg, "COST_SHUFFLE", 5.0))
        if not self.tax.levy("SHUFFLE", {"atp": cost}):
            return True
        for p_attr in ("active_physics", "phys"):
            p_obj = getattr(self.interface.eng, p_attr, None)
            if p_obj is not None:
                safe_set(p_obj, "narrative_drag", 0.0)
        self.interface.log(
            f"{self.P.VIOLET}[ !s ] THE SHUFFLE: Lateral shift initiated.{self.P.RST}")
        self.interface.log(
            f"{self.P.GRY}Control illusion shattered. Narrative drag reset to 0. (Cost: {cost} ATP){self.P.RST}")
        return True
