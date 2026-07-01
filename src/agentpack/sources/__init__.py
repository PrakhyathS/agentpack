from __future__ import annotations

from pathlib import Path

from ..ingest import CONVERTIBLE_EXTENSIONS, convert_file

_IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", ".cache", "coverage",
}

_TEXT_EXTENSIONS = {".md", ".txt"}
_DEFAULT_EXTENSIONS = _TEXT_EXTENSIONS | CONVERTIBLE_EXTENSIONS


def scan(
    directory: Path, extensions: set[str] | None = None
) -> tuple[dict[str, str], list[str]]:
    """Return ({relative_path: content}, warnings) for all readable files
    under directory. Files with a convertible extension (PDF/Office/etc.)
    are routed through the ingest layer; if that layer can't convert one
    (missing optional dependency, conversion failure), it's skipped and
    noted in `warnings` rather than silently dropped."""
    exts = extensions or _DEFAULT_EXTENSIONS
    sources: dict[str, str] = {}
    warnings: list[str] = []

    for path in sorted(directory.rglob("*")):
        if path.is_dir():
            continue
        if any(part in _IGNORED_DIRS for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix not in exts:
            continue

        rel = str(path.relative_to(directory))

        if suffix in _TEXT_EXTENSIONS:
            try:
                sources[rel] = path.read_text(encoding="utf-8", errors="replace")
            except (OSError, PermissionError):
                pass
            continue

        content, quality_warning = convert_file(path)
        if content is not None:
            # Every target filters sources by a ".md"/".txt" extension —
            # tag converted content as markdown so it's actually included,
            # not silently dropped by every target's own filter.
            sources[f"{rel}.md"] = content
            if quality_warning:
                warnings.append(quality_warning)
        else:
            warnings.append(
                f"skipped {rel} — install agentpack-skills[office] for PDF/Office support"
            )

    return sources, warnings
