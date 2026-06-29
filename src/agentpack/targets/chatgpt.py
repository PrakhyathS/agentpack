from .base import BaseTarget, Issue, ValidationResult

# ChatGPT custom instructions hard limit (enforced by the UI)
_HARD_MAX = 1_500


class ChatGPTTarget(BaseTarget):
    name = "chatgpt"
    output_filename = "custom_instructions.md"
    hard_max_chars = _HARD_MAX

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.hard_max_chars:
            over = char_count - self.hard_max_chars
            issues.append(Issue(
                code="GPT_001",
                message=(
                    f"Exceeds ChatGPT's hard {self.hard_max_chars}-char limit "
                    f"by {over} chars — content will be silently truncated."
                ),
                severity="error",
                fixable=True,
            ))
            score -= 40

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
            # Avoid cutting mid-word
            last_space = result.rfind(" ")
            if last_space > self.hard_max_chars * 0.9:
                result = result[:last_space]

        return result

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        fixes: list[str] = []
        fixed = content

        if any(i.code == "GPT_001" for i in result.issues):
            fixed = fixed[: self.hard_max_chars]
            last_space = fixed.rfind(" ")
            if last_space > self.hard_max_chars * 0.9:
                fixed = fixed[:last_space]
            fixes.append(f"Trimmed to {self.hard_max_chars}-char hard limit")

        return fixed, fixes
