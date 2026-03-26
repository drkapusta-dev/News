import pytest

from poslovnipuls_pipeline.config import _validate_sources


def test_validate_sources_accepts_supported_rights_modes() -> None:
    sources = _validate_sources(
        [
            {"name": "A", "rss_url": "https://example.com/a", "rights_mode": "summary_only"},
            {"name": "B", "rss_url": "https://example.com/b", "rights_mode": "full_publish"},
            {"name": "C", "rss_url": "https://example.com/c", "rights_mode": "disabled"},
        ]
    )

    assert [s.rights_mode for s in sources] == ["summary_only", "full_publish", "disabled"]
    assert [s.enabled for s in sources] == [True, True, False]


def test_validate_sources_rejects_unsupported_rights_mode() -> None:
    with pytest.raises(ValueError):
        _validate_sources(
            [{"name": "Bad", "rss_url": "https://example.com/bad", "rights_mode": "republish"}]
        )
