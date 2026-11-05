# Sơ Đồ Ánh Xạ Không Gian - Thời Gian Sang Ảnh 3 Kênh (Image Encoding Mapping)
## Phục vụ mô hình nền tảng DINOv3 (Phase 3, Bước 3.1)

Tài liệu này đặc tả cấu trúc toán học và quy tắc chuyển đổi chuỗi thời gian khí tượng đa trạm sang ma trận ảnh 3 kênh phù hợp với kiến trúc Vision Transformer (ViT-S/16) của DINOv3.

---

## 1. Cấu Trúc Ma Trận Không Gian - Thời Gian Gốc $(66 \times 72)$

Mỗi mẫu quan sát tại thời điểm $t$ được biểu diễn dưới dạng ma trận kích thước:
$$H \times W = 66 \times 72$$

Trong đó:
- **Chiều cao ($H = 66$):** Tương ứng với 6 trạm $\times$ 11 biến khí tượng.
- **Chiều rộng ($W = 72$):** Tương ứng với 72 mốc thời gian quá khứ $[t-71, t]$ (chu kỳ 5 phút $\rightarrow$ 6 giờ lịch sử).

### Thứ tự các hàng (Row Index Mapping)
Mỗi hàng $r \in [0, 65]$ đại diện cho cặp $(\text{Station}, \text{Variable})$ cố định:

| Dải hàng (Row Index) | Trạm quan trắc (`Station ID`) | Danh mục 11 biến theo thứ tự |
| :---: | :--- | :--- |
| **0 – 10** | `ST01_HOANKIEM` | `temperature`, `humidity`, `dew_point`, `apparent_temperature`, `surface_pressure`, `precipitation`, `cloud_cover`, `wind_speed_10m`, `wind_gusts_10m`, `solar_radiation`, `direct_radiation` |
| **11 – 21** | `ST02_BADINH` | (11 biến tương tự theo thứ tự trên) |
| **22 – 32** | `ST03_CAUGIAY` | (11 biến tương tự theo thứ tự trên) |
| **33 – 43** | `ST04_HADONG` | (11 biến tương tự theo thứ tự trên) |
| **44 – 54** | `ST05_DONGANH` | (11 biến tương tự theo thứ tự trên) |
| **55 – 65** | `ST06_SOCSON` | (11 biến tương tự theo thứ tự trên) |

### Thứ tự các cột (Column Index Mapping)
Mỗi cột $c \in [0, 71]$ đại diện cho mốc thời gian $t - (71 - c) \times 5$ phút:
- Cột $0$: Thời điểm $t - 71$ (6 giờ trước thời điểm dự báo).
- Cột $71$: Thời điểm $t$ (mốc quan sát gần nhất trước khi dự báo).

---

## 2. Ý Nghĩa Vật Lý Của 3 Kênh (Three-Channel Tensor: $3 \times H \times W$)

Tensor ảnh gồm 3 kênh $C \in \{0, 1, 2\}$:

1. **Kênh 0 - Normalized Values ($Z$-Score):**
   $$C_0[r, c] = \frac{x[r, c] - \mu_r^{\text{train}}}{\sigma_r^{\text{train}}}$$
   Trong đó $\mu_r^{\text{train}}, \sigma_r^{\text{train}}$ được tính độc quyền từ tập Train. Bảo toàn độ lớn tương đối và tương quan giữa các biến.

2. **Kênh 1 - Past Temporal Deltas (Sai phân biến thiên quá khứ):**
   $$C_1[r, c] = \begin{cases} 0 & \text{khi } c = 0 \\ C_0[r, c] - C_0[r, c-1] & \text{khi } c \ge 1 \end{cases}$$
   Phản ánh tốc độ biến thiên tức thời (nhiệt độ tăng/giảm nhanh, áp suất sụt giảm trước giông lốc).

3. **Kênh 2 - Observation Mask (Mặt nạ trạng thái quan sát):**
   $$C_2[r, c] = \begin{cases} 1.0 & \text{nếu ô dữ liệu thực tế hợp lệ} \\ 0.0 & \text{nếu ô dữ liệu bị khuyết thiếu/imputed} \end{cases}$$
   Cho phép backbone DINOv3 phân biệt chính xác giữa dữ liệu thực và dữ liệu điền khuyết.

---

## 3. Nội Suy Lên Kích Thước DINOv3 ($224 \times 224$)

Để tương thích với Vision Transformer ViT-S/16 (yêu cầu ảnh vuông $224 \times 224$ chia hết cho patch size $16 \times 16 = 196$ patches):
$$\text{Tensor } (3, 66, 72) \xrightarrow{\text{Bilinear Interpolation}} \text{Tensor } (3, 224, 224)$$

### Cam Kết Chống Rò Rỉ Thời Gian (Zero Future Leakage)
Toàn bộ thông tin trong tensor $(3, 224, 224)$ được trích xuất hoàn toàn từ quá khứ $[t-71, t]$. Thay đổi bất kỳ dữ liệu nào sau thời điểm $t$ (ví dụ tại $t+1, t+12$) **không làm thay đổi dù chỉ 1 pixel** trong tensor ảnh đầu vào.
