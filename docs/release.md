# Quy Trình Phát Hành & Quản Lý Phiên Bản (Release Management & CD)
## (Hanoi Weather Multi-Station Temperature Forecasting System)

Tài liệu hướng dẫn chi tiết quy trình phát hành tự động qua GitHub Actions và Docker Hub, cấu hình secrets, kiểm định digest và phương án rollback an toàn khi vận hành hệ thống.

---

### 1. Tổng Quan Quy Trình Phát Hành (CD Architecture)

```
[Git Tag v1.0.0] 
       │
       ▼
[GitHub Actions: release.yml]
       ├── 1. Pre-Release Quality Gate (Chạy toàn bộ 49/49 Pytest suites)
       ├── 2. Setup Docker Buildx & Cache GHA
       ├── 3. Extract Metadata & Semantic Versioning Tags (v1.0.0, v1.0, latest)
       ├── 4. Authenticate Docker Hub bằng Token (Masked Secrets)
       ├── 5. Build & Push Multi-platform Image
       └── 6. Ghi nhận Immutable Image Digest vào GitHub Step Summary
```

---

### 2. Cấu Hình Xác Thực Docker Hub (Setup Secrets)

#### Bước 2.1: Tạo Access Token trên Docker Hub
1. Đăng nhập tài khoản Docker Hub tại [hub.docker.com](https://hub.docker.com/).
2. Điều hướng tới **Account Settings** $\rightarrow$ **Security** $\rightarrow$ **New Access Token**.
3. Đặt mô tả token: `github-actions-hanoi-weather`.
4. Cấp quyền hạn tối thiểu cần thiết: **Read, Write, Delete** (hoặc **Read & Write**).
5. Nhấn **Generate** và sao chép Personal Access Token (PAT).

> [!CAUTION]
> Tuyệt đối không lưu token này vào mã nguồn git, file commit, hoặc tài liệu công khai.

#### Bước 2.2: Cấu hình GitHub Secrets
1. Mở repository dự án trên GitHub.
2. Vào **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
3. Nhấn **New repository secret** và thêm 2 bí mật:
   - `DOCKERHUB_USERNAME`: Tên tài khoản Docker Hub của bạn (ví dụ: `hanguynthun`).
   - `DOCKERHUB_TOKEN`: Chuỗi Access Token vừa tạo ở Bước 2.1.
4. Toàn bộ giá trị này được GitHub tự động mã hóa AES-256 và che giấu (masked) trong toàn bộ build logs.

---

### 3. Quy Trình Kích Hoạt Release Bằng Git Tag

Hệ thống CD chỉ kích hoạt khi có Git Tag hợp lệ tuân thủ chuẩn **Semantic Versioning (SemVer)** với tiền tố `v` (ví dụ: `v1.0.0`, `v1.0.1`, `v1.1.0`). Các commit thông thường hoặc Pull Request sẽ **không** kích hoạt việc đẩy image lên Docker Hub.

#### Lệnh tạo và đẩy Git Tag:
```bash
# 1. Kiểm tra trạng thái git sạch
git status

# 2. Tạo Git annotated tag
git tag -a v1.0.0 -m "Release v1.0.0: DINOv3 Forecaster, FastAPI Serving & Docker Container"

# 3. Đẩy tag lên GitHub
git push origin v1.0.0
```

#### Theo dõi tiến trình:
1. Truy cập tab **Actions** trên GitHub repository.
2. Chọn workflow **Continuous Deployment (CD Release)** tương ứng với tag `v1.0.0`.
3. Kiểm tra các bước thực thi:
   - `Pre-Release Quality Gate`: Chạy toàn bộ 49/49 unit tests.
   - `Build & Push Docker Hub Release`: Biên dịch image và đẩy lên Docker Hub.

---

### 4. Kiểm Định Bằng Chứng Nghiệm Thu (Verification & Digest)

Sau khi workflow hoàn tất thành công, GitHub Step Summary sẽ tự động xuất báo cáo chi tiết:

- **Image Repository:** `hanguynthun/hanoi-temperature`
- **Release Tag:** `v1.0.0`
- **Các tags được sinh tự động:**
  - `hanguynthun/hanoi-temperature:1.0.0`
  - `hanguynthun/hanoi-temperature:1.0`
  - `hanguynthun/hanoi-temperature:latest`
- **Immutable Digest (Mã băm bất biến SHA-256):**
  Ví dụ: `sha256:8f4c1e0b3...`

#### Kiểm tra trên máy trạm sạch (Clean Host):
```bash
# Kéo image bằng tag
docker pull hanguynthun/hanoi-temperature:v1.0.0

# Hoặc kéo chính xác bằng digest bất biến
docker pull hanguynthun/hanoi-temperature@sha256:<digest_hash>

# Chạy container kiểm tra
docker run -d --name test-hanoi-api -p 8000:8000 hanguynthun/hanoi-temperature:v1.0.0
curl -f http://localhost:8000/health
```

---

### 5. Chiến Lược Rollback An Toàn (Rollback Strategy)

Trong trường hợp phát hiện sự cố sau khi release phiên bản mới (ví dụ `v1.0.1` gặp lỗi không mong muốn trong môi trường production):

1. **Tuyệt đối không xóa image cũ trên Docker Hub:** Việc lưu trữ các phiên bản cũ bảo đảm tính toàn vẹn và khả năng truy vết lịch sử.
2. **Rollback bằng Image Digest hoặc Tag trước đó:**
   Chuyển hướng deployment về đúng mã băm digest hoặc tag ổn định trước đó:
   ```bash
   # Khởi động lại dịch vụ với phiên bản v1.0.0 ổn định
   docker stop hanoi-weather-api
   docker rm hanoi-weather-api
   
   docker run -d \
     --name hanoi-weather-api \
     -p 8000:8000 \
     -v "$(pwd)/checkpoints:/app/checkpoints:ro" \
     -v "$(pwd)/artifacts:/app/artifacts:ro" \
     --restart unless-stopped \
     hanguynthun/hanoi-temperature:v1.0.0
   ```
3. **Phát hành bản vá sửa lỗi (Hotfix):**
   Sửa lỗi trên branch `main`, tạo tag mới `v1.0.2` và kích hoạt lại pipeline CD tự động.

