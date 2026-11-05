# Dự Án Dự Báo Nhiệt Độ Ngắn Hạn Đa Khu Vực Tại Hà Nội
## (Hanoi Multi-Station Short-Term Temperature Forecasting using DINOv3 Backbone)

Dự án nghiên cứu và triển khai hệ thống học sâu dự báo nhiệt độ ngắn hạn (t + 60 phút) tại 6 trạm quan trắc khí tượng trọng điểm trên địa bàn Hà Nội. Dự án ứng dụng kiến trúc chuyển đổi không gian - thời gian thành biểu diễn ảnh 3 kênh kết hợp với mô hình nền tảng thị giác **DINOv3 (Meta Research)** và regression head đa đầu ra.

---

## 1. Mục Tiêu Dự Án & Quyết Định Thiết Kế

- **Mục tiêu chính:** Dự báo nhiệt độ đồng thời tại cả 6 trạm sau **60 phút** (t + 12 mốc 5 phút) từ chuỗi quan sát quá khứ đến thời điểm $t$.
- **Thử nghiệm phụ:** Dự báo tại mốc **30 phút** (t + 6 mốc).
- **Đơn vị mẫu:** Cửa sổ trượt lookback 72 mốc (tương đương 6 giờ dữ liệu quá khứ, chu kỳ 5 phút).
- **Mã hóa DINOv3:** Dữ liệu chuỗi thời gian đa trạm đa biến được mã hóa thành tensor ma trận ảnh 3 kênh:
  - *Channel 1:* Giá trị chuẩn hóa.
  - *Channel 2:* Sai phân biến thiên quá khứ.
  - *Channel 3:* Mask đánh dấu trạng thái thiếu dữ liệu.
- **Backbone:** DINOv3 (ViT-S/16) đóng băng trọng số ban đầu, gắn Regression Head trả về 6 giá trị nhiệt độ.
- **Tiêu chuẩn bàn giao:** GitHub Public, Kaggle Dataset Public, Docker Hub Image Public, tài liệu PDF step-by-step cho CI/CD & Docker.

---

## 2. Cấu Trúc Repository

```text
ChuyenDe/
├── configs/                       # Cấu hình tham số mô hình, dữ liệu, huấn luyện
│   ├── default.yaml
│   └── split.yaml                 # Đóng băng giao thức chia dữ liệu, lookback=72, horizon=12
├── data/
│   ├── sample/                    # 6 file CSV mẫu (1.000 dòng/trạm) phục vụ test
│   └── README.md                  # Hướng dẫn chi tiết về dữ liệu
├── docs/
│   ├── data_inventory.md          # Kiểm kê dữ liệu, mã băm SHA-256, số dòng, khoảng thời gian
│   └── licensing_decisions.md     # Quyết định bản quyền, giấy phép dữ liệu & checkpoint
├── manifests/
│   ├── raw.json                   # Manifest bất biến dữ liệu thô 10 năm 6 trạm
│   └── split_manifest.json        # Manifest phân chia Chronological Split (Train/Val/Test)
├── release/
│   └── public/                    # Gói phát hành công khai Kaggle (DATA_CARD, metadata, data)
├── reports/
│   ├── baselines.csv              # Bảng chỉ số đối chuẩn MAE, RMSE, MedAE, Latency
│   ├── baseline_comparison.png    # Biểu đồ so sánh trực quan chuỗi thực tế vs dự báo
│   ├── data_quality.md            # Báo cáo kiểm định chất lượng & đồng bộ dữ liệu
│   ├── kaggle_verification.md     # Báo cáo kiểm định phát hành & đối chiếu mã băm Kaggle
│   └── predictions_baseline.csv   # Dữ liệu chuỗi dự báo chi tiết của các baseline
├── scripts/
│   ├── inventory_check.py         # Script kiểm kê mã băm dữ liệu 6 trạm
│   ├── publish_kaggle.py          # Script tự động đăng tải & đối chiếu dataset lên Kaggle
│   ├── setup.ps1                  # Khởi tạo môi trường ảo và cài đặt dependencies
│   ├── test.ps1                   # Chạy bộ kiểm thử tự động pytest
│   ├── train.ps1                  # Huấn luyện mô hình
│   ├── evaluate.ps1               # Đánh giá mô hình
│   └── serve.ps1                  # Khởi chạy FastAPI inference service
├── src/
│   └── weather/                   # Package mã nguồn chính
│       ├── data/                  # Ingestion, validation, windowing, image encoding
│       ├── models/                # Baseline (Persistence, Ridge, LightGBM) & DINOv3 Forecaster
│       ├── evaluate.py            # Pipeline đánh giá độc lập & kiểm định thủ công
│       └── api/                   # FastAPI serving endpoints
├── tests/
│   ├── test_smoke.py              # Bộ smoke test kiểm tra toàn vẹn Phase 0
│   ├── test_validation.py         # Bộ kiểm thử chất lượng dữ liệu & chống lệch pha (Phase 1)
│   ├── test_release.py            # Bộ kiểm thử tính toàn vẹn gói phát hành Kaggle (Phase 1)
│   ├── test_window.py             # Bộ kiểm thử cửa sổ trượt, không rò rỉ & scaler (Phase 2)
│   └── test_baseline.py           # Bộ kiểm thử tái lập mô hình baseline & metrics (Phase 2)
├── .env.example                   # Mẫu khai báo biến môi trường (không chứa secret)
├── .gitignore                     # Chặn file nhạy cảm, data/raw, checkpoints
├── pyproject.toml                 # Đặc tả gói và metadata dự án
├── requirements.txt               # Danh mục phụ thuộc chính
├── requirements.lock              # Khóa phiên bản phụ thuộc chi tiết
├── run.ps1                        # Runner PowerShell điều phối toàn bộ pipeline
└── README.md
```

---

## 3. Nhật Ký Tiến Độ Thực Thi (Phase Progress Log)

| Phase | Nội dung | Trạng thái | Bằng chứng nghiệm thu |
| :---: | :--- | :---: | :--- |
| **Phase 0** | **Khởi tạo và cổng quyền sử dụng** | **HOÀN THÀNH** | • Cấu trúc repo & khóa dependencies (`pyproject.toml`, `requirements.lock`)<br>• Script Runner: `run.ps1` (setup, test, inventory)<br>• 6/6 Smoke tests đạt 100% (`tests/test_smoke.py`)<br>• Báo cáo kiểm kê dữ liệu 6 trạm: [docs/data_inventory.md](docs/data_inventory.md)<br>• Báo cáo bản quyền & checkpoint: [docs/licensing_decisions.md](docs/licensing_decisions.md)<br>• Commit Git: `addcd63` |
| **Phase 1** | **Thu thập dữ liệu private và phát hành Kaggle** | **HOÀN THÀNH** | • Nạp dữ liệu 10 năm 6 trạm (6,312,384 dòng): `src/weather/data/ingest.py`<br>• Manifest bất biến: [manifests/raw.json](manifests/raw.json)<br>• Bộ kiểm tra chất lượng & chống lệch pha: `src/weather/data/validate.py`<br>• 16/16 Tests chất lượng & release đạt 100%: `tests/test_validation.py`, `tests/test_release.py`<br>• Bảng wide đồng bộ 67 cột (1,052,064 dòng): `release/public/weather_wide_synced.csv.gz` (SHA-256: `1a449407ab7983bdfb3838376d792668e1e587af3fa73f7b87a43da57e92e30b`)<br>• Báo cáo chất lượng dữ liệu: [reports/data_quality.md](reports/data_quality.md)<br>• Gói xuất bản: [release/public/DATA_CARD.md](release/public/DATA_CARD.md) & [dataset-metadata.json](release/public/dataset-metadata.json)<br>• Script đăng tải & báo cáo nghiệm thu Kaggle: [scripts/publish_kaggle.py](scripts/publish_kaggle.py), [reports/kaggle_verification.md](reports/kaggle_verification.md)<br>• **Dataset Kaggle Public:** [hanguynthun/hanoi-weather-multi-station-benchmark](https://www.kaggle.com/datasets/hanguynthun/hanoi-weather-multi-station-benchmark) |
| **Phase 2** | **Đóng băng giao thức đánh giá** | **HOÀN THÀNH** | • Lookback 72 mốc (6h), Horizon 12 mốc (60p) & Split theo thời gian (70% train, 15% val, 15% test): [src/weather/data/window.py](src/weather/data/window.py)<br>• Cấu hình đóng băng cố định: [configs/split.yaml](configs/split.yaml)<br>• Scaler Standard hoá huấn luyện độc quyền trên Train: `artifacts/scaler.pkl`<br>• Manifest phân chia & 3 mẫu kiểm chứng: [manifests/split_manifest.json](manifests/split_manifest.json)<br>• 25/25 Tests tự động đạt 100%: [tests/test_window.py](tests/test_window.py), [tests/test_baseline.py](tests/test_baseline.py)<br>• Mô hình đối chuẩn (Persistence, Ridge, LightGBM): [src/weather/models/baseline.py](src/weather/models/baseline.py)<br>• Pipeline đánh giá tự động: [src/weather/evaluate.py](src/weather/evaluate.py)<br>• Bảng kết quả đối chuẩn test: [reports/baselines.csv](reports/baselines.csv)<br>• Biểu đồ so sánh trực quan thực tế và dự báo: [reports/baseline_comparison.png](reports/baseline_comparison.png) |
| Phase 3 | Thay encoder hoặc backbone bằng DINOv3 | Chờ lệnh | Sẽ thực hiện khi có yêu cầu |
| Phase 4 | Đóng gói API và Docker | Chờ lệnh | Sẽ thực hiện khi có yêu cầu |
| Phase 5 | CI/CD và PDF step by step | Chờ lệnh | Sẽ thực hiện khi có yêu cầu |
| Phase 6 | Bàn giao và checklist cuối | Chờ lệnh | Sẽ thực hiện khi có yêu cầu |

### Bảng Kết Quả Đối Chuẩn Mô Hình Baseline (Phase 2 Benchmark)

| Mô hình (Model) | Macro MAE (°C) | Macro RMSE (°C) | Macro MedAE (°C) | Độ trễ suy luận (ms/mẫu) | Đánh giá |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Persistence ($\hat{y} = y_t$)** | 1.0025 | 1.0689 | 1.0167 | < 0.01 ms | Ngưỡng tối thiểu (mốc cơ sở) |
| **Ridge Regression** | **0.2185** | **0.2712** | **0.1829** | 0.03 ms | Giảm 78.2% MAE so với Persistence |
| **LightGBM Regressor** | **0.2357** | **0.2921** | **0.2061** | 0.25 ms | Giảm 76.5% MAE so với Persistence |

*Toàn bộ 3 mô hình được đánh giá trên cùng tập Test (15% cuối dòng thời gian) với cùng scaler fit độc quyền trên tập Train.*

---

## 4. Hướng Dẫn Tái Lập (Quickstart & Reproduction)

### 4.1 Khởi tạo môi trường
Yêu cầu: Python 3.10 – 3.12 trên hệ điều hành Windows / Linux.
```powershell
# Chạy thiết lập tự động
.\run.ps1 setup
```

### 4.2 Chạy kiểm tra Smoke Test (Phase 0 Verification)
```powershell
# Chạy bộ test kiểm tra cấu trúc và tính toàn vẹn của dữ liệu mẫu
.\run.ps1 test -Smoke
```
*Kết quả mong đợi:* Toàn bộ 6/6 test cases đạt `PASSED` trong vòng dưới 2 giây.

### 4.3 Kiểm kê và xác minh mã băm dữ liệu
```powershell
.\run.ps1 inventory
```
*Kết quả mong đợi:* Hiển thị chi tiết mã băm SHA-256, 1.000 dòng dữ liệu, chu kỳ 5 phút và 0 giá trị khuyết thiếu cho cả 6 trạm.

### 4.4 Chạy bộ kiểm thử toàn diện (Unit Tests & Quality Suite)
```powershell
.\run.ps1 test
```
*Kết quả mong đợi:* Toàn bộ 25/25 test cases đạt `PASSED` (kiểm tra smoke test, chất lượng dữ liệu, chống lệch pha, metadata gói Kaggle, cửa sổ trượt, không rò rỉ thời gian và tái lập baseline).

### 4.5 Phát hành và kiểm định gói dữ liệu Kaggle (Bước 1.3)
```powershell
# Chế độ kiểm định gói phát hành cục bộ (Dry Run)
.\run.ps1 publish-kaggle -DryRun

# Hoặc đẩy trực tiếp lên tài khoản Kaggle của bạn (khi đã cấu hình Kaggle CLI/Token)
.\run.ps1 publish-kaggle
```
*Kết quả mong đợi:* Báo cáo nghiệm thu được tự động ghi nhận tại [reports/kaggle_verification.md](reports/kaggle_verification.md).

### 4.6 Đánh giá các mô hình đối chuẩn Baseline (Bước 2.2)
```powershell
# Chạy đánh giá Persistence, Ridge Regression và LightGBM
.\run.ps1 evaluate
```
*Kết quả mong đợi:* Tự động sinh báo cáo số liệu tại [reports/baselines.csv](reports/baselines.csv), lưu chuỗi dự báo [reports/predictions_baseline.csv](reports/predictions_baseline.csv) và biểu đồ trực quan tại [reports/baseline_comparison.png](reports/baseline_comparison.png).

---

## 5. Giấy Phép & Bảo Mật

- Dữ liệu riêng tư và checkpoint không được commit lên Git (đã được cấu hình trong `.gitignore`).
- Mã nguồn dự án tuân thủ giấy phép mã nguồn mở MIT.
- Trọng số mô hình DINOv3 tuân thủ điều khoản nghiên cứu của Meta AI.
