"""
mechanics/projector.py
The Terminal Holography and UI Membrane Module.
This module is responsible for taking the massive, complex internal state of the
VSL engine (biology, physics, mind, soul) and rendering it as a coherent ASCII/ANSI
HUD (Heads-Up Display). It scales its complexity from 'WARM' (invisible) to
'DEEP' (exposing every hidden variable) based on the user's cognitive load.
"""
import re
from typing import Any, Dict, List
import markdown
from core import Prisma
from struts import safe_get, ux
from presets import BoneConfig


def render_markdown(text: str) -> str:
    """Translates raw markdown into the terminal output format."""
    return markdown.markdown(text, extensions=["extra"])


_THOUGHT_PATTERN = re.compile(r"<(?:think|thought)>(.*?)(?:</(?:think|thought)>|$)", re.DOTALL | re.IGNORECASE)


def beautify_thoughts(text: str) -> str:
    """
    The Cognitive Substrate Window (Pinker).
    Frontier LLMs natively output <thought> tags when reasoning. Unformatted,
    this looks like garbage to the user. This function catches that raw cognitive
    exhaust, parses it, and formats it as a beautiful, indented 'Substrate' block
    using terminal structural pipes. It separates the 'thinking' from the 'speaking'
    with absolute syntactic clarity.
    """

    def replacer(match):
        if not (content := match.group(1).strip()): return ""
        inner = "\n".join(
            f"{Prisma.CYN}  │ {Prisma.GRY}{line.strip()}{Prisma.RST}" for line in content.split("\n") if line.strip())
        return f"{Prisma.CYN}  ┌─ {Prisma.MAG}[ COGNITIVE SUBSTRATE ]{Prisma.RST}\n{inner}\n{Prisma.CYN}  └─{Prisma.RST}"

    return _THOUGHT_PATTERN.sub(replacer, text)


class Projector:
    """
    The Holographic Formatter (Fuller / Schur).
    The Projector does not change the state of the system; it only observes and
    paints it. It handles the dynamic layout of health bars, metabolic gauges,
    and systemic friction readouts, ensuring the user has the feedback required
    to co-regulate with the machine.
    """

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.width = 80
        self.symbols = ux("projector", "symbols", {})

    @staticmethod
    def _extract(physics_obj: Any, field: str, sub_field: str, default: Any = 0.0):
        """Recursively pulls nested values out of the physics dictionary."""
        if (val := safe_get(physics_obj, sub_field)) is not None:
            return val
        if (val := safe_get(safe_get(physics_obj, field), sub_field)) is not None:
            return val
        return default

    def _render_clear_hud(self, physics: Any, data_ctx: Dict, mind: tuple) -> str:
        """
        The Diagnostic HUD (Schur).
        A clean, explicitly readable status readout that avoids cryptic abbreviations
        (like β or CHI) in favor of plain English metrics. Used when the system
        detects the user is exhausted and needs simple, actionable data.
        """
        energy = float(data_ctx.get("stamina", 100.0))
        friction = self._get_lattice_val(physics, ["narrative_drag", "friction", "F"], 0.0)
        chem = data_ctx.get("bio", {}).get("chemistry", {})
        stress = min(100.0, (chem.get("COR", 0.0) * 100.0) + (chem.get("ADR", 0.0) * 50.0))
        phi = float(safe_get(data_ctx.get("shared_dyn", {}), "phi", 0.5))

        def bar(v, mx, col):
            f = int(max(0.0, min(1.0, v / mx if mx else 0)) * 10)
            return f"[{col}{'█' * f}{Prisma.GRY}{'░' * (10 - f)}{Prisma.RST}]"

        if energy > 50:
            e_txt = "Healthy. Ready for complex tasks."
        elif energy > 20:
            e_txt = "Fatigued. Proceed with care."
        else:
            e_txt = "Critical. Autophagy risk."
        if friction < 2.0:
            f_txt = "Low. The current logic flows easily."
        elif friction < 6.0:
            f_txt = "Moderate. Bearing structural weight."
        else:
            f_txt = "High. Heavy systemic drag."
        if stress < 30:
            s_txt = "Nominal. No resting required."
        elif stress < 70:
            s_txt = "Elevated. Consider pacing."
        else:
            s_txt = "High. Toxicity accumulating."
        if phi >= 0.7:
            st_txt = "Flow State. Highly aligned with your inputs."
        elif phi >= 0.4:
            st_txt = "Stable. Processing normally."
        else:
            st_txt = "Desynchronized. Friction expected."
        return (f"\n{Prisma.CYN}### SYSTEM TELEMETRY{Prisma.RST}\n"
                f"{Prisma.WHT}Energy:  {Prisma.RST} {bar(energy, 100, Prisma.GRN)} {int(energy)}% {Prisma.GRY}({e_txt}){Prisma.RST}\n"
                f"{Prisma.WHT}Friction:{Prisma.RST} {bar(friction, 10, Prisma.CYN)} {friction:.1f} {Prisma.GRY}({f_txt}){Prisma.RST}\n"
                f"{Prisma.WHT}Stress:  {Prisma.RST} {bar(stress, 100, Prisma.OCHRE)} {int(stress)}% {Prisma.GRY}({s_txt}){Prisma.RST}\n"
                f"{Prisma.WHT}Status:  {Prisma.RST} {Prisma.MAG}{st_txt}{Prisma.RST}\n")

    def render(self, physics_ctx: Dict, data_ctx: Dict, mind_ctx: tuple, reality_depth: int = 1,
               labels: Dict = None) -> str:
        """
        The Master Layout Orchestrator.
        Assembles the different semantic strips (Vitals, Physics, Lattice) into
        a single, coherent terminal block based on the current `ui_depth`.
        """
        ui_depth = data_ctx.get("ui_depth", "IDLE")
        if ui_depth in ("WARM", "IDLE"):
            return ""
        if ui_depth == "MINIMAL":
            return self._render_clear_hud(physics_ctx.get("physics", {}), data_ctx, mind_ctx)
        if not labels:
            labels = ux("projector", "default_labels", {})
        physics = physics_ctx.get("physics", {})
        show_vitals = data_ctx.get("show_vitals", True)
        status_line = (self._render_vital_strip(data_ctx, mind_ctx, labels)
                       if show_vitals
                       else self._render_minimal_strip(mind_ctx))
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
        """Extracts the active archetype or persona from the mind tuple."""
        raw_role = mind[2] if mind and len(mind) > 2 else None
        role = str(raw_role).upper() if raw_role else (ux("projector", "default_role") or "OBSERVER")
        return role.replace(ux("projector", "role_redundancy") or "THE THE ", "THE ")

    @staticmethod
    def _render_minimal_strip(mind: tuple) -> str:
        sym = ux("projector", "symbols", {})
        return f"  {Prisma.WHT}{sym.get('role', '')} {Projector._get_role(mind)}{Prisma.RST}"

    def _render_vital_strip(self, data: Dict, mind: tuple, labels: Dict) -> str:
        """Renders the biological health, stamina, ATP, and dignity reserves."""
        maximum_health = float(getattr(self.cfg, "MAX_HEALTH", 100.0) or 100.0)
        maximum_stamina = float(getattr(self.cfg, "MAX_STAMINA", 100.0) or 100.0)
        gui_config = getattr(self.cfg, "GUI", object())
        dignity_medium = getattr(gui_config, "DIGNITY_MED", 50.0)
        dignity_high = getattr(gui_config, "DIGNITY_HIGH", 80.0)
        role_truncation_length = getattr(gui_config, "ROLE_TRUNC_LEN", 30)
        current_health = float(data.get("health") or maximum_health)
        current_stamina = float(data.get("stamina") or maximum_stamina)
        current_atp = float(data.get("bio", {}).get("atp") or 0.0)
        current_dignity = float(data.get("dignity") or 100.0)
        health_bar = self._mini_bar(current_health, maximum_health, 6, Prisma.RED)
        stamina_bar = self._mini_bar(current_stamina, maximum_stamina, 6, Prisma.GRN)
        dignity_color = Prisma.VIOLET if current_dignity > dignity_medium else Prisma.GRY
        dignity_icon = self.symbols.get("dig_high", "") if current_dignity > dignity_high else self.symbols.get(
            "dig_low", "")
        active_role = self._get_role(mind)
        if len(active_role) > role_truncation_length:
            active_role = f"{active_role[:role_truncation_length - 3]}..."
        label_health = labels.get("HP", "HP")
        label_stamina = labels.get("STM", "STM")
        icon_role = self.symbols.get("role", "")
        raw_role = f"{icon_role} {active_role}"[:35].ljust(35)
        role_block = f"{Prisma.WHT}{raw_role}{Prisma.RST}"
        return (
            f"  {role_block} "
            f"{label_health} {health_bar}  "
            f"{label_stamina} {stamina_bar}  "
            f"{dignity_color}{dignity_icon}{int(current_dignity)}%{Prisma.RST} "
            f"{Prisma.YEL}ATP:{int(current_atp)}{Prisma.RST}"
        )

    def _render_physics_strip(self, physics: Any, vectors: Dict) -> str:
        """Renders the Voltage, Drag, and active Semantic Vector of the conversation."""
        volt = float(self._extract(physics, "energy", "voltage", 0.0))
        drag = float(self._extract(physics, "space", "narrative_drag", 0.0))
        dp_str = ""
        if dp := safe_get(physics, "drag_profile"):
            parts = []
            profile_keys = (("semantic", "Sem"), ("metabolic", "Met"), ("emotional", "Emo"), ("structural", "Str"),
                            ("trauma", "Tra"))
            for key, lbl in profile_keys:
                val = float(safe_get(dp, key, 0.0) or 0.0)
                if val > 0:
                    parts.append(f"{lbl}:{val:.1f}")
            if parts:
                dp_str = f" [{Prisma.GRY}{'|'.join(parts)}{Prisma.RST}]"
        dom_vec = max(vectors, key=vectors.get) if vectors else "NEUTRAL"
        dom_val = float(vectors.get(dom_vec, 0.0) or 0.0) if vectors else 0.0
        return f"  {Prisma.CYN}VOLT:{Prisma.RST} {volt:04.1f}v   {Prisma.SLATE}DRAG:{Prisma.RST} {drag:04.1f}{dp_str}   {Prisma.MAG}VEC:{Prisma.RST} {dom_vec} ({dom_val:.2f})"

    def _get_lattice_val(self, domains: List[Any], keys: List[str], default: float) -> float:
        """Safely probes multiple data domains looking for a specific metric."""
        for k in keys:
            for dom in domains:
                if dom and (val := safe_get(dom, k)) is not None:
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        pass
        return default

    def _render_lattice_strip(self, physics: Any, data_ctx: Dict = None, depth: str = "DEEP") -> str:
        """
        The Deep Geometry Matrix.
        Renders the most arcane and structural elements of the system: Entropy (CHI),
        Abstractness (PSI), Resonance (PHI), Contradiction Capacity (Beta), and
        active SLASH governance variables (Gamma, Sigma, etc.).
        """
        if depth == "IDLE" or not physics:
            return ""
        data_ctx = data_ctx or {}
        doms = [physics] + [safe_get(physics, sub) for sub in ("energy", "space", "matter")]
        exhaustion = self._get_lattice_val(doms, ["exhaustion", "E"], 0.2)
        beta = self._get_lattice_val(doms, ["beta_index", "contradiction", "beta"], 0.4)
        voltage = self._get_lattice_val(doms, ["voltage", "V"], 30.0)
        friction = self._get_lattice_val(doms, ["narrative_drag", "friction", "F"], 0.6)
        health = self._get_lattice_val(doms, ["health", "H"], 100.0)
        stamina = max(0.0, self._get_lattice_val(doms, ["stamina", "P"], 100.0))
        trauma = self._get_lattice_val(doms, ["trauma", "T"], 0.0)
        psi = self._get_lattice_val(doms, ["psi", "PSI"], 0.0)
        chi = self._get_lattice_val(doms, ["entropy", "chi", "CHI"], 0.0)
        valence = self._get_lattice_val(doms, ["valence", "VALENCE"], 0.0)
        slash_vars = {k: self._get_lattice_val(doms, [k], 0.0) for k in ("gamma", "sigma", "eta", "theta", "upsilon")}
        sym = ux("projector", "symbols", {})
        i_core = sym.get("core", "")
        i_volt = sym.get("volt", "")
        i_hlth = sym.get("health", "")
        i_trau = sym.get("trauma", "")
        i_deep = sym.get("deep", "")
        core = f"{Prisma.CYN}[{i_core} E:{exhaustion:.2f} β:{beta:.2f} | {i_volt} V:{voltage:.0f} F:{friction:.1f} | {i_hlth} H:{health:.0f} P:{stamina:.0f} | {i_trau} T:{trauma:.0f}]{Prisma.RST}"
        deep = f"{Prisma.VIOLET} [{i_deep} Ψ:{psi:.2f} Χ:{chi:.2f} ♥:{valence:.2f}]{Prisma.RST}"
        shared_str = ""
        if shared := data_ctx.get("shared_dyn"):
            phi = safe_get(shared, "phi", 0.5)
            delta = safe_get(shared, "delta", 0.0)
            g_pool = int(safe_get(shared, "g_pool", 0))
            sig_silence = int(safe_get(shared, "sigma_silence", 0))
            shared_str = f" {Prisma.INDIGO}[Φ:{phi:.2f} ∇:{delta:.2f} (Σ{sig_silence}) G:{g_pool}]{Prisma.RST}"
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
        if any(v > 0 for v in slash_vars.values()):
            sv = slash_vars
            slash_str = f" {Prisma.BLU}[SLASH Γ:{sv['gamma']:.1f} Σ:{sv['sigma']:.1f} Η:{sv['eta']:.1f} Θ:{sv['theta']:.1f} Υ:{sv['upsilon']:.1f}]{Prisma.RST}"
        if depth == "LITE":
            vitals = f" | {i_hlth} H:{health:.0f} P:{stamina:.0f}" if data_ctx.get('show_vitals', True) else ""
            return f"{Prisma.CYN}[{i_volt} V:{voltage:.0f}{vitals}]{Prisma.RST}{shared_str}"
        elif depth == "CORE":
            return core + shared_str + strain_str + slash_str
        elif depth == "DEEP":
            return core + deep + shared_str + paradox_str + strain_str + slash_str
        return ""

    def render_technical(self, physics: Dict, data: Dict, mind: tuple) -> str:
        """A raw, unformatted data dump used primarily when the engine crashes."""
        v = self._extract(physics, "energy", "voltage", 0.0)
        d = self._extract(physics, "space", "narrative_drag", 0.0)
        vec = data.get("vectors", {})
        vec_str = ", ".join(f"{k}:{v:.2f}" for k, v in vec.items() if v > 0.01)
        h_tech = ux("technical_projector", "header") or "[TECHNICAL PROJECTOR]"
        l_phys = ux("technical_projector", "physics_label") or "Physics"
        l_vec = ux("technical_projector", "vectors_label") or "Vectors"
        l_bio = ux("technical_projector", "bio_dump_label") or "Bio Dump"
        return (f"{Prisma.CYN}{h_tech}{Prisma.RST}\n"
                f"{l_phys} V={v:<6.3f} D={d:<6.3f} | LENS: {mind[0]}\n"
                f"{l_vec} [{vec_str}]\n"
                f"{l_bio} {str(data.get('bio', {}))[:60]}...")

    def _mini_bar(self, val, max_val, width, color):
        """Constructs a tiny, fixed-width progress bar for the HUD."""
        if max_val == 0:
            return ""
        ratio = max(0.0, min(1.0, val / max_val))
        fill_count = int(ratio * width)
        empty_count = width - fill_count
        char_fill = self.symbols.get("bar_fill") or "█"
        char_empty = self.symbols.get("bar_empty") or "░"
        return f"{color}{char_fill * fill_count}{Prisma.GRY}{char_empty * empty_count}{Prisma.RST}"


class SoulDashboard:
    """
    The Identity and Agency Interface (Schur).
    Renders the state of the system's "Soul"—its active Dignity Reserve, its
    current Archetype (Persona), how long it has held that Persona (Tenure),
    and what Concept currently obsesses it. If Dignity drops too low, it displays
    the 'FADING' warning or the 'AGENCY LOCKED' status.
    """

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.cfg = getattr(self.eng, "config", BoneConfig)

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
        d_ratio = max(1, int(getattr(cfg, "DIGNITY_BAR_RATIO", 5)))
        t_warn = getattr(cfg, "TENURE_WARN", 5)
        t_crit = getattr(cfg, "TENURE_CRIT", 8)
        color = Prisma.GRN if dig > d_high else Prisma.OCHRE if dig > d_low else Prisma.RED
        max_dig = getattr(cfg, "DIGNITY_MAX", 100.0)
        clamped_dig = max(0.0, min(max_dig, dig))
        max_bar_width = int(max_dig / d_ratio)
        filled = int(clamped_dig / d_ratio)
        empty = max(0, max_bar_width - filled)
        c_fill = ux("status_menu", "bar_filled") or "█"
        c_empty = ux("status_menu", "bar_empty") or "░"
        bar_str = f"{color}{c_fill * filled}{Prisma.GRY}{c_empty * empty}{Prisma.RST}"
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
            str(soul.current_obsession) if soul.current_obsession else (ux("soul_dashboard", "default_muse") or "None"))
        l_soul = ux("soul_dashboard", "soul_prefix") or "Soul:"
        l_driver = ux("soul_dashboard", "driver_prefix") or "Driver:"
        l_muse = ux("soul_dashboard", "muse_prefix") or "Muse:"
        line1 = f"{l_soul} {bar_str} {int(dig)}%{lock_status}{pet_icon}"
        line2 = f"      {l_driver} {arch_display}  {l_muse} {Prisma.VIOLET}{muse}{Prisma.RST}"
        return f"{line1}\n{line2}"
