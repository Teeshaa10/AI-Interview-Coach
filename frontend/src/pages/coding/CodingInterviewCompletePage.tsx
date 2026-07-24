import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2 } from "lucide-react";

import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { AlertTriangle } from "lucide-react";
import { codingInterviewApi } from "@/api/codingInterviewApi";

/**
 * GET /coding-interviews/{id} returns final_score/completed directly, so
 * unlike InterviewCompletePage this doesn't need to search through a
 * history list.
 */
export function CodingInterviewCompletePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { data: session, isLoading, isError } = useQuery({
    queryKey: ["coding-interviews", sessionId],
    queryFn: () => codingInterviewApi.get(sessionId!),
    enabled: Boolean(sessionId),
  });

  if (isLoading) return <Spinner label="Loading results..." />;

  if (isError || !session) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Results not found"
        description="We couldn't find this coding interview."
      />
    );
  }

  return (
    <div className="mx-auto max-w-xl">
      <Card>
        <CardBody className="flex flex-col items-center gap-4 pt-8 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/15">
            <CheckCircle2 className="h-7 w-7 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-100">Coding interview complete</h1>
            <p className="mt-1 text-sm text-slate-400">
              {session.role} · {session.difficulty}
            </p>
          </div>
          <p className="text-4xl font-semibold text-brand-300">{session.final_score.toFixed(1)}</p>
          <p className="text-xs text-slate-500">Average score across {session.questions.length} question(s)</p>

          <div className="mt-2 flex w-full gap-3">
            <Link to="/coding/setup" className="flex-1">
              <Button variant="secondary" className="w-full">Start another</Button>
            </Link>
            <Link to="/history" className="flex-1">
              <Button className="w-full">View history</Button>
            </Link>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
