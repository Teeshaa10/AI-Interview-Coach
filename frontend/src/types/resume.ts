/**
 * Mirrors backend/app/schemas/resume.py exactly.
 *
 * IMPORTANT (discovered by inspecting the backend, not assumed):
 * GET /resume/me returns a single ResumeResponse - the caller's most recent
 * resume only. There is no "list all my resumes" endpoint and no
 * GET /resume/{resume_id} endpoint. The only per-id resume operation the
 * backend exposes is DELETE /resume/{resume_id}. The frontend's "resume
 * history" is therefore a single current-resume view, not a list.
 */

export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_path: string;
  extracted_text: string;
  created_at: string;
  updated_at: string;
}

export interface UploadResumeResponse {
  message: string;
  resume: Resume;
}

export interface DeleteResumeResponse {
  message: string;
}

/**
 * Mirrors backend/app/schemas/embedding.py (POST /embeddings/search).
 *
 * BACKEND LIMITATION: the embeddings router is defined in
 * app/api/v1/embeddings.py and app/api/v1/router.py, but that router is
 * never included in the live FastAPI app (app/main.py only registers
 * auth/resume/interview/resume_analysis/voice/reports/coding_interview
 * routers). Calling this endpoint against the current backend will 404
 * until `app.include_router(embeddings_router)` is added to main.py. See
 * CHECKPOINT.md for details - this is flagged there, not silently patched,
 * since it is outside the "CORS only" backend-change allowance.
 */
export interface SemanticSearchRequest {
  query: string;
  top_k?: number;
  resume_id?: string;
  min_similarity?: number;
}

export interface SemanticSearchResultChunk {
  chunk_id: string;
  chunk_text: string;
  similarity_score: number;
  resume_id: string;
  filename: string;
  chunk_index: number;
  start_char: number;
  end_char: number;
}

export interface SemanticSearchResponse {
  query: string;
  count: number;
  results: SemanticSearchResultChunk[];
}
