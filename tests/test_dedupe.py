from poslovnipuls_pipeline.dedupe import make_dedupe_key
from poslovnipuls_pipeline.models import FeedItem


def test_dedupe_key_is_stable() -> None:
    item = FeedItem(
        source_name="Source",
        source_url="https://example.com/rss",
        external_id="abc",
        title="Hello",
        link="https://example.com/post?utm_source=x",
        published_at=None,
        content="content",
        rights_mode="summary_only",
    )
    assert make_dedupe_key(item) == make_dedupe_key(item)


def test_dedupe_key_normalizes_tracking_query_params() -> None:
    item1 = FeedItem("Source", "https://example.com/rss", "abc", "Hello", "https://example.com/post?utm_source=x", None, "content", "summary_only")
    item2 = FeedItem("Source", "https://example.com/rss", "abc", "Hello", "https://example.com/post", None, "content", "summary_only")

    assert make_dedupe_key(item1) == make_dedupe_key(item2)
