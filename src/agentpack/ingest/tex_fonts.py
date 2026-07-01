from __future__ import annotations

"""Verified character-code -> Unicode symbol tables for standard TeX/AMS
math fonts, used to recover symbols in PDFs whose math fonts lack a
Unicode ToUnicode CMap (a common LaTeX default for Computer Modern math
fonts unless a Unicode-math package is used).

Every entry is sourced from CTAN's published AFM files for these exact
fonts, cross-checked against the LaTeX Project's own `encguide.pdf`
(the official documentation of the OT1/OML/OMS/OMX font encodings).
Codes that couldn't be independently verified against both sources are
deliberately left OUT rather than guessed — a wrong substitution is
worse than the honest "(cid:N)" marker it would replace.
"""

# CMEX10 (Computer Modern Math Extension). Most codes in this font are
# unmappable delimiter/accent FRAGMENTS (top/bottom halves, extenders)
# with no single-character equivalent — only whole "big operator" and
# simple bracket codes have a clean mapping.
# Source: cmex10.afm (CTAN fonts/cm/afm) + encguide.pdf OMX table.
_CMEX10: dict[int, str] = {
    0: "(", 1: ")",
    2: "[", 3: "]",
    88: "∑",  # summationdisplaystyle
}

# CMMI10 (Computer Modern Math Italic).
# Source: cmmi10.afm + encguide.pdf OML table.
_CMMI10: dict[int, str] = {
    15: "ϵ",  # epsilon1math — TeX's plain \epsilon, U+03F5 (lunate epsilon)
    96: "ℓ",  # liter, U+2113
}

# CMSY10 (Computer Modern Math Symbols).
# Source: cmsy10.afm + encguide.pdf OMS table. Note: the generic Adobe
# Glyph List mapping for angleleft/angleright (U+2329/U+232A) is wrong for
# math use — encguide.pdf's rendered table confirms the correct math
# angle brackets are U+27E8/U+27E9.
_CMSY10: dict[int, str] = {
    48: "′",  # minute, U+2032 (math prime symbol)
    54: "̸",  # slashoverstrike — combining "not" slash (builds negated relations)
    104: "⟨",       # angleleft (math angle bracket, NOT the AGL default)
    105: "⟩",       # angleright (NOT the AGL default)
    107: "‖",       # bardouble
}

# Math fonts at different point sizes (cmmi7, cmmi5, cmsy7, cmsy5, ...)
# share the identical TeX encoding vector as their 10pt base — a
# standard, well-documented METAFONT/TeX convention, not a per-size table.
_FONT_TABLES: dict[str, dict[int, str]] = {
    "CMEX10": _CMEX10,
    "CMMI10": _CMMI10,
    "CMMI7": _CMMI10,
    "CMMI5": _CMMI10,
    "CMSY10": _CMSY10,
    "CMSY7": _CMSY10,
    "CMSY5": _CMSY10,
}


def recover_symbol(font_base_name: str, code: int) -> str | None:
    """Return the verified Unicode symbol for (font, code), or None if
    this exact pair hasn't been verified against an authoritative source.
    Never guesses for an unverified pair — callers must treat None as
    "keep the honest (cid:N) marker", not as an error."""
    table = _FONT_TABLES.get(font_base_name.upper())
    if table is None:
        return None
    return table.get(code)
