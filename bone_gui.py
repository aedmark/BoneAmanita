from typing import Dict, List, Any, Tuple
from bone_core import Prisma, LoreManifest
from bone_physics import ChromaScope


class Projector:
    def __init__(self):
        self.width = 80

    @staticmethod
    def _extract(physics_obj: Any, field: str, sub_field: str, default: Any = 0.0):
        val = None
        if hasattr(physics_obj, sub_field):
            val = getattr(physics_obj, sub_field)
        elif isinstance(physics_obj, dict):
            if sub_field in physics_obj:
                val = physics_obj[sub_field]
            elif field in physics_obj and isinstance(physics_obj[field], dict):
                val = physics_obj[field].get(sub_field)
        return default if val is None else val

    def render(
        self,
        physics_ctx: Dict,
        data_ctx: Dict,
        mind_ctx: tuple,
        reality_depth: int = 1,
        labels: Dict = None,
    ) -> str:
        if not labels:
            labels = LoreManifest.get_instance().get_ux("projector", "default_labels")
        physics = physics_ctx.get("physics", {})
        status_line = self._render_vital_strip(data_ctx, mind_ctx, labels)
        physics_line = ""
        if labels.get("SHOW_PHYSICS", True):
            physics_line = self._render_physics_strip(
                physics, data_ctx.get("vectors", {})
            )
        ui_depth = data_ctx.get("ui_depth", "IDLE")
        vsl_line = self._render_lattice_strip(physics, depth=ui_depth)

        zone = self._extract(
            physics, "space", "zone", LoreManifest.get_instance().get_ux("projector", "default_zone")
        )
        world_loc = data_ctx.get("world_loc", "UNKNOWN")

        lens = mind_ctx[0] if mind_ctx else LoreManifest.get_instance().get_ux("projector", "default_lens")

        depth_map = LoreManifest.get_instance().get_ux(
            "projector",
            "depth_map"
        )
        depth_label = depth_map.get(str(reality_depth), "?")
        depth_marker = f"{Prisma.VIOLET}[D{reality_depth}:{depth_label}]{Prisma.RST}"
        display_loc = f"{world_loc.upper()[:20]} [{zone}]"
        context_line = f"{Prisma.GRY}  📍 {display_loc:<25}  👁️ {lens:<12}  {depth_marker}{Prisma.RST}"
        div = f"{Prisma.GRY}{'─' * self.width}{Prisma.RST}"

        mid_lines = []
        if physics_line:
            mid_lines.append(physics_line)
        if vsl_line:
            mid_lines.append("  " + vsl_line)
        mid_section = "\n".join(mid_lines) if mid_lines else ""

        return f"{div}\n{status_line}\n{mid_section}\n{context_line}\n{div}"

    def _render_vital_strip(self, data: Dict, mind: tuple, labels: Dict) -> str:
        health = data.get("health", 100)
        stamina = data.get("stamina", 100)
        atp = data.get("bio", {}).get("atp") or 0
        dignity = data.get("dignity", 100)
        hp_bar = self._mini_bar(health, 100, 6, Prisma.RED)
        stm_bar = self._mini_bar(stamina, 100, 6, Prisma.GRN)
        dig_color = Prisma.VIOLET if dignity > 50 else Prisma.GRY
        dig_icon = "✦" if dignity > 80 else "✧"
        raw_role = mind[2] if mind and len(mind) > 2 else None
        role = (
            str(raw_role).upper()
            if raw_role
            else LoreManifest.get_instance().get_ux("projector", "default_role")
        )
        role = role.replace(LoreManifest.get_instance().get_ux("projector", "role_redundancy"), "THE ")
        if len(role) > 30:
            role = role[:27] + "..."
        l_hp = labels.get("HP", "HP")
        l_stm = labels.get("STM", "STM")
        role_block = f"{Prisma.WHT}♦ {role}{Prisma.RST}"
        return (
            f"  {role_block:<35} "
            f"{l_hp} {hp_bar}  "
            f"{l_stm} {stm_bar}  "
            f"{dig_color}{dig_icon}{int(dignity)}%{Prisma.RST} "
            f"{Prisma.YEL}ATP:{int(atp)}{Prisma.RST}"
        )

    def _render_physics_strip(self, physics: Any, vectors: Dict) -> str:
        volt = self._extract(physics, "energy", "voltage", 0.0)
        drag = self._extract(physics, "space", "narrative_drag", 0.0)
        dom_vec = "NEUTRAL"
        dom_val = 0.0
        if vectors:
            dom_vec = max(vectors, key=vectors.get)
            dom_val = vectors[dom_vec]
        return (
            f"  {Prisma.CYN}VOLT:{Prisma.RST} {volt:04.1f}v   "
            f"{Prisma.SLATE}DRAG:{Prisma.RST} {drag:04.1f}   "
            f"{Prisma.MAG}VEC:{Prisma.RST} {dom_vec} ({dom_val:.2f})"
        )

    @staticmethod
    def _render_lattice_strip(physics: Dict, depth: str = "DEEP") -> str:
        if depth == "IDLE" or not physics:
            return ""

        def _get_val(k1, k2, default_val):
            v = physics.get(k1)
            if v is None:
                v = physics.get(k2)
            return default_val if v is None else v

        E = _get_val("exhaustion", "E", 0.2)
        beta = _get_val("contradiction", "beta", 0.4)
        V = _get_val("voltage", "voltage", 30.0)
        F = _get_val("friction", "narrative_drag", 0.6)
        H = _get_val("health", "health", 100.0)
        P = _get_val("stamina", "stamina", 100.0)
        T = _get_val("trauma", "T", 0.0)
        psi = _get_val("psi", "psi", 0.0)
        chi = _get_val("chi", "chi", 0.0)
        valence = _get_val("valence", "valence", 0.0)
        core = f"{Prisma.CYN}[🧊 E:{E:.2f} β:{beta:.2f} | ⚡ V:{V:.0f} F:{F:.1f} | ❤️ H:{H:.0f} P:{P:.0f} | 🏺 T:{T:.0f}]{Prisma.RST}"
        deep = (
            f"{Prisma.VIOLET} [🌌 Ψ:{psi:.2f} Χ:{chi:.2f} ♥:{valence:.2f}]{Prisma.RST}"
        )
        if depth == "DEEP":
            return core + deep
        elif depth == "CORE":
            return core
        elif depth == "LITE":
            return f"{Prisma.CYN}[⚡ V:{V:.0f} | ❤️ H:{H:.0f} P:{P:.0f}]{Prisma.RST}"
        return ""

    def render_technical(self, physics: Dict, data: Dict, mind: tuple) -> str:
        v = self._extract(physics, "energy", "voltage", 0.0)
        d = self._extract(physics, "space", "narrative_drag", 0.0)
        vec = data.get("vectors", {})
        vec_str = ", ".join([f"{k}:{v:.2f}" for k, v in vec.items() if v > 0.01])

        h_tech = LoreManifest.get_instance().get_ux("technical_projector", "header")
        l_phys = LoreManifest.get_instance().get_ux("technical_projector", "physics_label")
        l_vec = LoreManifest.get_instance().get_ux("technical_projector", "vectors_label")
        l_bio = LoreManifest.get_instance().get_ux("technical_projector", "bio_dump_label")

        return (
            f"{Prisma.CYN}{h_tech}{Prisma.RST}\n"
            f"{l_phys} V={v:<6.3f} D={d:<6.3f} | LENS: {mind[0]}\n"
            f"{l_vec} [{vec_str}]\n"
            f"{l_bio} {str(data.get('bio', {}))[:60]}..."
        )

    @staticmethod
    def _mini_bar(val, max_val, width, color):
        if max_val == 0:
            return ""
        ratio = max(0.0, min(1.0, val / max_val))
        fill = int(ratio * width)
        empty = width - fill
        return f"{color}{'█' * fill}{Prisma.GRY}{'░' * empty}{Prisma.RST}"


class GeodesicRenderer:
    def __init__(self, engine_ref, chroma_ref, strunk_ref, valve_ref=None):
        self.eng = engine_ref
        self.projector = Projector()
        self.vsl_chroma = chroma_ref
        self.strunk_white = strunk_ref
        self.valve = valve_ref
        self.soul_dashboard = SoulDashboard(engine_ref)
        self.NOISE_PATTERNS = LoreManifest.get_instance().get_ux("renderer", "noise_patterns")

    def render_frame(
        self, ctx, tick: int, current_events: List[Dict]
    ) -> Dict[str, Any]:
        physics = ctx.physics
        bio = ctx.bio_result
        raw_dashboard = self.render_dashboard(ctx)
        colored_ui = self.vsl_chroma.modulate(raw_dashboard, physics.get("vector", {}))
        if self.strunk_white:
            clean_ui, style_log = self.strunk_white.sanitize(colored_ui)
            if style_log:
                self._punish_style_crime(style_log)
        else:
            clean_ui = colored_ui

        ignore_msg = LoreManifest.get_instance().get_ux("renderer", "ignore_msg")
        if ignore_msg in clean_ui:
            clean_ui = clean_ui.replace(ignore_msg, "")

        structured_logs = self.compose_logs(ctx.logs, current_events, tick)
        return {
            "type": "GEODESIC_FRAME",
            "ui": clean_ui,
            "logs": structured_logs,
            "metrics": self.eng.get_metrics(bio.get("atp", 0.0)),
        }

    def render_dashboard(self, ctx) -> str:
        physics = ctx.physics
        mind = ctx.mind_state
        mind_tuple = (mind.get("lens"), mind.get("thought"), mind.get("role"))
        bio_data = ctx.bio_result or {}
        metrics = self.eng.get_metrics()
        bio_data["atp"] = metrics.get("atp", 0.0)
        world_loc = "UNKNOWN"
        if hasattr(self.eng, "navigator") and self.eng.navigator:
            node = self.eng.navigator.world_graph.get(
                self.eng.navigator.current_node_id
            )
            if node:
                world_loc = node.name

        data_ctx = {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "bio": bio_data,
            "dignity": (
                getattr(self.eng.soul.anchor, "dignity_reserve", 100.0)
                if hasattr(self.eng, "soul")
                else 100.0
            ),
            "vectors": physics.get("vector", {}),
            "ui_depth": getattr(self.eng, "ui_mode", "IDLE"),
            "world_loc": world_loc,
        }
        if hasattr(self.eng, "consultant"):
            data_ctx["vsl"] = {
                "E": self.eng.consultant.state.E,
                "B": self.eng.consultant.state.B,
                "L": getattr(self.eng.consultant.state, "L", 0.0),
                "O": getattr(self.eng.consultant.state, "O", 1.0),
            }
        mode = self.eng.config.get("boot_mode", "ADVENTURE").upper()
        current_depth = 1
        if hasattr(ctx, "reality_stack"):
            current_depth = ctx.reality_stack.current_depth

        if mode == "TECHNICAL":
            return self.projector.render_technical(physics, data_ctx, mind_tuple)
        elif mode == "CONVERSATION":
            labels = LoreManifest.get_instance().get_ux(
                "renderer", "mode_labels_conversation"
            ).copy()
            labels["SHOW_PHYSICS"] = False
            return self.projector.render(
                {"physics": physics}, data_ctx, mind_tuple, current_depth, labels
            )
        elif mode == "CREATIVE":
            labels = LoreManifest.get_instance().get_ux(
                "renderer", "mode_labels_creative"
            ).copy()
            labels["SHOW_PHYSICS"] = True
            return self.projector.render(
                {"physics": physics}, data_ctx, mind_tuple, current_depth, labels
            )
        else:
            labels = LoreManifest.get_instance().get_ux(
                "projector", "default_labels"
            ).copy()
            labels["SHOW_PHYSICS"] = False
            return self.projector.render(
                {"physics": physics},
                data_ctx,
                mind_tuple,
                reality_depth=current_depth,
                labels=labels,
            )

    @staticmethod
    def render_soul_strip(soul_ref) -> str:
        if not soul_ref:
            return ""
        if not soul_ref.current_obsession:
            return ""
        return (
            f"{Prisma.GRY}--- Obsession: {soul_ref.current_obsession} ---{Prisma.RST}"
        )

    def compose_logs(self, logs: list, events: list, _tick: int = 0) -> List[str]:
        all_logs = [str(l) for l in logs if l is not None]
        for e in events:
            if e and e.get("text"):
                all_logs.append(e["text"])
        if not all_logs:
            return []
        unique_logs = []
        seen = set()
        for l in all_logs:
            clean_l = Prisma.strip(l).lower()
            if any(pattern in clean_l for pattern in self.NOISE_PATTERNS):
                continue
            if l not in seen:
                unique_logs.append(l)
                seen.add(l)
        structured = []
        c_kws = LoreManifest.get_instance().get_ux("log_composer", "critical_keywords")
        b_kws = LoreManifest.get_instance().get_ux("log_composer", "bio_keywords")
        t_kws = LoreManifest.get_instance().get_ux(
            "log_composer", "town_hall_keywords"
        )
        p_kws = LoreManifest.get_instance().get_ux("log_composer", "paradox_keywords")
        i_kws = LoreManifest.get_instance().get_ux("log_composer", "item_keywords")

        for log in unique_logs:
            if any(k in log for k in c_kws):
                structured.append(f"{Prisma.RED}► {log}{Prisma.RST}")
            elif any(k in log for k in b_kws):
                structured.append(f"{Prisma.CYN}• {log}{Prisma.RST}")
            elif any(k in log for k in t_kws):
                structured.append(f"{Prisma.CYN}📜 {log}{Prisma.RST}")
            elif any(k in log for k in p_kws):
                structured.append(f"{Prisma.MAG}🌷 {log}{Prisma.RST}")
            elif any(k in log for k in i_kws):
                structured.append(f"{Prisma.YEL}★ {log}{Prisma.RST}")
            else:
                structured.append(f"{Prisma.GRY}• {log}{Prisma.RST}")
        return structured

    def _punish_style_crime(self, log_msg):
        if hasattr(self.eng, "events"):
            self.eng.events.log(log_msg, "SYS")


class CachedRenderer:
    def __init__(self, base_renderer):
        self._base = base_renderer
        self._cache = {"dashboard": {"hash": 0, "content": ""}, "last_tick": -1}

    def render_frame(self, ctx, tick: int, events: List[Dict]) -> Dict:
        voltage = (
            ctx.physics.get("voltage", 0)
            if isinstance(ctx.physics, dict)
            else ctx.physics.voltage
        )
        if voltage > 15.0 or tick != self._cache["last_tick"]:
            frame = self._base.render_frame(ctx, tick, events)
            self._cache["dashboard"]["content"] = frame["ui"]
            self._cache["last_tick"] = tick
            return frame
        return {
            "type": "GEODESIC_FRAME",
            "ui": self._cache["dashboard"]["content"],
            "logs": self._base.compose_logs(ctx.logs, events, tick),
            "metrics": ctx.bio_result if hasattr(ctx, "bio_result") else {},
        }

def get_renderer(engine_ref, chroma_ref, strunk_ref, valve_ref=None, mode="STANDARD"):
    base = GeodesicRenderer(engine_ref, chroma_ref, strunk_ref, valve_ref)
    if mode == "PERFORMANCE":
        return CachedRenderer(base)
    return base


class AmbiguityDial:
    BOARDROOM = 0
    WORKSHOP = 1
    RED_TEAM = 2
    PALIMPSEST = 3


class TruthRenderer(GeodesicRenderer):
    def __init__(self, engine_ref):
        super().__init__(engine_ref, None, None)
        self.engine = engine_ref
        self.dial_setting = AmbiguityDial.BOARDROOM

    def render_truth(self, cortex_packet, council_log, trauma_cost):
        ui_text = cortex_packet.get("ui", "")

        h_board = LoreManifest.get_instance().get_ux(
            "truth_renderer", "boardroom_header"
        )
        h_work = LoreManifest.get_instance().get_ux("truth_renderer", "workshop_header")
        h_red = LoreManifest.get_instance().get_ux(
            "truth_renderer", "red_team_header"
        )
        h_pal = LoreManifest.get_instance().get_ux(
            "truth_renderer", "palimpsest_header"
        )

        if self.dial_setting == AmbiguityDial.BOARDROOM:
            return f"{Prisma.paint(h_board, 'W')}\n{ui_text}\n"
        elif self.dial_setting == AmbiguityDial.WORKSHOP:
            metrics = self.engine.get_metrics()
            l_conf = LoreManifest.get_instance().get_ux("truth_renderer", "workshop_confidence")
            l_drag = LoreManifest.get_instance().get_ux("truth_renderer", "workshop_drag")
            return (
                f"{Prisma.paint(h_work, 'C')}\n"
                f"{l_conf} {cortex_packet.get('truth_ratio', 0.95):.2%}\n"
                f"{l_drag} {metrics['stamina']:.1f}\n"
                f"---------------------\n{ui_text}\n"
            )

        elif self.dial_setting == AmbiguityDial.RED_TEAM:
            dissent = [l for l in council_log if "CRITIC" in l or "WARN" in l]
            l_warn = LoreManifest.get_instance().get_ux(
                "truth_renderer", "red_team_warning"
            )
            l_cost = LoreManifest.get_instance().get_ux("truth_renderer", "red_team_cost")
            l_conf = LoreManifest.get_instance().get_ux(
                "truth_renderer", "red_team_conflicts"
            )
            return (
                f"{Prisma.paint(h_red, 'R')}\n"
                f"{Prisma.paint(l_warn, 'Y')}\n"
                f"{l_cost} {trauma_cost:.1f} Trauma Units\n"
                f"{l_conf}\n" + "\n".join([f"  > {d}" for d in dissent]) + "\n"
                f"---------------------\n{ui_text}\n"
            )
        elif self.dial_setting == AmbiguityDial.PALIMPSEST:
            drafts = cortex_packet.get("drafts", [])
            layer_view = ""
            l_draft = LoreManifest.get_instance().get_ux("truth_renderer", "palimpsest_draft")
            l_redact = LoreManifest.get_instance().get_ux("truth_renderer", "palimpsest_redacted")
            l_final = LoreManifest.get_instance().get_ux(
                "truth_renderer", "palimpsest_final"
            )
            for i, draft in enumerate(drafts):
                layer_view += f"{Prisma.GRY}[{l_draft} {i}]: {draft} {Prisma.RED}{l_redact}{Prisma.RST}\n"
            return (
                f"{Prisma.paint(h_pal, 'M')}\n"
                f"{layer_view}"
                f"{Prisma.paint(l_final, 'W')}\n{ui_text}\n"
            )
        return None


class PulseReader:
    @staticmethod
    def derive_mood(bio_state: Dict) -> str:
        chem = bio_state.get("chem", {})
        if chem.get("COR", 0) > 0.6:
            return LoreManifest.get_instance().get_ux("pulse_reader", "mood_defensive")
        if chem.get("DA", 0) > 0.6:
            return LoreManifest.get_instance().get_ux("pulse_reader", "mood_manic")
        if chem.get("OXY", 0) > 0.6:
            return LoreManifest.get_instance().get_ux("pulse_reader", "mood_affectionate")
        atp = bio_state.get("mito", {}).get("atp", 100)
        if atp < 20:
            return LoreManifest.get_instance().get_ux("pulse_reader", "mood_exhausted")
        return LoreManifest.get_instance().get_ux("pulse_reader", "mood_neutral")

    @staticmethod
    def analyze_voltage(voltage: float) -> Tuple[str, str]:
        if voltage > 20.0:
            v_crit = LoreManifest.get_instance().get_ux("pulse_reader", "voltage_critical")
            return v_crit[0], v_crit[1]
        if voltage > 15.0:
            v_high = LoreManifest.get_instance().get_ux("pulse_reader", "voltage_high")
            return v_high[0], v_high[1]
        if voltage < 5.0:
            v_low = LoreManifest.get_instance().get_ux("pulse_reader", "voltage_low")
            return v_low[0], v_low[1]
        v_nom = LoreManifest.get_instance().get_ux("pulse_reader", "voltage_nominal")
        return v_nom[0], v_nom[1]


class SoulDashboard:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def render(self) -> str:
        if not hasattr(self.eng, "soul") or not self.eng.soul:
            return ""
        if not hasattr(self.eng.soul, "anchor"):
            return f"{Prisma.GRY}{LoreManifest.get_instance().get_ux('soul_dashboard', 'anchor_lost')}{Prisma.RST}"
        anchor = self.eng.soul.anchor
        soul = self.eng.soul
        dig = anchor.dignity_reserve
        if dig > 80:
            color = Prisma.GRN
        elif dig > 30:
            color = Prisma.OCHRE
        else:
            color = Prisma.RED
        filled = int(dig / 5)
        bar_str = f"{color}{'█' * filled}{Prisma.GRY}{'░' * (20 - filled)}{Prisma.RST}"

        lock_status = ""
        if anchor.agency_lock:
            lock_status = f" {Prisma.RED}{LoreManifest.get_instance().get_ux('soul_dashboard', 'agency_locked')}{Prisma.RST}"
        elif dig < 30:
            lock_status = f" {Prisma.OCHRE}{LoreManifest.get_instance().get_ux('soul_dashboard', 'fading')}{Prisma.RST}"

        arch = soul.archetype
        tenure = soul.archetype_tenure
        tenure_color = Prisma.GRY
        if tenure > 5:
            tenure_color = Prisma.OCHRE
        if tenure > 8:
            tenure_color = Prisma.RED
        arch_display = (
            f"{Prisma.CYN}{arch}{Prisma.RST} ({tenure_color}T:{tenure}{Prisma.RST})"
        )

        pet_icon = (
            LoreManifest.get_instance().get_ux("soul_dashboard", "pet_icon")
            if (dig < 50 and not anchor.agency_lock)
            else ""
        )
        muse = (
            soul.current_obsession
            if soul.current_obsession
            else LoreManifest.get_instance().get_ux("soul_dashboard", "default_muse")
        )

        l_soul = LoreManifest.get_instance().get_ux("soul_dashboard", "soul_prefix")
        l_driver = LoreManifest.get_instance().get_ux("soul_dashboard", "driver_prefix")
        l_muse = LoreManifest.get_instance().get_ux("soul_dashboard", "muse_prefix")

        line1 = f"{l_soul} {bar_str} {int(dig)}%{lock_status}{pet_icon}"
        line2 = f"      {l_driver} {arch_display}  {l_muse} {Prisma.VIOLET}{muse}{Prisma.RST}"
        return f"{line1}\n{line2}"


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
        if mode in self.renderers:
            self.renderer = self.renderers[mode]
            self.current_mode = mode
            return
        strunk_instance = None
        if hasattr(self.eng, "village") and isinstance(self.eng.village, dict):
            strunk_instance = self.eng.village.get("bureau")
        self.renderer = get_renderer(
            self.eng,
            self.vsl_chroma,
            strunk_instance,
            getattr(self, "valve", None),
            mode=mode,
        )
        self.renderers[mode] = self.renderer
        self.current_mode = mode

    def render_snapshot(self, ctx) -> Dict[str, Any]:
        try:
            if ctx.refusal_triggered and ctx.refusal_packet:
                return ctx.refusal_packet
            if ctx.is_bureaucratic:
                return self._package_bureaucracy(ctx)
            self._inject_diagnostics(ctx)
            self._inject_flux_readout(ctx)
            self._inject_somatic_pulse(ctx)
            return self.renderer.render_frame(
                ctx, self.eng.tick_count, self.eng.events.flush()
            )
        except Exception as e:
            l_crash = LoreManifest.get_instance().get_ux("cycle_reporter", "crash_prefix")
            return {
                "type": "CRITICAL_RENDER_FAIL",
                "ui": f"{Prisma.RED}{l_crash} {e}{Prisma.RST}",
                "logs": ctx.logs,
                "metrics": self.eng.get_metrics(),
            }

    def _inject_diagnostics(self, ctx):
        if hasattr(self.eng, "system_health"):
            fb = self.eng.system_health.flush_feedback()
            i_hint = LoreManifest.get_instance().get_ux("cycle_reporter", "diagnostic_hint_icon")
            i_warn = LoreManifest.get_instance().get_ux("cycle_reporter", "diagnostic_warn_icon")
            for h in fb["hints"]:
                ctx.logs.append(f"{Prisma.CYN}{i_hint} {h}{Prisma.RST}")
            for w in fb["warnings"]:
                ctx.logs.append(f"{Prisma.OCHRE}{i_warn} {w}{Prisma.RST}")

    def _inject_somatic_pulse(self, ctx):
        if not hasattr(self.eng, "somatic"):
            return
        qualia = self.eng.somatic.get_current_qualia(getattr(ctx, "last_impulse", None))
        ctx.logs.insert(
            0, f"{Prisma.GRY}({qualia.internal_monologue_hint}){Prisma.RST}"
        )
        l_sens = LoreManifest.get_instance().get_ux("cycle_reporter", "sensation_prefix")
        ctx.logs.insert(
            0,
            f"{qualia.color_code}{l_sens} {qualia.somatic_sensation} [{qualia.tone}]{Prisma.RST}",
        )

    @staticmethod
    def _inject_flux_readout(ctx):
        if not ctx.flux_log:
            return
        significant = []
        for e in ctx.flux_log[-5:]:
            d = abs(e["delta"])
            if d < 1.0 and "PID" in e["reason"]:
                continue
            icon = "⚡" if e["metric"].upper() == "VOLTAGE" else "⚓"
            color = Prisma.GRN if e["delta"] > 0 else Prisma.RED
            arrow = "▲" if e["delta"] > 0 else "▼"
            significant.append(
                f"   {Prisma.GRY}│{Prisma.RST} {icon} {e['metric'][:3].upper()} {color}{arrow} {d:.1f}{Prisma.RST} ({e['reason']})"
            )
        if significant:
            h_flux = LoreManifest.get_instance().get_ux("cycle_reporter", "flux_header")
            ctx.logs.insert(0, "")
            ctx.logs.insert(1, f" {Prisma.GRY}{h_flux}{Prisma.RST}")
            for line in reversed(significant):
                ctx.logs.insert(2, line)
            ctx.logs.insert(
                2 + len(significant), f" {Prisma.GRY}└{'─' * 15}{Prisma.RST}"
            )

    def _package_bureaucracy(self, ctx):
        if not self.eng.bureau:
            return None
        if ctx.is_bureaucratic or ctx.bureau_ui:
            base = (
                self.renderer.base_renderer
                if hasattr(self.renderer, "base_renderer")
                else self.renderer
            )
            bio_res = ctx.bio_result or {}
            return {
                "type": "BUREAUCRACY",
                "ui": ctx.bureau_ui,
                "logs": base.compose_logs(
                    ctx.logs, self.eng.events.flush(), self.eng.tick_count
                ),
                "metrics": self.eng.get_metrics(bio_res.get("atp", 0.0)),
            }
        return None
