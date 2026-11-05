"""
Unit tests for Kaggle Release Artifacts and Public Deliverables (Phase 1, Step 1.3).
Verifies metadata structure, Data Card completeness, and archive file integrity.
"""

import os
import json
import hashlib
import gzip
import pytest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_DIR = os.path.join(BASE_DIR, "release", "public")
METADATA_FILE = os.path.join(RELEASE_DIR, "dataset-metadata.json")
DATA_CARD_FILE = os.path.join(RELEASE_DIR, "DATA_CARD.md")
DATA_FILE = os.path.join(RELEASE_DIR, "weather_wide_synced.csv.gz")
DATA_QUALITY_REPORT = os.path.join(BASE_DIR, "reports", "data_quality.md")


def compute_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def test_dataset_metadata_validity():
    """Validates dataset-metadata.json conform to Kaggle CLI specifications."""
    assert os.path.exists(METADATA_FILE), "dataset-metadata.json must exist in release/public/"
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "title" in meta and len(meta["title"]) > 5
    assert "id" in meta and "/" in meta["id"]
    assert "licenses" in meta and len(meta["licenses"]) > 0
    assert meta["licenses"][0]["name"] in ["CC-BY-4.0", "CC0-1.0", "MIT", "Apache-2.0"]


def test_data_card_completeness():
    """Validates DATA_CARD.md contains all 6 stations and required sections."""
    assert os.path.exists(DATA_CARD_FILE), "DATA_CARD.md must exist in release/public/"
    with open(DATA_CARD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Check 6 stations
    stations = [
        "ST01_HOANKIEM", "ST02_BADINH", "ST03_CAUGIAY",
        "ST04_HADONG", "ST05_DONGANH", "ST06_SOCSON"
    ]
    for st in stations:
        assert st in content, f"DATA_CARD.md missing station {st}"

    # Check essential units and fields
    required_keywords = [
        "temperature", "humidity", "surface_pressure", "CC-BY-4.0",
        "Asia/Ho_Chi_Minh", "5min"
    ]
    for kw in required_keywords:
        assert kw in content, f"DATA_CARD.md missing keyword {kw}"


def test_release_dataset_integrity_and_checksum():
    """Validates weather_wide_synced.csv.gz integrity and hash consistency."""
    assert os.path.exists(DATA_FILE), "weather_wide_synced.csv.gz must exist"
    assert os.path.getsize(DATA_FILE) > 10 * 1024 * 1024  # Must be > 10MB compressed

    # Compute hash and match data quality report
    actual_sha = compute_sha256(DATA_FILE)

    assert os.path.exists(DATA_QUALITY_REPORT), "reports/data_quality.md must exist"
    with open(DATA_QUALITY_REPORT, "r", encoding="utf-8") as f:
        report_content = f.read()

    assert actual_sha in report_content, f"SHA-256 {actual_sha} must match data_quality.md"


def test_release_dataset_sample_schema():
    """Validates decompressed gzip stream matches the 67-column synchronized schema."""
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as f:
        # Read first 10 rows
        df_sample = pd.read_csv(f, nrows=10)

    assert df_sample.shape[1] == 67, f"Expected 67 columns, got {df_sample.shape[1]}"
    assert "timestamp" in df_sample.columns
    # Check that each station has temperature column
    for i in range(1, 7):
        st_prefix = f"st0{i}"
        target_col = f"{st_prefix}_temperature"
        assert target_col in df_sample.columns, f"Missing target temperature column {target_col}"
