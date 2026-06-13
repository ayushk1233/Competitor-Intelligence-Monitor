"use client";

import type { ReactNode } from "react";
import { useAuth } from "@/hooks/use-auth";
import { redirect } from "next/navigation";
import { useTheme } from "@/providers/ThemeProvider";
import { Shield, BarChart3, Bell, TrendingUp, Sun, Moon } from "lucide-react";

const valueProps = [
  {
    icon: BarChart3,
    title: "Track competitor landscape",
    desc: "Monitor positioning, messaging, and feature changes across your market",
  },
  {
    icon: Bell,
    title: "Real-time alerts",
    desc: "Get notified when competitors launch, pivot, or shift strategy",
  },
  {
    icon: TrendingUp,
    title: "Momentum scoring",
    desc: "Quantified competitive momentum with data-driven signals",
  },
  {
    icon: Shield,
    title: "Intelligence feed",
    desc: "Curated intelligence feed of actionable competitor changes",
  },
];

export default function AuthLayout({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const { theme, toggle } = useTheme();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--orange)] border-t-transparent" />
      </div>
    );
  }

  if (isAuthenticated) {
    redirect("/dashboard");
  }

    return (
      <div className="flex min-h-screen">
        <div className={`relative hidden w-1/2 flex-col justify-between p-16 font-mono lg:flex ${theme === "dark" ? "bg-[#A2C2AB]" : "bg-[var(--background-secondary)]"}`}>
          <div className="relative z-10">
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${theme === "dark" ? "bg-[#064A2C]" : "bg-[#0D5E3A]"}`}>
                <Shield className="h-5 w-5 text-white" />
              </div>
              <span className={`text-lg font-bold tracking-tight font-mono ${theme === "dark" ? "text-[#064A2C]" : "text-[#0D5E3A]"}`}>CIM</span>
            </div>
            <h1 className={`mt-20 text-[2.5rem] font-bold leading-[1.1] tracking-tight font-mono ${theme === "dark" ? "text-[#064A2C]" : "text-black"}`}>
              Know everything your<br />competitors are doing.
            </h1>
            <p className={`mt-4 max-w-md text-base ${theme === "dark" ? "text-[#064A2C]/70" : "text-black/60"}`}>
              Automated competitive intelligence powered by AI. Track, analyze, and act on competitor movements.
            </p>
          </div>
          <div className="relative z-10 space-y-10">
            {valueProps.map((prop, i) => (
              <div key={i} className="flex items-start gap-5">
                <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${theme === "dark" ? "bg-[#064A2C]/10" : "bg-black/10"}`}>
                  <prop.icon className={`h-5 w-5 ${theme === "dark" ? "text-[#064A2C]" : "text-black"}`} />
                </div>
                <div>
                  <p className={`text-sm font-semibold font-mono ${theme === "dark" ? "text-[#064A2C]" : "text-black"}`}>{prop.title}</p>
                  <p className={`mt-0.5 text-sm ${theme === "dark" ? "text-[#064A2C]/60" : "text-black/60"}`}>{prop.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <p className={`relative z-10 text-sm ${theme === "dark" ? "text-[#064A2C]/50" : "text-black/50"}`}>
            &copy; 2026 CIM. All rights reserved.
          </p>
        </div>
        <div className="flex w-full items-center justify-center bg-card px-6 lg:w-1/2">
        <div className="relative w-full max-w-sm">
          <button
            onClick={toggle}
            className="absolute right-0 top-0 -translate-y-full mb-4 flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-mono text-muted-foreground transition-colors hover:text-foreground"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            {theme === "dark" ? "Light" : "Dark"}
          </button>
          {children}
        </div>
      </div>
    </div>
  );
}
