from __future__ import annotations

import re

# A markdown table row: starts and ends with '|'.
_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
# A separator row: every cell is only dashes/colons, e.g. "| --- | :-: |".
_SEP_RE = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")

# Above this fraction of blank cells, a table is almost certainly PDF layout
# noise (justified text split into fake columns), not real tabular data.
_EMPTY_CELL_RATIO_THRESHOLD = 0.25


def _split_cells(line: str) -> list[str]:
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def _is_spurious(all_rows: list[list[str]]) -> bool:
    total = sum(len(row) for row in all_rows)
    if total == 0:
        return True

    empty = sum(1 for row in all_rows for cell in row if not cell)
    if (empty / total) > _EMPTY_CELL_RATIO_THRESHOLD:
        return True

    # A table with only a header + at most one data row is very unlikely to
    # be an intentional table — real ones almost always have 2+ data rows.
    return len(all_rows) <= 2


def flatten_spurious_tables(text: str) -> str:
    """markitdown's PDF backend frequently misdetects justified prose as
    tables — common with LaTeX-generated academic PDFs, where unusual
    character spacing trips up its column-detection heuristic. Detects
    these false positives (many blank filler cells, or a suspiciously
    small row count) and flattens them back into plain sentences. Tables
    with several fully-populated data rows are left untouched as likely
    genuine tabular data."""
    lines = text.splitlines()
    out: list[str] = []
    i, n = 0, len(lines)

    while i < n:
        if _ROW_RE.match(lines[i]) and i + 1 < n and _SEP_RE.match(lines[i + 1]):
            header_cells = _split_cells(lines[i])
            j = i + 2
            data_rows: list[list[str]] = []
            while j < n and _ROW_RE.match(lines[j]) and not _SEP_RE.match(lines[j]):
                data_rows.append(_split_cells(lines[j]))
                j += 1

            all_rows = [header_cells] + data_rows
            if _is_spurious(all_rows):
                flat = " ".join(cell for row in all_rows for cell in row if cell)
                if flat:
                    out.append(flat)
            else:
                out.extend(lines[i:j])

            i = j
        else:
            out.append(lines[i])
            i += 1

    return "\n".join(out)
