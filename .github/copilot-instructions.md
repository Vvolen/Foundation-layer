# GitHub Copilot Instructions — Foundation-layer

> These instructions guide the Copilot coding agent when it works on this repository. Read `CLAUDE.md` for comprehensive context.

## Repository Identity

This is the **build repo** for the NickOS ingestion pipeline. You are implementing an 8-node pipeline that transforms raw sources into structured memory fragments in Supabase with pgvector.

## Build Priority Order

Always work on nodes in sequence: `extractor → cleaner → chunker → fact_extractor → deduplicator → router → supabase_writer → notion_writer/reporter`

Do not implement a later node before an earlier node is complete and tested.

## Code Style Conventions

- Python 3.11+
- Type hints on all function signatures
- Docstrings on all public functions and classes (NumPy style)
- `python-dotenv` for environment variables — always load with `load_dotenv()` at module top
- Logging via the standard `logging` module, not `print()`
- Error handling: nodes 1–4 should `raise` on error; nodes 5–8 should catch, log, and continue

## Node Interface Contract

Each node must follow this interface:

```python
def node_name(state: PipelineState) -> PipelineState:
    """
    Brief description.

    Parameters
    ----------
    state : PipelineState
        The shared pipeline state object.

    Returns
    -------
    PipelineState
        Updated state with this node's output populated.

    Raises
    ------
    NodeError
        If this is a critical node (1–4) and processing fails.
    """
    ...
```

## Database Rules

- **Never** create tables — use `specs/supabase_schema.sql` only
- **Never** hardcode column names — import from a constants module or read the schema
- **Always** use parameterized queries — no string interpolation in SQL
- **Always** batch inserts — max 50 records per upsert call
- **Always** handle the case where `embedding` column already has a value (upsert, not insert)

## Deduplication Rules

The dedup thresholds are fixed — do not change them without explicit instruction:
- Cosine similarity ≥ 0.92: duplicate → skip (do not write)
- Cosine similarity 0.75–0.92: gray zone → call LLM with `gpt-4o` to decide
- Cosine similarity < 0.75: new fact → write

## Testing Requirements

- Each node must have at least one unit test in `tests/`
- Tests must use mocked Supabase/OpenAI clients — never make real API calls in tests
- Smoke test in `tests/test_smoke.py` must pass before any node is considered "done"

## What To Do When Assigned an Issue

1. Read `CLAUDE.md` first
2. Read `plans/task_plan.md` for current phase status
3. Read `plans/progress.md` for last session state
4. Check `plans/findings.md` for relevant architectural decisions
5. Read the relevant node file's docstring to understand the interface
6. Implement, test, update `plans/progress.md`

## What NOT To Do

- Do not read entire large files — use progressive disclosure
- Do not change the `PipelineState` dataclass without updating the orchestrator
- Do not skip writing tests
- Do not commit `.env` or any file containing API keys
- Do not use `print()` for logging — use the `logging` module
- Do not change dedup thresholds without explicit instruction from the repo owner
- Do not implement Phase 2 or Phase 3 features until Phase 1 is complete and passing tests
