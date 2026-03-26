from __future__ import annotations

from pathlib import Path


def iter_owned_content(content_dir: str | Path) -> list[Path]:
    base = Path(content_dir)
    if not base.exists():
        return []

    files = [*base.glob("*.md"), *base.glob("*.txt")]
    return sorted(files)
