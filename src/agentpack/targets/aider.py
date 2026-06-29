from .base import BaseTarget, Issue, ValidationResult

_RECOMMENDED_MAX = 3_000


class AiderTarget(BaseTarget):
    name = "aider"
    output_filename = ".aider.md"
    recommended_max_chars = _RECOMMENDED_MAX

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.recommended_max_chars:
            issues.append(Issue(
                code="AIDER_001",
                message=(
                    f"Content is {char_count} chars, above recommended "
                    f"{self.recommended_max_chars}. Aider loads this on every turn."
                ),
                severity="warning",
                fixable=True,
            ))
            score -= 20

        # Aider works best with explicit coding conventions, not background info
        if "## Background" in content or "## About" in content:
            issues.append(Issue(
                code="AIDER_002",
                message=(
                    "Background/About sections waste context. "
                    "Aider only benefits from actionable coding conventions."
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
        parts: list[str] = []
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
        if any(i.code == "AIDER_001" for i in result.issues):
            fixed = fixed[: self.recommended_max_chars]
            fixes.append(f"Trimmed to {self.recommended_max_chars} chars")
        return fixed, fixes
