import argparse
import json
from pathlib import Path

from .validation import validate_processing_result


def infer_result_folder_outputs(folder):
    folder = Path(folder)
    result = {"output_dir": str(folder)}
    annotations = sorted(str(path) for path in folder.glob("*_annotated_p*.jpg"))
    if annotations:
        result["annotations"] = annotations
    for key, patterns in {
        "audio": ("*.mp3",),
        "midi": ("*.mid", "*.midi"),
        "video": ("*.mp4",),
    }.items():
        matches = []
        for pattern in patterns:
            matches.extend(path for path in folder.glob(pattern) if not path.name.startswith("_"))
        if matches:
            result[key] = str(sorted(matches)[0])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a PyClef result folder.")
    parser.add_argument("folder", help="Path to a results_* folder.")
    parser.add_argument("--language", choices=("en", "pt"), default="en")
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON.")
    args = parser.parse_args(argv)

    result = infer_result_folder_outputs(args.folder)
    options = {
        "annotations": bool(result.get("annotations")),
        "audio": bool(result.get("audio")),
        "midi": bool(result.get("midi")),
        "video": bool(result.get("video")),
        "language": args.language,
    }
    report = validate_processing_result(result, options, language=args.language)
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        status = "OK" if report.ok else "FAILED"
        print(f"PyClef validation: {status}")
        for issue in report.issues:
            print(f"- {issue.severity.upper()}: {issue.message}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
