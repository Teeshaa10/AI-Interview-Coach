import { useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Input, Select } from "@/components/common/FormControls";
import { Button } from "@/components/common/Button";
import { useMyResume } from "@/hooks/useMyResume";
import { codingInterviewApi } from "@/api/codingInterviewApi";
import {
  codingInterviewSetupSchema,
  type CodingInterviewSetupFormValues,
} from "@/schemas/codingInterviewSchemas";
import { CODING_DIFFICULTIES } from "@/types/codingInterview";

const EXPERIENCE_LEVELS = ["Fresher", "Entry Level", "Mid Level", "Senior", "Lead / Staff"];

interface CodingInterviewSetupFormProps {
  onSubmit: (values: CodingInterviewSetupFormValues) => void;
  isSubmitting?: boolean;
}

export function CodingInterviewSetupForm({ onSubmit, isSubmitting }: CodingInterviewSetupFormProps) {
  // Resume is optional for coding interviews (unlike text/voice), so this
  // just pre-fills resume_id when one exists rather than blocking submit.
  const { data: resume } = useMyResume();
  const { data: languagesData } = useQuery({
    queryKey: ["coding-interviews", "languages"],
    queryFn: codingInterviewApi.languages,
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CodingInterviewSetupFormValues>({
    resolver: zodResolver(codingInterviewSetupSchema),
    defaultValues: {
      difficulty: "medium",
      topics: [],
      language: "cpp",
      number_of_questions: 3,
    },
  });

  const languageOptions = (languagesData?.languages ?? ["cpp", "python", "java", "javascript"]).map((lang) => ({
    label: lang,
    value: lang,
  }));

  const handleFormSubmit = (values: CodingInterviewSetupFormValues) => {
    onSubmit({ ...values, resume_id: resume?.id ?? values.resume_id });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5" noValidate>
      {resume && (
        <p className="text-xs text-slate-500">
          Questions may be tailored using your resume ({resume.original_filename}).
        </p>
      )}

      <Input
        label="Role"
        placeholder="e.g. Backend Engineer"
        error={errors.role?.message}
        {...register("role")}
      />

      <Select
        label="Experience level"
        placeholder="Select a level"
        options={EXPERIENCE_LEVELS.map((level) => ({ label: level, value: level }))}
        error={errors.experience_level?.message}
        {...register("experience_level")}
      />

      <Select
        label="Difficulty"
        options={CODING_DIFFICULTIES.map((level) => ({ label: level, value: level }))}
        error={errors.difficulty?.message}
        {...register("difficulty")}
      />

      <Select
        label="Language"
        options={languageOptions}
        error={errors.language?.message}
        {...register("language")}
      />

      <Input
        label="Number of questions"
        type="number"
        min={1}
        max={5}
        error={errors.number_of_questions?.message}
        hint="Between 1 and 5 questions"
        {...register("number_of_questions")}
      />

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Start coding interview
      </Button>
    </form>
  );
}
