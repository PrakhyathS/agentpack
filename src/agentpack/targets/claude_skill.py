from __future__ import annotations

import re
from pathlib import Path

from ..config import SkillConfig
from .base import BaseTarget, Issue, ValidationResult

_BODY_MAX_LINES = 500
_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "project-knowledge"


def _first_paragraph(text: str) -> str:
    para: list[str] = []
    for line in text.strip().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if para:
                break
            continue
        para.append(stripped)
    return " ".join(para) if para else "Compiled project knowledge."


def _derive_name(md_sources: dict[str, str]) -> str:
    readme = md_sources.get("README.md") or md_sources.get("readme.md")
    if readme:
        for line in readme.strip().splitlines():
            if line.strip().startswith("# "):
                return _slugify(line.strip()[2:])
    return "project-knowledge"


def _derive_description(md_sources: dict[str, str]) -> str:
    readme = md_sources.get("README.md") or md_sources.get("readme.md")
    summary = _first_paragraph(readme) if readme else "Compiled project knowledge."
    return (
        f"{summary} Use for any question about this repository's docs, "
        "notes, or reference material — check this SKILL.md and its "
        "references/ FIRST, before scanning raw source files."
    )


def _parse_frontmatter(content: str) -> dict[str, str]:
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


class ClaudeSkillTarget(BaseTarget):
    name = "claude-skill"
    output_filename = "SKILL.md"
    is_package = True

    def compile(self, sources: dict[str, str]) -> str:
        return self.compile_package(sources)["SKILL.md"]

    def compile_package(
        self, sources: dict[str, str], config: SkillConfig | None = None
    ) -> dict[str, str]:
        config = config or SkillConfig()
        md_sources = {
            k: v for k, v in sources.items() if k.endswith(".md") or k.endswith(".txt")
        }

        skill_name = config.name or _derive_name(md_sources)
        description = config.description or _derive_description(md_sources)

        frontmatter_lines = ["---", f"name: {skill_name}", f"description: {description}"]
        if config.license:
            frontmatter_lines.append(f"license: {config.license}")
        frontmatter_lines.append("---")
        frontmatter = "\n".join(frontmatter_lines) + "\n"

        if not md_sources:
            body = "\nNo source documents found.\n"
            return {"SKILL.md": frontmatter + body}

        ordered = sorted(md_sources.keys(), key=lambda x: (x.lower() != "readme.md", x))
        body_lines = ["", "## Reference index", ""]
        package: dict[str, str] = {}
        for path in ordered:
            ref_path = f"references/{path}"
            title = Path(path).stem.replace("-", " ").replace("_", " ").title()
            body_lines.append(f"- **{title}** — see `{ref_path}` for full content.")
            # Verbatim, untruncated — progressive disclosure moves overflow
            # into references/ instead of ever cutting content.
            package[ref_path] = md_sources[path]

        package["SKILL.md"] = frontmatter + "\n".join(body_lines) + "\n"
        return package

    def validate(self, content: str) -> ValidationResult:
        issues: list[Issue] = []
        score = 100
        char_count = len(content)

        fm = _parse_frontmatter(content)
        skill_name = fm.get("name", "")
        description = fm.get("description", "")

        if not skill_name or not description:
            issues.append(Issue(
                code="SKILL_001",
                message="Missing required 'name' and/or 'description' frontmatter.",
                severity="error",
            ))
            score -= 40

        if description and not (40 <= len(description) <= 1024):
            issues.append(Issue(
                code="SKILL_002",
                message=(
                    f"Description is {len(description)} chars — aim for 40-1024 "
                    "chars stating what the skill does and when to use it."
                ),
                severity="warning",
            ))
            score -= 10

        fm_match = _FRONTMATTER_RE.match(content)
        body = content[fm_match.end():] if fm_match else content
        body_lines = body.count("\n") + (1 if body else 0)
        if body_lines > _BODY_MAX_LINES:
            issues.append(Issue(
                code="SKILL_003",
                message=(
                    f"SKILL.md body is {body_lines} lines — above the "
                    f"{_BODY_MAX_LINES}-line convention. Move detail into references/."
                ),
                severity="warning",
                fixable=True,
            ))
            score -= 15

        if skill_name and not _NAME_RE.match(skill_name):
            issues.append(Issue(
                code="SKILL_004",
                message=f"name '{skill_name}' isn't lowercase-hyphenated (e.g. 'my-project').",
                severity="error",
                fixable=True,
            ))
            score -= 20

        return ValidationResult(
            target=self.name,
            passed=all(i.severity != "error" for i in issues),
            issues=issues,
            score=max(0, score),
            char_count=char_count,
        )

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        fixes: list[str] = []
        fixed = content

        if any(i.code == "SKILL_004" for i in result.issues):
            fm_match = re.search(r"(name:\s*)(.+)", fixed)
            if fm_match:
                slugified = _slugify(fm_match.group(2).strip())
                fixed = fixed[: fm_match.start(2)] + slugified + fixed[fm_match.end(2):]
                fixes.append(f"Slugified name to '{slugified}'")

        if any(i.code == "SKILL_003" for i in result.issues):
            fm_match = _FRONTMATTER_RE.match(fixed)
            head = fixed[: fm_match.end()] if fm_match else ""
            body = fixed[fm_match.end():] if fm_match else fixed
            body_lines = body.splitlines()
            if len(body_lines) > _BODY_MAX_LINES:
                trimmed = "\n".join(body_lines[:_BODY_MAX_LINES])
                fixed = (
                    head + trimmed
                    + "\n\n<!-- agentpack: re-run `agentpack compile` to properly "
                    "split overflow into references/ -->\n"
                )
                fixes.append(f"Trimmed body to {_BODY_MAX_LINES} lines")

        return fixed, fixes
