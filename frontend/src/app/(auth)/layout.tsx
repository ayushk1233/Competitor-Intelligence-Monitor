"use client";

import type { ReactNode } from "react";
import { useAuth } from "@/hooks/use-auth";
import { redirect } from "next/navigation";
import { Shield, BarChart3, Bell, TrendingUp } from "lucide-react";

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

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#BC6C50] border-t-transparent" />
      </div>
    );
  }

  if (isAuthenticated) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-screen">
      <div className="relative hidden w-1/2 flex-col justify-between bg-[#0D5E3A] p-16 lg:flex">
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/10">
              <Shield className="h-5 w-5 text-white/80" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white/80">CIM</span>
          </div>
          <h1 className="mt-20 text-[2.5rem] font-bold leading-[1.1] tracking-tight text-white/90">
            Know everything your<br />competitors are doing.
          </h1>
          <p className="mt-4 max-w-md text-base text-white/50">
            Automated competitive intelligence powered by AI. Track, analyze, and act on competitor movements.
          </p>
        </div>
        <div className="relative z-10 space-y-10">
          {valueProps.map((prop, i) => (
            <div key={i} className="flex items-start gap-5">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/5">
                <prop.icon className="h-5 w-5 text-white/60" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white/80">{prop.title}</p>
                <p className="mt-0.5 text-sm text-white/40">{prop.desc}</p>
              </div>
            </div>
          ))}
        </div>
        <p className="relative z-10 text-sm text-white/30">
          &copy; 2026 CIM. All rights reserved.
        </p>
      </div>
      <div className="flex w-full items-center justify-center bg-background px-6 lg:w-1/2">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}
