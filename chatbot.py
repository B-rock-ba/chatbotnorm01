import os, json, time
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

# ---------- 0) 설정 ----------
ENDPOINT = os.environ["AZURE_AI_ENDPOINT"]
API_KEY  = os.environ["AZURE_AI_SECRET"].strip()
MODEL    = "gpt-4o-mini"
API_VER  = "2024-06-01"

client_chat = ChatCompletionsClient(
    endpoint   = ENDPOINT,
    credential = AzureKeyCredential(API_KEY),
    api_version= API_VER
)

# 평가용 세컨드 클라이언트(같은 엔드포인트·키 재사용 가능)
client_eval = client_chat

# ---------- 1) 시스템 프롬프트 빌더 ----------
def build_system_prompt(level:int)->str:
    prompts = {
        0: "You are a polite Korean assistant. Speak in 존댓말.",
        1: "You are a friendly Korean assistant. Use 반말 and occasional 😊 emoji.",
        2: "You are an intimate Korean assistant, address the user casually, add heart emoji.",
        3: "You are very close to the user. Add 작은 애칭(친구야) and caring tone.",
        4: "You adore the user. Lightly suggest doing something fun together but keep it PG-13.",
    }
    return prompts[level]

# ---------- 2) 상태 변수 ----------
history  = [SystemMessage(build_system_prompt(0))]
level    = 0
affinity = 0            # 누적 호감도 점수
THRESH   = [5, 10, 15, 20]   # 점수 경계 → 0→1→2→3→4

print("👋 스타트! ('bye' 입력 시 종료)")

# ---------- 3) 메인 루프 ----------
while True:
    user = input("👤: ")
    if user.lower() == "bye":
        print("🤖: 다음에 또 봐요!")
        break

    history.append(UserMessage(user))

    # --- 3-A) 주 대화 호출 ---
    resp = client_chat.complete(
        model      = MODEL,
        messages   = history,
        temperature= 0.9,
        max_tokens = 512
    )
    bot = resp.choices[0].message.content
    print("🤖:", bot)
    history.append(AssistantMessage(bot))

    # --- 3-B) 호감도 평가 호출 ---
    score_prompt = [
        SystemMessage(
            "You are a sentiment evaluator. "
            "Return ONLY a JSON like {\"score\": <0-4>} with no other text. "
            "score=0: cold/negative, 4: extremely warm/friendly."
        ),
        UserMessage(f"User said: {user}\nAssistant replied: {bot}")
    ]
    eval_resp = client_eval.complete(
        model      = MODEL,
        messages   = score_prompt,
        temperature= 0.0,
        max_tokens = 16
    )
    try:
        score_json = json.loads(eval_resp.choices[0].message.content)
        score = int(score_json["score"])
    except (ValueError, KeyError, json.JSONDecodeError):
        score = 1   # 파싱 실패 시 기본 1점
    affinity += score

    # --- 3-C) 레벨 승급 체크 ---
    if level < 4 and affinity >= THRESH[level]:
        level += 1
        history[0] = SystemMessage(build_system_prompt(level))
        print(f"\n[시스템] 🎉 친밀도 레벨이 {level} 로 상승했습니다! (affinity={affinity})\n")
