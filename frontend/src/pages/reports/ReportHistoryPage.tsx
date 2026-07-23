import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { BarChart3 } from "lucide-react";

import { interviewApi } from "@/api/interviewApi";
import { reportApi } from "@/api/reportApi";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card, CardBody } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import { formatDate } from "@/utils/format";
import { scoreTone } from "@/utils/score";

export function ReportHistoryPage() {
  const { data: interviewData, isLoading: isInterviewsLoading } = useQuery({
    queryKey: ["interviews", "history"],
    queryFn: interviewApi.history,
  });

  const { data: reportData, isLoading: isReportsLoading } = useQuery({
    queryKey: ["reports", "history"],
    queryFn: () => reportApi.history(1, 100),
  });

  const isLoading = isInterviewsLoading || isReportsLoading;
  const interviews = interviewData?.interviews ?? [];
  const reportsByInterviewId = new Map((reportData?.reports ?? []).map((report) => [report.interview_id, report]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Interview history</h1>
        <p className="mt-1 text-sm text-slate-400">Every interview you've taken, with its report status.</p>
      </div>

      {isLoading && <Spinner label="Loading history..." />}

      {!isLoading && interviews.length === 0 && (
        <EmptyState
          icon={BarChart3}
          title="No interview history yet"
          description="Complete an interview to start building your report history."
        />
      )}

      {!isLoading && interviews.length > 0 && (
        <div className="space-y-3">
          {interviews.map((interview) => {
            const report = reportsByInterviewId.get(interview.interview_id);
            const displayScore = report ? report.overall_score : interview.average_score;

            return (
              <Card key={interview.interview_id}>
                <CardBody className="flex flex-wrap items-center justify-between gap-4 pt-5">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-100">{interview.job_role}</p>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {interview.experience_level} &middot; {formatDate(interview.created_at)}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    {interview.completed ? (
                      <Badge tone={scoreTone(displayScore)}>{displayScore.toFixed(1)} avg</Badge>
                    ) : (
                      <Badge tone="warning">In progress</Badge>
                    )}
                    {report && <Badge tone="brand">Report ready</Badge>}

                    {interview.completed ? (
                      <Link to={`/reports/interview/${interview.interview_id}`}>
                        <Button variant="secondary" size="sm">
                          {report ? "View report" : "Generate report"}
                        </Button>
                      </Link>
                    ) : (
                      <Button variant="secondary" size="sm" disabled>
                        View report
                      </Button>
                    )}
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
