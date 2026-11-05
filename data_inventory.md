# Báo Cáo Kiểm Kê Dữ Liệu (Data Inventory)

Tài liệu này thực hiện theo yêu cầu của **Bước 0.2 (Kiểm kê dữ liệu và giấy phép)** trong Kế hoạch chi tiết dự án dự báo nhiệt độ ngắn hạn đa khu vực tại Hà Nội.

---

## 1. Tổng quan dữ liệu mẫu hiện có

Tập dữ liệu mẫu phục vụ kiểm thử và dựng pipeline bao gồm 6 trạm thời tiết phân bố tại khu vực thủ đô Hà Nội.
- **Thư mục lưu trữ trong repo:** `data/sample/`
- **Tần suất quan trắc:** 5 phút một lần (`00:05:00`)
- **Khoảng thời gian:** Từ `2016-01-01 00:00:00` đến `2016-01-04 11:15:00`
- **Múi giờ (Timezone):** Asia/Ho_Chi_Minh (UTC+7)
- **Tổng số mẫu mỗi trạm:** 1.000 dòng dữ liệu
- **Tình trạng thiếu dữ liệu (NaN):** 0 giá trị thiếu trong toàn bộ 6 file mẫu

---

## 2. Bảng kiểm kê chi tiết 6 trạm thời tiết Hà Nội

| STT | Mã trạm (`station_id`) | Tên tệp tin | Số dòng | Số cột | Khoảng thời gian | Mã băm SHA-256 | Nhà cung cấp gốc |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| 1 | `ST01_HOANKIEM` | `st01_hoankiem.csv` | 1.000 | 13 | `2016-01-01 00:00` – `2016-01-04 11:15` | `825c605410ecd4e2af7bdcf18ca0028526ca00e018f2b308f700d7dcc13b0431` | **Chưa xác minh** (Thu thập qua AI cào web tổng hợp) |
| 2 | `ST02_BADINH` | `st02_badinh.csv` | 1.000 | 13 | `2016-01-01 00:00` – `2016-01-04 11:15` | `a1ef2f4e26272bf648b1911bc641f9e55e0aa9ed05711bcc32a74126a5d99d23` | **Chưa xác minh** (Thu thập qua AI cào web tổng hợp) |
| 3 | `ST03_CAUGIAY` | `st03_caugiay.csv` | 1.000 | 13 | `2016-01-01 00:00` – `2016-01-04 11:15` | `b3f709dd8959da7818d895d6392a3561470f2b2ad51ccf1353b03f3a3957bc46` | **Chưa xác minh** (Thu thập qua AI cào web tổng hợp) |
| 4 | `ST04_HADONG` | `st04_hadong.csv` | 1.000 | 13 | `2016-01-01 00:00` – `2016-01-04 11:15` | `d5750d348a433d6a29f2405f09d41ce329eb3f12318cc1aa1ebe0d430ba56a16` | **Chưa xác minh** (Thu thập qua AI cào web tổng hợp) |
| 5 | `ST05_DONGANH` | `st05_donganh.csv` | 1.000 | 13 | `2016-01-01 00:00` – `2016-01-04 11:15` | `120a29866984022656943473670f00d20ec28af4a447a5968b0d1edbbccc3c4c` | **Chưa xác minh** (Thu thập qua AI cào web tổng hợp) |
| 6 | `ST06_SOCSON` | `st06_socson.csv` | 1.000 | 13 | `2016-01-01 00:00` – `2016-01-04 11:15` | `207f0a07dbd25f330c3d8fbb38ea520b33ac3d42c87142eb26dd625f97f0032c` | **Chưa xác minh** (Thu thập qua AI cào web tổng hợp) |

---

## 3. Đặc tả chi tiết từng trường dữ liệu và đơn vị đo

Cả 6 tệp tin có cùng cấu trúc cột và kiểu dữ liệu chuẩn:

| Cột | Tên trường | Kiểu dữ liệu | Đơn vị đo | Ý nghĩa vật lý | Miền giá trị trong mẫu |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `timestamp` | `object` / datetime | ISO-8601 | Thời điểm quan trắc | `2016-01-01 00:00:00` đến `2016-01-04 11:15:00` |
| 2 | `station_id` | `object` / string | Danh định | Mã định danh trạm | `ST01_HOANKIEM` ... `ST06_SOCSON` |
| 3 | `temperature` | `float64` | °C | Nhiệt độ không khí (Mục tiêu dự báo) | 10.2°C – 22.4°C |
| 4 | `humidity` | `float64` | % | Độ ẩm tương đối | 55.0% – 98.0% |
| 5 | `dew_point` | `float64` | °C | Điểm sương | 8.0°C – 18.5°C |
| 6 | `apparent_temperature`| `float64` | °C | Nhiệt độ cảm nhận thực tế | 9.5°C – 23.0°C |
| 7 | `surface_pressure` | `float64` | hPa | Áp suất khí quyển tại bề mặt | 1010.0 hPa – 1025.0 hPa |
| 8 | `precipitation` | `float64` | mm | Lượng mưa tức thời | 0.0 mm – 5.2 mm |
| 9 | `cloud_cover` | `float64` | % | Mức độ che phủ mây bầu trời | 0% – 100% |
| 10| `wind_speed_10m` | `float64` | m/s | Tốc độ gió tại độ cao 10m | 0.5 m/s – 7.8 m/s |
| 11| `wind_gusts_10m` | `float64` | m/s | Gió giật tại độ cao 10m | 1.0 m/s – 12.5 m/s |
| 12| `solar_radiation` | `float64` | W/m² | Bức xạ mặt trời tổng cộng | 0.0 W/m² – 750.0 W/m² |
| 13| `direct_radiation` | `float64` | W/m² | Bức xạ mặt trời chiếu thẳng | 0.0 W/m² – 450.0 W/m² |

---

## 4. Lệnh kiểm tra và xác minh

Lệnh thực hiện tái tạo kiểm kê dữ liệu:
```powershell
python scripts/inventory_check.py
```
Kết quả ghi nhận trạng thái kiểm kê đạt 100% về tính toàn vẹn và khớp hoàn toàn với quy định tại Kế hoạch chi tiết.

