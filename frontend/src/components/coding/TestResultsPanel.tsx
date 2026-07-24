import { CheckCircle2, XCircle } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import type { TestExecutionResult } from "@/types/codingInterview";

export function TestResultsPanel({
  results,
  passed,
  total,
}: {
  results: TestExecutionResult[];
  passed: number;
  total: number;
}) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">Test results</h3>
        <span className={`text-sm font-medium ${passed === total ? "text-emerald-400" : "text-amber-400"}`}>
          {passed}/{total} passed
        </span>
      </CardHeader>
      <CardBody className="space-y-2 pt-3">
        {results.map((result, index) => (
          <div
            key={index}
            className="rounded-lg border border-surface-700 bg-surface-800/60 p-3 font-mono text-xs text-slate-300"
          >
            <div className="mb-1.5 flex items-center gap-2 font-sans">
              {result.passed ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              ) : (
                <XCircle className="h-4 w-4 text-red-400" />
              )}
              <span className="font-medium text-slate-200">Test case {index + 1}</span>
            </div>
            <p><span className="text-slate-500">Input:</span> {result.input}</p>
            <p><span className="text-slate-500">Expected:</span> {result.expected_output}</p>
            <p><span className="text-slate-500">Actual:</span> {result.actual_output || "—"}</p>
            {result.stderr && <p className="mt-1 text-red-400">{result.stderr}</p>}
          </div>
        ))}
      </CardBody>
    </Card>
  );
}
