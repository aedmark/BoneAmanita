""" bone_gui.py """

import re
from typing import Dict, List, Any, Tuple
from bone_presets import BoneConfig
from bone_core import Prisma, ux
from bone_physics import ChromaScope


def beautify_thoughts(text: str) -> str:
    def replacer(match):
        content = match.group(1).strip()
        if not content:
            return ""
        lines = content.split('\n')
        formatted_lines = [f"{Prisma.CYN}  │ {Prisma.GRY}{line.strip()}{Prisma.RST}" for line in lines if line.strip()]
        header = f"{Prisma.CYN}  ┌─ {Prisma.MAG}[ COGNITIVE SUBSTRATE ]{Prisma.RST}"
        footer = f"{Prisma.CYN}  └─{Prisma.RST}"
        return f"{header}\n" + "\n".join(formatted_lines) + f"\n{footer}"

    pattern = re.compile(r"<(?:think|thought)>(.*?)(?:</(?:think|thought)>|$)", re.DOTALL | re.IGNORECASE)
    return pattern.sub(replacer, text)


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

    def render(self, physics_ctx: Dict, data_ctx: Dict, mind_ctx: tuple, reality_depth: int = 1,
               labels: Dict = None, ) -> str:
        ui_depth = data_ctx.get("ui_depth", "IDLE")
        if ui_depth == "WARM":
            return ""
        if not labels:
            labels = ux("projector", "default_labels", {})
        physics = physics_ctx.get("physics", {})
        show_vitals = data_ctx.get("show_vitals", True)
        status_line = self._render_vital_strip(data_ctx, mind_ctx,
                                               labels) if show_vitals else self._render_minimal_strip(mind_ctx)
        physics_line = ""
        if labels.get("SHOW_PHYSICS", True):
            physics_line = self._render_physics_strip(physics, data_ctx.get("vectors", {}))
        ui_depth = data_ctx.get("ui_depth", "IDLE")
        vsl_line = self._render_lattice_strip(physics, data_ctx=data_ctx, depth=ui_depth)
        lens = mind_ctx[0] if mind_ctx and mind_ctx[0] else (ux("projector", "default_lens") or "RAW")
        depth_map = ux("projector", "depth_map", {})
        depth_label = depth_map.get(str(reality_depth), "?")
        depth_marker = f"{Prisma.VIOLET}[D{reality_depth}:{depth_label}]{Prisma.RST}"
        sym = ux("projector", "symbols", {})
        i_lens = sym.get("lens", "")
        i_div = sym.get("divider", "")
        show_location = data_ctx.get("show_location", True)
        if show_location:
            zone = self._extract(
                physics, "space", "zone", ux("projector", "default_zone") or "UNKNOWN")
            world_loc = data_ctx.get("world_loc", "UNKNOWN")
            display_loc = f"{world_loc.upper()[:20]} [{zone}]"
            i_loc = sym.get("loc", "")
            context_line = f"{Prisma.GRY}  {i_loc} {display_loc:<25}  {i_lens} {lens:<12}  {depth_marker}{Prisma.RST}"
        else:
            context_line = f"{Prisma.GRY}  {i_lens} {lens:<12}  {depth_marker}{Prisma.RST}"
        div = f"{Prisma.GRY}{i_div * self.width}{Prisma.RST}"
        mid_lines = []
        if physics_line:
            mid_lines.append(physics_line)
        if vsl_line:
            mid_lines.append("  " + vsl_line)
        mid_section = "\n".join(mid_lines) if mid_lines else ""
        return f"{div}\n{status_line}\n{mid_section}\n{context_line}\n{div}"

    @staticmethod
    def _render_minimal_strip(mind: tuple) -> str:
        sym = ux("projector", "symbols", {})
        raw_role = mind[2] if mind and len(mind) > 2 else None
        role = (str(raw_role).upper()
                if raw_role
                else (ux("projector", "default_role") or "OBSERVER"))
        role = role.replace(ux("projector", "role_redundancy") or "THE THE ", "THE ")
        i_role = sym.get("role", "")
        return f"  {Prisma.WHT}{i_role} {role}{Prisma.RST}"

    def _render_vital_strip(self, data: Dict, mind: tuple, labels: Dict) -> str:
        max_h = float(getattr(BoneConfig, "MAX_HEALTH", 100.0) or 100.0)
        max_s = float(getattr(BoneConfig, "MAX_STAMINA", 100.0) or 100.0)
        cfg = getattr(BoneConfig, "GUI", None)
        d_med = getattr(cfg, "DIGNITY_MED", 50.0) if cfg else 50.0
        d_high = getattr(cfg, "DIGNITY_HIGH", 80.0) if cfg else 80.0
        r_len = getattr(cfg, "ROLE_TRUNC_LEN", 30) if cfg else 30
        health = float(data.get("health") or max_h)
        stamina = float(data.get("stamina") or max_s)
        atp = float(data.get("bio", {}).get("atp") or 0.0)
        dignity = float(data.get("dignity") or 100.0)
        hp_bar = self._mini_bar(health, max_h, 6, Prisma.RED)
        stm_bar = self._mini_bar(stamina, max_s, 6, Prisma.GRN)
        dig_color = Prisma.VIOLET if dignity > d_med else Prisma.GRY
        sym = ux("projector", "symbols", {})
        dig_icon = sym.get("dig_high", "") if dignity > d_high else sym.get("dig_low", "")
        raw_role = mind[2] if mind and len(mind) > 2 else None
        role = (str(raw_role).upper()
                if raw_role
                else (ux("projector", "default_role") or "OBSERVER"))
        role = role.replace(ux("projector", "role_redundancy") or "THE THE ", "THE ")
        if len(role) > r_len:
            role = role[:r_len - 3] + "..."
        l_hp = labels.get("HP", "HP")
        l_stm = labels.get("STM", "STM")
        i_role = sym.get("role", "")
        role_block = f"{Prisma.WHT}{i_role} {role}{Prisma.RST}"
        return (f"  {role_block:<35} "
                f"{l_hp} {hp_bar}  "
                f"{l_stm} {stm_bar}  "
                f"{dig_color}{dig_icon}{int(dignity)}%{Prisma.RST} "
                f"{Prisma.YEL}ATP:{int(atp)}{Prisma.RST}")

    def _render_physics_strip(self, physics: Any, vectors: Dict) -> str:
        volt = float(self._extract(physics, "energy", "voltage", 0.0) or 0.0)
        drag = float(self._extract(physics, "space", "narrative_drag", 0.0) or 0.0)
        drag_profile_str = ""
        if hasattr(physics, "drag_profile") or (isinstance(physics, dict) and "drag_profile" in physics):
            dp = getattr(physics, "drag_profile", None) or physics.get("drag_profile", {})
            sem = float(getattr(dp, "semantic", 0.0) if hasattr(dp, "semantic") else dp.get("semantic", 0.0) or 0.0)
            met = float(getattr(dp, "metabolic", 0.0) if hasattr(dp, "metabolic") else dp.get("metabolic", 0.0) or 0.0)
            emo = float(getattr(dp, "emotional", 0.0) if hasattr(dp, "emotional") else dp.get("emotional", 0.0) or 0.0)
            struc = float(
                getattr(dp, "structural", 0.0) if hasattr(dp, "structural") else dp.get("structural", 0.0) or 0.0)
            tra = float(getattr(dp, "trauma", 0.0) if hasattr(dp, "trauma") else dp.get("trauma", 0.0) or 0.0)
            parts = []
            if sem > 0: parts.append(f"Sem:{sem:.1f}")
            if met > 0: parts.append(f"Met:{met:.1f}")
            if emo > 0: parts.append(f"Emo:{emo:.1f}")
            if struc > 0: parts.append(f"Str:{struc:.1f}")
            if tra > 0: parts.append(f"Tra:{tra:.1f}")
            if parts:
                drag_profile_str = f" [{Prisma.GRY}{'|'.join(parts)}{Prisma.RST}]"
        dom_vec = "NEUTRAL"
        dom_val = 0.0
        if vectors:
            dom_vec = max(vectors, key=vectors.get)
            dom_val = float(vectors.get(dom_vec, 0.0) or 0.0)
        return (f"  {Prisma.CYN}VOLT:{Prisma.RST} {volt:04.1f}v   "
                f"{Prisma.SLATE}DRAG:{Prisma.RST} {drag:04.1f}{drag_profile_str}   "
                f"{Prisma.MAG}VEC:{Prisma.RST} {dom_vec} ({dom_val:.2f})")

    @staticmethod
    def _render_lattice_strip(physics: Any, data_ctx: Dict = None, depth: str = "DEEP") -> str:
        if depth == "IDLE" or not physics:
            return ""
        if data_ctx is None:
            data_ctx = {}

        def _get_val(keys, default_val):
            val = None
            if isinstance(physics, dict):
                for k in keys:
                    if k in physics and physics[k] is not None:
                        val = physics[k]
                        break
                    for sub in ["energy", "space", "matter"]:
                        if sub in physics and k in physics[sub] and physics[sub][k] is not None:
                            val = physics[sub][k]
                            break
                    if val is not None: break
            else:
                for k in keys:
                    if hasattr(physics, k) and getattr(physics, k) is not None:
                        val = getattr(physics, k)
                        break
                    for sub in ["energy", "space", "matter"]:
                        if hasattr(physics, sub) and hasattr(getattr(physics, sub), k) and getattr(
                                getattr(physics, sub), k) is not None:
                            val = getattr(getattr(physics, sub), k)
                            break
                    if val is not None: break
            if val is None:
                return default_val
            try:
                return float(val)
            except (ValueError, TypeError):
                return default_val

        E = _get_val(["exhaustion", "E"], 0.2)
        beta = _get_val(["beta_index", "contradiction", "beta"], 0.4)
        V = _get_val(["voltage", "V"], 30.0)
        F = _get_val(["narrative_drag", "friction", "F"], 0.6)
        H = _get_val(["health", "H"], 100.0)
        P = max(0.0, _get_val(["stamina", "P"], 100.0))
        T = _get_val(["trauma", "T"], 0.0)
        psi = _get_val(["psi", "PSI"], 0.0)
        chi = _get_val(["entropy", "chi", "CHI"], 0.0)
        valence = _get_val(["valence", "VALENCE"], 0.0)
        sym = ux("projector", "symbols", {})
        i_core = sym.get("core", "")
        i_volt = sym.get("volt", "")
        i_hlth = sym.get("health", "")
        i_trau = sym.get("trauma", "")
        i_deep = sym.get("deep", "")
        core = f"{Prisma.CYN}[{i_core} E:{E:.2f} β:{beta:.2f} | {i_volt} V:{V:.0f} F:{F:.1f} | {i_hlth} H:{H:.0f} P:{P:.0f} | {i_trau} T:{T:.0f}]{Prisma.RST}"
        deep = f"{Prisma.VIOLET} [{i_deep} Ψ:{psi:.2f} Χ:{chi:.2f} ♥:{valence:.2f}]{Prisma.RST}"
        shared_str = ""
        shared = data_ctx.get("shared_dyn")
        if shared:
            def _safe_val(obj, k, default):
                v = getattr(obj, k, None) if hasattr(obj, k) else obj.get(k) if isinstance(obj, dict) else None
                if v is None: return default
                try:
                    return float(v)
                except (ValueError, TypeError):
                    return default
            phi = _safe_val(shared, "phi", 0.5)
            delta = _safe_val(shared, "delta", 0.0)
            g_pool = int(_safe_val(shared, "g_pool", 0))
            sigma = int(_safe_val(shared, "sigma_silence", 0))
            shared_str = f" {Prisma.INDIGO}[Φ:{phi:.2f} ∇:{delta:.2f} (Σ{sigma}) G:{g_pool}]{Prisma.RST}"
        paradox_str = ""
        paradox = data_ctx.get("paradox")
        if paradox and paradox.get("active"):
            y = float(paradox.get("yield") or 0.0)
            b_max = float(paradox.get("beta_max") or 0.0)
            paradox_str = f" {Prisma.MAG}[Πx: ACTIVE | Ω:{y:.0f} | β_max:{b_max:.2f}]{Prisma.RST}"
        strain = float(data_ctx.get("lattice_strain", 0.0))
        if strain < 0.5:
            strain_color = Prisma.GRN
        elif strain < 5.0:
            strain_color = Prisma.OCHRE
        else:
            strain_color = Prisma.RED
        strain_str = f" {Prisma.GRY}[Q_n Strain:{strain_color}{strain:.2f}{Prisma.GRY}]{Prisma.RST}"
        if depth == "DEEP":
            return core + deep + shared_str + paradox_str + strain_str
        elif depth == "CORE":
            return core + shared_str + strain_str
        elif depth == "LITE":
            if data_ctx.get("show_vitals", True):
                return f"{Prisma.CYN}[{i_volt} V:{V:.0f} | {i_hlth} H:{H:.0f} P:{P:.0f}]{Prisma.RST}" + shared_str
            return f"{Prisma.CYN}[{i_volt} V:{V:.0f}]{Prisma.RST}" + shared_str
        return ""

    def render_technical(self, physics: Dict, data: Dict, mind: tuple) -> str:
        v = self._extract(physics, "energy", "voltage", 0.0)
        d = self._extract(physics, "space", "narrative_drag", 0.0)
        vec = data.get("vectors", {})
        vec_str = ", ".join([f"{k}:{v:.2f}" for k, v in vec.items() if v > 0.01])
        h_tech = ux("technical_projector", "header") or "[TECHNICAL PROJECTOR]"
        l_phys = ux("technical_projector", "physics_label") or "Physics"
        l_vec = ux("technical_projector", "vectors_label") or "Vectors"
        l_bio = ux("technical_projector", "bio_dump_label") or "Bio Dump"
        return (f"{Prisma.CYN}{h_tech}{Prisma.RST}\n"
                f"{l_phys} V={v:<6.3f} D={d:<6.3f} | LENS: {mind[0]}\n"
                f"{l_vec} [{vec_str}]\n"
                f"{l_bio} {str(data.get('bio', {}))[:60]}...")

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
        self.projector = Projector()
        self.vsl_chroma = chroma_ref
        self.strunk_white = strunk_ref
        self.valve = valve_ref
        self.soul_dashboard = SoulDashboard(engine_ref)
        self.NOISE_PATTERNS = ux("renderer", "noise_patterns") or []

    def render_frame(
            self, ctx, tick: int, current_events: List[Dict]) -> Dict[str, Any]:
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
        ignore_msg = ux("renderer", "ignore_msg") or "The system is listening."
        if ignore_msg in clean_ui:
            clean_ui = clean_ui.replace(ignore_msg, "")
        structured_logs = self.compose_logs(ctx.logs, current_events, tick)
        return {"type": "GEODESIC_FRAME", "ui": clean_ui, "logs": structured_logs,
                "metrics": self.eng.get_metrics(bio.get("atp", 0.0)), }

    def render_dashboard(self, ctx) -> str:
        physics = ctx.physics
        mind = ctx.mind_state
        mind_tuple = (mind.get("lens"), mind.get("thought"), mind.get("role"))
        bio_data = ctx.bio_result or {}
        metrics = self.eng.get_metrics()
        bio_data["atp"] = metrics.get("atp", 0.0)
        mode_settings = self.eng.config.get("mode_settings", {})
        world_loc = "UNKNOWN"
        if mode_settings.get("show_location", True):
            if hasattr(self.eng, "navigator") and self.eng.navigator:
                node = self.eng.navigator.world_graph.get(self.eng.navigator.current_node_id)
                if node:
                    world_loc = node.name
        else:
            world_loc = "OMNIPRESENT"
        data_ctx = {"health": self.eng.health, "stamina": self.eng.stamina, "bio": bio_data, "dignity": (
            getattr(self.eng.soul.anchor, "dignity_reserve", 100.0) if hasattr(self.eng, "soul") else 100.0),
                    "vectors": physics.get("vector", {}), "ui_depth": mode_settings.get("default_ui_depth", "IDLE"),
                    "world_loc": world_loc, "show_vitals": mode_settings.get("show_vitals", True),
                    "show_location": mode_settings.get("show_location", True)}
        if hasattr(ctx, "shared_dyn"):
            data_ctx["shared_dyn"] = ctx.shared_dyn
            data_ctx["user_state"] = ctx.user_state
        if hasattr(self.eng, "paradox_engine"):
            data_ctx["paradox"] = {"active": self.eng.paradox_engine.is_active,
                                   "yield": self.eng.paradox_engine.paradox_yield,
                                   "beta_max": self.eng.paradox_engine.beta_max}
        consultant = getattr(self.eng, "consultant", None)
        if consultant and getattr(consultant, "state", None):
            c_state = consultant.state
            data_ctx["vsl"] = {"E": getattr(c_state, "E", 0.2), "B": getattr(c_state, "B", 0.4),
                               "L": getattr(c_state, "L", 0.0), "O": getattr(c_state, "O", 1.0)}
        q_matrix = None
        phys = getattr(self.eng, "phys", None)
        if phys:
            observer = getattr(phys, "observer", None)
            if observer:
                q_matrix = getattr(observer, "Q_n", None)
        strain = 0.0
        if isinstance(q_matrix, list) and len(q_matrix) > 0 and isinstance(q_matrix[0], list):
            strain = sum(
                float(abs(q_matrix[i][j]))
                for i in range(len(q_matrix))
                for j in range(len(q_matrix[0]))
                if i != j)
        data_ctx["lattice_strain"] = float(strain)
        mode = self.eng.config.get("boot_mode", "ADVENTURE").upper()
        current_depth = 1
        if hasattr(ctx, "reality_stack"):
            current_depth = ctx.reality_stack.current_depth
        if mode == "TECHNICAL":
            return self.projector.render_technical(physics, data_ctx, mind_tuple)
        labels = ux("projector", "default_labels", {}).copy()
        if mode == "CONVERSATION":
            labels = ux("renderer", "mode_labels_conversation", {}).copy()
        elif mode == "CREATIVE":
            labels = ux("renderer", "mode_labels_creative", {}).copy()
        labels["SHOW_PHYSICS"] = mode_settings.get("allow_metrics", False)
        return self.projector.render({"physics": physics}, data_ctx, mind_tuple, reality_depth=current_depth, labels=labels)

    @staticmethod
    def render_soul_strip(soul_ref) -> str:
        if not soul_ref:
            return ""
        if not soul_ref.current_obsession:
            return ""
        strip_format = ux("soul_dashboard", "obsession_strip")
        formatted_strip = strip_format.replace("{obs}", str(soul_ref.current_obsession))
        return f"{Prisma.GRY}{formatted_strip}{Prisma.RST}"

    def compose_logs(self, logs: list, events: list, _tick: int = 0) -> List[str]:
        all_logs = [str(l) for l in logs if l is not None]
        for e in events:
            if e and e.get("text"):
                all_logs.append(e["text"])
        mode_settings = self.eng.config.get("mode_settings", {}) if hasattr(self, "eng") else {}
        if mode_settings.get("default_ui_depth", "IDLE") == "WARM":
            muted_tags = ["[BIO]", "[CRITIC]", "[SYS]", "[MERCY]", "(The system feels"]
            all_logs = [l for l in all_logs if not any(tag in l for tag in muted_tags)]
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
        c_kws = ux("log_composer", "critical_keywords")
        b_kws = ux("log_composer", "bio_keywords")
        t_kws = ux("log_composer", "town_hall_keywords")
        p_kws = ux("log_composer", "paradox_keywords")
        i_kws = ux("log_composer", "item_keywords")
        prefixes = ux("log_composer", "log_prefixes")
        for log in unique_logs:
            if any(k in log for k in c_kws):
                structured.append(f"{Prisma.RED}{prefixes.get('critical', '► ')}{log}{Prisma.RST}")
            elif any(k in log for k in b_kws):
                structured.append(f"{Prisma.CYN}{prefixes.get('bio', '• ')}{log}{Prisma.RST}")
            elif any(k in log for k in t_kws):
                structured.append(f"{Prisma.CYN}{prefixes.get('town_hall', '📜 ')}{log}{Prisma.RST}")
            elif any(k in log for k in p_kws):
                structured.append(f"{Prisma.MAG}{prefixes.get('paradox', '🌷 ')}{log}{Prisma.RST}")
            elif any(k in log for k in i_kws):
                structured.append(f"{Prisma.YEL}{prefixes.get('item', '★ ')}{log}{Prisma.RST}")
            else:
                structured.append(f"{Prisma.GRY}{prefixes.get('default', '• ')}{log}{Prisma.RST}")
        return structured

    def _punish_style_crime(self, log_msg):
        if hasattr(self.eng, "events"):
            self.eng.events.log(log_msg, "SYS")

class CachedRenderer:
    def __init__(self, base_renderer):
        self._base = base_renderer
        self._cached_ui_content = ""
        self._last_tick = -1

    def render_frame(self, ctx, tick: int, events: List[Dict]) -> Dict:
        voltage = (
            ctx.physics.get("voltage", 0)
            if isinstance(ctx.physics, dict)
            else ctx.physics.voltage)
        cfg = getattr(BoneConfig, "GUI", None)
        v_refresh = getattr(cfg, "HIGH_VOLTAGE_REFRESH", 15.0) if cfg else 15.0
        if voltage > v_refresh or tick != self._last_tick:
            frame = self._base.render_frame(ctx, tick, events)
            self._cached_ui_content = frame["ui"]
            self._last_tick = tick
            return frame
        return {"type": "GEODESIC_FRAME", "ui": self._cached_ui_content,
                "logs": self._base.compose_logs(ctx.logs, events, tick),
                "metrics": ctx.bio_result if hasattr(ctx, "bio_result") else {}, }

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
            return (f"{Prisma.paint(h_work, 'C')}\n"
                    f"{l_conf} {cortex_packet.get('truth_ratio', 0.95):.2%}\n"
                    f"{l_drag} {metrics['stamina']:.1f}\n"
                    f"---------------------\n{ui_text}\n")
        elif self.dial_setting == AmbiguityDial.RED_TEAM:
            dissent = [l for l in council_log if "CRITIC" in l or "WARN" in l]
            l_warn = ux("truth_renderer", "red_team_warning")
            l_cost = ux("truth_renderer", "red_team_cost")
            l_conf = ux("truth_renderer", "red_team_conflicts")
            return (f"{Prisma.paint(h_red, 'R')}\n"
                    f"{Prisma.paint(l_warn, 'Y')}\n"
                    f"{l_cost} {trauma_cost:.1f} Trauma Units\n"
                    f"{l_conf}\n" + "\n".join(
                [f"  > {d}" for d in dissent]) + "\n" f"---------------------\n{ui_text}\n")
        elif self.dial_setting == AmbiguityDial.PALIMPSEST:
            drafts = cortex_packet.get("drafts", [])
            layer_view = ""
            l_draft = ux("truth_renderer", "palimpsest_draft")
            l_redact = ux("truth_renderer", "palimpsest_redacted")
            l_final = ux("truth_renderer", "palimpsest_final")
            for i, draft in enumerate(drafts):
                layer_view += f"{Prisma.GRY}[{l_draft} {i}]: {draft} {Prisma.RED}{l_redact}{Prisma.RST}\n"
            return (f"{Prisma.paint(h_pal, 'M')}\n"
                    f"{layer_view}"
                    f"{Prisma.paint(l_final, 'W')}\n{ui_text}\n")
        return None

class PulseReader:
    @staticmethod
    def derive_mood(bio_state: Dict) -> str:
        cfg = getattr(BoneConfig, "GUI", None)
        c_warn = getattr(cfg, "CHEM_HIGH_WARN", 0.6) if cfg else 0.6
        a_warn = getattr(cfg, "ATP_EXHAUSTED_WARN", 20.0) if cfg else 20.0
        chem = bio_state.get("chem", {})
        if chem.get("COR", 0) > c_warn:
            return ux("pulse_reader", "mood_defensive")
        if chem.get("DA", 0) > c_warn:
            return ux("pulse_reader", "mood_manic")
        if chem.get("OXY", 0) > c_warn:
            return ux("pulse_reader", "mood_affectionate")
        atp = bio_state.get("mito", {}).get("atp", 100)
        if atp < a_warn:
            return ux("pulse_reader", "mood_exhausted")
        return ux("pulse_reader", "mood_neutral")

    @staticmethod
    def analyze_voltage(voltage: float) -> Tuple[str, str]:
        cfg = getattr(BoneConfig, "GUI", None)
        v_crit_t = getattr(cfg, "V_CRIT", 20.0) if cfg else 20.0
        v_high_t = getattr(cfg, "V_HIGH", 15.0) if cfg else 15.0
        v_low_t = getattr(cfg, "V_LOW", 5.0) if cfg else 5.0
        if voltage > v_crit_t:
            v_crit = ux("pulse_reader", "voltage_critical")
            return v_crit[0], v_crit[1]
        if voltage > v_high_t:
            v_high = ux("pulse_reader", "voltage_high")
            return v_high[0], v_high[1]
        if voltage < v_low_t:
            v_low = ux("pulse_reader", "voltage_low")
            return v_low[0], v_low[1]
        v_nom = ux("pulse_reader", "voltage_nominal")
        return v_nom[0], v_nom[1]

class SoulDashboard:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def render(self) -> str:
        if not hasattr(self.eng, "soul") or not self.eng.soul:
            return ""
        if not hasattr(self.eng.soul, "anchor"):
            return f"{Prisma.GRY}{ux('soul_dashboard', 'anchor_lost') or 'No Anchor.'}{Prisma.RST}"
        anchor = self.eng.soul.anchor
        soul = self.eng.soul
        dig = anchor.dignity_reserve
        cfg = getattr(BoneConfig, "GUI", None)
        d_high = getattr(cfg, "DIGNITY_HIGH", 80.0) if cfg else 80.0
        d_med = getattr(cfg, "DIGNITY_MED", 50.0) if cfg else 50.0
        d_low = getattr(cfg, "DIGNITY_LOW", 30.0) if cfg else 30.0
        d_ratio = getattr(cfg, "DIGNITY_BAR_RATIO", 5) if cfg else 5
        t_warn = getattr(cfg, "TENURE_WARN", 5) if cfg else 5
        t_crit = getattr(cfg, "TENURE_CRIT", 8) if cfg else 8
        if dig > d_high:
            color = Prisma.GRN
        elif dig > d_low:
            color = Prisma.OCHRE
        else:
            color = Prisma.RED
        filled = int(dig / d_ratio)
        c_fill = ux("status_menu", "bar_filled")
        c_empty = ux("status_menu", "bar_empty")
        bar_str = f"{color}{c_fill * filled}{Prisma.GRY}{c_empty * (20 - filled)}{Prisma.RST}"
        lock_status = ""
        if anchor.agency_lock:
            lock_status = f" {Prisma.RED}{ux('soul_dashboard', 'agency_locked') or '[AGENCY LOCKED]'}{Prisma.RST}"
        elif dig < d_low:
            lock_status = f" {Prisma.OCHRE}{ux('soul_dashboard', 'fading') or '[FADING]'}{Prisma.RST}"
        arch = soul.archetype
        tenure = soul.archetype_tenure
        tenure_color = Prisma.GRY
        if tenure > t_warn:
            tenure_color = Prisma.OCHRE
        if tenure > t_crit:
            tenure_color = Prisma.RED
        arch_display = (
            f"{Prisma.CYN}{arch}{Prisma.RST} ({tenure_color}T:{tenure}{Prisma.RST})")
        pet_icon = (
            ux("soul_dashboard", "pet_icon")
            if (dig < d_med and not anchor.agency_lock)
            else "")
        muse = (str(soul.current_obsession)
                if soul.current_obsession
                else (ux("soul_dashboard", "default_muse") or "None"))
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
        if mode in self.renderers:
            self.renderer = self.renderers[mode]
            self.current_mode = mode
            return
        strunk_instance = None
        if hasattr(self.eng, "village") and isinstance(self.eng.village, dict):
            strunk_instance = self.eng.village.get("bureau")
        self.renderer = get_renderer(self.eng, self.vsl_chroma, strunk_instance, getattr(self, "valve", None), mode=mode)
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
            return self.renderer.render_frame(ctx, self.eng.tick_count, self.eng.events.flush())
        except Exception as e:
            l_crash = ux("cycle_reporter", "crash_prefix") or "CRITICAL FAILURE:"
            return {"type": "CRITICAL_RENDER_FAIL", "ui": f"{Prisma.RED}{l_crash} {e}{Prisma.RST}", "logs": ctx.logs,
                    "metrics": self.eng.get_metrics(), }

    def _inject_diagnostics(self, ctx):
        if hasattr(self.eng, "system_health"):
            fb = self.eng.system_health.flush_feedback()
            i_hint = ux("cycle_reporter", "diagnostic_hint_icon") or "[!]"
            i_warn = ux("cycle_reporter", "diagnostic_warn_icon") or "[*]"
            for h in fb["hints"]:
                ctx.logs.append(f"{Prisma.CYN}{i_hint} {h}{Prisma.RST}")
            for w in fb["warnings"]:
                ctx.logs.append(f"{Prisma.OCHRE}{i_warn} {w}{Prisma.RST}")

    def _inject_somatic_pulse(self, ctx):
        if not hasattr(self.eng, "somatic"):
            return
        qualia = self.eng.somatic.get_current_qualia(getattr(ctx, "last_impulse", None))
        ctx.logs.insert(0, f"{Prisma.GRY}({qualia.internal_monologue_hint}){Prisma.RST}")
        l_sens = ux("cycle_reporter", "sensation_prefix") or "Felt:"
        ctx.logs.insert(0, f"{qualia.color_code}{l_sens} {qualia.somatic_sensation} [{qualia.tone}]{Prisma.RST}", )

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
                f"   {Prisma.GRY}{pipe}{Prisma.RST} {icon} {e['metric'][:3].upper()} {color}{arrow} {d:.1f}{Prisma.RST} ({e['reason']})")
        if significant:
            h_flux = ux("cycle_reporter", "flux_header") or "SYSTEM FLUX DETECTED:"
            ctx.logs.insert(0, "")
            ctx.logs.insert(1, f" {Prisma.GRY}{h_flux}{Prisma.RST}")
            for line in reversed(significant):
                ctx.logs.insert(2, line)
            ctx.logs.insert(2 + len(significant), f" {Prisma.GRY}{footer}{Prisma.RST}")

    def _package_bureaucracy(self, ctx):
        if not self.eng.bureau:
            return None
        if ctx.is_bureaucratic or ctx.bureau_ui:
            base = (self.renderer.base_renderer
                    if hasattr(self.renderer, "base_renderer")
                    else self.renderer)
            bio_res = ctx.bio_result or {}
            return {"type": "BUREAUCRACY", "ui": ctx.bureau_ui,
                    "logs": base.compose_logs(ctx.logs, self.eng.events.flush(), self.eng.tick_count),
                    "metrics": self.eng.get_metrics(bio_res.get("atp", 0.0)), }
        return None