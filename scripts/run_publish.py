from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from poslovnipuls_pipeline.config import load_config
from poslovnipuls_pipeline.logging_utils import configure_logging
from poslovnipuls_pipeline.pipeline import run_publish


def main() -> None:
    parser = argparse.ArgumentParser(description="Run publish step (draft-only)")
    parser.add_argument("--config", default="sources.json", help="Path to JSON source registry")
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)
    published = run_publish(config)
    print(f"Publish completed. Drafts created: {published}")


if __name__ == "__main__":
    main()
