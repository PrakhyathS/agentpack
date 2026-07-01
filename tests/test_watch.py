import sys
import time
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from agentpack.watch import DebouncedHandler, watch


@dataclass
class _FakeEvent:
    is_directory: bool = False


def test_debounce_collapses_rapid_events():
    calls = []
    handler = DebouncedHandler(on_change=lambda: calls.append(1), debounce=0.05)

    for _ in range(5):
        handler.dispatch(_FakeEvent())
        time.sleep(0.01)  # faster than the debounce window

    time.sleep(0.15)  # let the final debounce timer fire
    assert calls == [1]


def test_debounce_fires_again_after_quiet_period():
    calls = []
    handler = DebouncedHandler(on_change=lambda: calls.append(1), debounce=0.05)

    handler.dispatch(_FakeEvent())
    time.sleep(0.15)
    handler.dispatch(_FakeEvent())
    time.sleep(0.15)

    assert calls == [1, 1]


def test_debounce_ignores_directory_events():
    calls = []
    handler = DebouncedHandler(on_change=lambda: calls.append(1), debounce=0.02)

    handler.dispatch(_FakeEvent(is_directory=True))
    time.sleep(0.1)

    assert calls == []


def test_watch_runs_initial_compile_before_entering_loop(tmp_path):
    run_compile = MagicMock(side_effect=KeyboardInterrupt)
    console = MagicMock()

    # KeyboardInterrupt from the initial (pre-loop) run_compile call isn't
    # caught by watch()'s try/except (that only wraps the idle-wait loop),
    # so it propagates — proving run_compile fired first, before any
    # watchdog Observer was even started.
    with pytest.raises(KeyboardInterrupt):
        watch(tmp_path, "claude-skill", None, run_compile, console)

    run_compile.assert_called_once_with(tmp_path, "claude-skill", None)


def test_watch_shows_clear_error_without_watchdog(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "watchdog", None)
    monkeypatch.setitem(sys.modules, "watchdog.events", None)
    monkeypatch.setitem(sys.modules, "watchdog.observers", None)

    console = MagicMock()
    with pytest.raises(SystemExit):
        watch(tmp_path, "claude-skill", None, MagicMock(), console)

    assert any("agentpack-skills[watch]" in str(call) for call in console.print.call_args_list)
