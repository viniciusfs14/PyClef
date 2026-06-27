from pyclef_app import (
    MainClef,
    Pyclef,
    ScoreProcessingPipeline,
    collect_environment_diagnostics,
    process_score_files,
    process_score_pipeline,
    validate_processing_result,
)

__all__ = [
    "Pyclef",
    "MainClef",
    "process_score_files",
    "process_score_pipeline",
    "ScoreProcessingPipeline",
    "collect_environment_diagnostics",
    "validate_processing_result",
]

if __name__ == "__main__":
    Pyclef()
