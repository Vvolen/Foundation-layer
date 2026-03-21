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

import nltk

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


# Token estimation: ~1.3 tokens per whitespace-delimited word
_TOKENS_PER_WORD = 1.3

# Minimum chunk size in estimated tokens — discard anything smaller
_MIN_CHUNK_TOKENS = 50


def _estimate_tokens(text: str) -> int:
    """Approximate token count from text using word count × 1.3."""
    return int(len(text.split()) * _TOKENS_PER_WORD)


def _tokenize_sentences(text: str) -> list[str]:
    """Split text into sentences using NLTK's punkt tokenizer."""
    try:
        sentences = nltk.tokenize.sent_tokenize(text)
    except LookupError:
        # Download punkt_tab if not available
        nltk.download("punkt_tab", quiet=True)
        sentences = nltk.tokenize.sent_tokenize(text)
    return sentences


def chunk(
    clean_text: str,
    target_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[Chunk]:
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

    logger.info(
        "Chunking text of length %d (target=%d tokens, overlap=%d tokens)",
        len(clean_text), target_tokens, overlap_tokens,
    )

    # Tokenize into sentences
    sentences = _tokenize_sentences(clean_text)

    if not sentences:
        raise NodeChunkingError("Sentence tokenization produced 0 sentences")

    logger.info("Tokenized into %d sentences", len(sentences))

    # Build sentence metadata: token count and character offsets
    sentence_meta = []
    search_start = 0
    for sent in sentences:
        tok_count = _estimate_tokens(sent)

        # Find the sentence's position in the original text
        char_start = clean_text.find(sent, search_start)
        if char_start == -1:
            # Fallback: use current search position
            char_start = search_start
        char_end = char_start + len(sent)
        search_start = char_end

        sentence_meta.append({
            "text": sent,
            "tokens": tok_count,
            "char_start": char_start,
            "char_end": char_end,
        })

    # Accumulate sentences into chunks using sliding window
    chunks: list[Chunk] = []
    chunk_index = 0
    i = 0  # Current sentence index

    while i < len(sentence_meta):
        # Accumulate sentences until we reach the target token count
        chunk_sentences = []
        chunk_token_count = 0
        start_i = i

        while i < len(sentence_meta) and chunk_token_count < target_tokens:
            chunk_sentences.append(sentence_meta[i])
            chunk_token_count += sentence_meta[i]["tokens"]
            i += 1

        if not chunk_sentences:
            break

        # Build the chunk text
        chunk_text = " ".join(s["text"] for s in chunk_sentences)
        char_start = chunk_sentences[0]["char_start"]
        char_end = chunk_sentences[-1]["char_end"]
        token_count = _estimate_tokens(chunk_text)

        # Only keep chunks that meet the minimum size
        if token_count >= _MIN_CHUNK_TOKENS:
            chunks.append(Chunk(
                text=chunk_text,
                index=chunk_index,
                token_count=token_count,
                char_start=char_start,
                char_end=char_end,
                metadata={
                    "sentence_count": len(chunk_sentences),
                },
            ))
            chunk_index += 1

        # Calculate overlap: back up by overlap_tokens worth of sentences
        if i < len(sentence_meta):
            overlap_accumulated = 0
            backtrack = 0
            for j in range(len(chunk_sentences) - 1, -1, -1):
                overlap_accumulated += chunk_sentences[j]["tokens"]
                backtrack += 1
                if overlap_accumulated >= overlap_tokens:
                    break

            # Move the pointer back for overlap
            i = max(start_i + 1, i - backtrack)

    if not chunks:
        # If no chunks met the minimum, create a single chunk from everything
        total_tokens = _estimate_tokens(clean_text)
        if total_tokens > 0:
            chunks.append(Chunk(
                text=clean_text,
                index=0,
                token_count=total_tokens,
                char_start=0,
                char_end=len(clean_text),
                metadata={"sentence_count": len(sentences)},
            ))
        else:
            raise NodeChunkingError(
                "Chunking produced no valid chunks from input of length "
                f"{len(clean_text)}"
            )

    logger.info(
        "Produced %d chunks (avg %d tokens each)",
        len(chunks),
        sum(c.token_count for c in chunks) // max(len(chunks), 1),
    )

    return chunks