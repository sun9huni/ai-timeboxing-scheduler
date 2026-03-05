# 🤖 AI Timeboxing Scheduler

> AI가 할 일을 분석하고 우선순위를 정해 Google Calendar에 자동으로 타임박스 일정을 등록하는 스마트 스케줄러

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/sun9huni/ai-timeboxing-scheduler)

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 🧠 AI 타임박싱 | GPT-4o가 작업 복잡도·우선순위를 분석해 9시~18시 일정 자동 생성 |
| 🔗 Google Calendar 연동 | OAuth 2.0으로 기존 일정 조회 및 새 이벤트 자동 등록 |
| 🤖 6단계 Agent 파이프라인 | Reflection → Ranking → Decomposition → Evolution → Proximity → Meta-review |
| ✂️ COT 작업 분해 | 복잡한 작업을 ADHD 친화적 서브태스크로 자동 분해 |
| 🎨 인터랙티브 타임라인 | 시간 블록 시각화 + 드래그 삭제 |
| 🎤 음성 입력 | Web Speech API (Chrome) 지원 |
| 💾 프로필 저장 | localStorage 기반 다중 프로필 관리 |
| 🎯 스케줄링 프리셋 | 균형잡힌 / 엄격한 / 유연한 / 긴급 우선 |

## 🏗️ 아키텍처

```
ai-timeboxing-scheduler/
├── api/                        # FastAPI – Vercel Serverless
│   ├── index.py               # 메인 앱 (Mangum ASGI 어댑터)
│   └── lib/
│       ├── ai_scheduler.py    # OpenAI 프롬프트 빌더
│       ├── scheduling_agent.py# 6단계 Agent 파이프라인
│       ├── task_decomposer.py # COT 작업 분해
│       ├── validation.py      # 입력/출력 검증
│       ├── profile_manager.py # 프로필 템플릿
│       └── calendar_service.py# Google Calendar Web OAuth
├── app/                        # Next.js 14 App Router
│   ├── page.tsx               # 메인 페이지 (5단계 마법사)
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ProfileSidebar.tsx     # 프로필·API키·프리셋 설정
│   ├── CalendarConnect.tsx    # Google 연동 버튼
│   ├── TaskInput.tsx          # 할 일 입력 + 음성
│   └── ScheduleTimeline.tsx   # 인터랙티브 타임라인
├── lib/
│   ├── api.ts                 # API 클라이언트
│   └── types.ts               # TypeScript 타입
├── vercel.json                 # Vercel 라우팅 설정
├── next.config.mjs
├── tailwind.config.ts
└── requirements.txt
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/sun9huni/ai-timeboxing-scheduler.git
cd ai-timeboxing-scheduler
```

### 2. 환경변수 설정

```bash
cp .env.example .env.local
```

`.env.local` 파일을 열어 값을 채웁니다:

```env
OPENAI_API_KEY=sk-...
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. 프론트엔드 실행

```bash
npm install
npm run dev
```

### 4. 백엔드 실행 (별도 터미널)

```bash
pip install -r requirements.txt
npm run dev:api
# 또는: cd api && uvicorn index:app --reload --port 8000
```

→ 브라우저에서 `http://localhost:3000` 접속

---

## ☁️ Vercel 배포

### 사전 준비

#### Google Calendar API 설정

1. [Google Cloud Console](https://console.cloud.google.com/) → 새 프로젝트 생성
2. **API 및 서비스 > 라이브러리** → `Google Calendar API` 사용 설정
3. **사용자 인증 정보 > OAuth 클라이언트 ID** 생성 (웹 애플리케이션 유형)
4. **승인된 리디렉션 URI** 추가:
   - 개발: `http://localhost:3000/api/calendar/callback`
   - 프로덕션: `https://your-domain.vercel.app/api/calendar/callback`

#### Vercel 환경변수 설정

Vercel 대시보드 → 프로젝트 → Settings → Environment Variables:

| 변수 | 값 |
|---|---|
| `OPENAI_API_KEY` | `sk-...` |
| `GOOGLE_CLIENT_ID` | Google OAuth 클라이언트 ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 클라이언트 시크릿 |
| `NEXT_PUBLIC_APP_URL` | `https://your-domain.vercel.app` |

### CLI로 배포

```bash
npm install -g vercel
vercel login
vercel --prod
```

---

## 📖 사용 방법

1. **Google Calendar 연결** — 첫 실행 시 Google 계정 인증
2. **프로필 설정** — 역할, OKR, 선호 시간대 입력 (템플릿 제공)
3. **날짜 선택 & 기존 일정 불러오기** — 오늘 또는 원하는 날짜 선택
4. **할 일 입력** — 텍스트 또는 음성으로 입력
5. **AI 스케줄 생성** — 버튼 클릭 한 번으로 최적 타임박스 생성
6. **확인 & 저장** — 타임라인 확인 후 Google Calendar에 저장

---

## 🔑 API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/api/health` | 상태 확인 |
| `POST` | `/api/schedule` | AI 스케줄 생성 |
| `GET` | `/api/calendar/auth` | Google OAuth URL 반환 |
| `GET` | `/api/calendar/callback` | OAuth 콜백 처리 |
| `GET` | `/api/calendar/events?date=YYYY-MM-DD` | 캘린더 이벤트 조회 |
| `POST` | `/api/calendar/sync` | 이벤트 일괄 저장 |
| `GET` | `/api/profile/templates` | 프로필 템플릿 목록 |

---

## ⚠️ 주의사항

- `credentials.json`, `token.json` 파일은 `.gitignore`에 포함되어 있으며 절대 커밋하지 마세요.
- OpenAI API 사용량에 따라 비용이 발생합니다.
- Vercel Hobby 플랜은 함수 타임아웃 10초로 제한됩니다. AI 스케줄 생성은 Pro 플랜(60초) 권장.
- Google Calendar OAuth는 프로덕션 환경에서 `NEXT_PUBLIC_APP_URL`이 올바르게 설정되어야 합니다.

## 📝 라이선스

MIT License
