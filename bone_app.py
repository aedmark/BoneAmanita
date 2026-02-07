""" bone_app.py - The Glass Terminal Interface (Fixed) """

import streamlit as st
import time
import json
import os
from bone_main import BoneAmanita, ConfigWizard
from bone_core import Prisma

st.set_page_config(
    page_title="BONEAMANITA [GLASS TERMINAL]",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stChatMessage .stMarkdown p {
        margin-bottom: 1.5em !important; /* Increased from 1.2em */
        line-height: 1.8 !important;     /* Increased from 1.6 */
        font-size: 1.05rem;
        display: block;                  /* Ensure block formatting */
    }
    
    /* Ensure lists don't look crushed */
    .stChatMessage .stMarkdown ul, .stChatMessage .stMarkdown ol {
        margin-bottom: 1.2em !important;
    }
    
    /* Main Background & Text */
    .stApp {
        background-color: #050505;
        color: #00ff41;
        font-family: 'Courier New', monospace;
    }
    
    /* Input Field Styling */
    .stTextInput > div > div > input {
        background-color: #111;
        color: #00ff41;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }
    
    /* Metric Values */
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        color: #00ff41 !important;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background-color: #00ff41;
    }
    
    /* Chat Messages - Container */
    .stChatMessage {
        background-color: #0e1117;
        border: 1px solid #222;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    /* Chat Messages - Typography Fixes */
    /* This targets the paragraph tags inside the markdown to ensure spacing */
    .stChatMessage .stMarkdown p {
        margin-bottom: 1.2em !important; /* Force paragraph spacing */
        line-height: 1.6 !important;     /* Improve readability */
        font-size: 1.05rem;
    }
    
    /* Button Styling */
    .stButton > button {
        border: 1px solid #00ff41;
        color: #00ff41;
        background-color: transparent;
        font-family: 'Courier New', monospace;
    }
    .stButton > button:hover {
        background-color: #00ff41;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

def strip_ansi(text):
    return Prisma.strip(text)

def format_log_entry(log_str):
    clean = strip_ansi(log_str)
    if "██" in clean or "♦ THE ARCHITECT" in clean:
        return None
    if "[BIO]" in clean: return f"🧬 {clean}"
    if "[PHYSICS]" in clean or "VOLTAGE" in clean: return f"⚡ {clean}"
    if "[COUNCIL]" in clean: return f"⚖️ {clean}"
    if "[REM]" in clean: return f"💤 {clean}"
    if "ERROR" in clean or "CRITICAL" in clean: return f"❌ {clean}"
    return f"🔹 {clean}"

if "history" not in st.session_state:
    st.session_state.history = []

def init_engine():
    try:
        config = ConfigWizard.load_or_create()
        if not config: return None
        new_instance = BoneAmanita(config)
        if not st.session_state.history:
            boot_packet = new_instance.engage_cold_boot()
            if boot_packet and "ui" in boot_packet:
                st.session_state.history.append({
                    "role": "assistant",
                    "content": boot_packet["ui"],
                    "logs": boot_packet.get("logs", [])})
            else:
                st.session_state.history.append({
                    "role": "system",
                    "content": "SYSTEM_BOOT: SEQUENCE COMPLETE. \nSIGNAL ESTABLISHED (NO DATA).",
                    "logs": ["Kernel Loaded.", "Telemetry Link Active."]})
        return new_instance
    except Exception as e:
        st.error(f"Critical Boot Error: {e}")
        return None
if not os.path.exists(ConfigWizard.CONFIG_FILE) and "ENGINE" not in st.session_state:
    st.title("/// SYSTEM SETUP ///")
    with st.form("setup_form"):
        user_name = st.text_input("Designation", value="Traveler")
        provider = st.selectbox("Backend", ["Ollama (Local)", "OpenAI (Cloud)", "Mock"])
        api_key = st.text_input("API Key (if Cloud)", type="password")
        model_name = st.text_input("Model ID", value="gpt-4" if provider == "OpenAI (Cloud)" else "llama3")
        if st.form_submit_button("IGNITE"):
            cfg = {"user_name": user_name, "provider": provider.split()[0].lower(), "model": model_name}
            if api_key: cfg["api_key"] = api_key
            if cfg["provider"] == "ollama": cfg["base_url"] = "http://127.0.0.1:11434/v1/chat/completions"
            with open(ConfigWizard.CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=4)
            st.rerun()
    st.stop()
if "ENGINE" not in st.session_state:
    with st.spinner("Hydrating Spore Casing..."):
        st.session_state.ENGINE = init_engine()
engine = st.session_state.ENGINE
with st.sidebar:
    st.header(f"IDENTITY: {engine.user_name.upper()}")
    st.divider()
    st.subheader("BIO.MONITOR")
    hp = engine.health
    stam = engine.stamina
    atp = engine.bio.mito.state.atp_pool
    st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
    st.progress(min(1.0, max(0.0, stam / 100.0)), text=f"STAMINA: {stam:.1f}%")
    c1, c2 = st.columns(2)
    c1.metric("ATP", f"{atp:.1f} J")
    c2.metric("ENZYME", "ACTIVE")
    st.divider()
    st.subheader("GEO.DESICS")
    volts = 0.0
    drag = 0.0
    zone = "VOID"
    if engine.phys and hasattr(engine.phys, 'observer') and engine.phys.observer.last_physics_packet:
        packet = engine.phys.observer.last_physics_packet
        volts = packet.get("voltage", 0.0) if isinstance(packet, dict) else getattr(packet, "voltage", 0.0)
        drag = packet.get("narrative_drag", 0.0) if isinstance(packet, dict) else getattr(packet, "narrative_drag", 0.0)
        zone = packet.get("zone", "VOID") if isinstance(packet, dict) else getattr(packet, "zone", "VOID")
    c3, c4 = st.columns(2)
    c3.metric("VOLTAGE", f"{volts:.1f}v")
    c4.metric("DRAG", f"{drag:.1f}")
    st.info(f"📍 ZONE: {zone}")

    st.divider()
    st.subheader("GORDON.KNOT")
    inv = engine.gordon.inventory
    if inv:
        for item in inv: st.code(item, language=None)
    else: st.caption("Belt Empty.")
    st.divider()
    if st.button("☣️ EMERGENCY DUMP"):
        msg = engine.emergency_save(exit_cause="MANUAL_UI")
        st.toast(msg)

# --- CHAT LOOP ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        content_to_show = msg.get("raw_content", msg["content"])
        clean_content = strip_ansi(content_to_show)
        separator = "────────────────────────────────────────────────────────────"
        if separator in clean_content:
            parts = clean_content.split(separator)
            if len(parts) > 1:
                content_to_show = parts[-1].strip()
        elif "📍" in clean_content and "//" in clean_content:
            lines = clean_content.splitlines()
            narrative_lines = []
            recording = False
            for line in lines:
                if recording: narrative_lines.append(line)
                if "📍" in line and "//" in line: recording = True
            if narrative_lines:
                content_to_show = "\n".join(narrative_lines).strip()
        st.markdown(strip_ansi(content_to_show))
        if "logs" in msg and msg["logs"]:
            with st.expander("SYSTEM INTERNALS"):
                for log in msg["logs"]:
                    formatted = format_log_entry(log)
                    if formatted:
                        st.caption(formatted)
if prompt := st.chat_input("Broadcast Signal..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.spinner("Calculating Geodesics..."):
        packet = engine.process_turn(prompt)
    separator = "────────────────────────────────────────────────────────────"
    logs = packet.get("logs", [])
    response_text = packet.get("raw_content", packet.get("ui", "No signal."))
    if separator in response_text:
        parts = response_text.split(separator)
        if len(parts) > 1:
            response_text = parts[-1].strip()
    response_text = strip_ansi(response_text)
    st.session_state.history.append({
        "role": "assistant",
        "content": response_text,
        "raw_content": response_text,
        "logs": logs
    })
    st.rerun()