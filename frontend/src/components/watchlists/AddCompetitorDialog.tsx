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
import { useAddCompetitor } from "@/hooks/use-competitors";
import { extractApiError } from "@/lib/utils";

const priorities = ["high", "medium", "low"] as const;

const addCompetitorSchema = z.object({
  company_name: z.string().min(1, "Company name is required"),
  domain: z.string().optional().or(z.literal("")),
  priority: z.enum(priorities),
});

type AddCompetitorFormValues = z.infer<typeof addCompetitorSchema>;

interface AddCompetitorDialogProps {
  watchlistId: string;
}

export function AddCompetitorDialog({ watchlistId }: AddCompetitorDialogProps) {
  const [open, setOpen] = useState(false);
  const addCompetitor = useAddCompetitor(watchlistId);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<AddCompetitorFormValues>({
    resolver: zodResolver(addCompetitorSchema),
    defaultValues: { company_name: "", domain: "", priority: "medium" },
  });

  const onSubmit = handleSubmit(async (data) => {
    try {
      await addCompetitor.mutateAsync({
        company_name: data.company_name,
        domain: data.domain || undefined,
        priority: data.priority,
        monitoring_enabled: true,
      });
      toast.success("Competitor added");
      setOpen(false);
      reset();
    } catch (error) {
      toast.error(extractApiError(error));
    }
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-[var(--accent-color)] text-[var(--dialog-text)] hover:bg-[var(--accent-color-90)]">
          <Plus className="mr-1 h-4 w-4" />
          Add Competitor
        </Button>
      </DialogTrigger>
      <DialogContent className="border-[var(--dialog-border)] bg-[var(--dialog-bg)]">
        <DialogHeader>
          <DialogTitle className="text-[var(--dialog-text)]">Add Competitor</DialogTitle>
          <DialogDescription className="text-[var(--dialog-muted)]">
            Add a competitor to this watchlist.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="company_name" className="text-sm font-medium text-[var(--dialog-text)]">
              Company Name
            </label>
            <Input
              id="company_name"
              placeholder="e.g. Acme Corp"
              className="border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-text)] placeholder:text-[var(--dialog-placeholder)]"
              {...register("company_name")}
            />
            {errors.company_name && (
              <p className="text-xs text-[#EF4444]">{errors.company_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="domain" className="text-sm font-medium text-[var(--dialog-text)]">
              Domain
            </label>
            <Input
              id="domain"
              placeholder="Optional domain"
              className="border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-text)] placeholder:text-[var(--dialog-placeholder)]"
              {...register("domain")}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--dialog-text)]">Priority</label>
            <div className="flex gap-2">
              {priorities.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setValue("priority", p, { shouldValidate: true })}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    watch("priority") === p
                      ? "border-[var(--accent-color)] bg-[var(--accent-color-10)] text-[var(--accent-color)]"
                      : "border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-muted)] hover:text-[var(--dialog-text)]"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setOpen(false);
                reset();
              }}
              className="text-[var(--dialog-muted)] hover:text-[var(--dialog-text)] hover:bg-[var(--dialog-surface)]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={addCompetitor.isPending}
              className="bg-[var(--accent-color)] text-[var(--dialog-text)] hover:bg-[var(--accent-color-90)]"
            >
              {addCompetitor.isPending ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                "Add"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
