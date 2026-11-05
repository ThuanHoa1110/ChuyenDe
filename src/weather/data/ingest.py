"""
Data Ingestion Module for Hanoi Weather Forecasting Project.
Handles immutable raw data acquisition, SHA-256 hashing, and manifest generation.
Follows Phase 1, Step 1.1 specifications.
"""

import os
import sys
import glob
import json
import shutil
import hashlib
from datetime import datetime, timezone
import pandas as pd
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_SOURCE = r"E:\ChuyendeTTNTvaKHDL\data\stations"


def compute_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file efficiently in 64KB chunks."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def count_file_lines(filepath: str) -> int:
    """Count number of data records (excluding header) efficiently."""
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1


def inspect_csv_metadata(filepath: str) -> dict:
    """Read head and tail of CSV to extract start/end timestamps and station ID."""
    df_head = pd.read_csv(filepath, nrows=2)
    start_time = str(df_head["timestamp"].iloc[0])
    station_id = str(df_head["station_id"].iloc[0])

    # Find total lines to read last line
    total_lines = count_file_lines(filepath)
    df_tail = pd.read_csv(filepath, skiprows=range(1, total_lines), nrows=2)
    end_time = str(df_tail["timestamp"].iloc[-1])

    return {
        "station_id": station_id,
        "start_time": start_time,
        "end_time": end_time,
        "row_count": total_lines,
        "columns": df_head.columns.tolist()
    }


def run_ingest(source_dir: str = None, target_dir: str = None) -> dict:
    """
    Ingest station files from source directory into target immutable storage.
    Generates manifests/raw.json and logs actions.
    """
    if source_dir is None:
        source_dir = os.getenv("DATA_RAW_SOURCE_DIR", DEFAULT_SOURCE)
    if target_dir is None:
        target_dir = os.path.join(BASE_DIR, "data", "private", "raw_stations")

    os.makedirs(target_dir, exist_ok=True)
    manifest_dir = os.path.join(BASE_DIR, "manifests")
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, "raw.json")

    print(f"=== [Ingest] Bat dau qua trinh nạp du lieu ===")
    print(f"Nguon du lieu: {source_dir}")
    print(f"Thu muc dich:  {target_dir}")

    source_files = sorted(glob.glob(os.path.join(source_dir, "*.csv")))
    if not source_files:
        raise FileNotFoundError(f"Khong tim thay file CSV nao tai thu muc nguon: {source_dir}")

    manifest_entries = []
    total_records = 0

    for src_file in source_files:
        fname = os.path.basename(src_file)
        dst_file = os.path.join(target_dir, fname)

        src_hash = compute_sha256(src_file)
        already_exists = False

        if os.path.exists(dst_file):
            dst_hash = compute_sha256(dst_file)
            if src_hash == dst_hash:
                print(f"[San sang] {fname} da ton tai va khop ma bam SHA-256. Bo qua sao chep de bao toan tinh bat bien.")
                already_exists = True

        if not already_exists:
            print(f"[Sao chep] Dang copy {fname} sang {target_dir}...")
            shutil.copy2(src_file, dst_file)
            dst_hash = compute_sha256(dst_file)
            assert src_hash == dst_hash, f"Loi toan ven SHA-256 sau khi copy file {fname}!"

        # Extract metadata
        meta = inspect_csv_metadata(dst_file)
        total_records += meta["row_count"]

        entry = {
            "file_name": fname,
            "station_id": meta["station_id"],
            "source_path": src_file,
            "storage_path": os.path.relpath(dst_file, BASE_DIR).replace("\\", "/"),
            "sha256": dst_hash,
            "file_size_bytes": os.path.getsize(dst_file),
            "record_count": meta["row_count"],
            "start_timestamp": meta["start_time"],
            "end_timestamp": meta["end_time"],
            "time_frequency": "5min",
            "timezone": "Asia/Ho_Chi_Minh (UTC+7)",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "columns": meta["columns"]
        }
        manifest_entries.append(entry)

        print(f"  -> Tram: {meta['station_id']} | Ban ghi: {meta['row_count']:,} | Hash: {dst_hash[:16]}...")

    manifest_data = {
        "dataset_name": "hanoi-weather-multi-station-private",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_stations": len(manifest_entries),
        "total_records": total_records,
        "stations": manifest_entries
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print(f"\n[Thanh cong] Da xuat manifest tai: {manifest_path}")
    print(f"Tong so tram: {len(manifest_entries)} | Tong so ban ghi: {total_records:,}")
    return manifest_data


if __name__ == "__main__":
    run_ingest()
