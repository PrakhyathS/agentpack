import pytest

from agentpack.targets.chatgpt import ChatGPTTarget
from agentpack.targets.claude import ClaudeTarget
from agentpack.targets.cursor import CursorTarget
from agentpack.targets.gemini import GeminiTarget
from agentpack.targets import get_target, TARGETS


# ── ClaudeTarget ─────────────────────────────────────────────────────────────

def test_claude_passes_clean_content():
    t = ClaudeTarget()
    result = t.validate("# Rules\n\n- Do this\n- Not that\n")
    assert result.passed
    assert result.score == 100
    assert result.errors == []


def test_claude_warns_over_limit():
    t = ClaudeTarget()
    content = "word " * 2000  # well over 8000 chars
    result = t.validate(content)
    codes = [i.code for i in result.warnings]
    assert "CLAUDE_001" in codes


def test_claude_warns_on_html():
    t = ClaudeTarget()
    result = t.validate("# Title\n\n<b>bold</b>\n")
    codes = [i.code for i in result.warnings]
    assert "CLAUDE_002" in codes


def test_claude_fix_trims_long_content():
    t = ClaudeTarget()
    content = "x " * 5000
    result = t.validate(content)
    fixed, fixes = t.fix(content, result)
    assert len(fixed) <= ClaudeTarget.recommended_max_chars
    assert fixes


# ── ChatGPTTarget ─────────────────────────────────────────────────────────────

def test_chatgpt_passes_within_limit():
    t = ChatGPTTarget()
    result = t.validate("Keep answers concise.")
    assert result.passed
    assert result.score == 100


def test_chatgpt_errors_over_hard_limit():
    t = ChatGPTTarget()
    content = "word " * 400  # ~2000 chars
    result = t.validate(content)
    assert not result.passed
    assert any(i.code == "GPT_001" for i in result.errors)


def test_chatgpt_fix_trims_to_limit():
    t = ChatGPTTarget()
    content = "word " * 400
    result = t.validate(content)
    fixed, fixes = t.fix(content, result)
    assert len(fixed) <= ChatGPTTarget.hard_max_chars
    assert fixes


# ── CursorTarget ──────────────────────────────────────────────────────────────

def test_cursor_always_passes():
    t = CursorTarget()
    result = t.validate("- Always write tests.\n- Use TypeScript.\n")
    assert result.passed


def test_cursor_compiles_markdown():
    t = CursorTarget()
    sources = {"README.md": "# Project\n\n- Do this.\n"}
    out = t.compile(sources)
    assert "Project" in out


# ── GeminiTarget ──────────────────────────────────────────────────────────────

def test_gemini_warns_over_limit():
    t = GeminiTarget()
    content = "text " * 1500
    result = t.validate(content)
    assert any(i.code == "GEMINI_001" for i in result.warnings)


# ── Registry ──────────────────────────────────────────────────────────────────

def test_all_targets_registered():
    assert set(TARGETS.keys()) == {"claude", "cursor", "chatgpt", "gemini"}


def test_get_target_returns_instance():
    t = get_target("claude")
    assert isinstance(t, ClaudeTarget)


def test_get_target_version_pinning_ignored():
    t = get_target("claude@5")
    assert isinstance(t, ClaudeTarget)


def test_get_target_unknown_raises():
    with pytest.raises(ValueError, match="Unknown target"):
        get_target("nonexistent")


# ── compile() smoke test ──────────────────────────────────────────────────────

def test_claude_compile_from_sources():
    t = ClaudeTarget()
    sources = {
        "README.md": "# My Project\n\nThis is a test project.",
        "docs/rules.md": "# Rules\n\n- Always test your code.",
    }
    out = t.compile(sources)
    assert "My Project" in out
    assert "Rules" in out
