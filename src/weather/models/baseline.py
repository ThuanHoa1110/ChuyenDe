"""
Baseline Models for Hanoi Temperature Forecasting (Phase 2, Step 2.2).
Includes:
1. Persistence Baseline: y_hat = temperature at timestamp t.
2. Ridge Regression Baseline: Ridge with L2 regularization on lag features and time-of-day cyclics.
3. LightGBM Baseline: Gradient boosting regressors for multi-station forecasting.
"""

import time
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
import lightgbm as lgb


class PersistenceBaseline:
    """
    Persistence model: Forecast temperature at t + 12 steps (60 min)
    equals the observed temperature at current time t.
    """

    def __init__(self, target_station_indices: Optional[List[int]] = None):
        # By default, in feature_cols, target temperatures are located at known indices
        self.target_station_indices = target_station_indices

    def fit(self, X: np.ndarray, y: np.ndarray):
        # Persistence has no trainable parameters
        return self

    def predict(self, X: np.ndarray, feature_cols: List[str]) -> np.ndarray:
        """
        X: shape (num_samples, lookback, num_features)
        Returns y_pred: shape (num_samples, 6) taken from last step of lookback (time t).
        """
        # Find indices of temperature columns for ST01..ST06
        temp_indices = [feature_cols.index(f"st0{i}_temperature") for i in range(1, 7)]
        # Last step of lookback is at index -1
        y_pred = X[:, -1, temp_indices]
        return y_pred


def extract_tabular_features(
    X: np.ndarray,
    timestamps_t: np.ndarray,
    feature_cols: List[str]
) -> np.ndarray:
    """
    Transforms 3D window (num_samples, lookback, num_features) into 2D tabular features:
    - Current step t values (all 66 features).
    - Lags at t-1, t-2, t-6, t-12, t-24, t-71 for temperature and pressure.
    - Window statistics (mean, std, min, max, delta from t-71 to t) for 6 station temperatures.
    - Cyclic temporal features: sin/cos of hour of day and day of year.
    """
    num_samples, lookback, num_features = X.shape
    features_list = []

    # 1. Current state at time t
    x_t = X[:, -1, :]  # shape (num_samples, 66)
    features_list.append(x_t)

    # 2. Selected lags for temperatures
    temp_indices = [feature_cols.index(f"st0{i}_temperature") for i in range(1, 7)]
    selected_lags = [1, 2, 6, 12, 24, 71]  # offsets from t
    for lag in selected_lags:
        lag_idx = lookback - 1 - lag
        if 0 <= lag_idx < lookback:
            features_list.append(X[:, lag_idx, temp_indices])

    # 3. Summary statistics over lookback for temperatures
    temps_lookback = X[:, :, temp_indices]  # (num_samples, lookback, 6)
    features_list.append(np.mean(temps_lookback, axis=1))
    features_list.append(np.std(temps_lookback, axis=1))
    features_list.append(np.max(temps_lookback, axis=1))
    features_list.append(np.min(temps_lookback, axis=1))
    # Trend delta: t minus t-71
    features_list.append(temps_lookback[:, -1, :] - temps_lookback[:, 0, :])

    # 4. Cyclic temporal features from timestamps_t
    t_dt = pd.to_datetime(timestamps_t)
    hours = t_dt.hour.to_numpy() + t_dt.minute.to_numpy() / 60.0
    doy = t_dt.day_of_year.to_numpy() if hasattr(t_dt, "day_of_year") else t_dt.dayofyear.to_numpy()

    sin_hour = np.sin(2 * np.pi * hours / 24.0)[:, np.newaxis]
    cos_hour = np.cos(2 * np.pi * hours / 24.0)[:, np.newaxis]
    sin_doy = np.sin(2 * np.pi * doy / 365.25)[:, np.newaxis]
    cos_doy = np.cos(2 * np.pi * doy / 365.25)[:, np.newaxis]

    features_list.extend([sin_hour, cos_hour, sin_doy, cos_doy])

    tabular_X = np.hstack(features_list).astype(np.float32)
    return tabular_X


class RidgeBaselineModel:
    """Multi-station Ridge Regression baseline on tabular lag features."""

    def __init__(self, alpha: float = 1.0, random_seed: int = 42):
        self.alpha = alpha
        self.random_seed = random_seed
        self.models: List[Ridge] = []

    def fit(self, X_tab: np.ndarray, y: np.ndarray):
        num_stations = y.shape[1]
        self.models = []
        for i in range(num_stations):
            model = Ridge(alpha=self.alpha, random_state=self.random_seed)
            model.fit(X_tab, y[:, i])
            self.models.append(model)
        return self

    def predict(self, X_tab: np.ndarray) -> np.ndarray:
        preds = [model.predict(X_tab)[:, np.newaxis] for model in self.models]
        return np.hstack(preds)


class LightGBMBaselineModel:
    """Multi-station LightGBM Regressor baseline."""

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.05, random_seed: int = 42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.random_seed = random_seed
        self.models: List[lgb.LGBMRegressor] = []

    def fit(self, X_tab: np.ndarray, y: np.ndarray):
        num_stations = y.shape[1]
        self.models = []
        for i in range(num_stations):
            model = lgb.LGBMRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                random_state=self.random_seed,
                verbosity=-1,
                n_jobs=-1
            )
            model.fit(X_tab, y[:, i])
            self.models.append(model)
        return self

    def predict(self, X_tab: np.ndarray) -> np.ndarray:
        preds = [model.predict(X_tab)[:, np.newaxis] for model in self.models]
        return np.hstack(preds)
