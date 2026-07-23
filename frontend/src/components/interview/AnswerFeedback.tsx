import { CheckCircle2, XCircle } from "lucide-react";

import { Card, CardBody } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import type { InterviewQuestion } from "@/types/interview";

export function AnswerFeedback({ question }: { question: InterviewQuestion }) {
  return (
    <Card>
      <CardBody className="space-y-4 pt-5">
        <div className="flex flex-wrap items-center gap-2">
          {question.overall_score !== null && (
            <Badge tone="brand">Overall: {question.overall_score.toFixed(1)}/10</Badge>
          )}
          {question.technical_score !== null && <Badge>Technical: {question.technical_score.toFixed(1)}</Badge>}
          {question.communication_score !== null && (
            <Badge>Communication: {question.communication_score.toFixed(1)}</Badge>
          )}
          {question.completeness_score !== null && (
            <Badge>Completeness: {question.completeness_score.toFixed(1)}</Badge>
          )}
        </div>

        {question.feedback && <p className="text-sm leading-relaxed text-slate-200">{question.feedback}</p>}

        {question.strengths.length > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">Strengths</p>
            <ul className="space-y-1">
              {question.strengths.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {question.weaknesses.length > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
              Areas to improve
            </p>
            <ul className="space-y-1">
              {question.weaknesses.map((item, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
                  <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {question.better_answer && (
          <div className="rounded-lg bg-surface-950 p-4">
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
              A stronger answer
            </p>
            <p className="text-sm leading-relaxed text-slate-300">{question.better_answer}</p>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
