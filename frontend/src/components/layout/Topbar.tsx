"use client";

import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { useTheme } from "@/providers/ThemeProvider";
import { Menu, Sun, Moon } from "lucide-react";

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
  const { theme, toggle } = useTheme();

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-[var(--topbar-bg)] px-4 lg:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-500 hover:text-white lg:hidden"
        >
          <Menu className="h-4 w-4" />
        </button>
        <h2 className="text-sm font-semibold tracking-tight text-foreground font-mono">
          {getPageTitle(pathname)}
        </h2>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggle}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-400 hover:text-[var(--topbar-icon-hover)] transition-colors"
          title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
        <span className="text-xs text-neutral-500">
          {user?.display_name || user?.email}
        </span>
      </div>
    </header>
  );
}
