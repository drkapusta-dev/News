from __future__ import annotations

import logging
from pathlib import Path

from .config import AppConfig, load_config
from .db import get_connection
from .dedupe import make_dedupe_key
from .localization import CroatianLocalizer
from .models import FeedItem, ProcessedItem
from .owned_content import load_owned_items
from .repository import get_pending_wordpress_items, insert_item, mark_wordpress_draft
from .rss import fetch_feed_items
from .summarization import Summarizer
from .wordpress import create_draft

logger = logging.getLogger(__name__)


def _read_source_items(source) -> list[FeedItem]:
    if source.source_type in {"rss", "medium_rss"}:
        return fetch_feed_items(source)
    if source.source_type == "owned_manual":
        return load_owned_items(source)
    raise ValueError(f"Unsupported source_type={source.source_type!r}")


def run_ingest(config: AppConfig) -> int:
    summarizer = Summarizer()
    localizer = CroatianLocalizer()
    inserted_count = 0

    with get_connection(config.db_path) as conn:
        for source in config.sources:
            if not source.enabled:
                logger.info("Skipping disabled source: %s", source.name)
                continue

            try:
                source_items = _read_source_items(source)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed fetching source=%s error=%s", source.name, exc)
                continue

            for item in source_items:
                processed = ProcessedItem(item=item, dedupe_key=make_dedupe_key(item))
                processed.summary_en = summarizer.summarize_en(item)
                processed.summary_hr = localizer.localize_summary(processed.summary_en)

                inserted = insert_item(conn, processed)
                if inserted:
                    inserted_count += 1

    logger.info("Ingest completed: inserted=%s", inserted_count)
    return inserted_count


def run_publish(config: AppConfig) -> int:
    if config.wordpress is None:
        logger.warning("WordPress config missing. Skipping publish phase.")
        return 0

    created_count = 0
    with get_connection(config.db_path) as conn:
        pending_items = get_pending_wordpress_items(conn)
        for processed in pending_items:
            try:
                wp_result = create_draft(config.wordpress, processed)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed WordPress draft creation for %s: %s", processed.item.link, exc)
                continue

            mark_wordpress_draft(
                conn,
                dedupe_key=processed.dedupe_key,
                post_id=wp_result.post_id,
                status=wp_result.status,
            )
            created_count += 1

    logger.info("Publish completed: drafts_created=%s", created_count)
    return created_count


def run_pipeline(config: AppConfig) -> None:
    run_ingest(config)
    run_publish(config)


def healthcheck(config: AppConfig | None = None, config_path: str | Path = "sources.json") -> list[str]:
    messages: list[str] = []
    registry_path = Path(config_path)

    dotenv_path = Path(".env")
    messages.append(".env present: yes" if dotenv_path.exists() else ".env present: no (.env file not found)")

    if registry_path.exists():
        messages.append(f"source registry present: yes ({registry_path})")
    else:
        messages.append(f"source registry present: no ({registry_path} missing)")
        return messages

    if config is None:
        try:
            config = load_config(registry_path)
            messages.append("source registry parse: ok")
        except Exception as exc:  # noqa: BLE001
            messages.append(f"source registry parse: failed ({exc})")
            return messages

    if config.db_path.exists():
        messages.append(f"DB present: yes ({config.db_path})")
    else:
        messages.append(f"DB present: no ({config.db_path} missing; run scripts/init_db.py)")

    owned_dirs = [s.content_dir for s in config.sources if s.source_type == "owned_manual" and s.content_dir is not None]
    if owned_dirs:
        for directory in owned_dirs:
            exists = directory.exists()
            messages.append(f"owned content directory present: {'yes' if exists else 'no'} ({directory})")
    else:
        messages.append("owned content directory present: no owned_manual source configured")

    messages.append("WordPress credentials present: yes" if config.wordpress else "WordPress credentials present: no")
    return messages
