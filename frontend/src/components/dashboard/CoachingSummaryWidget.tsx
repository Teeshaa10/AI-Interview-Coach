import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Brain } from "lucide-react";

import { coachingApi } from "@/api/coachingApi";
import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Spinner } from "@/components/common/Spinner";
import { READINESS_LABELS, type ReadinessLevel } from "@/types/coaching";

const READINESS_TONE: Record<ReadinessLevel, "neutral" | "warning" | "brand" | "success"> = {
  getting_started: "neutral",
  building_confidence: "warning",
  interview_ready: "brand",
  highly_prepared: "success",
};

/**
 * Compact coaching summary for the main dashboard. Intentionally light -
 * just readiness + next milestone, with a link to the full
 * CoachingDashboardPage for everything else (strengths, recommendation,
 * practice plan). Loading and no-history states are handled here rather
 * than duplicating the full dashboard's empty-state logic.
 */
export function CoachingSummaryWidget() {
  const { data: insights, isLoading, isError } = useQuery({
    queryKey: ["coaching", "insights"],
    queryFn: coachingApi.insights,
  });

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-brand-400" />
          <h3 className="text-sm font-semibold text-slate-100">AI Coach</h3>
        </div>
        {insights && <Badge tone={READINESS_TONE[insights.readiness_level]}>{READINESS_LABELS[insights.readiness_level]}</Badge>}
      </CardHeader>
      <CardBody className="space-y-3">
        {isLoading ? (
          <Spinner label="Loading readiness..." />
        ) : isError || !insights ? (
          <p className="text-sm text-slate-500">Couldn't load your coaching summary right now.</p>
        ) : (
          <p className="text-sm text-slate-400">{insights.next_milestone}</p>
        )}

        <Link
          to="/coaching"
          className="flex items-center gap-1.5 text-sm font-medium text-brand-300 hover:text-brand-200"
        >
          Open AI Coach
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </CardBody>
    </Card>
  );
}
