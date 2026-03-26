from __future__ import annotations

import hashlib

from .models import FeedItem


def make_dedupe_key(item: FeedItem) -> str:
    base = "|".join(
        [
            item.source_name.strip().lower(),
            (item.external_id or "").strip().lower(),
            item.link.strip().lower(),
            item.title.strip().lower(),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
