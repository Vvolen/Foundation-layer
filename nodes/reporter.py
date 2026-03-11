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
    logger.info("Generating report for run %s", state.run_id if state else "unknown")

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 8b (reporter) not yet implemented — Phase 1")
