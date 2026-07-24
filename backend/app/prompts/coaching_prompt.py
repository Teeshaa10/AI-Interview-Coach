from app.schemas.coaching import CoachingProfile


def build_insight_summary_prompt(profile: CoachingProfile) -> str:
    """Short natural-language explanation of the deterministic readiness
    numbers - Gemini is only used for phrasing here, never for the score
    itself, per Module 9.5."""

    return (
        "You are an encouraging interview-prep coach. In 2-3 short sentences (no bullet points, "
        "no headers), explain this candidate's current readiness in plain language and point them "
        "toward one clear next step. Do not invent facts not given below.\n\n"
        f"Target role: {profile.target_role or 'not specified yet'}\n"
        f"Total practice sessions: {profile.total_sessions} (completed: {profile.completed_sessions})\n"
        f"Average score: {profile.average_score_overall}/10\n"
        f"Average technical score: {profile.average_technical_score}/10\n"
        f"Average communication score: {profile.average_communication_score}/10\n"
        f"Current streak: {profile.current_streak_days} days\n"
        f"Strongest topics: {', '.join(profile.strongest_topics) or 'none yet'}\n"
        f"Weakest topics: {', '.join(profile.weakest_topics) or 'none yet'}"
    )
