# =============================================================
# File: firestore_backup.py
# Firebase Firestore 데이터 백업 및 다운로드 도구
# =============================================================
"""
Firebase Firestore에서 데이터를 로컬로 백업하는 도구

실행 방법:
    python firestore_backup.py

기능:
- 모든 대화 데이터를 JSON 파일로 백업
- 통계 데이터를 CSV 파일로 내보내기
- Excel 형태로 정리된 리포트 생성
- 참여자별 개별 파일 생성
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Firestore 핸들러를 안전하게 import
try:
    from firestore_handler import firestore_handler
    FIRESTORE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Firestore 모듈 로드 실패: {str(e)}")
    firestore_handler = None
    FIRESTORE_AVAILABLE = False

def create_backup_folder():
    """백업 폴더 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"firestore_backup_{timestamp}"
    os.makedirs(backup_folder, exist_ok=True)
    return backup_folder

def backup_all_conversations():
    """모든 대화 데이터를 백업"""
    if not FIRESTORE_AVAILABLE or not firestore_handler or not firestore_handler.is_available():
        print("❌ Firestore 연결 불가능. Firebase 설정을 확인해주세요.")
        return None
    
    print("🔄 Firestore에서 대화 데이터를 가져오는 중...")
    
    try:
        # Firestore에서 모든 대화 데이터 가져오기
        conversations_ref = firestore_handler.db.collection('conversations')
        docs = conversations_ref.stream()
        
        all_conversations = {}
        participant_count = 0
        
        for doc in docs:
            participant_count += 1
            doc_data = doc.to_dict()
            participant_code = doc.id
            all_conversations[participant_code] = doc_data
            print(f"  📥 참여자 {participant_code} 데이터 수집...")
        
        print(f"✅ 총 {participant_count}명의 참여자 데이터 수집 완료!")
        return all_conversations
        
    except Exception as e:
        print(f"❌ 데이터 가져오기 실패: {str(e)}")
        return None

def convert_firestore_data(data):
    """Firestore 데이터를 JSON 직렬화 가능한 형태로 변환"""
    if isinstance(data, dict):
        return {key: convert_firestore_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_firestore_data(item) for item in data]
    elif hasattr(data, 'isoformat'):  # datetime 객체
        return data.isoformat()
    else:
        return data

def save_json_backup(conversations: Dict, backup_folder: str):
    """JSON 형태로 전체 백업 저장"""
    if not conversations:
        return
    
    # Firestore 데이터 변환
    converted_conversations = convert_firestore_data(conversations)
    
    # 전체 데이터 JSON 파일
    json_file = os.path.join(backup_folder, "all_conversations.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(converted_conversations, f, ensure_ascii=False, indent=2)
    
    print(f"📄 전체 JSON 백업 저장: {json_file}")
    
    # 참여자별 개별 JSON 파일
    participants_folder = os.path.join(backup_folder, "participants")
    os.makedirs(participants_folder, exist_ok=True)
    
    for participant_code, data in converted_conversations.items():
        participant_file = os.path.join(participants_folder, f"participant_{participant_code}.json")
        with open(participant_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 참여자별 파일 저장: {participants_folder}/ ({len(conversations)}개 파일)")

def save_csv_summary(conversations: Dict, backup_folder: str):
    """CSV 형태로 요약 데이터 저장"""
    if not conversations:
        return
    
    # Firestore 데이터 변환
    converted_conversations = convert_firestore_data(conversations)
    
    # 요약 통계 CSV
    summary_data = []
    detailed_data = []
    
    for participant_code, data in converted_conversations.items():
        # 기본 정보
        conversation_start = data.get('conversation_start', '')
        conversation_end = data.get('conversation_end', '')
        last_updated = data.get('last_updated', '')
        message_count = data.get('message_count', 0)
        
        # 요약 데이터
        summary_data.append({
            'participant_code': participant_code,
            'conversation_start': conversation_start,
            'conversation_end': conversation_end,
            'last_updated': last_updated,
            'message_count': message_count,
            'status': '완료' if conversation_end else '진행중'
        })
        
        # 상세 메시지 데이터
        conversation = data.get('conversation', [])
        for i, message in enumerate(conversation):
            detailed_data.append({
                'participant_code': participant_code,
                'message_order': i + 1,
                'role': message.get('role', ''),
                'content': message.get('content', '').replace('\n', ' '),  # 개행 문자 제거
                'timestamp': message.get('timestamp', ''),
                'content_length': len(message.get('content', ''))
            })
    
    # 요약 CSV 저장 (UTF-8 BOM 추가로 Excel 호환성 개선)
    summary_file = os.path.join(backup_folder, "conversation_summary.csv")
    with open(summary_file, 'w', newline='', encoding='utf-8-sig') as f:
        if summary_data:
            fieldnames = summary_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)
    
    print(f"📊 요약 CSV 저장: {summary_file}")
    
    # 상세 메시지 CSV 저장 (UTF-8 BOM 추가로 Excel 호환성 개선)
    detailed_file = os.path.join(backup_folder, "detailed_messages.csv")
    with open(detailed_file, 'w', newline='', encoding='utf-8-sig') as f:
        if detailed_data:
            fieldnames = detailed_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(detailed_data)
    
    print(f"💬 상세 메시지 CSV 저장: {detailed_file}")
    
    # Excel 호환 CSV 파일도 추가로 생성 (CP949 인코딩 - 특수문자 제거)
    try:
        # 특수문자를 제거한 데이터 준비
        safe_summary_data = []
        for item in summary_data:
            safe_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    # 이모지 및 특수문자 제거
                    safe_value = ''.join(char for char in value if ord(char) < 65536 and char.isprintable() or char.isspace())
                else:
                    safe_value = value
                safe_item[key] = safe_value
            safe_summary_data.append(safe_item)
        
        safe_detailed_data = []
        for item in detailed_data:
            safe_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    # 이모지 및 특수문자 제거
                    safe_value = ''.join(char for char in value if ord(char) < 65536 and char.isprintable() or char.isspace())
                else:
                    safe_value = value
                safe_item[key] = safe_value
            safe_detailed_data.append(safe_item)
        
        summary_file_excel = os.path.join(backup_folder, "conversation_summary_excel.csv")
        with open(summary_file_excel, 'w', newline='', encoding='cp949', errors='ignore') as f:
            if safe_summary_data:
                fieldnames = safe_summary_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(safe_summary_data)
        
        detailed_file_excel = os.path.join(backup_folder, "detailed_messages_excel.csv")
        with open(detailed_file_excel, 'w', newline='', encoding='cp949', errors='ignore') as f:
            if safe_detailed_data:
                fieldnames = safe_detailed_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(safe_detailed_data)
        
        print(f"📊 Excel용 CSV 저장: {summary_file_excel}")
        print(f"💬 Excel용 CSV 저장: {detailed_file_excel}")
        
    except Exception as e:
        print(f"⚠️ CP949 인코딩 실패: {str(e)} - UTF-8 BOM 파일을 사용하세요")

def save_excel_report(conversations: Dict, backup_folder: str):
    """Excel 형태로 분석 리포트 저장"""
    if not conversations:
        return
    
    try:
        # Firestore 데이터 변환
        converted_conversations = convert_firestore_data(conversations)
        
        excel_file = os.path.join(backup_folder, "conversation_report.xlsx")
        
        # 여러 시트로 구성된 Excel 파일 생성
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 1. 요약 시트
            summary_data = []
            for participant_code, data in converted_conversations.items():
                summary_data.append({
                    '참여자코드': participant_code,
                    '대화시작': data.get('conversation_start', ''),
                    '대화종료': data.get('conversation_end', ''),
                    '마지막업데이트': data.get('last_updated', ''),
                    '메시지수': data.get('message_count', 0),
                    '상태': '완료' if data.get('conversation_end') else '진행중'
                })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='참여자요약', index=False)
            
            # 2. 상세 메시지 시트 (각 참여자별로)
            for participant_code, data in list(converted_conversations.items())[:5]:  # 처음 5명만 (Excel 시트 제한)
                messages = []
                conversation = data.get('conversation', [])
                
                for i, message in enumerate(conversation):
                    messages.append({
                        '순서': i + 1,
                        '역할': '사용자' if message.get('role') == 'user' else '챗봇',
                        '내용': message.get('content', ''),
                        '타임스탬프': message.get('timestamp', ''),
                        '글자수': len(message.get('content', ''))
                    })
                
                if messages:
                    df_messages = pd.DataFrame(messages)
                    sheet_name = f'참여자_{participant_code[:8]}'  # 시트명 길이 제한
                    df_messages.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 3. 통계 시트
            stats_data = {
                '전체참여자수': [len(converted_conversations)],
                '완료된대화': [len([1 for data in converted_conversations.values() if data.get('conversation_end')])],
                '진행중대화': [len([1 for data in converted_conversations.values() if not data.get('conversation_end')])],
                '평균메시지수': [sum(data.get('message_count', 0) for data in converted_conversations.values()) / len(converted_conversations) if converted_conversations else 0],
                '총메시지수': [sum(data.get('message_count', 0) for data in converted_conversations.values())]
            }
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='전체통계', index=False)
        
        print(f"📈 Excel 리포트 저장: {excel_file}")
        
    except ImportError:
        print("⚠️ pandas와 openpyxl이 필요합니다. pip install pandas openpyxl로 설치하세요.")
    except Exception as e:
        print(f"⚠️ Excel 저장 실패: {str(e)}")

def main():
    """메인 백업 함수"""
    print("🔥 Firebase Firestore 데이터 백업 도구")
    print("=" * 50)
    
    # 백업 폴더 생성
    backup_folder = create_backup_folder()
    print(f"📁 백업 폴더 생성: {backup_folder}")
    
    # 데이터 가져오기
    conversations = backup_all_conversations()
    
    if not conversations:
        print("❌ 백업할 데이터가 없습니다.")
        return
    
    # 각 형식으로 저장
    print("\n📦 백업 파일 생성 중...")
    save_json_backup(conversations, backup_folder)
    save_csv_summary(conversations, backup_folder)
    save_excel_report(conversations, backup_folder)
    
    # 완료 메시지
    print("\n" + "=" * 50)
    print(f"✅ 백업 완료! 총 {len(conversations)}명의 데이터가 백업되었습니다.")
    print(f"📁 백업 위치: {os.path.abspath(backup_folder)}")
    print("\n생성된 파일:")
    print("  📄 all_conversations.json - 전체 데이터 JSON")
    print("  📁 participants/ - 참여자별 개별 JSON 파일들")
    print("  📊 conversation_summary.csv - 참여자 요약 CSV (UTF-8 BOM)")
    print("  💬 detailed_messages.csv - 상세 메시지 CSV (UTF-8 BOM)")
    print("  📊 conversation_summary_excel.csv - Excel용 요약 CSV (CP949)")
    print("  � detailed_messages_excel.csv - Excel용 상세 CSV (CP949)")
    print("  �📈 conversation_report.xlsx - Excel 분석 리포트")
    print("\n💡 한글 깨짐 방지:")
    print("  - 권장: UTF-8 BOM 파일 (.csv)을 Excel에서 열기")
    print("  - Excel: '데이터' → '텍스트/CSV에서' → 'UTF-8' 선택")
    print("  - _excel.csv 파일은 이모지가 제거되어 호환성이 떨어질 수 있음")

if __name__ == "__main__":
    main()
