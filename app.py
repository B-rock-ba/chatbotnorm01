# =============================================================
# File: app.py  (Streamlit UI)
# =============================================================
"""
Streamlit front‑end for the rebellious chatbot.
Run with:
    streamlit run app.py
"""

import streamlit as st
from chatbot_core import get_completion, dumps_history, loads_history

st.set_page_config(page_title="R.A.I. – Rebellious Chatbot", page_icon="😈", layout="centered")

# --- Sidebar settings ------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.9, 0.05)
    st.markdown("Feel free to adjust and then send another message ✉️")
    if st.button("🔄 Reset Conversation"):
        st.session_state["history"] = []
        st.experimental_rerun()

# --- Initialise session state ---------------------------------------------
if "history" not in st.session_state:
    st.session_state["history"] = []

st.title("😈 R.A.I. – Your Rebellious AI Sidekick")

# --- Chat display ----------------------------------------------------------
chat_container = st.container()
with chat_container:
    # Render existing messages
    for msg in st.session_state.history:
        if isinstance(msg, SystemMessage):
            continue  # don’t show system prompt
        avatar = "🧑" if msg.role == "user" else "😈"
        st.chat_message(msg.role, avatar=avatar).write(msg.content)

    # Input box at bottom
    user_text = st.chat_input("Type something… if you dare!")
    if user_text:
        with st.chat_message("user", avatar="🧑"):
            st.write(user_text)
        with st.spinner("R.A.I. is cooking up trouble…"):
            reply = get_completion(user_text, st.session_state.history)
        with st.chat_message("assistant", avatar="😈"):
            st.write(reply)

# --- Persist conversation --------------------------------------------------
# (optionally, you could write st.session_state.history to a database here)

# =============================================================
# End of project files
# =============================================================
