"""
Dual-Window Local Contrast Method (DW-LCM) for infrared small target detection.

Reference:
    Chen, C.L.P., Li, H., Wei, Y., Xia, T., & Tang, Y.Y. (2014).
    A local contrast method for small infrared target detection.
    IEEE Transactions on Geoscience and Remote Sensing, 52(1), 574-581.
"""
from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


def compute_local_contrast(
    img: np.ndarray, inner_size: int = 3, outer_size: int = 9
) -> np.ndarray:
    """
    Compute the dual-window local contrast map.

    For each pixel the contrast is:
        LC(i,j) = max(0, μ_inner - μ_outer) / (μ_outer + ε)

    Args:
        img:        Grayscale infrared image (uint8 or float32).
        inner_size: Size of the inner window (must be odd, e.g. 3).
        outer_size: Size of the outer window (must be odd, > inner_size).

    Returns:
        Local contrast map as float32 array of the same spatial size.
    """
    img_f = img.astype(np.float32)

    kernel_i = np.ones((inner_size, inner_size), np.float32) / (inner_size ** 2)
    mean_inner = cv2.filter2D(img_f, -1, kernel_i)

    kernel_o = np.ones((outer_size, outer_size), np.float32) / (outer_size ** 2)
    mean_outer = cv2.filter2D(img_f, -1, kernel_o)

    eps = 1e-6
    lc = np.maximum(0.0, mean_inner - mean_outer) / (mean_outer + eps)
    return lc


def detect_targets_dwlcm(
    img: np.ndarray,
    threshold_factor: float = 3.0,
    max_target_area: int = 100,
) -> Tuple[np.ndarray, List[dict]]:
    """
    Detect small infrared targets via multi-scale Dual-Window Local Contrast Method.

    A three-scale LC map is fused before thresholding so that targets of
    slightly different apparent sizes are captured robustly.

    Args:
        img:               Grayscale infrared image.
        threshold_factor:  Adaptive threshold = mean + factor × std of the fused LC map.
        max_target_area:   Maximum connected-component area (px²) to classify as a
                           small target (larger blobs are rejected).

    Returns:
        (processed_bgr, targets)  where processed_bgr is the input rendered in BGR
        with detected targets highlighted, and targets is a list of dicts with keys
        x, y, width, height, area, confidence.
    """
    # Fuse three (inner, outer) scale pairs
    lc1 = compute_local_contrast(img, inner_size=3, outer_size=7)
    lc2 = compute_local_contrast(img, inner_size=3, outer_size=9)
    lc3 = compute_local_contrast(img, inner_size=5, outer_size=11)
    lc_map = (lc1 + lc2 + lc3) / 3.0

    lc_norm = cv2.normalize(lc_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    mean_val = float(np.mean(lc_map))
    std_val = float(np.std(lc_map))
    max_lc = float(np.max(lc_map)) + 1e-9
    thresh_val = int(
        np.clip(
            (mean_val + threshold_factor * std_val) / max_lc * 255,
            10,
            250,
        )
    )
    _, binary = cv2.threshold(lc_norm, thresh_val, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    targets: List[dict] = []
    processed = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        if area > max_target_area:
            continue
        cx, cy = int(centroids[i][0]), int(centroids[i][1])
        confidence = float(
            np.max(lc_map[max(0, y) : y + h, max(0, x) : x + w])
        )
        targets.append(
            {"x": cx, "y": cy, "width": int(w), "height": int(h), "area": int(area), "confidence": round(confidence, 4)}
        )
        radius = max(w, h) // 2 + 6
        cv2.circle(processed, (cx, cy), radius, (0, 255, 0), 2)
        cv2.circle(processed, (cx, cy), 2, (0, 0, 255), -1)

    return processed, targets
