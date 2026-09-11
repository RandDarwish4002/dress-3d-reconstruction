"""End-to-end orchestration: front photo + back photo -> one textured 3D garment."""
from __future__ import annotations

from pathlib import Path

from .config import PipelineConfig
from .mesh_exporter import MeshExporter
from .preprocessing import ImagePreprocessor
from .reconstruction import TripoSRReconstructor
from .texture_baker import TextureBaker


class DressReconstructionPipeline:
    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig()
        self.preprocessor = ImagePreprocessor(canvas_size=self.config.projection_size)
        self.reconstructor = TripoSRReconstructor(
            self.config.triposr_dir, self.config.venv_python
        )
        self.baker = TextureBaker(
            camera_distance=self.config.camera.distance,
            fovy_deg=self.config.camera.fovy_deg,
            camera_scale=self.config.camera.scale,
            texture_size=self.config.texture_size,
        )

    def run(self, front_path: Path, back_path: Path, name: str = "garment") -> Path:
        front_path, back_path = Path(front_path), Path(back_path)
        out_dir = self.config.output_dir / name
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Base geometry from the front photo (TripoSR).
        mesh_path = self.reconstructor.reconstruct(front_path, out_dir / "reconstruction")

        # 2. Normalise both photos onto matching square canvases so the
        #    shared camera model in the baker lines up with both of them.
        front_img = self.preprocessor.prepare(front_path)
        back_img = self.preprocessor.prepare(back_path)

        # 3. Bake both views into a single UV texture.
        texture_path = self.baker.bake(mesh_path, front_img, back_img, out_dir / "texture.png")

        # 4. Export one textured mesh: this is the final single 3D piece.
        final_path = MeshExporter.export_textured_mesh(
            mesh_path, texture_path, out_dir / f"{name}.glb"
        )
        return final_path
