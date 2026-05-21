import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Bajaj Automation Qualifier",
  description: "FastAPI + Next.js API test harness",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

