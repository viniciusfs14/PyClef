import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


CONFIDENCE_BUCKETS = (
    ("low", 0.0, 0.38),
    ("review", 0.38, 0.55),
    ("high", 0.55, 1.01),
)


def _event_dict(event):
    if hasattr(event, "to_dict"):
        return event.to_dict()
    return dict(event)


def _safe_number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _counter_dict(counter):
    return {str(key): int(value) for key, value in sorted(counter.items())}


def _confidence_histogram(events):
    counts = {key: 0 for key, _low, _high in CONFIDENCE_BUCKETS}
    for event in events:
        confidence = event.get("confidence")
        if confidence is None:
            continue
        value = _safe_number(confidence)
        for key, low, high in CONFIDENCE_BUCKETS:
            if low <= value < high:
                counts[key] += 1
                break
    return counts


def _duration_profile(events):
    counts = Counter()
    for event in events:
        duration = int(_safe_number(event.get("duration_ms")))
        if duration <= 0:
            counts["invalid"] += 1
        elif duration < 260:
            counts["short"] += 1
        elif duration < 760:
            counts["medium"] += 1
        else:
            counts["long"] += 1
    return _counter_dict(counts)


def _pitch_range(events):
    midi_values = [
        int(_safe_number(event.get("midi_note")))
        for event in events
        if event.get("midi_note") is not None
    ]
    if not midi_values:
        return {"min_midi": None, "max_midi": None, "span_semitones": 0}
    return {
        "min_midi": min(midi_values),
        "max_midi": max(midi_values),
        "span_semitones": max(midi_values) - min(midi_values),
    }


def build_musical_interpretation(events, key_signatures=None):
    pitch_classes = Counter()
    hands = Counter()
    dynamics = Counter()
    accidentals = Counter()

    for event in events:
        note = event.get("note") or ""
        accidental = event.get("accidental") or ""
        if note:
            pitch_classes[f"{note}{accidental}"] += 1
        hands[event.get("hand") or "unknown"] += 1
        dynamic = event.get("dynamic")
        if dynamic:
            dynamics[dynamic] += 1
        if accidental:
            accidentals[accidental] += 1

    return {
        "pitch_range": _pitch_range(events),
        "pitch_class_counts": _counter_dict(pitch_classes),
        "hand_distribution": _counter_dict(hands),
        "dynamic_distribution": _counter_dict(dynamics),
        "accidental_distribution": _counter_dict(accidentals),
        "duration_profile": _duration_profile(events),
        "key_signatures": list(key_signatures or []),
    }


def build_timing_interpretation(events):
    starts = Counter(int(_safe_number(event.get("start_ms"))) for event in events)
    sorted_starts = sorted(starts)
    gaps = [
        max(0, sorted_starts[index + 1] - sorted_starts[index])
        for index in range(len(sorted_starts) - 1)
    ]
    dense_moments = [
        {"start_ms": start, "event_count": count}
        for start, count in starts.items()
        if count >= 6
    ]
    dense_moments.sort(key=lambda item: (-item["event_count"], item["start_ms"]))
    return {
        "column_count": len(starts),
        "max_polyphony": max(starts.values(), default=0),
        "dense_moment_count": len(dense_moments),
        "dense_moments": dense_moments[:12],
        "average_gap_ms": round(sum(gaps) / len(gaps), 2) if gaps else 0,
        "min_gap_ms": min(gaps) if gaps else 0,
        "max_gap_ms": max(gaps) if gaps else 0,
    }


def build_quality_profile(events, review, timing, duration_ms):
    event_count = len(events)
    duration_seconds = max(0.001, _safe_number(duration_ms) / 1000)
    average_confidence = review.get("average_confidence")
    if average_confidence is None:
        confidence_values = [
            _safe_number(event.get("confidence"))
            for event in events
            if event.get("confidence") is not None
        ]
        average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
    average_confidence = _safe_number(average_confidence)

    low_count = int(review.get("low_confidence_count", 0) or 0)
    review_count = int(review.get("review_confidence_count", 0) or 0)
    invalid_duration_count = int(review.get("invalid_duration_count", 0) or 0)
    left_count = int(review.get("left_hand_count", 0) or 0)
    right_count = int(review.get("right_hand_count", 0) or 0)
    hand_total = max(1, left_count + right_count)
    balanced_hand_pct = round((min(left_count, right_count) / hand_total) * 100, 1)
    review_load_pct = round(((low_count + review_count) / max(1, event_count)) * 100, 1)
    low_confidence_pct = round((low_count / max(1, event_count)) * 100, 1)
    density = round(event_count / duration_seconds, 2)
    average_gap_ms = _safe_number(timing.get("average_gap_ms"))
    max_gap_ms = _safe_number(timing.get("max_gap_ms"))

    score = average_confidence * 100
    score -= review_load_pct * 0.45
    score -= min(18, invalid_duration_count * 4)
    if event_count == 0:
        score = 0
    elif max_gap_ms > 1800:
        score -= 6
    score = int(max(0, min(100, round(score))))

    if event_count == 0:
        status = "empty"
    elif score >= 88 and review_load_pct <= 4:
        status = "strong"
    elif score >= 72 and review_load_pct <= 12:
        status = "ready"
    else:
        status = "review"

    action_items = []
    if event_count == 0:
        action_items.append("No playable notes were exported. Check model setup and source quality.")
    if review_load_pct > 12:
        action_items.append("Review low-confidence detections before sharing the exported files.")
    if max_gap_ms > 1800:
        action_items.append("Check large timeline gaps; they can indicate missed rests, barlines, or system transitions.")
    if invalid_duration_count:
        action_items.append("Some events have invalid durations and should be inspected.")
    if balanced_hand_pct < 18 and hand_total >= 20:
        action_items.append("Hand distribution is highly skewed. If this is a piano score, review staff grouping.")
    recovery = review.get("staff_crop_recovery") or {}
    if recovery.get("recovered_count", 0):
        action_items.append("Staff-crop recovery added notes. Open detailed annotations to confirm recovered detections.")
    if not action_items:
        action_items.append("No immediate scientific warnings were found.")

    return {
        "quality_score": score,
        "status": status,
        "review_load_pct": review_load_pct,
        "low_confidence_pct": low_confidence_pct,
        "note_density_per_second": density,
        "balanced_hand_pct": balanced_hand_pct,
        "max_polyphony": int(timing.get("max_polyphony", 0) or 0),
        "average_gap_ms": round(average_gap_ms, 2),
        "max_gap_ms": int(max_gap_ms),
        "action_items": action_items,
    }


def build_scientific_payload(
    *,
    score_events,
    review,
    validation,
    output_options,
    source_files,
    bpm,
    page_count,
    duration_ms,
    key_signatures=None,
):
    events = [_event_dict(event) for event in (score_events or [])]
    validation_payload = validation or {}
    if hasattr(validation_payload, "to_dict"):
        validation_payload = validation_payload.to_dict()
    timing_interpretation = build_timing_interpretation(events)
    review_payload = dict(review or {})

    payload = {
        "format_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_files": [str(path) for path in source_files],
            "bpm": int(bpm),
            "page_count": int(page_count),
            "duration_seconds": round(max(0, int(duration_ms)) / 1000, 3),
            "output_options": dict(output_options or {}),
        },
        "recognition": {
            "event_count": len(events),
            "review": review_payload,
            "confidence_histogram": _confidence_histogram(events),
        },
        "musical_interpretation": build_musical_interpretation(events, key_signatures),
        "timing_interpretation": timing_interpretation,
        "quality_profile": build_quality_profile(
            events,
            review_payload,
            timing_interpretation,
            duration_ms,
        ),
        "validation": validation_payload,
        "reliability_analysis": {
            "recommended_chart": "confidence_distribution",
            "message": (
                "Without ground-truth labels, confidence and musical-distribution "
                "charts are more useful than a confusion matrix. Use them to find "
                "where the score should be reviewed before exporting or comparing "
                "against a future baseline."
            ),
        },
        "events": events,
    }
    return payload


def _bar_chart_svg(items, title, color="#40d6ff"):
    items = list(items.items())
    if not items:
        items = [("none", 0)]
    max_value = max(1, max(value for _label, value in items))
    row_height = 34
    width = 760
    height = 58 + row_height * len(items)
    rows = []
    for index, (label, value) in enumerate(items):
        y = 42 + index * row_height
        bar_width = int((width - 210) * (value / max_value))
        rows.append(
            f'<text x="20" y="{y + 18}" class="chart-label">{html.escape(str(label))}</text>'
            f'<rect x="160" y="{y}" width="{bar_width}" height="22" rx="7" class="chart-bar"/>'
            f'<text x="{172 + bar_width}" y="{y + 17}" class="chart-value">{int(value)}</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">'
        f'<style>.chart-title{{font:700 18px Inter,Arial;fill:#e9f7ff}}'
        f'.chart-label,.chart-value{{font:600 13px Inter,Arial;fill:#b9d8ea}}'
        f'.chart-bar{{fill:{color};filter:drop-shadow(0 0 8px rgba(64,214,255,.42))}}</style>'
        f'<text x="20" y="24" class="chart-title">{html.escape(title)}</text>'
        + "".join(rows)
        + "</svg>"
    )


def _metric(label, value):
    return (
        '<div class="metric">'
        f'<span>{html.escape(str(label))}</span>'
        f'<strong>{html.escape(str(value))}</strong>'
        "</div>"
    )


def render_scientific_html(payload):
    review = payload.get("recognition", {}).get("review", {})
    interpretation = payload.get("musical_interpretation", {})
    validation = payload.get("validation") or {}
    issues = validation.get("issues", []) if isinstance(validation, dict) else []
    reliability = payload.get("reliability_analysis", {})
    quality = payload.get("quality_profile", {})
    metrics = "".join(
        (
            _metric("Events", review.get("event_count", payload.get("recognition", {}).get("event_count", 0))),
            _metric("Pages", review.get("page_count", "-")),
            _metric("Duration", f'{review.get("duration_seconds", 0)}s'),
            _metric("Avg. confidence", review.get("average_confidence", "N/A")),
            _metric("Low confidence", review.get("low_confidence_count", 0)),
            _metric("Accidentals", review.get("accidental_count", 0)),
        )
    )
    key_rows = "".join(
        "<li>"
        f'Page {item.get("page", "-")}, staff {item.get("staff", "-")}: '
        f'{html.escape(str(item.get("key_signature", {})))}'
        "</li>"
        for item in interpretation.get("key_signatures", [])
    ) or "<li>No key-signature accidentals were registered.</li>"
    issue_rows = "".join(
        f'<li><strong>{html.escape(issue.get("severity", "info"))}</strong>: '
        f'{html.escape(issue.get("message", ""))}</li>'
        for issue in issues
    ) or "<li>No validation warnings were reported.</li>"
    action_rows = "".join(
        f"<li>{html.escape(str(item))}</li>"
        for item in quality.get("action_items", [])
    ) or "<li>No immediate scientific warnings were found.</li>"
    quality_metrics = "".join(
        (
            _metric("Quality score", quality.get("quality_score", "-")),
            _metric("Review load", f'{quality.get("review_load_pct", 0)}%'),
            _metric("Note density", f'{quality.get("note_density_per_second", 0)}/s'),
            _metric("Hand balance", f'{quality.get("balanced_hand_pct", 0)}%'),
        )
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PyClef Scientific Report</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #07111f;
      --panel: rgba(17, 27, 45, .82);
      --panel-strong: rgba(28, 40, 62, .92);
      --text: #f6fbff;
      --muted: #b9d8ea;
      --cyan: #40d6ff;
      --line: rgba(117, 226, 255, .22);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 18% 10%, rgba(64, 214, 255, .19), transparent 28%),
        radial-gradient(circle at 84% 24%, rgba(34, 255, 178, .10), transparent 25%),
        var(--bg);
      color: var(--text);
    }}
    main {{ width: min(1120px, calc(100% - 36px)); margin: 34px auto 56px; }}
    header, section {{
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: 0 24px 70px rgba(0, 0, 0, .34);
      backdrop-filter: blur(18px);
      padding: 28px;
      margin-bottom: 18px;
    }}
    .eyebrow {{ color: var(--cyan); font-weight: 800; letter-spacing: .12em; text-transform: uppercase; font-size: 12px; }}
    h1 {{ margin: 10px 0 8px; font-size: clamp(34px, 7vw, 76px); line-height: .94; }}
    h2 {{ margin: 0 0 18px; font-size: 24px; }}
    p {{ color: var(--muted); line-height: 1.65; max-width: 820px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin-top: 24px; }}
    .metric {{
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 18px;
      background: var(--panel-strong);
      padding: 14px;
      min-height: 78px;
    }}
    .metric span {{ color: var(--muted); display: block; font-size: 12px; }}
    .metric strong {{ display: block; margin-top: 8px; font-size: 22px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .chart {{ border: 1px solid rgba(255,255,255,.10); border-radius: 20px; background: rgba(6, 15, 27, .42); padding: 8px; overflow: hidden; }}
    ul {{ color: var(--muted); line-height: 1.7; }}
    .matrix {{
      border: 1px dashed rgba(64, 214, 255, .48);
      border-radius: 20px;
      padding: 18px;
      color: var(--muted);
      background: rgba(64, 214, 255, .07);
    }}
    code {{
      display: inline-block;
      border: 1px solid rgba(255,255,255,.13);
      border-radius: 12px;
      padding: 6px 9px;
      color: var(--text);
      background: rgba(255,255,255,.06);
    }}
    @media (max-width: 860px) {{
      .metrics, .grid {{ grid-template-columns: 1fr; }}
      header, section {{ padding: 22px; border-radius: 22px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">PyClef scientific mode</div>
      <h1>Recognition report</h1>
      <p>Generated from PyClef predictions, validation checks, and musical interpretation metadata.</p>
      <div class="metrics">{metrics}</div>
    </header>
    <section>
      <h2>Quality overview</h2>
      <div class="metrics">{quality_metrics}</div>
      <p>Status: <code>{html.escape(str(quality.get("status", "-")))}</code></p>
      <ul>{action_rows}</ul>
    </section>
    <section>
      <h2>Recognition charts</h2>
      <div class="grid">
        <div class="chart">{_bar_chart_svg(payload.get("recognition", {}).get("confidence_histogram", {}), "Confidence buckets")}</div>
        <div class="chart">{_bar_chart_svg(interpretation.get("hand_distribution", {}), "Hand distribution", "#65f0b7")}</div>
        <div class="chart">{_bar_chart_svg(interpretation.get("pitch_class_counts", {}), "Pitch classes", "#73e2ff")}</div>
        <div class="chart">{_bar_chart_svg(interpretation.get("duration_profile", {}), "Duration profile", "#9fdcff")}</div>
      </div>
    </section>
    <section>
      <h2>Musical interpretation</h2>
      <p>Pitch range: <code>{html.escape(str(interpretation.get("pitch_range", {})))}</code></p>
      <p>Detected key-signature context:</p>
      <ul>{key_rows}</ul>
    </section>
    <section>
      <h2>Reliability analysis</h2>
      <div class="matrix">
        <strong>Recommended chart:</strong> {html.escape(reliability.get("recommended_chart", "confidence_distribution"))}<br>
        {html.escape(reliability.get("message", ""))}
      </div>
    </section>
    <section>
      <h2>Validation</h2>
      <ul>{issue_rows}</ul>
    </section>
  </main>
</body>
</html>"""


def write_scientific_report(output_dir, output_stem, payload):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_stem}_scientific_report.json"
    html_path = output_dir / f"{output_stem}_scientific_report.html"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    html_path.write_text(render_scientific_html(payload), encoding="utf-8")
    return html_path, json_path
