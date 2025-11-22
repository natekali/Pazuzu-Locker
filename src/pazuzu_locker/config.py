"""Configuration management with typed models and multi-source loading."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

try:  # pragma: no cover - fallback for Python < 3.11
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib

ENV_PREFIX = "PAZUZU_"
ENV_NESTED_DELIMITER = "__"


class ProviderConfig(BaseModel):
    """Configuration for remote manifest storage providers."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(default="pixeldrain")
    upload_endpoint: str = Field(default="https://pixeldrain.com/api/file")
    download_endpoint: str = Field(default="https://pixeldrain.com/api/file/{id}")


class AppConfig(BaseModel):
    """Validated configuration for the Pazuzu Locker workflows."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    start_dir: Path = Field(default_factory=Path.cwd)
    manifest_dir: Path = Field(default_factory=lambda: Path.cwd() / "manifests")
    include_globs: tuple[str, ...] = ("**/*",)
    exclude_globs: tuple[str, ...] = ("**/*.pazuzu",)
    dry_run: bool = True
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    manifest_id: str | None = Field(default=None, alias="pxfile_id")
    provider: ProviderConfig = Field(default_factory=ProviderConfig)

    @field_validator("start_dir", "manifest_dir", mode="before")
    @classmethod
    def _expand_path(cls, value: str | Path) -> Path:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        return path

    @field_validator("include_globs", "exclude_globs", mode="before")
    @classmethod
    def _ensure_tuple(cls, value: Any) -> tuple[str, ...]:
        if value is None:
            return tuple()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple)):
            return tuple(str(item) for item in value)
        raise TypeError("Glob patterns must be a string or sequence of strings")

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        upper = str(value).upper()
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {sorted(allowed)}")
        return upper

    @field_validator("log_format", mode="before")
    @classmethod
    def _normalize_log_format(cls, value: str) -> str:
        lower = str(value).lower()
        allowed = {"json", "text"}
        if lower not in allowed:
            raise ValueError(f"log_format must be one of {sorted(allowed)}")
        return lower


def discover_config_file(explicit_path: Path | None = None) -> Path | None:
    """Discover the configuration file path using common conventions."""

    candidates: list[Path] = []

    if explicit_path is not None:
        candidates.append(Path(explicit_path).expanduser())

    env_override = os.environ.get("PAZUZU_CONFIG_FILE") or os.environ.get("PAZUZU_CONFIG")
    if env_override:
        candidates.append(Path(env_override).expanduser())

    candidates.append(Path.cwd() / "config" / "pazuzu.toml")
    package_dir = Path(__file__).resolve().parent
    project_root = package_dir.parents[1]
    candidates.append(project_root / "config" / "pazuzu.toml")

    for path in candidates:
        try_path = path
        if try_path.exists() and try_path.is_file():
            return try_path
    return None


def load_config(
    config_file: Path | str | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> AppConfig:
    """Load configuration from TOML, environment variables, and overrides."""

    config_path = discover_config_file(Path(config_file) if config_file else None)
    data: dict[str, Any] = {}

    if config_path:
        with config_path.open("rb") as handle:
            toml_data = tomllib.load(handle)
            data = toml_data.get("pazuzu", toml_data)

    env_data = _load_env()
    data = _merge_dicts(data, env_data)

    if overrides:
        data = _merge_dicts(data, overrides)

    return AppConfig.model_validate(data)


def _merge_dicts(base: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overrides.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, Mapping)
        ):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_env() -> dict[str, Any]:
    env_data: dict[str, Any] = {}
    for env_key, env_value in os.environ.items():
        if not env_key.startswith(ENV_PREFIX):
            continue
        path_parts = env_key[len(ENV_PREFIX) :].lower().split(ENV_NESTED_DELIMITER)
        target = env_data
        for part in path_parts[:-1]:
            target = target.setdefault(part, {})  # type: ignore[assignment]
        target[path_parts[-1]] = _coerce_value(env_value)
    return env_data


def _coerce_value(value: str) -> Any:
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            continue
    if "," in value:
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if len(parts) > 1:
            return parts
    return value
