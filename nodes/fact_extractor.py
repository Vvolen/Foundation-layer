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

import json
import logging
import os
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# LLM configuration
EXTRACTION_MODEL = "gpt-4o-mini"
EXTRACTION_TEMPERATURE = 0.1
MAX_RETRIES = 3


class NodeFactExtractionError(Exception):
    """Raised when fact extraction fails critically."""


@dataclass
class AtomicFact:
    text: str
    chunk_index: int
    source_type: str
    source_ref: str
    extraction_model: str = EXTRACTION_MODEL
    metadata: dict = field(default_factory=dict)


EXTRACTION_PROMPT = """You are an atomic fact extractor. Given a text passage, extract all atomic facts.

An atomic fact is:
- A single, standalone sentence
- Verifiable and specific
- Does not require surrounding context to be understood
- Contains specific names, numbers, dates, or details where relevant

Do NOT include:
- Vague or generic statements ("This is interesting")
- Context-dependent references ("As mentioned earlier", "This explains why")
- Opinions or subjective assessments
- Filler content or pleasantries

Respond with a JSON array of strings. Each string is one atomic fact.
Example: ["Fact one.", "Fact two.", "Fact three."]

If the passage contains no extractable facts (filler, noise, etc.), return an empty array: []

Text passage:
{chunk_text}"""


def _init_openai_client(openai_client=None):
    """Initialize or return an existing OpenAI client."""
    if openai_client is not None:
        return openai_client

    try:
        from openai import OpenAI
    except ImportError as e:
        raise NodeFactExtractionError(
            "openai package not installed. Run: pip install openai"
        ) from e

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise NodeFactExtractionError(
            "OPENAI_API_KEY environment variable is not set"
        )

    return OpenAI(api_key=api_key)


def _extract_facts_from_chunk(
    client,
    chunk_text: str,
    chunk_index: int,
) -> list[str]:
    """
    Call the LLM to extract atomic facts from a single chunk.

    Returns a list of fact strings. Retries with exponential backoff
    on rate limits and transient errors.
    """
    prompt = EXTRACTION_PROMPT.format(chunk_text=chunk_text)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=EXTRACTION_MODEL,
                temperature=EXTRACTION_TEMPERATURE,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise fact extraction engine. "
                            "Always respond with a valid JSON array of strings."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                # Request JSON output
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content.strip()

            # Parse the JSON response
            parsed = json.loads(content)

            # Handle both {"facts": [...]} and direct [...] formats
            if isinstance(parsed, list):
                facts = parsed
            elif isinstance(parsed, dict):
                # Try common keys
                for key in ("facts", "atomic_facts", "results", "data"):
                    if key in parsed and isinstance(parsed[key], list):
                        facts = parsed[key]
                        break
                else:
                    # Use all string values from the dict
                    facts = [v for v in parsed.values() if isinstance(v, (str, list))]
                    if facts and isinstance(facts[0], list):
                        facts = facts[0]
            else:
                logger.warning(
                    "Chunk %d: unexpected response type %s, skipping",
                    chunk_index, type(parsed).__name__,
                )
                return []

            # Filter: only keep non-empty strings
            facts = [f.strip() for f in facts if isinstance(f, str) and f.strip()]

            return facts

        except json.JSONDecodeError as e:
            logger.warning(
                "Chunk %d attempt %d: JSON parse error: %s",
                chunk_index, attempt + 1, e,
            )
            # Try to extract JSON array from the response with regex
            if attempt == MAX_RETRIES - 1:
                import re
                content_str = content if 'content' in dir() else ""
                match = re.search(r'\[.*\]', content_str, re.DOTALL)
                if match:
                    try:
                        facts = json.loads(match.group())
                        return [f.strip() for f in facts if isinstance(f, str) and f.strip()]
                    except json.JSONDecodeError:
                        pass
                logger.error(
                    "Chunk %d: all %d parse attempts failed",
                    chunk_index, MAX_RETRIES,
                )
                return []

        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = "rate" in error_str or "429" in error_str
            is_transient = "500" in error_str or "502" in error_str or "503" in error_str

            if (is_rate_limit or is_transient) and attempt < MAX_RETRIES - 1:
                wait_time = 2 ** (attempt + 1)
                logger.warning(
                    "Chunk %d attempt %d: %s — retrying in %ds",
                    chunk_index, attempt + 1, e, wait_time,
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    "Chunk %d attempt %d: unrecoverable error: %s",
                    chunk_index, attempt + 1, e,
                )
                return []

    return []


def extract_facts(
    chunks: list,
    source_type: str,
    source_ref: str,
    openai_client=None,
) -> list[AtomicFact]:
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
    openai_client : openai.OpenAI, optional
        Pre-initialized OpenAI client. If None, initializes from env.

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

    client = _init_openai_client(openai_client)

    all_facts: list[AtomicFact] = []
    chunks_succeeded = 0
    chunks_failed = 0

    for chunk_obj in chunks:
        # Support both Chunk dataclass and dict
        if hasattr(chunk_obj, "text"):
            chunk_text = chunk_obj.text
            chunk_index = chunk_obj.index
        elif isinstance(chunk_obj, dict):
            chunk_text = chunk_obj.get("text", "")
            chunk_index = chunk_obj.get("index", 0)
        else:
            logger.warning("Skipping unrecognized chunk type: %s", type(chunk_obj))
            chunks_failed += 1
            continue

        if not chunk_text.strip():
            logger.debug("Skipping empty chunk %d", chunk_index)
            continue

        fact_strings = _extract_facts_from_chunk(client, chunk_text, chunk_index)

        if fact_strings:
            for fact_text in fact_strings:
                all_facts.append(AtomicFact(
                    text=fact_text,
                    chunk_index=chunk_index,
                    source_type=source_type,
                    source_ref=source_ref,
                    extraction_model=EXTRACTION_MODEL,
                    metadata={},
                ))
            chunks_succeeded += 1
            logger.debug(
                "Chunk %d: extracted %d facts", chunk_index, len(fact_strings)
            )
        else:
            chunks_failed += 1
            logger.debug("Chunk %d: no facts extracted", chunk_index)

    logger.info(
        "Fact extraction complete: %d facts from %d chunks "
        "(%d succeeded, %d failed/empty)",
        len(all_facts), len(chunks), chunks_succeeded, chunks_failed,
    )

    if not all_facts and chunks_succeeded == 0:
        raise NodeFactExtractionError(
            f"All {len(chunks)} chunks failed to produce any facts. "
            "Check OPENAI_API_KEY and network connectivity."
        )

    return all_facts