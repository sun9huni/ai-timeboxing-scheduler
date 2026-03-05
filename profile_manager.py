"""
사용자 프로필 관리 모듈
프로필 저장, 로드, 템플릿 기능 제공
"""
import json
import os
from typing import Dict, List, Optional

PROFILES_FILE = 'profiles.json'

# 기본 프로필 템플릿
PROFILE_TEMPLATES = {
    "프로덕트 매니저": {
        "role": "프로덕트 매니저 (PM)",
        "current_okr": "3분기 '신규 기능 X' 런칭",
        "deep_work_time": "오전 10:00 - 12:00",
        "meeting_preference": "오후 1시 이후",
        "admin_work_time": "오후 4시 이후"
    },
    "개발자": {
        "role": "소프트웨어 개발자",
        "current_okr": "코드 품질 향상 및 기술 부채 감소",
        "deep_work_time": "오전 9:00 - 12:00",
        "meeting_preference": "오후 2시 이후",
        "admin_work_time": "오후 5시 이후"
    },
    "디자이너": {
        "role": "UX/UI 디자이너",
        "current_okr": "사용자 경험 개선 프로젝트",
        "deep_work_time": "오전 10:00 - 12:00",
        "meeting_preference": "오후 1시 이후",
        "admin_work_time": "오후 3시 이후"
    },
    "마케터": {
        "role": "마케팅 매니저",
        "current_okr": "Q3 마케팅 캠페인 성과 달성",
        "deep_work_time": "오전 9:00 - 11:00",
        "meeting_preference": "오전 11시 이후",
        "admin_work_time": "오후 4시 이후"
    },
    "프리랜서": {
        "role": "프리랜서",
        "current_okr": "고객 만족도 향상",
        "deep_work_time": "오전 9:00 - 12:00",
        "meeting_preference": "오후 2시 이후",
        "admin_work_time": "오후 5시 이후"
    }
}

def load_profiles() -> Dict[str, Dict]:
    """저장된 프로필들을 로드합니다."""
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"프로필 로드 오류: {e}")
            return {}
    return {}

def save_profiles(profiles: Dict[str, Dict]):
    """프로필들을 파일에 저장합니다."""
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"프로필 저장 오류: {e}")
        return False

def save_profile(name: str, profile: Dict) -> bool:
    """단일 프로필을 저장합니다."""
    profiles = load_profiles()
    profiles[name] = profile
    return save_profiles(profiles)

def get_profile(name: str) -> Optional[Dict]:
    """특정 이름의 프로필을 가져옵니다."""
    profiles = load_profiles()
    return profiles.get(name)

def delete_profile(name: str) -> bool:
    """프로필을 삭제합니다."""
    profiles = load_profiles()
    if name in profiles:
        del profiles[name]
        return save_profiles(profiles)
    return False

def get_template_names() -> List[str]:
    """사용 가능한 템플릿 이름 목록을 반환합니다."""
    return list(PROFILE_TEMPLATES.keys())

def get_template(name: str) -> Optional[Dict]:
    """템플릿을 가져옵니다."""
    return PROFILE_TEMPLATES.get(name)

