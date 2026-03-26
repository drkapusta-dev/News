from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from poslovnipuls_pipeline.config import AppConfig, load_config
from poslovnipuls_pipeline.logging_utils import configure_logging
from poslovnipuls_pipeline.pipeline import run_ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Import only owned manual content")
    parser.add_argument("--config", default="sources.json", help="Path to JSON source registry")
    args = parser.parse_args()

    configure_logging()
    base_config = load_config(args.config)
    owned_sources = [source for source in base_config.sources if source.source_type == "owned_manual" and source.enabled]
    owned_config = AppConfig(db_path=base_config.db_path, sources=owned_sources, wordpress=base_config.wordpress)

    inserted = run_ingest(owned_config)
    print(f"Owned content import completed. Inserted: {inserted}")


if __name__ == "__main__":
    main()
