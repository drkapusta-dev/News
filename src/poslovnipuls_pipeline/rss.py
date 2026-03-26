from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Iterable
from urllib.request import urlopen

from .config import SourceConfig
from .models import FeedItem

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    return " ".join(text.replace("<", " ").replace(">", " ").split())


def fetch_feed_items(source: SourceConfig, timeout: int = 20) -> list[FeedItem]:
    if source.source_type not in {"rss", "medium_rss"}:
        raise ValueError(f"Unsupported feed fetch for source_type={source.source_type!r}")
    if not source.rss_url:
        raise ValueError(f"Missing rss_url for source {source.name!r}")

    with urlopen(source.rss_url, timeout=timeout) as response:  # noqa: S310
        content = response.read()

    root = ET.fromstring(content)
    items: list[FeedItem] = []
    for node in _iter_item_nodes(root):
        title = _node_text(node, "title") or "Untitled"
        link = _node_text(node, "link") or ""
        if not link:
            logger.warning("Skipping feed item without link: source=%s title=%s", source.name, title)
            continue
        description = _node_text(node, "description") or _node_text(node, "content") or ""
        guid = _node_text(node, "guid")
        pub_date = _node_text(node, "pubDate") or _node_text(node, "published")

        items.append(
            FeedItem(
                source_name=source.name,
                source_url=source.rss_url,
                external_id=guid,
                title=_strip_html(title),
                link=link.strip(),
                published_at=pub_date,
                content=_strip_html(description),
                rights_mode=source.rights_mode,
            )
        )
    return items


def _iter_item_nodes(root: ET.Element) -> Iterable[ET.Element]:
    return list(root.findall("./channel/item")) + list(root.findall("./entry"))


def _node_text(node: ET.Element, tag: str) -> str | None:
    found = node.find(tag)
    if found is not None and found.text:
        return found.text.strip()
    return None
