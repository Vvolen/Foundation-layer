"""
Node 2: Cleaner
===============
Responsibility: Takes raw extracted text and normalizes it for downstream
processing. Removes artifacts, normalizes whitespace, strips timestamps,
and produces clean, consistent text ready for chunking.

Input/Output Contract
---------------------
Input:
    state.raw_text  : str  — Raw text from Node 1

Output:
    state.clean_text : str  — Normalized, cleaned text

Error Behavior:
    CRITICAL NODE (2 of 4) — raises NodeCleaningError on failure.

Libraries Used:
    - re    (regex for pattern-based cleaning)
    - unicodedata (Unicode normalization)

Cleaning Steps Applied:
    1. Unicode normalization (NFC)
    2. Remove YouTube timestamp patterns (e.g., "[00:01:23]", "0:01")
    3. Remove HTML entities and tags (if any leaked through)
    4. Remove auto-caption fillers ([Music], [Applause], [inaudible], etc.)
    5. Fix common transcript artifacts (missing spaces after periods)
    6. Collapse multiple newlines
    7. Collapse multiple spaces
    8. Strip leading/trailing whitespace per line
    9. Strip leading/trailing whitespace from full text
"""

import logging
import re
import unicodedata

logger = logging.getLogger(__name__)


class NodeCleaningError(Exception):
    """Raised when the cleaner cannot process the given text."""


def clean(raw_text: str) -> str:
    """
    Clean and normalize raw extracted text.

    Parameters
    ----------
    raw_text : str
        Raw text from the extractor node.

    Returns
    -------
    str
        Cleaned, normalized text ready for chunking.

    Raises
    ------
    NodeCleaningError
        If the input is empty, None, or results in empty output after cleaning.
    """
    if not raw_text or not raw_text.strip():
        raise NodeCleaningError("Input raw_text is empty or None")

    logger.info("Cleaning text of length %d", len(raw_text))

    text = raw_text

    # ── Step 1: Unicode normalization (NFC) ──────────────────────────────
    text = unicodedata.normalize("NFC", text)

    # ── Step 2: Remove YouTube timestamp patterns ────────────────────────
    # Matches [0:00], [00:01:23], [1:23:45], standalone or at line starts
    text = re.sub(r"\[\d{1,2}:\d{2}(?::\d{2})?\]\s*", "", text)
    # Also match bare timestamps like "0:01" at the start of lines
    text = re.sub(r"(?m)^\d{1,2}:\d{2}(?::\d{2})?\s+", "", text)

    # ── Step 3: Remove residual HTML entities and tags ───────────────────
    text = re.sub(r"<[^>]+>", "", text)                    # HTML tags
    text = re.sub(r"&(?:amp|lt|gt|quot|apos|nbsp);", " ", text)  # Common entities
    text = re.sub(r"&#\d+;", "", text)                     # Numeric entities
    text = re.sub(r"&[a-zA-Z]+;", "", text)                # Named entities

    # ── Step 4: Remove auto-caption fillers ──────────────────────────────
    filler_pattern = (
        r"\[(?:Music|Applause|Laughter|inaudible|crosstalk|silence|"
        r"foreign|Foreign|MUSIC|APPLAUSE|music|applause|laughter)\]"
    )
    text = re.sub(filler_pattern, "", text, flags=re.IGNORECASE)
    # Also handle parenthesized versions
    text = re.sub(
        r"\((?:music|applause|laughter|inaudible|crosstalk|silence)\)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # ── Step 5: Fix common transcript artifacts ──────────────────────────
    # Missing space after period when next word starts with uppercase
    text = re.sub(r"\.([A-Z])", r". \1", text)
    # Missing space after common punctuation
    text = re.sub(r"([,;:!?])([A-Za-z])", r"\1 \2", text)

    # ── Step 6: Collapse multiple newlines ───────────────────────────────
    text = re.sub(r"\n{3,}", "\n\n", text)

    # ── Step 7: Collapse multiple spaces ─────────────────────────────────
    text = re.sub(r" {2,}", " ", text)
    # Also collapse tabs
    text = re.sub(r"\t+", " ", text)

    # ── Step 8: Strip leading/trailing whitespace per line ───────────────
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    text = "\n".join(lines)

    # ── Step 9: Strip leading/trailing whitespace from full text ─────────
    text = text.strip()

    # ── Validation ───────────────────────────────────────────────────────
    if not text:
        raise NodeCleaningError(
            "Cleaning produced empty text from input of length "
            f"{len(raw_text)}"
        )

    reduction = (1 - len(text) / len(raw_text)) * 100
    logger.info(
        "Cleaned: %d → %d characters (%.1f%% reduction)",
        len(raw_text), len(text), reduction,
    )

    return text