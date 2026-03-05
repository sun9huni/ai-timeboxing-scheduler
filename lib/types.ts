export interface Profile {
  role: string;
  current_okr: string;
  deep_work_time: string;
  meeting_preference: string;
  admin_work_time: string;
}

export interface ScheduleItem {
  task_name: string;
  start_time: string;
  end_time: string;
  priority: number;
  notes: string;
}

export interface CalendarEvent {
  time: string;
  title: string;
  id: string;
}

export interface ScheduleResponse {
  schedule: ScheduleItem[];
  agent_reasoning: {
    reflection: Record<string, unknown>;
    ranking: Record<string, unknown>;
    decomposition_applied: boolean;
    iterations: Array<{
      iteration: number;
      quality_score: number;
      issues: string[];
    }>;
    meta_review: {
      total_tasks: number;
      total_time_minutes: number;
      quality_score: number;
      issues: string[];
    };
  };
  validation_errors: string[];
  overlap_count: number;
}

export interface ScheduleRequest {
  tasks: string;
  profile: Profile;
  existing_events: string;
  date: string;
  preset: string;
  api_key: string;
  max_iterations?: number;
}

export type SchedulingPreset = "균형잡힌" | "엄격한" | "유연한" | "긴급 우선";

export const DEFAULT_PROFILE: Profile = {
  role: "프로덕트 매니저 (PM)",
  current_okr: "3분기 '신규 기능 X' 런칭",
  deep_work_time: "오전 10:00 - 12:00",
  meeting_preference: "오후 1시 이후",
  admin_work_time: "오후 4시 이후",
};

export const PRESET_LABELS: Record<string, string> = {
  "균형잡힌": "균형잡힌 스케줄러",
  "엄격한": "엄격한 스케줄러",
  "유연한": "유연한 스케줄러",
  "긴급 우선": "긴급 우선 스케줄러",
};
