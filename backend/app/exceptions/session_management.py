from fastapi import status


class SessionManagementError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class SessionNotFoundError(SessionManagementError):
    def __init__(self):
        super().__init__("Session not found", status.HTTP_404_NOT_FOUND)


class ForbiddenSessionAccessError(SessionManagementError):
    def __init__(self):
        super().__init__("Access denied", status.HTTP_403_FORBIDDEN)


class InvalidSessionTypeError(SessionManagementError):
    def __init__(self, session_type: str):
        super().__init__(f"Unknown session type: {session_type}", status.HTTP_400_BAD_REQUEST)
