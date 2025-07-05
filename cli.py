# cli.py
import time
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
import chatbot_core as core          # 👉 방금 만든 ‘엔진’ 모듈

# -- 상태 변수 ---------------------------------------------------
history   = [SystemMessage(core.build_system_prompt(0))]
level     = 0
affinity  = 0
THRESHOLD = [5, 10, 15, 20]          # 누적 점수 기준

print("👋 시작! (‘bye’ 입력 시 종료)")
while True:
    user = input("👤: ")
    if user.lower() == "bye":
        print("🤖: 다음에 또 봐요!")
        break

    # 1) 대화 기록
    history.append(UserMessage(user))

    # 2) GPT 호출
    bot = core.chat_one_turn(history)
    print("🤖:", bot)
    history.append(AssistantMessage(bot))

    # 3) 호감도 평가
    score     = core.score_affinity(user, bot)
    affinity += score

    # 4) 레벨 업 확인
    if level < 4 and affinity >= THRESHOLD[level]:
        level += 1
        history[0] = SystemMessage(core.build_system_prompt(level))
        print(f"\n[시스템] 🎉 친밀도 레벨이 {level} 로 상승했습니다! "
              f"(affinity={affinity})\n")
