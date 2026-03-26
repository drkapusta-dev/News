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


def _build_summary_only_content(item: ProcessedItem) -> str:
    summary_hr = (item.summary_hr or "").strip()
    summary_en = (item.summary_en or "").strip()
    why_matters = "Ova tema je važna jer može utjecati na poslovne odluke, tržište i operativne prioritete."

    blocks = [
        "<p><strong>Kratki uvod:</strong> U nastavku donosimo sažetak ključnih informacija iz izvora.</p>",
        f"<p><strong>Sažetak (HR):</strong> {summary_hr}</p>",
        f"<p><strong>Zašto je važno:</strong> {why_matters}</p>",
        f"<p><strong>Izvor:</strong> {item.item.source_name}</p>",
        f"<p><strong>Original URL:</strong> <a href=\"{item.item.link}\">{item.item.link}</a></p>",
    ]
    if summary_en:
        blocks.append(f"<p><strong>English summary:</strong> {summary_en}</p>")
    return "\n".join(blocks)


def _build_full_publish_content(item: ProcessedItem) -> str:
    return "\n".join(
        [
            "<p><strong>Uvod (HR):</strong> Cjelovitiji prikaz sadržaja za urednički pregled.</p>",
            f"<p><strong>Sažetak (HR):</strong> {(item.summary_hr or '').strip()}</p>",
            f"<p><strong>Summary (EN):</strong> {(item.summary_en or '').strip()}</p>",
            f"<p><strong>Original naslov:</strong> {item.item.title}</p>",
            f"<p><strong>Sadržaj:</strong> {item.item.content[:1200]}</p>",
            f"<p><strong>Izvor:</strong> {item.item.source_name}</p>",
            f"<p><strong>Original URL:</strong> <a href=\"{item.item.link}\">{item.item.link}</a></p>",
        ]
    )


def build_draft_payload(item: ProcessedItem) -> dict[str, object] | None:
    if item.item.rights_mode == "disabled":
        return None

    title = item.item.title.strip()
    if not title:
        return None

    if item.item.rights_mode == "summary_only":
        content = _build_summary_only_content(item)
    else:
        content = _build_full_publish_content(item)

    content = content.strip()
    if not content:
        return None

    payload: dict[str, object] = {
        "title": title,
        "status": "draft",
        "content": content,
        "meta": {
            "source_name": item.item.source_name,
            "source_url": item.item.link,
            "rights_mode": item.item.rights_mode,
        },
    }
    return payload


def _validate_payload(payload: dict[str, object] | None) -> bool:
    if payload is None:
        return False
    status = payload.get("status")
    if status != "draft":
        return False
    title = str(payload.get("title", "")).strip()
    content = str(payload.get("content", "")).strip()
    return bool(title and content)


def create_draft(config: WordPressConfig, item: ProcessedItem, timeout: int = 20) -> WordPressDraftResult:
    if config.default_status != "draft":
        raise ValueError("Safety check failed: WordPress posts must remain drafts.")

    payload = build_draft_payload(item)
    if not _validate_payload(payload):
        logger.error("Skipping malformed or empty WordPress payload for link=%s", item.item.link)
        raise ValueError("Malformed WordPress payload")

    url = f"{config.base_url}/wp-json/wp/v2/posts"

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
