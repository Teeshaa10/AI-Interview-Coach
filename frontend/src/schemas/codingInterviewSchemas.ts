import { z } from "zod";

/**
 * Mirrors CodingInterviewStartRequest in
 * backend/app/schemas/coding_interview.py: role (2-120 chars),
 * experience_level (2-80 chars, default "Fresher"), topics capped at 10,
 * number_of_questions between 1 and 5.
 */
export const codingInterviewSetupSchema = z.object({
  resume_id: z.string().optional(),
  role: z.string().min(2, "Enter the role you're preparing for").max(120),
  experience_level: z.string().min(2, "Select an experience level").max(80),
  difficulty: z.enum(["easy", "medium", "hard"]),
  topics: z.array(z.string()).max(10, "Choose up to 10 topics"),
  language: z.string().min(1, "Select a language"),
  number_of_questions: z.coerce.number().int().min(1, "Minimum 1 question").max(5, "Maximum 5 questions"),
});

export type CodingInterviewSetupFormValues = z.infer<typeof codingInterviewSetupSchema>;
