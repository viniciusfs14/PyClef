import json
import re
from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack

from . import audio_utils


NOTE_RE = re.compile(r"^\s*([A-Ga-g])((?:##|bb|#|b|s)?)(-?\d+)\s*$")


def parse_note_label(label):
    match = NOTE_RE.match(str(label or ""))
    if not match:
        raise ValueError(f"Invalid note label: {label!r}")
    note = match.group(1).upper()
    accidental_text = match.group(2)
    octave = int(match.group(3))
    accidental = ""
    if accidental_text == "##":
        accidental = "ss"
    elif accidental_text == "bb":
        accidental = "bb"
    elif accidental_text in {"#", "s"}:
        accidental = "s"
    elif accidental_text == "b":
        accidental = "b"
    return note, accidental, octave


def normalized_label(label):
    note, accidental, octave = parse_note_label(label)
    suffix = {"s": "#", "ss": "##", "b": "b", "bb": "bb"}.get(accidental, "")
    return f"{note}{suffix}{octave}"


def corrected_events_from_payload(payload, corrections):
    events = payload.get("events", [])
    by_index = {int(item.get("index", -1)): item for item in corrections}
    corrected = []
    for index, event in enumerate(events):
        correction = by_index.get(index, {})
        if correction.get("enabled", True) is False:
            continue
        label = correction.get("label") or event.get("label")
        try:
            note, accidental, octave = parse_note_label(label)
            midi_note = audio_utils.note_to_midi(note, accidental, octave)
        except ValueError:
            note = event.get("note", "C")
            accidental = event.get("accidental", "")
            octave = int(event.get("octave", 4))
            midi_note = int(event.get("midi_note", audio_utils.note_to_midi(note, accidental, octave)))
            label = event.get("label", f"{note}{octave}")
        copied = dict(event)
        copied.update({
            "label": normalized_label(label),
            "note": note,
            "accidental": accidental,
            "octave": octave,
            "midi_note": midi_note,
        })
        corrected.append(copied)
    return corrected


def load_scientific_payload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_corrections(path, corrections):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"format_version": "1.0", "corrections": corrections}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def export_corrected_midi(scientific_json_path, corrections_path, output_path, bpm=72):
    payload = load_scientific_payload(scientific_json_path)
    corrections_payload = load_scientific_payload(corrections_path)
    corrections = corrections_payload.get("corrections", [])
    events = corrected_events_from_payload(payload, corrections)

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=int(60000000 / max(1, int(bpm)))))
    track.append(Message("program_change", program=0, channel=0, time=0))

    note_events = []
    for event in events:
        start = int(event.get("start_ms", 0))
        duration = max(1, int(event.get("duration_ms", 1)))
        midi_note = max(0, min(127, int(event.get("midi_note", 60))))
        velocity = max(1, min(127, int(event.get("velocity") or 82)))
        channel = 1 if event.get("hand") == "left" else 0
        note_events.append((start, 1, midi_note, velocity, channel))
        note_events.append((start + duration, 0, midi_note, 0, channel))

    note_events.sort(key=lambda item: (item[0], item[1], item[4], item[2]))
    ticks_per_ms = mid.ticks_per_beat / (60000 / max(1, int(bpm)))
    current_ticks = 0
    for start_ms, is_on, midi_note, velocity, channel in note_events:
        absolute_ticks = int(start_ms * ticks_per_ms)
        track.append(
            Message(
                "note_on" if is_on else "note_off",
                note=midi_note,
                velocity=velocity,
                channel=channel,
                time=max(0, absolute_ticks - current_ticks),
            )
        )
        current_ticks = absolute_ticks

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(output_path))
    return output_path
