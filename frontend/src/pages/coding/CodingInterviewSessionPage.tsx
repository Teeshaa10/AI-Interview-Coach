import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { AlertTriangle, ArrowRight, Play } from "lucide-react";

import { CodingProblemPanel } from "@/components/coding/CodingProblemPanel";
import { CodeEditor } from "@/components/coding/CodeEditor";
import { TestResultsPanel } from "@/components/coding/TestResultsPanel";
import { CodingSubmissionFeedback } from "@/components/coding/CodingSubmissionFeedback";
import { Textarea } from "@/components/common/FormControls";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { codingInterviewApi } from "@/api/codingInterviewApi";
import { getApiErrorMessage } from "@/api/client";
import type {
  CodingRunResponse,
  CodingSubmission,
} from "@/types/codingInterview";

/**
 * Unlike the text-interview module, GET /coding-interviews/{id} DOES
 * return the full question set (see types/codingInterview.ts doc-comment),
 * so this session is safely resumable after a refresh - no sessionStorage
 * needed here.
 */
export function CodingInterviewSessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    data: session,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["coding-interviews", sessionId],
    queryFn: () => codingInterviewApi.get(sessionId!),
    enabled: Boolean(sessionId),
  });

  const [currentIndex, setCurrentIndex] = useState(0);
  const [code, setCode] = useState("");
  const [explanation, setExplanation] = useState("");
  const [runResult, setRunResult] = useState<CodingRunResponse | null>(null);
  const [submission, setSubmission] = useState<CodingSubmission | null>(null);
  const [isSubmitting] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);

  const currentQuestion = session?.questions[currentIndex];

  useEffect(() => {
    if (!currentQuestion) return;

    setCode(currentQuestion.starter_code[session!.language] ?? "");
    setExplanation("");
    setRunResult(null);
    setSubmission(null);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentQuestion?.question_number]);

  if (!sessionId) return null;

  if (isLoading) {
    return <Spinner label="Loading coding interview..." />;
  }

  if (isError || !session) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="This session can't be loaded"
        description="It may not exist, or you may not have access to it."
        action={
          <Button onClick={() => navigate("/coding/setup")}>
            Start a new coding interview
          </Button>
        }
      />
    );
  }

  if (session.completed) {
    navigate(`/coding/${sessionId}/complete`, { replace: true });
    return null;
  }

  if (!currentQuestion) return null;

  const isLastQuestion =
    currentIndex === session.questions.length - 1;

  const handleRun = () => {
    toast(
      "Code execution is temporarily unavailable in this demo environment. The coding module is integrated with a pluggable Judge0/Piston execution provider and can be enabled when the sandbox service is deployed.",
      {
        duration: 7000,
        icon: "ℹ️",
      },
    );
  };

  const handleSubmit = () => {
    toast(
      "Solution submission is temporarily unavailable in this demo environment because the sandbox execution service is not currently deployed.",
      {
        duration: 7000,
        icon: "ℹ️",
      },
    );
  };

  const handleNext = () => {
    setCurrentIndex((index) => index + 1);
  };

  const handleFinish = async () => {
    setIsFinishing(true);

    try {
      await codingInterviewApi.complete(sessionId);

      queryClient.removeQueries({
        queryKey: ["coding-interviews", sessionId],
      });

      navigate(`/coding/${sessionId}/complete`);
    } catch (error) {
      toast.error(
        getApiErrorMessage(error, "Could not finish the interview."),
      );
    } finally {
      setIsFinishing(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          Question {currentIndex + 1} of {session.questions.length}
        </p>

        <p className="text-xs text-slate-500">
          {session.role} · {session.difficulty}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <CodingProblemPanel question={currentQuestion} />

        <div className="space-y-4">
          <CodeEditor
            value={code}
            onChange={setCode}
            language={session.language}
            disabled={Boolean(submission)}
          />

          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={handleRun}
              disabled={Boolean(submission)}
            >
              <Play className="h-4 w-4" />
              Run code
            </Button>

            {!submission && (
              <Button
                onClick={handleSubmit}
                isLoading={isSubmitting}
                className="flex-1"
              >
                Submit solution
              </Button>
            )}
          </div>

          {!submission && (
            <Textarea
              label="Explain your approach (optional)"
              placeholder="Briefly describe your approach and complexity..."
              value={explanation}
              onChange={(event) =>
                setExplanation(event.target.value)
              }
            />
          )}

          {runResult && !submission && (
            <TestResultsPanel
              results={runResult.test_results}
              passed={runResult.tests_passed}
              total={runResult.tests_total}
            />
          )}

          {submission && (
            <>
              <CodingSubmissionFeedback submission={submission} />

              {isLastQuestion ? (
                <Button
                  className="w-full"
                  onClick={handleFinish}
                  isLoading={isFinishing}
                >
                  Finish interview
                </Button>
              ) : (
                <Button
                  className="w-full"
                  onClick={handleNext}
                >
                  Next question
                  <ArrowRight className="h-4 w-4" />
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}