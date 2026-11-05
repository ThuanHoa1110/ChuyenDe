# DATA CARD: Hanoi Multi-Station Short-Term Meteorology Benchmark Dataset

## 1. Dataset Summary (Tóm tắt dữ liệu)
- **Tên tập dữ liệu:** Hanoi Multi-Station Short-Term Meteorology Benchmark Dataset (Decadal 6.3M Benchmark)
- **Mục tiêu nghiên cứu:** Cung cấp bộ chuẩn benchmark chuỗi thời gian không gian - thời gian tần suất cao (5 phút/mẫu) phục vụ bài toán dự báo nhiệt độ ngắn hạn ($t + 60$ phút) kết hợp biến ngoại sinh và mô hình nền tảng thị giác **DINOv3 (Meta AI)**.
- **Quy mô:** 6 trạm quan trắc $\times$ 1,052,064 mẫu = **6,312,384 bản ghi (hơn 6.3 triệu dòng)**.
- **Phạm vi thời gian:** 10 năm liên tục từ `2016-01-01 00:00:00` đến `2025-12-31 23:55:00`.
- **Múi giờ:** Asia/Ho_Chi_Minh (UTC+7).
- **Chu kỳ lấy mẫu:** 5 phút một lần (`5min`).
- **Giấy phép công bố:** Creative Commons Attribution 4.0 International (CC-BY-4.0).

---

## 2. Mạng Lưới 6 Trạm Quan Trắc Hà Nội (Station Network)

| Mã trạm (`station_id`) | Khu vực quan trắc | Tọa độ địa lý | Đặc trưng tiểu khí hậu |
| :--- | :--- | :--- | :--- |
| `ST01_HOANKIEM` | Quận Hoàn Kiếm | $21.0285^\circ\text{N}, 105.8542^\circ\text{E}$ | Đô thị lõi cổ, hiệu ứng đảo nhiệt đô thị (Urban Heat Island) rõ nét nhất ($+1.2^\circ\text{C}$). |
| `ST02_BADINH` | Quận Ba Đình | $21.0341^\circ\text{N}, 105.8236^\circ\text{E}$ | Trung tâm hành chính, điều hòa nhiệt bởi hồ Tây và mật độ cây xanh ($+0.4^\circ\text{C}$). |
| `ST03_CAUGIAY` | Quận Cầu Giấy | $21.0362^\circ\text{N}, 105.7905^\circ\text{E}$ | Khu đô thị mới, mật độ giao thông và cao ốc văn phòng cao ($+0.8^\circ\text{C}$). |
| `ST04_HADONG` | Quận Hà Đông | $20.9721^\circ\text{N}, 105.7766^\circ\text{E}$ | Vành đai đô thị hóa phía Tây Nam Hà Nội ($0.0^\circ\text{C}$). |
| `ST05_DONGANH` | Huyện Đông Anh | $21.1367^\circ\text{N}, 105.8468^\circ\text{E}$ | Vành đai công nghiệp và đồng bằng phía Bắc sông Hồng ($-0.6^\circ\text{C}$). |
| `ST06_SOCSON` | Huyện Sóc Sơn | $21.2825^\circ\text{N}, 105.8494^\circ\text{E}$ | Vùng đồi gò bán sơn địa, địa hình cao, nhiệt độ thấp hơn trung tâm ($-1.5^\circ\text{C}$). |

---

## 3. Đặc Tả Thuộc Tính Dữ Liệu (Schema & Data Dictionary)

Mỗi trạm bao gồm 13 trường dữ liệu:

| Tên trường | Kiểu dữ liệu | Đơn vị đo | Ý nghĩa vật lý | Miền kiểm tra hợp lệ |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | Datetime (ISO) | `YYYY-MM-DD HH:MM:SS` | Mốc thời gian ghi nhận dữ liệu | `2016-01-01` đến `2025-12-31` |
| `station_id` | String | Danh định trạm | Mã trạm quan trắc (`ST01` .. `ST06`) | Cố định theo file |
| `temperature` | Float | °C | Nhiệt độ không khí ở 2m (**Biến mục tiêu**) | [-10.0, 50.0] |
| `humidity` | Float | % | Độ ẩm tương đối | [0.0, 100.0] |
| `dew_point` | Float | °C | Điểm sương của không khí | [-20.0, 40.0] |
| `apparent_temperature` | Float | °C | Nhiệt độ cảm nhận thực tế | [-15.0, 55.0] |
| `surface_pressure` | Float | hPa | Áp suất khí quyển bề mặt | [900.0, 1100.0] |
| `precipitation` | Float | mm | Lượng mưa tích lũy tức thời | [0.0, 300.0] |
| `cloud_cover` | Float | % | Độ che phủ mây toàn bầu trời | [0.0, 100.0] |
| `wind_speed_10m` | Float | m/s | Tốc độ gió ở độ cao 10m | [0.0, 60.0] |
| `wind_gusts_10m` | Float | m/s | Gió giật cực đại ở 10m | [0.0, 80.0] |
| `solar_radiation` | Float | W/m² | Bức xạ mặt trời tổng cộng | [0.0, 1500.0] |
| `direct_radiation` | Float | W/m² | Bức xạ mặt trời trực tiếp | [0.0, 1200.0] |

---

## 4. Kiểm Soát Chất Lượng & Tính Hợp Lệ (Quality Assurance)

1. **Tính đơn điệu và chu kỳ:** 100% mốc thời gian tăng đơn điệu đều đặn đúng 5 phút một lần, không có khoảng nhảy cách bất thường.
2. **Giá trị khuyết thiếu (NaN):** Tỷ lệ missing là **0.00%** trên toàn bộ 6.3 triệu bản ghi.
3. **Đồng bộ hóa đồng hồ (Clock Synchronization):** Cả 6 trạm có timestamp hoàn toàn trùng khớp từng bước quan trắc, không có độ trôi đồng hồ (clock drift = 0).
4. **Quy luật vật lý:** Dữ liệu thỏa mãn các nguyên lý nhiệt động học khí quyển: $T \ge T_{\text{dew}}$, độ ẩm tăng cao khi có mưa, bức xạ đêm bằng 0.

---

## 5. Giới Hạn Của Dữ Liệu (Limitations)

- Dữ liệu thu thập và tinh chỉnh dựa trên mô hình tái phân tích khí tượng và AI cào mạng đa nguồn do tác giả biên soạn, phản ánh sát đặc trưng khí hậu nhiệt đới gió mùa Hà Nội.
- Phục vụ nghiên cứu học thuật và huấn luyện thử nghiệm mô hình trí tuệ nhân tạo. Người dùng không nên sử dụng đơn lẻ cho mục đích cảnh báo thiên tai khẩn cấp mang tính pháp lý.

