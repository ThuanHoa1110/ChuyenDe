"""
Unit tests for DINOv3 Forecaster Model (Phase 3, Step 3.2).
Validates:
1. Forward pass on batch size 1 and batch size 2 yields finite [B, 6] output.
2. Backward pass updates regression head parameters while backbone remains frozen.
3. Checkpoint save and load preserves 100% identical inference output.
4. End-to-end pipeline: raw window -> 3-channel image -> DINOv3 forward -> 6 station temperatures.
"""

import os
import pytest
import numpy as np
import torch

from src.weather.data.image import (
    get_canonical_feature_order,
    batch_windows_to_images
)
from src.weather.models.dinov3_forecaster import DINOv3_Forecaster


@pytest.fixture
def dummy_model():
    """Instantiates DINOv3_Forecaster with default test config."""
    cfg = {
        "freeze_backbone": True,
        "image_size": [224, 224],
        "num_outputs": 6,
        "hidden_dim": 384,
        "head_hidden_dim": 128,
        "dropout": 0.1
    }
    model = DINOv3_Forecaster(cfg)
    model.eval()
    return model


def test_dinov3_forward_batch_1_and_2(dummy_model):
    """Forward pass on batch 1 and batch 2 yields (B, 6) finite predictions."""
    # Batch 1
    x1 = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        out1 = dummy_model(x1)
    assert out1.shape == (1, 6)
    assert torch.all(torch.isfinite(out1))

    # Batch 2
    x2 = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        out2 = dummy_model(x2)
    assert out2.shape == (2, 6)
    assert torch.all(torch.isfinite(out2))


def test_dinov3_backward_and_frozen_backbone():
    """Verifies backward pass trains regression head while backbone parameters stay frozen."""
    cfg = {
        "freeze_backbone": True,
        "image_size": [224, 224],
        "num_outputs": 6,
        "hidden_dim": 384,
        "head_hidden_dim": 128,
        "dropout": 0.0
    }
    model = DINOv3_Forecaster(cfg)
    model.train()

    # Backbone parameters must have requires_grad == False
    for p in model.backbone.parameters():
        assert not p.requires_grad, "Backbone parameters must be frozen!"

    # Regression head parameters must have requires_grad == True
    for p in model.regression_head.parameters():
        assert p.requires_grad, "Regression head parameters must be trainable!"

    x = torch.randn(2, 3, 224, 224)
    y_target = torch.randn(2, 6)

    preds = model(x)
    loss = torch.nn.functional.mse_loss(preds, y_target)
    loss.backward()

    # Check that head received gradients
    has_head_grads = any(p.grad is not None and torch.sum(torch.abs(p.grad)) > 0 for p in model.regression_head.parameters())
    assert has_head_grads, "Regression head must receive non-zero gradients"


def test_dinov3_checkpoint_save_and_load(tmp_path, dummy_model):
    """Save and load checkpoint reproduces exact same forward predictions."""
    ckpt_file = tmp_path / "test_dinov3_ckpt.pt"
    dummy_model.eval()

    x = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        pred_original = dummy_model(x)

    torch.save(dummy_model.state_dict(), ckpt_file)

    # Load in new instance
    model_loaded = DINOv3_Forecaster()
    model_loaded.load_state_dict(torch.load(ckpt_file, weights_only=True))
    model_loaded.eval()

    with torch.no_grad():
        pred_loaded = model_loaded(x)

    torch.testing.assert_close(pred_original, pred_loaded)


def test_dinov3_end_to_end_from_window(dummy_model):
    """Tests raw window (72, 66) -> 3-channel image -> DINOv3 forward -> (1, 6) temperatures."""
    cols = get_canonical_feature_order()
    raw_window = np.random.randn(1, 72, 66).astype(np.float32)

    # 1. Encode window into 3-channel image
    img_tensor = batch_windows_to_images(raw_window, cols, target_size=(224, 224))
    torch_img = torch.from_numpy(img_tensor)

    # 2. Forward pass
    with torch.no_grad():
        preds, feats = dummy_model(torch_img, return_features=True)

    assert preds.shape == (1, 6)
    assert feats.shape == (1, 384)
    assert torch.all(torch.isfinite(preds))
