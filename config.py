# config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

YOLO_MODEL = BASE_DIR / "model" / "best.pt"

OUTPUT_BASE_NAME = "vinicin"
POPPLER_PATH = r'C:\poppler\Library\bin' 

FPS = 30 
SAMPLE_RATE = 44100 

ID_MAP = {
    24: 'quarter', 26: 'quarter', 156: 'quarter',
    28: 'half', 30: 'half', 157: 'half',
    32: 'whole', 34: 'whole', 158: 'whole',
    84: 'rest_whole', 85: 'rest_half', 86: 'rest_quarter', 184: 'rest_quarter',
    5: 'clefG', 141: 'clefG', 8: 'clefF', 143: 'clefF',
    63: 'sharp', 172: 'sharp', 59: 'flat', 170: 'flat',
    0: 'brace', 136: 'brace',
    48: 'dynamicP', 46: 'dynamicF', 47: 'dynamicMF', 49: 'dynamicMP'
}

VOLUME_MAP = {'dynamicP': 0.4, 'dynamicMP': 0.55, 'dynamicMF': 0.75, 'dynamicF': 1.0, 'default': 0.7}
LATIN_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']