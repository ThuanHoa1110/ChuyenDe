# Thư Mục Dữ Liệu (Data Directory)

Thư mục này quản lý dữ liệu phục vụ nghiên cứu và huấn luyện mô hình dự báo nhiệt độ ngắn hạn cho 6 trạm tại Hà Nội.

---

## 1. Cấu Trúc Thư Mục Dữ Liệu

- `sample/`: Chứa dữ liệu mẫu tối thiểu (6 file CSV, mỗi trạm 1.000 dòng, chu kỳ 5 phút từ `2016-01-01 00:00:00` đến `2016-01-04 11:15:00`). Thư mục này được commit lên Git phục vụ unit test và smoke test.
- `private/raw_stations/`: Lưu trữ 6 file dữ liệu thô gốc trọn vẹn 10 năm (1,052,064 dòng/trạm = 6,312,384 dòng tổng cộng). **Bị loại bỏ bởi `.gitignore`**, không commit lên Git.
- `processed/`: Chứa bảng wide đồng bộ 6 trạm đã làm sạch và nén (`weather_wide_synced.csv.gz`, 1,052,064 dòng x 67 cột). Kèm bản mẫu 1.000 dòng `weather_wide_synced_sample.csv`. **Bị loại bỏ bởi `.gitignore`**.

---

## 2. Danh Sách 6 Trạm Quan Trắc Hà Nội

1. `st01_hoankiem.csv` (`ST01_HOANKIEM`) – Hoàn Kiếm (Đô thị lõi)
2. `st02_badinh.csv` (`ST02_BADINH`) – Ba Đình (Hồ Tây & trung tâm hành chính)
3. `st03_caugiay.csv` (`ST03_CAUGIAY`) – Cầu Giấy (Đô thị mới & giao thông cao)
4. `st04_hadong.csv` (`ST04_HADONG`) – Hà Đông (Vành đai phía Tây Nam)
5. `st05_donganh.csv` (`ST05_DONGANH`) – Đông Anh (Vành đai công nghiệp phía Bắc)
6. `st06_socson.csv` (`ST06_SOCSON`) – Sóc Sơn (Vùng gò đồi bán sơn địa)

---

## 3. Đặc Tả Thuộc Tính Dữ Liệu

| Tên trường | Kiểu dữ liệu | Đơn vị | Mô tả |
| :--- | :--- | :--- | :--- |
| `timestamp` | String (ISO) | `YYYY-MM-DD HH:MM:SS` | Mốc thời gian ghi nhận dữ liệu |
| `station_id` | String | Mã trạm | Định danh trạm quan trắc |
| `temperature` | Float | °C | Nhiệt độ không khí (biến mục tiêu chính) |
| `humidity` | Float | % | Độ ẩm tương đối |
| `dew_point` | Float | °C | Điểm sương |
| `apparent_temperature` | Float | °C | Nhiệt độ cảm nhận |
| `surface_pressure` | Float | hPa | Áp suất bề mặt |
| `precipitation` | Float | mm | Lượng mưa tích lũy |
| `cloud_cover` | Float | % | Độ che phủ của mây |
| `wind_speed_10m` | Float | m/s | Tốc độ gió ở độ cao 10m |
| `wind_gusts_10m` | Float | m/s | Gió giật ở độ cao 10m |
| `solar_radiation` | Float | W/m² | Bức xạ mặt trời |
| `direct_radiation` | Float | W/m² | Bức xạ trực tiếp |

---

## 4. Quản Lý Tiến Trình & Báo Cáo Chất Lượng

- **Manifest dữ liệu thô:** Xem tại [manifests/raw.json](../manifests/raw.json).
- **Báo cáo kiểm kê ban đầu:** Xem tại [docs/data_inventory.md](../docs/data_inventory.md).
- **Báo cáo chất lượng & xác thực đồng bộ 10 năm:** Xem tại [reports/data_quality.md](../reports/data_quality.md).
- **Quyết định bản quyền & cấp phép:** Xem tại [docs/licensing_decisions.md](../docs/licensing_decisions.md).
