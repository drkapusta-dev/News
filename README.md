# poslovnipuls-pipeline

Lean Python MVP pipeline for the first v0 pilot:

1. Load approved sources from `sources.yaml`
2. Ingest from `rss`, `medium_rss`, and `owned_manual`
3. Deduplicate in SQLite across repeated runs
4. Generate English + Croatian summaries
5. Create WordPress **draft-only** posts
6. Never auto-publish

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## First Pilot Run

### 1) Configure

- Review `sources.yaml` and keep exactly 3 pilot sources (external RSS, COTRUGLI medium_rss, owned_manual).
- Ensure all sources have `rights_mode` in: `summary_only`, `full_publish`, `disabled`.
- Keep `wordpress.default_status: draft`.

### 2) Initialize DB

```bash
python scripts/init_db.py --config sources.yaml
```

### 3) Healthcheck

```bash
python -m poslovnipuls_pipeline.cli healthcheck --config sources.yaml
```

### 4) Ingest

```bash
python -m poslovnipuls_pipeline.cli ingest --config sources.yaml
```

### 5) Publish drafts

```bash
python -m poslovnipuls_pipeline.cli publish --config sources.yaml
```

### 6) Expected WordPress result

- New posts appear in WordPress Admin as **Draft** only.
- `summary_only` sources create compact Croatian-first drafts with attribution + original URL.
- `full_publish` sources create fuller bilingual drafts.
- SQLite stores `wordpress_post_id` and `wordpress_status`.

### 7) Safe rerun

Re-run ingest and publish commands anytime. Duplicate items are skipped via stable content hashing and unique `dedupe_key`.

## Testing

```bash
pytest
```
