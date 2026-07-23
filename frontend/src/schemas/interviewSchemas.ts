import { z } from "zod";

/**
 * Mirrors InterviewSessionCreate in
 * backend/app/schemas/interview_session.py: number_of_questions is
 * constrained to 4-40 by the backend (Field(ge=4, le=40)); job_role and
 * experience_level must be non-blank strings.
 */
export const interviewSetupSchema = z.object({
  resume_id: z.string().min(1, "Select a resume to base the interview on"),
  job_role: z.string().min(2, "Enter the job role you're preparing for").max(120),
  experience_level: z.string().min(2, "Select an experience level"),
  number_of_questions: z.coerce.number().int().min(4, "Minimum 4 questions").max(40, "Maximum 40 questions"),
});

export type InterviewSetupFormValues = z.infer<typeof interviewSetupSchema>;
