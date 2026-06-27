# audio_utils.py
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass

import numpy as np
from pydub import AudioSegment
from . import config
from .config import SAMPLE_RATE, LATIN_NOTES

def get_frequency(note_base, accidental, octave):
    semitones = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n = semitones[note_base]
    if accidental == 's': n += 1
    elif accidental == 'ss': n += 2
    elif accidental == 'b': n -= 1
    elif accidental == 'bb': n -= 2
    return 16.3516 * (2 ** (octave + n/12))

def note_to_midi(note_base, accidental, octave):
    semitones = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    accidental_offset = {'s': 1, 'ss': 2, 'b': -1, 'bb': -2}.get(accidental, 0)
    return 12 + (octave * 12) + semitones[note_base] + accidental_offset


@dataclass(frozen=True)
class PianoTimbre:
    partials: tuple
    voices: tuple
    attack_seconds: float
    body_decay: float
    hammer_noise: float
    hammer_decay: float
    brightness: float
    release_power: float
    velocity_curve: float
    output_gain: float


PIANO_TIMBRES = {
    "piano": PianoTimbre(
        partials=(
            (1.0, 1.00, 0.28),
            (2.0, 0.44, 0.72),
            (3.0, 0.24, 1.12),
            (4.0, 0.15, 1.70),
            (5.0, 0.095, 2.25),
            (6.0, 0.058, 2.90),
            (7.0, 0.035, 3.65),
            (8.0, 0.024, 4.35),
            (9.0, 0.015, 5.15),
            (10.0, 0.010, 6.10),
        ),
        voices=((0.0, 1.0), (-0.75, 0.20), (0.65, 0.18)),
        attack_seconds=0.0042,
        body_decay=0.105,
        hammer_noise=0.020,
        hammer_decay=72.0,
        brightness=0.18,
        release_power=1.82,
        velocity_curve=0.86,
        output_gain=0.73,
    ),
    "soft_piano": PianoTimbre(
        partials=(
            (1.0, 1.00, 0.26),
            (2.0, 0.32, 0.70),
            (3.0, 0.15, 1.15),
            (4.0, 0.070, 1.95),
            (5.0, 0.032, 2.80),
            (6.0, 0.014, 3.70),
        ),
        voices=((0.0, 1.0), (-0.45, 0.14), (0.40, 0.12)),
        attack_seconds=0.0075,
        body_decay=0.095,
        hammer_noise=0.008,
        hammer_decay=90.0,
        brightness=0.055,
        release_power=2.18,
        velocity_curve=0.82,
        output_gain=0.76,
    ),
    "bright_piano": PianoTimbre(
        partials=(
            (1.0, 1.00, 0.33),
            (2.0, 0.50, 0.82),
            (3.0, 0.32, 1.18),
            (4.0, 0.20, 1.65),
            (5.0, 0.13, 2.20),
            (6.0, 0.082, 2.80),
            (7.0, 0.050, 3.45),
            (8.0, 0.033, 4.15),
            (9.0, 0.022, 4.95),
            (10.0, 0.014, 5.80),
            (11.0, 0.009, 6.70),
        ),
        voices=((0.0, 1.0), (-0.95, 0.24), (0.85, 0.22)),
        attack_seconds=0.0032,
        body_decay=0.13,
        hammer_noise=0.026,
        hammer_decay=64.0,
        brightness=0.28,
        release_power=1.70,
        velocity_curve=0.90,
        output_gain=0.70,
    ),
}


def normalize_timbre(timbre):
    return timbre if timbre in available_timbres() else "piano"


def available_timbres():
    return tuple(PIANO_TIMBRES.keys()) + ("soundfont_piano",)


def soundfont_timbres():
    return {"soundfont_piano"}


def is_soundfont_timbre(timbre):
    return timbre in soundfont_timbres()


def cents_to_ratio(cents):
    return 2 ** (cents / 1200)


def high_pass_noise(num_samples):
    noise = np.random.uniform(-1, 1, num_samples)
    previous = np.concatenate(([0.0], noise[:-1]))
    return noise - (previous * 0.72)


def add_air(signal, amount):
    if amount <= 0:
        return signal
    previous = np.concatenate(([0.0], signal[:-1]))
    transient = signal - previous
    return signal + (transient * amount)


def generate_piano_sound(freq, duration_ms, velocity=0.7, release_ms=260, timbre="piano"):
    if freq <= 0:
        return np.zeros(100, dtype=np.int16)

    normalized_timbre = normalize_timbre(timbre)
    profile_key = "piano" if is_soundfont_timbre(normalized_timbre) else normalized_timbre
    profile = PIANO_TIMBRES[profile_key]
    velocity = max(0.05, min(1.0, float(velocity)))
    duration_ms = max(30, int(duration_ms))
    release_ms = max(0, int(release_ms))
    total_ms = duration_ms + release_ms
    num_samples = max(1, int(SAMPLE_RATE * (total_ms / 1000)))
    hold_samples = min(num_samples, int(SAMPLE_RATE * (duration_ms / 1000)))

    t = np.arange(num_samples) / SAMPLE_RATE

    samples = np.zeros(num_samples)
    for harmonic, amplitude, decay in profile.partials:
        harmonic_mix = np.zeros(num_samples)
        for cents, voice_gain in profile.voices:
            voice_freq = freq * harmonic * cents_to_ratio(cents)
            phase = (harmonic * 0.37) + (cents * 0.013)
            harmonic_mix += (
                voice_gain
                * np.sin((2 * np.pi * voice_freq * t) + phase)
            )
        partial_attack = 1 - np.exp(
            -t / max(0.0016, profile.attack_seconds / (1 + harmonic * 0.32))
        )
        sparkle = 1 + (profile.brightness * min(1.0, harmonic / 8.0) * velocity)
        samples += amplitude * sparkle * harmonic_mix * np.exp(-decay * t) * partial_attack

    body_envelope = np.exp(-profile.body_decay * t)
    hammer_noise = (
        high_pass_noise(num_samples)
        * np.exp(-profile.hammer_decay * t)
        * profile.hammer_noise
        * (0.65 + velocity * 0.55)
    )
    release_envelope = np.ones(num_samples)
    if release_ms > 0 and hold_samples < num_samples:
        release_t = np.linspace(0, 1, num_samples - hold_samples)
        release_envelope[hold_samples:] = (
            np.cos(release_t * np.pi / 2) ** profile.release_power
        )

    shaped = ((samples * body_envelope) + hammer_noise) * release_envelope
    shaped = add_air(shaped, profile.brightness * 0.10)
    shaped = np.tanh(shaped * 1.08) / np.tanh(1.08)
    peak = np.max(np.abs(shaped)) or 1
    gain = min(0.86, (velocity ** profile.velocity_curve) * profile.output_gain)
    shaped = shaped / peak * gain
    return (shaped * 32767).astype(np.int16)

def ensure_default_soundfont(progress_callback=None):
    soundfont_path = config.SOUNDFONT_PATH
    if soundfont_path.exists() and soundfont_path.stat().st_size > 0:
        return soundfont_path

    if not config.SOUNDFONT_URL:
        raise FileNotFoundError(
            "SoundFont not found. Set PYCLEF_SOUNDFONT_PATH or PYCLEF_SOUNDFONT_URL."
        )

    soundfont_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = soundfont_path.with_suffix(soundfont_path.suffix + ".download")
    if temp_path.exists():
        temp_path.unlink()

    downloaded = 0
    try:
        with urllib.request.urlopen(config.SOUNDFONT_URL, timeout=30) as response:
            total = int(response.headers.get("Content-Length") or 0)
            with temp_path.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
        temp_path.replace(soundfont_path)
    except (urllib.error.URLError, OSError) as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(
            "Could not download the PyClef test SoundFont. "
            f"URL: {config.SOUNDFONT_URL}"
        ) from exc

    return soundfont_path


def resolve_fluidsynth_path():
    configured = config.FLUIDSYNTH_PATH
    if configured and ("/" in configured or "\\" in configured):
        return configured if shutil.which(configured) or configured else None
    return shutil.which(configured) or shutil.which("fluidsynth")


def render_midi_with_soundfont(midi_path, wav_path, soundfont_path=None, gain=0.62):
    soundfont_path = soundfont_path or ensure_default_soundfont()
    fluidsynth_path = resolve_fluidsynth_path()
    if not fluidsynth_path:
        raise FileNotFoundError(
            "FluidSynth was not found. Install FluidSynth or set PYCLEF_FLUIDSYNTH_PATH."
        )

    command = [
        fluidsynth_path,
        "-ni",
        "-g",
        str(gain),
        "-F",
        str(wav_path),
        "-r",
        str(SAMPLE_RATE),
        str(soundfont_path),
        str(midi_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "FluidSynth failed to render the MIDI file.\n"
            f"STDOUT: {completed.stdout}\nSTDERR: {completed.stderr}"
        )
    return wav_path

def normalize_peak(audio_segment, target_max_dbfs=-2.0):
    if audio_segment.max_dBFS == float("-inf"):
        return audio_segment
    return audio_segment.apply_gain(target_max_dbfs - audio_segment.max_dBFS)

def apply_reverb(audio_segment, gain=0.3):
    delay_ms = 50
    silence = AudioSegment.silent(duration=delay_ms)
    delayed = silence + (audio_segment - (10 * (1-gain)))
    return audio_segment.overlay(delayed)
