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
import os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 100
WRITE_BATCH_SIZE = 50
EMBEDDING_MODEL = "text-embedding-3-small"


@dataclass
class WriteResults:
    written: int = 0
    failed: int = 0
    fragment_ids: list = field(default_factory=list)
    errors: list = field(default_factory=list)


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
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]


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

    results = WriteResults()

    try:
        oai_client = _init_openai_client(openai_client)
    except Exception as e:
        logger.error("Failed to init OpenAI client: %s", e)
        results.failed = len(routed_facts)
        results.errors.append(f"OpenAI init failed: {e}")
        return results

    try:
        sb_client = _init_supabase_client(supabase_client)
    except Exception as e:
        logger.error("Failed to init Supabase client: %s", e)
        results.failed = len(routed_facts)
        results.errors.append(f"Supabase init failed: {e}")
        return results

    # Step 1: Extract fact texts for embedding
    fact_texts = []
    for rf in routed_facts:
        if hasattr(rf, "fact_text"):
            fact_texts.append(rf.fact_text)
        elif isinstance(rf, dict):
            fact_texts.append(rf.get("fact_text", str(rf)))
        else:
            fact_texts.append(str(rf))

    # Step 2: Embed all facts in batches
    logger.info("Generating embeddings for %d facts", len(fact_texts))
    all_embeddings: list[list[float] | None] = []

    for batch_start in range(0, len(fact_texts), EMBED_BATCH_SIZE):
        batch = fact_texts[batch_start:batch_start + EMBED_BATCH_SIZE]
        try:
            embeddings = _embed_batch(oai_client, batch)
            all_embeddings.extend(embeddings)
            logger.debug(
                "Embedded batch %d–%d",
                batch_start, batch_start + len(batch),
            )
        except Exception as e:
            logger.error("Embedding batch %d failed: %s", batch_start, e)
            all_embeddings.extend([None] * len(batch))

    # Step 3: Build fragment records
    fragment_records = []
    provenance_records = []

    for i, (rf, embedding) in enumerate(zip(routed_facts, all_embeddings)):
        if embedding is None:
            results.failed += 1
            results.errors.append(f"Fact {i}: embedding failed")
            continue

        # Extract fields from RoutedFact
        if hasattr(rf, "fact_text"):
            fact_text = rf.fact_text
            memory_tier = rf.memory_tier
            source_type = rf.source_type
            source_ref = rf.source_ref
            content_hash = rf.content_hash
            metadata = rf.metadata if hasattr(rf, "metadata") else {}
        elif isinstance(rf, dict):
            fact_text = rf.get("fact_text", "")
            memory_tier = rf.get("memory_tier", "episodic")
            source_type = rf.get("source_type", "unknown")
            source_ref = rf.get("source_ref", "unknown")
            content_hash = rf.get("content_hash", "")
            metadata = rf.get("metadata", {})
        else:
            results.failed += 1
            results.errors.append(f"Fact {i}: unrecognized type {type(rf)}")
            continue

        fragment = {
            "content": fact_text,
            "source_type": source_type,
            "source_ref": source_ref,
            "memory_tier": memory_tier,
            "embedding": embedding,
            "content_hash": content_hash,
            "pipeline_run_id": pipeline_run_id,
            "metadata": metadata or {},
        }
        fragment_records.append(fragment)

        # Build provenance record (will be inserted after fragments)
        provenance = {
            "source_type": source_type,
            "source_ref": source_ref,
            "chunk_index": metadata.get("chunk_index") if metadata else None,
            "pipeline_run_id": pipeline_run_id,
            "extraction_model": metadata.get("extraction_model") if metadata else None,
            "content_hash": content_hash,  # Temp key for linking
        }
        provenance_records.append(provenance)

    # Step 4: Upsert fragments in batches of WRITE_BATCH_SIZE
    logger.info("Upserting %d fragments to Supabase", len(fragment_records))

    written_hashes = {}  # content_hash -> fragment_id mapping

    for batch_start in range(0, len(fragment_records), WRITE_BATCH_SIZE):
        batch = fragment_records[batch_start:batch_start + WRITE_BATCH_SIZE]

        try:
            response = (
                sb_client.table("memory_fragments")
                .upsert(batch, on_conflict="content_hash")
                .execute()
            )

            if response.data:
                for row in response.data:
                    frag_id = row.get("id", "")
                    c_hash = row.get("content_hash", "")
                    results.fragment_ids.append(frag_id)
                    results.written += 1
                    if c_hash:
                        written_hashes[c_hash] = frag_id

                logger.debug(
                    "Batch %d–%d: %d rows upserted",
                    batch_start, batch_start + len(batch),
                    len(response.data),
                )
            else:
                # Upsert returned no data but didn't error — count as written
                results.written += len(batch)
                logger.debug(
                    "Batch %d–%d: %d rows upserted (no data returned)",
                    batch_start, batch_start + len(batch), len(batch),
                )

        except Exception as e:
            logger.error(
                "Batch %d–%d upsert failed: %s",
                batch_start, batch_start + len(batch), e,
            )
            results.failed += len(batch)
            results.errors.append(
                f"Batch {batch_start}–{batch_start + len(batch)}: {e}"
            )

    # Step 5: Insert provenance records for successfully written fragments
    if written_hashes:
        prov_to_insert = []
        for prov in provenance_records:
            c_hash = prov.pop("content_hash", None)
            if c_hash and c_hash in written_hashes:
                prov["fragment_id"] = written_hashes[c_hash]
                prov_to_insert.append(prov)

        if prov_to_insert:
            try:
                for batch_start in range(0, len(prov_to_insert), WRITE_BATCH_SIZE):
                    batch = prov_to_insert[batch_start:batch_start + WRITE_BATCH_SIZE]
                    sb_client.table("memory_provenance").insert(batch).execute()

                logger.info("Inserted %d provenance records", len(prov_to_insert))
            except Exception as e:
                logger.warning("Provenance insert failed: %s (non-critical)", e)
                results.errors.append(f"Provenance insert failed: {e}")

    logger.info(
        "Supabase write complete: %d written, %d failed, %d fragment IDs returned",
        results.written, results.failed, len(results.fragment_ids),
    )

    return results