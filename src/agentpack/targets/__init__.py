from .aider import AiderTarget
from .base import BaseTarget, Issue, ValidationResult
from .chatgpt import ChatGPTTarget
from .claude import ClaudeTarget
from .codex import CodexTarget
from .copilot import CopilotTarget
from .cursor import CursorTarget
from .gemini import GeminiTarget

TARGETS: dict[str, type[BaseTarget]] = {
    "claude": ClaudeTarget,
    "cursor": CursorTarget,
    "chatgpt": ChatGPTTarget,
    "gemini": GeminiTarget,
    "copilot": CopilotTarget,
    "codex": CodexTarget,
    "aider": AiderTarget,
}


def get_target(name: str) -> BaseTarget:
    if "@" in name:
        name, _version = name.split("@", 1)  # version pinning reserved for future use
    if name not in TARGETS:
        available = ", ".join(TARGETS)
        raise ValueError(f"Unknown target '{name}'. Available: {available}")
    return TARGETS[name]()
