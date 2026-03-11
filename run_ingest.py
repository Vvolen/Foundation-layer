"""
run_ingest.py — NickOS Foundation-layer Pipeline Orchestrator
=============================================================
The main entry point for the ingestion pipeline. Orchestrates all 8 nodes
in sequence, manages the PipelineState dataclass, handles checkpointing,
and produces a final run report.

Usage:
    python run_ingest.py --source youtube --url "https://youtube.com/watch?v=..."
    python run_ingest.py --source pdf --path "/path/to/file.pdf"
    python run_ingest.py --source url --url "https://example.com/article"
    python run_ingest.py --source text --text "Raw text to ingest..."
    python run_ingest.py --resume <checkpoint_path>

Error Handling Strategy:
    Nodes 1–4 (critical path):  halt pipeline on error
    Nodes 5–8 (non-critical):   log error, continue, accumulate in state.errors

Checkpoint Pattern:
    After each node completes, state is saved to pipeline_artifacts/checkpoint_<run_id>.json
    Re-run with --resume <path> to pick up from where a failed run left off.

Environment Variables (loaded from .env):
    SUPABASE_URL          — Supabase project URL
    SUPABASE_SERVICE_KEY  — Supabase service role key (full access)
    OPENAI_API_KEY        — OpenAI API key
    NOTION_API_KEY        — Notion integration token
    NOTION_DATABASE_ID    — Notion database to write ingestion summaries to
"""

import argparse
import json
import logging
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_ingest")

ARTIFACTS_DIR = Path("pipeline_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)


# =============================================================================
# PIPELINE STATE
# =============================================================================


@dataclass
class PipelineState:
    """
    Shared state object passed through all 8 pipeline nodes.

    Never mutate this outside of the designated node function.
    Use asdict(state) to serialize to JSON for checkpointing.
    """

    run_id: str
    source_type: str
    source_ref: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Node outputs (populated sequentially)
    raw_text: str | None = None           # Node 1: extractor
    clean_text: str | None = None         # Node 2: cleaner
    chunks: list | None = None            # Node 3: chunker
    facts: list | None = None             # Node 4: fact_extractor
    dedup_decisions: list | None = None   # Node 5: deduplicator
    routed_facts: list | None = None      # Node 6: router
    write_results: dict | None = None     # Node 7: supabase_writer
    notion_result: dict | None = None     # Node 8a: notion_writer
    report: dict | None = None            # Node 8b: reporter

    # Error accumulation (nodes 5–8 append here instead of halting)
    errors: list = field(default_factory=list)

    # Checkpoint tracking
    last_completed_node: int = 0
    checkpoint_path: str = ""

    completed_at: str | None = None


# =============================================================================
# CHECKPOINT HELPERS
# =============================================================================


def save_checkpoint(state: PipelineState) -> None:
    """Save pipeline state to a JSON file in pipeline_artifacts/."""
    if not state.checkpoint_path:
        state.checkpoint_path = str(ARTIFACTS_DIR / f"checkpoint_{state.run_id}.json")

    data = asdict(state)
    with open(state.checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    logger.debug("Checkpoint saved: %s (node %d)", state.checkpoint_path, state.last_completed_node)


def load_checkpoint(path: str) -> PipelineState:
    """Load a PipelineState from a checkpoint JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    state = PipelineState(**{k: v for k, v in data.items() if k in PipelineState.__dataclass_fields__})
    logger.info("Resumed from checkpoint: %s (node %d)", path, state.last_completed_node)
    return state


# =============================================================================
# PIPELINE EXECUTION
# =============================================================================


def run_pipeline(state: PipelineState) -> PipelineState:
    """
    Execute the full 8-node ingestion pipeline.

    Nodes 1–4 halt on error (critical path).
    Nodes 5–8 log errors and continue (non-critical).

    Parameters
    ----------
    state : PipelineState
        Initial state with source_type, source_ref, and run_id populated.

    Returns
    -------
    PipelineState
        Completed state with all node outputs populated (or None on failure).
    """
    logger.info("=" * 60)
    logger.info("Pipeline run started: %s", state.run_id)
    logger.info("Source: %s — %s", state.source_type, state.source_ref[:80])
    logger.info("=" * 60)

    # Import nodes here to avoid circular imports and allow lazy loading
    from nodes.extractor import extract
    from nodes.cleaner import clean
    from nodes.chunker import chunk
    from nodes.fact_extractor import extract_facts
    from nodes.deduplicator import deduplicate
    from nodes.router import route
    from nodes.supabase_writer import write_to_supabase
    from nodes.notion_writer import write_to_notion
    from nodes.reporter import generate_report

    # -------------------------------------------------------------------------
    # NODE 1: Extract (CRITICAL — halt on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 1:
        logger.info("[Node 1/8] Extracting from source...")
        try:
            result = extract(state.source_type, state.source_ref)
            state.raw_text = result.raw_text
            state.last_completed_node = 1
            save_checkpoint(state)
            logger.info("[Node 1/8] ✓ Extracted %d characters", len(state.raw_text))
        except Exception as e:
            logger.error("[Node 1/8] CRITICAL FAILURE: %s", e)
            state.errors.append({"node": 1, "error": str(e)})
            save_checkpoint(state)
            return state

    # -------------------------------------------------------------------------
    # NODE 2: Clean (CRITICAL — halt on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 2:
        logger.info("[Node 2/8] Cleaning text...")
        try:
            state.clean_text = clean(state.raw_text)
            state.last_completed_node = 2
            save_checkpoint(state)
            logger.info("[Node 2/8] ✓ Cleaned to %d characters", len(state.clean_text))
        except Exception as e:
            logger.error("[Node 2/8] CRITICAL FAILURE: %s", e)
            state.errors.append({"node": 2, "error": str(e)})
            save_checkpoint(state)
            return state

    # -------------------------------------------------------------------------
    # NODE 3: Chunk (CRITICAL — halt on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 3:
        logger.info("[Node 3/8] Chunking text...")
        try:
            state.chunks = chunk(state.clean_text)
            state.last_completed_node = 3
            save_checkpoint(state)
            logger.info("[Node 3/8] ✓ Produced %d chunks", len(state.chunks))
        except Exception as e:
            logger.error("[Node 3/8] CRITICAL FAILURE: %s", e)
            state.errors.append({"node": 3, "error": str(e)})
            save_checkpoint(state)
            return state

    # -------------------------------------------------------------------------
    # NODE 4: Extract Facts (CRITICAL — halt on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 4:
        logger.info("[Node 4/8] Extracting atomic facts...")
        try:
            state.facts = extract_facts(state.chunks, state.source_type, state.source_ref)
            state.last_completed_node = 4
            save_checkpoint(state)
            logger.info("[Node 4/8] ✓ Extracted %d facts", len(state.facts))
        except Exception as e:
            logger.error("[Node 4/8] CRITICAL FAILURE: %s", e)
            state.errors.append({"node": 4, "error": str(e)})
            save_checkpoint(state)
            return state

    # -------------------------------------------------------------------------
    # NODE 5: Deduplicate (NON-CRITICAL — continue on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 5:
        logger.info("[Node 5/8] Deduplicating facts...")
        try:
            from nodes.deduplicator import DedupAction, DedupDecision
            state.dedup_decisions = deduplicate(state.facts)
            state.last_completed_node = 5
            save_checkpoint(state)
            skipped = sum(1 for d in state.dedup_decisions if d.action == DedupAction.SKIP)
            logger.info("[Node 5/8] ✓ Dedup done: %d skipped, %d to write", skipped, len(state.facts) - skipped)
        except Exception as e:
            logger.error("[Node 5/8] Non-critical failure: %s", e)
            state.errors.append({"node": 5, "error": str(e)})
            # Default: treat all facts as INSERT to avoid data loss
            from nodes.deduplicator import DedupAction, DedupDecision
            state.dedup_decisions = [
                DedupDecision(fact_text=f.text, action=DedupAction.INSERT)
                for f in state.facts
            ]
            state.last_completed_node = 5
            save_checkpoint(state)

    # -------------------------------------------------------------------------
    # NODE 6: Route (NON-CRITICAL — continue on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 6:
        logger.info("[Node 6/8] Routing facts to memory tiers...")
        try:
            state.routed_facts = route(state.facts, state.dedup_decisions)
            state.last_completed_node = 6
            save_checkpoint(state)
            logger.info("[Node 6/8] ✓ Routed %d facts", len(state.routed_facts))
        except Exception as e:
            logger.error("[Node 6/8] Non-critical failure: %s", e)
            state.errors.append({"node": 6, "error": str(e)})
            state.routed_facts = []
            state.last_completed_node = 6
            save_checkpoint(state)

    # -------------------------------------------------------------------------
    # NODE 7: Write to Supabase (NON-CRITICAL — continue on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 7:
        logger.info("[Node 7/8] Writing to Supabase...")
        try:
            results = write_to_supabase(state.routed_facts, state.run_id)
            state.write_results = {
                "written": results.written,
                "failed": results.failed,
                "fragment_ids": results.fragment_ids,
                "errors": results.errors,
            }
            state.last_completed_node = 7
            save_checkpoint(state)
            logger.info("[Node 7/8] ✓ Wrote %d fragments (%d failed)", results.written, results.failed)
        except Exception as e:
            logger.error("[Node 7/8] Non-critical failure: %s", e)
            state.errors.append({"node": 7, "error": str(e)})
            state.write_results = {"written": 0, "failed": len(state.routed_facts), "fragment_ids": [], "errors": [str(e)]}
            state.last_completed_node = 7
            save_checkpoint(state)

    # -------------------------------------------------------------------------
    # NODE 8a: Write to Notion (NON-CRITICAL — continue on error)
    # -------------------------------------------------------------------------
    if state.last_completed_node < 8:
        logger.info("[Node 8a/8] Writing summary to Notion...")
        try:
            state.notion_result = write_to_notion(
                write_results=state.write_results,
                source_type=state.source_type,
                source_ref=state.source_ref,
                source_title=state.source_ref,
                facts=state.facts or [],
                pipeline_run_id=state.run_id,
            )
            logger.info("[Node 8a/8] ✓ Notion page created")
        except Exception as e:
            logger.warning("[Node 8a/8] Non-critical failure: %s", e)
            state.errors.append({"node": "8a", "error": str(e)})
            state.notion_result = {}

    # -------------------------------------------------------------------------
    # NODE 8b: Generate Report (NON-CRITICAL — always attempt)
    # -------------------------------------------------------------------------
    logger.info("[Node 8b/8] Generating final report...")
    try:
        state.report = generate_report(state)
    except Exception as e:
        logger.warning("[Node 8b/8] Non-critical failure: %s", e)
        state.errors.append({"node": "8b", "error": str(e)})
        state.report = {"run_id": state.run_id, "status": "partial", "errors": state.errors}

    state.last_completed_node = 8
    state.completed_at = datetime.now(timezone.utc).isoformat()
    save_checkpoint(state)

    logger.info("=" * 60)
    logger.info("Pipeline run COMPLETE: %s", state.run_id)
    if state.write_results:
        logger.info("Result: %d fragments written", state.write_results.get("written", 0))
    if state.errors:
        logger.warning("Non-critical errors: %d", len(state.errors))
    logger.info("=" * 60)

    return state


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NickOS Foundation-layer Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ingest.py --source youtube --url "https://youtube.com/watch?v=..."
  python run_ingest.py --source pdf --path "/path/to/file.pdf"
  python run_ingest.py --source url --url "https://example.com/article"
  python run_ingest.py --source text --text "Raw text to ingest..."
  python run_ingest.py --resume pipeline_artifacts/checkpoint_<run_id>.json
        """,
    )

    parser.add_argument("--source", choices=["youtube", "pdf", "url", "text"], help="Source type")
    parser.add_argument("--url", help="Source URL (for youtube and url sources)")
    parser.add_argument("--path", help="File path (for pdf source)")
    parser.add_argument("--text", help="Raw text to ingest (for text source)")
    parser.add_argument("--resume", help="Path to checkpoint file to resume from")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.resume:
        # Resume from a checkpoint
        if not Path(args.resume).exists():
            logger.error("Checkpoint file not found: %s", args.resume)
            return 1
        state = load_checkpoint(args.resume)

    else:
        # New pipeline run
        if not args.source:
            logger.error("--source is required for new pipeline runs")
            return 1

        # Determine source_ref from args
        if args.source == "youtube":
            if not args.url:
                logger.error("--url is required for youtube source")
                return 1
            source_ref = args.url
        elif args.source == "pdf":
            if not args.path:
                logger.error("--path is required for pdf source")
                return 1
            source_ref = args.path
        elif args.source == "url":
            if not args.url:
                logger.error("--url is required for url source")
                return 1
            source_ref = args.url
        elif args.source == "text":
            if not args.text:
                logger.error("--text is required for text source")
                return 1
            source_ref = args.text
        else:
            logger.error("Unknown source type: %s", args.source)
            return 1

        state = PipelineState(
            run_id=str(uuid.uuid4()),
            source_type=args.source,
            source_ref=source_ref,
        )

    state = run_pipeline(state)

    # Exit code: 0 if at least some data was written, 1 if critical failure
    if state.last_completed_node < 4:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
