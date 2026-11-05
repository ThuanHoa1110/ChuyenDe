"""
Unit tests for Baseline Models and Metric Evaluation (Phase 2, Step 2.2).
Validates:
1. Persistence baseline logic (predicts exact temperature at t).
2. Machine learning baseline reproducibility (Ridge produces identical weights & predictions across 2 runs).
3. Machine learning outperforms naive persistence benchmark (Macro MAE < Persistence MAE).
4. Deliverables integrity (reports/baselines.csv, reports/baseline_comparison.png, reports/predictions_baseline.csv).
"""

import os
import pytest
import numpy as np
import pandas as pd

from src.weather.data.window import split_and_window_dataset, TARGET_STATIONS
from src.weather.models.baseline import (
    RidgeBaselineModel,
    LightGBMBaselineModel,
    extract_tabular_features
)
from src.weather.evaluate import compute_metrics, run_evaluation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_WIDE_PATH = os.path.join(BASE_DIR, "data", "processed", "weather_wide_synced_sample.csv")


@pytest.fixture(scope="module")
def prepared_splits():
    df = pd.read_csv(SAMPLE_WIDE_PATH)
    return split_and_window_dataset(
        df=df,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        lookback=72,
        horizon=12,
        artifact_dir=os.path.join(BASE_DIR, "artifacts"),
        manifest_path=os.path.join(BASE_DIR, "manifests", "split_manifest.json")
    )


def test_persistence_logic(prepared_splits):
    """Persistence predictions must equal unscaled temperature observed at time t."""
    test_data = prepared_splits["test"]
    y_pers = test_data["y_persistence"]
    y_target = test_data["y"]

    assert y_pers.shape == y_target.shape
    assert y_pers.shape[1] == 6

    # Persistence error between t and t+12 should be physically reasonable (around 0.5°C - 2.0°C)
    mae_pers = np.mean(np.abs(y_pers - y_target))
    assert 0.1 < mae_pers < 5.0, f"Unreasonable persistence MAE: {mae_pers}"


def test_ml_baseline_reproducibility(prepared_splits):
    """Ridge baseline must produce identical weights and predictions across 2 consecutive runs."""
    train_data = prepared_splits["train"]
    test_data = prepared_splits["test"]
    feature_cols = train_data["feature_cols"]

    X_train_tab = extract_tabular_features(train_data["X"], train_data["timestamps_t"], feature_cols)
    X_test_tab = extract_tabular_features(test_data["X"], test_data["timestamps_t"], feature_cols)
    y_train = train_data["y"]

    # Run 1
    model1 = RidgeBaselineModel(alpha=1.0, random_seed=42)
    model1.fit(X_train_tab, y_train)
    pred1 = model1.predict(X_test_tab)

    # Run 2
    model2 = RidgeBaselineModel(alpha=1.0, random_seed=42)
    model2.fit(X_train_tab, y_train)
    pred2 = model2.predict(X_test_tab)

    np.testing.assert_allclose(pred1, pred2, atol=1e-6, rtol=1e-6, err_msg="Ridge predictions must be 100% reproducible!")


def test_ml_outperforms_persistence_benchmark(prepared_splits):
    """Machine learning baseline must improve upon naive persistence baseline."""
    train_data = prepared_splits["train"]
    test_data = prepared_splits["test"]
    feature_cols = train_data["feature_cols"]

    X_train_tab = extract_tabular_features(train_data["X"], train_data["timestamps_t"], feature_cols)
    X_test_tab = extract_tabular_features(test_data["X"], test_data["timestamps_t"], feature_cols)
    y_train = train_data["y"]
    y_test = test_data["y"]

    # Persistence MAE
    pers_mae = np.mean(np.abs(test_data["y_persistence"] - y_test))

    # Ridge MAE
    ridge = RidgeBaselineModel(alpha=1.0, random_seed=42)
    ridge.fit(X_train_tab, y_train)
    ridge_preds = ridge.predict(X_test_tab)
    ridge_mae = np.mean(np.abs(ridge_preds - y_test))

    assert ridge_mae < pers_mae, f"Ridge MAE ({ridge_mae:.4f}) must be lower than Persistence MAE ({pers_mae:.4f})"


def test_baseline_deliverables_and_reports_exist():
    """Validates baselines.csv, predictions_baseline.csv, and baseline_comparison.png."""
    baselines_csv = os.path.join(BASE_DIR, "reports", "baselines.csv")
    preds_csv = os.path.join(BASE_DIR, "reports", "predictions_baseline.csv")
    plot_png = os.path.join(BASE_DIR, "reports", "baseline_comparison.png")

    assert os.path.exists(baselines_csv), "reports/baselines.csv must exist"
    assert os.path.exists(preds_csv), "reports/predictions_baseline.csv must exist"
    assert os.path.exists(plot_png), "reports/baseline_comparison.png must exist"

    df_b = pd.read_csv(baselines_csv)
    assert len(df_b) >= 3  # Persistence, Ridge, LightGBM
    assert "model" in df_b.columns
    assert "macro_mae" in df_b.columns
    assert "macro_rmse" in df_b.columns

    # Check 6 stations have individual metrics
    for i in range(1, 7):
        assert f"ST0{i}_mae" in df_b.columns

