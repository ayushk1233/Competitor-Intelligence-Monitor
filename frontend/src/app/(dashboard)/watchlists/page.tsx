"use client";

import { useWatchlists } from "@/hooks/use-watchlists";
import { WatchlistCard, WatchlistCardSkeleton } from "@/components/watchlists/WatchlistCard";
import { CreateWatchlistDialog } from "@/components/watchlists/CreateWatchlistDialog";
import { EmptyState } from "@/components/shared/EmptyState";
import { Layers, AlertCircle } from "lucide-react";

export default function WatchlistsPage() {
  const { data, isLoading, isError, error } = useWatchlists();

  if (isError) {
    return (
        <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-[#A0A0A0]">Manage your competitor monitoring groups</p>
          </div>
        </div>
        <div className="flex flex-col items-center gap-3 py-20 text-center">
          <AlertCircle className="h-10 w-10 text-[#EF4444]" />
          <p className="text-sm text-[#A0A0A0]">Failed to load watchlists</p>
          <p className="text-xs text-[#6B7280]">{(error as Error)?.message || "An error occurred"}</p>
        </div>
      </div>
    );
  }

  const watchlists = data?.items ?? [];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-[#94A3B8]">Manage your competitor monitoring groups</p>
        </div>
        {!isLoading && watchlists.length > 0 && <CreateWatchlistDialog />}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <WatchlistCardSkeleton />
          <WatchlistCardSkeleton />
          <WatchlistCardSkeleton />
          <WatchlistCardSkeleton />
          <WatchlistCardSkeleton />
          <WatchlistCardSkeleton />
        </div>
      ) : watchlists.length === 0 ? (
        <EmptyState
          icon={<Layers className="h-7 w-7" />}
          title="No watchlists yet"
          description="Create your first watchlist to start tracking competitors"
          cta={<CreateWatchlistDialog />}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {watchlists.map((wl) => (
            <WatchlistCard key={wl.id} watchlist={wl} />
          ))}
        </div>
      )}
    </div>
  );
}
