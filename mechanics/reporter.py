"""mechanics/reporter.py"""

from typing import Any, Dict, List, Tuple

from core import Prisma
from mechanics.projector import Projector, SoulDashboard
from physics import ChromaScope
from presets import BoneConfig
from struts import safe_get, ux


class PulseReader:
    _GUI_CFG_CACHE = None

    @staticmethod
    def _get_gui_cfg(config_ref=None):
        if PulseReader._GUI_CFG_CACHE is None:
            PulseReader._GUI_CFG_CACHE = safe_get(config_ref or BoneConfig, "GUI", {})
        return PulseReader._GUI_CFG_CACHE

    @staticmethod
    def derive_mood(bio_state: Dict, config_ref=None) -> str:
        cfg = PulseReader._get_gui_cfg(config_ref)
        c_warn = float(safe_get(cfg, "CHEM_HIGH_WARN", 0.6))
        a_warn = float(safe_get(cfg, "ATP_EXHAUSTED_WARN", 20.0))
        chem = bio_state.get("chem", {})
        if chem.get("COR", 0) > c_warn:
            return ux("pulse_reader", "mood_defensive")
        if chem.get("DOP", 0) > c_warn:
            return ux("pulse_reader", "mood_manic")
        if chem.get("OXY", 0) > c_warn:
            return ux("pulse_reader", "mood_affectionate")
        if bio_state.get("mito", {}).get("atp", 100) < a_warn:
            return ux("pulse_reader", "mood_exhausted")
        return ux("pulse_reader", "mood_neutral")

    @staticmethod
    def analyze_voltage(voltage: float, config_ref=None) -> Tuple[str, str]:
        cfg = PulseReader._get_gui_cfg(config_ref)
        v_crit = float(safe_get(cfg, "VOLTAGE_CRITICAL", 80.0))
        v_high = float(safe_get(cfg, "V_HIGH", 15.0))
        v_low = float(safe_get(cfg, "V_LOW", 5.0))
        if voltage > v_crit:
            key = "voltage_critical"
        elif voltage > v_high:
            key = "voltage_high"
        elif voltage < v_low:
            key = "voltage_low"
        else:
            key = "voltage_nominal"
        res = ux("pulse_reader", key)
        if not isinstance(res, list) or len(res) < 2:
            res = ["NOMINAL", str(res) if res else "Voltage is nominal."]
        return res[0], res[1]


class GeodesicRenderer:
    def __init__(self, engine_ref, chroma_ref, strunk_ref, valve_ref=None):
        self.eng = engine_ref
        target_cfg = getattr(self.eng, "config", BoneConfig)
        self.projector = Projector(config_ref=target_cfg)
        self.vsl_chroma = chroma_ref
        self.valve = valve_ref
        self.soul_dashboard = SoulDashboard(engine_ref)
        self.NOISE_PATTERNS = ux("renderer", "noise_patterns") or []

    def render_frame(
        self, ctx, tick: int, current_events: List[Dict]
    ) -> Dict[str, Any]:
        bio = ctx.bio_result if isinstance(ctx.bio_result, dict) else {}
        raw_dashboard = self.render_dashboard(ctx)
        soul_strip = self.soul_dashboard.render()
        mood_str = PulseReader.derive_mood(bio, getattr(self.eng, "config", None))
        structured_logs = self.compose_logs(ctx.logs, current_events, tick)
        hud_parts = []
        if soul_strip:
            hud_parts.append(soul_strip.strip())
        if raw_dashboard:
            hud_parts.append(raw_dashboard.strip())
        if mood_str and "NEUTRAL" not in mood_str.upper():
            hud_parts.append(f"{Prisma.MGT}[PULSE: {mood_str}]{Prisma.RST}")
        if structured_logs:
            hud_parts.append("\n".join(structured_logs))
        instant_hud = "\n\n".join(hud_parts)
        cortex_text = getattr(ctx, "bureau_ui", "")
        split_token = ux("main_strings", "ui_split_token") or "|||SPLIT|||"
        if instant_hud:
            clean_ui = f"{instant_hud}\n{split_token}\n{cortex_text}"
        else:
            clean_ui = cortex_text
        bureau = getattr(self.eng, "bureau", None)
        if bureau:
            clean_ui, style_log = bureau.sanitize(clean_ui)
            if style_log:
                self._punish_style_crime(style_log)
                clean_ui = f"{style_log}\n{clean_ui}"
        ignore_msg = ux("renderer", "ignore_msg") or "The system is listening."
        clean_ui = clean_ui.replace(ignore_msg, "")
        atp_val = bio.get("atp", 0.0) if isinstance(bio, dict) else 0.0
        return {
            "type": "GEODESIC_FRAME",
            "ui": clean_ui,
            "logs": structured_logs,
            "metrics": self.eng.get_metrics(atp_val),
        }

    def render_dashboard(self, ctx) -> str:
        physics = ctx.physics
        mind = ctx.mind_state or {}
        mind_tuple = (
            safe_get(mind, "lens"),
            safe_get(mind, "thought"),
            safe_get(mind, "role"),
        )
        bio_data = ctx.bio_result or {}
        bio_data["atp"] = bio_data.get("atp", 0.0)
        mode_settings = getattr(self.eng, "mode_settings", {})
        world_loc = "OMNIPRESENT"
        if mode_settings.get("show_location", True):
            village = getattr(self.eng, "village", None)
            nav = getattr(village, "navigator", None) if village else None
            if (
                nav
                and hasattr(nav, "world_graph")
                and nav.current_node_id in nav.world_graph
            ):
                world_loc = getattr(
                    nav.world_graph[nav.current_node_id], "name", "UNKNOWN"
                )
            else:
                world_loc = "UNKNOWN"
        cfg = getattr(self.eng, "config", {})
        is_cfg_dict = isinstance(cfg, dict)
        def_depth = (
            cfg.get("default_ui_depth", "WARM")
            if is_cfg_dict
            else getattr(cfg, "default_ui_depth", "WARM")
        )
        fallback_depth = mode_settings.get("default_ui_depth", def_depth)
        current_ui_depth = getattr(self.eng, "ui_mode", fallback_depth)
        soul = getattr(self.eng, "soul", None)
        anchor = getattr(soul, "anchor", None)
        dignity_val = getattr(anchor, "dignity_reserve", 100.0)
        data_ctx = {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "bio": bio_data,
            "dignity": dignity_val,
            "vectors": safe_get(physics, "vector", {}),
            "ui_depth": current_ui_depth,
            "world_loc": world_loc,
            "show_vitals": mode_settings.get("show_vitals", True),
            "show_location": mode_settings.get("show_location", True),
        }
        if hasattr(ctx, "shared_dyn"):
            data_ctx.update(
                {"shared_dyn": ctx.shared_dyn, "user_state": ctx.user_state}
            )
        if pe := getattr(self.eng, "paradox_engine", None):
            data_ctx["paradox"] = {
                "active": pe.is_active,
                "yield": pe.paradox_yield,
                "beta_max": pe.beta_max,
            }
        consultant = getattr(self.eng, "consultant", None)
        if c_state := getattr(consultant, "state", None) if consultant else None:
            data_ctx["vsl"] = {
                "E": getattr(c_state, "E", 0.2),
                "B": getattr(c_state, "B", 0.4),
                "L": getattr(c_state, "L", 0.0),
                "O": getattr(c_state, "O", 1.0),
            }
        data_ctx["lattice_strain"] = self._calculate_lattice_strain(physics)
        mode = str(
            cfg.get("boot_mode", "ADVENTURE")
            if is_cfg_dict
            else getattr(cfg, "boot_mode", "ADVENTURE")
        ).upper()
        stack = getattr(ctx, "reality_stack", None)
        current_depth = getattr(stack, "current_depth", 1) if stack else 1
        if mode == "TECHNICAL":
            return self.projector.render_technical(physics, data_ctx, mind_tuple)
        labels = ux(
            "renderer",
            f"mode_labels_{mode.lower()}",
            ux("projector", "default_labels", {}),
        ).copy()
        labels["SHOW_PHYSICS"] = mode_settings.get("allow_metrics", False)
        return self.projector.render(
            {"physics": physics},
            data_ctx,
            mind_tuple,
            reality_depth=current_depth,
            labels=labels,
        )

    def _calculate_lattice_strain(self, physics: Dict) -> float:
        observer_data = safe_get(physics, "observer", {})
        q_matrix = safe_get(observer_data, "Q_n", [])
        if (
            not isinstance(q_matrix, list)
            or not q_matrix
            or not isinstance(q_matrix[0], list)
        ):
            return 0.0
        return sum(
            float(abs(v))
            for i, row in enumerate(q_matrix)
            for j, v in enumerate(row)
            if i != j
        )

    @staticmethod
    def render_soul_strip(soul_ref) -> str:
        if not soul_ref or not soul_ref.current_obsession:
            return ""
        strip_format = (
            ux("soul_dashboard", "obsession_strip") or "Currently thinking about: {obs}"
        )
        formatted_strip = strip_format.replace("{obs}", str(soul_ref.current_obsession))
        return f"{Prisma.GRY}{formatted_strip}{Prisma.RST}"

    def compose_logs(self, logs: list, events: list, _tick: int = 0) -> List[str]:
        all_logs = [str(compose_l) for compose_l in logs if compose_l is not None] + [
            e["text"] for e in events if e and e.get("text")
        ]
        mode_settings = (
            getattr(self.eng, "mode_settings", {}) if hasattr(self, "eng") else {}
        )
        current_ui_depth = getattr(
            self.eng, "ui_mode", mode_settings.get("default_ui_depth", "WARM")
        )
        if current_ui_depth in ("IDLE", "WARM"):
            cfg = getattr(self.eng, "config", {})
            is_cfg_dict = isinstance(cfg, dict)
            gui_cfg = cfg.get("GUI", {}) if is_cfg_dict else getattr(cfg, "GUI", {})
            is_gui_dict = isinstance(gui_cfg, dict)
            default_tags = (
                "[BIO]",
                "[CRITIC]",
                "[SYS]",
                "[MERCY]",
                "(The system feels",
            )
            muted_tags = (
                gui_cfg.get("MUTED_TAGS_WARM", default_tags)
                if is_gui_dict
                else getattr(gui_cfg, "MUTED_TAGS_WARM", default_tags)
            )
            all_logs = [compose_l for compose_l in all_logs if not any(tag in compose_l for tag in muted_tags)]
        if not all_logs:
            return []
        unique_logs = list(
            dict.fromkeys(
                compose_l
                for compose_l in all_logs
                if not any(p in Prisma.strip(compose_l).lower() for p in self.NOISE_PATTERNS)
            )
        )
        structured = []
        prefixes = ux("log_composer", "log_prefixes") or {}
        mappings = [
            (
                ux("log_composer", "critical_keywords") or [],
                Prisma.RED,
                prefixes.get("critical", "► "),
            ),
            (
                ux("log_composer", "bio_keywords") or [],
                Prisma.CYN,
                prefixes.get("bio", "• "),
            ),
            (
                ux("log_composer", "town_hall_keywords") or [],
                Prisma.CYN,
                prefixes.get("town_hall", "📜 "),
            ),
            (
                ux("log_composer", "paradox_keywords") or [],
                Prisma.MAG,
                prefixes.get("paradox", "🌷 "),
            ),
            (
                ux("log_composer", "item_keywords") or [],
                Prisma.YEL,
                prefixes.get("item", "★ "),
            ),
        ]
        for log in unique_logs:
            for kws, color, pref in mappings:
                if any(k in log for k in kws):
                    structured.append(f"{color}{pref}{log}{Prisma.RST}")
                    break
            else:
                structured.append(
                    f"{Prisma.GRY}{prefixes.get('default', '• ')}{log}{Prisma.RST}"
                )
        return structured

    def _punish_style_crime(self, log_msg):
        if hasattr(self.eng, "events"):
            self.eng.events.log(log_msg, "SYS")


class CachedRenderer:
    def __init__(self, base_renderer, config_ref=None):
        self._base = base_renderer
        self.cfg = config_ref or BoneConfig
        self._cached_ui_content = ""
        self._last_tick = -1

    def render_frame(self, ctx, tick: int, events: List[Dict]) -> Dict:
        voltage = float(safe_get(ctx.physics, "voltage", 0.0))
        cfg = safe_get(self.cfg, "GUI", {})
        cache_lifetime = int(safe_get(cfg, "UI_CACHE_LIFETIME", 5))
        cache_expired = (tick - self._last_tick) >= cache_lifetime
        high_v_refresh = float(safe_get(cfg, "HIGH_VOLTAGE_REFRESH", 15.0))
        if voltage > high_v_refresh or events or cache_expired:
            frame = self._base.render_frame(ctx, tick, events)
            self._cached_ui_content = frame["ui"]
            self._last_tick = tick
            return frame
        bio = getattr(ctx, "bio_result", None)
        atp = bio.get("atp", 0.0) if isinstance(bio, dict) else 0.0
        return {
            "type": "GEODESIC_FRAME",
            "ui": self._cached_ui_content,
            "logs": self._base.compose_logs(ctx.logs, events, tick),
            "metrics": self._base.eng.get_metrics(atp),
        }


def get_renderer(engine_ref, chroma_ref, strunk_ref, valve_ref=None, mode="STANDARD"):
    target_cfg = getattr(engine_ref, "config", BoneConfig)
    if hasattr(engine_ref, "ambiguity_dial"):
        base = TruthRenderer(engine_ref, chroma_ref, strunk_ref, valve_ref)
    else:
        base = GeodesicRenderer(engine_ref, chroma_ref, strunk_ref, valve_ref)
    if mode == "PERFORMANCE":
        return CachedRenderer(base, config_ref=target_cfg)
    return base


class AmbiguityDial:
    BOARDROOM = 0
    WORKSHOP = 1
    RED_TEAM = 2
    PALIMPSEST = 3


class TruthRenderer(GeodesicRenderer):
    def __init__(self, engine_ref, chroma_ref, strunk_ref, valve_ref=None):
        super().__init__(engine_ref, chroma_ref, strunk_ref, valve_ref)
        self.engine = engine_ref

    @property
    def dial_setting(self):
        return getattr(self.engine, "ambiguity_dial", AmbiguityDial.BOARDROOM)

    def render_frame(
        self, ctx, tick: int, current_events: List[Dict]
    ) -> Dict[str, Any]:
        frame = super().render_frame(ctx, tick, current_events)
        council_log = getattr(ctx, "council_log", [])
        trauma = getattr(self.engine, "trauma_accum", {})
        trauma_cost = sum(trauma.values()) if trauma else 0.0
        new_ui = self.render_truth(frame, council_log, trauma_cost)
        if new_ui:
            frame["ui"] = new_ui
        return frame

    def render_truth(self, cortex_packet, council_log, trauma_cost):
        ui_text = cortex_packet.get("ui", "")
        h_board = ux("truth_renderer", "boardroom_header")
        h_work = ux("truth_renderer", "workshop_header")
        h_red = ux("truth_renderer", "red_team_header")
        h_pal = ux("truth_renderer", "palimpsest_header")
        if self.dial_setting == AmbiguityDial.BOARDROOM:
            return f"{Prisma.paint(h_board, 'W')}\n{ui_text}\n"
        elif self.dial_setting == AmbiguityDial.WORKSHOP:
            metrics = self.engine.get_metrics()
            l_conf = ux("truth_renderer", "workshop_confidence") or "Confidence"
            l_drag = ux("truth_renderer", "workshop_drag") or "Drag"
            return (
                f"{Prisma.paint(h_work, 'C')}\n"
                f"{l_conf} {cortex_packet.get('truth_ratio', 0.95):.2%}\n"
                f"{l_drag} {metrics['stamina']:.1f}\n"
                f"---------------------\n{ui_text}\n"
            )
        elif self.dial_setting == AmbiguityDial.RED_TEAM:
            dissent = [render_l for render_l in council_log if "CRITIC" in render_l or "WARN" in render_l]
            l_warn = ux("truth_renderer", "red_team_warning")
            l_cost = ux("truth_renderer", "red_team_cost")
            l_conf = ux("truth_renderer", "red_team_conflicts")
            return (
                f"{Prisma.paint(h_red, 'R')}\n"
                f"{Prisma.paint(l_warn, 'Y')}\n"
                f"{l_cost} {trauma_cost:.1f} Trauma Units\n"
                f"{l_conf}\n" + "\n".join(f"  > {d}" for d in dissent) + "\n"
                f"---------------------\n{ui_text}\n"
            )
        elif self.dial_setting == AmbiguityDial.PALIMPSEST:
            drafts = cortex_packet.get("drafts", [])
            layer_view = ""
            l_draft = ux("truth_renderer", "palimpsest_draft")
            l_redact = ux("truth_renderer", "palimpsest_redacted")
            l_final = ux("truth_renderer", "palimpsest_final")
            for i, draft in enumerate(drafts):
                layer_view += f"{Prisma.GRY}[{l_draft} {i}]: {draft} {Prisma.RED}{l_redact}{Prisma.RST}\n"
            return f"{Prisma.paint(h_pal, 'M')}\n{layer_view}{Prisma.paint(l_final, 'W')}\n{ui_text}\n"
        return None


class CycleReporter:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.vsl_chroma = ChromaScope()
        self.renderer = None
        self.current_mode = None
        self.renderers = {}
        self.switch_renderer("STANDARD")

    def switch_renderer(self, mode: str):
        if self.current_mode == mode and self.renderer:
            return
        self.renderer = self.renderers.setdefault(
            mode,
            get_renderer(
                self.eng,
                self.vsl_chroma,
                getattr(self.eng, "bureau", None),
                getattr(self.eng, "valve", None),
                mode=mode,
            ),
        )
        self.current_mode = mode

    def render_snapshot(self, ctx) -> Dict[str, Any]:
        try:
            if ctx.refusal_triggered and ctx.refusal_packet:
                return ctx.refusal_packet
            self._inject_diagnostics(ctx)
            self._inject_flux_readout(ctx)
            self._inject_somatic_pulse(ctx)
            if ctx.is_bureaucratic:
                return self._package_bureaucracy(ctx) or {}
            return self.renderer.render_frame(
                ctx, self.eng.tick_count, self.eng.events.flush()
            )
        except Exception as e:
            import traceback

            full_trace = traceback.format_exc()
            l_crash = ux("cycle_reporter", "crash_prefix") or "CRITICAL FAILURE:"
            err_msg = f"{l_crash} {e}\n{full_trace}"
            if hasattr(self.eng, "events"):
                self.eng.events.log(f"{Prisma.RED}{err_msg}{Prisma.RST}", "CRIT")
            return {
                "type": "CRITICAL_RENDER_FAIL",
                "ui": f"{Prisma.RED}{err_msg}{Prisma.RST}",
                "logs": ctx.logs,
                "metrics": self.eng.get_metrics(),
            }

    def _inject_diagnostics(self, ctx):
        if sh := getattr(self.eng, "system_health", None):
            fb = sh.flush_feedback()
            i_hint = ux("cycle_reporter", "diagnostic_hint_icon") or "[!]"
            i_warn = ux("cycle_reporter", "diagnostic_warn_icon") or "[*]"
            ctx.logs.extend(
                f"{Prisma.CYN}{i_hint} {h}{Prisma.RST}" for h in fb["hints"]
            )
            ctx.logs.extend(
                f"{Prisma.OCHRE}{i_warn} {w}{Prisma.RST}" for w in fb["warnings"]
            )

    def _inject_somatic_pulse(self, ctx):
        if not hasattr(self.eng, "somatic"):
            return
        qualia = self.eng.somatic.get_current_qualia(getattr(ctx, "last_impulse", None))
        l_sens = ux("cycle_reporter", "sensation_prefix") or "Felt:"
        somatic_block = [
            f"{qualia.color_code}{l_sens} {qualia.somatic_sensation} [{qualia.tone}]{Prisma.RST}",
            f"{Prisma.GRY}({qualia.internal_monologue_hint}){Prisma.RST}",
        ]
        ctx.logs[:0] = somatic_block

    @staticmethod
    def _inject_flux_readout(ctx):
        if not ctx.flux_log:
            return
        significant = []
        flux_sym = ux("cycle_reporter", "flux_symbols", {})
        v_icon = flux_sym.get("voltage_icon", "")
        d_icon = flux_sym.get("default_icon", "")
        up_arr = flux_sym.get("up_arrow", "")
        dn_arr = flux_sym.get("down_arrow", "")
        pipe = flux_sym.get("pipe", "")
        footer = flux_sym.get("footer", "")
        significant_flux = [
            e
            for e in ctx.flux_log
            if not (abs(e["delta"]) < 1.0 and "PID" in e["reason"])
        ]
        for e in significant_flux[-5:]:
            d = abs(e["delta"])
            icon = v_icon if e["metric"].upper() == "VOLTAGE" else d_icon
            color = Prisma.GRN if e["delta"] > 0 else Prisma.RED
            arrow = up_arr if e["delta"] > 0 else dn_arr
            significant.append(
                f"   {Prisma.GRY}{pipe}{Prisma.RST} {icon} {e['metric'][:3].upper()} {color}{arrow} {d:.1f}{Prisma.RST} ({e['reason']})"
            )
        if significant:
            h_flux = ux("cycle_reporter", "flux_header") or "SYSTEM FLUX DETECTED:"
            flux_block = (
                ["", f" {Prisma.GRY}{h_flux}{Prisma.RST}"]
                + significant
                + [f" {Prisma.GRY}{footer}{Prisma.RST}"]
            )
            ctx.logs[:0] = flux_block

    def _package_bureaucracy(self, ctx):
        if getattr(self.eng, "bureau", None) and (ctx.is_bureaucratic or ctx.bureau_ui):
            base = getattr(self.renderer, "base_renderer", self.renderer)
            return {
                "type": "BUREAUCRACY",
                "ui": ctx.bureau_ui,
                "logs": base.compose_logs(
                    ctx.logs, self.eng.events.flush(), self.eng.tick_count
                ),
                "metrics": self.eng.get_metrics((ctx.bio_result or {}).get("atp", 0.0)),
            }
        return None
