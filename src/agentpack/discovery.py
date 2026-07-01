from pathlib import Path

_MARKER_START = "<!-- agentpack:discovery-contract -->"
_MARKER_END = "<!-- /agentpack:discovery-contract -->"


def _build_block(skill_output_dir: Path) -> str:
    return (
        f"{_MARKER_START}\n"
        "## Compiled knowledge (agentpack)\n"
        f"- Compiled skill lives in `{skill_output_dir}/` (SKILL.md + references/).\n"
        "- When answering questions about this project's docs, notes, PDFs, or\n"
        f"  slides, check `{skill_output_dir}/SKILL.md` FIRST — only fall back to\n"
        "  scanning raw source files if the compiled skill doesn't cover it.\n"
        f"{_MARKER_END}"
    )


def sync_claude_md(source_dir: Path, skill_output_dir: Path) -> None:
    """Insert or idempotently replace a short discovery-contract block in the
    project's own CLAUDE.md, pointing at the compiled skill package. Creates
    CLAUDE.md if it doesn't exist. Never touches content outside the marked
    block on repeat calls."""
    claude_md = source_dir / "CLAUDE.md"
    try:
        display_path = skill_output_dir.relative_to(source_dir)
    except ValueError:
        display_path = skill_output_dir
    block = _build_block(display_path)

    if not claude_md.exists():
        claude_md.write_text(block + "\n", encoding="utf-8")
        return

    existing = claude_md.read_text(encoding="utf-8")
    start = existing.find(_MARKER_START)
    end = existing.find(_MARKER_END)

    if start != -1 and end != -1:
        end += len(_MARKER_END)
        updated = existing[:start] + block + existing[end:]
    else:
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        updated = existing + separator + block + "\n"

    claude_md.write_text(updated, encoding="utf-8")
