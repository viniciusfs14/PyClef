import cv2
import numpy as np
from ultralytics import YOLO
from pdf2image import convert_from_path
from PIL import Image
from pydub import AudioSegment
from mido import Message, MidiFile, MidiTrack, MetaMessage

from . import config
from . import audio_utils
from . import vision_utils
from . vision_utils import *


class PyClefEngine:

    def __init__(self, bpm=72):

        self.bpm = bpm
        self.model = YOLO(config.YOLO_MODEL)

    def process_files(self, file_list):

        pages_images = []

        for f in file_list:

            if f.lower().endswith(".pdf"):

                pages_images.extend(
                    convert_from_path(
                        f,
                        dpi=200,
                        poppler_path=config.POPPLER_PATH
                    )
                )

            else:

                pages_images.append(Image.open(f))

        return self.process_pages(pages_images)


    def process_pages(self, pages_images):

        full_song = AudioSegment.silent(duration=1200000)

        midi_events = []
        video_events = []
        page_frames = []

        ms_per_beat = (60 / self.bpm) * 1000

        global_time_ms = 500
        current_velocity = config.VOLUME_MAP['default']

        # AQUI entra todo o resto do algoritmo
        # praticamente igual ao que você já escreveu

        return {
            "audio": full_song,
            "midi_events": midi_events,
            "video_events": video_events,
            "frames": page_frames
        }