import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { coachingApi } from "@/api/coachingApi";
import { getApiErrorMessage } from "@/api/client";
import { CoachingReadinessCard } from "@/components/coaching/CoachingReadinessCard";
import { StrengthsWeaknessesPanel } from "@/components/coaching/StrengthsWeaknessesPanel";
import { NextInterviewRecommendation } from "@/components/coaching/NextInterviewRecommendation";
import { PracticePlanTimeline } from "@/components/coaching/PracticePlanTimeline";
import { ProgressSummary } from "@/components/coaching/ProgressSummary";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { AlertTriangle } from "lucide-react";
import type { PlanDuration } from "@/types/coaching";

export function CoachingDashboardPage() {
  const queryClient = useQueryClient();
  const [togglingItemId, setTogglingItemId] = useState<string | null>(null);

  const profileQuery = useQuery({ queryKey: ["coaching", "profile"], queryFn: coachingApi.profile });
  const insightsQuery = useQuery({ queryKey: ["coaching", "insights"], queryFn: coachingApi.insights });
  const recommendationQuery = useQuery({
    queryKey: ["coaching", "recommendation"],
    queryFn: coachingApi.recommendation,
  });
  const planQuery = useQuery({ queryKey: ["coaching", "plan", "active"], queryFn: coachingApi.activePlan });

  const createPlanMutation = useMutation({
    mutationFn: (duration: PlanDuration) => coachingApi.createPlan({ duration_days: duration }),
    onSuccess: (plan) => {
      queryClient.setQueryData(["coaching", "plan", "active"], plan);
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not generate a practice plan.")),
  });

  const regeneratePlanMutation = useMutation({
    mutationFn: (planId: string) => coachingApi.regeneratePlan(planId),
    onSuccess: (plan) => {
      queryClient.setQueryData(["coaching", "plan", "active"], plan);
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not regenerate the practice plan.")),
  });

  const updateItemMutation = useMutation({
    mutationFn: ({ planId, itemId, completed }: { planId: string; itemId: string; completed: boolean }) =>
      coachingApi.updatePlanItem(planId, itemId, { completed }),
    onMutate: ({ itemId }) => setTogglingItemId(itemId),
    onSuccess: (plan) => {
      queryClient.setQueryData(["coaching", "plan", "active"], plan);
    },
    onError: (error) => toast.error(getApiErrorMessage(error, "Could not update that session.")),
    onSettled: () => setTogglingItemId(null),
  });

  const isLoading =
    profileQuery.isLoading || insightsQuery.isLoading || recommendationQuery.isLoading || planQuery.isLoading;

  const hasError = profileQuery.isError || insightsQuery.isError || recommendationQuery.isError;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">AI Coach</h1>
        <p className="mt-1 text-sm text-slate-400">
          Personalized readiness, recommendations, and a practice plan built from your session history.
        </p>
      </div>

      {isLoading ? (
        <Spinner label="Loading your coaching dashboard..." />
      ) : hasError ? (
        <EmptyState
          icon={AlertTriangle}
          title="Could not load your coaching data"
          description={getApiErrorMessage(
            profileQuery.error ?? insightsQuery.error ?? recommendationQuery.error,
            "Something went wrong loading the coaching dashboard.",
          )}
        />
      ) : (
        <>
          {insightsQuery.data && <CoachingReadinessCard insights={insightsQuery.data} />}

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {recommendationQuery.data && (
              <NextInterviewRecommendation recommendation={recommendationQuery.data} />
            )}
            {insightsQuery.data && <StrengthsWeaknessesPanel insights={insightsQuery.data} />}
          </div>

          <PracticePlanTimeline
            plan={planQuery.data}
            isLoading={planQuery.isLoading}
            onCreatePlan={(duration) => createPlanMutation.mutate(duration)}
            isCreating={createPlanMutation.isPending}
            onRegeneratePlan={() => {
              if (planQuery.data) regeneratePlanMutation.mutate(planQuery.data.id);
            }}
            isRegenerating={regeneratePlanMutation.isPending}
            onToggleItem={(itemId, completed) => {
              if (planQuery.data) updateItemMutation.mutate({ planId: planQuery.data.id, itemId, completed });
            }}
            togglingItemId={togglingItemId}
          />

          {profileQuery.data && <ProgressSummary profile={profileQuery.data} />}
        </>
      )}
    </div>
  );
}
