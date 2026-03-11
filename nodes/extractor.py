"""
Node 1: Extractor
=================
Responsibility: Given a source reference (URL, file path, or YouTube URL),
extract the raw text content. This is the entry point of the pipeline.

Input/Output Contract
---------------------
Input:
    state.source_type : str  — "youtube" | "pdf" | "url" | "text"
    state.source_ref  : str  — URL or file path

Output:
    state.raw_text    : str  — Unprocessed raw text from the source

Error Behavior:
    CRITICAL NODE (1 of 4) — raises NodeExtractionError on failure.
    The pipeline halts if extraction fails.

Libraries Used:
    - youtube-transcript-api  (YouTube transcripts)
    - pdfplumber               (PDF text extraction)
    - requests + beautifulsoup4 (web page extraction)

Notes:
    - YouTube: uses auto-generated captions if manual transcript unavailable
    - PDF: extracts text page-by-page; preserves page boundaries with \\n---\\n
    - URL: strips navigation, ads, and boilerplate; keeps main article content
    - Text: passes through as-is
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NodeExtractionError(Exception):
    """Raised when the extractor cannot process the given source."""


@dataclass
class ExtractionResult:
    raw_text: str
    source_type: str
    source_ref: str
    metadata: dict


def extract(source_type: str, source_ref: str) -> ExtractionResult:
    """
    Extract raw text from the given source.

    Parameters
    ----------
    source_type : str
        One of "youtube", "pdf", "url", "text".
    source_ref : str
        The URL or file path to extract from. For "text" type, pass the
        raw text directly as the source_ref.

    Returns
    -------
    ExtractionResult
        Dataclass with raw_text, source_type, source_ref, and metadata dict.

    Raises
    ------
    NodeExtractionError
        If extraction fails for any reason (network error, unsupported format,
        empty transcript, etc.).
    ValueError
        If source_type is not one of the supported types.
    """
    if source_type not in ("youtube", "pdf", "url", "text"):
        raise ValueError(f"Unsupported source_type: {source_type!r}")

    logger.info("Extracting from %s: %s", source_type, source_ref[:80])

    if source_type == "youtube":
        return _extract_youtube(source_ref)
    elif source_type == "pdf":
        return _extract_pdf(source_ref)
    elif source_type == "url":
        return _extract_url(source_ref)
    elif source_type == "text":
        return _extract_text(source_ref)


def _extract_youtube(url: str) -> ExtractionResult:
    """Extract transcript from a YouTube video URL."""
    raise NotImplementedError("Node 1 (YouTube) not yet implemented — Phase 1")


def _extract_pdf(path: str) -> ExtractionResult:
    """Extract text from a PDF file."""
    raise NotImplementedError("Node 1 (PDF) not yet implemented — Phase 1")


def _extract_url(url: str) -> ExtractionResult:
    """Extract article text from a web page URL."""
    raise NotImplementedError("Node 1 (URL) not yet implemented — Phase 1")


def _extract_text(text: str) -> ExtractionResult:
    """Pass through raw text directly."""
    raise NotImplementedError("Node 1 (text) not yet implemented — Phase 1")
