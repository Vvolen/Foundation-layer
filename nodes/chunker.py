"""
Node 3: Chunker
===============
Responsibility: Splits clean text into semantically coherent chunks suitable
for embedding and fact extraction. Uses a sliding window with overlap to
prevent facts from being cut across chunk boundaries.

Input/Output Contract
---------------------
Input:
    state.clean_text : str       — Cleaned text from Node 2

Output:
    state.chunks     : list[Chunk] — List of text chunks with metadata

Error Behavior:
    CRITICAL NODE (3 of 4) — raises NodeChunkingError on failure.

Libraries Used:
    - nltk  (sentence tokenization)

Chunking Strategy:
    - Target chunk size: 512 tokens (~400 words)
    - Overlap: 50 tokens (~40 words) between adjacent chunks
    - Boundaries: always split on sentence boundaries, never mid-sentence
    - Minimum chunk size: 50 tokens (discard shorter chunks as noise)

Chunk Metadata:
    Each Chunk includes:
        - text         : str   — The chunk text
        - index        : int   — Position in the document (0-based)
        - token_count  : int   — Approximate token count
        - char_start   : int   — Start character offset in clean_text
        - char_end     : int   — End character offset in clean_text
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NodeChunkingError(Exception):
    """Raised when the chunker cannot process the given text."""


@dataclass
class Chunk:
    text: str
    index: int
    token_count: int
    char_start: int
    char_end: int
    metadata: dict = field(default_factory=dict)


def chunk(clean_text: str, target_tokens: int = 512, overlap_tokens: int = 50) -> list[Chunk]:
    """
    Split clean text into overlapping semantic chunks.

    Parameters
    ----------
    clean_text : str
        Cleaned text from Node 2.
    target_tokens : int, optional
        Target size for each chunk in tokens (default 512).
    overlap_tokens : int, optional
        Number of tokens to overlap between adjacent chunks (default 50).

    Returns
    -------
    list[Chunk]
        List of Chunk dataclasses, each with text and positional metadata.

    Raises
    ------
    NodeChunkingError
        If the input is empty or chunking produces no valid chunks.
    """
    if not clean_text or not clean_text.strip():
        raise NodeChunkingError("Input clean_text is empty or None")

    logger.info("Chunking text of length %d (target=%d tokens)", len(clean_text), target_tokens)

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 3 (chunker) not yet implemented — Phase 1")
