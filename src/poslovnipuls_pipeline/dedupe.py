from __future__ import annotations

import hashlib
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .models import FeedItem


TRACKING_QUERY_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split()).strip().lower()


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    cleaned_query = urlencode(
        sorted((k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in TRACKING_QUERY_PARAMS)
    )
    normalized_path = parsed.path.rstrip("/") or "/"
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            normalized_path,
            "",
            cleaned_query,
            "",
        )
    )


def make_dedupe_key(item: FeedItem) -> str:
    base = "|".join(
        [
            _normalize_whitespace(item.source_name),
            _normalize_url(item.link),
            _normalize_whitespace(item.title),
            _normalize_whitespace(item.content),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
