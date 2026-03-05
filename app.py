import streamlit as st
import datetime
import pytz
import json
import pandas as pd
import os

# 로컬 모듈 임포트
import google_calendar
import ai_scheduler
import profile_manager
import validation
import task_decomposer
import scheduling_agent
import voice_input

# --- 페이지 설정 ---
st.set_page_config(
    page_title="AI 타임박싱 스케줄러",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 메인 타이틀 스타일 */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .main-title h1 {
        color: white !important;
        font-size: 2.5rem;
        margin: 0;
    }
    
    /* 단계 헤더 스타일 */
    .step-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 카드 스타일 */
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 4px solid #667eea;
    }
    
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* 버튼 개선 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* 메트릭 스타일 */
    .metric-container {
        background: rgba(102, 126, 234, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .main-title {
            padding: 20px !important;
            margin-bottom: 20px !important;
        }
        
        .main-title h1 {
            font-size: 1.8rem !important;
        }
        
        .main-title p {
            font-size: 1rem !important;
        }
        
        .step-header {
            padding: 15px !important;
            margin: 15px 0 !important;
        }
        
        .step-header h2, .step-header h3 {
            font-size: 1.2rem !important;
        }
        
        /* 터치 친화적 버튼 */
        .stButton>button {
            min-height: 48px;
            font-size: 16px;
            padding: 12px 24px;
        }
        
        /* 사이드바 최적화 */
        .css-1dvm0jo {
            width: 100% !important;
        }
        
        /* 컬럼 레이아웃 조정 */
        [data-testid="column"] {
            width: 100% !important;
        }
        
        /* 텍스트 입력 크기 */
        .stTextInput>div>div>input {
            font-size: 16px;
            padding: 12px;
        }
        
        .stTextArea>div>div>textarea {
            font-size: 16px;
            padding: 12px;
        }
        
        /* 카드 패딩 조정 */
        .info-card {
            padding: 15px !important;
        }
        
        /* 테이블 스크롤 */
        .stDataFrame {
            overflow-x: auto;
        }
    }
    
    /* 태블릿 최적화 */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main-title h1 {
            font-size: 2rem !important;
        }
        
        .step-header {
            padding: 18px !important;
        }
    }
    
    /* 터치 디바이스 최적화 */
    @media (hover: none) and (pointer: coarse) {
        .stButton>button {
            min-height: 44px;
            touch-action: manipulation;
        }
        
        .stSelectbox>div>div {
            min-height: 44px;
        }
        
        .stRadio>div {
            gap: 15px;
        }
        
        .stRadio>div>label {
            padding: 12px;
            min-height: 44px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown("""
<div class="main-title">
    <h1>🤖 AI 타임박싱 스케줄러</h1>
    <p style="font-size: 1.2rem; margin: 10px 0 0 0; opacity: 0.9;">
        당신의 할 일을 입력하면, AI가 우선순위를 정해 Google 캘린더에 자동으로 등록해줍니다
    </p>
</div>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
if 'ai_schedule' not in st.session_state:
    st.session_state.ai_schedule = None
if 'service' not in st.session_state:
    st.session_state.service = None
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = None
if 'schedule_versions' not in st.session_state:
    st.session_state.schedule_versions = []  # 여러 버전의 스케줄 저장
if 'selected_schedule_version' not in st.session_state:
    st.session_state.selected_schedule_version = None
if 'advanced_decomposed' not in st.session_state:
    st.session_state.advanced_decomposed = None
if 'show_advanced_decomposed' not in st.session_state:
    st.session_state.show_advanced_decomposed = False
if 'tasks_input_updated' not in st.session_state:
    st.session_state.tasks_input_updated = None

# --- 사이드바: 설정 ---
with st.sidebar:
    # 사이드바 스타일
    st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #1C202B 0%, #0E1117 100%);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ 설정")
    st.markdown("---")
    
    # 1. OpenAI API 키 입력 (환경 변수 또는 세션 저장 지원)
    st.markdown("#### 🔑 OpenAI API Key")
    
    # 환경 변수에서 먼저 시도
    env_api_key = os.getenv('OPENAI_API_KEY')
    default_value = env_api_key if env_api_key else (st.session_state.openai_api_key or "")
    
    api_key_input = st.text_input(
        "OpenAI API Key", 
        value=default_value,
        type="password", 
        help="OpenAI API 키를 입력하세요. 환경 변수 OPENAI_API_KEY로도 설정할 수 있습니다.",
        key="api_key_input"
    )
    
    # API 키 저장/제거 버튼
    col_save, col_clear = st.columns(2)
    with col_save:
        if st.button("💾 저장", use_container_width=True, key="save_api_key"):
            if api_key_input:
                st.session_state.openai_api_key = api_key_input
                st.success("API 키가 저장되었습니다!")
                st.rerun()
            else:
                st.warning("API 키를 입력해주세요.")
    with col_clear:
        if st.button("🗑️ 삭제", use_container_width=True, key="delete_api_key"):
            st.session_state.openai_api_key = None
            st.rerun()
    
    # 현재 저장된 API 키 표시 (마스킹)
    if st.session_state.openai_api_key or env_api_key:
        saved_key = st.session_state.openai_api_key or env_api_key
        masked_key = saved_key[:8] + "..." + saved_key[-4:] if len(saved_key) > 12 else "***"
        st.caption(f"✅ 저장됨: {masked_key}")
    
    # 사용할 API 키 결정 (환경 변수 > 세션 > 입력값)
    api_key = env_api_key or st.session_state.openai_api_key or api_key_input
    
    st.divider()
    
    # 2. 사용자 프로필 설정
    st.header("👤 사용자 프로필")
    
    # 프로필 관리 상태 초기화
    if 'current_profile_name' not in st.session_state:
        st.session_state.current_profile_name = None
    if 'saved_profiles' not in st.session_state:
        st.session_state.saved_profiles = profile_manager.load_profiles()
    
    # 프로필 선택/저장 섹션
    col_profile_select, col_profile_save = st.columns([2, 1])
    
    with col_profile_select:
        # 저장된 프로필 목록
        saved_profile_names = list(st.session_state.saved_profiles.keys())
        if saved_profile_names:
            selected_saved = st.selectbox(
                "저장된 프로필 선택",
                ["새 프로필"] + saved_profile_names,
                key="profile_select"
            )
            if selected_saved != "새 프로필":
                # 저장된 프로필 로드
                loaded_profile = profile_manager.get_profile(selected_saved)
                if loaded_profile:
                    st.session_state.current_profile_name = selected_saved
                    st.info(f"✅ '{selected_saved}' 프로필이 로드되었습니다.")
        else:
            selected_saved = "새 프로필"
    
    with col_profile_save:
        st.caption("프로필 관리")
    
    # 템플릿 선택
    st.subheader("📋 템플릿에서 시작하기")
    template_names = profile_manager.get_template_names()
    selected_template = st.selectbox(
        "템플릿 선택 (선택 사항)",
        ["템플릿 사용 안 함"] + template_names,
        key="template_select"
    )
    
    # 프로필 기본값 설정
    default_profile = {}
    if selected_template != "템플릿 사용 안 함":
        template = profile_manager.get_template(selected_template)
        if template:
            default_profile = template.copy()
    
    # 현재 프로필이 있으면 기본값으로 사용
    if selected_saved != "새 프로필" and st.session_state.current_profile_name:
        loaded = profile_manager.get_profile(st.session_state.current_profile_name)
        if loaded:
            for key in default_profile:
                default_profile[key] = loaded.get(key, default_profile[key])
    
    # 프로필 입력 필드
    st.subheader("✏️ 프로필 정보 입력")
    st.info("AI가 당신의 성향에 맞춰 일정을 계획합니다.")
    
    profile = {
        "role": st.text_input("역할", value=default_profile.get("role", "프로덕트 매니저 (PM)"), key="profile_role", help="예: 프로덕트 매니저, 개발자, 디자이너"),
        "current_okr": st.text_input("핵심 목표(OKR)", value=default_profile.get("current_okr", "3분기 '신규 기능 X' 런칭"), key="profile_okr", help="현재 달성하고자 하는 주요 목표"),
        "deep_work_time": st.text_input("집중 업무 시간", value=default_profile.get("deep_work_time", "오전 10:00 - 12:00"), key="profile_deep", help="예: 오전 10:00 - 12:00"),
        "meeting_preference": st.text_input("회의 선호 시간", value=default_profile.get("meeting_preference", "오후 1시 이후"), key="profile_meeting", help="예: 오후 1시 이후"),
        "admin_work_time": st.text_input("행정 업무 시간", value=default_profile.get("admin_work_time", "오후 4시 이후"), key="profile_admin", help="예: 오후 4시 이후")
    }
    
    # 프로필 검증
    if not profile['role'].strip():
        st.warning("⚠️ 역할을 입력해주세요.")
    if not profile['current_okr'].strip():
        st.warning("⚠️ 핵심 목표를 입력해주세요.")
    
    # 프로필 저장 섹션
    with st.expander("💾 프로필 저장/관리"):
        col_save_name, col_save_btn = st.columns([2, 1])
        with col_save_name:
            profile_save_name = st.text_input(
                "프로필 이름",
                value=st.session_state.current_profile_name or "",
                placeholder="예: 평일 업무, 주말 프로젝트",
                key="profile_save_name"
            )
        with col_save_btn:
            st.write("")  # 공간 맞추기
            if st.button("💾 저장", use_container_width=True, key="save_profile"):
                if profile_save_name:
                    if profile_manager.save_profile(profile_save_name, profile):
                        st.success(f"'{profile_save_name}' 프로필이 저장되었습니다!")
                        st.session_state.saved_profiles = profile_manager.load_profiles()
                        st.session_state.current_profile_name = profile_save_name
                        st.rerun()
                    else:
                        st.error("프로필 저장에 실패했습니다.")
                else:
                    st.warning("프로필 이름을 입력해주세요.")
        
        # 저장된 프로필 목록 및 삭제
        if st.session_state.saved_profiles:
            st.subheader("저장된 프로필 목록")
            for name in list(st.session_state.saved_profiles.keys()):
                col_list, col_del = st.columns([3, 1])
                with col_list:
                    st.write(f"📌 {name}")
                with col_del:
                    if st.button("🗑️", key=f"delete_profile_{name}"):
                        if profile_manager.delete_profile(name):
                            st.success(f"'{name}' 프로필이 삭제되었습니다!")
                            st.session_state.saved_profiles = profile_manager.load_profiles()
                            if st.session_state.current_profile_name == name:
                                st.session_state.current_profile_name = None
                            st.rerun()
    
    st.divider()
    
    # 2-1. 스케줄링 프리셋 선택
    st.header("🎯 스케줄링 스타일")
    
    # 프리셋 옵션 가져오기
    preset_options = ai_scheduler.get_preset_options()
    
    # 세션 상태에 프리셋 저장
    if 'selected_preset' not in st.session_state:
        st.session_state.selected_preset = "균형잡힌"
    
    # 프리셋 선택
    selected_preset = st.selectbox(
        "스케줄링 스타일 선택",
        options=list(preset_options.keys()),
        format_func=lambda x: preset_options[x],
        index=list(preset_options.keys()).index(st.session_state.selected_preset) if st.session_state.selected_preset in preset_options else 0,
        key="preset_select"
    )
    
    st.session_state.selected_preset = selected_preset
    
    # 프리셋 설명 표시
    preset_desc = ai_scheduler.get_preset_description(selected_preset)
    preset_info = ai_scheduler.SCHEDULING_PRESETS.get(selected_preset)
    
    if preset_info:
        with st.expander(f"📋 {preset_info['name']} 상세 정보", expanded=False):
            st.write(f"**설명:** {preset_info['description']}")
            st.write(f"**버퍼 타임:** {preset_info['buffer_time']}")
            st.write(f"**휴식 시간:** {preset_info['break_duration']}")
            st.write(f"**점심 시간:** {preset_info['lunch_duration']}")
    
    st.divider()
    
    # 3. 날짜 선택
    st.header("🗓️ 날짜 선택")
    
    # 날짜 선택 모드 (단일/범위)
    date_mode = st.radio(
        "날짜 선택 모드",
        ["단일 날짜", "날짜 범위"],
        horizontal=True,
        key="date_mode"
    )
    
    if date_mode == "단일 날짜":
        selected_date = st.date_input("일정을 계획할 날짜", datetime.date.today())
        date_range = [selected_date]
    else:
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("시작 날짜", datetime.date.today())
        with col_end:
            end_date = st.date_input("종료 날짜", datetime.date.today() + datetime.timedelta(days=6))
        
        if start_date > end_date:
            st.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")
            date_range = [datetime.date.today()]
        else:
            # 날짜 범위 생성
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += datetime.timedelta(days=1)
            
            if len(date_range) > 7:
                st.warning(f"선택된 날짜 범위가 너무 큽니다 ({len(date_range)}일). 최대 7일까지만 표시됩니다.")
                date_range = date_range[:7]
    
    # 기본 선택 날짜 (기존 호환성 유지)
    selected_date = date_range[0] if date_range else datetime.date.today()
    
    TIMEZONE = 'Asia/Seoul'
    tz = pytz.timezone(TIMEZONE)

# --- 메인 화면 ---

# Step 1: Google Calendar 연동
st.markdown("""
<div class="step-header">
    <h2 style="color: white; margin: 0;">📅 Step 1: Google Calendar 연동</h2>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    if st.session_state.service is None:
        st.markdown("""
        <div class="info-card">
            <strong>📌 연동 안내</strong><br>
            Google 캘린더에 연동하려면 아래 버튼을 클릭하세요.<br>
            <small>앱을 처음 실행하는 경우, 브라우저에서 Google 인증 팝업이 뜹니다.</small>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn, col_info = st.columns([2, 1])
        with col_btn:
            if st.button("🔗 Google Calendar 연결하기", key="connect_calendar", use_container_width=True, type="primary"):
                # get_calendar_service는 @st.cache_resource로 캐시됩니다.
                # 최초 실행 시 인증 절차(브라우저 팝업)가 진행됩니다.
                st.session_state.service = google_calendar.get_calendar_service()
                if st.session_state.service:
                    st.rerun() # 인증 성공 시 새로고침
        with col_info:
            st.metric("연결 상태", "❌ 미연결")
    else:
        st.markdown("""
        <div class="success-card">
            ✅ Google Calendar가 성공적으로 연결되었습니다!
        </div>
        """, unsafe_allow_html=True)
        st.metric("연결 상태", "✅ 연결됨")
        
# Step 2: 기존 일정 확인 및 할 일 입력
if st.session_state.service:
    # 여러 날짜 선택 시 다른 UI 표시
    if len(date_range) > 1:
        st.info(f"📅 {len(date_range)}일치 일정을 계획합니다: {date_range[0]} ~ {date_range[-1]}")
        
        # 주간 뷰 탭
        week_tabs = st.tabs([f"{d.strftime('%m/%d')}" for d in date_range[:7]])
        
        all_existing_events = {}
        for idx, date in enumerate(date_range[:7]):
            if idx < len(week_tabs):
                with week_tabs[idx]:
                    st.subheader(f"{date.strftime('%Y년 %m월 %d일')} ({date.strftime('%A')[:3]})")
                    with st.spinner(f"{date} 일정을 불러오는 중..."):
                        events_str = google_calendar.get_existing_events(
                            st.session_state.service, 
                            date,
                            TIMEZONE
                        )
                    all_existing_events[date.isoformat()] = events_str
                    st.text_area(
                        "기존 일정", 
                        events_str, 
                        height=200,
                        disabled=True,
                        key=f"events_{date}"
                    )
        
        st.divider()
        st.header("Step 3: 할 일 입력")
        
        # 텍스트 입력 영역
        tasks_input = st.text_area(
            "✏️ 계획할 할 일을 입력하세요 (여러 날짜에 걸쳐 자동 분배됩니다)",
            "예시)\n- '신규 기능 X' 기획서 최종본 작성 (가장 중요함, 2일 소요)\n- 개발팀 주간 싱크 미팅 (1시간)\n- A/B 테스트 결과 데이터 분석 (2시간)\n- 밀린 이메일 및 슬랙 답장하기",
            height=250,
            key="tasks_week",
            help="텍스트로 입력하거나 아래 음성 입력 버튼을 사용하세요"
        )
        
        # 음성 입력 버튼 (주간 뷰용)
        col_voice_week, _ = st.columns([1, 3])
        with col_voice_week:
            voice_input.render_voice_input_button("tasks_week", language="ko-KR")
        
        existing_events_str = f"여러 날짜의 기존 일정:\n" + "\n".join([f"{date}: {all_existing_events[date.isoformat()]}" for date in date_range[:7]])
        
    else:
        # Step 2 & 3 헤더
        st.markdown("""
        <div style="display: flex; gap: 20px; margin: 20px 0;">
            <div class="step-header" style="flex: 1;">
                <h3 style="color: white; margin: 0;">📋 Step 2: 기존 일정 확인</h3>
            </div>
            <div class="step-header" style="flex: 1;">
                <h3 style="color: white; margin: 0;">✏️ Step 3: 할 일 입력</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True, height=400):
                st.markdown("### 🗓️ 오늘의 기존 일정")
                st.caption("AI가 이 정보를 참고하여 최적의 스케줄을 생성합니다")
                with st.spinner(f"{selected_date} 일정을 불러오는 중..."):
                    existing_events_str = google_calendar.get_existing_events(
                        st.session_state.service, 
                        selected_date,
                        TIMEZONE
                    )
                st.text_area(
                    "기존 일정", 
                    existing_events_str, 
                    height=250,
                    disabled=True,
                    label_visibility="collapsed"
                )

        with col2:
            with st.container(border=True, height=400):
                st.markdown("### ✏️ 오늘 완료해야 할 일")
                st.caption("할 일을 입력하면 AI가 우선순위를 정해 일정을 계획합니다")
                
                # 업데이트된 작업이 있으면 사용
                default_tasks = st.session_state.get('tasks_input_updated') or "예시)\n- '신규 기능 X' 기획서 최종본 작성 (가장 중요함)\n- 개발팀 주간 싱크 미팅 (1시간)\n- A/B 테스트 결과 데이터 분석 (2시간)\n- 밀린 이메일 및 슬랙 답장하기"
                if st.session_state.get('tasks_input_updated'):
                    st.session_state.tasks_input_updated = None  # 사용 후 초기화
                
                # 텍스트 입력과 음성 입력을 함께 배치
                tasks_input = st.text_area(
                    "할 일 입력",
                    default_tasks,
                    height=180,
                    label_visibility="collapsed",
                    key="tasks_input",
                    help="텍스트로 입력하거나 아래 음성 입력 버튼을 사용하세요"
                )
                
                # 음성 입력 버튼
                voice_input.render_voice_input_button("tasks_input", language="ko-KR")
                
                # Agent 정보 표시
                st.caption("💡 AI Agent가 자동으로 작업을 분석하고 필요시 분해합니다")

    # Agent의 사고 과정 표시 (분해가 적용된 경우)
    if st.session_state.get('agent_reasoning') and st.session_state.agent_reasoning.get('decomposition_applied'):
        agent_reasoning = st.session_state.agent_reasoning
        decomposition_details = []
        
        # 분해 상세 정보 수집
        for info in agent_reasoning.get('decomposed_tasks_info', []):
            if 'decomposed' in info:
                decomposition_details.append({
                    'original_task': info.get('original_task', ''),
                    'decomposed': info.get('decomposed', {}),
                    'reason': info.get('reason', '')
                })
        
        if decomposition_details:
            st.markdown("---")
            st.markdown("""
            <div class="step-header">
                <h2 style="color: white; margin: 0;">🧠 Agent의 작업 분해 결과</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # 분해된 작업들을 탭으로 표시
            if len(decomposition_details) > 0:
                decomposition_tabs = st.tabs([f"작업 {i+1}" for i in range(len(decomposition_details))])
                
                for idx, detail in enumerate(decomposition_details):
                    if idx < len(decomposition_tabs):
                        with decomposition_tabs[idx]:
                            decomposed = detail.get('decomposed', {})
                            original_task = detail.get('original_task', 'N/A')
                            
                            st.markdown(f"#### ✂️ '{original_task}' 분해 결과")
                            
                            # 분석 요약
                            analysis = decomposed.get('analysis', {})
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                complexity = analysis.get('complexity', 'medium')
                                complexity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(complexity, "🟡")
                                st.metric("복잡도", f"{complexity_emoji} {complexity}")
                            with col2:
                                st.metric("예상 시간", f"{decomposed.get('total_duration', 0)}분")
                            with col3:
                                st.metric("Pomodoro 수", f"{decomposed.get('estimated_pomodoros', 0)}개")
                            
                            # 분해된 작업 목록
                            st.markdown("##### 분해된 작업")
                            for item in decomposed.get('decomposed_tasks', []):
                                difficulty = item.get('difficulty', '보통')
                                difficulty_emoji = {
                                    "쉬움": "🟢", 
                                    "보통": "🟡", 
                                    "어려움": "🔴"
                                }.get(difficulty, "🟡")
                                
                                quick_win = "⚡" if item.get('adhd_optimizations', {}).get('quick_wins') else ""
                                st.write(f"**{item.get('step', '?')}. {item.get('task', 'N/A')}** ({item.get('duration', 0)}분) {difficulty_emoji} {quick_win}")
                            
                            # 사고 과정 (간략 버전)
                            reasoning = decomposed.get('reasoning', {})
                            step_by_step = reasoning.get('step_by_step_thought', [])
                            if step_by_step:
                                with st.expander("🧠 Agent의 사고 과정", expanded=False):
                                    for i, step in enumerate(step_by_step[:3], 1):  # 처음 3단계만
                                        st.caption(f"단계 {i}: {step[:150]}...")
                            
                            st.caption(f"**분해 이유:** {detail.get('reason', '복잡한 작업')}")
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # 기존 고급 분해 결과 표시 (수동 분해가 있는 경우 - 하위 호환성)
    if st.session_state.get('show_advanced_decomposed') and st.session_state.get('advanced_decomposed'):
        decomposed = st.session_state.advanced_decomposed
        
        st.markdown("---")
        st.markdown("""
        <div class="step-header">
            <h2 style="color: white; margin: 0;">🧠 고급 작업 분해 결과 (COT)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 탭으로 상세 정보 분리
        tab_overview, tab_reasoning, tab_details, tab_alternatives = st.tabs([
            "📋 개요", "🧠 사고 과정", "📝 상세", "🔄 대안"
        ])
        
        with tab_overview:
            st.markdown(f"#### ✂️ '{decomposed.get('original_task', 'N/A')}' 분해 결과")
            
            # 분석 요약
            analysis = decomposed.get('analysis', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                complexity = analysis.get('complexity', 'medium')
                complexity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(complexity, "🟡")
                st.metric("복잡도", f"{complexity_emoji} {complexity}")
            with col2:
                st.metric("예상 시간", f"{decomposed.get('total_duration', 0)}분")
            with col3:
                st.metric("Pomodoro 수", f"{decomposed.get('estimated_pomodoros', 0)}개")
            
            # 분해된 작업 목록
            st.markdown("##### 분해된 작업")
            decomposed_text = f"- {decomposed.get('original_task', 'N/A')} (분해됨):\n"
            for item in decomposed.get('decomposed_tasks', []):
                difficulty = item.get('difficulty', '보통')
                difficulty_emoji = {
                    "쉬움": "🟢", 
                    "보통": "🟡", 
                    "어려움": "🔴"
                }.get(difficulty, "🟡")
                
                quick_win = "⚡" if item.get('adhd_optimizations', {}).get('quick_wins') else ""
                decomposed_text += f"  - {item.get('step', '?')}. {item.get('task', 'N/A')} ({item.get('duration', 0)}분) {difficulty_emoji} {quick_win}\n"
            
            st.text_area(
                "분해된 작업",
                decomposed_text,
                height=200,
                key="advanced_decomposed_tasks_display"
            )
        
        with tab_reasoning:
            st.markdown("#### 🧠 AI의 사고 과정 (COT)")
            
            reasoning = decomposed.get('reasoning', {})
            step_by_step = reasoning.get('step_by_step_thought', [])
            
            if step_by_step:
                for i, step in enumerate(step_by_step, 1):
                    with st.expander(f"단계 {i}", expanded=(i <= 3)):
                        st.write(step)
            else:
                st.info("사고 과정 정보가 없습니다.")
            
            st.markdown("##### 전략 선택 근거")
            strategy_rationale = reasoning.get('strategy_rationale', 'N/A')
            if strategy_rationale and strategy_rationale != 'N/A':
                st.info(strategy_rationale)
            else:
                st.info("전략 근거 정보가 없습니다.")
        
        with tab_details:
            st.markdown("#### 📝 각 작업 상세 정보")
            
            for item in decomposed.get('decomposed_tasks', []):
                step_num = item.get('step', '?')
                task_name = item.get('task', 'N/A')
                duration = item.get('duration', 0)
                
                with st.expander(
                    f"단계 {step_num}: {task_name} ({duration}분)",
                    expanded=False
                ):
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.write("**기본 정보**")
                        st.write(f"- 난이도: {item.get('difficulty', 'N/A')}")
                        st.write(f"- 인지 부하: {item.get('cognitive_load', 'N/A')}")
                        deps = item.get('dependencies', [])
                        if deps:
                            st.write(f"- 의존성: {deps}")
                        else:
                            st.write("- 의존성: 없음")
                        
                        prerequisites = item.get('prerequisites', [])
                        if prerequisites:
                            st.write("**필요한 준비물**")
                            for prereq in prerequisites:
                                st.write(f"- {prereq}")
                        
                        deliverables = item.get('deliverables', [])
                        if deliverables:
                            st.write("**산출물**")
                            for deliverable in deliverables:
                                st.write(f"- {deliverable}")
                    
                    with col_right:
                        st.write("**ADHD 최적화**")
                        optimizations = item.get('adhd_optimizations', {})
                        st.write(f"- 시작 장벽: {optimizations.get('start_barrier', 'N/A')}")
                        st.write(f"- 집중 필요도: {optimizations.get('focus_required', 'N/A')}")
                        st.write(f"- 모멘텀 구축: {'✅' if optimizations.get('momentum_building') else '❌'}")
                        st.write(f"- Quick Win: {'✅' if optimizations.get('quick_wins') else '❌'}")
                        
                        success_criteria = item.get('success_criteria', [])
                        if success_criteria:
                            st.write("**완료 기준**")
                            for criteria in success_criteria:
                                st.write(f"- {criteria}")
                        
                        obstacles = item.get('potential_obstacles', [])
                        if obstacles:
                            st.write("**예상 장애물**")
                            for obstacle in obstacles:
                                if isinstance(obstacle, dict):
                                    obstacle_text = obstacle.get('obstacle', '')
                                    mitigation = obstacle.get('mitigation', '')
                                    st.warning(f"⚠️ {obstacle_text}")
                                    if mitigation:
                                        st.caption(f"   → {mitigation}")
                                else:
                                    st.warning(f"⚠️ {obstacle}")
        
        with tab_alternatives:
            st.markdown("#### 🔄 대안 접근 방법")
            
            alternatives = decomposed.get('alternative_approaches', [])
            if alternatives:
                for alt in alternatives:
                    approach_name = alt.get('approach_name', '대안')
                    with st.expander(approach_name, expanded=False):
                        description = alt.get('description', 'N/A')
                        if description and description != 'N/A':
                            st.write(f"**설명:** {description}")
                        
                        col_pros, col_cons = st.columns(2)
                        with col_pros:
                            pros = alt.get('pros', [])
                            if pros:
                                st.write("**장점**")
                                for pro in pros:
                                    st.success(f"✅ {pro}")
                        with col_cons:
                            cons = alt.get('cons', [])
                            if cons:
                                st.write("**단점**")
                                for con in cons:
                                    st.error(f"❌ {con}")
                        
                        when_to_use = alt.get('when_to_use', '')
                        if when_to_use:
                            st.info(f"**언제 사용:** {when_to_use}")
            else:
                st.info("대안 접근 방법이 없습니다.")
        
        # 최적화 제안
        st.markdown("---")
        st.markdown("#### 💡 최적화 제안")
        optimizations = decomposed.get('optimization_suggestions', {})
        
        if optimizations.get('pomodoro_recommended'):
            pomodoro_rationale = optimizations.get('pomodoro_rationale', '')
            if pomodoro_rationale:
                st.success(f"🍅 Pomodoro 기법 권장: {pomodoro_rationale}")
            else:
                st.success("🍅 Pomodoro 기법을 권장합니다.")
        
        energy_alignment = optimizations.get('energy_alignment', {})
        if energy_alignment:
            recommended_schedule = energy_alignment.get('recommended_schedule', '')
            if recommended_schedule:
                st.info(f"⚡ 에너지 배정: {recommended_schedule}")
        
        # 위험 평가
        risk_assessment = decomposed.get('risk_assessment', {})
        if risk_assessment:
            overall_risk = risk_assessment.get('overall_risk', '')
            if overall_risk:
                risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(overall_risk, "🟡")
                st.metric("전체 위험도", f"{risk_emoji} {overall_risk}")
            
            high_risk_factors = risk_assessment.get('high_risk_factors', [])
            if high_risk_factors:
                with st.expander("⚠️ 주요 위험 요소", expanded=False):
                    for risk_factor in high_risk_factors:
                        if isinstance(risk_factor, dict):
                            risk_text = risk_factor.get('risk', '')
                            mitigation = risk_factor.get('mitigation', '')
                            st.warning(f"⚠️ {risk_text}")
                            if mitigation:
                                st.caption(f"   완화 전략: {mitigation}")
                        else:
                            st.warning(f"⚠️ {risk_factor}")
        
        # 동기 부여 메시지
        motivation_boosters = decomposed.get('motivation_boosters', [])
        if motivation_boosters:
            st.markdown("---")
            st.markdown("#### 💪 동기 부여")
            for booster in motivation_boosters:
                st.success(f"✨ {booster}")
        
        # 사용 버튼
        st.markdown("---")
        col_use, col_dismiss = st.columns([2, 1])
        with col_use:
            if st.button("✅ 이 분해 결과 사용하기", use_container_width=True, key="use_advanced_decomposed", type="primary"):
                # 분해된 작업으로 교체
                original_text = tasks_input
                original_task = decomposed.get('original_task', '')
                
                # 원본 작업을 찾아서 교체
                new_text = original_text
                if original_task:
                    # 여러 패턴으로 찾기
                    patterns = [
                        f"- {original_task}",
                        f"• {original_task}",
                        original_task
                    ]
                    for pattern in patterns:
                        if pattern in new_text:
                            new_text = new_text.replace(pattern, decomposed_text.strip())
                            break
                
                st.session_state.tasks_input_updated = new_text
                st.session_state.show_advanced_decomposed = False
                st.success("분해된 작업이 적용되었습니다!")
                st.rerun()
        
        with col_dismiss:
            if st.button("❌ 무시", use_container_width=True, key="dismiss_advanced_decomposed"):
                st.session_state.show_advanced_decomposed = False
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Step 4: AI로 타임박스 생성
    st.markdown("""
    <div class="step-header">
        <h2 style="color: white; margin: 0;">🤖 Step 4: AI로 타임박스 생성하기</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 생성 버튼 섹션
    col_generate, col_regenerate, col_info = st.columns([2, 1, 1])
    
    with col_generate:
        selected_preset_name = ai_scheduler.get_preset_options().get(st.session_state.get('selected_preset', '균형잡힌'), '균형잡힌 스케줄러')
        generate_button = st.button(
            f"🚀 AI 스케줄 생성하기 ({selected_preset_name})", 
            type="primary", 
            use_container_width=True, 
            key="generate_schedule"
        )
    with col_regenerate:
        if st.session_state.ai_schedule:
            regenerate_button = st.button(
                "🔄 다시 생성", 
                use_container_width=True, 
                key="regenerate_schedule"
            )
        else:
            regenerate_button = False
            st.button("🔄 다시 생성", disabled=True, use_container_width=True)
    with col_info:
        if api_key:
            st.metric("API 키", "✅ 설정됨")
        else:
            st.metric("API 키", "❌ 미설정")
    
    if generate_button or regenerate_button:
        # 입력 검증
        validation_errors = []
        
        # API 키 검증
        if not api_key:
            validation_errors.append("OpenAI API Key를 입력하세요.")
        elif not validation.validate_api_key_format(api_key):
            validation_errors.append("API Key 형식이 올바르지 않습니다.")
        
        # 프로필 검증
        is_valid_profile, profile_error = validation.validate_profile(profile)
        if not is_valid_profile:
            validation_errors.append(profile_error)
        
        # 할 일 검증
        is_valid_tasks, tasks_error = validation.validate_tasks_input(tasks_input)
        if not is_valid_tasks:
            validation_errors.append(tasks_error)
        
        # 검증 오류 표시
        if validation_errors:
            for error in validation_errors:
                st.error(f"⚠️ {error}", icon="🔑")
            st.stop()
        
        # 검증 통과 시 실행 - Agent 사용
        with st.spinner("🤖 AI Agent가 작업을 분석하고 최적의 스케줄을 생성 중입니다... (최대 60초 소요)"):
            try:
                # Agent 초기화 및 처리
                selected_preset = st.session_state.get('selected_preset', '균형잡힌')
                agent = scheduling_agent.SchedulingAgent(api_key)
                
                # Agent가 자동으로 처리 (복잡도 판단, 필요시 분해, 반복 개선)
                result = agent.process_tasks(
                    tasks_input,
                    profile,
                    existing_events_str,
                    selected_date,
                    preset=selected_preset,
                    max_iterations=3
                )
                
                # 결과 추출
                new_schedule = result.get('schedule', [])
                agent_reasoning = result.get('agent_reasoning', {})
                
                # Agent의 사고 과정을 세션 상태에 저장
                st.session_state.agent_reasoning = agent_reasoning
                
                # Agent 동작 정보 표시
                if agent_reasoning.get('decomposition_applied'):
                    decomposed_info = agent_reasoning.get('decomposed_tasks_info', [])
                    if decomposed_info:
                        st.info(f"🧠 Agent가 {len(decomposed_info)}개의 복잡한 작업을 자동으로 분해했습니다.")
                        for info in decomposed_info:
                            st.caption(f"  • {info.get('original_task', 'N/A')}: {info.get('reason', '')}")
                
                # 반복 개선 정보 표시
                iterations = agent_reasoning.get('iterations', [])
                if len(iterations) > 1:
                    best_iter = agent_reasoning.get('best_iteration', 1)
                    quality_score = iterations[best_iter - 1].get('quality_score', 0) if best_iter <= len(iterations) else 0
                    st.success(f"✨ Agent가 {len(iterations)}번 반복하여 최적의 스케줄을 찾았습니다. (품질 점수: {quality_score:.2f})")
                
                # 메타 리뷰 정보
                meta_review = agent_reasoning.get('meta_review', {})
                if meta_review.get('issues'):
                    for issue in meta_review.get('issues', []):
                        st.warning(f"⚠️ {issue}")
                
                # 스케줄 데이터 구조 통일 (기존 코드와 호환)
                schedule_data = {"schedule": new_schedule}
                
                # 에러 체크
                if 'error' in schedule_data:
                    st.error(f"AI 호출 오류: {schedule_data.get('error')}")
                    st.stop()
                
                if not new_schedule:
                    st.error("AI Agent가 스케줄을 생성하지 못했습니다. 입력값이나 API 키를 확인하세요.")
                else:
                    # 4. 데이터 유효성 검증 (validation 모듈 사용)
                    validated_schedule, schedule_errors = validation.validate_schedule(new_schedule, selected_date)
                    
                    if not validated_schedule:
                        st.error("생성된 스케줄의 데이터 형식이 올바르지 않습니다.")
                        if schedule_errors:
                            st.write("**발견된 오류:**")
                            for error in schedule_errors[:10]:  # 최대 10개 표시
                                st.caption(f"  • {error}")
                        st.stop()
                    
                    # 5. 중복 검사
                    overlaps = validation.check_schedule_overlaps(validated_schedule)
                    if overlaps:
                        st.warning(f"⚠️ {len(overlaps)}개의 겹치는 일정이 발견되었습니다. 일부 일정을 수동으로 조정해주세요.")
                    
                    if schedule_errors:
                        st.warning(f"⚠️ {len(schedule_errors)}개의 스케줄 항목에 경고가 있습니다:")
                        for error in schedule_errors[:5]:  # 최대 5개만 표시
                            st.caption(f"  • {error}")
                    
                    # 6. 여러 날짜 처리
                    if len(date_range) > 1:
                        st.info(f"📅 여러 날짜 선택됨: {len(date_range)}일 중 {selected_date} 일정만 생성되었습니다. (추가 날짜는 별도로 생성 가능)")
                    
                    # 7. 기존 스케줄이 있으면 버전으로 저장
                    if st.session_state.ai_schedule and regenerate_button:
                        version_info = {
                            'version': len(st.session_state.schedule_versions) + 1,
                            'schedule': st.session_state.ai_schedule.copy(),
                            'timestamp': datetime.datetime.now().isoformat()
                        }
                        st.session_state.schedule_versions.append(version_info)
                    
                    # 8. 새 스케줄 설정
                    st.session_state.ai_schedule = validated_schedule
                    
                    # Agent 정보 표시
                    agent_reasoning = st.session_state.get('agent_reasoning', {})
                    if agent_reasoning:
                        iterations = agent_reasoning.get('iterations', [])
                        if len(iterations) > 1:
                            best_iter = agent_reasoning.get('best_iteration', 1)
                            quality_score = iterations[best_iter - 1].get('quality_score', 0) if best_iter <= len(iterations) else 0
                            st.markdown(f"""
                            <div class="success-card">
                                ✨ AI Agent가 최적의 스케줄을 생성했습니다! (품질: {quality_score:.0%})
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="success-card">
                                ✨ 새로운 스케줄이 생성되었습니다!
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="success-card">
                            ✨ 새로운 스케줄이 생성되었습니다!
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if regenerate_button:
                        st.info(f"💾 이전 버전이 저장되었습니다. 현재 버전: {len(st.session_state.schedule_versions) + 1}")
                    st.balloons()
                    
            except json.JSONDecodeError as e:
                st.error("AI Agent의 응답이 올바른 JSON 형식이 아닙니다. 다시 시도해주세요.")
                st.code(str(e), language="text")
            except Exception as e:
                error_msg = str(e)
                st.error(f"Agent 처리 중 오류 발생: {error_msg}")
                
                # 사용자 친화적인 에러 메시지
                if "API" in error_msg or "key" in error_msg.lower():
                    st.info("💡 OpenAI API 키를 확인해주세요.")
                elif "rate limit" in error_msg.lower():
                    st.info("💡 API 사용량 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
                elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                    st.info("💡 네트워크 연결을 확인해주세요.")
                else:
                    st.info("💡 작업이 너무 복잡할 수 있습니다. 작업을 더 작게 나누어 시도해보세요.")

# Step 5: 결과 확인 및 캘린더에 저장
if st.session_state.ai_schedule:
    st.markdown("""
    <div class="step-header">
        <h2 style="color: white; margin: 0;">📊 Step 5: AI 추천 스케줄 확인 및 저장</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent의 사고 과정 요약 표시
    if st.session_state.get('agent_reasoning'):
        agent_reasoning = st.session_state.agent_reasoning
        with st.expander("🤖 Agent의 사고 과정 요약", expanded=False):
            # Reflection 정보
            reflection = agent_reasoning.get('reflection', {})
            if reflection:
                st.write("**1. 작업 분석 (Reflection)**")
                overall_complexity = reflection.get('overall_complexity', 'N/A')
                total_time = reflection.get('total_estimated_time', 0)
                st.caption(f"  • 전체 복잡도: {overall_complexity}")
                st.caption(f"  • 예상 총 시간: {total_time}분")
            
            # Ranking 정보
            ranking = agent_reasoning.get('ranking', {})
            if ranking.get('decomposition_applied'):
                st.write("**2. 우선순위 및 분해 판단 (Ranking)**")
                st.caption(f"  • 복잡한 작업 발견: {len(ranking.get('complex_tasks', []))}개")
                st.caption("  • 자동 분해 적용됨")
            
            # Evolution 정보
            iterations = agent_reasoning.get('iterations', [])
            if len(iterations) > 1:
                st.write("**3. 반복 개선 (Evolution)**")
                best_iter = agent_reasoning.get('best_iteration', 1)
                st.caption(f"  • 총 반복 횟수: {len(iterations)}회")
                st.caption(f"  • 최적 버전: {best_iter}번째")
                if best_iter <= len(iterations):
                    quality_score = iterations[best_iter - 1].get('quality_score', 0)
                    st.caption(f"  • 품질 점수: {quality_score:.2f}")
            
            # Meta-review 정보
            meta_review = agent_reasoning.get('meta_review', {})
            if meta_review:
                st.write("**4. 최종 검토 (Meta-review)**")
                total_tasks = meta_review.get('total_tasks', 0)
                total_time_minutes = meta_review.get('total_time_minutes', 0)
                st.caption(f"  • 총 작업 수: {total_tasks}개")
                st.caption(f"  • 총 시간: {total_time_minutes}분")
                issues = meta_review.get('issues', [])
                if issues:
                    st.caption(f"  • 발견된 이슈: {len(issues)}개")
    
    # 버전 비교 섹션
    if st.session_state.schedule_versions:
        with st.expander("📊 스케줄 버전 비교", expanded=False):
            st.subheader("이전 버전과 비교하기")
            
            # 현재 버전과 이전 버전 비교
            version_tabs = []
            for i, version_info in enumerate(st.session_state.schedule_versions):
                version_tabs.append(f"버전 {version_info['version']}")
            version_tabs.append("현재 버전")
            
            selected_tab = st.selectbox("비교할 버전 선택", version_tabs)
            
            # 선택된 버전 표시
            if selected_tab == "현재 버전":
                compare_schedule = st.session_state.ai_schedule
            else:
                version_num = int(selected_tab.split()[1])
                compare_schedule = next((v['schedule'] for v in st.session_state.schedule_versions if v['version'] == version_num), None)
            
            if compare_schedule:
                df_compare = pd.DataFrame(compare_schedule)
                if not df_compare.empty:
                    df_compare['start_time'] = pd.to_datetime(df_compare['start_time'])
                    df_compare['end_time'] = pd.to_datetime(df_compare['end_time'])
                    df_compare['start_str'] = df_compare['start_time'].dt.strftime('%H:%M')
                    df_compare['end_str'] = df_compare['end_time'].dt.strftime('%H:%M')
                    
                    for _, row in df_compare.iterrows():
                        st.write(f"**{row['start_str']} - {row['end_str']}** | {row['task_name']}")
                    
                    # 이 버전을 사용하기 버튼
                    if selected_tab != "현재 버전":
                        if st.button(f"✅ 이 버전 ({selected_tab})으로 전환", use_container_width=True, key=f"switch_version_{selected_tab}"):
                            st.session_state.ai_schedule = compare_schedule
                            st.success(f"{selected_tab}으로 전환되었습니다!")
                            st.rerun()
        
        # 버전 목록 정리
        if st.button("🗑️ 모든 버전 삭제", type="secondary", key="delete_all_versions"):
            st.session_state.schedule_versions = []
            st.rerun()
        
        st.divider()
    
    # 주간/월간 뷰 추가 (여러 날짜 선택 시)
    if len(date_range) > 1 and st.session_state.ai_schedule:
        with st.expander("📅 주간 뷰", expanded=True):
            st.subheader(f"주간 스케줄 요약 ({date_range[0]} ~ {date_range[-1]})")
            
            # 날짜별로 그룹화
            df_week = pd.DataFrame(st.session_state.ai_schedule)
            df_week['start_time'] = pd.to_datetime(df_week['start_time'])
            df_week['date'] = df_week['start_time'].dt.date
            
            for date in date_range[:7]:
                day_schedule = df_week[df_week['date'] == date]
                if not day_schedule.empty:
                    st.write(f"**{date.strftime('%m월 %d일 (%A)')}**")
                    for _, row in day_schedule.iterrows():
                        start_str = row['start_time'].strftime('%H:%M')
                        st.write(f"- {start_str} | {row['task_name']}")
                    st.divider()
        
        st.divider()
    
    try:
        # Pandas DataFrame으로 변환
        df = pd.DataFrame(st.session_state.ai_schedule)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60  # 분 단위
        
        # 탭으로 테이블/시각화 분리
        tab_table, tab_timeline, tab_edit = st.tabs(["📋 테이블 뷰", "📊 타임라인", "✏️ 편집"])
        
        with tab_table:
            # 시간 관련 열만 간단히 표시
            df_display = df[['task_name', 'start_time', 'end_time', 'notes']].copy()
            
            # 시간 포맷팅 (T 이후의 시간만 표시)
            df_display['start_time'] = df_display['start_time'].dt.strftime('%H:%M')
            df_display['end_time'] = df_display['end_time'].dt.strftime('%H:%M')
            df_display.rename(columns={
                'task_name': '일정 제목',
                'start_time': '시작',
                'end_time': '종료',
                'notes': 'AI 메모'
            }, inplace=True)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        with tab_timeline:
            st.subheader("📊 시간대별 일정 분포")
            
            # Gantt 차트 스타일의 타임라인 시각화
            chart_data = []
            for idx, row in df.iterrows():
                chart_data.append({
                    'task': row['task_name'],
                    'start': row['start_time'].strftime('%H:%M'),
                    'end': row['end_time'].strftime('%H:%M'),
                    'duration': row['duration']
                })
            
            # 간단한 바 차트로 시간대별 분포 표시
            import altair as alt
            
            # 시간대별 작업 밀도
            df['hour'] = df['start_time'].dt.hour
            hour_counts = df.groupby('hour').size().reset_index(name='count')
            
            chart = alt.Chart(hour_counts).mark_bar(color='#4A90E2').encode(
                x=alt.X('hour:O', title='시간'),
                y=alt.Y('count:Q', title='일정 개수'),
                tooltip=['hour', 'count']
            ).properties(
                width=600,
                height=200,
                title='시간대별 일정 분포'
            )
            st.altair_chart(chart, use_container_width=True)
            
            # 타임라인 리스트
            st.subheader("🕐 시간 순 일정")
            for idx, row in df.sort_values('start_time').iterrows():
                start_str = row['start_time'].strftime('%H:%M')
                end_str = row['end_time'].strftime('%H:%M')
                duration_str = f"{int(row['duration'])}분"
                
                with st.container(border=True):
                    col_time, col_task, col_duration = st.columns([2, 5, 1])
                    with col_time:
                        st.markdown(f"**{start_str}** - {end_str}")
                    with col_task:
                        st.markdown(f"**{row['task_name']}**")
                        if row.get('notes'):
                            st.caption(row['notes'])
                    with col_duration:
                        st.caption(f"⏱️ {duration_str}")
        
        with tab_edit:
            st.subheader("✏️ 스케줄 편집")
            st.info("일정을 삭제하거나 다시 생성할 수 있습니다.")
            
            # 편집 가능한 데이터프레임
            editable_df = df[['task_name', 'start_time', 'end_time', 'notes', 'priority']].copy()
            editable_df['start_time_str'] = editable_df['start_time'].dt.strftime('%H:%M')
            editable_df['end_time_str'] = editable_df['end_time'].dt.strftime('%H:%M')
            editable_df = editable_df.reset_index(drop=True)  # 인덱스를 0부터 시작하도록 리셋
            
            # 삭제할 인덱스 저장
            if 'to_delete' not in st.session_state:
                st.session_state.to_delete = []
            
            for list_idx, (df_idx, row) in enumerate(editable_df.iterrows()):
                with st.expander(f"🔹 {row['task_name']} ({row['start_time_str']} - {row['end_time_str']})"):
                    col_del, col_info = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑️ 삭제", key=f"delete_{list_idx}", type="secondary"):
                            st.session_state.to_delete.append(list_idx)
                            st.rerun()
                    with col_info:
                        st.write(f"**우선순위:** {row.get('priority', 'N/A')}")
                        st.write(f"**메모:** {row.get('notes', '없음')}")
            
            # 삭제된 항목 제거
            if st.session_state.to_delete:
                # 역순으로 정렬하여 인덱스 문제 방지
                for idx in sorted(st.session_state.to_delete, reverse=True):
                    if idx < len(st.session_state.ai_schedule):
                        st.session_state.ai_schedule.pop(idx)
                st.session_state.to_delete = []
                st.rerun()
            
            if st.button("🔄 스케줄 새로고침", type="primary", key="refresh_schedule"):
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 저장 버튼 섹션
        st.markdown("### 💾 캘린더에 저장")
        col_save, col_clear, col_stats = st.columns([3, 1, 1])
        with col_save:
            if st.button("✅ Google Calendar에 저장하기", use_container_width=True, key="save_to_calendar", type="primary"):
                with st.spinner("캘린더에 일정을 저장하는 중..."):
                    count = 0
                    errors = []
                    for event in st.session_state.ai_schedule:
                        try:
                            google_calendar.create_calendar_event(
                                st.session_state.service, 
                                event, 
                                TIMEZONE
                            )
                            count += 1
                        except Exception as e:
                            errors.append(f"{event.get('task_name', 'Unknown')}: {str(e)}")
                    
                    if errors:
                        st.warning(f"⚠️ {len(errors)}개의 일정 저장 중 오류가 발생했습니다.")
                        for error in errors:
                            st.error(error)
                    else:
                        st.markdown(f"""
                        <div class="success-card">
                            🎉 총 {count}개의 일정이 Google Calendar에 성공적으로 저장되었습니다!
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        # 저장이 완료되면 세션 상태 초기화
                        st.session_state.ai_schedule = None
        with col_clear:
            st.write("")
            st.write("")
            if st.button("🗑️ 초기화", use_container_width=True, key="clear_schedule", type="secondary"):
                st.session_state.ai_schedule = None
                st.rerun()
        with col_stats:
            st.metric("일정 개수", len(st.session_state.ai_schedule) if st.session_state.ai_schedule else 0)

    except Exception as e:
        st.error(f"스케줄 표시 중 오류 발생: {e}")
        st.json(st.session_state.ai_schedule) # 원본 JSON 표시

