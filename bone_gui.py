""" bone_gui.py - The Visual Cortex """
from typing import Dict, List, Any
import streamlit as st
import time
from bone_core import Prisma
from bone_entity import ConversationalEntity

st.set_page_config(
    page_title="BONEAMANITA 14.0.0",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded")
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: #0e1117;
        color: #00ff41;
        font-family: 'Courier New', monospace;
    }
    .stMarkdown {
        font-family: 'Courier New', monospace;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem; 
    }
    .stProgress > div > div > div > div {
        background-color: #00ff41;
    }
</style>
""", unsafe_allow_html=True)
if "entity" not in st.session_state:
    with st.status("Initializing System Kernel...", expanded=True) as status:
        st.write("Waking the Entity...")
        st.session_state.entity = ConversationalEntity(user_name="Traveler")
        boot_packet = st.session_state.entity.boot_system()
        st.write("Loading Neural Weights...")
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": boot_packet.text})
        st.session_state.meta = {
            "mood": boot_packet.mood,
            "voltage": boot_packet.voltage,
            "location": boot_packet.location,
            "health": boot_packet.health,
            "stamina": boot_packet.stamina}
        status.update(label="System Online", state="complete", expanded=False)
with st.sidebar:
    st.title("BoneAmanita v14.0.0")
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("VOLTAGE", f"{st.session_state.meta.get('voltage', 0.0):.1f}v")
    col2.metric("MOOD", st.session_state.meta.get('mood', 'Booting'))
    st.metric("LOCATION", st.session_state.meta.get('location', 'Void'))
    st.divider()
    st.write("BIO.STATUS")
    health_val = st.session_state.meta.get('health', 100.0)
    st.progress(min(1.0, max(0.0, health_val / 100.0)), text=f"INTEGRITY: {health_val:.1f}%")
    stamina_val = st.session_state.meta.get('stamina', 100.0)
    st.progress(min(1.0, max(0.0, stamina_val / 100.0)), text=f"STAMINA: {stamina_val:.1f}%")
    st.divider()
    if st.button("EMERGENCY SAVE", type="primary"):
        save_msg = st.session_state.entity.save()
        st.success(save_msg)
st.title("BONEAMANITA 14.0.0")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
if prompt := st.chat_input("Enter signal..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.status("Processing Signal...", expanded=True) as status:
            response_packet = st.session_state.entity.talk(prompt)
            full_response = response_packet.text
            st.session_state.meta = {
                "mood": response_packet.mood,
                "voltage": response_packet.voltage,
                "location": response_packet.location,
                "health": response_packet.health,
                "stamina": response_packet.stamina}
            status.update(label="Transmission Received", state="complete", expanded=False)
            st.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

class Projector:
    def __init__(self):
        self.width = 60

    def render(self, physics_ctx: Dict, data_ctx: Dict, mind_ctx: tuple, reality_depth: int = 1) -> str:
        physics = physics_ctx.get("physics", {})
        status_line = self._render_vital_strip(data_ctx, mind_ctx)
        physics_line = self._render_physics_strip(physics, data_ctx.get("vectors", {}))
        zone = physics.get("zone", "UNKNOWN")
        lens = mind_ctx[0] if mind_ctx else "RAW"
        depth_map = {0: "TERMINAL", 1: "SIM", 2: "VILLAGE", 3: "DEBUG", 4: "DEEP_CX"}
        depth_label = depth_map.get(reality_depth, "UNKNOWN")
        depth_marker = f"{Prisma.VIOLET}[D{reality_depth}:{depth_label}]{Prisma.RST}"
        context_line = f"{Prisma.GRY}📍 {zone} // 👁️ {lens}{Prisma.RST} // {depth_marker}"
        div = f"{Prisma.GRY}{'─' * 60}{Prisma.RST}"
        return f"{status_line}\n{physics_line}\n{context_line}\n{div}"

    def _render_vital_strip(self, data: Dict, mind: tuple) -> str:
        health = data.get("health", 100)
        stamina = data.get("stamina", 100)
        atp = data.get("bio", {}).get("atp") or 0
        dignity = data.get("dignity", 100)
        hp_bar = self._mini_bar(health, 100, 4, Prisma.RED)
        stm_bar = self._mini_bar(stamina, 100, 4, Prisma.GRN)
        dig_color = Prisma.VIOLET if dignity > 50 else Prisma.GRY
        dig_icon = "✦" if dignity > 80 else "✧"
        role = str(mind[2]).upper() if mind and len(mind) > 2 else "OBSERVER"
        return (
            f"{Prisma.WHT}♦ {role}{Prisma.RST}   "
            f"HP {hp_bar}  STM {stm_bar}  "
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

    def _mini_bar(self, val, max_val, width, color):
        if max_val == 0: return ""
        ratio = max(0.0, min(1.0, val / max_val))
        fill = int(ratio * width)
        empty = width - fill
        return f"{color}{'█'*fill}{Prisma.GRY}{'░'*empty}{Prisma.RST}"

class GeodesicRenderer:
    def __init__(self, engine_ref, chroma_ref, strunk_ref, valve_ref):
        self.eng = engine_ref
        self.projector = Projector()
        self.vsl_chroma = chroma_ref
        self.strunk_white = strunk_ref

    def render_frame(self, ctx, current_tick: int, current_events: List[Dict]) -> Dict[str, Any]:
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
        if "The system is listening." in clean_ui:
            clean_ui = clean_ui.replace("The system is listening.", "")
        if hasattr(self.eng, 'soul'):
            soul_ui = self.render_soul_strip(self.eng.soul)
            clean_ui = f"{clean_ui}\n{soul_ui}"
        structured_logs = self.compose_logs(ctx.logs, current_events, current_tick)
        return {
            "type": "GEODESIC_FRAME",
            "ui": clean_ui,
            "logs": structured_logs,
            "metrics": self.eng.get_metrics(bio.get("atp", 0.0))}

    def render_dashboard(self, ctx) -> str:
        physics = ctx.physics
        mind = ctx.mind_state
        bio = ctx.bio_result
        mind_tuple = (mind.get("lens"), mind.get("thought"), mind.get("role"))
        dignity_val = 100.0
        if hasattr(self.eng, 'soul') and hasattr(self.eng.soul, 'anchor'):
            dignity_val = self.eng.soul.anchor.dignity_reserve
        data_ctx = {
            "health": self.eng.health,
            "stamina": self.eng.stamina,
            "bio": bio,
            "dignity": dignity_val,
            "vectors": physics.get("vector", {})}
        current_depth = 1
        if hasattr(ctx, "reality_stack"):
            current_depth = ctx.reality_stack.current_depth
        return self.projector.render(
            {"physics": physics},
            data_ctx,
            mind_tuple,
            reality_depth=current_depth)

    def render_soul_strip(self, soul_ref) -> str:
        if not soul_ref: return ""
        obsession = soul_ref.current_obsession or "Void"
        return f"{Prisma.GRY}--- Obsession: {obsession} ---{Prisma.RST}"

    @staticmethod
    def compose_logs(logs: list, events: list, tick: int) -> List[str]:
        all_logs = [str(l) for l in logs if l is not None]
        for e in events:
            if e and e.get("text"):
                all_logs.append(e["text"])
        if not all_logs: return []
        unique_logs = []
        seen = set()
        for l in all_logs:
            if l not in seen:
                unique_logs.append(l)
                seen.add(l)
        structured = []
        for log in unique_logs:
            if "CRITICAL" in log or "RUPTURE" in log:
                structured.append(f"{Prisma.RED}► {log}{Prisma.RST}")
            elif "PHASE" in log:
                structured.append(f"{Prisma.CYN}{log}{Prisma.RST}")
            else:
                structured.append(f"• {log}")
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

def get_renderer(engine_ref, chroma_ref, strunk_ref, valve_ref, mode="STANDARD"):
    base = GeodesicRenderer(engine_ref, chroma_ref, strunk_ref, valve_ref)
    if mode == "PERFORMANCE":
        return CachedRenderer(base)
    return base