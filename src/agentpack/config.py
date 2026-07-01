from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillConfig:
    name: str | None = None
    description: str | None = None
    license: str | None = None


def load_skill_config(source_dir: Path) -> SkillConfig:
    """Load optional [skill] overrides from agentpack.toml in the source
    root. Returns an all-None config if the file doesn't exist — callers
    fall back to auto-derived values in that case."""
    config_path = source_dir / "agentpack.toml"
    if not config_path.exists():
        return SkillConfig()

    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # Python 3.10 fallback

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    skill = data.get("skill", {})
    return SkillConfig(
        name=skill.get("name"),
        description=skill.get("description"),
        license=skill.get("license"),
    )
