"use client";

import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Menu } from "lucide-react";

interface TopbarProps {
  onMenuToggle: () => void;
}

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/watchlists": "Watchlists",
  "/notifications": "Notifications",
  "/alerts": "Alerts",
  "/trends": "Trends",
  "/run-history": "Run History",
  "/battlecards": "Battlecards",
  "/intel-search": "Intel Search",
};

function getPageTitle(pathname: string): string {
  if (pathname.match(/^\/reports\/.+/)) {
    return "Intelligence Report";
  }
  if (pathname.match(/^\/watchlists\/[^/]+\/competitors\/.+/)) {
    return "Competitor Detail";
  }
  if (pathname.startsWith("/watchlists/")) {
    return "Watchlist Detail";
  }
  return pageTitles[pathname] || "Dashboard";
}

export function Topbar({ onMenuToggle }: TopbarProps) {
  const pathname = usePathname();
  const { user } = useAuth();

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-background px-4 lg:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-500 hover:text-white lg:hidden"
        >
          <Menu className="h-4 w-4" />
        </button>
        <h2 className="text-sm font-semibold tracking-tight text-white font-mono">
          {getPageTitle(pathname)}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-xs text-neutral-500">
          {user?.display_name || user?.email}
        </span>
      </div>
    </header>
  );
}
