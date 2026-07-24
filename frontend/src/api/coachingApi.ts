import { apiClient } from "@/api/client";
import type {
  CoachingInsights,
  CoachingProfile,
  CreatePlanRequest,
  NextInterviewRecommendation,
  PlanItemUpdateRequest,
  PracticePlanResponse,
} from "@/types/coaching";

/**
 * Paths verified against app/api/v1/coaching.py:
 * APIRouter(prefix="/coaching"), mounted directly on the app (no /api/v1),
 * same as /interview, /reports, /voice, /coding-interviews, /sessions.
 */
export const coachingApi = {
  profile: async (): Promise<CoachingProfile> => {
    const { data } = await apiClient.get<CoachingProfile>("/coaching/profile");
    return data;
  },

  insights: async (): Promise<CoachingInsights> => {
    const { data } = await apiClient.get<CoachingInsights>("/coaching/insights");
    return data;
  },

  recommendation: async (): Promise<NextInterviewRecommendation> => {
    const { data } = await apiClient.get<NextInterviewRecommendation>("/coaching/recommendation");
    return data;
  },

  activePlan: async (): Promise<PracticePlanResponse | null> => {
    const { data } = await apiClient.get<PracticePlanResponse | null>("/coaching/plans/active");
    return data;
  },

  createPlan: async (payload: CreatePlanRequest): Promise<PracticePlanResponse> => {
    const { data } = await apiClient.post<PracticePlanResponse>("/coaching/plans", payload);
    return data;
  },

  regeneratePlan: async (planId: string): Promise<PracticePlanResponse> => {
    const { data } = await apiClient.post<PracticePlanResponse>(`/coaching/plans/${planId}/regenerate`);
    return data;
  },

  updatePlanItem: async (
    planId: string,
    itemId: string,
    payload: PlanItemUpdateRequest,
  ): Promise<PracticePlanResponse> => {
    const { data } = await apiClient.patch<PracticePlanResponse>(
      `/coaching/plans/${planId}/items/${itemId}`,
      payload,
    );
    return data;
  },
};
