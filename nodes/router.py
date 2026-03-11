"""
Node 6: Router
==============
Responsibility: Classify each fact into a memory tier and assign metadata
before writing to Supabase. This determines WHERE in the memory architecture
each fact lives.

Input/Output Contract
---------------------
Input:
    state.facts           : list[AtomicFact]    — Facts from Node 4
    state.dedup_decisions : list[DedupDecision] — Dedup outcomes from Node 5

Output:
    state.routed_facts    : list[RoutedFact]    — Facts with tier + metadata assigned

Error Behavior:
    NON-CRITICAL NODE (6 of 8) — logs errors and continues.
    Facts that cannot be routed default to 'episodic' tier.

Memory Tiers:
    episodic   — Raw events, experiences, specific instances
                 ("On March 10, 2026, GitHub released agentic workflows")
    semantic   — Distilled, generalized knowledge
                 ("GitHub Actions supports cron-scheduled workflows")
    procedural — How-to sequences, step-by-step instructions
                 ("To assign an issue to Copilot: Settings → Copilot → Enable → assign issue")

Routing Logic:
    - Procedural: detect step-by-step language ("step 1", "first do", "then", numbered lists)
    - Semantic: detect generalizations, definitions, relationships
    - Episodic: default for specific events, dated content, personal observations

Libraries Used:
    - re   (pattern matching for procedural detection)
    - LLM optional: gpt-4o-mini for ambiguous cases
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MEMORY_TIERS = ("episodic", "semantic", "procedural")


@dataclass
class RoutedFact:
    fact_text: str
    memory_tier: str
    source_type: str
    source_ref: str
    content_hash: str
    metadata: dict = field(default_factory=dict)


def route(facts: list, dedup_decisions: list) -> list[RoutedFact]:
    """
    Assign memory tier and metadata to each fact that passed dedup.

    Parameters
    ----------
    facts : list[AtomicFact]
        All atomic facts from Node 4.
    dedup_decisions : list[DedupDecision]
        Dedup outcomes from Node 5. Facts with action=SKIP are excluded.

    Returns
    -------
    list[RoutedFact]
        Facts with memory_tier assigned, ready for writing to Supabase.
        Only includes facts where dedup_decision.action != SKIP.

    Notes
    -----
    Default tier is 'episodic'. Explicit procedural patterns take priority,
    then semantic patterns, then episodic as fallback.
    """
    if not facts:
        return []

    logger.info("Routing %d facts (after dedup filter)", len(facts))

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 6 (router) not yet implemented — Phase 1")
