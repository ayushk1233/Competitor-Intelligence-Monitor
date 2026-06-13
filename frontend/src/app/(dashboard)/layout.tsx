"use client";

import { useState, type ReactNode } from "react";
import { useAuth } from "@/hooks/use-auth";
import { redirect } from "next/navigation";
import { ROUTES } from "@/constants";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { DetailPanelProvider } from "@/components/detail/DetailPanelContext";
import { DetailPanel } from "@/components/detail/DetailPanel";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#BC6C50] border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    redirect(ROUTES.login);
  }

  return (
    <DetailPanelProvider>
      <div className="flex h-screen overflow-hidden">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="flex flex-1 flex-col min-w-0">
          <Topbar onMenuToggle={() => setSidebarOpen(true)} />
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
        <DetailPanel />
      </div>
    </DetailPanelProvider>
  );
}
