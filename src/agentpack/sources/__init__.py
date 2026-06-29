from pathlib import Path

_IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", ".cache", "coverage",
}

_DEFAULT_EXTENSIONS = {".md", ".txt"}


def scan(directory: Path, extensions: set[str] | None = None) -> dict[str, str]:
    """Return {relative_path: content} for all readable files under directory."""
    exts = extensions or _DEFAULT_EXTENSIONS
    sources: dict[str, str] = {}

    for path in sorted(directory.rglob("*")):
        if path.is_dir():
            continue
        if any(part in _IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in exts:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            sources[str(path.relative_to(directory))] = content
        except (OSError, PermissionError):
            pass

    return sources
