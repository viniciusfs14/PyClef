# PyClef

PyClef is a desktop Optical Music Recognition workflow for turning sheet music
into annotated pages, audio, MIDI, and synchronized video.

## Usage

```python
from pyclef import Pyclef

Pyclef()
```

Or from the terminal:

```bash
pyclef
```

## Model file

The YOLO model is not included in the PyPI package because it is larger than the
default file limits for GitHub and PyPI.

Place `best.pt` here:

```text
pyclef_app/model/best.pt
```

Or set the environment variable `PYCLEF_MODEL_PATH` to the full path of the
model file before starting PyClef.

## External requirements

PDF input uses Poppler through `pdf2image`. On Windows, install Poppler and make
sure the path configured in `pyclef_app/config.py` is available on your machine.
