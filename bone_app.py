import streamlit as st
from bone_main import BoneAmanita, ConfigWizard, typewriter
from bone_types import Prisma

st.set_page_config(
    page_title="BONEAMANITA [GLASS TERMINAL]",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
<style>
    /* TERMINAL VIBES */
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; }
    /* INPUT FIELDS */
    .stTextInput > div > div > input { 
        background-color: #111; 
        color: #00ff41; 
        border: 1px solid #333; 
        font-family: 'Courier New', monospace; 
    }
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    /* METRICS */
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; color: #00ff41 !important; }
    /* CHAT BUBBLES */
    .stChatMessage { background-color: #0e1117; border: 1px solid #222; border-radius: 5px; margin-bottom: 15px; }
    /* EXPANDER HEADERS */
    .streamlit-expanderHeader { font-family: 'Courier New', monospace; font-size: 0.8rem; color: #666; }
</style>
""",
    unsafe_allow_html=True,
)

def clean_engine_output(raw_text):
    if not raw_text:
        return "No signal."
    clean = Prisma.strip(raw_text)
    return clean.split("──────")[-1].strip() if "──────" in clean else clean

def format_log_entry(log_str):
    clean = Prisma.strip(log_str).strip()
    if "██" in clean or "♦ THE ARCHITECT" in clean:
        return None
    icon_map = {
        "TOWN HALL": "📜", "VITAL SIGNS": "🩺", "PARADOX BLOOM": "🌷",
        "CARTOGRAPHER": "🗺️", "[BIO]": "🧬", "[PHYSICS]": "⚡", "VOLTAGE": "⚡",
        "ASCENSION": "✨", "AIRSTRIKE": "💣", "LEGACY": "⛓️", "EFFICIENCY": "📉",
        "[COUNCIL]": "⚖️", "[SLASH]": "🗡️", "SANTIAGO": "🗡️", "PINKER": "🗡️",
        "CRITICAL": "🔴", "VSL": "🧊"
    }
    for key, icon in icon_map.items():
        if key in clean:
            text = clean.replace(key, "").replace(icon, "").strip()
            return f"{icon} {text}" if text else f"{icon} {key}"
    return f"🔹 {clean}"


def render_dashboard(eng_ref):
    mode = getattr(eng_ref, "boot_mode", "ADVENTURE")
    depth = st.session_state.get("ui_depth", "BUNNY")

    with st.sidebar:
        st.title("💀 BONEAMANITA")
        st.caption(
            f"Kernel: {getattr(eng_ref, 'kernel_hash', 'UNKNOWN')} | Mode: {mode}"
        )

        if mode == "ADVENTURE":
            st.markdown("*The mist parts. A new path lies ahead.*")
        elif mode == "CREATIVE":
            st.markdown("*The canvas is waiting. Paint with voltage.*")
            if depth == "BUNNY":
                st.caption("Type `[VSL_LITE]` to reveal machinery.")
        elif mode == "TECHNICAL":
            st.markdown("*System nominal. Diagnostic mode ready.*")
            if depth == "BUNNY":
                st.caption("Type `[VSL_DEEP]` for full telemetry.")
        else:
            st.markdown("*The connection is stable.*")

        phys_dict = {}
        if hasattr(eng_ref, "phys") and eng_ref.phys:
            obs = getattr(eng_ref.phys, "observer", None)
            if obs and obs.last_physics_packet:
                dash_packet = obs.last_physics_packet
                phys_dict = (
                    dash_packet
                    if isinstance(dash_packet, dict)
                    else dash_packet.to_dict()
                )

        zone = phys_dict.get("zone", "UNKNOWN")
        if hasattr(eng_ref, "navigator") and eng_ref.navigator:
            current_node = eng_ref.navigator.world_graph.get(
                eng_ref.navigator.current_node_id
            )
            if current_node:
                zone = current_node.name

        if depth == "BUNNY" and mode != "ADVENTURE":
            return
        show_vitals = getattr(eng_ref, "mode_settings", {}).get("show_vitals", True)
        if show_vitals and depth in ["BUNNY", "LITE", "CORE", "DEEP"]:
            st.divider()
            st.subheader("STATUS" if mode == "ADVENTURE" else "VITALS")
            hp = phys_dict.get("health", getattr(eng_ref, "health", 100.0))
            stam = phys_dict.get("stamina", getattr(eng_ref, "stamina", 100.0))
            st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"❤️ Health: {hp:.1f}%")
            st.progress(
                min(1.0, max(0.0, stam / 100.0)), text=f"🔋 Stamina: {stam:.1f}%"
            )

        if mode == "ADVENTURE" or depth in ["CORE", "DEEP"]:
            st.info(f"📍 LOC: {zone}")

        if depth in ["CORE", "DEEP"]:
            if hasattr(eng_ref, "soul") and eng_ref.soul:
                st.caption(f"**ARCHETYPE:** `{eng_ref.soul.archetype}`")

        if depth in ["CORE", "DEEP"]:
            st.divider()
            st.subheader("🧊 VSL CORE")
            volts = phys_dict.get("voltage", 30.0)
            drag = phys_dict.get("friction", phys_dict.get("narrative_drag", 0.6))
            exhaustion = phys_dict.get("exhaustion", phys_dict.get("E", 0.2))
            contradiction = phys_dict.get("contradiction", phys_dict.get("beta", 0.4))
            trauma = phys_dict.get("trauma", phys_dict.get("T", 0.0))

            c1, c2 = st.columns(2)
            c1.metric("⚡ Volt (V)", f"{volts:.1f}v")
            c2.metric("⚓ Drag (F)", f"{drag:.1f}")
            c1.metric("🧊 Exh (E)", f"{exhaustion:.2f}")
            c2.metric("⚔️ Para (β)", f"{contradiction:.2f}")
            st.metric("🏺 Trauma (T)", f"{trauma:.0f}")

        if depth == "DEEP":
            st.divider()
            st.subheader("🌌 DEEP PHYSICS")
            psi = phys_dict.get("psi", 0.0)
            chi = phys_dict.get("chi", 0.0)
            valence = phys_dict.get("valence", 0.0)
            liminal = phys_dict.get("vector", {}).get("LAMBDA", 0.0)
            c3, c4, c5 = st.columns(3)
            c3.metric("Void (Ψ)", f"{psi:.2f}")
            c4.metric("Chaos (Χ)", f"{chi:.2f}")
            c5.metric("Val (♥)", f"{valence:.2f}")
            if liminal > 0:
                st.progress(min(1.0, liminal), text=f"🌌 Liminal (Λ): {liminal:.2f}")
            if hasattr(eng_ref, "bio") and hasattr(eng_ref.bio, "endo"):
                endo = eng_ref.bio.endo
                st.caption(
                    f"🩸 **CHEM:** ADR: {endo.adrenaline:.2f} | COR: {endo.cortisol:.2f} | OXY: {endo.oxytocin:.2f}"
                )

            if hasattr(eng_ref, "phys") and hasattr(eng_ref.phys, "theremin"):
                theremin = eng_ref.phys.theremin
                if theremin.decoherence_buildup > 1.0 or theremin.is_stuck:
                    st.divider()
                    st.subheader("MACHINERY")
                    resin = theremin.decoherence_buildup
                    max_resin = theremin.SHATTER_POINT
                    st.progress(
                        min(1.0, resin / max_resin),
                        text=f"🎻 RESIN PRESSURE: {resin:.1f}",
                    )
                    if theremin.is_stuck:
                        st.error("⚠️ THEREMIN STUCK (AMBER)")
                    elif resin > (max_resin * 0.8):
                        st.warning("💣 AIRSTRIKE IMMINENT")

        if mode == "ADVENTURE" or depth in ["CORE", "DEEP"]:
            st.divider()
            st.subheader("🎒 INVENTORY")
            if hasattr(eng_ref, "gordon") and eng_ref.gordon:
                items = eng_ref.gordon.inventory
                if items:
                    for item in items:
                        st.code(item)
                else:
                    st.caption("Pockets Empty.")


if "history" not in st.session_state:
    st.session_state.history = []
if "ENGINE" not in st.session_state:
    try:
        sys_config = ConfigWizard.load_or_create()
        st.session_state.ENGINE = BoneAmanita(config=sys_config)
        if "ui_depth" not in st.session_state:
            st.session_state.ui_depth = st.session_state.ENGINE.mode_settings.get("default_ui_depth", "BUNNY")
        with st.spinner("Hydrating Spore Casing..."):
            session = st.session_state.ENGINE
            boot_packet = session.engage_cold_boot()
            if boot_packet:
                raw_ui = boot_packet.get("ui", "System Ready.")
                print(
                    "\n" + Prisma.paint("/// STREAMLIT TERMINAL MIRROR ACTIVE ///", "C")
                )
                if "──────" in raw_ui:
                    parts = raw_ui.split("──────")
                    print(
                        parts[0]
                        + "────────────────────────────────────────────────────────────"
                    )
                    typewriter("\n" + parts[-1].strip())
                else:
                    typewriter(raw_ui)
                clean_ui = clean_engine_output(raw_ui)
                st.session_state.history.append(
                    {
                        "role": "assistant",
                        "content": clean_ui,
                        "raw_content": raw_ui,
                        "logs": boot_packet.get("logs", ["System Boot Complete"]),
                    }
                )
    except Exception as e:
        st.error(f"CRITICAL BOOT FAILURE: {e}")
        st.stop()
engine = st.session_state.ENGINE
render_dashboard(engine)
for hist_msg in st.session_state.history:
    with st.chat_message(hist_msg["role"]):
        raw = hist_msg.get("raw_content", hist_msg["content"])
        clean_show = clean_engine_output(raw)
        st.markdown(clean_show)
        if "logs" in hist_msg and hist_msg["logs"]:
            with st.expander("SYSTEM INTERNALS"):
                for hist_log in hist_msg["logs"]:
                    formatted = format_log_entry(hist_log)
                    if formatted:
                        st.caption(formatted)
if prompt := st.chat_input("Broadcast Signal..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    p_lower = prompt.strip().lower()
    if p_lower in ["exit", "quit", "/exit", "/quit"]:
        st.warning("Disconnecting from the lattice...")
        engine.shutdown()
        st.success("Session Terminated. You may close the tab.")
        st.stop()
    user_name = getattr(engine, "user_name", "TRAVELER")
    print(f"\n{Prisma.paint(f'{user_name} >', 'W')} {prompt}")
    if "[vsl_lite]" in p_lower:
        st.session_state.ui_depth = "LITE"
    elif "[vsl_core]" in p_lower:
        st.session_state.ui_depth = "CORE"
    elif "[vsl_deep]" in p_lower:
        st.session_state.ui_depth = "DEEP"
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.spinner("Calculating Geodesics..."):
        try:
            packet = engine.process_turn(prompt)
        except Exception as e:
            packet = {"ui": f"RUNTIME ERROR: {e}", "logs": ["CRITICAL FAILURE"]}
    logs = packet.get("logs", [])
    raw_response = packet.get("ui", "No signal.")
    clean_response = clean_engine_output(raw_response)
    with st.chat_message("assistant"):
        st.markdown(clean_response)
        if logs:
            with st.expander("SYSTEM INTERNALS"):
                for log in logs:
                    formatted = format_log_entry(log)
                    if formatted:
                        st.caption(formatted)
    st.session_state.history.append(
        {
            "role": "assistant",
            "content": clean_response,
            "raw_content": raw_response,
            "logs": logs,
        }
    )
    if packet.get("type") == "DEATH":
        st.error("System Halt. The timeline has ended.")
        st.stop()
    st.rerun()
