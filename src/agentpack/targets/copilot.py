import re

from .base import BaseTarget, Issue, ValidationResult

# GitHub Copilot reads .github/copilot-instructions.md
# GitHub docs state an 8000 char limit
_HARD_MAX = 8_000


class CopilotTarget(BaseTarget):
    name = "copilot"
    output_filename = ".github/copilot-instructions.md"
    hard_max_chars = _HARD_MAX

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.hard_max_chars:
            over = char_count - self.hard_max_chars
            issues.append(Issue(
                code="COPILOT_001",
                message=(
                    f"Exceeds GitHub Copilot's {self.hard_max_chars}-char limit "
                    f"by {over} chars — content beyond the limit is ignored."
                ),
                severity="error",
                fixable=True,
            ))
            score -= 35

        # Copilot instructions work best as imperative statements
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]
        question_lines = [l for l in lines if l.endswith("?")]
        if len(question_lines) > 2:
            issues.append(Issue(
                code="COPILOT_002",
                message=(
                    "Instructions contain questions. Copilot responds better to "
                    "imperative statements ('Always do X') than questions."
                ),
                severity="warning",
            ))
            score -= 5

        return ValidationResult(
            target=self.name,
            passed=all(i.severity != "error" for i in issues),
            issues=issues,
            score=max(0, score),
            char_count=char_count,
        )

    def compile(self, sources: dict[str, str]) -> str:
        parts: list[str] = []
        for path, body in sorted(sources.items()):
            if path.endswith(".md"):
                parts.append(body.strip())

        result = "\n\n".join(parts)
        if len(result) > self.hard_max_chars:
            result = result[: self.hard_max_chars]
            last_newline = result.rfind("\n")
            if last_newline > self.hard_max_chars * 0.9:
                result = result[:last_newline]
        return result

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        fixes: list[str] = []
        fixed = content
        if any(i.code == "COPILOT_001" for i in result.issues):
            fixed = fixed[: self.hard_max_chars]
            last_newline = fixed.rfind("\n")
            if last_newline > self.hard_max_chars * 0.9:
                fixed = fixed[:last_newline]
            fixes.append(f"Trimmed to {self.hard_max_chars}-char hard limit")
        return fixed, fixes
