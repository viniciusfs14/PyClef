from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


DENSE_CLASS_COUNT = 208

KNOWN_DENSE_NAMES = {
    0: "brace",
    5: "clefG",
    8: "clefF",
    24: "quarter",
    26: "quarter_alt1",
    28: "half",
    30: "half_alt1",
    32: "whole",
    34: "whole_alt1",
    46: "dynamicF",
    47: "dynamicMF",
    48: "dynamicP",
    49: "dynamicMP",
    59: "flat",
    63: "sharp",
    84: "rest_whole",
    85: "rest_half",
    86: "rest_quarter",
    134: "staff",
    136: "brace_alt1",
    141: "clefG_alt1",
    143: "clefF_alt1",
    156: "quarter_alt2",
    157: "half_alt2",
    158: "whole_alt2",
    170: "flat_alt1",
    172: "sharp_alt1",
    184: "rest_quarter_alt1",
    207: "staff_alt1",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
PDF_EXTENSIONS = {".pdf"}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_dataset_root() -> Path:
    return project_root() / "training" / "datasets" / "pyclef_hard_cases"


def default_runs_root() -> Path:
    return project_root() / "training" / "runs"


def default_model_path() -> Path:
    env_model = os.environ.get("PYCLEF_MODEL_PATH")
    if env_model:
        return Path(env_model)
    return project_root() / "pyclef_app" / "model" / "best.pt"


def dense_class_names() -> list[str]:
    names = []
    for index in range(DENSE_CLASS_COUNT):
        names.append(KNOWN_DENSE_NAMES.get(index, f"dense_{index:03d}"))
    return names


def ensure_yolo_dirs(root: Path) -> None:
    for split in ("train", "val", "test"):
        (root / "images" / split).mkdir(parents=True, exist_ok=True)
        (root / "labels" / split).mkdir(parents=True, exist_ok=True)
    for bucket in (
        "missed_notes",
        "false_positives",
        "dense_chords",
        "bass_clef",
        "braces",
        "scanned_scores",
    ):
        (root / "raw" / bucket).mkdir(parents=True, exist_ok=True)


def write_dense_data_yaml(root: Path, force: bool = False) -> Path:
    data_yaml = root / "data.yaml"
    if data_yaml.exists() and not force:
        return data_yaml

    root_text = root.resolve().as_posix()
    lines = [
        f"path: {root_text}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "names:",
    ]
    for index, name in enumerate(dense_class_names()):
        lines.append(f"  {index}: {name}")
    data_yaml.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data_yaml


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem).strip("._")
    return stem or "score"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def iter_input_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.suffix.lower() in IMAGE_EXTENSIONS | PDF_EXTENSIONS:
                    files.append(child)
        elif path.suffix.lower() in IMAGE_EXTENSIONS | PDF_EXTENSIONS:
            files.append(path)
    return files


def render_pdf_pages(pdf_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    try:
        from pdf2image import convert_from_path
    except ImportError as exc:
        raise RuntimeError("pdf2image is required to render PDF pages.") from exc

    poppler_path = None
    try:
        from pyclef_app import config

        poppler_path = config.POPPLER_PATH
    except Exception:
        poppler_path = None

    pages = convert_from_path(str(pdf_path), dpi=dpi, poppler_path=poppler_path)
    rendered_paths: list[Path] = []
    for page_index, page in enumerate(pages, start=1):
        page_path = unique_path(output_dir / f"{safe_stem(pdf_path)}_p{page_index:03d}.png")
        page.save(page_path)
        rendered_paths.append(page_path)
    return rendered_paths


def copy_or_render_input(input_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = input_path.suffix.lower()
    if suffix in PDF_EXTENSIONS:
        return render_pdf_pages(input_path, output_dir, dpi=dpi)
    if suffix in IMAGE_EXTENSIONS:
        destination = unique_path(output_dir / f"{safe_stem(input_path)}{suffix}")
        shutil.copy2(input_path, destination)
        return [destination]
    return []

