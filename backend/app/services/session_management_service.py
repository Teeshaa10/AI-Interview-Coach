from collections import Counter
from datetime import datetime, timedelta

from app.exceptions.session_management import (
    InvalidSessionTypeError,
    SessionNotFoundError,
)
from app.repositories.coding_interview_repository import CodingInterviewRepository
from app.repositories.interview_report_repository import InterviewReportRepository
from app.repositories.interview_repository import InterviewRepository
from app.schemas.session_management import (
    AnalyticsInsightsResponse,
    AnalyticsTrendPoint,
    SessionTypeBreakdown,
    UnifiedAnalyticsOverview,
    UnifiedHistoryResponse,
    UnifiedSessionItem,
)


class SessionManagementService:
    """Unifies the three places interview practice is stored today —
    interview_sessions (mode="text"), interview_sessions (mode="voice"), and
    coding_interviews — into one history list and one analytics overview,
    per Module 6/7. It reads through the existing repositories rather than
    introducing a new collection, so Modules 1-5 are untouched."""

    def __init__(
        self,
        interview_repository: InterviewRepository,
        coding_repository: CodingInterviewRepository,
        report_repository: InterviewReportRepository,
    ):
        self.interview_repository = interview_repository
        self.coding_repository = coding_repository
        self.report_repository = report_repository

    async def _all_items(self, user_id: str) -> list[UnifiedSessionItem]:
        interviews = await self.interview_repository.get_user_interviews(user_id)
        coding_sessions = await self.coding_repository.list_all_user_sessions(user_id)
        reports = await self.report_repository.list_all_user_reports(user_id)
        reported_interview_ids = {r.interview_id for r in reports}

        items: list[UnifiedSessionItem] = []

        for interview in interviews:
            session_type = "voice" if interview.mode == "voice" else "text"
            has_report = interview.id in reported_interview_ids
            if interview.completed:
                resume_path = f"/reports/interview/{interview.id}" if has_report else None
                resumable = has_report
            else:
                resume_path = f"/voice/{interview.id}" if session_type == "voice" else f"/interviews/{interview.id}"
                resumable = True

            items.append(UnifiedSessionItem(
                session_id=interview.id or "",
                type=session_type,
                title=interview.job_role,
                subtitle=interview.experience_level,
                status="completed" if interview.completed else "in_progress",
                score=interview.average_score if interview.completed else None,
                created_at=interview.created_at,
                completed_at=interview.completed_at,
                resumable=resumable,
                resume_path=resume_path,
                has_report=has_report,
                favorite=interview.favorite,
            ))

        for session in coding_sessions:
            # Module 8: the coding frontend now exists. A completed session
            # can be reopened on its completion summary; an in-progress one
            # can be resumed because GET /coding-interviews/{id} returns the
            # full question set (unlike text/voice sessions, which rely on
            # sessionStorage - see interviewApi.ts).
            if session.completed:
                resume_path = f"/coding/{session.id}/complete"
                has_report = True
            else:
                resume_path = f"/coding/{session.id}"
                has_report = False

            items.append(UnifiedSessionItem(
                session_id=session.id or "",
                type="coding",
                title=session.role,
                subtitle=f"{session.difficulty} · {session.language}",
                status="completed" if session.completed else "in_progress",
                score=session.final_score if session.completed else None,
                created_at=session.created_at,
                completed_at=session.completed_at,
                resumable=True,
                resume_path=resume_path,
                has_report=has_report,
                favorite=session.favorite,
            ))

        items.sort(key=lambda i: i.created_at, reverse=True)
        return items

    async def list_history(
        self,
        user_id: str,
        session_type: str = "all",
        session_status: str = "all",
        search: str | None = None,
        favorite_only: bool = False,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        limit: int = 20,
    ) -> UnifiedHistoryResponse:
        if session_type not in ("all", "text", "voice", "coding"):
            raise InvalidSessionTypeError(session_type)
        if session_status not in ("all", "in_progress", "completed"):
            raise InvalidSessionTypeError(session_status)
        if sort_by not in ("created_at", "score", "title"):
            raise InvalidSessionTypeError(sort_by)
        if sort_dir not in ("asc", "desc"):
            raise InvalidSessionTypeError(sort_dir)

        items = await self._all_items(user_id)

        if session_type != "all":
            items = [i for i in items if i.type == session_type]
        if session_status != "all":
            items = [i for i in items if i.status == session_status]
        if favorite_only:
            items = [i for i in items if i.favorite]
        if search:
            needle = search.strip().lower()
            if needle:
                items = [
                    i for i in items
                    if needle in i.title.lower() or needle in i.subtitle.lower()
                ]

        reverse = sort_dir == "desc"
        if sort_by == "score":
            items.sort(key=lambda i: i.score if i.score is not None else -1, reverse=reverse)
        elif sort_by == "title":
            items.sort(key=lambda i: i.title.lower(), reverse=reverse)
        else:
            items.sort(key=lambda i: i.created_at, reverse=reverse)

        total = len(items)
        start = (page - 1) * limit
        page_items = items[start:start + limit]

        return UnifiedHistoryResponse(sessions=page_items, total=total, page=page, limit=limit)

    async def toggle_favorite(self, user_id: str, session_type: str, session_id: str, favorite: bool) -> None:
        if session_type == "coding":
            updated = await self.coding_repository.set_favorite(session_id, user_id, favorite)
        elif session_type in ("text", "voice"):
            updated = await self.interview_repository.set_favorite(session_id, user_id, favorite)
        else:
            raise InvalidSessionTypeError(session_type)

        if not updated:
            raise SessionNotFoundError()

    async def delete_session(self, user_id: str, session_type: str, session_id: str) -> None:
        if session_type == "coding":
            deleted = await self.coding_repository.delete_session(session_id, user_id)
        elif session_type in ("text", "voice"):
            # delete_owned_interview() is ObjectId-safe and already scopes
            # the delete to user_id, so an invalid id or someone else's
            # session both just come back as "not deleted" -> 404 below,
            # without needing an extra unsafe lookup first.
            deleted = await self.interview_repository.delete_owned_interview(session_id, user_id)
            if deleted:
                # Best-effort cleanup of an orphaned report so history and
                # /reports/history don't disagree about what still exists.
                report = await self.report_repository.get_by_interview_id(session_id)
                if report and report.id:
                    await self.report_repository.delete(report.id, user_id)
        else:
            raise InvalidSessionTypeError(session_type)

        if not deleted:
            raise SessionNotFoundError()

    async def get_analytics_overview(self, user_id: str) -> UnifiedAnalyticsOverview:
        items = await self._all_items(user_id)
        completed = [i for i in items if i.status == "completed" and i.score is not None]

        def avg(values: list[float]) -> float:
            return round(sum(values) / len(values), 2) if values else 0.0

        by_type: list[SessionTypeBreakdown] = []
        for t in ("text", "voice", "coding"):
            type_items = [i for i in items if i.type == t]
            type_completed = [i for i in type_items if i.status == "completed" and i.score is not None]
            scores = [i.score for i in type_completed]
            by_type.append(SessionTypeBreakdown(
                type=t,
                total=len(type_items),
                completed=len(type_completed),
                in_progress=len([i for i in type_items if i.status == "in_progress"]),
                average_score=avg(scores),
                best_score=max(scores) if scores else 0.0,
            ))

        trend_source = sorted(completed, key=lambda i: i.completed_at or i.created_at)
        score_trend = [
            AnalyticsTrendPoint(
                date=i.completed_at or i.created_at,
                type=i.type,
                score=i.score or 0.0,
                title=i.title,
            )
            for i in trend_source[-50:]
        ]

        practice_days = sorted({(i.completed_at or i.created_at).date() for i in completed})
        current_streak, longest_streak = self._compute_streaks(practice_days)

        reports = await self.report_repository.list_all_user_reports(user_id)
        strengths = Counter(item for report in reports for item in report.strengths)
        weaknesses = Counter(item for report in reports for item in report.weak_topics + report.weaknesses)

        scores_all = [i.score for i in completed]

        return UnifiedAnalyticsOverview(
            total_sessions=len(items),
            completed_sessions=len(completed),
            in_progress_sessions=len(items) - len(completed),
            average_score_overall=avg(scores_all),
            best_score_overall=max(scores_all) if scores_all else 0.0,
            lowest_score_overall=min(scores_all) if scores_all else 0.0,
            average_technical_score=avg([r.technical_score for r in reports]),
            average_communication_score=avg([r.communication_score for r in reports]),
            by_type=by_type,
            score_trend=score_trend,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            strongest_topics=[x for x, _ in strengths.most_common(5)],
            weakest_topics=[x for x, _ in weaknesses.most_common(5)],
        )

    async def get_insights(self, user_id: str, gemini_client, model_name: str) -> AnalyticsInsightsResponse:
        """Short, human-readable takeaways about the user's practice
        history. Uses Gemini when configured (reusing the same client
        pattern as InterviewService/EvaluationService); falls back to
        simple rule-based observations when it isn't, so this endpoint
        never hard-fails just because GEMINI_API_KEY is unset."""

        overview = await self.get_analytics_overview(user_id)

        if overview.total_sessions == 0:
            return AnalyticsInsightsResponse(
                insights=["Complete your first practice interview to start seeing personalized insights here."],
                generated_by_ai=False,
            )

        fallback = self._rule_based_insights(overview)

        if gemini_client is None:
            return AnalyticsInsightsResponse(insights=fallback, generated_by_ai=False)

        try:
            prompt = (
                "You are an interview-prep coach. In 3-5 short bullet points (no more than "
                "20 words each), give the candidate encouraging, specific, actionable feedback "
                "based on this practice summary. Reply with plain bullet lines only, no headers.\n\n"
                f"Total sessions: {overview.total_sessions} "
                f"(text: {next(t.total for t in overview.by_type if t.type == 'text')}, "
                f"voice: {next(t.total for t in overview.by_type if t.type == 'voice')}, "
                f"coding: {next(t.total for t in overview.by_type if t.type == 'coding')})\n"
                f"Average score: {overview.average_score_overall}, best: {overview.best_score_overall}, "
                f"lowest: {overview.lowest_score_overall}\n"
                f"Average technical score: {overview.average_technical_score}, "
                f"average communication score: {overview.average_communication_score}\n"
                f"Current streak: {overview.current_streak_days} days, longest: {overview.longest_streak_days} days\n"
                f"Strongest topics: {', '.join(overview.strongest_topics) or 'none yet'}\n"
                f"Weakest topics: {', '.join(overview.weakest_topics) or 'none yet'}"
            )
            response = await gemini_client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = (response.text or "").strip()
            lines = [
                line.lstrip("-•* ").strip()
                for line in text.splitlines()
                if line.strip()
            ]
            if lines:
                return AnalyticsInsightsResponse(insights=lines[:5], generated_by_ai=True)
        except Exception:
            # Gemini being unavailable/erroring shouldn't break the
            # analytics dashboard - fall back to rule-based insights.
            pass

        return AnalyticsInsightsResponse(insights=fallback, generated_by_ai=False)

    @staticmethod
    def _rule_based_insights(overview: UnifiedAnalyticsOverview) -> list[str]:
        insights = [
            f"You've completed {overview.completed_sessions} of {overview.total_sessions} practice sessions, "
            f"averaging {overview.average_score_overall}/10.",
        ]
        if overview.current_streak_days >= 2:
            insights.append(f"You're on a {overview.current_streak_days}-day practice streak - keep it going.")
        if overview.strongest_topics:
            insights.append(f"Strongest so far: {', '.join(overview.strongest_topics[:3])}.")
        if overview.weakest_topics:
            insights.append(f"Focus your next sessions on: {', '.join(overview.weakest_topics[:3])}.")
        if overview.in_progress_sessions:
            insights.append(f"You have {overview.in_progress_sessions} session(s) still in progress - finish them for a score.")
        return insights

    @staticmethod
    def _compute_streaks(practice_days: list) -> tuple[int, int]:
        if not practice_days:
            return 0, 0

        longest = 1
        run = 1
        for previous, current in zip(practice_days, practice_days[1:]):
            if current - previous == timedelta(days=1):
                run += 1
            elif current != previous:
                run = 1
            longest = max(longest, run)

        today = datetime.utcnow().date()
        last_day = practice_days[-1]
        if last_day not in (today, today - timedelta(days=1)):
            current_streak = 0
        else:
            current_streak = 1
            cursor = last_day
            for day in reversed(practice_days[:-1]):
                if cursor - day == timedelta(days=1):
                    current_streak += 1
                    cursor = day
                elif cursor - day == timedelta(days=0):
                    continue
                else:
                    break

        return current_streak, longest
