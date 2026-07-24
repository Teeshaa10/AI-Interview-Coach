import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { InterviewSetupForm } from "@/components/interview/InterviewSetupForm";
import { interviewApi } from "@/api/interviewApi";
import { getApiErrorMessage } from "@/api/client";
import { saveInterviewState } from "@/utils/interviewSession";
import type { InterviewSetupFormValues } from "@/schemas/interviewSchemas";

/**
 * There is no separate "start voice interview" endpoint - a voice
 * interview is the same POST /interview/start session as the text
 * interview (see backend/app/api/v1/voice.py: submit_voice_answer looks
 * the interview up through the same InterviewRepository). This page
 * exists mainly so the person lands in the voice session flow
 * afterwards, reusing the exact same setup form/contract as Module 3.
 */
export function VoiceInterviewSetupPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values: InterviewSetupFormValues) => {
    setIsSubmitting(true);
    try {
      const response = await interviewApi.start({ ...values, mode: "voice" });
      saveInterviewState({
        interviewId: response.interview_id,
        questions: response.questions,
        currentIndex: 0,
      });
      navigate(`/voice/${response.interview_id}`);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not start the voice interview."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Set up your voice interview</h1>
        <p className="mt-1 text-sm text-slate-400">
          Speak your answers out loud - they're transcribed and scored automatically.
        </p>
      </div>
      <InterviewSetupForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
    </div>
  );
}
