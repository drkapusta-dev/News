# poslovnipuls-pipeline

Lean Python MVP pipeline for:

1. Loading approved sources from `sources.yaml`
2. Fetching RSS items
3. Cleaning and storing items in SQLite
4. Generating English summaries
5. Generating Croatian localized summaries
6. Creating WordPress **draft** posts through REST API
7. Never auto-publishing

## Project structure

```text
src/poslovnipuls_pipeline/
  cli.py
  config.py
  db.py
  dedupe.py
  localization.py
  logging_utils.py
  models.py
  pipeline.py
  repository.py
  rss.py
  summarization.py
  wordpress.py
tests/
  test_dedupe.py
  test_rss.py
  test_wordpress.py
sources.yaml
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Configure

Edit `sources.yaml`:

- Add approved RSS feeds under `sources`
- Keep `summary_only: true` for external sources where full republishing is disallowed
- Fill WordPress credentials
- Keep `wordpress.default_status: draft`

## Run

```bash
python -m poslovnipuls_pipeline.cli --config sources.yaml
```

## Notes on compliance and safety

- The database stores `summary_only` flag for each item.
- WordPress payloads are summary-based and include original source link.
- WordPress client enforces `status='draft'`.
- Pipeline logs fetch and publish failures and continues processing.

## Testing

```bash
pytest
```
