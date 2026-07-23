import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { InterviewSetupForm } from "@/components/interview/InterviewSetupForm";
import { interviewApi } from "@/api/interviewApi";
import { getApiErrorMessage } from "@/api/client";
import { saveInterviewState } from "@/utils/interviewSession";
import type { InterviewSetupFormValues } from "@/schemas/interviewSchemas";

export function InterviewSetupPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values: InterviewSetupFormValues) => {
    setIsSubmitting(true);
    try {
      const response = await interviewApi.start(values);
      saveInterviewState({
        interviewId: response.interview_id,
        questions: response.questions,
        currentIndex: 0,
      });
      navigate(`/interviews/${response.interview_id}`);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not start the interview."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Set up your interview</h1>
        <p className="mt-1 text-sm text-slate-400">
          Questions are generated from your resume and the role you're targeting.
        </p>
      </div>
      <InterviewSetupForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
    </div>
  );
}
