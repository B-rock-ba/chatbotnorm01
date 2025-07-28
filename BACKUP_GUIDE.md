# 📦 Firebase 데이터 백업 가이드

## 🚀 빠른 사용법

Firebase Firestore에 저장된 대화 데이터를 로컬로 백업받으려면:

```bash
python firestore_backup.py
```

## 📁 생성되는 파일들

실행하면 `firestore_backup_YYYYMMDD_HHMMSS` 폴더가 생성되고, 다음 파일들이 저장됩니다:

### 1. 📄 **all_conversations.json**
- 모든 참여자의 대화 데이터를 포함한 전체 JSON 파일
- 프로그래밍적으로 데이터를 처리할 때 사용

### 2. 📁 **participants/** 폴더
- 각 참여자별로 개별 JSON 파일들이 저장됨
- 파일명: `participant_12345678.json`
- 특정 참여자의 데이터만 필요할 때 유용

### 3. 📊 **conversation_summary.csv** / **conversation_summary_excel.csv**
- 참여자별 요약 통계 (Excel에서 열기 가능)
- 포함 정보: 참여자코드, 대화시작/종료시간, 메시지수, 진행상태 등
- **_excel.csv**: Excel용 CP949 인코딩 (한글 깨짐 방지)

### 4. 💬 **detailed_messages.csv** / **detailed_messages_excel.csv**
- 모든 메시지의 상세 내용 (Excel에서 열기 가능)
- 포함 정보: 참여자코드, 메시지순서, 역할(사용자/챗봇), 내용, 타임스탬프 등
- **_excel.csv**: Excel용 CP949 인코딩 (한글 깨짐 방지)

### 5. 📈 **conversation_report.xlsx**
- Excel 형태의 종합 분석 리포트
- 여러 시트로 구성:
  - **참여자요약**: 전체 참여자 현황
  - **참여자_XXXXXXXX**: 각 참여자별 상세 대화 내용 (최대 5명)
  - **전체통계**: 전체 데이터 통계

## 🔧 필요한 패키지

백업 도구 실행 전에 다음 패키지들이 설치되어 있어야 합니다:

```bash
pip install firebase-admin pandas openpyxl
```

## 📋 사용 예시

1. **일반 백업**:
   ```bash
   python firestore_backup.py
   ```

2. **백업 후 Excel 파일로 분석**:
   - 생성된 `conversation_report.xlsx` 파일을 Excel로 열기
   - 다양한 시트에서 데이터 확인 및 분석

3. **CSV 파일로 데이터 처리**:
   - `conversation_summary.csv`: 참여자 현황 분석
   - `detailed_messages.csv`: 메시지 내용 분석

## ⚠️ 주의사항

- Firebase 연결이 필요하므로 `firebase-key.json` 파일이 있어야 합니다
- 대용량 데이터의 경우 백업에 시간이 걸릴 수 있습니다
- 백업된 파일들은 개인정보를 포함하므로 보안에 주의하세요

## 🔍 백업 파일 예시

### conversation_summary.csv
```csv
participant_code,conversation_start,conversation_end,last_updated,message_count,status
12345678,2025-07-28T05:00:00,2025-07-28T05:30:00,2025-07-28T05:30:00,10,완료
87654321,2025-07-28T06:00:00,,2025-07-28T06:15:00,6,진행중
```

### detailed_messages.csv
```csv
participant_code,message_order,role,content,timestamp,content_length
12345678,1,user,안녕하세요,2025-07-28T05:00:00,5
12345678,2,assistant,안녕하세요! 무엇을 도와드릴까요?,2025-07-28T05:00:01,18
```

## 📞 문제 해결

### 🇰🇷 **한글 깨짐 문제 해결**

**문제**: CSV 파일을 Excel에서 열면 한글이 깨져서 보임

**해결방법**:

1. **_excel.csv 파일 사용 (권장)**:
   - `conversation_summary_excel.csv`
   - `detailed_messages_excel.csv`
   - 이 파일들은 Excel용 CP949 인코딩으로 저장되어 한글이 깨지지 않습니다

2. **Excel에서 UTF-8 파일 열기**:
   - Excel → '데이터' 탭 → '텍스트/CSV에서'
   - 파일 선택 → '파일 원본'에서 'UTF-8' 선택
   - '구분 기호'를 '쉼표'로 설정

3. **메모장으로 확인**:
   - UTF-8 파일들을 메모장에서 열면 한글이 정상적으로 보입니다

**"Firestore 연결 불가능" 오류가 나는 경우:**
1. `firebase-key.json` 파일이 프로젝트 루트에 있는지 확인
2. Firebase 프로젝트 설정이 올바른지 확인
3. 인터넷 연결 상태 확인

**"패키지를 찾을 수 없음" 오류가 나는 경우:**
```bash
pip install firebase-admin pandas openpyxl
```
