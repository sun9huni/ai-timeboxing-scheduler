@echo off
echo AI 타임박싱 스케줄러 설정을 시작합니다...

REM Python 가상환경 생성
echo 가상환경을 생성하는 중...
python -m venv venv

REM 가상환경 활성화
echo 가상환경을 활성화하는 중...
call venv\Scripts\activate.bat

REM 필요한 패키지 설치
echo 필요한 패키지를 설치하는 중...
pip install --upgrade pip
pip install streamlit openai google-api-python-client google-auth-httplib2 google-auth-oauthlib pytz pandas

echo 설정이 완료되었습니다!
echo.
echo 실행하려면 다음 명령어를 사용하세요:
echo   venv\Scripts\activate.bat
echo   streamlit run app.py
echo.
pause







