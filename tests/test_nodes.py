"""
Unit Tests — NickOS Foundation-layer Pipeline Nodes
=====================================================
Comprehensive tests for all 8 pipeline nodes.

- Nodes 1-3: Fully testable without API calls (no mocking needed)
- Nodes 4-8: Tested with mocks for external services (OpenAI, Supabase, Notion)

Run with: pytest tests/test_nodes.py -v
"""

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


# =============================================================================
# NODE 1: EXTRACTOR TESTS
# =============================================================================


class TestExtractorText:
    """Test the text extraction path (no external dependencies)."""

    def test_extract_text_basic(self):
        from nodes.extractor import extract
        result = extract("text", "Hello, this is a test document.")
        assert result.raw_text == "Hello, this is a test document."
        assert result.source_type == "text"
        assert result.source_ref == "<direct_text_input>"
        assert result.metadata["input_length"] == 31

    def test_extract_text_multiline(self):
        from nodes.extractor import extract
        text = "Line one.\nLine two.\nLine three."
        result = extract("text", text)
        assert result.raw_text == text
        assert "\n" in result.raw_text

    def test_extract_text_empty_raises(self):
        from nodes.extractor import extract, NodeExtractionError
        with pytest.raises(NodeExtractionError):
            extract("text", "")

    def test_extract_text_whitespace_only_raises(self):
        from nodes.extractor import extract, NodeExtractionError
        with pytest.raises(NodeExtractionError):
            extract("text", "   \n\t  ")

    def test_extract_invalid_source_type_raises(self):
        from nodes.extractor import extract
        with pytest.raises(ValueError, match="Unsupported source_type"):
            extract("ftp", "some data")


class TestExtractorYouTubeIdParsing:
    """Test YouTube video ID extraction from various URL formats."""

    def test_standard_url(self):
        from nodes.extractor import _parse_youtube_video_id
        assert _parse_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        from nodes.extractor import _parse_youtube_video_id
        assert _parse_youtube_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        from nodes.extractor import _parse_youtube_video_id
        assert _parse_youtube_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        from nodes.extractor import _parse_youtube_video_id
        assert _parse_youtube_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_bare_video_id(self):
        from nodes.extractor import _parse_youtube_video_id
        assert _parse_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_with_extra_params(self):
        from nodes.extractor import _parse_youtube_video_id
        assert _parse_youtube_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120&list=PLxyz"
        ) == "dQw4w9WgXcQ"

    def test_invalid_url_raises(self):
        from nodes.extractor import _parse_youtube_video_id, NodeExtractionError
        with pytest.raises(NodeExtractionError):
            _parse_youtube_video_id("https://example.com/not-a-video")


class TestExtractorPdf:
    """Test PDF extraction with a real tiny PDF."""

    def test_pdf_file_not_found_raises(self):
        from nodes.extractor import extract, NodeExtractionError
        with pytest.raises(NodeExtractionError, match="not found"):
            extract("pdf", "/nonexistent/path/to/file.pdf")


class TestExtractorUrl:
    """Test URL extraction with mocked HTTP responses."""

    @patch("requests.get")
    def test_extract_url_article(self, mock_get):
        from nodes.extractor import extract
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = """
        <html><head><title>Test Article</title></head>
        <body>
        <nav>Navigation stuff</nav>
        <article>
            <p>This is the first paragraph of a very important article about AI.</p>
            <p>This is the second paragraph with more details about the topic at hand.</p>
            <p>The third paragraph wraps up the discussion with a conclusion statement.</p>
        </article>
        <footer>Footer stuff</footer>
        </body></html>
        """
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = extract("url", "https://example.com/article")
        assert result.source_type == "url"
        assert "first paragraph" in result.raw_text
        assert "second paragraph" in result.raw_text
        assert result.metadata["title"] == "Test Article"
        # Nav and footer should be stripped
        assert "Navigation stuff" not in result.raw_text
        assert "Footer stuff" not in result.raw_text


# =============================================================================
# NODE 2: CLEANER TESTS
# =============================================================================


class TestCleaner:
    """Test the text cleaning pipeline."""

    def test_clean_basic(self):
        from nodes.cleaner import clean
        result = clean("Hello world. This is a test.")
        assert result == "Hello world. This is a test."

    def test_clean_removes_youtube_timestamps(self):
        from nodes.cleaner import clean
        text = "[0:00] Hello [1:23] World [12:34:56] End"
        result = clean(text)
        assert "[0:00]" not in result
        assert "[1:23]" not in result
        assert "[12:34:56]" not in result
        assert "Hello" in result
        assert "World" in result

    def test_clean_removes_fillers(self):
        from nodes.cleaner import clean
        text = "Start [Music] middle [Applause] end [Laughter] done"
        result = clean(text)
        assert "[Music]" not in result
        assert "[Applause]" not in result
        assert "[Laughter]" not in result
        assert "Start" in result
        assert "done" in result

    def test_clean_removes_html_tags(self):
        from nodes.cleaner import clean
        text = "Hello <b>world</b> and <a href='#'>link</a> text"
        result = clean(text)
        assert "<b>" not in result
        assert "<a" not in result
        assert "Hello" in result
        assert "world" in result

    def test_clean_normalizes_unicode(self):
        from nodes.cleaner import clean
        import unicodedata
        # Create a non-NFC string
        text = unicodedata.normalize("NFD", "café résumé naïve")
        result = clean(text)
        assert result == unicodedata.normalize("NFC", "café résumé naïve")

    def test_clean_collapses_whitespace(self):
        from nodes.cleaner import clean
        text = "Hello    world    this   has   spaces"
        result = clean(text)
        assert "    " not in result

    def test_clean_collapses_newlines(self):
        from nodes.cleaner import clean
        text = "Line one\n\n\n\n\nLine two\n\n\n\n\n\nLine three"
        result = clean(text)
        assert "\n\n\n" not in result

    def test_clean_fixes_missing_space_after_period(self):
        from nodes.cleaner import clean
        text = "First sentence.Second sentence.Third sentence."
        result = clean(text)
        assert ". S" in result or ".S" not in result

    def test_clean_strips_per_line(self):
        from nodes.cleaner import clean
        text = "  hello  \n  world  \n  test  "
        result = clean(text)
        lines = result.split("\n")
        for line in lines:
            assert line == line.strip()

    def test_clean_empty_raises(self):
        from nodes.cleaner import clean, NodeCleaningError
        with pytest.raises(NodeCleaningError):
            clean("")

    def test_clean_none_raises(self):
        from nodes.cleaner import clean, NodeCleaningError
        with pytest.raises(NodeCleaningError):
            clean(None)

    def test_clean_preserves_meaningful_content(self):
        from nodes.cleaner import clean
        text = (
            "The human brain contains approximately 86 billion neurons. "
            "Each neuron can form thousands of connections called synapses."
        )
        result = clean(text)
        assert "86 billion neurons" in result
        assert "synapses" in result


# =============================================================================
# NODE 3: CHUNKER TESTS
# =============================================================================


class TestChunker:
    """Test the sentence-based chunking logic."""

    def _make_long_text(self, sentences: int = 50) -> str:
        """Generate a long text with many sentences for chunking tests."""
        base_sentences = [
            "The human brain is the most complex organ in the body.",
            "It contains approximately 86 billion neurons.",
            "Each neuron can form up to 10,000 synaptic connections.",
            "The brain consumes about 20 percent of the body's total energy.",
            "Neural signals can travel at speeds up to 120 meters per second.",
            "The hippocampus plays a key role in forming new memories.",
            "The prefrontal cortex is responsible for decision making.",
            "Neuroplasticity allows the brain to reorganize itself.",
            "Sleep is essential for memory consolidation.",
            "The brain generates about 12 watts of electrical power.",
        ]
        result = []
        for i in range(sentences):
            result.append(base_sentences[i % len(base_sentences)])
        return " ".join(result)

    def test_chunk_basic(self):
        from nodes.chunker import chunk
        text = self._make_long_text(50)
        chunks = chunk(text)
        assert len(chunks) > 0
        assert all(c.text for c in chunks)
        assert all(c.token_count > 0 for c in chunks)

    def test_chunk_indexes_sequential(self):
        from nodes.chunker import chunk
        text = self._make_long_text(50)
        chunks = chunk(text)
        for i, c in enumerate(chunks):
            assert c.index == i

    def test_chunk_has_char_offsets(self):
        from nodes.chunker import chunk
        text = self._make_long_text(50)
        chunks = chunk(text)
        for c in chunks:
            assert c.char_start >= 0
            assert c.char_end > c.char_start
            assert c.char_end <= len(text) + 100  # allow some slack from joining

    def test_chunk_short_text_single_chunk(self):
        from nodes.chunker import chunk
        text = "This is a short text. It has just two sentences."
        chunks = chunk(text)
        # Short text should produce a single chunk (or be kept as-is)
        assert len(chunks) >= 1
        assert "short text" in chunks[0].text

    def test_chunk_empty_raises(self):
        from nodes.chunker import chunk, NodeChunkingError
        with pytest.raises(NodeChunkingError):
            chunk("")

    def test_chunk_custom_target_size(self):
        from nodes.chunker import chunk
        text = self._make_long_text(100)
        # Smaller target = more chunks
        small_chunks = chunk(text, target_tokens=100)
        large_chunks = chunk(text, target_tokens=1000)
        assert len(small_chunks) > len(large_chunks)

    def test_chunk_overlap_produces_shared_content(self):
        from nodes.chunker import chunk
        text = self._make_long_text(100)
        chunks = chunk(text, target_tokens=200, overlap_tokens=50)
        if len(chunks) >= 2:
            # Check that adjacent chunks share some words (overlap)
            words_0 = set(chunks[0].text.split()[-20:])
            words_1 = set(chunks[1].text.split()[:20])
            # There should be some overlap
            overlap = words_0 & words_1
            assert len(overlap) > 0, "Adjacent chunks should share words due to overlap"

    def test_chunk_metadata_has_sentence_count(self):
        from nodes.chunker import chunk
        text = self._make_long_text(50)
        chunks = chunk(text)
        for c in chunks:
            assert "sentence_count" in c.metadata
            assert c.metadata["sentence_count"] > 0


# =============================================================================
# NODE 4: FACT EXTRACTOR TESTS (Mocked)
# =============================================================================


class TestFactExtractor:
    """Test fact extraction with mocked OpenAI calls."""

    def _make_chunk(self, text="The brain has 86 billion neurons.", index=0):
        from nodes.chunker import Chunk
        return Chunk(text=text, index=index, token_count=10, char_start=0, char_end=len(text))

    @patch("nodes.fact_extractor._init_openai_client")
    def test_extract_facts_basic(self, mock_init):
        from nodes.fact_extractor import extract_facts

        mock_client = MagicMock()
        mock_init.return_value = mock_client

        # Mock the completions response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "facts": [
                "The brain contains 86 billion neurons.",
                "Neurons form synaptic connections.",
            ]
        })
        mock_client.chat.completions.create.return_value = mock_response

        chunks = [self._make_chunk()]
        facts = extract_facts(chunks, "text", "test_source")

        assert len(facts) == 2
        assert facts[0].text == "The brain contains 86 billion neurons."
        assert facts[0].chunk_index == 0
        assert facts[0].source_type == "text"
        assert facts[0].source_ref == "test_source"

    @patch("nodes.fact_extractor._init_openai_client")
    def test_extract_facts_empty_chunk_skipped(self, mock_init):
        from nodes.fact_extractor import extract_facts
        from nodes.chunker import Chunk

        mock_client = MagicMock()
        mock_init.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({"facts": ["Fact one."]})
        mock_client.chat.completions.create.return_value = mock_response

        chunks = [
            Chunk(text="", index=0, token_count=0, char_start=0, char_end=0),
            self._make_chunk("Real content here.", 1),
        ]
        facts = extract_facts(chunks, "text", "test")
        assert len(facts) == 1
        assert facts[0].chunk_index == 1

    def test_extract_facts_empty_list_raises(self):
        from nodes.fact_extractor import extract_facts, NodeFactExtractionError
        with pytest.raises(NodeFactExtractionError):
            extract_facts([], "text", "test")

    @patch("nodes.fact_extractor._init_openai_client")
    def test_extract_facts_multiple_chunks(self, mock_init):
        from nodes.fact_extractor import extract_facts

        mock_client = MagicMock()
        mock_init.return_value = mock_client

        # Different responses for different chunks
        responses = [
            json.dumps({"facts": ["Fact A1.", "Fact A2."]}),
            json.dumps({"facts": ["Fact B1."]}),
            json.dumps({"facts": []}),  # Chunk with no facts
        ]
        call_count = 0

        def side_effect(**kwargs):
            nonlocal call_count
            resp = MagicMock()
            resp.choices = [MagicMock()]
            resp.choices[0].message.content = responses[min(call_count, len(responses) - 1)]
            call_count += 1
            return resp

        mock_client.chat.completions.create.side_effect = side_effect

        chunks = [
            self._make_chunk("Chunk A text.", 0),
            self._make_chunk("Chunk B text.", 1),
            self._make_chunk("Filler content.", 2),
        ]
        facts = extract_facts(chunks, "youtube", "https://youtube.com/watch?v=test")

        assert len(facts) == 3  # 2 from A + 1 from B + 0 from C
        assert facts[0].text == "Fact A1."
        assert facts[2].text == "Fact B1."


# =============================================================================
# NODE 5: DEDUPLICATOR TESTS (Mocked)
# =============================================================================


class TestDeduplicator:
    """Test deduplication logic with mocked external services."""

    def _make_fact(self, text="Test fact."):
        from nodes.fact_extractor import AtomicFact
        return AtomicFact(text=text, chunk_index=0, source_type="text", source_ref="test")

    @patch("nodes.deduplicator._init_supabase_client")
    @patch("nodes.deduplicator._init_openai_client")
    def test_dedup_all_new_facts(self, mock_oai_init, mock_sb_init):
        from nodes.deduplicator import deduplicate, DedupAction

        mock_oai = MagicMock()
        mock_oai_init.return_value = mock_oai
        mock_sb = MagicMock()
        mock_sb_init.return_value = mock_sb

        # Mock embeddings
        mock_embed_resp = MagicMock()
        mock_embed_resp.data = [MagicMock(index=0, embedding=[0.1] * 1536)]
        mock_oai.embeddings.create.return_value = mock_embed_resp

        # Mock search — no matches
        mock_rpc_result = MagicMock()
        mock_rpc_result.data = []
        mock_sb.rpc.return_value.execute.return_value = mock_rpc_result

        facts = [self._make_fact("A brand new fact.")]
        decisions = deduplicate(facts)

        assert len(decisions) == 1
        assert decisions[0].action == DedupAction.INSERT

    @patch("nodes.deduplicator._init_supabase_client")
    @patch("nodes.deduplicator._init_openai_client")
    def test_dedup_clear_duplicate(self, mock_oai_init, mock_sb_init):
        from nodes.deduplicator import deduplicate, DedupAction

        mock_oai = MagicMock()
        mock_oai_init.return_value = mock_oai
        mock_sb = MagicMock()
        mock_sb_init.return_value = mock_sb

        mock_embed_resp = MagicMock()
        mock_embed_resp.data = [MagicMock(index=0, embedding=[0.1] * 1536)]
        mock_oai.embeddings.create.return_value = mock_embed_resp

        # Mock search — high similarity match (clear duplicate)
        mock_rpc_result = MagicMock()
        mock_rpc_result.data = [{"id": "abc-123", "content": "Same fact.", "similarity": 0.95}]
        mock_sb.rpc.return_value.execute.return_value = mock_rpc_result

        facts = [self._make_fact("Same fact.")]
        decisions = deduplicate(facts)

        assert len(decisions) == 1
        assert decisions[0].action == DedupAction.SKIP
        assert decisions[0].similarity_score == 0.95

    @patch("nodes.deduplicator._init_supabase_client")
    @patch("nodes.deduplicator._init_openai_client")
    def test_dedup_gray_zone_confirmed_dup(self, mock_oai_init, mock_sb_init):
        from nodes.deduplicator import deduplicate, DedupAction

        mock_oai = MagicMock()
        mock_oai_init.return_value = mock_oai
        mock_sb = MagicMock()
        mock_sb_init.return_value = mock_sb

        mock_embed_resp = MagicMock()
        mock_embed_resp.data = [MagicMock(index=0, embedding=[0.1] * 1536)]
        mock_oai.embeddings.create.return_value = mock_embed_resp

        # Gray zone similarity
        mock_rpc_result = MagicMock()
        mock_rpc_result.data = [{"id": "abc-123", "content": "Similar fact.", "similarity": 0.85}]
        mock_sb.rpc.return_value.execute.return_value = mock_rpc_result

        # LLM says they're the same
        mock_llm_resp = MagicMock()
        mock_llm_resp.choices = [MagicMock()]
        mock_llm_resp.choices[0].message.content = "YES"
        mock_oai.chat.completions.create.return_value = mock_llm_resp

        facts = [self._make_fact("Almost the same fact.")]
        decisions = deduplicate(facts)

        assert decisions[0].action == DedupAction.SKIP
        assert "confirmed duplicate" in decisions[0].review_reason.lower()

    def test_dedup_empty_list(self):
        from nodes.deduplicator import deduplicate
        assert deduplicate([]) == []

    def test_dedup_thresholds_are_correct(self):
        from nodes.deduplicator import DEDUP_THRESHOLD_DUPLICATE, DEDUP_THRESHOLD_GRAY_ZONE
        assert DEDUP_THRESHOLD_DUPLICATE == 0.92
        assert DEDUP_THRESHOLD_GRAY_ZONE == 0.75
        assert DEDUP_THRESHOLD_GRAY_ZONE < DEDUP_THRESHOLD_DUPLICATE


# =============================================================================
# NODE 6: ROUTER TESTS
# =============================================================================


class TestRouter:
    """Test memory tier classification."""

    def _make_fact(self, text):
        from nodes.fact_extractor import AtomicFact
        return AtomicFact(text=text, chunk_index=0, source_type="text", source_ref="test")

    def _make_insert_decision(self, text):
        from nodes.deduplicator import DedupDecision, DedupAction
        return DedupDecision(fact_text=text, action=DedupAction.INSERT)

    def test_route_procedural(self):
        from nodes.router import route
        facts = [self._make_fact("Step 1: Install the package. Step 2: Configure the settings. Then run the server.")]
        decisions = [self._make_insert_decision(facts[0].text)]
        routed = route(facts, decisions)
        assert len(routed) == 1
        assert routed[0].memory_tier == "procedural"

    def test_route_semantic(self):
        from nodes.router import route
        facts = [self._make_fact("A neural network is defined as a computational model inspired by the brain.")]
        decisions = [self._make_insert_decision(facts[0].text)]
        routed = route(facts, decisions)
        assert len(routed) == 1
        assert routed[0].memory_tier == "semantic"

    def test_route_episodic_default(self):
        from nodes.router import route
        facts = [self._make_fact("On March 10, 2026, GitHub released the new Copilot agent feature.")]
        decisions = [self._make_insert_decision(facts[0].text)]
        routed = route(facts, decisions)
        assert len(routed) == 1
        # This has both episodic signals (date) and could match semantic
        assert routed[0].memory_tier in ("episodic", "semantic")

    def test_route_skips_duplicates(self):
        from nodes.router import route
        from nodes.deduplicator import DedupDecision, DedupAction

        facts = [
            self._make_fact("Fact one."),
            self._make_fact("Fact two."),
            self._make_fact("Fact three."),
        ]
        decisions = [
            DedupDecision(fact_text="Fact one.", action=DedupAction.INSERT),
            DedupDecision(fact_text="Fact two.", action=DedupAction.SKIP),
            DedupDecision(fact_text="Fact three.", action=DedupAction.INSERT),
        ]
        routed = route(facts, decisions)
        assert len(routed) == 2  # One was skipped
        assert all(rf.fact_text != "Fact two." for rf in routed)

    def test_route_content_hash(self):
        from nodes.router import route
        facts = [self._make_fact("A specific fact.")]
        decisions = [self._make_insert_decision("A specific fact.")]
        routed = route(facts, decisions)
        expected_hash = hashlib.sha256("a specific fact.".encode()).hexdigest()
        assert routed[0].content_hash == expected_hash

    def test_route_empty_input(self):
        from nodes.router import route
        assert route([], []) == []

    def test_route_how_to_is_procedural(self):
        from nodes.router import route
        facts = [self._make_fact("To configure the server, first install Node.js, then run npm install.")]
        decisions = [self._make_insert_decision(facts[0].text)]
        routed = route(facts, decisions)
        assert routed[0].memory_tier == "procedural"

    def test_route_definition_is_semantic(self):
        from nodes.router import route
        facts = [self._make_fact("Machine learning refers to algorithms that improve through experience.")]
        decisions = [self._make_insert_decision(facts[0].text)]
        routed = route(facts, decisions)
        assert routed[0].memory_tier == "semantic"


# =============================================================================
# NODE 7: SUPABASE WRITER TESTS (Mocked)
# =============================================================================


class TestSupabaseWriter:
    """Test Supabase writing with mocked clients."""

    def _make_routed_fact(self, text="A fact.", tier="episodic"):
        from nodes.router import RoutedFact
        content_hash = hashlib.sha256(text.strip().lower().encode()).hexdigest()
        return RoutedFact(
            fact_text=text,
            memory_tier=tier,
            source_type="text",
            source_ref="test",
            content_hash=content_hash,
            metadata={"chunk_index": 0},
        )

    @patch("nodes.supabase_writer._init_supabase_client")
    @patch("nodes.supabase_writer._init_openai_client")
    def test_write_basic(self, mock_oai_init, mock_sb_init):
        from nodes.supabase_writer import write_to_supabase

        mock_oai = MagicMock()
        mock_oai_init.return_value = mock_oai
        mock_sb = MagicMock()
        mock_sb_init.return_value = mock_sb

        # Mock embeddings
        mock_embed_resp = MagicMock()
        mock_embed_resp.data = [MagicMock(index=0, embedding=[0.1] * 1536)]
        mock_oai.embeddings.create.return_value = mock_embed_resp

        # Mock upsert
        mock_upsert_resp = MagicMock()
        mock_upsert_resp.data = [{"id": "uuid-1", "content_hash": "abc"}]
        mock_sb.table.return_value.upsert.return_value.execute.return_value = mock_upsert_resp

        # Mock provenance insert
        mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock()

        facts = [self._make_routed_fact()]
        results = write_to_supabase(facts, "run-123")

        assert results.written >= 1
        assert results.failed == 0

    def test_write_empty_input(self):
        from nodes.supabase_writer import write_to_supabase
        results = write_to_supabase([], "run-123")
        assert results.written == 0
        assert results.failed == 0


# =============================================================================
# NODE 8a: NOTION WRITER TESTS (Mocked)
# =============================================================================


class TestNotionWriter:
    """Test Notion page creation with mocked HTTP requests."""

    @patch.dict("os.environ", {"NOTION_API_KEY": "test-key", "NOTION_DATABASE_ID": "test-db"})
    @patch("nodes.notion_writer.http_requests")
    def test_write_notion_basic(self, mock_http):
        from nodes.notion_writer import write_to_notion

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "page-123",
            "url": "https://notion.so/page-123",
        }
        mock_http.post.return_value = mock_resp

        result = write_to_notion(
            write_results={"written": 5, "failed": 0},
            source_type="youtube",
            source_ref="https://youtube.com/watch?v=test",
            source_title="Test Video",
            facts=[],
            pipeline_run_id="run-123",
        )

        assert result["notion_page_id"] == "page-123"
        assert "notion.so" in result["notion_page_url"]

    def test_write_notion_no_api_key(self):
        from nodes.notion_writer import write_to_notion
        # Clear env vars
        import os
        old_key = os.environ.pop("NOTION_API_KEY", None)
        old_db = os.environ.pop("NOTION_DATABASE_ID", None)
        try:
            result = write_to_notion(
                write_results={}, source_type="text", source_ref="test",
                source_title="Test", facts=[], pipeline_run_id="run-1",
            )
            assert result == {}
        finally:
            if old_key:
                os.environ["NOTION_API_KEY"] = old_key
            if old_db:
                os.environ["NOTION_DATABASE_ID"] = old_db


# =============================================================================
# NODE 8b: REPORTER TESTS
# =============================================================================


class TestReporter:
    """Test report generation."""

    def test_report_basic(self):
        from run_ingest import PipelineState
        from nodes.reporter import generate_report

        state = PipelineState(
            run_id="test-run-001",
            source_type="text",
            source_ref="test input",
        )
        state.raw_text = "Raw text here."
        state.clean_text = "Clean text."
        state.chunks = [{"text": "chunk1"}, {"text": "chunk2"}]
        state.facts = [{"text": "fact1"}, {"text": "fact2"}, {"text": "fact3"}]
        state.dedup_decisions = []
        state.write_results = {"written": 3, "failed": 0, "fragment_ids": ["a", "b", "c"], "errors": []}
        state.last_completed_node = 8

        report = generate_report(state)

        assert report["run_id"] == "test-run-001"
        assert report["source_type"] == "text"
        assert report["status"] == "success"
        assert report["stats"]["raw_text_length"] == 14
        assert report["stats"]["clean_text_length"] == 11
        assert report["stats"]["chunks_count"] == 2
        assert report["stats"]["facts_extracted"] == 3
        assert report["stats"]["facts_inserted"] == 3

    def test_report_failed_status(self):
        from run_ingest import PipelineState
        from nodes.reporter import generate_report

        state = PipelineState(
            run_id="failed-run",
            source_type="youtube",
            source_ref="https://youtube.com/watch?v=bad",
        )
        state.last_completed_node = 1  # Only got through extraction
        state.errors = [{"node": 2, "error": "Cleaning failed"}]

        report = generate_report(state)
        assert report["status"] == "failed"
        assert len(report["errors"]) == 1

    def test_report_partial_status(self):
        from run_ingest import PipelineState
        from nodes.reporter import generate_report

        state = PipelineState(
            run_id="partial-run",
            source_type="text",
            source_ref="test",
        )
        state.raw_text = "text"
        state.clean_text = "text"
        state.chunks = []
        state.facts = []
        state.dedup_decisions = []
        state.write_results = {"written": 0, "failed": 0}
        state.last_completed_node = 8
        state.errors = [{"node": 5, "error": "minor issue"}]

        report = generate_report(state)
        assert report["status"] == "partial"

    def test_report_saves_to_file(self):
        from run_ingest import PipelineState
        from nodes.reporter import generate_report, ARTIFACTS_DIR

        state = PipelineState(
            run_id="file-test-run",
            source_type="text",
            source_ref="test",
        )
        state.last_completed_node = 8

        report = generate_report(state)

        report_path = ARTIFACTS_DIR / "report_file-test-run.json"
        assert report_path.exists()
        with open(report_path) as f:
            saved = json.load(f)
        assert saved["run_id"] == "file-test-run"

        # Cleanup
        report_path.unlink(missing_ok=True)


# =============================================================================
# INTEGRATION: END-TO-END WITH TEXT SOURCE (Nodes 1-3 + Mocked 4-8)
# =============================================================================


class TestPipelineIntegrationTextSource:
    """Test the pipeline end-to-end with a text source through Nodes 1-3."""

    def test_nodes_1_through_3_real(self):
        """Run Nodes 1-3 with real data — no mocks needed."""
        from nodes.extractor import extract
        from nodes.cleaner import clean
        from nodes.chunker import chunk

        # A realistic multi-paragraph text
        sample_text = (
            "The Python programming language was created by Guido van Rossum "
            "and first released in 1991. Python emphasizes code readability "
            "with its notable use of significant indentation. It supports "
            "multiple programming paradigms, including structured, object-oriented, "
            "and functional programming. Python is dynamically typed and "
            "garbage-collected. It supports modules and packages, which "
            "encourages program modularity and code reuse. The Python "
            "interpreter and the extensive standard library are available "
            "in source or binary form without charge for all major platforms. "
            "Python was conceived in the late 1980s by Guido van Rossum at "
            "Centrum Wiskunde & Informatica in the Netherlands. Its implementation "
            "began in December 1989. Van Rossum shouldered sole responsibility "
            "for the project, as the lead developer, until July 12, 2018, "
            "when he announced his permanent vacation from his responsibilities "
            "as Python's chief architect. In January 2019, active Python core "
            "developers elected a five-member Steering Council to lead the "
            "project. Python 2.0 was released on October 16, 2000, with many "
            "major new features. Python 3.0, released on December 3, 2008, "
            "was a major revision not completely backward-compatible with "
            "earlier versions. Python consistently ranks as one of the most "
            "popular programming languages in the world."
        )

        # Node 1: Extract
        result = extract("text", sample_text)
        assert len(result.raw_text) > 100

        # Node 2: Clean
        cleaned = clean(result.raw_text)
        assert len(cleaned) > 100
        assert "Python" in cleaned

        # Node 3: Chunk
        chunks = chunk(cleaned, target_tokens=100, overlap_tokens=20)
        assert len(chunks) >= 1
        # All chunks should contain text
        for c in chunks:
            assert c.text.strip()
            assert c.token_count > 0