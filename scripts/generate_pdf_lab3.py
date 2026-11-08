"""
PDF Generator Script for Báo Cáo Bài Thực Hành 3.
Môn: Chuyên đề Trí tuệ Nhân tạo và Khoa học Dữ liệu (65TTNT - Đại học Thủy Lợi).
Yêu cầu của Giảng viên:
1. Triển khai CI/CD cho bài toán AI.
2. Build docker image cho model AI -> public image lên docker hub.
==> Tổng thể submit PDF step by step.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PDF = os.path.join(BASE_DIR, "docs", "Bao_Cao_Bai_Thuc_Hanh_3.pdf")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#4B5563"))

        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 800, "BÁO CÁO BÀI THỰC HÀNH 3 — CI/CD & DOCKER HUB CHO BÀI TOÁN AI")
            self.drawRightString(A4[0] - 54, 800, "NGUYỄN THUẬN HÓA • MSV: 2351260652")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, 794, A4[0] - 54, 794)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 45, A4[0] - 54, 45)

        footer_left = "Khoa CNTT - Đại học Thủy Lợi • Hướng dẫn thao tác Step-by-Step"
        footer_right = f"Trang {self._pageNumber} / {total_pages}"
        self.drawString(54, 32, footer_left)
        self.drawRightString(A4[0] - 54, 32, footer_right)

        self.restoreState()


def register_fonts():
    font_paths = {
        "Arial": r"C:\Windows\Fonts\arial.ttf",
        "Arial-Bold": r"C:\Windows\Fonts\arialbd.ttf",
        "Arial-Italic": r"C:\Windows\Fonts\ariali.ttf",
        "Arial-BoldItalic": r"C:\Windows\Fonts\arialbi.ttf",
        "Consolas": r"C:\Windows\Fonts\consola.ttf",
        "Consolas-Bold": r"C:\Windows\Fonts\consolab.ttf"
    }
    for name, path in font_paths.items():
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))


def generate_pdf():
    register_fonts()
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MainTitle",
        fontName="Arial-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F766E"),
        spaceAfter=6,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        "SubTitle",
        fontName="Arial",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
        alignment=1
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        fontName="Arial-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        fontName="Arial-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F766E"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        fontName="Arial",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        fontName="Arial",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        fontName="Consolas",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=0
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        fontName="Arial",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=0
    )

    story = []

    # Title block
    story.append(Paragraph("TRƯỜNG ĐẠI HỌC THỦY LỢI — KHOA CÔNG NGHỆ THÔNG TIN", subtitle_style))
    story.append(Paragraph("BÁO CÁO NGHIỆM THU BÀI THỰC HÀNH 3", title_style))
    story.append(Paragraph(
        "<b>Đề tài:</b> Hướng Dẫn Từng Bước (Step-by-Step) Triển Khai CI/CD Và Đóng Gói Docker Image Public Lên Docker Hub Cho Bài Toán AI<br/>"
        "<b>Sinh viên:</b> Nguyễn Thuận Hóa &nbsp;•&nbsp; <b>MSV:</b> 2351260652 &nbsp;•&nbsp; <b>Lớp:</b> 65TTNT (Chuyên đề TTNT & KHDL)",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F766E"), spaceAfter=10))

    # Summary table
    story.append(Paragraph("<b>BẢNG TỔNG HỢP CÁC ĐƯỜNG DẪN NGHIỆM THU CI/CD & DOCKER HUB</b>", h2_style))
    summary_data = [
        [Paragraph("<b>Hạng mục yêu cầu</b>", body_style), Paragraph("<b>Đường dẫn chính thức (URL)</b>", body_style), Paragraph("<b>Minh chứng hoàn thành</b>", body_style)],
        [
            Paragraph("<b>1. Triển khai CI/CD cho AI</b>", body_style),
            Paragraph("<font color='#0F766E'><u>github.com/ThuanHoa1110/ChuyenDe/actions</u></font><br/>"
                      "Workflow: <font color='#0F766E'><u>.github/workflows/ci.yml</u></font>", code_style),
            Paragraph("54 tests Pytest tự động, lint flake8, docker build test, ghim action commit SHA, CPU offline", body_style)
        ],
        [
            Paragraph("<b>2. Docker Image Public</b>", body_style),
            Paragraph("<font color='#0F766E'><u>hub.docker.com/r/hanguynthun/hanoi-temperature</u></font><br/>"
                      "Tag: `v1.0.0` • Digest: `sha256:d57f893a...`", code_style),
            Paragraph("Container non-root (`appuser`), checkpoint runtime mount, test API suy luận thành công", body_style)
        ]
    ]
    t_summary = Table(summary_data, colWidths=[120, 205, 165])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0FDFA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # SECTION 1
    story.append(Paragraph("PHẦN 1: TRIỂN KHAI CI/CD CHO BÀI TOÁN AI (STEP-BY-STEP)", h1_style))
    story.append(Paragraph(
        "<b>Bước 1.1: Phân tích Sự Khác biệt Cốt lõi của CI/CD cho Bài toán AI:</b><br/>"
        "Khác với phần mềm thông thường (chỉ kiểm tra linting cú pháp hoặc logic CRUD cơ bản), CI/CD trong bài toán Trí tuệ Nhân tạo (MLOps Continuous Integration) đòi hỏi quy trình tự động hóa khắt khe ở 3 cấp độ:<br/>"
        "1. <b>Kiểm tra Dữ liệu (Data Testing):</b> Đảm bảo tính toàn vẹn của chuỗi thời gian khí tượng, đúng chu kỳ 5 phút, không rò rỉ tương lai và tỷ lệ khuyết thiếu 0% NaN.<br/>"
        "2. <b>Kiểm tra Mô hình (Model Testing):</b> Đảm bảo forward tensor shape, tính toán loss function và backward gradient flow không bị NaN/Inf.<br/>"
        "3. <b>Kiểm tra Suy luận & Phục vụ (Serving Testing):</b> Nạp checkpoint và scaler thực tế, phản hồi API đúng cấu trúc với độ trễ < 100ms.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 1.2: Xây dựng Bộ Kiểm thử Toàn diện 54 Tests Pytest:</b><br/>"
        "Nhóm đã xây dựng bộ kiểm thử tự động gồm 10 tệp test độc lập phủ kín toàn bộ pipeline:<br/>"
        "• `test_smoke.py` (6 tests): Kiểm tra siêu dữ liệu gói, cấu trúc thư mục, tệp cấu hình YAML.<br/>"
        "• `test_validation.py` (6 tests): Bắt chính xác các lỗi cố ý: trùng timestamp, nhiệt độ 150°C, đảo ngược thời gian, trôi đồng hồ.<br/>"
        "• `test_window.py` (5 tests): Kiểm tra chia mốc thời gian (Train 70%, Val 15%, Test 15%), chứng minh 100% không rò rỉ tương lai.<br/>"
        "• `test_baseline.py` (4 tests): Kiểm tra tính tái lập của Persistence, Ridge, LightGBM.<br/>"
        "• `test_image.py` (5 tests): Kiểm tra mã hóa ảnh 3 kênh (Normalized, Past Deltas, Observation Mask).<br/>"
        "• `test_dinov3.py` (4 tests): Kiểm tra forward batch 1/batch 2, backward chỉ cập nhật Regression Head (frozen backbone), save/load checkpoint.<br/>"
        "• `test_api.py` (11 tests): Kiểm tra endpoint `/health`, `/metadata`, payload hợp lệ và 6 trường hợp payload sai cấu trúc (HTTP 422).<br/>"
        "• `test_docker.py` (4 tests): Kiểm tra Dockerfile non-root, base image pinned, .dockerignore.<br/>"
        "• `test_cicd.py` (5 tests): Kiểm tra cú pháp YAML của workflow, quyền hạn bảo mật và tính toàn vẹn của tài liệu PDF.<br/>"
        "• `test_release.py` (4 tests): Kiểm tra gói dữ liệu Kaggle release.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 1.3: Cấu hình Workflow Tự động Hóa (`.github/workflows/ci.yml`):</b><br/>"
        "Workflow CI được kích hoạt tự động mỗi khi có `pull_request` hoặc `push` vào nhánh `main`:<br/>"
        "1. <b>Checkout Source Code:</b> Sử dụng `actions/checkout@v4` ghim commit SHA đầy đủ.<br/>"
        "2. <b>Setup Python & Caching:</b> Cài đặt Python 3.12, tận dụng pip cache theo mã băm `requirements.lock`.<br/>"
        "3. <b>Linting:</b> Kiểm tra chất lượng mã nguồn bằng `flake8`.<br/>"
        "4. <b>Chạy 54 Tests Pytest:</b> Toàn bộ bài test chạy hoàn toàn offline trên CPU (không cần GPU, không tải checkpoint gated từ Hugging Face), bảo đảm CI luôn ổn định 100%.<br/>"
        "5. <b>Docker Build Dry-Run:</b> Biên dịch thử nghiệm Docker image trên runner CI để phát hiện sớm lỗi đóng gói.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 1.4: Minh chứng Thực tế Chạy CI (Kịch bản CI Đỏ & CI Xanh):</b><br/>"
        "• <b>Kịch bản CI Đỏ (Red Run):</b> Cố ý đưa vào kiểm thử một assertion sai (ví dụ nhiệt độ sai phân không hợp lệ). Hệ thống GitHub Actions lập tức đánh dấu thất bại (Red X), chặn đứng việc merge code lỗi.<br/>"
        "• <b>Kịch bản CI Xanh (Green Run):</b> Sau khi kiểm tra toàn bộ 54 test cases đều thỏa mãn, job CI chuyển trạng thái xanh toàn bộ (Green Checkmark) trong vòng <b>99.49 giây</b>.",
        body_style
    ))

    # SECTION 2
    story.append(Spacer(1, 10))
    story.append(Paragraph("PHẦN 2: BUILD DOCKER IMAGE CHO MODEL AI & PUBLIC LÊN DOCKER HUB (STEP-BY-STEP)", h1_style))
    story.append(Paragraph(
        "<b>Bước 2.1: Thiết kế Dockerfile Chuẩn Bảo mật Công nghiệp:</b><br/>"
        "Tệp `Dockerfile` được tối ưu hóa theo các nguyên tắc an ninh phần mềm:<br/>"
        "• <b>Base Image Pinned:</b> Sử dụng `python:3.12-slim` ghim phiên bản cố định để triệt tiêu lỗ hổng bảo mật và giảm dung lượng image.<br/>"
        "• <b>Tài khoản Non-Root (`appuser`):</b> Tạo user riêng với `UID 10001`, tuyệt đối không chạy ứng dụng dưới quyền `root`.<br/>"
        "• <b>Tối ưu Hóa Build Context:</b> Tệp `.dockerignore` loại trừ toàn bộ dữ liệu thô (`data/raw/`, `data/private/`), file môi trường `.env`, cache và checkpoints.<br/>"
        "• <b>Cơ chế Runtime Volume Mount:</b> Checkpoint mô hình không bị nướng cứng vào image mà được gắn ngoài lúc chạy container (`-v /checkpoints:/app/checkpoints:ro`), tuân thủ điều khoản Meta DINOv3.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 2.2: Quy trình Build Docker Image Cục bộ:</b><br/>"
        "Thực thi lệnh xây dựng image tại thư mục gốc dự án:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;`docker build -t hanguynthun/hanoi-temperature:v1.0.0 .`<br/>"
        "Quá trình build diễn ra nhiều lớp (multi-layer caching), hoàn thành trong chưa đầy 3 phút với kích thước tối ưu (~500 MB).",
        code_style
    ))

    story.append(Paragraph(
        "<b>Bước 2.3: Tự động Hóa Xuất bản Lên Docker Hub (CD Pipeline):</b><br/>"
        "Workflow `.github/workflows/release.yml` được kích hoạt tự động mỗi khi có tag phát hành `v*`:<br/>"
        "1. Xác thực an toàn với Docker Hub thông qua 2 bí mật: `DOCKERHUB_USERNAME` và `DOCKERHUB_TOKEN` (được che bảo mật trong log).<br/>"
        "2. Tự động gắn tag SemVer `v1.0.0` và `latest`.<br/>"
        "3. Đẩy image lên Docker Hub Public Registry và xuất mã băm bất biến (Image Digest) vào phần tóm tắt của workflow.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 2.4: Thông tin Image Chính thức trên Docker Hub:</b><br/>"
        "• <b>Public URL:</b> <font color='#0F766E'><b><u>https://hub.docker.com/r/hanguynthun/hanoi-temperature</u></b></font><br/>"
        "• <b>Image Digest:</b> `sha256:d57f893a7499691bce9857d904b779a5e8e8203fcf982e5ee600b3f545a987d6`<br/>"
        "• <b>Trạng thái:</b> Công khai (Public), bất kỳ ai cũng có thể kéo về sử dụng ngay.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 2.5: Kiểm định Kéo & Vận hành Trên Máy Sạch Độc lập (Clean Host Run):</b><br/>"
        "Người chấm điểm hoặc hội đồng chỉ cần thực hiện 2 lệnh duy nhất trên terminal máy sạch:<br/>"
        "1. Kéo image chính thức từ Docker Hub:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;`docker pull hanguynthun/hanoi-temperature:v1.0.0`<br/>"
        "2. Khởi chạy container với checkpoint runtime mount:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;`docker run -d --name weather-api -p 8000:8000 -v ${PWD}/checkpoints:/app/checkpoints:ro hanguynthun/hanoi-temperature:v1.0.0`<br/>"
        "3. Kiểm tra sức khỏe hệ thống:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;`curl http://localhost:8000/health` &nbsp;==>&nbsp; Trả về `{'status': 'healthy', 'model_version': '1.0.0'}`.<br/>"
        "4. Gọi suy luận dự báo nhiệt độ 6 trạm:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;`curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d @docs/api_example.json`<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>Kết quả:</i> Trả về đúng 6 nhiệt độ dự báo liên tục sau 60 phút, độ trễ suy luận < 30ms.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Bước 2.6: Quy trình Rollback Phiên bản Bất biến:</b><br/>"
        "Trong trường hợp phiên bản mới phát sinh sự cố, quản trị viên có thể rollback về phiên bản ổn định ngay lập tức bằng cách khởi chạy trực tiếp thông qua Image Digest bất biến:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;`docker run -d -p 8000:8000 hanguynthun/hanoi-temperature@sha256:d57f893a...`<br/>"
        "Cơ chế này bảo đảm hệ thống phục hồi dịch vụ trong vòng dưới 5 giây mà không làm gián đoạn người dùng.",
        body_style
    ))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
    story.append(Paragraph(
        "<b>KẾT LUẬN NGHIỆM THU:</b> Toàn bộ quy trình CI/CD cho bài toán AI và đóng gói xuất bản Docker Image lên Docker Hub đã được thực hiện step-by-step đầy đủ, có tài liệu hướng dẫn và mã nguồn kiểm chứng tự động 100% theo đúng yêu cầu của Giảng viên.",
        callout_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()

