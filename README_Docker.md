# 🐳 Docker로 AI 타임박싱 스케줄러 실행하기

Docker를 사용하여 환경 설정 없이 바로 실행할 수 있습니다.

## 🚀 빠른 시작

### 1. Docker 이미지 빌드
```bash
docker build -t ai-scheduler .
```

### 2. Docker 컨테이너 실행
```bash
docker run -p 8501:8501 -v $(pwd)/credentials.json:/app/credentials.json:ro ai-scheduler
```

### 3. Docker Compose 사용 (권장)
```bash
docker-compose up --build
```

## 📋 사전 준비

### 1. Google Calendar API 설정
- `credentials.json` 파일을 프로젝트 폴더에 준비하세요
- Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 다운로드

### 2. Docker 설치 확인
```bash
docker --version
docker-compose --version
```

## 🔧 사용법

1. **애플리케이션 실행**
   ```bash
   docker-compose up
   ```

2. **브라우저에서 접속**
   - `http://localhost:8501`로 이동

3. **애플리케이션 중지**
   ```bash
   docker-compose down
   ```

## 📁 파일 구조
```
streamlit-ai-scheduler/
├── Dockerfile              # Docker 이미지 설정
├── docker-compose.yml      # Docker Compose 설정
├── .dockerignore          # Docker 빌드 시 제외할 파일
├── requirements.txt        # Python 의존성
├── credentials.json        # Google API 인증 (사용자가 준비)
├── app.py                 # 메인 애플리케이션
├── ai_scheduler.py        # AI 로직
├── google_calendar.py     # Google Calendar API
└── README_Docker.md       # 이 파일
```

## ⚠️ 주의사항

- `credentials.json` 파일이 없으면 Google Calendar 연동이 안 됩니다
- OpenAI API 키는 애플리케이션 내에서 입력해야 합니다
- Docker 컨테이너를 중지하면 데이터가 사라질 수 있습니다

## 🐛 문제 해결

### 포트 충돌
```bash
# 다른 포트 사용
docker run -p 8502:8501 ai-scheduler
```

### 권한 문제
```bash
# Windows에서
docker run -p 8501:8501 -v "%cd%":/app ai-scheduler
```







