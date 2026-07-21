from collections import Counter, defaultdict
from datetime import datetime

from app.exceptions.report import InterviewNotCompleteError, ReportAlreadyExistsError
from app.repositories.interview_report_repository import InterviewReportRepository
from app.repositories.interview_repository import InterviewRepository
from app.schemas.interview_report import InterviewReport, QuestionReportItem


class InterviewReportService:
    def __init__(self, interview_repository: InterviewRepository, report_repository: InterviewReportRepository):
        self.interview_repository = interview_repository
        self.report_repository = report_repository

    async def generate(self, *, interview_id: str, user_id: str, regenerate: bool = False) -> InterviewReport:
        interview = await self.interview_repository.get_interview_by_id(interview_id)
        if interview is None:
            from app.exceptions.report import ReportError
            raise ReportError("Interview not found", 404)
        if interview.user_id != user_id:
            from app.exceptions.report import ForbiddenReportAccessError
            raise ForbiddenReportAccessError()
        if not interview.completed:
            raise InterviewNotCompleteError()

        existing = await self.report_repository.get_by_interview_id(interview_id)
        if existing and not regenerate:
            raise ReportAlreadyExistsError()

        answered = [q for q in interview.questions if q.answer]
        total = len(interview.questions)

        def avg(values: list[float | None]) -> float:
            clean = [float(v) for v in values if v is not None]
            return round(sum(clean) / len(clean), 2) if clean else 0.0

        category_values: dict[str, list[float]] = defaultdict(list)
        strengths_counter: Counter[str] = Counter()
        weaknesses_counter: Counter[str] = Counter()
        breakdown = []

        for question in interview.questions:
            if question.overall_score is not None:
                category_values[question.category].append(question.overall_score)
            strengths_counter.update(s.strip() for s in question.strengths if s.strip())
            weaknesses_counter.update(w.strip() for w in question.weaknesses if w.strip())
            breakdown.append(QuestionReportItem(
                question_number=question.question_number,
                question=question.question,
                category=question.category,
                answer=question.answer,
                technical_score=question.technical_score,
                communication_score=question.communication_score,
                completeness_score=question.completeness_score,
                overall_score=question.overall_score,
                strengths=question.strengths,
                weaknesses=question.weaknesses,
                feedback=question.feedback,
                improved_answer=question.better_answer,
            ))

        overall = avg([q.overall_score for q in answered])
        technical = avg([q.technical_score for q in answered])
        communication = avg([q.communication_score for q in answered])
        completeness = avg([q.completeness_score for q in answered])
        category_scores = {key: avg(value) for key, value in category_values.items()}
        strengths = [item for item, _ in strengths_counter.most_common(5)]
        weaknesses = [item for item, _ in weaknesses_counter.most_common(5)]
        weak_topics = [category for category, score in sorted(category_scores.items(), key=lambda x: x[1]) if score < 6.5][:3]

        improvement_plan = []
        if technical < 7:
            improvement_plan.append("Review core technical concepts and practise explaining trade-offs with examples.")
        if communication < 7:
            improvement_plan.append("Use a structured answer format: context, approach, result, and reflection.")
        if completeness < 7:
            improvement_plan.append("Address every part of the question and include measurable outcomes where possible.")
        if weak_topics:
            improvement_plan.append(f"Prioritise practice for: {', '.join(weak_topics)}.")
        if not improvement_plan:
            improvement_plan.append("Continue with harder mock interviews and refine concise, evidence-based answers.")

        next_difficulty = "hard" if overall >= 8 else "medium" if overall >= 6 else "easy"
        summary = (
            f"Completed {len(answered)} of {total} questions with an overall score of {overall}/10. "
            f"Technical: {technical}/10, communication: {communication}/10, completeness: {completeness}/10."
        )

        report = InterviewReport(
            user_id=user_id,
            interview_id=interview_id,
            job_role=interview.job_role,
            experience_level=interview.experience_level,
            total_questions=total,
            answered_questions=len(answered),
            completion_percentage=round((len(answered) / total) * 100, 2) if total else 0.0,
            overall_score=overall,
            technical_score=technical,
            communication_score=communication,
            completeness_score=completeness,
            category_scores=category_scores,
            question_breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
            weak_topics=weak_topics,
            improvement_plan=improvement_plan,
            recommended_next_difficulty=next_difficulty,
            summary=summary,
            interview_completed_at=interview.completed_at,
            updated_at=datetime.utcnow(),
        )

        if existing:
            report.id = await self.report_repository.replace_for_interview(report)
        else:
            report.id = await self.report_repository.create(report)
        return report
