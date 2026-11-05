# Thư mục Dữ liệu (Data Directory)

Thư mục này quản lý dữ liệu phục vụ nghiên cứu và huấn luyện mô hình dự báo nhiệt độ ngắn hạn cho 6 trạm tại Hà Nội.

## Cấu trúc thư mục

- `sample/`: Chứa dữ liệu mẫu tối thiểu (6 file CSV, mỗi trạm 1.000 dòng, chu kỳ 5 phút từ 01/01/2016 00:00:00 đến 04/01/2016 11:15:00). Thư mục này được commit lên Git phục vụ unit test và smoke test.
- `raw/`: Lưu trữ dữ liệu thô tải về, có dung lượng lớn. **Bị loại bỏ bởi `.gitignore`**, không commit lên Git.
- `private/`: Lưu trữ dữ liệu mở rộng nội bộ phục vụ huấn luyện quy mô lớn. **Bị loại bỏ bởi `.gitignore`**.
- `processed/`: Dữ liệu sau khi làm sạch, đồng bộ hóa timestamp 6 trạm và chuẩn hóa. **Bị loại bỏ bởi `.gitignore`**.

## Danh sách 6 trạm quan trắc Hà Nội

1. `st01_hoankiem.csv` (`ST01_HOANKIEM`)
2. `st02_badinh.csv` (`ST02_BADINH`)
3. `st03_caugiay.csv` (`ST03_CAUGIAY`)
4. `st04_hadong.csv` (`ST04_HADONG`)
5. `st05_donganh.csv` (`ST05_DONGANH`)
6. `st06_socson.csv` (`ST06_SOCSON`)

## Từ điển dữ liệu (Data Dictionary)

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

## Giấy phép & Điều khoản dữ liệu

Xem chi tiết kiểm kê dữ liệu tại [docs/data_inventory.md](../docs/data_inventory.md) và chính sách cấp phép tại [docs/licensing_decisions.md](../docs/licensing_decisions.md).
Dữ liệu thô và tập dữ liệu quy mô lớn không được tự ý công bố công khai khi chưa có giấy phép rõ ràng.

