"""Central configuration for the dress-3d-reconstruction pipeline.

Keeping every path and camera constant in one place means the rest of the
codebase never hard-codes "/content/..." style paths again.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# The values below (1.9 / 40.0 / 1.2040) were reverse-engineered from
# TripoSR's own rendering camera and confirmed against real projections
# during experimentation. Change them here only if TripoSR's camera changes.


@dataclass
class CameraConfig:
    distance: float = 1.9
    fovy_deg: float = 40.0
    scale: float = 1.2040


@dataclass
class PipelineConfig:
    project_root: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[2]
    )
    triposr_dir: Path = None
    venv_python: Path = None
    input_dir: Path = None
    output_dir: Path = None

    texture_size: int = 2048
    projection_size: int = 1536

    camera: CameraConfig = field(default_factory=CameraConfig)

    def __post_init__(self) -> None:
        self.project_root = Path(self.project_root)
        if self.triposr_dir is None:
            self.triposr_dir = self.project_root / "triposr"
        if self.venv_python is None:
            self.venv_python = Path("/content/triposr_env/bin/python")
        if self.input_dir is None:
            self.input_dir = self.project_root / "input"
        if self.output_dir is None:
            self.output_dir = self.project_root / "output"

        self.triposr_dir = Path(self.triposr_dir)
        self.venv_python = Path(self.venv_python)
        self.input_dir = Path(self.input_dir)
        self.output_dir = Path(self.output_dir)
