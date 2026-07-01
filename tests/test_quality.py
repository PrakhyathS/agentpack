from pathlib import Path

from agentpack import sources as sources_module
from agentpack.ingest.quality import build_warning, detect_math_degradation
from agentpack.sources import scan


def test_detects_math_degraded_text():
    text = (
        "Stirling's Formula: √ (cid:18) (cid:18) (cid:19)(cid:19) "
        "(cid:16)n(cid:17)n 1 1 n! = 2πn 1+ +O e 12n n2"
    )
    assert detect_math_degradation(text)


def test_does_not_flag_normal_prose():
    text = "This is a completely normal paragraph with no extraction issues at all."
    assert not detect_math_degradation(text)


def test_ignores_single_stray_cid_token():
    # One isolated occurrence isn't enough signal to warn about — avoid
    # noisy false positives on otherwise-clean documents.
    text = "Mostly fine text with one stray (cid:5) artifact."
    assert not detect_math_degradation(text)


def test_build_warning_names_the_file_and_advises_verification():
    warning = build_warning(Path("FormulaSheet.pdf"))
    assert "FormulaSheet.pdf" in warning
    assert "verify" in warning.lower()


def test_scan_surfaces_math_degradation_warning(tmp_path, monkeypatch):
    pdf = tmp_path / "formulas.pdf"
    pdf.write_bytes(b"fake pdf bytes")
    degraded_text = "n! = 2πn (cid:18) (cid:19) (cid:16) (cid:17) (cid:20)"
    monkeypatch.setattr(
        sources_module, "convert_file", lambda path: (degraded_text, build_warning(path))
    )

    sources, warnings = scan(tmp_path)

    assert "formulas.pdf.md" in sources  # content is still included, not dropped
    assert any("formulas.pdf" in w and "verify" in w.lower() for w in warnings)
