# app.py ─ 2025-07-06 4th pass
"""
Streamlit front-end for the intimacy-level chatbot.

주요 변경
    • "last score" + "total score" 두 배지 추가
    • show_status 토글이 level / last / total 세 배지를 한꺼번에 숨김·표시
"""

import time
import streamlit as st
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
import chatbot_core as core            # 💡 shared engine

# -------------------------------------------------
# 🖼️  Page & theme
# -------------------------------------------------
st.set_page_config(page_title="Cozy Chatbot", layout="wide", page_icon="💬")

# 종료 페이지 ------------------------------------------------------
if st.session_state.get("finished"):
    st.markdown("""
    <h1 style='text-align:center;font-size:2.2rem;margin-top:2rem'>🎉 End of Conversation!</h1>
    <p style='text-align:center;font-size:1.1rem'>All conversation is finished.<br>
       Please close this tab and return to your survey.</p>""",
        unsafe_allow_html=True)
    st.stop()

# 헤더 -------------------------------------------------------------
st.markdown("<h1 style='text-align:center;font-size:2.6rem;margin-top:0;'>💬 DEMO CHATBOT</h1>",
            unsafe_allow_html=True)

# -------------------------------------------------
# 🎨  CSS  (버블 + 배지 + 라이트 잠금 + 전송아이콘)
# -------------------------------------------------
st.markdown("""
<style>
.stApp{background:#f8f9fa!important;color:#262730!important}
.message-user{display:flex;justify-content:flex-end;margin:10px 0}
.message-assistant{display:flex;justify-content:flex-start;margin:10px 0}
.bubble-user{
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)!important;
  color:#fff;padding:12px 16px;border-radius:18px 18px 5px 18px;
  max-width:70%;font-size:14px;line-height:1.4;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.bubble-assistant{
  background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%)!important;
  color:#fff;padding:12px 16px;border-radius:18px 18px 18px 5px;
  max-width:70%;font-size:14px;line-height:1.4;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.badge{display:inline-block;padding:4px 12px;border-radius:15px;font-size:12px;
       font-weight:700;margin:4px 0}
.level-badge{background:linear-gradient(45deg,#FFD700,#FFA500);color:#333}
.last-pill{background:#4CAF50;color:#fff}
.total-pill{background:#ff6b6b;color:#fff}
.stChatInput>div>div{background:#fff;border:2px solid #e1e5e9}
.stChatInput button{background:transparent!important;border:none!important}
.stChatInput button svg{fill:#764ba2!important}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# ##### BEGIN_SETTINGS (admin sidebar)
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings (admin)")

    # status toggle ------------------------------------------------
    show_status = st.checkbox("Show status (badge + score)",
                              value=st.session_state.get("show_status", True))
    st.session_state.show_status = show_status

    # prompts ------------------------------------------------------
    if "prompts" not in st.session_state:
        st.session_state.prompts = {i: core.build_system_prompt(i) for i in range(5)}

    st.markdown("### Edit prompts")
    for i in range(5):
        st.session_state.prompts[i] = st.text_area(
            f"Level {i}", st.session_state.prompts[i], key=f"prompt_{i}", height=80
        )

    # thresholds ---------------------------------------------------
    if "thresholds" not in st.session_state:
        st.session_state.thresholds = [5, 10, 15, 20]

    st.markdown("### Score thresholds (cumulative)")
    for i in range(4):
        st.session_state.thresholds[i] = st.number_input(
            f"→ Level {i+1}",
            min_value=1, max_value=100,
            value=st.session_state.thresholds[i],
            step=1, key=f"th_{i}",
        )
    st.caption("※ higher number = hard level up")

    # end button ---------------------------------------------------
    if st.button("End conversation 🚪"):
        st.session_state.finished = True
        st.rerun()
# -------------------------------------------------
# ##### END_SETTINGS
# -------------------------------------------------

# -------------------------------------------------
# 📝  Session-state init
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.level = 0
    st.session_state.affinity = 0          # total score
    st.session_state.last_score = 0        # <<< NEW
    st.session_state.history = [SystemMessage(st.session_state.prompts[0])]
    st.session_state.start_ts = time.time()

# live-edit 시스템 프롬프트 적용
current_prompt = st.session_state.prompts[st.session_state.level]
if current_prompt != st.session_state.history[0].content:
    st.session_state.history[0] = SystemMessage(current_prompt)

# -------------------------------------------------
# 🏷️  Status badges (level / last / total)
# -------------------------------------------------
if st.session_state.show_status:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<span class='badge level-badge'>🏆 level {st.session_state.level}</span>",
                    unsafe_allow_html=True)
    with col2:
        st.markdown(f"<span class='badge last-pill'>💚 last {st.session_state.last_score}</span>",
                    unsafe_allow_html=True)
    with col3:
        st.markdown(f"<span class='badge total-pill'>❤️ total {st.session_state.affinity}</span>",
                    unsafe_allow_html=True)

st.divider()

# -------------------------------------------------
# 💬  Chat history render
# -------------------------------------------------
for msg in st.session_state.history[1:]:
    if isinstance(msg, AssistantMessage):
        st.markdown(
            f"<div class='message-assistant'><div class='bubble-assistant'>{msg.content}</div></div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div class='message-user'><div class='bubble-user'>{msg.content}</div></div>",
            unsafe_allow_html=True)

# -------------------------------------------------
# 🔥  Input & inference
# -------------------------------------------------
user_input = st.chat_input("Ask anything to chatbot...")

if user_input:
    # a) user bubble
    st.markdown(
        f"<div class='message-user'><div class='bubble-user'>{user_input}</div></div>",
        unsafe_allow_html=True)
    st.session_state.history.append(UserMessage(user_input))

    # b) assistant
    bot_reply = core.chat_one_turn(st.session_state.history)
    st.session_state.history.append(AssistantMessage(bot_reply))
    st.markdown(
        f"<div class='message-assistant'><div class='bubble-assistant'>{bot_reply}</div></div>",
        unsafe_allow_html=True)

    # c) scoring
    score = core.score_affinity(user_input)   # ← 1인자
    st.session_state.last_score = score       # <<< NEW
    st.session_state.affinity   += score

    # d) level-up check
    thresholds = st.session_state.thresholds
    if (st.session_state.level < 4 and
        st.session_state.affinity >= thresholds[st.session_state.level]):
        st.session_state.level += 1
        st.session_state.history[0] = SystemMessage(
            st.session_state.prompts[st.session_state.level])
        if st.session_state.show_status:
            st.success(f"🎉 레벨 {st.session_state.level} 로 상승!")
        st.rerun()
