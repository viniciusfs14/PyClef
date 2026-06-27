# PyClef Regression Checks

Use the scientific report JSON as a stable regression artifact.

1. Generate a score with `Scientific report` enabled.
2. Create a baseline:

```bash
pyclef-regression --actual results_score/score_scientific_report.json --baseline tests/regression/baselines/score.json --write-baseline
```

3. Compare future runs:

```bash
pyclef-regression --actual results_score/score_scientific_report.json --baseline tests/regression/baselines/score.json
```

The comparison focuses on recognition counts, confidence buckets, hand distribution, pitch classes, durations, validation status, and key-signature context.
