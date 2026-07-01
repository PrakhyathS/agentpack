from __future__ import annotations

from pathlib import Path

from . import office

CONVERTIBLE_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls",
    ".html", ".csv", ".json", ".xml", ".epub",
}


def convert_file(path: Path) -> tuple[str | None, str | None]:
    """Dispatch a file to the right ingestor. Returns (content, quality_warning).
    content is None if unconvertible or if the required optional dependency
    isn't installed — callers should treat None as "skip this file", never
    as an error. quality_warning is set alongside real content when
    extraction is likely degraded but still usable."""
    if path.suffix.lower() in CONVERTIBLE_EXTENSIONS:
        return office.convert(path)
    return None, None
