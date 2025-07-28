# =============================================================
# File: firestore_handler.py
# Firebase Firestore 연동 모듈
# =============================================================
"""
Firebase Firestore와의 연동을 담당하는 모듈

주요 기능:
- 참여자별 대화 데이터 실시간 저장
- 통계 데이터 조회
- 로그 데이터 백업 및 복원

환경 변수 요구사항:
- FIREBASE_SERVICE_ACCOUNT_KEY: Firebase 서비스 계정 키 (JSON 문자열)
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

class FirestoreHandler:
    def __init__(self):
        self.db = None
        self.initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Firebase 초기화"""
        try:
            # Firebase가 이미 초기화되었는지 확인
            if not firebase_admin._apps:
                # 환경 변수에서 서비스 계정 키 가져오기
                service_account_key = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
                
                if service_account_key:
                    # JSON 문자열을 파싱
                    cred_dict = json.loads(service_account_key)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                else:
                    # 개발 환경용: 서비스 계정 키 파일 사용
                    key_file_path = "firebase-key.json"
                    if os.path.exists(key_file_path):
                        cred = credentials.Certificate(key_file_path)
                        firebase_admin.initialize_app(cred)
                    else:
                        # Firebase 설정이 없어도 앱이 계속 작동하도록 함
                        print("⚠️ Firebase 설정이 없습니다. 로컬 저장만 사용됩니다.")
                        self.initialized = False
                        return
            
            self.db = firestore.client()
            self.initialized = True
            print("✅ Firebase Firestore 연결 성공!")
            
        except Exception as e:
            print(f"❌ Firebase 초기화 실패: {str(e)}")
            print("📝 로컬 저장만 사용됩니다.")
            self.initialized = False
    
    def is_available(self) -> bool:
        """Firestore 사용 가능 여부 확인"""
        return self.initialized and self.db is not None
    
    def save_conversation(self, participant_code: str, conversation_data: List[Dict], 
                         conversation_end: bool = False) -> bool:
        """참여자 대화 데이터를 Firestore에 저장"""
        if not self.is_available():
            return False
        
        try:
            # 컬렉션 및 문서 참조
            doc_ref = self.db.collection('conversations').document(participant_code)
            
            # 현재 시간
            timestamp = datetime.now()
            
            # 기존 문서가 있는지 확인
            doc = doc_ref.get()
            conversation_start = timestamp
            
            if doc.exists:
                existing_data = doc.to_dict()
                conversation_start = existing_data.get('conversation_start', timestamp)
            
            # 저장할 데이터 구성
            data = {
                'participant_code': participant_code,
                'conversation_start': conversation_start,
                'conversation_end': timestamp if conversation_end else None,
                'last_updated': timestamp,
                'message_count': len(conversation_data),
                'conversation': conversation_data,
                'created_at': conversation_start,
                'updated_at': timestamp
            }
            
            # Firestore에 저장
            doc_ref.set(data)
            return True
            
        except Exception as e:
            print(f"❌ Firestore 저장 실패: {str(e)}")
            return False
    
    def get_conversation_stats(self) -> tuple:
        """전체 대화 통계 조회"""
        if not self.is_available():
            return 0, 0
        
        try:
            # 모든 대화 문서 조회
            docs = self.db.collection('conversations').stream()
            
            total_participants = 0
            total_messages = 0
            
            for doc in docs:
                data = doc.to_dict()
                total_participants += 1
                total_messages += data.get('message_count', 0)
            
            return total_participants, total_messages
            
        except Exception as e:
            print(f"❌ 통계 조회 실패: {str(e)}")
            return 0, 0
    
    def get_participant_conversation(self, participant_code: str) -> Optional[Dict]:
        """특정 참여자의 대화 데이터 조회"""
        if not self.is_available():
            return None
        
        try:
            doc_ref = self.db.collection('conversations').document(participant_code)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
                
        except Exception as e:
            st.error(f"❌ 대화 조회 실패: {str(e)}")
            return None
    
    def get_all_conversations(self) -> List[Dict]:
        """모든 대화 데이터 조회"""
        if not self.is_available():
            return []
        
        try:
            docs = self.db.collection('conversations').stream()
            conversations = []
            
            for doc in docs:
                data = doc.to_dict()
                conversations.append(data)
            
            return conversations
            
        except Exception as e:
            st.error(f"❌ 전체 대화 조회 실패: {str(e)}")
            return []
    
    def backup_to_local(self) -> bool:
        """Firestore 데이터를 로컬 JSON 파일로 백업"""
        if not self.is_available():
            return False
        
        try:
            conversations = self.get_all_conversations()
            
            # 백업 파일명 생성
            backup_filename = f"firestore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # JSON 파일로 저장
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2, default=str)
            
            st.success(f"✅ 백업 완료: {backup_filename}")
            return True
            
        except Exception as e:
            st.error(f"❌ 백업 실패: {str(e)}")
            return False

# 전역 Firestore 핸들러 인스턴스
firestore_handler = FirestoreHandler()
