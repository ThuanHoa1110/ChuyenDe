"""
Helper script to generate the 20 standalone test script modules in testing_report/scripts/
Matching the reference naming conventions:
- scripts.tc01_health_availability
- scripts.tc02_input_validation
- scripts.tc03_e2e_workflow
- scripts.tc04_output_integrity
- scripts.tc05_prediction_quality
- scripts.tc06_noise_robustness
- scripts.tc07_temporal_consistency
- scripts.tc08_ood_behavior
- scripts.tc09_external_service_failure
- scripts.tc10_inference_failure
- scripts.at01_malformed_input
- scripts.at02_oversized_payload
- scripts.at03_api_flooding
- scripts.at04_adversarial_noise
- scripts.at05_temporal_manipulation
- scripts.at06_ood_input
- scripts.at07_invalid_numerics
- scripts.at08_parameter_tampering
- scripts.at09_resource_exhaustion
- scripts.at10_tensor_shape_tampering
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "testing_report" / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

TEST_MODULES = [
    ("tc01_health_availability.py", "run_tc01", "TC01 – Health check & endpoint availability"),
    ("tc02_input_validation.py", "run_tc02", "TC02 – Input validation & boundary constraints"),
    ("tc03_e2e_workflow.py", "run_tc03", "TC03 – E2E workflow & inference latency"),
    ("tc04_output_integrity.py", "run_tc04", "TC04 – Output integrity & determinism"),
    ("tc05_prediction_quality.py", "run_tc05", "TC05 – Model accuracy benchmark"),
    ("tc06_noise_robustness.py", "run_tc06", "TC06 – Noise robustness analysis"),
    ("tc07_temporal_consistency.py", "run_tc07", "TC07 – Temporal consistency & sensor dropout"),
    ("tc08_ood_behavior.py", "run_tc08", "TC08 – OOD extreme climate behavior"),
    ("tc09_external_service_failure.py", "run_tc09", "TC09 – Mock external weather service failure"),
    ("tc10_inference_failure.py", "run_tc10", "TC10 – Mock inference engine failure & corrupt checkpoint"),
    ("at01_malformed_input.py", "run_at01", "AT01 – Malformed input & Pydantic schema pollution"),
    ("at02_oversized_payload.py", "run_at02", "AT02 – Oversized payload & Buffer overflow DoS"),
    ("at03_api_flooding.py", "run_at03", "AT03 – API query flooding & concurrency stress"),
    ("at04_adversarial_noise.py", "run_at04", "AT04 – Adversarial perturbation (FGSM & PGD attacks)"),
    ("at05_temporal_manipulation.py", "run_at05", "AT05 – Temporal manipulation & clock drift"),
    ("at06_ood_input.py", "run_at06", "AT06 – Out-of-distribution synthetic injection"),
    ("at07_invalid_numerics.py", "run_at07", "AT07 – Invalid numerics (NaN / Infinity injection)"),
    ("at08_parameter_tampering.py", "run_at08", "AT08 – Parameter tampering & Path traversal"),
    ("at09_resource_exhaustion.py", "run_at09", "AT09 – Resource exhaustion via long-horizon forecast"),
    ("at10_tensor_shape_tampering.py", "run_at10", "AT10 – Tensor dimension & shape tampering"),
]

TEMPLATE = '''"""
Standalone Executable Script for {title}
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
from testing_report.run_all import {func_name}

def main():
    print("=" * 70)
    print("Executing {title}...")
    print("=" * 70)
    with TestClient(app) as client:
        result = {func_name}(client)
    print(f"Result: {{result.get('verdict')}}")

if __name__ == "__main__":
    main()
'''

def generate_scripts():
    for filename, func_name, title in TEST_MODULES:
        filepath = SCRIPTS_DIR / filename
        content = TEMPLATE.format(func_name=func_name, title=title)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    generate_scripts()

