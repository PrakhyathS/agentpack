from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from .cid_recovery import recover_cid_symbols
from .quality import build_warning, detect_math_degradation
from .tables import flatten_spurious_tables

# Below this many non-whitespace characters, a "converted" PDF is treated as
# scanned/image-only rather than genuinely short — triggers the OCR fallback.
_SCANNED_TEXT_THRESHOLD = 50


def convert(path: Path) -> tuple[str | None, str | None]:
    """Convert an office/PDF document to markdown text.

    Returns (content, quality_warning). content is None (never raises) if
    markitdown isn't installed or conversion fails, so a missing optional
    dependency degrades gracefully instead of crashing the whole compile.
    quality_warning is set alongside real content when the extraction is
    likely degraded (e.g. math notation) but still usable — never silently
    hidden.
    """
    try:
        from markitdown import MarkItDown
    except ImportError:
        return None, None

    try:
        text = MarkItDown(enable_plugins=False).convert(str(path)).text_content
    except Exception:
        return None, None

    if path.suffix.lower() == ".pdf":
        if len(text.strip()) < _SCANNED_TEXT_THRESHOLD:
            ocr_text = _try_ocr_fallback(path)
            if ocr_text:
                text = ocr_text
        else:
            text = recover_cid_symbols(path, text)

    text = flatten_spurious_tables(text)
    warning = build_warning(path) if detect_math_degradation(text) else None

    return text, warning


def _try_ocr_fallback(path: Path) -> str | None:
    """Re-run a likely-scanned PDF through ocrmypdf (Tesseract backend)."""
    if shutil.which("ocrmypdf") is None:
        return None

    from markitdown import MarkItDown

    with tempfile.TemporaryDirectory() as tmp:
        out_pdf = Path(tmp) / "ocr.pdf"
        try:
            subprocess.run(
                ["ocrmypdf", str(path), str(out_pdf)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, OSError):
            return None

        try:
            return MarkItDown(enable_plugins=False).convert(str(out_pdf)).text_content
        except Exception:
            return None
