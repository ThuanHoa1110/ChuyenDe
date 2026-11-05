# Quyết Định Cấp Phép & Bản Quyền (Licensing Decisions)

Tài liệu này xác lập ranh giới pháp lý, quyền sở hữu trí tuệ và phương án phân phối dữ liệu / mô hình theo yêu cầu của **Bước 0.2** trong Kế hoạch chi tiết.

---

## 1. Bảng phân quyền dữ liệu quan trắc thời tiết

| Hạng mục dữ liệu | Được lưu private | Được dùng huấn luyện | Được công bố Raw | Được công bố Processed | Điều kiện ghi nguồn / Ghi chú |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dữ liệu 6 trạm mẫu (`data/sample/` 1.000 dòng)** | **CÓ** | **CÓ** | **CÓ** (Chỉ mẫu test) | **CÓ** | Mẫu kiểm thử nội bộ (smoke test), do người dùng tổng hợp. Được phép commit vào Git repo để phục vụ test pipeline. |
| **Dữ liệu thô mở rộng cào mạng (`data/raw/` & `data/private/`)** | **CÓ** | **CÓ** | **KHÔNG** | **CẦN DUYỆT** | Nguồn gốc từ AI cào web chưa xác minh nhà cung cấp gốc. **Cấm tuyệt đối** công bố raw lên Kaggle/GitHub để tránh rủi ro bản quyền của bên thứ ba. |
| **Tập dữ liệu phát hành Kaggle (Dự kiến Phase 1)** | **CÓ** | **CÓ** | **KHÔNG** | **CÓ** (Sau làm sạch) | Chỉ công bố bản đã xử lý (processed/aggregated) kèm DATA_CARD mô tả rõ giới hạn và ghi nhận quyền tác giả biên soạn của người dùng. |

### Nguyên tắc quản lý dữ liệu (Data Governance)
1. Tuyệt đối không commit tệp dữ liệu thô lớn hoặc dữ liệu private vào Git (`.gitignore` đã được cấu hình chặt chẽ).
2. Khi phát hành dataset trên Kaggle ở Phase 1, phải cung cấp `dataset-metadata.json` với giấy phép mở phù hợp (ví dụ: `CC-BY-4.0` hoặc `DbCL`) cho bản đã xử lý.

---

## 2. Bảng bản quyền mô hình và trọng số DINOv3

| Hạng mục | Nguồn gốc / Cơ quan | Giấy phép (License) | Phương án phân phối & Sử dụng |
| :--- | :--- | :--- | :--- |
| **Mã nguồn DINOv3** | Meta AI Research | Apache-2.0 / MIT | Tích hợp vào thư mục `src/weather/models/` hoặc gọi qua PyTorch Hub / Hugging Face Transformers. |
| **Trọng số Checkpoint DINOv3** (ViT-S/16) | Meta AI Research | Gated Research / Non-commercial | **Quy tắc bất biến:** Không nướng trực tiếp trọng số vào Docker image công khai hoặc commit lên GitHub. |

### Phương án truy cập Checkpoint hợp lệ lúc Runtime:
1. **Qua biến môi trường:** Sử dụng `HF_TOKEN` trong `.env` để tải trực tiếp từ Hugging Face Hub khi chạy lần đầu.
2. **Qua cơ chế Docker Mount:** Khi triển khai container, nạp checkpoint từ ổ cứng máy chủ thông qua cờ mount:
   ```bash
   docker run -p 8000:8000 -v /path/to/checkpoints:/models:ro hanoi-temperature:v1.0.0
   ```
3. Phương án này bảo đảm 100% tuân thủ điều khoản phân phối của Meta và quy tắc cốt lõi của dự án (Quy tắc 20 trong tài liệu kế hoạch).

---

## 3. Kết luận nghiệm thu cổng bản quyền (Phase 0 Gate)

- Không còn nguồn dữ liệu không rõ ràng trong các gói xuất bản công khai.
- Đã thiết lập cơ chế bảo vệ checkpoint DINOv3 an toàn và có kiểm soát.
- Đạt điều kiện nghiệm thu của Bước 0.2.

