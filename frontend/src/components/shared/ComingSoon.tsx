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
        <div className="text-[var(--muted-text)]">{icon}</div>
      </div>
      <div>
        <p className="text-base font-medium text-foreground">{title}</p>
        <p className="mt-1 text-sm text-[var(--muted-text)]">
          {description || "This feature is coming soon. Stay tuned."}
        </p>
      </div>
      <span className="rounded-full bg-[var(--accent-color-10)] px-3 py-0.5 text-[11px] font-semibold text-[var(--accent-color)]">
        UPCOMING
      </span>
    </div>
  );
}
