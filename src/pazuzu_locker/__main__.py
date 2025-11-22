"""Package entry point for `python -m pazuzu_locker`."""

from __future__ import annotations

import sys

from .cli import run_cli


def main() -> int:
    """Execute the CLI when the package is invoked as a module."""

    return run_cli()


if __name__ == "__main__":
    sys.exit(main())

