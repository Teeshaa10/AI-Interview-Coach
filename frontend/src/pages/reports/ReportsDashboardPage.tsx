import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, History } from "lucide-react";

import { reportApi } from "@/api/reportApi";
import { Button } from "@/components/common/Button";
import { Card, CardBody } from "@/components/common/Card";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { ScoreSummaryGrid } from "@/components/reports/ScoreSummaryGrid";
import { ScoreHistoryChart } from "@/components/reports/ScoreHistoryChart";
import { RadarScoreChart } from "@/components/reports/RadarScoreChart";
import { ProgressChart } from "@/components/reports/ProgressChart";
import { StrengthWeaknessList } from "@/components/reports/StrengthWeaknessList";
import { UnifiedOverviewPanel } from "@/components/dashboard/UnifiedOverviewPanel";

export function ReportsDashboardPage() {
  const { data: summary, isLoading: isSummaryLoading, isError: isSummaryError } = useQuery({
    queryKey: ["reports", "analytics", "summary"],
    queryFn: reportApi.analyticsSummary,
  });

  const { data: trends, isLoading: isTrendsLoading } = useQuery({
    queryKey: ["reports", "analytics", "trends", "weekly"],
    queryFn: () => reportApi.analyticsTrends("weekly"),
  });

  const isLoading = isSummaryLoading || isTrendsLoading;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">Reports</h1>
          <p className="mt-1 text-sm text-slate-400">Your interview performance at a glance.</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/history">
            <Button variant="secondary">
              <History className="h-4 w-4" />
              Unified history
            </Button>
          </Link>
          <Link to="/reports/history">
            <Button variant="secondary">View all reports</Button>
          </Link>
        </div>
      </div>

      <UnifiedOverviewPanel />

      {isLoading && <Spinner label="Loading your analytics..." />}

      {isSummaryError && !isLoading && (
        <EmptyState
          icon={BarChart3}
          title="Couldn't load analytics"
          description="Something went wrong while fetching your report analytics. Please try again."
        />
      )}

      {!isLoading && !isSummaryError && summary && (
        <>
          {summary.interviews_completed === 0 ? (
            <EmptyState
              icon={BarChart3}
              title="No reports yet"
              description="Complete an interview and generate a report to see your analytics here."
              action={
                <Link to="/interviews/setup">
                  <Button>Start an interview</Button>
                </Link>
              }
            />
          ) : (
            <>
              <ScoreSummaryGrid
                overallScore={summary.average_overall_score}
                technicalScore={summary.technical_average}
                communicationScore={summary.communication_average}
                completenessScore={summary.completeness_average}
              />

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <Card>
                  <CardBody className="pt-5">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Interviews reported
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-slate-100">{summary.interviews_completed}</p>
                  </CardBody>
                </Card>
                <Card>
                  <CardBody className="pt-5">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Best score</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-100">{summary.best_score.toFixed(1)}</p>
                  </CardBody>
                </Card>
                <Card>
                  <CardBody className="pt-5">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Recent improvement
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-slate-100">
                      {summary.recent_improvement_percentage === null
                        ? "\u2014"
                        : `${summary.recent_improvement_percentage > 0 ? "+" : ""}${summary.recent_improvement_percentage.toFixed(1)}%`}
                    </p>
                  </CardBody>
                </Card>
              </div>

              <ScoreHistoryChart points={summary.score_trend} />

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <RadarScoreChart
                  title="Average category scores"
                  data={[
                    { axis: "Technical", score: summary.technical_average },
                    { axis: "Communication", score: summary.communication_average },
                    { axis: "Completeness", score: summary.completeness_average },
                  ]}
                />
                <ProgressChart points={trends?.points ?? []} />
              </div>

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <StrengthWeaknessList
                  title="Strongest topics"
                  items={summary.strongest_topics}
                  tone="success"
                  emptyLabel="No recurring strengths identified yet."
                />
                <StrengthWeaknessList
                  title="Topics to improve"
                  items={summary.weakest_topics}
                  tone="danger"
                  emptyLabel="No recurring weak spots identified yet."
                />
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
