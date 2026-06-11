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

BASE_DIR = Path(__file__).resolve().parent

PROGRESS_MESSAGES = {
    "pt": {
        "loading_model": "Carregando modelo de reconhecimento...",
        "downloading_model": "Baixando modelo PyClef... {downloaded_mb}/{total_mb} MB",
        "extracting_model": "Extraindo modelo PyClef...",
        "model_ready": "Modelo pronto.",
        "preparing_pages": "Preparando paginas da partitura...",
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
        "done": "Sincronia de sistemas corrigida!",
    },
    "en": {
        "loading_model": "Loading recognition model...",
        "downloading_model": "Downloading PyClef model... {downloaded_mb}/{total_mb} MB",
        "extracting_model": "Extracting PyClef model...",
        "model_ready": "Model ready.",
        "preparing_pages": "Preparing score pages...",
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
SYSTEM_WIDTH_BEATS = rhythm.SYSTEM_WIDTH_BEATS
MIN_COLUMN_ADVANCE_BEATS = rhythm.MIN_COLUMN_ADVANCE_BEATS
SYSTEM_GAP_BEATS = rhythm.SYSTEM_GAP_BEATS
STAFF_IDS = {134, 207}
BRACE_IDS = {0, 136}
RHYTHMIC_MARKERS = ("quarter", "half", "whole", "note")

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
            color = group[0]["color"]
            for item in group:
                b = item["box"].astype(int)
                cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), color, 2)
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
            b = item["box"].astype(int)
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), item["color"], 2)
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
                border_color=item["color"],
                guide_points=[item["center"]],
                guide_color=item["color"],
            )

def draw_annotation_legend(img, annotation_mode, language):
    labels = {
        "pt": {
            "title": "PyClef anotacoes",
            "treble": "Clave de Sol",
            "bass": "Clave de Fa",
            "guide": "Linha-guia",
            "mode": "Modo limpo" if annotation_mode != "detailed" else "Modo detalhado",
        },
        "en": {
            "title": "PyClef annotations",
            "treble": "Treble staff",
            "bass": "Bass staff",
            "guide": "Guide line",
            "mode": "Clean mode" if annotation_mode != "detailed" else "Detailed mode",
        },
    }.get(language, {})
    lines = [
        labels.get("title", "PyClef annotations"),
        labels.get("treble", "Treble staff"),
        labels.get("bass", "Bass staff"),
        labels.get("guide", "Guide line"),
        labels.get("mode", "Clean mode"),
    ]
    font_scale = 0.58
    thickness = 1
    line_height = 18
    panel_width = 250
    panel_height = 112
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
            (lines[4], (210, 210, 210)),
        )
    ):
        current_y = swatch_y + (idx * line_height)
        cv2.rectangle(img, (x + 15, current_y - 9), (x + 31, current_y + 3), color, -1)
        cv2.putText(img, text, (x + 40, current_y + 3), FONT_FACE, font_scale, COLOR_TEXT, thickness, cv2.LINE_AA)

def is_rhythmic_object(otype):
    return any(marker in otype for marker in RHYTHMIC_MARKERS)

def duration_for_type(otype, ms_per_beat):
    return rhythm.duration_ms_for_type(otype, ms_per_beat)

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
            group = [candidates[0], candidates[-1]]
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
    if len(upper_system) != 1 or len(lower_system) < 2:
        return False

    upper_bounds = system_bounds(upper_system)
    lower_bounds = system_bounds(lower_system)
    if lower_bounds[1] <= upper_bounds[3]:
        return False

    overlap = horizontal_overlap_ratio(upper_bounds, lower_bounds)
    if overlap < 0.58:
        return False

    gap = lower_bounds[1] - upper_bounds[3]
    staff_height = (average_staff_height(upper_system) + average_staff_height(lower_system)) / 2
    max_gap = max(220, staff_height * 7.5)
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

def build_staff_note_columns(system, objects):
    staff_data = []
    staff_columns = []
    system_left = min(staff[0] for staff in system)
    system_right = max(staff[2] for staff in system)
    system_width = max(1, system_right - system_left)
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
        rhythmic_objs = [
            {**o, "staff_index": s_idx}
            for o in objs_pauta
            if is_rhythmic_object(config.ID_MAP.get(o['id'], ""))
        ]
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
        x = int(playhead['x'])
        y = int(playhead['y'])
        cv2.line(frame, (x, 0), (x, frame.shape[0]), (255, 190, 60), 2)
        cv2.circle(frame, (x, y), 12, (255, 190, 60), 2)

    for event in active_events:
        if event['page'] != current_page:
            continue
        pulse = 0.65 + 0.35 * np.sin((t_ms - event['time']) / max(1, event['dur']) * np.pi)
        radius = int(16 + 8 * pulse)
        cv2.circle(frame, (int(event['x']), int(event['y'])), radius, (0, 0, 255), -1)
        cv2.circle(frame, (int(event['x']), int(event['y'])), radius + 4, (255, 255, 255), 2)

    return frame

def process_score_files(file_list, bpm, progress_callback=None, output_options=None):
    output_options = output_options or {
        "annotations": True,
        "audio": True,
        "midi": True,
        "video": True,
        "annotation_mode": "clean",
    }
    language = output_options.get("language", "pt")
    if language not in PROGRESS_MESSAGES:
        language = "pt"
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
    want_annotations = output_options.get("annotations", False)
    want_audio = output_options.get("audio", False)
    want_midi = output_options.get("midi", False)
    want_video = output_options.get("video", False)
    annotation_mode = output_options.get("annotation_mode", "clean")
    if annotation_mode not in {"clean", "detailed"}:
        annotation_mode = "clean"
    timbre = audio_utils.normalize_timbre(output_options.get("timbre", "piano"))
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
    midi_events, video_events, page_frames = [], [], []
    ms_per_beat = (60 / bpm) * 1000
    global_time_ms = 1000 

    def write_midi_file(target_path):
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(MetaMessage('set_tempo', tempo=int(60000000 / bpm)))
        track.append(Message('program_change', program=0, time=0))
        sorted_events = sorted(
            midi_events,
            key=lambda event: (event['time'], 0 if event['type'] == 'off' else 1),
        )
        curr_t = 0
        t_to_ticks = mid.ticks_per_beat / ms_per_beat
        for event in sorted_events:
            abs_ticks = int(event['time'] * t_to_ticks)
            track.append(
                Message(
                    'note_on' if event['type'] == 'on' else 'note_off',
                    note=event['note'],
                    velocity=event['vel'],
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

        # Detecção
        res1 = model.predict(img_cv, conf=0.45, imgsz=1024, verbose=False)[0]
        res2 = model.predict(img_cv, conf=0.25, imgsz=1280, verbose=False)[0]
        
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

        staves.sort(key=lambda x: x[1])
        
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
            staff_data, note_columns, system_left, system_width = build_staff_note_columns(system, objects)
            timeline = rhythm.build_column_timeline(
                note_columns,
                system_left,
                system_width,
                ms_per_beat,
            )

            for column_index, column in enumerate(note_columns):
                rhythm_point = timeline[column_index]
                column_time = global_time_ms + rhythm_point.offset_ms
                gap_to_next = rhythm_point.gap_to_next_ms
                column_end = column_time
                played_in_column = set()
                note_infos = []

                for o in column['items']:
                    staff_info = staff_data[o["staff_index"]]
                    s_coords = staff_info["coords"]
                    otype = config.ID_MAP.get(o['id'], "")
                    dur = duration_for_type(otype, ms_per_beat)
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

                    b = o['box'].astype(int)
                    note_infos.append({
                        "object": o,
                        "box": b,
                        "label": f"{nb}{octv}",
                        "note": nb,
                        "octave": octv,
                        "duration": play_dur,
                        "notated_duration": dur,
                        "audio_duration": audio_dur,
                        "release_tail": tail,
                        "staff_index": o["staff_index"],
                        "color": staff_annotation_color(staff_info["clef"]),
                        "center": (int(o["x"]), int(o["y"])),
                        "confidence": o.get("conf"),
                    })

                if want_annotations:
                    draw_column_annotations(img_traduzido, note_infos, label_rects, annotation_mode)

                for info in note_infos:
                    nb = info["note"]
                    octv = info["octave"]
                    dur = info["notated_duration"]
                    play_dur = info["duration"]
                    release_tail = info["release_tail"]
                    freq = audio_utils.get_frequency(nb, "", octv)
                    midi_p = audio_utils.note_to_midi(nb, "", octv)
                    if midi_p in played_in_column:
                        continue
                    played_in_column.add(midi_p)

                    wave = audio_utils.generate_piano_sound(
                        freq,
                        dur,
                        velocity=0.68,
                        release_ms=release_tail,
                        timbre=timbre,
                    )
                    tone = AudioSegment(wave.tobytes(), frame_rate=config.SAMPLE_RATE, sample_width=2, channels=1)
                    full_song = full_song.overlay(tone, position=column_time)
                    column_end = max(column_end, column_time + len(tone))

                    midi_events.append({'time': column_time, 'type': 'on', 'note': midi_p, 'vel': 92})
                    midi_events.append({'time': column_time + int(dur), 'type': 'off', 'note': midi_p, 'vel': 0})
                    video_events.append({
                        'time': column_time,
                        'x': info["center"][0],
                        'y': info["center"][1],
                        'dur': play_dur,
                        'vol': 0.72,
                        'page': p_idx,
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
            global_time_ms += int(ms_per_beat * 1.0)
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
    video_path = output_dir / f"{output_stem}.mp4"
    if not want_video:
        progress("done", 100)
        result = {}
        if want_annotations:
            result["annotations"] = annotated_files
        if want_audio:
            result["audio"] = str(audio_path)
        if want_midi:
            result["midi"] = str(midi_path)
        return result

    # Vídeo com Sincronia
    progress("rendering_video", 86)
    video_events.sort(key=lambda event: event['time'])
    vid_h, vid_w = page_frames[0].shape[:2]
    temp_video_path = output_dir / f"_{output_stem}_temp.mp4"
    out_v = cv2.VideoWriter(str(temp_video_path), cv2.VideoWriter_fourcc(*'mp4v'), config.FPS, (vid_w, vid_h))
    total_frames = int((len(final_audio)/1000)*config.FPS)
    progress_step = max(1, total_frames // 20)
    for f in range(total_frames):
        t_ms = (f/config.FPS)*1000
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
    final_clip.write_videofile(str(video_path), codec='libx264', logger=None)
    final_clip.close()
    audio_clip.close()
    video_clip.close()
    os.remove(temp_video_path)
    if not want_audio and temp_audio_path.exists():
        os.remove(temp_audio_path)
    progress("done", 100)

    result = {}
    if want_annotations:
        result["annotations"] = annotated_files
    if want_audio:
        result["audio"] = str(audio_path)
    if want_midi:
        result["midi"] = str(midi_path)
    result["video"] = str(video_path)
    return result

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
