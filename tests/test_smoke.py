"""
Smoke Tests — NickOS Foundation-layer
======================================
Basic structural tests that validate the repository scaffolding is correct
and the pipeline modules can be imported without errors.

These tests do NOT make real API calls. They verify:
- All node modules exist and are importable
- PipelineState dataclass is correctly structured
- CLI argument parser works
- Node function signatures match the expected interface
- run_ingest.py can be imported without side effects

Run with: pytest tests/test_smoke.py -v
"""

import importlib
import inspect
import sys
from pathlib import Path

import pytest

# Ensure the repo root is on the path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


# =============================================================================
# Module Import Tests
# =============================================================================


class TestModuleImports:
    """Verify all pipeline node modules can be imported."""

    NODE_MODULES = [
        "nodes",
        "nodes.extractor",
        "nodes.cleaner",
        "nodes.chunker",
        "nodes.fact_extractor",
        "nodes.deduplicator",
        "nodes.router",
        "nodes.supabase_writer",
        "nodes.notion_writer",
        "nodes.reporter",
    ]

    @pytest.mark.parametrize("module_name", NODE_MODULES)
    def test_module_importable(self, module_name):
        """Each node module must be importable without error."""
        mod = importlib.import_module(module_name)
        assert mod is not None

    def test_run_ingest_importable(self):
        """run_ingest.py must be importable without side effects."""
        import run_ingest
        assert run_ingest is not None


# =============================================================================
# PipelineState Dataclass Tests
# =============================================================================


class TestPipelineState:
    """Verify the PipelineState dataclass has all required fields."""

    REQUIRED_FIELDS = [
        "run_id",
        "source_type",
        "source_ref",
        "raw_text",
        "clean_text",
        "chunks",
        "facts",
        "dedup_decisions",
        "routed_facts",
        "write_results",
        "report",
        "errors",
        "last_completed_node",
        "checkpoint_path",
    ]

    def test_pipeline_state_has_required_fields(self):
        """PipelineState must have all required fields."""
        from run_ingest import PipelineState
        fields = {f.name for f in PipelineState.__dataclass_fields__.values()}
        for required in self.REQUIRED_FIELDS:
            assert required in fields, f"PipelineState missing required field: {required!r}"

    def test_pipeline_state_instantiation(self):
        """PipelineState must be instantiable with minimal args."""
        from run_ingest import PipelineState
        state = PipelineState(run_id="test-run", source_type="text", source_ref="hello world")
        assert state.run_id == "test-run"
        assert state.source_type == "text"
        assert state.source_ref == "hello world"
        assert state.errors == []
        assert state.last_completed_node == 0
        assert state.raw_text is None

    def test_pipeline_state_error_accumulation(self):
        """Errors list should accumulate entries without halting."""
        from run_ingest import PipelineState
        state = PipelineState(run_id="test-run", source_type="text", source_ref="x")
        state.errors.append({"node": 5, "error": "test error"})
        state.errors.append({"node": 6, "error": "another error"})
        assert len(state.errors) == 2


# =============================================================================
# Node Function Signature Tests
# =============================================================================


class TestNodeSignatures:
    """Verify node functions exist and have the expected signatures."""

    def test_extractor_extract_function_exists(self):
        from nodes.extractor import extract
        sig = inspect.signature(extract)
        params = list(sig.parameters)
        assert "source_type" in params
        assert "source_ref" in params

    def test_cleaner_clean_function_exists(self):
        from nodes.cleaner import clean
        sig = inspect.signature(clean)
        params = list(sig.parameters)
        assert "raw_text" in params

    def test_chunker_chunk_function_exists(self):
        from nodes.chunker import chunk
        sig = inspect.signature(chunk)
        params = list(sig.parameters)
        assert "clean_text" in params

    def test_fact_extractor_function_exists(self):
        from nodes.fact_extractor import extract_facts
        sig = inspect.signature(extract_facts)
        params = list(sig.parameters)
        assert "chunks" in params

    def test_deduplicator_function_exists(self):
        from nodes.deduplicator import deduplicate
        sig = inspect.signature(deduplicate)
        params = list(sig.parameters)
        assert "facts" in params

    def test_router_function_exists(self):
        from nodes.router import route
        sig = inspect.signature(route)
        params = list(sig.parameters)
        assert "facts" in params
        assert "dedup_decisions" in params

    def test_supabase_writer_function_exists(self):
        from nodes.supabase_writer import write_to_supabase
        sig = inspect.signature(write_to_supabase)
        params = list(sig.parameters)
        assert "routed_facts" in params
        assert "pipeline_run_id" in params

    def test_notion_writer_function_exists(self):
        from nodes.notion_writer import write_to_notion
        sig = inspect.signature(write_to_notion)
        params = list(sig.parameters)
        assert "pipeline_run_id" in params

    def test_reporter_function_exists(self):
        from nodes.reporter import generate_report
        sig = inspect.signature(generate_report)
        params = list(sig.parameters)
        assert "state" in params


# =============================================================================
# Dedup Constants Tests
# =============================================================================


class TestDedupConstants:
    """Verify dedup thresholds are at the correct values."""

    def test_dedup_thresholds_are_correct(self):
        from nodes.deduplicator import DEDUP_THRESHOLD_DUPLICATE, DEDUP_THRESHOLD_GRAY_ZONE
        assert DEDUP_THRESHOLD_DUPLICATE == 0.92, "Duplicate threshold must be 0.92"
        assert DEDUP_THRESHOLD_GRAY_ZONE == 0.75, "Gray zone threshold must be 0.75"
        assert DEDUP_THRESHOLD_GRAY_ZONE < DEDUP_THRESHOLD_DUPLICATE

    def test_dedup_action_enum(self):
        from nodes.deduplicator import DedupAction
        assert DedupAction.INSERT == "INSERT"
        assert DedupAction.SKIP == "SKIP"
        assert DedupAction.REVIEW == "REVIEW"


# =============================================================================
# File Structure Tests
# =============================================================================


class TestRepositoryStructure:
    """Verify the required files and directories exist."""

    REQUIRED_FILES = [
        "CLAUDE.md",
        "README.md",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "run_ingest.py",
        "specs/supabase_schema.sql",
        "plans/MASTER_PLAN.md",
        "plans/GITHUB_ECOSYSTEM_GUIDE.md",
        "plans/task_plan.md",
        "plans/findings.md",
        "plans/progress.md",
        ".github/copilot-instructions.md",
        ".github/workflows/test.yml",
        ".github/workflows/ingest-nightly.yml",
        ".github/workflows/evolve.yml",
        ".devcontainer/devcontainer.json",
        "nodes/__init__.py",
        "nodes/extractor.py",
        "nodes/cleaner.py",
        "nodes/chunker.py",
        "nodes/fact_extractor.py",
        "nodes/deduplicator.py",
        "nodes/router.py",
        "nodes/supabase_writer.py",
        "nodes/notion_writer.py",
        "nodes/reporter.py",
        "tests/__init__.py",
    ]

    @pytest.mark.parametrize("filepath", REQUIRED_FILES)
    def test_required_file_exists(self, filepath):
        """Each required file must exist in the repository."""
        full_path = REPO_ROOT / filepath
        assert full_path.exists(), f"Required file missing: {filepath}"
        assert full_path.stat().st_size > 0, f"Required file is empty: {filepath}"

    def test_env_example_has_required_vars(self):
        """`.env.example` must contain all required environment variable keys."""
        env_example = (REPO_ROOT / ".env.example").read_text()
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_SERVICE_KEY",
            "OPENAI_API_KEY",
            "NOTION_API_KEY",
            "NOTION_DATABASE_ID",
        ]
        for var in required_vars:
            assert var in env_example, f".env.example missing required variable: {var}"

    def test_gitignore_excludes_env(self):
        """`.gitignore` must exclude `.env` file."""
        gitignore = (REPO_ROOT / ".gitignore").read_text()
        assert ".env" in gitignore

    def test_gitignore_excludes_venv(self):
        """`.gitignore` must exclude virtual environment directories."""
        gitignore = (REPO_ROOT / ".gitignore").read_text()
        assert ".venv" in gitignore or "venv" in gitignore

    def test_schema_sql_has_required_tables(self):
        """supabase_schema.sql must define all required tables."""
        schema = (REPO_ROOT / "specs/supabase_schema.sql").read_text()
        required_tables = [
            "memory_fragments",
            "memory_contradictions",
            "memory_provenance",
            "schema_versions",
        ]
        for table in required_tables:
            assert table in schema, f"Schema missing table: {table}"

    def test_schema_sql_has_vector_column(self):
        """supabase_schema.sql must define the pgvector embedding column."""
        schema = (REPO_ROOT / "specs/supabase_schema.sql").read_text()
        assert "vector(1536)" in schema, "Schema must have embedding vector(1536) column"

    def test_requirements_has_core_deps(self):
        """requirements.txt must include core dependencies."""
        reqs = (REPO_ROOT / "requirements.txt").read_text()
        required_packages = ["openai", "supabase", "python-dotenv"]
        for pkg in required_packages:
            assert pkg in reqs, f"requirements.txt missing package: {pkg}"
