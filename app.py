# app.py
import streamlit as st, time
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from chatbot_core import build_system_prompt, chat_one_turn, score_affinity

st.set_page_config(page_title="연구용 친밀도 챗봇", layout="centered")
st.title("💬 연구용 친밀도 챗봇 데모")

# --- 세션 상태 초기화 ------------------------------------------
if "history" not in st.session_state:
    st.session_state.history   = [SystemMessage(build_system_prompt(0))]
    st.session_state.level     = 0
    st.session_state.affinity  = 0
    st.session_state.start_ts  = time.time()

# --- 이전 대화 보여주기 ---------------------------------------
for msg in st.session_state.history[1:]:         # 0번은 시스템
    role = "assistant" if isinstance(msg, AssistantMessage) else "user"
    st.chat_message(role).write(msg.content)

# --- 입력 받기 -------------------------------------------------
user_input = st.chat_input("메시지를 입력하세요 (‘bye’ → 종료)")

if user_input:
    if user_input.lower() == "bye":
        st.stop()

    # 1) 기록
    st.session_state.history.append(UserMessage(user_input))

    # 2) 모델 호출
    bot_reply = chat_one_turn(st.session_state.history)
    st.session_state.history.append(AssistantMessage(bot_reply))
    st.chat_message("assistant").write(bot_reply)

    # 3) 호감도 스코어링
    score = score_affinity(user_input, bot_reply)
    st.session_state.affinity += score

    # 4) 레벨 체크 & 프롬프트 갱신
    thresholds = [5, 10, 15, 20]
    if (st.session_state.level < 4 and
        st.session_state.affinity >= thresholds[st.session_state.level]):
        st.session_state.level += 1
        st.session_state.history[0] = SystemMessage(
            build_system_prompt(st.session_state.level)
        )
        st.success(f"🎉 친밀도 레벨이 {st.session_state.level} 로 상승했어요!")
