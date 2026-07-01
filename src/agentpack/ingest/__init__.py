from __future__ import annotations

from pathlib import Path

from . import office

CONVERTIBLE_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls",
    ".html", ".csv", ".json", ".xml", ".epub",
}


def convert_file(path: Path) -> str | None:
    """Dispatch a file to the right ingestor. Returns None if unconvertible
    or if the required optional dependency isn't installed — callers should
    treat None as "skip this file", never as an error."""
    if path.suffix.lower() in CONVERTIBLE_EXTENSIONS:
        return office.convert(path)
    return None
