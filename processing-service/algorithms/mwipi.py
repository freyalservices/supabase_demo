"""
Multiscale Window Infrared Patch-Image (MW-IPI) model for small target detection.

The patch-image model decomposes an image into:
  - Low-rank matrix  L  (smooth background clutter)
  - Sparse matrix    S  (small bright/dark targets)

This implementation uses a truncated SVD approximation of the low-rank component,
fused across multiple patch scales for robustness.

Reference:
    Gao, C., Meng, D., Yang, Y., Wang, Y., Zhou, X., & Hauptmann, A.G. (2013).
    Infrared Patch-Image Model for Small Target Detection in a Single Image.
    IEEE Transactions on Image Processing, 22(12), 4996-5009.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import cv2
import numpy as np


def _patch_image_model(
    img: np.ndarray, patch_size: int = 40, step: int = 8, rank: int = 3
) -> np.ndarray:
    """
    Apply the patch-image low-rank + sparse decomposition.

    Args:
        img:        Grayscale image.
        patch_size: Height/width of square patches.
        step:       Stride between patches.
        rank:       Number of singular values kept for the background (low-rank) model.

    Returns:
        Sparse (target) component as a float64 array the same size as img.
    """
    h, w = img.shape
    if patch_size >= h or patch_size >= w:
        return np.zeros_like(img, dtype=np.float64)

    img_f = img.astype(np.float64)
    patches: List[np.ndarray] = []
    positions: List[Tuple[int, int]] = []

    for r in range(0, h - patch_size + 1, step):
        for c in range(0, w - patch_size + 1, step):
            patches.append(img_f[r : r + patch_size, c : c + patch_size].flatten())
            positions.append((r, c))

    if not patches:
        return np.zeros_like(img_f)

    D = np.column_stack(patches)  # shape: (patch_size^2, num_patches)

    effective_rank = min(rank, min(D.shape) - 1)
    U, s, Vt = np.linalg.svd(D, full_matrices=False)
    s_bg = s.copy()
    s_bg[effective_rank:] = 0.0
    L = U @ np.diag(s_bg) @ Vt

    S = D - L  # sparse (target) component

    target_img = np.zeros((h, w), dtype=np.float64)
    weight_map = np.zeros((h, w), dtype=np.float64)

    for idx, (r, c) in enumerate(positions):
        patch_t = S[:, idx].reshape(patch_size, patch_size)
        target_img[r : r + patch_size, c : c + patch_size] += patch_t
        weight_map[r : r + patch_size, c : c + patch_size] += 1.0

    weight_map = np.maximum(weight_map, 1.0)
    target_img /= weight_map
    return target_img


def detect_targets_mwipi(
    img: np.ndarray,
    scales: Optional[List[int]] = None,
    threshold_factor: float = 2.5,
    max_target_area: int = 150,
) -> Tuple[np.ndarray, List[dict]]:
    """
    Detect small infrared targets using the Multiscale Window Patch-Image Model.

    Args:
        img:               Grayscale infrared image.
        scales:            List of patch sizes for multiscale analysis.
                           Defaults to [30, 50].
        threshold_factor:  Adaptive threshold = mean + factor × std.
        max_target_area:   Maximum area (px²) for a valid small target.

    Returns:
        (processed_bgr, targets) — same convention as detect_targets_dwlcm.
    """
    if scales is None:
        scales = [30, 50]

    h, w = img.shape
    combined = np.zeros((h, w), dtype=np.float64)
    valid_scales = 0

    for scale in scales:
        if scale >= h or scale >= w:
            continue
        component = _patch_image_model(img, patch_size=scale, step=max(scale // 5, 5))
        component = np.maximum(0.0, component)  # keep bright targets only
        max_c = np.max(component)
        if max_c > 0:
            combined += component / max_c
            valid_scales += 1

    if valid_scales:
        combined /= valid_scales

    target_norm = cv2.normalize(combined, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    mean_val = float(np.mean(combined))
    std_val = float(np.std(combined))
    max_val = float(np.max(combined)) + 1e-9
    thresh_val = int(
        np.clip(
            (mean_val + threshold_factor * std_val) / max_val * 255,
            10,
            250,
        )
    )
    _, binary = cv2.threshold(target_norm, thresh_val, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    targets: List[dict] = []
    processed = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for i in range(1, num_labels):
        x, y, bw, bh, area = stats[i]
        if area > max_target_area:
            continue
        cx, cy = int(centroids[i][0]), int(centroids[i][1])
        confidence = float(
            np.max(combined[max(0, y) : y + bh, max(0, x) : x + bw])
        )
        targets.append(
            {
                "x": cx,
                "y": cy,
                "width": int(bw),
                "height": int(bh),
                "area": int(area),
                "confidence": round(confidence, 4),
            }
        )
        cv2.rectangle(processed, (x - 3, y - 3), (x + bw + 3, y + bh + 3), (0, 255, 255), 2)
        cv2.circle(processed, (cx, cy), 2, (0, 0, 255), -1)

    return processed, targets
