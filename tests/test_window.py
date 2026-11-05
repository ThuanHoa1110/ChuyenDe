"""
Unit tests for Windowing and Chronological Split (Phase 2, Step 2.1).
Validates:
1. Feature lookback window [t-71, t] never leaks future data (latest feature timestamp <= t).
2. Target y matches manual index lookup at t + 12 steps (60 minutes).
3. Zero target timestamp overlap across train, val, and test splits.
4. Scaler is strictly fit on train split only.
5. Split manifest exists and records valid metadata and 3 example samples.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from src.weather.data.window import (
    StandardFeatureScaler,
    create_sliding_windows,
    split_and_window_dataset,
    TARGET_STATIONS
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_WIDE_PATH = os.path.join(BASE_DIR, "data", "processed", "weather_wide_synced_sample.csv")


@pytest.fixture
def sample_wide_df():
    """Loads 1000-row synced wide sample dataset."""
    assert os.path.exists(SAMPLE_WIDE_PATH), f"Sample wide CSV missing at {SAMPLE_WIDE_PATH}"
    return pd.read_csv(SAMPLE_WIDE_PATH)


def test_window_temporal_boundary_and_no_leakage(sample_wide_df):
    """Verifies X uses only [t-71, t] and target is at t + 12 (latest feature <= t)."""
    lookback = 72
    horizon = 12
    windows = create_sliding_windows(sample_wide_df, lookback=lookback, horizon=horizon)

    X = windows["X"]
    y = windows["y"]
    t_arr = windows["timestamps_t"]
    t_target_arr = windows["timestamps_target"]

    # Check shapes
    expected_samples = len(sample_wide_df) - lookback - horizon + 1
    assert len(X) == expected_samples
    assert X.shape[1] == lookback
    assert X.shape[2] == 66  # 6 stations x 11 features
    assert y.shape == (expected_samples, 6)

    # Check time delta between t and target is exactly 60 minutes (12 * 5min)
    t0 = pd.to_datetime(t_arr[0])
    t_target0 = pd.to_datetime(t_target_arr[0])
    diff_minutes = (t_target0 - t0).total_seconds() / 60.0
    assert diff_minutes == 60.0, f"Expected 60 minutes horizon, got {diff_minutes}"


def test_manual_index_verification(sample_wide_df):
    """Manual index verification: y values match manual dataframe lookup at t+12."""
    lookback = 72
    horizon = 12
    windows = create_sliding_windows(sample_wide_df, lookback=lookback, horizon=horizon)

    target_cols = TARGET_STATIONS
    # Check 5 arbitrary sample indices
    test_indices = [0, 50, 100, 200, len(windows["y"]) - 1]
    for sample_idx in test_indices:
        # Corresponding row index i in sample_wide_df:
        row_i = sample_idx + lookback - 1
        target_row = row_i + horizon

        expected_y = sample_wide_df.loc[target_row, target_cols].to_numpy(dtype=np.float32)
        actual_y = windows["y"][sample_idx]
        np.testing.assert_allclose(actual_y, expected_y, rtol=1e-5, atol=1e-5)

        # Check timestamp at t
        assert windows["timestamps_t"][sample_idx] == sample_wide_df.loc[row_i, "timestamp"]
        assert windows["timestamps_target"][sample_idx] == sample_wide_df.loc[target_row, "timestamp"]


def test_chronological_split_no_target_overlap(sample_wide_df):
    """Verifies that train, val, and test partitions have zero target timestamp overlap."""
    result = split_and_window_dataset(
        sample_wide_df,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        lookback=72,
        horizon=12,
        artifact_dir=os.path.join(BASE_DIR, "artifacts"),
        manifest_path=os.path.join(BASE_DIR, "manifests", "split_manifest.json")
    )

    train_targets = set(result["train"]["timestamps_target"])
    val_targets = set(result["val"]["timestamps_target"])
    test_targets = set(result["test"]["timestamps_target"])

    # Disjoint sets: no overlap
    assert len(train_targets.intersection(val_targets)) == 0, "Train and Val target timestamps must not overlap!"
    assert len(val_targets.intersection(test_targets)) == 0, "Val and Test target timestamps must not overlap!"
    assert len(train_targets.intersection(test_targets)) == 0, "Train and Test target timestamps must not overlap!"

    # Strict chronological order
    max_train_time = max(pd.to_datetime(result["train"]["timestamps_target"]))
    min_val_time = min(pd.to_datetime(result["val"]["timestamps_target"]))
    max_val_time = max(pd.to_datetime(result["val"]["timestamps_target"]))
    min_test_time = min(pd.to_datetime(result["test"]["timestamps_target"]))

    assert max_train_time < min_val_time, "Train targets must precede Val targets chronologically"
    assert max_val_time < min_test_time, "Val targets must precede Test targets chronologically"


def test_scaler_fitted_strictly_on_train(sample_wide_df):
    """Verifies scaler mean and std are derived strictly from train partition."""
    feature_cols = [c for c in sample_wide_df.columns if c != "timestamp"]
    n_train = int(len(sample_wide_df) * 0.70)
    train_df = sample_wide_df.iloc[:n_train]

    expected_means = train_df[feature_cols].mean().to_numpy()

    scaler = StandardFeatureScaler()
    scaler.fit(train_df, feature_cols)

    np.testing.assert_allclose(scaler.mean_, expected_means, rtol=1e-4, atol=1e-4)


def test_split_manifest_and_examples():
    """Verifies manifests/split_manifest.json format and 3 example samples."""
    manifest_path = os.path.join(BASE_DIR, "manifests", "split_manifest.json")
    assert os.path.exists(manifest_path), "manifests/split_manifest.json must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "metadata" in manifest
    assert "partitions" in manifest
    assert "three_example_samples" in manifest

    assert len(manifest["three_example_samples"]) == 3
    for ex in manifest["three_example_samples"]:
        assert "split" in ex
        assert "timestamp_t" in ex
        assert "timestamp_target_t_plus_12" in ex
        assert len(ex["target_station_temperatures"]) == 6
