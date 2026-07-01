from __future__ import annotations

import re
from pathlib import Path

# PDFs using math fonts without a Unicode ToUnicode CMap (common with
# LaTeX documents using Computer Modern / AMS math fonts) extract as raw
# font glyph IDs like "(cid:18)" instead of the actual symbol. Normal text
# never contains this pattern, so its presence is an unambiguous signal —
# no ratio/threshold tuning needed, just a minimum count to ignore a
# single stray false positive.
_CID_TOKEN_RE = re.compile(r"\(cid:\d+\)")
_MIN_CID_TOKENS_TO_FLAG = 3


def detect_math_degradation(text: str) -> bool:
    return len(_CID_TOKEN_RE.findall(text)) >= _MIN_CID_TOKENS_TO_FLAG


def build_warning(path: Path) -> str:
    return (
        f"{path.name} — math/symbol notation may not have extracted correctly "
        "(the PDF's font lacks a Unicode mapping for its math symbols). "
        "Verify formulas against the original document before relying on them."
    )
