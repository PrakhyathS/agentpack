from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable

RunCompile = Callable[[Path, str, "Path | None"], None]


class DebouncedHandler:
    """Collapses rapid-fire filesystem events into a single callback,
    firing `on_change` only after `debounce` seconds of silence."""

    def __init__(self, on_change: Callable[[], None], debounce: float) -> None:
        self._on_change = on_change
        self._debounce = debounce
        self._timer: threading.Timer | None = None

    def dispatch(self, event) -> None:
        if getattr(event, "is_directory", False):
            return
        if self._timer is not None:
            self._timer.cancel()
        self._timer = threading.Timer(self._debounce, self._on_change)
        self._timer.start()


def watch(
    source: Path,
    target: str,
    output: Path | None,
    run_compile: RunCompile,
    console,
    debounce: float = 0.75,
) -> None:
    """Watch `source` and re-run `run_compile` on every filesystem change,
    debounced so rapid saves don't trigger a recompile storm."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        console.print(
            "[red]Missing dependency.[/red] Install with: "
            "pip install 'agentpack-skills[watch]'"
        )
        raise SystemExit(1)

    def _recompile() -> None:
        console.print("\n[dim]Change detected — recompiling...[/dim]")
        try:
            run_compile(source, target, output)
        except Exception as exc:
            console.print(f"[red]Compile failed:[/red] {exc}")

    debounced = DebouncedHandler(_recompile, debounce)

    class _WatchdogHandler(FileSystemEventHandler):
        def on_any_event(self, event) -> None:
            debounced.dispatch(event)

    console.print(f"[bold]Watching {source} for changes...[/bold] (Ctrl+C to stop)")
    run_compile(source, target, output)

    observer = Observer()
    observer.schedule(_WatchdogHandler(), str(source), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
