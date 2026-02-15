""" bone_gui.py - The Visual Cortex (Renderer Library)
    Refactored for Multi-Modal UX
"""

from typing import Dict, List, Any, Tuple
from bone_core import Prisma

class Projector:
    def __init__(self):
        self.width = 60

    def render(self, physics_ctx: Dict, data_ctx: Dict, mind_ctx: tuple, reality_depth: int = 1,
               labels: Dict = None) -> str:
        if not labels: labels = {"HP": "HP", "STM": "STM"}
        physics = physics_ctx.get("physics", {})
        status_line = self._render_vital_strip(data_ctx, mind_ctx, labels)
        physics_line = ""
        if labels.get("SHOW_PHYSICS", True):
            physics_line = "\n" + self._render_physics_strip(physics, data_ctx.get("vectors", {}))
        vsl_line = self._render_lattice_strip(data_ctx.get("vsl", {}))
        zone = physics.get("zone", "UNKNOWN")
        lens = mind_ctx[0] if mind_ctx else "RAW"
        depth_map = {0: "TERM", 1: "SIM", 2: "VIL", 3: "DBG", 4: "DEEP"}
        depth_label = depth_map.get(reality_depth, "?")
        depth_marker = f"{Prisma.VIOLET}[D{reality_depth}:{depth_label}]{Prisma.RST}"
        context_line = f"{Prisma.GRY}📍 {zone} // 👁️ {lens}{Prisma.RST} // {depth_marker}"
        div = f"{Prisma.GRY}{'─' * self.width}{Prisma.RST}"
        return f"{div}\n{status_line}{physics_line}{vsl_line}\n{context_line}\n{div}"

    def _render_lattice_strip(self, vsl_data: Dict) -> str:
        if not vsl_data: return ""
        e = vsl_data.get("E", 0.0)
        b = vsl_data.get("B", 0.0)
        l = vsl_data.get("L", 0.0)
        o = vsl_data.get("O", 1.0)
        if e < 0.15 and b < 0.1 and l < 0.1: return ""
        def bar(val, color):
            p = int(val * 10)
            return f"{color}{'|' * p}{Prisma.GRY}{'.' * (10 - p)}{Prisma.RST}"
        e_str = f"E:{bar(e, Prisma.CYN)}"
        b_str = f" β:{bar(b, Prisma.MAG)}"
        l_str = ""
        if l > 0.1:
            l_str = f" Λ:{bar(l, Prisma.VIOLET)}"
        o_str = ""
        if o > 0.8:
            o_str = f" Ω:{Prisma.BLU}[LOCKED]{Prisma.RST}"
        elif o < 0.5:
            o_str = f" Ω:{Prisma.RED}[FRACTURED]{Prisma.RST}"
        return f"\n{Prisma.GRY}LATTICE:{Prisma.RST} {e_str}{b_str}{l_str}{o_str}"

    def _render_vital_strip(self, data: Dict, mind: tuple, labels: Dict) -> str:
        health = data.get("health", 100)
        stamina = data.get("stamina", 100)
        atp = data.get("bio", {}).get("atp") or 0
        dignity = data.get("dignity", 100)
        hp_bar = self._mini_bar(health, 100, 4, Prisma.RED)
        stm_bar = self._mini_bar(stamina, 100, 4, Prisma.GRN)
        dig_color = Prisma.VIOLET if dignity > 50 else Prisma.GRY
        dig_icon = "✦" if dignity > 80 else "✧"
        raw_role = mind[2] if mind and len(mind) > 2 else None
        role = str(raw_role).upper() if raw_role else "OBSERVER"
        if len(role) > 15: role = role[:12] + "..."
        l_hp = labels.get("HP", "HP")
        l_stm = labels.get("STM", "STM")
        return (
            f"{Prisma.WHT}♦ {role}{Prisma.RST}   "
            f"{l_hp} {hp_bar}  {l_stm} {stm_bar}  "
            f"{dig_color}{dig_icon} {int(dignity)}%{Prisma.RST}  "
            f"{Prisma.YEL}ATP {int(atp)}{Prisma.RST}")

    def _render_physics_strip(self, physics: Dict, vectors: Dict) -> str:
        volt = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        dom_vec = "N/A"
        dom_val = 0.0
        if vectors:
            dom_vec = max(vectors, key=vectors.get)
            dom_val = vectors[dom_vec]
        return (
            f"⚡ {volt:.1f}v  "
            f"⚓ {drag:.1f}  "
            f"📐 {dom_vec} ({dom_val:.2f})")

    def render_technical(self, physics: Dict, data: Dict, mind: tuple) -> str:
        v = physics.get("voltage", 0.0)
        d = physics.get("narrative_drag", 0.0)
        vec = data.get("vectors", {})
        vec_str = ", ".join([f"{k}:{v:.2f}" for k, v in vec.items() if v > 0.01])
        return (
            f"{Prisma.CYN}/// KERNEL TELEMETRY ///{Prisma.RST}\n"
            f"PHYSICS : V={v:<6.3f} D={d:<6.3f} | LENS: {mind[0]}\n"
            f"VECTORS : [{vec_str}]\n"
            f"BIO_DUMP: {str(data.get('bio', {}))[:60]}...")

    def _mini_bar(self, val, max_val, width, color):
        if max_val == 0: return ""
        ratio = max(0.0, min(1.0, val / max_val))
        fill = int(ratio * width)
        empty = width - fill
        return f"{color}{'█'*fill}{Prisma.GRY}{'░'*empty}{Prisma.RST}"

class GeodesicRenderer:
    def __init__(self, engine_ref, chroma_ref, strunk_ref):
        self.eng = engine_ref
        self.projector = Projector()
        self.vsl_chroma = chroma_ref
        self.strunk_white = strunk_ref
        self.soul_dashboard = SoulDashboard(engine_ref)
        self.NOISE_PATTERNS = [
            "stabilizer:", "pid_", "flux", "phase execution",
            "vector collapse", "manifold", "orbit:", "update_coordinates",
            "active correction", "drag reduced", "voltage spiked",
            "live state mirror", "auto_trace", "wayfinder"]

    def render_frame(self, ctx, current_events: List[Dict]) -> Dict[str, Any]:
        physics = ctx.physics
        bio = ctx.bio_result
        raw_dashboard = self.render_dashboard(ctx)
        colored_ui = self.vsl_chroma.modulate(raw_dashboard, physics.get("vector", {}))
        if self.strunk_white:
            clean_ui, style_log = self.strunk_white.sanitize(colored_ui)
            if style_log: self._punish_style_crime(style_log)
        else:
            clean_ui = colored_ui
        if "The system is listening." in clean_ui:
            clean_ui = clean_ui.replace("The system is listening.", "")
        structured_logs = self.compose_logs(ctx.logs, current_events)
        return {
            "type": "GEODESIC_FRAME",
            "ui": clean_ui,
            "logs": structured_logs,
            "metrics": self.eng.get_metrics(bio.get("atp", 0.0))}

    def render_dashboard(self, ctx) -> str:
        physics = ctx.physics
        mind = ctx.mind_state
        mind_tuple = (mind.get("lens"), mind.get("thought"), mind.get("role"))
        bio_data = ctx.bio_result or {}
        if "atp" not in bio_data and hasattr(self.eng, "bio") and hasattr(self.eng.bio, "mito"):
            bio_data = bio_data.copy()
            bio_data["atp"] = self.eng.bio.mito.state.atp_pool
        data_ctx = {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "bio": bio_data,
            "dignity": getattr(self.eng.soul.anchor, 'dignity_reserve', 100.0) if hasattr(self.eng, 'soul') else 100.0,
            "vectors": physics.get("vector", {})}
        mode = self.eng.config.get("boot_mode", "ADVENTURE").upper()
        current_depth = 1
        if hasattr(ctx, "reality_stack"):
            current_depth = ctx.reality_stack.current_depth
        if mode == "TECHNICAL":
            return self.projector.render_technical(physics, data_ctx, mind_tuple)
        elif mode == "CONVERSATION":
            labels = {"HP": "LINK", "STM": "SYNC", "SHOW_PHYSICS": False}
            return self.projector.render(
                {"physics": physics}, data_ctx, mind_tuple, current_depth, labels)
        elif mode == "CREATIVE":
            labels = {"HP": "INT", "STM": "FLOW", "SHOW_PHYSICS": True}
            return self.projector.render(
                {"physics": physics}, data_ctx, mind_tuple, current_depth, labels)
        else:
            return self.projector.render(
                {"physics": physics},
                data_ctx,
                mind_tuple,
                reality_depth=current_depth)

    def render_soul_strip(self, soul_ref) -> str:
        if not soul_ref: return ""
        if not soul_ref.current_obsession:
            return ""
        return f"{Prisma.GRY}--- Obsession: {soul_ref.current_obsession} ---{Prisma.RST}"

    def compose_logs(self, logs: list, events: list) -> List[str]:
        all_logs = [str(l) for l in logs if l is not None]
        for e in events:
            if e and e.get("text"):
                all_logs.append(e["text"])
        if not all_logs: return []
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
        for log in unique_logs:
            if "CRITICAL" in log or "RUPTURE" in log:
                structured.append(f"{Prisma.RED}► {log}{Prisma.RST}")
            elif "Bio-Alert" in log or "SENSATION" in log:
                structured.append(f"{Prisma.CYN}• {log}{Prisma.RST}")
            elif "ITEM:" in log or "GAINED" in log:
                structured.append(f"{Prisma.YEL}★ {log}{Prisma.RST}")
            else:
                structured.append(f"{Prisma.GRY}• {log}{Prisma.RST}")
        return structured

    def _punish_style_crime(self, log_msg):
        if hasattr(self.eng, 'events'):
            self.eng.events.log(log_msg, "SYS")

class CachedRenderer:
    def __init__(self, base_renderer):
        self._base = base_renderer
        self._cache = {
            "dashboard": {"hash": 0, "content": ""},
            "last_tick": -1}

    def render_frame(self, ctx, tick: int, events: List[Dict]) -> Dict:
        voltage = ctx.physics.get("voltage", 0) if isinstance(ctx.physics, dict) else ctx.physics.voltage
        if voltage > 15.0 or tick != self._cache["last_tick"]:
            frame = self._base.render_frame(ctx, tick, events)
            self._cache["dashboard"]["content"] = frame["ui"]
            self._cache["last_tick"] = tick
            return frame
        return {
            "type": "GEODESIC_FRAME",
            "ui": self._cache["dashboard"]["content"],
            "logs": self._base.compose_logs(ctx.logs, events, tick),
            "metrics": ctx.bio_result if hasattr(ctx, 'bio_result') else {}}

def get_renderer(engine_ref, chroma_ref, strunk_ref, mode="STANDARD"):
    base = GeodesicRenderer(engine_ref, chroma_ref, strunk_ref)
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
        if self.dial_setting == AmbiguityDial.BOARDROOM:
            return f"{Prisma.paint('--- EXECUTIVE SUMMARY ---', 'W')}\n{ui_text}\n"
        elif self.dial_setting == AmbiguityDial.WORKSHOP:
            metrics = self.engine.get_metrics()
            return (
                f"{Prisma.paint('--- ENGINEER VIEW ---', 'C')}\n"
                f"Confidence: {cortex_packet.get('truth_ratio', 0.95):.2%}\n"
                f"System Drag: {metrics['stamina']:.1f}\n"
                f"---------------------\n{ui_text}\n")

        elif self.dial_setting == AmbiguityDial.RED_TEAM:
            dissent = [l for l in council_log if "CRITIC" in l or "WARN" in l]
            return (
                    f"{Prisma.paint('--- RED TEAM DASHBOARD ---', 'R')}\n"
                    f"{Prisma.paint('⚠️ ADVERSARIAL SIMULATION ACTIVE', 'Y')}\n"
                    f"Cost of Blandness: {trauma_cost:.1f} Trauma Units\n"
                    f"Active Conflicts:\n" + "\n".join([f"  > {d}" for d in dissent]) + "\n"
                    f"---------------------\n{ui_text}\n")
        elif self.dial_setting == AmbiguityDial.PALIMPSEST:
            drafts = cortex_packet.get("drafts", [])
            layer_view = ""
            for i, draft in enumerate(drafts):
                layer_view += f"{Prisma.GRY}[Draft {i}]: {draft} {Prisma.RED}[REDACTED]{Prisma.RST}\n"
            return (
                f"{Prisma.paint('--- PALIMPSEST VIEW ---', 'M')}\n"
                f"{layer_view}"
                f"{Prisma.paint('--- FINAL SURFACE ---', 'W')}\n{ui_text}\n")
        return None

class PulseReader:
    @staticmethod
    def derive_mood(bio_state: Dict) -> str:
        chem = bio_state.get("chem", {})
        if chem.get("COR", 0) > 0.6: return "Defensive"
        if chem.get("DA", 0) > 0.6: return "Manic"
        if chem.get("OXY", 0) > 0.6: return "Affectionate"
        atp = bio_state.get("mito", {}).get("atp", 100)
        if atp < 20: return "Exhausted"
        return "Neutral"

    @staticmethod
    def analyze_voltage(voltage: float) -> Tuple[str, str]:
        if voltage > 20.0: return "CRITICAL", "⚡"
        if voltage > 15.0: return "HIGH", "🔥"
        if voltage < 5.0: return "LOW", "❄️"
        return "NOMINAL", "🟢"

class SoulDashboard:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def render(self) -> str:
        if not hasattr(self.eng, 'soul') or not self.eng.soul:
            return ""
        if not hasattr(self.eng.soul, 'anchor'):
            return f"{Prisma.GRY}[SOUL DETECTED - ANCHOR LOST]{Prisma.RST}"
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
            lock_status = f" {Prisma.RED}[🔒 AGENCY LOCKED]{Prisma.RST}"
        elif dig < 30:
            lock_status = f" {Prisma.OCHRE}[⚠ FADING]{Prisma.RST}"
        arch = soul.archetype
        tenure = soul.archetype_tenure
        tenure_color = Prisma.GRY
        if tenure > 5: tenure_color = Prisma.OCHRE
        if tenure > 8: tenure_color = Prisma.RED
        arch_display = f"{Prisma.CYN}{arch}{Prisma.RST} ({tenure_color}T:{tenure}{Prisma.RST})"
        pet_icon = " 🐕" if (dig < 50 and not anchor.agency_lock) else ""
        muse = soul.current_obsession if soul.current_obsession else "Void"
        line1 = f"SOUL: {bar_str} {int(dig)}%{lock_status}{pet_icon}"
        line2 = f"      DRIVER: {arch_display}  MUSE: {Prisma.VIOLET}{muse}{Prisma.RST}"
        return f"{line1}\n{line2}"