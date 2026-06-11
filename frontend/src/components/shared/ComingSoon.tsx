"use client";

import type { ReactNode } from "react";

interface ComingSoonProps {
  title: string;
  description?: string;
  icon: ReactNode;
}

export function ComingSoon({ title, description, icon }: ComingSoonProps) {
  return (
    <div className="flex flex-col items-center gap-4 py-24 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-[#2A2A2A]">
        <div className="text-[#6B7280]">{icon}</div>
      </div>
      <div>
        <p className="text-base font-medium text-white">{title}</p>
        <p className="mt-1 text-sm text-[#A0A0A0]">
          {description || "This feature is coming soon. Stay tuned."}
        </p>
      </div>
      <span className="rounded-full bg-[#BC6C50]/15 px-3 py-0.5 text-[11px] font-semibold text-[#BC6C50]">
        UPCOMING
      </span>
    </div>
  );
}
