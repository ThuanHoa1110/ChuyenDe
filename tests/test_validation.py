"""
Unit tests for Data Validation and Quality Assurance (Phase 1, Step 1.2).
Tests intentional corruptions: duplicate timestamps, missing stations, unreasonable temperature,
and non-monotonic time ordering.
"""

import pytest
import pandas as pd
import numpy as np

from src.weather.data.validate import (
    validate_station_df,
    validate_multi_station_sync,
    ValidationError
)


@pytest.fixture
def clean_station_df():
    """Generates a clean synthetic station dataframe conforming to schema."""
    timestamps = pd.date_range("2026-01-01 00:00:00", periods=50, freq="5min")
    data = {
        "timestamp": [str(t) for t in timestamps],
        "station_id": ["ST01_HOANKIEM"] * 50,
        "temperature": np.linspace(15.0, 25.0, 50),
        "humidity": np.linspace(60.0, 80.0, 50),
        "dew_point": np.linspace(10.0, 15.0, 50),
        "apparent_temperature": np.linspace(14.0, 24.0, 50),
        "surface_pressure": np.linspace(1012.0, 1015.0, 50),
        "precipitation": [0.0] * 50,
        "cloud_cover": [20.0] * 50,
        "wind_speed_10m": [2.5] * 50,
        "wind_gusts_10m": [4.0] * 50,
        "solar_radiation": [100.0] * 50,
        "direct_radiation": [50.0] * 50,
    }
    return pd.DataFrame(data)


def test_clean_data_passes_validation(clean_station_df):
    """Clean data should pass validation with is_valid == True and zero errors."""
    report = validate_station_df(clean_station_df, expected_station_id="ST01_HOANKIEM")
    assert report["is_valid"] is True
    assert len(report["errors"]) == 0
    assert report["metrics"]["duplicate_keys"] == 0
    assert report["metrics"]["is_monotonic_increasing"] is True


def test_intentional_duplicate_timestamps(clean_station_df):
    """Intentional corruption 1: Duplicate timestamp must be detected."""
    corrupted_df = clean_station_df.copy()
    # Duplicate first row timestamp into second row
    corrupted_df.loc[1, "timestamp"] = corrupted_df.loc[0, "timestamp"]

    report = validate_station_df(corrupted_df, expected_station_id="ST01_HOANKIEM")
    assert report["is_valid"] is False
    assert report["metrics"]["duplicate_keys"] == 1
    assert any("trung lap" in err for err in report["errors"])


def test_intentional_unreasonable_temperature(clean_station_df):
    """Intentional corruption 2: Extreme unrealistic temperature (> 50°C) must be detected."""
    corrupted_df = clean_station_df.copy()
    corrupted_df.loc[10, "temperature"] = 150.0  # Physically impossible in Hanoi

    report = validate_station_df(corrupted_df, expected_station_id="ST01_HOANKIEM")
    assert report["is_valid"] is False
    assert "temperature" in report["metrics"]["out_of_bounds"]
    assert report["metrics"]["out_of_bounds"]["temperature"]["total"] == 1
    assert any("ngoai mien vat ly" in err for err in report["errors"])


def test_intentional_non_monotonic_time_order(clean_station_df):
    """Intentional corruption 3: Reversed / inverted time order must be caught."""
    corrupted_df = clean_station_df.iloc[::-1].reset_index(drop=True)  # Reverse rows

    report = validate_station_df(corrupted_df, expected_station_id="ST01_HOANKIEM")
    assert report["is_valid"] is False
    assert report["metrics"]["is_monotonic_increasing"] is False
    assert any("khong tang dan don dieu" in err for err in report["errors"])


def test_intentional_missing_required_columns(clean_station_df):
    """Intentional corruption 4: Dropping a required column must raise ValidationError."""
    corrupted_df = clean_station_df.drop(columns=["surface_pressure"])

    with pytest.raises(ValidationError) as exc_info:
        validate_station_df(corrupted_df)
    assert "surface_pressure" in str(exc_info.value)


def test_intentional_station_clock_drift_and_mismatch(clean_station_df):
    """Intentional corruption 5: Clock mismatch across stations must be caught by sync check."""
    df1 = clean_station_df.copy()
    df2 = clean_station_df.copy()

    # Shift df2 timestamps by 10 minutes
    t2 = pd.to_datetime(df2["timestamp"]) + pd.Timedelta(minutes=10)
    df2["timestamp"] = [str(t) for t in t2]
    df2["station_id"] = "ST02_BADINH"

    station_dict = {"ST01_HOANKIEM": df1, "ST02_BADINH": df2}
    sync_report = validate_multi_station_sync(station_dict)

    assert sync_report["is_synced"] is False
    assert len(sync_report["errors"]) > 0
    assert any("Lech dong ho" in err for err in sync_report["errors"])

