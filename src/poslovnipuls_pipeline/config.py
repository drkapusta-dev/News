from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


RightsMode = Literal["summary_only", "full_publish", "disabled"]
SourceType = Literal["rss", "medium_rss", "owned_manual"]


@dataclass(slots=True)
class SourceConfig:
    name: str
    source_type: SourceType
    language: str = "en"
    rights_mode: RightsMode = "summary_only"
    enabled: bool = True
    rss_url: str | None = None
    content_dir: Path | None = None


@dataclass(slots=True)
class WordPressConfig:
    base_url: str
    username: str
    app_password: str
    default_status: str = "draft"


@dataclass(slots=True)
class AppConfig:
    db_path: Path
    sources: list[SourceConfig]
    wordpress: WordPressConfig | None = None


ALLOWED_RIGHTS_MODES = {"summary_only", "full_publish", "disabled"}
ALLOWED_SOURCE_TYPES = {"rss", "medium_rss", "owned_manual"}


def _parse_rights_mode(source: dict[str, Any]) -> RightsMode:
    if "rights_mode" not in source:
        raise ValueError(
            f"Missing required 'rights_mode' for source {source.get('name', '<unknown>')!r}."
        )

    mode = str(source["rights_mode"]).strip()
    if mode not in ALLOWED_RIGHTS_MODES:
        raise ValueError(
            "Unsupported rights_mode for source "
            f"{source.get('name', '<unknown>')!r}: {mode!r}. "
            "Allowed: summary_only, full_publish, disabled."
        )
    return mode  # type: ignore[return-value]


def _parse_source_type(source: dict[str, Any]) -> SourceType:
    raw = str(source.get("source_type", "rss")).strip()
    if raw not in ALLOWED_SOURCE_TYPES:
        raise ValueError(
            f"Unsupported source_type for source {source.get('name', '<unknown>')!r}: {raw!r}. "
            "Allowed: rss, medium_rss, owned_manual."
        )
    return raw  # type: ignore[return-value]


def _validate_sources(raw_sources: list[dict[str, Any]]) -> list[SourceConfig]:
    validated: list[SourceConfig] = []
    for source in raw_sources:
        if "name" not in source:
            raise ValueError("Each source must include 'name'.")

        rights_mode = _parse_rights_mode(source)
        source_type = _parse_source_type(source)
        enabled = bool(source.get("enabled", True)) and rights_mode != "disabled"

        rss_url: str | None = None
        content_dir: Path | None = None
        if source_type in {"rss", "medium_rss"}:
            rss_url = str(source.get("rss_url", "")).strip()
            if not rss_url:
                raise ValueError(
                    f"Source {source['name']!r} with source_type={source_type!r} must include rss_url."
                )
        elif source_type == "owned_manual":
            raw_dir = str(source.get("content_dir", "")).strip()
            if not raw_dir:
                raise ValueError(
                    f"Source {source['name']!r} with source_type='owned_manual' must include content_dir."
                )
            content_dir = Path(raw_dir)

        validated.append(
            SourceConfig(
                name=str(source["name"]),
                source_type=source_type,
                language=str(source.get("language", "en")),
                rights_mode=rights_mode,
                enabled=enabled,
                rss_url=rss_url,
                content_dir=content_dir,
            )
        )
    return validated


def _load_dotenv(path: Path = Path(".env")) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _load_registry_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Source registry not found: {path}")

    if path.suffix.lower() != ".json":
        raise ValueError(
            "Only JSON source registry is supported in offline mode. "
            f"Please convert {path.name} to JSON."
        )

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Config root must be a JSON object.")
    return payload


def load_config(config_path: str | Path = "sources.json") -> AppConfig:
    path = Path(config_path)
    payload = _load_registry_payload(path)

    raw_sources = payload.get("sources", [])
    if not isinstance(raw_sources, list):
        raise ValueError("'sources' must be a list.")

    dotenv_values = _load_dotenv()
    wp_raw = payload.get("wordpress") or {}
    wp_base_url = str(wp_raw.get("base_url") or os.environ.get("WP_BASE_URL") or dotenv_values.get("WP_BASE_URL") or "").strip()
    wp_username = str(wp_raw.get("username") or os.environ.get("WP_USERNAME") or dotenv_values.get("WP_USERNAME") or "").strip()
    wp_password = str(wp_raw.get("app_password") or os.environ.get("WP_APP_PASSWORD") or dotenv_values.get("WP_APP_PASSWORD") or "").strip()

    wordpress: WordPressConfig | None = None
    if wp_base_url or wp_username or wp_password:
        if not (wp_base_url and wp_username and wp_password):
            raise ValueError("WordPress config is partial. Set base_url, username and app_password.")
        wordpress = WordPressConfig(
            base_url=wp_base_url.rstrip("/"),
            username=wp_username,
            app_password=wp_password,
            default_status=str(wp_raw.get("default_status", "draft")),
        )
        if wordpress.default_status != "draft":
            raise ValueError("WordPress default_status must remain 'draft'.")

    db_path = Path(payload.get("database", {}).get("path", "data/app.db"))

    return AppConfig(
        db_path=db_path,
        sources=_validate_sources(raw_sources),
        wordpress=wordpress,
    )
