"""
Script kiểm kê và tính mã băm SHA-256 cho 6 trạm dữ liệu mẫu tại Hà Nội.
Phục vụ Bước 0.2 trong Kế hoạch chi tiết.
"""

import hashlib
import glob
import os
import sys
import pandas as pd

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def compute_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_dir = os.path.join(base_dir, "data", "sample")
    csv_files = sorted(glob.glob(os.path.join(sample_dir, "*.csv")))

    print(f"Kiểm tra thư mục: {sample_dir}")
    print(f"Số lượng file tìm thấy: {len(csv_files)}\n")

    results = []

    for f in csv_files:
        fname = os.path.basename(f)
        sha = compute_sha256(f)
        df = pd.read_csv(f)

        t_series = pd.to_datetime(df["timestamp"])
        diffs = t_series.diff().dropna().unique()

        record = {
            "file": fname,
            "station_id": str(df["station_id"].iloc[0]),
            "rows": len(df),
            "columns": len(df.columns),
            "start": str(df["timestamp"].iloc[0]),
            "end": str(df["timestamp"].iloc[-1]),
            "interval": str(diffs[0]) if len(diffs) > 0 else "N/A",
            "is_monotonic": t_series.is_monotonic_increasing,
            "nulls": int(df.isnull().sum().sum()),
            "temp_min": float(df["temperature"].min()),
            "temp_max": float(df["temperature"].max()),
            "sha256": sha,
        }
        results.append(record)

        print(f"Trạm: {record['station_id']} ({fname})")
        print(f"  SHA-256: {record['sha256']}")
        print(f"  Số dòng: {record['rows']} | Số cột: {record['columns']}")
        print(f"  Khoảng thời gian: {record['start']} -> {record['end']}")
        print(f"  Chu kỳ: {record['interval']} | Tăng dần liên tục: {record['is_monotonic']}")
        print(f"  Số ô NaN: {record['nulls']}")
        print(f"  Khoảng nhiệt độ: {record['temp_min']}°C -> {record['temp_max']}°C\n")

    return results


if __name__ == "__main__":
    main()
