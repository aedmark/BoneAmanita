"""bone_gui.py"""

import re
from typing import Any, Dict, List, Tuple

import markdown
from bone_core import Prisma, safe_get, ux
from bone_physics import ChromaScope
from bone_presets import BoneConfig


def render_markdown(text: str) -> str:
    return markdown.markdown(text, extensions=["extra"])


_THOUGHT_PATTERN = re.compile(r"<(?:think|thought)>(.*?)(?:</(?:think|thought)>|$)", re.DOTALL | re.IGNORECASE)


def beautify_thoughts(text: str) -> str:
    def replacer(match):
        if not (content := match.group(1).strip()): return ""
        inner = "\n".join(f"{Prisma.CYN}  │ {Prisma.GRY}{line.strip()}{Prisma.RST}" for line in content.split("\n") if line.strip())
        return f"<div class='substrate-block'>{Prisma.CYN}  ┌─ {Prisma.MAG}[ COGNITIVE SUBSTRATE ]{Prisma.RST}\n{inner}\n{Prisma.CYN}  └─{Prisma.RST}</div>"

    return _THOUGHT_PATTERN.sub(replacer, text)


class Projector:

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.width = 80

    @staticmethod
    def _safe_val(obj, k, default):
        try:
            return float(v) if (v := safe_get(obj, k)) is not None else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _extract(physics_obj: Any, field: str, sub_field: str, default: Any = 0.0):
        if (val := safe_get(physics_obj, sub_field)) is not None:
            return val
        if (val := safe_get(safe_get(physics_obj, field), sub_field)) is not None:
            return val
        return default

    def _render_clear_hud(self, physics: Any, data_ctx: Dict, mind: tuple) -> str:
        energy = float(data_ctx.get("stamina", 100.0))
        friction = self._get_lattice_val(physics, ["narrative_drag", "friction", "F"], 0.0)
        chem = data_ctx.get("bio", {}).get("chemistry", {})
        stress = min(100.0, (chem.get("COR", 0.0) * 100.0) + (chem.get("ADR", 0.0) * 50.0))
        phi = float(self._safe_val(data_ctx.get("shared_dyn", {}), "phi", 0.5))

        def bar(v, mx, col):
            f = int(max(0.0, min(1.0, v / mx if mx else 0)) * 10)
            return f"[{col}{'█'*f}{Prisma.GRY}{'░'*(10-f)}{Prisma.RST}]"

        e_txt = (
            "Healthy. Ready for complex tasks."
            if energy > 50
            else "Fatigued. Proceed with care." if energy > 20 else "Critical. Autophagy risk."
        )
        f_txt = (
            "Low. The current logic flows easily."
            if friction < 2.0
            else "Moderate. Bearing structural weight." if friction < 6.0 else "High. Heavy systemic drag."
        )
        s_txt = (
            "Nominal. No resting required."
            if stress < 30
            else "Elevated. Consider pacing." if stress < 70 else "High. Toxicity accumulating."
        )
        st_txt = (
            "Flow State. Highly aligned with your inputs."
            if phi >= 0.7
            else "Stable. Processing normally." if phi >= 0.4 else "Desynchronized. Friction expected."
        )
        return (
            f"\n{Prisma.CYN}### SYSTEM TELEMETRY{Prisma.RST}\n"
            f"{Prisma.WHT}Energy:  {Prisma.RST} {bar(energy, 100, Prisma.GRN)} {int(energy)}% {Prisma.GRY}({e_txt}){Prisma.RST}\n"
            f"{Prisma.WHT}Friction:{Prisma.RST} {bar(friction, 10, Prisma.CYN)} {friction:.1f} {Prisma.GRY}({f_txt}){Prisma.RST}\n"
            f"{Prisma.WHT}Stress:  {Prisma.RST} {bar(stress, 100, Prisma.OCHRE)} {int(stress)}% {Prisma.GRY}({s_txt}){Prisma.RST}\n"
            f"{Prisma.WHT}Status:  {Prisma.RST} {Prisma.MAG}{st_txt}{Prisma.RST}\n"
        )

    def render(
        self, physics_ctx: Dict, data_ctx: Dict, mind_ctx: tuple, reality_depth: int = 1, labels: Dict = None
    ) -> str:
        ui_depth = data_ctx.get("ui_depth", "IDLE")
        if ui_depth == "WARM":
            return ""
        if ui_depth == "MINIMAL":
            return self._render_clear_hud(physics_ctx.get("physics", {}), data_ctx, mind_ctx)
        if not labels:
            labels = ux("projector", "default_labels", {})
        physics = physics_ctx.get("physics", {})
        show_vitals = data_ctx.get("show_vitals", True)
        status_line = (
            self._render_vital_strip(data_ctx, mind_ctx, labels)
            if show_vitals
            else self._render_minimal_strip(mind_ctx)
        )
        physics_line = ""
        if labels.get("SHOW_PHYSICS", True):
            physics_line = self._render_physics_strip(physics, data_ctx.get("vectors", {}))
        vsl_line = self._render_lattice_strip(physics, data_ctx=data_ctx, depth=ui_depth)
        lens = mind_ctx[0] if mind_ctx and mind_ctx[0] else (ux("projector", "default_lens") or "RAW")
        depth_map = ux("projector", "depth_map", {})
        depth_label = depth_map.get(str(reality_depth), "?")
        depth_marker = f"{Prisma.VIOLET}[D{reality_depth}:{depth_label}]{Prisma.RST}"
        sym = ux("projector", "symbols", {})
        i_lens = sym.get("lens", "")
        i_div = sym.get("divider", "")
        loc_str = ""
        if data_ctx.get("show_location", True):
            zone = self._extract(physics, "space", "zone", ux("projector", "default_zone") or "UNKNOWN")
            loc_str = f"{sym.get('loc', '')} {data_ctx.get('world_loc', 'UNKNOWN').upper()[:20]} [{zone}]  "
        context_line = f"{Prisma.GRY}  {loc_str}{i_lens} {lens:<12}  {depth_marker}{Prisma.RST}"
        div = f"{Prisma.GRY}{i_div * self.width}{Prisma.RST}"
        mid_section = "\n".join(line for line in (physics_line, f"  {vsl_line}" if vsl_line else "") if line)
        return f"{div}\n{status_line}\n{mid_section}\n{context_line}\n{div}"

    @staticmethod
    def _get_role(mind: tuple) -> str:
        raw_role = mind[2] if mind and len(mind) > 2 else None
        role = str(raw_role).upper() if raw_role else (ux("projector", "default_role") or "OBSERVER")
        return role.replace(ux("projector", "role_redundancy") or "THE THE ", "THE ")

    @staticmethod
    def _render_minimal_strip(mind: tuple) -> str:
        sym = ux("projector", "symbols", {})
        return f"  {Prisma.WHT}{sym.get('role', '')} {Projector._get_role(mind)}{Prisma.RST}"

    def _render_vital_strip(self, data: Dict, mind: tuple, labels: Dict) -> str:
        max_h = float(getattr(self.cfg, "MAX_HEALTH", 100.0) or 100.0)
        max_s = float(getattr(self.cfg, "MAX_STAMINA", 100.0) or 100.0)
        cfg = getattr(self.cfg, "GUI", object())
        d_med = getattr(cfg, "DIGNITY_MED", 50.0)
        d_high = getattr(cfg, "DIGNITY_HIGH", 80.0)
        r_len = getattr(cfg, "ROLE_TRUNC_LEN", 30)
        health = float(data.get("health") or max_h)
        stamina = float(data.get("stamina") or max_s)
        atp = float(data.get("bio", {}).get("atp") or 0.0)
        dignity = float(data.get("dignity") or 100.0)
        hp_bar = self._mini_bar(health, max_h, 6, Prisma.RED)
        stm_bar = self._mini_bar(stamina, max_s, 6, Prisma.GRN)
        dig_color = Prisma.VIOLET if dignity > d_med else Prisma.GRY
        sym = ux("projector", "symbols", {})
        dig_icon = sym.get("dig_high", "") if dignity > d_high else sym.get("dig_low", "")
        role = self._get_role(mind)
        role = f"{role[:r_len - 3]}..." if len(role) > r_len else role
        l_hp = labels.get("HP", "HP")
        l_stm = labels.get("STM", "STM")
        i_role = sym.get("role", "")
        role_block = f"{Prisma.WHT}{i_role} {role}{Prisma.RST}"
        return (
            f"  {role_block:<35} "
            f"{l_hp} {hp_bar}  "
            f"{l_stm} {stm_bar}  "
            f"{dig_color}{dig_icon}{int(dignity)}%{Prisma.RST} "
            f"{Prisma.YEL}ATP:{int(atp)}{Prisma.RST}"
        )

    def _render_physics_strip(self, physics: Any, vectors: Dict) -> str:
        volt = float(self._extract(physics, "energy", "voltage", 0.0) or 0.0)
        drag = float(self._extract(physics, "space", "narrative_drag", 0.0) or 0.0)
        dp_str = ""
        if dp := safe_get(physics, "drag_profile"):
            parts = [
                f"{lbl}:{val:.1f}"
                for k, lbl in (
                    ("semantic", "Sem"),
                    ("metabolic", "Met"),
                    ("emotional", "Emo"),
                    ("structural", "Str"),
                    ("trauma", "Tra"),
                )
                if (val := float(safe_get(dp, k, 0.0) or 0.0)) > 0
            ]
            if parts:
                dp_str = f" [{Prisma.GRY}{'|'.join(parts)}{Prisma.RST}]"
        dom_vec = max(vectors, key=vectors.get) if vectors else "NEUTRAL"
        dom_val = float(vectors.get(dom_vec, 0.0) or 0.0) if vectors else 0.0
        return f"  {Prisma.CYN}VOLT:{Prisma.RST} {volt:04.1f}v   {Prisma.SLATE}DRAG:{Prisma.RST} {drag:04.1f}{dp_str}   {Prisma.MAG}VEC:{Prisma.RST} {dom_vec} ({dom_val:.2f})"

    def _get_lattice_val(self, domains: List[Any], keys: List[str], default: float) -> float:
        for k in keys:
            for dom in domains:
                if dom and (val := safe_get(dom, k)) is not None:
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        pass
        return default

    def _render_lattice_strip(self, physics: Any, data_ctx: Dict = None, depth: str = "DEEP") -> str:
        if depth == "IDLE" or not physics:
            return ""
        data_ctx = data_ctx or {}
        doms = [physics] + [safe_get(physics, sub) for sub in ("energy", "space", "matter")]
        E = self._get_lattice_val(doms, ["exhaustion", "E"], 0.2)
        beta = self._get_lattice_val(doms, ["beta_index", "contradiction", "beta"], 0.4)
        V = self._get_lattice_val(doms, ["voltage", "V"], 30.0)
        F = self._get_lattice_val(doms, ["narrative_drag", "friction", "F"], 0.6)
        H = self._get_lattice_val(doms, ["health", "H"], 100.0)
        P = max(0.0, self._get_lattice_val(doms, ["stamina", "P"], 100.0))
        T = self._get_lattice_val(doms, ["trauma", "T"], 0.0)
        psi = self._get_lattice_val(doms, ["psi", "PSI"], 0.0)
        chi = self._get_lattice_val(doms, ["entropy", "chi", "CHI"], 0.0)
        valence = self._get_lattice_val(doms, ["valence", "VALENCE"], 0.0)
        gamma = self._get_lattice_val(doms, ["gamma"], 0.0)
        sigma = self._get_lattice_val(doms, ["sigma"], 0.0)
        eta = self._get_lattice_val(doms, ["eta"], 0.0)
        theta = self._get_lattice_val(doms, ["theta"], 0.0)
        upsilon = self._get_lattice_val(doms, ["upsilon"], 0.0)
        sym = ux("projector", "symbols", {})
        i_core = sym.get("core", "")
        i_volt = sym.get("volt", "")
        i_hlth = sym.get("health", "")
        i_trau = sym.get("trauma", "")
        i_deep = sym.get("deep", "")
        core = f"{Prisma.CYN}[{i_core} E:{E:.2f} β:{beta:.2f} | {i_volt} V:{V:.0f} F:{F:.1f} | {i_hlth} H:{H:.0f} P:{P:.0f} | {i_trau} T:{T:.0f}]{Prisma.RST}"
        deep = f"{Prisma.VIOLET} [{i_deep} Ψ:{psi:.2f} Χ:{chi:.2f} ♥:{valence:.2f}]{Prisma.RST}"
        shared_str = ""
        if shared := data_ctx.get("shared_dyn"):
            phi = self._safe_val(shared, "phi", 0.5)
            delta = self._safe_val(shared, "delta", 0.0)
            g_pool = int(self._safe_val(shared, "g_pool", 0))
            sigma = int(self._safe_val(shared, "sigma_silence", 0))
            shared_str = f" {Prisma.INDIGO}[Φ:{phi:.2f} ∇:{delta:.2f} (Σ{sigma}) G:{g_pool}]{Prisma.RST}"
        paradox_str = ""
        paradox = data_ctx.get("paradox")
        if paradox and paradox.get("active"):
            y = float(paradox.get("yield") or 0.0)
            b_max = float(paradox.get("beta_max") or 0.0)
            paradox_str = f" {Prisma.MAG}[Πx: ACTIVE | Ω:{y:.0f} | β_max:{b_max:.2f}]{Prisma.RST}"
        strain = float(data_ctx.get("lattice_strain", 0.0))
        strain_color = Prisma.GRN if strain < 0.5 else Prisma.OCHRE if strain < 5.0 else Prisma.RED
        strain_str = f" {Prisma.GRY}[Q_n Strain:{strain_color}{strain:.2f}{Prisma.GRY}]{Prisma.RST}"
        slash_str = ""
        if gamma > 0 or sigma > 0 or eta > 0 or theta > 0 or upsilon > 0:
            slash_str = f" {Prisma.BLU}[SLASH Γ:{gamma:.1f} Σ:{sigma:.1f} Η:{eta:.1f} Θ:{theta:.1f} Υ:{upsilon:.1f}]{Prisma.RST}"
        return {
            "DEEP": core + deep + shared_str + paradox_str + strain_str + slash_str,
            "CORE": core + shared_str + strain_str + slash_str,
            "LITE": f"{Prisma.CYN}[{i_volt} V:{V:.0f}{f' | {i_hlth} H:{H:.0f} P:{P:.0f}' if data_ctx.get('show_vitals', True) else ''}]{Prisma.RST}{shared_str}",
        }.get(depth, "")

    def render_technical(self, physics: Dict, data: Dict, mind: tuple) -> str:
        v = self._extract(physics, "energy", "voltage", 0.0)
        d = self._extract(physics, "space", "narrative_drag", 0.0)
        vec = data.get("vectors", {})
        vec_str = ", ".join(f"{k}:{v:.2f}" for k, v in vec.items() if v > 0.01)
        h_tech = ux("technical_projector", "header") or "[TECHNICAL PROJECTOR]"
        l_phys = ux("technical_projector", "physics_label") or "Physics"
        l_vec = ux("technical_projector", "vectors_label") or "Vectors"
        l_bio = ux("technical_projector", "bio_dump_label") or "Bio Dump"
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
        sym = ux("projector", "symbols", {})
        c_fill = sym.get("bar_fill", "")
        c_empty = sym.get("bar_empty", "")
        return f"{color}{c_fill * fill}{Prisma.GRY}{c_empty * empty}{Prisma.RST}"


class GeodesicRenderer:

    def __init__(self, engine_ref, chroma_ref, strunk_ref, valve_ref=None):
        self.eng = engine_ref
        target_cfg = getattr(self.eng, "bone_config", BoneConfig)
        self.projector = Projector(config_ref=target_cfg)
        self.vsl_chroma = chroma_ref
        self.strunk_white = strunk_ref
        self.valve = valve_ref
        self.soul_dashboard = SoulDashboard(engine_ref)
        self.NOISE_PATTERNS = ux("renderer", "noise_patterns") or []

    def render_frame(self, ctx, tick: int, current_events: List[Dict]) -> Dict[str, Any]:
        physics = ctx.physics
        bio = ctx.bio_result
        raw_dashboard = self.render_dashboard(ctx)
        colored_ui = self.vsl_chroma.modulate(raw_dashboard, physics.get("vector", {}))
        clean_ui = colored_ui
        if self.strunk_white:
            clean_ui, style_log = self.strunk_white.sanitize(colored_ui)
            if style_log:
                self._punish_style_crime(style_log)

        ignore_msg = ux("renderer", "ignore_msg") or "The system is listening."
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
        mode_settings = getattr(self.eng, "mode_settings", {})
        world_loc = "OMNIPRESENT"
        if mode_settings.get("show_location", True):
            nav = getattr(self.eng, "navigator", None)
            world_loc = getattr(nav.world_graph.get(nav.current_node_id) if nav else None, "name", "UNKNOWN")
        current_ui_depth = getattr(
            self.eng, "ui_mode",
            self.eng.config.get("default_ui_depth", mode_settings.get("default_ui_depth", "WARM"))
        )
        if current_ui_depth == "IDLE":
            current_ui_depth = "WARM"
        data_ctx = {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "bio": bio_data,
            "dignity": (
                getattr(self.eng.soul.anchor, "dignity_reserve", 100.0) if hasattr(self.eng, "soul") else 100.0
            ),
            "vectors": physics.get("vector", {}),
            "ui_depth": current_ui_depth,
            "world_loc": world_loc,
            "show_vitals": mode_settings.get("show_vitals", True),
            "show_location": mode_settings.get("show_location", True),
        }
        if hasattr(ctx, "shared_dyn"):
            data_ctx.update({"shared_dyn": ctx.shared_dyn, "user_state": ctx.user_state})
        if pe := getattr(self.eng, "paradox_engine", None):
            data_ctx["paradox"] = {"active": pe.is_active, "yield": pe.paradox_yield, "beta_max": pe.beta_max}
        if c_state := getattr(getattr(self.eng, "consultant", None), "state", None):
            data_ctx["vsl"] = {
                "E": getattr(c_state, "E", 0.2),
                "B": getattr(c_state, "B", 0.4),
                "L": getattr(c_state, "L", 0.0),
                "O": getattr(c_state, "O", 1.0),
            }
        phys_obs = getattr(getattr(self.eng, "phys", None), "observer", None)
        q_matrix = getattr(phys_obs, "Q_n", None) if phys_obs else None
        strain = 0.0
        if isinstance(q_matrix, list) and q_matrix and isinstance(q_matrix[0], list):
            strain = sum(float(abs(v)) for i, row in enumerate(q_matrix) for j, v in enumerate(row) if i != j)
        data_ctx["lattice_strain"] = float(strain)
        mode = self.eng.config.get("boot_mode", "ADVENTURE").upper()
        current_depth = getattr(getattr(ctx, "reality_stack", None), "current_depth", 1)
        if mode == "TECHNICAL":
            return self.projector.render_technical(physics, data_ctx, mind_tuple)
        labels = ux("renderer", f"mode_labels_{mode.lower()}", ux("projector", "default_labels", {})).copy()
        labels["SHOW_PHYSICS"] = mode_settings.get("allow_metrics", False)
        return self.projector.render(
            {"physics": physics}, data_ctx, mind_tuple, reality_depth=current_depth, labels=labels
        )

    @staticmethod
    def render_soul_strip(soul_ref) -> str:
        if not soul_ref or not soul_ref.current_obsession:
            return ""
        strip_format = ux("soul_dashboard", "obsession_strip")
        formatted_strip = strip_format.replace("{obs}", str(soul_ref.current_obsession))
        return f"{Prisma.GRY}{formatted_strip}{Prisma.RST}"

    def compose_logs(self, logs: list, events: list, _tick: int = 0) -> List[str]:
        all_logs = [str(l) for l in logs if l is not None] + [e["text"] for e in events if e and e.get("text")]
        mode_settings = getattr(self.eng, "mode_settings", {}) if hasattr(self, "eng") else {}
        current_ui_depth = getattr(self.eng, "ui_mode", mode_settings.get("default_ui_depth", "WARM"))
        if current_ui_depth in ("IDLE", "WARM"):
            muted_tags = ("[BIO]", "[CRITIC]", "[SYS]", "[MERCY]", "(The system feels")
            all_logs = [l for l in all_logs if not any(tag in l for tag in muted_tags)]
        if not all_logs:
            return []
        unique_logs = list(
            dict.fromkeys(l for l in all_logs if not any(p in Prisma.strip(l).lower() for p in self.NOISE_PATTERNS))
        )
        structured = []
        prefixes = ux("log_composer", "log_prefixes") or {}
        mappings = [
            (ux("log_composer", "critical_keywords") or [], Prisma.RED, prefixes.get("critical", "► ")),
            (ux("log_composer", "bio_keywords") or [], Prisma.CYN, prefixes.get("bio", "• ")),
            (ux("log_composer", "town_hall_keywords") or [], Prisma.CYN, prefixes.get("town_hall", "📜 ")),
            (ux("log_composer", "paradox_keywords") or [], Prisma.MAG, prefixes.get("paradox", "🌷 ")),
            (ux("log_composer", "item_keywords") or [], Prisma.YEL, prefixes.get("item", "★ ")),
        ]
        for log in unique_logs:
            for kws, color, pref in mappings:
                if any(k in log for k in kws):
                    structured.append(f"{color}{pref}{log}{Prisma.RST}")
                    break
            else:
                structured.append(f"{Prisma.GRY}{prefixes.get('default', '• ')}{log}{Prisma.RST}")
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
        cfg = getattr(self.cfg, "GUI", object())
        if voltage > getattr(cfg, "HIGH_VOLTAGE_REFRESH", 15.0) or tick != self._last_tick:
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
    target_cfg = getattr(engine_ref, "bone_config", BoneConfig)
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

    def __init__(self, engine_ref):
        super().__init__(engine_ref, None, None)
        self.engine = engine_ref
        self.dial_setting = AmbiguityDial.BOARDROOM

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
            dissent = [l for l in council_log if "CRITIC" in l or "WARN" in l]
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


class PulseReader:

    @staticmethod
    def derive_mood(bio_state: Dict, config_ref=None) -> str:
        cfg = getattr(config_ref or BoneConfig, "GUI", object())
        c_warn, a_warn = getattr(cfg, "CHEM_HIGH_WARN", 0.6), getattr(cfg, "ATP_EXHAUSTED_WARN", 20.0)
        if mood := next(
            (
                m
                for h, m in (("COR", "defensive"), ("DA", "manic"), ("OXY", "affectionate"))
                if bio_state.get("chem", {}).get(h, 0) > c_warn
            ),
            None,
        ):
            return ux("pulse_reader", f"mood_{mood}")
        return ux(
            "pulse_reader", "mood_exhausted" if bio_state.get("mito", {}).get("atp", 100) < a_warn else "mood_neutral"
        )

    @staticmethod
    def analyze_voltage(voltage: float, config_ref=None) -> Tuple[str, str]:
        cfg = getattr(config_ref or BoneConfig, "GUI", object())
        key = (
            "voltage_critical"
            if voltage > getattr(cfg, "V_CRIT", 20.0)
            else (
                "voltage_high"
                if voltage > getattr(cfg, "V_HIGH", 15.0)
                else "voltage_low" if voltage < getattr(cfg, "V_LOW", 5.0) else "voltage_nominal"
            )
        )
        res = ux("pulse_reader", key)
        return res[0], res[1]


class SoulDashboard:

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.cfg = getattr(self.eng, "bone_config", BoneConfig)

    def render(self) -> str:
        if not (soul := getattr(self.eng, "soul", None)):
            return ""
        if not (anchor := getattr(soul, "anchor", None)):
            return f"{Prisma.GRY}{ux('soul_dashboard', 'anchor_lost') or 'No Anchor.'}{Prisma.RST}"
        dig = anchor.dignity_reserve
        cfg = getattr(self.cfg, "GUI", object())
        d_high = getattr(cfg, "DIGNITY_HIGH", 80.0)
        d_med = getattr(cfg, "DIGNITY_MED", 50.0)
        d_low = getattr(cfg, "DIGNITY_LOW", 30.0)
        d_ratio = getattr(cfg, "DIGNITY_BAR_RATIO", 5)
        t_warn = getattr(cfg, "TENURE_WARN", 5)
        t_crit = getattr(cfg, "TENURE_CRIT", 8)
        color = Prisma.GRN if dig > d_high else Prisma.OCHRE if dig > d_low else Prisma.RED
        filled = int(dig / d_ratio)
        c_fill, c_empty = ux("status_menu", "bar_filled"), ux("status_menu", "bar_empty")
        bar_str = f"{color}{c_fill * filled}{Prisma.GRY}{c_empty * (20 - filled)}{Prisma.RST}"
        lock_status = ""
        if anchor.agency_lock:
            lock_status = f" {Prisma.RED}{ux('soul_dashboard', 'agency_locked') or '[AGENCY LOCKED]'}{Prisma.RST}"
        elif dig < d_low:
            lock_status = f" {Prisma.OCHRE}{ux('soul_dashboard', 'fading') or '[FADING]'}{Prisma.RST}"
        arch, tenure = soul.archetype, soul.archetype_tenure
        tenure_color = Prisma.RED if tenure > t_crit else Prisma.OCHRE if tenure > t_warn else Prisma.GRY
        arch_display = f"{Prisma.CYN}{arch}{Prisma.RST} ({tenure_color}T:{tenure}{Prisma.RST})"
        pet_icon = ux("soul_dashboard", "pet_icon") if (dig < d_med and not anchor.agency_lock) else ""
        muse = (
            str(soul.current_obsession) if soul.current_obsession else (ux("soul_dashboard", "default_muse") or "None")
        )
        l_soul = ux("soul_dashboard", "soul_prefix") or "Soul:"
        l_driver = ux("soul_dashboard", "driver_prefix") or "Driver:"
        l_muse = ux("soul_dashboard", "muse_prefix") or "Muse:"
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
            if ctx.is_bureaucratic:
                return self._package_bureaucracy(ctx)
            self._inject_diagnostics(ctx)
            self._inject_flux_readout(ctx)
            self._inject_somatic_pulse(ctx)
            return self.renderer.render_frame(ctx, self.eng.tick_count, self.eng.events.flush())
        except Exception as e:
            l_crash = ux("cycle_reporter", "crash_prefix") or "CRITICAL FAILURE:"
            err_msg = f"{l_crash} {e}"
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
            fb, i_hint, i_warn = sh.flush_feedback(), ux("cycle_reporter", "diagnostic_hint_icon") or "[!]", ux("cycle_reporter", "diagnostic_warn_icon") or "[*]"
            ctx.logs.extend(f"{Prisma.CYN}{i_hint} {h}{Prisma.RST}" for h in fb["hints"])
            ctx.logs.extend(f"{Prisma.OCHRE}{i_warn} {w}{Prisma.RST}" for w in fb["warnings"])

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
        for e in ctx.flux_log[-5:]:
            d = abs(e["delta"])
            if d < 1.0 and "PID" in e["reason"]:
                continue
            icon = v_icon if e["metric"].upper() == "VOLTAGE" else d_icon
            color = Prisma.GRN if e["delta"] > 0 else Prisma.RED
            arrow = up_arr if e["delta"] > 0 else dn_arr
            significant.append(
                f"   {Prisma.GRY}{pipe}{Prisma.RST} {icon} {e['metric'][:3].upper()} {color}{arrow} {d:.1f}{Prisma.RST} ({e['reason']})"
            )
        if significant:
            h_flux = ux("cycle_reporter", "flux_header") or "SYSTEM FLUX DETECTED:"
            flux_block = (
                ["", f" {Prisma.GRY}{h_flux}{Prisma.RST}"] + significant + [f" {Prisma.GRY}{footer}{Prisma.RST}"]
            )
            ctx.logs[:0] = flux_block

    def _package_bureaucracy(self, ctx):
        if getattr(self.eng, "bureau", None) and (ctx.is_bureaucratic or ctx.bureau_ui):
            base = getattr(self.renderer, "base_renderer", self.renderer)
            return {
                "type": "BUREAUCRACY",
                "ui": ctx.bureau_ui,
                "logs": base.compose_logs(ctx.logs, self.eng.events.flush(), self.eng.tick_count),
                "metrics": self.eng.get_metrics((ctx.bio_result or {}).get("atp", 0.0)),
            }
        return None
