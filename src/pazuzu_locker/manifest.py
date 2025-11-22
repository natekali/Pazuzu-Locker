"""Manifest CSV operations for tracking encrypted files and keys."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .crypto import decode_key, encode_key


@dataclass
class ManifestEntry:
    """Single entry in the encryption manifest."""

    file_path: str
    encryption_key: bytes

    def to_row(self) -> tuple[str, str]:
        """Convert to CSV row format."""
        return (self.file_path, encode_key(self.encryption_key))

    @classmethod
    def from_row(cls, row: tuple[str, str]) -> ManifestEntry:
        """Create entry from CSV row."""
        file_path, encoded_key = row
        return cls(
            file_path=file_path,
            encryption_key=decode_key(encoded_key),
        )


class Manifest:
    """Handles reading and writing the manifest CSV."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._entries: list[ManifestEntry] = []

    def add_entry(self, file_path: str, encryption_key: bytes) -> None:
        """Add a new entry to the manifest."""
        self._entries.append(ManifestEntry(file_path, encryption_key))

    def write(self) -> None:
        """Write manifest entries to CSV file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="") as f:
            writer = csv.writer(f)
            for entry in self._entries:
                writer.writerow(entry.to_row())

    @classmethod
    def read(cls, path: Path) -> Manifest:
        """Read manifest from CSV file."""
        manifest = cls(path)
        with path.open("r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    manifest._entries.append(ManifestEntry.from_row((row[0], row[1])))
        return manifest

    @classmethod
    def from_content(cls, content: str) -> Manifest:
        """Parse manifest from CSV content string."""
        manifest = cls(Path("remote_manifest.csv"))
        reader = csv.reader(content.splitlines())
        for row in reader:
            if len(row) == 2:
                manifest._entries.append(ManifestEntry.from_row((row[0], row[1])))
        return manifest

    def __iter__(self) -> Iterator[ManifestEntry]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)
