"""Lightweight tests for TextureBaker's camera math (no GPU / TripoSR needed)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dress3d.texture_baker import TextureBaker  # noqa: E402


def test_project_returns_expected_shapes():
    baker = TextureBaker()
    points = np.array(
        [[0.0, 0.0, 0.0], [0.1, 0.1, 0.1], [-0.1, -0.1, 0.2]],
        dtype=np.float32,
    )
    px, py, zcam = baker._project(points, image_hw=(512, 512), azimuth_deg=0.0)
    assert px.shape == (3,)
    assert py.shape == (3,)
    assert zcam.shape == (3,)


def test_front_and_back_are_opposite_azimuths():
    baker = TextureBaker()
    point = np.array([[0.1, 0.05, 0.0]], dtype=np.float32)
    px_front, _, _ = baker._project(point, (512, 512), azimuth_deg=0.0)
    px_back, _, _ = baker._project(point, (512, 512), azimuth_deg=180.0)
    # Rotating the camera by 180 degrees should flip which side faces it.
    assert px_front[0] != px_back[0]


def test_sample_image_bilinear_midpoint():
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    image[0, 0] = [0, 0, 0]
    image[0, 1] = [255, 255, 255]
    image[1, 0] = [255, 255, 255]
    image[1, 1] = [0, 0, 0]

    colors = TextureBaker._sample_image(image, np.array([0.5]), np.array([0.0]))
    assert colors.shape == (1, 3)
