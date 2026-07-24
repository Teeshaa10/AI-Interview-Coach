import uuid
from datetime import datetime

from app.exceptions.coaching import (
    ForbiddenCoachingAccessError,
    PracticePlanItemNotFoundError,
    PracticePlanNotFoundError,
)
from app.prompts.coaching_prompt import build_insight_summary_prompt
from app.repositories.coaching_repository import CoachingRepository
from app.repositories.coding_interview_repository import CodingInterviewRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.coaching import (
    CoachingInsights,
    CoachingProfile,
    NextInterviewRecommendation,
    PracticePlan,
    PracticePlanItem,
    PracticePlanResponse,
)
from app.services.session_management_service import SessionManagementService

_DEFAULT_TOPICS = ["arrays", "system design basics", "behavioral storytelling", "communication clarity"]


class CoachingService:
    """Module 9: builds a coaching profile, insights, a recommended next
    session, and structured practice plans - all derived from data the
    project already collects (Modules 1-8) rather than new tracking, per
    the 'do not add generic hardcoded advice' / 'derive from existing
    data' requirements."""

    def __init__(
        self,
        *,
        session_management_service: SessionManagementService,
        coaching_repository: CoachingRepository,
        interview_repository: InterviewRepository,
        coding_repository: CodingInterviewRepository,
        resume_repository: ResumeRepository,
        gemini_client,
        model_name: str,
    ):
        self.sessions = session_management_service
        self.repository = coaching_repository
        self.interview_repository = interview_repository
        self.coding_repository = coding_repository
        self.resume_repository = resume_repository
        self.gemini_client = gemini_client
        self.model_name = model_name

    async def _target_role(self, user_id: str) -> str | None:
        interviews = await self.interview_repository.get_user_interviews(user_id)
        coding_sessions = await self.coding_repository.list_all_user_sessions(user_id)

        candidates: list[tuple[datetime, str]] = [(i.created_at, i.job_role) for i in interviews]
        candidates += [(s.created_at, s.role) for s in coding_sessions]

        if not candidates:
            return None
        candidates.sort(key=lambda c: c[0], reverse=True)
        return candidates[0][1]

    async def build_profile(self, user_id: str) -> CoachingProfile:
        overview = await self.sessions.get_analytics_overview(user_id)
        resume = await self.resume_repository.get_resume_by_user(user_id)
        target_role = await self._target_role(user_id)

        return CoachingProfile(
            is_new_user=overview.total_sessions == 0,
            has_resume=resume is not None,
            target_role=target_role,
            total_sessions=overview.total_sessions,
            completed_sessions=overview.completed_sessions,
            in_progress_sessions=overview.in_progress_sessions,
            average_score_overall=overview.average_score_overall,
            average_technical_score=overview.average_technical_score,
            average_communication_score=overview.average_communication_score,
            current_streak_days=overview.current_streak_days,
            longest_streak_days=overview.longest_streak_days,
            strongest_topics=overview.strongest_topics,
            weakest_topics=overview.weakest_topics,
            by_type=overview.by_type,
        )

    @staticmethod
    def _readiness(profile: CoachingProfile) -> tuple[str, float]:
        if profile.is_new_user:
            return "getting_started", 5.0

        # Deterministic blend: completion volume (up to 40 pts) + average
        # score (up to 50 pts) + consistency (up to 10 pts). Capped at 100.
        volume_score = min(40.0, profile.completed_sessions * 4.0)
        quality_score = min(50.0, (profile.average_score_overall / 10.0) * 50.0)
        consistency_score = min(10.0, profile.current_streak_days * 2.0)
        score = round(volume_score + quality_score + consistency_score, 1)

        if score < 30:
            level = "getting_started"
        elif score < 60:
            level = "building_confidence"
        elif score < 85:
            level = "interview_ready"
        else:
            level = "highly_prepared"
        return level, score

    async def get_insights(self, user_id: str) -> CoachingInsights:
        profile = await self.build_profile(user_id)
        level, score = self._readiness(profile)

        if profile.is_new_user:
            return CoachingInsights(
                readiness_level=level,
                readiness_score=score,
                top_strengths=[],
                priority_weaknesses=[],
                recommended_topics=_DEFAULT_TOPICS,
                consistency_insight="No practice sessions yet - your first one will unlock personalized insights.",
                next_milestone="Complete your first practice interview.",
                ai_summary=None,
                generated_by_ai=False,
            )

        consistency_insight = (
            f"You're on a {profile.current_streak_days}-day streak (best: {profile.longest_streak_days})."
            if profile.current_streak_days > 0
            else "No active streak - practicing on consecutive days builds momentum faster."
        )

        if level == "highly_prepared":
            next_milestone = "Keep sessions sharp with harder difficulty settings and timed practice."
        elif level == "interview_ready":
            next_milestone = "Polish your weakest topics to move from ready to highly prepared."
        elif level == "building_confidence":
            next_milestone = f"Complete {max(1, 5 - profile.completed_sessions % 5)} more sessions to build consistency."
        else:
            next_milestone = "Finish a few more sessions across all interview types to establish a baseline."

        recommended_topics = profile.weakest_topics[:5] or _DEFAULT_TOPICS

        ai_summary = None
        generated_by_ai = False
        if self.gemini_client is not None:
            try:
                prompt = build_insight_summary_prompt(profile)
                response = await self.gemini_client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                text = (response.text or "").strip()
                if text:
                    ai_summary = text
                    generated_by_ai = True
            except Exception:
                # Gemini being unavailable shouldn't break the coaching page.
                pass

        return CoachingInsights(
            readiness_level=level,
            readiness_score=score,
            top_strengths=profile.strongest_topics[:5],
            priority_weaknesses=profile.weakest_topics[:5],
            recommended_topics=recommended_topics,
            consistency_insight=consistency_insight,
            next_milestone=next_milestone,
            ai_summary=ai_summary,
            generated_by_ai=generated_by_ai,
        )

    async def get_recommendation(self, user_id: str) -> NextInterviewRecommendation:
        profile = await self.build_profile(user_id)

        if profile.is_new_user:
            return NextInterviewRecommendation(
                interview_type="text",
                topic="general behavioral and role fundamentals",
                difficulty="easy",
                target_skill="baseline assessment",
                reason="You haven't completed a practice session yet - a short text interview establishes your baseline.",
                suggested_duration_minutes=20,
                suggested_number_of_questions=5,
                setup_path="/interviews/setup",
            )

        by_type = {t.type: t for t in profile.by_type}
        coding = by_type.get("coding")
        voice = by_type.get("voice")
        text = by_type.get("text")

        # Weak coding performance -> targeted coding practice.
        if coding and coding.completed > 0 and coding.average_score < 6.0:
            return NextInterviewRecommendation(
                interview_type="coding",
                topic=(profile.weakest_topics[0] if profile.weakest_topics else "data structures & algorithms"),
                difficulty="medium",
                target_skill="coding correctness and complexity analysis",
                reason=f"Your average coding score is {coding.average_score}/10 - focused practice should raise it.",
                suggested_duration_minutes=30,
                suggested_number_of_questions=2,
                setup_path="/coding/setup",
            )

        # Strong technical but weak communication -> voice/behavioral practice.
        if profile.average_technical_score >= 7.0 and profile.average_communication_score < 6.0:
            return NextInterviewRecommendation(
                interview_type="voice",
                topic="behavioral communication",
                difficulty="medium",
                target_skill="verbal communication clarity",
                reason=(
                    f"Your technical score ({profile.average_technical_score}/10) is strong, but communication "
                    f"({profile.average_communication_score}/10) is lagging behind."
                ),
                suggested_duration_minutes=25,
                suggested_number_of_questions=6,
                setup_path="/voice/setup",
            )

        # Repeated weakness in a topic -> focused technical interview.
        if profile.weakest_topics:
            return NextInterviewRecommendation(
                interview_type="text",
                topic=profile.weakest_topics[0],
                difficulty="medium",
                target_skill=profile.weakest_topics[0],
                reason=f"'{profile.weakest_topics[0]}' keeps showing up as a weak area across your reports.",
                suggested_duration_minutes=25,
                suggested_number_of_questions=6,
                setup_path="/interviews/setup",
            )

        # Least-practiced type -> round out experience.
        least_practiced = min(
            (t for t in (text, voice, coding) if t is not None),
            key=lambda t: t.total,
            default=None,
        )
        if least_practiced is not None and least_practiced.type == "coding":
            setup_path, itype = "/coding/setup", "coding"
        elif least_practiced is not None and least_practiced.type == "voice":
            setup_path, itype = "/voice/setup", "voice"
        else:
            setup_path, itype = "/interviews/setup", "text"

        return NextInterviewRecommendation(
            interview_type=itype,
            topic="well-rounded practice",
            difficulty="medium",
            target_skill="overall interview readiness",
            reason="Your performance is fairly balanced - keep practicing across all interview types.",
            suggested_duration_minutes=25,
            suggested_number_of_questions=6,
            setup_path=setup_path,
        )

    @staticmethod
    def _to_response(plan: PracticePlan) -> PracticePlanResponse:
        completed = sum(1 for item in plan.items if item.completed)
        return PracticePlanResponse(
            id=plan.id or "",
            duration_days=plan.duration_days,
            items=plan.items,
            completed_items=completed,
            total_items=len(plan.items),
            completion_percentage=plan.completion_percentage,
            created_at=plan.created_at,
        )

    async def _generate_plan_items(self, user_id: str, duration_days: int) -> list[PracticePlanItem]:
        profile = await self.build_profile(user_id)
        recommendation = await self.get_recommendation(user_id)

        weak_topics = profile.weakest_topics or _DEFAULT_TOPICS
        interview_cycle: list[tuple[str, str]] = [
            ("text", "/interviews/setup"),
            ("coding", "/coding/setup"),
            ("voice", "/voice/setup"),
        ]

        # Bias the cycle toward the recommended interview type so the plan
        # actually reflects the person's current weak spot.
        interview_cycle.sort(key=lambda pair: pair[0] != recommendation.interview_type)

        items: list[PracticePlanItem] = []
        sessions_per_week = 3 if duration_days == 7 else (4 if duration_days == 14 else 5)
        practice_days = sorted(
            {round(i * duration_days / sessions_per_week) + 1 for i in range(sessions_per_week)}
        )
        practice_days = [d for d in practice_days if 1 <= d <= duration_days] or [1]

        for index, day in enumerate(practice_days):
            interview_type, setup_path = interview_cycle[index % len(interview_cycle)]
            topic = weak_topics[index % len(weak_topics)]
            difficulty = "easy" if profile.is_new_user or index == 0 else "medium"

            items.append(
                PracticePlanItem(
                    item_id=str(uuid.uuid4()),
                    day_number=day,
                    focus_area=topic,
                    interview_type=interview_type,
                    topic=topic,
                    difficulty=difficulty,
                    estimated_minutes=25 if interview_type != "coding" else 35,
                    objective=f"Strengthen {topic} through a {interview_type} practice session.",
                    recommended_activity=f"Start a {interview_type} interview focused on {topic} ({setup_path}).",
                    reason=(
                        f"Prioritized because '{topic}' is a current weak area."
                        if topic in profile.weakest_topics
                        else "Rounds out practice across interview types."
                    ),
                    completed=False,
                )
            )

        return items

    async def create_plan(self, user_id: str, duration_days: int) -> PracticePlanResponse:
        items = await self._generate_plan_items(user_id, duration_days)
        plan = PracticePlan(user_id=user_id, duration_days=duration_days, items=items, is_active=True)

        await self.repository.deactivate_all_plans(user_id)
        plan.id = await self.repository.create_plan(plan)
        return self._to_response(plan)

    async def get_active_plan(self, user_id: str) -> PracticePlanResponse | None:
        plan = await self.repository.get_active_plan(user_id)
        if plan is None:
            return None
        return self._to_response(plan)

    async def regenerate_plan(self, user_id: str, plan_id: str) -> PracticePlanResponse:
        existing = await self.repository.get_plan(plan_id)
        if existing is None:
            raise PracticePlanNotFoundError()
        if existing.user_id != user_id:
            raise ForbiddenCoachingAccessError()
        return await self.create_plan(user_id, existing.duration_days)

    async def set_item_completion(self, user_id: str, plan_id: str, item_id: str, completed: bool) -> PracticePlanResponse:
        plan = await self.repository.get_plan(plan_id)
        if plan is None:
            raise PracticePlanNotFoundError()
        if plan.user_id != user_id:
            raise ForbiddenCoachingAccessError()
        if not any(item.item_id == item_id for item in plan.items):
            raise PracticePlanItemNotFoundError()

        updated = await self.repository.set_item_completion(plan_id, user_id, item_id, completed)
        if not updated:
            raise PracticePlanItemNotFoundError()

        refreshed = await self.repository.get_plan(plan_id)
        return self._to_response(refreshed)  # type: ignore[arg-type]
