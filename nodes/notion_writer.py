"""
Node 8a: Notion Writer
======================
Responsibility: Write a structured summary of the ingestion run to Notion.
Creates a new page in the configured Notion database with a summary of
what was ingested, how many facts were extracted, and key highlights.

Input/Output Contract
---------------------
Input:
    state.write_results : WriteResults  — Summary from Node 7
    state.source_type   : str           — Source type
    state.source_ref    : str           — Source URL or path
    state.facts         : list          — All extracted facts (for highlights)

Output:
    Returns a dict with the Notion page URL and page ID.

Error Behavior:
    NON-CRITICAL NODE (8 of 8) — logs errors and continues.
    Notion write failure does NOT fail the pipeline.

Libraries Used:
    - requests  (Notion API via HTTP — no official Python SDK needed)

Notion Page Structure:
    Title: "[INGESTED] {source_title} — {date}"
    Properties:
        Source Type: select
        Source URL: URL
        Facts Written: number
        Pipeline Run ID: text
    Body (blocks):
        ## Summary
        - N facts extracted, M written to memory
        ## Key Facts (top 5 by tier: procedural, then semantic, then episodic)
        - Bullet list of top facts
        ## Stats
        - Timing, error count, etc.
"""

import logging

logger = logging.getLogger(__name__)


def write_to_notion(
    write_results,
    source_type: str,
    source_ref: str,
    source_title: str,
    facts: list,
    pipeline_run_id: str,
    notion_api_key: str | None = None,
    notion_database_id: str | None = None,
) -> dict:
    """
    Write an ingestion summary page to Notion.

    Parameters
    ----------
    write_results : WriteResults
        Summary of what was written to Supabase (from Node 7).
    source_type : str
        The source type ("youtube", "pdf", "url", "text").
    source_ref : str
        The source URL or file path.
    source_title : str
        Human-readable title for the Notion page.
    facts : list[AtomicFact]
        All extracted facts (used to select highlights for the page body).
    pipeline_run_id : str
        Pipeline run UUID for traceability.
    notion_api_key : str, optional
        Notion API key. If None, loaded from NOTION_API_KEY env var.
    notion_database_id : str, optional
        Notion database ID. If None, loaded from NOTION_DATABASE_ID env var.

    Returns
    -------
    dict
        {"notion_page_id": str, "notion_page_url": str}
        Returns empty dict on failure (non-critical node).
    """
    logger.info("Writing ingestion summary to Notion for run %s", pipeline_run_id)

    # TODO: Implement in Phase 1
    raise NotImplementedError("Node 8a (notion_writer) not yet implemented — Phase 1")
