"""
재사용 가능한 UI 컴포넌트
"""
import streamlit as st
from datetime import datetime

def render_step_header(step_num, title, icon="📋", completed=False):
    """단계 헤더를 렌더링합니다."""
    status_icon = "✅" if completed else "⏳"
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h2 style="color: white; margin: 0;">
            {status_icon} Step {step_num}: {icon} {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)

def render_info_card(title, content, icon="ℹ️", color="#4A90E2"):
    """정보 카드를 렌더링합니다."""
    st.markdown(f"""
    <div style="
        background-color: {color}15;
        border-left: 4px solid {color};
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    ">
        <strong>{icon} {title}</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)

def render_success_card(message):
    """성공 메시지 카드를 렌더링합니다."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    ">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def render_warning_card(message):
    """경고 메시지 카드를 렌더링합니다."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
    ">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)

def render_progress_indicator(current_step, total_steps):
    """진행 상황 표시기를 렌더링합니다."""
    progress = current_step / total_steps
    st.progress(progress)
    st.caption(f"진행률: {current_step}/{total_steps} 단계 완료")

def render_empty_state(message, icon="📭"):
    """빈 상태를 렌더링합니다."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 40px;
        color: #666;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">{icon}</div>
        <div style="font-size: 18px;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

