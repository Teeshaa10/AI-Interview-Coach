/**
 * Mirrors backend/app/schemas/interview_session.py exactly.
 *
 * IMPORTANT (discovered by inspecting the backend, not assumed): there is
 * no GET /interview/{interview_id} endpoint to reload a session's full
 * question/answer state. The only read endpoints are:
 *   - POST /interview/start          (returns the full question set)
 *   - POST /interview/{id}/answer    (returns one graded question)
 *   - POST /interview/{id}/finish    (returns the average score)
 *   - GET  /interview/history        (returns summary rows only, no
 *                                     per-question detail)
 * Because of this, the in-progress question/answer state is kept in
 * sessionStorage on the frontend so a refresh doesn't lose it - the
 * backend cannot re-supply it. See CHECKPOINT.md.
 */

export interface InterviewQuestion {
  question_number: number;
  question: string;
  category: string;
  answer: string | null;
  technical_score: number | null;
  communication_score: number | null;
  completeness_score: number | null;
  overall_score: number | null;
  strengths: string[];
  weaknesses: string[];
  better_answer: string | null;
  feedback: string | null;
}

export interface StartInterviewPayload {
  resume_id: string;
  job_role: string;
  experience_level: string;
  number_of_questions: number;
}

export interface StartInterviewResponse {
  interview_id: string;
  questions: InterviewQuestion[];
}

export interface SubmitAnswerPayload {
  question_number: number;
  answer: string;
}

export interface SubmitAnswerResponse {
  question: InterviewQuestion;
}

export interface FinishInterviewResponse {
  interview_id: string;
  average_score: number;
  completed: boolean;
}

export interface InterviewHistoryItem {
  interview_id: string;
  job_role: string;
  experience_level: string;
  average_score: number;
  completed: boolean;
  created_at: string;
}

export interface InterviewHistoryResponse {
  interviews: InterviewHistoryItem[];
}

export const EXPERIENCE_LEVELS = ["Entry Level", "Mid Level", "Senior", "Lead / Staff"] as const;
