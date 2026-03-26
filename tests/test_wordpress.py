import pytest

from poslovnipuls_pipeline.config import WordPressConfig
from poslovnipuls_pipeline.models import FeedItem, ProcessedItem
from poslovnipuls_pipeline.wordpress import build_draft_payload, create_draft


def _processed_item(rights_mode: str = "summary_only") -> ProcessedItem:
    feed_item = FeedItem(
        source_name="Example",
        source_url="https://example.com/rss",
        external_id="1",
        title="Sample Title",
        link="https://example.com/post",
        published_at=None,
        content="long content",
        rights_mode=rights_mode,
    )
    return ProcessedItem(
        item=feed_item,
        dedupe_key="k1",
        summary_en="English summary",
        summary_hr="Hrvatski sazetak",
    )


def test_build_draft_payload_summary_only_structure() -> None:
    payload = build_draft_payload(_processed_item("summary_only"))

    assert payload is not None
    assert payload["status"] == "draft"
    assert "Sažetak (HR)" in str(payload["content"])
    assert "Zašto je važno" in str(payload["content"])
    assert "Original URL" in str(payload["content"])


def test_build_draft_payload_full_publish_structure() -> None:
    payload = build_draft_payload(_processed_item("full_publish"))

    assert payload is not None
    assert payload["status"] == "draft"
    assert "Summary (EN)" in str(payload["content"])
    assert "Sadržaj" in str(payload["content"])


def test_build_draft_payload_skips_disabled() -> None:
    assert build_draft_payload(_processed_item("disabled")) is None


def test_create_draft_rejects_non_draft_default() -> None:
    config = WordPressConfig(
        base_url="https://wp.test",
        username="u",
        app_password="p",
        default_status="publish",
    )

    with pytest.raises(ValueError):
        create_draft(config, _processed_item())


def test_create_draft_rejects_non_draft_api_response(monkeypatch) -> None:
    config = WordPressConfig(
        base_url="https://wp.test",
        username="u",
        app_password="p",
        default_status="draft",
    )

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return None

        def read(self) -> bytes:
            return b'{"id": 1, "status": "publish"}'

    def fake_urlopen(req, timeout: int):
        assert timeout == 20
        return _Response()

    monkeypatch.setattr("poslovnipuls_pipeline.wordpress.urlopen", fake_urlopen)

    with pytest.raises(ValueError):
        create_draft(config, _processed_item())
