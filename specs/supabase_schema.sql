-- =============================================================================
-- NickOS Foundation-layer — Supabase Schema DDL
-- =============================================================================
-- Prerequisites:
--   1. Enable the pgvector extension in Supabase:
--      Dashboard → Database → Extensions → Search "vector" → Enable
--   2. Run this entire file in the Supabase SQL Editor
--   3. Never re-run CREATE TABLE statements — use ALTER TABLE for schema changes
--      and record changes in schema_versions
-- =============================================================================

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- SCHEMA VERSION TRACKING
-- =============================================================================

CREATE TABLE IF NOT EXISTS schema_versions (
    id            BIGSERIAL PRIMARY KEY,
    version       TEXT        NOT NULL UNIQUE,
    applied_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description   TEXT,
    migration_sql TEXT
);

-- Record this initial schema version
INSERT INTO schema_versions (version, description)
VALUES ('0.1.0', 'Initial schema — memory_fragments, memory_contradictions, memory_provenance, schema_versions')
ON CONFLICT (version) DO NOTHING;

-- =============================================================================
-- MEMORY FRAGMENTS
-- The core memory table. Every atomic fact extracted from every source
-- lives here as a row. The embedding enables semantic search via pgvector.
-- =============================================================================

CREATE TABLE IF NOT EXISTS memory_fragments (
    -- Identity
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Content
    content         TEXT        NOT NULL,                        -- The atomic fact / memory fragment text
    summary         TEXT,                                        -- Optional one-sentence summary
    source_type     TEXT        NOT NULL,                        -- 'youtube' | 'pdf' | 'url' | 'text'
    source_ref      TEXT        NOT NULL,                        -- URL, file path, or identifier
    source_title    TEXT,                                        -- Human-readable source title

    -- Memory tier classification
    memory_tier     TEXT        NOT NULL DEFAULT 'episodic',     -- 'episodic' | 'semantic' | 'procedural'

    -- Vector embedding (text-embedding-3-small = 1536 dimensions)
    embedding       vector(1536),

    -- Temporal scoring
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed   TIMESTAMPTZ,
    access_count    INTEGER     NOT NULL DEFAULT 0,
    decay_score     FLOAT       NOT NULL DEFAULT 1.0,            -- 1.0 = fresh, approaches 0 with time

    -- Deduplication
    content_hash    TEXT        NOT NULL,                        -- SHA-256 of normalized content for exact dedup
    is_duplicate    BOOLEAN     NOT NULL DEFAULT FALSE,
    canonical_id    UUID        REFERENCES memory_fragments(id), -- Points to the canonical version if this is a dup

    -- Pipeline tracking
    pipeline_run_id TEXT,                                        -- The run_id that ingested this fragment
    node_version    TEXT,                                        -- Version of the node that produced this

    -- Metadata (flexible JSON for source-specific fields)
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

-- Indexes for memory_fragments
CREATE INDEX IF NOT EXISTS idx_mf_memory_tier    ON memory_fragments (memory_tier);
CREATE INDEX IF NOT EXISTS idx_mf_source_type    ON memory_fragments (source_type);
CREATE INDEX IF NOT EXISTS idx_mf_content_hash   ON memory_fragments (content_hash);
CREATE INDEX IF NOT EXISTS idx_mf_ingested_at    ON memory_fragments (ingested_at DESC);
CREATE INDEX IF NOT EXISTS idx_mf_decay_score    ON memory_fragments (decay_score DESC);
CREATE INDEX IF NOT EXISTS idx_mf_pipeline_run   ON memory_fragments (pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_mf_is_duplicate   ON memory_fragments (is_duplicate);

-- Full-text search index (GIN for fast ILIKE / to_tsvector queries)
CREATE INDEX IF NOT EXISTS idx_mf_content_fts
    ON memory_fragments USING GIN (to_tsvector('english', content));

-- HNSW vector index for fast approximate nearest-neighbor search
-- ef_construction=128, m=16 are good defaults for production
CREATE INDEX IF NOT EXISTS idx_mf_embedding_hnsw
    ON memory_fragments USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 128);

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mf_updated_at
    BEFORE UPDATE ON memory_fragments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- MEMORY CONTRADICTIONS
-- When two memory fragments assert conflicting facts, a contradiction record
-- is created for review and resolution.
-- =============================================================================

CREATE TABLE IF NOT EXISTS memory_contradictions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- The two conflicting fragments
    fragment_a_id   UUID        NOT NULL REFERENCES memory_fragments(id) ON DELETE CASCADE,
    fragment_b_id   UUID        NOT NULL REFERENCES memory_fragments(id) ON DELETE CASCADE,

    -- Conflict description
    conflict_type   TEXT        NOT NULL,                        -- 'factual' | 'temporal' | 'semantic' | 'numerical'
    conflict_detail TEXT        NOT NULL,                        -- LLM-generated explanation of the conflict
    similarity_score FLOAT,                                      -- Cosine similarity that triggered detection

    -- Resolution
    status          TEXT        NOT NULL DEFAULT 'pending',      -- 'pending' | 'resolved_a' | 'resolved_b' | 'both_valid' | 'archived'
    resolved_at     TIMESTAMPTZ,
    resolved_by     TEXT,                                        -- 'human' | 'llm_auto' | agent name
    resolution_note TEXT,

    -- Pipeline tracking
    pipeline_run_id TEXT,

    CONSTRAINT chk_different_fragments CHECK (fragment_a_id != fragment_b_id)
);

CREATE INDEX IF NOT EXISTS idx_mc_fragment_a   ON memory_contradictions (fragment_a_id);
CREATE INDEX IF NOT EXISTS idx_mc_fragment_b   ON memory_contradictions (fragment_b_id);
CREATE INDEX IF NOT EXISTS idx_mc_status       ON memory_contradictions (status);
CREATE INDEX IF NOT EXISTS idx_mc_conflict_type ON memory_contradictions (conflict_type);

CREATE TRIGGER trg_mc_updated_at
    BEFORE UPDATE ON memory_contradictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- MEMORY PROVENANCE
-- Tracks WHERE each memory fragment came from — the full lineage.
-- One fragment can have multiple provenance records if it was synthesized
-- from multiple sources (e.g., RAPTOR consolidation).
-- =============================================================================

CREATE TABLE IF NOT EXISTS memory_provenance (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- The fragment this provenance record belongs to
    fragment_id     UUID        NOT NULL REFERENCES memory_fragments(id) ON DELETE CASCADE,

    -- Source details
    source_type     TEXT        NOT NULL,                        -- 'youtube' | 'pdf' | 'url' | 'text' | 'synthesis'
    source_ref      TEXT        NOT NULL,                        -- URL, file path, or synthesis description
    source_title    TEXT,
    source_author   TEXT,
    source_date     DATE,

    -- Location within source
    chunk_index     INTEGER,                                     -- Which chunk in the source document
    page_number     INTEGER,                                     -- PDF page number (if applicable)
    timestamp_start FLOAT,                                       -- YouTube timestamp start (seconds)
    timestamp_end   FLOAT,                                       -- YouTube timestamp end (seconds)

    -- Context
    context_before  TEXT,                                        -- Text immediately before the extracted fact
    context_after   TEXT,                                        -- Text immediately after the extracted fact

    -- Pipeline tracking
    pipeline_run_id TEXT,
    extraction_model TEXT                                        -- Which LLM model extracted this fact
);

CREATE INDEX IF NOT EXISTS idx_mp_fragment_id   ON memory_provenance (fragment_id);
CREATE INDEX IF NOT EXISTS idx_mp_source_type   ON memory_provenance (source_type);
CREATE INDEX IF NOT EXISTS idx_mp_source_ref    ON memory_provenance (source_ref);
CREATE INDEX IF NOT EXISTS idx_mp_pipeline_run  ON memory_provenance (pipeline_run_id);

-- =============================================================================
-- HELPER FUNCTIONS (for use in pipeline and RPCs)
-- =============================================================================

-- Semantic search function: find the top-k most similar memory fragments
-- Usage: SELECT * FROM search_memory('some query text embedding'::vector, 10, 0.7);
CREATE OR REPLACE FUNCTION search_memory(
    query_embedding vector(1536),
    match_count     INTEGER DEFAULT 10,
    match_threshold FLOAT   DEFAULT 0.75
)
RETURNS TABLE (
    id              UUID,
    content         TEXT,
    source_type     TEXT,
    source_ref      TEXT,
    memory_tier     TEXT,
    similarity      FLOAT,
    decay_score     FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        id,
        content,
        source_type,
        source_ref,
        memory_tier,
        1 - (embedding <=> query_embedding) AS similarity,
        decay_score
    FROM memory_fragments
    WHERE
        is_duplicate = FALSE
        AND 1 - (embedding <=> query_embedding) >= match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Increment access count and update last_accessed timestamp
CREATE OR REPLACE FUNCTION record_access(fragment_id UUID)
RETURNS VOID
LANGUAGE SQL
AS $$
    UPDATE memory_fragments
    SET
        access_count = access_count + 1,
        last_accessed = NOW()
    WHERE id = fragment_id;
$$;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- Enable RLS so the service key bypasses it but anon key cannot read raw facts.
-- =============================================================================

ALTER TABLE memory_fragments       ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_contradictions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_provenance      ENABLE ROW LEVEL SECURITY;

-- Service role has full access (used by pipeline)
CREATE POLICY "service_role_all_fragments" ON memory_fragments
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_contradictions" ON memory_contradictions
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_provenance" ON memory_provenance
    FOR ALL TO service_role USING (true) WITH CHECK (true);
