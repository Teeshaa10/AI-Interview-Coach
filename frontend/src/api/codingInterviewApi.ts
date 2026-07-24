import { apiClient } from "@/api/client";
import type {
  CodingHistoryResponse,
  CodingInterviewResponse,
  CodingInterviewStartPayload,
  CodingRunPayload,
  CodingRunResponse,
  CodingSubmission,
  CodingSubmitPayload,
  CodingSubmitResponse,
  SupportedLanguagesResponse,
} from "@/types/codingInterview";

/**
 * Paths verified against app/api/v1/coding_interview.py:
 * APIRouter(prefix="/coding-interviews"), mounted directly on the app
 * (no /api/v1).
 */
export const codingInterviewApi = {
  start: async (payload: CodingInterviewStartPayload): Promise<CodingInterviewResponse> => {
    const { data } = await apiClient.post<CodingInterviewResponse>("/coding-interviews/start", payload);
    return data;
  },

  get: async (sessionId: string): Promise<CodingInterviewResponse> => {
    const { data } = await apiClient.get<CodingInterviewResponse>(`/coding-interviews/${sessionId}`);
    return data;
  },

  run: async (sessionId: string, payload: CodingRunPayload): Promise<CodingRunResponse> => {
    const { data } = await apiClient.post<CodingRunResponse>(`/coding-interviews/${sessionId}/run`, payload);
    return data;
  },

  submit: async (sessionId: string, payload: CodingSubmitPayload): Promise<CodingSubmitResponse> => {
    const { data } = await apiClient.post<CodingSubmitResponse>(`/coding-interviews/${sessionId}/submit`, payload);
    return data;
  },

  complete: async (sessionId: string): Promise<CodingInterviewResponse> => {
    const { data } = await apiClient.post<CodingInterviewResponse>(`/coding-interviews/${sessionId}/complete`);
    return data;
  },

  submissions: async (sessionId: string): Promise<CodingSubmission[]> => {
    const { data } = await apiClient.get<CodingSubmission[]>(`/coding-interviews/${sessionId}/submissions`);
    return data;
  },

  languages: async (): Promise<SupportedLanguagesResponse> => {
    const { data } = await apiClient.get<SupportedLanguagesResponse>("/coding-interviews/languages");
    return data;
  },

  history: async (page = 1, limit = 20): Promise<CodingHistoryResponse> => {
    const { data } = await apiClient.get<CodingHistoryResponse>("/coding-interviews/history", {
      params: { page, limit },
    });
    return data;
  },
};
