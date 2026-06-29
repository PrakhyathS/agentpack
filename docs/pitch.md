# agentpack — Anthropic API Credits Pitch

## TL;DR

`agentpack` is an open-source Agent Knowledge Compiler that turns any repository into
validated, Claude-ready knowledge packages. Claude is the first-class target.
I'm requesting API credits to test and refine compilation quality at scale.

---

## The problem

Developers spend hours manually writing CLAUDE.md, skills files, and agent instructions.
They discover formatting problems only after the agent fails — wrong character counts,
unsupported markdown, missing frontmatter, duplicate sections.

There is no tool that validates agent context files before they're loaded.

---

## What agentpack does

```bash
pip install agentpack

# Compile any repository into a Claude-ready knowledge package
agentpack compile . --target claude        # → dist/claude/CLAUDE.md

# Validate an existing file before loading it
agentpack validate CLAUDE.md --target claude

# Auto-fix issues
agentpack fix CLAUDE.md --target claude --inplace

# Score your repo against every supported agent at once
agentpack score .
```

Sample validation output:

```
┌─ Validation ───────────────────────────────────────────────────┐
│ PASSED  Score: [████████░░] 82/100                             │
│ Target: claude  •  6,234 chars                                 │
└────────────────────────────────────────────────────────────────┘

Warnings:
  ⚠ [CLAUDE_001] Content is 6234 chars — above recommended 8000.  (fixable)
  ⚠ [CLAUDE_003] Markdown tables detected — may not render in all Claude contexts.
```

---

## Architecture

The compiler is data-driven and plugin-based. Each agent is a single file:

```
src/agentpack/targets/
├── base.py       ← BaseTarget ABC shared by all adapters
├── claude.py     ← CLAUDE.md, 8 000-char recommended, 5 validation rules
├── cursor.py     ← .cursorrules, 10 000-char recommended
├── chatgpt.py    ← custom_instructions.md, 1 500-char hard limit
├── gemini.py     ← GEMINI.md, 5 000-char recommended
├── copilot.py    ← .github/copilot-instructions.md, 8 000-char hard limit
├── codex.py      ← AGENTS.md for OpenAI Codex CLI
└── aider.py      ← .aider.md, 3 000-char recommended
```

When Anthropic updates its recommendations, only `claude.py` changes — not every user's repo.
This is the same separation TypeScript gives between source code and compilation targets.

---

## Why Claude is the first-class target

- The Claude adapter has the most validation rules (5 vs 1–2 for other targets)
- CLAUDE.md is the output format most developers ask about
- The project was designed specifically to reduce friction for developers building with Claude Code
- The pitch, README, and CLI examples all feature Claude first

---

## Current state

- **Repo**: https://github.com/PrakhyathS/agentpack (MIT, public)
- **7 targets**: claude, cursor, chatgpt, gemini, copilot, codex, aider
- **25+ tests**, all passing
- **CI**: GitHub Actions runs tests on Python 3.10/3.11/3.12 on every push
- **PyPI publish workflow**: ready, triggered on version tags

---

## The ask

**API credits** to test compilation quality at scale across real-world repositories.

Specifically, I want to use the API to:
1. Run the compiled CLAUDE.md files through Claude and measure how well it incorporates them
2. Compare output quality before and after agentpack compilation
3. Build a benchmark dataset of before/after examples (open-sourced)

This is research that directly benefits the Claude developer ecosystem.

---

## Where to reach Anthropic

- Developer support: https://support.anthropic.com (submit under "Research / API credits")
- Anthropic research grants: https://www.anthropic.com/research
- Developer Discord: search "Anthropic Discord" — staff are active there
- X/Twitter: @AnthropicAI — a short demo thread with the repo link works well

---

## Pitch template (email / Discord DM)

> **Subject: API credits request — open-source Agent Knowledge Compiler**
>
> I'm building **agentpack** (https://github.com/PrakhyathS/agentpack), an open-source
> compiler that transforms repositories into validated, agent-specific knowledge packages.
>
> Claude is the first-class target. The compiler validates CLAUDE.md files against
> Claude's documented conventions — character limits, markdown support, duplicate sections,
> HTML — and auto-fixes violations before developers discover them through trial and error.
>
> The project is MIT-licensed, has 7 supported agent targets, 25+ tests, and CI on GitHub.
> I'm requesting API credits to benchmark compilation quality: measure how much better
> Claude performs when given an agentpack-compiled context vs. an uncompiled one, and
> publish the benchmark dataset open-source.
>
> GitHub: https://github.com/PrakhyathS/agentpack
>
> Thank you.
