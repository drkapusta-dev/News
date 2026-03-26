from poslovnipuls_pipeline.config import AppConfig, SourceConfig
from poslovnipuls_pipeline.db import create_schema
from poslovnipuls_pipeline.pipeline import healthcheck


def test_healthcheck_reports_missing_wordpress_credentials(tmp_path) -> None:
    db_path = tmp_path / "app.db"
    create_schema(db_path)
    config = AppConfig(
        db_path=db_path,
        sources=[
            SourceConfig(
                name="Owned",
                source_type="owned_manual",
                content_dir=tmp_path,
                rights_mode="full_publish",
            )
        ],
        wordpress=None,
    )

    lines = healthcheck(config)
    assert any("WordPress credentials present: no" in line for line in lines)
