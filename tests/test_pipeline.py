from io import BytesIO

from poslovnipuls_pipeline.config import AppConfig, SourceConfig
from poslovnipuls_pipeline.db import create_schema, get_connection
from poslovnipuls_pipeline.pipeline import run_ingest


RSS_XML = b"""
<rss><channel>
  <item>
    <title>News A</title>
    <link>https://example.com/a?utm_source=x</link>
    <guid>id-a</guid>
    <description>Hello A</description>
  </item>
</channel></rss>
"""


class _Response(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_disabled_source_is_skipped(tmp_path) -> None:
    db_path = tmp_path / "app.db"
    create_schema(db_path)
    config = AppConfig(
        db_path=db_path,
        sources=[
            SourceConfig(
                name="Disabled",
                source_type="rss",
                rss_url="https://example.com/rss",
                rights_mode="disabled",
                enabled=False,
            )
        ],
        wordpress=None,
    )

    inserted = run_ingest(config)
    assert inserted == 0


def test_repeated_ingest_skips_duplicates(monkeypatch, tmp_path) -> None:
    def fake_urlopen(url: str, timeout: int):
        return _Response(RSS_XML)

    monkeypatch.setattr("poslovnipuls_pipeline.rss.urlopen", fake_urlopen)

    db_path = tmp_path / "app.db"
    create_schema(db_path)

    config = AppConfig(
        db_path=db_path,
        sources=[
            SourceConfig(
                name="RSS",
                source_type="rss",
                rss_url="https://example.com/rss",
                rights_mode="summary_only",
                enabled=True,
            )
        ],
        wordpress=None,
    )

    assert run_ingest(config) == 1
    assert run_ingest(config) == 0

    with get_connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM items").fetchone()
    assert int(row["c"]) == 1
