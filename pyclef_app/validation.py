from pathlib import Path

import cv2
from mido import MidiFile
from pydub import AudioSegment

try:
    import moviepy.editor as mp
except ModuleNotFoundError:
    import moviepy as mp

from .models import OutputOptions, ValidationReport


MESSAGES = {
    "en": {
        "missing_file": "Expected output was not created.",
        "empty_file": "Output file is empty.",
        "audio_ok": "Audio duration: {duration:.1f}s.",
        "audio_error": "Could not inspect audio: {error}",
        "midi_ok": "MIDI notes: {notes}.",
        "midi_empty": "MIDI has no note_on events.",
        "midi_error": "Could not inspect MIDI: {error}",
        "video_ok": "Video frames: {frames} at {fps:.1f} FPS.",
        "video_audio_missing": "Video does not appear to contain an audio track.",
        "video_error": "Could not inspect video: {error}",
        "events_ok": "Recognized musical events: {count}.",
        "events_missing": "No musical events were registered.",
        "invalid_event_duration": "Some musical events have invalid duration.",
    },
    "pt": {
        "missing_file": "Saída esperada não foi criada.",
        "empty_file": "Arquivo de saída está vazio.",
        "audio_ok": "Duração do áudio: {duration:.1f}s.",
        "audio_error": "Não foi possível inspecionar o áudio: {error}",
        "midi_ok": "Notas no MIDI: {notes}.",
        "midi_empty": "MIDI não possui eventos note_on.",
        "midi_error": "Não foi possível inspecionar o MIDI: {error}",
        "video_ok": "Quadros do vídeo: {frames} a {fps:.1f} FPS.",
        "video_audio_missing": "O vídeo parece não possuir faixa de áudio.",
        "video_error": "Não foi possível inspecionar o vídeo: {error}",
        "events_ok": "Eventos musicais reconhecidos: {count}.",
        "events_missing": "Nenhum evento musical foi registrado.",
        "invalid_event_duration": "Alguns eventos musicais possuem duração inválida.",
    },
}


def _tr(language, key, **kwargs):
    text = MESSAGES.get(language, MESSAGES["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text


def _path_from_result(result, key):
    value = result.get(key)
    if isinstance(value, list):
        return [Path(item) for item in value]
    if value:
        return Path(value)
    return None


def _check_file(report, path, language):
    if not path or not path.exists():
        report.add("error", _tr(language, "missing_file"), path)
        return False
    if path.stat().st_size <= 0:
        report.add("error", _tr(language, "empty_file"), path)
        return False
    return True


def _inspect_audio(report, audio_path, language):
    if not _check_file(report, audio_path, language):
        return
    try:
        audio = AudioSegment.from_file(str(audio_path))
        duration = len(audio) / 1000
        report.summary["audio_duration_seconds"] = round(duration, 3)
        report.add("info", _tr(language, "audio_ok", duration=duration), audio_path)
    except Exception as exc:
        report.add("warning", _tr(language, "audio_error", error=str(exc).splitlines()[0]), audio_path)


def _inspect_midi(report, midi_path, language):
    if not _check_file(report, midi_path, language):
        return
    try:
        midi = MidiFile(str(midi_path))
        note_count = sum(
            1
            for track in midi.tracks
            for message in track
            if message.type == "note_on" and message.velocity > 0
        )
        report.summary["midi_note_count"] = note_count
        if note_count:
            report.add("info", _tr(language, "midi_ok", notes=note_count), midi_path)
        else:
            report.add("warning", _tr(language, "midi_empty"), midi_path)
    except Exception as exc:
        report.add("warning", _tr(language, "midi_error", error=str(exc).splitlines()[0]), midi_path)


def _inspect_video(report, video_path, language):
    if not _check_file(report, video_path, language):
        return
    try:
        capture = cv2.VideoCapture(str(video_path))
        frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
        capture.release()
        report.summary["video_frame_count"] = frames
        report.summary["video_fps"] = round(fps, 3)
        report.add("info", _tr(language, "video_ok", frames=frames, fps=fps), video_path)
    except Exception as exc:
        report.add("warning", _tr(language, "video_error", error=str(exc).splitlines()[0]), video_path)
        return

    try:
        clip = mp.VideoFileClip(str(video_path))
        has_audio = clip.audio is not None
        clip.close()
        report.summary["video_has_audio"] = has_audio
        if not has_audio:
            report.add("warning", _tr(language, "video_audio_missing"), video_path)
    except Exception as exc:
        report.add("warning", _tr(language, "video_error", error=str(exc).splitlines()[0]), video_path)


def validate_processing_result(result, expected_options=None, musical_events=None, language="en"):
    options = OutputOptions.from_mapping(expected_options)
    language = language if language in MESSAGES else "en"
    report = ValidationReport()
    musical_events = list(musical_events or [])

    if options.annotations:
        annotation_paths = _path_from_result(result, "annotations") or []
        if not annotation_paths:
            report.add("error", _tr(language, "missing_file"))
        for path in annotation_paths:
            _check_file(report, path, language)

    if options.audio:
        _inspect_audio(report, _path_from_result(result, "audio"), language)
    if options.midi:
        _inspect_midi(report, _path_from_result(result, "midi"), language)
    if options.video:
        _inspect_video(report, _path_from_result(result, "video"), language)

    report.summary["event_count"] = len(musical_events)
    if musical_events:
        report.add("info", _tr(language, "events_ok", count=len(musical_events)))
        if any(event.duration_ms <= 0 for event in musical_events):
            report.add("warning", _tr(language, "invalid_event_duration"))
    elif options.audio or options.midi or options.video:
        report.add("warning", _tr(language, "events_missing"))

    return report
