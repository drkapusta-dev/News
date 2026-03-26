from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from poslovnipuls_pipeline.config import load_config
from poslovnipuls_pipeline.pipeline import healthcheck


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline-safe environment healthcheck")
    parser.add_argument("--config", default="sources.json", help="Path to JSON source registry")
    args = parser.parse_args()

    config = None
    try:
        config = load_config(args.config)
    except Exception:
        config = None

    for line in healthcheck(config=config, config_path=args.config):
        print(line)


if __name__ == "__main__":
    main()
