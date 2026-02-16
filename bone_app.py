""" bone_app.py - The Glass Terminal Interface v1.9 """

import streamlit as st
import re
from bone_main import BoneAmanita, ConfigWizard

st.set_page_config(
    page_title="BONEAMANITA [GLASS TERMINAL]",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown("""
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
""", unsafe_allow_html=True)

def clean_engine_output(raw_text):
    if not raw_text: return "No signal."
    clean = re.sub(r'\x1b\[[0-9;]*m', '', raw_text)
    if "──────" in clean:
        clean = clean.split("──────")[-1].strip()
    return clean

def format_log_entry(log_str):
    clean = re.sub(r'\x1b\[[0-9;]*m', '', log_str).strip()

    if "██" in clean or "♦ THE ARCHITECT" in clean: return None
    if "[BIO]" in clean: return f"🧬 {clean.replace('[BIO]', '')}"
    if "[PHYSICS]" in clean or "VOLTAGE" in clean: return f"⚡ {clean.replace('[PHYSICS]', '')}"
    if "ASCENSION" in clean: return f"✨ {clean}"
    if "AIRSTRIKE" in clean: return f"💣 {clean}"
    if "LEGACY" in clean: return f"⛓️ {clean}"
    if "EFFICIENCY" in clean: return f"📉 {clean}"
    if "[COUNCIL]" in clean: return f"⚖️ {clean.replace('[COUNCIL]', '')}"
    if "[SLASH]" in clean or "SANTIAGO" in clean or "PINKER" in clean: return f"🗡️ {clean}"
    if "CRITICAL" in clean: return f"🔴 {clean}"
    if "VSL" in clean: return f"🧊 {clean}"

    return f"🔹 {clean}"

def render_dashboard(eng_ref):
    mode = getattr(eng_ref, "boot_mode", "ADVENTURE")

    with st.sidebar:
        st.title("💀 BONEAMANITA")
        st.caption(f"Kernel: {getattr(eng_ref, 'kernel_hash', 'UNKNOWN')} | Mode: {mode}")

        st.divider()
        st.subheader("IDENTITY")
        if hasattr(eng_ref, 'soul') and eng_ref.soul:
            anchor = eng_ref.soul.anchor
            dig = anchor.dignity_reserve
            dig_color = "red" if dig < 30 else ("orange" if dig < 60 else "green")
            st.markdown(f"**DIGNITY:** :{dig_color}[{int(dig)}%]")
            st.progress(min(100, max(0, int(dig))))
            if anchor.agency_lock:
                st.error("🔒 AGENCY LOCKED")
            st.markdown(f"**ARCHETYPE:** `{eng_ref.soul.archetype}`")
            if eng_ref.soul.current_obsession:
                 st.caption(f"Obsession: {eng_ref.soul.current_obsession}")

        st.divider()
        st.subheader("STATUS")

        hp = eng_ref.health
        stam = eng_ref.stamina

        st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
        st.progress(min(1.0, max(0.0, stam / 100.0)), text=f"STAMINA: {stam:.1f}%")
        atp = 0.0
        if hasattr(eng_ref, 'bio') and eng_ref.bio and hasattr(eng_ref.bio, 'mito'):
            atp = eng_ref.bio.mito.state.atp_pool

        eff = getattr(eng_ref.host_stats, 'efficiency_index', 1.0)
        c_atp, c_eff = st.columns(2)
        c_atp.metric("ATP", f"{atp:.0f} J")

        if eff < 0.6:
            c_eff.metric("EFFICIENCY", f"{eff:.2f}", delta_color="off")
        elif eff > 1.2:
            c_eff.metric("EFFICIENCY", f"{eff:.2f}", delta_color="inverse")
        else:
            c_eff.metric("EFFICIENCY", f"{eff:.2f}", delta_color="normal")

        if hasattr(eng_ref, 'consultant'):
            st.divider()
            st.subheader("🧊 VSL LATTICE")
            s = eng_ref.consultant.state
            c1, c2 = st.columns(2)
            c1.metric("EXH", f"{s.E:.2f}")
            c2.metric("PAR", f"{s.B:.2f}")

            if s.L > 0.1 or "LIMINAL" in s.active_modules:
                st.progress(min(1.0, s.L), text=f"LIM (Dark Matter): {s.L:.2f}")

            if s.O > 0.8:
                st.caption(f"Ω Structure: LOCKED ({s.O:.2f})")
            elif s.O < 0.5:
                st.caption(f"Ω Structure: FRACTURED ({s.O:.2f})")

        st.divider()
        st.subheader("PHYSICS")
        volts = 0.0
        drag = 0.0
        zone = "VOID"

        if hasattr(eng_ref, 'phys') and eng_ref.phys:
            obs = getattr(eng_ref.phys, 'observer', None)
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

        c3, c4 = st.columns(2)
        c3.metric("VOLT", f"{volts:.1f}v")
        c4.metric("DRAG", f"{drag:.1f}")
        st.info(f"📍 ZONE: {zone}")

        if hasattr(eng_ref, 'phys') and hasattr(eng_ref.phys, 'theremin'):
            theremin = eng_ref.phys.theremin
            if theremin.decoherence_buildup > 1.0 or theremin.is_stuck:
                st.divider()
                st.subheader("MACHINERY")
                resin = theremin.decoherence_buildup
                max_resin = theremin.SHATTER_POINT
                st.progress(min(1.0, resin / max_resin), text=f"RESIN PRESSURE: {resin:.1f}")
                if theremin.is_stuck:
                    st.error("⚠️ THEREMIN STUCK (AMBER)")
                elif resin > (max_resin * 0.8):
                    st.warning("💣 AIRSTRIKE IMMINENT")

        st.divider()
        st.subheader("INVENTORY")
        if hasattr(eng_ref, 'gordon') and eng_ref.gordon:
            items = eng_ref.gordon.inventory
            if items:
                for item in items:
                    st.code(item)
            else:
                st.caption("Pockets Empty.")
        else:
            st.warning("Inventory Module Sleeping.")


if "history" not in st.session_state:
    st.session_state.history = []

if "ENGINE" not in st.session_state:
    try:
        sys_config = ConfigWizard.load_or_create()
        sys_config["boot_mode"] = "ADVENTURE"
        st.session_state.ENGINE = BoneAmanita(config=sys_config)

        with st.spinner("Hydrating Spore Casing..."):
            session = st.session_state.ENGINE

            if hasattr(session, 'resume_checkpoint'):
                try:
                    session.resume_checkpoint()
                except Exception:
                    pass

            st.session_state.history.append({
                "role": "assistant",
                "content": "VSL-CryoSomatic Hypervisor v1.9 ONLINE.\nThe Glacier is listening. [Type 'start' to begin]",
                "raw_content": "VSL-CryoSomatic Hypervisor v1.9 ONLINE.\nThe Glacier is listening. [Type 'start' to begin]",
                "logs": ["System Boot Complete", "Lattice Coordinates Set", "Slash Council: STANDBY"]
            })

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
                    if formatted: st.caption(formatted)

if prompt := st.chat_input("Broadcast Signal..."):
    with st.chat_message("user"):
        st.markdown(prompt)
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
                    if formatted: st.caption(formatted)

    st.session_state.history.append({
        "role": "assistant",
        "content": clean_response,
        "raw_content": raw_response,
        "logs": logs
    })

    st.rerun()