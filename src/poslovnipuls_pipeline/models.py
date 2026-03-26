from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FeedItem:
    source_name: str
    source_url: str
    external_id: str | None
    title: str
    link: str
    published_at: str | None
    content: str
    summary_only: bool


@dataclass(slots=True)
class ProcessedItem:
    item: FeedItem
    dedupe_key: str
    summary_en: str | None = None
    summary_hr: str | None = None
