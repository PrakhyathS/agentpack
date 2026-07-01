# agentpack

[![CI](https://github.com/PrakhyathS/agentpack/actions/workflows/ci.yml/badge.svg)](https://github.com/PrakhyathS/agentpack/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/agentpack-skills)](https://pypi.org/project/agentpack-skills/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

**Agent Knowledge Compiler** — compile your repository's knowledge into optimized,
validated packages for any AI agent.

Write your documentation once. Generate agent-specific outputs for Claude, Cursor,
ChatGPT, Gemini, Copilot, Codex, Aider, and more. Think of it as TypeScript for AI
knowledge: one source, many compatible targets, with validation and auto-fix built in.

```
Books · code · Markdown · docs · slides
              │
              ▼
       agentpack compiler
              │
    ┌─────────┼─────────┬──────────┐
    ▼         ▼         ▼          ▼
CLAUDE.md  .cursorrules  AGENTS.md  custom_instructions.md
```

---

## Install

```bash
pip install agentpack-skills

# Optional extras
pip install "agentpack-skills[office]"  # PDF/DOCX/PPTX/XLSX ingestion
pip install "agentpack-skills[ocr]"     # OCR fallback for scanned PDFs (needs `tesseract-ocr` on PATH)
pip install "agentpack-skills[watch]"   # `agentpack watch` auto-recompile
pip install "agentpack-skills[all]"     # everything
```

---

## Usage

```bash
# Compile your repo for a specific agent
agentpack compile . --target claude        # → dist/claude/CLAUDE.md
agentpack compile . --target claude-skill  # → dist/claude-skill/SKILL.md + references/
agentpack compile . --target cursor        # → dist/cursor/.cursorrules
agentpack compile . --target chatgpt       # → dist/chatgpt/custom_instructions.md
agentpack compile . --target gemini        # → dist/gemini/GEMINI.md
agentpack compile . --target copilot       # → dist/copilot/.github/copilot-instructions.md
agentpack compile . --target codex         # → dist/codex/AGENTS.md
agentpack compile . --target aider         # → dist/aider/.aider.md

# Watch a directory and auto-recompile on every file drop/edit
agentpack watch . --target claude-skill

# Validate an existing file before loading it into an agent
agentpack validate CLAUDE.md --target claude

# Auto-fix issues in place
agentpack fix CLAUDE.md --target claude --inplace

# Score your repo against all targets at once
agentpack score .
```

---

## Validation output

```
┌─ Validation ───────────────────────────────────────────────────┐
│ PASSED  Score: [████████░░] 82/100                             │
│ Target: claude  •  6,234 chars                                 │
└────────────────────────────────────────────────────────────────┘

Warnings:
  ⚠ [CLAUDE_001] Content is 6234 chars — above recommended 8000.  (fixable — run `agentpack fix`)
  ⚠ [CLAUDE_003] Markdown tables detected — may not render in all Claude contexts.
```

---

## Compatibility score

```
agentpack score .

 Agent Compatibility
┌──────────┬──────────────────┬────────┬────────┬──────────┐
│ Target   │ Score            │ Status │ Errors │ Warnings │
├──────────┼──────────────────┼────────┼────────┼──────────┤
│ claude   │ ██████████ 100%  │ Pass   │ 0      │ 0        │
│ cursor   │ ██████████ 100%  │ Pass   │ 0      │ 0        │
│ chatgpt  │ ████████░░ 82%   │ Pass   │ 0      │ 1        │
│ gemini   │ ██████████ 100%  │ Pass   │ 0      │ 0        │
│ copilot  │ ██████████ 100%  │ Pass   │ 0      │ 0        │
│ codex    │ ██████████ 100%  │ Pass   │ 0      │ 0        │
│ aider    │ ██████████ 100%  │ Pass   │ 0      │ 0        │
└──────────┴──────────────────┴────────┴────────┴──────────┘
```

---

## Supported targets

| Target | Output | Key constraint | Notes |
|--------|-------------|----------------|-------|
| `claude` | `CLAUDE.md` (single file) | 8 000 chars recommended | Anthropic Claude Code project memory |
| `claude-skill` | `SKILL.md` + `references/` (package) | frontmatter required, body <500 lines | An actual Claude **Skill** — see below |
| `cursor` | `.cursorrules` | 10 000 chars recommended | Cursor IDE |
| `chatgpt` | `custom_instructions.md` | **1 500 chars hard limit** | OpenAI ChatGPT |
| `gemini` | `GEMINI.md` | 5 000 chars recommended | Google Gemini |
| `copilot` | `.github/copilot-instructions.md` | **8 000 chars hard limit** | GitHub Copilot |
| `codex` | `AGENTS.md` | 5 000 chars recommended | OpenAI Codex CLI |
| `aider` | `.aider.md` | 3 000 chars recommended | aider-chat |

Version pinning syntax is supported and reserved for future per-version adapters:
`--target claude@5`

---

## `claude-skill` — a real Claude Skill, not just a context file

`CLAUDE.md` (the `claude` target) and a Claude **Skill** are different artifacts.
A Skill is a `SKILL.md` + `references/`/`scripts/`/`assets/` package with required
`name`/`description` frontmatter that Claude auto-triggers on. `--target claude-skill`
produces the real thing:

```bash
agentpack compile . --target claude-skill
```

```
dist/claude-skill/
├── SKILL.md              # frontmatter + short body linking to references/
└── references/
    ├── README.md          # full, untruncated original content
    └── docs/rules.md      # full, untruncated original content
```

Overflow never gets truncated — instead of cutting content to fit a size limit
(what the `claude` target does), detail moves into `references/`, which has no
size limit. This is Claude's own progressive-disclosure pattern: frontmatter is
always loaded, `SKILL.md`'s body loads when the skill triggers, and
`references/` loads on demand.

**Name and description** are auto-derived from your `README.md`'s title and
first paragraph. To hand-tune them, add an `agentpack.toml` in your project root:

```toml
[skill]
name = "my-project"
description = "Use when the user asks about X, Y, or Z in this repo."
license = "MIT"
```

### The discovery contract — this is what actually saves tokens

Building `SKILL.md` only helps if a *future* session finds it before burning
tokens re-scanning raw source files. Every `claude-skill` compile automatically
inserts a short block into your project's own `CLAUDE.md` (idempotent — safe to
re-run):

```markdown
<!-- agentpack:discovery-contract -->
## Compiled knowledge (agentpack)
- Compiled skill lives in `dist/claude-skill/` (SKILL.md + references/).
- When answering questions about this project's docs, notes, PDFs, or
  slides, check `dist/claude-skill/SKILL.md` FIRST — only fall back to
  scanning raw source files if the compiled skill doesn't cover it.
<!-- /agentpack:discovery-contract -->
```

Since `CLAUDE.md` is loaded unconditionally at session start, this guarantees
Claude checks the compiled skill before ever reading raw source files —
whether or not the skill's own description happens to trigger first.

---

## Ingesting more than markdown

PDFs, Word docs, PowerPoint decks, and spreadsheets are converted to markdown
automatically (via [markitdown](https://github.com/microsoft/markitdown)) when
you install the `office` extra:

```bash
pip install "agentpack-skills[office]"
agentpack compile . --target claude-skill   # PDFs/DOCX/PPTX/XLSX now included
```

Without the extra installed, unconvertible files are skipped with a clear
warning — never silently dropped:

```
⚠ skipped slides.pdf — install agentpack-skills[office] for PDF/Office support
```

Scanned (image-only) PDFs fall back to OCR via
[ocrmypdf](https://github.com/ocrmypdf/OCRmyPDF)'s Tesseract backend, if the
`ocr` extra and a system `tesseract-ocr` binary are both installed
(`brew install tesseract` / `apt install tesseract-ocr`):

```bash
pip install "agentpack-skills[ocr]"
```

---

## Auto-recompile with `agentpack watch`

```bash
pip install "agentpack-skills[watch]"
agentpack watch . --target claude-skill
```

Watches the source directory and recompiles automatically whenever a file is
added, edited, or removed — debounced so rapid saves collapse into a single
recompile. Foreground command, `Ctrl+C` to stop.

---

## Adding a new target

Each target is a single Python file with three methods:

```python
# src/agentpack/targets/myagent.py
from .base import BaseTarget, Issue, ValidationResult

class MyAgentTarget(BaseTarget):
    name = "myagent"
    output_filename = "MYAGENT.md"
    recommended_max_chars = 4_000

    def validate(self, content: str) -> ValidationResult:
        ...

    def compile(self, sources: dict[str, str]) -> str:
        ...

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        ...
```

Then register it in [`src/agentpack/targets/__init__.py`](src/agentpack/targets/__init__.py):

```python
from .myagent import MyAgentTarget
TARGETS["myagent"] = MyAgentTarget
```

For multi-file/package outputs (like `claude-skill`), set `is_package = True`
and override `compile_package(sources, config) -> dict[str, str]` instead —
see [`src/agentpack/targets/claude_skill.py`](src/agentpack/targets/claude_skill.py)
for a complete example. The default `compile_package()` just wraps `compile()`,
so single-file targets need no changes at all.

No changes needed anywhere else.

---

## Development

```bash
git clone https://github.com/PrakhyathS/agentpack
cd agentpack
pip install typer rich pytest
PYTHONPATH=src python -m pytest tests/ -v
```

---

## Why agentpack?

Every AI agent has different constraints — character limits, markdown support, frontmatter
schemas, formatting expectations. Developers discover these constraints by trial and error,
after the agent has already failed or silently degraded.

`agentpack` makes constraints explicit, machine-checkable, and auto-fixable — the same
way TypeScript catches type errors at compile time rather than at runtime.

When an agent provider updates their recommendations, only the relevant adapter changes.
Your source knowledge stays the same.

---

## Contributing

Pull requests welcome. The highest-value contributions are new target adapters for agents
not yet supported. Each adapter is ~60 lines. See
[`src/agentpack/targets/`](src/agentpack/targets/) for examples.

## License

MIT © [PrakhyathS](https://github.com/PrakhyathS)
