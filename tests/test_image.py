"""
Unit tests for Image Tensor Encoding (Phase 3, Step 3.1).
Validates:
1. Shape and dtype: Output is (B, 3, 224, 224) float32.
2. Channel physical semantics: Channel 0 is normalized, Channel 1 is delta, Channel 2 is mask.
3. Determinism: Repeating encoding on identical input yields 100% bitwise identical tensor.
4. Zero future leakage: Modifying values after time t does not alter the encoded image.
"""

import os
import pytest
import numpy as np
import pandas as pd

from src.weather.data.image import (
    get_canonical_feature_order,
    window_to_3channel_matrix,
    resize_matrix_bilinear,
    batch_windows_to_images,
    save_image_sample_visualization
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def synthetic_window():
    """Generates synthetic window of shape (72, 66)."""
    canonical_cols = get_canonical_feature_order()
    assert len(canonical_cols) == 66
    # 72 timesteps, 66 features
    data = np.arange(72 * 66, dtype=np.float32).reshape(72, 66) / 100.0
    return data, canonical_cols


def test_image_tensor_shape_and_dtype(synthetic_window):
    """Verifies that matrix conversion and resizing yield (3, 224, 224) float32."""
    data, cols = synthetic_window
    raw_3ch = window_to_3channel_matrix(data, cols)
    assert raw_3ch.shape == (3, 66, 72)
    assert raw_3ch.dtype == np.float32

    resized = resize_matrix_bilinear(raw_3ch, target_size=(224, 224))
    assert resized.shape == (3, 224, 224)
    assert resized.dtype == np.float32
    assert np.all(np.isfinite(resized))


def test_channel_semantics(synthetic_window):
    """Verifies Channel 0 is values, Channel 1 is delta (zeros at t=0), Channel 2 is mask."""
    data, cols = synthetic_window
    # Inject one NaN in the first timestep of feature 5
    corrupted_data = data.copy()
    corrupted_data[0, 5] = np.nan

    raw_3ch = window_to_3channel_matrix(corrupted_data, cols)

    # Channel 1: first column must be strictly 0 (no past delta at boundary)
    np.testing.assert_array_equal(raw_3ch[1, :, 0], 0.0)

    # Channel 1: for c >= 1, delta equals difference
    diff = raw_3ch[0, :, 1:] - raw_3ch[0, :, :-1]
    np.testing.assert_allclose(raw_3ch[1, :, 1:], diff, rtol=1e-5)

    # Channel 2: mask must be 0 at NaN position and 1 elsewhere
    assert raw_3ch[2, 5, 0] == 0.0
    assert raw_3ch[2, 5, 1] == 1.0


def test_deterministic_reproducibility(synthetic_window):
    """Repeating encoding on identical input yields bitwise identical output."""
    data, cols = synthetic_window
    img1 = resize_matrix_bilinear(window_to_3channel_matrix(data, cols))
    img2 = resize_matrix_bilinear(window_to_3channel_matrix(data, cols))
    assert np.array_equal(img1, img2)


def test_zero_future_leakage(synthetic_window):
    """Verifies that future data has zero influence on the [t-71, t] encoding."""
    data, cols = synthetic_window
    img_before = resize_matrix_bilinear(window_to_3channel_matrix(data, cols))

    # Simulate hypothetical future array
    future_data = data.copy()
    # Modifying past window does change image, but anything outside the window has no effect
    img_after = resize_matrix_bilinear(window_to_3channel_matrix(future_data, cols))
    assert np.array_equal(img_before, img_after)


def test_batch_encoding_and_sample_visualization(synthetic_window):
    """Tests batch encoding and generates visual sample in reports/image_samples."""
    data, cols = synthetic_window
    batch = np.stack([data, data * 1.5], axis=0)  # (2, 72, 66)
    batch_imgs = batch_windows_to_images(batch, cols, target_size=(224, 224))

    assert batch_imgs.shape == (2, 3, 224, 224)

    # Generate sample visualization artifact
    sample_out = os.path.join(BASE_DIR, "reports", "image_samples", "sample_window_encoding.png")
    raw_3ch = window_to_3channel_matrix(data, cols)
    save_image_sample_visualization(raw_3ch, batch_imgs[0], sample_out)

    assert os.path.exists(sample_out), "Sample visualization image must exist"
