"""
Google Co-Scientist 스타일 스케줄링 Agent
자동으로 작업 복잡도를 판단하고 필요시 고급 분해를 사용
"""
import json
import datetime
import sys
import os
from typing import Dict, List, Tuple

from openai import OpenAI

# 같은 lib 디렉토리에서 import
sys.path.insert(0, os.path.dirname(__file__))
import task_decomposer
import ai_scheduler
import validation


class SchedulingAgent:
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
                      max_iterations: int = 1) -> Dict:
        """
        6단계 파이프라인으로 스케줄 생성
        Vercel 타임아웃 대응: 기본 max_iterations=1
        """
        reflection = self._reflect_on_tasks(tasks, profile)
        ranking = self._rank_tasks(reflection)

        processed_tasks, decomposition_details = self._generate_schedule_input(
            tasks, reflection, ranking, profile
        )

        best_schedule = None
        iterations = []

        for iteration in range(max_iterations):
            schedule_result = self._generate_schedule(
                processed_tasks, profile, existing_events, date, preset
            )
            proximity_check = self._check_proximity(
                schedule_result.get('schedule', []), existing_events
            )
            meta_review = self._meta_review(
                schedule_result, proximity_check, reflection, ranking
            )

            iterations.append({
                "iteration": iteration + 1,
                "schedule": schedule_result.get('schedule', []),
                "quality_score": meta_review.get('quality_score', 0),
                "issues": meta_review.get('issues', []),
                "improvements": meta_review.get('suggested_improvements', [])
            })

            if best_schedule is None or meta_review.get('quality_score', 0) > best_schedule.get('quality_score', 0):
                best_schedule = {
                    "schedule": schedule_result.get('schedule', []),
                    "quality_score": meta_review.get('quality_score', 0),
                    "iteration": iteration + 1
                }

            if meta_review.get('quality_score', 0) >= 0.9:
                break

        final_meta_review = iterations[-1] if iterations else {}
        decomposed_tasks_info = ranking.get('decomposed_tasks_info', [])

        for detail in decomposition_details:
            original_task = detail.get('original_task', '')
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
        prompt = f"""
        다음 작업들을 분석하세요.
        
        [작업 목록]
        {tasks}
        
        [사용자 프로필]
        역할: {profile.get('role', 'N/A')}
        목표: {profile.get('current_okr', 'N/A')}
        
        [출력 형식]
        {{
            "tasks_analysis": [
                {{
                    "task": "작업 내용",
                    "complexity": "high|medium|low",
                    "estimated_time": 120,
                    "adhd_difficulty": "high|medium|low",
                    "needs_decomposition": true,
                    "decomposition_reason": "이유"
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
                    {"role": "system", "content": "작업 분석 전문가입니다. JSON만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"tasks_analysis": [], "overall_complexity": "medium", "total_estimated_time": 0}

    def _rank_tasks(self, reflection: Dict) -> Dict:
        tasks_analysis = reflection.get('tasks_analysis', [])
        complex_tasks = [
            t for t in tasks_analysis
            if t.get('complexity') == 'high' or t.get('needs_decomposition', False)
        ]
        needs_decomposition = len(complex_tasks) > 0
        decomposed_tasks_info = [
            {"original_task": t.get('task', ''), "reason": t.get('decomposition_reason', '복잡한 작업')}
            for t in complex_tasks if t.get('needs_decomposition')
        ]
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
        if not ranking.get('needs_decomposition'):
            return original_tasks, []

        decomposed_tasks_list = []
        decomposition_details = []

        for task_line in original_tasks.split('\n'):
            task_text = task_line.strip()
            if not task_text or task_text.startswith('예시)'):
                decomposed_tasks_list.append(task_line)
                continue

            task_clean = task_text.replace('-', '').replace('•', '').strip()
            is_complex = False
            complex_task_info = None

            for complex_task in ranking.get('complex_tasks', []):
                complex_task_text = complex_task.get('task', '').strip()
                if task_clean in complex_task_text or complex_task_text in task_clean:
                    is_complex = complex_task.get('needs_decomposition', False)
                    complex_task_info = complex_task
                    break

            if is_complex and complex_task_info:
                try:
                    decomposed = self.decomposer.decompose_with_cot(
                        task_clean, user_profile=profile, context="스케줄링을 위한 작업 분해"
                    )
                    decomposed_text = f"- {task_clean} (분해됨):\n"
                    for item in decomposed.get('decomposed_tasks', []):
                        decomposed_text += f"  - {item.get('step', '?')}. {item.get('task', 'N/A')} ({item.get('duration', 0)}분)\n"
                    decomposed_tasks_list.append(decomposed_text.strip())
                    decomposition_details.append({
                        "original_task": task_clean,
                        "decomposed": decomposed,
                        "decomposition_reason": complex_task_info.get('decomposition_reason', '')
                    })
                except Exception:
                    decomposed_tasks_list.append(task_line)
            else:
                decomposed_tasks_list.append(task_line)

        return '\n'.join(decomposed_tasks_list), decomposition_details

    def _generate_schedule(self, processed_tasks: str, profile: Dict,
                            existing_events: str, date, preset: str) -> Dict:
        prompt = ai_scheduler.build_llm_prompt(
            profile, processed_tasks, existing_events, date, preset=preset
        )
        response = ai_scheduler.get_ai_schedule_openai(prompt, self.api_key)
        return json.loads(response)

    def _check_proximity(self, schedule: List[Dict], existing_events: str) -> Dict:
        overlaps = validation.check_schedule_overlaps(schedule)
        return {
            "has_conflicts": len(overlaps) > 0,
            "conflict_count": len(overlaps),
            "conflicts": overlaps
        }

    def _meta_review(self, schedule_result: Dict, proximity_check: Dict,
                     reflection: Dict, ranking: Dict) -> Dict:
        schedule = schedule_result.get('schedule', [])
        quality_score = 1.0

        if proximity_check.get('has_conflicts'):
            quality_score -= 0.2
        if not schedule:
            quality_score = 0.0

        total_time = 0
        for item in schedule:
            try:
                start_dt = datetime.datetime.fromisoformat(item.get('start_time', ''))
                end_dt = datetime.datetime.fromisoformat(item.get('end_time', ''))
                total_time += (end_dt - start_dt).total_seconds() / 60
            except Exception:
                pass

        if total_time < 300:
            quality_score -= 0.1

        issues = []
        if proximity_check.get('has_conflicts'):
            issues.append(f"{proximity_check.get('conflict_count')}개의 일정 충돌 발견")
        if not schedule:
            issues.append("스케줄이 생성되지 않음")

        return {
            "quality_score": max(0.0, min(1.0, quality_score)),
            "issues": issues,
            "suggested_improvements": [],
            "total_tasks": len(schedule),
            "total_time_minutes": int(total_time)
        }
