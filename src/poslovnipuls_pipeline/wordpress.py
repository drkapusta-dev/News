from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .config import WordPressConfig
from .models import ProcessedItem

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WordPressDraftResult:
    post_id: int
    status: str


def build_draft_payload(item: ProcessedItem) -> dict[str, object]:
    summary_en = item.summary_en or ""
    summary_hr = item.summary_hr or ""

    content_blocks = [
        f"<p><strong>Source:</strong> <a href=\"{item.item.link}\">{item.item.link}</a></p>",
        f"<p>{summary_en}</p>",
        f"<p>{summary_hr}</p>",
    ]

    return {
        "title": item.item.title,
        "status": "draft",
        "content": "\n".join(content_blocks),
        "meta": {
            "source_name": item.item.source_name,
            "source_url": item.item.link,
            "rights_mode": item.item.rights_mode,
        },
    }


def create_draft(config: WordPressConfig, item: ProcessedItem, timeout: int = 20) -> WordPressDraftResult:
    if config.default_status != "draft":
        raise ValueError("Safety check failed: WordPress posts must remain drafts.")

    url = f"{config.base_url}/wp-json/wp/v2/posts"
    payload = build_draft_payload(item)
    payload["status"] = "draft"

    auth_raw = f"{config.username}:{config.app_password}".encode("utf-8")
    auth_header = base64.b64encode(auth_raw).decode("ascii")

    req = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        logger.error("WordPress API error %s body=%s", exc.code, body)
        raise

    status = str(data.get("status", "draft"))
    if status != "draft":
        raise ValueError(f"Safety check failed: WordPress returned non-draft status={status!r}.")
    return WordPressDraftResult(post_id=int(data["id"]), status="draft")
