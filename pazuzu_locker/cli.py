from __future__ import annotations

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.table import Table

from pazuzu_locker import __version__
from pazuzu_locker.config import (
    ConfigError,
    LockerConfig,
    load_config,
    write_template,
)
from pazuzu_locker.services.decryption import DecryptionError, DecryptionService
from pazuzu_locker.services.encryption import EncryptionError, EncryptionService
from pazuzu_locker.state import load_summary, save_summary
from pazuzu_locker.storage.provider import ProviderError, get_provider
from pazuzu_locker.utils import format_bytes, scan_target

app = typer.Typer(
    name="pazuzu-locker",
    help="🔐 Pazuzu Locker – secure file encryption toolkit with remote manifest storage",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 1
EXIT_ENCRYPTION_ERROR = 2
EXIT_DECRYPTION_ERROR = 3
EXIT_PROVIDER_ERROR = 4
EXIT_USER_ABORT = 5


def setup_logging(level: str):
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )


def print_banner():
    banner_text = r"""
[bold magenta]              ████████████████
        ████████      █████       ██
     █████          ████        ███
   ███            ███          █████
 ███           █████          ████████
██            ██████          ██    ███
            ████  ████        ███    ██
           ███      █████           ███
          ███     ████████████████████
         ███      ███     █████████
         ██     ███     █████[/]            [bold white];-.[/]
        [bold magenta]███    ██      ███[/]               [bold white]|  )[/]
        [bold magenta]██     █      ███[/]                [bold white]|-'[/] [bold magenta],-:[/] [bold white],-,[/] [bold magenta]. .[/] [bold white],-,[/] [bold magenta]. .[/] [bold white]  |  [/] [bold magenta],-.,-.[/] [bold white]| ,[/] [bold magenta],-.;-.[/]
        [bold magenta]██      █     ██[/]                 [bold white]|  [/] [bold magenta]| |[/] [bold white] / [/] [bold magenta]| |[/] [bold white] / [/] [bold magenta]| |[/] [bold white]  |  [/] [bold magenta]| |[/] [bold white]|  [/] [bold magenta]|< [/] [bold white]|-'[/] [bold magenta]|[/]
        [bold magenta] █            ██[/]                 [bold white]'  [/] [bold magenta]`-`[/] [bold white]'-'[/] [bold magenta]`-`[/] [bold white]'-'[/] [bold magenta]`-`[/] [bold white]  `--'[/] [bold magenta]`-'[/] [bold white]`-'[/] [bold magenta]' `[/] [bold white]`-'[/] [bold magenta]'[/]
                      [bold magenta]██[/]
                      [bold magenta]███[/]                                 𝔫𝔬𝔱 𝔣𝔬𝔯 𝔦𝔩𝔩𝔢𝔤𝔞𝔩 𝔭𝔲𝔯𝔭𝔬𝔰𝔢
                       [bold magenta]███[/]                             𝔥𝔱𝔱𝔭𝔰://𝔤𝔦𝔱𝔥𝔲𝔟.𝔠𝔬𝔪/𝔫𝔞𝔱𝔢𝔨𝔞𝔩𝔦
                        [bold magenta]███[/]
                          [bold magenta]███[/]
                            [bold magenta]███[/]
"""
    console.print(banner_text)


def version_callback(show_version: bool):
    if show_version:
        console.print(f"[bold magenta]Pazuzu Locker[/] version [cyan]{__version__}[/]")
        raise typer.Exit(EXIT_SUCCESS)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    pass


@app.command()
def encrypt(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Target directory to encrypt (overrides conf.py)",
    ),
    manifest: Optional[Path] = typer.Option(
        None,
        "--manifest",
        "-m",
        help="Path to store the manifest CSV",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        help="Manifest storage provider (pixeldrain, local)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview actions without making changes",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip confirmation prompts",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging verbosity (DEBUG, INFO, WARNING, ERROR)",
    ),
):
    """
    🔒 Encrypt files in a target directory using Fernet encryption.

    [bold cyan]Examples:[/]

        # Encrypt a directory with prompts
        pazuzu-locker encrypt --path ~/documents

        # Force encryption without confirmation (use with caution!)
        pazuzu-locker encrypt --path ~/documents --force

        # Dry-run to preview what would be encrypted
        pazuzu-locker encrypt --path ~/documents --dry-run
    """
    setup_logging(log_level)
    print_banner()

    try:
        config = load_config(
            start_dir=path,
            manifest_path=manifest,
            provider=provider,
            log_level=log_level,
        )
    except ConfigError as exc:
        console.print(f"[bold red]Configuration Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_CONFIG_ERROR)

    if "start_dir" in config.missing:
        console.print(
            "[bold red]Error:[/] Target directory is not configured.\n"
            "Provide [cyan]--path[/] or set [cyan]start_dir[/] in conf.py",
            style="red",
        )
        raise typer.Exit(EXIT_CONFIG_ERROR)

    target_path = config.require_path("start_dir")
    manifest_path = config.require_path("manifest_path")

    try:
        files, dir_count, total_size = scan_target(target_path, exclude=manifest_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        console.print(f"[bold red]Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_CONFIG_ERROR)

    file_count = len(files)

    if file_count == 0:
        console.print("[bold yellow]No eligible files found to encrypt.[/]")
        raise typer.Exit(EXIT_SUCCESS)

    table = Table(title="📊 Encryption Summary", title_style="bold magenta")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Target Directory", str(target_path))
    table.add_row("Manifest Path", str(manifest_path))
    table.add_row("Provider", config.provider)
    table.add_row("Files Found", str(file_count))
    table.add_row("Directories", str(dir_count))
    table.add_row("Estimated Size", format_bytes(total_size))
    table.add_row("Mode", "[yellow]DRY RUN[/]" if dry_run else "[green]LIVE[/]")
    console.print(table)

    if not force and not dry_run:
        if file_count > 100:
            console.print(
                f"[bold yellow]⚠️  Warning:[/] You are about to encrypt [bold]{file_count}[/] files!",
                style="yellow",
            )
        confirmed = Confirm.ask(
            f"[bold]Proceed with encryption of {file_count} files in [cyan]{target_path}[/]?[/]",
            console=console,
        )
        if not confirmed:
            console.print("[bold yellow]Encryption cancelled by user.[/]")
            raise typer.Exit(EXIT_USER_ABORT)

    try:
        storage = get_provider(config.provider)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Encrypting files...[/]", total=file_count
            )
            
            def update_progress(p: Path):
                progress.advance(task)
            
            service = EncryptionService(
                target_dir=target_path,
                manifest_path=manifest_path,
                provider=storage,
                dry_run=dry_run,
                files=files,
                progress_callback=update_progress if file_count > 0 else None,
            )
            result = service.run()

        stats_table = Table(title="✅ Encryption Results", title_style="bold green")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Count", justify="right", style="white")
        stats_table.add_row("Files Scanned", str(service.stats.total_files))
        stats_table.add_row("Encrypted", str(service.stats.encrypted))
        stats_table.add_row("Skipped", str(service.stats.skipped))
        stats_table.add_row("Failed", str(service.stats.failed))
        stats_table.add_row("Data Processed", format_bytes(service.stats.bytes_processed))
        console.print(stats_table)

        summary_payload = {
            "operation": "encrypt",
            "timestamp": datetime.utcnow().isoformat(),
            "target": str(target_path),
            "files": service.stats.encrypted,
            "skipped": service.stats.skipped,
            "failed": service.stats.failed,
            "bytes": service.stats.bytes_processed,
            "provider": config.provider,
            "dry_run": dry_run,
            "manifest_path": str(manifest_path),
            "destination": result.destination,
            "metadata": result.metadata,
        }
        save_summary(summary_payload)

        if not dry_run and service.stats.encrypted > 0:
            console.print(
                Panel(
                    f"[bold green]Manifest uploaded to:[/]\n[cyan]{result.destination}[/]\n\n"
                    f"[bold]ID:[/] [yellow]{result.metadata.get('px_id', 'N/A')}[/]",
                    title="🎉 Success",
                    border_style="green",
                )
            )

        if service.stats.failed > 0:
            console.print(f"[yellow]⚠️  {service.stats.failed} errors occurred. Check logs for details.[/]")

    except (EncryptionError, ProviderError) as exc:
        console.print(f"[bold red]Encryption Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_ENCRYPTION_ERROR)
    except Exception as exc:  # pragma: no cover - defensive catch-all
        console.print(f"[bold red]Unexpected Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_ENCRYPTION_ERROR)


@app.command()
def decrypt(
    px_id: Optional[str] = typer.Option(
        None,
        "--px-id",
        help="PixelDrain file ID for the manifest (overrides conf.py)",
    ),
    manifest: Optional[Path] = typer.Option(
        None,
        "--manifest",
        "-m",
        help="Path to a local manifest file (use with --provider local)",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        help="Manifest storage provider (pixeldrain, local)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview actions without restoring files",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip confirmation prompts",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging verbosity (DEBUG, INFO, WARNING, ERROR)",
    ),
):
    """
    🔓 Decrypt files using a manifest from the storage provider.

    [bold cyan]Examples:[/]

        # Decrypt using manifest from PixelDrain
        pazuzu-locker decrypt --px-id FPJZjoAd

        # Decrypt from local manifest file
        pazuzu-locker decrypt --provider local --px-id /tmp/manifest.csv

        # Dry-run to preview decryption
        pazuzu-locker decrypt --px-id FPJZjoAd --dry-run
    """
    setup_logging(log_level)
    print_banner()

    try:
        config = load_config(
            pxfile_id=px_id,
            manifest_path=manifest,
            provider=provider,
            log_level=log_level,
        )
    except ConfigError as exc:
        console.print(f"[bold red]Configuration Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_CONFIG_ERROR)

    if config.provider == "local":
        manifest_path_value = config.manifest_path
        if not manifest_path_value:
            console.print(
                "[bold red]Error:[/] Provide [cyan]--manifest[/] or set [cyan]tmp_csv[/] in conf.py for local provider.",
                style="red",
            )
            raise typer.Exit(EXIT_CONFIG_ERROR)
        manifest_identifier = str(manifest_path_value)
    else:
        manifest_identifier = config.require_px_id()

    console.print(
        f"[bold]Decryption Configuration:[/]\n"
        f"  Provider: [cyan]{config.provider}[/]\n"
        f"  Manifest ID: [yellow]{manifest_identifier}[/]\n"
        f"  Mode: {'[yellow]DRY RUN[/]' if dry_run else '[green]LIVE[/]'}",
    )

    if not force and not dry_run:
        confirmed = Confirm.ask(
            f"[bold]Proceed with decryption using manifest [cyan]{manifest_identifier}[/]?[/]",
            console=console,
        )
        if not confirmed:
            console.print("[bold yellow]Decryption cancelled by user.[/]")
            raise typer.Exit(EXIT_USER_ABORT)

    try:
        storage = get_provider(config.provider)
        manifest_content = storage.fetch_manifest(manifest_identifier)
        
        reader = csv.reader(manifest_content.splitlines())
        entry_count = sum(1 for row in reader if len(row) == 2)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Decrypting files...[/]", total=entry_count
            )
            
            def update_progress(p: Path):
                progress.advance(task)
            
            service = DecryptionService(
                dry_run=dry_run,
                progress_callback=update_progress if entry_count > 0 else None,
            )
            stats = service.run_from_manifest(manifest_content)

        stats_table = Table(title="✅ Decryption Results", title_style="bold green")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Count", justify="right", style="white")
        stats_table.add_row("Entries Processed", str(stats.processed))
        stats_table.add_row("Files Restored", str(stats.restored))
        stats_table.add_row("Skipped", str(stats.skipped))
        stats_table.add_row("Failed", str(stats.failed))
        stats_table.add_row("Data Processed", format_bytes(stats.bytes_processed))
        console.print(stats_table)

        summary_payload = {
            "operation": "decrypt",
            "timestamp": datetime.utcnow().isoformat(),
            "files": stats.restored,
            "skipped": stats.skipped,
            "failed": stats.failed,
            "bytes": stats.bytes_processed,
            "provider": config.provider,
            "manifest_id": manifest_identifier,
            "dry_run": dry_run,
        }
        save_summary(summary_payload)

        if stats.failed > 0:
            console.print(f"[yellow]⚠️  {stats.failed} errors occurred. Check logs for details.[/]")
        elif not dry_run:
            console.print(
                Panel(
                    f"[bold green]Successfully restored {stats.restored} files![/]",
                    title="🎉 Success",
                    border_style="green",
                )
            )

    except (DecryptionError, ProviderError) as exc:
        console.print(f"[bold red]Decryption Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_DECRYPTION_ERROR)
    except Exception as exc:  # pragma: no cover - defensive catch-all
        console.print(f"[bold red]Unexpected Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_DECRYPTION_ERROR)


@app.command()
def status(
    manifest: Optional[Path] = typer.Option(
        None,
        "--manifest",
        "-m",
        help="Path to local manifest CSV to inspect",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging verbosity (DEBUG, INFO, WARNING, ERROR)",
    ),
):
    """
    📊 Show status of last encryption manifest.

    [bold cyan]Examples:[/]

        # Show status of last manifest from config
        pazuzu-locker status

        # Inspect a specific manifest file
        pazuzu-locker status --manifest /tmp/manifest.csv
    """
    setup_logging(log_level)

    try:
        config = load_config(manifest_path=manifest, log_level=log_level)
    except ConfigError as exc:
        console.print(f"[bold red]Configuration Error:[/] {exc}", style="red")
        raise typer.Exit(EXIT_CONFIG_ERROR)

    summary = load_summary()
    if summary:
        summary_table = Table(title="📝 Last Run", title_style="bold green")
        summary_table.add_column("Field", style="cyan")
        summary_table.add_column("Value", style="white")
        summary_table.add_row("Operation", summary.get("operation", "unknown"))
        summary_table.add_row("Timestamp", summary.get("timestamp", "-"))
        summary_table.add_row("Provider", summary.get("provider", "-"))
        summary_table.add_row("Files", str(summary.get("files", 0)))
        summary_table.add_row("Bytes", format_bytes(summary.get("bytes", 0)))
        summary_table.add_row("Result", summary.get("destination", "-"))
        console.print(summary_table)
    else:
        console.print("[bold yellow]No previous runs found.[/]")

    manifest_path = config.manifest_path
    if not manifest_path and summary and summary.get("manifest_path"):
        manifest_path = Path(summary["manifest_path"])

    if not manifest_path or not Path(manifest_path).exists():
        console.print(
            "[bold yellow]⚠️  Manifest file not available.[/]\n"
            "Provide [cyan]--manifest[/] to inspect a local file.",
            style="yellow",
        )
        return

    entries = []
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        entries = list(reader)

    table = Table(title="📊 Manifest Status", title_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Manifest Path", str(manifest_path))
    table.add_row("File Size", format_bytes(Path(manifest_path).stat().st_size))
    table.add_row("Entries", str(len(entries)))
    console.print(table)

    if entries:
        sample_table = Table(title="🔍 Sample Entries", title_style="bold cyan", show_lines=True)
        sample_table.add_column("Encrypted File", style="yellow", overflow="fold")
        sample_table.add_column("Key (truncated)", style="dim white")
        for filepath, key_b64 in entries[:5]:
            sample_table.add_row(filepath, key_b64[:20] + "...")
        console.print(sample_table)
        if len(entries) > 5:
            console.print(f"[dim]... and {len(entries) - 5} more entries[/]")


@app.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Display the current resolved configuration",
    ),
    write_template_path: Optional[Path] = typer.Option(
        None,
        "--write-template",
        help="Write a configuration template to the specified path",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing config template if it exists",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging verbosity (DEBUG, INFO, WARNING, ERROR)",
    ),
):
    """
    ⚙️  Manage configuration settings.

    [bold cyan]Examples:[/]

        # Show current resolved configuration
        pazuzu-locker config --show

        # Write a configuration template file
        pazuzu-locker config --write-template ./my-conf.py

        # Overwrite existing config template
        pazuzu-locker config --write-template ./conf.py --overwrite
    """
    setup_logging(log_level)

    if write_template_path:
        try:
            written = write_template(write_template_path, overwrite=overwrite)
            console.print(
                Panel(
                    f"[bold green]Configuration template written to:[/]\n[cyan]{written}[/]",
                    title="✅ Success",
                    border_style="green",
                )
            )
        except ConfigError as exc:
            console.print(f"[bold red]Error:[/] {exc}", style="red")
            raise typer.Exit(EXIT_CONFIG_ERROR)
        return

    if show or (not write_template_path):
        try:
            cfg = load_config()
        except ConfigError as exc:
            console.print(f"[bold red]Configuration Error:[/] {exc}", style="red")
            raise typer.Exit(EXIT_CONFIG_ERROR)

        table = Table(title="⚙️  Current Configuration", title_style="bold cyan")
        table.add_column("Setting", style="magenta", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_row("start_dir", str(cfg.start_dir) if cfg.start_dir else "[dim]Not set[/]")
        table.add_row("manifest_path", str(cfg.manifest_path) if cfg.manifest_path else "[dim]Not set[/]")
        table.add_row("provider", cfg.provider)
        table.add_row("pxfile_id", cfg.pxfile_id if cfg.pxfile_id else "[dim]Not set[/]")
        table.add_row("log_level", cfg.log_level)
        if cfg.missing:
            table.add_row("missing", ", ".join(cfg.missing))
        console.print(table)


def cli_entry():  # pragma: no cover - entry point wrapper
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/]")
        sys.exit(EXIT_USER_ABORT)


if __name__ == "__main__":  # pragma: no cover - dev entry point
    cli_entry()
