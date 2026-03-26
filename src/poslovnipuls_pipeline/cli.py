from __future__ import annotations

import argparse

from .config import load_config
from .logging_utils import configure_logging
from .pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run poslovnipuls editorial pipeline")
    parser.add_argument("--config", default="sources.yaml", help="Path to config YAML")
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)
    run_pipeline(config)


if __name__ == "__main__":
    main()
