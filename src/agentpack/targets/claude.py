import re
from pathlib import Path

from .base import BaseTarget, Issue, ValidationResult

# Claude Code CLAUDE.md constraints based on documented best practices
_RECOMMENDED_MAX = 8_000   # beyond this, context overhead grows
_SKILL_MAX = 950            # individual skill file limit (Claude Code docs)


class ClaudeTarget(BaseTarget):
    name = "claude"
    output_filename = "CLAUDE.md"
    recommended_max_chars = _RECOMMENDED_MAX
    skill_max_chars = _SKILL_MAX

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        if char_count > self.recommended_max_chars:
            issues.append(Issue(
                code="CLAUDE_001",
                message=(
                    f"Content is {char_count} chars, above the recommended "
                    f"{self.recommended_max_chars}. Context overhead may degrade performance."
                ),
                severity="warning",
                fixable=True,
            ))
            score -= 15

        if re.search(r"<[a-zA-Z][^>]*>", content):
            issues.append(Issue(
                code="CLAUDE_002",
                message="HTML tags detected — Claude renders these as literal text, not HTML.",
                severity="warning",
            ))
            score -= 10

        if re.search(r"^\|.+\|", content, re.MULTILINE):
            issues.append(Issue(
                code="CLAUDE_003",
                message="Markdown tables detected — may not render in all Claude contexts.",
                severity="warning",
            ))
            score -= 5

        headers = re.findall(r"^#{1,3} (.+)$", content, re.MULTILINE)
        seen: set[str] = set()
        for h in headers:
            key = h.lower().strip()
            if key in seen:
                issues.append(Issue(
                    code="CLAUDE_004",
                    message=f"Duplicate section '## {h}' — consider merging.",
                    severity="warning",
                ))
                score -= 10
            seen.add(key)

        # Detect sections with no body text
        empty = re.findall(r"^(#{1,3} .+)\n+(?=#{1,3} |\Z)", content, re.MULTILINE)
        if empty:
            issues.append(Issue(
                code="CLAUDE_005",
                message=f"Empty sections: {', '.join(empty[:3])}. Remove or fill them.",
                severity="warning",
                fixable=True,
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
        md = {k: v for k, v in sources.items() if k.endswith(".md")}
        if not md:
            return "# Project Knowledge\n\nNo markdown sources found.\n"

        # README first, then alphabetical
        ordered = sorted(md.keys(), key=lambda x: (x.lower() != "readme.md", x))
        sections: list[str] = []
        for path in ordered:
            title = Path(path).stem.replace("-", " ").replace("_", " ").title()
            sections.append(f"## {title}\n\n{md[path].strip()}")

        result = "\n\n---\n\n".join(sections)

        if len(result) > self.recommended_max_chars:
            result = result[: self.recommended_max_chars]
            result = result[: result.rfind("\n")]
            result += "\n\n<!-- agentpack: content trimmed to recommended limit -->"

        return result

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        fixes: list[str] = []
        fixed = content

        if any(i.code == "CLAUDE_005" for i in result.issues):
            fixed = re.sub(
                r"(^#{1,3} .+$\n)\n+(^#{1,3})", r"\1\2", fixed, flags=re.MULTILINE
            )
            fixes.append("Collapsed empty sections")

        if any(i.code == "CLAUDE_001" for i in result.issues):
            fixed = fixed[: self.recommended_max_chars]
            fixed = fixed[: fixed.rfind("\n")]
            fixes.append(f"Trimmed to {self.recommended_max_chars} chars")

        return fixed, fixes
