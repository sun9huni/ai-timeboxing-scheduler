"""
Google Calendar 서비스 - 서버리스 웹 OAuth 방식
"""
import os
import json
import datetime
import pytz
from typing import Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']


def _get_client_config() -> dict:
    return {
        "web": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def get_auth_url(redirect_uri: str) -> Tuple[str, str]:
    """Google OAuth 인증 URL 생성"""
    client_config = _get_client_config()
    client_config["web"]["redirect_uris"] = [redirect_uri]

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url, state


def exchange_code(code: str, state: str, redirect_uri: str) -> str:
    """OAuth 코드를 토큰으로 교환, JSON 문자열 반환"""
    client_config = _get_client_config()
    client_config["web"]["redirect_uris"] = [redirect_uri]

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
        redirect_uri=redirect_uri
    )
    flow.fetch_token(code=code)
    creds = flow.credentials

    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else list(SCOPES),
    }
    return json.dumps(token_data)


def get_service_from_token(token_json: str):
    """토큰 JSON에서 Calendar 서비스 객체 생성"""
    token_data = json.loads(token_json)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', SCOPES)
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('calendar', 'v3', credentials=creds)
    updated_token = json.dumps({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else list(SCOPES),
    })
    return service, updated_token


def get_existing_events(service, date, tz_str: str = 'Asia/Seoul') -> list:
    """지정 날짜의 캘린더 이벤트 조회"""
    tz = pytz.timezone(tz_str)
    if isinstance(date, str):
        date = datetime.date.fromisoformat(date)

    start_of_day = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz).isoformat()
    end_of_day = datetime.datetime(date.year, date.month, date.day, 23, 59, 59, tzinfo=tz).isoformat()

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            try:
                start_dt = datetime.datetime.fromisoformat(start)
                start_formatted = start_dt.strftime('%H:%M')
            except ValueError:
                start_formatted = start
            event_list.append({
                "time": start_formatted,
                "title": event.get('summary', '제목 없음'),
                "id": event.get('id', '')
            })
        return event_list

    except HttpError as error:
        raise Exception(f"캘린더 조회 실패: {error}") from error


def create_calendar_events(service, schedule: list, tz_str: str = 'Asia/Seoul') -> dict:
    """스케줄을 Google Calendar 이벤트로 일괄 생성"""
    created = 0
    errors = []

    for event_data in schedule:
        event = {
            'summary': event_data.get('task_name', '제목 없음'),
            'description': event_data.get('notes', 'AI 타임박싱 스케줄러로 생성'),
            'start': {'dateTime': event_data['start_time'], 'timeZone': tz_str},
            'end': {'dateTime': event_data['end_time'], 'timeZone': tz_str},
        }
        try:
            service.events().insert(calendarId='primary', body=event).execute()
            created += 1
        except HttpError as error:
            errors.append(f"'{event_data.get('task_name', 'N/A')}' 생성 실패: {error}")

    return {"created": created, "errors": errors}
