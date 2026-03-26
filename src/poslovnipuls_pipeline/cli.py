from __future__ import annotations

import argparse

from .config import load_config
from .logging_utils import configure_logging
from .pipeline import healthcheck, run_ingest, run_pipeline, run_publish


def main() -> None:
    parser = argparse.ArgumentParser(description="Run poslovnipuls editorial pipeline")
    parser.add_argument("--config", default="sources.json", help="Path to JSON source registry")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "ingest", "publish", "healthcheck"],
        help="Pipeline command",
    )
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)

    if args.command == "ingest":
        run_ingest(config)
        return
    if args.command == "publish":
        run_publish(config)
        return
    if args.command == "healthcheck":
        for line in healthcheck(config, args.config):
            print(line)
        return

    run_pipeline(config)


if __name__ == "__main__":
    main()
