import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { InterviewCompletionCard } from "@/components/interview/InterviewCompletionCard";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { AlertTriangle } from "lucide-react";
import { interviewApi } from "@/api/interviewApi";

/**
 * There's no GET /interview/{id} to fetch the final score directly, so
 * this reuses GET /interview/history (which does include average_score
 * and completed) and finds this session's row in it.
 */
export function InterviewCompletePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["interviews", "history"],
    queryFn: interviewApi.history,
  });

  if (isLoading) return <Spinner label="Loading results..." />;

  const interview = data?.interviews.find((item) => item.interview_id === sessionId);

  if (!interview) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Results not found"
        description="We couldn't find this interview in your history."
      />
    );
  }

  return (
    <div className="mx-auto max-w-xl">
      <InterviewCompletionCard averageScore={interview.average_score} />
    </div>
  );
}
