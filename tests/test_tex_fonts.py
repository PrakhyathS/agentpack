from agentpack.ingest.tex_fonts import recover_symbol


def test_recovers_verified_cmex10_codes():
    assert recover_symbol("CMEX10", 0) == "("
    assert recover_symbol("CMEX10", 1) == ")"
    assert recover_symbol("CMEX10", 88) == "∑"


def test_recovers_verified_cmmi10_codes():
    assert recover_symbol("CMMI10", 15) == "ϵ"
    assert recover_symbol("CMMI10", 96) == "ℓ"


def test_recovers_verified_cmsy10_codes():
    assert recover_symbol("CMSY10", 48) == "′"
    assert recover_symbol("CMSY10", 104) == "⟨"
    assert recover_symbol("CMSY10", 105) == "⟩"
    assert recover_symbol("CMSY10", 107) == "‖"


def test_size_variants_share_base_encoding():
    # cmmi7/cmsy7 etc. use the identical encoding vector as their 10pt base.
    assert recover_symbol("CMMI7", 96) == recover_symbol("CMMI10", 96)
    assert recover_symbol("CMSY7", 104) == recover_symbol("CMSY10", 104)


def test_unknown_font_returns_none():
    assert recover_symbol("SOMERANDOMFONT10", 0) is None


def test_unverified_code_in_known_font_returns_none():
    # CMEX10 code 16 was never independently verified (mostly delimiter
    # fragments in this font) — must not guess.
    assert recover_symbol("CMEX10", 16) is None


def test_case_insensitive_font_lookup():
    assert recover_symbol("cmmi10", 96) == recover_symbol("CMMI10", 96)
