"""UIForge CLI entry point."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich import print as rprint

console = Console()


def _require_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            "[bold red]Error:[/] ANTHROPIC_API_KEY is not set.\n"
            "Get a key at [link=https://console.anthropic.com]console.anthropic.com[/link] "
            "then run:\n\n"
            "  [bold]export ANTHROPIC_API_KEY=sk-ant-...[/]",
        )
        sys.exit(1)


def _print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold violet]UIForge[/] [dim]v0.1.0[/]\n"
            "[dim]Screenshot → Production React[/]",
            border_style="violet",
            padding=(0, 2),
        )
    )


@click.group(invoke_without_command=True)
@click.argument("image", required=False, type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default=None, type=click.Path(path_type=Path), help="Output directory")
@click.option("--framework", "-f", default="vite", type=click.Choice(["vite", "next", "html"]), help="Target framework")
@click.option("--model", default="claude-sonnet-4-6", help="Claude model to use")
@click.option("--context", "-c", default="", help="Extra context about the UI")
@click.option("--open", "open_browser", is_flag=True, default=False, help="Open output dir when done")
@click.option("--dry-run", is_flag=True, default=False, help="Analyze only, do not generate code")
@click.pass_context
def main(
    ctx: click.Context,
    image: Path | None,
    output: Path | None,
    framework: str,
    model: str,
    context: str,
    open_browser: bool,
    dry_run: bool,
) -> None:
    """Convert a UI screenshot into production-ready React components.

    \b
    Examples:
      uiforge dashboard.png
      uiforge dashboard.png --output ./my-app
      uiforge dashboard.png --framework next
      uiforge dashboard.png --context "dark theme SaaS dashboard"
    """
    if ctx.invoked_subcommand is not None:
        return

    if image is None:
        click.echo(ctx.get_help())
        return

    _require_api_key()
    _run(image, output, framework, model, context, open_browser, dry_run)


def _run(
    image: Path,
    output: Path | None,
    framework: str,
    model: str,
    context: str,
    open_browser: bool,
    dry_run: bool,
) -> None:
    from uiforge.pipeline.analyzer import analyze_image
    from uiforge.pipeline.generator import generate_all, _flatten_components
    from uiforge.pipeline.scaffolder import scaffold_project

    _print_banner()

    # ── Step 1: Analyze ──────────────────────────────────────────────────────
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"[violet]Analyzing[/] {image.name}…", total=None)

        try:
            analysis = analyze_image(image, model=model, extra_context=context)
        except Exception as exc:
            progress.stop()
            console.print(f"[red]Analysis failed:[/] {exc}")
            sys.exit(1)

        progress.update(task, description=f"[green]✓ Analyzed[/] {image.name}")
        progress.stop()

    all_components = _flatten_components(analysis.components)

    t = Table(show_header=True, header_style="bold violet", box=None, padding=(0, 1))
    t.add_column("Component")
    t.add_column("Type")
    t.add_column("Shadcn/UI")
    for c in all_components:
        t.add_row(c.name, c.type, c.shadcn_component or "—")

    console.print()
    console.print(f"[bold]Page:[/] {analysis.page_name}  [dim]({analysis.page_type} / {analysis.layout})[/]")
    console.print(t)
    console.print()

    if dry_run:
        console.print("[dim]Dry run — skipping code generation.[/]")
        return

    # ── Step 2: Generate ─────────────────────────────────────────────────────
    generated: dict[str, str] = {}
    pending = [c.name for c in all_components] + [analysis.page_name]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[violet]Generating components…[/]", total=None)
        done: list[str] = []

        def on_progress(name: str) -> None:
            done.append(name)
            progress.update(
                task,
                description=f"[violet]Generating[/] {name}… [dim]({len(done)}/{len(pending)})[/]",
            )

        try:
            generated = generate_all(analysis, model=model, on_progress=on_progress)
        except Exception as exc:
            progress.stop()
            console.print(f"[red]Generation failed:[/] {exc}")
            sys.exit(1)

        progress.update(task, description=f"[green]✓ Generated[/] {len(generated)} files")
        progress.stop()

    # ── Step 3: Scaffold ──────────────────────────────────────────────────────
    if output is None:
        output = Path.cwd() / analysis.page_name.lower()

    with console.status(f"[violet]Writing project to[/] {output}…"):
        written = scaffold_project(output, analysis, generated, framework=framework)

    console.print()
    console.print(Panel(
        f"[bold green]Done![/] {len(written)} files written to [bold]{output}[/]\n\n"
        "  [bold]cd[/] " + str(output) + "\n"
        "  [bold]npm install[/]\n"
        "  [bold]npm run dev[/]",
        title="[bold green]UIForge[/]",
        border_style="green",
        padding=(0, 2),
    ))
    console.print()

    if open_browser:
        import subprocess
        subprocess.Popen(["code", str(output)], shell=True)


@main.command()
def version() -> None:
    """Show UIForge version."""
    from uiforge import __version__
    console.print(f"uiforge {__version__}")


if __name__ == "__main__":
    main()
