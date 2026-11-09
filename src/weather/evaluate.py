"""
Evaluation and Baseline Comparison Pipeline (Phase 2, Step 2.2).
Trains and evaluates:
1. Persistence Baseline
2. Ridge Regression Baseline
3. LightGBM Baseline

Computes station-level and macro MAE, RMSE, MedAE, latency,
performs manual verification on 5 samples, and generates comparison CSV and figures.
"""

import os
import sys
import time
import argparse
import yaml
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.weather.data.window import (
    split_and_window_dataset,
    create_sliding_windows,
    TARGET_STATIONS
)
from src.weather.models.baseline import (
    PersistenceBaseline,
    RidgeBaselineModel,
    LightGBMBaselineModel,
    extract_tabular_features
)

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, latency_ms: float = 0.0) -> dict:
    """Computes MAE, RMSE, MedAE per station and macro average."""
    errors = y_pred - y_true
    abs_errors = np.abs(errors)
    sq_errors = errors ** 2

    mae_per_station = np.mean(abs_errors, axis=0)
    rmse_per_station = np.sqrt(np.mean(sq_errors, axis=0))
    medae_per_station = np.median(abs_errors, axis=0)

    macro_mae = float(np.mean(mae_per_station))
    macro_rmse = float(np.mean(rmse_per_station))
    macro_medae = float(np.mean(medae_per_station))

    metrics = {
        "macro_mae": round(macro_mae, 4),
        "macro_rmse": round(macro_rmse, 4),
        "macro_medae": round(macro_medae, 4),
        "latency_ms_per_sample": round(latency_ms, 4)
    }

    for i, st in enumerate(TARGET_STATIONS):
        st_name = st.replace("_temperature", "").upper()
        metrics[f"{st_name}_mae"] = round(float(mae_per_station[i]), 4)
        metrics[f"{st_name}_rmse"] = round(float(rmse_per_station[i]), 4)
        metrics[f"{st_name}_medae"] = round(float(medae_per_station[i]), 4)

    return metrics


def verify_metrics_manually_on_samples(y_true: np.ndarray, y_pred: np.ndarray, n_samples: int = 5):
    """Prints manual step-by-step verification on 5 samples."""
    print("\n--- [Kiểm Tra Thủ Công Metric Trên 5 Mẫu Đầu Tiên] ---")
    sub_true = y_true[:n_samples]
    sub_pred = y_pred[:n_samples]

    for k in range(n_samples):
        sample_abs_err = np.abs(sub_pred[k] - sub_true[k])
        print(f"Mẫu {k+1}:")
        print(f"  Thực tế (y)  : {np.round(sub_true[k], 2)}")
        print(f"  Dự báo (y_hat): {np.round(sub_pred[k], 2)}")
        print(f"  Sai số tuyệt đối (|y - y_hat|): {np.round(sample_abs_err, 2)} | MAE mẫu: {np.mean(sample_abs_err):.4f}")

    manual_macro_mae = np.mean(np.abs(sub_pred - sub_true))
    manual_macro_rmse = np.sqrt(np.mean((sub_pred - sub_true) ** 2))
    print(f">> Tính tay trên {n_samples} mẫu: Macro MAE = {manual_macro_mae:.4f} °C, Macro RMSE = {manual_macro_rmse:.4f} °C\n")


def plot_baseline_comparison(
    timestamps: np.ndarray,
    y_true: np.ndarray,
    preds_dict: dict,
    output_png: str,
    num_plot_points: int = 150
):
    """Generates comparison charts: Actual vs Predicted across models for representative station."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), dpi=150)
    plt.subplots_adjust(hspace=0.35)

    n_pts = min(num_plot_points, len(timestamps))
    t_slice = pd.to_datetime(timestamps[:n_pts])
    st_idx = 0  # ST01 Hoan Kiem
    st_name = "ST01 (Hoàn Kiếm)"

    # Plot 1: Time series actual vs predicted
    ax1 = axes[0]
    ax1.plot(t_slice, y_true[:n_pts, st_idx], label="Thực Tế (Ground Truth)", color="black", linewidth=2.0)
    colors = {"Persistence": "#e74c3c", "Ridge": "#3498db", "LightGBM": "#2ecc71"}

    for model_name, y_pred in preds_dict.items():
        c = colors.get(model_name, "orange")
        ax1.plot(t_slice, y_pred[:n_pts, st_idx], label=f"Dự báo {model_name}", color=c, linestyle="--", alpha=0.85)

    ax1.set_title(f"Dự Báo Nhiệt Độ Sau 60 Phút Tại {st_name} - So Sánh Các Mô Hình Baseline", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Nhiệt độ (°C)", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left")

    # Plot 2: Absolute error over time
    ax2 = axes[1]
    for model_name, y_pred in preds_dict.items():
        err = np.abs(y_pred[:n_pts, st_idx] - y_true[:n_pts, st_idx])
        c = colors.get(model_name, "orange")
        ax2.plot(t_slice, err, label=f"Lỗi tuyệt đối ({model_name})", color=c, alpha=0.85)

    ax2.set_title(f"Sai Số Tuyệt Đối (|y - ŷ|) Theo Thời Gian Tại {st_name}", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Thời gian", fontsize=11)
    ax2.set_ylabel("Sai số tuyệt đối (°C)", fontsize=11)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper left")

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, bbox_inches="tight")
    plt.close()
    print(f"📊 Đã lưu biểu đồ so sánh: {output_png}")


def run_evaluation(
    config_path: str = "configs/split.yaml",
    use_full_dataset: bool = False
) -> pd.DataFrame:
    print("=" * 65)
    print("🚀 BƯỚC 2.2: ĐÁNH GIÁ VÀ SO SÁNH CÁC MÔ HÌNH BASELINE")
    print("=" * 65)

    full_config_path = os.path.join(BASE_DIR, config_path)
    with open(full_config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    lookback = cfg["dataset"]["lookback_steps"]
    horizon = cfg["dataset"]["horizon_steps"]
    random_seed = cfg["dataset"]["random_seed"]

    # Select data path
    if use_full_dataset and os.path.exists(os.path.join(BASE_DIR, cfg["data_paths"]["full_wide_csv"])):
        data_path = os.path.join(BASE_DIR, cfg["data_paths"]["full_wide_csv"])
        print(f"📂 Đang nạp tập dữ liệu toàn vẹn: {data_path}")
        df = pd.read_csv(data_path, compression="gzip")
    else:
        sample_path = os.path.join(BASE_DIR, cfg["data_paths"]["sample_wide_csv"])
        print(f"📂 Đang nạp tập dữ liệu mẫu chuẩn hoá: {sample_path}")
        df = pd.read_csv(sample_path)

    print(f"   Kích thước dữ liệu: {df.shape[0]:,} dòng x {df.shape[1]} cột")

    # 1. Split and window dataset
    artifact_dir = os.path.join(BASE_DIR, "artifacts")
    manifest_path = os.path.join(BASE_DIR, cfg["data_paths"]["manifest_path"])

    print("\n[1/4] Phân chia dữ liệu theo thời gian (Train 70%, Val 15%, Test 15%)...")
    split_res = split_and_window_dataset(
        df=df,
        train_ratio=cfg["split"]["train_ratio"],
        val_ratio=cfg["split"]["val_ratio"],
        test_ratio=cfg["split"]["test_ratio"],
        lookback=lookback,
        horizon=horizon,
        artifact_dir=artifact_dir,
        manifest_path=manifest_path,
        data_version=cfg["dataset"]["data_version"],
        random_seed=random_seed
    )

    train_data = split_res["train"]
    test_data = split_res["test"]
    feature_cols = train_data["feature_cols"]

    y_test_true = test_data["y"]
    test_timestamps = test_data["timestamps_target"]
    num_test_samples = len(y_test_true)
    print(f"   Số lượng mẫu tập Test: {num_test_samples:,}")

    # 2. Prepare Tabular Features for Ridge & LightGBM
    print("\n[2/4] Trích xuất đặc trưng lag & chu kỳ thời gian...")
    X_train_tab = extract_tabular_features(train_data["X"], train_data["timestamps_t"], feature_cols)
    X_test_tab = extract_tabular_features(test_data["X"], test_data["timestamps_t"], feature_cols)
    y_train = train_data["y"]

    # 3. Fit and evaluate models
    print("\n[3/4] Huấn luyện và dự báo các mô hình Baseline...")
    results = []
    predictions_dict = {}

    # Model 1: Persistence (ŷ at t+12 = temperature at t in °C)
    print("  -> Đang chạy Persistence Baseline...")
    t0 = time.perf_counter()
    y_pred_pers = test_data["y_persistence"]
    pers_latency = ((time.perf_counter() - t0) / num_test_samples) * 1000.0
    pers_metrics = compute_metrics(y_test_true, y_pred_pers, pers_latency)
    pers_metrics["model"] = "Persistence"
    results.append(pers_metrics)
    predictions_dict["Persistence"] = y_pred_pers

    # Model 2: Ridge
    print("  -> Đang huấn luyện Ridge Regression Baseline...")
    ridge_model = RidgeBaselineModel(alpha=1.0, random_seed=random_seed)
    ridge_model.fit(X_train_tab, y_train)
    t0 = time.perf_counter()
    y_pred_ridge = ridge_model.predict(X_test_tab)
    ridge_latency = ((time.perf_counter() - t0) / num_test_samples) * 1000.0
    ridge_metrics = compute_metrics(y_test_true, y_pred_ridge, ridge_latency)
    ridge_metrics["model"] = "Ridge"
    results.append(ridge_metrics)
    predictions_dict["Ridge"] = y_pred_ridge

    # Model 3: LightGBM
    print("  -> Đang huấn luyện LightGBM Baseline...")
    lgb_model = LightGBMBaselineModel(n_estimators=80, learning_rate=0.05, random_seed=random_seed)
    lgb_model.fit(X_train_tab, y_train)
    t0 = time.perf_counter()
    y_pred_lgb = lgb_model.predict(X_test_tab)
    lgb_latency = ((time.perf_counter() - t0) / num_test_samples) * 1000.0
    lgb_metrics = compute_metrics(y_test_true, y_pred_lgb, lgb_latency)
    lgb_metrics["model"] = "LightGBM"
    results.append(lgb_metrics)
    predictions_dict["LightGBM"] = y_pred_lgb

    # Manual verification check on Persistence & LightGBM
    verify_metrics_manually_on_samples(y_test_true, y_pred_lgb, n_samples=5)

    # 4. Save metrics report and visualizations
    print("[4/4] Lưu trữ báo cáo kết quả nghiệm thu...")
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    metrics_df = pd.DataFrame(results)
    # Reorder columns with model first
    cols = ["model", "macro_mae", "macro_rmse", "macro_medae", "latency_ms_per_sample"] + [
        c for c in metrics_df.columns if c not in ["model", "macro_mae", "macro_rmse", "macro_medae", "latency_ms_per_sample"]
    ]
    metrics_df = metrics_df[cols]

    baselines_csv_path = os.path.join(reports_dir, "baselines.csv")
    metrics_df.to_csv(baselines_csv_path, index=False)
    print(f"📄 Đã lưu bảng so sánh metrics: {baselines_csv_path}")

    # Save actual vs predictions
    pred_records = {"timestamp_target": test_timestamps}
    for i, st in enumerate(TARGET_STATIONS):
        st_short = st.replace("_temperature", "").upper()
        pred_records[f"{st_short}_actual"] = y_test_true[:, i]
        for m_name, preds in predictions_dict.items():
            pred_records[f"{st_short}_{m_name}"] = preds[:, i]

    pred_df = pd.DataFrame(pred_records)
    pred_csv_path = os.path.join(reports_dir, "predictions_baseline.csv")
    pred_df.to_csv(pred_csv_path, index=False)
    print(f"📄 Đã lưu chuỗi dự báo chi tiết: {pred_csv_path}")

    # Generate plot
    plot_path = os.path.join(reports_dir, "baseline_comparison.png")
    plot_baseline_comparison(test_timestamps, y_test_true, predictions_dict, plot_path)

    # Print summary table
    print("\n" + "=" * 65)
    print("📊 BẢNG TỔNG HỢP SO SÁNH METRICS BASELINES (Tập Test)")
    print("=" * 65)
    print(metrics_df[["model", "macro_mae", "macro_rmse", "macro_medae", "latency_ms_per_sample"]].to_string(index=False))
    print("=" * 65 + "\n")

    return metrics_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate baseline forecasting models")
    parser.add_argument("--config", type=str, default="configs/split.yaml", help="Path to split config")
    parser.add_argument("--full", action="store_true", help="Use full 10-year dataset")
    parser.add_argument("--checkpoint", type=str, default="", help="Checkpoint path (reserved for DL models)")
    args = parser.parse_args()

    run_evaluation(config_path=args.config, use_full_dataset=args.full)
