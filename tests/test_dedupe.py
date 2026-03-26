from poslovnipuls_pipeline.dedupe import make_dedupe_key
from poslovnipuls_pipeline.models import FeedItem


def test_dedupe_key_is_stable() -> None:
    item = FeedItem(
        source_name="Source",
        source_url="https://example.com/rss",
        external_id="abc",
        title="Hello",
        link="https://example.com/post",
        published_at=None,
        content="content",
        summary_only=True,
    )
    assert make_dedupe_key(item) == make_dedupe_key(item)


def test_dedupe_key_changes_when_link_changes() -> None:
    item1 = FeedItem("Source", "https://example.com/rss", "abc", "Hello", "https://example.com/post1", None, "content", True)
    item2 = FeedItem("Source", "https://example.com/rss", "abc", "Hello", "https://example.com/post2", None, "content", True)

    assert make_dedupe_key(item1) != make_dedupe_key(item2)
