import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["AZURE_AI_ENDPOINT"]
model_name = "gpt-4o-mini"
token = os.environ["AZURE_AI_SECRET"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# 대화 기록을 저장할 리스트 초기화
conversation_history = [
    SystemMessage("You are a helpful assistant.")
]

print("안녕하세요! 챗봇입니다. 질문을 입력하세요. 종료하려면 'bye'를 입력하세요.")

while True:
    user_input = input("\n당신: ")
    
    if user_input.lower() == 'bye':
        print("챗봇: 안녕히가세요!")
        break
    
    # 사용자 메시지를 대화 기록에 추가
    conversation_history.append(UserMessage(user_input))
    
    response = client.complete(
        messages=conversation_history,
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )
    
    assistant_response = response.choices[0].message.content
    print(f"챗봇: {assistant_response}")
    
    # AI 응답을 대화 기록에 추가
    conversation_history.append(AssistantMessage(assistant_response))
