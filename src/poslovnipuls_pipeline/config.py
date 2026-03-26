from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any



@dataclass(slots=True)
class SourceConfig:
    name: str
    rss_url: str
    language: str = "en"
    summary_only: bool = True
    enabled: bool = True


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


def _validate_sources(raw_sources: list[dict[str, Any]]) -> list[SourceConfig]:
    validated: list[SourceConfig] = []
    for source in raw_sources:
        if "name" not in source or "rss_url" not in source:
            raise ValueError("Each source must include 'name' and 'rss_url'.")
        validated.append(
            SourceConfig(
                name=str(source["name"]),
                rss_url=str(source["rss_url"]),
                language=str(source.get("language", "en")),
                summary_only=bool(source.get("summary_only", True)),
                enabled=bool(source.get("enabled", True)),
            )
        )
    return validated


def load_config(config_path: str | Path = "sources.yaml") -> AppConfig:
    path = Path(config_path)
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to load sources.yaml") from exc

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    raw_sources = payload.get("sources", [])
    if not isinstance(raw_sources, list):
        raise ValueError("'sources' must be a list.")

    wp_raw = payload.get("wordpress")
    wordpress: WordPressConfig | None = None
    if wp_raw:
        wordpress = WordPressConfig(
            base_url=str(wp_raw["base_url"]).rstrip("/"),
            username=str(wp_raw["username"]),
            app_password=str(wp_raw["app_password"]),
            default_status=str(wp_raw.get("default_status", "draft")),
        )
        if wordpress.default_status != "draft":
            raise ValueError("WordPress default_status must remain 'draft'.")

    db_path = Path(payload.get("database", {}).get("path", "pipeline.db"))

    return AppConfig(
        db_path=db_path,
        sources=_validate_sources(raw_sources),
        wordpress=wordpress,
    )
