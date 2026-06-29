from pathlib import Path

from .sources import scan
from .targets.base import BaseTarget, ValidationResult


class Compiler:
    def __init__(self, target: BaseTarget):
        self.target = target

    def compile(self, source_dir: Path) -> str:
        sources = scan(source_dir)
        return self.target.compile(sources)

    def validate(self, content: str) -> ValidationResult:
        return self.target.validate(content)

    def fix(self, content: str) -> tuple[str, list[str]]:
        result = self.validate(content)
        return self.target.fix(content, result)
