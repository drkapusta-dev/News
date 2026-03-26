# poslovnipuls-pipeline

Lean Python MVP pipeline (offline-friendly v0):

1. Load approved sources from `sources.json`
2. Ingest from `rss`, `medium_rss`, and `owned_manual`
3. Deduplicate in SQLite across repeated runs
4. Generate English + Croatian summaries (local placeholder logic)
5. Create WordPress **draft-only** posts
6. Never auto-publish

## Offline / restricted bootstrap (no package install required)

> Prerequisite: Python 3.11+ available as `python3`.

```bash
cp .env.example .env
python3 scripts/init_db.py
python3 scripts/healthcheck.py
python3 scripts/import_owned_content.py
python3 scripts/run_ingest.py
python3 scripts/run_publish.py
```

All commands are designed to run directly from repo root using only Python standard library modules.

## Required project files

This repo ships with:

- `README.md`
- `.env.example`
- `sources.json` (source registry)
- `scripts/init_db.py`
- `scripts/healthcheck.py`
- `scripts/import_owned_content.py`
- `scripts/run_ingest.py`
- `scripts/run_publish.py`
- `app/`

## Configuration

### Source registry (`sources.json`)

- Keep exactly 3 pilot sources (external RSS, COTRUGLI medium_rss, owned_manual) unless editorially expanded.
- Ensure every source has `rights_mode` in: `summary_only`, `full_publish`, `disabled`.
- Keep `wordpress.default_status` set to `draft`.

### Environment variables (`.env`)

WordPress publishing is optional. If credentials are absent, publish step is skipped safely.

## Healthcheck output

`python3 scripts/healthcheck.py` reports:

- `.env` presence
- source registry presence + parse status
- DB presence
- WordPress credentials presence
- owned content directory presence

## Notes on safety

- WordPress publishing path is draft-only by payload and response validation.
- If WordPress credentials are missing, nothing is posted.
- Re-running ingest/publish is safe due to stable dedupe keys and DB uniqueness.
