"""
Data Validation Module for Hanoi Weather Forecasting Project.
Checks primary keys, monotonicity, sampling intervals, missing values, physical ranges, and cross-station clock drift.
Follows Phase 1, Step 1.2 specifications.
"""

import sys
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Physical range thresholds for meteorological variables in Hanoi climate
PHYSICAL_RANGES = {
    "temperature": (-10.0, 50.0),            # °C
    "humidity": (0.0, 100.0),               # %
    "dew_point": (-20.0, 40.0),             # °C
    "apparent_temperature": (-15.0, 55.0),   # °C
    "surface_pressure": (900.0, 1100.0),     # hPa
    "precipitation": (0.0, 300.0),           # mm
    "cloud_cover": (0.0, 100.0),            # %
    "wind_speed_10m": (0.0, 60.0),          # m/s
    "wind_gusts_10m": (0.0, 80.0),          # m/s
    "solar_radiation": (0.0, 1500.0),        # W/m²
    "direct_radiation": (0.0, 1200.0)        # W/m²
}

REQUIRED_COLUMNS = [
    "timestamp",
    "station_id",
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


class ValidationError(Exception):
    """Raised when data validation fails critical integrity checks."""
    pass


def validate_station_df(df: pd.DataFrame, expected_station_id: str = None) -> Dict:
    """
    Validate an individual station DataFrame against all quality criteria.
    Returns a comprehensive validation report dictionary.
    """
    report = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "metrics": {}
    }

    # 1. Check required columns and schema
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        msg = f"Thieu cac cot bat buoc: {missing_cols}"
        report["errors"].append(msg)
        report["is_valid"] = False
        raise ValidationError(msg)

    # 2. Check station_id stability
    unique_stations = df["station_id"].unique()
    if len(unique_stations) != 1:
        msg = f"Phat hien nhieu hon 1 station_id trong cung 1 tap tin: {unique_stations}"
        report["errors"].append(msg)
        report["is_valid"] = False
    elif expected_station_id and unique_stations[0] != expected_station_id:
        msg = f"station_id {unique_stations[0]} khong khop voi ky vong {expected_station_id}"
        report["errors"].append(msg)
        report["is_valid"] = False

    station_name = str(unique_stations[0]) if len(unique_stations) > 0 else "UNKNOWN"
    total_rows = len(df)
    report["metrics"]["total_rows"] = total_rows
    report["metrics"]["station_id"] = station_name

    # 3. Check uniqueness of (station_id, timestamp)
    duplicates = df.duplicated(subset=["station_id", "timestamp"]).sum()
    report["metrics"]["duplicate_keys"] = int(duplicates)
    report["metrics"]["duplicate_pct"] = float(duplicates / total_rows * 100) if total_rows > 0 else 0.0
    if duplicates > 0:
        msg = f"Khoa (station_id, timestamp) bi trung lap: {duplicates} ban ghi ({report['metrics']['duplicate_pct']:.4f}%)"
        report["errors"].append(msg)
        report["is_valid"] = False

    # 4. Check timestamp parsing, monotonic order, and fixed 5-min intervals
    try:
        t_series = pd.to_datetime(df["timestamp"])
    except Exception as e:
        msg = f"Loi parse timestamp ISO: {e}"
        report["errors"].append(msg)
        report["is_valid"] = False
        return report

    is_monotonic = t_series.is_monotonic_increasing
    report["metrics"]["is_monotonic_increasing"] = bool(is_monotonic)
    if not is_monotonic:
        msg = "Chuoi thoi gian khong tang dan don dieu nghiem ngat!"
        report["errors"].append(msg)
        report["is_valid"] = False

    deltas = t_series.diff().dropna().unique()
    expected_delta = pd.Timedelta(minutes=5)
    report["metrics"]["intervals"] = [str(d) for d in deltas]
    if len(deltas) != 1 or deltas[0] != expected_delta:
        msg = f"Buoc thoi gian khong dong nhat 5 phut! Cac buoc phat hien: {deltas}"
        report["errors"].append(msg)
        report["is_valid"] = False

    # 5. Check missing values (NaN rates)
    nan_summary = {}
    for col in REQUIRED_COLUMNS:
        null_count = int(df[col].isnull().sum())
        null_pct = float(null_count / total_rows * 100) if total_rows > 0 else 0.0
        nan_summary[col] = {"count": null_count, "pct": round(null_pct, 4)}
        if null_count > 0:
            report["warnings"].append(f"Cot {col} co {null_count} gia tri thieu ({null_pct:.2f}%)")
    report["metrics"]["missing_values"] = nan_summary

    # 6. Check physical range boundaries
    out_of_bounds = {}
    for var, (vmin, vmax) in PHYSICAL_RANGES.items():
        if var in df.columns:
            series = pd.to_numeric(df[var], errors="coerce")
            below = int((series < vmin).sum())
            above = int((series > vmax).sum())
            total_oob = below + above
            if total_oob > 0:
                out_of_bounds[var] = {
                    "below_min": below,
                    "above_max": above,
                    "total": total_oob,
                    "pct": round(total_oob / total_rows * 100, 4),
                    "range": [vmin, vmax]
                }
                report["errors"].append(f"Cot {var} co {total_oob} gia tri ngoai mien vat ly [{vmin}, {vmax}]")
                report["is_valid"] = False
    report["metrics"]["out_of_bounds"] = out_of_bounds

    return report


def validate_multi_station_sync(station_dfs: Dict[str, pd.DataFrame]) -> Dict:
    """
    Verify cross-station clock synchronization and alignment across all 6 stations.
    """
    report = {
        "is_synced": True,
        "errors": [],
        "station_counts": {}
    }

    station_names = list(station_dfs.keys())
    if len(station_names) < 2:
        return report

    first_st = station_names[0]
    base_timestamps = pd.to_datetime(station_dfs[first_st]["timestamp"]).reset_index(drop=True)
    base_len = len(base_timestamps)

    for st in station_names:
        df = station_dfs[st]
        report["station_counts"][st] = len(df)
        if len(df) != base_len:
            report["is_synced"] = False
            report["errors"].append(f"Tram {st} co so luong ban ghi ({len(df)}) khac voi tram {first_st} ({base_len})")
            continue

        st_timestamps = pd.to_datetime(df["timestamp"]).reset_index(drop=True)
        mismatches = (base_timestamps != st_timestamps).sum()
        if mismatches > 0:
            report["is_synced"] = False
            report["errors"].append(f"Lech dong ho (clock drift) giua {st} va {first_st}: {mismatches} moc thoi gian khong khop!")

    return report

