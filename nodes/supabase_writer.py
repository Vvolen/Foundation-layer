"""
Node 7: Supabase Writer
=======================
Responsibility: Write routed facts to Supabase as memory_fragments,
with their embeddings, provenance records, and metadata.

Input/Output Contract
---------------------
Input:
    state.routed_facts : list[RoutedFact]  — Facts from Node 6

Output:
    state.write_results : dict             — Summary of write operations
        {
            "written": int,          # Number of fragments successfully written
            "failed": int,           # Number of fragments that failed
            "fragment_ids": list,    # UUIDs of written fragments
            "errors": list           # Per-item error details
        }

Error Behavior:
    NON-CRITICAL NODE (7 of 8) — logs errors and continues.
    Failed writes are logged and included in write_results["errors"].

Libraries Used:
    - supabase  (Python client for Supabase)
    - openai    (text-embedding-3-small for generating embeddings)
    - hashlib   (SHA-256 content hash for exact dedup)

Batch Strategy:
    - Embed facts in batches of 100 (OpenAI embeddings API limit per request)
    - Upsert to Supabase in batches of 50 (avoids timeout)
    - On_conflict: content_hash (so re-running the pipeline is idempotent)

Important:
    - Always compute content_hash before writing (SHA-256 of normalized text)
    - Always generate provenance record alongside the fragment
    - Use pipeline_run_id for traceability
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 100
WRITE_BATCH_SIZE = 50


@dataclass
class WriteResults:
    written: int = 0
    failed: int = 0
    fragment_ids: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def write_to_supabase(
    routed_facts: list,
    pipeline_run_id: str,
    supabase_client=None,
    openai_client=None,
) -> WriteResults:
    """
    Write routed facts to Supabase memory_fragments table.

    Parameters
    ----------
    routed_facts : list[RoutedFact]
        Facts from Node 6 with memory tier and metadata assigned.
    pipeline_run_id : str
        The UUID of this pipeline run for traceability.
    supabase_client : supabase.Client, optional
        Initialized Supabase client. If None, initializes from env vars.
    openai_client : openai.OpenAI, optional
        Initialized OpenAI client. If None, initializes from env vars.

    Returns
    -------
    WriteResults
        Summary of how many fragments were written vs. failed.

    Notes
    -----
    Uses upsert on content_hash, so the pipeline is idempotent —
    re-running on the same source will not create duplicate rows.
    """
    if not routed_facts:
        logger.info("No routed facts to write")
        return WriteResults()

    logger.info("Writing %d facts to Supabase", len(routed_facts))

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 7 (supabase_writer) not yet implemented — Phase 1")
