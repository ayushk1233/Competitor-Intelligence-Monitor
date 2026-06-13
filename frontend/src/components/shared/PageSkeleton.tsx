import { Skeleton } from "@/components/ui/skeleton";

export function PageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="space-y-1">
        <Skeleton className="h-7 w-48 bg-[#1A2332]" />
        <Skeleton className="h-4 w-64 bg-[#1A2332]" />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="space-y-3 rounded-lg border border-[#1A2332] bg-[#121826] p-5"
          >
            <Skeleton className="h-9 w-9 rounded-lg bg-[#1A2332]" />
            <Skeleton className="h-4 w-3/4 bg-[#1A2332]" />
            <Skeleton className="h-3 w-full bg-[#1A2332]" />
          </div>
        ))}
      </div>
    </div>
  );
}
