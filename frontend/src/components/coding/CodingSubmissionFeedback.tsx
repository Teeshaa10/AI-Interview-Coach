import { Card, CardBody, CardHeader } from "@/components/common/Card";
import type { CodingSubmission } from "@/types/codingInterview";

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="font-medium text-slate-200">{score.toFixed(0)}</span>
      </div>
      <div className="h-1.5 rounded-full bg-surface-800">
        <div className="h-1.5 rounded-full bg-brand-500" style={{ width: `${Math.min(100, Math.max(0, score))}%` }} />
      </div>
    </div>
  );
}

export function CodingSubmissionFeedback({ submission }: { submission: CodingSubmission }) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">Submission results</h3>
        <span className="text-lg font-semibold text-brand-300">{submission.overall_score.toFixed(0)}</span>
      </CardHeader>
      <CardBody className="space-y-4 pt-3">
        <p className="text-xs text-slate-400">
          {submission.tests_passed}/{submission.tests_total} test cases passed
        </p>

        <div className="grid grid-cols-2 gap-4">
          <ScoreBar label="Correctness" score={submission.correctness_score} />
          <ScoreBar label="Quality" score={submission.quality_score} />
          <ScoreBar label="Complexity" score={submission.complexity_score} />
          <ScoreBar label="Explanation" score={submission.explanation_score} />
        </div>

        {submission.feedback.length > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium text-slate-300">Feedback</p>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-400">
              {submission.feedback.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
