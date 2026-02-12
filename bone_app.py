""" bone_app.py - The Glass Terminal Interface (Refactored) """

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
    initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stChatMessage .stMarkdown p { margin-bottom: 1.5em !important; line-height: 1.8 !important; font-size: 1.05rem; }
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    .stTextInput > div > div > input { background-color: #111; color: #00ff41; border: 1px solid #333; font-family: 'Courier New', monospace; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; color: #00ff41 !important; }
    .stChatMessage { background-color: #0e1117; border: 1px solid #222; border-radius: 5px; margin-bottom: 15px; }
    .stButton > button { border: 1px solid #00ff41; color: #00ff41; background-color: transparent; font-family: 'Courier New', monospace; }
    .stButton > button:hover { background-color: #00ff41; color: #000; }
</style>
""", unsafe_allow_html=True)

def clean_engine_output(raw_text):
    if not raw_text: return "No signal."
    clean = Prisma.strip(raw_text)
    lines = clean.split('\n')
    filtered = []
    for line in lines:
        norm = line.strip()
        is_artifact = False
        if set(norm).issubset({'─', '-', ' '}) and len(norm) > 4:
            is_artifact = True
        if "♦" in norm and "HP" in norm and "STM" in norm:
            is_artifact = True
        if "⚡" in norm and "v" in norm and "⚓" in norm:
            is_artifact = True
        if "📍" in norm and "//" in norm:
            is_artifact = True
        if "SOUL:" in norm and ("█" in norm or "%" in norm):
            is_artifact = True
        if "DRIVER:" in norm and "MUSE:" in norm:
            is_artifact = True
        if not is_artifact:
            filtered.append(line)
    return "\n".join(filtered).strip()

def perform_autosave(engine_ref, history_ref):
    try:
        if not os.path.exists("saves"):
            os.makedirs("saves")
        result = engine_ref.save_checkpoint(history=history_ref)
        if "❌" in result:
            st.error(result)
    except Exception as e:
        st.error(f"Autosave Crashed: {e}")

def format_log_entry(log_str):
    clean = Prisma.strip(log_str)
    if "██" in clean or "♦ THE ARCHITECT" in clean: return None
    if "[BIO]" in clean: return f"🧬 {clean}"
    if "[PHYSICS]" in clean or "VOLTAGE" in clean: return f"⚡ {clean}"
    if "[COUNCIL]" in clean: return f"⚖️ {clean}"
    if "[REM]" in clean: return f"💤 {clean}"
    if "ERROR" in clean or "CRITICAL" in clean: return f"❌ {clean}"
    if "ITEM:" in clean or "GAINED" in clean: return f"🎒 {clean}"
    return f"🔹 {clean}"

def generate_transcript(history, user_name="TRAVELER"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"# BONEAMANITA TRANSCRIPT - {timestamp}", f"Identity: {user_name}", "---"]
    for entry in history:
        raw_role = entry["role"].upper()
        display_name = user_name.upper() if raw_role == "USER" else "THE SYSTEM"
        icon = "👤" if raw_role == "USER" else "💀"
        clean_content = Prisma.strip(entry.get("raw_content", entry["content"]))
        lines.append(f"\n### {icon} {display_name}")
        lines.append(clean_content)
        if "logs" in entry and entry["logs"]:
            lines.append("\n> **SYSTEM INTERNALS:**")
            for internal_log in entry["logs"]:
                clean_log = Prisma.strip(str(internal_log))
                lines.append(f"> * {clean_log}")
    lines.append("\n---\n*End of Transmission*")
    return "\n".join(lines)


def render_dashboard(eng_ref):
    with st.sidebar:
        st.title("💀 BONEAMANITA")
        st.caption(f"Kernel: {getattr(eng_ref, 'kernel_hash', 'UNKNOWN')}")
        st.divider()

        st.subheader("IDENTITY")
        if hasattr(eng_ref, 'soul') and eng_ref.soul:
            anchor = eng_ref.soul.anchor
            dig = anchor.dignity_reserve
            st.progress(min(100, max(0, int(dig))), text=f"DIGNITY: {int(dig)}%")
            if anchor.agency_lock:
                st.error("🔒 AGENCY LOCKED")
            st.markdown(f"**ARCHETYPE: {eng_ref.soul.archetype}**")
            st.caption(f"Tenure: {eng_ref.soul.archetype_tenure} cycles")
            if eng_ref.soul.current_obsession:
                 st.caption(f"Obsession: {eng_ref.soul.current_obsession}")

        st.divider()
        st.subheader("VITALS")
        hp = eng_ref.health
        stam = eng_ref.stamina
        atp = 0.0
        if hasattr(eng_ref, 'bio') and eng_ref.bio and hasattr(eng_ref.bio, 'mito'):
             atp = eng_ref.bio.mito.state.atp_pool
        st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
        st.progress(min(1.0, max(0.0, stam / 100.0)), text=f"STAMINA: {stam:.1f}%")
        c1, c2 = st.columns(2)
        c1.metric("ATP", f"{atp:.1f} J")

        if hasattr(eng_ref, 'bio') and eng_ref.bio and eng_ref.bio.endo:
            chem = eng_ref.bio.endo.get_state()
            cor = chem.get("COR", 0.0)
            c2.metric("CORTISOL", f"{cor:.2f}", delta="-Stress" if cor < 0.3 else "+Stress", delta_color="inverse")

        st.divider()
        st.subheader("PHYSICS")
        volts = 0.0
        drag = 0.0
        zone = "VOID"

        if eng_ref.phys and hasattr(eng_ref.phys, 'observer') and eng_ref.phys.observer.last_physics_packet:
            packet = eng_ref.phys.observer.last_physics_packet
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
        inv = eng_ref.gordon.inventory
        if inv:
            for item in inv: st.code(item, language=None)
        else:
            st.caption("Belt Empty.")

        st.divider()
        transcript_txt = generate_transcript(st.session_state.history, user_name=eng_ref.user_name)
        st.download_button(
            label="📜 EXPORT LOG",
            data=transcript_txt,
            file_name=f"bone_log_{int(time.time())}.md",
            mime="text/markdown")
        if st.button("☣️ EMERGENCY DUMP"):
            msg = eng_ref.emergency_save(exit_cause="MANUAL_UI")
            st.toast(msg)
        if st.button("💾 SAVE & HIBERNATE"):
            with st.spinner("Compiling Spore..."):
                eng_ref.save_checkpoint(history=st.session_state.history)
                eng_ref.shutdown()
                st.success("System State Saved. You may close the terminal.")


if "history" not in st.session_state:
    st.session_state.history = []

@st.cache_data
def load_config_cached():
    return ConfigWizard.load_or_create()

def init_engine():
    try:
        config = load_config_cached()
        if not config: return None
        new_instance = BoneAmanita(config)

        print(f"[BOOT] Checking for saves in {os.path.abspath('saves')}...")
        restored, saved_history = new_instance.resume_checkpoint()
        if restored and saved_history:
            st.session_state.history = saved_history
            st.toast("System State Restored.")

        if not st.session_state.history:
            print("[BOOT] Cold Boot.")
            boot_packet = new_instance.engage_cold_boot()
            if boot_packet and "ui" in boot_packet:
                st.session_state.history.append({
                    "role": "assistant",
                    "content": clean_engine_output(boot_packet["ui"]),
                    "logs": boot_packet.get("logs", [])})
            else:
                st.session_state.history.append({
                    "role": "system",
                    "content": "SYSTEM_BOOT: SEQUENCE COMPLETE.",
                    "logs": ["Kernel Loaded."]})
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
if st.session_state.ENGINE is None:
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
        packet = engine.process_turn(prompt)
    logs = packet.get("logs", [])
    raw_response = packet.get("ui", "No signal.")
    clean_response = clean_engine_output(raw_response)
    st.session_state.history.append({
        "role": "assistant",
        "content": clean_response,
        "raw_content": raw_response,
        "logs": logs})
    perform_autosave(engine, st.session_state.history)
    st.rerun()