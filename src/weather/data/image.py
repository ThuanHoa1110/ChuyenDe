"""
Image Tensor Encoding Module for DINOv3 Forecaster (Phase 3, Step 3.1).
Converts multi-station time series windows (batch, lookback=72, num_features=66)
into 3-channel spatial-temporal image tensors:
- Channel 0: Normalized meteorological features (H=66, W=72)
- Channel 1: Past temporal deltas (x_t - x_{t-1})
- Channel 2: Observation mask (1.0 = valid, 0.0 = missing)
Resizes to standard DINOv3 input shape (batch, 3, 224, 224).
"""

import os
import sys
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

STATION_ORDER = [
    "ST01_HOANKIEM",
    "ST02_BADINH",
    "ST03_CAUGIAY",
    "ST04_HADONG",
    "ST05_DONGANH",
    "ST06_SOCSON"
]

VARIABLE_ORDER = [
    "temperature",
    "humidity",
    "dew_point",
    "apparent_temperature",
    "surface_pressure",
    "precipitation",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
    "solar_radiation",
    "direct_radiation"
]


def get_canonical_feature_order() -> List[str]:
    """Returns canonical list of 66 column names in strict station and variable order."""
    cols = []
    for st in STATION_ORDER:
        st_short = st.split("_")[0].lower()
        for var in VARIABLE_ORDER:
            cols.append(f"{st_short}_{var}")
    return cols


def window_to_3channel_matrix(
    window: np.ndarray,
    feature_cols: List[str]
) -> np.ndarray:
    """
    Transforms single window (lookback=72, num_features=66) into (3, 66, 72) matrix.
    Channel 0: Normalized values
    Channel 1: Past deltas (first difference along time axis)
    Channel 2: Observation mask
    """
    assert window.ndim == 2, f"Expected 2D window (lookback, features), got {window.shape}"
    lookback, num_feats = window.shape

    canonical_cols = get_canonical_feature_order()
    # Map feature_cols to canonical row index
    col_to_idx = {c: i for i, c in enumerate(feature_cols)}
    reorder_indices = [col_to_idx[c] for c in canonical_cols]

    # Transpose so rows are 66 features, columns are 72 timesteps
    # window is (72, 66) -> reordered_matrix is (66, 72)
    reordered_matrix = window[:, reorder_indices].T.astype(np.float32)  # shape (66, 72)

    # Channel 0: Normalized values
    c0 = np.nan_to_num(reordered_matrix, nan=0.0)

    # Channel 1: Past temporal differences: c0[:, t] - c0[:, t-1]
    c1 = np.zeros_like(c0)
    c1[:, 1:] = c0[:, 1:] - c0[:, :-1]

    # Channel 2: Observation mask (1.0 for valid observed numbers)
    c2 = np.isfinite(reordered_matrix).astype(np.float32)

    return np.stack([c0, c1, c2], axis=0)  # shape (3, 66, 72)


def resize_matrix_bilinear(tensor_3ch: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Pure numpy/scipy bilinear interpolation resizing from (3, H, W) to (3, target_H, target_W).
    Avoids requiring torch at import time if running lightweight tests.
    """
    C, H, W = tensor_3ch.shape
    out_H, out_W = target_size

    # Scale factors
    scale_y = (H - 1) / (out_H - 1) if out_H > 1 else 0.0
    scale_x = (W - 1) / (out_W - 1) if out_W > 1 else 0.0

    y_indices = np.arange(out_H) * scale_y
    x_indices = np.arange(out_W) * scale_x

    y0 = np.floor(y_indices).astype(int)
    y1 = np.clip(y0 + 1, 0, H - 1)
    x0 = np.floor(x_indices).astype(int)
    x1 = np.clip(x0 + 1, 0, W - 1)

    wy = (y_indices - y0).reshape(-1, 1)
    wx = (x_indices - x0).reshape(1, -1)

    out = np.empty((C, out_H, out_W), dtype=np.float32)
    for c in range(C):
        mat = tensor_3ch[c]
        top_left = mat[np.ix_(y0, x0)]
        top_right = mat[np.ix_(y0, x1)]
        bottom_left = mat[np.ix_(y1, x0)]
        bottom_right = mat[np.ix_(y1, x1)]

        top = top_left * (1.0 - wx) + top_right * wx
        bottom = bottom_left * (1.0 - wx) + bottom_right * wx
        out[c] = top * (1.0 - wy) + bottom * wy

    return out


def batch_windows_to_images(
    X_windows: np.ndarray,
    feature_cols: List[str],
    target_size: Tuple[int, int] = (224, 224)
) -> np.ndarray:
    """
    Batch encoder: Converts (B, 72, 66) -> (B, 3, 224, 224).
    """
    B = len(X_windows)
    images = np.empty((B, 3, target_size[0], target_size[1]), dtype=np.float32)
    for i in range(B):
        mat_3ch = window_to_3channel_matrix(X_windows[i], feature_cols)
        images[i] = resize_matrix_bilinear(mat_3ch, target_size=target_size)
    return images


def save_image_sample_visualization(
    raw_window_3ch: np.ndarray,
    resized_image: np.ndarray,
    output_path: str,
    sample_title: str = "Hanoi Weather Window Encoding"
):
    """
    Visualizes the 3 channels before and after interpolation.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), dpi=150)
    plt.subplots_adjust(wspace=0.25, hspace=0.3)

    channel_names = [
        "Channel 0: Normalized Values",
        "Channel 1: Temporal Deltas (x_t - x_{t-1})",
        "Channel 2: Observation Mask"
    ]

    # Row 1: Raw 66 x 72
    for c in range(3):
        ax = axes[0, c]
        im = ax.imshow(raw_window_3ch[c], aspect="auto", cmap="viridis" if c < 2 else "gray")
        ax.set_title(f"Gốc (66 x 72)\n{channel_names[c]}", fontsize=10, fontweight="bold")
        ax.set_xlabel("Mốc thời gian (t-71 -> t)")
        ax.set_ylabel("Hàng (6 trạm x 11 biến)")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # Row 2: Resized 224 x 224
    for c in range(3):
        ax = axes[1, c]
        im = ax.imshow(resized_image[c], aspect="equal", cmap="viridis" if c < 2 else "gray")
        ax.set_title(f"Nội suy DINOv3 (224 x 224)\n{channel_names[c]}", fontsize=10, fontweight="bold")
        ax.set_xlabel("Pixel X")
        ax.set_ylabel("Pixel Y")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle(f"{sample_title} - DINOv3 Spatial-Temporal Tensor Encoding", fontsize=13, fontweight="bold")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"🖼️ Đã lưu mẫu ảnh trực quan hoá: {output_path}")
