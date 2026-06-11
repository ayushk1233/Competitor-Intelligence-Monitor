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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Loader2 } from "lucide-react";
import { useCreateNotificationChannel } from "@/hooks/use-notifications";
import { extractApiError } from "@/lib/utils";

const createChannelSchema = z.object({
  channel_type: z.string().min(1, "Channel type is required"),
  destination: z.string().min(1, "Destination is required"),
  label: z.string().optional().or(z.literal("")),
});

type CreateChannelFormValues = z.infer<typeof createChannelSchema>;

export function CreateChannelDialog() {
  const [open, setOpen] = useState(false);
  const createChannel = useCreateNotificationChannel();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CreateChannelFormValues>({
    resolver: zodResolver(createChannelSchema),
    defaultValues: { channel_type: "", destination: "", label: "" },
  });

  const channelType = watch("channel_type");

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createChannel.mutateAsync({
        channel_type: data.channel_type,
        destination: data.destination,
        label: data.label || undefined,
      });
      toast.success("Notification channel created");
      setOpen(false);
      reset();
    } catch (error) {
      toast.error(extractApiError(error));
    }
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-[#14B8A6] text-[#0B1020] hover:bg-[#14B8A6]/90">
          <Plus className="mr-1 h-4 w-4" />
          Add Channel
        </Button>
      </DialogTrigger>
      <DialogContent className="border-[#1A2332] bg-[#121826]">
        <DialogHeader>
          <DialogTitle className="text-[#F8FAFC]">Add Notification Channel</DialogTitle>
          <DialogDescription className="text-[#94A3B8]">
            Configure a channel to receive alerts and notifications.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="channel_type"
              className="text-sm font-medium text-[#CBD5E1]"
            >
              Channel Type
            </label>
            <Select
              value={channelType}
              onValueChange={(value) => setValue("channel_type", value)}
            >
              <SelectTrigger className="w-full border-[#1A2332] bg-[#0B1020] text-[#F8FAFC]">
                <SelectValue placeholder="Select channel type" />
              </SelectTrigger>
              <SelectContent className="border-[#1A2332] bg-[#121826]">
                <SelectItem
                  value="EMAIL"
                  className="text-[#F8FAFC] focus:bg-[#1A2332] focus:text-[#F8FAFC]"
                >
                  Email
                </SelectItem>
                <SelectItem
                  value="SLACK"
                  className="text-[#F8FAFC] focus:bg-[#1A2332] focus:text-[#F8FAFC]"
                >
                  Slack
                </SelectItem>
                <SelectItem
                  value="WEBHOOK"
                  className="text-[#F8FAFC] focus:bg-[#1A2332] focus:text-[#F8FAFC]"
                >
                  Webhook
                </SelectItem>
              </SelectContent>
            </Select>
            {errors.channel_type && (
              <p className="text-xs text-[#EF4444]">
                {errors.channel_type.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="destination"
              className="text-sm font-medium text-[#CBD5E1]"
            >
              Destination
            </label>
            <Input
              id="destination"
              placeholder={
                channelType === "EMAIL"
                  ? "email@example.com"
                  : channelType === "SLACK"
                    ? "https://hooks.slack.com/..."
                    : "https://..."
              }
              className="border-[#1A2332] bg-[#0B1020] text-[#F8FAFC] placeholder:text-[#6B7280]"
              {...register("destination")}
            />
            {errors.destination && (
              <p className="text-xs text-[#EF4444]">
                {errors.destination.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="label"
              className="text-sm font-medium text-[#CBD5E1]"
            >
              Label
            </label>
            <Input
              id="label"
              placeholder="Optional label"
              className="border-[#1A2332] bg-[#0B1020] text-[#F8FAFC] placeholder:text-[#6B7280]"
              {...register("label")}
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setOpen(false);
                reset();
              }}
              className="text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#1A2332]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createChannel.isPending}
              className="bg-[#14B8A6] text-[#0B1020] hover:bg-[#14B8A6]/90"
            >
              {createChannel.isPending ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                "Add Channel"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
