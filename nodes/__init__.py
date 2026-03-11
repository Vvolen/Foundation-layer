"""
NickOS Foundation-layer — Pipeline Nodes Package

The 8-node ingestion pipeline:
    Node 1: extractor       — source → raw_text
    Node 2: cleaner         — raw_text → clean_text
    Node 3: chunker         — clean_text → List[Chunk]
    Node 4: fact_extractor  — List[Chunk] → List[AtomicFact]
    Node 5: deduplicator    — List[AtomicFact] → dedup decisions
    Node 6: router          — List[AtomicFact] → memory-tier routing
    Node 7: supabase_writer — write fragments to Supabase
    Node 8: notion_writer + reporter — notify and summarize

Import conventions:
    from nodes.extractor import extract
    from nodes.cleaner import clean
    etc.
"""
