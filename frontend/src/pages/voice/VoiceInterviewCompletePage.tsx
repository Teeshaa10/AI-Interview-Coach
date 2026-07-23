import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";

import { InterviewCompletionCard } from "@/components/interview/InterviewCompletionCard";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { interviewApi } from "@/api/interviewApi";

/**
 * Same approach as InterviewCompletePage (Module 3): there's no
 * GET /interview/{id}, so the finished session's score is read from
 * GET /interview/history, matched by interview_id.
 */
export function VoiceInterviewCompletePage() {
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
        description="We couldn't find this voice interview in your history."
      />
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <InterviewCompletionCard
        averageScore={interview.average_score}
        setupHref="/voice/setup"
        reportHref={sessionId ? `/reports/interview/${sessionId}` : undefined}
      />
      <p className="text-center text-sm text-slate-400">
        {interview.job_role} &middot; {interview.experience_level}
      </p>
    </div>
  );
}
