from collections import Counter, defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_user
from app.exceptions.report import ForbiddenReportAccessError, ReportNotFoundError
from app.models.user import UserInDB
from app.report_dependencies import get_interview_report_repository, get_interview_report_service
from app.repositories.interview_report_repository import InterviewReportRepository
from app.schemas.interview_report import (
    GenerateReportRequest,
    InterviewReport,
    ReportAnalyticsSummary,
    ReportHistoryResponse,
    ReportTrendsResponse,
    ScoreTrendPoint,
)
from app.services.interview_report_service import InterviewReportService

router = APIRouter(prefix="/reports", tags=["Advanced Interview Reports"])


def _check_owner(report: InterviewReport | None, user_id: str) -> InterviewReport:
    if report is None:
        raise ReportNotFoundError()
    if report.user_id != user_id:
        raise ForbiddenReportAccessError()
    return report


@router.post("/interview/{interview_id}/generate", response_model=InterviewReport, status_code=status.HTTP_201_CREATED)
async def generate_report(
    interview_id: str,
    request: GenerateReportRequest,
    current_user: UserInDB = Depends(get_current_user),
    service: InterviewReportService = Depends(get_interview_report_service),
):
    return await service.generate(interview_id=interview_id, user_id=current_user.id, regenerate=request.regenerate)


@router.get("/interview/{interview_id}", response_model=InterviewReport)
async def get_report_by_interview(
    interview_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewReportRepository = Depends(get_interview_report_repository),
):
    return _check_owner(await repository.get_by_interview_id(interview_id), current_user.id)


@router.get("/history", response_model=ReportHistoryResponse)
async def report_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewReportRepository = Depends(get_interview_report_repository),
):
    reports, total = await repository.list_user_reports(current_user.id, page, limit)
    return ReportHistoryResponse(reports=reports, page=page, limit=limit, total=total)


@router.get("/analytics/summary", response_model=ReportAnalyticsSummary)
async def analytics_summary(
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewReportRepository = Depends(get_interview_report_repository),
):
    reports = await repository.list_all_user_reports(current_user.id)
    if not reports:
        return ReportAnalyticsSummary(
            interviews_completed=0,
            average_overall_score=0,
            best_score=0,
            latest_score=0,
            technical_average=0,
            communication_average=0,
            completeness_average=0,
            strongest_topics=[],
            weakest_topics=[],
            recent_improvement_percentage=None,
            score_trend=[],
        )

    def avg(values: list[float]) -> float:
        return round(sum(values) / len(values), 2) if values else 0.0

    strengths = Counter(item for report in reports for item in report.strengths)
    weaknesses = Counter(item for report in reports for item in report.weak_topics + report.weaknesses)
    improvement = None
    if len(reports) >= 2 and reports[-2].overall_score:
        improvement = round(((reports[-1].overall_score - reports[-2].overall_score) / reports[-2].overall_score) * 100, 2)

    return ReportAnalyticsSummary(
        interviews_completed=len(reports),
        average_overall_score=avg([r.overall_score for r in reports]),
        best_score=max(r.overall_score for r in reports),
        latest_score=reports[-1].overall_score,
        technical_average=avg([r.technical_score for r in reports]),
        communication_average=avg([r.communication_score for r in reports]),
        completeness_average=avg([r.completeness_score for r in reports]),
        strongest_topics=[x for x, _ in strengths.most_common(5)],
        weakest_topics=[x for x, _ in weaknesses.most_common(5)],
        recent_improvement_percentage=improvement,
        score_trend=[ScoreTrendPoint(
            date=r.interview_completed_at or r.created_at,
            overall_score=r.overall_score,
            technical_score=r.technical_score,
            communication_score=r.communication_score,
        ) for r in reports],
    )


@router.get("/analytics/trends", response_model=ReportTrendsResponse)
async def analytics_trends(
    grouping: str = Query("weekly", pattern="^(weekly|monthly)$"),
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewReportRepository = Depends(get_interview_report_repository),
):
    reports = await repository.list_all_user_reports(current_user.id)
    buckets: dict[str, list[InterviewReport]] = defaultdict(list)
    for report in reports:
        date = report.interview_completed_at or report.created_at
        key = f"{date.isocalendar().year}-W{date.isocalendar().week:02d}" if grouping == "weekly" else date.strftime("%Y-%m")
        buckets[key].append(report)
    points = []
    for period, values in sorted(buckets.items()):
        points.append({
            "period": period,
            "interviews": len(values),
            "average_overall_score": round(sum(v.overall_score for v in values) / len(values), 2),
            "average_technical_score": round(sum(v.technical_score for v in values) / len(values), 2),
            "average_communication_score": round(sum(v.communication_score for v in values) / len(values), 2),
        })
    return ReportTrendsResponse(grouping=grouping, points=points)


@router.get("/{report_id}", response_model=InterviewReport)
async def get_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewReportRepository = Depends(get_interview_report_repository),
):
    return _check_owner(await repository.get_by_id(report_id), current_user.id)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewReportRepository = Depends(get_interview_report_repository),
):
    report = _check_owner(await repository.get_by_id(report_id), current_user.id)
    if not await repository.delete(report.id or report_id, current_user.id):
        raise ReportNotFoundError()
