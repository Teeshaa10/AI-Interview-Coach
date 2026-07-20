import asyncio
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile
from pymongo.errors import PyMongoError

from app.exceptions.resume import (
    InvalidResumeFileError,
    ResumeAccessDeniedError,
    ResumeFileTooLargeError,
    ResumeNotFoundError,
    ResumeParsingError,
    ResumeStorageError,
)
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.semantic_search_service import SemanticSearchService
from app.utils.docx_parser import extract_text_from_docx
from app.utils.pdf_parser import extract_text_from_pdf

logger = logging.getLogger(__name__)


class ResumeService:
    """
    Business-logic layer for resume operations.

    It coordinates validation, streaming file storage, signature checks, text
    extraction, MongoDB persistence, authorization, and rollback cleanup.
    """

    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
    READ_CHUNK_SIZE_BYTES = 1024 * 1024

    ALLOWED_EXTENSIONS = {
        ".pdf": "pdf",
        ".docx": "docx",
    }

    ALLOWED_CONTENT_TYPES = {
        ".pdf": {
            "application/pdf",
            "application/octet-stream",
        },
        ".docx": {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/octet-stream",
            "application/zip",
        },
    }

    def __init__(
        self,
        repository: ResumeRepository,
        upload_directory: Path,
        semantic_search_service: SemanticSearchService,
    ) -> None:
        self._repository = repository
        self._upload_directory = upload_directory
        self._semantic_search_service = semantic_search_service

    async def upload_resume(
        self,
        *,
        user_id: str,
        upload_file: UploadFile,
    ) -> Resume:
        """
        Validate, store, parse, and persist an uploaded resume.

        The file is deleted automatically when parsing or database persistence
        fails so orphaned files are not left on disk.
        """

        original_filename, extension, file_type = self._validate_metadata(
            upload_file
        )

        await asyncio.to_thread(
            self._upload_directory.mkdir,
            parents=True,
            exist_ok=True,
        )

        stored_filename = f"{uuid4().hex}{extension}"
        stored_path = self._upload_directory / stored_filename
        resume: Resume | None = None

        try:
            await self._save_upload(upload_file, stored_path)

            await asyncio.to_thread(
                self._validate_file_signature,
                stored_path,
                extension,
            )

            extracted_text = await self._extract_text(
                stored_path,
                file_type,
            )

            timestamp = datetime.now(timezone.utc)

            resume = await self._repository.create_resume(
                user_id=user_id,
                filename=stored_filename,
                original_filename=original_filename,
                file_type=file_type,
                file_path=str(stored_path.resolve()),
                extracted_text=extracted_text,
                created_at=timestamp,
                updated_at=timestamp,
            )

            await self._semantic_search_service.index_resume(
                resume_id=resume.id,
                user_id=user_id,
                filename=original_filename,
                text=extracted_text,
            )

            logger.info(
                "Resume uploaded and indexed",
                extra={
                    "resume_id": resume.id,
                    "user_id": user_id,
                    "file_type": file_type,
                },
            )

            return resume

        except (
            InvalidResumeFileError,
            ResumeFileTooLargeError,
            ResumeParsingError,
        ):
            await self._remove_file_safely(stored_path)
            raise

        except PyMongoError as exc:
            if resume is not None:
                await self._rollback_persisted_resume(resume)

            await self._remove_file_safely(stored_path)

            logger.exception(
                "Database failure while storing resume",
                extra={"user_id": user_id},
            )

            raise ResumeStorageError(
                "The resume was parsed but could not be saved"
            ) from exc

        except OSError as exc:
            if resume is not None:
                await self._rollback_persisted_resume(resume)

            await self._remove_file_safely(stored_path)

            logger.exception(
                "Filesystem failure during resume upload",
                extra={"file_path": str(stored_path)},
            )

            raise ResumeStorageError(
                "The resume file could not be stored"
            ) from exc

        except Exception as exc:
            if resume is not None:
                await self._rollback_persisted_resume(resume)

            await self._remove_file_safely(stored_path)

            logger.exception(
                "Unexpected resume upload failure",
                extra={"user_id": user_id},
            )

            raise ResumeStorageError(
                "An unexpected error occurred while processing the resume"
            ) from exc

        finally:
            await upload_file.close()

    async def get_resume_for_user(
        self,
        *,
        user_id: str,
    ) -> Resume:
        """Return the authenticated user's latest resume."""

        try:
            resume = await self._repository.get_resume_by_user(user_id)

        except PyMongoError as exc:
            logger.exception(
                "Failed to retrieve user resume",
                extra={"user_id": user_id},
            )

            raise ResumeStorageError(
                "The resume could not be retrieved"
            ) from exc

        if resume is None:
            raise ResumeNotFoundError(
                "No resume has been uploaded by this user"
            )

        return resume

    async def delete_resume(
        self,
        *,
        resume_id: str,
        user_id: str,
    ) -> None:
        """Delete a resume only when it belongs to the authenticated user."""

        try:
            resume = await self._repository.get_resume_by_id(resume_id)

        except PyMongoError as exc:
            raise ResumeStorageError(
                "The resume could not be retrieved"
            ) from exc

        if resume is None:
            raise ResumeNotFoundError()

        if resume.user_id != user_id:
            logger.warning(
                "Unauthorized resume deletion attempt",
                extra={
                    "resume_id": resume_id,
                    "requesting_user_id": user_id,
                },
            )

            raise ResumeAccessDeniedError()

        try:
            await self._semantic_search_service.delete_resume_embeddings(
                resume_id=resume_id,
                user_id=user_id,
            )

            deleted = await self._repository.delete_resume(resume_id)

        except Exception as exc:
            logger.exception(
                "Failed to delete resume and embeddings",
                extra={
                    "resume_id": resume_id,
                    "user_id": user_id,
                },
            )

            raise ResumeStorageError(
                "The resume and its embeddings could not be deleted"
            ) from exc

        if not deleted:
            raise ResumeNotFoundError()

        await self._remove_file_safely(Path(resume.file_path))

    async def _rollback_persisted_resume(
        self,
        resume: Resume,
    ) -> None:
        try:
            await self._semantic_search_service.delete_resume_embeddings(
                resume_id=resume.id,
                user_id=resume.user_id,
            )

        except Exception:
            logger.exception(
                "Failed to roll back resume embeddings",
                extra={"resume_id": resume.id},
            )

        try:
            await self._repository.delete_resume(resume.id)

        except Exception:
            logger.exception(
                "Failed to roll back resume document",
                extra={"resume_id": resume.id},
            )

    def _validate_metadata(
        self,
        upload_file: UploadFile,
    ) -> tuple[str, str, str]:
        """Validate the filename extension and declared MIME type."""

        if not upload_file.filename:
            raise InvalidResumeFileError(
                "The uploaded file must have a filename"
            )

        original_filename = Path(upload_file.filename).name.strip()

        if not original_filename:
            raise InvalidResumeFileError(
                "The filename is invalid"
            )

        extension = Path(original_filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise InvalidResumeFileError(
                "Only PDF and DOCX files are supported"
            )

        content_type = (
            upload_file.content_type or "application/octet-stream"
        ).lower()

        if content_type not in self.ALLOWED_CONTENT_TYPES[extension]:
            raise InvalidResumeFileError(
                "The uploaded file content type does not match its extension"
            )

        return (
            original_filename,
            extension,
            self.ALLOWED_EXTENSIONS[extension],
        )

    async def _save_upload(
        self,
        upload_file: UploadFile,
        destination: Path,
    ) -> None:
        """Stream the upload to disk while enforcing the 10 MB limit."""

        total_size = 0

        async with aiofiles.open(destination, "wb") as output_file:
            while chunk := await upload_file.read(
                self.READ_CHUNK_SIZE_BYTES
            ):
                total_size += len(chunk)

                if total_size > self.MAX_FILE_SIZE_BYTES:
                    raise ResumeFileTooLargeError(
                        "Resume files must not exceed 10 MB"
                    )

                await output_file.write(chunk)

        if total_size == 0:
            raise InvalidResumeFileError(
                "The uploaded resume is empty"
            )

    @staticmethod
    def _validate_file_signature(
        file_path: Path,
        extension: str,
    ) -> None:
        """Verify the actual file format instead of trusting metadata alone."""

        if extension == ".pdf":
            with file_path.open("rb") as file:
                if file.read(5) != b"%PDF-":
                    raise InvalidResumeFileError(
                        "The uploaded file is not a valid PDF"
                    )

            return

        if extension == ".docx":
            try:
                with zipfile.ZipFile(file_path) as archive:
                    entries = set(archive.namelist())

            except (zipfile.BadZipFile, OSError) as exc:
                raise InvalidResumeFileError(
                    "The uploaded file is not a valid DOCX"
                ) from exc

            required_entries = {
                "[Content_Types].xml",
                "word/document.xml",
            }

            if not required_entries.issubset(entries):
                raise InvalidResumeFileError(
                    "The uploaded file is not a valid DOCX"
                )

            return

        raise InvalidResumeFileError(
            "Unsupported resume format"
        )

    async def _extract_text(
        self,
        file_path: Path,
        file_type: str,
    ) -> str:
        """Run synchronous parser libraries outside the event loop."""

        try:
            if file_type == "pdf":
                return await asyncio.to_thread(
                    extract_text_from_pdf,
                    file_path,
                )

            if file_type == "docx":
                return await asyncio.to_thread(
                    extract_text_from_docx,
                    file_path,
                )

            raise InvalidResumeFileError(
                "Unsupported resume format"
            )

        except InvalidResumeFileError:
            raise

        except (ValueError, RuntimeError) as exc:
            raise ResumeParsingError(str(exc)) from exc

        except Exception as exc:
            logger.exception(
                "Unexpected resume parser failure",
                extra={
                    "file_path": str(file_path),
                    "file_type": file_type,
                },
            )

            raise ResumeParsingError(
                "The uploaded resume could not be parsed"
            ) from exc

    @staticmethod
    async def _remove_file_safely(
        file_path: Path,
    ) -> None:
        """Delete a file without replacing the original application error."""

        try:
            await asyncio.to_thread(
                file_path.unlink,
                missing_ok=True,
            )

        except OSError:
            logger.exception(
                "Failed to remove resume file",
                extra={"file_path": str(file_path)},
            )