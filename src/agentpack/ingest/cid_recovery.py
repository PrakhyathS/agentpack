from __future__ import annotations

import re
from pathlib import Path

from .tex_fonts import recover_symbol

_CID_RE = re.compile(r"\(cid:(\d+)\)")
_SUBSET_PREFIX_RE = re.compile(r"^[A-Z]{6}\+")


def _apply_substitutions(text: str, candidates: dict[int, set[str]]) -> str:
    """Substitute (cid:N) only when every occurrence of that code across
    the document resolved to the SAME verified symbol. If a code maps to
    more than one distinct symbol (e.g. used by two different fonts with
    conflicting meanings), abstain entirely for that code rather than
    risk a wrong substitution — safety over completeness."""
    for code, symbols in candidates.items():
        if len(symbols) == 1:
            (symbol,) = symbols
            text = text.replace(f"(cid:{code})", symbol)
    return text


def _collect_candidates(path: Path) -> dict[int, set[str]]:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTChar, LTTextContainer

    candidates: dict[int, set[str]] = {}
    for page_layout in extract_pages(str(path)):
        for element in page_layout:
            if not isinstance(element, LTTextContainer):
                continue
            for line in element:
                for char in line:
                    if not isinstance(char, LTChar):
                        continue
                    match = _CID_RE.match(char.get_text())
                    if not match:
                        continue
                    code = int(match.group(1))
                    font = _SUBSET_PREFIX_RE.sub("", char.fontname)
                    symbol = recover_symbol(font, code)
                    if symbol is not None:
                        candidates.setdefault(code, set()).add(symbol)
    return candidates


def recover_cid_symbols(path: Path, text: str) -> str:
    """Attempt to recover correct symbols for "(cid:N)" placeholders in
    already-extracted PDF text, by re-reading the PDF's actual per-
    character font data (lost once markitdown flattens to plain text).
    Returns text unchanged if pdfminer isn't available, the PDF can't be
    re-read, or nothing is verifiably recoverable — never raises."""
    if "(cid:" not in text:
        return text

    try:
        candidates = _collect_candidates(path)
    except Exception:
        return text

    return _apply_substitutions(text, candidates)
