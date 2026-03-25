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
import os
from datetime import datetime, timezone

import requests as http_requests

logger = logging.getLogger(__name__)

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"


def _get_notion_headers(api_key: str) -> dict:
    """Build Notion API request headers."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def _truncate(text: str, max_len: int = 2000) -> str:
    """Truncate text to max_len characters for Notion blocks."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def _build_page_blocks(
    write_results,
    facts: list,
    source_type: str,
    source_ref: str,
    pipeline_run_id: str,
) -> list[dict]:
    """Build the Notion page body blocks."""
    blocks = []

    # -- Summary heading --
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "Summary"}}],
        },
    })

    # -- Summary paragraph --
    written = 0
    failed = 0
    if isinstance(write_results, dict):
        written = write_results.get("written", 0)
        failed = write_results.get("failed", 0)
    elif hasattr(write_results, "written"):
        written = write_results.written
        failed = write_results.failed

    total_facts = len(facts) if facts else 0
    summary_text = (
        f"Ingested {total_facts} atomic facts from {source_type} source. "
        f"{written} fragments written to memory, {failed} failed. "
        f"Pipeline run: {pipeline_run_id}"
    )
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": summary_text}}],
        },
    })

    # -- Key Facts heading --
    if facts:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Key Facts"}}],
            },
        })

        # Select top 5 facts by tier priority: procedural > semantic > episodic
        # Since we may not have tier info on AtomicFact, just take first 5
        top_facts = facts[:5] if len(facts) >= 5 else facts

        for fact in top_facts:
            fact_text = fact.text if hasattr(fact, "text") else str(fact)
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": _truncate(fact_text)},
                    }],
                },
            })

    # -- Stats heading --
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "Stats"}}],
        },
    })

    stats_lines = [
        f"Source: {source_type} — {_truncate(source_ref, 200)}",
        f"Total facts extracted: {total_facts}",
        f"Fragments written: {written}",
        f"Fragments failed: {failed}",
        f"Run ID: {pipeline_run_id}",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
    ]

    for line in stats_lines:
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": line},
                }],
            },
        })

    return blocks


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

    # Resolve API key
    api_key = notion_api_key or os.environ.get("NOTION_API_KEY")
    if not api_key:
        logger.warning("NOTION_API_KEY not set — skipping Notion write")
        return {}

    # Resolve database ID
    database_id = notion_database_id or os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        logger.warning("NOTION_DATABASE_ID not set — skipping Notion write")
        return {}

    headers = _get_notion_headers(api_key)

    # Build page title
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title_text = _truncate(source_title, 200) if source_title else source_ref[:200]
    page_title = f"[INGESTED] {title_text} — {date_str}"

    # Build the facts count
    written = 0
    if isinstance(write_results, dict):
        written = write_results.get("written", 0)
    elif hasattr(write_results, "written"):
        written = write_results.written

    # Build page properties
    properties = {
        "title": {
            "title": [{"text": {"content": page_title}}],
        },
    }

    # Try to set additional properties if database supports them
    # These are optional — Notion will ignore unsupported properties
    optional_props = {
        "Source Type": {
            "select": {"name": source_type},
        },
        "Source URL": {
            "url": source_ref if source_ref.startswith("http") else None,
        },
        "Facts Written": {
            "number": written,
        },
        "Pipeline Run ID": {
            "rich_text": [{"text": {"content": pipeline_run_id}}],
        },
    }

    # Only include Source URL if it's a valid URL
    if optional_props["Source URL"]["url"] is None:
        del optional_props["Source URL"]

    properties.update(optional_props)

    # Build page body blocks
    blocks = _build_page_blocks(
        write_results, facts, source_type, source_ref, pipeline_run_id,
    )

    # Create the Notion page
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties,
        "children": blocks,
    }

    try:
        resp = http_requests.post(
            f"{NOTION_BASE_URL}/pages",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code == 200:
            data = resp.json()
            page_id = data.get("id", "")
            page_url = data.get("url", "")
            logger.info("Notion page created: %s", page_url)
            return {"notion_page_id": page_id, "notion_page_url": page_url}
        else:
            error_body = resp.text[:500]
            logger.warning(
                "Notion API returned %d: %s", resp.status_code, error_body,
            )
            # If properties are unsupported, retry with just title
            if resp.status_code == 400 and "property" in error_body.lower():
                logger.info("Retrying with minimal properties...")
                minimal_payload = {
                    "parent": {"database_id": database_id},
                    "properties": {
                        "title": {
                            "title": [{"text": {"content": page_title}}],
                        },
                    },
                    "children": blocks,
                }
                resp2 = http_requests.post(
                    f"{NOTION_BASE_URL}/pages",
                    headers=headers,
                    json=minimal_payload,
                    timeout=30,
                )
                if resp2.status_code == 200:
                    data = resp2.json()
                    return {
                        "notion_page_id": data.get("id", ""),
                        "notion_page_url": data.get("url", ""),
                    }
                else:
                    logger.warning("Notion retry also failed: %d", resp2.status_code)

            return {}

    except http_requests.RequestException as e:
        logger.warning("Notion API request failed: %s", e)
        return {}
    except Exception as e:
        logger.warning("Unexpected error writing to Notion: %s", e)
        return {}