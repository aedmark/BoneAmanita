""" bone_app.py - The Glass Terminal Interface (Restored & Polished) """

import streamlit as st
import time
import json
import os
import re
from bone_main import BoneAmanita, ConfigWizard
from bone_core import Prisma


def render_sidebar(eng_ref):
    if not hasattr(eng_ref, 'soul') or not eng_ref.soul:
        return
    soul = eng_ref.soul
    anchor = soul.anchor
    host_diag = "WAITING"
    if hasattr(eng_ref, 'symbiosis') and eng_ref.symbiosis.current_health:
        host_diag = eng_ref.symbiosis.current_health.diagnosis
    with st.sidebar:
        st.title("💀 BONEAMANITA")
        st.caption(f"Kernel: {getattr(eng_ref, 'kernel_hash', 'UNKNOWN')}")
        st.markdown("---")
        st.subheader("👁️ Symbiosis Link")
        if host_diag == "STABLE":
            st.success(f"SIGNAL: {host_diag}")
        elif host_diag in ["REFUSAL", "LOOPING"]:
            st.error(f"SIGNAL: {host_diag}")
        else:
            st.warning(f"SIGNAL: {host_diag}")
        dig = anchor.dignity_reserve
        st.subheader("⚓ Dignity Reserve")
        st.progress(min(100, max(0, int(dig))))
        if anchor.agency_lock:
            st.error("🔒 AGENCY LOCKED")
        elif dig < 30:
            st.warning("⚠ CRITICAL FADE")
        st.markdown("---")
        st.subheader("🩸 Endocrine Levels")
        chem = {}
        if hasattr(eng_ref, 'bio') and eng_ref.bio and eng_ref.bio.endo:
            chem = eng_ref.bio.endo.get_state()
        c1, c2 = st.columns(2)
        cor = chem.get("COR", 0.0)
        c1.metric("Cortisol", f"{cor:.2f}", delta="-Stress" if cor < 0.3 else "+Stress", delta_color="inverse")
        dop = chem.get("DOP", 0.0)
        c2.metric("Dopamine", f"{dop:.2f}", delta="Reward")
        st.markdown("---")
        st.subheader("🎭 Active Driver")
        st.markdown(f"**{soul.archetype}**")
        tenure = soul.archetype_tenure
        st.caption(f"Tenure: {tenure} cycles")
        with st.expander("System Vectors"):
            v = 0.0
            d = 0.0
            if hasattr(eng_ref, 'phys') and eng_ref.phys and hasattr(eng_ref.phys, 'observer'):
                v_packet = eng_ref.phys.observer.last_physics_packet
                if v_packet:
                    if isinstance(v_packet, dict):
                        v = v_packet.get("voltage", 0.0)
                        d = v_packet.get("narrative_drag", 0.0)
                    else:
                        v = getattr(v_packet, "voltage", 0.0)
                        d = getattr(v_packet, "narrative_drag", 0.0)
            st.metric("Voltage", f"{v:.1f}v")
            st.metric("Narrative Drag", f"{d:.1f}")
st.set_page_config(
    page_title="BONEAMANITA [GLASS TERMINAL]",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stChatMessage .stMarkdown p {
        margin-bottom: 1.5em !important;
        line-height: 1.8 !important;
        font-size: 1.05rem;
        display: block;
    }
    .stChatMessage .stMarkdown ul, .stChatMessage .stMarkdown ol {
        margin-bottom: 1.2em !important;
    }
    .stApp {
        background-color: #050505;
        color: #00ff41;
        font-family: 'Courier New', monospace;
    }
    .stTextInput > div > div > input {
        background-color: #111;
        color: #00ff41;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
    }
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        color: #00ff41 !important;
    }
    .stProgress > div > div > div > div {
        background-color: #00ff41;
    }
    .stChatMessage {
        background-color: #0e1117;
        border: 1px solid #222;
        border-radius: 5px;
        margin-bottom: 15px;
    }
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
    if not text: return ""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def clean_engine_output(raw_text):
    if not raw_text: return "No signal."

    clean = strip_ansi(raw_text)

    separator = "────────────────────────────────────────────────────────────"
    if separator in clean:
        parts = clean.split(separator)
        if len(parts) > 1:
            clean = parts[-1].strip()

    if "♦ THE ARCHITECT" in clean and "//" in clean:
        lines = clean.splitlines()
        content_lines = []
        recording = False
        for line in lines:
            if recording:
                content_lines.append(line)
                continue

            if line.strip().startswith("♦") or line.strip().startswith("⚡") or "HP ██" in line:
                continue

            if "─────" in line:
                recording = True
                continue

            content_lines.append(line)

        if recording and content_lines:
             clean = "\n".join(content_lines).strip()

    return clean

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

def generate_transcript(history, user_name="TRAVELER"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"# BONEAMANITA TRANSCRIPT - {timestamp}", f"Identity: {user_name}", "---"]
    for entry in history:
        raw_role = entry["role"].upper()
        display_name = raw_role
        if raw_role == "USER":
            display_name = user_name.upper()
        elif raw_role == "ASSISTANT":
            display_name = "THE SYSTEM"
        content = entry.get("raw_content", entry["content"])
        clean_content = strip_ansi(content)
        icon = "👤" if raw_role == "USER" else "💀"
        lines.append(f"\n### {icon} {display_name}")
        lines.append(clean_content)
        if "logs" in entry and entry["logs"]:
            lines.append("\n> **SYSTEM INTERNALS:**")
            for internal_log in entry["logs"]:
                clean_log = strip_ansi(str(internal_log))
                lines.append(f"> * {clean_log}")
    lines.append("\n---")
    lines.append("*End of Transmission*")
    return "\n".join(lines)


if "history" not in st.session_state:
    st.session_state.history = []

def init_engine():
    try:
        config = ConfigWizard.load_or_create()
        if not config: return None
        new_instance = BoneAmanita(config)
        restored, saved_history = new_instance.resume_checkpoint()
        if restored and saved_history:
            st.session_state.history = saved_history
        if not st.session_state.history:
            boot_packet = new_instance.engage_cold_boot()
            if boot_packet and "ui" in boot_packet:
                clean_boot = clean_engine_output(boot_packet["ui"])
                st.session_state.history.append({
                    "role": "assistant",
                    "content": clean_boot,
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
        setup_user_name = st.text_input("Designation", value="Traveler")
        provider = st.selectbox("Backend", ["Ollama (Local)", "OpenAI (Cloud)", "Mock"])
        api_key = st.text_input("API Key (if Cloud)", type="password")
        model_name = st.text_input("Model ID", value="gpt-4" if provider == "OpenAI (Cloud)" else "llama3")
        if st.form_submit_button("IGNITE"):
            cfg = {"user_name": setup_user_name, "provider": provider.split()[0].lower(), "model": model_name}
            if api_key: cfg["api_key"] = api_key
            if cfg["provider"] == "ollama": cfg["base_url"] = "http://127.0.0.1:11434/v1/chat/completions"
            with open(ConfigWizard.CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=4)
            st.rerun()
    st.stop()

if "ENGINE" not in st.session_state:
    with st.spinner("Hydrating Spore Casing..."):
        st.session_state.ENGINE = init_engine()

if "ENGINE" in st.session_state:
    render_sidebar(st.session_state.ENGINE)

engine = st.session_state.ENGINE

with st.sidebar:
    st.header(f"IDENTITY: {engine.user_name.upper()}")
    st.divider()

    st.subheader("BIO.MONITOR")
    hp = engine.health
    stam = engine.stamina
    atp = 0.0
    if hasattr(engine, 'bio') and engine.bio and hasattr(engine.bio, 'mito'):
         atp = engine.bio.mito.state.atp_pool

    st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
    st.progress(min(1.0, max(0.0, stam / 100.0)), text=f"STAMINA: {stam:.1f}%")

    c1, c2 = st.columns(2)
    c1.metric("ATP", f"{atp:.1f} J")
    c2.metric("ENZYME", "ACTIVE")

    st.divider()

    st.subheader("COORDINATES")
    volts = 0.0
    drag = 0.0
    zone = "VOID"

    if engine.phys and hasattr(engine.phys, 'observer') and engine.phys.observer.last_physics_packet:
        packet = engine.phys.observer.last_physics_packet
        if isinstance(packet, dict):
            volts = packet.get("voltage", 0.0)
            drag = packet.get("narrative_drag", 0.0)
            zone = packet.get("zone", "VOID")
        else:
            volts = getattr(packet, "voltage", 0.0)
            drag = getattr(packet, "narrative_drag", 0.0)
            zone = getattr(packet, "zone", "VOID")

    c3, c4 = st.columns(2)
    c3.metric("VOLTAGE", f"{volts:.1f}v")
    c4.metric("DRAG", f"{drag:.1f}")
    st.info(f"📍 ZONE: {zone}")

    st.divider()

    st.subheader("INVENTORY")
    inv = engine.gordon.inventory
    if inv:
        for item in inv: st.code(item, language=None)
    else: st.caption("Belt Empty.")

    transcript_txt = generate_transcript(st.session_state.history, user_name=engine.user_name)
    st.download_button(
        label="📜 EXPORT LOG",
        data=transcript_txt,
        file_name=f"bone_log_{int(time.time())}.md",
        mime="text/markdown")

    st.divider()

    if st.button("☣️ EMERGENCY DUMP"):
        msg = engine.emergency_save(exit_cause="MANUAL_UI")
        st.toast(msg)
    if st.button("💾 SAVE & HIBERNATE"):
        if 'ENGINE' in st.session_state:
            with st.spinner("Compiling Spore..."):
                st.session_state.ENGINE.save_checkpoint(history=st.session_state.history)
                st.session_state.ENGINE.shutdown()
                st.success("System State Saved. You may close the terminal.")

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
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.spinner("Calculating Geodesics..."):
        packet = engine.process_turn(prompt)

    logs = packet.get("logs", [])
    raw_response = packet.get("ui", "No signal.")

    clean_response = clean_engine_output(raw_response)

    st.session_state.history.append({
        "role": "assistant",
        "content": clean_response,
        "raw_content": raw_response,
        "logs": logs})

    engine.save_checkpoint(history=st.session_state.history)
    st.rerun()