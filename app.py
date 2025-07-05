# app.py  (Streamlit UI)
"""
Streamlit front‑end for the intimacy‑level chatbot.

2025‑07‑06 3rd pass
    • Restored big header, status toggle now affects both badge+score.
    • Sidebar wrapped with ##### BEGIN_SETTINGS / END_SETTINGS ##### so
      you can comment‑out or delete en bloc before production deploy.
    • Added "End conversation" button → shows final page.
"""

import time
import streamlit as st
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
import chatbot_core as core  # 💡 shared engine

# -------------------------------------------------
# 🖼️  Page & theme -------------------------------------------------
# -------------------------------------------------

st.set_page_config(page_title="친밀도 챗봇", layout="wide", page_icon="💬")

# early‑exit page if conversation finished ----------------------------------
if st.session_state.get("finished"):
    st.markdown("""
    <h1 style='text-align:center;font-size:2.2rem;margin-top:2rem'>🎉 대화를 모두 마쳤습니다!</h1>
    <p style='text-align:center;font-size:1.1rem'>All conversation is finished. Please close this tab and return to your survey.</p>
    """, unsafe_allow_html=True)
    st.stop()

# ---- big centered header ---------------------------------------------------

st.markdown(
    """
    <h1 style='text-align:center; font-size:2.6rem; margin-top:0;'>
        💬 연구용 친밀도 챗봇 데모
    </h1>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# 🎨  Custom CSS (bubbles, light theme lock, send‑icon)
# -------------------------------------------------

st.markdown(
    """
    <style>
    .stApp{background:#f8f9fa!important;color:#262730!important}
    /* Chat bubbles */
    .message-user{display:flex;justify-content:flex-end;margin:10px 0}
    .message-assistant{display:flex;justify-content:flex-start;margin:10px 0}
    .bubble-user{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)!important;color:#fff;padding:12px 16px;border-radius:18px 18px 5px 18px;max-width:70%;font-size:14px;line-height:1.4;box-shadow:0 2px 8px rgba(0,0,0,.08)}
    .bubble-assistant{background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%)!important;color:#fff;padding:12px 16px;border-radius:18px 18px 18px 5px;max-width:70%;font-size:14px;line-height:1.4;box-shadow:0 2px 8px rgba(0,0,0,.08)}
    /* Status badges */
    .level-badge{display:inline-block;background:linear-gradient(45deg,#FFD700,#FFA500);color:#333;padding:4px 12px;border-radius:15px;font-size:12px;font-weight:700;margin:4px 0}
    .affinity-pill{display:inline-block;background:#ff6b6b;color:#fff;padding:4px 12px;border-radius:15px;font-size:12px;font-weight:700;margin:4px 0}
    /* Chat‑input tweaks */
    .stChatInput>div>div{background:#fff;border:2px solid #e1e5e9}
    .stChatInput button{background:transparent!important;border:none!important}
    .stChatInput button svg{fill:#764ba2!important}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# ##### BEGIN_SETTINGS (admin sidebar) #####
# -------------------------------------------------

with st.sidebar:
    st.header("⚙️ Settings (admin)")

    # status visibility toggle
    show_status = st.checkbox(
        "Show status (badge + score)",
        value=st.session_state.get("show_status", True),
    )
    st.session_state.show_status = show_status

    # prompts dict
    if "prompts" not in st.session_state:
        st.session_state.prompts = {i: core.build_system_prompt(i) for i in range(5)}

    st.markdown("### Edit prompts")
    for i in range(5):
        st.session_state.prompts[i] = st.text_area(
            f"Level {i}", st.session_state.prompts[i], key=f"prompt_{i}", height=80
        )

    # thresholds list
    if "thresholds" not in st.session_state:
        st.session_state.thresholds = [5, 10, 15, 20]

    st.markdown("### Score thresholds (cumulative)")
    for i in range(4):
        st.session_state.thresholds[i] = st.number_input(
            f"→ Level {i+1}",
            min_value=1,
            max_value=100,
            value=st.session_state.thresholds[i],
            step=1,
            key=f"th_{i}",
        )

    st.caption("※ 큰 숫자일수록 레벨‑업이 어려워집니다 (누적 점수)")

    # END button
    if st.button("End conversation 🚪"):
        st.session_state.finished = True
        st.rerun()

# -------------------------------------------------
# ##### END_SETTINGS #####
# -------------------------------------------------

# -------------------------------------------------
# 📝  Session‑state initialisation
# -------------------------------------------------

if "history" not in st.session_state:
    st.session_state.level = 0
    st.session_state.affinity = 0
    st.session_state.history = [SystemMessage(st.session_state.prompts[0])]
    st.session_state.start_ts = time.time()

# live‑edit current prompt
current_prompt = st.session_state.prompts[st.session_state.level]
if current_prompt != st.session_state.history[0].content:
    st.session_state.history[0] = SystemMessage(current_prompt)

# -------------------------------------------------
# 🏷️  Status (badge + affinity)
# -------------------------------------------------

if st.session_state.show_status:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<span class='level-badge'>🏆 level {st.session_state.level}</span>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<span class='affinity-pill'>❤️ score {st.session_state.affinity}</span>",
            unsafe_allow_html=True,
        )

st.divider()

# -------------------------------------------------
# 💬  Chat history render
# -------------------------------------------------

for msg in st.session_state.history[1:]:
    if isinstance(msg, AssistantMessage):
        st.markdown(
            f"<div class='message-assistant'><div class='bubble-assistant'>{msg.content}</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='message-user'><div class='bubble-user'>{msg.content}</div></div>",
            unsafe_allow_html=True,
        )

# -------------------------------------------------
# 🔥  Input & inference
# -------------------------------------------------

user_input = st.chat_input("메시지를 입력하세요 (‘bye’ 입력 시 종료)")

if user_input:
    if user_input.lower() == "bye":
        st.stop()

    # a) user bubble immediately
    st.markdown(
        f"<div class='message-user'><div class='bubble-user'>{user_input}</div></div>",
        unsafe_allow_html=True,
    )
    st.session_state.history.append(UserMessage(user_input))

    # b) model call
    bot_reply = core.chat_one_turn(st.session_state.history)
    st.session_state.history.append(AssistantMessage(bot_reply))
    st.markdown(
        f"<div class='message-assistant'><div class='bubble-assistant'>{bot_reply}</div></div>",
        unsafe_allow_html=True,
    )

    # c) affinity & level logic
    score = core.score_affinity(user_input, bot_reply)
    st.session_state.affinity += score

    thresholds = st.session_state.thresholds  # live‑edited via sidebar
    if (
        st.session_state.level < 4
        and st.session_state.affinity >= thresholds[st.session_state.level]
    ):
        st.session_state.level += 1
        st.session_state.history[0] = SystemMessage(
            st.session_state.prompts[st.session_state.level]
        )
        if st.session_state.show_status:
            st.success(f"🎉 레벨 {st.session_state.level} 로 상승!")
        st.rerun()  # refresh to reflect new status
