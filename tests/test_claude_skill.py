from agentpack.config import SkillConfig
from agentpack.targets.claude_skill import ClaudeSkillTarget


def test_is_package_target():
    assert ClaudeSkillTarget.is_package is True
    assert ClaudeSkillTarget.output_filename == "SKILL.md"


def test_compile_package_produces_skill_md_and_references():
    t = ClaudeSkillTarget()
    sources = {
        "README.md": "# My Project\n\nA tool for doing things.",
        "docs/rules.md": "# Rules\n\n- Always test your code.\n- Never skip lint.",
    }

    package = t.compile_package(sources)

    assert "SKILL.md" in package
    assert "references/README.md" in package
    assert "references/docs/rules.md" in package
    # Verbatim, untruncated — no lossy summarization.
    assert package["references/docs/rules.md"] == sources["docs/rules.md"]


def test_skill_md_has_required_frontmatter():
    t = ClaudeSkillTarget()
    sources = {"README.md": "# My Project\n\nA tool for doing things."}

    package = t.compile_package(sources)
    skill_md = package["SKILL.md"]

    assert skill_md.startswith("---\n")
    assert "name: my-project" in skill_md
    assert "description:" in skill_md


def test_description_states_when_to_use():
    t = ClaudeSkillTarget()
    sources = {"README.md": "# My Project\n\nA tool for doing things."}

    package = t.compile_package(sources)

    assert "check this SKILL.md" in package["SKILL.md"]
    assert "before scanning raw source files" in package["SKILL.md"]


def test_config_overrides_auto_derived_name_and_description():
    t = ClaudeSkillTarget()
    sources = {"README.md": "# My Project\n\nA tool for doing things."}
    config = SkillConfig(name="custom-name", description="Use when the user asks about X.")

    package = t.compile_package(sources, config)

    assert "name: custom-name" in package["SKILL.md"]
    assert "description: Use when the user asks about X." in package["SKILL.md"]


def test_compile_package_with_no_sources():
    t = ClaudeSkillTarget()
    package = t.compile_package({})
    assert "No source documents found" in package["SKILL.md"]


def test_compile_wraps_compile_package():
    t = ClaudeSkillTarget()
    sources = {"README.md": "# My Project\n\nA tool for doing things."}
    assert t.compile(sources) == t.compile_package(sources)["SKILL.md"]


# ── Validation ─────────────────────────────────────────────────────────────

def test_validate_passes_well_formed_skill():
    t = ClaudeSkillTarget()
    content = (
        "---\n"
        "name: my-project\n"
        "description: Use this when the user asks about anything in this "
        "repository's documentation or reference material.\n"
        "---\n\n"
        "## Reference index\n"
    )
    result = t.validate(content)
    assert result.passed


def test_validate_errors_on_missing_frontmatter():
    t = ClaudeSkillTarget()
    result = t.validate("Just some text, no frontmatter at all.")
    assert not result.passed
    assert any(i.code == "SKILL_001" for i in result.errors)


def test_validate_errors_on_bad_name_format():
    t = ClaudeSkillTarget()
    content = "---\nname: My Project!\ndescription: " + "x" * 50 + "\n---\n"
    result = t.validate(content)
    assert any(i.code == "SKILL_004" for i in result.errors)


def test_validate_warns_on_short_description():
    t = ClaudeSkillTarget()
    content = "---\nname: my-project\ndescription: too short\n---\n"
    result = t.validate(content)
    assert any(i.code == "SKILL_002" for i in result.warnings)


def test_validate_warns_on_long_body():
    t = ClaudeSkillTarget()
    body = "\n".join(f"line {i}" for i in range(600))
    content = (
        "---\nname: my-project\ndescription: " + "x" * 50 + "\n---\n" + body
    )
    result = t.validate(content)
    assert any(i.code == "SKILL_003" for i in result.warnings)


def test_fix_slugifies_bad_name():
    t = ClaudeSkillTarget()
    content = "---\nname: My Project!\ndescription: " + "x" * 50 + "\n---\n"
    result = t.validate(content)
    fixed, fixes = t.fix(content, result)
    assert "name: my-project" in fixed
    assert fixes
