"""
Node 8b: Reporter
=================
Responsibility: Generate a structured ingestion report as a Python dict
(and optionally as a JSON file in pipeline_artifacts/). This report is
the final output of a pipeline run — it summarizes what happened,
what was written, what was skipped, and any errors encountered.

Input/Output Contract
---------------------
Input:
    state (full PipelineState)  — All node outputs for this run

Output:
    state.report : dict  — The final pipeline run report

Error Behavior:
    NON-CRITICAL NODE (8 of 8) — logs errors and continues.
    Always returns at least a minimal report, even if some state is missing.

Report Structure:
    {
        "run_id": str,
        "timestamp": str (ISO 8601),
        "source_type": str,
        "source_ref": str,
        "status": "success" | "partial" | "failed",
        "stats": {
            "raw_text_length": int,
            "clean_text_length": int,
            "chunks_count": int,
            "facts_extracted": int,
            "facts_skipped_dedup": int,
            "facts_inserted": int,
            "facts_failed_write": int,
        },
        "errors": list,
        "notion_page_url": str | None,
        "duration_seconds": float
    }

Libraries Used:
    - json      (serialize report to file)
    - datetime  (ISO timestamps)
    - pathlib   (write to pipeline_artifacts/)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path("pipeline_artifacts")


def generate_report(state) -> dict:
    """
    Generate the final pipeline run report from the completed PipelineState.

    Parameters
    ----------
    state : PipelineState
        The completed pipeline state after all nodes have run.

    Returns
    -------
    dict
        The full pipeline run report. Also saved to
        pipeline_artifacts/report_{run_id}.json.

    Notes
    -----
    Always returns a report dict. If data is missing (node failed),
    the relevant fields will be None or 0.
    """
    run_id = getattr(state, "run_id", "unknown")
    logger.info("Generating report for run %s", run_id)

    now = datetime.now(timezone.utc).isoformat()

    # Calculate duration
    duration_seconds = None
    started_at = getattr(state, "started_at", None)
    if started_at:
        try:
            if isinstance(started_at, str):
                start_dt = datetime.fromisoformat(started_at)
            else:
                start_dt = started_at
            duration_seconds = (datetime.now(timezone.utc) - start_dt).total_seconds()
        except Exception as e:
            logger.debug("Could not compute duration: %s", e)

    # Gather stats safely
    raw_text = getattr(state, "raw_text", None)
    clean_text = getattr(state, "clean_text", None)
    chunks = getattr(state, "chunks", None)
    facts = getattr(state, "facts", None)
    dedup_decisions = getattr(state, "dedup_decisions", None)
    write_results = getattr(state, "write_results", None)
    notion_result = getattr(state, "notion_result", None)
    errors = getattr(state, "errors", [])
    last_completed_node = getattr(state, "last_completed_node", 0)

    # Count dedup skips
    facts_skipped_dedup = 0
    if dedup_decisions:
        from nodes.deduplicator import DedupAction
        for d in dedup_decisions:
            if hasattr(d, "action") and d.action == DedupAction.SKIP:
                facts_skipped_dedup += 1
            elif isinstance(d, dict) and d.get("action") == "SKIP":
                facts_skipped_dedup += 1

    # Extract write stats
    facts_inserted = 0
    facts_failed_write = 0
    if isinstance(write_results, dict):
        facts_inserted = write_results.get("written", 0)
        facts_failed_write = write_results.get("failed", 0)
    elif write_results and hasattr(write_results, "written"):
        facts_inserted = write_results.written
        facts_failed_write = write_results.failed

    # Determine overall status
    if last_completed_node < 4:
        status = "failed"
    elif errors:
        status = "partial"
    else:
        status = "success"

    # Notion page URL
    notion_page_url = None
    if isinstance(notion_result, dict):
        notion_page_url = notion_result.get("notion_page_url")

    # Build report
    report = {
        "run_id": run_id,
        "timestamp": now,
        "source_type": getattr(state, "source_type", "unknown"),
        "source_ref": getattr(state, "source_ref", "unknown"),
        "status": status,
        "last_completed_node": last_completed_node,
        "stats": {
            "raw_text_length": len(raw_text) if raw_text else 0,
            "clean_text_length": len(clean_text) if clean_text else 0,
            "chunks_count": len(chunks) if chunks else 0,
            "facts_extracted": len(facts) if facts else 0,
            "facts_skipped_dedup": facts_skipped_dedup,
            "facts_inserted": facts_inserted,
            "facts_failed_write": facts_failed_write,
        },
        "errors": [str(e) if not isinstance(e, (str, dict)) else e for e in errors],
        "notion_page_url": notion_page_url,
        "duration_seconds": round(duration_seconds, 2) if duration_seconds else None,
    }

    # Save report to file
    try:
        ARTIFACTS_DIR.mkdir(exist_ok=True)
        report_path = ARTIFACTS_DIR / f"report_{run_id}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info("Report saved to %s", report_path)
        report["report_path"] = str(report_path)
    except Exception as e:
        logger.warning("Could not save report to file: %s", e)

    # Log summary
    logger.info(
        "Report: status=%s, facts=%d, written=%d, skipped=%d, failed=%d, errors=%d",
        status,
        report["stats"]["facts_extracted"],
        facts_inserted,
        facts_skipped_dedup,
        facts_failed_write,
        len(errors),
    )

    return report