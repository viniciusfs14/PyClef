from dataclasses import dataclass

from . import config


SYSTEM_WIDTH_BEATS = 24
MIN_COLUMN_ADVANCE_BEATS = 0.48
SYSTEM_GAP_BEATS = 0.42


@dataclass
class RhythmPoint:
    offset_ms: int
    gap_to_next_ms: int | None
    advance_beats: float


def is_rest_type(otype):
    return "rest" in otype


def beats_for_type(otype):
    if "whole" in otype:
        return 4.0
    if "half" in otype:
        return 2.0
    if "16" in otype or "sixteenth" in otype:
        return 0.25
    if "eighth" in otype or "8th" in otype:
        return 0.5
    return 1.0


def duration_ms_for_type(otype, ms_per_beat):
    return beats_for_type(otype) * ms_per_beat


def quantize_advance_beats(raw_beats):
    if raw_beats <= 0:
        return 0.0

    choices = (
        0.25,
        1 / 3,
        0.5,
        2 / 3,
        0.75,
        1.0,
        1.25,
        1.5,
        2.0,
        3.0,
        4.0,
    )
    nearest = min(choices, key=lambda value: abs(value - raw_beats))
    tolerance = max(0.08, raw_beats * 0.16)
    return nearest if abs(nearest - raw_beats) <= tolerance else raw_beats


def column_advance_beats(delta_x, system_width):
    if delta_x <= 10:
        return 0.0

    beat_width = max(1, system_width / SYSTEM_WIDTH_BEATS)
    raw_beats = delta_x / beat_width
    quantized = quantize_advance_beats(raw_beats)
    return max(MIN_COLUMN_ADVANCE_BEATS, quantized)


def column_advance_ms(delta_x, system_width, ms_per_beat):
    return int(column_advance_beats(delta_x, system_width) * ms_per_beat)


def column_types(column):
    return [
        config.ID_MAP.get(item["id"], "")
        for item in column.get("items", [])
    ]


def column_has_notes(column):
    return any(not is_rest_type(otype) for otype in column_types(column))


def column_notated_beats(column):
    types = column_types(column)
    if not types:
        return 0.0
    return max(beats_for_type(otype) for otype in types)


def build_column_timeline(note_columns, system_left, system_width, ms_per_beat):
    points = []
    if not note_columns:
        return points

    last_x = system_left
    current_beat = 0.0
    starts = []
    advances = []

    for column in note_columns:
        delta_x = column["x"] - last_x
        advance = column_advance_beats(delta_x, system_width)

        if advance:
            current_beat += advance
        elif starts:
            current_beat += 0.0

        starts.append(current_beat)
        advances.append(advance)
        last_x = column["x"]

    for idx, start in enumerate(starts):
        if idx + 1 < len(starts):
            gap_ms = int(max(0, starts[idx + 1] - start) * ms_per_beat)
        else:
            gap_ms = None
        points.append(
            RhythmPoint(
                offset_ms=int(start * ms_per_beat),
                gap_to_next_ms=gap_ms,
                advance_beats=advances[idx],
            )
        )

    return points


def audible_duration_ms(otype, notated_duration, gap_to_next, ms_per_beat):
    if is_rest_type(otype) or gap_to_next is None or gap_to_next <= 0:
        return int(notated_duration)
    if "half" in otype or "whole" in otype:
        return int(notated_duration)
    release_floor = int(ms_per_beat * 0.30)
    articulated = int(gap_to_next * 0.96)
    return int(min(notated_duration, max(release_floor, articulated)))


def release_tail_ms(otype, gap_to_next, ms_per_beat):
    if is_rest_type(otype):
        return 0
    if "whole" in otype:
        return int(min(ms_per_beat * 0.85, 780))
    if "half" in otype:
        return int(min(ms_per_beat * 0.70, 620))
    if gap_to_next is not None and gap_to_next <= ms_per_beat * 0.55:
        return int(min(ms_per_beat * 0.46, 420))
    return int(min(ms_per_beat * 0.38, 360))


def system_gap_ms(ms_per_beat):
    return int(ms_per_beat * SYSTEM_GAP_BEATS)
