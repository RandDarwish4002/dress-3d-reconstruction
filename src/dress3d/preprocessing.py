"""Prepares raw garment photos (front/back) before reconstruction and texture baking."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


class ImagePreprocessor:
    """Removes the background from a garment photo and centres it on a square canvas.

    A shared square canvas size is what lets the front and back photos line up
    with the same camera model later, in :class:`dress3d.texture_baker.TextureBaker`.
    """

    def __init__(self, canvas_size: int = 1536):
        self.canvas_size = canvas_size

    def remove_background(self, image_path: Path) -> Image.Image:
        """Returns an RGBA image with the background removed."""
        from rembg import remove  # imported lazily: only needed at runtime

        with Image.open(image_path) as img:
            return remove(img.convert("RGB"))

    def to_square_canvas(self, image: np.ndarray) -> np.ndarray:
        """Fits `image` inside a centred `canvas_size x canvas_size` black canvas."""
        import cv2

        h, w = image.shape[:2]
        scale = self.canvas_size / max(h, w)
        nw, nh = int(round(w * scale)), int(round(h * scale))

        resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_AREA)

        canvas = np.zeros((self.canvas_size, self.canvas_size, 3), dtype=np.uint8)
        x, y = (self.canvas_size - nw) // 2, (self.canvas_size - nh) // 2
        canvas[y:y + nh, x:x + nw] = resized
        return canvas

    def prepare(self, image_path: Path, remove_bg: bool = True) -> np.ndarray:
        """Full prep for one photo: optional background removal, then centring."""
        if remove_bg:
            rgba = self.remove_background(image_path)
            rgb = np.array(rgba.convert("RGB"))
        else:
            rgb = np.array(Image.open(image_path).convert("RGB"))
        return self.to_square_canvas(rgb)
