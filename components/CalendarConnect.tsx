"use client";

import { useState, useEffect } from "react";
import { Calendar, CheckCircle, XCircle, Loader2, Link } from "lucide-react";
import { getCalendarAuthUrl, getCalendarStatus, disconnectCalendar } from "@/lib/api";

interface Props {
  onConnect: (connected: boolean) => void;
}

export default function CalendarConnect({ onConnect }: Props) {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    // URL 파라미터 확인 (OAuth 콜백 후)
    const params = new URLSearchParams(window.location.search);
    if (params.get("calendar_connected") === "true") {
      setConnected(true);
      onConnect(true);
      // URL 파라미터 제거
      window.history.replaceState({}, "", window.location.pathname);
    } else if (params.get("calendar_error")) {
      console.error("Calendar error:", params.get("calendar_error"));
      window.history.replaceState({}, "", window.location.pathname);
    }
    checkStatus();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const checkStatus = async () => {
    try {
      const { connected: isConnected } = await getCalendarStatus();
      setConnected(isConnected);
      onConnect(isConnected);
    } catch {
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const { auth_url } = await getCalendarAuthUrl();
      window.location.href = auth_url;
    } catch (e) {
      console.error(e);
      setConnecting(false);
      alert("Google 인증 URL을 가져오지 못했습니다. GOOGLE_CLIENT_ID/SECRET 환경변수를 확인하세요.");
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectCalendar();
      setConnected(false);
      onConnect(false);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-xl bg-surface border border-white/10">
        <Loader2 size={18} className="animate-spin text-brand-500" />
        <span className="text-sm text-gray-400">연결 상태 확인 중...</span>
      </div>
    );
  }

  if (connected) {
    return (
      <div className="flex items-center justify-between p-4 rounded-xl bg-green-500/10 border border-green-500/30">
        <div className="flex items-center gap-3">
          <CheckCircle size={20} className="text-green-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-green-400">Google Calendar 연결됨</p>
            <p className="text-xs text-gray-400 mt-0.5">일정을 읽고 새 이벤트를 추가할 수 있습니다</p>
          </div>
        </div>
        <button
          onClick={handleDisconnect}
          className="text-xs text-red-400 hover:text-red-300 transition-colors flex items-center gap-1 px-3 py-1.5 rounded-lg hover:bg-red-500/10"
        >
          <XCircle size={12} />
          연결 해제
        </button>
      </div>
    );
  }

  return (
    <div className="p-5 rounded-xl bg-surface border border-white/10">
      <div className="flex items-start gap-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
          style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}
        >
          <Calendar size={22} className="text-white" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-white mb-1">Google Calendar 연동</h3>
          <p className="text-xs text-gray-400 mb-4 leading-relaxed">
            기존 일정을 불러오고, AI가 생성한 스케줄을 자동으로 등록합니다.
            처음 실행 시 Google 계정 인증이 필요합니다.
          </p>
          <button
            onClick={handleConnect}
            disabled={connecting}
            className="btn-primary flex items-center gap-2 text-sm px-5 py-2.5"
          >
            {connecting ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                연결 중...
              </>
            ) : (
              <>
                <Link size={15} />
                Google Calendar 연결하기
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
