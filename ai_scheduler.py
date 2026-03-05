import datetime
import json
from openai import OpenAI

# Streamlit은 선택적 import (모듈 레벨에서는 사용하지 않지만 에러 처리에서 필요할 수 있음)
try:
    import streamlit as st
except ImportError:
    st = None

# 프롬프트 프리셋 정의
SCHEDULING_PRESETS = {
    "균형잡힌": {
        "name": "균형잡힌 스케줄러",
        "description": "일과 휴식을 적절히 균형 잡힌 스케줄",
        "buffer_time": "5분~10분",
        "break_duration": "10분",
        "prefer_continuous_work": False,
        "lunch_duration": "1시간",
        "instructions": """
    8.  일정과 일정 사이에 5분~10분의 짧은 휴식 시간(버퍼 타임)을 두는 것을 고려하되, 필수는 아닙니다.
    9.  각 주요 작업 후 적절한 휴식 시간을 제공하세요.
        """
    },
    "엄격한": {
        "name": "엄격한 스케줄러",
        "description": "버퍼 타임 최소화, 집중 업무 시간 최대화",
        "buffer_time": "최소화 (5분 이하)",
        "break_duration": "5분",
        "prefer_continuous_work": True,
        "lunch_duration": "30분",
        "instructions": """
    8.  버퍼 타임을 최소화(5분 이하)하여 최대한 많은 작업을 효율적으로 배정하세요.
    9.  집중력이 필요한 작업들을 연속적으로 배치하여 몰입 상태를 유지하세요.
    10. 점심 시간은 최소 30분으로 설정하고, 가능하면 작업을 계속할 수 있도록 배치하세요.
        """
    },
    "유연한": {
        "name": "유연한 스케줄러",
        "description": "충분한 휴식 시간, 여유 있게 계획",
        "buffer_time": "10분~15분",
        "break_duration": "15분~20분",
        "prefer_continuous_work": False,
        "lunch_duration": "1시간 30분",
        "instructions": """
    8.  일정과 일정 사이에 충분한 버퍼 타임(10분~15분)을 반드시 두어 여유 있게 계획하세요.
    9.  집중 작업 후에는 최소 15분~20분의 휴식 시간을 제공하세요.
    10. 급하지 않은 작업이라면 시간을 넉넉히 배정하여 스트레스를 줄이세요.
    11. 점심 시간은 충분히(1시간 30분) 제공하여 여유 있게 식사하고 휴식할 수 있게 하세요.
        """
    },
    "긴급 우선": {
        "name": "긴급 우선 스케줄러",
        "description": "마감일과 긴급도 기반 우선순위",
        "buffer_time": "5분",
        "break_duration": "5분~10분",
        "prefer_continuous_work": True,
        "lunch_duration": "30분",
        "instructions": """
    8.  마감일, 긴급도, 중요도를 종합적으로 고려하여 우선순위를 매기세요.
    9.  가장 긴급하고 중요한 작업을 오전에 최우선으로 배정하세요.
    10. 버퍼 타임은 최소화하되(5분), 불가피한 경우만 사용하세요.
    11. 긴급하지 않은 작업은 가능하면 뒤로 미루세요.
    12. 점심 시간은 최소한(30분)으로 설정하여 작업 시간을 최대화하세요.
        """
    }
}

def build_llm_prompt(profile, tasks, existing_events, date, preset="균형잡힌"):
    """LLM에게 전달할 상세한 프롬프트를 생성합니다."""
    
    # 프리셋 정보 가져오기
    preset_info = SCHEDULING_PRESETS.get(preset, SCHEDULING_PRESETS["균형잡힌"])
    
    # 날짜를 YYYY-MM-DD 형식의 문자열로 변환
    date_str = date.isoformat()

    prompt = f"""
    당신은 세계 최고의 전문 비서(타임박싱 전문가)입니다.
    당신의 임무는 사용자의 프로필, 오늘의 할 일, 기존 일정을 바탕으로 오전 9시부터 오후 6시까지의 최적의 '타임박스' 일정을 계획하는 것입니다.

    [오늘 날짜]
    {date_str}

    [사용자 프로필]
    - 역할: {profile['role']}
    - 핵심 목표(OKR): {profile['current_okr']}
    - 선호하는 집중 업무 시간: {profile['deep_work_time']}
    - 선호하는 회의 시간: {profile['meeting_preference']}
    - 선호하는 행정 업무 시간: {profile['admin_work_time']}

    [오늘의 고정된 기존 일정 (수정 불가)]
    {existing_events}

    [오늘 완료해야 할 일 목록]
    {tasks}

    [스케줄링 스타일: {preset_info['name']}]
    {preset_info['description']}
    
    [지시 사항]
    1.  모든 할 일을 분석하여 '핵심 목표'와의 관련성, 중요도, 긴급성을 판단해 우선순위를 매기세요.
    2.  가장 중요하고 집중력이 필요한 업무(예: 기획서 작성)는 사용자의 '집중 업무 시간'에 최우선 배정하세요.
    3.  회의는 '선호하는 회의 시간'에 가능한 한 묶어서 배정하세요.
    4.  '이메일 답장' 같은 자잘한 행정 업무는 '선호하는 행정 업무 시간'에 배정하세요.
    5.  '기존 일정'과는 절대 겹치지 않게 계획해야 합니다.
    6.  오전 9시부터 오후 6시까지의 일정을 계획합니다.
    7.  점심시간은 {preset_info['lunch_duration']}로 설정하고, "점심 식사"라는 이름으로 포함하세요. (기존 일정에 점심이 없다면)
    8.  모든 시간은 30분 단위로 나누어 배정하세요 (예: 9:00, 9:30, 10:00).
    {preset_info['instructions']}
    모든 시간은 오늘 날짜({date_str})에 맞춰 "YYYY-MM-DDTHH:MM:SS" 형식으로 생성하세요.
    
    [출력 형식]
    반드시 아래와 같은 JSON 형식으로만 응답하세요. 다른 설명은 절대 추가하지 마세요.

    {{
      "schedule": [
        {{
          "task_name": "[집중] 핵심 기획서 작성",
          "start_time": "{date_str}T09:00:00",
          "end_time": "{date_str}T10:30:00",
          "priority": 1,
          "notes": "OKR 관련 가장 중요한 업무. 집중 시간 배정."
        }},
        {{
          "task_name": "[회의] 주간 싱크 미팅",
          "start_time": "{date_str}T14:00:00",
          "end_time": "{date_str}T15:00:00",
          "priority": 2,
          "notes": "선호하는 회의 시간에 배정."
        }}
      ]
    }}
    """
    return prompt

def get_preset_options():
    """사용 가능한 프리셋 옵션을 반환합니다."""
    return {key: preset["name"] for key, preset in SCHEDULING_PRESETS.items()}

def get_preset_description(preset_key):
    """프리셋에 대한 설명을 반환합니다."""
    preset = SCHEDULING_PRESETS.get(preset_key)
    if preset:
        return preset["description"]
    return ""

def get_ai_schedule_openai(prompt, api_key):
    """OpenAI API를 호출하여 스케줄을 JSON으로 받습니다."""
    
    if not api_key:
        raise ValueError("OpenAI API 키가 제공되지 않았습니다.")

    try:
        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o", # 또는 gpt-4-turbo, gpt-4o-mini
            messages=[
                {"role": "system", "content": "당신은 JSON 응답만 하는 전문 비서입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # JSON 모드 활성화
        )
        return response.choices[0].message.content
    except Exception as e:
        # API 호출 실패 시 오류 메시지를 포함하는 JSON 반환
        error_message = f"OpenAI API 호출 중 오류 발생: {e}"
        # Streamlit이 있는 경우에만 에러 표시
        if st:
            st.error(error_message)
        # 에러를 raise하여 호출하는 쪽에서 처리하도록 함
        raise Exception(error_message) from e


