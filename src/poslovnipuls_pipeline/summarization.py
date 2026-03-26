from __future__ import annotations

from .models import FeedItem


class Summarizer:
    """Placeholder summarizer interface for English summaries."""

    def summarize_en(self, item: FeedItem) -> str:
        snippet = item.content[:280].strip()
        return f"Summary: {snippet}" if snippet else f"Summary: {item.title}"
