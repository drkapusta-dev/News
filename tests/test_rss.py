from io import BytesIO

from poslovnipuls_pipeline.config import SourceConfig
from poslovnipuls_pipeline.rss import fetch_feed_items


RSS_XML = b"""
<rss><channel>
  <item>
    <title>News A</title>
    <link>https://example.com/a</link>
    <guid>id-a</guid>
    <description>Hello A</description>
    <pubDate>Wed, 25 Mar 2026 10:00:00 GMT</pubDate>
  </item>
</channel></rss>
"""


class _Response(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_fetch_feed_items(monkeypatch) -> None:
    def fake_urlopen(url: str, timeout: int):
        assert url == "https://example.com/rss"
        assert timeout == 20
        return _Response(RSS_XML)

    monkeypatch.setattr("poslovnipuls_pipeline.rss.urlopen", fake_urlopen)

    source = SourceConfig(name="Example", rss_url="https://example.com/rss", rights_mode="summary_only")
    items = fetch_feed_items(source)

    assert len(items) == 1
    assert items[0].title == "News A"
    assert items[0].link == "https://example.com/a"
    assert items[0].rights_mode == "summary_only"
