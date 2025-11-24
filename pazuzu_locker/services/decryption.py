from __future__ import annotations

import base64
import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("pazuzu_locker.decryption")


class DecryptionError(Exception):
    """Raised when manifest decryption fails."""


@dataclass
class DecryptionStats:
    processed: int = 0
    restored: int = 0
    skipped: int = 0
    failed: int = 0
    bytes_processed: int = 0
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, any]:
        return {
            "processed": self.processed,
            "restored": self.restored,
            "skipped": self.skipped,
            "failed": self.failed,
            "bytes_processed": self.bytes_processed,
            "errors": self.errors[:10],
        }


class DecryptionService:
    def __init__(
        self,
        *,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[Path], None]] = None,
    ):
        self.dry_run = dry_run
        self.progress_callback = progress_callback
        self.stats = DecryptionStats()

    def run_from_manifest(self, csv_content: str) -> DecryptionStats:
        reader = csv.reader(csv_content.splitlines())
        for row in reader:
            if len(row) != 2:
                logger.debug("Skipping malformed row: %s", row)
                continue
            filepath, key_b64 = row
            self.stats.processed += 1
            if self.progress_callback:
                self.progress_callback(Path(filepath))
            try:
                self._restore(filepath, key_b64)
            except Exception as exc:  # pragma: no cover - catch-all recovery
                logger.warning("Failed to restore %s: %s", filepath, exc)
                self.stats.failed += 1
                self.stats.errors.append(f"{filepath}: {exc}")
        return self.stats

    def _restore(self, filepath: str, key_b64: str):
        source = Path(filepath)
        if not source.exists():
            logger.debug("Missing encrypted file: %s", source)
            self.stats.skipped += 1
            return
        key = base64.b64decode(key_b64)
        cipher = Fernet(key)
        encrypted_data = source.read_bytes()
        if self.dry_run:
            logger.debug("[DRY-RUN] Would decrypt %s", source)
            self.stats.restored += 1
            self.stats.bytes_processed += len(encrypted_data)
            return
        try:
            decrypted = cipher.decrypt(encrypted_data)
        except InvalidToken as exc:
            raise DecryptionError("Invalid key for file: %s" % source) from exc
        target = Path(str(source).replace(".pazuzu", ""))
        target.write_bytes(decrypted)
        source.unlink()
        self.stats.restored += 1
        self.stats.bytes_processed += len(decrypted)
