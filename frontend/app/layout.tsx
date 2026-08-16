import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Unravel — News Traceability Graph",
  description: "Unravel the story behind the news.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-[#FAF8F4] text-unravel-ink antialiased">{children}</body>
    </html>
  );
}
