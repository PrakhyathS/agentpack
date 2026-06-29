# Contributing to agentpack

Thanks for your interest in contributing. The highest-value contributions are **new agent target adapters** — each one is ~60 lines and follows the same pattern.

## Quickstart

```bash
git clone https://github.com/PrakhyathS/agentpack
cd agentpack
pip install typer rich pytest
PYTHONPATH=src python -m pytest tests/ -v
```

## Adding a new target

### 1. Create the adapter

Copy an existing target as a starting point:

```bash
cp src/agentpack/targets/cursor.py src/agentpack/targets/myagent.py
```

Edit it to define your agent's constraints:

```python
# src/agentpack/targets/myagent.py
from .base import BaseTarget, Issue, ValidationResult

class MyAgentTarget(BaseTarget):
    name = "myagent"
    output_filename = "MYAGENT.md"
    recommended_max_chars = 4_000

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.recommended_max_chars:
            issues.append(Issue(
                code="MYAGENT_001",
                message=f"Content is {char_count} chars, above recommended {self.recommended_max_chars}.",
                severity="warning",
                fixable=True,
            ))
            score -= 20

        return ValidationResult(
            target=self.name,
            passed=True,
            issues=issues,
            score=max(0, score),
            char_count=char_count,
        )

    def compile(self, sources: dict[str, str]) -> str:
        parts = [v.strip() for k, v in sorted(sources.items()) if k.endswith(".md")]
        result = "\n\n".join(parts)
        if len(result) > self.recommended_max_chars:
            result = result[: self.recommended_max_chars]
        return result

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        fixed = content
        fixes: list[str] = []
        if any(i.code == "MYAGENT_001" for i in result.issues):
            fixed = fixed[: self.recommended_max_chars]
            fixes.append(f"Trimmed to {self.recommended_max_chars} chars")
        return fixed, fixes
```

### 2. Register it

Add two lines to `src/agentpack/targets/__init__.py`:

```python
from .myagent import MyAgentTarget          # add this import

TARGETS: dict[str, type[BaseTarget]] = {
    ...
    "myagent": MyAgentTarget,               # add this entry
}
```

### 3. Add tests

Add a test block to `tests/test_compiler.py`:

```python
from agentpack.targets.myagent import MyAgentTarget

def test_myagent_passes_clean_content():
    t = MyAgentTarget()
    result = t.validate("- Keep responses concise.\n")
    assert result.passed

def test_myagent_warns_over_limit():
    t = MyAgentTarget()
    result = t.validate("x " * 3000)
    assert any(i.code == "MYAGENT_001" for i in result.warnings)
```

### 4. Update the registry test

In `tests/test_compiler.py`, add `"myagent"` to the set:

```python
def test_all_targets_registered():
    assert set(TARGETS.keys()) == {..., "myagent"}
```

### 5. Open a PR

```bash
git checkout -b target/myagent
git add src/agentpack/targets/myagent.py src/agentpack/targets/__init__.py tests/test_compiler.py
git commit -m "Add myagent target"
gh pr create --title "Add myagent target" --body "Adds support for MyAgent with validated output and auto-fix."
```

CI runs automatically. Once tests pass, it's ready to merge.

## Validation rules

Good validation rules are specific and actionable. Each rule should have:

| Field | Description |
|-------|-------------|
| `code` | Unique identifier e.g. `MYAGENT_001` |
| `message` | What's wrong and why it matters |
| `severity` | `"error"` (blocks use) or `"warning"` (degrades quality) |
| `fixable` | `True` if `fix()` can resolve it automatically |

Only add a rule if you have a source (agent docs, empirical testing, known behaviour). Don't guess.

## Targets we'd love to see

- `windsurf` — Windsurf IDE
- `continue` — Continue.dev
- `cline` — Cline VS Code extension
- `supermaven` — Supermaven
- `tabnine` — Tabnine

## Pull request checklist

- [ ] New target file in `src/agentpack/targets/`
- [ ] Registered in `src/agentpack/targets/__init__.py`
- [ ] At least 2 tests (passes clean content, warns/errors on violation)
- [ ] Registry test updated
- [ ] `PYTHONPATH=src python -m pytest tests/ -v` passes locally

## Reporting issues

Open an issue at [github.com/PrakhyathS/agentpack/issues](https://github.com/PrakhyathS/agentpack/issues) with:
- The target you were using
- The file content that caused the problem
- What you expected vs. what happened

## License

By contributing, you agree your contributions are licensed under MIT.
