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
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Loader2 } from "lucide-react";
import { useCreateWatchlist } from "@/hooks/use-watchlists";
import { extractApiError } from "@/lib/utils";

const sources = ["homepage", "pricing", "blog", "careers"] as const;
const sensitivities = ["low", "medium", "high"] as const;
const frequencies = ["daily", "weekly"] as const;

const createWatchlistSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional().or(z.literal("")),
  sensitivity: z.enum(sensitivities),
  frequency: z.enum(frequencies),
  sources: z.array(z.enum(sources)).min(1, "Select at least one source"),
});

type CreateWatchlistFormValues = z.infer<typeof createWatchlistSchema>;

export function CreateWatchlistDialog() {
  const [open, setOpen] = useState(false);
  const createWatchlist = useCreateWatchlist();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CreateWatchlistFormValues>({
    resolver: zodResolver(createWatchlistSchema),
    defaultValues: {
      name: "",
      description: "",
      sensitivity: "medium",
      frequency: "daily",
      sources: ["homepage", "pricing"],
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

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createWatchlist.mutateAsync({
        name: data.name,
        description: data.description || undefined,
        monitoring_config: {
          frequency: data.frequency,
          sources: data.sources,
          sensitivity: data.sensitivity,
        },
      });
      toast.success("Watchlist created");
      setOpen(false);
      reset();
    } catch (error) {
      toast.error(extractApiError(error));
    }
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-[#BC6C50] text-white hover:bg-[#BC6C50]/90">
          <Plus className="mr-1 h-4 w-4" />
          Create Watchlist
        </Button>
      </DialogTrigger>
      <DialogContent className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
        <DialogHeader>
          <DialogTitle className="text-white">Create Watchlist</DialogTitle>
          <DialogDescription className="text-[#A0A0A0]">
            What strategic question are you trying to answer?
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium text-white">
              Name
            </label>
            <Input
              id="name"
              placeholder="e.g. AI Coding Agents"
              className="border-[rgba(255,255,255,0.1)] bg-[#121212] text-white placeholder:text-[#6B7280]"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-xs text-[#EF4444]">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="description" className="text-sm font-medium text-white">
              Description / Goal
            </label>
            <Input
              id="description"
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
              onClick={() => {
                setOpen(false);
                reset();
              }}
              className="text-[#A0A0A0] hover:text-white hover:bg-[#2A2A2A]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createWatchlist.isPending}
              className="bg-[#BC6C50] text-white hover:bg-[#BC6C50]/90"
            >
              {createWatchlist.isPending ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
