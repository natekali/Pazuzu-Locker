from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger("pazuzu_locker")


def scan_target(
    root: Path,
    *,
    exclude: Optional[Path] = None,
) -> Tuple[List[Path], int, int]:
    """Scan *root* and return (files, directory_count, total_bytes).

    Files with the `.pazuzu` suffix and the optional *exclude* path are ignored.
    """
    if not root.exists():
        raise FileNotFoundError(f"Target directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Target path is not a directory: {root}")

    files: List[Path] = []
    dir_count = 0
    bytes_total = 0
    exclude_resolved = exclude.resolve() if exclude else None

    for current_dir, dirnames, filenames in os.walk(root):
        dir_count += len(dirnames)
        for name in filenames:
            path = Path(current_dir) / name
            if path.suffix == ".pazuzu":
                continue
            if exclude_resolved and path.resolve() == exclude_resolved:
                continue
            files.append(path)
            try:
                bytes_total += path.stat().st_size
            except (OSError, PermissionError):  # pragma: no cover - best effort
                logger.debug("Unable to read file size for %s", path)
    return files, dir_count, bytes_total


def format_bytes(size: int) -> str:
    """Format bytes into a human-readable string."""
    if size <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    idx = 0
    value = float(size)
    while value >= 1024 and idx < len(units) - 1:
        value /= 1024
        idx += 1
    return f"{value:.1f} {units[idx]}"
