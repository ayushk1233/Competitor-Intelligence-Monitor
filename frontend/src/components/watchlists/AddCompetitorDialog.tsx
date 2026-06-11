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
        <Button className="bg-[#BC6C50] text-white hover:bg-[#BC6C50]/90">
          <Plus className="mr-1 h-4 w-4" />
          Add Competitor
        </Button>
      </DialogTrigger>
      <DialogContent className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
        <DialogHeader>
          <DialogTitle className="text-white">Add Competitor</DialogTitle>
          <DialogDescription className="text-[#A0A0A0]">
            Add a competitor to this watchlist.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="company_name" className="text-sm font-medium text-white">
              Company Name
            </label>
            <Input
              id="company_name"
              placeholder="e.g. Acme Corp"
              className="border-[rgba(255,255,255,0.1)] bg-[#121212] text-white placeholder:text-[#6B7280]"
              {...register("company_name")}
            />
            {errors.company_name && (
              <p className="text-xs text-[#EF4444]">{errors.company_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="domain" className="text-sm font-medium text-white">
              Domain
            </label>
            <Input
              id="domain"
              placeholder="Optional domain"
              className="border-[rgba(255,255,255,0.1)] bg-[#121212] text-white placeholder:text-[#6B7280]"
              {...register("domain")}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white">Priority</label>
            <div className="flex gap-2">
              {priorities.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setValue("priority", p, { shouldValidate: true })}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium capitalize transition-colors ${
                    watch("priority") === p
                      ? "border-[#BC6C50] bg-[#BC6C50]/10 text-[#BC6C50]"
                      : "border-[rgba(255,255,255,0.1)] bg-[#121212] text-[#A0A0A0] hover:text-white"
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
              className="text-[#A0A0A0] hover:text-white hover:bg-[#2A2A2A]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={addCompetitor.isPending}
              className="bg-[#BC6C50] text-white hover:bg-[#BC6C50]/90"
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
