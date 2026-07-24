/**
 * Mirrors backend/app/schemas/coaching.py exactly.
 *
 * IMPORTANT (confirmed by reading app/api/v1/coaching.py):
 *   - GET  /coaching/profile                    -> CoachingProfile
 *   - GET  /coaching/insights                    -> CoachingInsights
 *   - GET  /coaching/recommendation              -> NextInterviewRecommendation
 *   - GET  /coaching/plans/active                -> PracticePlanResponse | null
 *   - POST /coaching/plans                       -> PracticePlanResponse (201)
 *   - POST /coaching/plans/{planId}/regenerate   -> PracticePlanResponse
 *   - PATCH /coaching/plans/{planId}/items/{itemId} -> PracticePlanResponse
 *
 * All routers are mounted directly on the app (no /api/v1 prefix), same
 * as /interview, /reports, /voice, /coding-interviews, /sessions.
 */

export type ReadinessLevel = "getting_started" | "building_confidence" | "interview_ready" | "highly_prepared";
export type CoachingInterviewType = "text" | "voice" | "coding";
export type PlanDuration = 7 | 14 | 30;
export type CoachingDifficulty = "easy" | "medium" | "hard";

export interface SessionTypeBreakdown {
  type: CoachingInterviewType;
  total: number;
  completed: number;
  in_progress: number;
  average_score: number;
  best_score: number;
}

export interface CoachingProfile {
  is_new_user: boolean;
  has_resume: boolean;
  target_role: string | null;
  total_sessions: number;
  completed_sessions: number;
  in_progress_sessions: number;
  average_score_overall: number;
  average_technical_score: number;
  average_communication_score: number;
  current_streak_days: number;
  longest_streak_days: number;
  strongest_topics: string[];
  weakest_topics: string[];
  by_type: SessionTypeBreakdown[];
}

export interface CoachingInsights {
  readiness_level: ReadinessLevel;
  readiness_score: number;
  top_strengths: string[];
  priority_weaknesses: string[];
  recommended_topics: string[];
  consistency_insight: string;
  next_milestone: string;
  ai_summary: string | null;
  generated_by_ai: boolean;
}

export interface NextInterviewRecommendation {
  interview_type: CoachingInterviewType;
  topic: string;
  difficulty: CoachingDifficulty;
  target_skill: string;
  reason: string;
  suggested_duration_minutes: number;
  suggested_number_of_questions: number;
  setup_path: string;
}

export interface PracticePlanItem {
  item_id: string;
  day_number: number;
  focus_area: string;
  interview_type: CoachingInterviewType;
  topic: string;
  difficulty: CoachingDifficulty;
  estimated_minutes: number;
  objective: string;
  recommended_activity: string;
  reason: string | null;
  completed: boolean;
}

export interface PracticePlanResponse {
  id: string;
  duration_days: PlanDuration;
  items: PracticePlanItem[];
  completed_items: number;
  total_items: number;
  completion_percentage: number;
  created_at: string;
}

export interface CreatePlanRequest {
  duration_days: PlanDuration;
}

export interface PlanItemUpdateRequest {
  completed: boolean;
}

export const PLAN_DURATIONS: PlanDuration[] = [7, 14, 30];

export const READINESS_LABELS: Record<ReadinessLevel, string> = {
  getting_started: "Getting Started",
  building_confidence: "Building Confidence",
  interview_ready: "Interview Ready",
  highly_prepared: "Highly Prepared",
};
