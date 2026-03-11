# MASTER PLAN — NickOS Foundation-layer
## The Complete Multi-Phase Execution Roadmap

> **Principle:** Plan before execution, always.
> This document is the authoritative roadmap. When in doubt, consult this first.
> Last updated: 2026-03-11

---

## Executive Summary

NickOS is a progressive-disclosure, agent-native knowledge operating system. You are building its foundation: the ingestion spine that transforms raw content into structured, searchable memory. This repository contains everything needed to build it — specs, planning documents, scaffolded code, and GitHub automation.

**The architecture has 5 layers:**

| Layer | Name | What It Does | Where It Lives |
|-------|------|--------------|----------------|
| A | Foundation | 8-node ingestion pipeline → Supabase memory | This repo |
| B | Memory | Supabase pgvector, dedup, decay scoring | Supabase project |
| C | Genome | Versailles repo — knowledge base, skills, META_INDEX | `Vvolen/Versailles` |
| D | Build | This repo — pipeline code, specs, planning | This repo |
| E | Agent Surface | Expert Factory, Roundtable, Meta-orchestration | Phase 3 |

---

## Phase 0: Repository Scaffolding & Planning — ✅ COMPLETE

### Goal
Establish the complete repository structure, all planning documents, database schema, and scaffolded code before any implementation begins.

### Deliverables — All Complete ✅

| Deliverable | File | Status |
|-------------|------|--------|
| Directory structure | (entire repo) | ✅ |
| Agent cold-start instructions | `CLAUDE.md` | ✅ |
| Copilot agent instructions | `.github/copilot-instructions.md` | ✅ |
| Database DDL | `specs/supabase_schema.sql` | ✅ |
| Environment template | `.env.example` | ✅ |
| Python dependencies | `requirements.txt` | ✅ |
| Node placeholders (9 files) | `nodes/*.py` | ✅ |
| Pipeline orchestrator scaffold | `run_ingest.py` | ✅ |
| Smoke tests | `tests/test_smoke.py` | ✅ |
| GitHub Actions workflows | `.github/workflows/` | ✅ |
| Codespace config | `.devcontainer/devcontainer.json` | ✅ |
| Task plan | `plans/task_plan.md` | ✅ |
| Findings log | `plans/findings.md` | ✅ |
| Progress log | `plans/progress.md` | ✅ |
| GitHub ecosystem guide | `plans/GITHUB_ECOSYSTEM_GUIDE.md` | ✅ |
| This master plan | `plans/MASTER_PLAN.md` | ✅ |

### Phase 0 Exit Criteria — Met ✅
- [x] All smoke tests pass (`pytest tests/test_smoke.py -v`)
- [x] Directory structure matches spec
- [x] Schema SQL contains all 4 tables with correct column types
- [x] Every node file has a docstring with input/output contract
- [x] `run_ingest.py` handles checkpoint/resume and all 8 nodes

---

## Phase 1: Ingestion Pipeline Build — 🔜 NEXT

### Goal
Implement all 8 pipeline nodes and verify the full pipeline works end-to-end on real sources.

### Node Build Order (Sequential — Do Not Skip Ahead)

```
Node 1: extractor       → Node 2: cleaner → Node 3: chunker → Node 4: fact_extractor
                                                                        ↓
Node 8b: reporter ← Node 8a: notion_writer ← Node 7: supabase_writer ← Node 5/6: deduplicator/router
```

### Node 1: Extractor

**File:** `nodes/extractor.py`
**What it does:** Takes a source reference and extracts raw text.
**Libraries:** `youtube-transcript-api`, `pdfplumber`, `requests`, `beautifulsoup4`

Implementation details:
- YouTube: use `YouTubeTranscriptApi.get_transcript(video_id)`, extract video_id from URL, concatenate transcript segments
- PDF: use `pdfplumber.open(path)`, iterate pages, join with `\n---\n` page separator
- URL: use `requests.get(url)`, parse with `BeautifulSoup(html, 'html.parser')`, extract `article` or `main` tag text, strip nav/footer
- Text: return as-is

Error handling: raise `NodeExtractionError` with descriptive message on failure

---

### Node 2: Cleaner

**File:** `nodes/cleaner.py`
**What it does:** Normalizes raw text for downstream processing.
**Libraries:** `re`, `unicodedata`

Cleaning pipeline (apply in order):
1. `unicodedata.normalize('NFC', text)` — Unicode normalization
2. Remove YouTube timestamps: `re.sub(r'\[\d+:\d+(?::\d+)?\]', '', text)`
3. Remove auto-caption fillers: `re.sub(r'\[(Music|Applause|Laughter|inaudible|crosstalk)\]', '', text, flags=re.IGNORECASE)`
4. Collapse multiple newlines: `re.sub(r'\n{3,}', '\n\n', text)`
5. Collapse multiple spaces: `re.sub(r' {2,}', ' ', text)`
6. Strip leading/trailing whitespace per line
7. Strip leading/trailing whitespace from full text

---

### Node 3: Chunker

**File:** `nodes/chunker.py`
**What it does:** Splits clean text into overlapping semantic chunks.
**Libraries:** `nltk` (punkt tokenizer)

Algorithm:
1. Tokenize into sentences using `nltk.tokenize.sent_tokenize(text)`
2. Accumulate sentences into chunks until token count reaches `target_tokens`
3. Add overlap by including the last N tokens of the previous chunk
4. Discard chunks shorter than 50 tokens
5. Token count approximation: `len(text.split()) * 1.3` (words-to-tokens factor)

---

### Node 4: Fact Extractor

**File:** `nodes/fact_extractor.py`
**What it does:** Calls `gpt-4o-mini` to extract atomic facts from each chunk.
**Libraries:** `openai`

Implementation:
1. Initialize `openai.OpenAI()` (reads `OPENAI_API_KEY` from env)
2. For each chunk, call `client.chat.completions.create()` with the `EXTRACTION_PROMPT`
3. Parse JSON array response into `AtomicFact` objects
4. Retry on rate limit with exponential backoff: `2^attempt` seconds, max 3 retries
5. On parse failure: log and skip the chunk (non-halting within the node, but node itself is critical)

---

### Node 5: Deduplicator

**File:** `nodes/deduplicator.py`
**What it does:** Checks each fact against memory for semantic duplicates.
**Libraries:** `openai`, `supabase`

Algorithm:
1. Embed all facts in batch: `openai.embeddings.create(model='text-embedding-3-small', input=fact_texts)`
2. For each fact embedding, call the `search_memory` Supabase RPC with `match_count=5, match_threshold=0.75`
3. Get the top result's similarity score
4. Apply decision tree:
   - ≥ 0.92: SKIP
   - 0.75–0.92: call LLM gray zone review
   - < 0.75: INSERT
5. Gray zone: call `gpt-4o` with the prompt "Are these two statements saying the same thing? Reply: YES or NO." Parse and decide.

---

### Node 6: Router

**File:** `nodes/router.py`
**What it does:** Classifies each fact into a memory tier.

Routing logic:
1. Check for procedural patterns: starts with a number + period, contains "step", "first do", "then", "finally", "how to", sequential imperative structure
2. Check for semantic patterns: contains "is defined as", "refers to", "means that", generalizations without specific dates or named events
3. Default: episodic

---

### Node 7: Supabase Writer

**File:** `nodes/supabase_writer.py`
**What it does:** Writes routed facts to `memory_fragments` with embeddings.
**Libraries:** `openai`, `supabase`, `hashlib`

Implementation:
1. Generate embeddings in batches of 100
2. Compute `content_hash = hashlib.sha256(fact_text.strip().lower().encode()).hexdigest()`
3. Build `memory_fragments` insert dict per fact
4. Upsert in batches of 50: `supabase.table('memory_fragments').upsert(batch, on_conflict='content_hash').execute()`
5. For each successful insert, create a `memory_provenance` record
6. Collect fragment IDs and write results

---

### Node 8a: Notion Writer

**File:** `nodes/notion_writer.py`
**What it does:** Creates a summary page in Notion after each ingestion run.
**Libraries:** `requests` (Notion API via HTTP)

Notion API calls:
1. `POST https://api.notion.com/v1/pages` with parent database ID
2. Set title, source URL, facts count as properties
3. Add blocks: summary paragraph, top-5 facts by tier (procedural first, then semantic, then episodic)
4. Return page URL

---

### Node 8b: Reporter

**File:** `nodes/reporter.py`
**What it does:** Generates a JSON report of the pipeline run.

Report includes: run_id, timestamps, source info, stats (facts extracted/written/skipped/failed), error list, duration.
Saves to `pipeline_artifacts/report_{run_id}.json`.

---

### Phase 1 Exit Criteria

Before moving to Phase 2:
- [ ] All 8 nodes implemented (no `NotImplementedError` remaining)
- [ ] `pytest tests/ -v` — all tests pass (100%)
- [ ] Full pipeline run on a YouTube URL produces rows in `memory_fragments` in Supabase
- [ ] Re-running on the same YouTube URL produces 0 new rows (dedup working)
- [ ] A Notion page is created in the configured database
- [ ] `plans/progress.md` updated

---

## Phase 2: Memory Automation — 📋 PLANNED

### Goal
Automate memory maintenance: consolidation, decay, and context hydration.

### Components

#### 2.1 RAPTOR Consolidation
- Periodically merge episodic fragments into semantic-tier summaries
- Algorithm: cluster episodic fragments by topic (embedding similarity), summarize each cluster with `gpt-4o`, write summary as a semantic-tier fragment, mark source episodic fragments as `consolidated=true`
- Trigger: pg_cron job or GitHub Action on schedule

#### 2.2 Temporal Decay Scoring
- Update `decay_score` for all fragments based on: `base_score × time_decay_factor × access_boost`
- `time_decay_factor`: exponential decay from `ingested_at`, half-life configurable (default: 90 days)
- `access_boost`: +10% per access, capped at 2x
- Run as a pg_cron job: `SELECT * FROM update_decay_scores()` nightly

#### 2.3 Session Hydration RPC
- Supabase RPC: `get_session_context(query_embedding vector(1536), tier text, n int)`
- Returns top-n most relevant, non-decayed fragments for a given query
- Used by agents to load relevant memory at session start

#### 2.4 pg_cron Jobs
```sql
-- Nightly decay update (midnight UTC)
SELECT cron.schedule('decay-update', '0 0 * * *', 'SELECT update_decay_scores()');

-- Weekly RAPTOR consolidation (Sunday 2am UTC)
SELECT cron.schedule('raptor-consolidate', '0 2 * * 0', 'SELECT raptor_consolidate()');
```

### Phase 2 Exit Criteria
- [ ] `decay_score` updates nightly in Supabase
- [ ] RAPTOR consolidation runs weekly and produces semantic-tier fragments
- [ ] Session hydration RPC returns relevant context in < 500ms
- [ ] `get_session_context` tested with realistic queries

---

## Phase 3: Agent Surface — 📋 PLANNED

### Goal
Build the Expert Factory, Roundtable, and meta-orchestration layer.

### Components

#### 3.1 Expert Factory MVP
- Function: `create_expert(specialty, memory_filter_tags)` → returns a configured agent persona
- Expert has: a name, a specialty description, a Supabase query to load relevant memory, a system prompt
- First experts to build: Domain Expert (knowledge answers), Builder Expert (code implementation), Critic Expert (review and challenge)

#### 3.2 Roundtable Coordination
- Protocol: Present a question to 2–3 experts, collect their responses, synthesize with a meta-agent
- Structure: `run_roundtable(question, experts=[...])` → returns synthesized response with attribution
- Storage: Roundtable sessions stored as `memory_tier='procedural'` fragments with source_type='roundtable'

#### 3.3 Meta-Orchestration
- The "director" that routes incoming tasks to the right expert or roundtable
- Reads the task, calls `search_memory` to find relevant context, selects the appropriate expert, delegates, returns result
- Entry point: `meta_orchestrator.handle(task: str)` → structured response

### Phase 3 Exit Criteria
- [ ] Expert Factory creates at least 3 working expert personas
- [ ] Roundtable produces synthesized responses on NickOS architecture questions
- [ ] Meta-orchestrator correctly routes 80%+ of test tasks to the right expert

---

## Architecture Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector DB | Supabase + pgvector | PostgreSQL + vector in one place |
| Embedding model | `text-embedding-3-small` (1536d) | Quality/cost balance |
| Fact extraction LLM | `gpt-4o-mini` | Speed + cost |
| Dedup gray zone LLM | `gpt-4o` | Quality for ambiguous cases |
| Dedup threshold | 0.92 / 0.75 | Fixed — do not change |
| Memory tiers | episodic / semantic / procedural | Human memory architecture |
| Pipeline pattern | Linear + checkpoint | Simple, resumable, testable |
| Code hosting | GitHub | Actions, Copilot, Codespaces |

See `plans/findings.md` for full decision rationale.

---

## Unknown Unknowns (Watch For These)

These risks were identified during planning and should be monitored:

### 1. Schema Drift
**Risk:** Supabase schema changes (column renames, type changes) break the pipeline silently.
**Mitigation:** `schema_versions` table. Always record migrations. Never ALTER TABLE without a version bump.

### 2. Semantic Bloat
**Risk:** Over time, `memory_fragments` fills with low-quality or redundant facts that the dedup doesn't catch (below the 0.75 threshold but semantically similar).
**Mitigation:** RAPTOR consolidation (Phase 2). Periodic quality audits. Decay scoring to surface underused fragments.

### 3. Context Window Cliff
**Risk:** As `memory_fragments` grows, session hydration returns too much context, exceeding agent context windows.
**Mitigation:** Session hydration RPC is scoped to top-N with decay weighting. Always use HNSW index (never full scan). Add `max_tokens` parameter to hydration RPC.

### 4. API Rate Limits
**Risk:** Running the pipeline on large sources (long videos, big PDFs) hits OpenAI rate limits mid-run.
**Mitigation:** Checkpoint pattern + `--resume` flag. Exponential backoff in all API calls. Batch size controls.

---

## Versailles Integration (Future)

The `Vvolen/Versailles` repo is the knowledge base. The integration plan:

1. `META_INDEX.md` in Versailles lists all available skills and knowledge sections
2. Agents can load the META_INDEX to understand what's available, then request specific sections
3. The self-evolution workflow (`evolve.yml`) periodically refreshes the META_INDEX based on what's been added to Supabase
4. The RAPTOR consolidation in Phase 2 feeds distilled knowledge back to Versailles as new skill entries

This integration begins in Phase 2. For now, focus on the foundation-layer pipeline.
