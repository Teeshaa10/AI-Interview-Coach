import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus, MessagesSquare } from "lucide-react";

import { interviewApi } from "@/api/interviewApi";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { Card, CardBody } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatDate } from "@/utils/format";

export function InterviewsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["interviews", "history"],
    queryFn: interviewApi.history,
  });

  const interviews = data?.interviews ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Interviews</h1>
          <p className="mt-1 text-sm text-slate-400">Your AI interview history.</p>
        </div>
        <Link to="/interviews/setup">
          <Button>
            <Plus className="h-4 w-4" />
            New interview
          </Button>
        </Link>
      </div>

      {isLoading && <Spinner label="Loading interviews..." />}

      {!isLoading && interviews.length === 0 && (
        <EmptyState
          icon={MessagesSquare}
          title="No interviews yet"
          description="Start your first AI interview to begin practicing."
          action={
            <Link to="/interviews/setup">
              <Button>Start an interview</Button>
            </Link>
          }
        />
      )}

      {interviews.length > 0 && (
        <div className="space-y-3">
          {interviews.map((interview) => (
            <Card key={interview.interview_id}>
              <CardBody className="flex items-center justify-between pt-5">
                <div>
                  <Link
                    to={
                      interview.completed
                        ? `/interviews/${interview.interview_id}/complete`
                        : `/interviews/${interview.interview_id}`
                    }
                    className="text-sm font-medium text-slate-100 hover:text-brand-300"
                  >
                    {interview.job_role}
                  </Link>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {interview.experience_level} &middot; {formatDate(interview.created_at)}
                  </p>
                </div>
                {interview.completed ? (
                  <Badge tone="success">{interview.average_score.toFixed(1)} avg</Badge>
                ) : (
                  <Badge tone="warning">In progress</Badge>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
