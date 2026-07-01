from pathlib import Path

from agentpack.ingest.cid_recovery import _apply_substitutions, recover_cid_symbols


def test_substitutes_unambiguous_code():
    text = "n! = 2πn (cid:18) (cid:19)"
    candidates = {18: {"("}, 19: {")"}}
    result = _apply_substitutions(text, candidates)
    assert result == "n! = 2πn ( )"


def test_abstains_on_ambiguous_code():
    # Same code resolved to two different symbols across the document —
    # must not guess which is correct; leave the honest marker in place.
    text = "(cid:96) and (cid:96) again"
    candidates = {96: {"ℓ", "∑"}}
    result = _apply_substitutions(text, candidates)
    assert result == text  # unchanged


def test_only_substitutes_codes_with_candidates():
    text = "some (cid:5) text (cid:6) here"
    candidates = {5: {"α"}}
    result = _apply_substitutions(text, candidates)
    assert result == "some α text (cid:6) here"


def test_recover_cid_symbols_returns_unchanged_when_no_cid_tokens():
    text = "Perfectly normal text, nothing to recover."
    assert recover_cid_symbols(Path("/nonexistent.pdf"), text) == text


def test_recover_cid_symbols_degrades_gracefully_on_bad_path():
    text = "Some text with (cid:18) in it."
    # Path doesn't exist — pdfminer will fail to open it; must not raise.
    result = recover_cid_symbols(Path("/definitely/does/not/exist.pdf"), text)
    assert result == text
