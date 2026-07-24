/**
 * Mirrors backend/app/schemas/coding_interview.py exactly.
 *
 * IMPORTANT (confirmed by reading app/api/v1/coding_interview.py):
 *   - POST /coding-interviews/start           returns the full question set
 *     (hidden_test_cases excluded via CodingQuestionPublic)
 *   - GET  /coding-interviews/{id}             also returns the full
 *     question set, so a session IS resumable after a refresh (unlike the
 *     text-interview module).
 *   - POST /coding-interviews/{id}/run         runs only visible test
 *     cases, no persistence, no scoring.
 *   - POST /coding-interviews/{id}/submit      runs all test cases,
 *     scores, persists, returns the next question.
 *   - POST /coding-interviews/{id}/complete    finalizes the session.
 */

export type CodingDifficulty = "easy" | "medium" | "hard";

export interface CodingExample {
  input: string;
  output: string;
  explanation: string;
}

export interface CodingTestCase {
  input: string;
  expected_output: string;
}

export interface ExpectedComplexity {
  time: string;
  space: string;
}

export interface CodingQuestion {
  question_number: number;
  title: string;
  problem_statement: string;
  difficulty: CodingDifficulty;
  topics: string[];
  constraints: string[];
  examples: CodingExample[];
  function_signature: string;
  starter_code: Record<string, string>;
  visible_test_cases: CodingTestCase[];
  expected_complexity: ExpectedComplexity;
}

export interface CodingInterviewStartPayload {
  resume_id?: string | null;
  role: string;
  experience_level: string;
  difficulty: CodingDifficulty;
  topics: string[];
  language: string;
  number_of_questions: number;
}

export interface CodingInterviewResponse {
  session_id: string;
  role: string;
  difficulty: CodingDifficulty;
  language: string;
  questions: CodingQuestion[];
  completed: boolean;
  final_score: number;
}

export interface CodingRunPayload {
  question_number: number;
  language: string;
  source_code: string;
}

export interface TestExecutionResult {
  input: string;
  expected_output: string;
  actual_output: string;
  passed: boolean;
  stderr: string;
  execution_time: number | null;
}

export interface CodingRunResponse {
  test_results: TestExecutionResult[];
  tests_passed: number;
  tests_total: number;
}

export interface CodingSubmitPayload {
  question_number: number;
  language: string;
  source_code: string;
  explanation?: string;
}

export interface CodingSubmission {
  id: string;
  session_id: string;
  question_number: number;
  language: string;
  source_code: string;
  explanation: string;
  test_results: TestExecutionResult[];
  tests_passed: number;
  tests_total: number;
  correctness_score: number;
  quality_score: number;
  complexity_score: number;
  explanation_score: number;
  overall_score: number;
  feedback: string[];
  created_at: string;
}

export interface CodingSubmitResponse {
  submission: CodingSubmission;
  next_question: CodingQuestion | null;
}

export interface CodingHistoryResponse {
  sessions: CodingInterviewResponse[];
  page: number;
  limit: number;
  total: number;
}

export interface SupportedLanguagesResponse {
  provider: string;
  languages: string[];
}

export const CODING_DIFFICULTIES: CodingDifficulty[] = ["easy", "medium", "hard"];
