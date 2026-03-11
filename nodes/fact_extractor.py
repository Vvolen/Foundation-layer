"""
Node 4: Fact Extractor
======================
Responsibility: Given a list of text chunks, extract atomic facts from each
chunk using an LLM. An atomic fact is a single, standalone, verifiable
statement that can be true or false on its own without needing surrounding
context.

Input/Output Contract
---------------------
Input:
    state.chunks : list[Chunk]         — Chunks from Node 3

Output:
    state.facts  : list[AtomicFact]    — All atomic facts extracted from all chunks

Error Behavior:
    CRITICAL NODE (4 of 4) — raises NodeFactExtractionError on failure.
    Per-chunk failures are logged and the chunk is skipped (not halting).

Libraries Used:
    - openai  (GPT-4o-mini for fact extraction)
    - json    (parse LLM JSON response)

LLM Configuration:
    - Model: gpt-4o-mini (fast, cheap, good enough for atomic fact extraction)
    - Temperature: 0.1 (near-deterministic for consistency)
    - Response format: JSON array of fact strings
    - Max retries: 3 with exponential backoff

Atomic Fact Definition:
    A good atomic fact:
    - Is a single sentence
    - Can stand alone without context
    - Is specific (contains names, numbers, dates where relevant)
    - Is verifiable (not an opinion)

    Examples:
        GOOD: "The human brain contains approximately 86 billion neurons."
        BAD:  "The brain is complex." (too vague)
        BAD:  "As mentioned earlier, this explains why..." (needs context)
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NodeFactExtractionError(Exception):
    """Raised when fact extraction fails critically."""


@dataclass
class AtomicFact:
    text: str
    chunk_index: int
    source_type: str
    source_ref: str
    extraction_model: str = "gpt-4o-mini"
    metadata: dict = field(default_factory=dict)


def extract_facts(chunks: list, source_type: str, source_ref: str) -> list[AtomicFact]:
    """
    Extract atomic facts from a list of text chunks using an LLM.

    Parameters
    ----------
    chunks : list[Chunk]
        Text chunks from Node 3.
    source_type : str
        The source type of the original content (for provenance).
    source_ref : str
        The source reference (URL or path) for provenance tracking.

    Returns
    -------
    list[AtomicFact]
        All atomic facts extracted from all chunks. May be fewer than chunks
        if some chunks yield no facts (noise/filler).

    Raises
    ------
    NodeFactExtractionError
        If the OpenAI client cannot be initialized or all chunks fail.
    """
    if not chunks:
        raise NodeFactExtractionError("Input chunks list is empty")

    logger.info("Extracting facts from %d chunks", len(chunks))

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 4 (fact_extractor) not yet implemented — Phase 1")


EXTRACTION_PROMPT = """
You are an atomic fact extractor. Given a text passage, extract all atomic facts.

An atomic fact is:
- A single, standalone sentence
- Verifiable and specific
- Does not require surrounding context to be understood

Respond with a JSON array of strings. Each string is one atomic fact.
Example: ["Fact one.", "Fact two.", "Fact three."]

If the passage contains no extractable facts (filler, noise, etc.), return an empty array: []

Text passage:
{chunk_text}
"""
