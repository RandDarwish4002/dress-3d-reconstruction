"""Wraps the TripoSR CLI to turn a single front-view photo into a base 3D mesh."""
from __future__ import annotations

import subprocess
from pathlib import Path


class TripoSRReconstructor:
    """Runs Stability AI's TripoSR (https://github.com/VAST-AI-Research/TripoSR)
    as a subprocess to get an initial single-view mesh, which the rest of the
    pipeline then re-textures using both the front and back photos.
    """

    def __init__(self, triposr_dir: Path, python_executable: Path):
        self.triposr_dir = Path(triposr_dir)
        self.python_executable = Path(python_executable)
        self.run_script = self.triposr_dir / "run.py"

    def reconstruct(self, image_path: Path, output_dir: Path) -> Path:
        """Runs TripoSR on `image_path`; returns the path to the generated mesh.obj."""
        if not self.run_script.exists():
            raise FileNotFoundError(
                f"TripoSR run.py not found at {self.run_script}. "
                "Run scripts/setup_env.sh first to clone and set it up."
            )

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(self.python_executable),
            "run.py",
            str(image_path),
            "--output-dir", str(output_dir),
        ]

        result = subprocess.run(cmd, cwd=self.triposr_dir, text=True)
        if result.returncode != 0:
            raise RuntimeError("TripoSR reconstruction failed (see console output above).")

        mesh_path = output_dir / "0" / "mesh.obj"
        if not mesh_path.exists():
            raise FileNotFoundError(f"Expected mesh not found at {mesh_path}")
        return mesh_path
