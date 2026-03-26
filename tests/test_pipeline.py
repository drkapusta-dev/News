from pathlib import Path

from poslovnipuls_pipeline.config import AppConfig, SourceConfig
from poslovnipuls_pipeline.db import create_schema, get_connection
from poslovnipuls_pipeline.pipeline import run_ingest
from poslovnipuls_pipeline.wordpress import build_draft_payload


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


def test_repeated_ingest_skips_duplicates(tmp_path) -> None:
    db_path = tmp_path / "app.db"
    create_schema(db_path)

    config = AppConfig(
        db_path=db_path,
        sources=[
            SourceConfig(
                name="Local RSS",
                source_type="rss",
                rss_url="tests/fixtures/local_rss.xml",
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


def test_local_pilot_modes_generate_expected_draft_shapes(tmp_path) -> None:
    owned_dir = tmp_path / "owned"
    owned_dir.mkdir(parents=True)
    (owned_dir / "owned-note.md").write_text("# Owned Pilot\nOwned body for full publish checks.", encoding="utf-8")

    db_path = tmp_path / "app.db"
    create_schema(db_path)
    config = AppConfig(
        db_path=db_path,
        sources=[
            SourceConfig(
                name="Local RSS",
                source_type="rss",
                rss_url="tests/fixtures/local_rss.xml",
                rights_mode="summary_only",
                enabled=True,
            ),
            SourceConfig(
                name="Owned",
                source_type="owned_manual",
                content_dir=Path(owned_dir),
                rights_mode="full_publish",
                enabled=True,
            ),
        ],
        wordpress=None,
    )

    assert run_ingest(config) == 2

    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT source_name, title, link, rights_mode, summary_en, summary_hr, content, dedupe_key FROM items ORDER BY source_name"
        ).fetchall()

    assert len(rows) == 2

    rss_row = next(row for row in rows if row["source_name"] == "Local RSS")
    owned_row = next(row for row in rows if row["source_name"] == "Owned")

    rss_payload = build_draft_payload(
        _processed_from_row(rss_row)
    )
    owned_payload = build_draft_payload(
        _processed_from_row(owned_row)
    )

    assert rss_payload is not None
    assert rss_payload["status"] == "draft"
    assert "Zašto je važno" in str(rss_payload["content"])
    assert "Original URL" in str(rss_payload["content"])

    assert owned_payload is not None
    assert owned_payload["status"] == "draft"
    assert "Sadržaj" in str(owned_payload["content"])
    assert "Summary (EN)" in str(owned_payload["content"])


def _processed_from_row(row):
    from poslovnipuls_pipeline.models import FeedItem, ProcessedItem

    return ProcessedItem(
        item=FeedItem(
            source_name=row["source_name"],
            source_url="local",
            external_id=None,
            title=row["title"],
            link=row["link"],
            published_at=None,
            content=row["content"] or "",
            rights_mode=row["rights_mode"],
        ),
        dedupe_key=row["dedupe_key"],
        summary_en=row["summary_en"],
        summary_hr=row["summary_hr"],
    )
