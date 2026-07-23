import { apiClient } from "@/api/client";
import type { VoiceAnswerResponse } from "@/types/voice";

export const voiceApi = {
  submitAnswer: async (
    interviewId: string,
    questionNumber: number,
    audioBlob: Blob,
    filename: string,
  ): Promise<VoiceAnswerResponse> => {
    const formData = new FormData();

    formData.append("question_number", String(questionNumber));
    formData.append(
      "audio",
      audioBlob,
      filename || `answer-${questionNumber}.webm`,
    );

    const { data } = await apiClient.post<VoiceAnswerResponse>(
      `/voice/interview/${interviewId}/answer`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );

    return data;
  },
};