from __future__ import annotations

import logging

from .config import AppConfig
from .db import get_connection
from .dedupe import make_dedupe_key
from .localization import CroatianLocalizer
from .models import ProcessedItem
from .repository import insert_item, mark_wordpress_draft
from .rss import fetch_feed_items
from .summarization import Summarizer
from .wordpress import create_draft

logger = logging.getLogger(__name__)


def run_pipeline(config: AppConfig) -> None:
    summarizer = Summarizer()
    localizer = CroatianLocalizer()

    with get_connection(config.db_path) as conn:
        for source in config.sources:
            if not source.enabled:
                logger.info("Skipping disabled source: %s", source.name)
                continue
            try:
                feed_items = fetch_feed_items(source)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed fetching source=%s error=%s", source.name, exc)
                continue

            for item in feed_items:
                processed = ProcessedItem(item=item, dedupe_key=make_dedupe_key(item))
                processed.summary_en = summarizer.summarize_en(item)
                processed.summary_hr = localizer.localize_summary(processed.summary_en)

                inserted = insert_item(conn, processed)
                if not inserted:
                    continue

                if config.wordpress is None:
                    continue

                try:
                    wp_result = create_draft(config.wordpress, processed)
                    mark_wordpress_draft(
                        conn,
                        dedupe_key=processed.dedupe_key,
                        post_id=wp_result.post_id,
                        status=wp_result.status,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Failed WordPress draft creation for %s: %s", item.link, exc)
