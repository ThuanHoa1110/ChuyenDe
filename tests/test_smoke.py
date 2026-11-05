"""
Smoke test suite for Phase 0 verification.
Ensures repository setup, directory structure, configurations, and sample data integrity.
"""

import glob
import os
import pandas as pd
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_package_metadata():
    """Verify package import and versioning."""
    import src.weather as weather
    assert hasattr(weather, "__version__")
    assert weather.__version__ == "0.1.0"


def test_required_directories_exist():
    """Verify all key directories required by repo architecture exist."""
    required_dirs = [
        "configs",
        "data",
        "data/sample",
        "src/weather",
        "src/weather/data",
        "src/weather/models",
        "src/weather/api",
        "docs",
        "scripts",
        "tests"
    ]
    for d in required_dirs:
        full_path = os.path.join(BASE_DIR, d)
        assert os.path.isdir(full_path), f"Required directory {d} missing!"


def test_default_config_validity():
    """Verify default.yaml exists and contains all required architectural settings."""
    cfg_path = os.path.join(BASE_DIR, "configs", "default.yaml")
    assert os.path.isfile(cfg_path), "configs/default.yaml does not exist!"

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert "project" in cfg
    assert "data" in cfg
    assert "model" in cfg
    assert "split" in cfg

    assert len(cfg["data"]["stations"]) == 6
    assert cfg["data"]["lookback_steps"] == 72
    assert cfg["data"]["horizon_steps"] == 12
    assert cfg["model"]["num_outputs"] == 6


def test_sample_data_integrity():
    """Verify 6 sample station files are intact, have 1000 rows, 5-min intervals, and 0 NaNs."""
    sample_dir = os.path.join(BASE_DIR, "data", "sample")
    files = sorted(glob.glob(os.path.join(sample_dir, "*.csv")))
    assert len(files) == 6, f"Expected 6 sample files, found {len(files)}"

    expected_stations = [
        "ST01_HOANKIEM",
        "ST02_BADINH",
        "ST03_CAUGIAY",
        "ST04_HADONG",
        "ST05_DONGANH",
        "ST06_SOCSON"
    ]

    for idx, f in enumerate(files):
        df = pd.read_csv(f)
        assert len(df) == 1000, f"{f} should have 1000 rows, found {len(df)}"
        assert len(df.columns) == 13, f"{f} should have 13 columns, found {len(df.columns)}"
        assert df["station_id"].iloc[0] == expected_stations[idx]
        assert df.isnull().sum().sum() == 0, f"{f} contains NaN values!"

        # Check monotonic timestamps and 5-min delta
        t_series = pd.to_datetime(df["timestamp"])
        assert t_series.is_monotonic_increasing, f"{f} timestamps are not strictly increasing!"
        deltas = t_series.diff().dropna().unique()
        assert len(deltas) == 1, f"{f} has irregular intervals: {deltas}"
        assert deltas[0] == pd.Timedelta(minutes=5), f"{f} interval is not 5 minutes!"


def test_security_and_ignore_rules():
    """Verify .gitignore and .env.example conform to security guidelines."""
    gitignore_path = os.path.join(BASE_DIR, ".gitignore")
    assert os.path.isfile(gitignore_path), ".gitignore must exist!"

    with open(gitignore_path, "r", encoding="utf-8") as f:
        ignore_content = f.read()

    assert ".env" in ignore_content
    assert "data/raw" in ignore_content
    assert "checkpoints" in ignore_content
    assert "artifacts" in ignore_content

    example_env_path = os.path.join(BASE_DIR, ".env.example")
    assert os.path.isfile(example_env_path), ".env.example must exist!"

    with open(example_env_path, "r", encoding="utf-8") as f:
        env_content = f.read()

    assert "HF_TOKEN=" in env_content
    assert "KAGGLE_USERNAME=" in env_content
    assert "DOCKERHUB_USERNAME=" in env_content


def test_documentation_deliverables_exist():
    """Verify Phase 0 documentation deliverables exist."""
    assert os.path.isfile(os.path.join(BASE_DIR, "docs", "data_inventory.md"))
    assert os.path.isfile(os.path.join(BASE_DIR, "docs", "licensing_decisions.md"))
    assert os.path.isfile(os.path.join(BASE_DIR, "data", "README.md"))

