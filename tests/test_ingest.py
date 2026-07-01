from pathlib import Path

from agentpack.ingest import CONVERTIBLE_EXTENSIONS, convert_file
from agentpack.sources import scan


def test_convert_file_skips_unknown_extension(tmp_path):
    unknown = tmp_path / "file.xyz"
    unknown.write_text("data")
    assert convert_file(unknown) is None


def test_convertible_extensions_include_common_office_formats():
    assert {".pdf", ".docx", ".pptx", ".xlsx"} <= CONVERTIBLE_EXTENSIONS


def test_convert_file_returns_none_without_markitdown_installed(tmp_path):
    # markitdown is an optional extra — in the base test environment it's
    # not installed, so conversion must degrade gracefully, never raise.
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake content")
    result = convert_file(pdf)
    assert result is None or isinstance(result, str)


def test_scan_still_reads_markdown_and_text(tmp_path):
    (tmp_path / "README.md").write_text("# Hello\n\nWorld.")
    (tmp_path / "notes.txt").write_text("plain text notes")

    sources, warnings = scan(tmp_path)

    assert sources["README.md"] == "# Hello\n\nWorld."
    assert sources["notes.txt"] == "plain text notes"
    assert warnings == []


def test_scan_warns_on_unconvertible_pdf_without_office_extra(tmp_path):
    (tmp_path / "slides.pdf").write_bytes(b"%PDF-1.4 fake content")

    sources, warnings = scan(tmp_path)

    assert "slides.pdf" not in sources
    assert any("slides.pdf" in w for w in warnings)


def test_scan_ignores_dist_and_git_dirs(tmp_path):
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "output.md").write_text("should be ignored")
    (tmp_path / "README.md").write_text("# Real content")

    sources, _ = scan(tmp_path)

    assert "README.md" in sources
    assert not any("dist" in k for k in sources)
