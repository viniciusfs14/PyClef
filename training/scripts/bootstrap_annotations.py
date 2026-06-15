from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image

from pyclef_training_common import (
    copy_or_render_input,
    default_dataset_root,
    default_model_path,
    ensure_yolo_dirs,
    iter_input_files,
    write_dense_data_yaml,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy hard-case scores into a YOLO dataset and optionally bootstrap labels with the current model."
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Score images, PDFs, or folders.")
    parser.add_argument("--root", type=Path, default=default_dataset_root(), help="YOLO dataset root.")
    parser.add_argument("--split", choices=("train", "val", "test"), default="train")
    parser.add_argument("--model", type=Path, default=default_model_path(), help="YOLO model used for bootstrap labels.")
    parser.add_argument("--conf", type=float, default=0.25, help="Prediction confidence for bootstrap labels.")
    parser.add_argument("--imgsz", type=int, default=1280, help="YOLO inference image size.")
    parser.add_argument("--dpi", type=int, default=240, help="PDF render DPI.")
    parser.add_argument("--no-predict", action="store_true", help="Create empty label files instead of model predictions.")
    return parser.parse_args()


def write_prediction_labels(model, image_path: Path, label_path: Path, conf: float, imgsz: int) -> int:
    result = model.predict(str(image_path), conf=conf, imgsz=imgsz, verbose=False)[0]
    lines = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        x_center, y_center, width, height = [float(value) for value in box.xywhn[0].cpu().tolist()]
        lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return len(lines)


def write_empty_label(label_path: Path) -> int:
    label_path.write_text("", encoding="utf-8")
    return 0


def main() -> None:
    args = parse_args()
    ensure_yolo_dirs(args.root)
    write_dense_data_yaml(args.root)

    input_files = iter_input_files(args.inputs)
    if not input_files:
        raise SystemExit("No supported score files were found.")

    yolo_model = None
    if not args.no_predict:
        if not args.model.exists():
            raise SystemExit(f"Model not found: {args.model}")
        from ultralytics import YOLO

        yolo_model = YOLO(str(args.model))

    image_dir = args.root / "images" / args.split
    label_dir = args.root / "labels" / args.split
    manifest_path = args.root / "source_manifest.csv"
    manifest_exists = manifest_path.exists()

    total_images = 0
    total_labels = 0
    with manifest_path.open("a", newline="", encoding="utf-8") as manifest_file:
        writer = csv.writer(manifest_file)
        if not manifest_exists:
            writer.writerow(["split", "image", "label", "source"])

        for input_path in input_files:
            prepared_images = copy_or_render_input(input_path, image_dir, dpi=args.dpi)
            for image_path in prepared_images:
                with Image.open(image_path) as image:
                    image.verify()
                label_path = label_dir / f"{image_path.stem}.txt"
                if yolo_model is None:
                    label_count = write_empty_label(label_path)
                else:
                    label_count = write_prediction_labels(
                        yolo_model,
                        image_path,
                        label_path,
                        conf=args.conf,
                        imgsz=args.imgsz,
                    )
                writer.writerow([args.split, image_path.name, label_path.name, str(input_path)])
                total_images += 1
                total_labels += label_count

    print(f"Prepared {total_images} image(s) in {image_dir}")
    print(f"Bootstrap labels: {total_labels}")
    print("Next step: correct the YOLO labels manually before training.")


if __name__ == "__main__":
    main()

