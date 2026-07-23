import { useState } from "react";
import { ChevronDown } from "lucide-react";
import clsx from "clsx";

import { Card, CardBody } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import type { QuestionReportItem } from "@/types/report";
import { formatScore, scoreTone } from "@/utils/score";

const toneMap: Record<ReturnType<typeof scoreTone>, "success" | "warning" | "danger"> = {
  success: "success",
  warning: "warning",
  danger: "danger",
};

export function QuestionBreakdownCard({ item }: { item: QuestionReportItem }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Card>
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
        aria-expanded={isOpen}
      >
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Question {item.question_number} &middot; {item.category}
          </p>
          <p className="mt-1 truncate text-sm font-medium text-slate-100">{item.question}</p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          {item.overall_score !== null && (
            <Badge tone={toneMap[scoreTone(item.overall_score)]}>{formatScore(item.overall_score)}</Badge>
          )}
          <ChevronDown className={clsx("h-4 w-4 text-slate-500 transition-transform", isOpen && "rotate-180")} />
        </div>
      </button>

      {isOpen && (
        <CardBody className="space-y-4 border-t border-surface-700 pt-4">
          <div className="grid grid-cols-3 gap-3 text-center">
            <ScoreChip label="Technical" value={item.technical_score} />
            <ScoreChip label="Communication" value={item.communication_score} />
            <ScoreChip label="Completeness" value={item.completeness_score} />
          </div>

          {item.answer && (
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Your answer</p>
              <p className="mt-1 whitespace-pre-wrap text-sm text-slate-300">{item.answer}</p>
            </div>
          )}

          {item.feedback && (
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">AI feedback</p>
              <p className="mt-1 whitespace-pre-wrap text-sm text-slate-300">{item.feedback}</p>
            </div>
          )}

          {item.improved_answer && (
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Suggested improvement</p>
              <p className="mt-1 whitespace-pre-wrap text-sm text-slate-300">{item.improved_answer}</p>
            </div>
          )}

          {(item.strengths.length > 0 || item.weaknesses.length > 0) && (
            <div className="grid gap-4 sm:grid-cols-2">
              {item.strengths.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-emerald-400/80">Strengths</p>
                  <ul className="mt-1.5 space-y-1 text-sm text-slate-300">
                    {item.strengths.map((strength, index) => (
                      <li key={index}>&bull; {strength}</li>
                    ))}
                  </ul>
                </div>
              )}
              {item.weaknesses.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-red-400/80">Weaknesses</p>
                  <ul className="mt-1.5 space-y-1 text-sm text-slate-300">
                    {item.weaknesses.map((weakness, index) => (
                      <li key={index}>&bull; {weakness}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardBody>
      )}
    </Card>
  );
}

function ScoreChip({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="rounded-lg bg-surface-800 px-2 py-2.5">
      <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-0.5 text-sm font-semibold text-slate-100">{formatScore(value)}</p>
    </div>
  );
}
