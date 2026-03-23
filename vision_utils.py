from .config import LATIN_NOTES

def calculate_pitch(note_y, staff_bottom, step_size, clef="clefG"):
    delta_y = staff_bottom - note_y
    steps = round(delta_y / step_size)
    base_idx = 2 if clef == "clefG" else 4 
    octave_base = 4 if clef == "clefG" else 2
    total = base_idx + steps 
    return LATIN_NOTES[total % 7], octave_base + (total // 7)

def calculate_iou(box1, box2):
    x1, y1 = max(box1[0], box2[0]), max(box1[1], box2[1])
    x2, y2 = min(box1[2], box2[2]), min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = (box1[2]-box1[0])*(box1[3]-box1[1]) + (box2[2]-box2[0])*(box2[3]-box2[1]) - inter
    return inter / union if union > 0 else 0