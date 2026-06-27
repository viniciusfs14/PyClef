from dataclasses import dataclass

from .models import OutputOptions


@dataclass(frozen=True)
class PipelineStage:
    key: str
    title: str


PIPELINE_STAGES = (
    PipelineStage("inputs", "Input preparation"),
    PipelineStage("detection", "Symbol detection"),
    PipelineStage("interpretation", "Musical interpretation"),
    PipelineStage("rendering", "Output rendering"),
    PipelineStage("validation", "Output validation"),
)


class ScoreProcessingPipeline:
    """Small public facade around the PyClef processing flow.

    The heavy OMR implementation still lives in engine.py, but this facade gives
    the application a stable orchestration surface for future stage extraction.
    """

    def __init__(self, bpm=72, output_options=None, progress_callback=None):
        self.bpm = bpm
        self.output_options = OutputOptions.from_mapping(output_options)
        self.progress_callback = progress_callback

    def run(self, file_list):
        from .engine import process_score_files

        return process_score_files(
            file_list=file_list,
            bpm=self.bpm,
            progress_callback=self.progress_callback,
            output_options=self.output_options.to_dict(),
        )


def process_score_pipeline(file_list, bpm=72, output_options=None, progress_callback=None):
    return ScoreProcessingPipeline(
        bpm=bpm,
        output_options=output_options,
        progress_callback=progress_callback,
    ).run(file_list)
