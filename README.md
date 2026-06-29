# agentpack

**Agent Knowledge Compiler** — compile your repository's knowledge into optimized packages for any AI agent.

Write your documentation once. Generate validated, agent-specific outputs for Claude, Cursor, ChatGPT, Gemini, and more.

```
Books, code, Markdown, PDFs, slides
           │
           ▼
    agentpack compiler
           │
    ┌──────┴──────┐──────────────┐
    ▼             ▼              ▼
CLAUDE.md    .cursorrules   custom_instructions.md
```

---

## Install

```bash
pip install agentpack
```

Or run directly without installing:

```bash
pipx run agentpack compile . --target claude
```

---

## Usage

```bash
# Compile your repo for a specific agent
agentpack compile . --target claude     # → dist/claude/CLAUDE.md
agentpack compile . --target cursor     # → dist/cursor/.cursorrules
agentpack compile . --target chatgpt    # → dist/chatgpt/custom_instructions.md
agentpack compile . --target gemini     # → dist/gemini/GEMINI.md

# Validate an existing file
agentpack validate CLAUDE.md --target claude

# Auto-fix issues
agentpack fix CLAUDE.md --target claude --inplace

# Score your repo against all targets at once
agentpack score .
```

---

## Validation output

```
┌─ Validation ──────────────────────────────────────────────────┐
│ PASSED  Score: [████████░░] 82/100                            │
│ Target: claude  •  6,234 chars                                │
└───────────────────────────────────────────────────────────────┘

Warnings:
  ⚠ [CLAUDE_001] Content is 6234 chars — above recommended 8000. (fixable)
  ⚠ [CLAUDE_003] Markdown tables detected — may not render in all Claude contexts.
```

---

## Supported targets

| Target | Output file | Key constraint |
|--------|-------------|----------------|
| `claude` | `CLAUDE.md` | 8 000 chars recommended |
| `cursor` | `.cursorrules` | 10 000 chars recommended |
| `chatgpt` | `custom_instructions.md` | **1 500 chars hard limit** |
| `gemini` | `GEMINI.md` | 5 000 chars recommended |

Version pinning is supported: `--target claude@5` (adapters per version coming soon).

---

## Adding a new target

Each target is a single Python file:

```python
# src/agentpack/targets/aider.py
from .base import BaseTarget, Issue, ValidationResult

class AiderTarget(BaseTarget):
    name = "aider"
    output_filename = ".aider.md"
    recommended_max_chars = 6_000

    def validate(self, content: str) -> ValidationResult: ...
    def compile(self, sources: dict[str, str]) -> str: ...
```

Then register it in `targets/__init__.py`:

```python
from .aider import AiderTarget
TARGETS["aider"] = AiderTarget
```

That's it. No changes to the compiler, CLI, or validator.

---

## Why agentpack?

Every AI agent has different constraints — character limits, formatting quirks, supported markdown, frontmatter schemas. Today developers discover these constraints by trial and error, after the agent fails.

`agentpack` makes the constraints explicit, machine-checkable, and auto-fixable — the same way TypeScript makes type errors visible at compile time rather than at runtime.

---

## Contributing

Pull requests welcome. The highest-value contributions are new target adapters for agents not yet supported. See [`src/agentpack/targets/`](src/agentpack/targets/) for examples.

## License

MIT © [PrakhyathS](https://github.com/PrakhyathS)
