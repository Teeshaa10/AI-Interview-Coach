/**
 * Mirrors backend/app/schemas/interview_report.py exactly.
 * Router is mounted at prefix "/reports" directly on the app (see
 * backend/app/main.py -> app.include_router(reports_router)), no
 * /api/v1 prefix, matching the pattern used by interviewApi.ts.
 */

export interface QuestionReportItem {
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
  feedback: string | null;
  improved_answer: string | null;
}

export interface InterviewReport {
  id: string | null;
  user_id: string;
  interview_id: string;
  job_role: string;
  experience_level: string;
  total_questions: number;
  answered_questions: number;
  completion_percentage: number;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  completeness_score: number;
  category_scores: Record<string, number>;
  question_breakdown: QuestionReportItem[];
  strengths: string[];
  weaknesses: string[];
  weak_topics: string[];
  improvement_plan: string[];
  recommended_next_difficulty: string;
  summary: string;
  interview_completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface GenerateReportPayload {
  regenerate: boolean;
}

export interface ReportHistoryResponse {
  reports: InterviewReport[];
  page: number;
  limit: number;
  total: number;
}

export interface ScoreTrendPoint {
  date: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
}

export interface ReportAnalyticsSummary {
  interviews_completed: number;
  average_overall_score: number;
  best_score: number;
  latest_score: number;
  technical_average: number;
  communication_average: number;
  completeness_average: number;
  strongest_topics: string[];
  weakest_topics: string[];
  recent_improvement_percentage: number | null;
  score_trend: ScoreTrendPoint[];
}

export type ReportTrendGrouping = "weekly" | "monthly";

export interface ReportTrendPoint {
  period: string;
  interviews: number;
  average_overall_score: number;
  average_technical_score: number;
  average_communication_score: number;
}

export interface ReportTrendsResponse {
  grouping: ReportTrendGrouping;
  points: ReportTrendPoint[];
}
