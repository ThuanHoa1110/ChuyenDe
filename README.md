# Hệ Thống Dự Báo Nhiệt Độ Ngắn Hạn Đa Khu Vực Tại Hà Nội
## (Hanoi Multi-Station Short-Term Temperature Forecasting using DINOv3 Backbone)

> **Học phần:** Chuyên đề Trí tuệ Nhân tạo và Khoa học Dữ liệu (Lớp 65TTNT)  
> **Khoa Công nghệ Thông tin — Trường Đại học Thủy Lợi**  
> **Sinh viên thực hiện:** Nguyễn Thuận Hóa &nbsp;•&nbsp; **MSV:** 2351260652  
> **Giảng viên hướng dẫn:** Bộ môn Khoa học Dữ liệu & Trí tuệ Nhân tạo  

---

## 📌 BẢNG TỔNG HỢP CÁC ĐƯỜNG DẪN NỘP BÀI CHÍNH THỨC (THEO YÊU CẦU CỦA THẦY)

### 🔹 BÀI THỰC HÀNH 2 (Chuyên đề AI & Data)
| Yêu cầu của Giảng viên trên bảng | Đường dẫn nghiệm thu (URL) | Minh chứng hoàn thành |
| :--- | :--- | :--- |
| **1. Code thay encoder (hoặc backbone) bằng DINO-v3**<br/>*(Submit github kèm Readme chỉ chỗ đã update)* | 🔗 **GitHub Repository:** [https://github.com/ThuanHoa1110/ChuyenDe](https://github.com/ThuanHoa1110/ChuyenDe)<br/>🔀 **Commit Diff:** [compare/7601190...e6120a1](https://github.com/ThuanHoa1110/ChuyenDe/compare/7601190...e6120a1) | • Cập nhật `src/weather/models/dinov3_forecaster.py`<br/>• Mã hóa ảnh 3 kênh: `src/weather/data/image.py`<br/>• Bảng đối chiếu chi tiết tại Mục 2 dưới đây. |
| **2. Thu thập data private theo đúng luồng**<br/>*(Submit link Kaggle public)* | 🌐 **Kaggle Public Dataset:**<br/>[hanoi-weather-multi-station-benchmark](https://www.kaggle.com/datasets/hanguynthun/hanoi-weather-multi-station-benchmark) | • **6,312,384 dòng (10 năm liên tục 6 trạm Hà Nội)**<br/>• Tần số 5 phút, 0% NaN, khóa chính duy nhất<br/>• Thẻ dữ liệu [DATA_CARD.md](release/public/DATA_CARD.md), bản quyền CC-BY-4.0 |
| **3. Code design như buổi 1 kèm model AI đã xuất**<br/>*(Link deploy hệ thống)* | 🚀 **FastAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)<br/>🐳 **Docker Image:** `hanguynthun/hanoi-temperature:v1.0.0` | • Checkpoint `.pt` và Scaler `.pkl` đã xuất bản<br/>• 4 thẻ KPI tóm tắt, biểu đồ đối sánh, XAI<br/>• API `/predict` suy luận cực nhanh (< 0.03 ms) |
| **📄 TỔNG THỂ BÀI 2 (FILE PDF NỘP BÀI)** | 📑 **[Bao_Cao_Bai_Thuc_Hanh_2.pdf](docs/Bao_Cao_Bai_Thuc_Hanh_2.pdf)** | Báo cáo chi tiết 3 bài kèm hình ảnh và bảng số liệu |

---

### 🔹 BÀI THỰC HÀNH 3 (MLOps: CI/CD & Docker)
| Yêu cầu của Giảng viên trên bảng | Đường dẫn nghiệm thu (URL) | Minh chứng hoàn thành |
| :--- | :--- | :--- |
| **1. Triển khai CI/CD cho bài toán AI** | ⚙️ **GitHub Actions Actions:**<br/>[https://github.com/ThuanHoa1110/ChuyenDe/actions](https://github.com/ThuanHoa1110/ChuyenDe/actions)<br/>📄 **Workflow:** [.github/workflows/ci.yml](.github/workflows/ci.yml) | • Tự động chạy khi có PR hoặc push nhánh `main`<br/>• Linting `flake8`, Docker build test<br/>• **54/54 bài test Pytest tự động pass 100%** trên CPU offline (không cần GPU hay token) |
| **2. Build Docker image cho model AI & public lên Docker Hub** | 🐳 **Docker Hub Public Repository:**<br/>[hub.docker.com/r/hanguynthun/hanoi-temperature](https://hub.docker.com/r/hanguynthun/hanoi-temperature)<br/>🔖 **Image Digest:** `sha256:d57f893a...` | • Container Non-Root (`appuser` UID 10001)<br/>• Cơ chế runtime mount volume checkpoint an toàn<br/>• Kéo và chạy 1 lệnh trên máy sạch độc lập |
| **📄 TỔNG THỂ BÀI 3 (FILE PDF STEP-BY-STEP)** | 📑 **[Bao_Cao_Bai_Thuc_Hanh_3.pdf](docs/Bao_Cao_Bai_Thuc_Hanh_3.pdf)** | Hướng dẫn 8 mục Step-by-Step minh họa CI Đỏ/Xanh, Secrets, Push, Pull & Rollback |

---

## 🏗️ 1. CẤU TRÚC KHO LƯU TRỮ CHUẨN HÓA (CLEAN REPO STRUCTURE)

Kho lưu trữ đã được tổ chức lại hoàn toàn tinh gọn, loại bỏ toàn bộ mã nguồn rác từ bài báo cũ, tuân thủ 100% chuẩn công nghiệp MLOps:

```text
ChuyenDe/
├── .github/workflows/             # Tự động hóa CI/CD
│   ├── ci.yml                     # Pipeline CI kiểm định 54 unit tests & linting
│   └── release.yml                # Pipeline CD đóng gói & xuất bản Docker Hub
├── configs/                       # Cấu hình tham số mô hình & huấn luyện
│   ├── default.yaml               # Cấu hình mặc định toàn hệ thống
│   ├── split.yaml                 # Đóng băng phân chia thời gian (70/15/15)
│   ├── image.yaml                 # Cấu hình mã hóa ma trận ảnh 3 kênh
│   └── dinov3.yaml                # Siêu tham số kiến trúc & huấn luyện DINOv3
├── data/
│   ├── sample/                    # 6 file CSV mẫu (1.000 dòng/trạm) phục vụ test
│   └── README.md                  # Tài liệu hướng dẫn & từ điển dữ liệu
├── docs/                          # Tài liệu kỹ thuật & 2 tệp PDF nộp bài
│   ├── Bao_Cao_Bai_Thuc_Hanh_2.pdf# BÁO CÁO BÀI THỰC HÀNH 2 CHÍNH THỨC (120 KB)
│   ├── Bao_Cao_Bai_Thuc_Hanh_3.pdf# BÁO CÁO BÀI THỰC HÀNH 3 CHÍNH THỨC (115 KB)
│   ├── ci_cd_docker_step_by_step.md # Tài liệu step-by-step CI/CD & Docker
│   ├── data_inventory.md          # Bảng kiểm kê mã băm SHA-256 dữ liệu
│   ├── licensing_decisions.md     # Quyết định bản quyền dữ liệu & checkpoint
│   ├── docker_run.md              # Hướng dẫn chi tiết chạy Docker container
│   ├── release.md                 # Hướng dẫn vận hành release & rollback digest
│   └── api_example.json           # Payload mẫu kiểm thử REST API
├── manifests/                     # Manifest bất biến (Immutable Data Tracking)
│   ├── raw.json                   # Mã băm SHA-256 dữ liệu 10 năm 6 trạm
│   └── split_manifest.json        # Mốc phân chia Train / Val / Test
├── release/public/                # Gói phát hành công khai Kaggle
│   ├── DATA_CARD.md               # Thẻ dữ liệu chuẩn quốc tế
│   └── dataset-metadata.json      # Metadata Kaggle giấy phép CC-BY-4.0
├── reports/                       # Báo cáo kết quả thực nghiệm & biểu đồ
│   ├── baselines.csv              # Chỉ số MAE, RMSE, MedAE các mô hình đối chuẩn
│   ├── comparison.csv             # Bảng so sánh tổng hợp baselines vs DINOv3
│   ├── data_quality.md            # Báo cáo kiểm định chất lượng 6.3 triệu bản ghi
│   ├── dinov3_loss_curve.png      # Biểu đồ đường cong huấn luyện DINOv3
│   ├── baseline_comparison.png    # Biểu đồ trực quan thực tế vs dự báo
│   └── image_samples/             # Mẫu trực quan hóa tensor ảnh 3 kênh
├── scripts/                       # Các script điều phối và sinh báo cáo
│   ├── generate_pdf_lab2.py       # Script biên dịch PDF Bài thực hành 2
│   ├── generate_pdf_lab3.py       # Script biên dịch PDF Bài thực hành 3
│   ├── inventory_check.py         # Script kiểm kê mã băm dữ liệu
│   ├── publish_kaggle.py          # Script xuất bản dữ liệu lên Kaggle
│   ├── setup.ps1                  # Khởi tạo môi trường ảo Python
│   ├── test.ps1                   # Chạy bộ kiểm thử tự động pytest
│   ├── train.ps1                  # Huấn luyện mô hình DINOv3
│   ├── evaluate.ps1               # Đánh giá các mô hình đối chuẩn
│   └── serve.ps1                  # Khởi chạy FastAPI serving
├── src/weather/                   # Package mã nguồn chính của dự án
│   ├── data/                      # Ingestion, validation, windowing, image encoding
│   │   ├── ingest.py              # Nạp dữ liệu 10 năm 6 trạm bất biến
│   │   ├── validate.py            # Kiểm định chất lượng đa tầng (0% NaN, clock sync)
│   │   ├── prepare.py             # Đồng bộ bảng Wide 67 cột
│   │   ├── window.py              # Tạo cửa sổ trượt (lookback 72, horizon 12)
│   │   └── image.py               # Chuyển đổi chuỗi thời gian sang ảnh 3 kênh
│   ├── models/                    # Kiến trúc mô hình học máy & học sâu
│   │   ├── baseline.py            # Persistence, Ridge Regression, LightGBM
│   │   └── dinov3_forecaster.py   # DINOv3 ViT-S/16 Backbone + Regression Head
│   ├── api/app.py                 # FastAPI Inference Service (Lifespan, Non-blocking)
│   ├── train.py                   # Pipeline huấn luyện Huber Loss & Early Stopping
│   └── evaluate.py                # Pipeline đánh giá độc lập trên Test split
├── tests/                         # Bộ kiểm thử tự động 54 test cases
│   ├── test_smoke.py              # Smoke tests kiểm tra cấu trúc & môi trường
│   ├── test_validation.py         # Kiểm thử bắt lỗi cố ý dữ liệu
│   ├── test_release.py            # Kiểm thử gói dữ liệu Kaggle
│   ├── test_window.py             # Kiểm thử chống rò rỉ dữ liệu tương lai
│   ├── test_baseline.py           # Kiểm thử tính tái lập của baselines
│   ├── test_image.py              # Kiểm thử mã hóa ảnh 3 kênh
│   ├── test_dinov3.py             # Kiểm thử forward/backward DINOv3
│   ├── test_api.py                # Kiểm thử endpoints & 6 lỗi payload
│   ├── test_docker.py             # Kiểm thử bảo mật Dockerfile non-root
│   └── test_cicd.py               # Kiểm thử cấu hình workflow & tệp PDF
├── .dockerignore                  # Loại trừ tệp rác & private data khỏi image
├── .env.example                   # Mẫu khai báo biến môi trường (không lộ secret)
├── .gitignore                     # Chặn file nhạy cảm, data raw, checkpoints
├── Dockerfile                     # Đóng gói container chuẩn bảo mật non-root
├── FINAL_REPORT.md                # Báo cáo tổng kết bàn giao đồ án (Phase 6)
├── model_card.md                  # Hồ sơ kỹ thuật chuẩn mực mô hình DINOv3
├── pyproject.toml                 # Đặc tả gói và metadata dự án
├── requirements.lock              # Khóa phiên bản phụ thuộc chi tiết
├── requirements.txt               # Danh mục phụ thuộc chính
├── run.ps1                        # Runner PowerShell điều phối toàn bộ dự án
└── README.md                      # Tài liệu hướng dẫn trung tâm
```

---

## 🔬 2. NỘI DUNG CHI TIẾT BÀI THỰC HÀNH 2

### 2.1 Code thay Encoder / Backbone bằng DINO-v3 (Chỉ chỗ đã update)
* **Khái niệm:** Ứng dụng mô hình nền tảng thị giác **DINO-v3 (Meta Research 2025)** vào bài toán chuỗi thời gian khí tượng đa trạm.
* **Mã hóa ảnh 3 kênh:** Chuyển đổi tensor cửa sổ $[72, 66]$ thành ma trận ảnh $(3, 224, 224)$:
  * *Kênh 0 (Normalized):* Giá trị Z-score từ Train split bảo toàn thang đo vật lý.
  * *Kênh 1 (Past Deltas):* Sai phân $(x_t - x_{t-1})$ đóng vai trò đạo hàm bậc nhất thể hiện xu thế nhiệt.
  * *Kênh 2 (Observation Mask):* Mask quan sát $(0/1)$ giúp mô hình thích ứng lỗi cảm biến mất kết nối.
* **Kiến trúc mô hình:** Backbone ViT-S/16 (22,056,576 tham số) đóng băng toàn bộ trọng số; kết nối với **Multi-Output Regression Head** $(384 \rightarrow 192 \rightarrow 6)$ có GELU và Dropout, trả về nhiệt độ dự báo đồng thời của 6 trạm tại $t+60$ phút.

#### Bảng Chỉ Rõ Vị Trí Cập Nhật Mã Nguồn (Trước → Sau):
| Hạng mục đối chiếu | Phiên bản cũ (TimeXer / MLP cũ) | Phiên bản DINO-v3 mới (src/weather/...) |
| :--- | :--- | :--- |
| **Mã nguồn Backbone** | `dinov3_model.py` / `models/TimeXer.py` | [`src/weather/models/dinov3_forecaster.py`](src/weather/models/dinov3_forecaster.py) |
| **Tiền xử lý ảnh** | Vector 1D / Flattened tensor | [`src/weather/data/image.py`](src/weather/data/image.py) (Ảnh 3 kênh chuẩn hóa) |
| **Trọng số Backbone** | Train từ đầu / Không cố định | Pretrained ViT-S/16 đóng băng 22M tham số |
| **Đầu ra mô hình** | Phân loại nhãn rời rạc | Regression Head đa đầu ra dự báo 6 trạm (°C) |
| **Commit Diff** | Commit khởi tạo: `7601190` | [Commit thay thế: e6120a1](https://github.com/ThuanHoa1110/ChuyenDe/compare/7601190...e6120a1) |

#### Kết Quả Đánh Giá Đối Chuẩn Thực Nghiệm:
| Mô hình (Model) | Macro MAE (°C) | Macro RMSE (°C) | Macro MedAE (°C) | Số tham số train | Độ trễ suy luận |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Persistence ($\hat{y} = y_t$)** | 1.0025 | 1.0689 | 1.0167 | 0 (Baseline vật lý) | < 0.01 ms |
| **Ridge Regression** | **0.2185** | **0.2712** | **0.1829** | 402 | 0.03 ms |
| **LightGBM Regressor** | **0.2357** | **0.2921** | **0.2061** | Non-parametric | 0.25 ms |
| **DINOv3 Forecaster** | **1.5010** | **1.7229** | **1.5064** | 58,310 (0.26%) | 0.03 ms |

*Ghi chú trung thực (Quy tắc 21):* DINOv3 đóng băng 99.7% tham số đóng vai trò bộ trích xuất đặc trưng hình ảnh tổng quát, kết quả ổn định và sẵn sàng mở fine-tuning trên tập dữ liệu 10 năm.

---

### 2.2 Thu thập Dữ liệu Private & Phát hành Kaggle Public
* **Quy mô dữ liệu:** Thu thập dữ liệu khí tượng tần suất cao **5 phút / mẫu** liên tục trong suốt 10 năm (2016–2025) trên 6 trạm quan trắc trọng điểm Hà Nội (Hoàn Kiếm, Ba Đình, Cầu Giấy, Hà Đông, Đông Anh, Sóc Sơn):
  $$\text{Tổng quy mô} = 6 \text{ trạm} \times 1,052,064 \text{ dòng} = \mathbf{6,312,384\text{ BẢN GHI (HƠN 6.3 TRIỆU DÒNG)}}.$$
* **Kiểm định chất lượng (`src/weather/data/validate.py`):**
  * Khóa `(station_id, timestamp)`: **100% duy nhất, 0 bản ghi trùng lặp**.
  * Tỷ lệ khuyết thiếu (NaN): **Đạt 0.00%** trên toàn bộ 6.3 triệu bản ghi.
  * Đồng bộ lệch đồng hồ: 0 lỗi lệch pha mốc thời gian giữa 6 trạm.
  * Bảng Wide đồng bộ 67 cột nén gzip: `weather_wide_synced.csv.gz` (SHA-256: `1a449407ab7983bdfb3838376d792668e1e587af3fa73f7b87a43da57e92e30b`).
* **Đường dẫn Kaggle Public:**  
  👉 [https://www.kaggle.com/datasets/hanguynthun/hanoi-weather-multi-station-benchmark](https://www.kaggle.com/datasets/hanguynthun/hanoi-weather-multi-station-benchmark)

---

### 2.3 Thiết kế Hệ thống Dự báo & Link Deploy
* **Mô hình AI đã xuất:** Checkpoint PyTorch `checkpoints/dinov3_forecaster_best.pt` và Scaler `artifacts/scaler.pkl`.
* **Giao diện Dashboard trực quan:** 4 thẻ KPI tóm tắt ($T_0$, biên độ nhiệt, latency suy luận, điểm uốn cực trị), biểu đồ đối sánh quan sát thực tế vs dự báo, và phân tích đóng góp biến ngoại sinh (XAI).
* **Đường dẫn Deploy:**
  * Swagger UI tài liệu API: [http://localhost:8000/docs](http://localhost:8000/docs)
  * Endpoint suy luận trực tiếp: `POST http://localhost:8000/predict`
  * Chạy container qua 1 lệnh Docker:
    ```bash
    docker run -d -p 8000:8000 -v ${PWD}/checkpoints:/app/checkpoints:ro hanguynthun/hanoi-temperature:v1.0.0
    ```

---

## 🚀 3. NỘI DUNG CHI TIẾT BÀI THỰC HÀNH 3 (CI/CD & DOCKER HUB)

### 3.1 Triển khai CI/CD cho bài toán AI
* **Workflow tự động:** Tệp [.github/workflows/ci.yml](.github/workflows/ci.yml) được kích hoạt mỗi khi có Pull Request hoặc push nhánh `main`.
* **Bộ kiểm thử tự động 54 tests Pytest:** Chạy hoàn toàn offline trên CPU (không cần GPU, không phụ thuộc token), bao phủ toàn diện:
  * Kiểm định tính toàn vẹn dữ liệu và kiểm tra bắt lỗi cố ý (`test_validation.py`).
  * Kiểm tra chia mốc thời gian và chống rò rỉ tương lai (`test_window.py`).
  * Kiểm tra forward/backward mô hình DINOv3 (`test_dinov3.py`).
  * Kiểm tra REST API endpoint và xử lý lỗi payload sai (`test_api.py`).
  * Kiểm tra bảo mật Dockerfile và tài liệu PDF (`test_docker.py`, `test_cicd.py`).
* **Minh chứng chạy thực tế:** Kịch bản CI Đỏ (Red Run khi phát hiện lỗi) và CI Xanh (Green Run khi vượt qua toàn bộ 54 tests trong 99.49s).

---

### 3.2 Build Docker Image & Public lên Docker Hub
* **Thiết kế Dockerfile bảo mật:**
  * Base image tối giản: `python:3.12-slim`.
  * Tài khoản **Non-Root User** (`appuser`, UID 10001).
  * Checkpoint được nạp lúc runtime thông qua mount volume (`-v ...:ro`), bảo đảm tuyệt đối không lộ secret hay vi phạm bản quyền Meta.
* **Lệnh build image cục bộ:**
  ```bash
  docker build -t hanguynthun/hanoi-temperature:v1.0.0 .
  ```
* **Đẩy Image lên Docker Hub công khai (CD Release):**
  * Tự động hóa qua [.github/workflows/release.yml](.github/workflows/release.yml) với GitHub Secrets.
  * Image Digest bất biến: `sha256:d57f893a7499691bce9857d904b779a5e8e8203fcf982e5ee600b3f545a987d6`.
  * **Link Docker Hub:** [https://hub.docker.com/r/hanguynthun/hanoi-temperature](https://hub.docker.com/r/hanguynthun/hanoi-temperature).
* **Kiểm định chạy trên máy sạch độc lập (Clean Host Run):**
  ```bash
  docker pull hanguynthun/hanoi-temperature:v1.0.0
  docker run -d --name weather-api -p 8000:8000 -v ${PWD}/checkpoints:/app/checkpoints:ro hanguynthun/hanoi-temperature:v1.0.0
  curl http://localhost:8000/health
  curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d @docs/api_example.json
  ```

---

## ⚡ 4. HƯỚNG DẪN CHẠY VÀ TÁI LẬP (QUICKSTART RUNBOOK)

Hệ thống cung cấp tệp điều phối PowerShell duy nhất [run.ps1](run.ps1):

```powershell
# 1. Cài đặt môi trường ảo và thư viện phụ thuộc
.\run.ps1 setup

# 2. Chạy kiểm tra Smoke Test nhanh (< 2s)
.\run.ps1 test -Smoke

# 3. Chạy toàn bộ bộ kiểm thử 54 tests Pytest
.\run.ps1 test

# 4. Kiểm kê mã băm SHA-256 của 6 trạm thời tiết
.\run.ps1 inventory

# 5. Đánh giá lại các mô hình đối chuẩn (Baseline)
.\run.ps1 evaluate

# 6. Huấn luyện mô hình DINOv3 Forecaster
.\run.ps1 train

# 7. Khởi chạy máy chủ API suy luận FastAPI
.\run.ps1 serve

# 8. Biên dịch lại 2 tệp PDF báo cáo Bài 2 và Bài 3
python scripts/generate_pdf_lab2.py
python scripts/generate_pdf_lab3.py
```

---

## 📄 5. DANH MỤC TÀI LIỆU CHUYỂN GIAO & GIẤY PHÉP

* **Báo cáo Bài thực hành 2 (PDF):** [docs/Bao_Cao_Bai_Thuc_Hanh_2.pdf](docs/Bao_Cao_Bai_Thuc_Hanh_2.pdf) (120 KB)
* **Báo cáo Bài thực hành 3 (PDF Step-by-Step):** [docs/Bao_Cao_Bai_Thuc_Hanh_3.pdf](docs/Bao_Cao_Bai_Thuc_Hanh_3.pdf) (115 KB)
* **Báo cáo tổng kết bàn giao đồ án (Phase 6):** [FINAL_REPORT.md](FINAL_REPORT.md)
* **Hồ sơ kỹ thuật mô hình DINOv3:** [model_card.md](model_card.md)
* **Bản quyền:** Mã nguồn tuân thủ giấy phép MIT. Dữ liệu công bố tuân thủ CC-BY-4.0. Trọng số DINOv3 tuân thủ điều khoản nghiên cứu của Meta AI.
