from pathlib import Path

from agentpack import sources as sources_module
from agentpack.ingest import CONVERTIBLE_EXTENSIONS, convert_file
from agentpack.sources import scan
from agentpack.targets.claude import ClaudeTarget
from agentpack.targets.claude_skill import ClaudeSkillTarget
from agentpack.targets.cursor import CursorTarget


def test_convert_file_skips_unknown_extension(tmp_path):
    unknown = tmp_path / "file.xyz"
    unknown.write_text("data")
    assert convert_file(unknown) == (None, None)


def test_convertible_extensions_include_common_office_formats():
    assert {".pdf", ".docx", ".pptx", ".xlsx"} <= CONVERTIBLE_EXTENSIONS


def test_convert_file_returns_none_without_markitdown_installed(tmp_path):
    # markitdown is an optional extra — in the base test environment it's
    # not installed, so conversion must degrade gracefully, never raise.
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake content")
    content, warning = convert_file(pdf)
    assert content is None or isinstance(content, str)
    assert warning is None or isinstance(warning, str)


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


# ── Regression: converted content must actually reach target output ──────────
#
# scan() successfully converting a PDF/PPTX/DOCX is not enough — every target
# filters its input by file extension (".md"/".txt"), so a converted file
# stored under its ORIGINAL extension (e.g. "slides.pptx") was silently
# dropped by every single target. Fixed by tagging converted content with a
# ".md" suffix in scan(); these tests pin that behavior so it can't regress.

def test_scan_tags_converted_content_with_md_suffix(tmp_path, monkeypatch):
    pptx = tmp_path / "slides.pptx"
    pptx.write_bytes(b"fake pptx bytes")
    monkeypatch.setattr(
        sources_module, "convert_file", lambda path: ("# Slide 1\n\nHello from slides.", None)
    )

    sources, warnings = scan(tmp_path)

    assert "slides.pptx.md" in sources
    assert sources["slides.pptx.md"] == "# Slide 1\n\nHello from slides."
    assert warnings == []


def test_converted_pptx_content_reaches_claude_skill_output(tmp_path, monkeypatch):
    pptx = tmp_path / "slides.pptx"
    pptx.write_bytes(b"fake pptx bytes")
    monkeypatch.setattr(
        sources_module, "convert_file", lambda path: ("# Slide 1\n\nImportant deck content.", None)
    )

    sources, _ = scan(tmp_path)
    package = ClaudeSkillTarget().compile_package(sources)

    assert "references/slides.pptx.md" in package
    assert "Important deck content." in package["references/slides.pptx.md"]
    assert "Important deck content." not in package["SKILL.md"]  # moved to references, not inlined


def test_converted_pdf_content_reaches_claude_md_output(tmp_path, monkeypatch):
    pdf = tmp_path / "handbook.pdf"
    pdf.write_bytes(b"fake pdf bytes")
    monkeypatch.setattr(
        sources_module, "convert_file", lambda path: ("# Handbook\n\nOnboarding steps here.", None)
    )

    sources, _ = scan(tmp_path)
    content = ClaudeTarget().compile(sources)

    assert "Onboarding steps here." in content


def test_converted_docx_content_reaches_cursor_output(tmp_path, monkeypatch):
    docx = tmp_path / "notes.docx"
    docx.write_bytes(b"fake docx bytes")
    monkeypatch.setattr(
        sources_module, "convert_file", lambda path: ("# Notes\n\nMeeting takeaways here.", None)
    )

    sources, _ = scan(tmp_path)
    content = CursorTarget().compile(sources)

    assert "Meeting takeaways here." in content
