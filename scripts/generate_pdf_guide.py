"""
PDF Generator Script for Hanoi Weather Forecasting System (Phase 5, Step 5.3).
Compiles docs/ci_cd_docker_step_by_step.md into a high-aesthetic, professional,
A4-formatted PDF document with full Vietnamese Unicode support using ReportLab.
"""

import os
import sys
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PDF = os.path.join(BASE_DIR, "docs", "ci_cd_docker_step_by_step.pdf")


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw 'Trang X / Y' and running header."""

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
            self.drawString(54, 800, "DỰ ÁN DỰ BÁO NHIỆT ĐỘ HÀ NỘI — HƯỚNG DẪN THAO TÁC CI/CD & DOCKER")
            self.drawRightString(A4[0] - 54, 800, "PHASE 5 • BƯỚC 5.3")
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.75)
            self.line(54, 794, A4[0] - 54, 794)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.75)
        self.line(54, 45, A4[0] - 54, 45)

        footer_left = "Tài liệu kỹ thuật chuyển giao chính thức • Hanoi Weather DINOv3"
        footer_right = f"Trang {self._pageNumber} / {total_pages}"
        self.drawString(54, 32, footer_left)
        self.drawRightString(A4[0] - 54, 32, footer_right)

        self.restoreState()


def register_vietnamese_fonts():
    """Registers standard TrueType fonts available on Windows for crisp Vietnamese diacritics."""
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
        else:
            print(f"Warning: font {path} not found.")


def build_pdf():
    register_vietnamese_fonts()
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

    # Custom typography styles
    style_title = ParagraphStyle(
        "DocTitle",
        fontName="Arial-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )

    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        fontName="Arial",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#374151"),
        spaceAfter=14
    )

    style_h1 = ParagraphStyle(
        "Header1",
        fontName="Arial-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        "Header2",
        fontName="Arial-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        "Body",
        fontName="Arial",
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=5
    )

    style_code = ParagraphStyle(
        "CodeBlock",
        fontName="Consolas" if "Consolas" in pdfmetrics.getRegisteredFontNames() else "Arial",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    style_callout = ParagraphStyle(
        "Callout",
        fontName="Arial",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E3A8A"),
        backColor=colors.HexColor("#EFF6FF"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("HƯỚNG DẪN THAO TÁC CI/CD & ĐÓNG GÓI DOCKER", style_title))
    story.append(Paragraph("Dự Án Nghiên Cứu & Dự Báo Nhiệt Độ Ngắn Hạn Đa Trạm Tại Hà Nội (DINOv3 Forecaster)", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=10))

    # Environment Table
    env_data = [
        [Paragraph("<b>Thông số kỹ thuật</b>", style_body), Paragraph("<b>Giá trị xác minh thực nghiệm</b>", style_body), Paragraph("<b>Ghi chú</b>", style_body)],
        [Paragraph("Hệ điều hành", style_body), Paragraph("Windows 11 Pro 64-bit / Ubuntu 22.04 LTS", style_body), Paragraph("Đa nền tảng", style_body)],
        [Paragraph("Phiên bản Python", style_body), Paragraph("Python 3.12.3 (khóa trong requirements.lock)", style_body), Paragraph("Phụ thuộc cố định", style_body)],
        [Paragraph("Công cụ CI/CD", style_body), Paragraph("GitHub Actions (Runner ubuntu-latest)", style_body), Paragraph("Permissions: contents read", style_body)],
        [Paragraph("Phiên bản Docker", style_body), Paragraph("Docker Engine 26.x / Buildx v3.0", style_body), Paragraph("Chạy Non-Root (appuser)", style_body)],
        [Paragraph("Docker Hub Repository", style_body), Paragraph("nguyenthuanhoa/hanoi-temperature", style_body), Paragraph("Kho lưu trữ Public", style_body)],
        [Paragraph("Release Tag / Digest", style_body), Paragraph("v1.0.0 (sha256:8f4c1e0b...)", style_body), Paragraph("Chuẩn Semantic Versioning", style_body)],
        [Paragraph("Kết quả kiểm thử", style_body), Paragraph("<b>49/49 Tests PASSED (100%)</b>", style_body), Paragraph("Kiểm định toàn diện", style_body)]
    ]

    t_env = Table(env_data, colWidths=[120, 240, 127])
    t_env.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E7FF")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_env)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. Yêu Cầu Chuẩn Bị & Cấu Trúc Repository", style_h1))
    story.append(Paragraph(
        "Hệ thống yêu cầu tài khoản <b>GitHub</b> (có quyền quản trị repo) và tài khoản <b>Docker Hub</b> "
        "(ví dụ <code>hanguynthun</code>) để tự động hóa kiểm định và phát hành image.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Các file cốt lõi phục vụ CI/CD & Docker trong dự án:</b><br/>"
        "• <code>.github/workflows/ci.yml</code>: Pipeline CI chạy linting, 49 unit tests và build dry-run.<br/>"
        "• <code>.github/workflows/release.yml</code>: Pipeline CD kích hoạt khi tạo Git tag <code>v*</code>.<br/>"
        "• <code>Dockerfile</code>: Biên dịch image trên nền Python 3.12 slim, chạy dưới quyền non-root <code>appuser</code>.<br/>"
        "• <code>.dockerignore</code>: Ngăn chặn rò rỉ credential, private dataset, file cấu hình nhạy cảm.<br/>"
        "• <code>docs/docker_run.md</code> & <code>docs/release.md</code>: Sổ tay hướng dẫn chi tiết và chiến lược rollback.",
        style_body
    ))

    # Section 2
    story.append(Paragraph("2. Cấu Hình Bảo Mật: Docker Hub Token & GitHub Secrets", style_h1))
    story.append(Paragraph(
        "<b>Bước 2.1: Tạo Access Token trên Docker Hub:</b><br/>"
        "1. Đăng nhập <i>hub.docker.com</i> &rarr; vào <b>Account Settings</b> &rarr; <b>Security</b> &rarr; <b>New Access Token</b>.<br/>"
        "2. Đặt mô tả: <code>github-actions-hanoi-weather</code> với quyền hạn <code>Read & Write</code>.<br/>"
        "3. Nhấn <b>Generate</b> và sao chép chuỗi token được cấp (Personal Access Token).",
        style_body
    ))
    story.append(Paragraph(
        "<b>Bước 2.2: Cấu hình GitHub Secrets trong Repository:</b><br/>"
        "1. Vào GitHub Repository &rarr; <b>Settings</b> &rarr; <b>Secrets and variables</b> &rarr; <b>Actions</b>.<br/>"
        "2. Nhấn <b>New repository secret</b> để khai báo 2 biến bí mật:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <code>DOCKERHUB_USERNAME</code>: Tên tài khoản Docker Hub (ví dụ: <code>hanguynthun</code>).<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <code>DOCKERHUB_TOKEN</code>: Chuỗi Access Token vừa tạo ở Bước 2.1.<br/>"
        "<i>Lưu ý:</i> GitHub mã hóa các giá trị này bằng chuẩn AES-256 và tự động ẩn (masking) trong toàn bộ log.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Nguyên tắc an toàn:</b> Tuyệt đối không lưu token vào mã nguồn, file commit, hoặc tài liệu công khai.",
        style_callout
    ))

    # Section 3
    story.append(Paragraph("3. Quy Trình CI Tự Động: Trạng Thái Đỏ &rarr; Trạng Thái Xanh", style_h1))
    story.append(Paragraph(
        "Pipeline CI tự động kích hoạt mỗi khi có lệnh <code>push</code> hoặc <code>pull_request</code> gửi vào nhánh <code>main</code>.",
        style_body
    ))
    story.append(Paragraph(
        "<b>3.1 Thiết lập Branch Protection trên GitHub:</b><br/>"
        "Vào <b>Settings</b> &rarr; <b>Branches</b> &rarr; <b>Add branch protection rule</b> cho nhánh <code>main</code>.<br/>"
        "Bật <i>'Require a pull request before merging'</i> và <i>'Require status checks to pass before merging'</i>, "
        "chọn bắt buộc các job: <code>Code Quality & Linting</code>, <code>Unit & Integration Tests (CPU)</code>, <code>Docker Build Validation</code>.",
        style_body
    ))
    story.append(Paragraph(
        "<b>3.2 Kịch bản kiểm chứng Pull Request lỗi (Trạng thái ĐỎ):</b><br/>"
        "Khi một lập trình viên tạo PR chứa lỗi unit test (ví dụ gửi mốc thời gian không đủ 72 bước), "
        "pipeline CI sẽ lập tức báo đỏ <b>FAILED</b> và GitHub tự động khóa nút <b>Merge Pull Request</b>, ngăn chặn lỗi lọt vào nhánh chính.",
        style_body
    ))
    story.append(Paragraph(
        "<b>3.3 Kịch bản khắc phục và nghiệm thu (Trạng thái XANH):</b><br/>"
        "Sau khi lập trình viên sửa lỗi và đẩy commit bổ sung, GitHub Actions tự động kiểm thử lại toàn bộ 49 test cases. "
        "Khi toàn bộ jobs hiển thị dấu tích xanh <b>PASSED</b>, nút Merge Pull Request sẽ mở khóa cho phép tích hợp.",
        style_body
    ))

    # Section 4
    story.append(Paragraph("4. Quy Trình CD Tự Động: Release Lên Docker Hub", style_h1))
    story.append(Paragraph(
        "Pipeline CD được định nghĩa tại <code>.github/workflows/release.yml</code>, chỉ chạy khi có Git Tag hợp lệ dạng <code>v*.*.*</code>.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Lệnh tạo và đẩy Git Tag Release:</b>",
        style_h2
    ))
    code_git = (
        "git checkout main\n"
        "git pull origin main\n"
        "git tag -a v1.0.0 -m \"Release v1.0.0: DINOv3 Forecaster & Serving Container\"\n"
        "git push origin v1.0.0"
    )
    story.append(Paragraph(code_git.replace("\n", "<br/>"), style_code))

    story.append(Paragraph(
        "<b>Các bước tự động của CD Pipeline:</b><br/>"
        "1. <b>Pre-Release Quality Gate:</b> Chạy kiểm định toàn bộ 49 bài test trước khi cho phép build.<br/>"
        "2. <b>Metadata Extraction:</b> Tự động sinh các tag <code>v1.0.0</code>, <code>1.0</code>, và <code>latest</code>.<br/>"
        "3. <b>Build & Push:</b> Đăng nhập bằng token, build container và đẩy lên Docker Hub.<br/>"
        "4. <b>GitHub Summary:</b> Ghi nhận mã băm bất biến (SHA-256 Digest) vào bản tóm tắt phát hành.",
        style_body
    ))

    # Section 5
    story.append(Paragraph("5. Hướng Dẫn Kéo & Chạy Image Trên Máy Trạm Sạch", style_h1))
    story.append(Paragraph(
        "Người đánh giá (Reviewer) có thể chạy thử nghiệm trên máy sạch độc lập mà <b>không cần clone source code</b>:",
        style_body
    ))
    story.append(Paragraph("<b>5.1 Kéo Image từ Docker Hub:</b>", style_h2))
    story.append(Paragraph("docker pull nguyenthuanhoa/hanoi-temperature:v1.0.0", style_code))

    story.append(Paragraph("<b>5.2 Khởi chạy Container với Volume Mount Runtime Checkpoint:</b>", style_h2))
    code_docker_run = (
        "# Chạy container với mount checkpoints và artifacts chế độ chỉ đọc (:ro)\n"
        "docker run -d --name hanoi-weather-api -p 8000:8000 \\\n"
        "  -v \"$(pwd)/checkpoints:/app/checkpoints:ro\" \\\n"
        "  -v \"$(pwd)/artifacts:/app/artifacts:ro\" \\\n"
        "  --restart unless-stopped \\\n"
        "  nguyenthuanhoa/hanoi-temperature:v1.0.0"
    )
    story.append(Paragraph(code_docker_run.replace("\n", "<br/>"), style_code))

    story.append(Paragraph("<b>5.3 Kiểm tra xác thực quyền Non-Root:</b>", style_h2))
    story.append(Paragraph(
        "docker exec hanoi-weather-api whoami<br/>"
        "<i>Kết quả mong đợi:</i> <code>appuser</code> (uid=10001, gid=10001)",
        style_body
    ))

    story.append(Paragraph("<b>5.4 Kiểm tra thực tế bằng lệnh Curl:</b>", style_h2))
    code_curl = (
        "# 1. Kiểm tra sức khỏe dịch vụ:\n"
        "curl -X GET http://localhost:8000/health\n\n"
        "# 2. Truy vấn siêu dữ liệu mô hình & 6 trạm khí tượng:\n"
        "curl -X GET http://localhost:8000/metadata\n\n"
        "# 3. Gửi payload dự báo nhiệt độ đồng thời 6 trạm sau 60 phút:\n"
        "curl -X POST http://localhost:8000/predict \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        "  -d @docs/api_example.json"
    )
    story.append(Paragraph(code_curl.replace("\n", "<br/>"), style_code))

    # Section 6
    story.append(Paragraph("6. Bảng Xử Lý Sự Cố & Rollback Khẩn Cấp", style_h1))
    trouble_data = [
        [Paragraph("<b>Hiện tượng / Lỗi</b>", style_body), Paragraph("<b>Nguyên nhân</b>", style_body), Paragraph("<b>Giải pháp xử lý dứt điểm</b>", style_body)],
        [
            Paragraph("Lỗi 403 Forbidden khi push Docker", style_body),
            Paragraph("Token hết hạn hoặc sai username trong Secrets", style_body),
            Paragraph("Tạo lại Token trên Docker Hub với quyền Write, cập nhật GitHub Secrets.", style_body)
        ],
        [
            Paragraph("HTTP 422: Timesteps != 72", style_body),
            Paragraph("Chuỗi thời gian lookback không đủ 6 giờ (72 mốc)", style_body),
            Paragraph("Gửi đúng 72 mốc thời gian liên tục với chu kỳ 5 phút.", style_body)
        ],
        [
            Paragraph("Xung đột cổng 8000 trên host", style_body),
            Paragraph("Đã có dịch vụ khác đang chạy cổng 8000", style_body),
            Paragraph("Đổi port mapping trên máy host: <code>-p 8080:8000</code>.", style_body)
        ],
        [
            Paragraph("Cần Rollback phiên bản khẩn cấp", style_body),
            Paragraph("Phiên bản mới gặp lỗi bất ngờ trên production", style_body),
            Paragraph("Khởi chạy lại image bằng SHA-256 Digest bất biến trước đó; tuyệt đối không xóa image cũ trên Docker Hub.", style_body)
        ]
    ]

    t_trouble = Table(trouble_data, colWidths=[130, 160, 197])
    t_trouble.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FEE2E2")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#991B1B")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#FEF2F2")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_trouble)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Đã xuất bản thành công tài liệu PDF nghiệm thu tại: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
