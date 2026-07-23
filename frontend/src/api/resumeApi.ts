import { apiClient } from "@/api/client";
import type {
  DeleteResumeResponse,
  Resume,
  SemanticSearchRequest,
  SemanticSearchResponse,
  UploadResumeResponse,
} from "@/types/resume";

/**
 * Paths verified against app/api/v1/resume.py:
 * APIRouter(prefix="/resume"), mounted directly on the app (no /api/v1).
 * Multipart field name is exactly "file" - see the `file: UploadFile =
 * File(...)` parameter in upload_resume().
 */
export const resumeApi = {
  upload: async (file: File, onProgress?: (percent: number) => void): Promise<UploadResumeResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await apiClient.post<UploadResumeResponse>("/resume/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (event) => {
        if (!onProgress || !event.total) return;
        onProgress(Math.round((event.loaded / event.total) * 100));
      },
    });
    return data;
  },

  /**
   * Returns only the caller's single most-recent resume - the backend has
   * no endpoint that lists every resume a user has uploaded.
   */
  getMyResume: async (): Promise<Resume> => {
    const { data } = await apiClient.get<Resume>("/resume/me");
    return data;
  },

  delete: async (resumeId: string): Promise<DeleteResumeResponse> => {
    const { data } = await apiClient.delete<DeleteResumeResponse>(`/resume/${resumeId}`);
    return data;
  },

  /**
   * BACKEND LIMITATION: POST /embeddings/search is defined in
   * app/api/v1/embeddings.py but that router is not included in
   * app/main.py's live FastAPI app, so this call will currently 404.
   * Fixing it is a one-line addition to main.py
   * (`app.include_router(embeddings_router)`), which is outside the
   * "CORS-only" backend-change allowance given for this task, so it has
   * been left for the project owner to decide on. See CHECKPOINT.md.
   */
  semanticSearch: async (payload: SemanticSearchRequest): Promise<SemanticSearchResponse> => {
    const { data } = await apiClient.post<SemanticSearchResponse>("/embeddings/search", payload);
    return data;
  },
};
