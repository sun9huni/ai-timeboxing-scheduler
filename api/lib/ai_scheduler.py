import datetime
import json
from openai import OpenAI

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
    preset_info = SCHEDULING_PRESETS.get(preset, SCHEDULING_PRESETS["균형잡힌"])
    date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)

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
    2.  가장 중요하고 집중력이 필요한 업무는 사용자의 '집중 업무 시간'에 최우선 배정하세요.
    3.  회의는 '선호하는 회의 시간'에 가능한 한 묶어서 배정하세요.
    4.  행정 업무는 '선호하는 행정 업무 시간'에 배정하세요.
    5.  '기존 일정'과는 절대 겹치지 않게 계획해야 합니다.
    6.  오전 9시부터 오후 6시까지의 일정을 계획합니다.
    7.  점심시간은 {preset_info['lunch_duration']}로 설정하고, "점심 식사"라는 이름으로 포함하세요.
    8.  모든 시간은 30분 단위로 나누어 배정하세요.
    {preset_info['instructions']}
    모든 시간은 오늘 날짜({date_str})에 맞춰 "YYYY-MM-DDTHH:MM:SS" 형식으로 생성하세요.
    
    [출력 형식]
    반드시 아래와 같은 JSON 형식으로만 응답하세요.

    {{
      "schedule": [
        {{
          "task_name": "[집중] 핵심 기획서 작성",
          "start_time": "{date_str}T09:00:00",
          "end_time": "{date_str}T10:30:00",
          "priority": 1,
          "notes": "OKR 관련 가장 중요한 업무."
        }}
      ]
    }}
    """
    return prompt


def get_preset_options():
    return {key: preset["name"] for key, preset in SCHEDULING_PRESETS.items()}


def get_preset_description(preset_key):
    preset = SCHEDULING_PRESETS.get(preset_key)
    return preset["description"] if preset else ""


def get_ai_schedule_openai(prompt, api_key):
    if not api_key:
        raise ValueError("OpenAI API 키가 제공되지 않았습니다.")
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 JSON 응답만 하는 전문 비서입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API 호출 중 오류 발생: {e}") from e
