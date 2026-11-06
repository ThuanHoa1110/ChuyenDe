# Báo Cáo Nghiệm Thu API Inference (Phase 4, Bước 4.1)
## (Hanoi Weather Multi-Station Temperature Forecasting API)

- **Ngày thực hiện:** 2026-11-06
- **Môi trường:** Python 3.12, FastAPI 0.162.0, Uvicorn 0.54.0, PyTorch 2.15.0
- **Mô hình phục vụ:** DINOv3 ViT-S/16 Backbone + Multi-Station Non-Linear Regression Head
- **Mã nguồn phục vụ:** [`src/weather/api/app.py`](../src/weather/api/app.py)
- **Tập kiểm thử tự động:** [`tests/test_api.py`](../tests/test_api.py) (11/11 tests PASSED)

---

### 1. Kiểm tra chẩn đoán trạng thái dịch vụ (GET /health)

Endpoint kiểm tra tính sẵn sàng của hệ thống, tải trọng số mô hình và scaler lúc khởi động, đảm bảo không huấn luyện lại mô hình khi có request.

**Lệnh curl mẫu:**
```bash
curl -X GET http://localhost:8000/health
```

**Mã trạng thái HTTP:** `200 OK`

**Nội dung phản hồi (Response Body):**
```json
{
  "status": "healthy",
  "uptime_seconds": 15.42,
  "model_loaded": true,
  "model_name": "DINOv3Forecaster",
  "model_checkpoint": "dinov3_forecaster_best.pt",
  "scaler_loaded": true,
  "device": "cpu",
  "timestamp": "2026-11-06T06:50:29.924970+00:00"
}
```

---

### 2. Truy vấn siêu dữ liệu mô hình & trạm (GET /metadata)

Endpoint cung cấp danh sách định danh chuẩn hóa của 6 trạm khí tượng, thứ tự biến, độ dài cửa sổ trượt (lookback 72 mốc = 6 giờ), khoảng thời gian dự báo (horizon 12 mốc = 60 phút) và bảng chỉ số đối chuẩn tổng thể.

**Lệnh curl mẫu:**
```bash
curl -X GET http://localhost:8000/metadata
```

**Mã trạng thái HTTP:** `200 OK`

**Nội dung phản hồi (Response Body):**
```json
{
  "model_name": "DINOv3Forecaster",
  "model_version": "v1.0.0",
  "data_version": "v1.0.0",
  "task": "Short-term multi-station temperature forecasting in Hanoi (t + 60 mins)",
  "stations": [
    {
      "id": "st01",
      "name": "ST01_HOANKIEM",
      "target_variable": "st01_temperature",
      "district": "Hoàn Kiếm"
    },
    {
      "id": "st02",
      "name": "ST02_BADINH",
      "target_variable": "st02_temperature",
      "district": "Ba Đình"
    },
    {
      "id": "st03",
      "name": "ST03_CAUGIAY",
      "target_variable": "st03_temperature",
      "district": "Cầu Giấy"
    },
    {
      "id": "st04",
      "name": "ST04_HADONG",
      "target_variable": "st04_temperature",
      "district": "Hà Đông"
    },
    {
      "id": "st05",
      "name": "ST05_DONGANH",
      "target_variable": "st05_temperature",
      "district": "Đông Anh"
    },
    {
      "id": "st06",
      "name": "ST06_SOCSON",
      "target_variable": "st06_temperature",
      "district": "Sóc Sơn"
    }
  ],
  "lookback_steps": 72,
  "lookback_hours": 6,
  "horizon_steps": 12,
  "horizon_minutes": 60,
  "step_interval_minutes": 5,
  "num_features": 66,
  "feature_order": [
    "st01_temperature", "st01_humidity", "st01_dew_point", "st01_apparent_temperature",
    "st01_surface_pressure", "st01_precipitation", "st01_cloud_cover", "st01_wind_speed_10m",
    "st01_wind_gusts_10m", "st01_solar_radiation", "st01_direct_radiation",
    "st02_temperature", "st02_humidity", "st02_dew_point", "st02_apparent_temperature",
    "st02_surface_pressure", "st02_precipitation", "st02_cloud_cover", "st02_wind_speed_10m",
    "st02_wind_gusts_10m", "st02_solar_radiation", "st02_direct_radiation",
    "st03_temperature", "st03_humidity", "st03_dew_point", "st03_apparent_temperature",
    "st03_surface_pressure", "st03_precipitation", "st03_cloud_cover", "st03_wind_speed_10m",
    "st03_wind_gusts_10m", "st03_solar_radiation", "st03_direct_radiation",
    "st04_temperature", "st04_humidity", "st04_dew_point", "st04_apparent_temperature",
    "st04_surface_pressure", "st04_precipitation", "st04_cloud_cover", "st04_wind_speed_10m",
    "st04_wind_gusts_10m", "st04_solar_radiation", "st04_direct_radiation",
    "st05_temperature", "st05_humidity", "st05_dew_point", "st05_apparent_temperature",
    "st05_surface_pressure", "st05_precipitation", "st05_cloud_cover", "st05_wind_speed_10m",
    "st05_wind_gusts_10m", "st05_solar_radiation", "st05_direct_radiation",
    "st06_temperature", "st06_humidity", "st06_dew_point", "st06_apparent_temperature",
    "st06_surface_pressure", "st06_precipitation", "st06_cloud_cover", "st06_wind_speed_10m",
    "st06_wind_gusts_10m", "st06_solar_radiation", "st06_direct_radiation"
  ],
  "units": {
    "temperature": "°C",
    "humidity": "%",
    "dew_point": "°C",
    "apparent_temperature": "°C",
    "surface_pressure": "hPa",
    "precipitation": "mm",
    "cloud_cover": "%",
    "wind_speed_10m": "m/s",
    "wind_gusts_10m": "m/s",
    "solar_radiation": "W/m²",
    "direct_radiation": "W/m²"
  },
  "metrics_summary": {
    "persistence_macro_mae": 1.0025,
    "persistence_macro_rmse": 1.0689,
    "ridge_macro_mae": 0.2185,
    "ridge_macro_rmse": 0.2712,
    "lightgbm_macro_mae": 0.2357,
    "lightgbm_macro_rmse": 0.2921,
    "dinov3_macro_mae": 1.5010,
    "dinov3_macro_rmse": 1.7229
  }
}
```

---

### 3. Thực hiện suy luận dự báo nhiệt độ đồng thời 6 trạm (POST /predict)

Endpoint nhận payload mẫu gồm 72 mốc thời gian 6 trạm, nạp và chuẩn hóa dữ liệu, mã hóa tensor ảnh 3 kênh $224 \times 224$ và trả về nhiệt độ dự báo tại $t+60$ phút cho 6 trạm.

**Lệnh curl mẫu:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @docs/api_example.json
```

**Mã trạng thái HTTP:** `200 OK`

**Nội dung phản hồi (Response Body):**
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
    "st04_hadong": 16.5,
    "st05_donganh": 15.93,
    "st06_socson": 15.1
  },
  "units": "°C",
  "latency_ms": 74.4
}
```

---

### 4. Bằng Chứng Nghiệm Thu Bộ Kiểm Thử (Pytest Suite)

Bộ kiểm thử tự động tại [`tests/test_api.py`](../tests/test_api.py) đã thực thi và đạt **100% 11/11 tests PASSED**:

```text
tests/test_api.py::test_health_endpoint PASSED                           [  9%]
tests/test_api.py::test_metadata_endpoint PASSED                         [ 18%]
tests/test_api.py::test_valid_prediction_dict_payload PASSED             [ 27%]
tests/test_api.py::test_valid_prediction_matrix_payload PASSED           [ 36%]
tests/test_api.py::test_api_prediction_matches_direct_model_inference PASSED [ 45%]
tests/test_api.py::test_invalid_payload_wrong_timesteps_count PASSED     [ 54%]
tests/test_api.py::test_invalid_payload_wrong_station_ids PASSED         [ 63%]
tests/test_api.py::test_invalid_payload_non_monotonic_timestamps PASSED  [ 72%]
tests/test_api.py::test_invalid_payload_missing_required_column PASSED   [ 81%]
tests/test_api.py::test_invalid_payload_matrix_dimension_mismatch PASSED [ 90%]
tests/test_api.py::test_invalid_payload_end_timestamp_mismatch PASSED    [100%]
============================== 11 passed in 9.20s ==============================
```

**Các điểm nhấn kỹ thuật quan trọng:**
1. **Kiểm chứng sai số không lệch pha (test_api_prediction_matches_direct_model_inference):**
   So sánh trực tiếp kết quả suy luận qua API với lệnh gọi trực tiếp mô hình trên cùng một mảng số học; sai số tuyệt đối $|\hat{y}_{\text{api}} - \hat{y}_{\text{model}}| < 10^{-2}$ (hoàn toàn tương đồng).
2. **Xử lý nghiêm ngặt các ngoại lệ đầu vào (HTTP 422):**
   - Từ chối khi sai số lượng mốc thời gian ($\neq 72$).
   - Từ chối khi thiếu trạm hoặc sai thứ tự trạm.
   - Từ chối khi thời gian không tăng đều hoặc bước nhảy thời gian bị biến dạng.
   - Từ chối khi thiếu bất kỳ biến nào trong 66 cột đặc trưng.
   - Từ chối khi ma trận không đúng kích thước $(72, 66)$.
   - Từ chối khi mốc `end_timestamp` không trùng khớp với mốc cuối cùng của chuỗi dữ liệu.

