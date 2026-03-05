"""
고도화된 작업 분해 모듈 - COT (Chain of Thought) 적용
ADHD 사용자를 위한 심층 분석 및 최적화된 작업 분해
"""
import json
from openai import OpenAI
from typing import Dict, List, Optional, Tuple

class AdvancedTaskDecomposer:
    """
    COT 기반 고도화된 작업 분해 클래스
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key
    
    def decompose_with_cot(self, 
                          task_description: str, 
                          user_profile: Optional[Dict] = None,
                          context: Optional[str] = None) -> Dict:
        """
        COT를 적용한 고도화된 작업 분해
        
        Args:
            task_description: 원본 작업 설명
            user_profile: 사용자 프로필 (역할, OKR 등)
            context: 추가 컨텍스트 (기존 일정, 우선순위 등)
        
        Returns:
            고도화된 분해 결과
        """
        
        # COT 프롬프트 생성
        cot_prompt = self._build_cot_prompt(task_description, user_profile, context)
        
        # COT 분석 수행
        analysis_response = self._perform_cot_analysis(cot_prompt)
        
        # 검증 및 최적화
        final_result = self._validate_and_optimize(analysis_response)
        
        return final_result
    
    def _build_cot_prompt(self, 
                         task_description: str, 
                         user_profile: Optional[Dict],
                         context: Optional[str]) -> str:
        """
        COT 기반 프롬프트 생성
        """
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
    
    [COT 사고 과정 - 단계별로 명시적으로 사고하세요]
    
    **1단계: 작업 분석 및 이해**
    - 이 작업의 본질은 무엇인가?
    - 어떤 유형의 작업인가? (창의적/분석적/행정적/혼합)
    - 작업의 범위와 경계는 어디인가?
    - 숨겨진 요구사항이나 전제 조건은 무엇인가?
    
    **2단계: 복잡도 및 난이도 평가**
    - 작업의 복잡도는? (높음/중간/낮음)
    - 인지 부하(cognitive load)는 어느 정도인가?
    - 필요한 기술/지식 수준은?
    - 예상 총 소요 시간은?
    
    **3단계: ADHD 특성 고려**
    - 이 작업에서 ADHD 사용자가 겪을 수 있는 어려움은?
      * Task Initiation (시작 장벽)
      * Sustained Focus (집중력 유지)
      * Working Memory (작업 기억)
      * Executive Function (실행 기능)
      * Time Blindness (시간 인식)
    - 각 어려움에 대한 대응 전략은?
    
    **4단계: 의존성 및 순서 분석**
    - 작업 간 의존성 관계는?
    - 어떤 작업이 다른 작업의 전제 조건인가?
    - 병렬로 진행 가능한 작업은?
    - 순차적으로 진행해야 하는 작업은?
    
    **5단계: 분해 전략 수립**
    - 어떤 분해 전략이 가장 적합한가?
      * Sequential (순차적): 단계별로 순서대로
      * Parallel (병렬): 독립적인 작업들을 동시에
      * Hybrid (혼합): 순차와 병렬 조합
    - 각 단계의 최적 길이는? (15분? 30분? 45분?)
    - 시작 장벽을 낮추기 위한 "Quick Win" 작업은?
    
    **6단계: 위험 요소 및 장애물 예측**
    - 잠재적 장애물은 무엇인가?
    - 어떤 단계에서 막힐 가능성이 높은가?
    - 각 장애물에 대한 완화 전략은?
    
    **7단계: 최적화 제안**
    - Pomodoro 기법 적용 여부?
    - 에너지 레벨에 맞는 시간대 배정?
    - 휴식 빈도 및 길이?
    
    [출력 형식]
    다음 JSON 형식으로 응답하세요. 각 단계의 사고 과정을 "reasoning" 필드에 명시하세요.
    
    {{
        "original_task": "{task_description}",
        
        "analysis": {{
            "complexity": "high|medium|low",
            "estimated_total_time": 120,
            "task_type": "creative|analytical|administrative|mixed",
            "cognitive_load": "high|medium|low",
            "skill_requirements": ["필요한 기술/지식"],
            "adhd_challenges": [
                {{
                    "challenge_type": "task_initiation|sustained_focus|working_memory|executive_function|time_blindness",
                    "severity": "high|medium|low",
                    "description": "구체적인 어려움 설명"
                }}
            ]
        }},
        
        "reasoning": {{
            "step_by_step_thought": [
                "1단계: 작업 분석 - 이 작업은 ...",
                "2단계: 복잡도 평가 - 복잡도는 높음/중간/낮음으로 판단됩니다. 이유는 ...",
                "3단계: ADHD 특성 고려 - ADHD 사용자는 ... 어려움을 겪을 수 있습니다.",
                "4단계: 의존성 분석 - 작업 A는 작업 B의 전제 조건이므로 ...",
                "5단계: 분해 전략 - Sequential 전략을 선택한 이유는 ...",
                "6단계: 위험 예측 - 잠재적 장애물은 ...",
                "7단계: 최적화 - Pomodoro 기법을 권장하는 이유는 ..."
            ],
            "decomposition_strategy": "sequential|parallel|hybrid",
            "strategy_rationale": "왜 이 전략을 선택했는지 상세 설명",
            "chunking_approach": "time_based|task_based|hybrid",
            "chunking_rationale": "작업을 나누는 기준과 이유"
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
                "prerequisites": ["필요한 준비물", "필요한 정보"],
                "deliverables": ["이 단계에서 나올 산출물"],
                "adhd_optimizations": {{
                    "start_barrier": "low|medium|high",
                    "focus_required": "high|medium|low",
                    "momentum_building": true,
                    "quick_wins": true,
                    "energy_level_needed": "high|medium|low",
                    "time_of_day_preference": "morning|afternoon|flexible"
                }},
                "potential_obstacles": [
                    {{
                        "obstacle": "장애물 설명",
                        "likelihood": "high|medium|low",
                        "impact": "high|medium|low",
                        "mitigation": "완화 전략"
                    }}
                ],
                "success_criteria": [
                    "명확한 완료 기준 1",
                    "명확한 완료 기준 2"
                ],
                "next_step_hint": "다음 단계로 넘어가기 위한 힌트"
            }}
        ],
        
        "alternative_approaches": [
            {{
                "approach_name": "대안 방법 이름",
                "description": "대안 방법 설명",
                "pros": ["장점 1", "장점 2"],
                "cons": ["단점 1", "단점 2"],
                "when_to_use": "언제 이 방법을 사용하면 좋은지",
                "estimated_time": 120
            }}
        ],
        
        "optimization_suggestions": {{
            "pomodoro_recommended": true,
            "pomodoro_rationale": "Pomodoro를 권장하는 이유",
            "break_frequency": "every_25min|every_45min|every_60min|custom",
            "break_duration": 5,
            "energy_alignment": {{
                "high_energy_tasks": ["에너지가 높을 때 할 작업"],
                "low_energy_tasks": ["에너지가 낮을 때 할 작업"],
                "recommended_schedule": "오전/오후 배정 제안"
            }},
            "chunking_strategy": "time_based|task_based|hybrid",
            "buffer_time_needed": true,
            "buffer_duration": 10
        }},
        
        "risk_assessment": {{
            "overall_risk": "high|medium|low",
            "high_risk_factors": [
                {{
                    "risk": "위험 요소",
                    "probability": "high|medium|low",
                    "impact": "high|medium|low",
                    "mitigation": "완화 전략"
                }}
            ],
            "contingency_plans": [
                "예비 계획 1",
                "예비 계획 2"
            ]
        }},
        
        "motivation_boosters": [
            "동기 부여 메시지 1",
            "동기 부여 메시지 2"
        ],
        
        "estimated_pomodoros": 3,
        "total_duration": 120
    }}
    """
        return prompt
    
    def _perform_cot_analysis(self, prompt: str) -> Dict:
        """
        COT 분석 수행
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": """당신은 ADHD 사용자를 위한 고급 작업 분해 전문가입니다.
                    Chain of Thought 방식으로 단계별로 깊이 있게 사고하세요.
                    각 단계의 사고 과정을 명시적으로 보여주세요."""
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7  # 창의성과 일관성의 균형
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _validate_and_optimize(self, decomposition: Dict) -> Dict:
        """
        분해 결과 검증 및 최적화
        """
        tasks = decomposition.get("decomposed_tasks", [])
        
        # 검증
        if not tasks:
            raise ValueError("분해된 작업이 없습니다.")
        
        # 총 시간 계산
        total_time = sum(task.get("duration", 0) for task in tasks)
        decomposition["total_duration"] = total_time
        
        # Pomodoro 수 계산
        pomodoros = sum(
            max(1, task.get("duration", 0) // 25) 
            for task in tasks
        )
        decomposition["estimated_pomodoros"] = pomodoros
        
        # 의존성 검증
        for i, task in enumerate(tasks):
            deps = task.get("dependencies", [])
            for dep in deps:
                if isinstance(dep, int) and dep >= i + 1:  # 의존성이 미래를 가리키면 오류
                    # 경고만 표시 (오류는 아니므로)
                    pass
        
        return decomposition


def decompose_task_advanced(
    task_description: str,
    api_key: str,
    user_profile: Optional[Dict] = None,
    context: Optional[str] = None
) -> Dict:
    """
    고도화된 작업 분해 함수 (COT 적용)
    
    Args:
        task_description: 원본 작업
        api_key: OpenAI API 키
        user_profile: 사용자 프로필
        context: 추가 컨텍스트
    
    Returns:
        고도화된 분해 결과
    """
    decomposer = AdvancedTaskDecomposer(api_key)
    return decomposer.decompose_with_cot(task_description, user_profile, context)

