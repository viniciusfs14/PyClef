from __future__ import annotations

import argparse
from pathlib import Path

from pyclef_training_common import default_dataset_root, ensure_yolo_dirs, write_dense_data_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create PyClef hard-case YOLO dataset folders.")
    parser.add_argument(
        "--root",
        type=Path,
        default=default_dataset_root(),
        help="Dataset root. Defaults to training/datasets/pyclef_hard_cases.",
    )
    parser.add_argument("--force-yaml", action="store_true", help="Rewrite data.yaml if it already exists.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_yolo_dirs(args.root)
    data_yaml = write_dense_data_yaml(args.root, force=args.force_yaml)
    print(f"Dataset scaffold ready: {args.root}")
    print(f"Dense-compatible data file: {data_yaml}")


if __name__ == "__main__":
    main()

