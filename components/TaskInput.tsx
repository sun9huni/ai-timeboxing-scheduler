"use client";

import { useState, useRef } from "react";
import { Mic, MicOff, CalendarDays, Loader2 } from "lucide-react";
import { getCalendarEvents } from "@/lib/api";
import type { CalendarEvent } from "@/lib/types";

interface Props {
  tasks: string;
  onTasksChange: (v: string) => void;
  selectedDate: string;
  onDateChange: (v: string) => void;
  calendarConnected: boolean;
}

export default function TaskInput({
  tasks,
  onTasksChange,
  selectedDate,
  onDateChange,
  calendarConnected,
}: Props) {
  const [isRecording, setIsRecording] = useState(false);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loadingEvents, setLoadingEvents] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);

  const toggleVoice = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    const SpeechRecognition = w.webkitSpeechRecognition || w.SpeechRecognition;
    if (!SpeechRecognition) {
      alert("이 브라우저는 음성 입력을 지원하지 않습니다. Chrome을 사용해주세요.");
      return;
    }

    if (isRecording && recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "ko-KR";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = (e: any) => {
      const transcript = Array.from(e.results)
        .map((r: any) => r[0].transcript)
        .join("\n");
      onTasksChange(tasks ? `${tasks}\n- ${transcript}` : `- ${transcript}`);
    };

    recognition.onend = () => setIsRecording(false);
    recognition.onerror = () => setIsRecording(false);

    recognition.start();
    recognitionRef.current = recognition;
    setIsRecording(true);
  };

  const loadEvents = async () => {
    if (!calendarConnected || !selectedDate) return;
    setLoadingEvents(true);
    try {
      const { events: evts } = await getCalendarEvents(selectedDate);
      setEvents(evts);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingEvents(false);
    }
  };

  const eventsToString = events.length
    ? events.map((e) => `- ${e.time} / ${e.title}`).join("\n")
    : "없음";

  return (
    <div className="space-y-4">
      {/* Date Picker */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <label className="block text-xs text-gray-400 mb-1.5">
            <CalendarDays size={12} className="inline mr-1" />
            날짜 선택
          </label>
          <input
            type="date"
            className="input-field"
            value={selectedDate}
            onChange={(e) => {
              onDateChange(e.target.value);
              setEvents([]);
            }}
          />
        </div>
        {calendarConnected && (
          <div className="mt-5">
            <button
              onClick={loadEvents}
              disabled={loadingEvents}
              className="btn-secondary flex items-center gap-2 text-sm py-3"
            >
              {loadingEvents ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <CalendarDays size={14} />
              )}
              기존 일정 불러오기
            </button>
          </div>
        )}
      </div>

      {/* Existing Events */}
      {events.length > 0 && (
        <div className="rounded-xl bg-surface-card border border-white/10 p-4 animate-fade-in">
          <p className="text-xs font-semibold text-brand-500 mb-2">
            📅 {selectedDate} 기존 일정
          </p>
          <div className="space-y-1">
            {events.map((ev, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-gray-300">
                <span className="text-brand-400 font-mono w-10 shrink-0">{ev.time}</span>
                <span>{ev.title}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Task Input */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="text-xs text-gray-400">
            ✏️ 오늘 완료해야 할 일 목록
          </label>
          <button
            onClick={toggleVoice}
            className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-all ${
              isRecording
                ? "bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse"
                : "bg-white/5 text-gray-400 hover:bg-white/10 border border-white/10"
            }`}
          >
            {isRecording ? (
              <>
                <MicOff size={12} />
                녹음 중지
              </>
            ) : (
              <>
                <Mic size={12} />
                음성 입력
              </>
            )}
          </button>
        </div>
        <textarea
          className="input-field resize-none leading-relaxed text-sm"
          rows={8}
          placeholder={`예시)\n- '신규 기능 X' 기획서 최종본 작성 (가장 중요함)\n- 개발팀 주간 싱크 미팅 (1시간)\n- A/B 테스트 결과 데이터 분석 (2시간)\n- 밀린 이메일 및 슬랙 답장하기`}
          value={tasks}
          onChange={(e) => onTasksChange(e.target.value)}
        />
        <p className="text-xs text-gray-500 mt-1">
          💡 AI Agent가 자동으로 복잡한 작업을 분해하고 최적의 순서를 결정합니다
        </p>
      </div>

      {/* Hidden events string for parent */}
      <input type="hidden" value={eventsToString} id="existing-events" />
    </div>
  );
}
