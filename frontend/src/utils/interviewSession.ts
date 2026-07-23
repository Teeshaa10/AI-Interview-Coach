import type { InterviewQuestion } from "@/types/interview";

/**
 * The backend cannot re-supply an in-progress interview's question/answer
 * state on refresh (no GET /interview/{id} - see types/interview.ts), so
 * this persists it in sessionStorage as a safety net. It is cleared once
 * the interview is finished.
 */
interface StoredInterviewState {
  interviewId: string;
  questions: InterviewQuestion[];
  currentIndex: number;
}

const keyFor = (interviewId: string) => `aic_interview_${interviewId}`;

export function saveInterviewState(state: StoredInterviewState): void {
  sessionStorage.setItem(keyFor(state.interviewId), JSON.stringify(state));
}

export function loadInterviewState(interviewId: string): StoredInterviewState | null {
  const raw = sessionStorage.getItem(keyFor(interviewId));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredInterviewState;
  } catch {
    return null;
  }
}

export function clearInterviewState(interviewId: string): void {
  sessionStorage.removeItem(keyFor(interviewId));
}
