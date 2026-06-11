"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Layers, Pencil, Trash2, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/constants";
import { useDeleteWatchlist } from "@/hooks/use-watchlists";
import { EditWatchlistDialog } from "@/components/watchlists/EditWatchlistDialog";
import { toast } from "sonner";
import { extractApiError } from "@/lib/utils";
import type { WatchlistResponse } from "@/types/api";

interface WatchlistCardProps {
  watchlist: WatchlistResponse;
}

export function WatchlistCard({ watchlist }: WatchlistCardProps) {
  const router = useRouter();
  const [editOpen, setEditOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const deleteWatchlist = useDeleteWatchlist();
  const sensitivity = watchlist.monitoring_config?.sensitivity ?? "medium";
  const sources = watchlist.monitoring_config?.sources ?? [];
  const freq = watchlist.monitoring_config?.frequency ?? watchlist.monitoring_frequency;

  const handleDelete = async () => {
    try {
      await deleteWatchlist.mutateAsync(watchlist.id);
      toast.success("Watchlist deleted");
      setShowDeleteConfirm(false);
    } catch (error) {
      toast.error(extractApiError(error));
    }
  };

  return (
    <>
      <div className="relative group">
        <button
          onClick={() => router.push(ROUTES.watchlistDetail(watchlist.id))}
          className="w-full text-left"
        >
          <Card className="cursor-pointer border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] transition-colors hover:border-[#BC6C50]/40">
            <CardContent className="flex flex-col gap-3 p-5">
              <div className="flex items-center justify-between">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#BC6C50]/10 text-[#BC6C50]">
                  <Layers className="h-4 w-4" />
                </div>
                <div className="flex items-center gap-2">
                  {watchlist.is_active ? (
                    <Badge
                      variant="outline"
                      className="border-[#22C55E]/30 bg-[#22C55E]/15 text-[#22C55E] text-[10px] font-medium"
                    >
                      Active
                    </Badge>
                  ) : (
                    <Badge
                      variant="outline"
                      className="border-[#6B7280]/30 bg-[#6B7280]/15 text-[#6B7280] text-[10px] font-medium"
                    >
                      Inactive
                    </Badge>
                  )}
                  <Badge variant="outline" className="border-[rgba(255,255,255,0.1)] bg-[#2A2A2A] text-[10px] text-[#A0A0A0] capitalize">
                    {sensitivity}
                  </Badge>
                </div>
              </div>

              <div className="space-y-1">
                <h3 className="text-sm font-semibold text-white">
                  {watchlist.name}
                </h3>
                {watchlist.description && (
                  <p className="line-clamp-2 text-xs text-[#A0A0A0]">
                    {watchlist.description}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between border-t border-[rgba(255,255,255,0.1)] pt-3 text-[10px] text-[#6B7280]">
                <span className="capitalize">{freq}</span>
                {sources.length > 0 && (
                  <span>{sources.length} sources</span>
                )}
                <span>
                  {new Date(watchlist.created_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </span>
              </div>
            </CardContent>
          </Card>
        </button>

        {/* Action buttons — visible on hover */}
        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setEditOpen(true);
            }}
            className="flex h-7 w-7 items-center justify-center rounded-md border border-[rgba(255,255,255,0.1)] bg-[#2A2A2A] text-[#A0A0A0] hover:text-white transition-colors"
            title="Edit watchlist"
          >
            <Pencil className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowDeleteConfirm(true);
            }}
            className="flex h-7 w-7 items-center justify-center rounded-md border border-[rgba(255,255,255,0.1)] bg-[#2A2A2A] text-[#A0A0A0] hover:text-red-500 transition-colors"
            title="Delete watchlist"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Edit Dialog */}
      <EditWatchlistDialog
        watchlist={watchlist}
        open={editOpen}
        onOpenChange={setEditOpen}
      />

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
          onClick={() => setShowDeleteConfirm(false)}
        >
          <div
            className="w-full max-w-sm rounded-xl border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-white">Delete Watchlist</h3>
            <p className="mt-2 text-sm text-[#A0A0A0]">
              Are you sure you want to delete <span className="text-white font-medium">&ldquo;{watchlist.name}&rdquo;</span>? This will also remove all competitors and run history. This action cannot be undone.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="rounded-lg border border-[rgba(255,255,255,0.1)] bg-transparent px-4 py-2 text-sm text-[#A0A0A0] hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteWatchlist.isPending}
                className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {deleteWatchlist.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export function WatchlistCardSkeleton() {
  return (
    <Card className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
      <CardContent className="flex flex-col gap-3 p-5">
        <div className="flex items-center justify-between">
          <Skeleton className="h-9 w-9 rounded-lg bg-[#2A2A2A]" />
          <Skeleton className="h-5 w-16 rounded-full bg-[#2A2A2A]" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-3/4 bg-[#2A2A2A]" />
          <Skeleton className="h-3 w-full bg-[#2A2A2A]" />
        </div>
        <div className="flex items-center justify-between border-t border-[rgba(255,255,255,0.1)] pt-3">
          <Skeleton className="h-3 w-20 bg-[#2A2A2A]" />
          <Skeleton className="h-3 w-24 bg-[#2A2A2A]" />
        </div>
      </CardContent>
    </Card>
  );
}
