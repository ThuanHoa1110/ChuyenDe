# Hướng Dẫn Đóng Gói, Triển Khai & Kiểm Định Docker Container (Phase 4, Bước 4.2)
## (Hanoi Weather Multi-Station Temperature Forecasting API)

Tài liệu hướng dẫn chi tiết quy trình xây dựng (build), kiểm định an toàn (security audit), chạy container với volume mount runtime và phát hành public lên Docker Hub.

---

### 1. Kiến Trúc & Quyết Định Thiết Kế Container

- **Base Image:** `python:3.12-slim-bookworm` (Debian Bookworm tối giản, được ghim phiên bản cụ thể).
- **Nguyên tắc bảo mật Non-Root:** Tạo user `appuser` (UID 10001) và group `appgroup` (GID 10001); tuyệt đối không chạy bằng quyền `root`.
- **Phân tách trọng số (Checkpoint Decoupling):** Trọng số mô hình (`checkpoints/*.pt`) được loại trừ khỏi Docker image thông qua `.dockerignore` và được gắn động lúc chạy (`volume mount:ro`), giúp image nhẹ (< 800MB), build nhanh và độc lập với phiên bản mô hình.
- **Không rò rỉ bí mật:** `.dockerignore` loại bỏ triệt để `.env`, `credentials.json`, `data/private/`, `.git/`.
- **Healthcheck tích hợp:** Tự động kiểm tra định kỳ endpoint `/health` bằng thư viện chuẩn Python (không cần cài thêm `curl`).

---

### 2. Các Bước Thực Thi (Step-by-Step)

#### Bước 2.1: Xây dựng Docker Image (Build)
Tại thư mục gốc của repository, thực hiện lệnh:

```bash
# Build image với tag chuẩn hóa
docker build -t nguyenthuanhoa/hanoi-temperature:v1.0.0 .
```

*Ghi chú cho Windows PowerShell:*
```powershell
docker build -t nguyenthuanhoa/hanoi-temperature:v1.0.0 .
```

#### Bước 2.2: Kiểm tra bảo mật & người dùng Non-Root
Trước khi triển khai, kiểm tra quyền thực thi bên trong container:

```bash
# Kiểm tra user thực thi (kết quả mong đợi: appuser)
docker run --rm nguyenthuanhoa/hanoi-temperature:v1.0.0 whoami

# Kiểm tra UID / GID (kết quả mong đợi: uid=10001(appuser) gid=10001(appgroup))
docker run --rm nguyenthuanhoa/hanoi-temperature:v1.0.0 id
```

#### Bước 2.3: Quét lịch sử layer & chống rò rỉ credential
Kiểm tra toàn bộ các layer để xác nhận không chứa file nhạy cảm:

```bash
# Liệt kê các command trong layer image
docker history --no-trunc nguyenthuanhoa/hanoi-temperature:v1.0.0

# Kiểm tra không tồn tại file .env hoặc private data trong container
docker run --rm nguyenthuanhoa/hanoi-temperature:v1.0.0 ls -la /app
```

#### Bước 2.4: Khởi chạy Container với Runtime Volume Mount
Khởi chạy container ở chế độ background (detached) với cổng 8000 và mount thư mục `checkpoints` cùng `artifacts` ở chế độ chỉ đọc (`:ro`):

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

---

### 3. Kiểm Tra Trạng Thái & Thực Hiện Dự Báo Từ Host

Sau khi container khởi chạy, bạn có thể kiểm thử trực tiếp từ máy host:

#### 3.1 Kiểm tra Healthcheck
```bash
curl -X GET http://localhost:8000/health
```
*Kết quả mẫu (HTTP 200):*
```json
{
  "status": "healthy",
  "uptime_seconds": 12.5,
  "model_loaded": true,
  "model_name": "DINOv3Forecaster",
  "model_checkpoint": "dinov3_forecaster_best.pt",
  "scaler_loaded": true,
  "device": "cpu"
}
```

#### 3.2 Truy vấn siêu dữ liệu mô hình
```bash
curl -X GET http://localhost:8000/metadata
```

#### 3.3 Gửi payload thực hiện dự báo nhiệt độ
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @docs/api_example.json
```
*Kết quả mẫu (HTTP 200):*
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

### 4. Đăng Tải Image Lên Docker Hub (Public Release)

Khi bạn muốn xuất bản image lên Docker Hub công khai:

```bash
# 1. Đăng nhập Docker Hub bằng Access Token cá nhân
docker login -u hanguynthun

# 2. Đẩy image lên Docker Hub
docker push nguyenthuanhoa/hanoi-temperature:v1.0.0

# 3. Gắn thêm tag latest và đẩy
docker tag nguyenthuanhoa/hanoi-temperature:v1.0.0 nguyenthuanhoa/hanoi-temperature:latest
docker push nguyenthuanhoa/hanoi-temperature:latest
```

---

### 5. Kiểm Thử Trên Máy Sạch Không Có Mã Nguồn (Clean Machine Verification)

Trên một máy tính sạch bất kỳ có cài đặt Docker (không cần clone source code repository):

```bash
# 1. Kéo image public từ Docker Hub
docker pull nguyenthuanhoa/hanoi-temperature:v1.0.0

# 2. Khởi chạy image
docker run -d --name test-weather -p 8000:8000 nguyenthuanhoa/hanoi-temperature:v1.0.0

# 3. Kiểm tra health check ngay từ bên ngoài
curl -f http://localhost:8000/health
```

