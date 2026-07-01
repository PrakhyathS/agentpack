from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from ..config import SkillConfig


@dataclass
class Issue:
    code: str
    message: str
    severity: str  # "error" | "warning"
    fixable: bool = False


@dataclass
class ValidationResult:
    target: str
    passed: bool
    issues: list[Issue] = field(default_factory=list)
    score: int = 100
    char_count: int = 0

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]


class BaseTarget(ABC):
    name: str
    output_filename: str
    is_package: bool = False

    @abstractmethod
    def validate(self, content: str) -> ValidationResult:
        pass

    @abstractmethod
    def compile(self, sources: dict[str, str]) -> str:
        """sources: {relative_path: file_content}"""
        pass

    def compile_package(
        self, sources: dict[str, str], config: SkillConfig | None = None
    ) -> dict[str, str]:
        """Override for multi-file outputs (set is_package = True).
        Default wraps compile() so single-file targets need no changes."""
        return {self.output_filename: self.compile(sources)}

    def fix(self, content: str, result: ValidationResult) -> tuple[str, list[str]]:
        """Return (fixed_content, list_of_applied_fix_descriptions)."""
        return content, []
