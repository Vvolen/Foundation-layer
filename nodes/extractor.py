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
import re
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


# ---------------------------------------------------------------------------
# YouTube Extraction
# ---------------------------------------------------------------------------

def _parse_youtube_video_id(url: str) -> str:
    """Extract the video ID from various YouTube URL formats."""
    patterns = [
        r"(?:v=|/v/)([a-zA-Z0-9_-]{11})",          # Standard & /v/ embed
        r"(?:/embed/)([a-zA-Z0-9_-]{11})",          # /embed/ URL
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",       # Short URL
        r"(?:shorts/)([a-zA-Z0-9_-]{11})",           # Shorts
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # Maybe the source_ref IS the video ID directly (11 chars)
    stripped = url.strip()
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", stripped):
        return stripped

    raise NodeExtractionError(
        f"Could not extract YouTube video ID from: {url!r}"
    )


def _extract_youtube(url: str) -> ExtractionResult:
    """Extract transcript from a YouTube video URL."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as e:
        raise NodeExtractionError(
            "youtube-transcript-api is not installed. "
            "Run: pip install youtube-transcript-api"
        ) from e

    video_id = _parse_youtube_video_id(url)
    logger.info("YouTube video ID: %s", video_id)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except Exception as e:
        raise NodeExtractionError(
            f"Failed to list transcripts for video {video_id}: {e}"
        ) from e

    # Prefer manually created transcripts, fall back to auto-generated
    transcript = None
    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
        logger.info("Using manually created English transcript")
    except Exception:
        try:
            transcript = transcript_list.find_generated_transcript(["en"])
            logger.info("Using auto-generated English transcript")
        except Exception:
            # Try any available transcript and translate to English
            try:
                for t in transcript_list:
                    transcript = t.translate("en")
                    logger.info("Translated transcript from %s to English", t.language_code)
                    break
            except Exception:
                pass

    if transcript is None:
        raise NodeExtractionError(
            f"No usable transcript found for video {video_id}"
        )

    try:
        segments = transcript.fetch()
    except Exception as e:
        raise NodeExtractionError(
            f"Failed to fetch transcript segments for {video_id}: {e}"
        ) from e

    if not segments:
        raise NodeExtractionError(
            f"Transcript for {video_id} returned 0 segments"
        )

    # Build raw text from segments — include timestamps as markers
    lines = []
    for seg in segments:
        text = seg.get("text", seg.text if hasattr(seg, "text") else str(seg))
        start = seg.get("start", getattr(seg, "start", None))
        if start is not None:
            minutes = int(float(start)) // 60
            seconds = int(float(start)) % 60
            lines.append(f"[{minutes}:{seconds:02d}] {text}")
        else:
            lines.append(text)

    raw_text = "\n".join(lines)

    if not raw_text.strip():
        raise NodeExtractionError(
            f"Transcript for {video_id} produced empty text"
        )

    return ExtractionResult(
        raw_text=raw_text,
        source_type="youtube",
        source_ref=url,
        metadata={
            "video_id": video_id,
            "segment_count": len(segments),
            "transcript_type": "manual" if "manual" in str(type(transcript)).lower() else "auto",
        },
    )


# ---------------------------------------------------------------------------
# PDF Extraction
# ---------------------------------------------------------------------------

def _extract_pdf(path: str) -> ExtractionResult:
    """Extract text from a PDF file."""
    try:
        import pdfplumber
    except ImportError as e:
        raise NodeExtractionError(
            "pdfplumber is not installed. Run: pip install pdfplumber"
        ) from e

    from pathlib import Path
    pdf_path = Path(path)
    if not pdf_path.exists():
        raise NodeExtractionError(f"PDF file not found: {path}")

    try:
        pages_text = []
        metadata = {}
        with pdfplumber.open(pdf_path) as pdf:
            metadata["page_count"] = len(pdf.pages)
            if pdf.metadata:
                metadata["pdf_metadata"] = {
                    k: str(v) for k, v in pdf.metadata.items() if v
                }
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(text)
                else:
                    logger.debug("Page %d yielded no text", i + 1)

        if not pages_text:
            raise NodeExtractionError(
                f"PDF {path} contains no extractable text "
                f"({metadata.get('page_count', 0)} pages scanned)"
            )

        raw_text = "\n---\n".join(pages_text)

        return ExtractionResult(
            raw_text=raw_text,
            source_type="pdf",
            source_ref=path,
            metadata=metadata,
        )

    except NodeExtractionError:
        raise
    except Exception as e:
        raise NodeExtractionError(f"Failed to extract PDF {path}: {e}") from e


# ---------------------------------------------------------------------------
# URL / Web Page Extraction
# ---------------------------------------------------------------------------

def _extract_url(url: str) -> ExtractionResult:
    """Extract article text from a web page URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise NodeExtractionError(
            "requests and/or beautifulsoup4 not installed. "
            "Run: pip install requests beautifulsoup4"
        ) from e

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise NodeExtractionError(f"Failed to fetch URL {url}: {e}") from e

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract title
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)

    # Remove noise elements
    for tag_name in ["script", "style", "nav", "footer", "header", "aside",
                     "noscript", "iframe", "form"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove common ad/nav classes
    for selector in [".sidebar", ".navigation", ".menu", ".ads", ".cookie",
                     ".popup", ".modal", "#cookie", "#nav", "#sidebar",
                     '[role="navigation"]', '[role="banner"]',
                     '[role="complementary"]']:
        for el in soup.select(selector):
            el.decompose()

    # Extract main content — try progressively broader selectors
    content = None
    for selector in ["article", "main", '[role="main"]',
                     ".post-content", ".article-content", ".entry-content",
                     ".content", "#content"]:
        content = soup.select_one(selector)
        if content:
            break

    # Fallback: use body
    if content is None:
        content = soup.find("body")

    if content is None:
        raise NodeExtractionError(f"Could not find any content on page: {url}")

    # Extract text with paragraph separation
    paragraphs = []
    for el in content.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6",
                                 "li", "blockquote", "pre", "td"]):
        text = el.get_text(separator=" ", strip=True)
        if text and len(text) > 10:  # Skip tiny fragments
            paragraphs.append(text)

    # If structured extraction yields little, fall back to get_text
    if len(paragraphs) < 3:
        raw_text = content.get_text(separator="\n", strip=True)
    else:
        raw_text = "\n\n".join(paragraphs)

    if not raw_text.strip():
        raise NodeExtractionError(f"Extracted empty content from URL: {url}")

    return ExtractionResult(
        raw_text=raw_text,
        source_type="url",
        source_ref=url,
        metadata={
            "title": title,
            "content_length": len(resp.text),
            "status_code": resp.status_code,
        },
    )


# ---------------------------------------------------------------------------
# Plain Text Extraction
# ---------------------------------------------------------------------------

def _extract_text(text: str) -> ExtractionResult:
    """Pass through raw text directly."""
    if not text or not text.strip():
        raise NodeExtractionError("Input text is empty or None")

    return ExtractionResult(
        raw_text=text,
        source_type="text",
        source_ref="<direct_text_input>",
        metadata={
            "input_length": len(text),
        },
    )