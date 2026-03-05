# 🤖 AI 타임박싱 스케줄러

사용자의 프로필과 할 일을 입력받아 OpenAI의 LLM(GPT)을 사용하여 지능적으로 우선순위를 정한 뒤, Google 캘린더에 자동으로 일정을 등록하는 Streamlit 애플리케이션입니다.

## 🚀 주요 기능

- **AI 기반 스케줄링**: OpenAI GPT를 활용한 지능적인 일정 계획
- **Google Calendar 연동**: 자동으로 캘린더에 일정 등록
- **사용자 맞춤형**: 개인 프로필과 선호도에 따른 최적화된 스케줄
- **기존 일정 고려**: 이미 있는 일정과 겹치지 않는 스마트한 계획

## 📋 사전 준비

### 1. Google Calendar API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속하여 새 프로젝트를 생성합니다.

2. **'API 및 서비스' > '라이브러리'**에서 **"Google Calendar API"**를 검색하여 '사용 설정'합니다.

3. **'API 및 서비스' > '사용자 인증 정보'**로 이동합니다.

4. **'+ 사용자 인증 정보 만들기' > 'OAuth 클라이언트 ID'**를 선택합니다.

5. '애플리케이션 유형'을 **'데스크톱 앱'**으로 선택하고 '만들기'를 누릅니다.

6. 생성된 인증 정보(JSON)를 다운로드하고, 파일 이름을 `credentials.json`으로 변경하여 프로젝트 폴더에 저장합니다.

### 2. OpenAI API 키 준비

[OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키를 생성하고 준비합니다.

## 🛠️ 설치 및 실행

### 1. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
streamlit run app.py
```

### 3. 사용 방법

1. **Google Calendar 연결**: 첫 실행 시 Google 인증을 진행합니다.
2. **사용자 프로필 설정**: 사이드바에서 개인 정보를 입력합니다.
3. **할 일 입력**: 오늘 완료해야 할 일을 입력합니다.
4. **AI 스케줄 생성**: AI가 최적의 스케줄을 생성합니다.
5. **캘린더 저장**: 생성된 스케줄을 Google Calendar에 저장합니다.

## 📁 파일 구조

```
streamlit-ai-scheduler/
├── 📂 .streamlit/
│   └── config.toml         # Streamlit 테마 설정
├── app.py                  # 메인 Streamlit 애플리케이션
├── ai_scheduler.py         # AI (LLM) 관련 로직 모듈
├── google_calendar.py      # Google Calendar API 로직 모듈
├── requirements.txt        # 필요한 라이브러리 목록
├── credentials.json        # Google API 인증 정보 (사용자가 준비)
├── credentials_template.json # 인증 정보 템플릿
└── README.md              # 이 파일
```

## 🔧 주요 모듈

### `app.py`
- 메인 Streamlit 애플리케이션
- 사용자 인터페이스 및 전체 워크플로우 관리

### `ai_scheduler.py`
- OpenAI API 호출 및 프롬프트 구성
- LLM을 통한 스케줄 생성 로직

### `google_calendar.py`
- Google Calendar API 인증 및 연동
- 기존 일정 조회 및 새 일정 생성

## ⚠️ 주의사항

- `credentials.json` 파일은 절대 공개 저장소에 업로드하지 마세요.
- OpenAI API 사용량에 따라 비용이 발생할 수 있습니다.
- Google Calendar API는 일일 할당량이 있습니다.

## 🐛 문제 해결

### Google 인증 오류
- `token.json` 파일을 삭제하고 다시 인증을 시도하세요.
- `credentials.json` 파일이 올바른 위치에 있는지 확인하세요.

### OpenAI API 오류
- API 키가 올바른지 확인하세요.
- API 사용량 한도를 확인하세요.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.








