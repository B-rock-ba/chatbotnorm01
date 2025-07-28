#!/usr/bin/env python3
# =============================================================
# File: log_analyzer.py
# 로그 데이터 분석 스크립트
# =============================================================
"""
참여자별 대화 로그를 분석하는 스크립트

사용법:
    python log_analyzer.py
"""

import json
import os
from datetime import datetime
import pandas as pd

def analyze_logs():
    """로그 파일들을 분석하여 통계를 출력"""
    
    if not os.path.exists("logs"):
        print("❌ logs 디렉토리가 존재하지 않습니다.")
        return
    
    log_files = [f for f in os.listdir("logs") if f.startswith("participant_") and f.endswith(".json")]
    
    if not log_files:
        print("❌ 로그 파일이 없습니다.")
        return
    
    print(f"📊 총 {len(log_files)}명의 참여자 로그 분석 중...")
    print("=" * 60)
    
    all_data = []
    total_messages = 0
    total_user_messages = 0
    total_ai_messages = 0
    
    for log_file in log_files:
        with open(f"logs/{log_file}", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        participant_code = data['participant_code']
        message_count = data['message_count']
        conversation_start = data.get('conversation_start', 'N/A')
        conversation_end = data.get('conversation_end', 'N/A')
        
        # 메시지 유형별 카운트
        user_msgs = len([msg for msg in data['conversation'] if msg['role'] == 'user'])
        ai_msgs = len([msg for msg in data['conversation'] if msg['role'] == 'assistant'])
        
        total_messages += message_count
        total_user_messages += user_msgs
        total_ai_messages += ai_msgs
        
        print(f"👤 참여자 {participant_code}:")
        print(f"   📝 총 메시지: {message_count}개 (사용자: {user_msgs}, AI: {ai_msgs})")
        print(f"   🕐 시작: {conversation_start}")
        print(f"   🕑 종료: {conversation_end}")
        print()
        
        # 전체 분석을 위한 데이터 수집
        all_data.append({
            'participant_code': participant_code,
            'total_messages': message_count,
            'user_messages': user_msgs,
            'ai_messages': ai_msgs,
            'conversation_start': conversation_start,
            'conversation_end': conversation_end
        })
    
    print("=" * 60)
    print("📈 전체 통계:")
    print(f"   👥 총 참여자 수: {len(log_files)}명")
    print(f"   💬 총 메시지 수: {total_messages}개")
    print(f"   👤 사용자 메시지: {total_user_messages}개")
    print(f"   🤖 AI 메시지: {total_ai_messages}개")
    print(f"   📊 평균 메시지/참여자: {total_messages/len(log_files):.1f}개")
    print("=" * 60)

def export_to_csv():
    """로그 데이터를 CSV로 내보내기"""
    
    if not os.path.exists("logs"):
        print("❌ logs 디렉토리가 존재하지 않습니다.")
        return
    
    log_files = [f for f in os.listdir("logs") if f.startswith("participant_") and f.endswith(".json")]
    
    if not log_files:
        print("❌ 로그 파일이 없습니다.")
        return
    
    all_conversations = []
    
    for log_file in log_files:
        with open(f"logs/{log_file}", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        participant_code = data['participant_code']
        
        for i, msg in enumerate(data['conversation']):
            all_conversations.append({
                'participant_code': participant_code,
                'message_order': i + 1,
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg.get('timestamp', ''),
                'conversation_start': data.get('conversation_start', ''),
                'conversation_end': data.get('conversation_end', '')
            })
    
    df = pd.DataFrame(all_conversations)
    csv_filename = f"conversation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    print(f"✅ CSV 파일로 내보냄: {csv_filename}")
    print(f"📝 총 {len(all_conversations)}개의 메시지 데이터")

def view_participant_conversation(participant_code):
    """특정 참여자의 대화 내용 보기"""
    
    log_file = f"logs/participant_{participant_code}.json"
    
    if not os.path.exists(log_file):
        print(f"❌ 참여자 {participant_code}의 로그 파일을 찾을 수 없습니다.")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"👤 참여자 {participant_code}의 대화:")
    print("=" * 60)
    
    for i, msg in enumerate(data['conversation'], 1):
        role_icon = "🧑" if msg['role'] == 'user' else "🤖"
        role_name = "사용자" if msg['role'] == 'user' else "R.A.I."
        print(f"{i:2d}. {role_icon} {role_name}: {msg['content']}")
        print()

if __name__ == "__main__":
    print("🔍 R.A.I. 대화 로그 분석기")
    print("=" * 60)
    
    while True:
        print("\n선택하세요:")
        print("1. 📊 전체 로그 분석")
        print("2. 📁 CSV로 내보내기")
        print("3. 👤 특정 참여자 대화 보기")
        print("4. 🚪 종료")
        
        choice = input("\n번호를 입력하세요: ").strip()
        
        if choice == "1":
            analyze_logs()
        elif choice == "2":
            try:
                export_to_csv()
            except ImportError:
                print("❌ pandas가 설치되지 않았습니다. pip install pandas로 설치하세요.")
        elif choice == "3":
            participant_code = input("참여자 코드를 입력하세요: ").strip()
            if participant_code:
                view_participant_conversation(participant_code)
        elif choice == "4":
            print("👋 분석기를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다.")
