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

On first processing, PyClef looks for the model in this order:

1. `PYCLEF_MODEL_PATH`, if set.
2. The user cache at `~/.pyclef/models/best.pt`.
3. Automatic download from `PYCLEF_MODEL_URL`.

By default, `PYCLEF_MODEL_URL` points to the PyClef GitHub Release asset:

```text
https://github.com/viniciusfs14/PyClef/releases/download/model-v1.0.0/best.pt
```

Create that release and attach `best.pt` to make the download automatic for
users.

For manual setup, place `best.pt` here:

```text
~/.pyclef/models/best.pt
```

Or set `PYCLEF_MODEL_PATH` to the full path of the model file before starting
PyClef.

## External requirements

PDF input uses Poppler through `pdf2image`. On Windows, install Poppler and make
sure the path configured in `pyclef_app/config.py` is available on your machine.
