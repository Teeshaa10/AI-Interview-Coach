import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { ArrowRight, LogOut, AlertTriangle } from "lucide-react";

import { QuestionCard } from "@/components/interview/QuestionCard";
import { AnswerFeedback } from "@/components/interview/AnswerFeedback";
import { InterviewProgress } from "@/components/interview/InterviewProgress";
import { InterviewTimer } from "@/components/interview/InterviewTimer";
import { ExitInterviewDialog } from "@/components/interview/ExitInterviewDialog";
import { VoiceAnswerRecorder } from "@/components/voice/VoiceAnswerRecorder";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { interviewApi } from "@/api/interviewApi";
import { voiceApi } from "@/api/voiceApi";
import { getApiErrorMessage } from "@/api/client";
import { getAudioFileExtension } from "@/utils/audio";
import { loadInterviewState, saveInterviewState, clearInterviewState } from "@/utils/interviewSession";
import type { InterviewQuestion } from "@/types/interview";

export function VoiceInterviewSessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [questions, setQuestions] = useState<InterviewQuestion[] | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [isExitDialogOpen, setIsExitDialogOpen] = useState(false);

  // Same recovery strategy as the text interview session page: the
  // backend has no GET endpoint for an in-progress interview, so the
  // question/answer state is recovered from sessionStorage. An empty
  // result means this session can't be recovered (new tab, expired
  // storage, or an invalid/unknown session id).
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
    return <Spinner label="Loading voice interview..." />;
  }

  if (questions.length === 0) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="This interview session can't be recovered"
        description="It looks like this interview wasn't started in this browser tab, has already been completed, or the page data expired. Start a new one instead."
        action={<Button onClick={() => navigate("/voice/setup")}>Start a new voice interview</Button>}
      />
    );
  }

  const currentQuestion = questions[currentIndex];
  const isLastQuestion = currentIndex === questions.length - 1;
  const isAnswered = Boolean(currentQuestion.feedback);

  const persist = (updatedQuestions: InterviewQuestion[], index: number) => {
    setQuestions(updatedQuestions);
    setCurrentIndex(index);
    saveInterviewState({ interviewId: sessionId, questions: updatedQuestions, currentIndex: index });
  };

  const handleRecordingSubmit = async (audioBlob: Blob, mimeType: string) => {
    if (isSubmittingAnswer || isAnswered) return; // guard against duplicate submission
    setIsSubmittingAnswer(true);
    try {
      const extension = getAudioFileExtension(mimeType);
      const filename = `answer-q${currentQuestion.question_number}.${extension}`;
      const response = await voiceApi.submitAnswer(
        sessionId,
        currentQuestion.question_number,
        audioBlob,
        filename,
      );
      const updated = [...questions];
      updated[currentIndex] = response.question;
      persist(updated, currentIndex);
    } catch (error) {
      toast.error(
        getApiErrorMessage(
          error,
          "Could not upload and process your recording. Please try recording your answer again.",
        ),
      );
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
      navigate(`/voice/${sessionId}/complete`);
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
        <InterviewProgress current={currentIndex + 1} total={questions.length} category={currentQuestion.category} />
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

      {isAnswered ? (
        <div className="space-y-4">
          {currentQuestion.answer && (
            <Card>
              <CardBody className="pt-5">
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Your answer (transcribed)
                </p>
                <p className="text-sm leading-relaxed text-slate-300">{currentQuestion.answer}</p>
              </CardBody>
            </Card>
          )}

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
        <VoiceAnswerRecorder onSubmit={handleRecordingSubmit} isSubmitting={isSubmittingAnswer} />
      )}

      <ExitInterviewDialog
        isOpen={isExitDialogOpen}
        onCancel={() => setIsExitDialogOpen(false)}
        onConfirm={handleExitConfirmed}
      />
    </div>
  );
}
