from fastapi import status


class ReportError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class ReportNotFoundError(ReportError):
    def __init__(self):
        super().__init__("Report not found", status.HTTP_404_NOT_FOUND)


class InterviewNotCompleteError(ReportError):
    def __init__(self):
        super().__init__("Interview must be completed before generating a report", status.HTTP_409_CONFLICT)


class ReportAlreadyExistsError(ReportError):
    def __init__(self):
        super().__init__("A report already exists for this interview", status.HTTP_409_CONFLICT)


class ForbiddenReportAccessError(ReportError):
    def __init__(self):
        super().__init__("Access denied", status.HTTP_403_FORBIDDEN)
