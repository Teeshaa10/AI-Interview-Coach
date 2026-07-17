from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeResponse(BaseModel):
    """Public API representation of a stored resume."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    filename: str
    original_filename: str
    file_type: str
    file_path: str
    extracted_text: str
    created_at: datetime
    updated_at: datetime


class UploadResponse(BaseModel):
    """Response returned after a successful upload and parsing operation."""

    message: str = Field(default="Resume uploaded and parsed successfully")
    resume: ResumeResponse


class DeleteResumeResponse(BaseModel):
    """Response returned after a resume is deleted."""

    message: str = Field(default="Resume deleted successfully")
