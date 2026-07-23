import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Input, Select } from "@/components/common/FormControls";
import { Button } from "@/components/common/Button";
import { ResumeSelector } from "@/components/interview/ResumeSelector";
import { interviewSetupSchema, type InterviewSetupFormValues } from "@/schemas/interviewSchemas";
import { EXPERIENCE_LEVELS } from "@/types/interview";

interface InterviewSetupFormProps {
  onSubmit: (values: InterviewSetupFormValues) => void;
  isSubmitting?: boolean;
}

export function InterviewSetupForm({ onSubmit, isSubmitting }: InterviewSetupFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<InterviewSetupFormValues>({
    resolver: zodResolver(interviewSetupSchema),
    defaultValues: { number_of_questions: 10 },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      <ResumeSelector onResumeId={(id) => setValue("resume_id", id ?? "", { shouldValidate: true })} />
      {errors.resume_id && <p className="text-xs text-red-400">{errors.resume_id.message}</p>}

      <Input
        label="Job role"
        placeholder="e.g. Senior Backend Engineer"
        error={errors.job_role?.message}
        {...register("job_role")}
      />

      <Select
        label="Experience level"
        placeholder="Select a level"
        options={EXPERIENCE_LEVELS.map((level) => ({ label: level, value: level }))}
        error={errors.experience_level?.message}
        {...register("experience_level")}
      />

      <Input
        label="Number of questions"
        type="number"
        min={4}
        max={40}
        error={errors.number_of_questions?.message}
        hint="Between 4 and 40 questions"
        {...register("number_of_questions")}
      />

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Start interview
      </Button>
    </form>
  );
}
