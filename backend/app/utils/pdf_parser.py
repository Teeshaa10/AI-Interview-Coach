import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from every page of a PDF.

    This function is synchronous because pdfplumber is synchronous. The service
    executes it through asyncio.to_thread to avoid blocking FastAPI's event loop.
    """

    if not file_path.is_file():
        raise FileNotFoundError(f"PDF file does not exist: {file_path}")

    page_texts: list[str] = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                try:
                    text = (page.extract_text() or "").strip()
                except Exception:
                    logger.exception(
                        "Failed to extract PDF page",
                        extra={
                            "file_path": str(file_path),
                            "page_number": page_number,
                        },
                    )
                    raise

                if text:
                    page_texts.append(text)
    except Exception as exc:
        logger.exception(
            "PDF parsing failed",
            extra={"file_path": str(file_path)},
        )
        raise RuntimeError("Unable to parse the uploaded PDF document") from exc

    extracted_text = "\n\n".join(page_texts).strip()

    if not extracted_text:
        raise ValueError(
            "No readable text was found in the PDF. "
            "Image-only PDFs require OCR, which is not enabled."
        )

    return extracted_text
