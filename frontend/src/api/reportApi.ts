import { apiClient } from "@/api/client";
import type {
  InterviewReport,
  ReportAnalyticsSummary,
  ReportHistoryResponse,
  ReportTrendGrouping,
  ReportTrendsResponse,
} from "@/types/report";

/**
 * Paths verified against app/api/v1/reports.py:
 * APIRouter(prefix="/reports"), mounted directly on the app (no
 * /api/v1). Route order in the backend matters for path matching
 * (e.g. "/history" and "/analytics/*" are declared before the
 * catch-all "/{report_id}"), but that's a server-side concern only.
 */
export const reportApi = {
  generate: async (interviewId: string, regenerate = false): Promise<InterviewReport> => {
    const { data } = await apiClient.post<InterviewReport>(`/reports/interview/${interviewId}/generate`, {
      regenerate,
    });
    return data;
  },

  getByInterview: async (interviewId: string): Promise<InterviewReport> => {
    const { data } = await apiClient.get<InterviewReport>(`/reports/interview/${interviewId}`);
    return data;
  },

  getById: async (reportId: string): Promise<InterviewReport> => {
    const { data } = await apiClient.get<InterviewReport>(`/reports/${reportId}`);
    return data;
  },

  history: async (page = 1, limit = 20): Promise<ReportHistoryResponse> => {
    const { data } = await apiClient.get<ReportHistoryResponse>("/reports/history", {
      params: { page, limit },
    });
    return data;
  },

  analyticsSummary: async (): Promise<ReportAnalyticsSummary> => {
    const { data } = await apiClient.get<ReportAnalyticsSummary>("/reports/analytics/summary");
    return data;
  },

  analyticsTrends: async (grouping: ReportTrendGrouping = "weekly"): Promise<ReportTrendsResponse> => {
    const { data } = await apiClient.get<ReportTrendsResponse>("/reports/analytics/trends", {
      params: { grouping },
    });
    return data;
  },

  deleteReport: async (reportId: string): Promise<void> => {
    await apiClient.delete(`/reports/${reportId}`);
  },
};
