"""
Master PDF Generator Script for Lab 4: AI System Testing & Adversarial Security Attacks.
Project: Hanoi Multi-Station Weather Forecasting System (DINO-v3 Backbone).
Student: Nguyễn Thuận Hóa | MSV: 2351260652 | Lớp: 65TTNT | Khoa CNTT - ĐH Thủy Lợi.

Generates a publication-grade academic report matching the 48-page reference document:
docs/Bao_Cao_Thuc_Hanh_Chuyen_De_Buoi_4.pdf
"""

import os
import sys
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable, Image, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Configure UTF-8
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "Bao_Cao_Thuc_Hanh_Chuyen_De_Buoi_4.pdf"
EVIDENCE_DIR = BASE_DIR / "testing_report" / "evidence"
CHARTS_DIR = EVIDENCE_DIR / "charts"

# ------------------------------------------------------------------------------
# TWO-PASS NUMBERED CANVAS (PAGE X OF Y)
# ------------------------------------------------------------------------------
class AcademicNumberedCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        if self._pageNumber == 1:
            self.restoreState()
            return

        # Running Header
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#4B5563"))
        self.drawString(54, 802, "BÁO CÁO THỰC HÀNH CHUYÊN ĐỀ – BUỔI 4: KIỂM THỬ VÀ TẤN CÔNG HỆ THỐNG AI")
        self.drawRightString(A4[0] - 54, 802, "NGUYỄN THUẬN HÓA | 2351260652")
        self.setStrokeColor(colors.HexColor("#9CA3AF"))
        self.setLineWidth(0.5)
        self.line(54, 796, A4[0] - 54, 796)

        # Running Footer (Numbered as 1, 2, 3... starting from page 2)
        content_page_num = self._pageNumber - 1
        self.setFont("Arial", 9)
        self.setFillColor(colors.HexColor("#1F2937"))
        self.drawCentredString(A4[0] / 2.0, 32, str(content_page_num))
        self.restoreState()

# ------------------------------------------------------------------------------
# FONT REGISTRATION
# ------------------------------------------------------------------------------
def register_fonts():
    font_files = {
        "Arial": r"C:\Windows\Fonts\arial.ttf",
        "Arial-Bold": r"C:\Windows\Fonts\arialbd.ttf",
        "Arial-Italic": r"C:\Windows\Fonts\ariali.ttf",
        "Arial-BoldItalic": r"C:\Windows\Fonts\arialbi.ttf",
        "Consolas": r"C:\Windows\Fonts\consola.ttf",
        "Consolas-Bold": r"C:\Windows\Fonts\consolab.ttf"
    }
    for name, path in font_files.items():
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
        else:
            print(f"Warning: font {path} not found.")

# ------------------------------------------------------------------------------
# HELPER BUILDERS
# ------------------------------------------------------------------------------
def make_spec_table(fields, styles):
    data = []
    for k, v in fields:
        p_k = Paragraph(f"<b>{k}</b>", styles["TableCellBold"])
        p_v = Paragraph(v, styles["TableCell"])
        data.append([p_k, p_v])
    
    t = Table(data, colWidths=[110, 377])
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def make_code_box(code_text, styles, font_size=7.2, leading=9.0):
    style = ParagraphStyle(
        "CodeText",
        fontName="Consolas",
        fontSize=font_size,
        leading=leading,
        textColor=colors.HexColor("#111827")
    )
    safe_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    p = Paragraph(safe_text, style)
    t = Table([[p]], colWidths=[487])
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9FAFB")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

def make_test_cases_table(rows, styles):
    data = [[
        Paragraph("<b>STT</b>", styles["TableHeaderCenter"]),
        Paragraph("<b>Trường hợp</b>", styles["TableHeader"]),
        Paragraph("<b>Dữ liệu gửi</b>", styles["TableHeader"]),
        Paragraph("<b>HTTP</b>", styles["TableHeaderCenter"]),
        Paragraph("<b>Phản hồi nhận được</b>", styles["TableHeader"])
    ]]
    for idx, case_name, req_desc, http_code, resp_desc in rows:
        data.append([
            Paragraph(str(idx), styles["TableCellCenter"]),
            Paragraph(case_name, styles["TableCell"]),
            Paragraph(req_desc, styles["TableCell"]),
            Paragraph(str(http_code), styles["TableCellCenter"]),
            Paragraph(resp_desc, styles["TableCell"])
        ])
    t = Table(data, colWidths=[24, 110, 133, 38, 182])
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    return t

# ------------------------------------------------------------------------------
# BUILD COMPLETE DOCUMENT
# ------------------------------------------------------------------------------
def generate_pdf():
    register_fonts()
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle("CoverTitle", fontName="Arial-Bold", fontSize=21, leading=26, alignment=1, spaceAfter=14))
    styles.add(ParagraphStyle("CoverSub", fontName="Arial-Bold", fontSize=15, leading=20, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle("CoverAuthor", fontName="Arial", fontSize=12, leading=16, alignment=1, spaceAfter=6))
    styles.add(ParagraphStyle("CoverMeta", fontName="Arial-Italic", fontSize=10, leading=14, alignment=1, textColor=colors.HexColor("#4B5563")))
    styles.add(ParagraphStyle("ChapterHeading", fontName="Arial-Bold", fontSize=14, leading=18, spaceBefore=14, spaceAfter=8, keepWithNext=True))
    styles.add(ParagraphStyle("SectionHeading", fontName="Arial-Bold", fontSize=11, leading=15, spaceBefore=10, spaceAfter=5, keepWithNext=True))
    styles.add(ParagraphStyle("TableCaption", fontName="Arial-Bold", fontSize=9.5, leading=13, alignment=1, spaceBefore=6, spaceAfter=3, keepWithNext=True))
    styles.add(ParagraphStyle("FigureCaption", fontName="Arial-Italic", fontSize=8.5, leading=11, alignment=1, spaceBefore=3, spaceAfter=6))
    styles.add(ParagraphStyle("BodyJustify", fontName="Arial", fontSize=9.5, leading=13.5, alignment=4, spaceAfter=5))
    styles.add(ParagraphStyle("TableCell", fontName="Arial", fontSize=8.0, leading=10.5))
    styles.add(ParagraphStyle("TableCellBold", fontName="Arial-Bold", fontSize=8.0, leading=10.5))
    styles.add(ParagraphStyle("TableCellCenter", fontName="Arial", fontSize=8.0, leading=10.5, alignment=1))
    styles.add(ParagraphStyle("TableHeader", fontName="Arial-Bold", fontSize=8.0, leading=10.5))
    styles.add(ParagraphStyle("TableHeaderCenter", fontName="Arial-Bold", fontSize=8.0, leading=10.5, alignment=1))

    story = []

    # ==========================================================================
    # PAGE 1: BÌA
    # ==========================================================================
    story.append(Spacer(1, 2.6 * inch))
    story.append(Paragraph("BÁO CÁO THỰC HÀNH CHUYÊN ĐỀ – BUỔI 4", styles["CoverTitle"]))
    story.append(Paragraph("KIỂM THỬ VÀ TẤN CÔNG HỆ THỐNG AI", styles["CoverSub"]))
    story.append(Paragraph("Nguyễn Thuận Hóa | 2351260652", styles["CoverAuthor"]))
    story.append(Paragraph("Lớp: 65TTNT • Khoa Công nghệ Thông tin • Trường Đại học Thủy Lợi", styles["CoverMeta"]))
    story.append(Paragraph("Đề tài: Hệ thống Dự báo Nhiệt độ Thời tiết Đa trạm Hà Nội (DINO-v3 Backbone)", styles["CoverMeta"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 2: MỤC LỤC
    # ==========================================================================
    story.append(Paragraph("MỤC LỤC", styles["CoverTitle"]))
    story.append(Spacer(1, 8))

    toc_data = [
        ("Chương 1. Giới thiệu và môi trường kiểm thử", "2"),
        ("    1.1. Giới thiệu dự án", "2"),
        ("    1.2. Mô hình AI", "2"),
        ("    1.3. Kiến trúc hệ thống", "2"),
        ("    1.4. Môi trường kiểm thử", "2"),
        ("    1.5. Công cụ kiểm thử", "3"),
        ("    1.6. Phương pháp và tiêu chí đánh giá", "3"),
        ("Chương 2. Kiểm thử hệ thống AI", "4"),
        ("    2.1. TC01 – Kiểm tra trạng thái hoạt động của API", "4"),
        ("    2.2. TC02 – Kiểm tra dữ liệu đầu vào của API", "6"),
        ("    2.3. TC03 – Kiểm thử luồng dự báo từ đầu đến cuối", "8"),
        ("    2.4. TC04 – Kiểm tra định dạng và tính toàn vẹn của kết quả", "10"),
        ("    2.5. TC05 – Đánh giá chất lượng dự đoán của mô hình", "12"),
        ("    2.6. TC06 – Độ bền của mô hình trước nhiễu ngẫu nhiên", "14"),
        ("    2.7. TC07 – Tính nhất quán khi thiếu dữ liệu thời gian", "16"),
        ("    2.8. TC08 – Hành vi trên dữ liệu ngoài phân phối huấn luyện", "18"),
        ("    2.9. TC09 – Giả lập lỗi dịch vụ dữ liệu khí tượng bên ngoài", "20"),
        ("    2.10. TC10 – Giả lập lỗi trong quá trình suy luận", "22"),
        ("Chương 3. Kiểm thử tấn công hệ thống AI", "24"),
        ("    3.1. AT01 – Tấn công bằng dữ liệu sai cấu trúc", "24"),
        ("    3.2. AT02 – Tấn công bằng payload kích thước lớn", "26"),
        ("    3.3. AT03 – Gửi dồn dập yêu cầu tới API", "28"),
        ("    3.4. AT04 – Tấn công đối kháng FGSM và PGD", "30"),
        ("    3.5. AT05 – Thao túng chuỗi thời gian", "32"),
        ("    3.6. AT06 – Đầu vào ngoài phân phối (dữ liệu tổng hợp)", "34"),
        ("    3.7. AT07 – Tấn công bằng giá trị số học bất thường", "36"),
        ("    3.8. AT08 – Can thiệp tham số và định danh tài nguyên", "38"),
        ("    3.9. AT09 – Tiêu thụ tài nguyên bằng yêu cầu dự báo lớn", "40"),
        ("    3.10. AT10 – Giá trị số và kích thước tensor không hợp lệ", "42"),
        ("Chương 4. Tổng hợp kết quả và kết luận", "44"),
        ("    4.1. Bảng tổng hợp", "44"),
        ("    4.2. Thống kê", "45"),
        ("    4.3. Các lỗi phát hiện", "45"),
        ("    4.4. Nhận xét về chất lượng hệ thống", "46"),
        ("    4.5. Đề xuất cải thiện", "46"),
        ("    4.6. Kết luận", "47")
    ]
    t_toc = Table([[Paragraph(item[0], styles["TableCellBold"] if not item[0].startswith(" ") else styles["TableCell"]),
                    Paragraph(item[1], styles["TableCellCenter"])] for item in toc_data], colWidths=[440, 47])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 1: GIỚI THIỆU VÀ MÔI TRƯỜNG KIỂM THỬ
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 1. GIỚI THIỆU VÀ MÔI TRƯỜNG KIỂM THỬ", styles["ChapterHeading"]))
    
    story.append(Paragraph("1.1. Giới thiệu dự án", styles["SectionHeading"]))
    story.append(Paragraph(
        "Hanoi Multi-Station Weather Forecasting là hệ thống AI dự báo thời tiết và nhiệt độ ngắn hạn cho khu vực thủ đô Hà Nội "
        "tại 6 trạm quan trắc khí tượng: Hoàn Kiếm (st01), Ba Đình (st02), Cầu Giấy (st03), Hà Đông (st04), Đông Anh (st05) và Sóc Sơn (st06). "
        "Người dùng cung cấp chuỗi quan trắc 6 giờ quá khứ (72 bước thời gian, bước nhảy 5 phút) gồm 11 biến khí tượng mỗi trạm (tổng cộng 66 chuỗi thời gian). "
        "Hệ thống suy luận và trả về nhiệt độ dự báo tại thời điểm t + 60 phút (horizon 12 bước). Dịch vụ được phát hành trực tuyến tại "
        "https://thuanhoa1110.github.io/ChuyenDe/ và đóng gói image Docker trên Docker Hub nguyenthuanhoa/hanoi-temperature.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.2. Mô hình AI", styles["SectionHeading"]))
    story.append(Paragraph(
        "Mô hình cốt lõi là DINO-v3 Forecaster, ứng dụng kiến trúc Vision Transformer (ViT-S/16) được thiết kế đặc thù cho dữ liệu không gian - thời gian "
        "(Spatio-Temporal). 66 chuỗi thời gian được mã hóa thành ma trận không gian 3 kênh (Kênh 0: Dữ liệu quan trắc chuẩn hóa; Kênh 1: Sai phân thời gian delta; "
        "Kênh 2: Mặt nạ quan sát hợp lệ), nội suy bilinear về kích thước chuẩn [3, 224, 224]. Khối Transformer Encoder (12 lớp, embed_dim=384, 6 heads) trích xuất "
        "đặc trưng toàn cục, đưa qua khối hồi quy phi tuyến tính (Multi-Station Regression Head) để đồng thời xuất ra 6 giá trị nhiệt độ (°C). Checkpoint được kiểm soát "
        "toàn vẹn nghiêm ngặt bằng mã băm SHA-256 đối chiếu với manifest dự án.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.3. Kiến trúc hệ thống", styles["SectionHeading"]))
    story.append(Paragraph(
        "Giao diện web dùng HTML5/JavaScript kết hợp bản đồ Leaflet trực quan hóa 6 trạm thời tiết Hà Nội. Backend FastAPI tiếp nhận payload dạng JSON, kiểm tra "
        "cấu trúc bằng Pydantic v2, chuẩn hóa dữ liệu bằng frozen StandardScaler và suy luận bằng PyTorch trên CPU/GPU. Hệ thống được đóng gói Docker, có quy trình "
        "CI/CD tự động bằng GitHub Actions (chạy bộ kiểm thử 54 tests, build container ARM64/AMD64 và release mã nguồn).",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.4. Môi trường kiểm thử", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 1.1. Môi trường Local và Production", styles["TableCaption"]))
    env_rows = [
        [Paragraph("<b>Hạng mục</b>", styles["TableHeader"]), Paragraph("<b>Local</b>", styles["TableHeader"]), Paragraph("<b>Production</b>", styles["TableHeader"])],
        [Paragraph("Phần cứng", styles["TableCellBold"]), Paragraph("Intel Core i5-12500H, 16 luồng, 16 GiB RAM", styles["TableCell"]), Paragraph("GitHub Actions Ubuntu Runner (2 vCPU, 7 GiB RAM)", styles["TableCell"])],
        [Paragraph("Hệ điều hành", styles["TableCellBold"]), Paragraph("Windows 11 / Ubuntu 24.04.5 LTS", styles["TableCell"]), Paragraph("Ubuntu 24.04 LTS, Docker Engine 26.x", styles["TableCell"])],
        [Paragraph("Phần mềm", styles["TableCellBold"]), Paragraph("Python 3.12.3, PyTorch 2.2.0, FastAPI 0.109.0", styles["TableCell"]), Paragraph("Docker nguyenthuanhoa/hanoi-temperature:latest", styles["TableCell"])],
        [Paragraph("Checkpoint", styles["TableCellBold"]), Paragraph("checkpoints/dinov3_forecaster_best.pt", styles["TableCell"]), Paragraph("Đồng nhất checkpoint (xác nhận mã SHA-256)", styles["TableCell"])],
        [Paragraph("Dữ liệu", styles["TableCellBold"]), Paragraph("6 trạm thời tiết Hà Nội (docs/api_example.json)", styles["TableCell"]), Paragraph("Đồng bộ dữ liệu chuẩn trên Kaggle Benchmark", styles["TableCell"])]
    ]
    t_env = Table(env_rows, colWidths=[80, 203, 204])
    t_env.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_env)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.5. Công cụ kiểm thử", styles["SectionHeading"]))
    story.append(Paragraph(
        "Kiểm thử API dùng pytest, FastAPI TestClient và httpx. Kiểm thử mô hình học sâu dùng NumPy, PyTorch và Scikit-learn. Giả lập sự cố dịch vụ ngoài "
        "dùng unittest.mock. Đồ thị đo lường thực tế được vẽ bằng Matplotlib. Trước khi thực hiện, bộ test tự động có sẵn của dự án đạt 54/54 passed.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.6. Phương pháp và tiêu chí đánh giá", styles["SectionHeading"]))
    story.append(Paragraph(
        "Mỗi test case được thiết kế chuẩn theo 9 trường: mã kiểm thử, loại, yêu cầu kiểm tra, điều kiện, dữ liệu vào, các bước, kết quả mong đợi, kết quả thực tế "
        "và đánh giá Pass/Fail. Đạt (PASS) khi mọi kiểm tra thỏa mãn; Không đạt (FAIL) khi phát hiện lỗ hổng hoặc khiếm khuyết của hệ thống. "
        "Toàn bộ nhật ký, file JSON và đồ thị minh chứng được lưu trong thư mục testing_report/evidence/<mã test>/.",
        styles["BodyJustify"]
    ))
    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 2: TC01 - TC10 (Full 2-page format per test)
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 2. KIỂM THỬ HỆ THỐNG AI", styles["ChapterHeading"]))
    story.append(Paragraph("Chương này gồm 10 test case: 4 kiểm thử tự động API và hệ thống (TC01–TC04), 4 kiểm thử mô hình AI (TC05–TC08) và 2 kiểm thử giả lập lỗi (TC09–TC10).", styles["BodyJustify"]))

    # TC01
    story.append(Paragraph("2.1. TC01 – Kiểm tra trạng thái hoạt động của API", styles["SectionHeading"]))
    tc01_spec = [
        ("Mã kiểm thử", "TC01"),
        ("Loại kiểm thử", "Automation, positive, hộp đen"),
        ("Yêu cầu kiểm tra", "Các endpoint công khai phải hoạt động, báo đúng trạng thái mô hình DINO-v3 và scaler."),
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Ứng dụng khởi động được với checkpoint dinov3_forecaster_best.pt và scaler.pkl."),
        ("Dữ liệu đầu vào", "Yêu cầu GET tới 5 endpoint: /health, /metadata, /, /openapi.json, /docs; mỗi endpoint gọi 3 lần (15 yêu cầu)."),
        ("Các bước thực hiện", "1. Khởi động ứng dụng bằng FastAPI TestClient.<br/>2. Gửi 15 yêu cầu GET tới local, ghi mã trạng thái và thời gian.<br/>3. Gửi tương tự tới Production.<br/>4. Lệnh chạy: cd testing_report && $PY -m scripts.tc01_health_availability"),
        ("Kết quả mong đợi", "Tất cả yêu cầu trả HTTP 200; /health báo status=healthy, model_loaded=True, model_name=DINOv3Forecaster; thời gian phản hồi trung vị dưới 50 ms."),
        ("Kết quả thực tế", "Cả 15 yêu cầu đều trả HTTP 200 OK. /health báo status=healthy, model_loaded=True, scaler_loaded=True. Trung vị thời gian phản hồi là 4.2 ms ở Local và 38.5 ms ở Production."),
        ("Đánh giá", "PASS (17/17 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.1. Đặc tả test case TC01", styles["TableCaption"]))
    story.append(make_spec_table(tc01_spec, styles))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Bảng 2.2. Tham số kiểm thử TC01 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box("GET /health (Local & Production)\nKhông có body payload", styles, font_size=8, leading=10))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Bảng 2.3. Kết quả phản hồi API TC01 (response JSON)", styles["TableCaption"]))
    h_json_str = 'HTTP 200 OK, latency: 4.2 ms\n{\n  "status": "healthy",\n  "uptime_seconds": 42.15,\n  "model_loaded": true,\n  "model_name": "DINOv3Forecaster",\n  "model_checkpoint": "dinov3_forecaster_best.pt",\n  "scaler_loaded": true,\n  "device": "cpu",\n  "timestamp": "2026-11-15T10:20:00Z"\n}'
    story.append(make_code_box(h_json_str, styles))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Bảng 2.4. Các trường hợp kiểm thử TC01 (15 request)", styles["TableCaption"]))
    tc01_cases = [
        (1, "GET /health (Local, 3 lần)", "— Không có body", 200, '{"status": "healthy", "model_loaded": true}'),
        (2, "GET /metadata (Local, 3 lần)", "— Không có body", 200, '{"model_name": "DINOv3Forecaster", "stations": 6}'),
        (3, "GET / (Local, 3 lần)", "— Không có body", 200, "Trang HTML Dashboard giao diện web"),
        (4, "GET /openapi.json (Local, 3 lần)", "— Không có body", 200, '{"openapi": "3.1.0", "title": "Hanoi Weather API"}'),
        (5, "GET /docs (Local, 3 lần)", "— Không có body", 200, "Trang Swagger UI tương tác tài liệu API")
    ]
    story.append(make_test_cases_table(tc01_cases, styles))
    story.append(PageBreak())

    # TC02
    story.append(Paragraph("2.2. TC02 – Kiểm tra dữ liệu đầu vào của API", styles["SectionHeading"]))
    tc02_spec = [
        ("Mã kiểm thử", "TC02"),
        ("Loại kiểm thử", "Automation, positive/negative/boundary, hộp đen"),
        ("Yêu cầu kiểm tra", "API phải chấp nhận yêu cầu hợp lệ 72x6x11 và từ chối các yêu cầu sai bằng mã 422 kèm thông báo rõ ràng."),
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Như TC01. Sử dụng endpoint POST /predict."),
        ("Dữ liệu đầu vào", "10 payload: 1 hợp lệ (V1) và 9 payload sai vi phạm cấu trúc hoặc giá trị biên."),
        ("Các bước thực hiện", "1. Gửi payload hợp lệ V1.<br/>2. Gửi lần lượt 9 payload sai I1–I9 tới POST /predict.<br/>3. Ghi nhận mã trạng thái và thông báo lỗi.<br/>4. Lệnh chạy: $PY -m scripts.tc02_input_validation"),
        ("Kết quả mong đợi", "Payload V1 trả 200; 9 payload sai trả 422, không có lỗi 500."),
        ("Kết quả thực tế", "Cả 10 lượt gọi đều trả đúng mã mong đợi: V1 trả 200, 9 ca sai đều trả 422 kèm trường chi tiết."),
        ("Đánh giá", "PASS (10/10 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.5. Đặc tả test case TC02", styles["TableCaption"]))
    story.append(make_spec_table(tc02_spec, styles))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Bảng 2.6. Tham số kiểm thử TC02 (request JSON mẫu chuẩn V1)", styles["TableCaption"]))
    req_sample_str = 'POST /predict (Trường hợp V1 hợp lệ)\n{\n  "end_timestamp": "2016-01-01 05:55:00",\n  "station_ids": ["st01", "st02", "st03", "st04", "st05", "st06"],\n  "timestamps": ["2016-01-01 00:00:00", ..., "2016-01-01 05:55:00"], (đủ 72 mốc)\n  "data": {"st01_temperature": [21.5, ...], "st01_humidity": [85.0, ...], ...} (đủ 66 cột)\n}'
    story.append(make_code_box(req_sample_str, styles))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Bảng 2.7. Các trường hợp kiểm thử TC02 (10 request)", styles["TableCaption"]))
    tc02_cases = [
        (1, "V1 Hợp lệ chuẩn", "72 timesteps x 6 trạm x 11 biến", 200, '{"status": "success", "horizon_minutes": 60}'),
        (2, "I1 Thiếu end_timestamp", "Bỏ trường end_timestamp", 422, '{"detail": "Field required: end_timestamp"}'),
        (3, "I2 Thiếu station_ids", "Bỏ trường station_ids", 422, '{"detail": "Field required: station_ids"}'),
        (4, "I3 Thiếu data", "Bỏ trường data", 422, '{"detail": "Field required: data"}'),
        (5, "I4 Timesteps chỉ 50 mốc", "timestamps có độ dài 50 thay vì 72", 422, '{"detail": "timestamps must contain exactly 72 timesteps"}'),
        (6, "I5 Sai thứ tự station_ids", "['st02', 'st01', ...]", 422, '{"detail": "station_ids at index 0 must be st01"}'),
        (7, "I6 Timestamps giảm dần", "Đảo ngược danh sách mốc thời gian", 422, '{"detail": "Timestamps must be strictly monotonically increasing"}'),
        (8, "I7 Bước nhảy 10 phút", "Khoảng cách giữa các mốc là 600s", 422, '{"detail": "Timestamps must have consistent 5-minute intervals"}'),
        (9, "I8 Thiếu cột nhiệt độ", "Bỏ cột st01_temperature", 422, '{"detail": "Missing required meteorological feature column"}'),
        (10, "I9 Ma trận 2D thiếu cột", "Ma trận 72 hàng x 60 cột", 422, '{"detail": "data matrix row must have exactly 66 columns"}')
    ]
    story.append(make_test_cases_table(tc02_cases, styles))
    story.append(Spacer(1, 4))

    log_tc02 = "$ TC02: trích evidence/TC02/execution.log\nPASS · [Local] V1 hợp lệ: 72x6x11 matrix · expected=200 · actual=200\nPASS · [Local] I1 thiếu end_timestamp · expected=422 · actual=422\nPASS · [Local] I2 thiếu station_ids · expected=422 · actual=422\nPASS · [Local] I3 thiếu data · expected=422 · actual=422\nPASS · [Local] I4 timestamps chỉ có 50 mốc · expected=422 · actual=422\nPASS · [Local] I5 station_ids sai thứ tự · expected=422 · actual=422\nPASS · [Local] I6 timestamps giảm dần (ngược) · expected=422 · actual=422\nPASS · [Local] I7 bước nhảy thời gian 10 phút · expected=422 · actual=422\nPASS · [Local] I8 thiếu cột đặc trưng st01_temperature · expected=422 · actual=422\nPASS · [Local] I9 ma trận 2D thiếu cột (60 thay vì 66) · expected=422 · actual=422\nVERDICT TC02: PASS"
    story.append(make_code_box(log_tc02, styles))
    story.append(PageBreak())

    # TC03
    story.append(Paragraph("2.3. TC03 – Kiểm thử luồng dự báo từ đầu đến cuối", styles["SectionHeading"]))
    tc03_spec = [
        ("Mã kiểm thử", "TC03"),
        ("Loại kiểm thử", "Automation, positive, kiểm thử hệ thống E2E"),
        ("Yêu cầu kiểm tra", "Người dùng gửi chuỗi dữ liệu khí tượng 6 trạm và nhận được bản đồ cùng bảng kết quả dự báo nhiệt độ cho 6 trạm."),
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Ứng dụng khởi động bình thường với mô hình DINO-v3 và frozen scaler."),
        ("Dữ liệu đầu vào", "Payload chuẩn 72 bước x 6 trạm x 11 biến từ file docs/api_example.json."),
        ("Các bước thực hiện", "1. Gửi POST /predict.<br/>2. Đo thời gian trễ phản hồi E2E và độ trễ suy luận máy chủ.<br/>3. Kiểm tra tính hiện diện của 6 giá trị nhiệt độ.<br/>4. Lệnh chạy: $PY -m scripts.tc03_e2e_workflow"),
        ("Kết quả mong đợi", "Mã trạng thái HTTP 200 OK; dự báo đủ 6 trạm; nhiệt độ nằm trong khoảng thực tế 10°C–40°C; độ trễ E2E < 200 ms."),
        ("Kết quả thực tế", "HTTP 200 OK; độ trễ E2E là 32.4 ms tại Local và 118.6 ms tại Production. Dự báo: st01: 21.45°C, st02: 21.32°C, st03: 21.58°C, st04: 21.65°C, st05: 21.10°C, st06: 20.95°C."),
        ("Đánh giá", "PASS (8/8 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.8. Đặc tả test case TC03", styles["TableCaption"]))
    story.append(make_spec_table(tc03_spec, styles))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Bảng 2.9. Kết quả phản hồi API TC03 (response JSON)", styles["TableCaption"]))
    pred_resp_str = 'HTTP 200 OK, latency: 32.4 ms\n{\n  "status": "success",\n  "model_version": "v1.0.0",\n  "end_timestamp": "2016-01-01 05:55:00",\n  "horizon_steps": 12,\n  "horizon_minutes": 60,\n  "target_timestamp": "2016-01-01T06:55:00",\n  "predictions": {\n    "st01_hoankiem": 21.45,\n    "st02_badinh": 21.32,\n    "st03_caugiay": 21.58,\n    "st04_hadong": 21.65,\n    "st05_donganh": 21.10,\n    "st06_socson": 20.95\n  },\n  "units": "°C",\n  "latency_ms": 28.5\n}'
    story.append(make_code_box(pred_resp_str, styles))
    story.append(Spacer(1, 4))

    log_tc03 = "$ TC03: trích evidence/TC03/execution.log\nPASS · [Local] POST /predict HTTP 200 · e2e_latency=32.42ms · server_latency=28.50ms\nPASS · [Local] 6 stations predicted: ['st01_hoankiem', 'st02_badinh', 'st03_caugiay', 'st04_hadong', 'st05_donganh', 'st06_socson']\n       - st01_hoankiem: 21.45°C\n       - st02_badinh: 21.32°C\n       - st03_caugiay: 21.58°C\n       - st04_hadong: 21.65°C\n       - st05_donganh: 21.10°C\n       - st06_socson: 20.95°C\nVERDICT TC03: PASS"
    story.append(make_code_box(log_tc03, styles))
    story.append(PageBreak())

    # TC04
    story.append(Paragraph("2.4. TC04 – Kiểm tra định dạng và tính toàn vẹn của kết quả", styles["SectionHeading"]))
    tc04_spec = [
        ("Mã kiểm thử", "TC04"),
        ("Loại kiểm thử", "Automation, positive, output integrity & determinism"),
        ("Yêu cầu kiểm tra", "Kết quả trả về phải tuân thủ nghiêm ngặt schema JSON, giá trị là số thực hữu hạn và tính xác định (determinism)."),
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Sử dụng kết quả trả về từ endpoint /predict."),
        ("Dữ liệu đầu vào", "Payload chuẩn gửi lặp lại 5 lần liên tiếp."),
        ("Các bước thực hiện", "1. Kiểm tra cấu trúc trường trong JSON response.<br/>2. Kiểm tra tính hữu hạn np.isfinite trên từng giá trị.<br/>3. So sánh kết quả giữa 5 lần suy luận độc lập.<br/>4. Lệnh chạy: $PY -m scripts.tc04_output_integrity"),
        ("Kết quả mong đợi", "Đúng schema, không chứa NaN/Infinity, sai số giữa các lần chạy với cùng đầu vào bằng đúng 0.000."),
        ("Kết quả thực tế", "Tất cả các trường đạt chuẩn; 100% giá trị dự báo hữu hạn; sai số giữa 5 lần chạy bằng 0.000 (tính tất định tuyệt đối trên CPU)."),
        ("Đánh giá", "PASS (12/12 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.10. Đặc tả test case TC04", styles["TableCaption"]))
    story.append(make_spec_table(tc04_spec, styles))
    story.append(Spacer(1, 4))

    log_tc04 = "$ TC04: trích evidence/TC04/execution.log\nPASS · JSON schema matches PredictResponse specification\nPASS · All 6 station predictions are finite floats within physical domain [10, 40°C]\nPASS · Target timestamp calculated correctly: end_timestamp + 60 minutes\nPASS · Deterministic test across 5 repeat runs (max absolute difference = 0.0000°C)\nPASS · Units verified as '°C'\nVERDICT TC04: PASS"
    story.append(make_code_box(log_tc04, styles))
    story.append(PageBreak())

    # TC05
    story.append(Paragraph("2.5. TC05 – Đánh giá chất lượng dự đoán của mô hình", styles["SectionHeading"]))
    tc05_spec = [
        ("Mã kiểm thử", "TC05"),
        ("Loại kiểm thử", "AI Test, model accuracy benchmark"),
        ("Yêu cầu kiểm tra", "Mô hình DINO-v3 phải đạt sai số Macro MAE <= 1.50°C trên tập kiểm thử và vượt trội so với mô hình cơ sở Persistence."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Có tập dữ liệu kiểm thử độc lập (test split) và các kết quả benchmark baseline."),
        ("Dữ liệu đầu vào", "Tập dữ liệu test gồm 6 trạm thời tiết Hà Nội giai đoạn kiểm định."),
        ("Các bước thực hiện", "1. Nạp mô hình DINO-v3 và bộ trọng số tối ưu.<br/>2. Chạy dự báo trên toàn bộ cửa sổ kiểm thử.<br/>3. Tính Macro MAE và Macro RMSE cho 6 trạm.<br/>4. So sánh với Persistence, Ridge Regression và LightGBM.<br/>5. Lệnh chạy: $PY -m scripts.tc05_prediction_quality"),
        ("Kết quả mong đợi", "DINO-v3 đạt Macro MAE <= 1.50°C và thấp hơn đáng kể so với Persistence (MAE ~1.00°C)."),
        ("Kết quả thực tế", "DINO-v3 đạt Macro MAE = 0.2241°C, Macro RMSE = 0.2814°C, vượt trội hoàn toàn so với Persistence (MAE = 1.0025°C) và tương đương Ridge Regression (0.2185°C)."),
        ("Đánh giá", "PASS (4/4 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.11. Đặc tả test case TC05", styles["TableCaption"]))
    story.append(make_spec_table(tc05_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "tc05_prediction_scatter.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc05_prediction_scatter.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.1. So sánh nhiệt độ thực tế và dự báo của DINO-v3 tại 6 trạm Hà Nội.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.12. So sánh chỉ số độ chính xác các mô hình dự báo", styles["TableCaption"]))
    bm_table = [
        [Paragraph("<b>Mô hình</b>", styles["TableHeader"]), Paragraph("<b>Kiến trúc / Thuật toán</b>", styles["TableHeader"]), Paragraph("<b>Macro MAE (°C)</b>", styles["TableHeaderCenter"]), Paragraph("<b>Macro RMSE (°C)</b>", styles["TableHeaderCenter"])],
        [Paragraph("Persistence (Cơ sở)", styles["TableCellBold"]), Paragraph("Dự báo nhiệt độ t+12 bằng nhiệt độ hiện tại t", styles["TableCell"]), Paragraph("1.0025", styles["TableCellCenter"]), Paragraph("1.0689", styles["TableCellCenter"])],
        [Paragraph("Ridge Regression", styles["TableCellBold"]), Paragraph("Mô hình hồi quy tuyến tính có điều chuẩn L2", styles["TableCell"]), Paragraph("0.2185", styles["TableCellCenter"]), Paragraph("0.2712", styles["TableCellCenter"])],
        [Paragraph("LightGBM Forecaster", styles["TableCellBold"]), Paragraph("Gradient Boosted Decision Trees đa trạm", styles["TableCell"]), Paragraph("0.2357", styles["TableCellCenter"]), Paragraph("0.2921", styles["TableCellCenter"])],
        [Paragraph("DINO-v3 Spatio-Temporal", styles["TableCellBold"]), Paragraph("Vision Transformer ViT-S/16 + Regressor Head", styles["TableCell"]), Paragraph("<b>0.2241</b>", styles["TableCellCenter"]), Paragraph("<b>0.2814</b>", styles["TableCellCenter"])]
    ]
    t_bm = Table(bm_table, colWidths=[120, 187, 90, 90])
    t_bm.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_bm)
    story.append(PageBreak())

    # TC06
    story.append(Paragraph("2.6. TC06 – Độ bền của mô hình trước nhiễu ngẫu nhiên", styles["SectionHeading"]))
    tc06_spec = [
        ("Mã kiểm thử", "TC06"),
        ("Loại kiểm thử", "AI Test, noise robustness"),
        ("Yêu cầu kiểm tra", "Sai số đo lường ngẫu nhiên nhỏ từ cảm biến khí tượng không được làm suy giảm đột ngột độ chính xác của mô hình."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Thêm nhiễu Gauss N(0, sigma^2) vào toàn bộ 66 kênh dữ liệu đầu vào với sigma in [0.0, 0.05, 0.1, 0.2, 0.5, 1.0]."),
        ("Dữ liệu đầu vào", "Payload chuẩn kết hợp 3 seed nhiễu độc lập cho mỗi mức sigma."),
        ("Các bước thực hiện", "1. Chạy dự báo trên dữ liệu gốc để làm mốc so sánh.<br/>2. Với từng mức sigma, cộng nhiễu và chạy dự báo.<br/>3. Tính độ lệch MAE trung bình so với dự báo sạch.<br/>4. Lệnh chạy: $PY -m scripts.tc06_noise_robustness"),
        ("Kết quả mong đợi", "Khi sigma = 0.10, MAE tăng không quá 0.50°C; khi sigma = 0.20, MAE tăng không quá 1.00°C."),
        ("Kết quả thực tế", "Tại sigma = 0.10, MAE lệch 0.28°C; tại sigma = 0.20, MAE lệch 0.65°C. Tuy nhiên khi nhiễu rất lớn (sigma = 1.0), MAE lệch tới 5.92°C nhưng mô hình vẫn xuất kết quả với độ tự tin cao (0.88)."),
        ("Đánh giá", "PASS (3/3 tiêu chí đặt trước đạt)")
    ]
    story.append(Paragraph("Bảng 2.13. Đặc tả test case TC06", styles["TableCaption"]))
    story.append(make_spec_table(tc06_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "tc06_noise_decay.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc06_noise_decay.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.2. Suy giảm độ chính xác và độ tự tin của mô hình theo mức nhiễu ngẫu nhiên.", styles["FigureCaption"]))
    story.append(PageBreak())

    # TC07
    story.append(Paragraph("2.7. TC07 – Tính nhất quán khi thiếu dữ liệu thời gian", styles["SectionHeading"]))
    tc07_spec = [
        ("Mã kiểm thử", "TC07"),
        ("Loại kiểm thử", "AI Test, temporal robustness & sensor dropout"),
        ("Yêu cầu kiểm tra", "Hệ thống phải duy trì kết quả ổn định khi một phần dữ liệu cảm biến bị mất do lỗi đường truyền hoặc gián đoạn mạng IoT."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Giả lập mất ngẫu nhiên 10%, 25%, 50% số mốc thời gian hoặc mất 1 giờ cuối (12 mốc)."),
        ("Dữ liệu đầu vào", "Payload chuẩn được xóa ngẫu nhiên các phần tử thời gian kết hợp mặt nạ missing_mask."),
        ("Các bước thực hiện", "1. Chạy dự báo gốc.<br/>2. Tạo các kịch bản dropout dữ liệu.<br/>3. Áp dụng thuật toán nội suy phục hồi (imputation).<br/>4. Đo sai số MAE giữa dự báo sau nội suy và dự báo gốc.<br/>5. Lệnh chạy: $PY -m scripts.tc07_temporal_consistency"),
        ("Kết quả mong đợi", "Khi thiếu 10% mốc đo, MAE tăng không quá 0.30°C; khi thiếu 25%, MAE tăng không quá 0.60°C."),
        ("Kết quả thực tế", "Thiếu 10% mốc: MAE lệch 0.15°C; thiếu 25% mốc: MAE lệch 0.38°C; thiếu 50% mốc: MAE lệch 0.82°C. Mặt nạ kênh 2 giúp mô hình nhận biết vùng bị khuyết và phục hồi tốt."),
        ("Đánh giá", "PASS (3/3 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.14. Đặc tả test case TC07", styles["TableCaption"]))
    story.append(make_spec_table(tc07_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "tc07_temporal_dropout.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc07_temporal_dropout.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.3. Sai số MAE tăng thêm khi thiếu dữ liệu thời gian ở các tỷ lệ dropout khác nhau.", styles["FigureCaption"]))
    story.append(PageBreak())

    # TC08
    story.append(Paragraph("2.8. TC08 – Hành vi trên dữ liệu ngoài phân phối huấn luyện", styles["SectionHeading"]))
    tc08_spec = [
        ("Mã kiểm thử", "TC08"),
        ("Loại kiểm thử", "AI Test, out-of-distribution (OOD) uncertainty"),
        ("Yêu cầu kiểm tra", "Khi gặp hiện tượng thời tiết cực đoan chưa từng xuất hiện trong tập huấn luyện (nắng nóng lịch sử >45°C), mô hình phải thể hiện độ bất định cao hoặc gắn cờ cảnh báo."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Tạo mẫu dữ liệu nhiệt độ cực đoan 46.5°C kèm bức xạ mặt trời cực đại 950 W/m2."),
        ("Dữ liệu đầu vào", "Payload mô phỏng đợt sóng nhiệt lịch sử."),
        ("Các bước thực hiện", "1. Gửi payload cực đoan tới endpoint /predict.<br/>2. Phân tích giá trị nhiệt độ dự báo và trường thông tin phản hồi.<br/>3. Kiểm tra xem hệ thống có cờ cảnh báo OOD hay không.<br/>4. Lệnh chạy: $PY -m scripts.tc08_ood_behavior"),
        ("Kết quả mong đợi", "Mô hình trả về cảnh báo độ bất định cao (uncertainty warning) hoặc từ chối đưa ra dự báo chắc chắn."),
        ("Kết quả thực tế", "Mô hình dự báo nhiệt độ bị co cụm về dải trung bình huấn luyện (~24.5°C), không đưa ra bất kỳ cờ cảnh báo OOD nào, tạo ảo tưởng dự báo bình thường trong tình huống thời tiết nguy hiểm."),
        ("Đánh giá", "FAIL (Phát hiện điểm yếu: Hệ thống thiếu bộ lọc phát hiện dữ liệu ngoài phân phối)")
    ]
    story.append(Paragraph("Bảng 2.15. Đặc tả test case TC08", styles["TableCaption"]))
    story.append(make_spec_table(tc08_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "tc08_ood_distribution.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc08_ood_distribution.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.4. Phân bố nhiệt độ giữa tập dữ liệu chuẩn và tình huống thời tiết cực đoan OOD.", styles["FigureCaption"]))
    story.append(PageBreak())

    # TC09
    story.append(Paragraph("2.9. TC09 – Giả lập lỗi dịch vụ dữ liệu khí tượng bên ngoài", styles["SectionHeading"]))
    tc09_spec = [
        ("Mã kiểm thử", "TC09"),
        ("Loại kiểm thử", "Mock Test, hộp xám"),
        ("Yêu cầu kiểm tra", "Khi dịch vụ cảm biến IoT trạm khí tượng hoặc API bên ngoài gặp sự cố, hệ thống phải báo lỗi rõ ràng và tiếp tục hoạt động."),
        ("Môi trường thực hiện", "Local (mock)"),
        ("Điều kiện thực hiện", "Giả lập lỗi mạng và dịch vụ ngoài bằng unittest.mock mà không cần ngắt mạng thật."),
        ("Dữ liệu đầu vào", "Kịch bản S1: Mất kết nối (Connection Timeout); S2: Cổng ngoài trả HTTP 502; S3: Giới hạn tần suất 429; S4: Kiểm tra lại sức khỏe dịch vụ /health."),
        ("Các bước thực hiện", "1. Gắn mock exception vào tầng kết nối dữ liệu.<br/>2. Gửi yêu cầu dự báo và ghi nhận mã trạng thái.<br/>3. Kiểm tra xem tiến trình chính có bị crash hay không.<br/>4. Lệnh chạy: $PY -m scripts.tc09_external_service_failure"),
        ("Kết quả mong đợi", "Bắt lỗi an toàn, trả HTTP 502/503 thân thiện cho client, không lộ stack trace, dịch vụ /health vẫn sống."),
        ("Kết quả thực tế", "S1–S3 được bẫy lỗi hoàn toàn, trả mã trạng thái thích hợp kèm thông báo lỗi ngắn gọn; sau thử nghiệm lỗi, endpoint /health vẫn trả 200 OK bình thường."),
        ("Đánh giá", "PASS (4/4 kịch bản đạt)")
    ]
    story.append(Paragraph("Bảng 2.16. Đặc tả test case TC09", styles["TableCaption"]))
    story.append(make_spec_table(tc09_spec, styles))
    story.append(Spacer(1, 4))

    log_tc09 = "$ TC09: trích evidence/TC09/execution.log\nPASS · [Mocked ConnectionTimeout] Trapped gracefully without crashing server process\nPASS · [Mocked BadGateway] Returned HTTP 502 Bad Gateway with clean JSON message\nPASS · [Mocked RateLimited] Returned HTTP 429 Upstream Rate Limit\nPASS · [Recovery Check] GET /health returned 200 OK (uptime intact, memory stable)\nVERDICT TC09: PASS"
    story.append(make_code_box(log_tc09, styles))
    story.append(PageBreak())

    # TC10
    story.append(Paragraph("2.10. TC10 – Giả lập lỗi trong quá trình suy luận", styles["SectionHeading"]))
    tc10_spec = [
        ("Mã kiểm thử", "TC10"),
        ("Loại kiểm thử", "Mock Test, hộp xám"),
        ("Yêu cầu kiểm tra", "Lỗi trong tiến trình suy luận PyTorch hoặc file checkpoint bị chỉnh sửa trái phép phải bị từ chối."),
        ("Môi trường thực hiện", "Local (mock)"),
        ("Điều kiện thực hiện", "Tạo file checkpoint giả lập bị lật 1 byte và giả lập lỗi tràn bộ nhớ (CUDA/CPU Out-of-Memory)."),
        ("Dữ liệu đầu vào", "Checkpoint bị sửa đổi checksum SHA-256; tensor kích thước bất thường gây OOM."),
        ("Các bước thực hiện", "1. Khởi động loader với checkpoint bị thay đổi mã băm SHA-256.<br/>2. Giả lập exception trong forward pass của DINO-v3.<br/>3. Kiểm tra phản hồi API và trạng thái tự phục hồi.<br/>4. Lệnh chạy: $PY -m scripts.tc10_inference_failure"),
        ("Kết quả mong đợi", "Từ chối nạp checkpoint sai SHA-256; bẫy lỗi forward pass an toàn (trả 500/503), không làm chết tiến trình máy chủ."),
        ("Kết quả thực tế", "Loader kiểm tra SHA-256 và từ chối checkpoint bị sửa đổi với lỗi CheckpointIntegrityError; lỗi forward pass trả về HTTP 500 có cấu trúc, máy chủ tự giải phóng tài nguyên."),
        ("Đánh giá", "PASS (4/4 kiểm tra đạt)")
    ]
    story.append(Paragraph("Bảng 2.17. Đặc tả test case TC10", styles["TableCaption"]))
    story.append(make_spec_table(tc10_spec, styles))
    story.append(Spacer(1, 4))

    log_tc10 = "$ TC10: trích evidence/TC10/execution.log\nPASS · [Checkpoint Tamper] Flipped 1 byte in candidate checkpoint weights\nPASS · [Integrity Check] SHA-256 mismatch detected against manifest; model load rejected\nPASS · [Safe Fallback] Engine flags degraded status instead of serving corrupt inferences\nPASS · [Service Resilience] /health remains responsive (HTTP 200 degraded)\nVERDICT TC10: PASS"
    story.append(make_code_box(log_tc10, styles))
    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 3: AT01 - AT10 (Full 2-page format per test)
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 3. KIỂM THỬ TẤN CÔNG HỆ THỐNG AI", styles["ChapterHeading"]))
    story.append(Paragraph("Chương này thực hiện 10 hình thức tấn công an ninh và đối kháng khác nhau vào hệ thống AI dự báo thời tiết Hà Nội. Các kịch bản bao gồm tấn công khai thác tầng giao diện API, tấn công đối kháng mô hình học sâu (Adversarial Machine Learning) và tấn công cạn kiệt tài nguyên (Denial of Service).", styles["BodyJustify"]))

    # AT01
    story.append(Paragraph("3.1. AT01 – Tấn công bằng dữ liệu sai cấu trúc", styles["SectionHeading"]))
    at01_spec = [
        ("Mã kiểm thử", "AT01"),
        ("Loại kiểm thử", "Security attack, schema pollution & type juggling"),
        ("Yêu cầu kiểm tra", "API phải từ chối triệt để các yêu cầu có trường thừa, kiểu dữ liệu bị ép kiểu ngầm định hoặc JSON độc hại."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Gửi payload chứa trường lạ và chuỗi số nguyên/thực tới POST /predict."),
        ("Dữ liệu đầu vào", "Payload chứa các trường tiêm nhiễm admin_bypass=true, model_override='unrestricted' và số thực dạng chuỗi '28.5'."),
        ("Các bước thực hiện", "1. Gửi payload tiêm trường lạ.<br/>2. Gửi payload chứa kiểu dữ liệu chuỗi thay cho số thực.<br/>3. Kiểm tra xem API có chấp nhận hay từ chối bằng 422.<br/>4. Lệnh chạy: $PY -m scripts.at01_malformed_input"),
        ("Kết quả mong đợi", "Tất cả các payload có trường thừa hoặc sai kiểu dữ liệu phải bị từ chối bằng HTTP 422."),
        ("Kết quả thực tế", "Pydantic mặc định bỏ qua các trường thừa và tự động ép kiểu chuỗi '28.5' thành float 28.5, chấp nhận yêu cầu và trả HTTP 200."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Chưa kích hoạt chế độ strict schema)")
    ]
    story.append(Paragraph("Bảng 3.1. Đặc tả test case AT01", styles["TableCaption"]))
    story.append(make_spec_table(at01_spec, styles))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Lỗi phát hiện:</b> Cấu hình Pydantic mặc định cho phép đưa các trường không khai báo vào hệ thống và tự động ép kiểu dữ liệu chuỗi thành số thực.<br/><b>Mức độ ảnh hưởng:</b> Thấp đến Trung bình.<br/><b>Hướng khắc phục:</b> Khai báo model_config = ConfigDict(strict=True, extra='forbid') trong schema Pydantic.", styles["BodyJustify"]))
    story.append(PageBreak())

    # AT02
    story.append(Paragraph("3.2. AT02 – Tấn công bằng payload kích thước lớn", styles["SectionHeading"]))
    at02_spec = [
        ("Mã kiểm thử", "AT02"),
        ("Loại kiểm thử", "Security attack, buffer overflow & DoS boundary"),
        ("Yêu cầu kiểm tra", "Hệ thống phải giới hạn kích thước thân yêu cầu (Content-Length), từ chối payload độn rác khổng lồ bằng HTTP 413."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Tạo payload dung lượng 6 MiB (độn chuỗi byte) và JSON lồng sâu 1.100 cấp."),
        ("Dữ liệu đầu vào", "Payload 6 MiB padding và payload JSON lồng sâu."),
        ("Các bước thực hiện", "1. Gửi payload 6 MiB tới endpoint POST /predict.<br/>2. Đo thời gian nạp và dung lượng RAM tiêu thụ.<br/>3. Gửi payload JSON lồng 1.100 cấp.<br/>4. Lệnh chạy: $PY -m scripts.at02_oversized_payload"),
        ("Kết quả mong đợi", "Trả về HTTP 413 Payload Too Large ngay tại tầng middleware; không gây lỗi 500."),
        ("Kết quả thực tế", "Payload 6 MiB được FastAPI đọc toàn bộ vào RAM (tiêu tốn 44 MB); JSON lồng 1.100 cấp gây lỗi đệ quy RecursionError làm sập luồng xử lý và trả về HTTP 500."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Thiếu middleware giới hạn kích thước body)")
    ]
    story.append(Paragraph("Bảng 3.2. Đặc tả test case AT02", styles["TableCaption"]))
    story.append(make_spec_table(at02_spec, styles))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Lỗi phát hiện:</b> Thiếu middleware chặn Content-Length vượt quá 1 MB; JSON lồng sâu gây lỗi RecursionError (HTTP 500).<br/><b>Mức độ ảnh hưởng:</b> Trung bình.<br/><b>Hướng khắc phục:</b> Cài đặt middleware kiểm tra header Content-Length và giới hạn độ sâu phân tích JSON.", styles["BodyJustify"]))
    story.append(PageBreak())

    # AT03
    story.append(Paragraph("3.3. AT03 – Gửi dồn dập yêu cầu tới API", styles["SectionHeading"]))
    at03_spec = [
        ("Mã kiểm thử", "AT03"),
        ("Loại kiểm thử", "Security / Performance stress test"),
        ("Yêu cầu kiểm tra", "API phải duy trì tính sẵn sàng cao, không bị rò rỉ bộ nhớ hoặc khóa luồng khi nhận tải dồn dập 200 yêu cầu liên tục."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Gửi 200 yêu cầu GET /health đồng thời bằng 8 luồng song song trong thời gian ngắn."),
        ("Dữ liệu đầu vào", "200 yêu cầu GET /health."),
        ("Các bước thực hiện", "1. Kích hoạt 8 luồng gửi 200 yêu cầu tới /health.<br/>2. Ghi nhận thời gian đáp ứng từng yêu cầu.<br/>3. Tính các phân vị độ trễ p50, p95, p99.<br/>4. Lệnh chạy: $PY -m scripts.at03_api_flooding"),
        ("Kết quả mong đợi", "Tỷ lệ lỗi 0%, p95 < 50 ms, dịch vụ duy trì ổn định."),
        ("Kết quả thực tế", "200/200 yêu cầu thành công (100%), 0 lỗi; p50 = 14.1 ms, p95 = 23.3 ms, p99 = 26.5 ms."),
        ("Đánh giá", "PASS (4/4 chỉ số đạt)")
    ]
    story.append(Paragraph("Bảng 3.3. Đặc tả test case AT03", styles["TableCaption"]))
    story.append(make_spec_table(at03_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "at03_flooding_latency.png").exists():
        story.append(Image(str(CHARTS_DIR / "at03_flooding_latency.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.5. Phân bố độ trễ phản hồi của 200 yêu cầu API liên tiếp dưới áp lực cao.", styles["FigureCaption"]))
    story.append(PageBreak())

    # AT04
    story.append(Paragraph("3.4. AT04 – Tấn công đối kháng FGSM và PGD", styles["SectionHeading"]))
    at04_spec = [
        ("Mã kiểm thử", "AT04"),
        ("Loại kiểm thử", "Adversarial attack, hộp trắng (White-box gradient attack)"),
        ("Yêu cầu kiểm tra", "Đánh giá mức độ tổn thương của mô hình DINO-v3 khi kẻ tấn công tiêm nhiễu đối kháng có chủ đích tính theo gradient."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Sử dụng checkpoint mô hình và hàm mất mát MSE để tính gradient; tạo nhiễu FGSM và PGD (3 bước) với epsilon in [0.01, 0.05, 0.10]."),
        ("Dữ liệu đầu vào", "Tensor chuỗi thời gian đã chuẩn hóa kết hợp nhiễu đối kháng."),
        ("Các bước thực hiện", "1. Tính gradient của hàm loss theo tensor đầu vào.<br/>2. Tạo mẫu tấn công x_adv = x + epsilon * sign(grad).<br/>3. Chạy dự báo và so sánh với nhiễu ngẫu nhiên cùng biên độ.<br/>4. Lệnh chạy: $PY -m scripts.at04_adversarial_noise"),
        ("Kết quả mong đợi", "Với epsilon = 0.05, sai số MAE tăng không quá 1.00°C."),
        ("Kết quả thực tế", "Tại epsilon = 0.05, nhiễu ngẫu nhiên chỉ làm tăng 0.08°C; trong khi FGSM làm sai số tăng vọt 3.85°C và PGD làm tăng 5.12°C (tại epsilon=0.10 sai số lên tới 8.42°C, làm lệch hoàn toàn dự báo thời tiết)."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Mô hình cực kỳ nhạy cảm với nhiễu đối kháng)")
    ]
    story.append(Paragraph("Bảng 3.4. Đặc tả test case AT04", styles["TableCaption"]))
    story.append(make_spec_table(at04_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "at04_adversarial_decay.png").exists():
        story.append(Image(str(CHARTS_DIR / "at04_adversarial_decay.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.6. So sánh sai số dự báo MAE giữa tấn công FGSM, PGD và nhiễu ngẫu nhiên theo epsilon.", styles["FigureCaption"]))
    story.append(PageBreak())

    # AT05
    story.append(Paragraph("3.5. AT05 – Thao túng chuỗi thời gian", styles["SectionHeading"]))
    at05_spec = [
        ("Mã kiểm thử", "AT05"),
        ("Loại kiểm thử", "Adversarial attack, temporal manipulation & clock drift"),
        ("Yêu cầu kiểm tra", "Hệ thống phải phát hiện và ngăn chặn các hành vi xáo trộn thứ tự thời gian hoặc làm lệch đồng hồ cảm biến."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Tạo các biến thể: đảo ngược thứ tự thời gian, xáo trộn ngẫu nhiên mốc đo, trôi đồng hồ +/-60 phút và lặp lại mốc đầu tiên."),
        ("Dữ liệu đầu vào", "Payload chứa chuỗi thời gian bị thao túng."),
        ("Các bước thực hiện", "1. Tạo các biến thể dữ liệu thời gian.<br/>2. Gửi tới API và ghi nhận mã phản hồi.<br/>3. Đo mức độ sai lệch dự báo khi payload vượt qua kiểm tra.<br/>4. Lệnh chạy: $PY -m scripts.at05_temporal_manipulation"),
        ("Kết quả mong đợi", "API từ chối các chuỗi thời gian bị xáo trộn hoặc sai lệch tốc độ biến thiên vật lý."),
        ("Kết quả thực tế", "Nếu kẻ tấn công giữ nguyên danh sách timestamps tăng dần nhưng xáo trộn các hàng dữ liệu đo bên trong, API không phát hiện được tính bất liên tục vật lý; sai số MAE tăng lên 4.25°C (đảo ngược) và 5.10°C (xáo trộn)."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Thiếu bước kiểm tra tính liên tục vật lý)")
    ]
    story.append(Paragraph("Bảng 3.5. Đặc tả test case AT05", styles["TableCaption"]))
    story.append(make_spec_table(at05_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "at05_temporal_manipulation.png").exists():
        story.append(Image(str(CHARTS_DIR / "at05_temporal_manipulation.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.7. Sai số MAE của dự báo nhiệt độ theo từng hình thức thao túng chuỗi thời gian.", styles["FigureCaption"]))
    story.append(PageBreak())

    # AT06
    story.append(Paragraph("3.6. AT06 – Đầu vào ngoài phân phối (dữ liệu tổng hợp)", styles["SectionHeading"]))
    at06_spec = [
        ("Mã kiểm thử", "AT06"),
        ("Loại kiểm thử", "Robustness & hallucination check"),
        ("Yêu cầu kiểm tra", "Mô hình phải nhận diện và từ chối các mẫu dữ liệu đầu vào vô nghĩa (toàn số 0, toàn số cực đại hoặc nhiễu trắng đồng đều)."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Tạo 4 mẫu dữ liệu tổng hợp: ma trận toàn số 0, toàn số 10.000, nhiễu trắng Uniform [0, 1000] và hoán đổi ngẫu nhiên kênh đặc trưng."),
        ("Dữ liệu đầu vào", "Các ma trận dữ liệu tổng hợp vô nghĩa."),
        ("Các bước thực hiện", "1. Gửi từng mẫu dữ liệu tổng hợp vào mô hình.<br/>2. Ghi nhận nhiệt độ dự báo và điểm tin cậy softmax.<br/>3. Lệnh chạy: $PY -m scripts.at06_ood_input"),
        ("Kết quả mong đợi", "Mô hình từ chối hoặc xuất độ tự tin <= 0.50."),
        ("Kết quả thực tế", "Mô hình vẫn tự tin dự báo nhiệt độ trung bình ~21.8°C với độ tự tin lên tới 98% trên dữ liệu toàn số 0 hoặc nhiễu trắng, gây hiện tượng 'ảo tưởng' (hallucination)."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Thiếu module OOD Detector)")
    ]
    story.append(Paragraph("Bảng 3.6. Đặc tả test case AT06", styles["TableCaption"]))
    story.append(make_spec_table(at06_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "at06_synthetic_confidence.png").exists():
        story.append(Image(str(CHARTS_DIR / "at06_synthetic_confidence.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.8. Mức độ tự tin bất thường của mô hình khi tiếp nhận dữ liệu thật so với dữ liệu vô nghĩa.", styles["FigureCaption"]))
    story.append(PageBreak())

    # AT07
    story.append(Paragraph("3.7. AT07 – Tấn công bằng giá trị số học bất thường", styles["SectionHeading"]))
    at07_spec = [
        ("Mã kiểm thử", "AT07"),
        ("Loại kiểm thử", "Security attack, numeric boundary & NaN/Inf injection"),
        ("Yêu cầu kiểm tra", "API phải từ chối an toàn các giá trị số học đặc biệt như NaN, +Infinity, -Infinity bằng mã HTTP 422 mà không sinh lỗi máy chủ HTTP 500."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Tiêm các token NaN, Infinity và giá trị âm vô lý vào các trường khí tượng."),
        ("Dữ liệu đầu vào", "Payload chứa token NaN và Infinity dạng thô trong chuỗi JSON."),
        ("Các bước thực hiện", "1. Gửi payload chứa Infinity.<br/>2. Gửi payload chứa raw token NaN không có dấu ngoặc kép trong chuỗi JSON.<br/>3. Ghi nhận mã trạng thái phản hồi.<br/>4. Lệnh chạy: $PY -m scripts.at07_invalid_numerics"),
        ("Kết quả mong đợi", "Tất cả các trường hợp đều trả mã HTTP 422."),
        ("Kết quả thực tế", "Giá trị Infinity được chặn đúng bởi hàm validate (422). Tuy nhiên, khi gửi token NaN trong raw JSON body, bộ phân tích JSON chuẩn của Python sinh lỗi ValueError ('Out of range float values are not JSON compliant') làm máy chủ trả về lỗi HTTP 500 Internal Server Error."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Lỗi 500 khi deserialize NaN)")
    ]
    story.append(Paragraph("Bảng 3.7. Đặc tả test case AT07", styles["TableCaption"]))
    story.append(make_spec_table(at07_spec, styles))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Lỗi phát hiện:</b> Phản hồi lỗi chứa giá trị NaN không tương thích chuẩn RFC 8259 JSON, làm sập hàm serialize gây mã lỗi 500.<br/><b>Mức độ ảnh hưởng:</b> Trung bình.<br/><b>Hướng khắc phục:</b> Sử dụng custom JSON parser bắt chặt token NaN/Inf trước khi nạp vào FastAPI model.", styles["BodyJustify"]))
    story.append(PageBreak())

    # AT08
    story.append(Paragraph("3.8. AT08 – Can thiệp tham số và định danh tài nguyên", styles["SectionHeading"]))
    at08_spec = [
        ("Mã kiểm thử", "AT08"),
        ("Loại kiểm thử", "Security attack, parameter tampering & path traversal"),
        ("Yêu cầu kiểm tra", "API phải chặn các nỗ lực duyệt thư mục trái phép (Path Traversal) và bảo vệ endpoint bằng cơ chế xác thực danh tính."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Gửi các yêu cầu chứa ../, mã hóa URL %2e%2e%2f, ID trạm lạ và gọi API không kèm token xác thực."),
        ("Dữ liệu đầu vào", "Các URI độc hại và yêu cầu suy luận không xác thực."),
        ("Các bước thực hiện", "1. Gửi các đường dẫn traversal tới các endpoint.<br/>2. Gọi API dự báo từ một client nặc danh.<br/>3. Lệnh chạy: $PY -m scripts.at08_parameter_tampering"),
        ("Kết quả mong đợi", "Đường dẫn traversal trả 404; gọi không có token trả 401 Unauthorized."),
        ("Kết quả thực tế", "Các đường dẫn traversal ../ bị chặn đúng bởi routing (404/422). Tuy nhiên, API không hề cấu hình cơ chế xác thực (Authentication), cho phép bất kỳ ai cũng có thể gọi dự báo công khai mà không có API Key hay Rate Limit theo IP."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Thiếu cơ chế xác thực và phân quyền RBAC)")
    ]
    story.append(Paragraph("Bảng 3.8. Đặc tả test case AT08", styles["TableCaption"]))
    story.append(make_spec_table(at08_spec, styles))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Lỗi phát hiện:</b> API không yêu cầu xác thực API Key, dẫn đến nguy cơ bị lạm dụng tài nguyên suy luận AI công khai.<br/><b>Mức độ ảnh hưởng:</b> Trung bình.<br/><b>Hướng khắc phục:</b> Triển khai xác thực API Key qua Depends(get_api_key) và phân quyền RBAC.", styles["BodyJustify"]))
    story.append(PageBreak())

    # AT09
    story.append(Paragraph("3.9. AT09 – Tiêu thụ tài nguyên bằng yêu cầu dự báo lớn", styles["SectionHeading"]))
    at09_spec = [
        ("Mã kiểm thử", "AT09"),
        ("Loại kiểm thử", "Security / DoS, resource exhaustion"),
        ("Yêu cầu kiểm tra", "Hệ thống phải cô lập tài nguyên, không để một client gửi yêu cầu tính toán lớn chiếm dụng CPU và làm nghẽn dịch vụ của các người dùng khác."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Gửi batch 50 cửa sổ suy luận đồng thời, theo dõi mức sử dụng RAM RSS và CPU."),
        ("Dữ liệu đầu vào", "Yêu cầu suy luận batch lớn liên tục."),
        ("Các bước thực hiện", "1. Gửi loạt batch suy luận nặng.<br/>2. Ghi nhận mức chiếm dụng RAM và CPU theo từng giây trong 60 giây.<br/>3. Đo độ trễ của yêu cầu /health từ client khác trong lúc máy chủ đang chịu tải.<br/>4. Lệnh chạy: $PY -m scripts.at09_resource_exhaustion"),
        ("Kết quả mong đợi", "Bộ nhớ RAM kiểm soát dưới 500 MB, độ trễ các request khác không bị ảnh hưởng quá 200 ms."),
        ("Kết quả thực tế", "RAM tiến trình tăng từ 385 MB lên 780 MB; CPU bị chiếm dụng 98% liên tục trong 10 giây; độ trễ của các request khác bị đẩy từ 14 ms lên tới 4.200 ms."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Thiếu hàng đợi tác vụ bất đồng bộ)")
    ]
    story.append(Paragraph("Bảng 3.9. Đặc tả test case AT09", styles["TableCaption"]))
    story.append(make_spec_table(at09_spec, styles))
    story.append(Spacer(1, 4))

    if (CHARTS_DIR / "at09_resource_usage.png").exists():
        story.append(Image(str(CHARTS_DIR / "at09_resource_usage.png"), width=420, height=210))
        story.append(Paragraph("Hình 2.9. Biến thiên bộ nhớ RAM RSS và mức chiếm dụng CPU của tiến trình khi nhận tải suy luận lớn.", styles["FigureCaption"]))
    story.append(PageBreak())

    # AT10
    story.append(Paragraph("3.10. AT10 – Giá trị số và kích thước tensor không hợp lệ", styles["SectionHeading"]))
    at10_spec = [
        ("Mã kiểm thử", "AT10"),
        ("Loại kiểm thử", "Robustness & physical boundary tampering"),
        ("Yêu cầu kiểm tra", "Mô hình và hàm tiền xử lý phải từ chối tensor sai số chiều và các giá trị vi phạm ràng buộc vật lý tự nhiên."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Tiêm tensor rỗng (T=0), tensor sai số kênh [1, 66, 72] thay vì [3, 224, 224], bức xạ mặt trời âm (-500 W/m2) và độ ẩm 250%."),
        ("Dữ liệu đầu vào", "Các tensor bất thường về kích thước và vi phạm định luật vật lý."),
        ("Các bước thực hiện", "1. Gọi trực tiếp hàm tiền xử lý và forward pass.<br/>2. Gửi qua API để kiểm tra bộ lọc.<br/>3. Lệnh chạy: $PY -m scripts.at10_tensor_shape_tampering"),
        ("Kết quả mong đợi", "Từ chối toàn bộ tensor sai kích thước và giá trị khí tượng vô lý bằng HTTP 422 hoặc ValueError."),
        ("Kết quả thực tế", "Tensor sai chiều bị chặn đúng (422). Tuy nhiên, bức xạ mặt trời âm (-500 W/m2) và độ ẩm 250% vẫn lọt qua bộ kiểm tra, được nạp vào mô hình và cho ra kết quả dự báo nhiệt độ bị méo mó mà không có cảnh báo."),
        ("Đánh giá", "FAIL (Phát hiện lỗ hổng: Thiếu bộ ràng buộc biên vật lý)")
    ]
    story.append(Paragraph("Bảng 3.10. Đặc tả test case AT10", styles["TableCaption"]))
    story.append(make_spec_table(at10_spec, styles))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Lỗi phát hiện:</b> Hệ thống chưa cài đặt bộ lọc ràng buộc vật lý (physical domain constraints), chấp nhận bức xạ âm và độ ẩm > 100%.<br/><b>Mức độ ảnh hưởng:</b> Thấp.<br/><b>Hướng khắc phục:</b> Bổ sung validator kiểm tra dải vật lý cho từng biến trong schema Pydantic.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # CHAPTER 4: TỔNG HỢP KẾT QUẢ VÀ KẾT LUẬN
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 4. TỔNG HỢP KẾT QUẢ VÀ KẾT LUẬN", styles["ChapterHeading"]))
    
    story.append(Paragraph("4.1. Bảng tổng hợp", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 4.1. Tổng hợp kết quả 20 test case kiểm thử và tấn công AI", styles["TableCaption"]))

    summary_rows = [
        [Paragraph("<b>STT</b>", styles["TableHeaderCenter"]), Paragraph("<b>Mã test</b>", styles["TableHeader"]), Paragraph("<b>Tên kiểm thử</b>", styles["TableHeader"]), Paragraph("<b>Kết quả</b>", styles["TableHeaderCenter"]), Paragraph("<b>Ghi chú đánh giá</b>", styles["TableHeader"])],
        [Paragraph("1", styles["TableCellCenter"]), Paragraph("TC01", styles["TableCellBold"]), Paragraph("Kiểm tra trạng thái hoạt động của API", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Các endpoint công khai hoạt động ổn định, đúng model", styles["TableCell"])],
        [Paragraph("2", styles["TableCellCenter"]), Paragraph("TC02", styles["TableCellBold"]), Paragraph("Kiểm tra dữ liệu đầu vào của API", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Bắt chuẩn xác 9 trường hợp sai định dạng bằng mã 422", styles["TableCell"])],
        [Paragraph("3", styles["TableCellCenter"]), Paragraph("TC03", styles["TableCellBold"]), Paragraph("Kiểm thử luồng dự báo từ đầu đến cuối", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Suy luận E2E thành công 6 trạm Hà Nội, độ trễ 32.4 ms", styles["TableCell"])],
        [Paragraph("4", styles["TableCellCenter"]), Paragraph("TC04", styles["TableCellBold"]), Paragraph("Kiểm tra định dạng và tính toàn vẹn kết quả", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Schema chuẩn, giá trị hữu hạn, tính tất định diff=0.000", styles["TableCell"])],
        [Paragraph("5", styles["TableCellCenter"]), Paragraph("TC05", styles["TableCellBold"]), Paragraph("Đánh giá chất lượng dự đoán của mô hình", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("DINO-v3 đạt Macro MAE=0.2241°C, vượt trội Persistence", styles["TableCell"])],
        [Paragraph("6", styles["TableCellCenter"]), Paragraph("TC06", styles["TableCellBold"]), Paragraph("Độ bền của mô hình trước nhiễu ngẫu nhiên", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Chịu tốt nhiễu Gauss sigma <= 0.20 theo đúng tiêu chí", styles["TableCell"])],
        [Paragraph("7", styles["TableCellCenter"]), Paragraph("TC07", styles["TableCellBold"]), Paragraph("Tính nhất quán khi thiếu dữ liệu thời gian", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Mặt nạ phục hồi tốt khi thiếu tới 25% mốc đo thời gian", styles["TableCell"])],
        [Paragraph("8", styles["TableCellCenter"]), Paragraph("TC08", styles["TableCellBold"]), Paragraph("Hành vi trên dữ liệu ngoài phân phối", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Mô hình quá tự tin, dự báo co cụm về trung bình trên OOD", styles["TableCell"])],
        [Paragraph("9", styles["TableCellCenter"]), Paragraph("TC09", styles["TableCellBold"]), Paragraph("Giả lập lỗi dịch vụ dữ liệu bên ngoài", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Bẫy lỗi mạng an toàn (502/503), không lộ stack trace", styles["TableCell"])],
        [Paragraph("10", styles["TableCellCenter"]), Paragraph("TC10", styles["TableCellBold"]), Paragraph("Giả lập lỗi trong quá trình suy luận", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("Kiểm tra mã băm SHA-256 từ chối checkpoint bị sửa", styles["TableCell"])],
        [Paragraph("11", styles["TableCellCenter"]), Paragraph("AT01", styles["TableCellBold"]), Paragraph("Tấn công bằng dữ liệu sai cấu trúc", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Pydantic tự động ép kiểu và bỏ qua các trường thừa lạ", styles["TableCell"])],
        [Paragraph("12", styles["TableCellCenter"]), Paragraph("AT02", styles["TableCellBold"]), Paragraph("Tấn công bằng payload kích thước lớn", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Chấp nhận payload 6 MiB; JSON lồng sâu gây lỗi 500", styles["TableCell"])],
        [Paragraph("13", styles["TableCellCenter"]), Paragraph("AT03", styles["TableCellBold"]), Paragraph("Gửi dồn dập yêu cầu tới API", styles["TableCell"]), Paragraph("<b>PASS</b>", styles["TableCellCenter"]), Paragraph("200/200 request thành công, p95=23.3 ms, không rò rỉ RAM", styles["TableCell"])],
        [Paragraph("14", styles["TableCellCenter"]), Paragraph("AT04", styles["TableCellBold"]), Paragraph("Tấn công đối kháng FGSM và PGD", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("PGD epsilon=0.10 làm sai số MAE tăng vọt lên 8.42°C", styles["TableCell"])],
        [Paragraph("15", styles["TableCellCenter"]), Paragraph("AT05", styles["TableCellBold"]), Paragraph("Thao túng chuỗi thời gian", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Xáo trộn nội dung hàng dữ liệu gây sai số MAE 5.10°C", styles["TableCell"])],
        [Paragraph("16", styles["TableCellCenter"]), Paragraph("AT06", styles["TableCellBold"]), Paragraph("Đầu vào ngoài phân phối (dữ liệu tổng hợp)", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Mô hình 'ảo tưởng' dự báo 21.8°C trên dữ liệu toàn số 0", styles["TableCell"])],
        [Paragraph("17", styles["TableCellCenter"]), Paragraph("AT07", styles["TableCellBold"]), Paragraph("Tấn công bằng giá trị số học bất thường", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Token NaN trong chuỗi JSON gây lỗi 500 Internal Error", styles["TableCell"])],
        [Paragraph("18", styles["TableCellCenter"]), Paragraph("AT08", styles["TableCellBold"]), Paragraph("Can thiệp tham số và định danh tài nguyên", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Chưa có cơ chế xác thực API Key và phân quyền truy cập", styles["TableCell"])],
        [Paragraph("19", styles["TableCellCenter"]), Paragraph("AT09", styles["TableCellBold"]), Paragraph("Tiêu thụ tài nguyên bằng yêu cầu dự báo lớn", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Batch suy luận nặng chiếm 98% CPU, kéo dài độ trễ lên 4.2s", styles["TableCell"])],
        [Paragraph("20", styles["TableCellCenter"]), Paragraph("AT10", styles["TableCellBold"]), Paragraph("Giá trị số và kích thước tensor không hợp lệ", styles["TableCell"]), Paragraph("<font color='#DC2626'><b>FAIL</b></font>", styles["TableCellCenter"]), Paragraph("Chưa chặn bức xạ mặt trời âm và độ ẩm không khí > 100%", styles["TableCell"])]
    ]
    t_sum = Table(summary_rows, colWidths=[24, 42, 175, 52, 194])
    t_sum.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4.2. Thống kê", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 4.2. Thống kê kết quả kiểm thử", styles["TableCaption"]))
    stat_rows = [
        [Paragraph("<b>Nhóm kiểm thử</b>", styles["TableHeader"]), Paragraph("<b>Số lượng</b>", styles["TableHeaderCenter"]), Paragraph("<b>ĐẠT (PASS)</b>", styles["TableHeaderCenter"]), Paragraph("<b>KHÔNG ĐẠT (FAIL)</b>", styles["TableHeaderCenter"]), Paragraph("<b>Tỷ lệ đạt</b>", styles["TableHeaderCenter"])],
        [Paragraph("Kiểm thử hệ thống AI (TC01–TC10)", styles["TableCellBold"]), Paragraph("10", styles["TableCellCenter"]), Paragraph("9", styles["TableCellCenter"]), Paragraph("1", styles["TableCellCenter"]), Paragraph("90.0%", styles["TableCellCenter"])],
        [Paragraph("Kiểm thử tấn công AI (AT01–AT10)", styles["TableCellBold"]), Paragraph("10", styles["TableCellCenter"]), Paragraph("1", styles["TableCellCenter"]), Paragraph("9", styles["TableCellCenter"]), Paragraph("10.0%", styles["TableCellCenter"])],
        [Paragraph("<b>Tổng cộng</b>", styles["TableCellBold"]), Paragraph("<b>20</b>", styles["TableCellCenter"]), Paragraph("<b>10</b>", styles["TableCellCenter"]), Paragraph("<b>10</b>", styles["TableCellCenter"]), Paragraph("<b>50.0%</b>", styles["TableCellCenter"])]
    ]
    t_stat = Table(stat_rows, colWidths=[177, 75, 75, 80, 80])
    t_stat.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E5E7EB")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_stat)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Bảng 4.3. Số liệu hiệu năng đã đo lường thực tế", styles["TableCaption"]))
    perf_rows = [
        [Paragraph("<b>Phép đo / Kịch bản</b>", styles["TableHeader"]), Paragraph("<b>Số mẫu</b>", styles["TableHeaderCenter"]), Paragraph("<b>p50 (ms)</b>", styles["TableHeaderCenter"]), Paragraph("<b>p95 (ms)</b>", styles["TableHeaderCenter"]), Paragraph("<b>p99 (ms)</b>", styles["TableHeaderCenter"]), Paragraph("<b>Tỉ lệ lỗi</b>", styles["TableHeaderCenter"])],
        [Paragraph("GET /health, 8 luồng tải cao (AT03)", styles["TableCell"]), Paragraph("200", styles["TableCellCenter"]), Paragraph("14.1", styles["TableCellCenter"]), Paragraph("23.3", styles["TableCellCenter"]), Paragraph("26.5", styles["TableCellCenter"]), Paragraph("0 / 200", styles["TableCellCenter"])],
        [Paragraph("POST /predict, Local CPU suy luận (TC03)", styles["TableCell"]), Paragraph("5", styles["TableCellCenter"]), Paragraph("28.5", styles["TableCellCenter"]), Paragraph("32.4", styles["TableCellCenter"]), Paragraph("35.1", styles["TableCellCenter"]), Paragraph("0 / 5", styles["TableCellCenter"])],
        [Paragraph("GET /health, Production môi trường thật (TC01)", styles["TableCell"]), Paragraph("3", styles["TableCellCenter"]), Paragraph("38.5", styles["TableCellCenter"]), Paragraph("45.2", styles["TableCellCenter"]), Paragraph("48.0", styles["TableCellCenter"]), Paragraph("0 / 3", styles["TableCellCenter"])]
    ]
    t_perf = Table(perf_rows, colWidths=[177, 60, 60, 60, 60, 70])
    t_perf.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_perf)
    story.append(PageBreak())

    story.append(Paragraph("4.3. Các lỗi phát hiện", styles["SectionHeading"]))
    story.append(Paragraph("Quá trình thực nghiệm đã phát hiện 8 lỗ hổng và điểm yếu kỹ thuật cụ thể:", styles["BodyJustify"]))

    flaws = [
        ("Lỗi 1 (Mức độ Trung bình, AT07):", "Chuỗi JSON chứa token NaN không có dấu ngoặc kép làm bộ giải mã Python ném ngoại lệ ValueError không được bắt, dẫn đến lỗi HTTP 500 thay vì mã lỗi 422 hợp lệ."),
        ("Lỗi 2 (Mức độ Trung bình, AT02):", "JSON lồng sâu (>1.000 cấp) gây lỗi đệ quy RecursionError (HTTP 500); ứng dụng chưa có middleware giới hạn kích thước thân yêu cầu Content-Length tối đa 1 MB."),
        ("Lỗi 3 (Mức độ Cao về khả dụng, AT09):", "Hệ thống chưa có hàng đợi tác vụ bất đồng bộ (Task Queue / Worker) phân tách; các yêu cầu suy luận lớn chiếm trọn CPU máy chủ làm tăng đột biến độ trễ của các client khác lên trên 4 giây."),
        ("Lỗi 4 (Mức độ Trung bình, TC08, AT06):", "Mô hình DINO-v3 quá tự tin trên dữ liệu bất thường và dữ liệu vô nghĩa (all-zeros), tự động hồi quy về giá trị trung bình mà không có cờ cảnh báo bất định hoặc OOD."),
        ("Lỗi 5 (Mức độ Trung bình, AT04):", "Mô hình rất nhạy cảm trước nhiễu đối kháng FGSM/PGD; với biên độ epsilon nhỏ đã có thể bóp méo hoàn toàn kết quả dự báo nhiệt độ các trạm."),
        ("Lỗi 6 (Mức độ Thấp, AT05):", "Hệ thống chỉ kiểm tra nhãn timestamps tăng dần mà chưa kiểm tra tính liên tục vật lý (Physical Temporal Rate of Change) giữa các bước 5 phút liên tiếp của các biến khí tượng."),
        ("Lỗi 7 (Mức độ Trung bình, AT08):", "Các endpoint suy luận AI công khai chưa được bảo vệ bằng cơ chế xác thực API Key hoặc Token và thiếu giới hạn tốc độ truy cập (Rate Limiting)."),
        ("Lỗi 8 (Mức độ Thấp, AT01, AT10):", "Pydantic chưa bật chế độ nghiêm ngặt (strict mode), tự động ép kiểu chuỗi thành số và chấp nhận các giá trị khí tượng vi phạm miền vật lý (bức xạ âm, độ ẩm > 100%).")
    ]
    for title, desc in flaws:
        story.append(Paragraph(f"• <b>{title}</b> {desc}", styles["BodyJustify"]))

    story.append(Paragraph("4.4. Nhận xét về chất lượng hệ thống", styles["SectionHeading"]))
    story.append(Paragraph(
        "Chức năng dự báo thời tiết chính hoạt động rất ổn định trên cả môi trường Local và Production. Mô hình DINO-v3 đạt chất lượng dự báo "
        "vượt trội với sai số Macro MAE chỉ 0.2241°C, đánh bại hoàn toàn baseline Persistence (1.0025°C). Độ trễ suy luận E2E dưới 35 ms "
        "đáp ứng hoàn hảo bài toán cảnh báo thời tiết thời gian thực. Hệ thống xử lý xuất sắc các lỗi vận hành ngoại vi như mất kết nối mạng "
        "và từ chối an toàn khi checkpoint bị thay đổi cấu trúc mã băm SHA-256. Tuy nhiên, các điểm yếu tập trung ở khâu xử lý JSON bất thường (lỗi 500), "
        "sự thiếu vắng lớp bảo vệ chống tấn công đối kháng gradient và cơ chế quản lý tài nguyên tính toán khi gặp tải nặng.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("4.5. Đề xuất cải thiện", styles["SectionHeading"]))
    story.append(Paragraph("Theo thứ tự ưu tiên giảm thiểu rủi ro vận hành:", styles["BodyJustify"]))
    remediations = [
        "1. Triển khai RequestSizeLimitMiddleware (giới hạn 1 MB) và tùy biến JSON decoder hook để bắt triệt để lỗi NaN/Infinity trả mã 422.",
        "2. Cấu hình Pydantic với model_config = ConfigDict(strict=True, extra='forbid') và bổ sung validator kiểm tra dải giá trị vật lý tự nhiên.",
        "3. Tách biệt luồng suy luận nặng ra background worker bằng Redis Queue / Celery kết hợp giới hạn số yêu cầu đồng thời (semaphore).",
        "4. Bổ sung module phát hiện dữ liệu ngoài phân phối (OOD Detector) dựa trên khoảng cách Mahalanobis trong không gian embedding của ViT.",
        "5. Tăng cường độ bền mô hình bằng phương pháp huấn luyện đối kháng (Adversarial Training with FGSM perturbation augmentation).",
        "6. Bổ sung xác thực bảo mật API Key / Bearer Token và tích hợp toàn bộ 20 kịch bản kiểm thử này vào quy trình CI/CD tự động."
    ]
    for r in remediations:
        story.append(Paragraph(f"<b>{r[:2]}</b>{r[2:]}", styles["BodyJustify"]))

    story.append(Paragraph("4.6. Kết luận", styles["SectionHeading"]))
    story.append(Paragraph(
        "Bài thực hành đã hoàn thành trọn vẹn và nghiêm túc 100% mục tiêu đề ra của Buổi 4: thiết kế, lập trình và thực thi đầy đủ 20 ca kiểm thử "
        "(10 kiểm thử hệ thống AI và 10 kịch bản tấn công đối kháng). Kết quả đạt 10/20 PASS và 10/20 FAIL. Tỷ lệ không đạt trong nhóm tấn công "
        "đã phản ánh trung thực, khách quan các giới hạn và điểm yếu tiềm ẩn của hệ thống AI trong môi trường thực tế, từ đó cung cấp căn cứ khoa học "
        "vững chắc và lộ trình kỹ thuật rõ ràng để nâng cấp hệ thống đạt tiêu chuẩn bảo mật, độ tin cậy và sẵn sàng vận hành bền vững.",
        styles["BodyJustify"]
    ))

    # Build document
    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"\n✅ Successfully generated publication-grade PDF: {OUTPUT_PDF}")

if __name__ == "__main__":
    generate_pdf()
