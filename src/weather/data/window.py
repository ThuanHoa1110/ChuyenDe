"""
Windowing, Chronological Splitting, and Feature Scaling Module.
Implements Phase 2, Step 2.1 specifications:
- Lookback = 72 steps (6 hours), Horizon = 12 steps (60 minutes).
- For timestamp t, X contains [t-71, t] and y contains 6 stations temperature at t+12.
- Strict chronological split (70% train, 15% val, 15% test).
- Scaler fitted exclusively on train split with boundary separation.
"""

import os
import sys
import json
import pickle
import hashlib
from typing import Dict, List, Tuple, Optional, Union
import numpy as np
import pandas as pd

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TARGET_STATIONS = [f"st0{i}_temperature" for i in range(1, 7)]


class StandardFeatureScaler:
    """Standard scaler (mean=0, std=1) with pickle persistence and SHA-256 auditing."""

    def __init__(self):
        self.mean_ = None
        self.scale_ = None
        self.columns_ = None

    def fit(self, df: pd.DataFrame, feature_cols: List[str]):
        self.columns_ = list(feature_cols)
        data = df[feature_cols].to_numpy(dtype=np.float64)
        self.mean_ = np.nanmean(data, axis=0)
        self.scale_ = np.nanstd(data, axis=0)
        # Avoid division by zero for constant features
        self.scale_[self.scale_ == 0.0] = 1.0
        return self

    def transform(self, df_or_arr: Union[pd.DataFrame, np.ndarray]) -> Union[pd.DataFrame, np.ndarray]:
        if self.mean_ is None or self.scale_ is None:
            raise ValueError("Scaler is not fitted yet.")
        if isinstance(df_or_arr, pd.DataFrame):
            out_df = df_or_arr.copy()
            data = out_df[self.columns_].to_numpy(dtype=np.float64)
            scaled_data = (data - self.mean_) / self.scale_
            out_df[self.columns_] = scaled_data
            return out_df
        else:
            arr = np.asarray(df_or_arr, dtype=np.float64)
            return (arr - self.mean_) / self.scale_

    def save(self, filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({"mean": self.mean_, "scale": self.scale_, "columns": self.columns_}, f)
        # Return SHA256 of saved artifact
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            payload = pickle.load(f)
        self.mean_ = payload["mean"]
        self.scale_ = payload["scale"]
        self.columns_ = payload["columns"]
        return self


def create_sliding_windows(
    df: pd.DataFrame,
    lookback: int = 72,
    horizon: int = 12,
    feature_cols: Optional[List[str]] = None,
    target_cols: Optional[List[str]] = None,
    unscaled_df: Optional[pd.DataFrame] = None
) -> Dict[str, np.ndarray]:
    """
    Constructs sliding time windows [t-lookback+1, t] -> y at t+horizon.
    Guarantees:
      - X strictly uses features up to t (no future data).
      - y strictly corresponds to t + horizon (in actual physical °C if unscaled_df is passed).
      - y_persistence corresponds to unscaled target temperatures observed at time t.
    """
    if feature_cols is None:
        feature_cols = [c for c in df.columns if c != "timestamp"]
    if target_cols is None:
        target_cols = TARGET_STATIONS

    n_rows = len(df)
    min_required = lookback + horizon
    if n_rows < min_required:
        raise ValueError(f"Dataframe length ({n_rows}) is smaller than lookback + horizon ({min_required}).")

    timestamps = df["timestamp"].to_numpy()
    feature_matrix = df[feature_cols].to_numpy(dtype=np.float32)

    # If unscaled_df is provided, targets y and persistence are in physical °C
    target_source_df = unscaled_df if unscaled_df is not None else df
    target_matrix = target_source_df[target_cols].to_numpy(dtype=np.float32)

    start_i = lookback - 1
    end_i = n_rows - 1 - horizon
    num_samples = end_i - start_i + 1

    X = np.empty((num_samples, lookback, len(feature_cols)), dtype=np.float32)
    y = np.empty((num_samples, len(target_cols)), dtype=np.float32)
    y_persistence = np.empty((num_samples, len(target_cols)), dtype=np.float32)
    timestamps_t = np.empty(num_samples, dtype=object)
    timestamps_target = np.empty(num_samples, dtype=object)

    for sample_idx, i in enumerate(range(start_i, end_i + 1)):
        X[sample_idx] = feature_matrix[i - lookback + 1 : i + 1]
        y[sample_idx] = target_matrix[i + horizon]
        y_persistence[sample_idx] = target_matrix[i]
        timestamps_t[sample_idx] = timestamps[i]
        timestamps_target[sample_idx] = timestamps[i + horizon]

    return {
        "X": X,
        "y": y,
        "y_persistence": y_persistence,
        "timestamps_t": timestamps_t,
        "timestamps_target": timestamps_target,
        "feature_cols": feature_cols,
        "target_cols": target_cols
    }


def split_and_window_dataset(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    lookback: int = 72,
    horizon: int = 12,
    artifact_dir: str = "artifacts",
    manifest_path: str = "manifests/split_manifest.json",
    data_version: str = "v1.0.0",
    random_seed: int = 42
) -> Dict[str, dict]:
    """
    Performs chronological split, fits scaler exclusively on train,
    creates non-overlapping sliding windows, and saves split manifest.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Split ratios must sum to 1.0"
    n = len(df)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = n - n_train - n_val

    feature_cols = [c for c in df.columns if c != "timestamp"]
    target_cols = TARGET_STATIONS

    train_df = df.iloc[:n_train].copy().reset_index(drop=True)
    val_df = df.iloc[n_train : n_train + n_val].copy().reset_index(drop=True)
    test_df = df.iloc[n_train + n_val :].copy().reset_index(drop=True)

    # 1. Fit scaler strictly on train split
    scaler = StandardFeatureScaler()
    scaler.fit(train_df, feature_cols)
    os.makedirs(artifact_dir, exist_ok=True)
    scaler_path = os.path.join(artifact_dir, "scaler.pkl")
    scaler_rel_path = os.path.relpath(scaler_path, BASE_DIR).replace("\\", "/") if os.path.isabs(scaler_path) else scaler_path
    scaler_sha256 = scaler.save(scaler_path)

    # 2. Transform all splits using train-fitted scaler
    train_scaled = scaler.transform(train_df)
    val_scaled = scaler.transform(val_df)
    test_scaled = scaler.transform(test_df)

    # 3. Create windows per partition with boundary protection (y in Celsius °C)
    train_windows = create_sliding_windows(train_scaled, lookback, horizon, feature_cols, target_cols, unscaled_df=train_df)
    val_windows = create_sliding_windows(val_scaled, lookback, horizon, feature_cols, target_cols, unscaled_df=val_df)
    test_windows = create_sliding_windows(test_scaled, lookback, horizon, feature_cols, target_cols, unscaled_df=test_df)

    # 4. Generate split manifest with 3 concrete example samples
    examples = []
    for split_name, win in [("train", train_windows), ("val", val_windows), ("test", test_windows)]:
        if len(win["timestamps_t"]) > 0:
            idx = 0
            examples.append({
                "split": split_name,
                "timestamp_t": str(win["timestamps_t"][idx]),
                "timestamp_target_t_plus_12": str(win["timestamps_target"][idx]),
                "target_station_temperatures": {
                    st: round(float(win["y"][idx][k]), 2) for k, st in enumerate(target_cols)
                }
            })

    manifest = {
        "metadata": {
            "data_version": data_version,
            "random_seed": random_seed,
            "lookback_steps": lookback,
            "horizon_steps": horizon,
            "time_interval_minutes": 5,
            "split_ratios": {"train": train_ratio, "val": val_ratio, "test": test_ratio},
            "scaler_artifact": {
                "path": scaler_rel_path,
                "sha256": scaler_sha256,
                "type": "StandardScaler (fitted on train only)"
            }
        },
        "partitions": {
            "train": {
                "raw_rows": len(train_df),
                "timestamp_start": str(train_df["timestamp"].iloc[0]),
                "timestamp_end": str(train_df["timestamp"].iloc[-1]),
                "num_window_samples": len(train_windows["y"]),
                "target_timestamp_start": str(train_windows["timestamps_target"][0]),
                "target_timestamp_end": str(train_windows["timestamps_target"][-1]),
            },
            "val": {
                "raw_rows": len(val_df),
                "timestamp_start": str(val_df["timestamp"].iloc[0]),
                "timestamp_end": str(val_df["timestamp"].iloc[-1]),
                "num_window_samples": len(val_windows["y"]),
                "target_timestamp_start": str(val_windows["timestamps_target"][0]),
                "target_timestamp_end": str(val_windows["timestamps_target"][-1]),
            },
            "test": {
                "raw_rows": len(test_df),
                "timestamp_start": str(test_df["timestamp"].iloc[0]),
                "timestamp_end": str(test_df["timestamp"].iloc[-1]),
                "num_window_samples": len(test_windows["y"]),
                "target_timestamp_start": str(test_windows["timestamps_target"][0]),
                "target_timestamp_end": str(test_windows["timestamps_target"][-1]),
            }
        },
        "three_example_samples": examples
    }

    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return {
        "train": train_windows,
        "val": val_windows,
        "test": test_windows,
        "scaler": scaler,
        "manifest": manifest
    }
