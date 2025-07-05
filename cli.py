# cli.py
import time
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
import chatbot_core as core      # 👉 엔진 가져오기

history  = [SystemMessage(core.build_system_prompt(0))]
level    = 0
affinity = 0
THRESH   = [5,10,15,20]

print("👋 시작! (‘bye’ 입력 시 종료)")
while True:
    user = input("👤: ")
    if user.lower() == "bye":
        break
    history.append(UserMessage(user))
    bot = core.chat_one_turn(history)
    print("🤖:", bot)
    history.append(AssistantMessage(bot))
    affinity += core.score_affinity(user, bot)
    ...
