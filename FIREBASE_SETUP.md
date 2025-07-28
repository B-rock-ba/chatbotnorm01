# 🔥 Firebase Firestore 설정 가이드

## 1️⃣ Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com/) 방문
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: `chatbot-logs`)
4. Google Analytics 설정 (선택사항)
5. 프로젝트 생성 完了

## 2️⃣ Firestore 데이터베이스 설정

1. Firebase Console에서 생성한 프로젝트 선택
2. 왼쪽 메뉴에서 "Firestore Database" 클릭
3. "데이터베이스 만들기" 클릭
4. **테스트 모드**로 시작 (개발용)
5. 지역 선택 (예: `asia-northeast3 (Seoul)`)

## 3️⃣ 서비스 계정 키 생성

1. Firebase Console → "프로젝트 설정" (톱니바퀴 아이콘)
2. "서비스 계정" 탭 클릭
3. "새 비공개 키 생성" 클릭
4. JSON 파일 다운로드
5. 파일 이름을 `firebase-key.json`으로 변경
6. 프로젝트 루트 폴더에 저장

## 4️⃣ 환경 변수 설정 (프로덕션용)

### Streamlit Cloud 배포 시:
1. Streamlit Cloud에서 앱 설정
2. "Secrets" 섹션에 다음 추가:

```toml
FIREBASE_SERVICE_ACCOUNT_KEY = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
"""
```

### 로컬 개발 시:
1. `firebase-key.json` 파일을 프로젝트 루트에 저장
2. 또는 환경 변수 설정:
```bash
export FIREBASE_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
```

## 5️⃣ 보안 규칙 설정 (중요!)

### 🚨 현재 상황: 테스트 모드 사용 중

현재 개발 단계에서는 **테스트 모드**를 사용하고 있어 별도 보안 규칙 설정이 불필요합니다.
- ✅ **현재**: 테스트 모드 (30일 후 자동 만료)
- ⚠️ **30일 후**: 아래 규칙을 적용해야 함

### 📋 서비스 계정용 보안 규칙 (30일 후 적용)

Firestore Console에서 규칙 탭으로 이동하여 다음 규칙 적용:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 서비스 계정으로 접근하는 chatbot 데이터
    match /conversations/{document} {
      // 서비스 계정 인증을 통한 접근 허용
      allow read, write: if true;
    }
    
    // 통계 데이터 접근
    match /statistics/{document} {
      allow read, write: if true;
    }
  }
}
```

### 🔐 더 안전한 보안 규칙 (프로덕션용)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 특정 서비스 계정만 접근 허용
    match /conversations/{document} {
      allow read, write: if request.auth != null 
        && request.auth.token.email == "firebase-adminsdk-xxxxx@chatbot-log-01.iam.gserviceaccount.com";
    }
  }
}
```

**중요**: 현재는 테스트 모드이므로 규칙 변경 불필요! 30일 후에만 적용하세요.

## 6️⃣ 파일 구조

```
chatbotnorm01/
├── app.py
├── chatbot_core.py
├── firestore_handler.py
├── firebase-key.json          # 개발용 (Git에 업로드 금지!)
├── requirements.txt
└── logs/                      # 로컬 백업
    └── participant_*.json
```

## 7️⃣ .gitignore 설정

다음 항목들이 `.gitignore`에 포함되어 있는지 확인:

```
# Firebase 키 파일 (보안상 중요!)
firebase-key.json

# 로그 데이터 (개인정보)
logs/

# 임시 파일
t.py
__pycache__/
```

## 🚀 완료!

이제 챗봇이 Firestore에 대화 데이터를 자동으로 저장합니다:
- ✅ 로컬 JSON 파일 저장 (백업)
- ✅ Firestore 실시간 저장
- ✅ 통계 데이터 실시간 조회
- ✅ 데이터 백업 기능

## 🔧 문제 해결

### Firestore 연결 안됨
1. `firebase-key.json` 파일 확인
2. Firebase 프로젝트 설정 확인
3. 서비스 계정 권한 확인

### 권한 오류
1. Firestore 보안 규칙 확인
2. 서비스 계정 역할 확인 (Firestore 편집자 권한 필요)

### 프로덕션 배포 시
1. 환경 변수 `FIREBASE_SERVICE_ACCOUNT_KEY` 설정
2. Firestore 보안 규칙 프로덕션 모드로 변경
