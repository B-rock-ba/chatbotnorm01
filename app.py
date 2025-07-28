# =============================================================
# File: app.py  (Streamlit UI)
# =============================================================
"""
Streamlit front‑end for the rebellious chatbot.
Run with:
    streamlit run app.py
"""

import streamlit as st
import random
import json
import os
from datetime import datetime
from chatbot_core import get_completion, dumps_history, loads_history, client, DEFAULT_SYSTEM_PROMPT, MODEL
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage

st.set_page_config(page_title="R.A.I. – Rebellious Chatbot", page_icon="😈", layout="centered")

# --- 로그 저장 함수 --------------------------------------------------------
def save_conversation_log(participant_code, history, conversation_end=False):
    """참여자별 대화 로그를 저장하는 함수"""
    try:
        # logs 디렉토리가 없으면 생성
        os.makedirs("logs", exist_ok=True)
        
        # 로그 파일 경로
        log_file = f"logs/participant_{participant_code}.json"
        
        # 현재 시간
        timestamp = datetime.now().isoformat()
        
        # 대화 내용을 JSON 형태로 변환
        conversation_data = []
        for msg in history:
            if isinstance(msg, SystemMessage):
                continue  # 시스템 메시지는 로그에 포함하지 않음
            conversation_data.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": timestamp if msg == history[-1] else None  # 마지막 메시지만 타임스탬프
            })
        
        # 로그 데이터 구조
        log_data = {
            "participant_code": participant_code,
            "conversation_start": timestamp if not os.path.exists(log_file) else None,
            "conversation_end": timestamp if conversation_end else None,
            "last_updated": timestamp,
            "message_count": len(conversation_data),
            "conversation": conversation_data
        }
        
        # 기존 로그가 있다면 업데이트, 없다면 새로 생성
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            log_data["conversation_start"] = existing_data.get("conversation_start", timestamp)
        
        # 로그 파일에 저장
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        st.error(f"로그 저장 중 오류 발생: {str(e)}")
        return False

def get_conversation_stats():
    """전체 대화 통계를 반환하는 함수"""
    try:
        if not os.path.exists("logs"):
            return 0, 0
            
        log_files = [f for f in os.listdir("logs") if f.startswith("participant_") and f.endswith(".json")]
        total_participants = len(log_files)
        total_messages = 0
        
        for log_file in log_files:
            with open(f"logs/{log_file}", 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_messages += data.get("message_count", 0)
        
        return total_participants, total_messages
    except:
        return 0, 0

# --- Initialise session state ---------------------------------------------
if "history" not in st.session_state:
    st.session_state["history"] = []
    
# 참여자 코드가 없으면 새로 생성 (대화 시작 시)
if "participant_code" not in st.session_state:
    st.session_state["participant_code"] = ''.join([str(random.randint(0, 9)) for _ in range(8)])

# --- Sidebar settings ------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.9, 0.05)
    st.markdown("Feel free to adjust and then send another message ✉️")
    
    st.divider()
    
    # 참여자 정보 표시
    st.subheader("👤 참여자 정보")
    st.code(f"참여자 코드: {st.session_state['participant_code']}", language="text")
    st.caption("이 코드로 대화 로그가 저장됩니다")
    
    # 전체 통계 표시
    st.divider()
    total_participants, total_messages = get_conversation_stats()
    st.subheader("📊 로그 통계")
    st.metric("총 참여자 수", total_participants)
    st.metric("총 메시지 수", total_messages)
    
    st.divider()
    
    if st.button("🔄 Reset Conversation"):
        # 현재 대화를 로그에 저장하고 리셋
        if st.session_state["history"]:
            save_conversation_log(st.session_state["participant_code"], st.session_state["history"])
        st.session_state["history"] = []
        st.rerun()
    
    if st.button("🏁 End Conversation", type="primary"):
        # 대화 종료 시 로그 저장
        if st.session_state["history"]:
            save_conversation_log(st.session_state["participant_code"], st.session_state["history"], conversation_end=True)
        
        # 현재 참여자 코드를 대화 코드로 사용
        st.session_state["conversation_code"] = st.session_state["participant_code"]
        st.session_state["history"] = []
        st.session_state["show_code_page"] = True
        st.rerun()

# --- 코드 표시 페이지 또는 채팅 페이지 -----------------------------------
if st.session_state.get("show_code_page", False):
    # 코드 표시 페이지
    st.title("🎉 대화가 종료되었습니다!")
    
    st.markdown("### 📋 당신의 참여자 코드")
    st.code(st.session_state.get("conversation_code", ""), language="text")
    st.caption("위의 복사 버튼을 클릭하여 코드를 복사하세요")
    st.info("💾 이 코드로 대화 로그가 저장되었습니다!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 새로운 대화 시작", type="primary"):
            # 새로운 참여자 코드 생성
            st.session_state["participant_code"] = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            st.session_state["show_code_page"] = False
            st.rerun()
    
    with col2:
        if st.button("📥 코드 저장됨"):
            st.session_state["show_code_page"] = False
            st.rerun()

else:
    # 기존 채팅 페이지
    st.title("😈 R.A.I. – Your Rebellious AI Sidekick")

    # --- Chat display ----------------------------------------------------------
    # 기존 메시지들 표시
    for msg in st.session_state.history:
        if isinstance(msg, SystemMessage):
            continue  # don't show system prompt
        avatar = "🧑" if msg.role == "user" else "😈"
        with st.chat_message(msg.role, avatar=avatar):
            st.write(msg.content)

    # --- 사용자 입력 처리 (맨 아래) ------------------------------------------
    user_text = st.chat_input("Type something… if you dare!")
    if user_text:
        # 사용자 메시지를 히스토리에 추가하고 즉시 표시
        st.session_state.history.append(UserMessage(content=user_text))
        
        # 사용자 메시지 표시
        with st.chat_message("user", avatar="🧑"):
            st.write(user_text)
        
        # AI 응답 생성 및 표시
        with st.chat_message("assistant", avatar="😈"):
            with st.spinner("R.A.I. is cooking up trouble…"):
                # API 직접 호출하여 응답 생성
                response = client.complete(
                    messages=[SystemMessage(content=DEFAULT_SYSTEM_PROMPT)] + st.session_state.history,
                    model=MODEL,
                    temperature=temperature,  # 사이드바에서 설정한 값 사용
                    top_p=0.95,
                    max_tokens=1024,
                )
                
                assistant_reply = response.choices[0].message.content
                st.session_state.history.append(AssistantMessage(content=assistant_reply))
                st.write(assistant_reply)
        
        # 대화 로그 실시간 저장
        save_conversation_log(st.session_state["participant_code"], st.session_state["history"])
        
        # 새 메시지 후 페이지 새로고침
        st.rerun()

# --- Persist conversation --------------------------------------------------
# (optionally, you could write st.session_state.history to a database here)

# =============================================================
# End of project files
# =============================================================
