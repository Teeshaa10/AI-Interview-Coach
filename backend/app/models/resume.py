from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class Resume:
    """
    Domain model representing a resume stored by the application.

    The domain model is independent of FastAPI and MongoDB so the service layer
    does not depend directly on transport or persistence implementation details.
    """

    id: str
    user_id: str
    filename: str
    original_filename: str
    file_type: str
    file_path: str
    extracted_text: str
    created_at: datetime
    updated_at: datetime
