from .base import BaseTarget, Issue, ValidationResult

_RECOMMENDED_MAX = 5_000


class GeminiTarget(BaseTarget):
    name = "gemini"
    output_filename = "GEMINI.md"
    recommended_max_chars = _RECOMMENDED_MAX

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.recommended_max_chars:
            issues.append(Issue(
                code="GEMINI_001",
                message=(
                    f"Content is {char_count} chars, above recommended "
                    f"{self.recommended_max_chars} for Gemini context files."
                ),
                severity="warning",
                fixable=True,
            ))
            score -= 15

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
        if any(i.code == "GEMINI_001" for i in result.issues):
            fixed = fixed[: self.recommended_max_chars]
            fixes.append(f"Trimmed to {self.recommended_max_chars} chars")
        return fixed, fixes
