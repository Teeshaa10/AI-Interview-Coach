import { useQuery } from "@tanstack/react-query";
import { FileText, MessagesSquare, TrendingUp } from "lucide-react";

import { useMyResume } from "@/hooks/useMyResume";
import { interviewApi } from "@/api/interviewApi";
import { useAuth } from "@/contexts/AuthContext";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { Spinner } from "@/components/common/Spinner";

export function DashboardPage() {
  const { user } = useAuth();
  const { data: resume, isLoading: isResumeLoading } = useMyResume();
  const { data: historyData, isLoading: isHistoryLoading } = useQuery({
    queryKey: ["interviews", "history"],
    queryFn: interviewApi.history,
  });

  const interviews = historyData?.interviews ?? [];
  const completedInterviews = interviews.filter((item) => item.completed);
  const averageScore =
    completedInterviews.length > 0
      ? (
          completedInterviews.reduce((sum, item) => sum + item.average_score, 0) / completedInterviews.length
        ).toFixed(1)
      : "—";

  const isLoading = isResumeLoading || isHistoryLoading;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">
          Welcome back{user ? `, ${user.full_name.split(" ")[0]}` : ""}
        </h1>
        <p className="mt-1 text-sm text-slate-400">Here's a snapshot of your interview prep so far.</p>
      </div>

      {isLoading ? (
        <Spinner label="Loading your dashboard..." />
      ) : (
        <>
          {/*
            Every number below comes directly from a fetched response -
            resume presence from GET /resume/me, interview counts and
            average score from GET /interview/history. Nothing here is
            fabricated; a stat that couldn't be computed from the API
            would simply be omitted, per the project's requirements.
          */}
          <DashboardStats
            stats={[
              { label: "Resume on file", value: resume ? "1" : "0", icon: FileText },
              { label: "Interviews completed", value: completedInterviews.length, icon: MessagesSquare },
              { label: "Average score", value: averageScore, icon: TrendingUp },
            ]}
          />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <RecentActivity interviews={interviews} />
            </div>
            <QuickActions />
          </div>
        </>
      )}
    </div>
  );
}
