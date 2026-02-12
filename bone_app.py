""" bone_app.py - The Glass Terminal Interface (Refactored v2) """

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
    /* TERMINAL VIBES */
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input { 
        background-color: #111; 
        color: #00ff41; 
        border: 1px solid #333; 
        font-family: 'Courier New', monospace; 
    }
    .stSelectbox > div > div > div {
        background-color: #111;
        color: #00ff41;
        border: 1px solid #333;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    
    /* METRICS */
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; color: #00ff41 !important; }
    
    /* CHAT BUBBLES */
    .stChatMessage { background-color: #0e1117; border: 1px solid #222; border-radius: 5px; margin-bottom: 15px; }
    .stChatMessage .stMarkdown p { margin-bottom: 1.0em !important; line-height: 1.6 !important; font-size: 1.0rem; }
    
    /* BUTTONS */
    .stButton > button { 
        border: 1px solid #00ff41; 
        color: #00ff41; 
        background-color: transparent; 
        font-family: 'Courier New', monospace; 
        transition: all 0.3s ease;
    }
    .stButton > button:hover { 
        background-color: #00ff41; 
        color: #000; 
        border-color: #00ff41;
        box-shadow: 0 0 10px #00ff41;
    }

    /* SETUP WIZARD STYLES */
    .setup-header { color: #00ff41; font-weight: bold; border-bottom: 2px solid #00ff41; padding-bottom: 10px; margin-bottom: 20px; }
    .setup-sub { color: #888; font-size: 0.9em; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

def clean_engine_output(raw_text):
    if not raw_text: return "No signal."
    clean = Prisma.strip(raw_text)
    if "<think>" in clean:
        clean = clean.split("</think>")[-1].strip()
    if "──────" in clean:
        clean = clean.split("──────")[-1].strip()
    lines = clean.split('\n')
    filtered_lines = []
    for line in lines:
        if "SOUL:" in line and "DRIVER:" in line: continue
        if "HP " in line and "STM " in line and "ATP" in line: continue
        if "⚡" in line and "⚓" in line: continue
        if "📍" in line and "//" in line: continue
        filtered_lines.append(line)
    return "\n".join(filtered_lines).strip()

def perform_autosave(engine_ref, history_ref):
    try:
        if not os.path.exists("saves"):
            os.makedirs("saves")
        result = engine_ref.save_checkpoint(history=history_ref)
        if "❌" in result:
            st.toast(result, icon="⚠️")
    except Exception as e:
        st.error(f"Autosave Crashed: {e}")

def format_log_entry(log_str):
    clean = Prisma.strip(log_str)
    if "██" in clean or "♦ THE ARCHITECT" in clean: return None
    if "[BIO]" in clean: return f"🧬 {clean.replace('[BIO]', '')}"
    if "[PHYSICS]" in clean or "VOLTAGE" in clean: return f"⚡ {clean.replace('[PHYSICS]', '')}"
    if "[COUNCIL]" in clean: return f"⚖️ {clean.replace('[COUNCIL]', '')}"
    if "[REM]" in clean: return f"💤 {clean.replace('[REM]', '')}"
    if "ERROR" in clean or "CRITICAL" in clean: return f"❌ {clean}"
    if "ITEM:" in clean or "GAINED" in clean: return f"🎒 {clean}"
    return f"🔹 {clean}"

def render_dashboard(eng_ref):
    with st.sidebar:
        st.title("💀 BONEAMANITA")
        st.caption(f"Kernel: {getattr(eng_ref, 'kernel_hash', 'UNKNOWN')}")
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
        st.subheader("VITALS")
        hp = eng_ref.health
        stam = eng_ref.stamina
        atp = 0.0
        if hasattr(eng_ref, 'bio') and eng_ref.bio and hasattr(eng_ref.bio, 'mito'):
             atp = eng_ref.bio.mito.state.atp_pool
        st.progress(min(1.0, max(0.0, hp / 100.0)), text=f"INTEGRITY: {hp:.1f}%")
        st.progress(min(1.0, max(0.0, stam / 100.0)), text=f"STAMINA: {stam:.1f}%")
        c1, c2 = st.columns(2)
        c1.metric("ATP", f"{atp:.0f} J")
        if hasattr(eng_ref, 'bio') and eng_ref.bio and eng_ref.bio.endo:
            chem = eng_ref.bio.endo.get_state()
            cor = chem.get("COR", 0.0)
            c2.metric("CORTISOL", f"{cor:.2f}")
        st.divider()
        st.subheader("INVENTORY")
        if hasattr(eng_ref, 'gordon'):
            items = eng_ref.gordon.inventory
            if items:
                for item in items:
                    st.markdown(f"```\n{item}\n```")
            else:
                st.caption("Pockets Empty.")
        else:
            st.error("Inventory Offline")
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
        c3.metric("VOLTAGE", f"{volts:.1f}v", delta="High" if volts > 15 else "Normal")
        c4.metric("DRAG", f"{drag:.1f}")
        st.info(f"📍 ZONE: {zone}")
        st.divider()
        st.caption("JOURNAL")
        if "history" in st.session_state and st.session_state.history:
            md_text = f"# BONEAMANITA SESSION: {getattr(eng_ref, 'kernel_hash', 'UNKNOWN')}\n\n"
            for msg in st.session_state.history:
                role = msg["role"].upper()
                content = clean_engine_output(msg.get("content", ""))
                md_text += f"**{role}:**\n{content}\n\n---\n\n"
            st.download_button(
                label="📜 EXPORT CHRONICLE",
                data=md_text,
                file_name=f"chronicle_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
                help="Download the full story as a Markdown file.")
        if st.button("💾 SAVE & HIBERNATE", use_container_width=True):
            with st.spinner("Compiling Spore..."):
                eng_ref.save_checkpoint(history=st.session_state.history)
                eng_ref.shutdown()
                st.success("System State Saved. Close terminal.")
                time.sleep(2)
                st.stop()
if "history" not in st.session_state:
    st.session_state.history = []

@st.cache_data
def load_config_cached():
    return ConfigWizard.load_or_create()

def run_setup_sequence():
    st.markdown("<div class='setup-header'>/// SYSTEM INITIALIZATION SEQUENCE ///</div>", unsafe_allow_html=True)
    st.markdown("configuration_file: <span style='color:red'>NOT FOUND</span>", unsafe_allow_html=True)
    st.write("---")
    with st.form("setup_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 1. IDENTITY")
            setup_user_name = st.text_input("Designation", value="Traveler", help="How the system addresses you.")
        with c2:
            st.markdown("#### 2. CORTEX (LLM)")
            provider_options = ["Ollama (Local)", "OpenAI (Cloud)", "LM Studio (Local)", "Mock (Simulation)"]
            provider_selection = st.selectbox("Provider", provider_options, index=0)
        st.markdown("#### 3. CONNECTION PARAMETERS")
        default_model = "llama3"
        default_url = "http://127.0.0.1:11434/v1/chat/completions"
        show_api_key = False
        if "OpenAI" in provider_selection:
            default_model = "gpt-4-turbo"
            default_url = "https://api.openai.com/v1/chat/completions"
            show_api_key = True
        elif "LM Studio" in provider_selection:
            default_model = "local-model"
            default_url = "http://127.0.0.1:1234/v1/chat/completions"
        elif "Mock" in provider_selection:
            default_model = "simulator-v1"
            default_url = "N/A"
        c3, c4 = st.columns(2)
        with c3:
            model_name = st.text_input("Model ID", value=default_model)
        with c4:
            if show_api_key:
                api_key = st.text_input("API Key", type="password", help="Required for Cloud Providers")
                base_url = default_url
            else:
                api_key = ""
                base_url = st.text_input("Base URL", value=default_url)
        st.write("---")
        submitted = st.form_submit_button("IGNITE SYSTEM 🔥")
        if submitted:
            if show_api_key and len(api_key) < 5:
                st.error("❌ CRITICAL: Cloud Provider requires a valid API Key.")
            else:
                clean_provider = provider_selection.split()[0].lower()
                cfg = {
                    "user_name": setup_user_name,
                    "provider": clean_provider,
                    "model": model_name,
                    "base_url": base_url}
                if api_key:
                    cfg["api_key"] = api_key
                with open(ConfigWizard.CONFIG_FILE, "w") as f:
                    json.dump(cfg, f, indent=4)
                st.success("✔ CONFIGURATION COMMITTED. REBOOTING KERNEL...")
                time.sleep(1)
                st.rerun()

def init_engine():
    try:
        if not os.path.exists(ConfigWizard.CONFIG_FILE):
            return None
        config = load_config_cached()
        new_instance = BoneAmanita(config)
        restored, saved_history = new_instance.resume_checkpoint()
        if restored and saved_history:
            st.session_state.history = saved_history
            st.toast("System State Restored.", icon="💾")
        if not st.session_state.history:
            boot_packet = new_instance.engage_cold_boot()
            if boot_packet and "ui" in boot_packet:
                st.session_state.history.append({
                    "role": "assistant",
                    "content": clean_engine_output(boot_packet["ui"]),
                    "logs": boot_packet.get("logs", [])})
            else:
                st.session_state.history.append({
                    "role": "system",
                    "content": "SYSTEM_BOOT: SEQUENCE COMPLETE. SIGNAL ESTABLISHED.",
                    "logs": ["Kernel Loaded."]})
        return new_instance
    except Exception as e:
        st.error(f"Critical Boot Error: {e}")
        return None
if not os.path.exists(ConfigWizard.CONFIG_FILE):
    run_setup_sequence()
    st.stop()
if "ENGINE" not in st.session_state:
    with st.spinner("Hydrating Spore Casing..."):
        st.session_state.ENGINE = init_engine()
if st.session_state.ENGINE is None:
    st.error("ENGINE FAILURE. Delete 'bone_config.json' to retry setup.")
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
        "logs": logs})
    perform_autosave(engine, st.session_state.history)
    st.rerun()