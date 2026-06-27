import os
import shutil
from pathlib import Path

from . import audio_utils, config
from .models import DiagnosticCheck


MESSAGES = {
    "en": {
        "model_ready": "Recognition model is available locally.",
        "model_download": "Model is not local yet, but an automatic download URL is configured.",
        "model_missing": "Recognition model is missing and no download URL is configured.",
        "poppler_ready": "PDF tools are available.",
        "poppler_missing": "Poppler was not found. PDF input may fail.",
        "ffmpeg_ready": "FFmpeg is available for MP3/video work.",
        "ffmpeg_missing": "FFmpeg was not found in PATH. MP3/video export may fail.",
        "soundfont_ready": "SoundFont file is available locally.",
        "soundfont_download": "SoundFont is not local yet, but an automatic download URL is configured.",
        "soundfont_missing": "SoundFont is missing and no download URL is configured.",
        "fluidsynth_ready": "FluidSynth is available for SoundFont rendering.",
        "fluidsynth_missing": "FluidSynth was not found. PyClef can fall back to internal synthesis.",
    },
    "pt": {
        "model_ready": "Modelo de reconhecimento disponivel localmente.",
        "model_download": "O modelo ainda nao esta local, mas ha URL configurada para download automatico.",
        "model_missing": "Modelo de reconhecimento ausente e sem URL de download configurada.",
        "poppler_ready": "Ferramentas de PDF disponiveis.",
        "poppler_missing": "Poppler nao encontrado. Entrada por PDF pode falhar.",
        "ffmpeg_ready": "FFmpeg disponivel para MP3/video.",
        "ffmpeg_missing": "FFmpeg nao encontrado no PATH. Exportacao MP3/video pode falhar.",
        "soundfont_ready": "SoundFont disponivel localmente.",
        "soundfont_download": "O SoundFont ainda nao esta local, mas ha URL configurada para download automatico.",
        "soundfont_missing": "SoundFont ausente e sem URL de download configurada.",
        "fluidsynth_ready": "FluidSynth disponivel para renderizacao SoundFont.",
        "fluidsynth_missing": "FluidSynth nao encontrado. O PyClef pode usar sintese interna.",
    },
}


def _tr(language, key):
    return MESSAGES.get(language, MESSAGES["en"]).get(key, key)


def _existing_command(command_name, directory=None):
    executable = f"{command_name}.exe" if os.name == "nt" else command_name
    if directory:
        candidate = Path(directory) / executable
        if candidate.exists():
            return str(candidate)
    return shutil.which(command_name)


def collect_environment_diagnostics(language="en"):
    language = language if language in MESSAGES else "en"
    checks = []

    model_path = Path(config.YOLO_MODEL)
    if model_path.exists() and model_path.stat().st_size > 0:
        checks.append(DiagnosticCheck("model", "Model", "ok", _tr(language, "model_ready"), str(model_path)))
    elif config.MODEL_URL:
        checks.append(DiagnosticCheck("model", "Model", "warning", _tr(language, "model_download"), config.MODEL_URL))
    else:
        checks.append(DiagnosticCheck("model", "Model", "error", _tr(language, "model_missing")))

    poppler_path = _existing_command("pdfinfo", config.POPPLER_PATH) or _existing_command("pdftoppm", config.POPPLER_PATH)
    if poppler_path:
        checks.append(DiagnosticCheck("poppler", "Poppler", "ok", _tr(language, "poppler_ready"), poppler_path))
    else:
        checks.append(DiagnosticCheck("poppler", "Poppler", "warning", _tr(language, "poppler_missing"), config.POPPLER_PATH))

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        checks.append(DiagnosticCheck("ffmpeg", "FFmpeg", "ok", _tr(language, "ffmpeg_ready"), ffmpeg_path))
    else:
        checks.append(DiagnosticCheck("ffmpeg", "FFmpeg", "warning", _tr(language, "ffmpeg_missing")))

    soundfont_path = Path(config.SOUNDFONT_PATH)
    if soundfont_path.exists() and soundfont_path.stat().st_size > 0:
        checks.append(DiagnosticCheck("soundfont", "SoundFont", "ok", _tr(language, "soundfont_ready"), str(soundfont_path)))
    elif config.SOUNDFONT_URL:
        checks.append(DiagnosticCheck("soundfont", "SoundFont", "warning", _tr(language, "soundfont_download"), config.SOUNDFONT_URL))
    else:
        checks.append(DiagnosticCheck("soundfont", "SoundFont", "warning", _tr(language, "soundfont_missing")))

    fluidsynth_path = audio_utils.resolve_fluidsynth_path()
    if fluidsynth_path:
        checks.append(DiagnosticCheck("fluidsynth", "FluidSynth", "ok", _tr(language, "fluidsynth_ready"), fluidsynth_path))
    else:
        checks.append(DiagnosticCheck("fluidsynth", "FluidSynth", "warning", _tr(language, "fluidsynth_missing")))

    return checks


def diagnostics_overall_status(checks):
    statuses = {check.status for check in checks}
    if "error" in statuses:
        return "error"
    if "warning" in statuses:
        return "warning"
    return "ok"


def summarize_diagnostics(checks, language="en"):
    language = language if language in MESSAGES else "en"
    ok_count = sum(1 for check in checks if check.status == "ok")
    warning_count = sum(1 for check in checks if check.status == "warning")
    error_count = sum(1 for check in checks if check.status == "error")
    if language == "pt":
        return f"{ok_count} OK, {warning_count} aviso(s), {error_count} erro(s)."
    return f"{ok_count} OK, {warning_count} warning(s), {error_count} error(s)."


def format_diagnostics(checks):
    return "\n".join(f"{check.title}: {check.message}" for check in checks)
