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
  owned_content.py
  pipeline.py
  repository.py
  rss.py
  summarization.py
  wordpress.py
scripts/
  init_db.py
tests/
  test_dedupe.py
  test_owned_content.py
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
- Use `rights_mode` with exactly one value per source:
  - `summary_only`
  - `full_publish`
  - `disabled`
- Keep `wordpress.default_status: draft`
- Keep `database.path: data/app.db`

## Initialize local DB

```bash
python scripts/init_db.py --config sources.yaml
```

## Run

```bash
python -m poslovnipuls_pipeline.cli --config sources.yaml
```

## Notes on compliance and safety

- The database stores `rights_mode` for each item.
- WordPress payloads use `status='draft'` only.
- The WordPress client rejects non-draft defaults and non-draft API responses.
- Pipeline logs fetch and draft creation failures and continues processing.

## Testing

```bash
pytest
```
