"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/constants";
import { AlertTriangle, RefreshCw, LayoutDashboard } from "lucide-react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0B1020] px-4">
      <div className="flex flex-col items-center gap-5 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#EF4444]/10">
          <AlertTriangle className="h-8 w-8 text-[#EF4444]" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-[#F8FAFC]">
            Something went wrong
          </h1>
          <p className="mt-1 text-sm text-[var(--muted-text)]">
            {error.message || "An unexpected error occurred"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={reset}
            className="bg-[#14B8A6] text-[#0B1020] hover:bg-[#14B8A6]/90"
          >
            <RefreshCw className="mr-1.5 h-4 w-4" />
            Try again
          </Button>
          <Button
            variant="outline"
            onClick={() => router.push(ROUTES.dashboard)}
            className="border-[#1A2332] text-[var(--muted-text)] hover:bg-[#1A2332] hover:text-[#F8FAFC]"
          >
            <LayoutDashboard className="mr-1.5 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
