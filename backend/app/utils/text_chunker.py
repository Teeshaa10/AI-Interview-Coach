"""
Text chunking utility used by the resume embedding pipeline.

Splits arbitrary text into overlapping chunks suitable for embedding, while
trying to keep paragraphs intact wherever possible.

Rules implemented:
    - target chunk size:      500 characters
    - overlap between chunks: 100 characters
    - paragraphs (separated by blank lines) are kept whole when they fit
      inside a single chunk; a paragraph larger than the chunk size is
      itself split with a sliding window (still respecting the overlap).
    - empty / whitespace-only chunks are dropped from the output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100

# Two or more consecutive newlines (optionally with whitespace) = paragraph break.
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")
_WHITESPACE_RE = re.compile(r"\s")


@dataclass
class TextChunk:
    """A single chunk of text produced by TextChunker."""

    index: int
    text: str
    start_char: int
    end_char: int
    char_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.char_count = len(self.text)

    def to_metadata(self) -> dict:
        """Metadata dict suitable for storing alongside a vector in Chroma."""
        return {
            "chunk_index": self.index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "char_count": self.char_count,
        }


class TextChunker:
    """
    Paragraph-aware sliding-window text chunker.

    Example:
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk(resume_text)
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def chunk(self, text: str) -> List[TextChunk]:
        """
        Chunk `text` into a list of TextChunk objects.

        Empty input, or input that collapses to nothing after stripping,
        returns an empty list. Empty/whitespace-only intermediate chunks
        are never included in the result.
        """
        if not text or not text.strip():
            return []

        paragraphs = self._split_paragraphs(text)
        if not paragraphs:
            return []

        spans = self._build_spans(text, paragraphs)
        return self._materialize(text, spans)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _split_paragraphs(self, text: str) -> List[Tuple[str, int, int]]:
        """Return list of (paragraph_text, start_char, end_char) with
        whitespace-only segments dropped."""
        paragraphs: List[Tuple[str, int, int]] = []
        last = 0
        for m in _PARAGRAPH_SPLIT_RE.finditer(text):
            self._append_paragraph(paragraphs, text[last:m.start()], last)
            last = m.end()
        self._append_paragraph(paragraphs, text[last:], last)
        return paragraphs

    @staticmethod
    def _append_paragraph(
        paragraphs: List[Tuple[str, int, int]], segment: str, offset: int
    ) -> None:
        stripped = segment.strip()
        if not stripped:
            return
        lstrip_len = len(segment) - len(segment.lstrip())
        start = offset + lstrip_len
        end = start + len(stripped)
        paragraphs.append((stripped, start, end))

    def _build_spans(
        self, text: str, paragraphs: List[Tuple[str, int, int]]
    ) -> List[Tuple[int, int]]:
        """Greedily merge paragraphs into (start, end) spans no larger than
        chunk_size, carrying `chunk_overlap` characters of context forward
        into the next span."""
        spans: List[Tuple[int, int]] = []
        idx = 0
        n = len(paragraphs)
        cur_start = None
        cur_end = None

        while idx < n:
            p_text, p_start, p_end = paragraphs[idx]
            p_len = p_end - p_start

            if cur_start is None:
                if p_len > self.chunk_size:
                    spans.extend(self._sliding_window(p_start, p_end))
                    idx += 1
                    continue
                cur_start, cur_end = p_start, p_end
                idx += 1
                continue

            candidate_len = p_end - cur_start
            if candidate_len <= self.chunk_size:
                cur_end = p_end
                idx += 1
                continue

            if cur_end > cur_start:
                # Flush what we have accumulated so far.
                spans.append((cur_start, cur_end))
                next_start = max(cur_start, cur_end - self.chunk_overlap)
                cur_start, cur_end = next_start, next_start
                continue  # retry this paragraph against the new window

            # Nothing accumulated (fresh/overlap-only window) and it still
            # doesn't fit combined with this paragraph.
            if p_len > self.chunk_size:
                spans.extend(self._sliding_window(p_start, p_end))
                idx += 1
                cur_start = cur_end = None
                continue

            # Drop the carried-over overlap and start clean at this paragraph.
            cur_start, cur_end = p_start, p_end
            idx += 1

        if cur_start is not None and cur_end > cur_start:
            spans.append((cur_start, cur_end))

        return spans

    def _sliding_window(self, start: int, end: int) -> List[Tuple[int, int]]:
        """Split an oversized paragraph's [start, end) range into fixed
        windows of chunk_size with chunk_overlap characters shared between
        consecutive windows."""
        spans: List[Tuple[int, int]] = []
        pos = start
        step = self.chunk_size - self.chunk_overlap
        while pos < end:
            seg_end = min(pos + self.chunk_size, end)
            spans.append((pos, seg_end))
            if seg_end >= end:
                break
            pos += step
        return spans

    def _materialize(
        self, text: str, spans: List[Tuple[int, int]]
    ) -> List[TextChunk]:
        chunks: List[TextChunk] = []
        seen: set = set()
        idx = 0
        for start, end in spans:
            if end <= start:
                continue
            segment = text[start:end]
            lstrip_len = len(segment) - len(segment.lstrip())
            rstrip_len = len(segment) - len(segment.rstrip())
            real_start = start + lstrip_len
            real_end = end - rstrip_len
            if real_end <= real_start:
                continue
            key = (real_start, real_end)
            if key in seen:
                continue
            seen.add(key)
            chunks.append(
                TextChunk(
                    index=idx,
                    text=text[real_start:real_end],
                    start_char=real_start,
                    end_char=real_end,
                )
            )
            idx += 1
        return chunks


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[TextChunk]:
    """Module-level convenience wrapper around TextChunker."""
    return TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap).chunk(text)
