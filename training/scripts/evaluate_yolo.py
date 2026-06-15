from __future__ import annotations

import argparse
from pathlib import Path

from pyclef_training_common import default_dataset_root, default_model_path, default_runs_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run visual predictions for a PyClef YOLO model.")
    parser.add_argument("--model", type=Path, default=default_model_path())
    parser.add_argument("--source", type=Path, default=default_dataset_root() / "images" / "val")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--project", type=Path, default=default_runs_root())
    parser.add_argument("--name", default="predict")
    parser.add_argument("--save-txt", action="store_true")
    parser.add_argument("--save-conf", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}")
    if not args.source.exists():
        raise SystemExit(f"Source not found: {args.source}")

    from ultralytics import YOLO

    model = YOLO(str(args.model))
    results = model.predict(
        source=str(args.source),
        conf=args.conf,
        imgsz=args.imgsz,
        save=True,
        save_txt=args.save_txt,
        save_conf=args.save_conf,
        project=str(args.project),
        name=args.name,
        exist_ok=True,
    )
    print(f"Predicted {len(results)} image(s).")
    print(f"Output folder: {args.project / args.name}")


if __name__ == "__main__":
    main()

