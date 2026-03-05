"""
입력 및 데이터 검증 유틸리티
"""
import datetime
import re
from typing import Dict, List, Optional, Tuple

def validate_time_format(time_str: str) -> bool:
    """시간 형식 검증 (예: '오전 10:00 - 12:00' 또는 '오후 1시 이후')"""
    if not time_str or not time_str.strip():
        return False
    
    # 기본적인 패턴 체크
    patterns = [
        r'오전|오후',  # 오전/오후 포함
        r'\d+시|\d+:\d+',  # 시간 형식
        r'이후|이전|-\s*\d+|~'  # 범위 표현
    ]
    
    # 하나 이상의 패턴이 매치되는지 확인
    return any(re.search(pattern, time_str) for pattern in patterns)

def validate_api_key_format(api_key: str) -> bool:
    """OpenAI API 키 기본 형식 검증"""
    if not api_key or not api_key.strip():
        return False
    
    # OpenAI API 키는 보통 'sk-'로 시작하고 충분한 길이를 가짐
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
    
    # 환경 변수나 다른 형식일 수 있으므로 최소 길이만 체크
    return len(api_key.strip()) >= 10

def validate_schedule_item(item: Dict) -> Tuple[bool, Optional[str]]:
    """스케줄 항목 유효성 검증"""
    # 필수 필드 확인
    required_fields = ['task_name', 'start_time', 'end_time']
    for field in required_fields:
        if field not in item:
            return False, f"필수 필드 '{field}'가 없습니다."
    
    # 시간 형식 검증
    try:
        start_dt = datetime.datetime.fromisoformat(item['start_time'])
        end_dt = datetime.datetime.fromisoformat(item['end_time'])
    except (ValueError, TypeError) as e:
        return False, f"시간 형식 오류: {str(e)}"
    
    # 시간 순서 검증
    if start_dt >= end_dt:
        return False, "시작 시간은 종료 시간보다 이전이어야 합니다."
    
    # 합리적인 범위 검증 (너무 긴 일정 체크)
    duration_minutes = (end_dt - start_dt).total_seconds() / 60
    if duration_minutes > 480:  # 8시간 초과
        return False, f"일정이 너무 깁니다 ({duration_minutes}분)."
    
    if duration_minutes < 15:  # 15분 미만
        return False, f"일정이 너무 짧습니다 ({duration_minutes}분)."
    
    return True, None

def validate_schedule(schedule: List[Dict], target_date: datetime.date) -> Tuple[List[Dict], List[str]]:
    """전체 스케줄 유효성 검증"""
    validated_schedule = []
    errors = []
    
    for idx, item in enumerate(schedule):
        is_valid, error_msg = validate_schedule_item(item)
        if is_valid:
            # 날짜 검증
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
    """스케줄 중복(겹침) 검사"""
    overlaps = []
    
    for i in range(len(schedule)):
        try:
            start_i = datetime.datetime.fromisoformat(schedule[i]['start_time'])
            end_i = datetime.datetime.fromisoformat(schedule[i]['end_time'])
        except:
            continue
        
        for j in range(i + 1, len(schedule)):
            try:
                start_j = datetime.datetime.fromisoformat(schedule[j]['start_time'])
                end_j = datetime.datetime.fromisoformat(schedule[j]['end_time'])
            except:
                continue
            
            # 시간 겹침 체크
            if not (end_i <= start_j or end_j <= start_i):
                overlaps.append((i, j))
    
    return overlaps

def validate_profile(profile: Dict) -> Tuple[bool, Optional[str]]:
    """프로필 유효성 검증"""
    if not profile.get('role') or not profile['role'].strip():
        return False, "역할을 입력해주세요."
    
    if not profile.get('current_okr') or not profile['current_okr'].strip():
        return False, "핵심 목표를 입력해주세요."
    
    # 시간 형식 검증 (선택적)
    time_fields = ['deep_work_time', 'meeting_preference', 'admin_work_time']
    for field in time_fields:
        if profile.get(field) and not validate_time_format(profile[field]):
            # 경고만 표시 (필수는 아님)
            pass
    
    return True, None

def validate_tasks_input(tasks: str) -> Tuple[bool, Optional[str]]:
    """할 일 입력 검증"""
    if not tasks or not tasks.strip():
        return False, "할 일을 입력해주세요."
    
    # 최소 길이 체크
    if len(tasks.strip()) < 10:
        return False, "할 일을 더 자세히 입력해주세요 (최소 10자)."
    
    # 줄 수 체크
    lines = [line.strip() for line in tasks.split('\n') if line.strip()]
    if len(lines) < 1:
        return False, "최소 1개 이상의 할 일을 입력해주세요."
    
    return True, None

