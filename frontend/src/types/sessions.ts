export type SessionType = "text" | "voice" | "coding";
export type SessionStatus = "in_progress" | "completed";

export interface UnifiedSessionItem {
  session_id: string;
  type: SessionType;
  title: string;
  subtitle: string;
  status: SessionStatus;
  score: number | null;
  created_at: string;
  completed_at: string | null;
  resumable: boolean;
  resume_path: string | null;
  has_report: boolean;
  favorite: boolean;
}

export interface UnifiedHistoryResponse {
  sessions: UnifiedSessionItem[];
  total: number;
  page: number;
  limit: number;
}

export interface SessionTypeBreakdown {
  type: SessionType;
  total: number;
  completed: number;
  in_progress: number;
  average_score: number;
  best_score: number;
}

export interface AnalyticsTrendPoint {
  date: string;
  type: SessionType;
  score: number;
  title: string;
}

export interface UnifiedAnalyticsOverview {
  total_sessions: number;
  completed_sessions: number;
  in_progress_sessions: number;
  average_score_overall: number;
  best_score_overall: number;
  lowest_score_overall: number;
  average_technical_score: number;
  average_communication_score: number;
  by_type: SessionTypeBreakdown[];
  score_trend: AnalyticsTrendPoint[];
  current_streak_days: number;
  longest_streak_days: number;
  strongest_topics: string[];
  weakest_topics: string[];
}

export interface AnalyticsInsightsResponse {
  insights: string[];
  generated_by_ai: boolean;
}

export interface HistoryQueryParams {
  type?: "all" | SessionType;
  status?: "all" | SessionStatus;
  search?: string;
  favorite_only?: boolean;
  sort_by?: "created_at" | "score" | "title";
  sort_dir?: "asc" | "desc";
  page?: number;
  limit?: number;
}
