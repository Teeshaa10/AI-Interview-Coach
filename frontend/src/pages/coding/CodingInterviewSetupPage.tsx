import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { CodingInterviewSetupForm } from "@/components/coding/CodingInterviewSetupForm";
import { codingInterviewApi } from "@/api/codingInterviewApi";
import { getApiErrorMessage } from "@/api/client";
import type { CodingInterviewSetupFormValues } from "@/schemas/codingInterviewSchemas";

export function CodingInterviewSetupPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values: CodingInterviewSetupFormValues) => {
    setIsSubmitting(true);
    try {
      const response = await codingInterviewApi.start({
        resume_id: values.resume_id || null,
        role: values.role,
        experience_level: values.experience_level,
        difficulty: values.difficulty,
        topics: values.topics,
        language: values.language,
        number_of_questions: values.number_of_questions,
      });
      navigate(`/coding/${response.session_id}`);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not start the coding interview."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Set up your coding interview</h1>
        <p className="mt-1 text-sm text-slate-400">
          Solve hands-on coding problems and get scored on correctness, quality, and complexity.
        </p>
      </div>
      <CodingInterviewSetupForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
    </div>
  );
}
