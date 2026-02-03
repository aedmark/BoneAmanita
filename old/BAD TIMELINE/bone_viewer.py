""" bone_view.py
 The Geodesic Viewport - Separation of Presentation and Logic """

import time
from typing import Dict, List, Any
from bone_bus import Prisma, BoneConfig

class Projector:
    def __init__(self):
        self.width = 60
        self.height = 15

    def render(self, physics_ctx, data_ctx, mind_ctx) -> str:
        physics = physics_ctx.get("physics", {})
        title_data = data_ctx.get("title", {})
        health = data_ctx.get("health", 100)
        stamina = data_ctx.get("stamina", 100)
        atp = data_ctx.get("bio", {}).get("atp", 0)
        vectors = data_ctx.get("vectors", {})
        hp_bar = self._bar(health, 100, 5, "█", Prisma.RED)
        stm_bar = self._bar(stamina, 100, 5, "█", Prisma.GRN)
        vel = vectors.get("VEL", 0.0)
        str_v = vectors.get("STR", 0.0)
        ent = vectors.get("ENT", 0.0)
        phi = vectors.get("PHI", 0.0)
        tmp = vectors.get("TMP", 0.0)
        psi = physics.get("psi", 0.0)
        header = (
            f"♦ NARRATOR  [HP: {hp_bar}] [STM: {stm_bar}] [ATP: {int(atp)}J] "
            f"[V:{physics.get('voltage', 0):.1f}⚡] [D:{physics.get('narrative_drag', 0):.1f}⚓]")
        vector_row = (
            f"VEL {vel:.1f} | STR {str_v:.1f} ENT {ent:.1f} | "
            f"PHI {phi:.1f} TMP {tmp:.1f} | PSI {psi:.1f}")
        zone = physics.get("zone", "UNKNOWN")
        if isinstance(zone, (list, tuple)):
            zone = zone[0]
        lens = mind_ctx[0] if mind_ctx else "RAW"
        sub_header = f"   🪐 {zone}  ({lens})"
        div = "—" * 40
        return (
            f"{header}\n"
            f"{Prisma.CYN}{vector_row}{Prisma.RST}\n"
            f"{sub_header}\n"
            f"{Prisma.GRY}{div}{Prisma.RST}\n")

    def _bar(self, val, max_val, width, char, color):
        if max_val == 0: return ""
        ratio = max(0.0, min(1.0, val / max_val))
        fill = int(ratio * width)
        return f"{color}{char * fill}{Prisma.GRY}{char * (width - fill)}{Prisma.RST}"

class GeodesicRenderer:
    def __init__(self, engine_ref, chroma_ref, strunk_ref, valve_ref=None):
        self.eng = engine_ref
        self.projector = self.eng.projector
        self.vsl_chroma = chroma_ref
        self.strunk_white = strunk_ref

    @staticmethod
    def render_soul_strip(soul_ref) -> str:
        if not soul_ref: return ""
        chapter = soul_ref.chapters[-1] if soul_ref.chapters else "The Prologue"
        obsession = soul_ref.current_obsession or "Drifting..."
        raw_prog = getattr(soul_ref, "obsession_progress", 0.0)
        normalized = max(0.0, min(1.0, raw_prog / 100.0))
        progress = int(normalized * 10)
        bar = f"{Prisma.MAG}{'■'*progress}{Prisma.GRY}{'□'*(10-progress)}{Prisma.RST}"
        traits = [f"{k[0]}:{v:.1f}" for k, v in soul_ref.traits.items()]
        trait_str = f"{Prisma.GRY}[{' '.join(traits)}]{Prisma.RST}"
        return (
            f"{Prisma.SLATE}{'-'*40}{Prisma.RST}\n"
            f"📖 {Prisma.WHT}{chapter}{Prisma.RST}\n"
            f"🧭 Obsession: {obsession} {bar} {trait_str}")

    def render_dashboard(self, ctx) -> str:
        physics = ctx.physics
        mind = ctx.mind_state
        bio = ctx.bio_result
        world = ctx.world_state

        title_data = self.eng.mind.wise.architect(
            {"physics": physics, "clean_words": ctx.clean_words},
            (mind.get("lens"), mind.get("thought"), mind.get("role")),
            False)
        raw_dashboard = self.projector.render(
            {"physics": physics},
            {
                "title": title_data,
                "health": self.eng.health,
                "stamina": self.eng.stamina,
                "bio": bio,
                "world": world,
                "inventory": self.eng.gordon.inventory if hasattr(self.eng, 'gordon') else [],
                "vectors": physics.get("vector", {})},
            (mind.get("lens"), mind.get("thought")))
        return raw_dashboard

    def render_frame(self, ctx, current_tick: int, current_events: List[Dict]) -> Dict[str, Any]:
        physics = ctx.physics
        bio = ctx.bio_result
        raw_dashboard = self.render_dashboard(ctx)
        colored_ui = self.vsl_chroma.modulate(raw_dashboard, physics.get("vector", {}))
        clean_ui, style_log = self.strunk_white.sanitize(colored_ui)
        if "The system is listening." in clean_ui:
            clean_ui = clean_ui.replace("The system is listening.", "")
        if hasattr(self.eng, 'soul'):
            soul_ui = self.render_soul_strip(self.eng.soul)
            clean_ui = f"{clean_ui}\n{soul_ui}"
        raw_logs = self.compose_logs(ctx.logs, current_events, current_tick)
        return {
            "type": "GEODESIC_FRAME",
            "ui": clean_ui,
            "logs": raw_logs,
            "metrics": self.eng.get_metrics(bio.get("atp", 0.0)),
            "system_instruction": self._get_chorus_instruction(physics)}

    def _get_title_data(self, mind, physics, clean_words):
        return self.eng.mind.wise.architect(
            {"physics": physics, "clean_words": clean_words},
            (mind.get("lens"), mind.get("thought"), mind.get("role")),
            False)

    def _punish_style_crime(self, log_msg):
        self.eng.events.log(log_msg, "SYS")
        self.eng.bio.endo.dopamine -= 0.05
        self.eng.phys.nav.shimmer.spend(5.0)
        self.eng.mind.mem.short_term_buffer.append({
            "trigger": ["style_violation"],
            "context": "STRUNK_WHITE",
            "voltage": 0.0,
            "significance": 5.0,
            "timestamp": time.time()})

    def _inject_rupture_warning(self, ui_text):
        return ui_text

    def _get_chorus_instruction(self, physics):
        if physics.get("kappa", 0) > 0.4:
            instr, active = self.eng.director.generate_chorus_instruction(physics)
            if active:
                self.eng.events.log(f"{Prisma.GRY}CHORUS ACTIVE: {', '.join(active)}{Prisma.RST}", "PSYCH")
                return instr
        return ""

    @staticmethod
    def compose_logs(logs: list, events: list, tick: int) -> List[str]:
        safe_logs = [str(l) for l in logs if l is not None]
        is_warmup = tick <= 5
        all_events = [{"text": l, "category": "NARRATIVE"} for l in safe_logs]
        all_events.extend(events)
        if not all_events: return []
        buckets = {"CRITICAL": [], "NARRATIVE": [], "CMD": [], "SYS": [], "BIO": [], "PSYCH": [], "OTHER": []}
        plasticity_count = 0
        mirror_count = 0
        for e in all_events:
            if not e: continue
            raw_cat = e.get("category", "OTHER") or "OTHER"
            cat = str(raw_cat).upper()
            text = str(e.get("text", ""))
            if is_warmup and cat in ["SYS", "BIO", "PSYCH", "OTHER"]: continue
            if "RUPTURE" in text or "DEATH" in text or "PANIC" in text: cat = "CRITICAL"
            if "NEUROPLASTICITY" in text:
                plasticity_count += 1
                continue
            if "[MIRROR]" in text:
                mirror_count += 1
                continue
            if cat not in buckets: cat = "OTHER"
            buckets[cat].append(text)
        if plasticity_count > 0:
            buckets["PSYCH"].append(f"NEUROPLASTICITY: Integrated {plasticity_count} new associations.")
        if mirror_count > 0:
            buckets["SYS"].append(f"🪞 [MIRROR]: Reflection adjusted ({mirror_count}x).")
        composed = []
        if buckets["CRITICAL"]:
            composed.append(f"{Prisma.RED}--- CRITICAL ALERTS ---{Prisma.RST}")
            composed.extend(buckets["CRITICAL"])
        if buckets["NARRATIVE"]:
            composed.extend(buckets["NARRATIVE"])
        compressible = [
            ("CMD", Prisma.WHT, "COMMANDS"),
            ("PSYCH", Prisma.VIOLET, "PSYCHOLOGY"),
            ("BIO", Prisma.GRN, "BIOLOGY"),
            ("SYS", Prisma.GRY, "SYSTEM"),
            ("OTHER", Prisma.GRY, "MISC")]
        for cat, color, label in compressible:
            items = buckets[cat]
            if not items: continue
            composed.append(f"{Prisma.SLATE}   .{label} ({len(items)}){' ' * (30 - len(label))}{Prisma.RST}")
            if len(items) > 4 and not BoneConfig.VERBOSE_LOGGING:
                composed.extend([f"   {i}" for i in items[:3]])
                composed.append(f"   {color}   ... and {len(items)-3} more.{Prisma.RST}")
            else:
                composed.extend([f"   {i}" for i in items])
        return composed

class CachedRenderer:
    def __init__(self, base_renderer):
        self._base = base_renderer
        self._cache = {
            "soul_strip": {"hash": 0, "content": ""},
            "dashboard": {"hash": 0, "content": ""},
            "last_tick": -1}
        self.THEMES = {
            "DEFAULT": {"border": "═", "accent": Prisma.CYN, "alert": Prisma.RED},
            "NOIR": {"border": "-", "accent": Prisma.GRY, "alert": Prisma.WHT},
            "RETRO": {"border": "*", "accent": Prisma.MAG, "alert": Prisma.YEL},
            "MINIMAL": {"border": " ", "accent": Prisma.RST, "alert": Prisma.RST}}
        self.active_theme = self.THEMES["DEFAULT"]

    def _compute_hash(self, data: Any) -> int:
        return hash(str(data))

    def render_frame(self, ctx, tick: int, events: List[Dict]) -> Dict:
        soul_ref = getattr(self._base.eng, 'soul', None)
        if soul_ref:
            soul_state = (soul_ref.current_obsession, soul_ref.obsession_progress)
            soul_hash = self._compute_hash(soul_state)
            if soul_hash != self._cache["soul_strip"]["hash"]:
                self._cache["soul_strip"]["content"] = self._base.render_soul_strip(soul_ref)
                self._cache["soul_strip"]["hash"] = soul_hash
        else:
            self._cache["soul_strip"]["content"] = ""
        voltage = ctx.physics.get("voltage", 0) if isinstance(ctx.physics, dict) else ctx.physics.voltage
        if voltage > 15.0 or tick != self._cache["last_tick"]:
            raw_dashboard = self._base.render_dashboard(ctx)
            colored = self._base.vsl_chroma.modulate(raw_dashboard, ctx.physics.get("vector", {}))
            clean, _ = self._base.strunk_white.sanitize(colored)
            self._cache["dashboard"]["content"] = clean
            self._cache["last_tick"] = tick
        frame = {
            "type": "GEODESIC_FRAME",
            "ui": f"{self._cache['dashboard']['content']}\n{self._cache['soul_strip']['content']}",
            "logs": self._base.compose_logs(ctx.logs, events, tick),
            "metrics": ctx.bio_result if hasattr(ctx, 'bio_result') else {}}
        return frame

class ThemeContext:
    THEMES = {
        "DEFAULT": {"border": "═", "accent": Prisma.CYN, "alert": Prisma.RED},
        "NOIR": {"border": "-", "accent": Prisma.GRY, "alert": Prisma.WHT},
        "RETRO": {"border": "*", "accent": Prisma.MAG, "alert": Prisma.YEL},
        "MINIMAL": {"border": " ", "accent": Prisma.RST, "alert": Prisma.RST}}

    def __init__(self, theme_name="DEFAULT"):
        self.active = self.THEMES.get(theme_name, self.THEMES["DEFAULT"])

    def frame(self, content: str, label: str = "") -> str:
        b = self.active["border"]
        c = self.active["accent"]
        r = Prisma.RST
        width = 60
        header = f"{c}{b*5} {label} {b*(width-7-len(label))}{r}"
        footer = f"{c}{b*width}{r}"
        return f"{header}\n{content}\n{footer}"

def get_renderer(engine_ref, chroma_ref, strunk_ref, valve_ref, mode="STANDARD"):
    base = GeodesicRenderer(engine_ref, chroma_ref, strunk_ref, valve_ref)
    if mode == "PERFORMANCE":
        return CachedRenderer(base)
    elif mode == "DEBUG":
        return base
    else:
        return base