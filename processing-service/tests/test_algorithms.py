"""
Unit tests for DW-LCM and MW-IPI detection algorithms.
No external services required — pure NumPy/OpenCV.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.dwlcm import compute_local_contrast, detect_targets_dwlcm
from algorithms.mwipi import detect_targets_mwipi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uniform_background(h: int = 100, w: int = 100, level: int = 80) -> np.ndarray:
    return np.full((h, w), level, dtype=np.uint8)


def _image_with_bright_point(h: int = 100, w: int = 100, row: int = 50, col: int = 50) -> np.ndarray:
    img = _uniform_background(h, w, 80)
    img[row, col] = 255
    img[row, col + 1] = 240
    img[row + 1, col] = 230
    return img


def _random_image(h: int = 100, w: int = 100, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(40, 110, size=(h, w), dtype=np.uint8)


# ---------------------------------------------------------------------------
# DW-LCM tests
# ---------------------------------------------------------------------------

class TestComputeLocalContrast:
    def test_output_shape_matches_input(self):
        img = _random_image()
        lc = compute_local_contrast(img, inner_size=3, outer_size=9)
        assert lc.shape == img.shape

    def test_output_is_float32(self):
        img = _random_image()
        lc = compute_local_contrast(img)
        assert lc.dtype == np.float32

    def test_uniform_image_has_near_zero_contrast(self):
        img = _uniform_background()
        lc = compute_local_contrast(img, inner_size=3, outer_size=9)
        # Uniform background should produce near-zero LC
        assert float(np.mean(lc)) < 0.05

    def test_bright_target_increases_contrast(self):
        img_flat = _uniform_background()
        img_target = _image_with_bright_point()
        lc_flat = compute_local_contrast(img_flat)
        lc_target = compute_local_contrast(img_target)
        assert float(np.max(lc_target)) > float(np.max(lc_flat))


class TestDetectTargetsDWLCM:
    def test_returns_tuple_of_image_and_list(self):
        img = _random_image()
        processed, targets = detect_targets_dwlcm(img)
        assert processed is not None
        assert isinstance(targets, list)

    def test_processed_image_is_bgr(self):
        img = _random_image()
        processed, _ = detect_targets_dwlcm(img)
        assert processed.ndim == 3
        assert processed.shape[2] == 3

    def test_processed_image_same_spatial_size(self):
        img = _random_image(64, 64)
        processed, _ = detect_targets_dwlcm(img)
        assert processed.shape[:2] == (64, 64)

    def test_detects_bright_point_target(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        img[50, 50] = 255
        _, targets = detect_targets_dwlcm(img, threshold_factor=2.0)
        assert len(targets) > 0

    def test_target_dict_has_required_keys(self):
        img = _image_with_bright_point()
        _, targets = detect_targets_dwlcm(img, threshold_factor=2.0)
        for t in targets:
            assert {"x", "y", "width", "height", "area", "confidence"}.issubset(t.keys())

    def test_no_false_alarms_on_uniform_image(self):
        img = _uniform_background()
        _, targets = detect_targets_dwlcm(img)
        assert len(targets) == 0


# ---------------------------------------------------------------------------
# MW-IPI tests
# ---------------------------------------------------------------------------

class TestDetectTargetsMWIPI:
    def test_returns_tuple(self):
        img = _random_image()
        processed, targets = detect_targets_mwipi(img, scales=[20, 30])
        assert processed is not None
        assert isinstance(targets, list)

    def test_processed_image_is_bgr(self):
        img = _random_image()
        processed, _ = detect_targets_mwipi(img, scales=[20, 30])
        assert processed.ndim == 3
        assert processed.shape[2] == 3

    def test_processed_image_same_spatial_size(self):
        img = _random_image(64, 64)
        processed, _ = detect_targets_mwipi(img, scales=[15, 25])
        assert processed.shape[:2] == (64, 64)

    def test_target_dict_has_required_keys(self):
        img = _image_with_bright_point()
        _, targets = detect_targets_mwipi(img, scales=[20, 30], threshold_factor=1.5)
        for t in targets:
            assert {"x", "y", "width", "height", "area", "confidence"}.issubset(t.keys())

    def test_handles_patch_larger_than_image_gracefully(self):
        """When all scales exceed image dimensions, the result should be empty targets."""
        img = np.zeros((20, 20), dtype=np.uint8)
        # scales larger than image → _patch_image_model returns zeros
        processed, targets = detect_targets_mwipi(img, scales=[100, 200])
        assert isinstance(targets, list)

    def test_uniform_image_returns_no_targets(self):
        img = _uniform_background()
        _, targets = detect_targets_mwipi(img, scales=[20, 30])
        assert len(targets) == 0
