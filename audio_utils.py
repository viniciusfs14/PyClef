# audio_utils.py
import numpy as np
from pydub import AudioSegment
from .config import SAMPLE_RATE, LATIN_NOTES

def get_frequency(note_base, accidental, octave):
    semitones = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n = semitones[note_base]
    if accidental == 's': n += 1
    elif accidental == 'b': n -= 1
    return 16.3516 * (2 ** (octave + n/12))

def note_to_midi(note_base, accidental, octave):
    semitones = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    return 12 + (octave * 12) + semitones[note_base] + (1 if accidental == 's' else -1 if accidental == 'b' else 0)

def generate_piano_sound(freq, duration_ms, velocity=0.7):
    if freq <= 0: return np.zeros(100, dtype=np.int16)
    num_samples = int(SAMPLE_RATE * (duration_ms / 1000))
    N = int(SAMPLE_RATE / freq)
    ring_buffer = np.random.uniform(-1, 1, N) * velocity 
    samples = np.zeros(num_samples)
    for i in range(num_samples):
        samples[i] = ring_buffer[0]
        avg = 0.5 * (ring_buffer[0] + ring_buffer[1])
        decay = 0.996 + (velocity * 0.002) 
        ring_buffer = np.append(ring_buffer[1:], avg * min(decay, 0.998))
    t = np.linspace(0, duration_ms/1000, num_samples)
    envelope = np.exp(-1.6 * t)
    return (samples * envelope * 32767).astype(np.int16)

def apply_reverb(audio_segment, gain=0.3):
    delay_ms = 50
    silence = AudioSegment.silent(duration=delay_ms)
    delayed = silence + (audio_segment - (10 * (1-gain)))
    return audio_segment.overlay(delayed)