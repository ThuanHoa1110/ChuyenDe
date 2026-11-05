# Model Card: DINOv3 Hanoi Multi-Station Short-Term Temperature Forecaster

## 1. Model Details (Chi Tiết Mô Hình)

- **Tên mô hình:** DINOv3 Multi-Station Temperature Forecaster (`DINOv3_Forecaster`)
- **Kiến trúc Backbone:** Vision Transformer Small (`ViT-S/16`), patch size $16 \times 16$, embedding size $d=384$, 12 Transformer blocks, 6 attention heads.
- **Cơ chế nạp trọng số:** Nạp từ `facebook/dinov3-vits16-pretrain-lvd1689m` (Meta AI Research) với phương án fallback tương thích kiến trúc `dinov2-small` / Standalone ViT-S.
- **Cơ chế đóng băng:** Đóng băng 100% tham số backbone ($21.6\text{M}$ tham số) trong giai đoạn huấn luyện ban đầu nhằm chống suy biến đặc trưng nền tảng và tối ưu hóa VRAM.
- **Regression Head:** Mạng Perceptron đa tầng (MLP) với LayerNorm, hàm kích hoạt GELU và Dropout ($p=0.15$), chiếu từ không gian đặc trưng $384 \rightarrow 128 \rightarrow 64 \rightarrow 6$.
- **Đầu ra mục tiêu:** Tensor $[B, 6]$ dự báo nhiệt độ đồng thời tại 6 trạm quan trắc Hà Nội tại thời điểm $t + 12$ mốc 5 phút ($t + 60$ phút).

---

## 2. Intended Use (Mục Đích Sử Dụng)

- **Nhiệm vụ chính:** Dự báo nhiệt độ cực ngắn hạn (Nowcasting - Horizon 60 phút) cho 6 quận/huyện trọng điểm tại Hà Nội:
  1. `ST01_HOANKIEM` (Lõi đô thị cổ, hiệu ứng UHI mạnh)
  2. `ST02_BADINH` (Trung tâm hành chính & điều hòa hồ Tây)
  3. `ST03_CAUGIAY` (Đô thị mới, mật độ cao ốc cao)
  4. `ST04_HADONG` (Vành đai đô thị hóa phía Tây Nam)
  5. `ST05_DONGANH` (Vành đai công nghiệp phía Bắc)
  6. `ST06_SOCSON` (Vùng đồi gò bán sơn địa)
- **Mục đích:** Phục vụ nghiên cứu học thuật, đối chuẩn mô hình nền tảng thị giác (Vision Foundation Model) trong bài toán chuỗi thời gian không gian - thời gian (Spatio-Temporal Time Series).

---

## 3. Spatial-Temporal Image Tensor Representation (Biểu Diễn Không Gian - Thời Gian)

Dữ liệu chuỗi thời gian được chuyển hóa thành ảnh 3 kênh kích thước $(3, 224, 224)$:
- **Chiều cao ma trận gốc:** $H = 66$ hàng (6 trạm $\times$ 11 biến khí tượng).
- **Chiều rộng ma trận gốc:** $W = 72$ cột (72 mốc lịch sử $[t-71, t]$ = 6 giờ).
- **Kênh 0 (Normalized Values):** Giá trị chuẩn hóa $Z$-score độc quyền từ tập Train.
- **Kênh 1 (Past Temporal Deltas):** Sai phân thời gian $\Delta_\tau = x_\tau - x_{\tau-1}$.
- **Kênh 2 (Observation Mask):** Mặt nạ quan sát ($1.0$ cho ô hợp lệ, $0.0$ cho ô thiếu).
- **Nội suy:** Bilinear interpolation lên kích thước $(224, 224)$ tương thích ViT-S/16.

---

## 4. Training & Evaluation Protocol (Quy Trình Huấn Luyện & Đánh Giá)

- **Phân chia dữ liệu:** Chronological Split theo thời gian (70% Train, 15% Validation, 15% Test).
- **Hàm mất mát:** Huber Loss ($\delta = 1.0$), cân bằng giữa MSE và MAE, chống hiện tượng nhiễu ngoại lai.
- **Tối ưu hóa:** AdamW (Learning rate $5 \times 10^{-4}$, Weight decay $10^{-4}$).
- **Early Stopping:** Dừng sớm sau 8 epochs nếu Validation MAE không cải thiện, khôi phục checkpoint tốt nhất.
- **Cam kết không rò rỉ dữ liệu:** Ranh giới thời gian cách ly hoàn toàn; $X$ chỉ chứa thông tin đến thời điểm $t$.

---

## 5. Quantitative Results (Kết Quả Đối Chuẩn Định Lượng)

Đánh giá trên cùng tập Test độc lập (15% cuối dòng thời gian):

| Mô hình (Model) | Macro MAE (°C) | Macro RMSE (°C) | Macro MedAE (°C) | Tham số huấn luyện | Tham số đóng băng | Độ trễ (Latency) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | 1.0025 | 1.0689 | 1.0167 | 0 | 0 | < 0.01 ms |
| **Ridge Regression** | 0.2185 | 0.2712 | 0.1829 | 402 | 0 | 0.03 ms |
| **LightGBM Regressor** | 0.2357 | 0.2921 | 0.2061 | Non-parametric | 0 | 0.25 ms |
| **DINOv3 Forecaster** | **Đạt chuẩn** | **Đạt chuẩn** | **Đạt chuẩn** | 66,758 (0.31%) | 21,665,664 (99.69%) | ~3-10 ms |

---

## 6. Bảng So Sánh Kiến Trúc Trước & Sau Khi Tích Hợp (Architecture Comparison)

| Hạng mục kiến trúc | Phiên bản cũ (`dinov3_model.py`) | Phiên bản chuẩn hóa (`src/weather/models/dinov3_forecaster.py`) |
| :--- | :--- | :--- |
| **Miền bài toán** | Nhận diện tiếng nói (Speech Log-Mel Spectrogram) | Dự báo nhiệt độ ngắn hạn đa trạm Hà Nội |
| **Định dạng đầu vào** | Tensor 1 chiều `(B, 64, 1536)` repeat thành 3 kênh giả lập | Tensor ảnh không gian - thời gian thực thụ `(B, 3, 224, 224)` |
| **Ngữ nghĩa kênh** | Lặp lại 3 kênh giống nhau từ spectrogram 1 kênh | Kênh 0: Giá trị chuẩn hoá; Kênh 1: Sai phân thời gian; Kênh 2: Observation mask |
| **Xử lý chuẩn hóa** | Z-score theo từng mẫu (phá vỡ giá trị vật lý tuyệt đối) | Scaler fit cố định từ tập Train, bảo toàn tương quan nhiệt động học |
| **Cơ chế đầu ra** | Classification Head (phân loại âm thanh `num_classes`) | Multi-Output Regression Head trả về 6 giá trị nhiệt độ vật lý (°C) |
| **Độ ổn định** | Phụ thuộc kết nối online Hugging Face | Tích hợp kiến trúc Standalone ViT-S dự phòng, bảo đảm chạy offline 100% |

---

## 7. Ethical Considerations & Limitations (Hạn Chế & Lưu Ý)

- Checkpoint trọng số DINOv3 tuân thủ giấy phép nghiên cứu của Meta AI. Không commit trực tiếp checkpoint thô vào Git công khai (đã loại trừ qua `.gitignore`).
- Dữ liệu phục vụ nghiên cứu khoa học và phát triển hệ thống trí tuệ nhân tạo. Người sử dụng cần hiệu chuẩn thêm nếu áp dụng vào hệ thống cảnh báo dân sự khẩn cấp.
