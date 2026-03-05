import type {
  ScheduleRequest,
  ScheduleResponse,
  CalendarEvent,
  Profile,
} from "./types";

const API_BASE = "/api";

async function fetchAPI<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ─── Schedule ─────────────────────────────────────────────────────────────────

export async function generateSchedule(
  req: ScheduleRequest
): Promise<ScheduleResponse> {
  return fetchAPI<ScheduleResponse>("/schedule", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

// ─── Calendar ─────────────────────────────────────────────────────────────────

export async function getCalendarAuthUrl(): Promise<{
  auth_url: string;
  state: string;
}> {
  return fetchAPI("/calendar/auth");
}

export async function getCalendarStatus(): Promise<{ connected: boolean }> {
  return fetchAPI("/calendar/status");
}

export async function disconnectCalendar(): Promise<void> {
  await fetchAPI("/calendar/disconnect", { method: "POST" });
}

export async function getCalendarEvents(
  date: string
): Promise<{ events: CalendarEvent[]; date: string }> {
  return fetchAPI(`/calendar/events?date=${date}`);
}

export async function syncToCalendar(
  schedule: ScheduleResponse["schedule"],
  timezone = "Asia/Seoul"
): Promise<{ created: number; errors: string[] }> {
  return fetchAPI("/calendar/sync", {
    method: "POST",
    body: JSON.stringify({ schedule, timezone }),
  });
}

// ─── Profile Templates ────────────────────────────────────────────────────────

export async function getProfileTemplates(): Promise<{
  templates: Record<string, Profile>;
  names: string[];
}> {
  return fetchAPI("/profile/templates");
}

// ─── Utils ────────────────────────────────────────────────────────────────────

export function formatTime(isoString: string): string {
  try {
    const dt = new Date(isoString);
    return dt.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  } catch {
    return isoString;
  }
}

export function getDurationMinutes(start: string, end: string): number {
  try {
    return (new Date(end).getTime() - new Date(start).getTime()) / 60000;
  } catch {
    return 0;
  }
}
