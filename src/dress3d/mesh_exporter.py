"""Attaches a baked texture to a mesh and exports one self-contained 3D file."""
from __future__ import annotations

from pathlib import Path

import trimesh
from PIL import Image


class MeshExporter:
    @staticmethod
    def export_textured_mesh(mesh_path: Path, texture_path: Path, output_path: Path) -> Path:
        """Combines geometry + baked texture into a single .glb/.obj file."""
        mesh = trimesh.load(mesh_path, force="mesh", process=False)
        texture_image = Image.open(texture_path)

        material = trimesh.visual.material.SimpleMaterial(image=texture_image)
        mesh.visual = trimesh.visual.TextureVisuals(
            uv=mesh.visual.uv, image=texture_image, material=material
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mesh.export(output_path)
        return output_path
