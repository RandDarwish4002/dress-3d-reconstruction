"""Bakes front & back garment photos onto a single UV texture map.

This is what turns two separate photos into one seamless 3D piece: each face
of the mesh is tested against the camera direction for the front (azimuth 0)
and back (azimuth 180) views, and whichever view actually sees that face
(and is more front-on / more confident) wins the pixels in the shared texture.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh
from PIL import Image


class TextureBaker:
    def __init__(
        self,
        camera_distance: float = 1.9,
        fovy_deg: float = 40.0,
        camera_scale: float = 1.2040,
        texture_size: int = 2048,
    ):
        self.camera_distance = camera_distance
        self.fovy_deg = fovy_deg
        self.camera_scale = camera_scale
        self.texture_size = texture_size

    # ---- camera model -------------------------------------------------

    def _project(self, points: np.ndarray, image_hw: tuple[int, int], azimuth_deg: float):
        """Projects 3D points into the pixel space of a camera at `azimuth_deg`."""
        H, W = image_hw
        az = np.radians(azimuth_deg)
        c, s = np.cos(az), np.sin(az)

        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        xr = c * x - s * y
        yr = s * x + c * y

        depth, horizontal, vertical = xr, yr, z
        zcam = self.camera_distance - depth

        focal = (H / 2.0) / np.tan(np.radians(self.fovy_deg) / 2.0) * self.camera_scale

        px = focal * horizontal / zcam + W / 2.0
        py = -focal * vertical / zcam + H / 2.0
        return px, py, zcam

    @staticmethod
    def _sample_image(image: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Bilinear sampling of `image` at fractional pixel coordinates (x, y)."""
        H, W = image.shape[:2]
        x = np.clip(x, 0, W - 1.001)
        y = np.clip(y, 0, H - 1.001)

        x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
        x1, y1 = np.minimum(x0 + 1, W - 1), np.minimum(y0 + 1, H - 1)
        dx, dy = x - x0, y - y0

        c00 = image[y0, x0].astype(np.float32)
        c10 = image[y0, x1].astype(np.float32)
        c01 = image[y1, x0].astype(np.float32)
        c11 = image[y1, x1].astype(np.float32)

        c0 = c00 * (1 - dx[:, None]) + c10 * dx[:, None]
        c1 = c01 * (1 - dx[:, None]) + c11 * dx[:, None]
        return (c0 * (1 - dy[:, None]) + c1 * dy[:, None]).astype(np.uint8)

    # ---- per-face rasterisation into UV space --------------------------

    def _rasterize_face(
        self, face_id, V, F, UV, image, azimuth_deg, view_name, texture, confidence
    ) -> int:
        ids = F[face_id]
        p3 = V[ids]

        a, b = p3[1] - p3[0], p3[2] - p3[0]
        normal = np.cross(a, b)
        n = np.linalg.norm(normal)
        if n < 1e-8:
            return 0
        normal /= n

        direction = np.array(
            [np.cos(np.radians(azimuth_deg)), np.sin(np.radians(azimuth_deg)), 0.0]
        )
        facing = np.dot(normal, direction)

        if view_name == "FRONT" and facing <= 0:
            return 0
        if view_name == "BACK" and facing >= 0:
            return 0

        px, py, depth = self._project(p3, image.shape[:2], azimuth_deg)

        size = self.texture_size
        uv = UV[ids]
        ux = uv[:, 0] * (size - 1)
        uy = (1.0 - uv[:, 1]) * (size - 1)

        minx, maxx = max(0, int(np.floor(ux.min()))), min(size - 1, int(np.ceil(ux.max())))
        miny, maxy = max(0, int(np.floor(uy.min()))), min(size - 1, int(np.ceil(uy.max())))
        if minx >= maxx or miny >= maxy:
            return 0

        U, VV = np.meshgrid(np.arange(minx, maxx + 1), np.arange(miny, maxy + 1))
        P = np.stack([U, VV], axis=-1).astype(np.float32)

        A = np.array([ux[0], uy[0]], dtype=np.float32)
        B = np.array([ux[1], uy[1]], dtype=np.float32)
        C = np.array([ux[2], uy[2]], dtype=np.float32)

        v0, v1, v2 = B - A, C - A, P - A
        denom = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(denom) < 1e-8:
            return 0

        w1 = (v2[..., 0] * v1[1] - v1[0] * v2[..., 1]) / denom
        w2 = (v0[0] * v2[..., 1] - v2[..., 0] * v0[1]) / denom
        w0 = 1.0 - w1 - w2
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not np.any(inside):
            return 0

        ix = w0 * px[0] + w1 * px[1] + w2 * px[2]
        iy = w0 * py[0] + w1 * py[1] + w2 * py[2]

        tx, ty = U[inside], VV[inside]
        ix, iy = ix[inside], iy[inside]

        imgH, imgW = image.shape[:2]
        valid = (ix >= 0) & (ix < imgW) & (iy >= 0) & (iy < imgH)
        if not np.any(valid):
            return 0

        tx, ty, ix, iy = tx[valid], ty[valid], ix[valid], iy[valid]
        colors = self._sample_image(image, ix, iy)

        avg_depth = float(np.mean(depth))
        conf = 1.0 / (1.0 + max(avg_depth, 0.0))

        old = confidence[ty, tx]
        better = conf > old
        if np.any(better):
            yy, xx = ty[better], tx[better]
            texture[yy, xx] = colors[better]
            confidence[yy, xx] = conf

        return int(len(tx))

    # ---- public entry point --------------------------------------------

    def bake(
        self,
        mesh_path: Path,
        front_image: np.ndarray,
        back_image: np.ndarray,
        output_path: Path,
    ) -> Path:
        """Bakes `front_image` (azimuth 0) and `back_image` (azimuth 180) onto the
        mesh's existing UV layout and writes the result as a single PNG texture.
        """
        mesh = trimesh.load(mesh_path, force="mesh")
        V = np.asarray(mesh.vertices, dtype=np.float32)
        F = np.asarray(mesh.faces, dtype=np.int32)

        if not hasattr(mesh.visual, "uv") or mesh.visual.uv is None:
            raise RuntimeError("Mesh has no UV coordinates; cannot bake a texture onto it.")
        UV = np.asarray(mesh.visual.uv, dtype=np.float32)

        size = self.texture_size
        texture = np.zeros((size, size, 3), dtype=np.uint8)
        confidence = np.zeros((size, size), dtype=np.float32)

        for i in range(len(F)):
            self._rasterize_face(i, V, F, UV, front_image, 0.0, "FRONT", texture, confidence)
        for i in range(len(F)):
            self._rasterize_face(i, V, F, UV, back_image, 180.0, "BACK", texture, confidence)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(texture).save(output_path)
        return output_path
