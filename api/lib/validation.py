"""
입력 및 데이터 검증 유틸리티
"""
import datetime
import re
from typing import Dict, List, Optional, Tuple


def validate_time_format(time_str: str) -> bool:
    if not time_str or not time_str.strip():
        return False
    patterns = [r'오전|오후', r'\d+시|\d+:\d+', r'이후|이전|-\s*\d+|~']
    return any(re.search(pattern, time_str) for pattern in patterns)


def validate_api_key_format(api_key: str) -> bool:
    if not api_key or not api_key.strip():
        return False
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
    return len(api_key.strip()) >= 10


def validate_schedule_item(item: Dict) -> Tuple[bool, Optional[str]]:
    required_fields = ['task_name', 'start_time', 'end_time']
    for field in required_fields:
        if field not in item:
            return False, f"필수 필드 '{field}'가 없습니다."
    try:
        start_dt = datetime.datetime.fromisoformat(item['start_time'])
        end_dt = datetime.datetime.fromisoformat(item['end_time'])
    except (ValueError, TypeError) as e:
        return False, f"시간 형식 오류: {str(e)}"
    if start_dt >= end_dt:
        return False, "시작 시간은 종료 시간보다 이전이어야 합니다."
    duration_minutes = (end_dt - start_dt).total_seconds() / 60
    if duration_minutes > 480:
        return False, f"일정이 너무 깁니다 ({duration_minutes}분)."
    if duration_minutes < 15:
        return False, f"일정이 너무 짧습니다 ({duration_minutes}분)."
    return True, None


def validate_schedule(schedule: List[Dict], target_date) -> Tuple[List[Dict], List[str]]:
    validated_schedule = []
    errors = []
    if isinstance(target_date, str):
        target_date = datetime.date.fromisoformat(target_date)
    for idx, item in enumerate(schedule):
        is_valid, error_msg = validate_schedule_item(item)
        if is_valid:
            try:
                start_dt = datetime.datetime.fromisoformat(item['start_time'])
                if start_dt.date() == target_date:
                    validated_schedule.append(item)
                else:
                    errors.append(f"항목 {idx+1}: 날짜가 일치하지 않습니다.")
            except Exception as e:
                errors.append(f"항목 {idx+1}: 날짜 검증 오류 - {str(e)}")
        else:
            errors.append(f"항목 {idx+1}: {error_msg}")
    return validated_schedule, errors


def check_schedule_overlaps(schedule: List[Dict]) -> List[Tuple[int, int]]:
    overlaps = []
    for i in range(len(schedule)):
        try:
            start_i = datetime.datetime.fromisoformat(schedule[i]['start_time'])
            end_i = datetime.datetime.fromisoformat(schedule[i]['end_time'])
        except Exception:
            continue
        for j in range(i + 1, len(schedule)):
            try:
                start_j = datetime.datetime.fromisoformat(schedule[j]['start_time'])
                end_j = datetime.datetime.fromisoformat(schedule[j]['end_time'])
            except Exception:
                continue
            if not (end_i <= start_j or end_j <= start_i):
                overlaps.append((i, j))
    return overlaps


def validate_profile(profile: Dict) -> Tuple[bool, Optional[str]]:
    if not profile.get('role') or not profile['role'].strip():
        return False, "역할을 입력해주세요."
    if not profile.get('current_okr') or not profile['current_okr'].strip():
        return False, "핵심 목표를 입력해주세요."
    return True, None


def validate_tasks_input(tasks: str) -> Tuple[bool, Optional[str]]:
    if not tasks or not tasks.strip():
        return False, "할 일을 입력해주세요."
    if len(tasks.strip()) < 10:
        return False, "할 일을 더 자세히 입력해주세요 (최소 10자)."
    lines = [line.strip() for line in tasks.split('\n') if line.strip()]
    if len(lines) < 1:
        return False, "최소 1개 이상의 할 일을 입력해주세요."
    return True, None
