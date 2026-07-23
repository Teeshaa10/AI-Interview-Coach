import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { ArrowLeft, BarChart3, Download, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";

import { reportApi } from "@/api/reportApi";
import { getApiErrorMessage } from "@/api/client";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import { ScoreSummaryGrid } from "@/components/reports/ScoreSummaryGrid";
import { RadarScoreChart } from "@/components/reports/RadarScoreChart";
import { StrengthWeaknessList } from "@/components/reports/StrengthWeaknessList";
import { QuestionBreakdownCard } from "@/components/reports/QuestionBreakdownCard";
import { formatDateTime } from "@/utils/format";
import { exportReportToPdf } from "@/utils/reportPdf";

export function ReportDetailPage() {
  const { interviewId } = useParams<{ interviewId: string }>();
  const queryClient = useQueryClient();
  const [isRegenerating, setIsRegenerating] = useState(false);

  const {
    data: report,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["reports", "byInterview", interviewId],
    queryFn: () => reportApi.getByInterview(interviewId as string),
    enabled: Boolean(interviewId),
    retry: false,
  });

  const generateMutation = useMutation({
    mutationFn: (regenerate: boolean) => reportApi.generate(interviewId as string, regenerate),
    onSuccess: (data) => {
      queryClient.setQueryData(["reports", "byInterview", interviewId], data);
      toast.success(isRegenerating ? "Report regenerated." : "Report generated.");
      setIsRegenerating(false);
    },
    onError: (mutationError: unknown) => {
      toast.error(getApiErrorMessage(mutationError, "Could not generate the report."));
      setIsRegenerating(false);
    },
  });

  const reportNotFound = axios.isAxiosError(error) && error.response?.status === 404;

  if (!interviewId) {
    return (
      <EmptyState icon={BarChart3} title="Missing interview" description="No interview was specified." />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            to="/reports/history"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-slate-200"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to history
          </Link>
          <h1 className="mt-2 text-xl font-semibold text-slate-100">Interview report</h1>
        </div>

        {report && (
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              isLoading={generateMutation.isPending && isRegenerating}
              onClick={() => {
                setIsRegenerating(true);
                generateMutation.mutate(true);
              }}
            >
              <RefreshCw className="h-4 w-4" />
              Regenerate
            </Button>
            <Button size="sm" onClick={() => exportReportToPdf(report)}>
              <Download className="h-4 w-4" />
              Export PDF
            </Button>
          </div>
        )}
      </div>

      {isLoading && <Spinner label="Loading report..." />}

      {!isLoading && reportNotFound && (
        <EmptyState
          icon={BarChart3}
          title="No report yet"
          description="This interview doesn't have a generated report yet. Generate one from its results."
          action={
            <Button
              isLoading={generateMutation.isPending && !isRegenerating}
              onClick={() => {
                setIsRegenerating(false);
                generateMutation.mutate(false);
              }}
            >
              Generate report
            </Button>
          }
        />
      )}

      {!isLoading && error && !reportNotFound && (
        <EmptyState
          icon={BarChart3}
          title="Couldn't load this report"
          description={getApiErrorMessage(error, "Something went wrong while fetching this report.")}
        />
      )}

      {!isLoading && report && (
        <>
          <Card>
            <CardBody className="flex flex-wrap items-center justify-between gap-4 pt-5">
              <div>
                <p className="text-sm font-medium text-slate-100">{report.job_role}</p>
                <p className="mt-0.5 text-xs text-slate-500">
                  {report.experience_level}
                  {report.interview_completed_at ? ` \u00b7 ${formatDateTime(report.interview_completed_at)}` : ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge tone="brand">{report.recommended_next_difficulty}</Badge>
                <Badge tone="neutral">
                  {report.answered_questions}/{report.total_questions} answered
                </Badge>
              </div>
            </CardBody>
          </Card>

          <ScoreSummaryGrid
            overallScore={report.overall_score}
            technicalScore={report.technical_score}
            communicationScore={report.communication_score}
            completenessScore={report.completeness_score}
          />

          {report.summary && (
            <Card>
              <CardHeader>
                <h2 className="text-sm font-semibold text-slate-100">Summary</h2>
              </CardHeader>
              <CardBody>
                <p className="whitespace-pre-wrap text-sm text-slate-300">{report.summary}</p>
              </CardBody>
            </Card>
          )}

          <RadarScoreChart
            data={
              Object.keys(report.category_scores).length > 0
                ? Object.entries(report.category_scores).map(([axis, score]) => ({ axis, score }))
                : [
                    { axis: "Technical", score: report.technical_score },
                    { axis: "Communication", score: report.communication_score },
                    { axis: "Completeness", score: report.completeness_score },
                  ]
            }
          />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <StrengthWeaknessList
              title="Strengths"
              items={report.strengths}
              tone="success"
              emptyLabel="No specific strengths were identified."
            />
            <StrengthWeaknessList
              title="Weaknesses"
              items={report.weaknesses}
              tone="danger"
              emptyLabel="No specific weaknesses were identified."
            />
          </div>

          {report.improvement_plan.length > 0 && (
            <Card>
              <CardHeader>
                <h2 className="text-sm font-semibold text-slate-100">Improvement plan</h2>
              </CardHeader>
              <CardBody>
                <ol className="list-decimal space-y-2 pl-4 text-sm text-slate-300">
                  {report.improvement_plan.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>
              </CardBody>
            </Card>
          )}

          {report.question_breakdown.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-slate-100">Question-by-question breakdown</h2>
              {report.question_breakdown.map((item) => (
                <QuestionBreakdownCard key={item.question_number} item={item} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
