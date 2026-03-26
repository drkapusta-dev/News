from __future__ import annotations

from pathlib import Path

from .config import SourceConfig
from .models import FeedItem


def iter_owned_content(content_dir: str | Path) -> list[Path]:
    base = Path(content_dir)
    if not base.exists():
        return []

    files = [*base.glob("*.md"), *base.glob("*.txt")]
    return sorted(files)


def load_owned_items(source: SourceConfig) -> list[FeedItem]:
    if source.content_dir is None:
        raise ValueError(f"owned_manual source {source.name!r} is missing content_dir")

    items: list[FeedItem] = []
    for file_path in iter_owned_content(source.content_dir):
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0].lstrip("# ") if lines else file_path.stem
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else text
        items.append(
            FeedItem(
                source_name=source.name,
                source_url=str(source.content_dir),
                external_id=file_path.name,
                title=title or file_path.stem,
                link=f"owned://{file_path.name}",
                published_at=None,
                content=content,
                rights_mode=source.rights_mode,
            )
        )
    return items
