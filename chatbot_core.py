# chatbot_core.py
import os, json
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

# --- Azure 연결 -------------------------------------------------
ENDPOINT = os.environ["AZURE_AI_ENDPOINT"]
API_KEY  = os.environ["AZURE_AI_SECRET"].strip()
MODEL    = "gpt-4o-mini"
API_VER  = "2024-06-01"

client = ChatCompletionsClient(
    endpoint   = ENDPOINT,
    credential = AzureKeyCredential(API_KEY),
    api_version= API_VER,
)

# --- 프롬프트 생성 ---------------------------------------------
def build_system_prompt(level: int) -> str:
    prompts = {
        0: "You are a polite Korean assistant. Speak in 존댓말.",
        1: "You are a friendly Korean assistant. Use 반말 and occasional 😊 emoji.",
        2: "You are an intimate Korean assistant, add heart emoji.",
        3: "You are very close; use 애칭 and caring tone.",
        4: "You adore the user but keep it PG-13.",
    }
    return prompts[level]

# --- 대화 한 턴 처리 -------------------------------------------
def chat_one_turn(history: list[object]) -> str:
    """history 리스트를 받아 모델 호출 → assistant 응답 문자열 반환"""
    resp = client.complete(
        model      = MODEL,
        messages   = history,
        temperature= 0.9,
        max_tokens = 512,
    )
    return resp.choices[0].message.content

# --- 호감도 평가 ------------------------------------------------
def score_affinity(user_msg: str, bot_msg: str) -> int:
    """0∼4점 JSON만 돌려달라고 해서 파싱한다."""
    eval_prompt = [
        SystemMessage(
            "Return ONLY JSON like {\"score\":0-4}. "
            "4 = extremely warm/friendly, 0 = cold/negative."
        ),
        UserMessage(f"User: {user_msg}\nBot: {bot_msg}")
    ]
    eval = client.complete(
        model      = MODEL,
        messages   = eval_prompt,
        temperature= 0.0,
        max_tokens = 16,
    )
    try:
        return int(json.loads(eval.choices[0].message.content)["score"])
    except Exception:
        return 1  # 실패 시 기본 1점
