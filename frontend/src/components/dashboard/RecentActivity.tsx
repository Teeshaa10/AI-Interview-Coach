import { Link } from "react-router-dom";
import { MessagesSquare } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/utils/format";
import type { InterviewHistoryItem } from "@/types/interview";

export function RecentActivity({ interviews }: { interviews: InterviewHistoryItem[] }) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-slate-100">Recent interviews</h3>
      </CardHeader>
      <CardBody>
        {interviews.length === 0 ? (
          <EmptyState
            icon={MessagesSquare}
            title="No interviews yet"
            description="Start your first AI interview to see it here."
          />
        ) : (
          <ul className="divide-y divide-surface-700">
            {interviews.slice(0, 5).map((interview) => (
              <li key={interview.interview_id} className="flex items-center justify-between py-3">
                <div>
                  <Link
                    to={interview.completed ? `/interviews/${interview.interview_id}/complete` : `/interviews/${interview.interview_id}`}
                    className="text-sm font-medium text-slate-100 hover:text-brand-300"
                  >
                    {interview.job_role}
                  </Link>
                  <p className="text-xs text-slate-500">
                    {interview.experience_level} &middot; {formatDate(interview.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {interview.completed ? (
                    <Badge tone="success">{interview.average_score.toFixed(1)} avg</Badge>
                  ) : (
                    <Badge tone="warning">In progress</Badge>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}
