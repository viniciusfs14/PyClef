# PyClef model retraining workflow

This folder contains a small training toolkit for improving the PyClef YOLO
model with real hard cases from the desktop app.

The first retraining path is **Dense-compatible**: it keeps the original class
IDs used by the current model, so `pyclef_app/config.py` can keep interpreting
predictions without changing the application logic.

## Recommended workflow

1. Create the dataset folders:

```bash
python training/scripts/scaffold_dataset.py
```

2. Bootstrap labels from the current model:

```bash
python training/scripts/bootstrap_annotations.py path/to/score.png --split train
```

You can pass many files or folders. PDF, PNG, JPG, and JPEG are supported.
PDF pages are rendered before prediction.

3. Correct the generated labels in your annotation tool.

The labels are YOLO text files in:

```text
training/datasets/pyclef_hard_cases/labels/train
training/datasets/pyclef_hard_cases/labels/val
```

Use the original score image, not the PyClef annotated output, whenever
possible. The annotated output is useful as a visual clue, but the model should
train on clean sheet music.

4. Train from the current PyClef model:

```bash
python training/scripts/train_yolo.py --epochs 80 --imgsz 1280 --batch 4
```

5. Evaluate predictions on validation pages:

```bash
python training/scripts/evaluate_yolo.py ^
  --model training/runs/pyclef-finetune-v1/weights/best.pt ^
  --source training/datasets/pyclef_hard_cases/images/val
```

6. Test the new model in the app without replacing the released model:

```powershell
$env:PYCLEF_MODEL_PATH="D:\PyClef\training\runs\pyclef-finetune-v1\weights\best.pt"
pyclef
```

## Annotation rules

- For notes, box the notehead as tightly as possible. Do not include the full
  stem unless the original Dense class expects it.
- In chords, each notehead should have its own box.
- Keep accidentals, clefs, rests, staves, and braces as separate boxes.
- Leave lyrics, chord names, guitar diagrams, dynamics that are not modeled,
  page numbers, and text unannotated. They become negative context.
- Split by song, not by page. Pages from the same song should not be mixed
  between train and validation.

## Known Dense-compatible class IDs used by PyClef

The current application maps several Dense class IDs into musical categories:

```text
0, 136       brace
5, 141       treble clef
8, 143       bass clef
24, 26, 156  quarter note
28, 30, 157  half note
32, 34, 158  whole note
59, 170      flat
63, 172      sharp
84           whole rest
85           half rest
86, 184      quarter rest
134, 207     staff
46, 47, 48, 49 dynamics
```

The generated `data.yaml` contains 208 class names so these sparse IDs remain
valid for YOLO training.

## Practical target

Start with 100 to 300 carefully corrected hard-case pages. That is usually more
useful than retraining with a large generic dataset that does not match the
scores PyClef receives.

