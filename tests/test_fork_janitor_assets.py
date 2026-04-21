"""Tests for fork janitor script/workflow/docs additions."""

from pathlib import Path


def test_script_uses_fork_filter_and_actions_permissions_endpoint() -> None:
    script = Path("scripts/fork-janitor.sh").read_text(encoding="utf-8")
    assert "--fork" in script
    assert "select(.isFork == true)" in script
    assert "actions/permissions" in script
    assert "-f enabled=false" in script


def test_script_defaults_to_dry_run() -> None:
    script = Path("scripts/fork-janitor.sh").read_text(encoding="utf-8")
    assert 'EXECUTE_VALUE="${EXECUTE:-0}"' in script
    assert "[DRY-RUN]" in script


def test_workflow_requires_explicit_pat_and_sets_min_permissions() -> None:
    workflow = Path(".github/workflows/fork-janitor.yml").read_text(encoding="utf-8")
    assert "FORK_JANITOR_PAT" in workflow
    assert "secrets.GITHUB_TOKEN" not in workflow
    assert "permissions:" in workflow
    assert "contents: read" in workflow


def test_workflow_has_dispatch_inputs_and_weekly_cron() -> None:
    workflow = Path(".github/workflows/fork-janitor.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "execute:" in workflow
    assert "default: false" in workflow
    assert "owner:" in workflow
    assert 'cron: "0 6 * * 1"' in workflow


def test_docs_cover_protected_non_fork_repos() -> None:
    doc = Path("docs/ops/fork-janitor.md").read_text(encoding="utf-8")
    assert "fork == false" in doc
    assert "Vvolen/Versailles" in doc
    assert "Vvolen/Foundation-layer" in doc
    assert "Vvolen/MUNCH-CONTEXT-PROTOCOL-MCP-" in doc
