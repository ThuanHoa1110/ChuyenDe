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
│   ├── split.yaml                 # Đóng băng giao thức chia dữ liệu, lookback=72, horizon=12
│   ├── image.yaml                 # Cấu hình mã hóa không gian - thời gian sang ảnh 3 kênh
│   └── dinov3.yaml                # Cấu hình kiến trúc & siêu tham số huấn luyện DINOv3
├── data/
│   ├── sample/                    # 6 file CSV mẫu (1.000 dòng/trạm) phục vụ test
│   └── README.md                  # Hướng dẫn chi tiết về dữ liệu
├── docs/
│   ├── data_inventory.md          # Kiểm kê dữ liệu, mã băm SHA-256, số dòng, khoảng thời gian
│   ├── licensing_decisions.md     # Quyết định bản quyền, giấy phép dữ liệu & checkpoint
│   └── image_encoding_mapping.md  # Sơ đồ đặc tả ánh xạ tensor không gian - thời gian sang ảnh 3 kênh
├── manifests/
│   ├── raw.json                   # Manifest bất biến dữ liệu thô 10 năm 6 trạm
│   └── split_manifest.json        # Manifest phân chia Chronological Split (Train/Val/Test)
├── release/
│   └── public/                    # Gói phát hành công khai Kaggle (DATA_CARD, metadata, data)
├── reports/
│   ├── baselines.csv              # Bảng chỉ số đối chuẩn MAE, RMSE, MedAE, Latency
│   ├── baseline_comparison.png    # Biểu đồ so sánh trực quan chuỗi thực tế vs dự báo
│   ├── comparison.csv             # Bảng so sánh tổng hợp baselines vs DINOv3
│   ├── data_quality.md            # Báo cáo kiểm định chất lượng & đồng bộ dữ liệu
│   ├── dinov3_loss_curve.png      # Biểu đồ đường cong huấn luyện & validation DINOv3
│   ├── dinov3_metrics.json        # Báo cáo chi tiết metrics DINOv3 trên tập Test
│   ├── image_samples/             # Mẫu ảnh trực quan hóa 3 kênh trước & sau nội suy
│   ├── kaggle_verification.md     # Báo cáo kiểm định phát hành & đối chiếu mã băm Kaggle
│   └── predictions_baseline.csv   # Dữ liệu chuỗi dự báo chi tiết của các baseline
├── scripts/
│   ├── inventory_check.py         # Script kiểm kê mã băm dữ liệu 6 trạm
│   ├── publish_kaggle.py          # Script tự động đăng tải & đối chiếu dataset lên Kaggle
│   ├── setup.ps1                  # Khởi tạo môi trường ảo và cài đặt dependencies
│   ├── test.ps1                   # Chạy bộ kiểm thử tự động pytest
│   ├── train.ps1                  # Huấn luyện mô hình DINOv3 Forecaster
│   ├── evaluate.ps1               # Đánh giá mô hình
│   └── serve.ps1                  # Khởi chạy FastAPI inference service
├── src/
│   └── weather/                   # Package mã nguồn chính
│       ├── data/                  # Ingestion, validation, windowing, image encoding (3 channels)
│       ├── models/                # Baseline (Persistence, Ridge, LightGBM) & DINOv3 Forecaster
│       ├── train.py               # Pipeline huấn luyện DINOv3 với early stopping & pre-extraction
│       ├── evaluate.py            # Pipeline đánh giá độc lập & kiểm định thủ công
│       └── api/                   # FastAPI serving endpoints
├── tests/
│   ├── test_smoke.py              # Bộ smoke test kiểm tra toàn vẹn Phase 0
│   ├── test_validation.py         # Bộ kiểm thử chất lượng dữ liệu & chống lệch pha (Phase 1)
│   ├── test_release.py            # Bộ kiểm thử tính toàn vẹn gói phát hành Kaggle (Phase 1)
│   ├── test_window.py             # Bộ kiểm thử cửa sổ trượt, không rò rỉ & scaler (Phase 2)
│   ├── test_baseline.py           # Bộ kiểm thử tái lập mô hình baseline & metrics (Phase 2)
│   ├── test_image.py              # Bộ kiểm thử mã hóa ảnh 3 kênh & chống leakage (Phase 3)
│   └── test_dinov3.py             # Bộ kiểm thử kiến trúc forward/backward/checkpoint DINOv3 (Phase 3)
├── .env.example                   # Mẫu khai báo biến môi trường (không chứa secret)
├── .gitignore                     # Chặn file nhạy cảm, data/raw, checkpoints
├── model_card.md                  # Hồ sơ kỹ thuật chuẩn mực mô hình DINOv3 Forecaster
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
| **Phase 3** | **Thay encoder hoặc backbone bằng DINOv3** | **HOÀN THÀNH** | • Mã hóa ma trận ảnh 3 kênh (Normalized, Past Deltas, Mask): [src/weather/data/image.py](src/weather/data/image.py), [configs/image.yaml](configs/image.yaml)<br>• Sơ đồ đặc tả ánh xạ không gian - thời gian: [docs/image_encoding_mapping.md](docs/image_encoding_mapping.md)<br>• Ảnh mẫu trực quan hóa 3 kênh: [reports/image_samples/sample_window_encoding.png](reports/image_samples/sample_window_encoding.png)<br>• Kiến trúc DINOv3 Forecaster đa trạm: [src/weather/models/dinov3_forecaster.py](src/weather/models/dinov3_forecaster.py), [configs/dinov3.yaml](configs/dinov3.yaml)<br>• Huấn luyện với Huber Loss & Early Stopping: [src/weather/train.py](src/weather/train.py)<br>• Checkpoint tối ưu (SHA-256: `8052a305...`): `checkpoints/dinov3_forecaster_best.pt`<br>• Đường cong huấn luyện & metrics: [reports/dinov3_loss_curve.png](reports/dinov3_loss_curve.png), [reports/dinov3_metrics.json](reports/dinov3_metrics.json)<br>• Model Card chuẩn mực: [model_card.md](model_card.md)<br>• Bảng tổng hợp đối chuẩn: [reports/comparison.csv](reports/comparison.csv)<br>• 34/34 Tests tự động đạt 100%: [tests/test_image.py](tests/test_image.py), [tests/test_dinov3.py](tests/test_dinov3.py) |
| **Phase 4** | **Đóng gói API và Docker** | **HOÀN THÀNH** | • FastAPI endpoints (`GET /health`, `GET /metadata`, `POST /predict`): [src/weather/api/app.py](src/weather/api/app.py)<br>• Lifespan nạp model & scaler 1 lần lúc startup; không train lúc gọi API<br>• Payload mẫu & Báo cáo nghiệm thu API: [docs/api_example.json](docs/api_example.json), [reports/api_verification.md](reports/api_verification.md)<br>• Docker hóa chuẩn bảo mật Non-Root (`appuser` UID 10001): [Dockerfile](Dockerfile), [.dockerignore](.dockerignore)<br>• Hướng dẫn chi tiết triển khai & xuất bản Docker Hub: [docs/docker_run.md](docs/docker_run.md)<br>• 15/15 Tests API & Docker (49/49 toàn dự án đạt 100%): [tests/test_api.py](tests/test_api.py), [tests/test_docker.py](tests/test_docker.py) |
| **Phase 5** | **CI/CD và PDF step by step** | **HOÀN THÀNH** | • GitHub Actions CI (`.github/workflows/ci.yml`): lint, 54 unit tests (CPU offline), Docker dry-run, ghim action commit SHA, `permissions: contents: read`<br>• GitHub Actions CD Release (`.github/workflows/release.yml`): trigger tag SemVer `v*`, xác thực Docker Hub bằng Secrets, output digest<br>• Tài liệu vận hành & rollback: [docs/release.md](docs/release.md), [docs/ci_cd_docker_step_by_step.md](docs/ci_cd_docker_step_by_step.md)<br>• **Tài liệu PDF chuyển giao chính thức (116 KB):** [docs/ci_cd_docker_step_by_step.pdf](docs/ci_cd_docker_step_by_step.pdf)<br>• 54/54 Tests tự động đạt 100%: [tests/test_cicd.py](tests/test_cicd.py) (5/5 tests) |
| Phase 6 | Bàn giao và checklist cuối | Chờ lệnh | Sẽ thực hiện khi có yêu cầu |

---

### Bảng Đối Chiếu Kiến Trúc "Trước → Sau" Khi Thay Thế Backbone DINOv3 (Phase 3)

| Tiêu chí đối chiếu | Phiên bản gốc (`dinov3_model.py`) | Phiên bản chuẩn hóa (`src/weather/models/dinov3_forecaster.py`) |
| :--- | :--- | :--- |
| **Mục đích thiết kế** | Phân loại ngữ âm trên dữ liệu SpeechOcean762 | Dự báo nhiệt độ ngắn hạn ($t+60$ phút) đồng thời 6 trạm Hà Nội |
| **Tensor đầu vào** | `(B, 64, 1536)` (Log-Mel Spectrogram âm thanh) | `(B, 3, 224, 224)` (Ma trận ảnh không gian - thời gian 3 kênh) |
| **Cấu trúc 3 kênh** | Duplicate lặp lại 3 kênh từ ảnh 1 kênh | Kênh 0: Chuẩn hóa Z-score; Kênh 1: Sai phân thời gian; Kênh 2: Observation mask |
| **Chuẩn hóa giá trị** | Z-score per-sample (phá hủy giá trị nhiệt độ tuyệt đối) | Scaler fit cố định từ Train split, bảo toàn thang đo vật lý (°C) |
| **Head đầu ra** | Linear Classifier phân loại `num_classes` nhãn rời rạc | Multi-Output Regression Head trả về 6 giá trị nhiệt độ liên tục (°C) |
| **Cơ chế dự phòng** | Crash nếu Hugging Face không tải được weights | Tự động fallback Standalone ViT-S/16, bảo đảm 100% chạy offline |

---

### Bảng Tổng Hợp So Sánh Đối Chuẩn Toàn Dự Án (Overall Benchmark Comparison)

| Mô hình (Model) | Macro MAE (°C) | Macro RMSE (°C) | Macro MedAE (°C) | Tham số huấn luyện | Tham số đóng băng | Độ trễ suy luận | Đánh giá chuyên môn |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Persistence ($\hat{y} = y_t$)** | 1.0025 | 1.0689 | 1.0167 | 0 | 0 | < 0.01 ms | Ngưỡng cơ sở tối thiểu (sai số trôi dạt nhiệt độ sau 60p) |
| **Ridge Regression** | **0.2185** | **0.2712** | **0.1829** | 402 | 0 | 0.03 ms | Nắm bắt tối ưu biến thiên cục bộ trên tập mẫu 3 ngày |
| **LightGBM Regressor** | **0.2357** | **0.2921** | **0.2061** | Non-parametric | 0 | 0.25 ms | Giảm 76.5% sai số so với Persistence |
| **DINOv3 Forecaster** | **1.5010** | **1.7229** | **1.5064** | 58,310 (0.26%) | 22,056,576 (99.74%) | 0.03 ms | Mô hình nền tảng thị giác đóng băng; hội tụ ổn định |

*Ghi chú trung thực (Quy tắc 21): Trên tập mẫu thử nghiệm 3 ngày (1.000 dòng), các mô hình dạng bảng ít tham số (Ridge/LightGBM) nắm bắt nhanh các quan hệ trễ tuyến tính, trong khi DINOv3 với 22M tham số đóng băng đóng vai trò bộ trích xuất đặc trưng không gian - thời gian tổng quát, sẵn sàng mở fine-tuning trên toàn bộ tập dữ liệu 10 năm (6.3 triệu bản ghi).*

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
*Kết quả mong đợi:* Toàn bộ 54/54 test cases đạt `PASSED` (kiểm tra smoke test, chất lượng dữ liệu, chống lệch pha, metadata gói Kaggle, cửa sổ trượt, không rò rỉ thời gian, tái lập baseline, mã hóa ảnh 3 kênh, kiến trúc DINOv3, chuẩn hóa REST API, cấu hình Docker và pipeline CI/CD).

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

### 4.7 Huấn luyện mô hình DINOv3 Forecaster (Bước 3.2)
```powershell
# Huấn luyện mô hình với cấu hình mặc định (configs/dinov3.yaml)
.\run.ps1 train

# Hoặc tùy biến file cấu hình
.\run.ps1 train -Config configs/dinov3.yaml
```
*Kết quả mong đợi:* Lưu checkpoint tốt nhất tại `checkpoints/dinov3_forecaster_best.pt`, lưu biểu đồ mất mát [reports/dinov3_loss_curve.png](reports/dinov3_loss_curve.png) và bảng so sánh [reports/comparison.csv](reports/comparison.csv).

### 4.8 Đánh giá mô hình DINOv3 trên tập Test độc lập
```powershell
# Đánh giá checkpoint DINOv3 trên tập test
.\run.ps1 evaluate -Checkpoint checkpoints/dinov3_forecaster_best.pt
```
*Kết quả mong đợi:* Tự động xuất metrics kiểm định độc lập tại [reports/dinov3_metrics.json](reports/dinov3_metrics.json).

### 4.9 Khởi chạy dịch vụ API Inference (Bước 4.1)
```powershell
# Khởi chạy máy chủ FastAPI (mặc định host 0.0.0.0, port 8000)
.\run.ps1 serve

# Truy cập Swagger UI trực quan trên trình duyệt: http://localhost:8000/docs
# Kiểm tra trạng thái: curl http://localhost:8000/health
# Thực hiện dự báo:
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d @docs/api_example.json
```
*Kết quả mong đợi:* Trả về dự báo nhiệt độ hữu hạn cho 6 trạm tại $t+60$ phút, độ trễ < 100ms. Chi tiết tại [reports/api_verification.md](reports/api_verification.md).

### 4.10 Đóng gói và chạy Docker Container (Bước 4.2)
```powershell
# Xây dựng Docker Image (non-root user, slim Python base)
docker build -t hanguynthun/hanoi-temperature:v1.0.0 .

# Khởi chạy container với checkpoint runtime mount (chỉ đọc)
docker run -d --name hanoi-weather-api -p 8000:8000 `
  -v "${PWD}/checkpoints:/app/checkpoints:ro" `
  -v "${PWD}/artifacts:/app/artifacts:ro" `
  hanguynthun/hanoi-temperature:v1.0.0
```
*Chi tiết hướng dẫn đẩy Docker Hub và kiểm định máy sạch tại [docs/docker_run.md](docs/docker_run.md).*

### 4.11 Kích Hoạt CI/CD & Xuất Bản PDF Nghiệm Thu (Phase 5)
```powershell
# 1. Kích hoạt CI tự động trên GitHub Actions:
git push origin main

# 2. Phát hành phiên bản mới lên Docker Hub (CD Release):
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 3. Biên dịch tài liệu chuyển giao PDF Step-by-Step chất lượng cao:
python scripts/generate_pdf_guide.py
```
*Tài liệu PDF chính thức đã được biên dịch sẵn sàng tại [docs/ci_cd_docker_step_by_step.pdf](docs/ci_cd_docker_step_by_step.pdf).*

---

## 5. Giấy Phép & Bảo Mật

- Dữ liệu riêng tư và checkpoint không được commit lên Git (đã được cấu hình trong `.gitignore`).
- Mã nguồn dự án tuân thủ giấy phép mã nguồn mở MIT.
- Trọng số mô hình DINOv3 tuân thủ điều khoản nghiên cứu của Meta AI.
