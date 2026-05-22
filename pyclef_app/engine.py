# main.py - VERSÃO COM AGRUPAMENTO RÍGIDO DE SISTEMAS
import cv2
import numpy as np
import os
import re
import tkinter as tk
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
from . import vision_utils

BASE_DIR = Path(__file__).resolve().parent

PROGRESS_MESSAGES = {
    "pt": {
        "loading_model": "Carregando modelo de reconhecimento...",
        "preparing_pages": "Preparando paginas da partitura...",
        "processing_page": "Processando pagina {page}...",
        "systems_found": "Sistemas encontrados: {systems} | pautas por sistema: {sizes} | braces detectados: {braces}",
        "page_done": "Pagina {page} concluida.",
        "exporting_files": "Exportando arquivos...",
        "generating_mp3": "Gerando MP3...",
        "preparing_video_audio": "Preparando audio temporario para o video...",
        "generating_midi": "Gerando MIDI...",
        "rendering_video": "Renderizando video. Esta etapa pode demorar...",
        "rendering_frames": "Renderizando quadros do video...",
        "syncing_video": "Sincronizando audio e video...",
        "done": "Sincronia de sistemas corrigida!",
    },
    "en": {
        "loading_model": "Loading recognition model...",
        "preparing_pages": "Preparing score pages...",
        "processing_page": "Processing page {page}...",
        "systems_found": "Systems found: {systems} | staves per system: {sizes} | braces detected: {braces}",
        "page_done": "Page {page} complete.",
        "exporting_files": "Exporting files...",
        "generating_mp3": "Generating MP3...",
        "preparing_video_audio": "Preparing temporary audio for the video...",
        "generating_midi": "Generating MIDI...",
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

# Configurações Visuais
COLOR_BOX = (225, 105, 65)
COLOR_TEXT = (255, 255, 255)
COLOR_BG_TEXT = (0, 0, 0)
FONT_SCALE = 1.2
FONT_THICKNESS = 3
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
STAFF_IDS = {134, 207}
BRACE_IDS = {0, 136}
RHYTHMIC_MARKERS = ("quarter", "half", "whole", "note")

def draw_text_with_background(img, text, x, y, font_face, font_scale, color, thickness, bg_color):
    (text_width, text_height), baseline = cv2.getTextSize(text, font_face, font_scale, thickness)
    cv2.rectangle(img, (x, y - text_height - baseline), (x + text_width, y + baseline), bg_color, -1)
    cv2.putText(img, text, (x, y), font_face, font_scale, color, thickness, cv2.LINE_AA)

def is_rhythmic_object(otype):
    return any(marker in otype for marker in RHYTHMIC_MARKERS)

def duration_for_type(otype, ms_per_beat):
    if "whole" in otype:
        return ms_per_beat * 4
    if "half" in otype:
        return ms_per_beat * 2
    return ms_per_beat

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

def group_staves_by_braces(staves, braces):
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

        for group in split_indices_by_staff_gaps(system_indices, staves, gap_threshold):
            if len(group) < 2:
                continue
            for idx in group:
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

        for idx in current_indices:
            used_staves.add(idx)
        current_system = [staves[idx] for idx in current_indices]
        systems.append(current_system)
        i = max(j, i + 1)

    return sorted(systems, key=lambda system: min(staff[1] for staff in system))

def group_objects_by_x(objects, tolerance):
    columns = []
    for obj in sorted(objects, key=lambda item: item['x']):
        if columns and abs(obj['x'] - columns[-1]['x']) <= tolerance:
            columns[-1]['items'].append(obj)
            columns[-1]['x'] = sum(item['x'] for item in columns[-1]['items']) / len(columns[-1]['items'])
        else:
            columns.append({'x': obj['x'], 'items': [obj]})
    return columns

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
    annotated_files = []
    output_stem = safe_output_stem(file_list[0])
    output_dir = Path.cwd() / f"results_{output_stem}"
    output_dir.mkdir(parents=True, exist_ok=True)

    progress("loading_model", 3)
    if not Path(config.YOLO_MODEL).exists():
        raise FileNotFoundError(
            "YOLO model not found. Place best.pt in pyclef_app/model/ "
            "or set the PYCLEF_MODEL_PATH environment variable to the model file."
        )
    model = YOLO(config.YOLO_MODEL)
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
                objects.append({'id': item['id'], 'x': (item['box'][0]+item['box'][2])/2, 'y': (item['box'][1]+item['box'][3])/2, 'box': item['box']})

        staves.sort(key=lambda x: x[1])
        
        systems = group_staves_by_braces(staves, braces)
        system_sizes = ", ".join(str(len(system)) for system in systems) or "0"
        progress(
            "systems_found",
            min(page_start_percent + 6, page_end_percent),
            systems=len(systems),
            sizes=system_sizes,
            braces=len(braces),
        )

        for system in systems:
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
                        draw_text_with_background(img_traduzido, f"{nb}{octv}", b[0], b[1]-15, FONT_FACE, FONT_SCALE, COLOR_TEXT, FONT_THICKNESS, COLOR_BG_TEXT)
                        
                        freq = audio_utils.get_frequency(nb, "", octv)
                        midi_p = audio_utils.note_to_midi(nb, "", octv)
                        
                        wave = audio_utils.generate_piano_sound(freq, dur, velocity=0.8)
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
    audio_path = output_dir / f"{output_stem}.mp3"
    temp_audio_path = output_dir / f"_{output_stem}_video_audio.mp3"
    if want_audio:
        progress("generating_mp3", 78)
        final_audio.export(str(audio_path), format="mp3")
    elif want_video:
        progress("preparing_video_audio", 78)
        final_audio.export(str(temp_audio_path), format="mp3")
    
    # MIDI
    midi_path = output_dir / f"{output_stem}.mid"
    if want_midi:
        progress("generating_midi", 82)
        mid = MidiFile()
        track = MidiTrack(); mid.tracks.append(track)
        track.append(MetaMessage('set_tempo', tempo=int(60000000 / bpm)))
        midi_events.sort(key=lambda x: x['time'])
        curr_t = 0
        t_to_ticks = mid.ticks_per_beat / ms_per_beat
        for e in midi_events:
            abs_ticks = int(e['time'] * t_to_ticks)
            track.append(Message('note_on' if e['type'] == 'on' else 'note_off', note=e['note'], velocity=e['vel'], time=max(0, abs_ticks - curr_t)))
            curr_t = abs_ticks
        mid.save(str(midi_path))
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
