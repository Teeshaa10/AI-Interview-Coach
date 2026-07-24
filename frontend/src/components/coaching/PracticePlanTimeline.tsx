import { useState } from "react";
import { Calendar, Check, RefreshCw } from "lucide-react";
import clsx from "clsx";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import { PLAN_DURATIONS, type PlanDuration, type PracticePlanResponse } from "@/types/coaching";

interface PracticePlanTimelineProps {
  plan: PracticePlanResponse | null | undefined;
  isLoading: boolean;
  onCreatePlan: (duration: PlanDuration) => void;
  isCreating: boolean;
  onRegeneratePlan: () => void;
  isRegenerating: boolean;
  onToggleItem: (itemId: string, completed: boolean) => void;
  togglingItemId: string | null;
}

export function PracticePlanTimeline({
  plan,
  isLoading,
  onCreatePlan,
  isCreating,
  onRegeneratePlan,
  isRegenerating,
  onToggleItem,
  togglingItemId,
}: PracticePlanTimelineProps) {
  const [selectedDuration, setSelectedDuration] = useState<PlanDuration>(7);

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">Practice plan</h3>
        {plan && (
          <Button variant="ghost" size="sm" onClick={onRegeneratePlan} isLoading={isRegenerating}>
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate
          </Button>
        )}
      </CardHeader>
      <CardBody>
        {isLoading ? (
          <Spinner label="Loading your practice plan..." />
        ) : !plan ? (
          <EmptyState
            icon={Calendar}
            title="No active practice plan"
            description="Generate a personalized, day-by-day plan built from your practice history."
            action={
              <div className="flex flex-col items-center gap-3">
                <div className="flex gap-2">
                  {PLAN_DURATIONS.map((duration) => (
                    <button
                      key={duration}
                      onClick={() => setSelectedDuration(duration)}
                      className={clsx(
                        "rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors",
                        selectedDuration === duration
                          ? "border-brand-500/40 bg-brand-500/10 text-brand-300"
                          : "border-surface-600 text-slate-400 hover:border-surface-500",
                      )}
                    >
                      {duration} days
                    </button>
                  ))}
                </div>
                <Button variant="primary" onClick={() => onCreatePlan(selectedDuration)} isLoading={isCreating}>
                  Generate plan
                </Button>
              </div>
            }
          />
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-slate-400">
              <span>
                {plan.completed_items} of {plan.total_items} sessions complete
              </span>
              <span>{plan.completion_percentage}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-surface-700">
              <div
                className="h-full rounded-full bg-brand-500 transition-all duration-500"
                style={{ width: `${plan.completion_percentage}%` }}
              />
            </div>

            <ul className="divide-y divide-surface-700">
              {plan.items
                .slice()
                .sort((a, b) => a.day_number - b.day_number)
                .map((item) => (
                  <li key={item.item_id} className="flex items-start gap-3 py-3.5">
                    <button
                      onClick={() => onToggleItem(item.item_id, !item.completed)}
                      disabled={togglingItemId === item.item_id}
                      aria-label={item.completed ? "Mark as not completed" : "Mark as completed"}
                      className={clsx(
                        "mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition-colors",
                        item.completed
                          ? "border-emerald-500 bg-emerald-500/20 text-emerald-400"
                          : "border-surface-600 text-transparent hover:border-slate-400",
                        togglingItemId === item.item_id && "opacity-50",
                      )}
                    >
                      <Check className="h-3 w-3" />
                    </button>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-medium text-slate-500">Day {item.day_number}</span>
                        <Badge tone="neutral">{item.interview_type}</Badge>
                        <Badge tone="neutral">{item.difficulty}</Badge>
                        <span className="text-xs text-slate-500">{item.estimated_minutes} min</span>
                      </div>
                      <p
                        className={clsx(
                          "mt-1 text-sm font-medium",
                          item.completed ? "text-slate-500 line-through" : "text-slate-100",
                        )}
                      >
                        {item.objective}
                      </p>
                      <p className="mt-0.5 text-sm text-slate-400">{item.recommended_activity}</p>
                      {item.reason && <p className="mt-0.5 text-xs text-slate-500">{item.reason}</p>}
                    </div>
                  </li>
                ))}
            </ul>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
