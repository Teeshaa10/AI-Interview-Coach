import { apiClient } from "@/api/client";
import type {
  AnalyticsInsightsResponse,
  HistoryQueryParams,
  SessionType,
  UnifiedAnalyticsOverview,
  UnifiedHistoryResponse,
} from "@/types/sessions";

/**
 * Paths verified against app/api/v1/sessions.py:
 * APIRouter(prefix="/sessions"), mounted directly on the app (no /api/v1),
 * same as /interview, /reports, /voice, /coding-interview.
 */
export const sessionsApi = {
  history: async (params: HistoryQueryParams = {}): Promise<UnifiedHistoryResponse> => {
    const { data } = await apiClient.get<UnifiedHistoryResponse>("/sessions/history", {
      params: {
        type: params.type ?? "all",
        status: params.status ?? "all",
        search: params.search || undefined,
        favorite_only: params.favorite_only ?? false,
        sort_by: params.sort_by ?? "created_at",
        sort_dir: params.sort_dir ?? "desc",
        page: params.page ?? 1,
        limit: params.limit ?? 20,
      },
    });
    return data;
  },

  analyticsOverview: async (): Promise<UnifiedAnalyticsOverview> => {
    const { data } = await apiClient.get<UnifiedAnalyticsOverview>("/sessions/analytics/overview");
    return data;
  },

  analyticsInsights: async (): Promise<AnalyticsInsightsResponse> => {
    const { data } = await apiClient.get<AnalyticsInsightsResponse>("/sessions/analytics/insights");
    return data;
  },

  setFavorite: async (type: SessionType, sessionId: string, favorite: boolean): Promise<void> => {
    await apiClient.put(`/sessions/${type}/${sessionId}/favorite`, null, {
      params: { favorite },
    });
  },

  deleteSession: async (type: SessionType, sessionId: string): Promise<void> => {
    await apiClient.delete(`/sessions/${type}/${sessionId}`);
  },
};
