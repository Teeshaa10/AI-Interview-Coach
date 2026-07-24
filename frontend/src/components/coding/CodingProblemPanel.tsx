import { Card, CardBody, CardHeader } from "@/components/common/Card";
import type { CodingQuestion } from "@/types/codingInterview";

const difficultyClasses: Record<string, string> = {
  easy: "bg-emerald-500/15 text-emerald-300",
  medium: "bg-amber-500/15 text-amber-300",
  hard: "bg-red-500/15 text-red-300",
};

export function CodingProblemPanel({ question }: { question: CodingQuestion }) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-slate-100">{question.title}</h2>
        <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${difficultyClasses[question.difficulty]}`}>
          {question.difficulty}
        </span>
      </CardHeader>
      <CardBody className="space-y-4 pt-3 text-sm text-slate-300">
        <p className="whitespace-pre-wrap">{question.problem_statement}</p>

        {question.topics.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {question.topics.map((topic) => (
              <span key={topic} className="rounded-full bg-surface-800 px-2.5 py-0.5 text-xs text-slate-400">
                {topic}
              </span>
            ))}
          </div>
        )}

        {question.constraints.length > 0 && (
          <div>
            <p className="mb-1 font-medium text-slate-200">Constraints</p>
            <ul className="list-inside list-disc space-y-0.5 text-slate-400">
              {question.constraints.map((constraint, index) => (
                <li key={index}>{constraint}</li>
              ))}
            </ul>
          </div>
        )}

        {question.examples.length > 0 && (
          <div className="space-y-3">
            <p className="font-medium text-slate-200">Examples</p>
            {question.examples.map((example, index) => (
              <div key={index} className="rounded-lg border border-surface-700 bg-surface-800/60 p-3 font-mono text-xs">
                <p><span className="text-slate-500">Input:</span> {example.input}</p>
                <p><span className="text-slate-500">Output:</span> {example.output}</p>
                {example.explanation && <p className="mt-1 font-sans text-slate-400">{example.explanation}</p>}
              </div>
            ))}
          </div>
        )}

        {(question.expected_complexity.time || question.expected_complexity.space) && (
          <p className="text-xs text-slate-500">
            Expected complexity: {question.expected_complexity.time || "—"} time,{" "}
            {question.expected_complexity.space || "—"} space
          </p>
        )}
      </CardBody>
    </Card>
  );
}
