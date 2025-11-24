from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PLACEHOLDER_VALUES = {"", None, "CHANGE_HERE"}

try:  # pragma: no cover - defensive import
    from conf import param as _CONF_PARAM
except Exception:  # pragma: no cover - user may remove conf.py
    _CONF_PARAM = {}


class ConfigError(Exception):
    """Raised when the CLI configuration cannot be resolved."""


@dataclass
class LockerConfig:
    """Represents the resolved configuration for the CLI commands."""

    start_dir: Optional[Path]
    manifest_path: Optional[Path]
    provider: str
    pxfile_id: Optional[str]
    log_level: str
    missing: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["start_dir"] = str(self.start_dir) if self.start_dir else None
        data["manifest_path"] = str(self.manifest_path) if self.manifest_path else None
        data["missing"] = list(self.missing)
        return data

    def require_path(self, field_name: str) -> Path:
        value = getattr(self, field_name)
        if value is None:
            raise ConfigError(
                f"'{field_name}' is not configured. Provide --{field_name.replace('_', '-')} or update conf.py."
            )
        return value

    def require_px_id(self) -> str:
        if not self.pxfile_id:
            raise ConfigError(
                "PixelDrain file ID is missing. Provide --px-id or set 'pxfile_id' in conf.py."
            )
        return self.pxfile_id


def _sanitize(value: Optional[str]) -> Optional[str]:
    if value in PLACEHOLDER_VALUES:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def _resolve_path(value: Optional[str], *, base: Optional[Path] = None) -> Optional[Path]:
    if value is None:
        return None
    raw_path = Path(value).expanduser()
    if raw_path.is_absolute():
        return raw_path.resolve()
    base_path = base or Path.cwd()
    return (base_path / raw_path).resolve()


def load_config(
    *,
    start_dir: Optional[str | Path] = None,
    manifest_path: Optional[str | Path] = None,
    provider: Optional[str] = None,
    pxfile_id: Optional[str] = None,
    log_level: Optional[str] = None,
) -> LockerConfig:
    """Load the configuration by merging CLI overrides with conf.py values."""

    missing: Tuple[str, ...]
    missing_list = []

    start_dir_override = _sanitize(str(start_dir)) if start_dir is not None else None
    conf_start_dir = _sanitize(_CONF_PARAM.get("start_dir"))
    resolved_start_dir = _resolve_path(start_dir_override or conf_start_dir)
    if resolved_start_dir is None:
        missing_list.append("start_dir")

    manifest_override = _sanitize(str(manifest_path)) if manifest_path is not None else None
    conf_manifest = _sanitize(_CONF_PARAM.get("tmp_csv"))
    resolved_manifest = _resolve_path(
        manifest_override or conf_manifest,
        base=resolved_start_dir,
    )
    if resolved_manifest is None:
        missing_list.append("manifest_path")

    provider_value = (provider or _CONF_PARAM.get("provider") or "pixeldrain").lower()

    px_id_value = pxfile_id or _sanitize(_CONF_PARAM.get("pxfile_id"))

    log_level_value = (log_level or "INFO").upper()

    missing = tuple(missing_list)

    return LockerConfig(
        start_dir=resolved_start_dir,
        manifest_path=resolved_manifest,
        provider=provider_value,
        pxfile_id=px_id_value,
        log_level=log_level_value,
        missing=missing,
    )


def write_template(destination: Path, *, overwrite: bool = False) -> Path:
    """Write a configuration template to the given path."""

    destination = destination.expanduser().resolve()
    if destination.exists() and not overwrite:
        raise ConfigError(
            f"Config template already exists at {destination}. Use --overwrite to replace it."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    template = (
        "param = {\n"
        "    'start_dir': '/path/to/target',\n"
        "    'tmp_csv': '/tmp/pazuzu-manifest.csv',\n"
        "    'pxfile_id': 'PIXELDRAIN_FILE_ID'\n"
        "}\n"
    )
    destination.write_text(template, encoding="utf-8")
    return destination
