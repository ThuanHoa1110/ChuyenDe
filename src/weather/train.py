"""
Training Pipeline for DINOv3 Temperature Forecaster (Phase 3, Step 3.2).
Trains the regression head with frozen DINOv3 ViT-S/16 backbone using Huber loss,
evaluates on validation set with early stopping, and saves the best model checkpoint.
"""

import os
import sys
import time
import json
import hashlib
import argparse
from typing import Optional, Dict, List, Tuple, Union
import yaml
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.weather.data.window import split_and_window_dataset, TARGET_STATIONS
from src.weather.data.image import batch_windows_to_images
from src.weather.models.dinov3_forecaster import DINOv3_Forecaster

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def compute_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def train_dinov3(
    config_path: str = "configs/dinov3.yaml",
    max_epochs_override: Optional[int] = None
) -> dict:
    print("=" * 65)
    print("🚀 BƯỚC 3.2: HUẤN LUYỆN DINOv3 TEMPERATURE FORECASTER")
    print("=" * 65)

    full_cfg_path = os.path.join(BASE_DIR, config_path)
    with open(full_cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # 1. Device selection
    device_cfg = cfg["training"].get("device", "auto")
    if device_cfg == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_cfg)
    print(f"🖥️ Thiết bị tính toán (Device): {device}")
    if device.type == "cuda":
        print(f"   GPU: {torch.cuda.get_device_name(0)}")

    # Set random seed
    seed = cfg["training"].get("random_seed", 42)
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    # 2. Data Preparation
    split_cfg_path = os.path.join(BASE_DIR, cfg["paths"]["split_config"])
    with open(split_cfg_path, "r", encoding="utf-8") as f:
        split_cfg = yaml.safe_load(f)

    sample_path = os.path.join(BASE_DIR, split_cfg["data_paths"]["sample_wide_csv"])
    print(f"📂 Đang nạp dữ liệu: {sample_path}")
    df = pd.read_csv(sample_path)

    split_res = split_and_window_dataset(
        df=df,
        train_ratio=split_cfg["split"]["train_ratio"],
        val_ratio=split_cfg["split"]["val_ratio"],
        test_ratio=split_cfg["split"]["test_ratio"],
        lookback=split_cfg["dataset"]["lookback_steps"],
        horizon=split_cfg["dataset"]["horizon_steps"],
        artifact_dir=os.path.join(BASE_DIR, "artifacts"),
        manifest_path=os.path.join(BASE_DIR, split_cfg["data_paths"]["manifest_path"]),
        data_version=split_cfg["dataset"]["data_version"],
        random_seed=seed
    )

    train_data = split_res["train"]
    val_data = split_res["val"]
    test_data = split_res["test"]
    feature_cols = train_data["feature_cols"]

    # 3. Convert windows to 3-channel image tensors
    print("\n🖼️ Đang chuyển đổi chuỗi cửa sổ sang ma trận ảnh 3 kênh (224 x 224)...")
    t0 = time.perf_counter()
    X_train_img = batch_windows_to_images(train_data["X"], feature_cols, target_size=(224, 224))
    X_val_img = batch_windows_to_images(val_data["X"], feature_cols, target_size=(224, 224))
    X_test_img = batch_windows_to_images(test_data["X"], feature_cols, target_size=(224, 224))
    print(f"   Thời gian mã hóa ảnh: {time.perf_counter() - t0:.2f}s")
    print(f"   Train images: {X_train_img.shape} | Val images: {X_val_img.shape} | Test images: {X_test_img.shape}")

    # Create PyTorch datasets and loaders
    batch_size = cfg["training"]["batch_size"]
    train_ds = TensorDataset(torch.from_numpy(X_train_img), torch.from_numpy(train_data["y"]))
    val_ds = TensorDataset(torch.from_numpy(X_val_img), torch.from_numpy(val_data["y"]))
    test_ds = TensorDataset(torch.from_numpy(X_test_img), torch.from_numpy(test_data["y"]))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    # 4. Instantiate Model
    print("\n🧠 Khởi tạo kiến trúc DINOv3 Forecaster...")
    model = DINOv3_Forecaster(cfg["model"]).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen_params = total_params - trainable_params
    print(f"   Backbone: {model.backbone_type}")
    print(f"   Tổng số tham số: {total_params:,}")
    print(f"   Tham số đóng băng (Frozen Backbone): {frozen_params:,}")
    print(f"   Tham số huấn luyện (Trainable Head): {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")

    # Fast Feature Pre-extraction for Frozen Backbone
    use_cached_features = cfg["model"].get("freeze_backbone", True)
    if use_cached_features:
        print("\n⚡ Trích xuất đặc trưng qua Frozen Backbone DINOv3 (Feature Pre-extraction)...")
        model.eval()
        def extract_all(loader):
            feats_list = []
            with torch.no_grad():
                for batch_x, _ in loader:
                    batch_x = batch_x.to(device)
                    f = model.extract_features(batch_x)
                    feats_list.append(f.cpu())
            return torch.cat(feats_list, dim=0)

        t_ext0 = time.perf_counter()
        train_feats = extract_all(train_loader)
        val_feats = extract_all(val_loader)
        test_feats = extract_all(test_loader)
        print(f"   Hoàn thành trích xuất trong {time.perf_counter() - t_ext0:.2f}s (Train shape: {train_feats.shape})")

        train_loader = DataLoader(TensorDataset(train_feats, torch.from_numpy(train_data["y"])), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(TensorDataset(val_feats, torch.from_numpy(val_data["y"])), batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(TensorDataset(test_feats, torch.from_numpy(test_data["y"])), batch_size=batch_size, shuffle=False)

    # Loss, Optimizer & Scheduler
    loss_fn = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg["training"]["learning_rate"],
        weight_decay=cfg["training"]["weight_decay"]
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3)

    # 5. Training Loop with Early Stopping
    max_epochs = max_epochs_override or cfg["training"]["max_epochs"]
    patience = cfg["training"]["early_stopping_patience"]
    best_val_mae = float("inf")
    patience_counter = 0

    checkpoint_dir = os.path.join(BASE_DIR, cfg["paths"]["checkpoint_dir"])
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(BASE_DIR, cfg["paths"]["checkpoint_path"])

    history = {"epoch": [], "train_loss": [], "val_mae": [], "val_rmse": []}
    print(f"\nBắt đầu huấn luyện (Max Epochs: {max_epochs}, Patience: {patience})...")

    for epoch in range(1, max_epochs + 1):
        model.train()
        train_loss_total = 0.0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model.regression_head(batch_x) if use_cached_features else model(batch_x)
            loss = loss_fn(preds, batch_y)
            loss.backward()
            optimizer.step()
            train_loss_total += loss.item() * len(batch_x)

        train_loss = train_loss_total / len(train_data["y"])

        # Validation phase
        model.eval()
        val_preds_list = []
        val_true_list = []

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(device)
                preds = model.regression_head(batch_x) if use_cached_features else model(batch_x)
                val_preds_list.append(preds.cpu().numpy())
                val_true_list.append(batch_y.numpy())

        val_preds = np.vstack(val_preds_list)
        val_true = np.vstack(val_true_list)
        val_mae = float(np.mean(np.abs(val_preds - val_true)))
        val_rmse = float(np.sqrt(np.mean((val_preds - val_true) ** 2)))

        scheduler.step(val_mae)

        history["epoch"].append(epoch)
        history["train_loss"].append(train_loss)
        history["val_mae"].append(val_mae)
        history["val_rmse"].append(val_rmse)

        improved = ""
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            patience_counter = 0
            # Save checkpoint
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_mae": val_mae,
                "val_rmse": val_rmse,
                "config": cfg
            }, checkpoint_path)
            improved = "⭐️ [BEST CHECKPOINT SAVED]"
        else:
            patience_counter += 1

        if epoch % 5 == 0 or epoch == 1 or improved:
            print(f"Epoch [{epoch:02d}/{max_epochs:02d}] Train Loss: {train_loss:.4f} | Val MAE: {val_mae:.4f} °C | Val RMSE: {val_rmse:.4f} °C {improved}")

        if patience_counter >= patience:
            print(f"⏹️ Early stopping kích hoạt tại epoch {epoch} (Validation MAE không giảm sau {patience} epochs).")
            break

    # 6. Evaluate Best Model on Test Set
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    test_preds_list = []
    test_true_list = []
    t_infer_start = time.perf_counter()

    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(device)
            preds = model.regression_head(batch_x) if use_cached_features else model(batch_x)
            test_preds_list.append(preds.cpu().numpy())
            test_true_list.append(batch_y.numpy())

    total_infer_time = time.perf_counter() - t_infer_start
    latency_ms = (total_infer_time / len(test_data["y"])) * 1000.0

    test_preds = np.vstack(test_preds_list)
    test_true = np.vstack(test_true_list)

    test_mae_per_st = np.mean(np.abs(test_preds - test_true), axis=0)
    test_rmse_per_st = np.sqrt(np.mean((test_preds - test_true) ** 2, axis=0))
    test_medae_per_st = np.median(np.abs(test_preds - test_true), axis=0)

    macro_mae = float(np.mean(test_mae_per_st))
    macro_rmse = float(np.sqrt(np.mean((test_preds - test_true) ** 2)))
    macro_medae = float(np.median(np.abs(test_preds - test_true)))

    ckpt_hash = compute_sha256(checkpoint_path)

    metrics_result = {
        "model": "DINOv3_Forecaster",
        "macro_mae": round(macro_mae, 4),
        "macro_rmse": round(macro_rmse, 4),
        "macro_medae": round(macro_medae, 4),
        "latency_ms_per_sample": round(latency_ms, 4),
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "checkpoint_sha256": ckpt_hash,
        "best_epoch": checkpoint["epoch"],
        "device": str(device)
    }

    for i, st in enumerate(TARGET_STATIONS):
        st_name = st.replace("_temperature", "").upper()
        metrics_result[f"{st_name}_mae"] = round(float(test_mae_per_st[i]), 4)
        metrics_result[f"{st_name}_rmse"] = round(float(test_rmse_per_st[i]), 4)

    metrics_path = os.path.join(BASE_DIR, cfg["paths"]["metrics_report"])
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_result, f, indent=2)

    # Plot training curve
    curve_path = os.path.join(BASE_DIR, "reports", "dinov3_loss_curve.png")
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=150)
    ax1.plot(history["epoch"], history["train_loss"], label="Train Huber Loss", color="#2980b9", lw=2)
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss", color="#2980b9")
    ax2 = ax1.twinx()
    ax2.plot(history["epoch"], history["val_mae"], label="Val MAE (°C)", color="#e74c3c", lw=2, linestyle="--")
    ax2.set_ylabel("Val MAE (°C)", color="#e74c3c")
    plt.title("Đường Cong Huấn Luyện DINOv3 Forecaster", fontsize=12, fontweight="bold")
    plt.savefig(curve_path, bbox_inches="tight")
    plt.close()

    print("\n" + "=" * 65)
    print("🎯 KẾT QUẢ NGHIỆM THU DINOv3 FORECASTER (Tập Test):")
    print(f"   Macro MAE : {macro_mae:.4f} °C")
    print(f"   Macro RMSE: {macro_rmse:.4f} °C")
    print(f"   Độ trễ    : {latency_ms:.2f} ms/mẫu")
    print(f"   Checkpoint: {checkpoint_path} (SHA-256: {ckpt_hash[:16]}...)")
    print("=" * 65)

    return {
        "metrics": metrics_result,
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": ckpt_hash,
        "test_preds": test_preds,
        "test_true": test_true
    }


if __name__ == "__main__":
    train_dinov3()
