import re
from pathlib import Path

from .base import BaseTarget, Issue, ValidationResult

_RECOMMENDED_MAX = 10_000


class CursorTarget(BaseTarget):
    name = "cursor"
    output_filename = ".cursorrules"
    recommended_max_chars = _RECOMMENDED_MAX

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.recommended_max_chars:
            issues.append(Issue(
                code="CURSOR_001",
                message=(
                    f"Content is {char_count} chars, above the recommended "
                    f"{self.recommended_max_chars}."
                ),
                severity="warning",
                fixable=True,
            ))
            score -= 20

        # Cursor works best with imperative bullet rules, not narrative prose
        lines = [l for l in content.splitlines() if l.strip()]
        bullet_lines = sum(1 for l in lines if l.strip().startswith(("-", "*", "•", ">")))
        if lines and bullet_lines / len(lines) < 0.3:
            issues.append(Issue(
                code="CURSOR_002",
                message=(
                    "Content is mostly prose. Cursor performs better with "
                    "short bullet-point instructions."
                ),
                severity="warning",
            ))
            score -= 10

        return ValidationResult(
            target=self.name,
            passed=True,
            issues=issues,
            score=max(0, score),
            char_count=char_count,
        )

    def compile(self, sources: dict[str, str]) -> str:
        parts = ["# Cursor Rules\n"]
        for path, body in sorted(sources.items()):
            if path.endswith(".md"):
                parts.append(body.strip())

        result = "\n\n".join(parts)
        if len(result) > self.recommended_max_chars:
            result = result[: self.recommended_max_chars]
        return result

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        fixes: list[str] = []
        fixed = content

        if any(i.code == "CURSOR_001" for i in result.issues):
            fixed = fixed[: self.recommended_max_chars]
            fixes.append(f"Trimmed to {self.recommended_max_chars} chars")

        return fixed, fixes
