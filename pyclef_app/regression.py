import argparse
import json
import shutil
import sys
from pathlib import Path


SUMMARY_REVIEW_KEYS = (
    "event_count",
    "page_count",
    "duration_seconds",
    "average_confidence",
    "low_confidence_count",
    "review_confidence_count",
    "high_confidence_count",
    "left_hand_count",
    "right_hand_count",
    "accidental_count",
    "invalid_duration_count",
    "key_signature_count",
)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_report(report):
    if "validation_ok" in report and "recognition" in report and "musical_interpretation" in report:
        return report
    recognition = report.get("recognition", {})
    review = recognition.get("review", {})
    interpretation = report.get("musical_interpretation", {})
    timing = report.get("timing_interpretation", {})
    validation = report.get("validation") or {}
    return {
        "recognition": {
            "review": {key: review.get(key) for key in SUMMARY_REVIEW_KEYS},
            "confidence_histogram": recognition.get("confidence_histogram", {}),
        },
        "musical_interpretation": {
            "pitch_range": interpretation.get("pitch_range", {}),
            "pitch_class_counts": interpretation.get("pitch_class_counts", {}),
            "hand_distribution": interpretation.get("hand_distribution", {}),
            "accidental_distribution": interpretation.get("accidental_distribution", {}),
            "duration_profile": interpretation.get("duration_profile", {}),
            "key_signatures": interpretation.get("key_signatures", []),
        },
        "timing_interpretation": {
            "column_count": timing.get("column_count"),
            "max_polyphony": timing.get("max_polyphony"),
            "dense_moment_count": timing.get("dense_moment_count"),
            "average_gap_ms": timing.get("average_gap_ms"),
            "min_gap_ms": timing.get("min_gap_ms"),
            "max_gap_ms": timing.get("max_gap_ms"),
        },
        "validation_ok": validation.get("ok") if isinstance(validation, dict) else None,
    }


def compare_values(expected, actual, path="", tolerance=0.001):
    issues = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(expected) | set(actual))
        for key in keys:
            issues.extend(
                compare_values(
                    expected.get(key),
                    actual.get(key),
                    f"{path}.{key}" if path else str(key),
                    tolerance,
                )
            )
        return issues
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [f"{path}: expected {len(expected)} item(s), got {len(actual)}"]
        for index, (left, right) in enumerate(zip(expected, actual)):
            issues.extend(compare_values(left, right, f"{path}[{index}]", tolerance))
        return issues
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if abs(float(expected) - float(actual)) > tolerance:
            return [f"{path}: expected {expected}, got {actual}"]
        return []
    if expected != actual:
        return [f"{path}: expected {expected!r}, got {actual!r}"]
    return []


def write_baseline(actual_path, baseline_path):
    baseline_path = Path(baseline_path)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_report(load_json(actual_path))
    baseline_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return baseline_path


def compare_report(actual_path, baseline_path, tolerance=0.001):
    actual = normalize_report(load_json(actual_path))
    baseline = load_json(baseline_path)
    return compare_values(baseline, actual, tolerance=tolerance)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare PyClef scientific reports against regression baselines."
    )
    parser.add_argument("--actual", required=True, help="Path to a generated *_scientific_report.json file.")
    parser.add_argument("--baseline", required=True, help="Path to the normalized baseline JSON.")
    parser.add_argument("--write-baseline", action="store_true", help="Create or update the baseline from the actual report.")
    parser.add_argument("--tolerance", type=float, default=0.001, help="Numeric comparison tolerance.")
    parser.add_argument("--copy-actual", help="Optional path to archive the full actual report JSON.")
    args = parser.parse_args(argv)

    actual_path = Path(args.actual)
    baseline_path = Path(args.baseline)
    if not actual_path.exists():
        print(f"Actual report not found: {actual_path}", file=sys.stderr)
        return 2

    if args.copy_actual:
        copy_path = Path(args.copy_actual)
        copy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(actual_path, copy_path)

    if args.write_baseline:
        written = write_baseline(actual_path, baseline_path)
        print(f"Baseline written: {written}")
        return 0

    if not baseline_path.exists():
        print(f"Baseline not found: {baseline_path}", file=sys.stderr)
        return 2

    issues = compare_report(actual_path, baseline_path, tolerance=args.tolerance)
    if issues:
        print("Regression check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Regression check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
