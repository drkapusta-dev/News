from __future__ import annotations

import logging
import sqlite3

from .models import ProcessedItem

logger = logging.getLogger(__name__)


def insert_item(conn: sqlite3.Connection, processed: ProcessedItem) -> bool:
    try:
        conn.execute(
            """
            INSERT INTO items (
                source_name, source_url, external_id, title, link,
                published_at, content, summary_en, summary_hr,
                summary_only, dedupe_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                processed.item.source_name,
                processed.item.source_url,
                processed.item.external_id,
                processed.item.title,
                processed.item.link,
                processed.item.published_at,
                processed.item.content,
                processed.summary_en,
                processed.summary_hr,
                int(processed.item.summary_only),
                processed.dedupe_key,
            ),
        )
        return True
    except sqlite3.IntegrityError:
        logger.info("Deduped item skipped: %s", processed.item.link)
        return False


def mark_wordpress_draft(
    conn: sqlite3.Connection,
    dedupe_key: str,
    post_id: int,
    status: str,
) -> None:
    conn.execute(
        """
        UPDATE items
        SET wordpress_post_id = ?, wordpress_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE dedupe_key = ?
        """,
        (post_id, status, dedupe_key),
    )
