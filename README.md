# NickOS Foundation-layer

> The ingestion spine and memory substrate for NickOS — a progressive-disclosure, agent-native knowledge operating system.

## What This Repo Is

This repository contains the **build artifacts** for the NickOS foundation layer:

- **Ingestion Pipeline** — 8-node pipeline that processes YouTube transcripts, PDFs, web pages, and text into structured memory fragments stored in Supabase with pgvector embeddings.
- **Memory Substrate** — Supabase schema with `memory_fragments`, `memory_contradictions`, `memory_provenance`, and `schema_versions` tables.
- **Pipeline Orchestrator** — `run_ingest.py` with checkpoint/resume logic, error handling, and per-node progress tracking.

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/Vvolen/Foundation-layer.git
cd Foundation-layer

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your actual keys

# 5. Run the pipeline
python run_ingest.py --source youtube --url <URL>
```

## Repository Structure

```
foundation-layer/
├── .github/
│   ├── copilot-instructions.md   # Instructions for the Copilot coding agent
│   └── workflows/
│       ├── test.yml              # Runs on every PR
│       ├── ingest-nightly.yml    # Scheduled nightly ingestion
│       └── evolve.yml            # Self-evolution workflow template
├── .devcontainer/
│   └── devcontainer.json         # Open this repo in a Codespace
├── nodes/                        # The 8 pipeline processing nodes
│   ├── extractor.py              # Node 1: source → raw text
│   ├── cleaner.py                # Node 2: raw text → clean text
│   ├── chunker.py                # Node 3: clean text → semantic chunks
│   ├── fact_extractor.py         # Node 4: chunks → atomic facts
│   ├── deduplicator.py           # Node 5: dedup against existing memory
│   ├── router.py                 # Node 6: route to correct memory tier
│   ├── supabase_writer.py        # Node 7: write to Supabase
│   ├── notion_writer.py          # Node 8a: write summary to Notion
│   └── reporter.py               # Node 8b: generate ingestion report
├── specs/
│   └── supabase_schema.sql       # Full DDL — run this first
├── plans/
│   ├── MASTER_PLAN.md            # The full multi-phase project roadmap
│   ├── GITHUB_ECOSYSTEM_GUIDE.md # GitHub Actions/Copilot/Codespaces deep-dive
│   ├── task_plan.md              # Cold-start task plan for any agent
│   ├── findings.md               # Architectural decisions log
│   └── progress.md               # Session progress log
├── tests/
│   └── test_smoke.py             # Basic smoke tests
├── pipeline_artifacts/           # Generated outputs (gitignored)
├── CLAUDE.md                     # Agent cold-start instructions
├── run_ingest.py                 # Main pipeline orchestrator
├── requirements.txt
├── .env.example
└── .gitignore
```

## Development

### Opening in Codespaces

Click the green **Code** button → **Codespaces** → **Create codespace on main**.  
The devcontainer auto-installs Python 3.11, all dependencies, and VS Code extensions.

### Running Tests

```bash
pytest tests/ -v
```

### GitHub Actions

- **`test.yml`** — Automatically runs on every PR. Installs deps, runs smoke tests.
- **`ingest-nightly.yml`** — Cron-scheduled pipeline run (configure and enable when ready).
- **`evolve.yml`** — Template for the Versailles self-evolution workflow.

## Architecture

See `plans/MASTER_PLAN.md` for the full multi-phase roadmap.

### Phase 0 (This PR) — Scaffolding & Planning
Repository structure, specs, planning documents, devcontainer, starter workflows.

### Phase 1 — Ingestion Pipeline Build
Implement all 8 nodes and the `run_ingest.py` orchestrator.

### Phase 2 — Memory Automation
RAPTOR consolidation, temporal decay scoring, session hydration RPCs, pg_cron jobs.

### Phase 3 — Agent Surface
Expert Factory MVP, Roundtable coordination, meta-orchestration.

## Key Constraints

- **Batch size**: max 50 facts per Supabase upsert
- **Embedding model**: `text-embedding-3-small` (1536 dimensions)
- **Dedup thresholds**: similarity ≥ 0.92 = duplicate, 0.75–0.92 = LLM review, < 0.75 = new
- **Context window**: never load entire files — use progressive disclosure

## Environment Variables

See `.env.example` for all required variables. Never commit `.env`.

## Contributing / Agent Instructions

If you are an AI agent working in this repo, read `CLAUDE.md` first.
