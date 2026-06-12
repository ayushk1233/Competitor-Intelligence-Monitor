"use client";

import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { useDashboardSummary } from "@/hooks/use-dashboard";
import { useTheme } from "@/providers/ThemeProvider";
import { ROUTES } from "@/constants";
import {
  LayoutDashboard,
  Users,
  Bell,
  TrendingUp,
  Layers,
  PlayCircle,
  Swords,
  Search,
  LogOut,
  X,
  Sun,
  Moon,
} from "lucide-react";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const monitoringItems = [
  { label: "Dashboard", href: ROUTES.dashboard, icon: LayoutDashboard },
  { label: "Competitors", href: ROUTES.watchlists, icon: Users, badgeKey: "competitors" as const },
  { label: "Alerts", href: "/alerts", icon: Bell, badgeKey: "alerts" as const, isAlert: true },
  { label: "Trends", href: "/trends", icon: TrendingUp },
];

const toolsItems = [
  { label: "Run History", href: "/run-history", icon: PlayCircle },
  { label: "Battlecards", href: "/battlecards", icon: Swords },
  { label: "Intel Search", href: "/intel-search", icon: Search },
];

function isActive(pathname: string, href: string): boolean {
  if (href === ROUTES.dashboard) return pathname === ROUTES.dashboard;
  return pathname.startsWith(href);
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const { data: summary } = useDashboardSummary();
  const { theme, toggle } = useTheme();

  const handleNav = (href: string) => {
    router.push(href);
    onClose();
  };

  const getBadge = (badgeKey: "competitors" | "alerts"): string | undefined => {
    if (!summary) return undefined;
    if (badgeKey === "competitors") return String(summary.competitors);
    if (badgeKey === "alerts") return String(summary.total_alerts);
    return undefined;
  };

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-40 bg-black/60 lg:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-neutral-800 bg-neutral-900 font-mono transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-3 p-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 8l8-5 8 5v9a2 2 0 01-2 2H6a2 2 0 01-2-2V8z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4" />
            </svg>
          </div>
          <div className="flex-1">
            <div className="text-lg font-bold text-white leading-none">CIM</div>
            <div className="text-xs text-neutral-500 leading-tight mt-0.5 font-sans">Intelligence Monitor</div>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-md text-neutral-500 hover:text-white lg:hidden"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-4">
          <div className="px-4 mb-2 mt-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
              Monitoring
            </p>
          </div>
          <nav className="mb-6 space-y-0.5">
            {monitoringItems.map((item) => {
              const active = isActive(pathname, item.href);
              const badge = item.badgeKey ? getBadge(item.badgeKey) : undefined;
              return (
                <button
                  key={item.href}
                  onClick={() => handleNav(item.href)}
                  className={`flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    active
                      ? "bg-neutral-800/50 text-white"
                      : "text-neutral-400 hover:bg-neutral-800/30 hover:text-white"
                  }`}
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  <span className="flex-1 text-left">{item.label}</span>
                  {badge !== undefined && item.isAlert ? (
                    <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1.5 text-[10px] font-bold text-white">
                      {badge}
                    </span>
                  ) : badge !== undefined ? (
                    <span className="text-xs text-neutral-500">{badge}</span>
                  ) : null}
                </button>
              );
            })}
          </nav>

          <div className="px-4 mb-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
              Tools
            </p>
          </div>
          <nav className="space-y-0.5">
            {toolsItems.map((item) => {
              const active = isActive(pathname, item.href);
              return (
                <button
                  key={item.href}
                  onClick={() => handleNav(item.href)}
                  className={`flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    active
                      ? "bg-neutral-800/50 text-white"
                      : "text-neutral-400 hover:bg-neutral-800/30 hover:text-white"
                  }`}
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  <span className="flex-1 text-left">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="border-t border-neutral-800 px-4 py-3">
          <p className="truncate text-xs text-neutral-500 font-sans">
            {user?.email || user?.display_name}
          </p>
          <div className="mt-1 flex items-center gap-1">
            <button
              onClick={toggle}
              className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-neutral-500 transition-colors hover:text-white"
            >
              {theme === "dark" ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
              {theme === "dark" ? "Light" : "Dark"}
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-neutral-500 transition-colors hover:text-red-500"
            >
              <LogOut className="h-3.5 w-3.5" />
              Logout
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
