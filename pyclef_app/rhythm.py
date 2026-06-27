from dataclasses import dataclass

from . import config


SYSTEM_WIDTH_BEATS = 24
MIN_COLUMN_ADVANCE_BEATS = 0.48
SYSTEM_GAP_BEATS = 0.0
PAGE_GAP_BEATS = 0.0
POLYPHONIC_ONSET_TOLERANCE_BEATS = 0.18


@dataclass
class RhythmPoint:
    offset_ms: int
    gap_to_next_ms: int | None
    advance_beats: float
    measure_index: int | None = None
    beat_in_measure: float | None = None
    source: str = "spacing"
    confidence: float = 0.0


def is_rest_type(otype):
    return "rest" in otype


def beats_for_type(otype):
    if not otype:
        return 1.0
    if "128th" in otype:
        return 0.03125
    if "64th" in otype:
        return 0.0625
    if "32nd" in otype:
        return 0.125
    if "whole" in otype:
        if "double_whole" in otype or "doubleWhole" in otype or "double_whole" in otype:
            return 8.0
        return 4.0
    if "half" in otype:
        return 2.0
    if "16" in otype or "sixteenth" in otype:
        return 0.25
    if "eighth" in otype or "8th" in otype:
        return 0.5
    if "grace" in otype:
        return 0.18
    return 1.0

def beats_for_item(item):
    try:
        value = float(item.get("duration_beats", 0))
    except (TypeError, ValueError):
        value = 0.0
    if value > 0:
        return value
    return beats_for_type(config.ID_MAP.get(item.get("id"), ""))


def duration_ms_for_type(otype, ms_per_beat):
    return beats_for_type(otype) * ms_per_beat

def duration_ms_for_item(otype, item, ms_per_beat):
    try:
        duration_beats = float(item.get("duration_beats", 0))
    except (TypeError, ValueError):
        duration_beats = 0.0
    if duration_beats <= 0:
        duration_beats = beats_for_type(otype)
    return duration_beats * ms_per_beat


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

def quantize_measure_beat(raw_beat, beats_per_measure):
    if raw_beat <= 0:
        return 0.0

    grid = (
        0.0,
        0.25,
        1 / 3,
        0.5,
        2 / 3,
        0.75,
        1.0,
        1.25,
        4 / 3,
        1.5,
        5 / 3,
        1.75,
        2.0,
        2.25,
        7 / 3,
        2.5,
        8 / 3,
        2.75,
        3.0,
        3.25,
        10 / 3,
        3.5,
        11 / 3,
        3.75,
        4.0,
        4.5,
        5.0,
        5.5,
        6.0,
        7.0,
        8.0,
        9.0,
        12.0,
    )
    candidates = [value for value in grid if value <= beats_per_measure + 0.05]
    nearest = min(candidates, key=lambda value: abs(value - raw_beat))
    tolerance = max(0.08, min(0.24, beats_per_measure * 0.035))
    return nearest if abs(nearest - raw_beat) <= tolerance else raw_beat


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
    items = column.get("items", [])
    if not items:
        return 0.0
    return max(beats_for_item(item) for item in items)


def column_onset_advance_beats(column):
    items = column.get("items", [])
    if not items:
        return 0.0

    note_beats = [
        beats_for_item(item)
        for item in items
        if not is_rest_type(config.ID_MAP.get(item.get("id"), ""))
    ]
    if note_beats:
        return min(note_beats)
    return max(beats_for_item(item) for item in items)


def duration_guided_advance_beats(previous_column, x_advance):
    duration_advance = column_onset_advance_beats(previous_column)
    if duration_advance <= 0:
        return x_advance
    if x_advance <= 0:
        return x_advance

    difference = abs(x_advance - duration_advance)
    tolerance = max(0.10, min(0.34, duration_advance * 0.34))
    if x_advance >= duration_advance and difference <= tolerance:
        return duration_advance

    return x_advance


def sanitize_measure_boundaries(measure_boundaries, system_left, system_width):
    if not measure_boundaries:
        return []

    system_right = system_left + system_width
    min_gap = max(28.0, system_width * 0.018)
    raw = sorted(
        float(value)
        for value in measure_boundaries
        if system_left - min_gap <= float(value) <= system_right + min_gap
    )
    if not raw:
        return []

    merged = []
    for value in raw:
        if not merged or abs(value - merged[-1]) > min_gap * 0.45:
            merged.append(value)
        else:
            merged[-1] = (merged[-1] + value) / 2.0

    if not merged or abs(merged[0] - system_left) > min_gap:
        merged.insert(0, float(system_left))
    else:
        merged[0] = float(system_left)

    if abs(merged[-1] - system_right) > min_gap:
        merged.append(float(system_right))
    else:
        merged[-1] = float(system_right)

    clean = [merged[0]]
    for value in merged[1:]:
        if value - clean[-1] >= min_gap:
            clean.append(value)

    if len(clean) < 2:
        return []
    widths = [clean[index + 1] - clean[index] for index in range(len(clean) - 1)]
    useful_widths = [width for width in widths if width >= system_width * 0.05]
    if len(useful_widths) < 1:
        return []
    return clean


def column_measure_index(column_x, boundaries):
    for index in range(len(boundaries) - 1):
        if boundaries[index] <= column_x <= boundaries[index + 1]:
            return index
    if column_x < boundaries[0]:
        return 0
    return max(0, len(boundaries) - 2)


def column_staff_indices(column):
    indices = column.get("staff_indices", set())
    if indices is None:
        return set()
    return set(indices)


def column_x_delta(previous_column, current_column):
    return abs(float(current_column["x"]) - float(previous_column["x"]))


def column_has_only_notes(column):
    types = column_types(column)
    return bool(types) and all(not is_rest_type(otype) for otype in types)


def columns_can_share_onset(
    previous_column,
    current_column,
    previous_measure_index,
    current_measure_index,
    system_width,
    beat_delta=0.0,
):
    if previous_column is None:
        return False
    if previous_measure_index != current_measure_index:
        return False

    previous_staffs = column_staff_indices(previous_column)
    current_staffs = column_staff_indices(current_column)
    x_delta = column_x_delta(previous_column, current_column)
    close_x = x_delta <= max(14.0, system_width * 0.007)

    if previous_staffs and current_staffs and previous_staffs.isdisjoint(current_staffs):
        if abs(beat_delta) <= POLYPHONIC_ONSET_TOLERANCE_BEATS:
            return True
        return close_x

    # Printed chords often offset adjacent noteheads to opposite sides of the
    # stem. They should keep a single musical attack even when their centers do
    # not fall inside the stricter detection-column tolerance.
    same_staff_chord_x = x_delta <= max(24.0, system_width * 0.012)
    if (
        previous_staffs
        and current_staffs
        and not previous_staffs.isdisjoint(current_staffs)
        and same_staff_chord_x
        and column_has_only_notes(previous_column)
        and column_has_only_notes(current_column)
        and abs(beat_delta) <= POLYPHONIC_ONSET_TOLERANCE_BEATS
    ):
        return True

    return close_x


def build_measure_grid_timeline(note_columns, system_left, system_width, ms_per_beat, measure_boundaries, beats_per_measure):
    boundaries = sanitize_measure_boundaries(measure_boundaries, system_left, system_width)
    if len(boundaries) < 2:
        return []

    beats_per_measure = max(1.0, float(beats_per_measure or 4.0))
    sorted_columns = sorted(note_columns, key=lambda item: item["x"])
    starts = []
    previous_start = None
    previous_column = None

    for column in sorted_columns:
        measure_index = column_measure_index(column["x"], boundaries)
        measure_left = boundaries[measure_index]
        measure_right = boundaries[measure_index + 1]
        measure_width = max(1.0, measure_right - measure_left)
        raw_beat = ((column["x"] - measure_left) / measure_width) * beats_per_measure
        beat_in_measure = max(0.0, min(beats_per_measure, quantize_measure_beat(raw_beat, beats_per_measure)))
        absolute_beat = (measure_index * beats_per_measure) + beat_in_measure

        if previous_start is not None and absolute_beat <= previous_start + POLYPHONIC_ONSET_TOLERANCE_BEATS:
            beat_delta = absolute_beat - previous_start
            if columns_can_share_onset(
                previous_column,
                column,
                starts[-1]["measure_index"],
                measure_index,
                system_width,
                beat_delta,
            ):
                absolute_beat = previous_start
                beat_in_measure = starts[-1]["beat_in_measure"]
            else:
                x_advance = column_advance_beats(column["x"] - previous_column["x"], system_width)
                duration_advance = duration_guided_advance_beats(previous_column, x_advance)
                absolute_beat = previous_start + max(MIN_COLUMN_ADVANCE_BEATS, duration_advance)
                measure_index = int(absolute_beat // beats_per_measure)
                beat_in_measure = absolute_beat - (measure_index * beats_per_measure)

        starts.append(
            {
                "absolute_beat": absolute_beat,
                "measure_index": measure_index,
                "beat_in_measure": beat_in_measure,
                "column": column,
            }
        )
        previous_start = absolute_beat
        previous_column = column

    if starts:
        first_beat = starts[0]["absolute_beat"]
        for item in starts:
            item["absolute_beat"] = max(0.0, item["absolute_beat"] - first_beat)

    points = []
    for idx, item in enumerate(starts):
        start = item["absolute_beat"]
        if idx + 1 < len(starts):
            gap_ms = int(max(0, starts[idx + 1]["absolute_beat"] - start) * ms_per_beat)
            advance = max(0.0, starts[idx + 1]["absolute_beat"] - start)
        else:
            gap_ms = None
            advance = 0.0
        points.append(
            RhythmPoint(
                offset_ms=int(start * ms_per_beat),
                gap_to_next_ms=gap_ms,
                advance_beats=advance,
                measure_index=item["measure_index"],
                beat_in_measure=round(item["beat_in_measure"], 4),
                source="measure_grid",
                confidence=0.78,
            )
        )
    return points


def build_spacing_timeline(note_columns, system_left, system_width, ms_per_beat):
    points = []
    if not note_columns:
        return points

    last_x = note_columns[0]["x"]
    current_beat = 0.0
    starts = []
    advances = []

    previous_column = None
    for column in note_columns:
        delta_x = column["x"] - last_x
        advance = column_advance_beats(delta_x, system_width)
        if previous_column is not None:
            advance = duration_guided_advance_beats(previous_column, advance)

        if advance:
            current_beat += advance
        elif starts:
            current_beat += 0.0

        starts.append(current_beat)
        advances.append(advance)
        last_x = column["x"]
        previous_column = column

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
                source="spacing",
                confidence=0.52,
            )
        )

    return points

def build_column_timeline(
    note_columns,
    system_left,
    system_width,
    ms_per_beat,
    measure_boundaries=None,
    beats_per_measure=4.0,
):
    if measure_boundaries and len(measure_boundaries) >= 2:
        measure_points = build_measure_grid_timeline(
            note_columns,
            system_left,
            system_width,
            ms_per_beat,
            measure_boundaries,
            beats_per_measure,
        )
        if len(measure_points) == len(note_columns):
            return measure_points
    return build_spacing_timeline(note_columns, system_left, system_width, ms_per_beat)


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


def page_gap_ms(ms_per_beat):
    return int(ms_per_beat * PAGE_GAP_BEATS)
