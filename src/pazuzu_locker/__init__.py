"""Pazuzu Locker package - file encryption toolkit with remote manifest storage.

This module exposes the high level configuration helpers and workflow functions
that power the `pazuzu_locker` CLI entry points. Downstream code can import
these objects to build custom automation around encryption and decryption.

Example:
    >>> from pazuzu_locker import load_config
    >>> config = load_config()
    >>> print(config.log_level)
    INFO
"""

from __future__ import annotations

from .config import AppConfig, ProviderConfig, load_config
from .crypto import decrypt_data, encrypt_data, generate_key
from .logging import configure_logging, get_logger
from .manifest import Manifest, ManifestEntry
from .providers import create_provider
from .workflow import decrypt_from_manifest, encrypt_directory

__all__ = [
    "AppConfig",
    "ProviderConfig",
    "load_config",
    "generate_key",
    "encrypt_data",
    "decrypt_data",
    "configure_logging",
    "get_logger",
    "Manifest",
    "ManifestEntry",
    "create_provider",
    "encrypt_directory",
    "decrypt_from_manifest",
]

__version__ = "0.2.0"
