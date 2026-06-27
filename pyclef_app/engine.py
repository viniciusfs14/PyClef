# main.py - VERSÃO COM AGRUPAMENTO RÍGIDO DE SISTEMAS
import cv2
import numpy as np
import os
import re
import tkinter as tk
import urllib.error
import urllib.request
import shutil
import zipfile
from pathlib import Path
from tkinter import filedialog, simpledialog
from ultralytics import YOLO
from pydub import AudioSegment
try:
    import moviepy.editor as mp
except ModuleNotFoundError:
    import moviepy as mp
from pdf2image import convert_from_path
from mido import Message, MidiFile, MidiTrack, MetaMessage
from PIL import Image
import sys

from . import config
from . import audio_utils
from . import rhythm
from . import vision_utils
from .models import OutputOptions, ProcessingResult, ScoreEvent
from .scientific import build_scientific_payload, write_scientific_report
from .validation import validate_processing_result

BASE_DIR = Path(__file__).resolve().parent

PROGRESS_MESSAGES = {
    "pt": {
        "loading_model": "Carregando modelo de reconhecimento...",
        "downloading_model": "Baixando modelo PyClef... {downloaded_mb}/{total_mb} MB",
        "extracting_model": "Extraindo modelo PyClef...",
        "model_ready": "Modelo pronto.",
        "preparing_pages": "Preparando paginas da partitura...",
        "preprocessing_page": "Melhorando imagem para reconhecimento...",
        "recovering_staff_crops": "Tentando recuperar notas por recortes de pauta...",
        "processing_page": "Processando pagina {page}...",
        "systems_found": "Sistemas encontrados: {systems} | pautas por sistema: {sizes} | braces detectados: {braces}",
        "page_done": "Pagina {page} concluida.",
        "exporting_files": "Exportando arquivos...",
        "generating_mp3": "Gerando MP3...",
        "preparing_video_audio": "Preparando audio temporario para o video...",
        "generating_midi": "Gerando MIDI...",
        "downloading_soundfont": "Baixando SoundFont de teste... {downloaded_mb}/{total_mb} MB",
        "rendering_soundfont": "Renderizando audio com SoundFont...",
        "soundfont_fallback": "SoundFont indisponivel; usando sintese interna. Motivo: {error}",
        "rendering_video": "Renderizando video. Esta etapa pode demorar...",
        "rendering_frames": "Renderizando quadros do video...",
        "syncing_video": "Sincronizando audio e video...",
        "generating_scientific_report": "Gerando relatorio cientifico...",
        "done": "Sincronia de sistemas corrigida!",
    },
    "en": {
        "loading_model": "Loading recognition model...",
        "downloading_model": "Downloading PyClef model... {downloaded_mb}/{total_mb} MB",
        "extracting_model": "Extracting PyClef model...",
        "model_ready": "Model ready.",
        "preparing_pages": "Preparing score pages...",
        "preprocessing_page": "Improving image for recognition...",
        "recovering_staff_crops": "Trying staff-crop note recovery...",
        "processing_page": "Processing page {page}...",
        "systems_found": "Systems found: {systems} | staves per system: {sizes} | braces detected: {braces}",
        "page_done": "Page {page} complete.",
        "exporting_files": "Exporting files...",
        "generating_mp3": "Generating MP3...",
        "preparing_video_audio": "Preparing temporary audio for the video...",
        "generating_midi": "Generating MIDI...",
        "downloading_soundfont": "Downloading test SoundFont... {downloaded_mb}/{total_mb} MB",
        "rendering_soundfont": "Rendering audio with SoundFont...",
        "soundfont_fallback": "SoundFont unavailable; using internal synthesis. Reason: {error}",
        "rendering_video": "Rendering video. This step can take a while...",
        "rendering_frames": "Rendering video frames...",
        "syncing_video": "Synchronizing audio and video...",
        "generating_scientific_report": "Generating scientific report...",
        "done": "System synchronization complete!",
    },
}


def safe_output_stem(path):
    stem = Path(path).stem if path else config.OUTPUT_BASE_NAME
    stem = re.sub(r"[^\w.-]+", "_", stem, flags=re.UNICODE).strip("._")
    return stem or config.OUTPUT_BASE_NAME


def ensure_model_file(progress):
    model_path = Path(config.YOLO_MODEL)
    if model_path.exists() and model_path.stat().st_size > 0:
        return model_path

    if not config.MODEL_URL:
        raise FileNotFoundError(
            "YOLO model not found. Set PYCLEF_MODEL_PATH or PYCLEF_MODEL_URL."
        )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = model_path.with_suffix(model_path.suffix + ".download")
    if temp_path.exists():
        temp_path.unlink()

    downloaded = 0
    try:
        with urllib.request.urlopen(config.MODEL_URL, timeout=30) as response:
            total = int(response.headers.get("Content-Length") or 0)
            total_mb = f"{total / (1024 * 1024):.1f}" if total else "?"
            progress("downloading_model", 4, downloaded_mb="0.0", total_mb=total_mb)
            with temp_path.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    downloaded_mb = f"{downloaded / (1024 * 1024):.1f}"
                    percent = 4
                    if total:
                        percent = 4 + int(min(1, downloaded / total) * 3)
                    progress(
                        "downloading_model",
                        percent,
                        downloaded_mb=downloaded_mb,
                        total_mb=total_mb,
                    )
        if config.MODEL_URL.lower().split("?", 1)[0].endswith(".zip"):
            progress("extracting_model", 7)
            with zipfile.ZipFile(temp_path) as archive:
                candidates = [
                    name
                    for name in archive.namelist()
                    if Path(name).name == "best.pt" and not name.endswith("/")
                ]
                if not candidates:
                    raise FileNotFoundError(
                        "The downloaded model archive does not contain best.pt."
                    )
                with archive.open(candidates[0]) as source, model_path.open("wb") as target:
                    shutil.copyfileobj(source, target)
            temp_path.unlink()
        else:
            temp_path.replace(model_path)
    except (urllib.error.URLError, OSError, zipfile.BadZipFile) as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(
            "Could not download the PyClef model. Upload best.pt.zip to the configured "
            "release URL or set PYCLEF_MODEL_PATH to a local model file. "
            f"URL: {config.MODEL_URL}"
        ) from exc

    progress("model_ready", 7)
    return model_path

# Configurações Visuais
COLOR_BOX = (225, 105, 65)
COLOR_TEXT = (255, 255, 255)
COLOR_BG_TEXT = (0, 0, 0)
FONT_SCALE = 0.82
FONT_THICKNESS = 2
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
LABEL_PADDING_X = 5
LABEL_PADDING_Y = 3
LABEL_MARGIN = 5
LABEL_COLLISION_MARGIN = 3
LABEL_BORDER_COLOR = (110, 110, 110)
LABEL_BG_ALPHA = 0.78
STAFF_COLOR_TREBLE = (255, 214, 64)
STAFF_COLOR_BASS = (125, 232, 132)
STAFF_COLOR_OTHER = (225, 105, 65)
STAFF_COLOR_REVIEW = (0, 198, 255)
STAFF_COLOR_LOW_CONFIDENCE = (0, 120, 255)
PIANO_ROLL_WIDTH = 1920
PIANO_ROLL_HEIGHT = 1080
PIANO_ROLL_LEAD_MS = 3400
PIANO_ROLL_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
PIANO_ROLL_BLACK_CLASSES = {1, 3, 6, 8, 10}
# These BGR colors mirror pyclef_app/player/midi_player.css.
PIANO_ROLL_BG = (24, 13, 8)
PIANO_ROLL_PANEL = (44, 28, 20)
PIANO_ROLL_PANEL_STRONG = (59, 39, 29)
PIANO_ROLL_BORDER = (220, 182, 152)
PIANO_ROLL_RIGHT_COLOR = (255, 214, 64)
PIANO_ROLL_RIGHT_DARK = (171, 140, 17)
PIANO_ROLL_LEFT_COLOR = (136, 255, 108)
PIANO_ROLL_LEFT_DARK = (60, 154, 30)
SYSTEM_WIDTH_BEATS = rhythm.SYSTEM_WIDTH_BEATS
MIN_COLUMN_ADVANCE_BEATS = rhythm.MIN_COLUMN_ADVANCE_BEATS
SYSTEM_GAP_BEATS = rhythm.SYSTEM_GAP_BEATS
STAFF_IDS = {134, 207}
BRACE_IDS = {0, 136}
ACCIDENTAL_TYPES = {
    "sharp": "s",
    "keySharp": "s",
    "flat": "b",
    "keyFlat": "b",
    "natural": "",
    "keyNatural": "",
    "doubleSharp": "ss",
    "doubleFlat": "bb",
}
DYNAMIC_TYPES = {"dynamicP", "dynamicMP", "dynamicM", "dynamicMF", "dynamicF", "dynamicS", "dynamicZ", "dynamicR"}
RHYTHMIC_CONTEXT_TYPES = {
    "augmentationDot",
    "stem",
    "beam",
    "tie",
    "slur",
    "tuplet",
    "tuplet1",
    "tuplet2",
    "tuplet3",
    "tuplet4",
    "tuplet5",
    "tuplet6",
    "tuplet7",
    "tuplet8",
    "tuplet9",
    "tupletBracket",
}
SHARP_KEY_ORDER = ("F", "C", "G", "D", "A", "E", "B")
FLAT_KEY_ORDER = ("B", "E", "A", "D", "G", "C", "F")

def clamp_value(value, minimum, maximum):
    return max(minimum, min(maximum, value))

def rects_overlap(a, b, margin=0):
    return not (
        a[2] + margin <= b[0]
        or a[0] >= b[2] + margin
        or a[3] + margin <= b[1]
        or a[1] >= b[3] + margin
    )

def overlap_area(a, b):
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    return max(0, right - left) * max(0, bottom - top)

def clamp_label_rect(left, top, width, height, img_width, img_height):
    left = max(0, min(max(0, img_width - width), int(left)))
    top = max(0, min(max(0, img_height - height), int(top)))
    return (left, top, left + width, top + height)

def draw_alpha_rect(img, rect, color, alpha):
    x1, y1, x2, y2 = [int(v) for v in rect]
    x1 = max(0, min(img.shape[1], x1))
    x2 = max(0, min(img.shape[1], x2))
    y1 = max(0, min(img.shape[0], y1))
    y2 = max(0, min(img.shape[0], y2))
    if x2 <= x1 or y2 <= y1:
        return
    roi = img[y1:y2, x1:x2]
    overlay = roi.copy()
    overlay[:] = color
    cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)

def nearest_point_on_rect(rect, point):
    left, top, right, bottom = rect
    px, py = point
    candidates = [
        (max(left, min(right, px)), top),
        (max(left, min(right, px)), bottom),
        (left, max(top, min(bottom, py))),
        (right, max(top, min(bottom, py))),
    ]
    return min(candidates, key=lambda p: (p[0] - px) ** 2 + (p[1] - py) ** 2)

def staff_annotation_color(clef):
    if clef == "clefF":
        return STAFF_COLOR_BASS
    if clef == "clefG":
        return STAFF_COLOR_TREBLE
    return STAFF_COLOR_OTHER

def confidence_annotation_color(base_color, confidence):
    if confidence is None:
        return base_color
    if confidence < 0.38:
        return STAFF_COLOR_LOW_CONFIDENCE
    if confidence < 0.55:
        return STAFF_COLOR_REVIEW
    return base_color

def split_label_lines(text):
    if isinstance(text, (list, tuple)):
        return [str(line) for line in text if str(line)]
    return [line for line in str(text).split("\n") if line]

def draw_text_with_background(
    img,
    text,
    x,
    y,
    font_face,
    font_scale,
    color,
    thickness,
    bg_color,
    occupied_rects=None,
    anchor_box=None,
    border_color=None,
    guide_points=None,
    guide_color=None,
    alpha=LABEL_BG_ALPHA,
):
    lines = split_label_lines(text)
    if not lines:
        return None

    line_sizes = [
        cv2.getTextSize(line, font_face, font_scale, thickness)[0]
        for line in lines
    ]
    _, baseline = cv2.getTextSize(lines[0], font_face, font_scale, thickness)
    img_height, img_width = img.shape[:2]
    text_width = max(width for width, _ in line_sizes)
    line_height = max(height for _, height in line_sizes)
    line_gap = max(2, int(line_height * 0.20))
    label_width = text_width + (LABEL_PADDING_X * 2)
    label_height = (
        (line_height * len(lines))
        + (line_gap * max(0, len(lines) - 1))
        + baseline
        + (LABEL_PADDING_Y * 2)
    )
    fallback_top = y - line_height - baseline - LABEL_PADDING_Y
    fallback_left = x - LABEL_PADDING_X
    candidates = [(fallback_left, fallback_top)]

    if anchor_box is not None:
        bx1, by1, bx2, by2 = [int(v) for v in anchor_box]
        box_width = max(1, bx2 - bx1)
        box_center_x = bx1 + (box_width // 2)
        box_center_y = by1 + max(1, by2 - by1) // 2
        center_left = box_center_x - (label_width // 2)
        above = by1 - label_height - LABEL_MARGIN
        below = by2 + LABEL_MARGIN

        candidates = [
            (center_left, above),
            (bx1 - LABEL_PADDING_X, above),
            (bx2 - label_width + LABEL_PADDING_X, above),
            (center_left, below),
            (bx1 - LABEL_PADDING_X, below),
            (bx2 - label_width + LABEL_PADDING_X, below),
            (bx2 + LABEL_MARGIN, box_center_y - label_height // 2),
            (bx1 - label_width - LABEL_MARGIN, box_center_y - label_height // 2),
        ]

        for row in range(2, 7):
            up = by1 - (row * (label_height + LABEL_MARGIN))
            down = by2 + ((row - 1) * (label_height + LABEL_MARGIN))
            for offset in (0, -label_width // 2, label_width // 2, -label_width, label_width):
                candidates.append((center_left + offset, up))
                candidates.append((center_left + offset, down))

    occupied = occupied_rects or []
    best_rect = None
    best_score = None

    for left, top in candidates:
        rect = clamp_label_rect(left, top, label_width, label_height, img_width, img_height)
        collision = any(rects_overlap(rect, placed, LABEL_COLLISION_MARGIN) for placed in occupied)
        overlap = sum(overlap_area(rect, placed) for placed in occupied)
        distance = abs(rect[0] - fallback_left) + abs(rect[1] - fallback_top)
        score = (overlap * 1000) + distance

        if not collision:
            best_rect = rect
            break

        if best_score is None or score < best_score:
            best_score = score
            best_rect = rect

    left, top, right, bottom = best_rect
    line_color = guide_color or border_color or LABEL_BORDER_COLOR
    if guide_points:
        for point in guide_points:
            px, py = int(point[0]), int(point[1])
            rx, ry = nearest_point_on_rect(best_rect, (px, py))
            cv2.line(img, (px, py), (int(rx), int(ry)), line_color, 1, cv2.LINE_AA)

    draw_alpha_rect(img, best_rect, bg_color, alpha)
    cv2.rectangle(img, (left, top), (right, bottom), border_color or LABEL_BORDER_COLOR, 1)

    text_y = top + LABEL_PADDING_Y + line_height
    for line in lines:
        cv2.putText(
            img,
            line,
            (left + LABEL_PADDING_X, text_y),
            font_face,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )
        text_y += line_height + line_gap
    if occupied_rects is not None:
        occupied_rects.append(best_rect)
    return best_rect

def compact_note_lines(labels, max_lines=5):
    labels = [str(label) for label in labels if str(label)]
    if len(labels) <= max_lines:
        return labels
    return labels[: max_lines - 1] + [f"+{len(labels) - max_lines + 1}"]

def draw_column_annotations(img, note_infos, occupied_rects, annotation_mode):
    if not note_infos:
        return

    detailed = annotation_mode == "detailed"
    groups = {}
    for info in note_infos:
        groups.setdefault(info["staff_index"], []).append(info)

    for group in groups.values():
        group.sort(key=lambda item: item["center"][1])
        if not detailed and len(group) > 1:
            labels = compact_note_lines([item["label"] for item in group])
            x1 = min(item["box"][0] for item in group)
            y1 = min(item["box"][1] for item in group)
            x2 = max(item["box"][2] for item in group)
            y2 = max(item["box"][3] for item in group)
            anchor = np.array([x1, y1, x2, y2]).astype(int)
            min_confidence = min(
                (item.get("confidence") for item in group if item.get("confidence") is not None),
                default=None,
            )
            color = confidence_annotation_color(group[0]["color"], min_confidence)
            for item in group:
                b = item["box"].astype(int)
                item_color = confidence_annotation_color(color, item.get("confidence"))
                cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), item_color, 2)
            draw_text_with_background(
                img,
                labels,
                int(x1),
                int(y1) - 15,
                FONT_FACE,
                FONT_SCALE,
                COLOR_TEXT,
                FONT_THICKNESS,
                COLOR_BG_TEXT,
                occupied_rects=occupied_rects,
                anchor_box=anchor,
                border_color=color,
                guide_points=[item["center"] for item in group],
                guide_color=color,
            )
            continue

        for item in group:
            label = item["label"]
            if detailed and item.get("confidence") is not None:
                label = [label, f"{int(item['confidence'] * 100)}%"]
                if item["confidence"] < 0.55:
                    label.append("review")
            b = item["box"].astype(int)
            annotation_color = confidence_annotation_color(item["color"], item.get("confidence"))
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), annotation_color, 2)
            draw_text_with_background(
                img,
                label,
                b[0],
                b[1] - 15,
                FONT_FACE,
                FONT_SCALE,
                COLOR_TEXT,
                FONT_THICKNESS,
                COLOR_BG_TEXT,
                occupied_rects=occupied_rects,
                anchor_box=b,
                border_color=annotation_color,
                guide_points=[item["center"]],
                guide_color=annotation_color,
            )

def draw_annotation_legend(img, annotation_mode, language):
    labels = {
        "pt": {
            "title": "PyClef anotacoes",
            "treble": "Clave de Sol",
            "bass": "Clave de Fa",
            "guide": "Linha-guia",
            "review": "Revisar",
            "mode": "Modo limpo" if annotation_mode != "detailed" else "Modo detalhado",
        },
        "en": {
            "title": "PyClef annotations",
            "treble": "Treble staff",
            "bass": "Bass staff",
            "guide": "Guide line",
            "review": "Review",
            "mode": "Clean mode" if annotation_mode != "detailed" else "Detailed mode",
        },
    }.get(language, {})
    lines = [
        labels.get("title", "PyClef annotations"),
        labels.get("treble", "Treble staff"),
        labels.get("bass", "Bass staff"),
        labels.get("guide", "Guide line"),
        labels.get("review", "Review"),
        labels.get("mode", "Clean mode"),
    ]
    font_scale = 0.58
    thickness = 1
    line_height = 18
    panel_width = 250
    panel_height = 134
    x = 24
    y = 24
    rect = (x, y, x + panel_width, y + panel_height)
    draw_alpha_rect(img, rect, COLOR_BG_TEXT, 0.62)
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), STAFF_COLOR_TREBLE, 1)
    cv2.putText(img, lines[0], (x + 14, y + 24), FONT_FACE, 0.62, COLOR_TEXT, 2, cv2.LINE_AA)
    swatch_y = y + 48
    for idx, (text, color) in enumerate(
        (
            (lines[1], STAFF_COLOR_TREBLE),
            (lines[2], STAFF_COLOR_BASS),
            (lines[3], STAFF_COLOR_OTHER),
            (lines[4], STAFF_COLOR_REVIEW),
            (lines[5], (210, 210, 210)),
        )
    ):
        current_y = swatch_y + (idx * line_height)
        cv2.rectangle(img, (x + 15, current_y - 9), (x + 31, current_y + 3), color, -1)
        cv2.putText(img, text, (x + 40, current_y + 3), FONT_FACE, font_scale, COLOR_TEXT, thickness, cv2.LINE_AA)

def is_rhythmic_object(otype):
    if not otype:
        return False
    if otype.startswith(("quarter", "half", "whole", "double_whole")):
        return True
    if otype.startswith("rest_"):
        return True
    return False

def accidental_label(accidental):
    if accidental == "s":
        return "#"
    if accidental == "ss":
        return "##"
    if accidental == "b":
        return "b"
    if accidental == "bb":
        return "bb"
    return ""

def label_note(note_base, accidental, octave):
    return f"{note_base}{accidental_label(accidental)}{octave}"

def preprocess_score_image_for_detection(image):
    """Enhance a score page for detection without changing geometry."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 7, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    sharpened = cv2.addWeighted(enhanced, 1.35, cv2.GaussianBlur(enhanced, (0, 0), 1.1), -0.35, 0)
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

def is_staff_crop_recoverable_type(otype):
    if not otype:
        return False
    if is_rhythmic_object(otype):
        return True
    if otype in ACCIDENTAL_TYPES or otype in DYNAMIC_TYPES:
        return True
    if otype in RHYTHMIC_CONTEXT_TYPES:
        return True
    if otype.startswith("flag"):
        return True
    return "rest" in otype

def system_crop_bounds(system, image_shape):
    height, width = image_shape[:2]
    left = min(float(staff[0]) for staff in system)
    top = min(float(staff[1]) for staff in system)
    right = max(float(staff[2]) for staff in system)
    bottom = max(float(staff[3]) for staff in system)
    system_width = max(1.0, right - left)
    staff_heights = [max(1.0, float(staff[3] - staff[1])) for staff in system]
    staff_height = float(np.median(staff_heights)) if staff_heights else 40.0
    margin_x = max(34, int(system_width * 0.025))
    margin_y = max(44, int(staff_height * 2.3))
    return (
        max(0, int(left - margin_x)),
        max(0, int(top - margin_y)),
        min(width, int(right + margin_x)),
        min(height, int(bottom + margin_y)),
    )

def object_center_from_box(box):
    return (float(box[0] + box[2]) / 2.0, float(box[1] + box[3]) / 2.0)

def is_box_duplicate(box, existing_boxes, iou_threshold=0.34):
    x, y = object_center_from_box(box)
    for existing in existing_boxes:
        if vision_utils.calculate_iou(box, existing) >= iou_threshold:
            return True
        ex, ey = object_center_from_box(existing)
        existing_width = max(1.0, float(existing[2] - existing[0]))
        existing_height = max(1.0, float(existing[3] - existing[1]))
        if abs(x - ex) <= existing_width * 0.45 and abs(y - ey) <= existing_height * 0.55:
            return True
    return False

def first_existing_music_x_in_system(system, objects):
    left = min(float(staff[0]) for staff in system)
    right = max(float(staff[2]) for staff in system)
    top = min(float(staff[1]) for staff in system)
    bottom = max(float(staff[3]) for staff in system)
    candidates = [
        float(obj["x"])
        for obj in objects
        if left <= obj["x"] <= right
        and top - 50 <= obj["y"] <= bottom + 50
        and is_rhythmic_object(config.ID_MAP.get(obj["id"], ""))
    ]
    return min(candidates) if candidates else None

def is_probable_system_header_false_positive(box, otype, system, objects):
    if not is_rhythmic_object(otype):
        return False
    first_music_x = first_existing_music_x_in_system(system, objects)
    if first_music_x is None:
        return False
    left = min(float(staff[0]) for staff in system)
    right = max(float(staff[2]) for staff in system)
    system_width = max(1.0, right - left)
    x, _y = object_center_from_box(box)
    return x < first_music_x - max(28.0, system_width * 0.035) and x < left + system_width * 0.18

def recover_objects_from_staff_crops(model, detection_img, systems, objects, existing_boxes):
    recovered = []
    stats = {"crop_count": 0, "recovered_count": 0, "rejected_count": 0}
    if not systems:
        return recovered, stats

    for system in systems:
        crop_left, crop_top, crop_right, crop_bottom = system_crop_bounds(system, detection_img.shape)
        if crop_right - crop_left < 80 or crop_bottom - crop_top < 60:
            stats["rejected_count"] += 1
            continue
        crop = detection_img[crop_top:crop_bottom, crop_left:crop_right]
        stats["crop_count"] += 1
        try:
            crop_result = model.predict(crop, conf=0.18, imgsz=1536, verbose=False)[0]
        except Exception:
            stats["rejected_count"] += 1
            continue

        for box in crop_result.boxes:
            class_id = int(box.cls[0])
            if class_id in STAFF_IDS or class_id in BRACE_IDS:
                continue
            otype = config.ID_MAP.get(class_id, "")
            if not is_staff_crop_recoverable_type(otype):
                stats["rejected_count"] += 1
                continue
            local_box = box.xyxy[0].cpu().numpy().astype(float)
            page_box = local_box + np.array([crop_left, crop_top, crop_left, crop_top], dtype=float)
            page_box[0] = max(0.0, page_box[0])
            page_box[1] = max(0.0, page_box[1])
            page_box[2] = min(float(detection_img.shape[1]), page_box[2])
            page_box[3] = min(float(detection_img.shape[0]), page_box[3])
            if page_box[2] <= page_box[0] or page_box[3] <= page_box[1]:
                stats["rejected_count"] += 1
                continue
            if is_probable_system_header_false_positive(page_box, otype, system, objects):
                stats["rejected_count"] += 1
                continue
            if is_box_duplicate(page_box, existing_boxes):
                continue
            x, y = object_center_from_box(page_box)
            new_object = {
                "id": class_id,
                "x": x,
                "y": y,
                "box": page_box,
                "conf": float(box.conf[0]),
                "source": "staff_crop",
            }
            recovered.append(new_object)
            objects.append(new_object)
            existing_boxes.append(page_box)
            stats["recovered_count"] += 1

    return recovered, stats

def rhythmic_objects_in_system(system, objects):
    left = min(float(staff[0]) for staff in system)
    right = max(float(staff[2]) for staff in system)
    top = min(float(staff[1]) for staff in system)
    bottom = max(float(staff[3]) for staff in system)
    return [
        obj
        for obj in objects
        if left <= obj["x"] <= right
        and top - 60 <= obj["y"] <= bottom + 60
        and is_rhythmic_object(config.ID_MAP.get(obj["id"], ""))
    ]

def candidate_barline_hits_staves(image, x, system):
    if image is None:
        return False
    height, width = image.shape[:2]
    x1 = max(0, int(x) - 2)
    x2 = min(width, int(x) + 3)
    if x2 <= x1:
        return False
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hit_count = 0
    for staff in system:
        top = max(0, int(staff[1]))
        bottom = min(height, int(staff[3]))
        staff_height = max(1, bottom - top)
        band = gray[top:bottom, x1:x2]
        if band.size == 0:
            continue
        dark_pixels = int((band < 115).sum())
        if dark_pixels >= staff_height * 0.42:
            hit_count += 1
    if len(system) <= 1:
        return hit_count >= 1
    return hit_count >= max(2, int(len(system) * 0.66))

def detect_system_measure_boundaries(image, system, objects=None):
    if image is None or not system:
        return []
    height, width = image.shape[:2]
    system_left = min(float(staff[0]) for staff in system)
    system_right = max(float(staff[2]) for staff in system)
    system_top = min(float(staff[1]) for staff in system)
    system_bottom = max(float(staff[3]) for staff in system)
    system_width = max(1.0, system_right - system_left)
    staff_heights = [max(1.0, float(staff[3] - staff[1])) for staff in system]
    staff_height = float(np.median(staff_heights)) if staff_heights else 42.0
    y_margin = max(8, int(staff_height * 0.18))
    x1 = max(0, int(system_left - 8))
    x2 = min(width, int(system_right + 8))
    y1 = max(0, int(system_top - y_margin))
    y2 = min(height, int(system_bottom + y_margin))
    if x2 - x1 < 80 or y2 - y1 < 35:
        return []

    crop = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 145, 255, cv2.THRESH_BINARY_INV)[1]
    kernel_height = max(18, int(staff_height * 0.72))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_height))
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    projection = vertical.sum(axis=0) / 255.0
    threshold = max(10.0, kernel_height * 0.34)

    candidates = []
    in_run = False
    start = 0
    for idx, value in enumerate(projection):
        if value >= threshold:
            if not in_run:
                start = idx
                in_run = True
        elif in_run:
            end = idx - 1
            center = x1 + ((start + end) / 2.0)
            candidates.append(center)
            in_run = False
    if in_run:
        center = x1 + ((start + len(projection) - 1) / 2.0)
        candidates.append(center)

    note_objects = rhythmic_objects_in_system(system, objects or [])
    note_centers = [obj["x"] for obj in note_objects]
    note_widths = [
        max(1.0, float(obj["box"][2] - obj["box"][0]))
        for obj in note_objects
        if "box" in obj
    ]
    filtered = []
    note_tolerance = max(
        9.0,
        system_width * 0.004,
        (float(np.median(note_widths)) * 0.85) if note_widths else 0.0,
    )
    for x in candidates:
        if not candidate_barline_hits_staves(image, x, system):
            continue
        if any(abs(x - note_x) <= note_tolerance for note_x in note_centers):
            continue
        filtered.append(float(x))

    if not filtered:
        return []
    if note_centers and len(filtered) > max(8, int(len(note_centers) * 0.35)):
        return []
    return rhythm.sanitize_measure_boundaries(filtered, system_left, system_width)

def detect_augmentation_dot(image, note_obj, staff_coords, step):
    if image is None:
        return False
    otype = config.ID_MAP.get(note_obj["id"], "")
    if "whole" in otype or "half" in otype or "quarter" in otype:
        pass
    else:
        return False

    height, width = image.shape[:2]
    box = np.array(note_obj["box"], dtype=float)
    search_left = max(0, int(box[2] + max(2, step * 0.15)))
    search_right = min(width, int(box[2] + max(12, step * 2.4)))
    search_top = max(0, int(note_obj["y"] - max(6, step * 1.30)))
    search_bottom = min(height, int(note_obj["y"] + max(6, step * 1.30)))
    if search_right - search_left < 4 or search_bottom - search_top < 4:
        return False

    region = image[search_top:search_bottom, search_left:search_right]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 105, 255, cv2.THRESH_BINARY_INV)[1]
    component_count, labels, stats, _centroids = cv2.connectedComponentsWithStats(binary, 8)
    max_size = max(3.0, step * 1.40)
    min_area = max(2.0, step * step * 0.025)
    max_area = max(18.0, step * step * 0.82)
    for label in range(1, component_count):
        x, y, w, h, area = stats[label]
        if not (min_area <= area <= max_area):
            continue
        if w > max_size or h > max_size or w < 2 or h < 2:
            continue
        aspect = w / max(1, h)
        if 0.45 <= aspect <= 2.2:
            return True
    return False

def detect_augmentation_dot_object(note_obj, staff_objects, step):
    note_x = float(note_obj["x"])
    note_y = float(note_obj["y"])
    x_window = max(24.0, step * 4.8)
    y_window = max(6.0, step * 1.25)
    for candidate in staff_objects:
        if candidate is note_obj:
            continue
        if config.ID_MAP.get(candidate["id"], "") != "augmentationDot":
            continue
        if 0 <= candidate["x"] - note_x <= x_window and abs(candidate["y"] - note_y) <= y_window:
            return True
    return False

def flag_duration_beats(otype):
    if "128th" in otype:
        return 0.03125
    if "64th" in otype:
        return 0.0625
    if "32nd" in otype:
        return 0.125
    if "16th" in otype:
        return 0.25
    if "8th" in otype:
        return 0.5
    return None

def infer_flagged_duration_beats(note_obj, staff_objects, staff_coords, step):
    otype = config.ID_MAP.get(note_obj["id"], "")
    if "quarter" not in otype:
        return None

    note_x = float(note_obj["x"])
    note_y = float(note_obj["y"])
    x_window = max(22.0, step * 5.5)
    y_window = max(28.0, step * 6.5)
    candidates = []

    for candidate in staff_objects:
        if candidate is note_obj:
            continue
        candidate_type = config.ID_MAP.get(candidate["id"], "")
        if candidate_type == "beam":
            if abs(candidate["x"] - note_x) <= x_window * 1.4 and abs(candidate["y"] - note_y) <= y_window:
                candidates.append(0.5)
            continue
        if not candidate_type.startswith("flag"):
            continue
        duration = flag_duration_beats(candidate_type)
        if duration is None:
            continue
        if abs(candidate["x"] - note_x) <= x_window and abs(candidate["y"] - note_y) <= y_window:
            candidates.append(duration)

    return min(candidates) if candidates else None

def detect_tie_or_slur_after_note(note_obj, staff_objects, step):
    note_x = float(note_obj["x"])
    note_y = float(note_obj["y"])
    x_window = max(28.0, step * 7.0)
    y_window = max(14.0, step * 2.8)
    for candidate in staff_objects:
        if candidate is note_obj:
            continue
        candidate_type = config.ID_MAP.get(candidate["id"], "")
        if candidate_type not in {"tie", "slur"}:
            continue
        if 0 <= candidate["x"] - note_x <= x_window and abs(candidate["y"] - note_y) <= y_window:
            return candidate_type
    return None

def enrich_rhythmic_object_for_theory(obj, staff_coords, step, image, staff_objects=None):
    otype = config.ID_MAP.get(obj["id"], "")
    staff_objects = staff_objects or []
    base_beats = infer_flagged_duration_beats(obj, staff_objects, staff_coords, step)
    if base_beats is None:
        base_beats = rhythm.beats_for_type(otype)
    dotted = detect_augmentation_dot_object(obj, staff_objects, step) or detect_augmentation_dot(image, obj, staff_coords, step)
    multiplier = 1.5 if dotted else 1.0
    duration_beats = base_beats * multiplier
    payload = {
        **obj,
        "duration_beats": duration_beats,
        "duration_multiplier": multiplier,
    }
    if multiplier > 1.0:
        payload["dotted"] = True
    tie_or_slur = detect_tie_or_slur_after_note(obj, staff_objects, step)
    if tie_or_slur:
        payload[tie_or_slur] = True
    return payload

def time_signature_digit(otype):
    if not otype.startswith("timeSig"):
        return None
    suffix = otype.replace("timeSig", "")
    if suffix.isdigit():
        return suffix
    return None

def time_signature_objects_in_system(system, objects):
    bounds = system_bounds(system)
    staff_height = average_staff_height(system)
    first_music_x = first_existing_music_x_in_system(system, objects)
    search_right = first_music_x if first_music_x is not None else bounds[0] + ((bounds[2] - bounds[0]) * 0.26)
    search_right = max(search_right, bounds[0] + staff_height * 2.8)
    candidates = []
    for obj in objects:
        otype = config.ID_MAP.get(obj["id"], "")
        if not (otype.startswith("timeSig") or otype.startswith("numeral")):
            continue
        if not (bounds[0] - 8 <= obj["x"] <= search_right + 12):
            continue
        if not (bounds[1] - staff_height <= obj["y"] <= bounds[3] + staff_height):
            continue
        candidates.append({**obj, "type": otype})
    return sorted(candidates, key=lambda item: (item["x"], item["y"]))

def parse_time_signature_digits(candidates):
    digits = [
        candidate
        for candidate in candidates
        if time_signature_digit(candidate["type"]) is not None
    ]
    if not digits:
        return None

    y_values = sorted(candidate["y"] for candidate in digits)
    if len(y_values) < 2:
        return None
    split_y = (y_values[0] + y_values[-1]) / 2.0
    top_digits = sorted(
        [item for item in digits if item["y"] <= split_y],
        key=lambda item: item["x"],
    )
    bottom_digits = sorted(
        [item for item in digits if item["y"] > split_y],
        key=lambda item: item["x"],
    )
    if not top_digits or not bottom_digits:
        return None

    numerator_text = "".join(time_signature_digit(item["type"]) for item in top_digits)
    denominator_text = "".join(time_signature_digit(item["type"]) for item in bottom_digits)
    try:
        numerator = int(numerator_text)
        denominator = int(denominator_text)
    except ValueError:
        return None
    if numerator <= 0 or denominator <= 0:
        return None
    if denominator not in {1, 2, 4, 8, 16, 32}:
        return None
    return numerator, denominator

def infer_system_beats_per_measure(system, objects):
    candidates = time_signature_objects_in_system(system, objects)
    if any(item["type"] == "timeSigCommon" for item in candidates):
        return 4.0
    if any(item["type"] == "timeSigCutCommon" for item in candidates):
        return 4.0

    parsed = parse_time_signature_digits(candidates)
    if parsed:
        numerator, denominator = parsed
        return max(1.0, min(16.0, numerator * (4.0 / denominator)))
    return 4.0

def count_projection_runs(projection, threshold):
    runs = 0
    in_run = False
    for value in projection:
        if value >= threshold:
            if not in_run:
                runs += 1
                in_run = True
        else:
            in_run = False
    return runs

def chord_diagram_grid_detected(image, note_obj, staff_coords, step):
    if image is None:
        return False

    staff_top = staff_coords[1]
    x = int(note_obj["x"])
    y = int(note_obj["y"])
    half_width = int(max(24, step * 3.8))
    half_height = int(max(28, step * 4.8))
    left = max(0, x - half_width)
    right = min(image.shape[1], x + half_width)
    top = max(0, y - half_height)
    bottom = min(image.shape[0], y + half_height, int(staff_top - (step * 0.35)))
    if right - left < 18 or bottom - top < 18:
        return False

    region = image[top:bottom, left:right]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    dark_pixels = gray < 105
    height, width = dark_pixels.shape
    vertical_lines = count_projection_runs(dark_pixels.sum(axis=0), height * 0.34)
    horizontal_lines = count_projection_runs(dark_pixels.sum(axis=1), width * 0.20)
    return vertical_lines >= 3 and horizontal_lines >= 3

def is_above_staff_note_candidate(note_obj, staff_coords, step):
    note_y = note_obj["y"]
    staff_top = staff_coords[1]
    return staff_top - (step * 14.0) <= note_y <= staff_top - (step * 1.35)

def is_probable_chord_diagram_note(note_obj, staff_objects, staff_coords, step, image=None):
    otype = config.ID_MAP.get(note_obj["id"], "")
    if not is_rhythmic_object(otype) or "rest" in otype:
        return False
    if not is_above_staff_note_candidate(note_obj, staff_coords, step):
        return False

    if chord_diagram_grid_detected(image, note_obj, staff_coords, step):
        return True

    nearby = [
        obj for obj in staff_objects
        if obj is not note_obj
        and is_rhythmic_object(config.ID_MAP.get(obj["id"], ""))
        and is_above_staff_note_candidate(obj, staff_coords, step)
        and abs(obj["x"] - note_obj["x"]) <= max(18, step * 4.2)
        and abs(obj["y"] - note_obj["y"]) <= max(22, step * 5.2)
    ]
    if len(nearby) < 2:
        return False

    cluster = nearby + [note_obj]
    x_values = [obj["x"] for obj in cluster]
    y_values = [obj["y"] for obj in cluster]
    x_span = max(x_values) - min(x_values)
    y_span = max(y_values) - min(y_values)
    return x_span <= step * 4.6 and y_span >= step * 1.1

def build_key_signature(accidentals, first_music_x, staff_coords):
    if first_music_x is None:
        return {}

    staff_left, _, staff_right, _ = staff_coords
    staff_width = max(1, staff_right - staff_left)
    key_region_right = min(first_music_x - 6, staff_left + staff_width * 0.24)
    key_accidentals = [
        accidental
        for accidental in sorted(accidentals, key=lambda item: item["x"])
        if accidental["x"] <= key_region_right
    ]

    if not key_accidentals:
        return {}

    deduped = []
    x_tolerance = max(4, staff_width * 0.004)
    y_tolerance = max(5, (staff_coords[3] - staff_coords[1]) * 0.08)
    for accidental in key_accidentals:
        if any(
            abs(accidental["x"] - existing["x"]) <= x_tolerance
            and abs(accidental["y"] - existing["y"]) <= y_tolerance
            and accidental["accidental"] == existing["accidental"]
            for existing in deduped
        ):
            continue
        deduped.append(accidental)

    accidental_types = {accidental["accidental"] for accidental in deduped}
    if len(accidental_types) == 1:
        accidental_type = next(iter(accidental_types))
        if accidental_type in {"s", "b"}:
            key_order = SHARP_KEY_ORDER if accidental_type == "s" else FLAT_KEY_ORDER
            return {
                note: accidental_type
                for note in key_order[: min(len(deduped), len(key_order))]
            }

    key_signature = {}
    for accidental in deduped:
        key_signature[accidental["note"]] = accidental["accidental"]

    return key_signature

def infer_note_accidental(note_obj, note_base, octave, staff_info, system_width):
    accidentals = staff_info.get("accidentals", [])
    if not accidentals:
        return staff_info.get("key_signature", {}).get(note_base, "")

    step = max(1, staff_info["step"])
    x_window = max(28, min(90, system_width * 0.04))
    y_window = max(12, step * 1.65)
    note_x = note_obj["x"]
    note_y = note_obj["y"]

    local_candidates = [
        accidental
        for accidental in accidentals
        if 0 <= note_x - accidental["x"] <= x_window
        and accidental["note"] == note_base
        and accidental["octave"] == octave
        and abs(note_y - accidental["y"]) <= y_window
    ]

    if local_candidates:
        local_candidates.sort(
            key=lambda accidental: (
                abs(note_x - accidental["x"]),
                abs(note_y - accidental["y"]),
            )
        )
        return local_candidates[0]["accidental"]

    return staff_info.get("key_signature", {}).get(note_base, "")

def normalize_midi_events(midi_events, fallback_duration_ms):
    active_notes = {}
    intervals = []
    sorted_events = sorted(
        midi_events,
        key=lambda event: (event['time'], 0 if event['type'] == 'off' else 1),
    )
    for event in sorted_events:
        note = event['note']
        channel = int(event.get('channel', 0))
        active_key = (channel, note)
        if event['type'] == 'on':
            active_notes.setdefault(active_key, []).append(event)
            continue

        pending = active_notes.get(active_key)
        if not pending:
            continue
        start_event = pending.pop(0)
        start_time = int(start_event['time'])
        end_time = max(start_time + 1, int(event['time']))
        intervals.append({
            'start': start_time,
            'end': end_time,
            'note': note,
            'channel': channel,
            'vel': start_event['vel'],
        })

    fallback_duration_ms = max(1, int(fallback_duration_ms))
    for pending_events in active_notes.values():
        for start_event in pending_events:
            start_time = int(start_event['time'])
            intervals.append({
                'start': start_time,
                'end': start_time + fallback_duration_ms,
                'note': start_event['note'],
                'channel': int(start_event.get('channel', 0)),
                'vel': start_event['vel'],
            })

    merged_intervals = []
    for interval in sorted(intervals, key=lambda item: (item['channel'], item['note'], item['start'], item['end'])):
        if (
            merged_intervals
            and merged_intervals[-1]['channel'] == interval['channel']
            and merged_intervals[-1]['note'] == interval['note']
            and merged_intervals[-1]['start'] == interval['start']
        ):
            merged_intervals[-1]['end'] = max(merged_intervals[-1]['end'], interval['end'])
            merged_intervals[-1]['vel'] = max(merged_intervals[-1]['vel'], interval['vel'])
            continue
        merged_intervals.append(interval)
    intervals = merged_intervals

    previous_by_note = {}
    for interval in sorted(intervals, key=lambda item: (item['channel'], item['note'], item['start'], item['end'])):
        active_key = (interval['channel'], interval['note'])
        previous = previous_by_note.get(active_key)
        if previous and previous['end'] >= interval['start']:
            previous['end'] = max(previous['start'] + 1, interval['start'] - 1)
        if interval['end'] <= interval['start']:
            interval['end'] = interval['start'] + 1
        previous_by_note[active_key] = interval

    normalized_events = []
    for interval in intervals:
        normalized_events.append({
            'time': interval['start'],
            'type': 'on',
            'note': interval['note'],
            'channel': interval['channel'],
            'vel': interval['vel'],
        })
        normalized_events.append({
            'time': interval['end'],
            'type': 'off',
            'note': interval['note'],
            'channel': interval['channel'],
            'vel': 0,
        })
    normalized_events.sort(key=lambda event: (event['time'], 0 if event['type'] == 'off' else 1, event.get('channel', 0), event['note']))
    return normalized_events

def collect_system_dynamics(system, objects):
    bounds = system_bounds(system)
    staff_height = average_staff_height(system)
    y_top = bounds[1] - staff_height * 1.6
    y_bottom = bounds[3] + staff_height * 1.9
    raw_dynamics = []

    for obj in objects:
        dynamic_type = config.ID_MAP.get(obj["id"], "")
        if dynamic_type not in DYNAMIC_TYPES:
            continue
        if not (bounds[0] - 40 <= obj["x"] <= bounds[2] + 40):
            continue
        if not (y_top <= obj["y"] <= y_bottom):
            continue
        raw_dynamics.append({
            "x": obj["x"],
            "y": obj["y"],
            "type": dynamic_type,
        })

    raw_dynamics.sort(key=lambda item: (item["x"], item["y"]))
    dynamics = []
    used = set()
    merge_window = max(14.0, staff_height * 0.42)
    for index, dynamic in enumerate(raw_dynamics):
        if index in used:
            continue
        if dynamic["type"] == "dynamicM":
            partner_index = None
            partner_type = None
            for next_index in range(index + 1, len(raw_dynamics)):
                candidate = raw_dynamics[next_index]
                if next_index in used:
                    continue
                if candidate["x"] - dynamic["x"] > merge_window:
                    break
                if abs(candidate["y"] - dynamic["y"]) > merge_window:
                    continue
                if candidate["type"] in {"dynamicP", "dynamicF"}:
                    partner_index = next_index
                    partner_type = "dynamicM" + candidate["type"][-1]
                    break
            if partner_index is not None:
                used.add(index)
                used.add(partner_index)
                partner = raw_dynamics[partner_index]
                dynamics.append({
                    "x": min(dynamic["x"], partner["x"]),
                    "y": (dynamic["y"] + partner["y"]) / 2,
                    "type": partner_type,
                })
                continue
        dynamics.append(dynamic)

    return sorted(dynamics, key=lambda item: item["x"])

def infer_note_dynamic(note_obj, staff_info):
    dynamics = staff_info.get("dynamics", [])
    if not dynamics:
        return "default"

    previous = [dynamic for dynamic in dynamics if dynamic["x"] <= note_obj["x"] + 8]
    if not previous:
        return "default"

    return max(previous, key=lambda item: item["x"])["type"]

def dynamic_audio_velocity(dynamic_type):
    return float(config.VOLUME_MAP.get(dynamic_type, config.VOLUME_MAP["default"]))

def dynamic_midi_velocity(dynamic_type):
    velocity = dynamic_audio_velocity(dynamic_type)
    return int(clamp_value(round(velocity * 118), 32, 122))

def duration_for_type(otype, ms_per_beat):
    return rhythm.duration_ms_for_type(otype, ms_per_beat)

def duration_for_object(obj, otype, ms_per_beat):
    return rhythm.duration_ms_for_item(otype, obj, ms_per_beat)

def column_advance_ms(delta_x, system_width, ms_per_beat):
    return rhythm.column_advance_ms(delta_x, system_width, ms_per_beat)

def audible_duration_ms(otype, notated_duration, gap_to_next, ms_per_beat):
    return rhythm.audible_duration_ms(otype, notated_duration, gap_to_next, ms_per_beat)

def release_tail_ms(otype, gap_to_next, ms_per_beat):
    return rhythm.release_tail_ms(otype, gap_to_next, ms_per_beat)

def infer_staff_gap_threshold(staves):
    if len(staves) < 2:
        return 140

    gaps = [
        max(0, staves[i + 1][1] - staves[i][3])
        for i in range(len(staves) - 1)
    ]
    positive_gaps = sorted(gap for gap in gaps if gap > 0)

    if not positive_gaps:
        return 140

    # Dense piano pages usually alternate small gaps inside a grand staff and
    # larger gaps between systems. Use the largest jump to separate both groups.
    best_jump = 0
    threshold = positive_gaps[len(positive_gaps) // 2]
    for left, right in zip(positive_gaps, positive_gaps[1:]):
        jump = right - left
        if jump > best_jump:
            best_jump = jump
            threshold = (left + right) / 2

    staff_heights = [max(1, staff[3] - staff[1]) for staff in staves]
    median_height = float(np.median(staff_heights))
    lower = max(55, median_height * 1.4)
    upper = max(lower + 10, median_height * 4.5)
    return min(max(threshold, lower), upper)

def split_indices_by_staff_gaps(indices, staves, gap_threshold):
    if not indices:
        return []

    groups = [[indices[0]]]
    for prev_idx, idx in zip(indices, indices[1:]):
        gap = staves[idx][1] - staves[prev_idx][3]
        if gap <= gap_threshold:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups

def consolidate_duplicate_staves(staves):
    if len(staves) < 2:
        return sorted(staves, key=lambda box: box[1])

    ordered = sorted(staves, key=lambda box: (box[1] + box[3]) / 2)
    heights = [max(1, float(staff[3] - staff[1])) for staff in ordered]
    center_threshold = max(18, float(np.median(heights)) * 0.58)
    groups = []

    for staff in ordered:
        center_y = (staff[1] + staff[3]) / 2
        if not groups:
            groups.append([staff])
            continue

        previous = groups[-1]
        previous_center = np.mean([(box[1] + box[3]) / 2 for box in previous])
        if abs(center_y - previous_center) <= center_threshold:
            previous.append(staff)
        else:
            groups.append([staff])

    consolidated = []
    for group in groups:
        if len(group) == 1:
            consolidated.append(group[0])
            continue

        widest = max(group, key=lambda box: box[2] - box[0])
        merged = widest.copy()
        merged[0] = min(box[0] for box in group)
        merged[2] = max(box[2] for box in group)
        consolidated.append(merged)

    return sorted(consolidated, key=lambda box: box[1])

def staff_clef_hint(staff_index, staff_coords, staves, objects):
    if objects:
        system = staves
        return infer_staff_clef(system, staff_index, staff_coords, objects)
    return "clefG" if staff_index % 2 == 0 else "clefF"

def split_staff_group_by_clefs(group_indices, staves, objects):
    if len(group_indices) <= 2:
        return [group_indices]

    if len(group_indices) == 3:
        top_gap = staves[group_indices[1]][1] - staves[group_indices[0]][3]
        bottom_gap = staves[group_indices[2]][1] - staves[group_indices[1]][3]
        if bottom_gap <= top_gap * 1.25:
            return [[group_indices[0]], [group_indices[1], group_indices[2]]]

    groups = []
    i = 0
    while i < len(group_indices):
        idx = group_indices[i]
        if i + 1 < len(group_indices):
            next_idx = group_indices[i + 1]
            clef_a = staff_clef_hint(idx, staves[idx], staves, objects)
            clef_b = staff_clef_hint(next_idx, staves[next_idx], staves, objects)
            gap = staves[next_idx][1] - staves[idx][3]
            if clef_a == "clefG" and clef_b == "clefF" and gap <= infer_staff_gap_threshold(staves):
                groups.append([idx, next_idx])
                i += 2
                continue
        groups.append([idx])
        i += 1
    return groups

def group_staves_by_braces(staves, braces, objects=None):
    objects = objects or []
    staves = consolidate_duplicate_staves(staves)
    systems = []
    used_staves = set()
    gap_threshold = infer_staff_gap_threshold(staves)

    for brace in sorted(braces, key=lambda box: (box[1], box[0])):
        brace_top, brace_bottom = brace[1], brace[3]
        brace_height = max(1, brace_bottom - brace_top)
        margin = max(25, brace_height * 0.05)
        system_indices = []

        for idx, staff in enumerate(staves):
            staff_center_y = (staff[1] + staff[3]) / 2
            if brace_top - margin <= staff_center_y <= brace_bottom + margin:
                system_indices.append(idx)

        system_indices = [
            idx for idx in sorted(system_indices)
            if idx not in used_staves
        ]

        if len(system_indices) >= 2:
            max_width = max(staves[idx][2] - staves[idx][0] for idx in system_indices)
            full_width_indices = [
                idx for idx in system_indices
                if (staves[idx][2] - staves[idx][0]) >= max_width * 0.72
            ]
            candidates = full_width_indices if len(full_width_indices) >= 2 else system_indices
            group = list(candidates)
            for idx in system_indices:
                used_staves.add(idx)
            systems.append([staves[idx] for idx in group])

    i = 0
    while i < len(staves):
        staff = staves[i]
        if i in used_staves:
            i += 1
            continue

        current_indices = [i]
        j = i + 1
        while j < len(staves) and j not in used_staves:
            gap = staves[j][1] - staves[current_indices[-1]][3]
            if gap > gap_threshold:
                break
            current_indices.append(j)
            j += 1

        for group in split_staff_group_by_clefs(current_indices, staves, objects):
            for idx in group:
                used_staves.add(idx)
            systems.append([staves[idx] for idx in group])
        i = max(j, i + 1)

    return sorted(systems, key=lambda system: min(staff[1] for staff in system))

def system_bounds(system):
    return (
        min(staff[0] for staff in system),
        min(staff[1] for staff in system),
        max(staff[2] for staff in system),
        max(staff[3] for staff in system),
    )

def horizontal_overlap_ratio(bounds_a, bounds_b):
    overlap = max(0, min(bounds_a[2], bounds_b[2]) - max(bounds_a[0], bounds_b[0]))
    reference_width = max(1, min(bounds_a[2] - bounds_a[0], bounds_b[2] - bounds_b[0]))
    return overlap / reference_width

def average_staff_height(system):
    return float(np.mean([max(1, staff[3] - staff[1]) for staff in system]))

def should_merge_system_pair(upper_system, lower_system):
    if len(upper_system) != 1 or len(lower_system) != 2:
        return False

    upper_bounds = system_bounds(upper_system)
    lower_bounds = system_bounds(lower_system)
    if lower_bounds[1] <= upper_bounds[3]:
        return False

    overlap = horizontal_overlap_ratio(upper_bounds, lower_bounds)
    if overlap < 0.45:
        return False

    gap = lower_bounds[1] - upper_bounds[3]
    staff_height = (average_staff_height(upper_system) + average_staff_height(lower_system)) / 2
    max_gap = max(260, staff_height * 9.0)
    return gap <= max_gap

def merge_playback_systems(systems):
    ordered = sorted(systems, key=lambda system: min(staff[1] for staff in system))
    playback_systems = []
    i = 0

    while i < len(ordered):
        current = ordered[i]
        if i + 1 < len(ordered) and should_merge_system_pair(current, ordered[i + 1]):
            merged = sorted(list(current) + list(ordered[i + 1]), key=lambda staff: staff[1])
            playback_systems.append(merged)
            i += 2
            continue
        playback_systems.append(current)
        i += 1

    return playback_systems

def group_objects_by_x(objects, tolerance):
    columns = []
    for obj in sorted(objects, key=lambda item: item['x']):
        if columns and abs(obj['x'] - columns[-1]['x']) <= tolerance:
            columns[-1]['items'].append(obj)
            columns[-1]['x'] = sum(item['x'] for item in columns[-1]['items']) / len(columns[-1]['items'])
        else:
            columns.append({'x': obj['x'], 'items': [obj]})
    return columns

def estimate_note_width(objects, fallback):
    widths = [
        max(1, float(obj["box"][2] - obj["box"][0]))
        for obj in objects
        if is_rhythmic_object(config.ID_MAP.get(obj["id"], ""))
    ]
    if not widths:
        return fallback
    return float(np.median(widths))

def annotate_local_column_spacing(columns, fallback_width):
    if not columns:
        return columns
    for idx, column in enumerate(columns):
        gaps = []
        if idx > 0:
            gaps.append(abs(column["x"] - columns[idx - 1]["x"]))
        if idx + 1 < len(columns):
            gaps.append(abs(columns[idx + 1]["x"] - column["x"]))
        positive_gaps = [gap for gap in gaps if gap > 0]
        column["local_spacing"] = min(positive_gaps) if positive_gaps else fallback_width
    return columns

def can_merge_staff_columns(column, candidate, base_tolerance):
    delta = abs(column["x"] - candidate["x"])
    local_spacing = min(
        column.get("local_spacing", base_tolerance * 4),
        candidate.get("local_spacing", base_tolerance * 4),
    )
    adaptive_tolerance = max(6, min(base_tolerance, local_spacing * 0.30))
    return delta <= adaptive_tolerance

def build_staff_note_columns(system, objects, image=None):
    staff_data = []
    staff_columns = []
    system_left = min(staff[0] for staff in system)
    system_right = max(staff[2] for staff in system)
    system_width = max(1, system_right - system_left)
    system_dynamics = collect_system_dynamics(system, objects)
    note_width = estimate_note_width(objects, max(8, system_width * 0.006))
    staff_tolerance = max(6, min(13, note_width * 0.42, system_width * 0.007))
    cross_staff_tolerance = max(10, min(24, note_width * 0.78, system_width * 0.014))

    for s_idx, s_coords in enumerate(system):
        step = (s_coords[3] - s_coords[1]) / 8
        objs_pauta = [
            o for o in objects
            if s_coords[1] - 40 < o['y'] < s_coords[3] + 40
        ]
        clef = infer_staff_clef(system, s_idx, s_coords, objects)
        accidental_objs = []
        for o in objs_pauta:
            accidental = ACCIDENTAL_TYPES.get(config.ID_MAP.get(o['id'], ""))
            if not accidental:
                continue
            acc_note, acc_octave = vision_utils.calculate_pitch(
                o['y'],
                s_coords[3],
                step,
                clef,
            )
            accidental_objs.append({
                **o,
                "accidental": accidental,
                "note": acc_note,
                "octave": acc_octave,
            })
        rhythmic_objs = []
        for o in objs_pauta:
            if not is_rhythmic_object(config.ID_MAP.get(o['id'], "")):
                continue
            if is_probable_chord_diagram_note(o, objs_pauta, s_coords, step, image):
                continue
            enriched = enrich_rhythmic_object_for_theory(o, s_coords, step, image, objs_pauta)
            rhythmic_objs.append({**enriched, "staff_index": s_idx})
        first_music_x = min((o["x"] for o in rhythmic_objs), default=None)
        staff_specific_columns = annotate_local_column_spacing(
            group_objects_by_x(rhythmic_objs, staff_tolerance),
            max(1, system_width / SYSTEM_WIDTH_BEATS),
        )
        for column in staff_specific_columns:
            column["staff_indices"] = {s_idx}
            staff_columns.append(column)
        staff_data.append({
            "coords": s_coords,
            "step": step,
            "clef": clef,
            "accidentals": accidental_objs,
            "key_signature": build_key_signature(accidental_objs, first_music_x, s_coords),
            "dynamics": system_dynamics,
        })

    system_columns = []
    for column in sorted(staff_columns, key=lambda item: item["x"]):
        target = None
        for candidate in system_columns:
            if column["staff_indices"] & candidate["staff_indices"]:
                continue
            if can_merge_staff_columns(column, candidate, cross_staff_tolerance):
                target = candidate
                break
        if target is None:
            system_columns.append({
                "x": column["x"],
                "items": list(column["items"]),
                "staff_indices": set(column["staff_indices"]),
            })
        else:
            target["items"].extend(column["items"])
            target["staff_indices"].update(column["staff_indices"])
            target["x"] = sum(item["x"] for item in target["items"]) / len(target["items"])
            target["local_spacing"] = min(
                target.get("local_spacing", cross_staff_tolerance),
                column.get("local_spacing", cross_staff_tolerance),
            )

    return staff_data, system_columns, system_left, system_width

def infer_staff_clef(system, staff_index, staff_coords, objects):
    staff_height = max(1, staff_coords[3] - staff_coords[1])
    staff_width = max(1, staff_coords[2] - staff_coords[0])
    staff_center_y = (staff_coords[1] + staff_coords[3]) / 2
    search_right = staff_coords[0] + staff_width * 0.22
    candidates = []

    for obj in objects:
        otype = config.ID_MAP.get(obj['id'], "")
        if otype not in ("clefG", "clefF"):
            continue
        if obj['x'] > search_right:
            continue
        if not (staff_coords[1] - staff_height <= obj['y'] <= staff_coords[3] + staff_height):
            continue
        candidates.append((abs(obj['y'] - staff_center_y), obj['x'], otype))

    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2]

    if len(system) >= 2:
        return "clefG" if staff_index == 0 else "clefF"

    return "clefG"

def get_event_context(events, t_ms):
    previous_event = None
    next_event = None

    for event in events:
        if event['time'] <= t_ms:
            previous_event = event
        else:
            next_event = event
            break

    return previous_event, next_event

def interpolate_playhead(previous_event, next_event, t_ms):
    if previous_event is None and next_event is None:
        return None
    if previous_event is None:
        return next_event
    if next_event is None:
        return previous_event
    if previous_event['page'] != next_event['page']:
        return previous_event

    span = max(1, next_event['time'] - previous_event['time'])
    progress = min(1, max(0, (t_ms - previous_event['time']) / span))
    eased = 0.5 - 0.5 * np.cos(np.pi * progress)

    return {
        'x': previous_event['x'] + (next_event['x'] - previous_event['x']) * eased,
        'y': previous_event['y'] + (next_event['y'] - previous_event['y']) * eased,
        'page': previous_event['page'],
        'vol': previous_event.get('vol', 0.8),
    }

def draw_soft_circle(frame, center, radius, color, alpha):
    overlay = frame.copy()
    cv2.circle(overlay, center, radius, color, -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_soft_line(frame, start, end, color, thickness, alpha):
    overlay = frame.copy()
    cv2.line(overlay, start, end, color, thickness, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_reading_marker(frame, playhead, t_ms):
    x = int(playhead['x'])
    y = int(playhead['y'])
    pulse = 0.5 + 0.5 * np.sin(t_ms / 190)
    glow_color = (255, 205, 80)
    core_color = (255, 245, 210)

    draw_soft_circle(frame, (x, y), int(40 + 8 * pulse), glow_color, 0.16)
    draw_soft_circle(frame, (x, y), int(22 + 5 * pulse), glow_color, 0.24)
    draw_soft_line(frame, (max(0, x - 58), y), (min(frame.shape[1] - 1, x + 34), y), glow_color, 5, 0.22)
    draw_soft_line(frame, (max(0, x - 38), y), (min(frame.shape[1] - 1, x + 18), y), core_color, 2, 0.52)
    cv2.circle(frame, (x, y), 9, glow_color, 2, cv2.LINE_AA)
    cv2.circle(frame, (x, y), 3, core_color, -1, cv2.LINE_AA)

def draw_active_note_highlight(frame, event, t_ms):
    x = int(event['x'])
    y = int(event['y'])
    duration = max(1, event['dur'])
    progress = min(1, max(0, (t_ms - event['time']) / duration))
    pulse = 0.5 + 0.5 * np.sin(progress * np.pi)
    volume = max(0.35, min(1.0, event.get('vol', 0.72)))
    halo_color = (64, 214, 255)
    core_color = (255, 255, 255)
    radius = int(14 + 12 * pulse * volume)

    draw_soft_circle(frame, (x, y), radius + 20, halo_color, 0.09 + 0.06 * volume)
    draw_soft_circle(frame, (x, y), radius + 6, halo_color, 0.16 + 0.07 * volume)
    cv2.circle(frame, (x, y), radius, halo_color, 2, cv2.LINE_AA)
    cv2.circle(frame, (x, y), 4, core_color, -1, cv2.LINE_AA)

def render_video_frame(page_frames, video_events, active_events, t_ms, transition_ms=450):
    previous_event, next_event = get_event_context(video_events, t_ms)

    current_page = previous_event['page'] if previous_event else 0
    if next_event and previous_event and next_event['page'] != previous_event['page']:
        transition_start = max(previous_event['time'], next_event['time'] - transition_ms)
        if t_ms >= transition_start:
            alpha = min(1, max(0, (t_ms - transition_start) / max(1, next_event['time'] - transition_start)))
            previous_frame = page_frames[previous_event['page']]
            next_frame = page_frames[next_event['page']]
            if previous_frame.shape != next_frame.shape:
                next_frame = cv2.resize(
                    next_frame,
                    (previous_frame.shape[1], previous_frame.shape[0]),
                    interpolation=cv2.INTER_AREA
                )
            frame = cv2.addWeighted(
                previous_frame,
                1 - alpha,
                next_frame,
                alpha,
                0
            )
            current_page = next_event['page'] if alpha >= 0.5 else previous_event['page']
        else:
            frame = page_frames[current_page].copy()
    elif previous_event is None and next_event is not None:
        frame = page_frames[next_event['page']].copy()
        current_page = next_event['page']
    else:
        frame = page_frames[current_page].copy()

    playhead = interpolate_playhead(previous_event, next_event, t_ms)
    if playhead and int(playhead['page']) == current_page:
        draw_reading_marker(frame, playhead, t_ms)

    for event in active_events:
        if event['page'] != current_page:
            continue
        draw_active_note_highlight(frame, event, t_ms)

    return frame

def midi_pitch_class(midi_note):
    return int(midi_note) % 12

def midi_is_black(midi_note):
    return midi_pitch_class(midi_note) in PIANO_ROLL_BLACK_CLASSES

def midi_note_name(midi_note):
    midi_note = int(midi_note)
    return f"{PIANO_ROLL_NOTE_NAMES[midi_pitch_class(midi_note)]}{(midi_note // 12) - 1}"

def visual_hand_for_staff(staff_index, staff_count, clef):
    if clef == "clefF":
        return "left"
    if clef == "clefG":
        return "right"
    if staff_count > 1 and staff_index >= max(1, staff_count // 2):
        return "left"
    return "right"

def clamp_midi_range(note_events):
    if not note_events:
        return 48, 84

    midi_values = [int(event.get("midi", 60)) for event in note_events]
    minimum = min(midi_values)
    maximum = max(midi_values)
    if maximum - minimum < 24:
        center = round((minimum + maximum) / 2)
        minimum = center - 12
        maximum = center + 12

    minimum = max(21, minimum - midi_pitch_class(minimum))
    maximum = min(108, maximum + (11 - midi_pitch_class(maximum)))
    return minimum, maximum

def build_piano_key_layout(min_midi, max_midi, left, right):
    white_midis = [midi for midi in range(min_midi, max_midi + 1) if not midi_is_black(midi)]
    white_count = max(1, len(white_midis))
    white_width = (right - left) / white_count
    black_width = white_width * 0.62
    layout = {}
    white_lefts = {}

    for index, midi in enumerate(white_midis):
        key_left = left + (index * white_width)
        layout[midi] = {
            "x": key_left,
            "width": white_width,
            "black": False,
        }
        white_lefts[midi] = key_left

    for midi in range(min_midi, max_midi + 1):
        if not midi_is_black(midi):
            continue
        previous_white = midi - 1
        while previous_white >= min_midi and midi_is_black(previous_white):
            previous_white -= 1
        if previous_white not in white_lefts:
            continue
        key_left = white_lefts[previous_white] + white_width - (black_width / 2)
        layout[midi] = {
            "x": key_left,
            "width": black_width,
            "black": True,
        }

    return layout, white_width, black_width

def draw_round_rect(frame, rect, color, radius=12, alpha=1.0):
    x1, y1, x2, y2 = [int(round(value)) for value in rect]
    x1 = max(0, min(frame.shape[1] - 1, x1))
    x2 = max(0, min(frame.shape[1], x2))
    y1 = max(0, min(frame.shape[0] - 1, y1))
    y2 = max(0, min(frame.shape[0], y2))
    if x2 <= x1 or y2 <= y1:
        return

    radius = int(max(0, min(radius, (x2 - x1) // 2, (y2 - y1) // 2)))
    if alpha < 1:
        roi = frame[y1:y2, x1:x2]
        target = roi.copy()
        local_x1, local_y1 = 0, 0
        local_x2, local_y2 = target.shape[1] - 1, target.shape[0] - 1
    else:
        target = frame
        local_x1, local_y1, local_x2, local_y2 = x1, y1, x2, y2

    if radius <= 0:
        cv2.rectangle(target, (local_x1, local_y1), (local_x2, local_y2), color, -1, cv2.LINE_AA)
    else:
        cv2.rectangle(target, (local_x1 + radius, local_y1), (local_x2 - radius, local_y2), color, -1, cv2.LINE_AA)
        cv2.rectangle(target, (local_x1, local_y1 + radius), (local_x2, local_y2 - radius), color, -1, cv2.LINE_AA)
        cv2.circle(target, (local_x1 + radius, local_y1 + radius), radius, color, -1, cv2.LINE_AA)
        cv2.circle(target, (local_x2 - radius, local_y1 + radius), radius, color, -1, cv2.LINE_AA)
        cv2.circle(target, (local_x1 + radius, local_y2 - radius), radius, color, -1, cv2.LINE_AA)
        cv2.circle(target, (local_x2 - radius, local_y2 - radius), radius, color, -1, cv2.LINE_AA)

    if alpha < 1:
        cv2.addWeighted(target, alpha, roi, 1 - alpha, 0, roi)

def draw_gradient_round_rect(frame, rect, top_color, bottom_color, radius=12, alpha=1.0, border_color=None, border_alpha=0.0):
    x1, y1, x2, y2 = [int(round(value)) for value in rect]
    x1 = max(0, min(frame.shape[1] - 1, x1))
    x2 = max(0, min(frame.shape[1], x2))
    y1 = max(0, min(frame.shape[0] - 1, y1))
    y2 = max(0, min(frame.shape[0], y2))
    if x2 <= x1 or y2 <= y1:
        return

    roi = frame[y1:y2, x1:x2]
    roi_h, roi_w = roi.shape[:2]
    local_mask = np.zeros((roi_h, roi_w), dtype=np.uint8)
    draw_round_rect(local_mask, (0, 0, roi_w - 1, roi_h - 1), 255, radius, 1.0)

    top = np.asarray(top_color, dtype=np.float32)
    bottom = np.asarray(bottom_color, dtype=np.float32)
    blend = np.linspace(0.0, 1.0, roi_h, dtype=np.float32)[:, None, None]
    gradient = np.broadcast_to(top * (1.0 - blend) + bottom * blend, (roi_h, roi_w, 3))
    mask_alpha = (local_mask.astype(np.float32) / 255.0 * alpha)[:, :, None]
    roi[:] = np.clip(roi.astype(np.float32) * (1.0 - mask_alpha) + gradient * mask_alpha, 0, 255).astype(np.uint8)

    if border_color is not None and border_alpha > 0:
        eroded = cv2.erode(local_mask, np.ones((3, 3), dtype=np.uint8), iterations=1)
        border = cv2.subtract(local_mask, eroded).astype(np.float32) / 255.0
        border = (border * border_alpha)[:, :, None]
        color = np.asarray(border_color, dtype=np.float32)[None, None, :]
        roi[:] = np.clip(roi.astype(np.float32) * (1.0 - border) + color * border, 0, 255).astype(np.uint8)

def add_glow(frame, mask, color, sigma=18, strength=0.65):
    points = cv2.findNonZero(mask)
    if points is None:
        return
    x, y, width, height = cv2.boundingRect(points)
    padding = max(4, int(round(sigma * 3)))
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(mask.shape[1], x + width + padding)
    y2 = min(mask.shape[0], y + height + padding)
    mask_roi = mask[y1:y2, x1:x2]
    blurred = cv2.GaussianBlur(mask_roi, (0, 0), sigmaX=sigma, sigmaY=sigma)
    glow_alpha = (blurred.astype(np.float32) / 255.0 * strength)[:, :, None]
    color_layer = np.asarray(color, dtype=np.float32)[None, None, :]
    roi = frame[y1:y2, x1:x2]
    roi[:] = np.clip(roi.astype(np.float32) * (1.0 - glow_alpha) + color_layer * glow_alpha, 0, 255).astype(np.uint8)

def draw_soft_rect_glow(frame, rect, color, radius=10, strength=0.30):
    for expansion, factor in ((18, 0.10), (10, 0.16), (5, 0.24)):
        expanded = (
            rect[0] - expansion,
            rect[1] - expansion,
            rect[2] + expansion,
            rect[3] + expansion,
        )
        draw_round_rect(frame, expanded, color, radius + expansion, strength * factor,)

def add_radial_glow(frame, center, radius, color, strength):
    center_x, center_y = center
    x1 = max(0, int(center_x - radius))
    x2 = min(frame.shape[1], int(center_x + radius))
    y1 = max(0, int(center_y - radius))
    y2 = min(frame.shape[0], int(center_y + radius))
    if x2 <= x1 or y2 <= y1:
        return

    yy, xx = np.ogrid[y1:y2, x1:x2]
    distance = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2) / max(1.0, radius)
    alpha = np.clip(1.0 - distance, 0.0, 1.0) ** 2
    alpha = (alpha * strength)[:, :, None]
    roi = frame[y1:y2, x1:x2].astype(np.float32)
    color_layer = np.asarray(color, dtype=np.float32)[None, None, :]
    frame[y1:y2, x1:x2] = np.clip(roi * (1.0 - alpha) + color_layer * alpha, 0, 255).astype(np.uint8)

def draw_glass_panel(frame, rect, radius=24, strong=False):
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    shadow_rect = (rect[0], rect[1] + 10, rect[2], rect[3] + 10)
    draw_round_rect(mask, shadow_rect, 255, radius, 1.0)
    add_glow(frame, mask, (0, 0, 0), sigma=28, strength=0.34)
    fill = PIANO_ROLL_PANEL_STRONG if strong else PIANO_ROLL_PANEL
    draw_gradient_round_rect(
        frame,
        rect,
        fill,
        PIANO_ROLL_BG,
        radius,
        0.88,
        PIANO_ROLL_BORDER,
        0.18,
    )

def draw_piano_roll_background(frame, top, keyboard_y, left, right, key_layout):
    height, width = frame.shape[:2]
    frame[:] = PIANO_ROLL_BG
    add_radial_glow(frame, (int(width * 0.14), int(height * 0.10)), int(width * 0.34), PIANO_ROLL_RIGHT_COLOR, 0.12)
    add_radial_glow(frame, (int(width * 0.85), int(height * 0.08)), int(width * 0.28), PIANO_ROLL_LEFT_COLOR, 0.10)

    draw_glass_panel(frame, (28, 28, width - 28, height - 28), 28, strong=False)

    play_line_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.line(play_line_mask, (left, keyboard_y), (right, keyboard_y), 255, 3, cv2.LINE_AA)
    add_glow(frame, play_line_mask, PIANO_ROLL_RIGHT_COLOR, sigma=16, strength=0.76)
    cv2.line(frame, (left, keyboard_y), (right, keyboard_y), PIANO_ROLL_RIGHT_COLOR, 3, cv2.LINE_AA)

    for midi, key in key_layout.items():
        if key["black"]:
            continue
        x = int(key["x"])
        cv2.line(frame, (x, top), (x, keyboard_y), (35, 30, 26), 1, cv2.LINE_AA)
    cv2.line(frame, (right, top), (right, keyboard_y), (35, 30, 26), 1, cv2.LINE_AA)

    for beat_line in range(1, 13):
        y = top + int((keyboard_y - top) * beat_line / 13)
        cv2.line(frame, (left, y), (right, y), (35, 30, 26), 1, cv2.LINE_AA)

def draw_piano_keyboard(frame, min_midi, max_midi, key_layout, white_width, black_width, keyboard_y, keyboard_h, active_hands, overlay_only=False):
    bottom = keyboard_y + keyboard_h
    for midi, hand in active_hands.items():
        key = key_layout.get(midi)
        if not key:
            continue
        key_bottom = keyboard_y + (int(keyboard_h * 0.62) if key["black"] else keyboard_h)
        glow_color = PIANO_ROLL_LEFT_COLOR if hand == "left" else PIANO_ROLL_RIGHT_COLOR
        draw_soft_rect_glow(frame, (key["x"], keyboard_y, key["x"] + key["width"], key_bottom), glow_color, 7, 0.42)

    for midi in range(min_midi, max_midi + 1):
        key = key_layout.get(midi)
        if not key or key["black"]:
            continue
        x1 = int(key["x"])
        x2 = int(key["x"] + key["width"])
        hand = active_hands.get(midi)
        if overlay_only and hand is None:
            continue
        if hand == "right":
            top_color, bottom_color = (255, 240, 138), PIANO_ROLL_RIGHT_COLOR
        elif hand == "left":
            top_color, bottom_color = (208, 255, 196), PIANO_ROLL_LEFT_COLOR
        else:
            top_color, bottom_color = (255, 255, 255), (245, 231, 220)
        draw_gradient_round_rect(frame, (x1, keyboard_y, x2, bottom), top_color, bottom_color, 8, 1.0, (26, 16, 10), 0.42)

        label = midi_note_name(midi)
        text_size = cv2.getTextSize(label, FONT_FACE, 0.42, 1)[0]
        cv2.putText(
            frame,
            label,
            (x1 + max(3, (x2 - x1 - text_size[0]) // 2), bottom - 14),
            FONT_FACE,
            0.42,
            (44, 58, 78),
            1,
            cv2.LINE_AA,
        )

    black_h = int(keyboard_h * 0.62)
    for midi in range(min_midi, max_midi + 1):
        key = key_layout.get(midi)
        if not key or not key["black"]:
            continue
        x1 = int(key["x"])
        x2 = int(key["x"] + black_width)
        hand = active_hands.get(midi)
        if hand == "right":
            top_color, bottom_color = PIANO_ROLL_RIGHT_DARK, (104, 83, 7)
        elif hand == "left":
            top_color, bottom_color = PIANO_ROLL_LEFT_DARK, (34, 90, 13)
        else:
            top_color, bottom_color = (39, 27, 21), (13, 6, 3)
        draw_gradient_round_rect(frame, (x1, keyboard_y, x2, keyboard_y + black_h), top_color, bottom_color, 7, 1.0, (0, 0, 0), 0.62)

def render_piano_roll_frame(note_events, t_ms, duration_ms, roll_state):
    width = roll_state["width"]
    height = roll_state["height"]
    top = roll_state["top"]
    left = roll_state["left"]
    right = roll_state["right"]
    keyboard_y = roll_state["keyboard_y"]
    keyboard_h = roll_state["keyboard_h"]
    key_layout = roll_state["key_layout"]
    min_midi = roll_state["min_midi"]
    max_midi = roll_state["max_midi"]
    white_width = roll_state["white_width"]
    black_width = roll_state["black_width"]
    lead_ms = roll_state["lead_ms"]
    px_per_ms = (keyboard_y - top) / lead_ms

    background = roll_state.get("background")
    if background is not None:
        frame = background.copy()
    else:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        draw_piano_roll_background(frame, top, keyboard_y, left, right, key_layout)

    active_hands = {
        int(event["midi"]): event.get("hand", "right")
        for event in note_events
        if event["time"] <= t_ms <= event["time"] + event["dur"]
    }

    visible_events = [
        event for event in note_events
        if event["time"] - lead_ms <= t_ms <= event["time"] + event["dur"] + 260
    ]
    visible_events.sort(key=lambda item: (midi_is_black(item.get("midi", 60)), item.get("time", 0)))

    rendered_notes = []
    for event in visible_events:
        midi = int(event.get("midi", 60))
        key = key_layout.get(midi)
        if key is None:
            continue

        note_start = float(event["time"])
        note_end = note_start + max(60, float(event["dur"]))
        y_bottom = keyboard_y - ((note_start - t_ms) * px_per_ms)
        y_top = keyboard_y - ((note_end - t_ms) * px_per_ms)
        if y_bottom < top or y_top > keyboard_y:
            continue

        y1 = max(top, min(keyboard_y, y_top))
        y2 = max(top, min(keyboard_y, y_bottom))
        if y2 - y1 < 5:
            y2 = y1 + 5

        hand = event.get("hand", "right")
        black_note = midi_is_black(midi)
        x1 = key["x"] + (2 if not key["black"] else 1)
        x2 = key["x"] + key["width"] - (2 if not key["black"] else 1)
        rendered_notes.append((event, x1, y1, x2, y2, hand, black_note, note_start, note_end))

    for event, x1, y1, x2, y2, hand, black_note, note_start, note_end in rendered_notes:
        if hand == "left":
            top_color = PIANO_ROLL_LEFT_DARK if black_note else PIANO_ROLL_LEFT_COLOR
            bottom_color = (34, 90, 13) if black_note else (74, 180, 43)
        else:
            top_color = PIANO_ROLL_RIGHT_DARK if black_note else PIANO_ROLL_RIGHT_COLOR
            bottom_color = (104, 83, 7) if black_note else (211, 169, 22)
        is_active = note_start <= t_ms <= note_end
        glow_color = PIANO_ROLL_LEFT_COLOR if hand == "left" else PIANO_ROLL_RIGHT_COLOR
        draw_soft_rect_glow(frame, (x1, y1, x2, y2), glow_color, 8, 0.26 if is_active else 0.16)
        draw_round_rect(frame, (x1, y1 + 8, x2, y2 + 8), (0, 0, 0), 8, 0.24)
        draw_gradient_round_rect(
            frame,
            (x1, y1, x2, y2),
            top_color,
            bottom_color,
            8,
            0.98 if is_active else 0.90,
            (255, 255, 255),
            0.46 if is_active else 0.28,
        )

        midi = int(event.get("midi", 60))
        key = key_layout.get(midi)
        if key and y2 - y1 > 30 and key["width"] > 26:
            label = event.get("label") or midi_note_name(midi)
            text_scale = 0.42 if key["width"] < 44 else 0.52
            text_size = cv2.getTextSize(label, FONT_FACE, text_scale, 1)[0]
            if text_size[0] < (x2 - x1) - 4:
                cv2.putText(
                    frame,
                    label,
                    (int(x1 + ((x2 - x1 - text_size[0]) / 2)), int(y2 - 10)),
                    FONT_FACE,
                    text_scale,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

    draw_piano_keyboard(
        frame,
        min_midi,
        max_midi,
        key_layout,
        white_width,
        black_width,
        keyboard_y,
        keyboard_h,
        active_hands,
        overlay_only=True,
    )

    return frame

def build_piano_roll_state(note_events):
    width = PIANO_ROLL_WIDTH
    height = PIANO_ROLL_HEIGHT
    left = 84
    right = width - 84
    top = 48
    keyboard_y = 782
    keyboard_h = 250
    min_midi, max_midi = clamp_midi_range(note_events)
    key_layout, white_width, black_width = build_piano_key_layout(min_midi, max_midi, left, right)
    state = {
        "width": width,
        "height": height,
        "left": left,
        "right": right,
        "top": top,
        "keyboard_y": keyboard_y,
        "keyboard_h": keyboard_h,
        "min_midi": min_midi,
        "max_midi": max_midi,
        "key_layout": key_layout,
        "white_width": white_width,
        "black_width": black_width,
        "lead_ms": PIANO_ROLL_LEAD_MS,
    }
    background = np.zeros((height, width, 3), dtype=np.uint8)
    draw_piano_roll_background(background, top, keyboard_y, left, right, key_layout)
    draw_piano_keyboard(
        background,
        min_midi,
        max_midi,
        key_layout,
        white_width,
        black_width,
        keyboard_y,
        keyboard_h,
        {},
    )
    state["background"] = background
    return state

def build_review_summary(score_events, page_count, duration_ms, key_signatures=None, staff_crop_recovery=None):
    events = list(score_events or [])
    confidence_values = [
        float(event.confidence)
        for event in events
        if event.confidence is not None
    ]
    low_confidence_count = sum(1 for value in confidence_values if value < 0.38)
    review_confidence_count = sum(1 for value in confidence_values if 0.38 <= value < 0.55)
    high_confidence_count = sum(1 for value in confidence_values if value >= 0.55)
    average_confidence = (
        round(sum(confidence_values) / len(confidence_values), 4)
        if confidence_values
        else None
    )

    left_hand_count = sum(1 for event in events if event.hand == "left")
    right_hand_count = sum(1 for event in events if event.hand != "left")
    accidental_count = sum(1 for event in events if event.accidental)
    invalid_duration_count = sum(1 for event in events if event.duration_ms <= 0)
    pitch_class_counts = {}
    for event in events:
        pitch_key = f"{event.note}{event.accidental}"
        pitch_class_counts[pitch_key] = pitch_class_counts.get(pitch_key, 0) + 1

    if not events:
        quality = "empty"
    elif low_confidence_count or review_confidence_count > max(3, len(events) * 0.08):
        quality = "review"
    else:
        quality = "ready"

    summary = {
        "quality": quality,
        "event_count": len(events),
        "page_count": int(page_count),
        "duration_seconds": round(max(0, int(duration_ms)) / 1000, 2),
        "average_confidence": average_confidence,
        "confidence_count": len(confidence_values),
        "low_confidence_count": low_confidence_count,
        "review_confidence_count": review_confidence_count,
        "high_confidence_count": high_confidence_count,
        "left_hand_count": left_hand_count,
        "right_hand_count": right_hand_count,
        "accidental_count": accidental_count,
        "invalid_duration_count": invalid_duration_count,
        "pitch_class_counts": dict(sorted(pitch_class_counts.items())),
        "key_signature_count": len(key_signatures or []),
    }
    if staff_crop_recovery:
        summary["staff_crop_recovery"] = {
            "enabled": bool(staff_crop_recovery.get("enabled")),
            "crop_count": int(staff_crop_recovery.get("crop_count", 0)),
            "recovered_count": int(staff_crop_recovery.get("recovered_count", 0)),
            "rejected_count": int(staff_crop_recovery.get("rejected_count", 0)),
            "pages": list(staff_crop_recovery.get("pages", [])),
        }
    return summary

def process_score_files(file_list, bpm, progress_callback=None, output_options=None):
    if output_options is None:
        output_options = {
            "annotations": True,
            "audio": True,
            "midi": True,
            "video": True,
            "annotation_mode": "clean",
        }
    options = OutputOptions.from_mapping(output_options)
    language = options.language
    if language not in PROGRESS_MESSAGES:
        language = "en"
    messages = PROGRESS_MESSAGES[language]

    def progress(message_key, percent=None, **kwargs):
        message = messages.get(message_key, message_key).format(**kwargs)
        if progress_callback:
            try:
                progress_callback(message, percent)
            except TypeError:
                progress_callback(message)
        print(message)

    if not file_list:
        return None

    file_list = sorted(list(file_list))
    want_annotations = options.annotations
    want_audio = options.audio
    want_midi = options.midi
    want_video = options.video
    want_scientific_report = options.scientific_report
    use_preprocessing = options.preprocess
    use_staff_crop_recovery = options.staff_crop_recovery
    annotation_mode = options.annotation_mode
    video_mode = options.video_mode
    timbre = audio_utils.normalize_timbre(options.timbre)
    use_soundfont_audio = audio_utils.is_soundfont_timbre(timbre)
    annotated_files = []
    output_stem = safe_output_stem(file_list[0])
    output_dir = Path.cwd() / f"results_{output_stem}"
    output_dir.mkdir(parents=True, exist_ok=True)

    progress("loading_model", 3)
    model_path = ensure_model_file(progress)
    model = YOLO(model_path)
    pages_images = []
    progress("preparing_pages", 8)
    for f in file_list:
        if f.lower().endswith('.pdf'): 
            pages_images.extend(convert_from_path(f, dpi=300, poppler_path=config.POPPLER_PATH))
        else: 
            pages_images.append(Image.open(f))

    full_song = AudioSegment.silent(duration=1200000) 
    midi_events, video_events, page_frames, score_events = [], [], [], []
    key_signature_records = []
    staff_crop_recovery_stats = {
        "enabled": bool(use_staff_crop_recovery),
        "crop_count": 0,
        "recovered_count": 0,
        "rejected_count": 0,
        "pages": [],
    }
    ms_per_beat = (60 / bpm) * 1000
    global_time_ms = 1000 

    def write_midi_file(target_path):
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(MetaMessage('set_tempo', tempo=int(60000000 / bpm)))
        track.append(Message('program_change', program=0, channel=0, time=0))
        track.append(Message('program_change', program=0, channel=1, time=0))
        normalized_events = normalize_midi_events(midi_events, int(ms_per_beat))

        curr_t = 0
        t_to_ticks = mid.ticks_per_beat / ms_per_beat
        for event in normalized_events:
            abs_ticks = int(event['time'] * t_to_ticks)
            track.append(
                Message(
                    'note_on' if event['type'] == 'on' else 'note_off',
                    note=event['note'],
                    velocity=event['vel'],
                    channel=int(event.get('channel', 0)),
                    time=max(0, abs_ticks - curr_t),
                )
            )
            curr_t = abs_ticks
        mid.save(str(target_path))
        return target_path

    total_pages = max(1, len(pages_images))
    for p_idx, p_img in enumerate(pages_images):
        page_start_percent = 12 + int((p_idx / total_pages) * 58)
        page_end_percent = 12 + int(((p_idx + 1) / total_pages) * 58)
        progress("processing_page", page_start_percent, page=p_idx + 1)
        img_cv = cv2.cvtColor(np.array(p_img), cv2.COLOR_RGB2BGR)
        
        h_orig, w_orig = img_cv.shape[:2]
        target_width = 2400 
        if w_orig > target_width:
            scale = target_width / w_orig
            img_cv = cv2.resize(img_cv, (int(w_orig*scale), int(h_orig*scale)), interpolation=cv2.INTER_LANCZOS4)
        
        page_frames.append(img_cv.copy())
        img_traduzido = img_cv.copy()
        label_rects = []
        detection_img = img_cv
        if use_preprocessing:
            progress("preprocessing_page", min(page_start_percent + 2, page_end_percent))
            detection_img = preprocess_score_image_for_detection(img_cv)

        # Detecção
        res1 = model.predict(detection_img, conf=0.45, imgsz=1024, verbose=False)[0]
        res2 = model.predict(detection_img, conf=0.25, imgsz=1280, verbose=False)[0]
        
        all_raw = []
        for r in [res1, res2]:
            for box in r.boxes:
                all_raw.append({'id': int(box.cls[0]), 'conf': float(box.conf[0]), 'box': box.xyxy[0].cpu().numpy()})
        
        all_raw.sort(key=lambda x: x['conf'], reverse=True)
        staves, braces, objects, final_boxes = [], [], [], []
        
        for item in all_raw:
            if item['id'] in STAFF_IDS: 
                if not any(vision_utils.calculate_iou(item['box'], s) > 0.7 for s in staves):
                    staves.append(item['box'])
            elif item['id'] in BRACE_IDS:
                if not any(vision_utils.calculate_iou(item['box'], b) > 0.5 for b in braces):
                    braces.append(item['box'])
            elif not any(vision_utils.calculate_iou(item['box'], fb) > 0.4 for fb in final_boxes):
                final_boxes.append(item['box'])
                objects.append({
                    'id': item['id'],
                    'x': (item['box'][0]+item['box'][2])/2,
                    'y': (item['box'][1]+item['box'][3])/2,
                    'box': item['box'],
                    'conf': item.get('conf'),
                })

        staves = consolidate_duplicate_staves(staves)
        
        systems = merge_playback_systems(group_staves_by_braces(staves, braces, objects))
        if use_staff_crop_recovery and systems:
            progress("recovering_staff_crops", min(page_start_percent + 4, page_end_percent))
            recovered_objects, page_recovery_stats = recover_objects_from_staff_crops(
                model,
                detection_img,
                systems,
                objects,
                final_boxes,
            )
            page_recovery_stats["page"] = p_idx + 1
            staff_crop_recovery_stats["pages"].append(page_recovery_stats)
            staff_crop_recovery_stats["crop_count"] += page_recovery_stats.get("crop_count", 0)
            staff_crop_recovery_stats["recovered_count"] += page_recovery_stats.get("recovered_count", 0)
            staff_crop_recovery_stats["rejected_count"] += page_recovery_stats.get("rejected_count", 0)
            if recovered_objects:
                systems = merge_playback_systems(group_staves_by_braces(staves, braces, objects))
        system_sizes = ", ".join(str(len(system)) for system in systems) or "0"
        progress(
            "systems_found",
            min(page_start_percent + 6, page_end_percent),
            systems=len(systems),
            sizes=system_sizes,
            braces=len(braces),
        )

        for system in systems:
            maior_tempo_sistema = global_time_ms
            staff_data, note_columns, system_left, system_width = build_staff_note_columns(system, objects, img_cv)
            measure_boundaries = detect_system_measure_boundaries(img_cv, system, objects)
            beats_per_measure = infer_system_beats_per_measure(system, objects)
            for staff_index, staff_info in enumerate(staff_data):
                key_signature = staff_info.get("key_signature") or {}
                if key_signature:
                    key_signature_records.append({
                        "page": p_idx + 1,
                        "staff": staff_index + 1,
                        "clef": staff_info.get("clef", ""),
                        "key_signature": dict(sorted(key_signature.items())),
                    })
            timeline = rhythm.build_column_timeline(
                note_columns,
                system_left,
                system_width,
                ms_per_beat,
                measure_boundaries=measure_boundaries,
                beats_per_measure=beats_per_measure,
            )

            for column_index, column in enumerate(note_columns):
                rhythm_point = timeline[column_index]
                column_time = global_time_ms + rhythm_point.offset_ms
                gap_to_next = rhythm_point.gap_to_next_ms
                column_end = column_time
                note_infos = []

                for o in column['items']:
                    staff_info = staff_data[o["staff_index"]]
                    s_coords = staff_info["coords"]
                    otype = config.ID_MAP.get(o['id'], "")
                    dur = duration_for_object(o, otype, ms_per_beat)
                    play_dur = audible_duration_ms(otype, dur, gap_to_next, ms_per_beat)
                    tail = release_tail_ms(otype, gap_to_next, ms_per_beat)
                    audio_dur = int(dur + tail)
                    column_end = max(column_end, column_time + int(play_dur))

                    if "rest" in otype:
                        continue

                    nb, octv = vision_utils.calculate_pitch(
                        o['y'],
                        s_coords[3],
                        staff_info["step"],
                        staff_info["clef"],
                    )
                    accidental = infer_note_accidental(
                        o,
                        nb,
                        octv,
                        staff_info,
                        system_width,
                    )
                    dynamic_type = infer_note_dynamic(o, staff_info)
                    audio_velocity = dynamic_audio_velocity(dynamic_type)
                    midi_velocity = dynamic_midi_velocity(dynamic_type)

                    b = o['box'].astype(int)
                    note_infos.append({
                        "object": o,
                        "box": b,
                        "label": label_note(nb, accidental, octv),
                        "note": nb,
                        "accidental": accidental,
                        "octave": octv,
                        "duration": play_dur,
                        "notated_duration": dur,
                        "audio_duration": audio_dur,
                        "release_tail": tail,
                        "dynamic": dynamic_type,
                        "velocity": audio_velocity,
                        "midi_velocity": midi_velocity,
                        "staff_index": o["staff_index"],
                        "hand": visual_hand_for_staff(
                            o["staff_index"],
                            len(staff_data),
                            staff_info["clef"],
                        ),
                        "color": staff_annotation_color(staff_info["clef"]),
                        "center": (int(o["x"]), int(o["y"])),
                        "confidence": o.get("conf"),
                    })

                if want_annotations:
                    draw_column_annotations(img_traduzido, note_infos, label_rects, annotation_mode)

                for info in note_infos:
                    nb = info["note"]
                    accidental = info["accidental"]
                    octv = info["octave"]
                    dur = info["notated_duration"]
                    play_dur = info["duration"]
                    release_tail = info["release_tail"]
                    velocity = info["velocity"]
                    midi_velocity = info["midi_velocity"]
                    freq = audio_utils.get_frequency(nb, accidental, octv)
                    midi_p = audio_utils.note_to_midi(nb, accidental, octv)
                    midi_channel = 1 if info["hand"] == "left" else 0

                    wave = audio_utils.generate_piano_sound(
                        freq,
                        dur,
                        velocity=velocity,
                        release_ms=release_tail,
                        timbre=timbre,
                    )
                    tone = AudioSegment(wave.tobytes(), frame_rate=config.SAMPLE_RATE, sample_width=2, channels=1)
                    full_song = full_song.overlay(tone, position=column_time)

                    score_events.append(
                        ScoreEvent(
                            start_ms=int(column_time),
                            duration_ms=int(play_dur),
                            midi_note=int(midi_p),
                            label=info["label"],
                            note=nb,
                            accidental=accidental,
                            octave=int(octv),
                            page_index=int(p_idx),
                            staff_index=int(info["staff_index"]),
                            hand=info["hand"],
                            x=int(info["center"][0]),
                            y=int(info["center"][1]),
                            confidence=info.get("confidence"),
                            dynamic=info.get("dynamic"),
                            velocity=midi_velocity,
                        )
                    )
                    midi_events.append({
                        'time': column_time,
                        'type': 'on',
                        'note': midi_p,
                        'vel': midi_velocity,
                        'channel': midi_channel,
                    })
                    midi_events.append({
                        'time': column_time + int(play_dur),
                        'type': 'off',
                        'note': midi_p,
                        'vel': 0,
                        'channel': midi_channel,
                    })
                    video_events.append({
                        'time': column_time,
                        'x': info["center"][0],
                        'y': info["center"][1],
                        'dur': play_dur,
                        'vol': velocity,
                        'page': p_idx,
                        'midi': midi_p,
                        'label': info["label"],
                        'hand': info["hand"],
                    })

                if column_end > maior_tempo_sistema:
                    maior_tempo_sistema = column_end

            global_time_ms = maior_tempo_sistema + rhythm.system_gap_ms(ms_per_beat)
            continue

            tempo_inicio_sistema = global_time_ms 
            maior_tempo_sistema = global_time_ms

            for s_idx, s_coords in enumerate(system):
                tempo_pauta = tempo_inicio_sistema 
                step = (s_coords[3]-s_coords[1])/8
                objs_pauta = [o for o in objects if s_coords[1]-40 < o['y'] < s_coords[3]+40]
                objs_pauta.sort(key=lambda o: o['x'])
                
                clef = infer_staff_clef(system, s_idx, s_coords, objects)

                last_x = s_coords[0]
                key_sig = {} 
                rhythmic_objs = [
                    o for o in objs_pauta
                    if is_rhythmic_object(config.ID_MAP.get(o['id'], ""))
                ]
                x_tolerance = max(10, min(22, (s_coords[2] - s_coords[0]) * 0.012))
                note_columns = group_objects_by_x(rhythmic_objs, x_tolerance)

                for column in note_columns:
                    delta_x = column['x'] - last_x
                    
                    if delta_x > 10: # Sensibilidade horizontal aumentada
                        tempo_pauta += int((delta_x / ((s_coords[2]-s_coords[0])/16)) * ms_per_beat)
                        last_x = column['x']

                    column_end = tempo_pauta

                    for o in column['items']:
                        otype = config.ID_MAP.get(o['id'], "")
                        dur = duration_for_type(otype, ms_per_beat)
                        column_end = max(column_end, tempo_pauta + int(dur))

                        if "rest" in otype:
                            continue

                        nb, octv = vision_utils.calculate_pitch(o['y'], s_coords[3], step, clef)
                        
                        b = o['box'].astype(int)
                        cv2.rectangle(img_traduzido, (b[0], b[1]), (b[2], b[3]), COLOR_BOX, 2)
                        draw_text_with_background(
                            img_traduzido,
                            f"{nb}{octv}",
                            b[0],
                            b[1] - 15,
                            FONT_FACE,
                            FONT_SCALE,
                            COLOR_TEXT,
                            FONT_THICKNESS,
                            COLOR_BG_TEXT,
                            occupied_rects=label_rects,
                            anchor_box=b,
                        )
                        
                        freq = audio_utils.get_frequency(nb, "", octv)
                        midi_p = audio_utils.note_to_midi(nb, "", octv)
                        
                        wave = audio_utils.generate_piano_sound(freq, dur, velocity=0.8, timbre=timbre)
                        tone = AudioSegment(wave.tobytes(), frame_rate=config.SAMPLE_RATE, sample_width=2, channels=1)
                        full_song = full_song.overlay(tone, position=tempo_pauta)
                        
                        midi_events.append({'time': tempo_pauta, 'type': 'on', 'note': midi_p, 'vel': 100})
                        midi_events.append({'time': tempo_pauta + int(dur), 'type': 'off', 'note': midi_p, 'vel': 0})
                        video_events.append({'time': tempo_pauta, 'x': o['x'], 'y': o['y'], 'dur': dur, 'vol': 0.8, 'page': p_idx})

                    if column_end > maior_tempo_sistema:
                        maior_tempo_sistema = column_end

                if tempo_pauta > maior_tempo_sistema:
                    maior_tempo_sistema = tempo_pauta

            # IMPORTANTE: global_time_ms PRECISA avançar aqui
            global_time_ms = maior_tempo_sistema + int(ms_per_beat * 0.5)

        if want_annotations:
            draw_annotation_legend(img_traduzido, annotation_mode, language)
        annotated_path = output_dir / f"{output_stem}_annotated_p{p_idx+1}.jpg"
        if want_annotations:
            cv2.imwrite(str(annotated_path), img_traduzido, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            annotated_files.append(str(annotated_path))
        if p_idx < len(pages_images) - 1:
            global_time_ms += rhythm.page_gap_ms(ms_per_beat)
        progress("page_done", page_end_percent, page=p_idx + 1)

    # Exportações Finais
    progress("exporting_files", 74)
    final_audio = full_song[:global_time_ms + 1000]
    final_audio = audio_utils.apply_reverb(final_audio.apply_gain(-4.0), gain=0.16).fade_out(450)
    audio_path = output_dir / f"{output_stem}.mp3"
    temp_audio_path = output_dir / f"_{output_stem}_video_audio.mp3"
    midi_path = output_dir / f"{output_stem}.mid"
    midi_written = False

    if use_soundfont_audio and (want_audio or want_video):
        soundfont_midi_path = midi_path if want_midi else output_dir / f"_{output_stem}_soundfont.mid"
        soundfont_wav_path = output_dir / f"_{output_stem}_soundfont.wav"
        try:
            write_midi_file(soundfont_midi_path)
            midi_written = soundfont_midi_path == midi_path

            def soundfont_download_progress(downloaded, total):
                total_mb = f"{total / (1024 * 1024):.1f}" if total else "?"
                downloaded_mb = f"{downloaded / (1024 * 1024):.1f}"
                progress(
                    "downloading_soundfont",
                    75,
                    downloaded_mb=downloaded_mb,
                    total_mb=total_mb,
                )

            soundfont_path = audio_utils.ensure_default_soundfont(soundfont_download_progress)
            progress("rendering_soundfont", 76)
            audio_utils.render_midi_with_soundfont(
                soundfont_midi_path,
                soundfont_wav_path,
                soundfont_path=soundfont_path,
                gain=0.62,
            )
            soundfont_audio = AudioSegment.from_file(str(soundfont_wav_path))
            required_ms = global_time_ms + 1000
            if len(soundfont_audio) < required_ms:
                soundfont_audio += AudioSegment.silent(duration=required_ms - len(soundfont_audio))
            final_audio = audio_utils.normalize_peak(soundfont_audio[:required_ms], -2.0).fade_out(450)
        except Exception as exc:
            progress("soundfont_fallback", 76, error=str(exc).splitlines()[0])
        finally:
            if soundfont_wav_path.exists():
                soundfont_wav_path.unlink()
            if not want_midi and soundfont_midi_path.exists():
                soundfont_midi_path.unlink()

    if want_audio:
        progress("generating_mp3", 78)
        final_audio.export(str(audio_path), format="mp3")
    elif want_video:
        progress("preparing_video_audio", 78)
        final_audio.export(str(temp_audio_path), format="mp3")
    
    if want_midi:
        progress("generating_midi", 82)
        if not midi_written:
            write_midi_file(midi_path)

    def build_result_dict(include_video=False):
        review_summary = build_review_summary(
            score_events,
            len(pages_images),
            global_time_ms,
            key_signature_records,
            staff_crop_recovery_stats,
        )
        processing_result = ProcessingResult(
            output_dir=output_dir,
            annotations=annotated_files if want_annotations else [],
            audio=str(audio_path) if want_audio else None,
            midi=str(midi_path) if want_midi else None,
            video=str(video_path) if include_video else None,
            event_count=len(score_events),
            review=review_summary,
            events=score_events,
        )
        result_payload = processing_result.to_dict(include_events=options.include_events)
        validation_payload = None
        if options.validate_outputs:
            report = validate_processing_result(
                result_payload,
                options.to_dict(),
                musical_events=score_events,
                language=language,
            )
            validation_payload = report.to_dict()
            result_payload["validation"] = validation_payload
        if want_scientific_report:
            progress("generating_scientific_report", 98)
            scientific_payload = build_scientific_payload(
                score_events=score_events,
                review=review_summary,
                validation=validation_payload,
                output_options=options.to_dict(),
                source_files=file_list,
                bpm=bpm,
                page_count=len(pages_images),
                duration_ms=global_time_ms,
                key_signatures=key_signature_records,
            )
            html_path, json_path = write_scientific_report(
                output_dir,
                output_stem,
                scientific_payload,
            )
            result_payload["scientific_report"] = str(html_path)
            result_payload["scientific_data"] = str(json_path)
        return result_payload

    video_path = output_dir / f"{output_stem}.mp4"
    if not want_video:
        result_payload = build_result_dict(False)
        progress("done", 100)
        return result_payload

    # Vídeo com Sincronia
    progress("rendering_video", 86)
    video_events.sort(key=lambda event: event['time'])
    temp_video_path = output_dir / f"_{output_stem}_temp.mp4"
    if video_mode == "piano_roll":
        roll_state = build_piano_roll_state(video_events)
        out_v = cv2.VideoWriter(
            str(temp_video_path),
            cv2.VideoWriter_fourcc(*'mp4v'),
            config.FPS,
            (roll_state["width"], roll_state["height"]),
        )
    else:
        vid_h, vid_w = page_frames[0].shape[:2]
        roll_state = None
        out_v = cv2.VideoWriter(str(temp_video_path), cv2.VideoWriter_fourcc(*'mp4v'), config.FPS, (vid_w, vid_h))
    total_frames = int((len(final_audio)/1000)*config.FPS)
    progress_step = max(1, total_frames // 20)
    for f in range(total_frames):
        t_ms = (f/config.FPS)*1000
        if video_mode == "piano_roll":
            frame = render_piano_roll_frame(video_events, t_ms, len(final_audio), roll_state)
        else:
            active = [ev for ev in video_events if ev['time'] <= t_ms <= ev['time'] + ev['dur']]
            frame = render_video_frame(page_frames, video_events, active, t_ms)
        out_v.write(frame)
        if f % progress_step == 0:
            progress("rendering_frames", 86 + int((f / max(1, total_frames)) * 8))

        # Pega a página da nota ativa mais recente
    out_v.release()

    progress("syncing_video", 95)
    video_clip = mp.VideoFileClip(str(temp_video_path))
    audio_clip = mp.AudioFileClip(str(audio_path if want_audio else temp_audio_path))
    final_clip = (
        video_clip.set_audio(audio_clip)
        if hasattr(video_clip, "set_audio")
        else video_clip.with_audio(audio_clip)
    )
    temp_aac_path = output_dir / f"_{output_stem}_aac_audio.m4a"
    final_clip.write_videofile(
        str(video_path),
        codec='libx264',
        audio_codec='aac',
        audio_bitrate='192k',
        audio_fps=config.SAMPLE_RATE,
        temp_audiofile=str(temp_aac_path),
        remove_temp=True,
        ffmpeg_params=['-pix_fmt', 'yuv420p', '-movflags', '+faststart'],
        logger=None,
    )
    final_clip.close()
    audio_clip.close()
    video_clip.close()
    os.remove(temp_video_path)
    if not want_audio and temp_audio_path.exists():
        os.remove(temp_audio_path)
    result_payload = build_result_dict(True)
    progress("done", 100)

    return result_payload

def main():
    root = tk.Tk(); root.withdraw()
    file_list = filedialog.askopenfilenames(title="Selecione as partes (PDF ou Imagens)")
    if not file_list:
        root.destroy()
        return
    bpm = simpledialog.askinteger("Config", "Digite o BPM:", initialvalue=72, minvalue=30)
    root.destroy()
    if not bpm:
        return
    process_score_files(file_list, bpm)

if __name__ == "__main__": main()
