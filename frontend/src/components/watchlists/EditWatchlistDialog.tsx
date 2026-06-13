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
      <DialogContent className="border-[var(--dialog-border)] bg-[var(--dialog-bg)]">
        <DialogHeader>
          <DialogTitle className="text-[var(--dialog-text)]">Edit Watchlist</DialogTitle>
          <DialogDescription className="text-[var(--dialog-muted)]">
            Update your watchlist configuration.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="edit-name" className="text-sm font-medium text-[var(--dialog-text)]">
              Name
            </label>
            <Input
              id="edit-name"
              placeholder="e.g. AI Coding Agents"
              className="border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-text)] placeholder:text-[var(--dialog-placeholder)]"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-xs text-[#EF4444]">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="edit-description" className="text-sm font-medium text-[var(--dialog-text)]">
              Description / Goal
            </label>
            <Input
              id="edit-description"
              placeholder="e.g. Monitor AI coding market evolution"
              className="border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-text)] placeholder:text-[var(--dialog-placeholder)]"
              {...register("description")}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--dialog-text)]">Sensitivity</label>
            <div className="flex gap-2">
              {sensitivities.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setValue("sensitivity", s, { shouldValidate: true })}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    watch("sensitivity") === s
                      ? "border-[var(--accent-color)] bg-[var(--accent-color-10)] text-[var(--accent-color)]"
                      : "border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-muted)] hover:text-[var(--dialog-text)]"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--dialog-text)]">Frequency</label>
            <div className="flex gap-2">
              {frequencies.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setValue("frequency", f, { shouldValidate: true })}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    watch("frequency") === f
                      ? "border-[var(--accent-color)] bg-[var(--accent-color-10)] text-[var(--accent-color)]"
                      : "border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-muted)] hover:text-[var(--dialog-text)]"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--dialog-text)]">Sources</label>
            <div className="flex flex-wrap gap-2">
              {sources.map((source) => (
                <button
                  key={source}
                  type="button"
                  onClick={() => toggleSource(source)}
                  className={`rounded-md border px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                    (selectedSources ?? []).includes(source)
                      ? "border-[var(--accent-color)] bg-[var(--accent-color-10)] text-[var(--accent-color)]"
                      : "border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-muted)] hover:text-[var(--dialog-text)]"
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
              className="text-[var(--dialog-muted)] hover:text-[var(--dialog-text)] hover:bg-[var(--dialog-surface)]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateWatchlist.isPending}
              className="bg-[var(--accent-color)] text-[var(--dialog-text)] hover:bg-[var(--accent-color-90)]"
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
