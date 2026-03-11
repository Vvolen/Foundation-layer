# Task Plan — NickOS Foundation-layer

> Cold-start document for any agent picking up this repo.
> Last updated: 2026-03-11

---

## What This Repo Is

The **build repo** for the NickOS ingestion pipeline. Your job is to build an 8-node pipeline that transforms raw content (YouTube transcripts, PDFs, web pages, text) into structured atomic fact memory fragments in Supabase with pgvector embeddings.

**Companion repo:** `Vvolen/Versailles` — the knowledge base / brain. You are NOT working in that repo here.

---

## Prerequisites Checklist

Before you start any Phase 1 work, verify:

- [ ] **Supabase project exists** and the `specs/supabase_schema.sql` DDL has been run in the SQL Editor
  - Check: `memory_fragments`, `memory_contradictions`, `memory_provenance`, `schema_versions` tables exist
  - Check: pgvector extension is enabled
- [ ] **Environment variables set** — copy `.env.example` to `.env` and fill in:
  - `SUPABASE_URL` — from Supabase project settings
  - `SUPABASE_SERVICE_KEY` — from Supabase project settings (service role key, not anon key)
  - `OPENAI_API_KEY` — from platform.openai.com
  - `NOTION_API_KEY` — from notion.so/my-integrations
  - `NOTION_DATABASE_ID` — the ID of the Notion database for ingestion summaries
- [ ] **Python 3.11+** installed (or use Codespace — it's pre-configured)
- [ ] **Dependencies installed**: `pip install -r requirements.txt`
- [ ] **Smoke tests pass**: `pytest tests/test_smoke.py -v` — all tests should pass before writing any new code

---

## Repo Structure to Know

```
nodes/          ← All 8 pipeline node files. Work here in Phase 1.
specs/          ← Database schema. Read-only for most agents.
plans/          ← This file, MASTER_PLAN.md, findings.md, progress.md
tests/          ← Add tests here alongside each node implementation
run_ingest.py   ← The orchestrator. Already scaffolded — nodes just need implementing.
CLAUDE.md       ← Read this first (you're already here)
```

---

## Build Steps — Phase 0 (Scaffolding) — COMPLETE

- [x] Create directory structure
- [x] Write `specs/supabase_schema.sql`
- [x] Write planning documents
- [x] Write `CLAUDE.md`
- [x] Write `.github/copilot-instructions.md`
- [x] Scaffold `run_ingest.py` with PipelineState and checkpoint logic
- [x] Create placeholder nodes with docstrings and function signatures
- [x] Write smoke tests
- [x] Create GitHub Actions workflows
- [x] Create devcontainer config

**Phase 0 exit criteria:** All smoke tests pass. ✅

---

## Build Steps — Phase 1 (Pipeline Implementation) — NEXT

Work through nodes in this exact order. Do NOT implement a later node before the earlier node is complete and tested.

### Node 1: `nodes/extractor.py` — IMPLEMENT FIRST
**Goal:** Make `extract(source_type, source_ref)` work for all 4 source types.

**Sub-tasks:**
1. Implement `_extract_text(text)` — trivial pass-through (start here to verify the interface works)
2. Implement `_extract_youtube(url)` — use `youtube-transcript-api`
3. Implement `_extract_pdf(path)` — use `pdfplumber`
4. Implement `_extract_url(url)` — use `requests` + `beautifulsoup4`
5. Add unit tests for each sub-extractor in `tests/test_extractor.py`
6. Run full smoke tests — they should still pass

**Exit criteria:** `python run_ingest.py --source text --text "Hello world"` runs Node 1 successfully and prints `[Node 1/8] ✓ Extracted N characters`.

---

### Node 2: `nodes/cleaner.py` — AFTER NODE 1
**Goal:** Make `clean(raw_text)` produce normalized text.

**Sub-tasks:**
1. Implement YouTube timestamp removal (regex: `\[\d+:\d+:\d+\]`, `\d+:\d+`)
2. Implement filler phrase removal (`[Music]`, `[Applause]`, `[inaudible]`)
3. Implement whitespace normalization
4. Implement Unicode normalization (NFC)
5. Add unit tests in `tests/test_cleaner.py`

**Exit criteria:** `python run_ingest.py --source text --text "[00:01] Hello [Music] world"` runs Nodes 1+2 successfully.

---

### Node 3: `nodes/chunker.py` — AFTER NODE 2
**Goal:** Make `chunk(clean_text)` split text into overlapping semantic chunks.

**Sub-tasks:**
1. Install and use NLTK sentence tokenizer
2. Implement sliding window chunking (512 token target, 50 token overlap)
3. Ensure chunks always split on sentence boundaries
4. Add unit tests in `tests/test_chunker.py`

**Exit criteria:** Pipeline runs through Node 3 producing a list of `Chunk` objects.

---

### Node 4: `nodes/fact_extractor.py` — AFTER NODE 3
**Goal:** Make `extract_facts(chunks, source_type, source_ref)` return atomic facts.

**Sub-tasks:**
1. Initialize OpenAI client (from env var `OPENAI_API_KEY`)
2. Implement the prompt call to `gpt-4o-mini` with the `EXTRACTION_PROMPT` template
3. Parse JSON response into `AtomicFact` objects
4. Add exponential backoff for API rate limits (max 3 retries)
5. Add unit tests with mocked OpenAI client in `tests/test_fact_extractor.py`

**Exit criteria:** Pipeline runs through Node 4 with a real (or mocked) OpenAI call.

---

### Node 5: `nodes/deduplicator.py` — AFTER NODE 4
**Goal:** Make `deduplicate(facts)` check each fact against Supabase and return dedup decisions.

**Sub-tasks:**
1. Initialize OpenAI + Supabase clients
2. Embed each fact using `text-embedding-3-small`
3. Call `search_memory` RPC in Supabase to find top-k similar fragments
4. Apply thresholds: ≥0.92 = SKIP, 0.75–0.92 = LLM review, <0.75 = INSERT
5. Implement LLM gray zone review (call `gpt-4o` with both facts)
6. Add unit tests with mocked clients

**Exit criteria:** Pipeline runs through Node 5. Re-running on the same source produces SKIPs for previously ingested facts.

---

### Node 6: `nodes/router.py` — AFTER NODE 5
**Goal:** Make `route(facts, dedup_decisions)` classify each fact into a memory tier.

**Sub-tasks:**
1. Implement procedural detector (regex: numbered lists, "step N", "first/then/finally")
2. Implement semantic detector (definitions, generalizations)
3. Default to episodic
4. Add unit tests

**Exit criteria:** Pipeline runs through Node 6 producing `RoutedFact` objects with `memory_tier` set.

---

### Node 7: `nodes/supabase_writer.py` — AFTER NODE 6
**Goal:** Make `write_to_supabase(routed_facts, pipeline_run_id)` write fragments to Supabase.

**Sub-tasks:**
1. Initialize Supabase client + OpenAI client
2. Generate embeddings for each fact (batches of 100)
3. Compute `content_hash` (SHA-256 of normalized fact text)
4. Upsert to `memory_fragments` in batches of 50
5. Create `memory_provenance` record for each fragment
6. Add integration test (requires real or test Supabase instance)

**Exit criteria:** Running the full pipeline on a new source writes rows to `memory_fragments`. Re-running the same source upserts (no duplicates).

---

### Nodes 8a + 8b: `nodes/notion_writer.py` + `nodes/reporter.py` — AFTER NODE 7
**Goal:** Write Notion page and generate run report.

**Sub-tasks:**
1. Implement `write_to_notion()` using the Notion API (POST to `https://api.notion.com/v1/pages`)
2. Implement `generate_report()` to serialize `PipelineState` to a JSON report file
3. Add unit tests with mocked Notion API

**Exit criteria:** Full pipeline run produces a Notion page (or graceful skip if Notion not configured) and a JSON report in `pipeline_artifacts/`.

---

### Phase 1 Final Exit Criteria
Before moving to Phase 2:
- [ ] All 8 nodes implemented
- [ ] `pytest tests/ -v` passes (all tests green)
- [ ] Full pipeline run on a YouTube video produces rows in `memory_fragments`
- [ ] Re-running on the same source produces no new rows (dedup working)
- [ ] Notion page created with ingestion summary
- [ ] `plans/progress.md` updated with Phase 1 completion notes

---

## Build Steps — Phase 2 (Memory Automation) — FUTURE

- [ ] RAPTOR consolidation: periodic summarization of episodic → semantic tier
- [ ] Temporal decay scoring: update `decay_score` based on recency and access frequency
- [ ] Session hydration RPC: `get_session_context(query, n=20)` for agent context injection
- [ ] pg_cron background jobs: schedule decay updates and RAPTOR runs in Supabase

---

## Build Steps — Phase 3 (Agent Surface) — FUTURE

- [ ] Expert Factory MVP: create specialized agent personas from memory subsets
- [ ] Roundtable coordination: multi-agent discussion protocol
- [ ] Meta-orchestration: agent that routes tasks to the right expert

---

## Key Constraints (Do Not Violate)

| Constraint | Value | Reason |
|------------|-------|--------|
| Supabase batch size | max 50 records/upsert | Avoids timeouts |
| Embedding batch size | max 100/request | OpenAI API limit |
| Embedding model | `text-embedding-3-small` (1536d) | Schema is fixed at 1536 |
| Dedup threshold (hard) | 0.92 | Do not change |
| Dedup threshold (gray zone) | 0.75 | Do not change |
| Fact extraction model | `gpt-4o-mini` | Cost control |
| Gray zone review model | `gpt-4o` | Quality for edge cases |
| API retries | max 3 | With exponential backoff |
| Context window | Never load entire files | Progressive disclosure |

---

## Where To Get Help

- Architecture questions → `plans/MASTER_PLAN.md`
- Past decisions → `plans/findings.md`
- Schema reference → `specs/supabase_schema.sql`
- GitHub ecosystem → `plans/GITHUB_ECOSYSTEM_GUIDE.md`
- Previous session state → `plans/progress.md`
