"""
AI 타임박싱 스케줄러 - FastAPI 백엔드
Vercel 서버리스 배포용 (Mangum ASGI 어댑터 사용)
"""
import sys
import os
import datetime
import json
import base64

# lib 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from mangum import Mangum

import ai_scheduler
import scheduling_agent as scheduling_agent_module
import validation
import profile_manager
import calendar_service

# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI 타임박싱 스케줄러 API",
    version="2.0.0",
    description="AI 기반 타임박싱 스케줄 생성 및 Google Calendar 연동"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Models ──────────────────────────────────────────────────────────

class ProfileModel(BaseModel):
    role: str
    current_okr: str
    deep_work_time: str = "오전 10:00 - 12:00"
    meeting_preference: str = "오후 1시 이후"
    admin_work_time: str = "오후 4시 이후"


class ScheduleRequest(BaseModel):
    tasks: str
    profile: ProfileModel
    existing_events: str = "없음"
    date: str  # YYYY-MM-DD
    preset: str = "균형잡힌"
    api_key: str
    max_iterations: int = 1


class CalendarSyncRequest(BaseModel):
    schedule: List[Dict[str, Any]]
    timezone: str = "Asia/Seoul"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_token_from_cookie(request: Request) -> Optional[str]:
    token_b64 = request.cookies.get("calendar_token")
    if not token_b64:
        return None
    try:
        return base64.b64decode(token_b64.encode()).decode()
    except Exception:
        return None


def _set_token_cookie(response: Response, token_json: str):
    token_b64 = base64.b64encode(token_json.encode()).decode()
    response.set_cookie(
        key="calendar_token",
        value=token_b64,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30  # 30일
    )


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# ─── Profile Templates ────────────────────────────────────────────────────────

@app.get("/api/profile/templates")
def get_templates():
    """프로필 템플릿 목록 반환"""
    return {
        "templates": profile_manager.get_all_templates(),
        "names": profile_manager.get_template_names()
    }


@app.get("/api/profile/presets")
def get_presets():
    """스케줄링 프리셋 옵션 반환"""
    return {
        "presets": ai_scheduler.SCHEDULING_PRESETS,
        "options": ai_scheduler.get_preset_options()
    }


# ─── Schedule ─────────────────────────────────────────────────────────────────

@app.post("/api/schedule")
async def generate_schedule(req: ScheduleRequest):
    """AI 스케줄 생성"""
    # 검증
    if not validation.validate_api_key_format(req.api_key):
        raise HTTPException(status_code=400, detail="유효하지 않은 API 키 형식입니다.")

    profile_dict = req.profile.model_dump()
    is_valid_profile, profile_error = validation.validate_profile(profile_dict)
    if not is_valid_profile:
        raise HTTPException(status_code=400, detail=profile_error)

    is_valid_tasks, tasks_error = validation.validate_tasks_input(req.tasks)
    if not is_valid_tasks:
        raise HTTPException(status_code=400, detail=tasks_error)

    try:
        target_date = datetime.date.fromisoformat(req.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).")

    try:
        agent = scheduling_agent_module.SchedulingAgent(req.api_key)
        result = agent.process_tasks(
            tasks=req.tasks,
            profile=profile_dict,
            existing_events=req.existing_events,
            date=target_date,
            preset=req.preset,
            max_iterations=req.max_iterations
        )

        schedule = result.get('schedule', [])
        if not schedule:
            raise HTTPException(status_code=500, detail="스케줄 생성에 실패했습니다.")

        validated_schedule, errors = validation.validate_schedule(schedule, target_date)
        overlaps = validation.check_schedule_overlaps(validated_schedule)

        return {
            "schedule": validated_schedule,
            "agent_reasoning": result.get('agent_reasoning', {}),
            "validation_errors": errors,
            "overlap_count": len(overlaps)
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API 사용량 한도에 도달했습니다.")
        elif "api" in error_msg.lower() or "key" in error_msg.lower():
            raise HTTPException(status_code=401, detail="OpenAI API 키를 확인해주세요.")
        raise HTTPException(status_code=500, detail=f"스케줄 생성 중 오류: {error_msg}")


# ─── Calendar Auth ────────────────────────────────────────────────────────────

@app.get("/api/calendar/auth")
async def calendar_auth(request: Request):
    """Google OAuth 인증 URL 반환"""
    # 환경변수 체크
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        raise HTTPException(
            status_code=503,
            detail="Google OAuth 환경변수가 설정되지 않았습니다. GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET을 설정하세요."
        )

    app_url = os.environ.get("NEXT_PUBLIC_APP_URL", str(request.base_url).rstrip('/'))
    redirect_uri = f"{app_url}/api/calendar/callback"

    try:
        auth_url, state = calendar_service.get_auth_url(redirect_uri)
        return {"auth_url": auth_url, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인증 URL 생성 실패: {e}")


@app.get("/api/calendar/callback")
async def calendar_callback(request: Request, code: str, state: str):
    """Google OAuth 콜백 - 토큰 교환 후 프론트엔드로 리다이렉트"""
    app_url = os.environ.get("NEXT_PUBLIC_APP_URL", str(request.base_url).rstrip('/'))
    redirect_uri = f"{app_url}/api/calendar/callback"

    try:
        token_json = calendar_service.exchange_code(code, state, redirect_uri)
        response = RedirectResponse(url=f"{app_url}?calendar_connected=true")
        _set_token_cookie(response, token_json)
        return response
    except Exception as e:
        return RedirectResponse(url=f"{app_url}?calendar_error={str(e)}")


@app.get("/api/calendar/status")
async def calendar_status(request: Request):
    """캘린더 연결 상태 확인"""
    token_json = _get_token_from_cookie(request)
    return {"connected": token_json is not None}


@app.post("/api/calendar/disconnect")
async def calendar_disconnect():
    """캘린더 연결 해제"""
    response = JSONResponse({"disconnected": True})
    response.delete_cookie("calendar_token")
    return response


# ─── Calendar Events ──────────────────────────────────────────────────────────

@app.get("/api/calendar/events")
async def get_events(request: Request, date: str):
    """지정 날짜의 캘린더 이벤트 조회"""
    token_json = _get_token_from_cookie(request)
    if not token_json:
        raise HTTPException(status_code=401, detail="Google Calendar에 연결되지 않았습니다.")

    try:
        target_date = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식 오류 (YYYY-MM-DD)")

    try:
        service, updated_token = calendar_service.get_service_from_token(token_json)
        events = calendar_service.get_existing_events(service, target_date)

        response = JSONResponse({"events": events, "date": date})
        if updated_token != token_json:
            _set_token_cookie(response, updated_token)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 조회 실패: {e}")


@app.post("/api/calendar/sync")
async def sync_to_calendar(request: Request, req: CalendarSyncRequest):
    """스케줄을 Google Calendar에 저장"""
    token_json = _get_token_from_cookie(request)
    if not token_json:
        raise HTTPException(status_code=401, detail="Google Calendar에 연결되지 않았습니다.")

    try:
        service, updated_token = calendar_service.get_service_from_token(token_json)
        result = calendar_service.create_calendar_events(service, req.schedule, req.timezone)

        response = JSONResponse(result)
        if updated_token != token_json:
            _set_token_cookie(response, updated_token)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 저장 실패: {e}")


# ─── Vercel ASGI Handler ──────────────────────────────────────────────────────

handler = Mangum(app, lifespan="off")
