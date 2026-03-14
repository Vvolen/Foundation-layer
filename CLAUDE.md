# CLAUDE.md — Agent Cold-Start Instructions

> Read this file first. It takes ~2 minutes. It will save you from making expensive mistakes.

## What This Repo Is

`Foundation-layer` is the **build repo** for NickOS — a progressive-disclosure, agent-native knowledge operating system. This repo contains the ingestion pipeline code, specs, and planning documents. It is NOT the knowledge base itself (that's `Vvolen/Versailles`).

**Your job here:** Build and maintain the 8-node ingestion pipeline that transforms raw sources (YouTube, PDFs, web pages, text) into structured memory fragments stored in Supabase with pgvector embeddings.

---

## What NOT To Do

1. **Do NOT read entire files at once.** Use progressive disclosure — read the file header/docstring first, then specific sections you need. Files will grow large.
2. **Do NOT create tables that already exist.** Always check `specs/supabase_schema.sql` before any `CREATE TABLE`. The schema is versioned — respect it.
3. **Do NOT hardcode column names** in queries. Reference `specs/supabase_schema.sql` for the canonical column list. Schema may evolve.
4. **Do NOT skip the dedup check.** Every fact MUST pass through Node 5 (`deduplicator.py`) before writing. Bypassing dedup breaks memory integrity.
5. **Do NOT commit `.env` files.** Use `.env.example` as the template. Never log API keys.
6. **Do NOT change the node interface contracts** without updating `plans/MASTER_PLAN.md`. The orchestrator depends on these contracts.
7. **Do NOT batch more than 50 records** per Supabase upsert. Larger batches cause timeouts.

---

## The Build Order (Sequential — Don't Skip Ahead)

```
Phase 0 (Planning)  ← YOU ARE HERE
  └── specs/supabase_schema.sql   (run in Supabase SQL editor first)
  └── plans/                      (all planning docs)
  └── nodes/                      (placeholder stubs)

Phase 1 (Pipeline Build)
  Node 1: nodes/extractor.py      — source → raw_text
  Node 2: nodes/cleaner.py        — raw_text → clean_text
  Node 3: nodes/chunker.py        — clean_text → List[Chunk]
  Node 4: nodes/fact_extractor.py — List[Chunk] → List[AtomicFact]
  Node 5: nodes/deduplicator.py   — List[AtomicFact] → dedup decision per fact
  Node 6: nodes/router.py         — List[AtomicFact] → routed to memory tier
  Node 7: nodes/supabase_writer.py — write fragments to Supabase
  Node 8: nodes/notion_writer.py + nodes/reporter.py — notify/summarize
  └── run_ingest.py               — orchestrate all 8 nodes

Phase 2 (Memory Automation)
  └── RAPTOR consolidation RPC
  └── Temporal decay scoring
  └── Session hydration RPC
  └── pg_cron background jobs

Phase 3 (Agent Surface)
  └── Expert Factory MVP
  └── Roundtable coordination
  └── Meta-orchestration
```

---

## Where To Find Things

| What You Need | Where To Look |
|---------------|---------------|
| Database schema (DDL) | `specs/supabase_schema.sql` |
| Full project roadmap | `plans/MASTER_PLAN.md` |
| GitHub ecosystem guide | `plans/GITHUB_ECOSYSTEM_GUIDE.md` |
| Cold-start task plan | `plans/task_plan.md` |
| Architectural decisions | `plans/findings.md` |
| Session progress log | `plans/progress.md` |
| **Power tools & MCP reference** | **`plans/POWER_TOOLS.md`** |
| Node function signatures | `nodes/<node_name>.py` docstrings |
| Pipeline orchestration | `run_ingest.py` |
| Environment variables | `.env.example` |
| Smoke tests | `tests/test_smoke.py` |

---

## Key Constraints

### API & Compute
- **Embedding model**: `text-embedding-3-small` (1536 dimensions)
- **LLM for fact extraction**: `gpt-4o-mini` (fast, cheap, good enough for atomic facts)
- **LLM for dedup gray zone**: `gpt-4o` (only when similarity is 0.75–0.92)
- **Supabase batch size**: max 50 records per upsert
- **OpenAI rate limit**: implement exponential backoff, max 3 retries

### Memory Architecture
- **Dedup thresholds**: ≥ 0.92 = duplicate (skip), 0.75–0.92 = LLM review, < 0.75 = new fact (insert)
- **Memory tiers**: episodic (raw events), semantic (distilled facts), procedural (how-to sequences)
- **Embedding column**: `embedding vector(1536)` — never change the dimension without migrating

### Pipeline Behavior
- **Nodes 1–4**: halt on error (critical path — bad input = bad output downstream)
- **Nodes 5–8**: continue on error (log the failure, skip the item, continue processing)
- **Checkpoint pattern**: save state after each node completes so pipeline can resume
- **Checkpoint file**: `pipeline_artifacts/checkpoint_<run_id>.json`

---

## How To Navigate This Codebase

```bash
# See what exists at the top level
ls -la

# See the plan (do this first)
head -100 plans/MASTER_PLAN.md

# See the database schema
cat specs/supabase_schema.sql

# See what a node does (don't read the full file, just the docstring)
python -c "import nodes.extractor; help(nodes.extractor.extract)"

# Check current progress
cat plans/progress.md
```

---

## Running the Pipeline

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with real values

# Run ingestion (single source)
python run_ingest.py --source youtube --url "https://youtube.com/watch?v=..."
python run_ingest.py --source pdf --path "/path/to/file.pdf"
python run_ingest.py --source url --url "https://example.com/article"

# Run tests
pytest tests/ -v
```

---

## The PipelineState Dataclass (Key Design Concept)

The orchestrator passes a single `PipelineState` object through all 8 nodes. Never mutate it outside the designated node function. The state tracks:

```python
@dataclass
class PipelineState:
    run_id: str                    # UUID for this pipeline run
    source_type: str               # "youtube" | "pdf" | "url" | "text"
    source_ref: str                # URL or file path
    raw_text: str | None           # Output of Node 1
    clean_text: str | None         # Output of Node 2
    chunks: list | None            # Output of Node 3
    facts: list | None             # Output of Node 4
    dedup_decisions: list | None   # Output of Node 5
    routed_facts: list | None      # Output of Node 6
    write_results: dict | None     # Output of Node 7
    report: dict | None            # Output of Node 8
    errors: list                   # Accumulated errors (nodes 5-8)
    checkpoint_path: str           # Where to save/load state
```

---

## Power Tools & Environment

This repo uses an enhanced Claude Code environment. See `plans/POWER_TOOLS.md` for the complete reference.

**Core tools (installed via setup script):**
- **Ruflo** — multi-agent swarm orchestrator (queen-node topology)
- **mcpc** — MCP context proxy (progressive disclosure for tools)
- **jCodeMunch** — token-efficient code exploration (99% savings)
- **skillfish** — universal skill manager

**Key MCP servers (configured in `.mcp.json`):**
- **Context7** — injects current library docs at prompt time
- **Context-Mode** — compresses output by up to 98%

**Design principle:** Progressive disclosure. Don't load everything at once. Start with structure, reveal details on demand. This applies to code reading, tool loading, skill activation, and memory hydration.

---

## Security Reminders

- All API keys in `.env` (never committed)
- Supabase service key has admin privileges — handle with care
- Notion API key scoped to specific databases only
- Never log fact content that may contain PII
