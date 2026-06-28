from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OutputOptions:
    annotations: bool = True
    audio: bool = False
    midi: bool = False
    video: bool = False
    annotation_mode: str = "clean"
    timbre: str = "piano"
    video_mode: str = "score"
    video_resolution: str = "720p"
    language: str = "en"
    include_events: bool = False
    validate_outputs: bool = True
    scientific_report: bool = False
    preprocess: bool = True
    quality_gate: bool = True
    staff_crop_recovery: bool = False

    @classmethod
    def from_mapping(cls, values=None):
        values = dict(values or {})
        options = cls(
            annotations=bool(values.get("annotations", True)),
            audio=bool(values.get("audio", False)),
            midi=bool(values.get("midi", False)),
            video=bool(values.get("video", False)),
            annotation_mode=values.get("annotation_mode", "clean"),
            timbre=values.get("timbre", "piano"),
            video_mode=values.get("video_mode", "score"),
            video_resolution=values.get("video_resolution", "720p"),
            language=values.get("language", "en"),
            include_events=bool(values.get("include_events", False)),
            validate_outputs=bool(values.get("validate_outputs", True)),
            scientific_report=bool(values.get("scientific_report", False)),
            preprocess=bool(values.get("preprocess", True)),
            quality_gate=bool(values.get("quality_gate", True)),
            staff_crop_recovery=bool(values.get("staff_crop_recovery", False)),
        )
        return options.normalized()

    def normalized(self):
        annotation_mode = self.annotation_mode if self.annotation_mode in {"clean", "detailed"} else "clean"
        video_mode = self.video_mode if self.video_mode in {"score", "piano_roll", "showcase"} else "score"
        video_resolution = self.video_resolution if self.video_resolution in {"720p", "1080p"} else "720p"
        language = self.language if self.language in {"en", "pt"} else "en"
        return OutputOptions(
            annotations=self.annotations,
            audio=self.audio,
            midi=self.midi,
            video=self.video,
            annotation_mode=annotation_mode,
            timbre=self.timbre,
            video_mode=video_mode,
            video_resolution=video_resolution,
            language=language,
            include_events=self.include_events,
            validate_outputs=self.validate_outputs,
            scientific_report=self.scientific_report,
            preprocess=self.preprocess,
            quality_gate=self.quality_gate,
            staff_crop_recovery=self.staff_crop_recovery,
        )

    def to_dict(self):
        return asdict(self)

    def wants_any_file(self):
        return self.annotations or self.audio or self.midi or self.video or self.scientific_report


@dataclass(frozen=True)
class ScoreEvent:
    start_ms: int
    duration_ms: int
    midi_note: int
    label: str
    note: str
    octave: int
    accidental: str = ""
    page_index: int = 0
    staff_index: int = 0
    hand: str = "right"
    x: int = 0
    y: int = 0
    confidence: float | None = None
    dynamic: str | None = None
    velocity: int | float | None = None

    @property
    def end_ms(self):
        return self.start_ms + self.duration_ms

    def to_dict(self):
        payload = asdict(self)
        payload["end_ms"] = self.end_ms
        return payload


@dataclass(frozen=True)
class DiagnosticCheck:
    key: str
    title: str
    status: str
    message: str
    path: str | None = None

    @property
    def ok(self):
        return self.status == "ok"

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    message: str
    path: str | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ValidationReport:
    ok: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add(self, severity, message, path=None):
        self.issues.append(ValidationIssue(severity, message, str(path) if path else None))
        if severity == "error":
            self.ok = False

    def to_dict(self):
        return {
            "ok": self.ok,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
        }


@dataclass
class ProcessingResult:
    output_dir: Path
    annotations: list[str] = field(default_factory=list)
    audio: str | None = None
    midi: str | None = None
    video: str | None = None
    scientific_report: str | None = None
    event_count: int = 0
    review: dict = field(default_factory=dict)
    validation: ValidationReport | dict | None = None
    events: list[ScoreEvent] = field(default_factory=list)

    def to_dict(self, include_events=False):
        payload = {"output_dir": str(self.output_dir), "event_count": self.event_count}
        if self.annotations:
            payload["annotations"] = self.annotations
        if self.audio:
            payload["audio"] = self.audio
        if self.midi:
            payload["midi"] = self.midi
        if self.video:
            payload["video"] = self.video
        if self.scientific_report:
            payload["scientific_report"] = self.scientific_report
        if self.review:
            payload["review"] = self.review
        if self.validation is not None:
            payload["validation"] = (
                self.validation.to_dict()
                if hasattr(self.validation, "to_dict")
                else self.validation
            )
        if include_events:
            payload["events"] = [event.to_dict() for event in self.events]
        return payload
