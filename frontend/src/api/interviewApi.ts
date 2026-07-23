import { apiClient } from "@/api/client";
import type {
  FinishInterviewResponse,
  InterviewHistoryResponse,
  StartInterviewPayload,
  StartInterviewResponse,
  SubmitAnswerPayload,
  SubmitAnswerResponse,
} from "@/types/interview";

/**
 * Paths verified against app/api/v1/interview.py:
 * APIRouter(prefix="/interview"), mounted directly on the app (no
 * /api/v1). There is deliberately no "get session by id" call here - the
 * backend does not expose one (see the doc-comment in types/interview.ts).
 */
export const interviewApi = {
  start: async (payload: StartInterviewPayload): Promise<StartInterviewResponse> => {
    const { data } = await apiClient.post<StartInterviewResponse>("/interview/start", payload);
    return data;
  },

  submitAnswer: async (interviewId: string, payload: SubmitAnswerPayload): Promise<SubmitAnswerResponse> => {
    const { data } = await apiClient.post<SubmitAnswerResponse>(`/interview/${interviewId}/answer`, payload);
    return data;
  },

  finish: async (interviewId: string): Promise<FinishInterviewResponse> => {
    const { data } = await apiClient.post<FinishInterviewResponse>(`/interview/${interviewId}/finish`);
    return data;
  },

  history: async (): Promise<InterviewHistoryResponse> => {
    const { data } = await apiClient.get<InterviewHistoryResponse>("/interview/history");
    return data;
  },
};
