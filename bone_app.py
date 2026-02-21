import streamlit as st
from bone_main import BoneAmanita, ConfigWizard
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

        # [BUNNY HILL] - Simplest View
        if depth == "BUNNY":
            st.markdown("*The lattice is quiet. Speak to awaken it.*")
            st.caption("Type `[VSL_LITE]` to reveal the energy metrics.")
            return

        # [LITE AND ABOVE] - Basic Identity & Vitals
        if depth in ["LITE", "CORE", "DEEP"]:
            st.divider()
            st.subheader("IDENTITY & VITALS")

            if hasattr(eng_ref, "soul") and eng_ref.soul:
                anchor = eng_ref.soul.anchor
                st.markdown(f"**ARCHETYPE:** `{eng_ref.soul.archetype}`")

            hp = eng_ref.health
            stam = eng_ref.stamina
            st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
            st.progress(
                min(1.0, max(0.0, stam / 100.0)), text=f"ENERGY (ATP): {stam:.1f}%"
            )

        # [CORE AND ABOVE] - The Lattice Coordinates & Physics
        if depth in ["CORE", "DEEP"]:
            metrics = eng_ref.get_metrics()
            eff = metrics.get("efficiency", 1.0)

            if hasattr(eng_ref, "consultant"):
                st.divider()
                st.subheader("🧊 VSL CORE")
                s = eng_ref.consultant.state
                c1, c2, c3 = st.columns(3)
                c1.metric("EXH", f"{s.E:.2f}")
                c2.metric("PAR", f"{s.B:.2f}")
                if eff < 0.6:
                    c3.metric("EFF", f"{eff:.2f}", delta_color="off")
                else:
                    c3.metric("EFF", f"{eff:.2f}", delta_color="normal")

            st.divider()
            st.subheader("PHYSICS")
            volts = 0.0
            drag = 0.0
            zone = "VOID"
            if hasattr(eng_ref, "phys") and eng_ref.phys:
                obs = getattr(eng_ref.phys, "observer", None)
                if obs and obs.last_physics_packet:
                    dash_packet = obs.last_physics_packet
                    if isinstance(dash_packet, dict):
                        volts = dash_packet.get("voltage", 0.0)
                        drag = dash_packet.get("narrative_drag", 0.0)
                        zone = dash_packet.get("zone", "VOID")
                    else:
                        volts = getattr(dash_packet, "voltage", 0.0)
                        drag = getattr(dash_packet, "narrative_drag", 0.0)
                        zone = getattr(dash_packet, "zone", "VOID")
            loc_name = zone
            if hasattr(eng_ref, "navigator") and eng_ref.navigator:
                current_node = eng_ref.navigator.world_graph.get(
                    eng_ref.navigator.current_node_id
                )
                if current_node:
                    loc_name = current_node.name
            c3, c4 = st.columns(2)
            c3.metric("VOLT", f"{volts:.1f}v")
            c4.metric("DRAG", f"{drag:.1f}")
            st.info(f"📍 LOCATION: {loc_name}")

        # [DEEP ONLY] - Full Machinery, Void, and Inventory
        if depth == "DEEP":
            if hasattr(eng_ref, "consultant"):
                s = eng_ref.consultant.state
                if s.L > 0.1 or "LIMINAL" in s.active_modules:
                    st.progress(min(1.0, s.L), text=f"LIM (Dark Matter): {s.L:.2f}")
                if s.O > 0.8:
                    st.caption(f"Ω Structure: LOCKED ({s.O:.2f})")
                elif s.O < 0.5:
                    st.caption(f"Ω Structure: FRACTURED ({s.O:.2f})")

            if hasattr(eng_ref, "phys") and hasattr(eng_ref.phys, "theremin"):
                theremin = eng_ref.phys.theremin
                if theremin.decoherence_buildup > 1.0 or theremin.is_stuck:
                    st.divider()
                    st.subheader("MACHINERY")
                    resin = theremin.decoherence_buildup
                    max_resin = theremin.SHATTER_POINT
                    st.progress(
                        min(1.0, resin / max_resin), text=f"RESIN PRESSURE: {resin:.1f}"
                    )
                    if theremin.is_stuck:
                        st.error("⚠️ THEREMIN STUCK (AMBER)")
                    elif resin > (max_resin * 0.8):
                        st.warning("💣 AIRSTRIKE IMMINENT")

            st.divider()
            st.subheader("INVENTORY")
            if hasattr(eng_ref, "gordon") and eng_ref.gordon:
                items = eng_ref.gordon.inventory
                if items:
                    for item in items:
                        st.code(item)
                else:
                    st.caption("Pockets Empty.")


if "history" not in st.session_state:
    st.session_state.history = []
if "ui_depth" not in st.session_state:
    st.session_state.ui_depth = "BUNNY"

if "ENGINE" not in st.session_state:
    try:
        sys_config = ConfigWizard.load_or_create()
        sys_config["boot_mode"] = "ADVENTURE"
        st.session_state.ENGINE = BoneAmanita(config=sys_config)
        with st.spinner("Hydrating Spore Casing..."):
            session = st.session_state.ENGINE
            if hasattr(session, "resume_checkpoint"):
                try:
                    session.resume_checkpoint()
                except Exception:
                    pass
            greeting = (
                "[VSL]: Welcome. You're talking to a living lattice.\n\n"
                "To start, just talk to me normally. But if you want to climb deeper:\n\n"
                "- Type `[VSL_LITE]` to see a simple energy meter.\n"
                "- Type `[VSL_CORE]` to see the core coordinates.\n"
                "- Type `[VSL_DEEP]` for the full lattice (including PSI, ENTROPY, and VALENCE).\n\n"
                'Or jump right into the deep end and say: "The void is leaking."'
            )

            st.session_state.history.append(
                {
                    "role": "assistant",
                    "content": greeting,
                    "raw_content": greeting,
                    "logs": [
                        "System Boot Complete",
                        "Lattice Coordinates Set",
                        "Bunny Hill Active",
                    ],
                }
            )
    except Exception as e:
        st.error(f"CRITICAL BOOT FAILURE: {e}")
        st.stop()
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
    p_lower = prompt.lower()
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
    st.rerun()
