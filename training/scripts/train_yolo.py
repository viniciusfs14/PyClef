from __future__ import annotations

import argparse
from pathlib import Path

from pyclef_training_common import default_dataset_root, default_model_path, default_runs_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune the PyClef YOLO model on hard cases.")
    parser.add_argument("--data", type=Path, default=default_dataset_root() / "data.yaml")
    parser.add_argument("--model", type=Path, default=default_model_path())
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--project", type=Path, default=default_runs_root())
    parser.add_argument("--name", default="pyclef-finetune-v1")
    parser.add_argument("--device", default=None, help="Example: 0, cpu, or cuda:0.")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--patience", type=int, default=25)
    parser.add_argument("--exist-ok", action="store_true")
    parser.add_argument(
        "--generic-aug",
        action="store_true",
        help="Use Ultralytics default augmentations instead of sheet-music-safe settings.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.data.exists():
        raise SystemExit(f"Data file not found: {args.data}")
    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}")

    from ultralytics import YOLO

    model = YOLO(str(args.model))
    train_kwargs = {
        "data": str(args.data),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "project": str(args.project),
        "name": args.name,
        "workers": args.workers,
        "patience": args.patience,
        "exist_ok": args.exist_ok,
    }
    if args.device:
        train_kwargs["device"] = args.device

    if not args.generic_aug:
        train_kwargs.update(
            {
                "fliplr": 0.0,
                "flipud": 0.0,
                "degrees": 1.5,
                "translate": 0.02,
                "scale": 0.10,
                "shear": 0.0,
                "perspective": 0.0,
                "mosaic": 0.0,
                "mixup": 0.0,
                "copy_paste": 0.0,
                "hsv_h": 0.0,
                "hsv_s": 0.0,
                "hsv_v": 0.12,
            }
        )

    results = model.train(**train_kwargs)
    save_dir = Path(getattr(results, "save_dir", args.project / args.name))
    print(f"Training complete: {save_dir}")
    print(f"Best weights: {save_dir / 'weights' / 'best.pt'}")


if __name__ == "__main__":
    main()

