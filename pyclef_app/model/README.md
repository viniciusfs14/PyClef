# PyClef model

The YOLO model file is not tracked in Git because GitHub and PyPI block large
files by default.

PyClef will download `best.pt` automatically from:

```text
https://github.com/viniciusfs14/PyClef/releases/download/model-v1.0.0/best.pt
```

Attach `best.pt` to that GitHub Release, or override the URL with
`PYCLEF_MODEL_URL`.

For local development, you can also set `PYCLEF_MODEL_PATH` to the full path of
the model file before starting PyClef.
