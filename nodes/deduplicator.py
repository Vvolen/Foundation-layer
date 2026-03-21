"""
Node 5: Deduplicator
====================
Responsibility: For each candidate atomic fact, check whether a semantically
equivalent fact already exists in Supabase. Route facts to one of three
outcomes: SKIP (duplicate), REVIEW (LLM gray zone), or INSERT (new fact).

Input/Output Contract
---------------------
Input:
    state.facts          : list[AtomicFact]    — Facts from Node 4

Output:
    state.dedup_decisions : list[DedupDecision] — One decision per fact

Error Behavior:
    NON-CRITICAL NODE (5 of 8) — logs errors and continues.
    If a fact cannot be deduplicated (API error), default to INSERT
    to avoid data loss.

Libraries Used:
    - openai   (text-embedding-3-small for embedding each fact)
    - supabase (vector similarity search via search_memory RPC)

Deduplication Thresholds (FIXED — do not change without explicit instruction):
    similarity >= 0.92  →  SKIP    (clear duplicate)
    0.75 <= sim < 0.92  →  REVIEW  (LLM gray zone — call gpt-4o to decide)
    similarity < 0.75   →  INSERT  (new knowledge)

Gray Zone LLM Logic:
    When similarity is in the 0.75–0.92 range, call gpt-4o with both facts
    and ask: "Are these two statements saying the same thing?"
    - If yes → SKIP (treat as duplicate)
    - If no  → INSERT (different enough to keep both)

Embedding Model:
    text-embedding-3-small (1536 dimensions) — matches the schema
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

DEDUP_THRESHOLD_DUPLICATE = 0.92
DEDUP_THRESHOLD_GRAY_ZONE = 0.75
EMBEDDING_MODEL = "text-embedding-3-small"
GRAY_ZONE_MODEL = "gpt-4o"
EMBED_BATCH_SIZE = 100


class DedupAction(str, Enum):
    INSERT = "INSERT"
    SKIP = "SKIP"
    REVIEW = "REVIEW"


@dataclass
class DedupDecision:
    fact_text: str
    action: DedupAction
    similarity_score: float | None = None
    matched_fragment_id: str | None = None
    review_reason: str | None = None
    metadata: dict = field(default_factory=dict)


def _init_openai_client(openai_client=None):
    """Initialize or return an existing OpenAI client."""
    if openai_client is not None:
        return openai_client
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError("openai not installed") from e
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


def _init_supabase_client(supabase_client=None):
    """Initialize or return an existing Supabase client."""
    if supabase_client is not None:
        return supabase_client
    try:
        from supabase import create_client
    except ImportError as e:
        raise RuntimeError("supabase not installed") from e
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(url, key)


def _embed_batch(client, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using OpenAI's embedding API."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    # Sort by index to ensure order matches input
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]


def _search_memory(supabase_client, embedding: list[float], match_count: int = 5) -> list[dict]:
    """
    Search existing memory_fragments for similar content.

    Returns a list of dicts with 'id', 'content', 'similarity'.
    """
    try:
        result = supabase_client.rpc(
            "search_memory",
            {
                "query_embedding": embedding,
                "match_count": match_count,
                "match_threshold": DEDUP_THRESHOLD_GRAY_ZONE,
            },
        ).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.warning("search_memory RPC failed: %s", e)
        return []


def _llm_gray_zone_review(
    openai_client,
    new_fact: str,
    existing_fact: str,
) -> bool:
    """
    Ask GPT-4o whether two facts are saying the same thing.

    Returns True if they're duplicates, False if they're different.
    """
    try:
        response = openai_client.chat.completions.create(
            model=GRAY_ZONE_MODEL,
            temperature=0.0,
            max_tokens=10,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You compare two statements and determine if they "
                        "convey the same information. Reply with exactly "
                        "YES or NO. Nothing else."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Statement A: {new_fact}\n\n"
                        f"Statement B: {existing_fact}\n\n"
                        "Are these two statements saying the same thing?"
                    ),
                },
            ],
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer.startswith("YES")
    except Exception as e:
        logger.warning("Gray zone LLM review failed: %s — defaulting to INSERT", e)
        return False  # Default to INSERT on error (avoid data loss)


def deduplicate(
    facts: list,
    supabase_client=None,
    openai_client=None,
) -> list[DedupDecision]:
    """
    Check each fact against existing memory and assign a dedup action.

    Parameters
    ----------
    facts : list[AtomicFact]
        Atomic facts from Node 4.
    supabase_client : supabase.Client, optional
        Initialized Supabase client. If None, will be initialized from env vars.
    openai_client : openai.OpenAI, optional
        Initialized OpenAI client. If None, will be initialized from env vars.

    Returns
    -------
    list[DedupDecision]
        One DedupDecision per input fact, in the same order.
        Decisions: INSERT (new fact), SKIP (duplicate), REVIEW (gray zone).

    Notes
    -----
    On any per-fact error, the fact defaults to INSERT to avoid data loss.
    Errors are logged and accumulated but do not halt processing.
    """
    if not facts:
        return []

    logger.info("Deduplicating %d facts", len(facts))

    try:
        oai_client = _init_openai_client(openai_client)
    except Exception as e:
        logger.error("Failed to init OpenAI client: %s — all facts default to INSERT", e)
        return [
            DedupDecision(
                fact_text=f.text if hasattr(f, "text") else str(f),
                action=DedupAction.INSERT,
                review_reason=f"OpenAI init failed: {e}",
            )
            for f in facts
        ]

    try:
        sb_client = _init_supabase_client(supabase_client)
    except Exception as e:
        logger.error("Failed to init Supabase client: %s — all facts default to INSERT", e)
        return [
            DedupDecision(
                fact_text=f.text if hasattr(f, "text") else str(f),
                action=DedupAction.INSERT,
                review_reason=f"Supabase init failed: {e}",
            )
            for f in facts
        ]

    # Step 1: Embed all facts in batches
    fact_texts = [f.text if hasattr(f, "text") else str(f) for f in facts]
    all_embeddings: list[list[float]] = []

    for batch_start in range(0, len(fact_texts), EMBED_BATCH_SIZE):
        batch = fact_texts[batch_start:batch_start + EMBED_BATCH_SIZE]
        try:
            embeddings = _embed_batch(oai_client, batch)
            all_embeddings.extend(embeddings)
        except Exception as e:
            logger.error(
                "Embedding batch %d failed: %s — defaulting those facts to INSERT",
                batch_start // EMBED_BATCH_SIZE, e,
            )
            all_embeddings.extend([None] * len(batch))

    # Step 2: Check each fact against existing memory
    decisions: list[DedupDecision] = []
    stats = {"insert": 0, "skip": 0, "review_insert": 0, "review_skip": 0, "error": 0}

    for i, (fact, embedding) in enumerate(zip(facts, all_embeddings)):
        fact_text = fact.text if hasattr(fact, "text") else str(fact)

        if embedding is None:
            decisions.append(DedupDecision(
                fact_text=fact_text,
                action=DedupAction.INSERT,
                review_reason="Embedding failed",
            ))
            stats["error"] += 1
            continue

        try:
            matches = _search_memory(sb_client, embedding, match_count=5)
        except Exception as e:
            logger.warning("Fact %d search failed: %s — defaulting to INSERT", i, e)
            decisions.append(DedupDecision(
                fact_text=fact_text,
                action=DedupAction.INSERT,
                review_reason=f"Search failed: {e}",
            ))
            stats["error"] += 1
            continue

        if not matches:
            # No matches above threshold — INSERT
            decisions.append(DedupDecision(
                fact_text=fact_text,
                action=DedupAction.INSERT,
                similarity_score=0.0,
            ))
            stats["insert"] += 1
            continue

        # Get the best match
        best = matches[0]
        similarity = best.get("similarity", 0.0)
        matched_id = str(best.get("id", ""))
        matched_content = best.get("content", "")

        if similarity >= DEDUP_THRESHOLD_DUPLICATE:
            # Clear duplicate — SKIP
            decisions.append(DedupDecision(
                fact_text=fact_text,
                action=DedupAction.SKIP,
                similarity_score=similarity,
                matched_fragment_id=matched_id,
            ))
            stats["skip"] += 1

        elif similarity >= DEDUP_THRESHOLD_GRAY_ZONE:
            # Gray zone — ask LLM
            is_dup = _llm_gray_zone_review(oai_client, fact_text, matched_content)
            if is_dup:
                decisions.append(DedupDecision(
                    fact_text=fact_text,
                    action=DedupAction.SKIP,
                    similarity_score=similarity,
                    matched_fragment_id=matched_id,
                    review_reason="LLM confirmed duplicate",
                ))
                stats["review_skip"] += 1
            else:
                decisions.append(DedupDecision(
                    fact_text=fact_text,
                    action=DedupAction.INSERT,
                    similarity_score=similarity,
                    matched_fragment_id=matched_id,
                    review_reason="LLM confirmed distinct",
                ))
                stats["review_insert"] += 1

        else:
            # Below gray zone — INSERT
            decisions.append(DedupDecision(
                fact_text=fact_text,
                action=DedupAction.INSERT,
                similarity_score=similarity,
            ))
            stats["insert"] += 1

    logger.info(
        "Dedup complete: %d insert, %d skip, %d gray→insert, %d gray→skip, %d errors",
        stats["insert"], stats["skip"], stats["review_insert"],
        stats["review_skip"], stats["error"],
    )

    return decisions