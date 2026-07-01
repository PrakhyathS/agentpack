from pathlib import Path

from .config import load_skill_config
from .sources import scan
from .targets.base import BaseTarget, ValidationResult


class Compiler:
    def __init__(self, target: BaseTarget):
        self.target = target
        self.last_warnings: list[str] = []

    def compile(self, source_dir: Path) -> str:
        sources, self.last_warnings = scan(source_dir)
        return self.target.compile(sources)

    def compile_package(self, source_dir: Path) -> dict[str, str]:
        sources, self.last_warnings = scan(source_dir)
        config = load_skill_config(source_dir)
        return self.target.compile_package(sources, config)

    def validate(self, content: str) -> ValidationResult:
        return self.target.validate(content)

    def fix(self, content: str) -> tuple[str, list[str]]:
        result = self.validate(content)
        return self.target.fix(content, result)
