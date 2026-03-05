import os
import datetime
import pytz

# Streamlit의 캐싱 기능을 사용해 API 서비스 객체를 관리합니다.
import streamlit as st

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API 스코프 (읽기/쓰기 권한)
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

@st.cache_resource(show_spinner="Google Calendar 서비스에 연결 중...")
def get_calendar_service():
    """
    Google Calendar API 서비스 객체를 인증하고 반환합니다.
    Streamlit의 @st.cache_resource를 사용해 재실행 시에도 연결을 유지합니다.
    """
    creds = None
    
    # token.json 파일이 있으면, 저장된 인증 정보 로드
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # 인증 정보가 없거나 유효하지 않으면, 새로 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                st.error(f"토큰 갱신 실패: {e}. 'token.json' 파일을 삭제하고 앱을 다시 실행하세요.")
                # 문제가 생긴 token.json 파일 삭제
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                return None
        else:
            # credentials.json 파일이 있는지 확인
            if not os.path.exists(CREDENTIALS_FILE):
                st.error(f"'{CREDENTIALS_FILE}' 파일이 없습니다.")
                st.info("Google Cloud Console에서 'OAuth 2.0 클라이언트 ID'를 생성하고 '데스크톱 앱' 유형으로 다운로드 받아주세요.")
                return None
            
            # 새 인증 흐름 시작 (로컬 서버 실행)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # run_local_server는 브라우저를 열어 인증을 요청합니다.
            creds = flow.run_local_server(port=0)
        
        # 새 인증 정보를 token.json에 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    try:
        # requests 기반의 AuthorizedSession 사용 (SSL 문제 해결)
        # httplib2 대신 requests를 사용하여 더 안정적인 SSL 연결
        # 직접 credentials만 전달하면 내부적으로 requests 사용
        service = build('calendar', 'v3', credentials=creds)
        st.success("Google Calendar 서비스에 성공적으로 연결되었습니다!")
        return service
    except HttpError as error:
        st.error(f'서비스 생성 중 오류 발생: {error}')
        return None
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        # SSL 관련 오류 처리
        if 'SSL' in error_msg or 'wrong version number' in error_msg.lower() or 'ssl' in error_type.lower():
            st.error("⚠️ SSL 연결 오류가 발생했습니다.")
            st.warning("네트워크 환경 문제로 보입니다. 다음 방법을 시도해보세요:")
            
            with st.expander("🔧 상세 해결 방법", expanded=True):
                st.markdown("""
                **1. 시스템 프록시 확인**
                - Windows: 설정 > 네트워크 및 인터넷 > 프록시
                - 프록시가 켜져 있다면 꺼보세요
                
                **2. 방화벽/보안 소프트웨어 확인**
                - Windows Defender나 다른 보안 프로그램이 SSL 연결을 차단하는지 확인
                - Python/Streamlit을 예외로 추가
                
                **3. VPN 연결 확인**
                - VPN이 켜져 있다면 일시적으로 해제 후 재시도
                
                **4. 회사 네트워크인 경우**
                - 회사 방화벽이 Google API 접근을 차단할 수 있습니다
                - IT 담당자에게 문의하세요
                
                **5. 임시 해결책 (개발 환경용)**
                - 다른 네트워크 환경(모바일 핫스팟 등)에서 시도
                """)
            
            # 재시도 옵션 제공
            if st.button("🔄 연결 재시도", key="retry_ssl_connection"):
                # 캐시 클리어하고 재시도
                get_calendar_service.clear()
                st.rerun()
            
            return None
        else:
            st.error(f'연결 중 오류 발생: {error_msg}')
            return None

def get_existing_events(service, date, tz_str='Asia/Seoul'):
    """지정된 날짜의 기존 캘린더 이벤트를 가져옵니다."""
    if not service:
        return "캘린더 서비스에 연결되지 않았습니다."

    tz = pytz.timezone(tz_str)
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
        if not events:
            return "없음"
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                # 날짜/시간 포맷팅
                try:
                    start_dt = datetime.datetime.fromisoformat(start)
                    start_formatted = start_dt.strftime('%H:%M')
                except ValueError:
                    start_formatted = start # 날짜만 있는 종일 일정
                
                event_list.append(f"- {start_formatted} / {event['summary']}")
            return "\n".join(event_list)
            
    except HttpError as error:
        error_msg = f"기존 일정 로드 실패: {error}"
        st.warning(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"일정 로드 중 오류 발생: {e}"
        # SSL 오류인 경우 특별 처리
        if 'SSL' in str(e) or 'wrong version number' in str(e):
            error_msg = "SSL 연결 오류: 네트워크 설정을 확인해주세요. 프록시나 방화벽이 SSL 연결을 차단할 수 있습니다."
        st.error(error_msg)
        return error_msg

def create_calendar_event(service, event_data, tz_str='Asia/Seoul'):
    """LLM이 생성한 데이터를 기반으로 캘린더 이벤트를 생성합니다."""
    if not service:
        st.error("캘린더 서비스에 연결되지 않아 이벤트를 생성할 수 없습니다.")
        return

    event = {
        'summary': event_data.get('task_name', '제목 없음'),
        'description': event_data.get('notes', 'AI가 생성한 일정'),
        'start': {
            'dateTime': event_data['start_time'],
            'timeZone': tz_str,
        },
        'end': {
            'dateTime': event_data['end_time'],
            'timeZone': tz_str,
        },
    }
    
    try:
        service.events().insert(
            calendarId='primary', 
            body=event
        ).execute()
    except HttpError as error:
        st.warning(f"'{event['summary']}' 이벤트 생성 중 오류 발생: {error}")

