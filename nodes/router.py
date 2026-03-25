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
    - hashlib (SHA-256 content hash)
"""

import hashlib
import logging
import re
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


def _compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of normalized text for exact dedup."""
    normalized = text.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Pattern-based tier classification
# ---------------------------------------------------------------------------

# Procedural patterns — detect how-to, step-by-step, sequential instructions
_PROCEDURAL_PATTERNS = [
    # Numbered steps
    r"(?:^|\s)(?:step\s+\d|1[\.\)]\s)",
    # Sequential language
    r"\b(?:first|then|next|finally|afterwards|subsequently)\b.*\b(?:then|next|after|finally)\b",
    # Imperative how-to
    r"\b(?:how\s+to|to\s+do\s+this|in\s+order\s+to)\b",
    # Direct instructions
    r"\b(?:run|execute|install|configure|set\s+up|create|open|click|navigate|type|enter|select)\b.*\b(?:then|next|and\s+then|after)\b",
    # Command-like patterns
    r"\b(?:run|execute|use|call|invoke)\s*[:`]",
    # "First... then..." pattern
    r"\bfirst\b.{5,80}\bthen\b",
]

# Semantic patterns — detect definitions, generalizations, relationships
_SEMANTIC_PATTERNS = [
    # Definitions
    r"\b(?:is\s+defined\s+as|refers\s+to|means\s+that|is\s+known\s+as)\b",
    # Generalizations
    r"\b(?:in\s+general|typically|usually|always|never|all|every|most|any)\b",
    # Relationships & categories
    r"\b(?:is\s+a\s+type\s+of|belongs\s+to|is\s+part\s+of|consists\s+of|is\s+composed\s+of)\b",
    # Properties & characteristics
    r"\b(?:has\s+the\s+property|is\s+characterized\s+by|features?\s+include)\b",
    # Scientific/factual statements
    r"\b(?:contains\s+approximately|is\s+approximately|measures\s+about|has\s+a\s+capacity\s+of)\b",
    # Principle/rule statements
    r"\b(?:the\s+principle\s+of|according\s+to\s+the|the\s+law\s+of|the\s+theory\s+of)\b",
    # "X is Y" definitional form
    r"^[A-Z][^.]{3,40}\bis\b[^.]{3,60}\.$",
    # Comparative/categorical
    r"\b(?:compared\s+to|in\s+contrast|whereas|while|unlike)\b",
]

# Episodic signals — specific events, dates, personal references
_EPISODIC_PATTERNS = [
    # Specific dates
    r"\b(?:on\s+)?(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?\b",
    # Year references with events
    r"\bin\s+(?:19|20)\d{2}\b",
    # Personal pronouns indicating experience
    r"\b(?:I\s+(?:was|did|went|saw|heard|learned|discovered|found|built|created))\b",
    # Event language
    r"\b(?:announced|released|launched|published|happened|occurred|took\s+place)\b",
]


def _classify_tier(fact_text: str) -> str:
    """
    Classify a fact into a memory tier using pattern matching.

    Priority: procedural > semantic > episodic (default)
    """
    text = fact_text.strip()

    # Check procedural first (highest priority for instructions)
    procedural_score = 0
    for pattern in _PROCEDURAL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            procedural_score += 1

    # Check semantic
    semantic_score = 0
    for pattern in _SEMANTIC_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            semantic_score += 1

    # Check episodic signals
    episodic_score = 0
    for pattern in _EPISODIC_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            episodic_score += 1

    # Decision: need at least 1 match, and highest score wins
    # Procedural takes priority on ties with semantic
    if procedural_score > 0 and procedural_score >= semantic_score:
        return "procedural"

    if semantic_score > 0 and semantic_score > episodic_score:
        return "semantic"

    # Default is episodic (specific events, or no clear pattern)
    return "episodic"


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

    logger.info("Routing %d facts (with %d dedup decisions)", len(facts), len(dedup_decisions))

    # Import DedupAction here to avoid circular imports at module level
    from nodes.deduplicator import DedupAction

    routed: list[RoutedFact] = []
    tier_counts = {"episodic": 0, "semantic": 0, "procedural": 0}
    skipped = 0

    for i, fact in enumerate(facts):
        # Check dedup decision — skip duplicates
        if i < len(dedup_decisions):
            decision = dedup_decisions[i]
            if hasattr(decision, "action"):
                action = decision.action
            elif isinstance(decision, dict):
                action = decision.get("action", DedupAction.INSERT)
            else:
                action = DedupAction.INSERT

            if action == DedupAction.SKIP:
                skipped += 1
                continue

        # Get fact text
        if hasattr(fact, "text"):
            fact_text = fact.text
            source_type = fact.source_type
            source_ref = fact.source_ref
        elif isinstance(fact, dict):
            fact_text = fact.get("text", str(fact))
            source_type = fact.get("source_type", "unknown")
            source_ref = fact.get("source_ref", "unknown")
        else:
            fact_text = str(fact)
            source_type = "unknown"
            source_ref = "unknown"

        # Classify into memory tier
        try:
            tier = _classify_tier(fact_text)
        except Exception as e:
            logger.warning("Fact %d classification failed: %s — defaulting to episodic", i, e)
            tier = "episodic"

        # Compute content hash
        content_hash = _compute_content_hash(fact_text)

        routed.append(RoutedFact(
            fact_text=fact_text,
            memory_tier=tier,
            source_type=source_type,
            source_ref=source_ref,
            content_hash=content_hash,
            metadata={
                "chunk_index": getattr(fact, "chunk_index", None),
                "extraction_model": getattr(fact, "extraction_model", None),
            },
        ))
        tier_counts[tier] += 1

    logger.info(
        "Routing complete: %d routed (episodic=%d, semantic=%d, procedural=%d), %d skipped",
        len(routed),
        tier_counts["episodic"],
        tier_counts["semantic"],
        tier_counts["procedural"],
        skipped,
    )

    return routed