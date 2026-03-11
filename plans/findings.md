# Plans — Architectural Findings & Decisions

> This file records key architectural decisions made during the NickOS build.
> New decisions get appended as they are made. Never edit past entries — append only.
> Format: `## Decision N — <Title> — <Date>`

---

## Decision 1 — 8-Node Linear Pipeline Architecture — 2026-03-06

**Context:** Needed an ingestion pipeline that could handle multiple source types (YouTube, PDF, URL, text) and produce structured memory fragments in Supabase.

**Decision:** Use a linear 8-node pipeline with a shared `PipelineState` dataclass:
`extractor → cleaner → chunker → fact_extractor → deduplicator → router → supabase_writer → notion_writer/reporter`

**Rationale:** Linear pipelines are easy to reason about, easy to test node-by-node, and easy to resume from checkpoints. Each node has a single responsibility with a clear input/output contract.

**Consequence:** Nodes 1–4 are on the critical path (halt on error). Nodes 5–8 are non-critical (log error, continue). This means we always get some output even if downstream nodes fail.

---

## Decision 2 — Supabase + pgvector for Memory Storage — 2026-03-06

**Context:** Needed a vector database for semantic search with the ability to add structured metadata and relational queries.

**Decision:** Use Supabase (PostgreSQL + pgvector extension) as the primary memory store.

**Rationale:**
- PostgreSQL gives us full relational capabilities alongside vector search
- pgvector HNSW indexes provide fast approximate nearest-neighbor search
- Supabase provides hosted infrastructure, RLS, auto-generated APIs
- Single data store for both vector similarity and structured queries (no separate vector DB needed)

**Consequence:** Embedding column must always be `vector(1536)` to match `text-embedding-3-small`. Never change dimensions without a migration.

---

## Decision 3 — Deduplication Thresholds — 2026-03-06

**Context:** Need to prevent the same fact from being stored multiple times as sources are re-ingested.

**Decision:** Three-tier dedup:
- Cosine similarity ≥ 0.92: SKIP (clear duplicate)
- Cosine similarity 0.75–0.92: LLM gray zone (call `gpt-4o` to decide)
- Cosine similarity < 0.75: INSERT (new knowledge)

**Rationale:** A hard threshold alone produces false positives (similar but distinct facts get skipped). The LLM gray zone handles paraphrases and near-duplicates with high accuracy.

**Consequence:** Dedup cost is O(n × k) where k = top-k similar fragments retrieved per fact. Budget for LLM calls in the 0.75–0.92 band.

---

## Decision 4 — Memory Tiers: Episodic, Semantic, Procedural — 2026-03-06

**Context:** Not all memory fragments are the same. Specific events, general knowledge, and how-to instructions need different treatment.

**Decision:** Three memory tiers:
- **Episodic**: Raw events, specific instances, dated observations
- **Semantic**: Distilled, generalized, timeless knowledge
- **Procedural**: Step-by-step instructions, how-to sequences

**Rationale:** Mirrors human memory architecture. Allows different retrieval and decay strategies per tier (episodic decays faster; semantic is more persistent; procedural is accessed differently).

**Consequence:** Router (Node 6) must classify each fact. Retrieval RPCs must support filtering by tier.

---

## Decision 5 — Checkpoint Pattern for Pipeline Resumability — 2026-03-06

**Context:** Pipeline runs can take minutes. Failures partway through (e.g., API timeout after Node 4) should not require restarting from scratch.

**Decision:** Save `PipelineState` to `pipeline_artifacts/checkpoint_<run_id>.json` after each node completes. Support `--resume <path>` CLI flag.

**Rationale:** Avoids duplicate API calls. Saves cost (no re-generating embeddings for facts already processed). Enables recovery from transient failures.

**Consequence:** `pipeline_artifacts/` is gitignored. Checkpoint files persist between runs on the same machine or in the same Codespace.

---

## Decision 6 — Embedding Model: text-embedding-3-small — 2026-03-06

**Context:** Need to choose an embedding model that balances quality, cost, and dimension size.

**Decision:** Use `text-embedding-3-small` (OpenAI) at 1536 dimensions for all fact embeddings.

**Rationale:**
- Good quality for semantic search (better than ada-002 on MTEB benchmarks)
- Lower cost than `text-embedding-3-large`
- 1536 dimensions is manageable for Supabase storage at scale
- OpenAI API is already required for `gpt-4o-mini` fact extraction

**Consequence:** The `embedding vector(1536)` column in `memory_fragments` is fixed. Any future switch to a different embedding model requires a migration + re-embedding of all existing fragments.

---

## Decision 7 — GitHub Actions for Pipeline Automation — 2026-03-11

**Context:** Need a way to run the ingestion pipeline on a schedule without manual intervention.

**Decision:** Use GitHub Actions with a cron-scheduled workflow (`ingest-nightly.yml`) for automated ingestion.

**Rationale:**
- Free for public repos; cheap for private
- Secrets management built in (no need for separate secret store)
- Can trigger on schedule, PR, issue, or manual dispatch
- Same environment as Codespaces (Python, dependencies)

**Consequence:** Pipeline runs in ephemeral containers — no persistent file system between runs. Use Supabase for persistent storage; use Actions artifacts for short-term checkpoint storage (7-day retention).

---

## Decision 8 — Progressive Disclosure Architecture — 2026-03-06

**Context:** AI agents working in this repo have finite context windows. Loading entire files wastes tokens.

**Decision:** Design all code files with progressive disclosure in mind:
- Every module has a rich docstring at the top (readable without loading the function bodies)
- Plans are structured with clear headers (readable section-by-section)
- CLAUDE.md is the canonical cold-start document

**Consequence:** Agents must be instructed (via `CLAUDE.md` and `copilot-instructions.md`) to read headers first, then drill into specifics. Never read entire large files.

---

*Append new decisions below this line.*
