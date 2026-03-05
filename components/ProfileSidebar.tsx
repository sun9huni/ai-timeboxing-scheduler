"use client";

import { useState } from "react";
import { User, ChevronDown, ChevronUp, Save, Trash2 } from "lucide-react";
import type { Profile } from "@/lib/types";
import { DEFAULT_PROFILE } from "@/lib/types";
import { clsx } from "clsx";

const TEMPLATES: Record<string, Profile> = {
  "프로덕트 매니저": {
    role: "프로덕트 매니저 (PM)",
    current_okr: "3분기 '신규 기능 X' 런칭",
    deep_work_time: "오전 10:00 - 12:00",
    meeting_preference: "오후 1시 이후",
    admin_work_time: "오후 4시 이후",
  },
  "개발자": {
    role: "소프트웨어 개발자",
    current_okr: "코드 품질 향상 및 기술 부채 감소",
    deep_work_time: "오전 9:00 - 12:00",
    meeting_preference: "오후 2시 이후",
    admin_work_time: "오후 5시 이후",
  },
  "디자이너": {
    role: "UX/UI 디자이너",
    current_okr: "사용자 경험 개선 프로젝트",
    deep_work_time: "오전 10:00 - 12:00",
    meeting_preference: "오후 1시 이후",
    admin_work_time: "오후 3시 이후",
  },
  "마케터": {
    role: "마케팅 매니저",
    current_okr: "Q3 마케팅 캠페인 성과 달성",
    deep_work_time: "오전 9:00 - 11:00",
    meeting_preference: "오전 11시 이후",
    admin_work_time: "오후 4시 이후",
  },
  "프리랜서": {
    role: "프리랜서",
    current_okr: "고객 만족도 향상",
    deep_work_time: "오전 9:00 - 12:00",
    meeting_preference: "오후 2시 이후",
    admin_work_time: "오후 5시 이후",
  },
};

interface Props {
  profile: Profile;
  onChange: (profile: Profile) => void;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  preset: string;
  onPresetChange: (preset: string) => void;
}

const PRESETS = [
  { key: "균형잡힌", label: "균형잡힌", desc: "일과 휴식의 균형" },
  { key: "엄격한", label: "엄격한", desc: "집중 업무 최대화" },
  { key: "유연한", label: "유연한", desc: "여유 있게 계획" },
  { key: "긴급 우선", label: "긴급 우선", desc: "마감일 기반 배치" },
];

export default function ProfileSidebar({
  profile,
  onChange,
  apiKey,
  onApiKeyChange,
  preset,
  onPresetChange,
}: Props) {
  const [profileOpen, setProfileOpen] = useState(true);
  const [savedProfiles, setSavedProfiles] = useState<Record<string, Profile>>(
    () => {
      try {
        return JSON.parse(localStorage.getItem("profiles") || "{}");
      } catch {
        return {};
      }
    }
  );
  const [saveName, setSaveName] = useState("");

  const handleSave = () => {
    if (!saveName.trim()) return;
    const updated = { ...savedProfiles, [saveName]: profile };
    setSavedProfiles(updated);
    localStorage.setItem("profiles", JSON.stringify(updated));
    setSaveName("");
  };

  const handleDelete = (name: string) => {
    const updated = { ...savedProfiles };
    delete updated[name];
    setSavedProfiles(updated);
    localStorage.setItem("profiles", JSON.stringify(updated));
  };

  const field = (
    label: string,
    key: keyof Profile,
    placeholder = ""
  ) => (
    <div className="mb-3">
      <label className="block text-xs text-gray-400 mb-1">{label}</label>
      <input
        className="input-field text-sm"
        value={profile[key]}
        placeholder={placeholder}
        onChange={(e) => onChange({ ...profile, [key]: e.target.value })}
      />
    </div>
  );

  return (
    <aside className="w-full lg:w-72 shrink-0 space-y-4">
      {/* API Key */}
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 rounded-full bg-brand-500" />
          <span className="text-sm font-semibold text-white">🔑 OpenAI API Key</span>
        </div>
        <input
          type="password"
          className="input-field text-sm"
          placeholder="sk-..."
          value={apiKey}
          onChange={(e) => onApiKeyChange(e.target.value)}
        />
        {apiKey && (
          <p className="text-xs text-green-400 mt-1">
            ✅ {apiKey.slice(0, 8)}...{apiKey.slice(-4)}
          </p>
        )}
      </div>

      {/* Preset */}
      <div className="card">
        <p className="text-sm font-semibold mb-3 text-white">🎯 스케줄링 스타일</p>
        <div className="grid grid-cols-2 gap-2">
          {PRESETS.map((p) => (
            <button
              key={p.key}
              onClick={() => onPresetChange(p.key)}
              className={clsx(
                "rounded-lg p-2.5 text-left transition-all text-xs border",
                preset === p.key
                  ? "border-brand-500 bg-brand-500/20 text-white"
                  : "border-white/10 bg-white/5 text-gray-400 hover:border-white/20"
              )}
            >
              <div className="font-medium">{p.label}</div>
              <div className="text-gray-500 mt-0.5">{p.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Profile */}
      <div className="card">
        <button
          className="flex items-center justify-between w-full mb-3"
          onClick={() => setProfileOpen(!profileOpen)}
        >
          <div className="flex items-center gap-2">
            <User size={14} className="text-brand-500" />
            <span className="text-sm font-semibold text-white">👤 사용자 프로필</span>
          </div>
          {profileOpen ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
        </button>

        {profileOpen && (
          <div className="animate-fade-in">
            {/* Templates */}
            <div className="mb-3">
              <label className="block text-xs text-gray-400 mb-1">템플릿</label>
              <select
                className="input-field text-sm"
                onChange={(e) => {
                  if (e.target.value && TEMPLATES[e.target.value]) {
                    onChange(TEMPLATES[e.target.value]);
                  }
                }}
                defaultValue=""
              >
                <option value="">템플릿 선택...</option>
                {Object.keys(TEMPLATES).map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </div>

            {/* Saved profiles */}
            {Object.keys(savedProfiles).length > 0 && (
              <div className="mb-3">
                <label className="block text-xs text-gray-400 mb-1">저장된 프로필</label>
                {Object.keys(savedProfiles).map((name) => (
                  <div key={name} className="flex items-center gap-1 mb-1">
                    <button
                      onClick={() => onChange(savedProfiles[name])}
                      className="flex-1 text-left text-xs bg-white/5 hover:bg-white/10 rounded px-2 py-1.5 text-gray-300 transition-colors"
                    >
                      📌 {name}
                    </button>
                    <button
                      onClick={() => handleDelete(name)}
                      className="p-1.5 hover:bg-red-500/20 rounded text-red-400 transition-colors"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {field("역할", "role", "예: 프로덕트 매니저")}
            {field("핵심 목표 (OKR)", "current_okr", "예: Q3 제품 런칭")}
            {field("집중 업무 시간", "deep_work_time", "예: 오전 10:00 - 12:00")}
            {field("회의 선호 시간", "meeting_preference", "예: 오후 1시 이후")}
            {field("행정 업무 시간", "admin_work_time", "예: 오후 4시 이후")}

            {/* Save profile */}
            <div className="flex gap-2 mt-2">
              <input
                className="input-field text-xs flex-1"
                placeholder="프로필 이름..."
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSave()}
              />
              <button
                onClick={handleSave}
                className="btn-secondary p-2 shrink-0"
                title="저장"
              >
                <Save size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
