"""Remote manifest providers for Pazuzu Locker."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import requests

from .config import ProviderConfig


class ManifestProvider(Protocol):
    """Protocol for manifest upload/download providers."""

    def upload_manifest(self, manifest_path: Path) -> tuple[str, str]:
        """Upload a manifest file and return (id, url)."""

    def download_manifest(self, manifest_id: str) -> str:
        """Download manifest content as string."""


class PixelDrainProvider:
    """PixelDrain implementation of the manifest provider."""

    def __init__(self, config: ProviderConfig, session: requests.Session | None = None) -> None:
        self.config = config
        self.session = session or requests.Session()

    def upload_manifest(self, manifest_path: Path) -> tuple[str, str]:
        with manifest_path.open("rb") as handle:
            files = {"file": (manifest_path.name, handle)}
            response = self.session.post(
                self.config.upload_endpoint,
                files=files,
                timeout=30,
            )
        response.raise_for_status()
        data = response.json()
        if not data.get("success", False):
            raise RuntimeError(f"Upload failed: {data}")
        manifest_id = data["id"]
        manifest_url = data.get("link", f"https://pixeldrain.com/u/{manifest_id}")
        return manifest_id, manifest_url

    def download_manifest(self, manifest_id: str) -> str:
        download_url = self.config.download_endpoint.format(id=manifest_id)
        response = self.session.get(download_url, timeout=30)
        response.raise_for_status()
        return response.text


def create_provider(config: ProviderConfig) -> ManifestProvider:
    """Factory to create a manifest provider based on config."""

    if config.name.lower() == "pixeldrain":
        return PixelDrainProvider(config=config)

    raise ValueError(f"Unsupported provider: {config.name}")
