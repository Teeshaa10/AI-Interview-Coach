import { Badge } from "@/components/common/Badge";

export function InterviewProgress({
  current,
  total,
  category,
}: {
  current: number;
  total: number;
  category: string;
}) {
  const percent = Math.round((current / total) * 100);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-400">
          Question {current} of {total}
        </span>
        <Badge tone="brand">{category}</Badge>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-700">
        <div className="h-full bg-brand-500 transition-all duration-300" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
