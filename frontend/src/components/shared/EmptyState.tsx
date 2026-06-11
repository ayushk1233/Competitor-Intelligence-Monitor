import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  cta?: ReactNode;
}

export function EmptyState({ icon, title, description, cta }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-4 py-20 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-[#1A2332]">
        <div className="text-[#6B7280]">{icon}</div>
      </div>
      <div>
        <p className="text-base font-medium text-[#F8FAFC]">{title}</p>
        <p className="mt-1 text-sm text-[#94A3B8]">{description}</p>
      </div>
      {cta}
    </div>
  );
}
