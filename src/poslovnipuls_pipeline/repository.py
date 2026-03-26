from __future__ import annotations

import logging
import sqlite3

from .models import FeedItem, ProcessedItem

logger = logging.getLogger(__name__)


def insert_item(conn: sqlite3.Connection, processed: ProcessedItem) -> bool:
    try:
        conn.execute(
            """
            INSERT INTO items (
                source_name, source_url, external_id, title, link,
                published_at, content, summary_en, summary_hr,
                rights_mode, dedupe_key
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
                processed.item.rights_mode,
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


def get_pending_wordpress_items(conn: sqlite3.Connection) -> list[ProcessedItem]:
    rows = conn.execute(
        """
        SELECT source_name, source_url, external_id, title, link, published_at, content,
               summary_en, summary_hr, rights_mode, dedupe_key
        FROM items
        WHERE wordpress_post_id IS NULL
        ORDER BY id ASC
        """
    ).fetchall()

    return [
        ProcessedItem(
            item=FeedItem(
                source_name=row["source_name"],
                source_url=row["source_url"],
                external_id=row["external_id"],
                title=row["title"],
                link=row["link"],
                published_at=row["published_at"],
                content=row["content"] or "",
                rights_mode=row["rights_mode"],
            ),
            dedupe_key=row["dedupe_key"],
            summary_en=row["summary_en"],
            summary_hr=row["summary_hr"],
        )
        for row in rows
    ]
