import { Sparkles } from "lucide-react";
import clsx from "clsx";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { READINESS_LABELS, type CoachingInsights, type ReadinessLevel } from "@/types/coaching";

const READINESS_TONE: Record<ReadinessLevel, "neutral" | "warning" | "brand" | "success"> = {
  getting_started: "neutral",
  building_confidence: "warning",
  interview_ready: "brand",
  highly_prepared: "success",
};

const READINESS_RING: Record<ReadinessLevel, string> = {
  getting_started: "stroke-slate-500",
  building_confidence: "stroke-amber-400",
  interview_ready: "stroke-brand-400",
  highly_prepared: "stroke-emerald-400",
};

export function CoachingReadinessCard({ insights }: { insights: CoachingInsights }) {
  const circumference = 2 * Math.PI * 42;
  const progress = Math.max(0, Math.min(100, insights.readiness_score));
  const dashOffset = circumference * (1 - progress / 100);

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">Interview readiness</h3>
        <Badge tone={READINESS_TONE[insights.readiness_level]}>{READINESS_LABELS[insights.readiness_level]}</Badge>
      </CardHeader>
      <CardBody className="flex flex-col gap-5 sm:flex-row sm:items-center">
        <div className="relative mx-auto h-28 w-28 shrink-0 sm:mx-0">
          <svg viewBox="0 0 100 100" className="h-28 w-28 -rotate-90">
            <circle cx="50" cy="50" r="42" strokeWidth="8" fill="none" className="stroke-surface-700" />
            <circle
              cx="50"
              cy="50"
              r="42"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              className={clsx("transition-all duration-500", READINESS_RING[insights.readiness_level])}
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-semibold text-slate-100">{Math.round(insights.readiness_score)}</span>
            <span className="text-xs text-slate-500">/ 100</span>
          </div>
        </div>

        <div className="min-w-0 flex-1 space-y-3">
          <p className="text-sm text-slate-300">{insights.consistency_insight}</p>
          <p className="text-sm text-slate-400">
            <span className="font-medium text-slate-300">Next milestone: </span>
            {insights.next_milestone}
          </p>
          {insights.ai_summary && (
            <div className="flex items-start gap-2 rounded-lg border border-brand-500/20 bg-brand-500/5 px-3 py-2.5">
              <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-brand-400" />
              <p className="text-sm text-slate-300">{insights.ai_summary}</p>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
