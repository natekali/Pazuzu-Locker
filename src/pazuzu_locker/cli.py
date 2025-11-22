"""Command line interface for the Pazuzu Locker package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from .config import load_config
from .logging import configure_logging, get_logger
from .providers import create_provider
from .workflow import decrypt_from_manifest, encrypt_directory


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pazuzu_locker",
        description="Encrypt or decrypt directories using the Pazuzu Locker workflows.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to pazuzu.toml configuration file (defaults to config/pazuzu.toml)",
    )
    parser.add_argument(
        "--start-dir",
        type=Path,
        help="Override the start directory defined in the configuration",
    )
    parser.add_argument(
        "--manifest-dir",
        type=Path,
        help="Override the manifest output directory",
    )
    parser.add_argument(
        "--include",
        dest="include_globs",
        action="append",
        help="Additional include glob patterns (can be repeated)",
    )
    parser.add_argument(
        "--exclude",
        dest="exclude_globs",
        action="append",
        help="Additional exclude glob patterns (can be repeated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate operations without writing files",
    )
    parser.add_argument(
        "--log-level",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        help="Override configured log level",
    )
    parser.add_argument(
        "--log-format",
        choices=["json", "text"],
        help="Override configured log format",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("encrypt", help="Encrypt files under the configured start directory")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt files using a manifest ID")
    decrypt_parser.add_argument(
        "--manifest-id",
        help="Manifest ID to download. Overrides configuration/env if provided.",
    )

    return parser


def _collect_overrides(args: argparse.Namespace) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if args.start_dir:
        overrides["start_dir"] = str(args.start_dir)
    if args.manifest_dir:
        overrides["manifest_dir"] = str(args.manifest_dir)
    if args.include_globs:
        overrides["include_globs"] = args.include_globs
    if args.exclude_globs:
        overrides["exclude_globs"] = args.exclude_globs
    if args.log_level:
        overrides["log_level"] = args.log_level
    if args.log_format:
        overrides["log_format"] = args.log_format
    if args.dry_run:
        overrides["dry_run"] = True
    return overrides


def run_cli(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    overrides = _collect_overrides(args)

    config = load_config(args.config, overrides=overrides)
    configure_logging(config.log_level, config.log_format)
    logger = get_logger(config)
    provider = create_provider(config.provider)

    try:
        if args.command == "encrypt":
            manifest_id = encrypt_directory(config, provider, logger)
            if manifest_id:
                logger.info(
                    "Manifest ready for download",
                    extra={
                        "action": "summary",
                        "manifest_id": manifest_id,
                        "provider": config.provider.name,
                    },
                )
        elif args.command == "decrypt":
            manifest_override = args.manifest_id or overrides.get("manifest_id")
            decrypt_from_manifest(
                config,
                provider,
                logger,
                manifest_id=manifest_override,
            )
        else:
            parser.error("Command is required")
        return 0
    except Exception as exc:  # pragma: no cover - safeguarded CLI path
        logger.error("Operation failed", extra={"action": args.command}, exc_info=True)
        return 1


def main() -> int:
    """Console script entry point."""

    return run_cli()


if __name__ == "__main__":
    sys.exit(run_cli())
