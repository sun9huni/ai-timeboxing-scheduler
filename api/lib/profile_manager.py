"""
사용자 프로필 관리 모듈 (서버리스 호환)
"""
from typing import Dict, List, Optional

PROFILE_TEMPLATES: Dict[str, Dict] = {
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


def get_template_names() -> List[str]:
    return list(PROFILE_TEMPLATES.keys())


def get_template(name: str) -> Optional[Dict]:
    return PROFILE_TEMPLATES.get(name)


def get_all_templates() -> Dict[str, Dict]:
    return PROFILE_TEMPLATES
