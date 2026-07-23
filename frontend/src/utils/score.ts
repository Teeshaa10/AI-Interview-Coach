export type ScoreTone = "success" | "warning" | "danger";

/**
 * Scores across the reports API are on a 0-10 scale (see
 * InterviewQuestion.overall_score usage elsewhere in the app).
 */
export function scoreTone(score: number): ScoreTone {
  if (score >= 7) return "success";
  if (score >= 4) return "warning";
  return "danger";
}

export function formatScore(score: number | null): string {
  return score === null ? "\u2014" : score.toFixed(1);
}
