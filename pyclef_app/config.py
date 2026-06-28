import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _runtime_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return BASE_DIR.parent


APP_ROOT = _runtime_root()
TOOLS_DIR = Path(os.environ.get("PYCLEF_TOOLS_DIR", APP_ROOT / "tools"))


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _first_existing_file(paths):
    for path in paths:
        candidate = Path(path)
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _first_existing_dir(paths):
    for path in paths:
        candidate = Path(path)
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def _executable_name(name):
    return f"{name}.exe" if os.name == "nt" else name


def _resolve_bundled_tool(env_name, executable_name, fallback):
    configured = os.environ.get(env_name)
    if configured:
        return configured

    candidates = [
        TOOLS_DIR / "ffmpeg" / "bin" / executable_name,
        TOOLS_DIR / "fluidsynth" / "bin" / executable_name,
        APP_ROOT / "ffmpeg" / "bin" / executable_name,
        APP_ROOT / "fluidsynth" / "bin" / executable_name,
        APP_ROOT / executable_name,
    ]
    match = _first_existing_file(candidates)
    return str(match) if match else fallback


def _prepend_tool_dir(tool_path):
    candidate = Path(str(tool_path))
    if not candidate.exists() or not candidate.is_file():
        return
    directory = str(candidate.parent)
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    if directory not in path_parts:
        os.environ["PATH"] = directory + os.pathsep + os.environ.get("PATH", "")


BUNDLED_MODEL = _first_existing_file([
    BASE_DIR / "model" / "best.pt",
    TOOLS_DIR / "model" / "best.pt",
    APP_ROOT / "model" / "best.pt",
])
PACKAGE_MODEL = BUNDLED_MODEL or BASE_DIR / "model" / "best.pt"
MODEL_CACHE_DIR = Path(os.environ.get("PYCLEF_MODEL_DIR", Path.home() / ".pyclef" / "models"))
MODEL_URL = os.environ.get(
    "PYCLEF_MODEL_URL",
    "https://github.com/viniciusfs14/PyClef/releases/download/model-v1.0.0/best.pt.zip",
)
YOLO_MODEL = Path(os.environ["PYCLEF_MODEL_PATH"]) if os.environ.get("PYCLEF_MODEL_PATH") else (
    PACKAGE_MODEL if PACKAGE_MODEL.exists() else MODEL_CACHE_DIR / "best.pt"
)
SOUNDFONT_CACHE_DIR = Path(
    os.environ.get("PYCLEF_SOUNDFONT_DIR", Path.home() / ".pyclef" / "soundfonts")
)
BUNDLED_SOUNDFONT = _first_existing_file([
    BASE_DIR / "soundfonts" / "GeneralUser-GS.sf2",
    TOOLS_DIR / "soundfonts" / "GeneralUser-GS.sf2",
    APP_ROOT / "soundfonts" / "GeneralUser-GS.sf2",
])
SOUNDFONT_URL = os.environ.get(
    "PYCLEF_SOUNDFONT_URL",
    "https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/GeneralUser-GS.sf2",
)
SOUNDFONT_PATH = (
    Path(os.environ["PYCLEF_SOUNDFONT_PATH"])
    if os.environ.get("PYCLEF_SOUNDFONT_PATH")
    else BUNDLED_SOUNDFONT or SOUNDFONT_CACHE_DIR / "GeneralUser-GS.sf2"
)
FFMPEG_PATH = _resolve_bundled_tool("PYCLEF_FFMPEG_PATH", _executable_name("ffmpeg"), "ffmpeg")
FFPROBE_PATH = _resolve_bundled_tool("PYCLEF_FFPROBE_PATH", _executable_name("ffprobe"), "ffprobe")
FLUIDSYNTH_PATH = _resolve_bundled_tool("PYCLEF_FLUIDSYNTH_PATH", _executable_name("fluidsynth"), "fluidsynth")
for _tool_path in (FFMPEG_PATH, FFPROBE_PATH, FLUIDSYNTH_PATH):
    _prepend_tool_dir(_tool_path)
if Path(str(FFMPEG_PATH)).exists():
    os.environ.setdefault("IMAGEIO_FFMPEG_EXE", str(FFMPEG_PATH))
OUTPUT_BASE_NAME = "vinicin"
POPPLER_PATH = os.environ.get("PYCLEF_POPPLER_PATH") or str(
    _first_existing_dir([
        TOOLS_DIR / "poppler" / "bin",
        TOOLS_DIR / "poppler" / "Library" / "bin",
        APP_ROOT / "poppler" / "bin",
        APP_ROOT / "poppler" / "Library" / "bin",
        Path(r"C:\poppler\Library\bin"),
    ])
    or Path(r"C:\poppler\Library\bin")
)

FPS = max(24, _env_int("PYCLEF_VIDEO_FPS", 60))
SAMPLE_RATE = 44100 

ID_MAP = {
    0: 'brace', 136: 'brace',
    1: 'ledgerLine', 137: 'ledgerLine',
    2: 'repeatDot', 138: 'repeatDot',
    3: 'segno', 139: 'segno',
    4: 'coda', 140: 'coda',
    5: 'clefG', 141: 'clefG',
    6: 'clefCAlto', 7: 'clefCTenor', 142: 'clefC',
    8: 'clefF', 143: 'clefF',
    9: 'clefPercussion', 10: 'clef8', 11: 'clef15',
    12: 'timeSig0', 13: 'timeSig1', 14: 'timeSig2', 15: 'timeSig3',
    16: 'timeSig4', 17: 'timeSig5', 18: 'timeSig6', 19: 'timeSig7',
    20: 'timeSig8', 21: 'timeSig9',
    22: 'timeSigCommon', 23: 'timeSigCutCommon',
    144: 'timeSig8', 145: 'timeSig0', 146: 'timeSig1', 147: 'timeSig2',
    148: 'timeSig3', 149: 'timeSig4', 150: 'timeSig5', 151: 'timeSig6',
    152: 'timeSig7', 153: 'timeSig9',
    154: 'timeSigCommon', 155: 'timeSigCutCommon',
    24: 'quarter', 25: 'quarter_small', 26: 'quarter', 27: 'quarter_small',
    156: 'quarter_small',
    28: 'half', 29: 'half_small', 30: 'half', 31: 'half_small',
    157: 'half_small',
    32: 'whole', 33: 'whole_small', 34: 'whole', 35: 'whole_small',
    158: 'whole',
    36: 'double_whole', 37: 'double_whole_small',
    38: 'double_whole', 39: 'double_whole_small',
    40: 'augmentationDot', 159: 'augmentationDot',
    41: 'stem', 160: 'stem',
    42: 'tremolo1', 43: 'tremolo2', 44: 'tremolo3', 45: 'tremolo4',
    46: 'tremolo5', 161: 'tremolo',
    47: 'flag8thUp', 48: 'flag8thUp', 49: 'flag16thUp',
    50: 'flag32ndUp', 51: 'flag64thUp', 52: 'flag128thUp',
    53: 'flag8thDown', 54: 'flag8thDown', 55: 'flag16thDown',
    56: 'flag32ndDown', 57: 'flag64thDown', 58: 'flag128thDown',
    162: 'flag8thUp', 163: 'flag16thUp', 164: 'flag32ndUp', 165: 'flag64thUp',
    166: 'flag8thDown', 167: 'flag16thDown', 168: 'flag32ndDown', 169: 'flag64thDown',
    59: 'flat', 60: 'flat', 170: 'flat',
    61: 'natural', 62: 'natural', 171: 'natural',
    63: 'sharp', 64: 'sharp', 172: 'sharp',
    65: 'doubleSharp', 173: 'doubleSharp',
    66: 'doubleFlat', 174: 'doubleFlat',
    67: 'keyFlat', 68: 'keyNatural', 69: 'keySharp',
    70: 'accent', 71: 'accent', 72: 'staccato', 73: 'staccato',
    74: 'tenuto', 75: 'tenuto', 76: 'staccatissimo', 77: 'staccatissimo',
    78: 'marcato', 79: 'marcato',
    175: 'accent', 176: 'staccato', 177: 'tenuto',
    178: 'marcato', 179: 'marcato',
    80: 'fermata', 81: 'fermata', 180: 'fermata', 181: 'fermata',
    82: 'caesura',
    83: 'rest_double_whole',
    84: 'rest_whole', 182: 'rest_whole',
    85: 'rest_half', 183: 'rest_half',
    86: 'rest_quarter', 184: 'rest_quarter',
    87: 'rest_8th', 185: 'rest_8th',
    88: 'rest_16th', 186: 'rest_16th',
    89: 'rest_32nd', 187: 'rest_32nd',
    90: 'rest_64th', 188: 'rest_64th',
    91: 'rest_128th',
    92: 'restHNr', 123: 'restHBar', 202: 'restHBar',
    93: 'dynamicP', 94: 'dynamicM', 95: 'dynamicF',
    96: 'dynamicS', 97: 'dynamicZ', 98: 'dynamicR',
    124: 'crescendoHairpin', 125: 'diminuendoHairpin',
    189: 'numeral',
    190: 'dynamicP', 191: 'dynamicM', 192: 'dynamicF',
    193: 'dynamicS', 194: 'dynamicZ', 195: 'dynamicR',
    203: 'crescendoHairpin', 204: 'diminuendoHairpin',
    99: 'graceAcciaccaturaUp', 100: 'graceAppoggiaturaUp',
    101: 'graceAcciaccaturaDown', 102: 'graceAppoggiaturaDown',
    196: 'graceAcciaccatura',
    103: 'trill', 104: 'turn', 105: 'turnInverted',
    106: 'mordent', 197: 'trill',
    107: 'downBow', 108: 'upBow',
    109: 'arpeggio', 198: 'arpeggio',
    110: 'pedalDown', 111: 'pedalUp',
    112: 'tuplet3', 113: 'tuplet6',
    126: 'tuplet1', 127: 'tuplet2', 128: 'tuplet4',
    129: 'tuplet5', 130: 'tuplet7', 131: 'tuplet8', 132: 'tuplet9',
    133: 'tupletBracket', 205: 'tuplet', 206: 'tupletBracket',
    114: 'fingering0', 115: 'fingering1', 116: 'fingering2',
    117: 'fingering3', 118: 'fingering4', 119: 'fingering5',
    120: 'slur', 199: 'slur',
    121: 'beam', 200: 'beam',
    122: 'tie', 201: 'tie',
    134: 'staff', 207: 'staff',
    135: 'ottavaBracket',
}

VOLUME_MAP = {
    'dynamicP': 0.40,
    'dynamicMP': 0.55,
    'dynamicM': 0.62,
    'dynamicMF': 0.75,
    'dynamicF': 0.95,
    'dynamicS': 1.0,
    'dynamicZ': 1.0,
    'dynamicR': 0.82,
    'default': 0.70,
}
LATIN_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
