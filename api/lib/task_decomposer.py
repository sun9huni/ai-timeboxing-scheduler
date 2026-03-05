"""
고도화된 작업 분해 모듈 - COT (Chain of Thought) 적용
ADHD 사용자를 위한 심층 분석 및 최적화된 작업 분해
"""
import json
from openai import OpenAI
from typing import Dict, List, Optional


class AdvancedTaskDecomposer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key

    def decompose_with_cot(self,
                           task_description: str,
                           user_profile: Optional[Dict] = None,
                           context: Optional[str] = None) -> Dict:
        cot_prompt = self._build_cot_prompt(task_description, user_profile, context)
        analysis_response = self._perform_cot_analysis(cot_prompt)
        return self._validate_and_optimize(analysis_response)

    def _build_cot_prompt(self, task_description: str,
                          user_profile: Optional[Dict],
                          context: Optional[str]) -> str:
        profile_info = ""
        if user_profile:
            profile_info = f"""
    [사용자 프로필]
    - 역할: {user_profile.get('role', 'N/A')}
    - 핵심 목표: {user_profile.get('current_okr', 'N/A')}
    - 집중 시간대: {user_profile.get('deep_work_time', 'N/A')}
            """
        context_info = f"\n[추가 컨텍스트]\n{context}" if context else ""

        prompt = f"""
    당신은 ADHD 사용자를 위한 고급 작업 분해 전문가입니다.
    Chain of Thought (COT) 방식으로 단계별로 깊이 있게 사고하여 작업을 분해하세요.

    [원본 작업]
    {task_description}
    {profile_info}
    {context_info}

    [출력 형식]
    다음 JSON 형식으로 응답하세요.

    {{
        "original_task": "{task_description}",
        "analysis": {{
            "complexity": "high|medium|low",
            "estimated_total_time": 120,
            "task_type": "creative|analytical|administrative|mixed",
            "cognitive_load": "high|medium|low"
        }},
        "reasoning": {{
            "step_by_step_thought": ["1단계: ...", "2단계: ..."],
            "decomposition_strategy": "sequential|parallel|hybrid",
            "strategy_rationale": "전략 선택 이유"
        }},
        "decomposed_tasks": [
            {{
                "step": 1,
                "task": "구체적인 작업 설명",
                "duration": 30,
                "unit": "분",
                "difficulty": "쉬움|보통|어려움",
                "cognitive_load": "high|medium|low",
                "dependencies": [],
                "adhd_optimizations": {{
                    "start_barrier": "low|medium|high",
                    "focus_required": "high|medium|low",
                    "momentum_building": true,
                    "quick_wins": true
                }},
                "success_criteria": ["완료 기준 1"]
            }}
        ],
        "optimization_suggestions": {{
            "pomodoro_recommended": true,
            "pomodoro_rationale": "권장 이유"
        }},
        "estimated_pomodoros": 3,
        "total_duration": 120
    }}
    """
        return prompt

    def _perform_cot_analysis(self, prompt: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "ADHD 사용자를 위한 작업 분해 전문가입니다. JSON만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"COT 분석 실패: {e}") from e

    def _validate_and_optimize(self, decomposition: Dict) -> Dict:
        tasks = decomposition.get("decomposed_tasks", [])
        if not tasks:
            raise ValueError("분해된 작업이 없습니다.")
        total_time = sum(task.get("duration", 0) for task in tasks)
        decomposition["total_duration"] = total_time
        pomodoros = sum(max(1, task.get("duration", 0) // 25) for task in tasks)
        decomposition["estimated_pomodoros"] = pomodoros
        return decomposition


def decompose_task_advanced(
    task_description: str,
    api_key: str,
    user_profile: Optional[Dict] = None,
    context: Optional[str] = None
) -> Dict:
    decomposer = AdvancedTaskDecomposer(api_key)
    return decomposer.decompose_with_cot(task_description, user_profile, context)
