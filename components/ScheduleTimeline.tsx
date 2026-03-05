"use client";

import { useMemo } from "react";
import { Trash2, Clock } from "lucide-react";
import type { ScheduleItem } from "@/lib/types";
import { formatTime, getDurationMinutes } from "@/lib/api";

interface Props {
  schedule: ScheduleItem[];
  onDelete: (index: number) => void;
}

const COLORS = [
  "from-blue-500/80 to-blue-600/80 border-blue-400/50",
  "from-purple-500/80 to-purple-600/80 border-purple-400/50",
  "from-indigo-500/80 to-indigo-600/80 border-indigo-400/50",
  "from-violet-500/80 to-violet-600/80 border-violet-400/50",
  "from-cyan-500/80 to-cyan-600/80 border-cyan-400/50",
  "from-teal-500/80 to-teal-600/80 border-teal-400/50",
];

const LUNCH_COLOR = "from-amber-500/80 to-orange-600/80 border-amber-400/50";

// 9:00 ~ 18:00 = 540분
const DAY_START = 9 * 60; // 540
const DAY_END = 18 * 60;   // 1080
const DAY_TOTAL = DAY_END - DAY_START; // 540

function getMinutes(isoString: string): number {
  const dt = new Date(isoString);
  return dt.getHours() * 60 + dt.getMinutes();
}

export default function ScheduleTimeline({ schedule, onDelete }: Props) {
  const sorted = useMemo(
    () => [...schedule].sort((a, b) =>
      new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    ),
    [schedule]
  );

  const hourMarkers = Array.from({ length: 10 }, (_, i) => i + 9); // 9 ~ 18

  return (
    <div className="space-y-6">
      {/* Visual Timeline */}
      <div className="rounded-xl bg-surface-card border border-white/10 p-5">
        <h3 className="text-sm font-semibold text-white mb-4">📊 타임라인</h3>

        {/* Hour markers */}
        <div className="relative">
          <div className="flex justify-between mb-1">
            {hourMarkers.map((h) => (
              <span key={h} className="text-xs text-gray-500 font-mono">
                {h.toString().padStart(2, "0")}
              </span>
            ))}
          </div>

          {/* Timeline bar */}
          <div className="relative h-14 bg-white/5 rounded-lg overflow-hidden border border-white/10">
            {sorted.map((item, idx) => {
              const startMin = getMinutes(item.start_time);
              const endMin = getMinutes(item.end_time);
              const left = ((startMin - DAY_START) / DAY_TOTAL) * 100;
              const width = ((endMin - startMin) / DAY_TOTAL) * 100;
              const isLunch = item.task_name.includes("점심");
              const colorClass = isLunch ? LUNCH_COLOR : COLORS[idx % COLORS.length];

              return (
                <div
                  key={idx}
                  className={`absolute top-1 bottom-1 rounded bg-gradient-to-r border ${colorClass} flex items-center justify-center overflow-hidden cursor-default transition-opacity hover:opacity-90`}
                  style={{ left: `${Math.max(0, left)}%`, width: `${Math.min(width, 100 - left)}%` }}
                  title={`${item.task_name} (${formatTime(item.start_time)} - ${formatTime(item.end_time)})`}
                >
                  {width > 8 && (
                    <span className="text-white text-xs font-medium truncate px-1">
                      {item.task_name.replace(/\[.*?\]\s*/, "")}
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Current time marker */}
          {(() => {
            const now = new Date();
            const nowMin = now.getHours() * 60 + now.getMinutes();
            if (nowMin >= DAY_START && nowMin <= DAY_END) {
              const pos = ((nowMin - DAY_START) / DAY_TOTAL) * 100;
              return (
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-red-400 z-10"
                  style={{ left: `${pos}%`, top: "24px", height: "56px" }}
                >
                  <div className="w-2 h-2 rounded-full bg-red-400 -ml-0.5 -mt-1" />
                </div>
              );
            }
            return null;
          })()}
        </div>
      </div>

      {/* Schedule Table */}
      <div className="space-y-2">
        {sorted.map((item, idx) => {
          const duration = getDurationMinutes(item.start_time, item.end_time);
          const isLunch = item.task_name.includes("점심");
          const colorClass = isLunch ? LUNCH_COLOR : COLORS[idx % COLORS.length];
          const originalIdx = schedule.indexOf(item);

          return (
            <div
              key={idx}
              className="group flex items-center gap-3 p-3.5 rounded-xl bg-surface border border-white/10 hover:border-white/20 transition-all animate-slide-up"
            >
              {/* Priority badge */}
              <div
                className={`w-1.5 h-10 rounded-full bg-gradient-to-b ${colorClass.split(" ").slice(0, 2).join(" ")} shrink-0`}
              />

              {/* Time */}
              <div className="text-center shrink-0 w-20">
                <p className="text-xs font-mono text-brand-400 font-semibold">
                  {formatTime(item.start_time)}
                </p>
                <p className="text-xs text-gray-500">―</p>
                <p className="text-xs font-mono text-gray-400">
                  {formatTime(item.end_time)}
                </p>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{item.task_name}</p>
                {item.notes && (
                  <p className="text-xs text-gray-400 mt-0.5 truncate">{item.notes}</p>
                )}
              </div>

              {/* Duration */}
              <div className="flex items-center gap-1 text-xs text-gray-500 shrink-0">
                <Clock size={11} />
                <span>{duration}분</span>
              </div>

              {/* Priority */}
              {item.priority && (
                <span className="text-xs bg-brand-500/20 text-brand-400 px-2 py-0.5 rounded-full shrink-0">
                  P{item.priority}
                </span>
              )}

              {/* Delete */}
              <button
                onClick={() => onDelete(originalIdx)}
                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 rounded-lg text-red-400 transition-all shrink-0"
              >
                <Trash2 size={13} />
              </button>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl bg-surface border border-white/10 p-3 text-center">
          <p className="text-2xl font-bold text-white">{schedule.length}</p>
          <p className="text-xs text-gray-400 mt-0.5">일정 수</p>
        </div>
        <div className="rounded-xl bg-surface border border-white/10 p-3 text-center">
          <p className="text-2xl font-bold text-brand-400">
            {Math.round(
              schedule.reduce(
                (acc, item) => acc + getDurationMinutes(item.start_time, item.end_time),
                0
              ) / 60
            )}h
          </p>
          <p className="text-xs text-gray-400 mt-0.5">총 시간</p>
        </div>
        <div className="rounded-xl bg-surface border border-white/10 p-3 text-center">
          <p className="text-2xl font-bold text-green-400">
            {Math.round(
              schedule.reduce(
                (acc, item) => acc + getDurationMinutes(item.start_time, item.end_time),
                0
              ) / 60 / 9 * 100
            )}%
          </p>
          <p className="text-xs text-gray-400 mt-0.5">일과 채움율</p>
        </div>
      </div>
    </div>
  );
}
