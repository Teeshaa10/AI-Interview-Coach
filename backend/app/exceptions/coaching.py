from fastapi import status


class CoachingError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class PracticePlanNotFoundError(CoachingError):
    def __init__(self):
        super().__init__("Practice plan not found", status.HTTP_404_NOT_FOUND)


class ForbiddenCoachingAccessError(CoachingError):
    def __init__(self):
        super().__init__("Access denied", status.HTTP_403_FORBIDDEN)


class PracticePlanItemNotFoundError(CoachingError):
    def __init__(self):
        super().__init__("Practice plan item not found", status.HTTP_404_NOT_FOUND)


class InvalidPlanDurationError(CoachingError):
    def __init__(self, duration_days: int):
        super().__init__(
            f"Unsupported plan duration: {duration_days} days (use 7, 14, or 30)",
            status.HTTP_400_BAD_REQUEST,
        )
