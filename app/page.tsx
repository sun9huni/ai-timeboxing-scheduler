"use client";

import { useState, useCallback } from "react";
import {
  Sparkles,
  Download,
  CheckCircle2,
  Loader2,
  AlertCircle,
  RotateCcw,
  CalendarCheck,
} from "lucide-react";
import ProfileSidebar from "@/components/ProfileSidebar";
import CalendarConnect from "@/components/CalendarConnect";
import TaskInput from "@/components/TaskInput";
import ScheduleTimeline from "@/components/ScheduleTimeline";
import { generateSchedule, syncToCalendar } from "@/lib/api";
import type { Profile, ScheduleItem, ScheduleResponse } from "@/lib/types";
import { DEFAULT_PROFILE } from "@/lib/types";

// Today as YYYY-MM-DD
function today() {
  return new Date().toISOString().split("T")[0];
}

type Step = 1 | 2 | 3 | 4 | 5;

export default function HomePage() {
  // State
  const [apiKey, setApiKey] = useState("");
  const [profile, setProfile] = useState<Profile>(DEFAULT_PROFILE);
  const [preset, setPreset] = useState("균형잡힌");
  const [selectedDate, setSelectedDate] = useState(today());
  const [tasks, setTasks] = useState("");
  const [calendarConnected, setCalendarConnected] = useState(false);

  const [generating, setGenerating] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState<ScheduleResponse | null>(null);
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [error, setError] = useState("");
  const [syncDone, setSyncDone] = useState(false);

  // Current wizard step
  const currentStep: Step =
    !calendarConnected ? 1
    : !tasks.trim() ? 3
    : !schedule.length ? 4
    : 5;

  const handleGenerate = useCallback(async () => {
    if (!apiKey) {
      setError("OpenAI API 키를 입력해주세요.");
      return;
    }
    if (!tasks.trim()) {
      setError("할 일을 입력해주세요.");
      return;
    }

    setError("");
    setGenerating(true);
    setResult(null);
    setSchedule([]);
    setSyncDone(false);

    const existingEventsEl = document.getElementById("existing-events") as HTMLInputElement | null;
    const existingEvents = existingEventsEl?.value || "없음";

    try {
      const res = await generateSchedule({
        tasks,
        profile,
        existing_events: existingEvents,
        date: selectedDate,
        preset,
        api_key: apiKey,
        max_iterations: 1,
      });
      setResult(res);
      setSchedule(res.schedule);
    } catch (e) {
      setError(e instanceof Error ? e.message : "스케줄 생성 중 오류가 발생했습니다.");
    } finally {
      setGenerating(false);
    }
  }, [apiKey, tasks, profile, selectedDate, preset]);

  const handleSync = async () => {
    if (!calendarConnected) {
      alert("Google Calendar를 먼저 연결해주세요.");
      return;
    }
    setSyncing(true);
    try {
      const res = await syncToCalendar(schedule);
      if (res.errors.length > 0) {
        alert(`${res.created}개 저장 완료. 오류: ${res.errors.join(", ")}`);
      } else {
        setSyncDone(true);
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : "저장 중 오류가 발생했습니다.");
    } finally {
      setSyncing(false);
    }
  };

  const handleExport = () => {
    const data = JSON.stringify(schedule, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `schedule-${selectedDate}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const stepLabel = (n: Step, title: string) => {
    const done = currentStep > n;
    const active = currentStep === n;
    return (
      <div className={`flex items-center gap-2 ${active ? "opacity-100" : done ? "opacity-70" : "opacity-40"}`}>
        {done ? (
          <span className="step-badge-done"><CheckCircle2 size={14} /></span>
        ) : active ? (
          <span className="step-badge">{n}</span>
        ) : (
          <span className="step-badge-pending">{n}</span>
        )}
        <span className={`text-sm font-semibold ${active ? "text-white" : "text-gray-400"}`}>{title}</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-surface-dark">
      {/* Header */}
      <header className="border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl bg-surface-dark/80">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
              style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}
            >
              🤖
            </div>
            <div>
              <h1 className="text-base font-bold text-white">AI 타임박싱 스케줄러</h1>
              <p className="text-xs text-gray-400 hidden sm:block">
                AI가 우선순위를 정해 Google 캘린더에 자동으로 등록합니다
              </p>
            </div>
          </div>

          {/* Step progress */}
          <div className="hidden md:flex items-center gap-1.5">
            {([1, 2, 3, 4, 5] as Step[]).map((s) => (
              <div
                key={s}
                className={`w-2 h-2 rounded-full transition-all ${
                  currentStep >= s ? "bg-brand-500" : "bg-white/20"
                }`}
              />
            ))}
            <span className="text-xs text-gray-400 ml-2">Step {currentStep}/5</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <ProfileSidebar
            profile={profile}
            onChange={setProfile}
            apiKey={apiKey}
            onApiKeyChange={setApiKey}
            preset={preset}
            onPresetChange={setPreset}
          />

          {/* Main Content */}
          <div className="flex-1 space-y-4 min-w-0">

            {/* Step 1: Calendar */}
            <div className="card">
              <div className="mb-4">{stepLabel(1, "Google Calendar 연동")}</div>
              <CalendarConnect onConnect={setCalendarConnected} />
            </div>

            {/* Step 2 & 3: Date + Tasks */}
            <div className="card">
              <div className="mb-4">{stepLabel(3, "할 일 입력")}</div>
              <TaskInput
                tasks={tasks}
                onTasksChange={setTasks}
                selectedDate={selectedDate}
                onDateChange={setSelectedDate}
                calendarConnected={calendarConnected}
              />
            </div>

            {/* Step 4: Generate */}
            <div className="card">
              <div className="mb-4">{stepLabel(4, "AI 스케줄 생성")}</div>

              {error && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/30 mb-4 text-sm text-red-400">
                  <AlertCircle size={15} />
                  {error}
                </div>
              )}

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="btn-primary flex items-center gap-2"
                >
                  {generating ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      AI 분석 중... (최대 60초)
                    </>
                  ) : (
                    <>
                      <Sparkles size={16} />
                      AI 스케줄 생성하기
                    </>
                  )}
                </button>

                {schedule.length > 0 && (
                  <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <RotateCcw size={14} />
                    다시 생성
                  </button>
                )}
              </div>

              {/* Generation info */}
              {result && (
                <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="rounded-lg bg-surface-card border border-white/10 p-3">
                    <p className="text-xs text-gray-400">일정 수</p>
                    <p className="text-lg font-bold text-white">{schedule.length}</p>
                  </div>
                  <div className="rounded-lg bg-surface-card border border-white/10 p-3">
                    <p className="text-xs text-gray-400">품질 점수</p>
                    <p className="text-lg font-bold text-brand-400">
                      {Math.round((result.agent_reasoning.meta_review.quality_score ?? 0) * 100)}%
                    </p>
                  </div>
                  <div className="rounded-lg bg-surface-card border border-white/10 p-3">
                    <p className="text-xs text-gray-400">총 시간</p>
                    <p className="text-lg font-bold text-green-400">
                      {Math.round((result.agent_reasoning.meta_review.total_time_minutes ?? 0) / 60)}h
                    </p>
                  </div>
                  <div className="rounded-lg bg-surface-card border border-white/10 p-3">
                    <p className="text-xs text-gray-400">작업 분해</p>
                    <p className="text-lg font-bold text-purple-400">
                      {result.agent_reasoning.decomposition_applied ? "✅" : "—"}
                    </p>
                  </div>
                </div>
              )}

              {/* Warnings */}
              {result?.validation_errors && result.validation_errors.length > 0 && (
                <div className="mt-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                  <p className="text-xs font-semibold text-yellow-400 mb-1">⚠️ 경고</p>
                  {result.validation_errors.slice(0, 3).map((e, i) => (
                    <p key={i} className="text-xs text-yellow-300">{e}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Step 5: View & Save */}
            {schedule.length > 0 && (
              <div className="card animate-fade-in">
                <div className="mb-4">{stepLabel(5, "스케줄 확인 및 저장")}</div>

                <ScheduleTimeline
                  schedule={schedule}
                  onDelete={(idx) => setSchedule((prev) => prev.filter((_, i) => i !== idx))}
                />

                {/* Actions */}
                <div className="flex flex-wrap gap-3 mt-5 pt-5 border-t border-white/10">
                  {syncDone ? (
                    <div className="flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold text-green-400 bg-green-500/10 border border-green-500/30">
                      <CheckCircle2 size={16} />
                      Google Calendar에 저장 완료!
                    </div>
                  ) : (
                    <button
                      onClick={handleSync}
                      disabled={syncing || !calendarConnected}
                      className="btn-primary flex items-center gap-2"
                    >
                      {syncing ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          저장 중...
                        </>
                      ) : (
                        <>
                          <CalendarCheck size={16} />
                          Google Calendar에 저장
                        </>
                      )}
                    </button>
                  )}

                  <button
                    onClick={handleExport}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Download size={14} />
                    JSON 내보내기
                  </button>

                  <button
                    onClick={() => { setSchedule([]); setResult(null); setSyncDone(false); }}
                    className="btn-secondary flex items-center gap-2 text-red-400 hover:text-red-300"
                  >
                    초기화
                  </button>
                </div>

                {!calendarConnected && (
                  <p className="text-xs text-yellow-400 mt-2 flex items-center gap-1">
                    <AlertCircle size={11} />
                    Google Calendar 연결 후 저장할 수 있습니다
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
