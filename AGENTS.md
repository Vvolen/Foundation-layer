# AGENTS.md — NickOS Foundation-layer

> **Cross-tool agent context file.** This file is the universal standard read by Claude Code,
> Codex CLI, Cursor, and GitHub Copilot. It supplements the tool-specific `CLAUDE.md` and
> `.github/copilot-instructions.md` with shared conventions.
>
> If you are an AI coding agent, read this file and `CLAUDE.md` before doing anything.

---

## Quick Start

1. Read `CLAUDE.md` for full cold-start instructions
2. Read the last 3 entries in `AGENT_NOTES.md` for cross-agent context
3. Read `plans/progress.md` for current session status
4. Do your work
5. Write an entry in `AGENT_NOTES.md` before finishing (**mandatory**)

## Repository Purpose

This is the **build repo** for NickOS — a progressive-disclosure, agent-native knowledge
operating system. The repo contains an 8-node ingestion pipeline that transforms raw sources
(YouTube, PDFs, web pages, text) into structured memory fragments stored in Supabase with
pgvector embeddings.

## Key Conventions

- **Language:** Python 3.11+
- **Type hints** on all function signatures
- **Docstrings** on all public functions (NumPy style)
- **Logging** via `logging` module — never `print()`
- **Environment:** `python-dotenv` with `load_dotenv()` at module top
- **Error handling:** nodes 1–4 raise on error; nodes 5–8 catch, log, continue
- **Database:** never create tables directly; use `specs/supabase_schema.sql`
- **Batch size:** max 50 records per Supabase upsert
- **Dedup thresholds:** ≥0.92 = duplicate (skip), 0.75–0.92 = LLM review, <0.75 = new (insert)

## Agent Memory Protocol

This repo uses an **append-only agent journal** (`AGENT_NOTES.md`) as persistent
cross-session memory. Every agent must:

1. **Read** the last 3 entries before starting work
2. **Write** a new entry before ending a session
3. **Never edit** past entries — append only

See `plans/COLLECTIVE_INTELLIGENCE.md` for the design philosophy and future ideas.

## File Map

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Cold-start instructions (Claude-specific) |
| `AGENTS.md` | Cross-tool agent context (this file) |
| `.github/copilot-instructions.md` | GitHub Copilot instructions |
| `AGENT_NOTES.md` | Append-only agent journal |
| `plans/COLLECTIVE_INTELLIGENCE.md` | Research & ideas for evolving agent memory |
| `plans/MASTER_PLAN.md` | Full project roadmap |
| `plans/progress.md` | Session status tracking |
| `plans/findings.md` | Architectural decisions |
| `specs/supabase_schema.sql` | Database schema (source of truth) |
| `run_ingest.py` | Pipeline orchestrator |
| `nodes/*.py` | Pipeline node implementations |
| `tests/test_smoke.py` | Structural smoke tests |

## Build & Test

```bash
pip install -r requirements.txt
pytest tests/ -v
```
