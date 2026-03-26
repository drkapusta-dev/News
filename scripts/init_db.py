from __future__ import annotations

import argparse

from poslovnipuls_pipeline.config import load_config
from poslovnipuls_pipeline.db import create_schema


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize local SQLite database schema")
    parser.add_argument("--config", default="sources.yaml", help="Path to config YAML")
    args = parser.parse_args()

    config = load_config(args.config)
    create_schema(config.db_path)
    print(f"Initialized database at {config.db_path}")


if __name__ == "__main__":
    main()
