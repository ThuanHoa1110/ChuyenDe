# Báo Cáo Chất Lượng Dữ Liệu (Data Quality Report)

**Phiên bản dữ liệu (Data Version):** `v1.0.0`  
**Thời điểm tạo:** 2026-11-05 05:10:39 UTC  
**Tập tin chính:** `weather_wide_synced.csv.gz`  
**Mã băm SHA-256:** `1a449407ab7983bdfb3838376d792668e1e587af3fa73f7b87a43da57e92e30b`  

---

## 1. Tổng Quan Quy Mô Bảng Wide Đồng Bộ

- **Tổng số mốc thời gian đồng bộ:** 1,052,064 dòng  
- **Tổng số cột:** 67 cột (1 timestamp + 6 trạm x 11 biến khí tượng)  
- **Mốc bắt đầu:** `2016-01-01 00:00:00`  
- **Mốc kết thúc:** `2025-12-31 23:55:00`  
- **Chu kỳ lấy mẫu:** Cố định 5 phút (`5min`)  
- **Múi giờ:** Asia/Ho_Chi_Minh (UTC+7)  

---

## 2. Kết Quả Kiểm Tra Độc Lập Từng Trạm

| Mã trạm | Số dòng | Trùng khóa `(st, t)` | NaN Rate (%) | Ngoài miền vật lý | Thứ tự thời gian | Kết luận |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `ST01_HOANKIEM` | 1,052,064 | 0 (0.00%) | 0 (0.00%) | 0 | Tăng đơn điệu 5p | ✅ ĐẠT |
| `ST02_BADINH` | 1,052,064 | 0 (0.00%) | 0 (0.00%) | 0 | Tăng đơn điệu 5p | ✅ ĐẠT |
| `ST03_CAUGIAY` | 1,052,064 | 0 (0.00%) | 0 (0.00%) | 0 | Tăng đơn điệu 5p | ✅ ĐẠT |
| `ST04_HADONG` | 1,052,064 | 0 (0.00%) | 0 (0.00%) | 0 | Tăng đơn điệu 5p | ✅ ĐẠT |
| `ST05_DONGANH` | 1,052,064 | 0 (0.00%) | 0 (0.00%) | 0 | Tăng đơn điệu 5p | ✅ ĐẠT |
| `ST06_SOCSON` | 1,052,064 | 0 (0.00%) | 0 (0.00%) | 0 | Tăng đơn điệu 5p | ✅ ĐẠT |

---

## 3. Kiểm Tra Đồng Bộ Hóa Đồng Hồ Giữa Các Trạm (Clock Drift)

- **Trạng thái đồng bộ:** ✅ 100% Khớp timestamp giữa 6 trạm
- **Số lượng mốc thời gian từng trạm:** Cả 6 trạm đều đạt chính xác 1,052,064 bản ghi.
- **Hiện tượng lệch pha:** 0 lỗi lệch đồng hồ.

---

## 4. Danh Mục Biến và Ranh Giới Kiểm Tra Vật Lý (Physical Sanity Checks)

| Tên biến | Đơn vị | Ngưỡng kiểm tra tối thiểu | Ngưỡng kiểm tra tối đa | Số lỗi phát hiện |
| :--- | :---: | :---: | :---: | :---: |
| `temperature` | chuẩn | -10.0 | 50.0 | 0 |
| `humidity` | chuẩn | 0.0 | 100.0 | 0 |
| `dew_point` | chuẩn | -20.0 | 40.0 | 0 |
| `apparent_temperature` | chuẩn | -15.0 | 55.0 | 0 |
| `surface_pressure` | chuẩn | 900.0 | 1100.0 | 0 |
| `precipitation` | chuẩn | 0.0 | 300.0 | 0 |
| `cloud_cover` | chuẩn | 0.0 | 100.0 | 0 |
| `wind_speed_10m` | chuẩn | 0.0 | 60.0 | 0 |
| `wind_gusts_10m` | chuẩn | 0.0 | 80.0 | 0 |
| `solar_radiation` | chuẩn | 0.0 | 1500.0 | 0 |
| `direct_radiation` | chuẩn | 0.0 | 1200.0 | 0 |

---

## 5. Quy Tắc Xử Lý Khuyết Thiếu & Cam Kết Chống Rò Rỉ Tương Lai (Data Leakage)

1. **Missing Data Policy:** Trong tập dữ liệu hiện tại, tỷ lệ missing là **0.00%**. Nếu xuất hiện dữ liệu khuyết thiếu trong tương lai, hệ thống áp dụng cơ chế kênh mask quan sát (Channel 3 của DINOv3 input tensor) và nội suy chỉ dựa vào dữ liệu quá khứ ($t' \le t$).
2. **Chống Data Leakage:** Không sử dụng bất kỳ biến tính toán hay biến tổng hợp nào có liên quan đến các mốc thời gian tương lai ($t' > t$). Nhãn dự báo nhiệt độ tại $t + 12$ hoàn toàn tách biệt khỏi không gian đặc trưng đầu vào.
