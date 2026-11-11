# Hướng Dẫn Thao Tác CI/CD & Đóng Gói Docker Từng Bước (Step-by-Step)
## Dự Án Dự Báo Nhiệt Độ Ngắn Hạn Đa Trạm Tại Hà Nội (Hanoi Weather DINOv3)

**Tài liệu kỹ thuật chính thức phục vụ nghiệm thu Phase 5 (Bước 5.3)**  
*Mã tài liệu: `DOC-PHASE5-CICD-DOCKER-STEP-BY-STEP`*  
*Người thực hiện: Nhóm Nghiên Cứu Khí Tượng Hà Nội (`hanguynthun`)*  

---

### Bảng Thông Tin Xác Minh Môi Trường Thực Nghiệm

| Thông số | Giá trị xác minh | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Hệ điều hành xác minh** | Windows 11 Pro 64-bit / Ubuntu 22.04 LTS | Kiểm định đa nền tảng |
| **Phiên bản Python** | Python 3.12.3 (`.venv`) | Cố định phụ thuộc trong `requirements.lock` |
| **Công cụ CI/CD** | GitHub Actions (Runner `ubuntu-latest`) | Permissions tối thiểu `contents: read` |
| **Phiên bản Docker** | Docker Engine 26.x / Docker Buildx v3.0 | Kiến trúc Non-Root `appuser` (UID 10001) |
| **Docker Hub Repository** | `nguyenthuanhoa/hanoi-temperature` | Image công khai (Public Image) |
| **Release Tag** | `v1.0.0` | Semantic Versioning chuẩn |
| **Image Digest** | `sha256:8f4c1e0b3d...` | Mã băm bất biến trên Docker Hub |
| **Commit Git kiểm định** | `3dfd766` | Branch `main` |
| **Ngày xác minh nghiệm thu**| 06/11/2026 | 100% 49/49 Tests PASSED |

---

## 1. Yêu Cầu Chuẩn Bị & Cấu Trúc Repository

### 1.1 Yêu cầu tài khoản
1. **Tài khoản GitHub:** Đã tạo repository chứa mã nguồn dự án, có quyền Quản trị (Admin) để cấu hình Secrets và Branch Protection.
2. **Tài khoản Docker Hub:** Tài khoản miễn phí hoặc tổ chức tại [hub.docker.com](https://hub.docker.com/) (ví dụ: `hanguynthun`).

### 1.2 Cấu trúc thư mục liên quan tới CI/CD & Docker
```text
ChuyenDe/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Pipeline CI (Lint, Test, Docker Dry-Run)
│       └── release.yml            # Pipeline CD (Release Docker Hub khi gắn Tag)
├── Dockerfile                     # Dockerfile non-root, slim Python 3.12
├── .dockerignore                  # Chặn rò rỉ credential, .env, raw data
├── docs/
│   ├── api_example.json           # Payload mẫu chuẩn kiểm thử API
│   ├── docker_run.md              # Tài liệu vận hành Docker container
│   ├── release.md                 # Hướng dẫn quy trình phát hành & rollback
│   └── ci_cd_docker_step_by_step.md # Tài liệu hướng dẫn chi tiết này
├── reports/
│   └── api_verification.md       # Báo cáo nghiệm thu kết quả gọi curl
├── src/weather/api/app.py         # Mã nguồn FastAPI Serving engine
└── tests/
    ├── test_api.py                # 11 tests kiểm thử API endpoints & validation
    └── test_docker.py             # 4 tests kiểm tra tính an toàn của Dockerfile
```

---

## 2. Cấu Hình Bảo Mật: Docker Hub Token & GitHub Secrets

### Bước 2.1: Tạo Access Token trên Docker Hub
1. Truy cập [hub.docker.com](https://hub.docker.com/) và đăng nhập.
2. Nhấn vào ảnh đại diện góc trên bên phải $\rightarrow$ **Account Settings** $\rightarrow$ chọn thẻ **Security**.
3. Nhấn **New Access Token**:
   - *Access Token Description:* `github-actions-hanoi-weather-ci`
   - *Access permissions:* Chọn `Read, Write, Delete` (hoặc `Read & Write`).
4. Nhấn **Generate**.
5. **Quan trọng:** Sao chép chuỗi token ngay lập tức (ví dụ: `dckr_pat_xxxxxxxxxxxxxxxxxxxx`). Docker Hub chỉ hiển thị token một lần duy nhất.

### Bước 2.2: Cấu hình GitHub Secrets
1. Mở repository dự án trên GitHub: `https://github.com/<user>/<repo>`.
2. Chọn **Settings** (biểu tượng bánh răng) $\rightarrow$ cột bên trái chọn **Secrets and variables** $\rightarrow$ **Actions**.
3. Nhấn nút xanh **New repository secret**:
   - Secret 1:
     - *Name:* `DOCKERHUB_USERNAME`
     - *Secret:* `<tên_tài_khoản_dockerhub>` (ví dụ: `hanguynthun`)
   - Secret 2:
     - *Name:* `DOCKERHUB_TOKEN`
     - *Secret:* Dán chuỗi Personal Access Token đã sao chép ở Bước 2.1.
4. **Nguyên tắc bảo mật:** Không bao giờ ghi trực tiếp giá trị token vào file tài liệu hay commit. GitHub sẽ tự động mã hóa AES-256 và ẩn giá trị (masking `***`) trong toàn bộ log của Actions.

---

## 3. Quy Trình CI Tự Động: Trạng Thái Đỏ $\rightarrow$ Trạng Thái Xanh

Pipeline CI được định nghĩa tại `.github/workflows/ci.yml`, tự động kích hoạt khi có `push` hoặc `pull_request` vào nhánh `main`.

### 3.1 Cơ chế kiểm soát Branch Protection
Để đảm bảo không bao giờ merge mã nguồn lỗi vào nhánh chính:
1. Vào GitHub repo $\rightarrow$ **Settings** $\rightarrow$ **Branches** $\rightarrow$ **Add branch protection rule**.
2. *Branch name pattern:* `main`.
3. Tích chọn các mục:
   - `Require a pull request before merging`.
   - `Require status checks to pass before merging`.
   - Tìm kiếm và tích chọn các job: `Unit & Integration Tests (CPU) (3.12)`, `Code Quality & Linting`, `Docker Build Validation (No Push)`.
4. Nhấn **Save changes**.

### 3.2 Kịch bản kiểm chứng: PR lỗi bị chặn (Trạng thái ĐỎ)
1. Tạo branch thử nghiệm: `git checkout -b test/intentional-failure`.
2. Tạo lỗi giả lập (ví dụ cố ý sửa hàm kiểm tra độ dài mốc thời gian thành sai).
3. Đẩy lên GitHub và tạo Pull Request vào `main`.
4. **Kết quả mong đợi:** Job `Unit & Integration Tests` thất bại, GitHub hiển thị **dấu chéo đỏ (FAILED)** và **khóa nút Merge Pull Request** theo đúng luật Branch Protection.

### 3.3 Kịch bản khắc phục: PR đúng vượt qua kiểm thử (Trạng thái XANH)
1. Sửa lại mã nguồn đúng chuẩn.
2. Commit và đẩy lên lại branch: `git commit -am "fix: restore valid test assertions" && git push`.
3. GitHub Actions tự động kích hoạt lại.
4. **Kết quả mong đợi:** Toàn bộ các job `lint`, `test (3.11, 3.12)` và `docker-dry-run` hoàn thành với **dấu tích xanh (PASSED)**. Nút Merge Pull Request được mở khóa.

---

## 4. Quy Trình CD Tự Động: Release Lên Docker Hub

Pipeline CD được định nghĩa tại `.github/workflows/release.yml`, chỉ kích hoạt khi có Git Tag hợp lệ (`v*.*.*`).

### Bước 4.1: Tạo và gắn thẻ Release Tag
Khi mã nguồn trên nhánh `main` đã vượt qua 100% bài kiểm tra:

```bash
# Đảm bảo bạn đang ở nhánh main và repo sạch
git checkout main
git pull origin main

# Tạo annotated tag theo chuẩn Semantic Versioning
git tag -a v1.0.0 -m "Release v1.0.0: DINOv3 Hanoi Weather Forecaster & Serving Container"

# Đẩy tag lên GitHub
git push origin v1.0.0
```

### Bước 4.2: Giám sát pipeline Release trên GitHub Actions
1. Vào tab **Actions** $\rightarrow$ chọn workflow **Continuous Deployment (CD Release)** của tag `v1.0.0`.
2. Quy trình tự động thực hiện:
   - `Pre-Release Quality Gate`: Chạy lại bộ 49/49 unit tests.
   - `Extract Docker Metadata`: Trích xuất các tag `v1.0.0`, `1.0`, `latest`.
   - `Log in to Docker Hub`: Xác thực bảo mật bằng secrets đã cấu hình.
   - `Build and Push`: Biên dịch image và đẩy lên Docker Hub.
   - `Generate GitHub Release Step Summary`: Xuất thông tin chi tiết kèm **SHA-256 Digest**.

---

## 5. Hướng Dẫn Kéo & Chạy Image Trên Máy Trạm Sạch (Clean Machine)

Người nghiệm thu (Reviewer) hoặc kỹ sư vận hành có thể tái hiện toàn bộ dịch vụ trên một máy tính sạch bất kỳ đã cài Docker **mà không cần clone source code**:

### Bước 5.1: Kéo image từ Docker Hub
```bash
docker pull nguyenthuanhoa/hanoi-temperature:v1.0.0
```

### Bước 5.2: Khởi chạy Container với Volume Mount
Để chạy container với checkpoint và scaler tối ưu, khởi chạy với volume mount chế độ chỉ đọc (`:ro`):

**Trên Linux / macOS:**
```bash
docker run -d \
  --name hanoi-weather-api \
  -p 8000:8000 \
  -v "$(pwd)/checkpoints:/app/checkpoints:ro" \
  -v "$(pwd)/artifacts:/app/artifacts:ro" \
  --restart unless-stopped \
  nguyenthuanhoa/hanoi-temperature:v1.0.0
```

**Trên Windows PowerShell:**
```powershell
docker run -d `
  --name hanoi-weather-api `
  -p 8000:8000 `
  -v "${PWD}/checkpoints:/app/checkpoints:ro" `
  -v "${PWD}/artifacts:/app/artifacts:ro" `
  --restart unless-stopped `
  nguyenthuanhoa/hanoi-temperature:v1.0.0
```

### Bước 5.3: Kiểm tra người dùng Non-Root
```bash
docker exec hanoi-weather-api whoami
# Kết quả mong đợi: appuser

docker exec hanoi-weather-api id
# Kết quả mong đợi: uid=10001(appuser) gid=10001(appgroup)
```

### Bước 5.4: Thực hiện kiểm tra Curl trực tiếp từ Host

#### 1. Kiểm tra sức khỏe dịch vụ:
```bash
curl -X GET http://localhost:8000/health
```
*Kết quả:*
```json
{
  "status": "healthy",
  "uptime_seconds": 15.42,
  "model_loaded": true,
  "model_name": "DINOv3Forecaster",
  "model_checkpoint": "dinov3_forecaster_best.pt",
  "scaler_loaded": true,
  "device": "cpu"
}
```

#### 2. Kiểm tra siêu dữ liệu 6 trạm:
```bash
curl -X GET http://localhost:8000/metadata
```

#### 3. Thực hiện dự báo nhiệt độ đồng thời 6 trạm sau 60 phút:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @docs/api_example.json
```
*Kết quả:*
```json
{
  "status": "success",
  "model_version": "v1.0.0",
  "data_version": "v1.0.0",
  "end_timestamp": "2016-01-01 05:55:00",
  "horizon_steps": 12,
  "horizon_minutes": 60,
  "target_timestamp": "2016-01-01T06:55:00",
  "predictions": {
    "st01_hoankiem": 17.72,
    "st02_badinh": 16.96,
    "st03_caugiay": 17.29,
    "st04_hadong": 16.50,
    "st05_donganh": 15.93,
    "st06_socson": 15.10
  },
  "units": "°C",
  "latency_ms": 74.4
}
```

---

## 6. Bảng Xử Lý Sự Cố & Lỗi Thường Gặp (Troubleshooting)

| Tình huống / Lỗi | Nguyên nhân | Cách xử lý dứt điểm |
| :--- | :--- | :--- |
| **Lỗi `403 Forbidden` khi Docker push trong CI** | `DOCKERHUB_USERNAME` hoặc `DOCKERHUB_TOKEN` trong GitHub Secrets bị sai hoặc hết hạn | Kiểm tra lại token trên Docker Hub, cấp quyền `Read & Write`, cập nhật lại Secrets trong GitHub Settings. |
| **Lỗi HTTP 422: `timestamps must contain exactly 72 timesteps`** | Payload gửi lên không đủ 72 mốc thời gian (lookback 6 giờ) | Đảm bảo mảng `timestamps` và dữ liệu chuỗi có đúng 72 phần tử với chu kỳ 5 phút. |
| **Lỗi HTTP 422: `station_ids must contain exactly 6 stations`** | Danh sách trạm bị thiếu hoặc sai thứ tự canonical | Sắp xếp đúng 6 trạm: `st01`, `st02`, `st03`, `st04`, `st05`, `st06`. |
| **Port 8000 bị xung đột trên host** | Đã có dịch vụ khác chiếm cổng 8000 | Đổi port map trên host, ví dụ `-p 8080:8000` và gọi `http://localhost:8080/health`. |
| **Cần Rollback phiên bản khẩn cấp** | Phiên bản mới gặp lỗi bất ngờ trên production | Chạy lại image theo digest bất biến trước đó: `docker run ... nguyenthuanhoa/hanoi-temperature@sha256:<previous_digest>`. |

