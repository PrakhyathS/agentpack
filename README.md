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
pip install agentpack
```

---

## Usage

```bash
# Compile your repo for a specific agent
agentpack compile . --target claude     # → dist/claude/CLAUDE.md
agentpack compile . --target cursor     # → dist/cursor/.cursorrules
agentpack compile . --target chatgpt    # → dist/chatgpt/custom_instructions.md
agentpack compile . --target gemini     # → dist/gemini/GEMINI.md
agentpack compile . --target copilot    # → dist/copilot/.github/copilot-instructions.md
agentpack compile . --target codex      # → dist/codex/AGENTS.md
agentpack compile . --target aider      # → dist/aider/.aider.md

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

| Target | Output file | Key constraint | Notes |
|--------|-------------|----------------|-------|
| `claude` | `CLAUDE.md` | 8 000 chars recommended | Anthropic Claude Code |
| `cursor` | `.cursorrules` | 10 000 chars recommended | Cursor IDE |
| `chatgpt` | `custom_instructions.md` | **1 500 chars hard limit** | OpenAI ChatGPT |
| `gemini` | `GEMINI.md` | 5 000 chars recommended | Google Gemini |
| `copilot` | `.github/copilot-instructions.md` | **8 000 chars hard limit** | GitHub Copilot |
| `codex` | `AGENTS.md` | 5 000 chars recommended | OpenAI Codex CLI |
| `aider` | `.aider.md` | 3 000 chars recommended | aider-chat |

Version pinning syntax is supported and reserved for future per-version adapters:
`--target claude@5`

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
