""" bone_gui.py - The Visual Cortex """

import streamlit as st
import time
from bone_entity import ConversationalEntity

st.set_page_config(
    page_title="BONEAMANITA 13.9.0",
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
</style>
""", unsafe_allow_html=True)
if "entity" not in st.session_state:
    with st.status("Initializing System Kernel...", expanded=True) as status:
        st.write("Waking the Entity...")
        st.session_state.entity = ConversationalEntity(user_name="Architect")
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
    st.title("BoneAmanita v13.9.0")
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("VOLTAGE", f"{st.session_state.meta.get('voltage', 0.0):.1f}v")
    col2.metric("MOOD", st.session_state.meta.get('mood', 'Booting'))
    st.metric("LOCATION", st.session_state.meta.get('location', 'Void'))
    st.divider()
    st.write("BIO.STATUS")
    health_val = st.session_state.meta.get('health', 100.0)
    st.progress(min(1.0, max(0.0, health_val / 100.0)), text=f"INTEGRITY: {health_val:.1f}%")
    st.divider()
    if st.button("EMERGENCY SAVE", type="primary"):
        save_msg = st.session_state.entity.save()
        st.success(save_msg)
st.title("BONEAMANITA 13.8.0")
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
            st.write("Synthesizing response...")
            message_placeholder = st.empty()
            full_response = response_packet.text  # Was: response_packet["text"]
            st.session_state.meta = {
                "mood": response_packet.mood,  # Was: .get("mood", "Neutral")
                "voltage": response_packet.voltage,  # Was: .get("voltage", 0.0)
                "location": response_packet.location,  # Was: .get("location", "Unknown")
                "health": response_packet.health,  # Was: .get("health", 100.0)
                "stamina": response_packet.stamina  # Was: .get("stamina", 100.0)
            }
            status.update(label="Transmission Received", state="complete", expanded=False)
            message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()