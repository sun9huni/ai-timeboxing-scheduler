"""
Google Co-Scientist 스타일 스케줄링 Agent
자동으로 작업 복잡도를 판단하고 필요시 고급 분해를 사용
"""
import json
import datetime
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
import task_decomposer
import ai_scheduler
import validation

class SchedulingAgent:
    """
    지능형 스케줄링 Agent
    - 작업 복잡도 자동 판단
    - 필요시 자동 분해
    - 반복적 개선
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key
        self.decomposer = task_decomposer.AdvancedTaskDecomposer(api_key)
    
    def process_tasks(self,
                     tasks: str,
                     profile: Dict,
                     existing_events: str,
                     date,
                     preset: str = "균형잡힌",
                     max_iterations: int = 3) -> Dict:
        """
        Google Co-Scientist 스타일의 멀티 스텝 처리
        
        Returns:
            {
                "schedule": [...],
                "agent_reasoning": {
                    "reflection": {...},
                    "ranking": {...},
                    "decomposition_applied": True/False,
                    "iterations": [...],
                    "meta_review": {...}
                }
            }
        """
        
        # Step 1: Reflection - 작업 분석 및 복잡도 평가
        reflection = self._reflect_on_tasks(tasks, profile)
        
        # Step 2: Ranking - 작업 우선순위 및 분해 필요성 판단
        ranking = self._rank_tasks(reflection)
        
        # Step 3: Generation - 필요시 분해, 스케줄 생성
        processed_tasks = self._generate_schedule_input(
            tasks, 
            reflection, 
            ranking, 
            profile
        )
        
        # Step 4: Evolution - 반복적 개선
        best_schedule = None
        iterations = []
        
        for iteration in range(max_iterations):
            schedule_result = self._generate_schedule(
                processed_tasks,
                profile,
                existing_events,
                date,
                preset
            )
            
            # Step 5: Proximity - 충돌 검사
            proximity_check = self._check_proximity(
                schedule_result.get('schedule', []),
                existing_events
            )
            
            # Step 6: Meta-review - 품질 평가
            meta_review = self._meta_review(
                schedule_result,
                proximity_check,
                reflection,
                ranking
            )
            
            iterations.append({
                "iteration": iteration + 1,
                "schedule": schedule_result.get('schedule', []),
                "quality_score": meta_review.get('quality_score', 0),
                "issues": meta_review.get('issues', []),
                "improvements": meta_review.get('suggested_improvements', [])
            })
            
            # 최고 품질 스케줄 선택
            if best_schedule is None or meta_review.get('quality_score', 0) > best_schedule.get('quality_score', 0):
                best_schedule = {
                    "schedule": schedule_result.get('schedule', []),
                    "quality_score": meta_review.get('quality_score', 0),
                    "iteration": iteration + 1
                }
            
            # 만족스러우면 조기 종료
            if meta_review.get('quality_score', 0) >= 0.9:
                break
        
        # 최종 메타 리뷰
        final_meta_review = iterations[-1] if iterations else {}
        
        # 분해 상세 정보 추가
        decomposed_tasks_info = ranking.get('decomposed_tasks_info', [])
        decomposition_details = ranking.get('decomposition_details', [])
        
        # 분해 상세 정보를 통합
        for detail in decomposition_details:
            original_task = detail.get('original_task', '')
            # decomposed_tasks_info에 상세 정보 추가
            for info in decomposed_tasks_info:
                if info.get('original_task') == original_task:
                    info['decomposed'] = detail.get('decomposed', {})
                    break
        
        return {
            "schedule": best_schedule.get('schedule', []) if best_schedule else [],
            "agent_reasoning": {
                "reflection": reflection,
                "ranking": ranking,
                "decomposition_applied": ranking.get('needs_decomposition', False),
                "decomposed_tasks_info": decomposed_tasks_info,
                "iterations": iterations,
                "best_iteration": best_schedule.get('iteration', 1) if best_schedule else 1,
                "meta_review": final_meta_review
            }
        }
    
    def _reflect_on_tasks(self, tasks: str, profile: Dict) -> Dict:
        """
        Step 1: Reflection - 작업 분석 및 복잡도 평가
        """
        prompt = f"""
        당신은 스케줄링 전문가입니다. 다음 작업들을 분석하세요.
        
        [작업 목록]
        {tasks}
        
        [사용자 프로필]
        역할: {profile.get('role', 'N/A')}
        목표: {profile.get('current_okr', 'N/A')}
        
        [분석 과제]
        1. 각 작업의 복잡도 평가 (high/medium/low)
        2. 예상 소요 시간 (분 단위)
        3. ADHD 사용자에게 어려울 수 있는 작업 식별
        4. 작업 분해가 필요한지 판단 (복잡하거나 큰 작업인 경우)
        
        [출력 형식]
        {{
            "tasks_analysis": [
                {{
                    "task": "작업 내용",
                    "complexity": "high|medium|low",
                    "estimated_time": 120,
                    "adhd_difficulty": "high|medium|low",
                    "needs_decomposition": true/false,
                    "decomposition_reason": "분해가 필요한 이유 (없으면 빈 문자열)"
                }}
            ],
            "overall_complexity": "high|medium|low",
            "total_estimated_time": 240
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 작업 분석 전문가입니다. JSON만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            # 오류 시 기본값 반환
            return {
                "tasks_analysis": [],
                "overall_complexity": "medium",
                "total_estimated_time": 0
            }
    
    def _rank_tasks(self, reflection: Dict) -> Dict:
        """
        Step 2: Ranking - 작업 우선순위 및 분해 필요성 판단
        """
        tasks_analysis = reflection.get('tasks_analysis', [])
        
        # 복잡한 작업 식별
        complex_tasks = [
            task for task in tasks_analysis 
            if task.get('complexity') == 'high' or task.get('needs_decomposition', False)
        ]
        
        needs_decomposition = len(complex_tasks) > 0
        
        # 분해된 작업 정보 수집
        decomposed_tasks_info = []
        for task in complex_tasks:
            if task.get('needs_decomposition'):
                decomposed_tasks_info.append({
                    "original_task": task.get('task', ''),
                    "reason": task.get('decomposition_reason', '복잡한 작업')
                })
        
        return {
            "needs_decomposition": needs_decomposition,
            "complex_tasks": complex_tasks,
            "decomposed_tasks_info": decomposed_tasks_info,
            "priority_order": sorted(
                tasks_analysis,
                key=lambda x: (
                    {'high': 3, 'medium': 2, 'low': 1}.get(x.get('complexity', 'low'), 1),
                    x.get('estimated_time', 0)
                ),
                reverse=True
            )
        }
    
    def _generate_schedule_input(self,
                                original_tasks: str,
                                reflection: Dict,
                                ranking: Dict,
                                profile: Dict) -> Tuple[str, List[Dict]]:
        """
        Step 3: Generation - 필요시 분해하여 최종 작업 목록 생성
        
        Returns:
            (processed_tasks, decomposition_details)
        """
        if not ranking.get('needs_decomposition'):
            return original_tasks, []
        
        # 복잡한 작업들을 분해
        decomposed_tasks_list = []
        decomposition_details = []
        tasks_lines = original_tasks.split('\n')
        
        for task_line in tasks_lines:
            task_text = task_line.strip()
            if not task_line.strip() or task_line.strip().startswith('예시)'):
                decomposed_tasks_list.append(task_line)
                continue
            
            # 복잡한 작업인지 확인
            task_clean = task_text.replace('-', '').replace('•', '').strip()
            
            # 복잡한 작업 목록에서 매칭
            is_complex = False
            complex_task_info = None
            for complex_task in ranking.get('complex_tasks', []):
                complex_task_text = complex_task.get('task', '').strip()
                if task_clean in complex_task_text or complex_task_text in task_clean:
                    is_complex = complex_task.get('needs_decomposition', False)
                    complex_task_info = complex_task
                    break
            
            if is_complex and complex_task_info:
                # 고급 분해 수행
                try:
                    decomposed = self.decomposer.decompose_with_cot(
                        task_clean,
                        user_profile=profile,
                        context="스케줄링을 위한 작업 분해"
                    )
                    
                    # 분해된 작업을 포맷팅
                    decomposed_text = f"- {task_clean} (분해됨):\n"
                    for item in decomposed.get('decomposed_tasks', []):
                        difficulty_emoji = {
                            "쉬움": "🟢", 
                            "보통": "🟡", 
                            "어려움": "🔴"
                        }.get(item.get('difficulty', '보통'), "🟡")
                        quick_win = "⚡" if item.get('adhd_optimizations', {}).get('quick_wins') else ""
                        decomposed_text += f"  - {item.get('step', '?')}. {item.get('task', 'N/A')} ({item.get('duration', 0)}분) {difficulty_emoji} {quick_win}\n"
                    
                    decomposed_tasks_list.append(decomposed_text.strip())
                    
                    # 분해 상세 정보 저장
                    decomposition_details.append({
                        "original_task": task_clean,
                        "decomposed": decomposed,
                        "decomposition_reason": complex_task_info.get('decomposition_reason', '')
                    })
                except Exception as e:
                    # 분해 실패 시 원본 사용
                    decomposed_tasks_list.append(task_line)
            else:
                decomposed_tasks_list.append(task_line)
        
        return '\n'.join(decomposed_tasks_list), decomposition_details
    
    def _generate_schedule(self,
                          processed_tasks: str,
                          profile: Dict,
                          existing_events: str,
                          date,
                          preset: str) -> Dict:
        """
        스케줄 생성
        """
        prompt = ai_scheduler.build_llm_prompt(
            profile,
            processed_tasks,
            existing_events,
            date,
            preset=preset
        )
        
        response = ai_scheduler.get_ai_schedule_openai(prompt, self.api_key)
        return json.loads(response)
    
    def _check_proximity(self, schedule: List[Dict], existing_events: str) -> Dict:
        """
        Step 5: Proximity - 기존 일정과의 충돌 검사
        """
        overlaps = validation.check_schedule_overlaps(schedule)
        
        return {
            "has_conflicts": len(overlaps) > 0,
            "conflict_count": len(overlaps),
            "conflicts": overlaps
        }
    
    def _meta_review(self,
                    schedule_result: Dict,
                    proximity_check: Dict,
                    reflection: Dict,
                    ranking: Dict) -> Dict:
        """
        Step 6: Meta-review - 최종 품질 평가 및 개선 제안
        """
        schedule = schedule_result.get('schedule', [])
        
        # 품질 점수 계산
        quality_score = 1.0
        
        # 충돌 감점
        if proximity_check.get('has_conflicts'):
            quality_score -= 0.2
        
        # 작업 완성도 체크
        if not schedule:
            quality_score = 0.0
        
        # 시간 분배 균형 체크
        total_time = 0
        for item in schedule:
            try:
                start_dt = datetime.datetime.fromisoformat(item.get('start_time', ''))
                end_dt = datetime.datetime.fromisoformat(item.get('end_time', ''))
                total_time += (end_dt - start_dt).total_seconds() / 60
            except:
                pass
        
        if total_time < 300:  # 5시간 미만
            quality_score -= 0.1
        
        issues = []
        if proximity_check.get('has_conflicts'):
            issues.append(f"{proximity_check.get('conflict_count')}개의 일정 충돌 발견")
        
        if not schedule:
            issues.append("스케줄이 생성되지 않음")
        
        suggested_improvements = []
        if quality_score < 0.8:
            if proximity_check.get('has_conflicts'):
                suggested_improvements.append("일정 충돌 해결 필요")
            if total_time < 300:
                suggested_improvements.append("더 많은 작업 배정 고려")
        
        return {
            "quality_score": max(0.0, min(1.0, quality_score)),
            "issues": issues,
            "suggested_improvements": suggested_improvements,
            "total_tasks": len(schedule),
            "total_time_minutes": int(total_time)
        }

