import { Link } from "react-router-dom";
import { PartyPopper } from "lucide-react";

import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";

interface InterviewCompletionCardProps {
  averageScore: number;
  /** Where "Start another interview" points. Defaults to the text-interview setup flow. */
  setupHref?: string;
  /** When provided, renders an extra "View report" link (e.g. to the Module 4 report for this interview). */
  reportHref?: string;
}

export function InterviewCompletionCard({
  averageScore,
  setupHref = "/interviews/setup",
  reportHref,
}: InterviewCompletionCardProps) {
  return (
    <Card>
      <CardBody className="flex flex-col items-center gap-4 py-10 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-500/15">
          <PartyPopper className="h-7 w-7 text-brand-400" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-100">Interview complete</h2>
          <p className="mt-1 text-sm text-slate-400">Here's how you did overall.</p>
        </div>
        <p className="text-4xl font-bold text-brand-300">{averageScore.toFixed(1)}/10</p>
        <div className="flex flex-wrap justify-center gap-3">
          {reportHref && (
            <Link to={reportHref}>
              <Button variant="secondary">View report</Button>
            </Link>
          )}
          <Link to={setupHref}>
            <Button variant="secondary">Start another interview</Button>
          </Link>
          <Link to="/dashboard">
            <Button>Back to dashboard</Button>
          </Link>
        </div>
      </CardBody>
    </Card>
  );
}
