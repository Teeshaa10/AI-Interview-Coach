import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { ArrowRight, LogOut } from "lucide-react";

import { QuestionCard } from "@/components/interview/QuestionCard";
import { AnswerEditor } from "@/components/interview/AnswerEditor";
import { AnswerFeedback } from "@/components/interview/AnswerFeedback";
import { InterviewProgress } from "@/components/interview/InterviewProgress";
import { InterviewTimer } from "@/components/interview/InterviewTimer";
import { ExitInterviewDialog } from "@/components/interview/ExitInterviewDialog";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { AlertTriangle } from "lucide-react";
import { interviewApi } from "@/api/interviewApi";
import { getApiErrorMessage } from "@/api/client";
import { loadInterviewState, saveInterviewState, clearInterviewState } from "@/utils/interviewSession";
import type { InterviewQuestion } from "@/types/interview";

export function InterviewSessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [questions, setQuestions] = useState<InterviewQuestion[] | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [isExitDialogOpen, setIsExitDialogOpen] = useState(false);

  // Recover in-progress state from sessionStorage. The backend has no
  // endpoint to re-fetch a session, so if this is empty (e.g. a fresh tab
  // that never called /interview/start), we can't recover and send the
  // person back to set up a new interview.
  useEffect(() => {
    if (!sessionId) return;
    const stored = loadInterviewState(sessionId);
    if (stored) {
      setQuestions(stored.questions);
      setCurrentIndex(stored.currentIndex);
    } else {
      setQuestions([]);
    }
  }, [sessionId]);

  // Warn before an accidental tab close/refresh mid-interview.
  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  if (!sessionId) return null;

  if (questions === null) {
    return <Spinner label="Loading interview..." />;
  }

  if (questions.length === 0) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="This interview session can't be recovered"
        description="It looks like this interview wasn't started in this browser tab, or the page data expired. Start a new one instead."
        action={
          <Button onClick={() => navigate("/interviews/setup")}>
            Start a new interview
          </Button>
        }
      />
    );
  }

  const currentQuestion = questions[currentIndex];
  const isLastQuestion = currentIndex === questions.length - 1;

  const persist = (updatedQuestions: InterviewQuestion[], index: number) => {
    setQuestions(updatedQuestions);
    setCurrentIndex(index);
    saveInterviewState({ interviewId: sessionId, questions: updatedQuestions, currentIndex: index });
  };

  const handleAnswerSubmit = async (answer: string) => {
    setIsSubmittingAnswer(true);
    try {
      const response = await interviewApi.submitAnswer(sessionId, {
        question_number: currentQuestion.question_number,
        answer,
      });
      const updated = [...questions];
      updated[currentIndex] = response.question;
      persist(updated, currentIndex);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not submit your answer."));
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleNext = () => {
    persist(questions, currentIndex + 1);
  };

  const handleFinish = async () => {
    setIsFinishing(true);
    try {
      await interviewApi.finish(sessionId);
      clearInterviewState(sessionId);
      navigate(`/interviews/${sessionId}/complete`);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not finish the interview."));
    } finally {
      setIsFinishing(false);
    }
  };

  const handleExitConfirmed = () => {
    setIsExitDialogOpen(false);
    navigate("/dashboard");
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <InterviewProgress
          current={currentIndex + 1}
          total={questions.length}
          category={currentQuestion.category}
        />
      </div>

      <div className="flex items-center justify-between">
        <InterviewTimer resetKey={currentQuestion.question_number} />
        <button
          onClick={() => setIsExitDialogOpen(true)}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-red-400"
        >
          <LogOut className="h-3.5 w-3.5" />
          Exit interview
        </button>
      </div>

      <QuestionCard question={currentQuestion.question} />

      {currentQuestion.feedback ? (
        <div className="space-y-4">
          <AnswerFeedback question={currentQuestion} />
          {isLastQuestion ? (
            <Button className="w-full" onClick={handleFinish} isLoading={isFinishing}>
              Finish interview
            </Button>
          ) : (
            <Button className="w-full" onClick={handleNext}>
              Next question
              <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      ) : (
        <AnswerEditor onSubmit={handleAnswerSubmit} isSubmitting={isSubmittingAnswer} />
      )}

      <ExitInterviewDialog
        isOpen={isExitDialogOpen}
        onCancel={() => setIsExitDialogOpen(false)}
        onConfirm={handleExitConfirmed}
      />
    </div>
  );
}
