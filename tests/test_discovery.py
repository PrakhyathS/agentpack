from pathlib import Path

from agentpack.discovery import sync_claude_md


def test_creates_claude_md_when_missing(tmp_path):
    sync_claude_md(tmp_path, tmp_path / "dist" / "claude-skill")

    claude_md = tmp_path / "CLAUDE.md"
    assert claude_md.exists()
    content = claude_md.read_text()
    assert "agentpack:discovery-contract" in content
    assert "dist/claude-skill/SKILL.md" in content


def test_appends_to_existing_claude_md(tmp_path):
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("# My existing project rules\n\n- Do X.\n- Do Y.\n")

    sync_claude_md(tmp_path, tmp_path / "dist" / "claude-skill")

    content = claude_md.read_text()
    assert "My existing project rules" in content
    assert "Do X." in content
    assert "agentpack:discovery-contract" in content


def test_idempotent_no_duplication_on_repeat_calls(tmp_path):
    out_dir = tmp_path / "dist" / "claude-skill"
    sync_claude_md(tmp_path, out_dir)
    sync_claude_md(tmp_path, out_dir)
    sync_claude_md(tmp_path, out_dir)

    content = (tmp_path / "CLAUDE.md").read_text()
    assert content.count("agentpack:discovery-contract") == 2  # start + end marker, once each


def test_unrelated_content_untouched_on_repeat_calls(tmp_path):
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("# Hand-written section\n\nImportant notes here.\n")

    sync_claude_md(tmp_path, tmp_path / "dist" / "claude-skill")
    sync_claude_md(tmp_path, tmp_path / "dist" / "claude-skill-v2")

    content = claude_md.read_text()
    assert "Hand-written section" in content
    assert "Important notes here." in content
    # Second call's output dir should replace the first's in the block.
    assert "claude-skill-v2" in content
    assert content.count("agentpack:discovery-contract") == 2
