/**
 * Mirrors backend/app/schemas/voice.py::VoiceAnswerResponse exactly.
 * Router is APIRouter(prefix="/voice"), mounted directly on the app (no
 * /api/v1) - see backend/app/main.py.
 *
 * There is no POST /voice/interview/start and no GET voice session
 * endpoint - a voice interview is created with the existing
 * POST /interview/start (see interviewApi.ts / types/interview.ts), and
 * each answer is uploaded + transcribed + evaluated in a single call to
 * POST /voice/interview/{interview_id}/answer (multipart: question_number
 * + audio file), which is why this file only needs to describe that one
 * response shape - everything else reuses InterviewQuestion from
 * types/interview.ts.
 */

import type { InterviewQuestion } from "@/types/interview";

export interface VoiceAnswerResponse {
  interview_id: string;
  transcription: string;
  question: InterviewQuestion;
}
