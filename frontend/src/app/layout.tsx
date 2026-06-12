import type { Metadata } from "next";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { Providers } from "@/providers";

export const metadata: Metadata = {
  title: "Competitor Intelligence Monitor",
  description: "AI-powered competitive intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${GeistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
