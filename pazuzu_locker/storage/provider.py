from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import requests


class ProviderError(Exception):
    """Raised when a manifest provider fails."""


@dataclass
class ProviderResult:
    provider: str
    destination: str
    metadata: Dict[str, Any]


class ManifestProvider:
    name: str

    def finalize_upload(self, manifest_path: Path) -> ProviderResult:  # pragma: no cover - interface
        raise NotImplementedError

    def fetch_manifest(self, identifier: str) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class PixelDrainProvider(ManifestProvider):
    name = "pixeldrain"
    upload_url = "https://pixeldrain.com/api/file"
    download_url = "https://pixeldrain.com/api/file/{id}"

    def finalize_upload(self, manifest_path: Path) -> ProviderResult:
        if not manifest_path.exists():
            raise ProviderError(f"Manifest file not found: {manifest_path}")
        with manifest_path.open("rb") as handle:
            response = requests.post(
                self.upload_url,
                files={"file": (manifest_path.name, handle)},
                timeout=60,
            )
        try:
            data = response.json()
        except json.JSONDecodeError as exc:  # pragma: no cover - network failure scenario
            raise ProviderError("PixelDrain response was not valid JSON") from exc
        if not data.get("success"):
            raise ProviderError(data.get("message", "Unable to upload manifest to PixelDrain"))
        manifest_path.unlink(missing_ok=True)
        px_id = data["id"]
        return ProviderResult(
            provider=self.name,
            destination=f"https://pixeldrain.com/u/{px_id}",
            metadata={"px_id": px_id},
        )

    def fetch_manifest(self, identifier: str) -> str:
        url = self.download_url.format(id=identifier)
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            raise ProviderError(
                f"PixelDrain returned {response.status_code} for id '{identifier}'"
            )
        return response.text


class LocalProvider(ManifestProvider):
    name = "local"

    def finalize_upload(self, manifest_path: Path) -> ProviderResult:
        if not manifest_path.exists():
            raise ProviderError(f"Manifest file not found: {manifest_path}")
        return ProviderResult(
            provider=self.name,
            destination=str(manifest_path),
            metadata={"bytes": manifest_path.stat().st_size},
        )

    def fetch_manifest(self, identifier: str) -> str:
        path = Path(identifier).expanduser().resolve()
        if not path.exists():
            raise ProviderError(f"Manifest file not found at {path}")
        return path.read_text(encoding="utf-8")


def get_provider(name: str) -> ManifestProvider:
    normalized = (name or "pixeldrain").lower()
    providers = {
        "pixeldrain": PixelDrainProvider(),
        "local": LocalProvider(),
    }
    if normalized not in providers:
        raise ProviderError(f"Unknown provider '{name}'. Choose from: {', '.join(providers)}")
    return providers[normalized]


def available_providers() -> Dict[str, ManifestProvider]:
    return {
        "pixeldrain": PixelDrainProvider(),
        "local": LocalProvider(),
    }
