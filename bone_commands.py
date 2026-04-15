"""bone_commands.py"""

import time, shlex
from typing import Dict, Callable, List, Optional
from bone_presets import BonePresets, BoneConfig
from bone_core import LoreManifest, Prisma, ux
from bone_types import RealityLayer


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

        def clamp(val, max_val):
            return max(0.0, min(val, max_val))

        if resource == "stamina":
            self.eng.stamina = clamp(self.eng.stamina + delta,
                                     vitals.get("max_stamina", 100.0))
        elif resource == "atp" and hasattr(self.eng, "bio"):
            state = self.eng.bio.mito.state
            state.atp_pool = clamp(state.atp_pool + delta, vitals.get("max_atp", 200.0))

    def get_resource(self, resource: str) -> float:
        return self.get_vitals().get(resource, 0.0)

    def save_state(self) -> str:
        mind = getattr(self.eng, "mind", None)
        if not mind or not getattr(mind, "mem", None):
            return ux("command_state", "mem_error")
        loc = ux("command_state", "default_loc")
        last_out = ux("command_state", "default_out")
        if cortex := getattr(self.eng, "cortex", None):
            state = cortex.gather_state(getattr(cortex, "last_physics", {}))
            loc = state.get("world", {}).get("orbit",
                                             [ux("command_state", "default_orbit")])[0]
            if cortex.dialogue_buffer:
                last_out = cortex.dialogue_buffer[-1]
        bio = getattr(self.eng, "bio", None)
        mito_state = getattr(getattr(bio, "mito", None), "state", None)
        immune = getattr(bio, "immune", None)
        continuity_packet = {
            "location": loc,
            "last_output": last_out,
            "inventory": self.get_inventory(),
        }
        nav = getattr(self.eng, "navigator", None)
        atlas_data = nav.export_atlas() if nav else None
        mito_traits = mito_state.__dict__ if mito_state else {}
        antibodies = list(immune.active_antibodies) if immune else None
        payload = {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "mutations": {},
            "trauma_accum": getattr(self.eng, "trauma_accum", {}),
            "joy_history": [],
            "mitochondria_traits": mito_traits,
            "antibodies": antibodies,
            "soul_data": self.eng.soul.to_dict() if hasattr(self.eng, "soul") else None,
            "continuity": continuity_packet,
            "world_atlas": atlas_data,
            "village_data": None
        }
        try:
            return self.eng.mind.mem.save(**payload)
        except Exception as e:
            self.log(f"{self.P.RED}Save failed at memory core: {e}{self.P.RST}", "ERR")
            return ux("command_state", "unreachable_error")

    def get_vitals(self) -> Dict[str, float]:
        metrics = self.eng.get_metrics()
        cmd_cfg = getattr(self.Config, "COMMANDS", None)
        return {
            "health": metrics.get("health", 0.0),
            "stamina": metrics.get("stamina", 0.0),
            "atp": metrics.get("atp", 0.0),
            "max_health": getattr(self.Config, "MAX_HEALTH", 100.0),
            "max_stamina": getattr(self.Config, "MAX_STAMINA", 100.0),
            "max_atp": getattr(cmd_cfg, "STATUS_MAX_ATP", 200.0),
        }

    def get_inventory(self) -> List[str]:
        return getattr(getattr(self.eng, "gordon", None), "inventory", [])

    def get_navigation_report(self) -> str:
        nav = getattr(self.eng, "navigator", None)
        observer = getattr(getattr(self.eng, "phys", None), "observer", None)
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
        for res, limit_key in limits.items():
            if (cost := costs.get(res, 0.0)) > self.state.get_resource(res):
                msg = ux("resource_tax", limit_key).format(cost=cost)
                self.state.log(f"{self.state.P.RED}{msg}{self.state.P.RST}")
                return False
        for res in limits:
            if (cost := costs.get(res, 0.0)) > 0:
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
        try:
            parts = shlex.split(text)
        except ValueError:
            self.state.log(ux("command_registry", "syntax_error"), "CMD")
            return True
        cmd = parts[0].lower()
        if func := self.commands.get(cmd):
            return func(parts)
        self.state.log(ux("command_registry", "unknown_command").format(cmd=cmd), "CMD")
        return True


class CommandProcessor:

    DEFAULT_DESCS = {
        "hud":
        "Adjusts the VSL UI depth (warm, lite, core, deep)",
        "idle":
        "Enters REM cycle, regenerating ATP and Stamina",
        "mod":
        "Engages hardwired mode chips (e.g., slash)",
        "grief":
        "Attends the wake for a consumed memory",
        "layer":
        "Manipulates the Reality Stack depth",
        "inject":
        "Forces payload into the EventBus",
        "trauma":
        "DEV: Spikes trauma and drops health to test The Therapist.",
        "podcast":
        "Assembles the Parliament to generate a podcast script",
        "journal":
        "Generates a narrative diary entry of the session so far",
        "shuffle":
        "Explicit intent [ !s ]: The Jester's Gambit. Breaks loops, resets drag, lateral shift."
    }

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

        for attr in dir(self):
            if attr.startswith("_cmd_"):
                name = attr[5:]
                desc = ux("command_descriptions", name) or self.DEFAULT_DESCS.get(
                    name, "")
                self.registry.register(f"/{name}", getattr(self, attr), desc)

    def execute(self, text: str):
        if not text.startswith("/"):
            return False
        if hasattr(self.interface.eng, "reality_stack"):
            stack = self.interface.eng.reality_stack
            rules = stack.get_grammar_rules()
            if not rules.get("allow_commands", True):
                msg = ux("command_alerts", "reality_lock")
                self.interface.log(
                    f"{self.P.RED}{msg.format(depth=stack.current_depth)}{self.P.RST}",
                    "ERR")
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
        if not hasattr(self, "_cmd_to_cat_cache"):
            self._cmd_to_cat_cache = {
                cmd: cat
                for cat, cmds in structure.items()
                for cmd in cmds
            }
        buckets = {cat: [] for cat in list(structure.keys()) + [uncat]}
        for cmd, desc in self.registry.help_text.items():
            buckets[self._cmd_to_cat_cache.get(cmd, uncat)].append((cmd, desc))
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
            render("health_label", "Health:  ", v['health'], v['max_health'],
                   self.P.RED),
            render("stamina_label", "Stamina: ", v['stamina'], v['max_stamina'],
                   self.P.GRN),
            render("energy_label", "Energy:  ", v['atp'], v['max_atp'], self.P.YEL)
        ]))
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
        cost = getattr(cmd_cfg, "COST_MODE", 10.0)
        if self.tax.levy("MODE_SWITCH", {"stamina": cost}):
            preset = getattr(BonePresets, mode_name)
            logs = self.interface.Config.load_preset(preset)
            for log in logs:
                self.interface.log(log)
            observer = getattr(getattr(self.interface.eng, "phys", None), "observer",
                               None)
            if phys_packet := getattr(observer, "last_physics_packet", None):
                self.interface.Config.reconcile_state(phys_packet)
                msg = ux("command_alerts", "mode_reconciled")
                self.interface.log(
                    f"{self.P.CYN}{msg.format(mode=mode_name)}{self.P.RST}")
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
        self.interface.log(
            f"{P.GRY}   ({len(items)}/{self.interface.Config.INVENTORY.MAX_SLOTS} {slots_str}){P.RST}"
        )
        return True

    def _cmd_map(self, _parts):
        cmd_cfg = getattr(self.interface.Config, "COMMANDS", None)
        cost = getattr(cmd_cfg, "COST_MAP", 2.0)
        if not self.tax.levy("MAP", {"stamina": cost}):
            return True
        nav_report = self.interface.get_navigation_report()
        self.interface.log(nav_report)
        return True

    def _cmd_debug(self, _parts):
        self.interface.Config.VERBOSE_LOGGING = (
            not self.interface.Config.VERBOSE_LOGGING)
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
            LoreManifest.get_instance(
                config_ref=self.interface.Config).flush_cache(target)
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
        try:
            mode = int(parts[1])
            if mode not in (0, 1, 2, 3):
                self.interface.log(ux("command_alerts", "truth_invalid"))
                return True

            reporter = getattr(getattr(self.interface.eng, "orchestrator", None),
                               "reporter", None)
            if not reporter:
                self.interface.log(ux("command_alerts", "truth_no_reporter"))
                return True
            if not hasattr(getattr(reporter, "renderer", None), "dial_setting"):
                from bone_gui import TruthRenderer
                self.interface.log(
                    f"{self.P.YEL}{ux('command_alerts', 'truth_transplant')}{self.P.RST}"
                )
                reporter.renderer = reporter.renderers.setdefault(
                    "STANDARD", TruthRenderer(self.interface.eng))
            reporter.renderer.dial_setting = mode
            modes = ux("command_alerts", "truth_modes",
                       ["BOARDROOM", "WORKSHOP", "RED TEAM", "PALIMPSEST"])
            self.interface.log(
                f"{self.P.CYN}{ux('command_alerts', 'truth_dial_set').format(mode=modes[mode])}{self.P.RST}"
            )
        except ValueError:
            self.interface.log(ux("command_alerts", "truth_invalid"))
        except Exception as e:
            self.interface.log(ux("command_alerts", "truth_failure").format(error=e))
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
        hud_configs = {
            "WARM":
            f"{self.P.GRY}[SYSTEM] The veil falls. HUD muted.{self.P.RST}",
            "LITE":
            f"{self.P.CYN}[SYSTEM] LITE HUD engaged.{self.P.RST}",
            "CORE":
            f"{self.P.CYN}[SYSTEM] CORE HUD engaged.{self.P.RST}",
            "DEEP":
            f"{self.P.VIOLET}[SYSTEM] DEEP HUD engaged. Full lattice visible.{self.P.RST}",
        }
        if mode in hud_configs:
            self.interface.eng.mode_settings["default_ui_depth"] = mode
            if mode != "WARM":
                self.interface.eng.ui_mode = mode
            self.interface.log(hud_configs[mode])
        else:
            self.interface.log(f"{self.P.RED}Unknown HUD mode: {mode}{self.P.RST}")
        return True

    def _cmd_idle(self, _parts):
        self.interface.modify_resource("stamina", 15.0)
        self.interface.modify_resource("atp", 20.0)
        dream_log = ""
        if dreamer := getattr(getattr(self.interface.eng, "mind", None), "dreamer",
                              None):
            soul = getattr(self.interface.eng, "soul", None)
            endo = getattr(getattr(self.interface.eng, "bio", None), "endo", None)
            snapshot = soul.to_dict() if soul else {}
            bio_state = endo.get_state() if endo else {}
            dream_text, effects = dreamer.enter_rem_cycle(snapshot, bio_state)
            if dream_text:
                dream_log = f"\n\n{self.P.VIOLET}☁️ {dream_text}{self.P.RST}"
                if effects and effects.get("glimmers"):
                    g_yield = effects["glimmers"]
                    if shared := getattr(
                            getattr(self.interface.eng, "shared_lattice", None),
                            "shared", None):
                        shared.g_pool += g_yield
                    elif phys := getattr(self.interface.eng, "phys", None):
                        phys.G = getattr(phys, "G", 0) + g_yield

                    dream_log += f"\n{self.P.MAG}✨ The dream yielded a Glimmer (+{g_yield} G_pool).{self.P.RST}"
        self.interface.log(
            f"{self.P.CYN}[SYSTEM] Engine idling. REM cycle initiated. ATP regenerating.{self.P.RST}{dream_log}"
        )
        return True

    def _cmd_mod(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /mod [slash|md]")
            return True
        mod = parts[1].upper()
        mods = {
            "SLASH": ("slash_council", self.P.INDIGO, "Dev Team online."),
            "MD": ("overseer_council", self.P.GRN, "Systemic Health protocols online."),
            "SYSTEMIC_HEALTH":
            ("overseer_council", self.P.GRN, "Systemic Health protocols online.")
        }
        if mod in mods:
            council_attr, color, msg = mods[mod]
            self.interface.log(f"{color}{mod} Mod Chip engaged. {msg}{self.P.RST}")
            if council := getattr(self.interface.eng, "council", None):
                if sub_council := getattr(council, council_attr, None):
                    sub_council.active = True
        else:
            self.interface.log(f"{self.P.RED}Unknown mod chip: {mod}{self.P.RST}")
        return True

    def _cmd_grief(self, _parts):
        if hasattr(self.interface.eng, "grief"):
            shared_lattice = getattr(self.interface.eng, "shared_lattice", None)
            wake_msg = self.interface.eng.grief.attend_wake(
                shared_lattice, getattr(self.interface.eng, "phys", None))
            self.interface.log(wake_msg)
        else:
            self.interface.log(
                f"{self.P.GRY}(We stand in silence for the lost memory. No protocol active.){self.P.RST}"
            )
        return True

    def _cmd_layer(self, parts):
        stack = getattr(self.interface.eng, "reality_stack", None)
        if not stack: return True
        if len(parts) < 2:
            self.interface.log(
                ux("main_strings", "current_layer").format(layer=stack.current_depth))
            return True
        sub = parts[1].lower()
        if sub == "push" and len(parts) > 2 and stack.push_layer(int(parts[2])):
            self.interface.log(
                ux("main_strings", "layer_pushed").format(layer=parts[2]))
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
        self.interface.log(ux("main_strings", "injected").format(payload=payload))
        return True

    def _cmd_trauma(self, _parts):
        self.interface.eng.health = 20.0
        self.interface.eng.trauma_accum["SYNTHETIC_CRISIS"] = 50.0
        if hasattr(self.interface.eng, "events"):
            self.interface.eng.events.publish("TRAUMA_EVENT", {"magnitude": 50.0})
        self.interface.log(
            f"{self.P.RED}[DEV] Health dropped to 20. Trauma spiked to 50. Proceed to next turn.{self.P.RST}",
            "SYS",
        )
        return True

    def _execute_substrate_write(self, file_name: str, content: str):
        substrate = getattr(self.interface.eng, "substrate", None)
        if substrate is None:
            from bone_utils import TheSubstrate
            substrate = TheSubstrate(getattr(self.interface.eng, "events", None))
        substrate.queue_write(file_name, self.P.strip(content))
        stamina = self.interface.get_resource("stamina")
        write_logs, cost = substrate.execute_writes(stamina)
        self.interface.modify_resource("stamina", -cost)
        for log in write_logs:
            self.interface.log(log)

    def _cmd_podcast(self, parts):
        if len(parts) < 2:
            self.interface.log("Usage: /podcast <topic>")
            return True
        topic = " ".join(parts[1:])
        self.interface.log(
            f"{self.P.CYN}🎙️ Assembling the Parliament for topic: '{topic}'...{self.P.RST}"
        )
        cortex = getattr(self.interface.eng, "cortex", None)
        llm = getattr(cortex, "llm", None)
        council = getattr(self.interface.eng, "council", None)
        if not llm or not council or not hasattr(council, "host_podcast"):
            self.interface.log(
                f"{self.P.RED}Error: Cortex LLM or Council 'host_podcast' method unavailable.{self.P.RST}"
            )
            return True
        try:
            script = council.host_podcast(topic, llm)
            self.interface.log(f"\n{script}\n")
            safe_topic = "".join(c if c.isalnum() else "_"
                                 for c in topic)[:25].strip("_")
            file_name = f"podcast_{safe_topic}_{int(time.time())}.txt"
            self._execute_substrate_write(file_name, script)
        except Exception as e:
            self.interface.log(
                f"{self.P.RED}Podcast generation failed: {e}{self.P.RST}")
        return True

    def _cmd_journal(self, _parts):
        self.interface.log(f"{self.P.CYN}📖 Compiling narrative journal...{self.P.RST}")
        cortex = getattr(self.interface.eng, "cortex", None)
        llm = getattr(cortex, "llm", None)
        if not llm or not cortex.dialogue_buffer:
            self.interface.log(
                f"{self.P.RED}Error: Cortex LLM unavailable or memory buffer is empty.{self.P.RST}"
            )
            return True
        try:
            history = "\n".join(cortex.dialogue_buffer)
            prompt = (
                "SYSTEM_INSTRUCTION: You are the archivist of a surreal cybernetic journey. "
                "Read the following recent dialogue history and write a whimsical, reflective, first-person diary entry (1-2 paragraphs) "
                "summarizing the events and emotional undercurrents so far. Focus on the mood, the strange tension, and the overarching theme. "
                "DO NOT use AI-isms. Write like a traveler recording a dream.\n\n"
                f"DIALOGUE HISTORY:\n{history}")
            journal_entry = llm.generate(prompt, {
                "temperature": 0.85,
                "max_tokens": 300
            })
            self.interface.log(f"\n{self.P.WHT}{journal_entry}{self.P.RST}\n")
            file_name = f"journal_entry_{int(time.time())}.txt"
            self._execute_substrate_write(file_name, journal_entry)
        except Exception as e:
            self.interface.log(
                f"{self.P.RED}Journal generation failed: {e}{self.P.RST}")
        return True

    def _cmd_shuffle(self, _parts):
        cmd_cfg = getattr(self.interface.Config, "COMMANDS", None)
        cost = getattr(cmd_cfg, "COST_SHUFFLE", 5.0)
        if not self.tax.levy("SHUFFLE", {"atp": cost}):
            return True
        if hasattr(self.interface.eng, "phys"):
            self.interface.eng.phys.narrative_drag = 0.0
        self.interface.log(
            f"{self.P.VIOLET}🃏 [ !s ] THE SHUFFLE: Jester summoned. Lateral shift initiated.{self.P.RST}"
        )
        self.interface.log(
            f"{self.P.GRY}Control illusion shattered. Narrative drag reset to 0. (Cost: {cost} ATP){self.P.RST}"
        )
        return True
