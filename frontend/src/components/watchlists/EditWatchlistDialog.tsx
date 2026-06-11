"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import { useUpdateWatchlist } from "@/hooks/use-watchlists";
import { extractApiError } from "@/lib/utils";
import type { WatchlistResponse } from "@/types/api";

const sources = ["homepage", "pricing", "blog", "careers"] as const;
const sensitivities = ["low", "medium", "high"] as const;
const frequencies = ["daily", "weekly"] as const;

const editWatchlistSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional().or(z.literal("")),
  sensitivity: z.enum(sensitivities),
  frequency: z.enum(frequencies),
  sources: z.array(z.enum(sources)).min(1, "Select at least one source"),
});

type EditWatchlistFormValues = z.infer<typeof editWatchlistSchema>;

interface EditWatchlistDialogProps {
  watchlist: WatchlistResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditWatchlistDialog({
  watchlist,
  open,
  onOpenChange,
}: EditWatchlistDialogProps) {
  const [confirmClose, setConfirmClose] = useState(false);
  const updateWatchlist = useUpdateWatchlist();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors, isDirty },
  } = useForm<EditWatchlistFormValues>({
    resolver: zodResolver(editWatchlistSchema),
    defaultValues: {
      name: watchlist.name,
      description: watchlist.description ?? "",
      sensitivity: (watchlist.monitoring_config?.sensitivity as typeof sensitivities[number]) ?? "medium",
      frequency: (watchlist.monitoring_config?.frequency as typeof frequencies[number]) ?? watchlist.monitoring_frequency.toLowerCase() as typeof frequencies[number],
      sources: (watchlist.monitoring_config?.sources as typeof sources[number][]) ?? ["homepage", "pricing"],
    },
  });

  const selectedSources = watch("sources");

  const toggleSource = (source: string) => {
    const current = selectedSources ?? [];
    if (current.includes(source as typeof sources[number])) {
      setValue("sources", current.filter((s) => s !== source), { shouldValidate: true });
    } else {
      setValue("sources", [...current, source as typeof sources[number]], { shouldValidate: true });
    }
  };

  const handleClose = () => {
    if (isDirty && !confirmClose) {
      setConfirmClose(true);
      return;
    }
    setConfirmClose(false);
    reset();
    onOpenChange(false);
  };

  const onSubmit = handleSubmit(async (data) => {
    try {
      await updateWatchlist.mutateAsync({
        id: watchlist.id,
        data: {
          name: data.name,
          description: data.description || undefined,
          monitoring_config: {
            frequency: data.frequency,
            sources: data.sources,
            sensitivity: data.sensitivity,
          },
        },
      });
      toast.success("Watchlist updated");
      setConfirmClose(false);
      reset(data);
      onOpenChange(false);
    } catch (error) {
      toast.error(extractApiError(error));
    }
  });

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
        <DialogHeader>
          <DialogTitle className="text-white">Edit Watchlist</DialogTitle>
          <DialogDescription className="text-[#A0A0A0]">
            Update your watchlist configuration.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="edit-name" className="text-sm font-medium text-white">
              Name
            </label>
            <Input
              id="edit-name"
              placeholder="e.g. AI Coding Agents"
              className="border-[rgba(255,255,255,0.1)] bg-[#121212] text-white placeholder:text-[#6B7280]"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-xs text-[#EF4444]">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="edit-description" className="text-sm font-medium text-white">
              Description / Goal
            </label>
            <Input
              id="edit-description"
              placeholder="e.g. Monitor AI coding market evolution"
              className="border-[rgba(255,255,255,0.1)] bg-[#121212] text-white placeholder:text-[#6B7280]"
              {...register("description")}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white">Sensitivity</label>
            <div className="flex gap-2">
              {sensitivities.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setValue("sensitivity", s, { shouldValidate: true })}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    watch("sensitivity") === s
                      ? "border-[#BC6C50] bg-[#BC6C50]/10 text-[#BC6C50]"
                      : "border-[rgba(255,255,255,0.1)] bg-[#121212] text-[#A0A0A0] hover:text-white"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white">Frequency</label>
            <div className="flex gap-2">
              {frequencies.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setValue("frequency", f, { shouldValidate: true })}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    watch("frequency") === f
                      ? "border-[#BC6C50] bg-[#BC6C50]/10 text-[#BC6C50]"
                      : "border-[rgba(255,255,255,0.1)] bg-[#121212] text-[#A0A0A0] hover:text-white"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white">Sources</label>
            <div className="flex flex-wrap gap-2">
              {sources.map((source) => (
                <button
                  key={source}
                  type="button"
                  onClick={() => toggleSource(source)}
                  className={`rounded-md border px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                    (selectedSources ?? []).includes(source)
                      ? "border-[#BC6C50] bg-[#BC6C50]/10 text-[#BC6C50]"
                      : "border-[rgba(255,255,255,0.1)] bg-[#121212] text-[#A0A0A0] hover:text-white"
                  }`}
                >
                  {source}
                </button>
              ))}
            </div>
            {errors.sources && (
              <p className="text-xs text-[#EF4444]">{errors.sources.message}</p>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={handleClose}
              className="text-[#A0A0A0] hover:text-white hover:bg-[#2A2A2A]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateWatchlist.isPending}
              className="bg-[#BC6C50] text-white hover:bg-[#BC6C50]/90"
            >
              {updateWatchlist.isPending ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
