from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .compiler import Compiler
from .discovery import sync_claude_md
from .targets import TARGETS, get_target
from .targets.base import ValidationResult

app = typer.Typer(
    name="agentpack",
    help="Agent Knowledge Compiler — one source, many AI targets.",
    no_args_is_help=True,
)
console = Console()

_TARGET_HELP = f"Target agent. One of: {', '.join(TARGETS)}"


@app.command()
def compile(
    source: Path = typer.Argument(Path("."), help="Source directory to compile."),
    target: str = typer.Option(..., "--target", "-t", help=_TARGET_HELP),
    output: Path | None = typer.Option(
        None, "--output", "-o",
        help="Output path — a file for single-file targets, a directory for package targets.",
    ),
) -> None:
    """Compile a repository into an agent-specific knowledge package."""
    _run_compile(source, target, output)


@app.command()
def watch(
    source: Path = typer.Argument(Path("."), help="Source directory to watch."),
    target: str = typer.Option(..., "--target", "-t", help=_TARGET_HELP),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output path."),
) -> None:
    """Watch a directory and auto-recompile whenever files are added, changed, or removed."""
    from .watch import watch as _watch

    _watch(source, target, output, run_compile=_run_compile, console=console)


# ── shared compile logic (used by both `compile` and `watch`) ────────────────

def _run_compile(source: Path, target: str, output: Path | None) -> None:
    ag_target = get_target(target)
    compiler = Compiler(ag_target)

    with console.status(f"[bold]Scanning {source}…[/bold]"):
        if ag_target.is_package:
            package = compiler.compile_package(source)
        else:
            content = compiler.compile(source)

    for warning in compiler.last_warnings:
        console.print(f"[yellow]⚠[/yellow] {escape(warning)}")

    if ag_target.is_package:
        out_dir = output or (source / "dist" / target)
        for rel_path, file_content in package.items():
            file_path = out_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_content, encoding="utf-8")

        sync_claude_md(source, out_dir)

        result = ag_target.validate(package["SKILL.md"])
        console.print()
        _render_result(result)
        console.print(
            f"\n[green]✓[/green] Output: [bold]{out_dir}[/bold]  ({len(package)} file(s))"
        )
        return

    result = ag_target.validate(content)
    out_path = output or (source / "dist" / target / ag_target.output_filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)

    console.print()
    _render_result(result)
    console.print(f"\n[green]✓[/green] Output: [bold]{out_path}[/bold]  ({result.char_count} chars)")


@app.command()
def validate(
    file: Path = typer.Argument(..., help="File to validate."),
    target: str = typer.Option(..., "--target", "-t", help=_TARGET_HELP),
) -> None:
    """Validate an existing file against a target's constraints."""
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(1)

    content = file.read_text(encoding="utf-8")
    ag_target = get_target(target)
    result = ag_target.validate(content)

    console.print()
    _render_result(result)

    if not result.passed:
        raise typer.Exit(1)


@app.command()
def fix(
    file: Path = typer.Argument(..., help="File to fix."),
    target: str = typer.Option(..., "--target", "-t", help=_TARGET_HELP),
    inplace: bool = typer.Option(False, "--inplace", "-i", help="Overwrite the original file."),
) -> None:
    """Auto-fix issues in a file for a target."""
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(1)

    content = file.read_text(encoding="utf-8")
    ag_target = get_target(target)
    result = ag_target.validate(content)
    fixed, applied = ag_target.fix(content, result)

    if not applied:
        console.print("[yellow]No auto-fixable issues found.[/yellow]")
        return

    for msg in applied:
        console.print(f"[green]✓[/green] {msg}")

    if inplace:
        file.write_text(fixed, encoding="utf-8")
        console.print(f"\n[green]Updated[/green] {file}")
    else:
        out = file.with_stem(file.stem + ".fixed")
        out.write_text(fixed, encoding="utf-8")
        console.print(f"\n[green]Saved[/green] → {out}  (use --inplace to overwrite)")


@app.command()
def score(
    source: Path = typer.Argument(Path("."), help="Source directory to score."),
) -> None:
    """Show compatibility scores across all supported targets."""
    table = Table(title="Agent Compatibility", show_header=True, header_style="bold")
    table.add_column("Target")
    table.add_column("Score")
    table.add_column("Status")
    table.add_column("Errors")
    table.add_column("Warnings")

    for name, TargetClass in TARGETS.items():
        ag_target = TargetClass()
        compiler = Compiler(ag_target)
        content = compiler.compile(source)
        result = ag_target.validate(content)

        bar = _bar(result.score)
        status = "[green]Pass[/green]" if result.passed else "[red]Fail[/red]"
        table.add_row(
            name,
            f"{bar} {result.score}%",
            status,
            str(len(result.errors)),
            str(len(result.warnings)),
        )

    console.print()
    console.print(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", is_eager=True),
) -> None:
    if version:
        console.print(f"agentpack {__version__}")
        raise typer.Exit()


# ── helpers ──────────────────────────────────────────────────────────────────

def _bar(score: int) -> str:
    filled = score // 10
    return "█" * filled + "░" * (10 - filled)


def _render_result(result: ValidationResult) -> None:
    color = "green" if result.passed else "red"
    status = "PASSED" if result.passed else "FAILED"

    console.print(Panel(
        f"[bold {color}]{status}[/bold {color}]  "
        f"Score: [{_bar(result.score)}] {result.score}/100\n"
        f"Target: [bold]{result.target}[/bold]  •  {result.char_count} chars",
        title="Validation",
        border_style=color,
    ))

    if result.errors:
        console.print("\n[red]Errors:[/red]")
        for issue in result.errors:
            tag = "  [dim](fixable — run `agentpack fix`)[/dim]" if issue.fixable else ""
            console.print(f"  [red]✗[/red] [{issue.code}] {escape(issue.message)}{tag}")

    if result.warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for issue in result.warnings:
            tag = "  [dim](fixable)[/dim]" if issue.fixable else ""
            console.print(f"  [yellow]⚠[/yellow] [{issue.code}] {escape(issue.message)}{tag}")
