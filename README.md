# poslovnipuls-pipeline

Lean Python MVP pipeline (offline-friendly v0):

1. Load approved sources from `sources.json`
2. Ingest from `rss`, `medium_rss`, and `owned_manual`
3. Deduplicate in SQLite across repeated runs
4. Generate English + Croatian summaries (local placeholder logic)
5. Create WordPress **draft-only** posts
6. Never auto-publish

## Standardized package layout

- Single Python package root: `src/poslovnipuls_pipeline`
- Scripts import directly from `src/poslovnipuls_pipeline`
- Legacy parallel package scaffolding under `app/` removed

## Restricted Environment Pilot (no internet required)

The default `sources.json` is now pilot-ready for offline execution:

- one local RSS fixture source (`tests/fixtures/local_rss.xml`, `summary_only`)
- one owned content source (`content/owned`, `full_publish`)
- one disabled source for validation (`rights_mode=disabled`)

> Prerequisite: Python 3.11+ available as `python3`.

```bash
cp .env.example .env
python3 scripts/init_db.py --config sources.json
python3 scripts/healthcheck.py --config sources.json
python3 scripts/import_owned_content.py --config sources.json
python3 scripts/run_ingest.py --config sources.json
python3 scripts/run_publish.py --config sources.json
python3 scripts/run_ingest.py --config sources.json
```

Expected restricted-environment pilot behavior:

- First `run_ingest` inserts the local RSS fixture item and owned content item.
- `run_publish` creates WordPress payloads as **draft-only** when credentials are present.
- Second `run_ingest` reports `Inserted: 0` due to dedupe.

All commands run directly from repo root using Python standard library only.

## Configuration

### Source registry (`sources.json`)

- Keep each source `rights_mode` in: `summary_only`, `full_publish`, `disabled`.
- Local RSS fixtures can be pointed to by a plain file path in `rss_url`.
- Keep `wordpress.default_status` set to `draft`.

### Environment variables (`.env`)

WordPress publishing is optional. If credentials are absent, publish step is skipped safely.

## Healthcheck output

`python3 scripts/healthcheck.py --config sources.json` reports:

- `.env` presence
- source registry presence + parse status
- DB presence
- WordPress credentials presence
- owned content directory presence

## Notes on safety

- WordPress publishing path is draft-only by payload and response validation.
- If WordPress credentials are missing, nothing is posted.
- Re-running ingest/publish is safe due to stable dedupe keys and DB uniqueness.
