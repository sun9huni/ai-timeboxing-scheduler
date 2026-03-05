@echo off
echo AI 타임박싱 스케줄러를 시작합니다...

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM Streamlit 실행
streamlit run app.py

pause







