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
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

DEDUP_THRESHOLD_DUPLICATE = 0.92
DEDUP_THRESHOLD_GRAY_ZONE = 0.75


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


def deduplicate(facts: list, supabase_client=None, openai_client=None) -> list[DedupDecision]:
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

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 5 (deduplicator) not yet implemented — Phase 1")
