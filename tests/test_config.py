import pytest

from poslovnipuls_pipeline.config import _validate_sources


def test_validate_sources_accepts_supported_rights_modes() -> None:
    sources = _validate_sources(
        [
            {"name": "A", "source_type": "rss", "rss_url": "https://example.com/a", "rights_mode": "summary_only"},
            {"name": "B", "source_type": "rss", "rss_url": "https://example.com/b", "rights_mode": "full_publish"},
            {"name": "C", "source_type": "rss", "rss_url": "https://example.com/c", "rights_mode": "disabled"},
        ]
    )

    assert [s.rights_mode for s in sources] == ["summary_only", "full_publish", "disabled"]
    assert [s.enabled for s in sources] == [True, True, False]


def test_validate_sources_rejects_unsupported_rights_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported rights_mode"):
        _validate_sources(
            [{"name": "Bad", "source_type": "rss", "rss_url": "https://example.com/bad", "rights_mode": "republish"}]
        )


def test_validate_sources_requires_rights_mode() -> None:
    with pytest.raises(ValueError, match="Missing required 'rights_mode'"):
        _validate_sources([{"name": "Bad", "source_type": "rss", "rss_url": "https://example.com/bad"}])


def test_validate_sources_rejects_missing_required_source_fields() -> None:
    with pytest.raises(ValueError, match="must include rss_url"):
        _validate_sources([{"name": "Bad", "source_type": "rss", "rights_mode": "summary_only"}])
