""" bone_app.py - The Glass Terminal Interface (Refactored & Linted) """

import streamlit as st
import time, json, os, re
from bone_main import BoneAmanita, ConfigWizard
from bone_core import Prisma

st.set_page_config(
    page_title="BONEAMANITA [GLASS TERMINAL]",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* GLOBAL THEME OVERRIDES */
    .stApp {
        background-color: #050505;
        color: #00ff41;
        font-family: 'Courier New', monospace;
    }
    
    /* CHAT MESSAGE BUBBLES */
    .stChatMessage {
        background-color: #0e1117;
        border: 1px solid #222;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    /* INPUT BOX */
    .stTextInput > div > div > input {
        background-color: #111;
        color: #00ff41;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }
    
    /* METRICS & TEXT */
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        color: #00ff41 !important;
    }
    p, .stMarkdown {
        line-height: 1.6 !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        border: 1px solid #00ff41;
        color: #00ff41;
        background-color: transparent;
        font-family: 'Courier New', monospace;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #00ff41;
        color: #000;
        border-color: #00ff41;
    }
</style>
""", unsafe_allow_html=True)

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def format_log_entry(log_str):
    clean = strip_ansi(log_str)
    if "██" in clean or "THE ARCHITECT" in clean: return None
    if "[BIO]" in clean: return f"🧬 {clean}"
    if "[PHYSICS]" in clean or "VOLTAGE" in clean: return f"⚡ {clean}"
    if "[COUNCIL]" in clean: return f"⚖️ {clean}"
    if "[REM]" in clean: return f"💤 {clean}"
    if "ERROR" in clean or "CRITICAL" in clean: return f"❌ {clean}"
    return f"🔹 {clean}"

def analyze_pulse(pulse_data: dict) -> str:
    chem = pulse_data.get("chem", {})
    if chem.get("COR", 0) > 0.6: return "Defensive"
    if chem.get("DA", 0) > 0.6: return "Manic"
    if chem.get("OXY", 0) > 0.6: return "Affectionate"

    energy_level = pulse_data.get("mito", {}).get("atp", 100)
    if energy_level < 20: return "Exhausted"
    return "Neutral"

def analyze_voltage(input_volts: float) -> tuple:
    if input_volts > 20.0: return "CRITICAL", "⚡"
    if input_volts > 15.0: return "HIGH", "🔥"
    if input_volts < 5.0: return "LOW", "❄️"
    return "NOMINAL", "🟢"


def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []

    if "engine" not in st.session_state:
        if not os.path.exists(ConfigWizard.CONFIG_FILE):
            st.session_state.needs_setup = True
            return

        with st.spinner("Bootstrapping Consciousness..."):
            try:
                sys_config = ConfigWizard.load_or_create()
                new_engine = BoneAmanita(config=sys_config)

                restored, saved_history = new_engine.resume_checkpoint()
                if restored and saved_history:
                    st.session_state.history = saved_history
                    st.toast("System State Restored.")
                else:
                    boot_packet = new_engine.engage_cold_boot()
                    if boot_packet and "ui" in boot_packet:
                        st.session_state.history.append({
                            "role": "assistant",
                            "content": strip_ansi(boot_packet["ui"]),
                            "logs": boot_packet.get("logs", [])
                        })

                st.session_state.engine = new_engine
                st.session_state.needs_setup = False

            except Exception as e:
                st.error(f"Boot Failure: {e}")


init_session_state()

if st.session_state.get("needs_setup", False):
    st.title("/// SYSTEM SETUP ///")
    st.markdown("No configuration detected. Initialize parameters.")

    with st.form("setup_form"):
        user_name = st.text_input("Designation (User Name)", value="Traveler")
        provider = st.selectbox("Backend Provider", ["Ollama (Local)", "OpenAI (Cloud)", "Mock"])
        api_key = st.text_input("API Key (Required for Cloud)", type="password")
        model_name = st.text_input("Model ID", value="gpt-4" if "Cloud" in provider else "llama3")

        if st.form_submit_button("IGNITE SYSTEM"):
            cfg = {
                "user_name": user_name,
                "provider": provider.split()[0].lower(),
                "model": model_name
            }
            if api_key: cfg["api_key"] = api_key
            if cfg["provider"] == "ollama":
                cfg["base_url"] = "http://127.0.0.1:11434/v1/chat/completions"

            with open(ConfigWizard.CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=4)

            st.rerun()
    st.stop()

engine = st.session_state.engine

with st.sidebar:
    st.header(f"IDENTITY: {engine.user_name.upper()}")
    st.divider()
    metrics = engine.get_metrics()
    bio_state = engine.bio.to_dict() if engine.bio else {}
    hp = metrics.get("health", 100)
    stam = metrics.get("stamina", 100)
    atp = bio_state.get("mito", {}).get("atp", 0)
    st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
    st.progress(min(1.0, max(0.0, stam / 100.0)), text=f"STAMINA: {stam:.1f}%")
    c1, c2 = st.columns(2)
    c1.metric("ATP", f"{atp:.1f} J")
    mood = analyze_pulse(bio_state)
    c2.metric("MOOD", mood)
    st.divider()
    phys_packet = engine.phys.observer.last_physics_packet if engine.phys else None
    volts = phys_packet.get("voltage", 0.0) if phys_packet else 0.0
    drag = phys_packet.get("narrative_drag", 0.0) if phys_packet else 0.0
    zone = phys_packet.get("zone", "VOID") if phys_packet else "VOID"
    volt_status, volt_icon = analyze_voltage(volts)
    c3, c4 = st.columns(2)
    c3.metric("VOLTAGE", f"{volts:.1f}v", delta=volt_icon)
    c4.metric("DRAG", f"{drag:.1f}")
    st.info(f"📍 ZONE: {zone}")
    st.divider()
    st.subheader("INVENTORY")
    inv = engine.gordon.inventory

    if inv:
        for item in inv: st.code(item, language=None)
    else:
        st.caption("Belt Empty.")
    st.divider()

    if st.button("💾 SAVE CHECKPOINT"):
        with st.spinner("Crystallizing State..."):
            msg = engine.save_checkpoint(history=st.session_state.history)
            st.toast(msg)

    if st.button("☣️ EMERGENCY DUMP"):
        msg = engine.emergency_save(exit_cause="MANUAL_UI")
        st.toast(msg)

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "logs" in msg and msg["logs"]:
            with st.expander("SYSTEM INTERNALS"):
                for log in msg["logs"]:
                    formatted = format_log_entry(log)
                    if formatted: st.caption(formatted)

if prompt := st.chat_input("Broadcast Signal..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Calculating Geodesics..."):
        packet = engine.process_turn(prompt)

    logs = packet.get("logs", [])
    raw_text = packet.get("ui", "No signal.")
    separator = "────────────────────────────────────────────────────────────"
    if separator in raw_text:
        parts = raw_text.split(separator)
        if len(parts) > 1: raw_text = parts[-1].strip()
    clean_text = strip_ansi(raw_text)
    st.session_state.history.append({
        "role": "assistant",
        "content": clean_text,
        "logs": logs})

    with st.chat_message("assistant"):
        st.markdown(clean_text)
        if logs:
            with st.expander("SYSTEM INTERNALS"):
                for log in logs:
                    formatted = format_log_entry(log)
                    if formatted: st.caption(formatted)

    engine.save_checkpoint(history=st.session_state.history)

    st.rerun()