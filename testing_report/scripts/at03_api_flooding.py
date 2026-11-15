"""
Standalone Executable Script for AT03 – API query flooding & concurrency stress
Hanoi Multi-Station Weather Forecasting System (Buổi 4: Kiểm thử và Tấn công Hệ thống AI).
Student: Nguyễn Thuận Hòa | MSV: 2351260652 | Lớp: 65TTNT | ĐH Thủy Lợi
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.weather.api.app import app
from testing_report.run_all import run_at03

def main():
    print("=" * 70)
    print("Executing AT03 – API query flooding & concurrency stress...")
    print("=" * 70)
    with TestClient(app) as client:
        result = run_at03(client)
    print(f"Result: {result.get('verdict')}")

if __name__ == "__main__":
    main()
