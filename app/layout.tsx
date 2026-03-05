import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 타임박싱 스케줄러",
  description: "AI가 우선순위를 정해 Google 캘린더에 자동으로 일정을 등록해주는 스마트 스케줄러",
  icons: { icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="antialiased">{children}</body>
    </html>
  );
}
