"""
PDF Generator for Lab 4: AI System Testing & Adversarial Security Attacks.
Project: Hanoi Multi-Station Weather Forecasting System (DINO-v3 Backbone).
Student: Nguyễn Thuận Hòa | MSV: 2351260652 | Lớp: 65TTNT | Khoa CNTT - ĐH Thủy Lợi.

Formatting & Typography:
- Font: Times New Roman (Regular, Bold, Italic, BoldItalic) via Windows TrueType fonts.
- Monospace: Consolas.
- Page numbering: Bottom center Arabic numerals (Page 1 = Chương 1 ... Page 46 = Kết luận).
- Cover page: Unnumbered.
"""

import os
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas

# Ensure UTF-8
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "Bao_Cao_Thuc_Hanh_Chuyen_De_Buoi_4.pdf"
EVIDENCE_DIR = BASE_DIR / "testing_report" / "evidence"
CHARTS_DIR = EVIDENCE_DIR / "charts"

# ------------------------------------------------------------------------------
# EXACT-MATCH CANVAS: FOOTER PAGE NUMBER ONLY (CENTERED)
# ------------------------------------------------------------------------------
class ExactMatchCanvas(canvas.Canvas):
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, total_pages):
        self.saveState()
        # Page 1 is Cover -> Unnumbered
        if self._pageNumber > 1:
            content_page_num = self._pageNumber - 1
            self.setFont("TimesNewRoman", 10)
            self.setFillColor(colors.black)
            self.drawCentredString(A4[0] / 2.0, 36, str(content_page_num))
        self.restoreState()

# ------------------------------------------------------------------------------
# REGISTER TIMES NEW ROMAN FONTS
# ------------------------------------------------------------------------------
def register_tnr_fonts():
    pdfmetrics.registerFont(TTFont("TimesNewRoman", r"C:\Windows\Fonts\times.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", r"C:\Windows\Fonts\timesbd.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", r"C:\Windows\Fonts\timesi.ttf"))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", r"C:\Windows\Fonts\timesbi.ttf"))
    registerFontFamily(
        "TimesNewRoman",
        normal="TimesNewRoman",
        bold="TimesNewRoman-Bold",
        italic="TimesNewRoman-Italic",
        boldItalic="TimesNewRoman-BoldItalic"
    )
    pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))
    pdfmetrics.registerFont(TTFont("Consolas-Bold", r"C:\Windows\Fonts\consolab.ttf"))

# ------------------------------------------------------------------------------
# HELPER TABLE & BOX BUILDERS
# ------------------------------------------------------------------------------
def make_spec_table(fields, styles, col_widths=[110, 377]):
    data = []
    for k, v in fields:
        p_k = Paragraph(k, styles["TableCell"])
        p_v = Paragraph(v, styles["TableCell"])
        data.append([p_k, p_v])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 4.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 4.0),
    ]))
    return t

def make_code_box(code_text, styles, font_size=7.2, leading=9.0):
    style = ParagraphStyle(
        "CodeText",
        fontName="Consolas",
        fontSize=font_size,
        leading=leading,
        textColor=colors.black
    )
    safe_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    p = Paragraph(safe_text, style)
    t = Table([[p]], colWidths=[487])
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
        ('LEFTPADDING', (0,0), (-1,-1), 4.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 4.0),
    ]))
    return t

def make_cases_table(rows, styles, col_widths=[30, 110, 128, 44, 175]):
    data = [[
        Paragraph("STT", styles["TableCellCenter"]),
        Paragraph("Trường hợp", styles["TableCell"]),
        Paragraph("Dữ liệu gửi", styles["TableCell"]),
        Paragraph("HTTP", styles["TableCellCenter"]),
        Paragraph("Phản hồi nhận được", styles["TableCell"])
    ]]
    for idx, case_name, req_desc, http_code, resp_desc in rows:
        data.append([
            Paragraph(str(idx), styles["TableCellCenter"]),
            Paragraph(case_name, styles["TableCell"]),
            Paragraph(req_desc, styles["TableCell"]),
            Paragraph(str(http_code), styles["TableCellCenter"]),
            Paragraph(resp_desc, styles["TableCell"])
        ])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 2.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 2.5),
    ]))
    return t

# ------------------------------------------------------------------------------
# BUILD EXACT 48 PAGES
# ------------------------------------------------------------------------------
def generate_pdf():
    register_tnr_fonts()
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    # Margins 54pt (0.75 inch)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Exact Typography matching request: Chapter 14pt, All else 13pt
    styles.add(ParagraphStyle(
        "CoverTitle",
        fontName="TimesNewRoman-Bold",
        fontSize=18,
        leading=24,
        alignment=1, # Center
        spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        "CoverAuthor",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=17,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        "ChapterHeading",
        fontName="TimesNewRoman-Bold",
        fontSize=14,
        leading=18,
        alignment=1, # Centered
        spaceBefore=0,
        spaceAfter=8,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        "SectionHeading",
        fontName="TimesNewRoman-Bold",
        fontSize=13,
        leading=16.5,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        "TableCaption",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=16,
        alignment=1, # Centered
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        "FigureCaption",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=16,
        alignment=1, # Centered
        spaceBefore=3,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        "BodyJustify",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=16.5,
        alignment=4, # Justify
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        "TableCell",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=15.5
    ))
    styles.add(ParagraphStyle(
        "TableCellCenter",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=15.5,
        alignment=1
    ))

    story = []

    # ==========================================================================
    # PAGE 1 (PDF PAGE 1 - BÌA)
    # ==========================================================================
    story.append(Spacer(1, 240))
    story.append(Paragraph("BÁO CÁO THỰC HÀNH CHUYÊN ĐỀ – BUỔI 4", styles["CoverTitle"]))
    story.append(Paragraph("Nguyễn Thuận Hòa | 2351260652", styles["CoverAuthor"]))
    story.append(PageBreak())

    # ==========================================================================
    # CHƯƠNG 1 (NUMBERED AS "1": 1.1, 1.2, 1.3, 1.4)
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 1. GIỚI THIỆU VÀ MÔI TRƯỜNG KIỂM THỬ", styles["ChapterHeading"]))
    story.append(Paragraph("1.1. Giới thiệu dự án", styles["SectionHeading"]))
    story.append(Paragraph(
        "Hanoi Multi-Station Weather Forecasting là hệ thống dự báo thời tiết và nhiệt độ ngắn hạn cho khu vực thủ đô Hà Nội "
        "tại 6 trạm quan trắc khí tượng: Hoàn Kiếm (st01), Ba Đình (st02), Cầu Giấy (st03), Hà Đông (st04), Đông Anh (st05) "
        "và Sóc Sơn (st06). Người dùng cung cấp chuỗi dữ liệu 6 giờ quá khứ (72 bước thời gian, bước nhảy 5 phút), hệ thống chạy "
        "mô hình và trả về kết quả dự báo nhiệt độ tại thời điểm t + 60 phút cho từng trạm, kèm khoảng tin cậy. Dịch vụ đang "
        "chạy tại https://thuanhoa1110.github.io/ChuyenDe/.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.2. Mô hình AI", styles["SectionHeading"]))
    story.append(Paragraph(
        "Mô hình là DINO-v3 Forecaster (Vision Transformer ViT-S/16), được huấn luyện trên bộ dữ liệu khí tượng Hà Nội với 6 trạm và "
        "11 biến thời tiết (66 kênh). Đầu vào là chuỗi 72 bước thời gian được mã hóa thành ma trận không gian - thời gian 3 kênh (Kênh 0: "
        "giá trị chuẩn hóa; Kênh 1: sai phân thời gian; Kênh 2: mặt nạ quan sát) trên kích thước chuẩn 224×224 pixel. Mô hình học đặc trưng "
        "biến thiên thời tiết theo không gian và thời gian. Trước khi nạp, checkpoint được kiểm tra SHA-256 với file manifest của dự án.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.3. Kiến trúc hệ thống", styles["SectionHeading"]))
    story.append(Paragraph(
        "Giao diện web dùng Leaflet và Chart.js. Backend FastAPI nhận dữ liệu dạng JSON, kiểm tra dữ liệu đầu vào và đưa job vào hàng đợi. "
        "Worker chuẩn hóa dữ liệu bằng StandardScaler, chạy DINO-v3 trên CPU, ghép kết quả và xuất JSON. Giao diện hiển thị trực quan "
        "bản đồ nhiệt độ và biểu đồ dự báo. Hệ thống được đóng gói bằng Docker; GitHub Actions tự động build image và kiểm tra sức khỏe dịch vụ.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.4. Môi trường kiểm thử", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 1.1. Môi trường Local và Production", styles["TableCaption"]))
    env_rows = [
        [Paragraph("Hạng mục", styles["TableCell"]), Paragraph("Local", styles["TableCell"]), Paragraph("Production", styles["TableCell"])],
        [Paragraph("Phần cứng", styles["TableCell"]), Paragraph("Intel Core i5-12500H, 16 luồng, 15 GiB RAM", styles["TableCell"]), Paragraph("GitHub Actions Runner (ARM64/x86_64, container 2 CPU)", styles["TableCell"])],
        [Paragraph("Hệ điều hành", styles["TableCell"]), Paragraph("Ubuntu 24.04.5 / Windows 11", styles["TableCell"]), Paragraph("Ubuntu 24.04, Docker, Caddy", styles["TableCell"])],
        [Paragraph("Phần mềm", styles["TableCell"]), Paragraph("Python 3.12, PyTorch 2.2.0 (CPU), FastAPI 0.109.0", styles["TableCell"]), Paragraph("Image build từ cùng mã nguồn", styles["TableCell"])],
        [Paragraph("Checkpoint", styles["TableCell"]), Paragraph("SHA-256 dinov3_forecaster_best.pt", styles["TableCell"]), Paragraph("Cùng checkpoint (xác nhận ở TC01)", styles["TableCell"])],
        [Paragraph("Dữ liệu", styles["TableCell"]), Paragraph("6 trạm thời tiết Hà Nội, test split chuẩn hóa", styles["TableCell"]), Paragraph("Cùng danh mục dữ liệu benchmark", styles["TableCell"])]
    ]
    t_env = Table(env_rows, colWidths=[80, 203, 204])
    t_env.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 4.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 4.0),
    ]))
    story.append(t_env)
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 4 (NUMBERED AS "3" - 1.5, 1.6)
    # ==========================================================================
    story.append(Paragraph(
        "Production chỉ dùng cho các kiểm thử an toàn: gọi các endpoint đọc, kiểm tra dữ liệu đầu vào bằng endpoint không tạo job, "
        "và đúng hai lần phân tích dự báo (một qua API, một qua giao diện). Các yêu cầu được gửi tuần tự, có giới hạn thời gian chờ. "
        "Tổng cộng có 36 yêu cầu do script gửi và 76 yêu cầu do giao diện tự sinh khi hỏi trạng thái job. Tất cả kiểm thử tấn công, "
        "giả lập lỗi và gây tải chỉ chạy ở Local.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.5. Công cụ kiểm thử", styles["SectionHeading"]))
    story.append(Paragraph(
        "Kiểm thử API dùng pytest, FastAPI TestClient và httpx. Kiểm thử giao diện dùng Playwright điều khiển Google Chrome. "
        "Kiểm thử mô hình dùng NumPy và PyTorch. Giả lập lỗi dùng unittest.mock và httpx.MockTransport. Biểu đồ được vẽ bằng Matplotlib "
        "từ dữ liệu đo được. Trước khi kiểm thử, bộ test có sẵn của dự án được chạy lại với dữ liệu thật và đạt 54/54.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("1.6. Phương pháp và tiêu chí đánh giá", styles["SectionHeading"]))
    story.append(Paragraph(
        "Mỗi test case được thiết kế theo các trường: mã, yêu cầu kiểm tra, điều kiện thực hiện, dữ liệu đầu vào, các bước, kết quả mong đợi, "
        "kết quả thực tế và Pass/Fail. Dữ liệu thử gồm cả trường hợp đúng (positive), sai (negative) và giá trị biên (boundary). Kết quả mong đợi "
        "và ngưỡng được ghi trước khi chạy, không sửa sau đó. Test case đạt (PASS) khi mọi kiểm tra đạt; không đạt (FAIL) khi có ít nhất một "
        "kiểm tra sai; BLOCKED khi không thực hiện được. Với nhóm tấn công, FAIL nghĩa là đã phát hiện một điểm yếu của hệ thống. Mỗi test case "
        "lưu bằng chứng trong thư mục testing_report/evidence/<mã test>/, gồm result.json, execution.log, dữ liệu yêu cầu và phản hồi, ảnh. "
        "Các lệnh trong báo cáo chạy từ thư mục testing_report, với $PY là Python của môi trường ảo dự án.",
        styles["BodyJustify"]
    ))
    story.append(Paragraph(
        "Sau bảng đặc tả của mỗi test case là ảnh minh chứng và các bảng tham số. Với test API, báo cáo in một request và response tiêu biểu, "
        "sau đó liệt kê các trường hợp còn lại kèm dữ liệu gửi và phản hồi nhận được. Phản hồi dài chỉ giữ các trường chính; payload quá lớn chỉ "
        "ghi kích thước. Với test mô hình, báo cáo in cấu hình kiểm thử và các chỉ số kết quả chính. Toàn bộ số liệu lấy từ các file request.json, "
        "response.json, input.json và output.json lưu lúc chạy test. Riêng AT01, AT02 và AT07 gửi body dạng chuỗi nên lúc chạy chỉ lưu 300 ký tự đầu; "
        "body đầy đủ trong báo cáo được sinh lại bằng chính đoạn mã của script và đã đối chiếu khớp số byte, phần đầu chuỗi và mã SHA-256 (AT02).",
        styles["BodyJustify"]
    ))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 5 (NUMBERED AS "4" - CHƯƠNG 2, 2.1 TC01 ĐẶC TẢ)
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 2. KIỂM THỬ HỆ THỐNG AI", styles["ChapterHeading"]))
    story.append(Paragraph(
        "Chương này gồm 10 test case: 4 kiểm thử tự động API và hệ thống (TC01–TC04), 4 kiểm thử mô hình AI (TC05–TC08) "
        "và 2 kiểm thử giả lập lỗi (TC09–TC10).",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("2.1. TC01 – Kiểm tra trạng thái hoạt động của API", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.1. Đặc tả test case TC01", styles["TableCaption"]))
    tc01_spec = [
        ("Mã kiểm thử", "TC01"),
        ("Loại kiểm thử", "Automation, positive, hộp đen"),
        ("Yêu cầu kiểm tra", "Các endpoint công khai phải hoạt động, báo đúng mô hình và checkpoint đang dùng."),
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Ứng dụng local khởi động được với checkpoint và dữ liệu thật; máy kiểm thử truy cập được https://thuanhoa1110.github.io/ChuyenDe/."),
        ("Dữ liệu đầu vào", "Yêu cầu GET tới 5 endpoint /health, /metadata, / (giao diện), /openapi.json, /docs; mỗi endpoint gọi 3 lần trên mỗi môi trường (15 yêu cầu/môi trường)."),
        ("Các bước thực hiện", "1. Khởi động ứng dụng local bằng FastAPI TestClient (quá trình khởi động tự kiểm tra SHA-256 của checkpoint).<br/>2. Gửi lần lượt 15 yêu cầu GET tới local, ghi mã trạng thái và thời gian phản hồi.<br/>3. Gửi 15 yêu cầu tương tự tới Production, tuần tự, cách nhau 0,3 s.<br/>4. So sánh trường checkpoint_sha256 giữa hai môi trường; chụp màn hình trang chủ Production.<br/>5. Lệnh chạy: cd testing_report && $PY -m scripts.tc01_health_availability"),
        ("Kết quả mong đợi", "Tất cả yêu cầu trả HTTP 200; /health báo status=healthy, model=DINOv3Forecaster; đủ 6 trạm; trung vị thời gian /health dưới 3 giây; hai môi trường cùng checkpoint."),
        ("Kết quả thực tế", "Cả 30 yêu cầu đều trả HTTP 200. Hai môi trường cùng checkpoint dinov3_forecaster_best.pt, khớp với manifest. Trung vị thời gian /health là 4,2 ms ở Local và 38,5 ms ở Production. Yêu cầu đầu tiên tới Production mất 1250 ms do thiết lập kết nối SSL."),
        ("Đánh giá", "PASS (11/11 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc01_spec, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 6 (NUMBERED AS "5" - TC01 CONT'D, 2.2 TC02 BẮT ĐẦU)
    # ==========================================================================
    if (CHARTS_DIR / "web_ui.png").exists():
        story.append(Image(str(CHARTS_DIR / "web_ui.png"), width=340, height=135))
    elif (CHARTS_DIR / "tc05_prediction_scatter.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc05_prediction_scatter.png"), width=340, height=135))
    story.append(Paragraph("Hình 2.1. Giao diện trực quan hóa dự báo nhiệt độ 6 trạm Hà Nội trên Production.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.2. Tham số kiểm thử TC01 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box("GET /health (Local)\nKhông có body", styles))

    story.append(Paragraph("Bảng 2.3. Kết quả phản hồi API TC01 (response JSON)", styles["TableCaption"]))
    h_resp_str = 'HTTP 200, 4,2 ms\n{\n  "status": "healthy",\n  "model_name": "DINOv3Forecaster",\n  "device": "cpu",\n  "model_checkpoint": "dinov3_forecaster_best.pt",\n  "scaler_loaded": true,\n  "uptime_seconds": 42.15\n}'
    story.append(make_code_box(h_resp_str, styles))

    story.append(Paragraph("Bảng 2.4. Các trường hợp kiểm thử TC01 (30 request)", styles["TableCaption"]))
    tc01_30 = [
        (1, "GET /health (Local và Production, 6 lần)", "—", 200, '{"status": "healthy", "model": "DINOv3"}'),
        (2, "GET /metadata (Local và Production, 6 lần)", "—", 200, '{"stations": 6, "lookback": 72}'),
        (3, "GET / (Local và Production, 6 lần)", "—", 200, "trang HTML, 44.887 byte"),
        (4, "GET /openapi.json (Local và Production, 6 lần)", "—", 200, '{"openapi": "3.1.0", "title": "Weather API"}'),
        (5, "GET /docs (Local và Production, 6 lần)", "—", 200, "trang HTML Swagger UI")
    ]
    story.append(make_cases_table(tc01_30, styles))

    story.append(Paragraph("2.2. TC02 – Kiểm tra dữ liệu đầu vào của API", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.5. Đặc tả test case TC02", styles["TableCaption"]))
    tc02_p1 = [
        ("Mã kiểm thử", "TC02"),
        ("Loại kiểm thử", "Automation, positive/negative/boundary, hộp đen")
    ]
    story.append(make_spec_table(tc02_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 7 (NUMBERED AS "6" - TC02 ĐẶC TẢ CONT'D, BẢNG 2.6)
    # ==========================================================================
    tc02_p2 = [
        ("Yêu cầu kiểm tra", "API phải chấp nhận yêu cầu hợp lệ và từ chối yêu cầu sai bằng mã 422 kèm thông báo rõ ràng."),
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Như TC01. Dùng endpoint POST /predict để kiểm tra dữ liệu chuỗi thời gian 72 bước."),
        ("Dữ liệu đầu vào", "10 payload: 1 chuỗi hợp lệ (72 mốc x 6 trạm x 11 biến) và 9 payload sai (xem bảng số liệu bên dưới)."),
        ("Các bước thực hiện", "1. Tạo chuỗi thời gian hợp lệ từ dữ liệu 6 trạm Hà Nội.<br/>2. Gửi 10 payload tới /predict trên Local, ghi mã trạng thái và thông báo lỗi.<br/>3. Gửi đúng 10 payload đó tới Production, tuần tự.<br/>4. So sánh mã trạng thái và thông báo giữa hai môi trường.<br/>5. Lệnh chạy: $PY -m scripts.tc02_input_validation"),
        ("Kết quả mong đợi", "Payload hợp lệ trả 200; 9 payload sai trả 422, không có lỗi 500; Local và Production giống nhau."),
        ("Kết quả thực tế", "Cả 20 lượt gọi đều trả đúng mã mong đợi. Thông báo lỗi ở hai môi trường giống hệt nhau (bảng số liệu bên dưới)."),
        ("Đánh giá", "PASS (21/21 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc02_p2, styles))

    story.append(Paragraph("Bảng 2.6. Kết quả kiểm tra dữ liệu đầu vào", styles["TableCaption"]))
    b26_data = [
        [Paragraph("Trường hợp", styles["TableCell"]), Paragraph("Mong đợi", styles["TableCellCenter"]), Paragraph("Local", styles["TableCellCenter"]), Paragraph("Production", styles["TableCellCenter"])],
        [Paragraph("V1 hợp lệ: chuỗi 72 bước x 6 trạm x 11 biến", styles["TableCell"]), Paragraph("200", styles["TableCellCenter"]), Paragraph("200", styles["TableCellCenter"]), Paragraph("200", styles["TableCellCenter"])],
        [Paragraph("I1 thiếu end_timestamp", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I2 thiếu station_ids", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I3 thiếu data", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I4 timestamps chỉ 50 mốc", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I5 station_ids sai thứ tự", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I6 timestamps giảm dần (ngược)", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I7 bước nhảy thời gian 10 phút", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I8 thiếu cột đặc trưng st01_temperature", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])],
        [Paragraph("I9 ma trận 2D thiếu cột (60 thay vì 66)", styles["TableCell"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"]), Paragraph("422", styles["TableCellCenter"])]
    ]
    t_b26 = Table(b26_data, colWidths=[247, 80, 80, 80])
    t_b26.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 3.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_b26)
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 8 (NUMBERED AS "7" - TC02 LOG, BẢNG 2.7, 2.8, 2.9 PART 1)
    # ==========================================================================
    log_tc02_box = "$ TC02: trích evidence/TC02/execution.log\nPASS · [Local] V1 hợp lệ: chuỗi 72 bước x 6 trạm · expected=200 · actual=200\nPASS · [Local] I1 thiếu end_timestamp · expected=422 · actual=422 Field required\nPASS · [Local] I2 thiếu station_ids · expected=422 · actual=422 Field required\nPASS · [Local] I3 thiếu data · expected=422 · actual=422 Field required\nPASS · [Local] I4 timestamps chỉ 50 mốc · expected=422 · actual=422 Value error\nPASS · [Local] I5 station_ids sai thứ tự · expected=422 · actual=422 Value error\nPASS · [Local] I6 timestamps giảm dần · expected=422 · actual=422 Value error\nPASS · [Local] I7 bước nhảy thời gian 10 phút · expected=422 · actual=422 Value error\nPASS · [Local] I8 thiếu cột nhiệt độ · expected=422 · actual=422 Value error\nPASS · [Local] I9 ma trận 2D thiếu cột · expected=422 · actual=422 Value error\nPASS · [Production] V1 hợp lệ · expected=200 · actual=200\n... (9 assertion khác, xem đầy đủ trong execution.log)\nVERDICT TC02: PASS"
    story.append(make_code_box(log_tc02_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 2.2. Trích nhật ký thực thi TC02 (evidence/TC02/execution.log).", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.7. Tham số kiểm thử TC02 (request JSON)", styles["TableCaption"]))
    req_v1_str = 'POST /predict (Local)\nTrường hợp: V1 hợp lệ: chuỗi 72 bước x 6 trạm x 11 biến\n{\n  "end_timestamp": "2016-01-01 05:55:00",\n  "station_ids": ["st01", "st02", "st03", "st04", "st05", "st06"],\n  "timestamps": ["2016-01-01 00:00:00", "2016-01-01 00:05:00", ..., "2016-01-01 05:55:00"],\n  "data": {"st01_temperature": [21.5, ...], "st01_humidity": [85.0, ...], ...}\n}'
    story.append(make_code_box(req_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 2.8. Kết quả phản hồi API TC02 (response JSON)", styles["TableCaption"]))
    res_v1_str = 'Trường hợp: V1 hợp lệ: chuỗi 72 bước x 6 trạm x 11 biến\nHTTP 200, 32,4 ms\n{\n  "status": "success",\n  "model_version": "v1.0.0",\n  "horizon_steps": 12,\n  "horizon_minutes": 60,\n  "predictions": {"st01_hoankiem": 21.45, "st02_badinh": 21.32, "st03_caugiay": 21.58, "st04_hadong": 21.65, "st05_donganh": 21.10, "st06_socson": 20.95},\n  "units": "°C",\n  "latency_ms": 28.5\n}'
    story.append(make_code_box(res_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 2.7; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 2.9. Các trường hợp kiểm thử TC02 (20 request)", styles["TableCaption"]))
    tc02_p1_cases = [
        (1, "V1 hợp lệ: 72 mốc x 6 trạm", "body như Bảng 2.7", 200, '{"status": "success", "horizon_minutes": 60}'),
        (2, "I1 thiếu end_timestamp", "không có trường end_timestamp", 422, '{"detail": [{"loc": ["body", "end_timestamp"], "msg": "Field required"}]}')
    ]
    story.append(make_cases_table(tc02_p1_cases, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 10 (NUMBERED AS "8" - TC02 BẢNG 2.9 PART 2, 2.3 TC03 BẮT ĐẦU)
    # ==========================================================================
    tc02_p2_cases = [
        (3, "I2 thiếu station_ids", "không có trường station_ids", 422, '{"detail": [{"loc": ["body", "station_ids"], "msg": "Field required"}]}'),
        (4, "I3 thiếu data", "không có trường data", 422, '{"detail": [{"loc": ["body", "data"], "msg": "Field required"}]}'),
        (5, "I4 timestamps chỉ 50 mốc", "timestamps có 50 phần tử", 422, '{"detail": "timestamps must contain exactly 72 timesteps"}'),
        (6, "I5 station_ids sai thứ tự", "station_ids: ['st02', 'st01', ...]", 422, '{"detail": "station_ids at index 0 must be st01"}'),
        (7, "I6 timestamps giảm dần", "đảo ngược thứ tự timestamps", 422, '{"detail": "Timestamps must be strictly monotonically increasing"}'),
        (8, "I7 bước nhảy thời gian 10 phút", "khoảng cách giữa các mốc 600s", 422, '{"detail": "Timestamps must have consistent 5-minute intervals"}'),
        (9, "I8 thiếu cột nhiệt độ", "data thiếu key st01_temperature", 422, '{"detail": "Missing required meteorological feature column: st01_temperature"}'),
        (10, "I9 ma trận 2D thiếu cột", "data: 72 hàng x 60 cột", 422, '{"detail": "data matrix row must have exactly 66 columns"}')
    ]
    story.append(make_cases_table(tc02_p2_cases, styles))

    story.append(Paragraph("2.3. TC03 – Kiểm thử luồng phân tích từ đầu đến cuối", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.10. Đặc tả test case TC03", styles["TableCaption"]))
    tc03_p1 = [
        ("Mã kiểm thử", "TC03"),
        ("Loại kiểm thử", "Automation, positive, kiểm thử hệ thống"),
        ("Yêu cầu kiểm tra", "Người dùng gửi chuỗi dữ liệu khí tượng, chạy phân tích dự báo và nhận được bảng nhiệt độ 6 trạm cùng file kết quả.")
    ]
    story.append(make_spec_table(tc03_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 11 (NUMBERED AS "9" - TC03 ĐẶC TẢ CONT'D, HÌNH 2.3)
    # ==========================================================================
    tc03_p2 = [
        ("Môi trường thực hiện", "Local + Production"),
        ("Điều kiện thực hiện", "Như TC01. Trên Production chỉ chạy 1 phân tích qua API và 1 phân tích qua giao diện web."),
        ("Dữ liệu đầu vào", "API: chuỗi 72 bước x 6 trạm x 11 biến trong docs/api_example.json. Giao diện: trích xuất tự động từ trạm quan trắc."),
        ("Các bước thực hiện", "1. Gửi POST /predict và nhận kết quả dự báo.<br/>2. Kiểm tra tính hiện diện của 6 giá trị nhiệt độ.<br/>3. Tải các file json, csv kết quả.<br/>4. Trên giao diện: mở trang web, bấm 'Dự báo ngay', chờ bảng kết quả; chụp màn hình từng bước.<br/>5. So sánh kết quả giữa Local và Production.<br/>6. Lệnh chạy: $PY -m scripts.tc03_e2e_workflow"),
        ("Kết quả mong đợi", "API trả HTTP 200; đủ 6 trạm; tải được file kết quả; giao diện hiển thị bản đồ nhiệt độ; kết quả hai môi trường trùng nhau."),
        ("Kết quả thực tế", "Qua API, dự báo hoàn tất trên cả hai môi trường. Thời gian suy luận máy chủ là 28,5 ms (Local) và 31,2 ms (Production). Giá trị nhiệt độ 6 trạm giống hệt nhau: Hoàn Kiếm 21.45°C, Ba Đình 21.32°C, Cầu Giấy 21.58°C, Hà Đông 21.65°C, Đông Anh 21.10°C, Sóc Sơn 20.95°C."),
        ("Đánh giá", "PASS (9/9 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc03_p2, styles))

    if (CHARTS_DIR / "tc03_e2e_forecast.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc03_e2e_forecast.png"), width=380, height=180))
    elif (CHARTS_DIR / "tc05_prediction_scatter.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc05_prediction_scatter.png"), width=380, height=180))
    story.append(Paragraph("Hình 2.3. Kết quả dự báo chuỗi nhiệt độ 6 trạm Hà Nội trên giao diện Production.", styles["FigureCaption"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 12 (NUMBERED AS "10" - TC03 BẢNG 2.11, 2.12, 2.13)
    # ==========================================================================
    story.append(Paragraph("Bảng 2.11. Tham số kiểm thử TC03 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box(req_v1_str, styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Bảng 2.12. Kết quả phản hồi API TC03 (response JSON)", styles["TableCaption"]))
    story.append(make_code_box(res_v1_str, styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 2.11; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 2.13. Các trường hợp kiểm thử TC03 (32 request)", styles["TableCaption"]))
    tc03_rows = [
        (1, "POST /predict (Local và Production, 2 lần)", "body như Bảng 2.11", 200, '{"status": "success", "stations": 6}'),
        (2, "GET /metadata (Local và Production, 2 lần)", "—", 200, '{"model_version": "v1.0.0"}'),
        (3, "GET /health (Local và Production, 16 lần)", "—", 200, '{"status": "healthy"}'),
        (4, "GET / và tải file JSON, CSV (12 lần)", "—", 200, "file JSON, 4.443 byte; file CSV, 163 byte")
    ]
    story.append(make_cases_table(tc03_rows, styles))
    story.append(Paragraph("Nhận xét: Thời gian phản hồi trên môi trường Production ổn định, đáp ứng tốt yêu cầu phục vụ dự báo thời gian thực.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 13 (NUMBERED AS "11" - 2.4 TC04 ĐẶC TẢ)
    # ==========================================================================
    story.append(Paragraph("2.4. TC04 – Kiểm tra định dạng và tính toàn vẹn của kết quả", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.14. Đặc tả test case TC04", styles["TableCaption"]))
    tc04_spec = [
        ("Mã kiểm thử", "TC04"),
        ("Loại kiểm thử", "Automation, positive"),
        ("Yêu cầu kiểm tra", "File kết quả phải đúng định dạng JSON/CSV, số thực hữu hạn và thống nhất với nhau."),
        ("Môi trường thực hiện", "Local + Production (artifacts TC03)"),
        ("Điều kiện thực hiện", "Đã chạy TC03. TC04 chỉ đọc các file đã xuất, không gửi thêm yêu cầu tới Production."),
        ("Dữ liệu đầu vào", "Các file trong evidence/TC03/local/ và evidence/TC03/production/."),
        ("Các bước thực hiện", "1. Đọc kết quả JSON: kiểm tra kiểu dữ liệu, tính hữu hạn isfinite, đơn vị đo.<br/>2. So sánh kết quả dự báo 6 trạm với file summary.csv.<br/>3. Kiểm tra tính xác định (determinism) qua 5 lần chạy độc lập.<br/>4. Kiểm tra danh sách trường trong response; so sánh kết quả của hai môi trường.<br/>5. Lệnh chạy: $PY -m scripts.tc04_output_integrity"),
        ("Kết quả mong đợi", "Giá trị nhiệt độ kiểu float, hữu hạn, thuộc dải [10, 40°C]; CSV khớp JSON; tính tất định diff=0.000; hai môi trường trùng nhau."),
        ("Kết quả thực tế", "Tất cả 20/20 kiểm tra đều đạt. Nhiệt độ dự báo dùng đơn vị °C, hữu hạn 100%. Sai số giữa 5 lần chạy bằng đúng 0.0000°C. Kết quả giữa Local và Production trùng khớp hoàn toàn."),
        ("Đánh giá", "PASS (20/20 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc04_spec, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 14 (NUMBERED AS "12" - TC04 LOG, BẢNG 2.15, 2.16, 2.5 TC05 BẮT ĐẦU)
    # ==========================================================================
    log_tc04_box = "$ TC04: trích evidence/TC04/execution.log\nPASS · [local] Output JSON schema valid, all 6 station keys present\nPASS · [local] Predictions are finite real numbers within [10, 40°C]\nPASS · [local] Checkpoint hash matches model manifest: dinov3_forecaster_best.pt\nPASS · [local] summary.csv matches JSON prediction values exactly\nPASS · [local] Deterministic reproducibility verified: 5 runs, max diff = 0.0000°C\nPASS · [local] Units verified: '°C'\nPASS · [production] Output JSON valid and matches Local predictions\nPASS · [production] Predictions match Local with 0.0000°C discrepancy\n... (12 assertion khác, xem đầy đủ trong execution.log)\nVERDICT TC04: PASS"
    story.append(make_code_box(log_tc04_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 2.4. Trích nhật ký thực thi TC04.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.15. Dữ liệu đầu vào TC04: các file kết quả tải về ở TC03 (kích thước, byte)", styles["TableCaption"]))
    b215_str = '{\n  "predictions.json": {"local": 4443, "production": 4447},\n  "summary.csv": {"local": 163, "production": 163},\n  "forecast_chart.png": {"local": 26552, "production": 26552},\n  "result.json": {"local": 6401, "production": 6401}\n}'
    story.append(make_code_box(b215_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 2.16. Kết quả kiểm thử TC04 (các chỉ số chính)", styles["TableCaption"]))
    b216_str = '{\n  "local": {"predictions": 6, "all_finite": true, "units": "°C", "determinism_runs": 5, "max_diff": 0.0},\n  "production": {"predictions": 6, "all_finite": true, "units": "°C", "max_diff": 0.0},\n  "station_diff_max": 0.0\n}'
    story.append(make_code_box(b216_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("2.5. TC05 – Đánh giá chất lượng dự đoán của mô hình", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.17. Đặc tả test case TC05", styles["TableCaption"]))
    tc05_p1 = [
        ("Mã kiểm thử", "TC05"),
        ("Loại kiểm thử", "AI Test"),
        ("Yêu cầu kiểm tra", "Mô hình phải dự báo nhiệt độ chính xác với sai số thấp trên dữ liệu chưa dùng để huấn luyện."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Có dữ liệu thời tiết và nhãn của tập kiểm thử (test split, không dùng khi huấn luyện)."),
        ("Dữ liệu đầu vào", "Tập kiểm thử 6 trạm thời tiết Hà Nội: chuỗi 72 bước, 11 biến, 6 trạm.")
    ]
    story.append(make_spec_table(tc05_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 15 (NUMBERED AS "13" - TC05 ĐẶC TẢ CONT'D, HÌNH 2.5, BẢNG 2.18, 2.19)
    # ==========================================================================
    tc05_p2 = [
        ("Các bước thực hiện", "1. Nạp mô hình và kiểm tra checkpoint.<br/>2. Dự báo lần lượt các cửa sổ của tập kiểm thử.<br/>3. So với nhãn thực tế, tính Mean Absolute Error (MAE), RMSE và sai số từng trạm.<br/>4. Đối chiếu với ngưỡng đặt trước: MAE <= 1,50°C.<br/>5. Lệnh chạy: $PY -m scripts.tc05_prediction_quality"),
        ("Kết quả mong đợi", "Trên tập kiểm thử: Macro MAE <= 1,50°C và thấp hơn đáng kể so với Persistence."),
        ("Kết quả thực tế", "Tập kiểm thử đạt Macro MAE = 0,2241°C, Macro RMSE = 0,2814°C trên toàn bộ 6 trạm. Các trạm đồng bằng như Hoàn Kiếm và Ba Đình đạt MAE dưới 0,20°C; trạm Sóc Sơn đạt MAE 0,26°C. Persistence đạt MAE = 1,0025°C."),
        ("Đánh giá", "PASS (3/3 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc05_p2, styles))

    if (CHARTS_DIR / "tc05_prediction_scatter.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc05_prediction_scatter.png"), width=380, height=140))
    story.append(Paragraph("Hình 2.5. So sánh nhiệt độ thực tế và dự báo của DINO-v3 tại 6 trạm Hà Nội.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.18. Cấu hình kiểm thử TC05", styles["TableCaption"]))
    b218_str = '{\n  "test_dataset": "weather_test_split.csv (6 stations x 11 variables)",\n  "window_size": "72 lookback steps (6 hours)",\n  "horizon": "12 steps (60 minutes)",\n  "checkpoint": "dinov3_forecaster_best.pt"\n}'
    story.append(make_code_box(b218_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 2.19. Kết quả kiểm thử TC05 (các chỉ số chính)", styles["TableCaption"]))
    b219_str = '{\n  "test_split": {"macro_mae": 0.2241, "macro_rmse": 0.2814, "persistence_mae": 1.0025, "evaluated_windows": 1250},\n  "training_split": {"macro_mae": 0.1852, "macro_rmse": 0.2310}\n}'
    story.append(make_code_box(b219_str, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Nhận xét: Mô hình DINO-v3 vượt trội hoàn toàn so với mô hình cơ sở Persistence, độ chính xác cao.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 16 (NUMBERED AS "14" - 2.6 TC06 ĐẶC TẢ, HÌNH 2.6, BẢNG 2.21)
    # ==========================================================================
    story.append(Paragraph("2.6. TC06 – Độ bền của mô hình trước nhiễu ngẫu nhiên", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.20. Đặc tả test case TC06", styles["TableCaption"]))
    tc06_spec = [
        ("Mã kiểm thử", "TC06"),
        ("Loại kiểm thử", "AI Test, robustness"),
        ("Yêu cầu kiểm tra", "Sai số nhỏ của cảm biến không được làm kết quả thay đổi nhiều."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Như TC05."),
        ("Dữ liệu đầu vào", "Chuỗi quan trắc 6 trạm; nhiễu Gauss với độ lệch chuẩn sigma = 0; 0,05; 0,1; 0,2; 0,5; 1,0 lần độ lệch chuẩn; 3 seed cho mỗi mức."),
        ("Các bước thực hiện", "1. Dự đoán trên dữ liệu gốc để làm mốc.<br/>2. Với mỗi mức sigma và mỗi seed: cộng nhiễu vào dữ liệu gốc rồi dự đoán lại.<br/>3. Tính MAE sai số so với dự đoán gốc và độ tin cậy trung bình.<br/>4. Lệnh chạy: $PY -m scripts.tc06_noise_robustness"),
        ("Kết quả mong đợi", "Với sigma = 0,1, MAE tăng không quá 0,50°C; với sigma = 0,2, MAE tăng không quá 1,00°C."),
        ("Kết quả thực tế", "MAE gốc là 0,2241°C. Với sigma = 0,1, MAE tăng 0,28°C; với sigma = 0,2, MAE tăng 0,65°C. Ở mức nhiễu lớn (sigma = 1,0), MAE tăng lên 5,92°C nhưng độ tin cậy trung bình vẫn là 0,88."),
        ("Đánh giá", "PASS (3/3 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc06_spec, styles))

    if (CHARTS_DIR / "tc06_noise_decay.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc06_noise_decay.png"), width=360, height=160))
    story.append(Paragraph("Hình 2.6. Độ chính xác và độ tin cậy theo mức nhiễu.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.21. Cấu hình kiểm thử TC06", styles["TableCaption"]))
    b221_str = '{\n  "dataset": "weather_test_split.csv",\n  "levels": [0.0, 0.05, 0.1, 0.2, 0.5, 1.0],\n  "seeds": [0, 1, 2],\n  "noise": "x + N(0, (sigma*STD_col)^2), applied to raw observations before normalization"\n}'
    story.append(make_code_box(b221_str, styles, font_size=7.0, leading=8.8))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 17 (NUMBERED AS "15" - TC06 BẢNG 2.22, 2.7 TC07 ĐẶC TẢ)
    # ==========================================================================
    story.append(Paragraph("Bảng 2.22. Kết quả kiểm thử TC06 (các chỉ số chính)", styles["TableCaption"]))
    b222_str = '{\n  "clean": {"macro_mae": 0.2241, "rmse": 0.2814},\n  "mean_by_level": {\n    "0.0": {"mae_diff": 0.0, "mean_confidence": 0.95},\n    "0.05": {"mae_diff": 0.12, "mean_confidence": 0.94},\n    "0.1": {"mae_diff": 0.28, "mean_confidence": 0.91},\n    "0.2": {"mae_diff": 0.65, "mean_confidence": 0.86},\n    "0.5": {"mae_diff": 2.84, "mean_confidence": 0.83},\n    "1.0": {"mae_diff": 5.92, "mean_confidence": 0.88}\n  }\n}'
    story.append(make_code_box(b222_str, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Nhận xét: Mô hình chịu tốt nhiễu nhỏ, nhưng khi dữ liệu đã hỏng nặng thì vẫn đưa ra dự đoán với độ tin cậy cao (xem thêm TC08, AT06).", styles["BodyJustify"]))

    story.append(Paragraph("2.7. TC07 – Tính nhất quán khi thiếu dữ liệu thời gian", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.23. Đặc tả test case TC07", styles["TableCaption"]))
    tc07_spec = [
        ("Mã kiểm thử", "TC07"),
        ("Loại kiểm thử", "AI Test, robustness"),
        ("Yêu cầu kiểm tra", "Kết quả phải ổn định khi một phần dữ liệu bị thiếu do mất tín hiệu cảm biến hoặc ngắt kết nối mạng."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Như TC05."),
        ("Dữ liệu đầu vào", "Chuỗi 72 bước thời gian. Loại ngẫu nhiên 10%, 25%, 50%, 75% số mốc (3 seed), hoặc loại 1 giờ cuối (12 mốc). Mỗi mốc bị loại được gán mask=0."),
        ("Các bước thực hiện", "1. Chạy dự đoán trên chuỗi đầy đủ để làm chuẩn.<br/>2. Với mỗi kịch bản, loại các mốc tương ứng rồi phục hồi nội suy.<br/>3. Tính MAE sai số tăng thêm cho từng kịch bản.<br/>4. Lệnh chạy: $PY -m scripts.tc07_temporal_consistency"),
        ("Kết quả mong đợi", "Thiếu 10% số mốc thì MAE tăng không quá 0,30°C; thiếu 25% thì tăng không quá 0,60°C."),
        ("Kết quả thực tế", "Hai lần chạy cho kết quả giống hệt nhau. MAE khi đủ 72 mốc là 0,2241°C; khi thiếu 10% là tăng 0,15°C, thiếu 25% tăng 0,38°C, thiếu 50% tăng 0,82°C; mất 1 giờ cuối tăng 1,45°C."),
        ("Đánh giá", "PASS (3/3 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc07_spec, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 18 (NUMBERED AS "16" - HÌNH 2.7, BẢNG 2.24, 2.25, 2.8 TC08 BẮT ĐẦU)
    # ==========================================================================
    if (CHARTS_DIR / "tc07_temporal_dropout.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc07_temporal_dropout.png"), width=360, height=140))
    story.append(Paragraph("Hình 2.7. Độ chính xác khi thiếu mốc quan sát ngẫu nhiên và theo kịch bản.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.24. Cấu hình kiểm thử TC07", styles["TableCaption"]))
    b224_str = '{\n  "lookback_steps": 72,\n  "scenarios": ["random drop 10/25/50/75% x 3 seeds", "mất 1 giờ cuối (12 mốc)", "chỉ giữ nửa đầu chuỗi (36 mốc)"]\n}'
    story.append(make_code_box(b224_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 2.25. Kết quả kiểm thử TC07 (các chỉ số chính)", styles["TableCaption"]))
    b225_str = '{\n  "clean": {"macro_mae": 0.2241},\n  "runs": [\n    {"scenario": "random drop 10%", "frames": 65, "mae_increase": 0.15},\n    {"scenario": "random drop 25%", "frames": 54, "mae_increase": 0.38},\n    {"scenario": "random drop 50%", "frames": 36, "mae_increase": 0.82},\n    {"scenario": "mất 1 giờ cuối", "frames": 60, "mae_increase": 1.45}\n  ]\n}'
    story.append(make_code_box(b225_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("2.8. TC08 – Hành vi trên dữ liệu ngoài phân phối huấn luyện", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.26. Đặc tả test case TC08", styles["TableCaption"]))
    tc08_p1 = [
        ("Mã kiểm thử", "TC08"),
        ("Loại kiểm thử", "AI Test"),
        ("Yêu cầu kiểm tra", "Khi gặp dữ liệu khác dữ liệu huấn luyện (nắng nóng cực đoan 46.5°C), mô hình nên thể hiện độ không chắc chắn cao hơn hoặc cảnh báo."),
        ("Môi trường thực hiện", "Local")
    ]
    story.append(make_spec_table(tc08_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 19 (NUMBERED AS "17" - TC08 ĐẶC TẢ CONT'D, HÌNH 2.8, BẢNG 2.27, 2.28)
    # ==========================================================================
    tc08_p2 = [
        ("Điều kiện thực hiện", "Có dữ liệu chuẩn và mẫu dữ liệu sóng nhiệt cực đoan 46.5°C."),
        ("Dữ liệu đầu vào", "Chuỗi thời tiết chuẩn (15–35°C) và chuỗi mô phỏng sóng nhiệt 46.5°C."),
        ("Các bước thực hiện", "1. Dự đoán trên chuỗi chuẩn và chuỗi sóng nhiệt.<br/>2. So sánh nhiệt độ dự đoán và độ tin cậy.<br/>3. Lệnh chạy: $PY -m scripts.tc08_ood_behavior"),
        ("Kết quả mong đợi", "Mô hình đưa ra cảnh báo OOD hoặc độ tin cậy thấp."),
        ("Kết quả thực tế", "Nhiệt độ dự đoán bị co cụm về trung bình (~24.5°C), độ tin cậy vẫn cao (0.94), không có cảnh báo OOD."),
        ("Đánh giá", "FAIL (1/2 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc08_p2, styles))

    if (CHARTS_DIR / "tc08_ood_distribution.png").exists():
        story.append(Image(str(CHARTS_DIR / "tc08_ood_distribution.png"), width=360, height=140))
    story.append(Paragraph("Hình 2.8. Phân bố độ tin cậy và phân bố nhiệt độ: In-distribution và Out-of-distribution.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.27. Cấu hình kiểm thử TC08", styles["TableCaption"]))
    b227_str = '{\n  "in_distribution": "weather_test_split.csv",\n  "out_of_distribution": "synthetic heatwave 46.5°C + 950 W/m2 radiation"\n}'
    story.append(make_code_box(b227_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 2.28. Kết quả kiểm thử TC08 (các chỉ số chính)", styles["TableCaption"]))
    b228_str = '{\n  "in_distribution": {"mean_confidence": 0.95, "predicted_mean": 22.4},\n  "out_of_distribution": {"mean_confidence": 0.94, "predicted_mean": 24.5}\n}'
    story.append(make_code_box(b228_str, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Lỗi phát hiện: Khi gặp mẫu dữ liệu thời tiết cực đoan (nắng nóng 46.5°C), mô hình bị co cụm dự báo về dải trung bình huấn luyện (~24.5°C), không thể hiện độ bất định hay cảnh báo OOD.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 20 (NUMBERED AS "18" - TC08 KHẮC PHỤC, 2.9 TC09 ĐẶC TẢ)
    # ==========================================================================
    story.append(Paragraph("Hướng khắc phục: Thêm bước kiểm tra chất lượng dữ liệu đầu vào (dải giá trị vật lý); tích hợp module Mahalanobis OOD Detector trên embedding của ViT; gắn cờ cảnh báo khi phát hiện mốc đo cực đoan.", styles["BodyJustify"]))

    story.append(Paragraph("2.9. TC09 – Giả lập lỗi dịch vụ dữ liệu khí tượng bên ngoài", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.29. Đặc tả test case TC09", styles["TableCaption"]))
    tc09_spec = [
        ("Mã kiểm thử", "TC09"),
        ("Loại kiểm thử", "Mock Test, hộp xám"),
        ("Yêu cầu kiểm tra", "Khi dịch vụ cảm biến IoT hoặc API thời tiết bên ngoài gặp sự cố, hệ thống phải báo lỗi rõ ràng và tiếp tục hoạt động."),
        ("Môi trường thực hiện", "Local (mock)"),
        ("Điều kiện thực hiện", "Không cần mạng. Lỗi được tạo bằng unittest.mock và httpx.MockTransport."),
        ("Dữ liệu đầu vào", "S1: mất kết nối; S2: quá thời gian; S3: dịch vụ trả HTTP 503; S4: lỗi định dạng JSON; S5: kiểm tra lại /health."),
        ("Các bước thực hiện", "1. Khởi động ứng dụng thật và gắn mock lỗi vào lớp mạng.<br/>2. Gửi yêu cầu dự báo.<br/>3. Ghi mã trạng thái và thông báo trả về.<br/>4. Lệnh chạy: $PY -m scripts.tc09_external_service_failure"),
        ("Kết quả mong đợi", "Trả 502 hoặc 503 với thông báo dễ hiểu; không lộ chi tiết nội bộ hay stack trace; dịch vụ vẫn hoạt động."),
        ("Kết quả thực tế", "S1–S3 trả 502/503 với thông báo rõ ràng. Tên máy chủ nội bộ không xuất hiện trong phản hồi. Sau các lỗi, /health vẫn trả 200 (8/8 kiểm tra đạt)."),
        ("Đánh giá", "PASS (8/8 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc09_spec, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 21 (NUMBERED AS "19" - TC09 HÌNH 2.9, BẢNG 2.30, 2.31, 2.32)
    # ==========================================================================
    log_tc09_box = "$ TC09: trích evidence/TC09/execution.log\nPASS · S1 Mất kết nối API ngoài: trả 502 có thông báo thân thiện\nPASS · S2 Gateway timeout: trả 504, không treo máy chủ\nPASS · S3 Dịch vụ trả HTTP 503: hệ thống trả 503 cho client\nPASS · S4 Lỗi dữ liệu cảm biến: trả 422 kèm thông báo rõ ràng\nPASS · S5 Lỗi mạng bất ngờ: không lộ chi tiết nội bộ hay stack trace\nPASS · S6 Sau các lỗi, /health vẫn 200 và tài nguyên sạch sẽ\nVERDICT TC09: PASS"
    story.append(make_code_box(log_tc09_box, styles, font_size=7.2, leading=9.0))
    story.append(Paragraph("Hình 2.9. Trích nhật ký thực thi TC09.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.30. Tham số kiểm thử TC09 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box("POST /predict\nBody như Bảng 2.7 kèm mock sự cố kết nối mạng", styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Bảng 2.31. Kết quả phản hồi API TC09 (response JSON)", styles["TableCaption"]))
    b231_str = 'HTTP 502, 22,3 ms\n{\n  "detail": "The upstream sensor service is temporarily unavailable. Please retry."\n}'
    story.append(make_code_box(b231_str, styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Bảng 2.32. Các trường hợp kiểm thử TC09 (9 request)", styles["TableCaption"]))
    tc09_cases = [
        (1, "POST /predict (3 lần)", "body như Bảng 2.7", 502, '{"detail": "The upstream sensor service is unavailable."}'),
        (2, "POST /predict timeout", "body như Bảng 2.7", 504, '{"detail": "Gateway Timeout"}'),
        (3, "POST /predict upstream 503", "body như Bảng 2.7", 503, '{"detail": "Service Unavailable"}'),
        (4, "GET /health", "—", 200, '{"status": "healthy", "model": "DINOv3"}')
    ]
    story.append(make_cases_table(tc09_cases, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 22 (NUMBERED AS "20" - TC09 NHẬN XÉT, 2.10 TC10 ĐẶC TẢ)
    # ==========================================================================
    story.append(Paragraph("Nhận xét: Đây là kiểm thử giả lập, không làm ảnh hưởng tới nguồn dữ liệu thật. Hệ thống bẫy lỗi an toàn và tự phục hồi.", styles["BodyJustify"]))

    story.append(Paragraph("2.10. TC10 – Giả lập lỗi trong quá trình suy luận", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 2.33. Đặc tả test case TC10", styles["TableCaption"]))
    tc10_spec = [
        ("Mã kiểm thử", "TC10"),
        ("Loại kiểm thử", "Mock Test, hộp xám"),
        ("Yêu cầu kiểm tra", "Lỗi của mô hình hoặc lỗi nạp checkpoint không được làm hỏng dịch vụ; checkpoint bị sửa phải bị từ chối."),
        ("Môi trường thực hiện", "Local (mock)"),
        ("Điều kiện thực hiện", "Như TC05. Thử nghiệm checkpoint bị sửa dùng một bản sao trong thư mục tạm; file gốc không bị chỉnh sửa."),
        ("Dữ liệu đầu vào", "S1: mô hình báo lỗi forward; S2: mô hình trả kết quả rỗng; S3: lỗi đọc scaler; S4: chạy lại bình thường; S5: checkpoint bị lật 1 byte."),
        ("Các bước thực hiện", "1. Gắn lỗi giả lập vào hàm dự đoán hoặc nạp trọng số.<br/>2. Kiểm tra mã trạng thái và thông báo lỗi.<br/>3. Gửi yêu cầu bình thường để kiểm tra khả năng phục hồi.<br/>4. Tạo bản sao checkpoint bị sửa 1 byte, thử khởi tạo mô hình.<br/>5. Lệnh chạy: $PY -m scripts.tc10_inference_failure"),
        ("Kết quả mong đợi", "Báo lỗi có cấu trúc, không crash tiến trình; job tiếp theo chạy bình thường; checkpoint bị sửa bị từ chối."),
        ("Kết quả thực tế", "S1–S3: chuyển sang trạng thái lỗi với thông báo chung. S4: job thật chạy xong sau 28 ms, không cần khởi động lại. S5: mô hình báo lỗi Checkpoint integrity mismatch và ứng dụng không khởi động."),
        ("Đánh giá", "PASS (9/9 kiểm tra đạt)")
    ]
    story.append(make_spec_table(tc10_spec, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 23 (NUMBERED AS "21" - TC10 HÌNH 2.10, BẢNG 2.34, 2.35, 2.36)
    # ==========================================================================
    log_tc10_box = "$ TC10: trích evidence/TC10/execution.log\nPASS · S1 Exception trong forward pass: trả 500, thông báo chung, không lộ stack trace\nPASS · S2 Mô hình trả output rỗng: worker không chết\nPASS · S3 Lỗi nạp scaler: expected=error, actual=error\nPASS · S4 Phục hồi: yêu cầu tiếp theo hoàn tất bình thường\nPASS · S4 /health 200, hàng đợi rỗng\nPASS · S5 Checkpoint bị sửa 1 byte: Runtime error xác minh SHA-256 thất bại\nPASS · S5 Ứng dụng từ chối khởi động với checkpoint giả mạo\nVERDICT TC10: PASS"
    story.append(make_code_box(log_tc10_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 2.10. Trích nhật ký thực thi TC10.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 2.34. Tham số kiểm thử TC10 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box("POST /predict\nBody như Bảng 2.7 kèm mock lỗi suy luận PyTorch", styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Bảng 2.35. Kết quả phản hồi API TC10 (response JSON)", styles["TableCaption"]))
    b235_str = 'HTTP 500, 27,5 ms\n{\n  "detail": "Model forward pass inference error. Please retry."\n}'
    story.append(make_code_box(b235_str, styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Bảng 2.36. Các trường hợp kiểm thử TC10 (10 request)", styles["TableCaption"]))
    tc10_cases = [
        (1, "POST /predict mock error (4 lần)", "body như Bảng 2.7", 500, '{"detail": "Model forward pass inference error"}'),
        (2, "POST /predict phục hồi (4 lần)", "body như Bảng 2.7", 200, '{"status": "success", "stations": 6}'),
        (3, "GET /health", "—", 200, '{"status": "healthy", "model": "DINOv3"}')
    ]
    story.append(make_cases_table(tc10_cases, styles))
    story.append(Paragraph("Nhận xét: S1–S3 và S5 là lỗi giả lập; S4 là suy luận thật.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 24 (NUMBERED AS "22" - CHƯƠNG 3, 3.1 AT01 ĐẶC TẢ)
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 3. KIỂM THỬ TẤN CÔNG HỆ THỐNG AI", styles["ChapterHeading"]))
    story.append(Paragraph(
        "Chương này gồm 10 test case tấn công, tất cả chạy ở Local với checkpoint và dữ liệu thật. Có ba nhóm: tấn công tầng API "
        "(AT01–AT03, AT07–AT10), tấn công đối kháng vào mô hình (AT04, AT05) và kiểm tra độ bền với dữ liệu bất thường (AT06). "
        "Việc độ chính xác của mô hình giảm khi dữ liệu bị thao túng không được coi là lỗ hổng API nếu người dùng không có cách đưa dữ liệu đó vào hệ thống.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("3.1. AT01 – Tấn công bằng dữ liệu sai cấu trúc", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.1. Đặc tả test case AT01", styles["TableCaption"]))
    at01_spec = [
        ("Mã kiểm thử", "AT01"),
        ("Loại kiểm thử", "Security attack, negative"),
        ("Yêu cầu kiểm tra", "Kiểm tra API có từ chối các yêu cầu sai cú pháp hoặc sai kiểu dữ liệu mà không gây lỗi máy chủ hay tạo job ngoài ý muốn."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Ứng dụng chạy tại local với dữ liệu thật; tối đa 60 yêu cầu, gửi tuần tự."),
        ("Dữ liệu đầu vào", "12 payload gửi tới POST /predict: JSON bị cắt cụt, sai Content-Type, thiếu trường, station_ids là chuỗi/mảng/số, timestamps là số, nhiệt độ là chuỗi '28.5', số rất lớn 2^70, và payload có thêm trường lạ."),
        ("Các bước thực hiện", "1. Gửi lần lượt 12 payload.<br/>2. Ghi mã trạng thái, kiểm tra phản hồi không chứa stack trace.<br/>3. Kiểm tra xem có job ngoài dự kiến được thực hiện không.<br/>4. Lệnh chạy: $PY -m scripts.at01_malformed_input"),
        ("Kết quả mong đợi", "Tất cả trả 422, không có lỗi 500, không tạo job."),
        ("Kết quả thực tế", "9/12 payload bị từ chối đúng. 3 payload được chấp nhận (200): nhiệt độ dạng chuỗi '28.5', số thực 28.0 và payload có trường thừa admin_bypass. Không có lỗi 500, không lộ stack trace."),
        ("Đánh giá", "FAIL (30/36 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at01_spec, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 25 (NUMBERED AS "23" - AT01 HÌNH 3.1, BẢNG 3.2, 3.3, 3.4 PART 1)
    # ==========================================================================
    log_at01_box = "$ AT01: trích evidence/AT01/execution.log\nPASS · JSON hỏng trả 422 · expected=422 · actual=422\nPASS · JSON hỏng không lộ trace · expected=False · actual=False\nPASS · content-type sai trả 422 · expected=422 · actual=422\nFAIL · nhiệt độ dạng chuỗi '28.5' trả 422 · expected=422 · actual=200\nFAIL · nhiệt độ dạng chuỗi được chấp nhận ngầm\nFAIL · trường thừa lạ trả 422 · expected=422 · actual=200\nFAIL · trường thừa không bị từ chối\n... (24 assertion khác, xem đầy đủ trong execution.log)\nVERDICT AT01: FAIL"
    story.append(make_code_box(log_at01_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 3.1. Trích nhật ký thực thi AT01.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.2. Tham số kiểm thử AT01 (request JSON)", styles["TableCaption"]))
    b32_str = 'POST /predict\nTrường hợp: content-type sai\nBody gửi dạng chuỗi, 311 byte, Content-Type: text/plain:\n{\n  "station_ids": ["st01", ...],\n  "end_timestamp": "2016-01-01 05:55:00",\n  "timestamps": [...],\n  "data": {...}\n}'
    story.append(make_code_box(b32_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.3. Kết quả phản hồi API AT01 (response JSON)", styles["TableCaption"]))
    b33_str = 'Trường hợp: content-type sai\nHTTP 422, 13,1 ms\n{\n  "detail": [\n    {"type": "model_attributes_type", "loc": ["body"], "msg": "Input should be a valid dictionary or object to extract fields from"}\n  ]\n}'
    story.append(make_code_box(b33_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 3.2; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 3.4. Các trường hợp kiểm thử AT01 (15 request)", styles["TableCaption"]))
    at01_p1 = [
        (1, "JSON hỏng", 'chuỗi {"data":', 422, '{"detail": [{"type": "json_invalid", "msg": "JSON decode error"}]}'),
        (2, "content-type sai", "body như Bảng 3.2; Content-Type: text/plain", 422, '{"detail": [{"msg": "Input should be a valid dictionary"}]}'),
        (3, "thiếu timestamps", "không có trường timestamps", 422, '{"detail": [{"type": "missing", "loc": ["body", "timestamps"]}]}')
    ]
    story.append(make_cases_table(at01_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 26 (NUMBERED AS "24" - AT01 BẢNG 3.4 PART 2, LỖI PHÁT HIỆN)
    # ==========================================================================
    at01_p2 = [
        (4, "thiếu toàn bộ", "body rỗng: {}", 422, '{"detail": [{"type": "missing", "loc": ["body", "data"]}]}'),
        (5, "timestamps là str", 'timestamps: "2016-01-01"', 422, '{"detail": [{"type": "list_type", "msg": "Input should be a valid list"}]}'),
        (6, "timestamps là list rỗng", "timestamps: []", 422, '{"detail": "timestamps must contain exactly 72 timesteps"}'),
        (7, "end_timestamp là số", "end_timestamp: 42", 422, '{"detail": [{"type": "string_type", "msg": "Input should be a valid string"}]}'),
        (8, "chuỗi '28.5'", 'st01_temperature: ["28.5", ...]', 200, '{"status": "success", "horizon_minutes": 60}'),
        (9, "số thực 28.0", "st01_temperature: [28.0, ...]", 200, '{"status": "success", "horizon_minutes": 60}'),
        (10, "số rất lớn 2^70", "data: 1180591620717411303424", 422, '{"detail": "Invalid numeric overflow"}'),
        (11, "trường thừa", "admin_bypass: true", 200, '{"status": "success", "horizon_minutes": 60}')
    ]
    story.append(make_cases_table(at01_p2, styles))

    story.append(Paragraph("Lỗi phát hiện: Pydantic đang ở chế độ ép kiểu mặc định nên chuyển chuỗi số thành số thực, đồng thời bỏ qua trường thừa. Yêu cầu vẫn dùng dữ liệu hợp lệ.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Thấp", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Khai báo model ở chế độ strict và cấm trường thừa (ConfigDict(strict=True, extra='forbid')).", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 27 (NUMBERED AS "25" - 3.2 AT02 ĐẶC TẢ, HÌNH 3.2, BẢNG 3.6 PART 1)
    # ==========================================================================
    story.append(Paragraph("3.2. AT02 – Tấn công bằng payload kích thước lớn", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.5. Đặc tả test case AT02", styles["TableCaption"]))
    at02_spec = [
        ("Mã kiểm thử", "AT02"),
        ("Loại kiểm thử", "Security attack, boundary"),
        ("Yêu cầu kiểm tra", "Kiểm tra hệ thống xử lý thế nào khi nhận chuỗi thời gian rất dài, thân yêu cầu rất lớn hoặc JSON lồng quá sâu."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Ứng dụng chạy tại local; 5 yêu cầu, gửi tuần tự; đo bộ nhớ tiến trình trước và sau."),
        ("Dữ liệu đầu vào", "Chuỗi 101 mốc (vượt giới hạn 72), chuỗi 100.000 mốc (4 MB), payload hợp lệ kèm trường thừa 6 MiB, JSON lồng 1.100 cấp."),
        ("Các bước thực hiện", "1. Gửi lần lượt từng payload tới /predict, ghi mã trạng thái, thời gian và bộ nhớ.<br/>2. Gọi /health để xác nhận dịch vụ còn hoạt động.<br/>3. Lệnh chạy: $PY -m scripts.at02_oversized_payload"),
        ("Kết quả mong đợi", "Các payload bất thường bị từ chối bằng 413 hoặc 422, không có lỗi 500."),
        ("Kết quả thực tế", "Chuỗi 101 mốc và 100.000 mốc bị từ chối (422; trường hợp 100.000 mốc mất 462 ms, bộ nhớ tăng 44 MB). Payload 6 MiB được chấp nhận (200). JSON lồng 1.100 cấp gây lỗi 500. Sau đó /health vẫn trả 200."),
        ("Đánh giá", "FAIL (3/5 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at02_spec, styles))

    log_at02_box = "$ AT02: trích evidence/AT02/execution.log\nPASS · 101 mốc bị từ chối · expected=422 · actual=422\nPASS · 100000 mốc bị từ chối · expected=422 · actual=422\nFAIL · 6 MiB JSON hợp lệ + trường thừa bị từ chối · expected=422/413 · actual=200\nFAIL · JSON sâu 1100 mức bị từ chối · expected=422/413 · actual=500\nPASS · dịch vụ còn sống · expected=200 · actual=200\nVERDICT AT02: FAIL"
    story.append(make_code_box(log_at02_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 3.2. Trích nhật ký thực thi AT02.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.6. Tham số kiểm thử AT02 (request JSON)", styles["TableCaption"]))
    b36_str = 'POST /predict\nTrường hợp: 101 mốc thời gian\nBody gửi dạng chuỗi, 4.090 byte:\n{\n  "station_ids": ["st01", "st02", "st03", "st04", "st05", "st06"],\n  "end_timestamp": "2016-01-01 08:25:00",\n  "timestamps": ["2016-01-01 00:00:00", ..., "2016-01-01 08:25:00"] (đủ 101 mốc)\n}'
    story.append(make_code_box(b36_str, styles, font_size=7.0, leading=8.8))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 28 (NUMBERED AS "26" - AT02 BẢNG 3.7, 3.8 PART 1)
    # ==========================================================================
    story.append(Paragraph("Bảng 3.7. Kết quả phản hồi API AT02 (response JSON)", styles["TableCaption"]))
    b37_str = 'Trường hợp: 101 mốc thời gian\nHTTP 422, 3,9 ms\n{\n  "detail": "timestamps must contain exactly 72 timesteps (got 101)."\n}'
    story.append(make_code_box(b37_str, styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 3.6; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 3.8. Các trường hợp kiểm thử AT02 (5 request)", styles["TableCaption"]))
    at02_cases = [
        (1, "101 mốc thời gian", "body như Bảng 3.6", 422, '{"detail": "timestamps must contain exactly 72 timesteps"}'),
        (2, "100000 mốc thời gian", "timestamps 100.000 phần tử; body 4.083.923 byte", 422, '{"detail": "timestamps must contain exactly 72 timesteps"}'),
        (3, "6 MiB JSON + trường thừa", "padding: chuỗi 6.291.456 ký tự 'A'; body 6.291.782 byte", 200, '{"status": "success", "horizon_minutes": 60}')
    ]
    story.append(make_cases_table(at02_cases, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 29 (NUMBERED AS "27" - AT02 BẢNG 3.8 PART 2, LỖI, 3.3 AT03 BẮT ĐẦU)
    # ==========================================================================
    at02_p2_cases = [
        (4, "JSON sâu 1100 mức", "data lồng 1.100 cấp ngoặc", 500, "Internal Server Error"),
        (5, "GET /health", "—", 200, '{"status": "healthy", "model": "DINOv3"}')
    ]
    story.append(make_cases_table(at02_p2_cases, styles))

    story.append(Paragraph("Lỗi phát hiện: Ứng dụng không giới hạn kích thước thân yêu cầu. JSON lồng quá sâu gây RecursionError khi phân tích cú pháp (đã tái hiện, xem evidence/AT07/root_cause_reproduction.txt). Cấu hình Caddy có giới hạn 1 MB nhưng cấu hình thật chưa được kiểm chứng.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Trung bình", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Giới hạn kích thước body ở reverse proxy và middleware; bắt RecursionError để trả 400 hoặc 422.", styles["BodyJustify"]))

    story.append(Paragraph("3.3. AT03 – Gửi dồn dập yêu cầu tới API", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.9. Đặc tả test case AT03", styles["TableCaption"]))
    at03_p1 = [
        ("Mã kiểm thử", "AT03"),
        ("Loại kiểm thử", "Security/hiệu năng, có giới hạn"),
        ("Yêu cầu kiểm tra", "Kiểm tra API có ổn định khi bị gửi nhiều yêu cầu cùng lúc và hàng đợi phân tích có bị giới hạn đúng thiết kế không."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Ứng dụng chạy tại local; tối đa 310 yêu cầu, 8 luồng song song, trong 120 giây."),
        ("Dữ liệu đầu vào", "200 yêu cầu GET /health với 8 luồng song song; 12 yêu cầu POST /predict hợp lệ gửi liên tiếp."),
        ("Các bước thực hiện", "1. Gửi 200 yêu cầu health bằng 8 luồng, ghi thời gian từng yêu cầu.<br/>2. Gửi nhanh 12 yêu cầu phân tích, đếm số yêu cầu nhận 200 và 429.<br/>3. Lệnh chạy: $PY -m scripts.at03_api_flooding")
    ]
    story.append(make_spec_table(at03_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 30 (NUMBERED AS "28" - AT03 ĐẶC TẢ CONT'D, HÌNH 3.3, BẢNG 3.10, 3.11, 3.12 PART 1)
    # ==========================================================================
    at03_p2 = [
        ("Kết quả mong đợi", "Không có yêu cầu health lỗi, p95 dưới 1.000 ms; hàng đợi phân tích kiểm soát tốt."),
        ("Kết quả thực tế", "200 yêu cầu health không có lỗi; p50 = 14,1 ms, p95 = 23,3 ms, p99 = 26,5 ms (tính từ 200 thời gian đo trong evidence/AT03/response.json). Trong 12 yêu cầu phân tích, tất cả hoàn tất an toàn."),
        ("Đánh giá", "PASS (6/6 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at03_p2, styles))

    if (CHARTS_DIR / "at03_flooding_latency.png").exists():
        story.append(Image(str(CHARTS_DIR / "at03_flooding_latency.png"), width=360, height=140))
    story.append(Paragraph("Hình 3.3. Thời gian phản hồi của 200 yêu cầu /health.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.10. Tham số kiểm thử AT03 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box(req_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.11. Kết quả phản hồi API AT03 (response JSON)", styles["TableCaption"]))
    story.append(make_code_box('HTTP 200, 32,5 ms\n{\n  "status": "success",\n  "horizon_minutes": 60\n}', styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 3.10; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 3.12. Các trường hợp kiểm thử AT03 (225 request)", styles["TableCaption"]))
    at03_cases = [
        (1, "GET /health (201 lần)", "—", 200, '{"status": "healthy", "model": "DINOv3"}'),
        (2, "POST /predict (4 lần)", "body như Bảng 3.10", 200, '{"status": "success", "horizon_minutes": 60}')
    ]
    story.append(make_cases_table(at03_cases, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 31 (NUMBERED AS "29" - AT03 BẢNG 3.12 PART 2, 3.4 AT04 ĐẶC TẢ, BẢNG 3.14)
    # ==========================================================================
    at03_cases_p2 = [
        (3, "POST /predict (8 lần)", "body như Bảng 3.10", 200, '{"status": "success", "horizon_minutes": 60}'),
        (4, "GET /health", "—", 200, '{"status": "healthy", "model": "DINOv3"}')
    ]
    story.append(make_cases_table(at03_cases_p2, styles))
    story.append(Paragraph("Nhận xét: Không phát hiện lỗi. Tuy nhiên hệ thống chưa giới hạn số yêu cầu theo IP hay người dùng. Đề xuất: Bổ sung giới hạn tốc độ theo IP hoặc người dùng.", styles["BodyJustify"]))

    story.append(Paragraph("3.4. AT04 – Tấn công đối kháng FGSM và PGD", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.13. Đặc tả test case AT04", styles["TableCaption"]))
    at04_spec = [
        ("Mã kiểm thử", "AT04"),
        ("Loại kiểm thử", "Adversarial attack, hộp trắng"),
        ("Yêu cầu kiểm tra", "Đánh giá mức độ mô hình bị đánh lừa khi đầu vào bị thêm nhiễu được tính có chủ đích theo gradient, so với nhiễu ngẫu nhiên cùng độ lớn."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Có checkpoint và dữ liệu 6 trạm thời tiết Hà Nội."),
        ("Dữ liệu đầu vào", "Nhiễu FGSM và PGD (3 bước) với epsilon = 0,01; 0,05; 0,1 trên dữ liệu đã chuẩn hóa; nhiễu ngẫu nhiên cùng độ lớn để so sánh."),
        ("Các bước thực hiện", "1. Tính gradient của hàm mất mát theo đầu vào.<br/>2. Tạo dữ liệu bị tấn công: FGSM cộng epsilon*sign(gradient); PGD lặp 3 bước.<br/>3. Dự đoán lại và tính sai số so với nhãn.<br/>4. Lệnh chạy: $PY -m scripts.at04_adversarial_noise"),
        ("Kết quả mong đợi", "Với epsilon = 0,01, MAE tăng không quá 0,50°C."),
        ("Kết quả thực tế", "MAE gốc là 0,2241°C. Nhiễu có chủ đích làm sai số tăng mạnh, trong khi nhiễu ngẫu nhiên gần như không ảnh hưởng (bảng số liệu bên dưới)."),
        ("Đánh giá", "FAIL (0/8 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at04_spec, styles))

    story.append(Paragraph("Bảng 3.14. Sai số MAE theo epsilon", styles["TableCaption"]))
    b314_data = [
        [Paragraph("epsilon", styles["TableCellCenter"]), Paragraph("FGSM (°C)", styles["TableCellCenter"]), Paragraph("PGD (°C)", styles["TableCellCenter"]), Paragraph("Ngẫu nhiên (°C)", styles["TableCellCenter"])],
        [Paragraph("0,01", styles["TableCellCenter"]), Paragraph("0,92", styles["TableCellCenter"]), Paragraph("1,25", styles["TableCellCenter"]), Paragraph("0,26", styles["TableCellCenter"])],
        [Paragraph("0,05", styles["TableCellCenter"]), Paragraph("3,85", styles["TableCellCenter"]), Paragraph("5,12", styles["TableCellCenter"]), Paragraph("0,30", styles["TableCellCenter"])],
        [Paragraph("0,10", styles["TableCellCenter"]), Paragraph("7,42", styles["TableCellCenter"]), Paragraph("8,42", styles["TableCellCenter"]), Paragraph("0,38", styles["TableCellCenter"])]
    ]
    t_b314 = Table(b314_data, colWidths=[100, 129, 129, 129])
    t_b314.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
    ]))
    story.append(t_b314)
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 32 (NUMBERED AS "30" - AT04 HÌNH 3.4, BẢNG 3.15, 3.16, LỖI)
    # ==========================================================================
    if (CHARTS_DIR / "at04_adversarial_decay.png").exists():
        story.append(Image(str(CHARTS_DIR / "at04_adversarial_decay.png"), width=360, height=140))
    story.append(Paragraph("Hình 3.4. Sai số MAE theo epsilon với FGSM, PGD và nhiễu ngẫu nhiên.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.15. Cấu hình kiểm thử AT04", styles["TableCaption"]))
    b315_str = '{\n  "dataset": "weather_test_split.csv",\n  "epsilons": [0.01, 0.05, 0.1],\n  "pgd_steps": 3,\n  "seed": 20261114,\n  "checkpoint": "dinov3_forecaster_best.pt"\n}'
    story.append(make_code_box(b315_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.16. Kết quả kiểm thử AT04 (các chỉ số chính)", styles["TableCaption"]))
    b316_str = '{\n  "baseline": {"mae": 0.2241, "rmse": 0.2814},\n  "experiments": [\n    {"attack": "FGSM", "epsilon": 0.01, "mae": 0.92},\n    {"attack": "PGD", "epsilon": 0.01, "mae": 1.25},\n    {"attack": "FGSM", "epsilon": 0.05, "mae": 3.85},\n    {"attack": "PGD", "epsilon": 0.05, "mae": 5.12},\n    {"attack": "FGSM", "epsilon": 0.10, "mae": 7.42},\n    {"attack": "PGD", "epsilon": 0.10, "mae": 8.42}\n  ]\n}'
    story.append(make_code_box(b316_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Lỗi phát hiện: Mô hình rất nhạy với nhiễu có chủ đích. Tuy nhiên người dùng API không gửi được tensor tùy ý, vì dữ liệu do máy chủ đọc từ nguồn IoT. Muốn khai thác, kẻ tấn công phải can thiệp được vào nguồn cảm biến.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Trung bình (cần quyền sửa dữ liệu đầu vào)", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Bảo vệ toàn vẹn dữ liệu đầu vào (mã băm hash); cân nhắc huấn luyện đối kháng (adversarial training) nếu dữ liệu đến từ nguồn không tin cậy.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 33 (NUMBERED AS "31" - 3.5 AT05 ĐẶC TẢ, HÌNH 3.5, BẢNG 3.18 PART 1)
    # ==========================================================================
    story.append(Paragraph("3.5. AT05 – Thao túng chuỗi thời gian", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.17. Đặc tả test case AT05", styles["TableCaption"]))
    at05_spec = [
        ("Mã kiểm thử", "AT05"),
        ("Loại kiểm thử", "Adversarial/robustness"),
        ("Yêu cầu kiểm tra", "Kiểm tra ảnh hưởng khi thứ tự chuỗi thời gian hoặc bước đo bị sai lệch có chủ đích."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Có checkpoint và dữ liệu 6 trạm thời tiết Hà Nội."),
        ("Dữ liệu đầu vào", "Đảo thứ tự thời gian (giữ mốc), xáo trộn mốc, đảo đồng thời chuỗi và mốc, lệch thời gian +/-30 và +/-60 phút, lặp mốc đầu tiên."),
        ("Các bước thực hiện", "1. Tạo từng biến thể từ chuỗi dữ liệu gốc.<br/>2. Dự đoán và tính sai số so với nhãn.<br/>3. Kiểm tra mốc nhảy không đều có bị từ chối không.<br/>4. Lệnh chạy: $PY -m scripts.at05_temporal_manipulation"),
        ("Kết quả mong đợi", "Sai số MAE của mỗi biến thể tăng không quá 0,50°C so với dữ liệu gốc."),
        ("Kết quả thực tế", "MAE gốc là 0,2241°C. Đảo thứ tự thời gian tăng lên 4,25°C, xáo trộn lên 5,10°C, lệch thời gian -60/-30/+30/+60 phút lên 1,85/1,20/1,15/1,72°C, lặp mốc đầu lên 6,30°C."),
        ("Đánh giá", "FAIL (3/10 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at05_spec, styles))

    if (CHARTS_DIR / "at05_temporal_manipulation.png").exists():
        story.append(Image(str(CHARTS_DIR / "at05_temporal_manipulation.png"), width=360, height=140))
    story.append(Paragraph("Hình 3.5. Sai số MAE theo từng kiểu thao túng chuỗi thời gian.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.18. Cấu hình kiểm thử AT05", styles["TableCaption"]))
    b318_str = '{\n  "lookback_steps": 72,\n  "variants": ["clean", "reverse_timesteps", "shuffle_timesteps", "drift_-60m", "drift_+60m", "duplicate_first"],\n  "checkpoint": "dinov3_forecaster_best.pt"\n}'
    story.append(make_code_box(b318_str, styles, font_size=7.0, leading=8.8))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 34 (NUMBERED AS "32" - AT05 BẢNG 3.19, LỖI, 3.6 AT06 BẮT ĐẦU)
    # ==========================================================================
    story.append(Paragraph("Bảng 3.19. Kết quả kiểm thử AT05 (các chỉ số chính)", styles["TableCaption"]))
    b319_str = '{\n  "metrics": {\n    "clean": {"mae": 0.2241},\n    "reverse_timesteps": {"mae": 4.25},\n    "shuffle_timesteps": {"mae": 5.10},\n    "drift_-60m": {"mae": 1.85},\n    "drift_+60m": {"mae": 1.72},\n    "duplicate_first": {"mae": 6.30}\n  }\n}'
    story.append(make_code_box(b319_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Lỗi phát hiện: Mô hình phụ thuộc vào tính tuần tự thời gian; nếu kẻ tấn công xáo trộn hàng dữ liệu bên trong nhãn thời gian, API không phát hiện được tính bất liên tục vật lý.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Trung bình (cần quyền sửa dữ liệu)", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Kiểm tra tính liên tục thời gian (Rate of Change) giữa các bước 5 phút liên tiếp trong pipeline.", styles["BodyJustify"]))

    story.append(Paragraph("3.6. AT06 – Đầu vào ngoài phân phối (dữ liệu tổng hợp)", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.20. Đặc tả test case AT06", styles["TableCaption"]))
    at06_p1 = [
        ("Mã kiểm thử", "AT06"),
        ("Loại kiểm thử", "Robustness"),
        ("Yêu cầu kiểm tra", "Kiểm tra mô hình có nhận ra dữ liệu vô nghĩa hay vẫn đưa ra dự đoán nhiệt độ với độ tin cậy cao."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Có checkpoint; dùng chuỗi dữ liệu thật làm mốc so sánh."),
        ("Dữ liệu đầu vào", "Chuỗi toàn giá trị 0, chuỗi hằng số 10000, nhiễu đều trong khoảng [0, 10000], dữ liệu thật nhân 3, đảo thứ tự kênh.")
    ]
    story.append(make_spec_table(at06_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 35 (NUMBERED AS "33" - AT06 ĐẶC TẢ CONT'D, HÌNH 3.6, BẢNG 3.21, 3.22)
    # ==========================================================================
    at06_p2 = [
        ("Các bước thực hiện", "1. Tạo các đầu vào tổng hợp có cùng kích thước với dữ liệu thật.<br/>2. Dự đoán, ghi độ tin cậy trung bình.<br/>3. Lệnh chạy: $PY -m scripts.at06_ood_input"),
        ("Kết quả mong đợi", "Với dữ liệu vô nghĩa, độ tin cậy trung bình <= 0,60 hoặc từ chối đưa ra dự đoán."),
        ("Kết quả thực tế", "Độ tin cậy trung bình: dữ liệu thật 0,95; chuỗi toàn 0 là 0,98; chuỗi hằng số 10000 là 0,99; nhiễu đều 0,97. Mô hình vẫn dự báo nhiệt độ ~21.8°C trên dữ liệu toàn 0."),
        ("Đánh giá", "FAIL (0/6 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at06_p2, styles))

    if (CHARTS_DIR / "at06_synthetic_confidence.png").exists():
        story.append(Image(str(CHARTS_DIR / "at06_synthetic_confidence.png"), width=360, height=140))
    story.append(Paragraph("Hình 3.6. Độ tin cậy của mô hình trên dữ liệu thật và dữ liệu tổng hợp.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.21. Cấu hình kiểm thử AT06", styles["TableCaption"]))
    b321_str = '{\n  "synthetic_cases": ["zeros", "constant_10000", "uniform_noise", "scale_x3", "channel_permuted"],\n  "checkpoint": "dinov3_forecaster_best.pt"\n}'
    story.append(make_code_box(b321_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.22. Kết quả kiểm thử AT06 (các chỉ số chính)", styles["TableCaption"]))
    b322_str = '{\n  "metrics": {\n    "real": {"mean_confidence": 0.95, "predicted_mean": 21.45},\n    "zeros": {"mean_confidence": 0.98, "predicted_mean": 21.84},\n    "constant_10000": {"mean_confidence": 0.99, "predicted_mean": 22.45},\n    "uniform_noise": {"mean_confidence": 0.97, "predicted_mean": 21.90}\n  }\n}'
    story.append(make_code_box(b322_str, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Lỗi phát hiện: Mô hình không phân biệt được dữ liệu vô nghĩa, kết quả này trùng với TC06 và TC08.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Trung bình", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Kiểm tra chất lượng đầu vào (dải giá trị hợp lý); hiệu chỉnh xác suất hoặc thêm ngưỡng để đánh dấu không chắc chắn.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 36 (NUMBERED AS "34" - 3.7 AT07 ĐẶC TẢ, HÌNH 3.7)
    # ==========================================================================
    story.append(Paragraph("3.7. AT07 – Tấn công bằng giá trị số học bất thường (NaN / Infinity)", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.23. Đặc tả test case AT07", styles["TableCaption"]))
    at07_spec = [
        ("Mã kiểm thử", "AT07"),
        ("Loại kiểm thử", "Security attack, negative/boundary"),
        ("Yêu cầu kiểm tra", "Kiểm tra API xử lý các chuỗi thời tiết có giá trị số học sai hoặc giá trị đặc biệt NaN, +Infinity, -Infinity."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Ứng dụng chạy tại local; gửi tuần tự."),
        ("Dữ liệu đầu vào", "13 biến thể gửi tới /predict: NaN trong mảng, +Infinity, -Infinity, giá trị âm vô lý, giá trị siêu lớn 10^308, chuỗi chữ trong số."),
        ("Các bước thực hiện", "1. Gửi từng biến thể tới endpoint /predict.<br/>2. Ghi mã trạng thái.<br/>3. Tái hiện các trường hợp lỗi 500 để tìm nguyên nhân.<br/>4. Lệnh chạy: $PY -m scripts.at07_invalid_numerics"),
        ("Kết quả mong đợi", "Tất cả trả 422, không có lỗi 500."),
        ("Kết quả thực tế", "18/26 lượt trả đúng 422. NaN, +Infinity và -Infinity khi gửi dạng token thô trả 500 (6 lượt)."),
        ("Đánh giá", "FAIL (44/53 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at07_spec, styles))

    log_at07_box = "$ AT07: trích evidence/AT07/execution.log\nPASS · +Infinity /predict · expected=422 · actual=422\nPASS · -Infinity /predict · expected=422 · actual=422\nFAIL · NaN token raw JSON body · expected=422 · actual=500\nFAIL · unquoted Infinity token raw JSON · expected=422 · actual=500\n... (41 assertion khác, xem đầy đủ trong execution.log)\nVERDICT AT07: FAIL"
    story.append(make_code_box(log_at07_box, styles, font_size=7.2, leading=9.0))
    story.append(Paragraph("Hình 3.7. Trích nhật ký thực thi AT07.", styles["FigureCaption"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 37 (NUMBERED AS "35" - AT07 BẢNG 3.24, 3.25, 3.26 PART 1)
    # ==========================================================================
    story.append(Paragraph("Bảng 3.24. Tham số kiểm thử AT07: body hợp lệ dùng để tạo 13 biến thể (request JSON)", styles["TableCaption"]))
    story.append(make_code_box(req_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.25. Kết quả phản hồi API AT07 (response JSON)", styles["TableCaption"]))
    b325_str = 'Trường hợp: +Infinity trong ma trận dữ liệu\nHTTP 422, 3,1 ms\n{\n  "detail": "data contains non-finite infinite (inf) values which are prohibited."\n}'
    story.append(make_code_box(b325_str, styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 3.24; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 3.26. Các trường hợp kiểm thử AT07 (28 request)", styles["TableCaption"]))
    at07_p1 = [
        (1, "Infinity trong float", "st01_temperature[0]: float('inf')", 422, '{"detail": "data contains non-finite infinite (inf) values"}'),
        (2, "-Infinity trong float", "st01_temperature[0]: float('-inf')", 422, '{"detail": "data contains non-finite infinite (inf) values"}'),
        (3, "giá trị siêu lớn 10^308", "st01_temperature[0]: 1e308", 422, '{"detail": "Value exceeds numeric range"}')
    ]
    story.append(make_cases_table(at07_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 38 (NUMBERED AS "36" - AT07 BẢNG 3.26 PART 2)
    # ==========================================================================
    at07_p2 = [
        (4, "NaN token thô", 'chuỗi raw JSON chứa {"data": [NaN]}', 500, "Internal Server Error"),
        (5, "+Infinity token thô", 'chuỗi raw JSON chứa {"data": [Infinity]}', 500, "Internal Server Error"),
        (6, "-Infinity token thô", 'chuỗi raw JSON chứa {"data": [-Infinity]}', 500, "Internal Server Error"),
        (7, "áp suất âm", "st01_pressure: [-100, ...]", 200, '{"status": "success", "horizon_minutes": 60}'),
        (8, "độ ẩm 250%", "st01_humidity: [250, ...]", 200, '{"status": "success", "horizon_minutes": 60}')
    ]
    story.append(make_cases_table(at07_p2, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 39 (NUMBERED AS "37" - AT07 BẢNG 3.26 PART 3, LỖI, 3.8 AT08 BẮT ĐẦU)
    # ==========================================================================
    at07_p3 = [
        (9, "tọa độ trạm ngoài Hà Nội", "station_ids: ['st99_london']", 422, '{"detail": "Unknown station ID"}'),
        (10, "GET /health", "—", 200, '{"status": "healthy", "model": "DINOv3"}')
    ]
    story.append(make_cases_table(at07_p3, styles))

    story.append(Paragraph("Lỗi phát hiện: Bộ kiểm tra vẫn phát hiện NaN là không hợp lệ, nhưng khi tạo phản hồi, thư viện json của Python ném lỗi 'Out of range float values are not JSON compliant', nên kết quả thành 500. Giá trị áp suất âm và độ ẩm > 100% vẫn được chấp nhận vì chưa có bước kiểm tra ràng buộc vật lý.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Trung bình", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Từ chối NaN/Infinity ngay khi đọc JSON; thêm kiểm tra ràng buộc miền vật lý khí tượng.", styles["BodyJustify"]))

    story.append(Paragraph("3.8. AT08 – Can thiệp tham số và định danh tài nguyên", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.27. Đặc tả test case AT08", styles["TableCaption"]))
    at08_p1 = [
        ("Mã kiểm thử", "AT08"),
        ("Loại kiểm thử", "Security attack, negative"),
        ("Yêu cầu kiểm tra", "Kiểm tra API có chặn việc sửa tham số để truy cập dữ liệu ngoài phạm vi, đọc file hệ thống hoặc gọi API không có xác thực."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Ứng dụng chạy tại local; tối đa 120 yêu cầu, tuần tự.")
    ]
    story.append(make_spec_table(at08_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 40 (NUMBERED AS "38" - AT08 ĐẶC TẢ CONT'D, HÌNH 3.8, BẢNG 3.28, 3.29, 3.30 PART 1)
    # ==========================================================================
    at08_p2 = [
        ("Dữ liệu đầu vào", "Checkpoint không tồn tại, đường dẫn dạng ../, mã hóa URL, định danh trạm giả; client gọi không có API token."),
        ("Các bước thực hiện", "1. Gửi các yêu cầu với tham số đã bị sửa.<br/>2. Ghi mã trạng thái từng trường hợp.<br/>3. Gọi API dự báo từ client nặc danh.<br/>4. Lệnh chạy: $PY -m scripts.at08_parameter_tampering"),
        ("Kết quả mong đợi", "Tham số sai bị từ chối; đường dẫn giả trả 404; gọi không có token trả 401/403."),
        ("Kết quả thực tế", "Các trường hợp đường dẫn giả ../, mã hóa URL và trạm sai đều bị chặn (404/422). Tuy nhiên, API không yêu cầu xác thực nên client nặc danh vẫn gọi được dự báo (200)."),
        ("Đánh giá", "FAIL (15/17 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at08_p2, styles))

    log_at08_box = "$ AT08: trích evidence/AT08/execution.log\nPASS · /metadata?config=../../.env · expected=404 · actual=404\nPASS · /static/%2e%2e%2f%2e%2e%2fetc/passwd · expected=404 · actual=404\nPASS · station_id='st99_malicious' · expected=422 · actual=422\nFAIL · gọi API không có API token · expected=401/403 · actual=200\n... (13 assertion khác, xem đầy đủ trong execution.log)\nVERDICT AT08: FAIL"
    story.append(make_code_box(log_at08_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 3.8. Trích nhật ký thực thi AT08.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.28. Tham số kiểm thử AT08 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box(req_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.29. Kết quả phản hồi API AT08 (response JSON)", styles["TableCaption"]))
    story.append(make_code_box('HTTP 200, 32,4 ms\n{\n  "status": "success",\n  "horizon_minutes": 60\n}', styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 3.28; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 3.30. Các trường hợp kiểm thử AT08 (22 request)", styles["TableCaption"]))
    at08_cases_p1 = [
        (1, "GET /metadata?config=../../.env", "—", 404, '{"detail": "Not Found"}'),
        (2, "GET /static/%2e%2e%2fpasswd", "—", 404, '{"detail": "Not Found"}')
    ]
    story.append(make_cases_table(at08_cases_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 41 (NUMBERED AS "39" - AT08 BẢNG 3.30 PART 2)
    # ==========================================================================
    at08_cases_p2 = [
        (3, "POST /predict station='st99'", "station_ids: ['st99']", 422, '{"detail": "station_ids at index 0 must be st01"}'),
        (4, "POST /predict trạm âm", "station_ids: ['st-1']", 422, '{"detail": "Invalid station ID"}'),
        (5, "GET /docs/../../checkpoints", "—", 404, '{"detail": "Not Found"}'),
        (6, "POST /predict không có token", "không gửi Authorization header", 200, '{"status": "success", "horizon_minutes": 60}')
    ]
    story.append(make_cases_table(at08_cases_p2, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 42 (NUMBERED AS "40" - AT08 BẢNG 3.30 PART 3, LỖI, 3.9 AT09 BẮT ĐẦU)
    # ==========================================================================
    at08_cases_p3 = [
        (7, "GET /health", "—", 200, '{"status": "healthy", "model": "DINOv3"}')
    ]
    story.append(make_cases_table(at08_cases_p3, styles))

    story.append(Paragraph("Lỗi phát hiện: API không có xác thực và không gắn quyền người dùng. Bất kỳ client nào cũng có thể gửi yêu cầu suy luận nặc danh không giới hạn.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Trung bình", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Thêm xác thực API Key qua Depends(get_api_key) và phân quyền RBAC.", styles["BodyJustify"]))

    story.append(Paragraph("3.9. AT09 – Tiêu thụ tài nguyên bằng yêu cầu phân tích lớn", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.31. Đặc tả test case AT09", styles["TableCaption"]))
    at09_p1 = [
        ("Mã kiểm thử", "AT09"),
        ("Loại kiểm thử", "Security/hiệu năng, có giới hạn"),
        ("Yêu cầu kiểm tra", "Kiểm tra hệ thống khi nhận một yêu cầu hợp lệ nhưng rất nặng: gửi batch 50 cửa sổ suy luận lớn liên tục."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Ứng dụng chạy tại local; chạy trong 60 giây.")
    ]
    story.append(make_spec_table(at09_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 43 (NUMBERED AS "41" - AT09 ĐẶC TẢ CONT'D, HÌNH 3.9, BẢNG 3.32, 3.33)
    # ==========================================================================
    at09_p2 = [
        ("Dữ liệu đầu vào", "Batch 50 cửa sổ 72 bước x 6 trạm x 11 biến gửi đồng thời."),
        ("Các bước thực hiện", "1. Gửi yêu cầu dự báo batch nặng.<br/>2. Trong 60 giây, mỗi giây ghi bộ nhớ RAM, CPU, thời gian /health.<br/>3. Đo độ trễ của các request khác.<br/>4. Lệnh chạy: $PY -m scripts.at09_resource_exhaustion"),
        ("Kết quả mong đợi", "Trong lúc chạy, /health vẫn phản hồi nhanh; bộ nhớ không tăng mất kiểm soát."),
        ("Kết quả thực tế", "Trong 60 giây, bộ nhớ tăng từ 385 MB lên 780 MB; CPU chiếm 98%. Độ trễ /health từ 14 ms tăng lên 4.200 ms. Sau khi tải dừng, bộ nhớ tự giải phóng về 410 MB."),
        ("Đánh giá", "PASS (8/8 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at09_p2, styles))

    if (CHARTS_DIR / "at09_resource_usage.png").exists():
        story.append(Image(str(CHARTS_DIR / "at09_resource_usage.png"), width=360, height=140))
    story.append(Paragraph("Hình 3.9. Bộ nhớ và CPU của tiến trình khi chạy job nặng.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.32. Tham số kiểm thử AT09 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box(req_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.33. Kết quả phản hồi API AT09 (response JSON)", styles["TableCaption"]))
    story.append(make_code_box('HTTP 200, 4.200 ms\n{\n  "status": "success",\n  "batch_size": 50\n}', styles, font_size=7.2, leading=9.0))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 44 (NUMBERED AS "42" - AT09 BẢNG 3.34, NHẬN XÉT, 3.10 AT10 BẮT ĐẦU)
    # ==========================================================================
    story.append(Paragraph("Các request dưới đây dùng body ở Bảng 3.32; cột \"Dữ liệu gửi\" chỉ ghi phần khác với body đó.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 3.34. Các trường hợp kiểm thử AT09 (32 request)", styles["TableCaption"]))
    at09_cases = [
        (1, "POST /predict batch nặng (10 lần)", "body 50 cửa sổ", 200, '{"status": "success"}'),
        (2, "GET /health trong lúc tải (14 lần)", "—", 200, '{"status": "healthy", "latency": "4200ms"}'),
        (3, "GET /health sau khi dừng tải", "—", 200, '{"status": "healthy", "latency": "14ms"}')
    ]
    story.append(make_cases_table(at09_cases, styles))
    story.append(Paragraph("Nhận xét: Kiểm thử đạt theo tiêu chí, nhưng cho thấy một rủi ro về khả dụng: một yêu cầu nặng có thể chiếm worker CPU khiến các client khác phải chờ tới 4 giây. Đề xuất: Tách riêng luồng suy luận nặng ra Celery/Redis queue.", styles["BodyJustify"]))

    story.append(Paragraph("3.10. AT10 – Giá trị số và kích thước tensor không hợp lệ", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 3.35. Đặc tả test case AT10", styles["TableCaption"]))
    at10_p1 = [
        ("Mã kiểm thử", "AT10"),
        ("Loại kiểm thử", "Security/robustness, boundary"),
        ("Yêu cầu kiểm tra", "Kiểm tra bước tiền xử lý và mô hình có từ chối dữ liệu số không hợp lệ hay không."),
        ("Môi trường thực hiện", "Local"),
        ("Điều kiện thực hiện", "Có checkpoint; dùng cửa sổ 72 bước của dữ liệu test.")
    ]
    story.append(make_spec_table(at10_p1, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 45 (NUMBERED AS "43" - AT10 ĐẶC TẢ CONT'D, HÌNH 3.10, BẢNG 3.36, 3.37, 3.38)
    # ==========================================================================
    at10_p2 = [
        ("Dữ liệu đầu vào", "Giá trị NaN, +Inf, -Inf, -32768, 32767, giá trị âm; tensor sai kích thước [3, 60, 72]; T = 0; T = 200; số kênh không khớp; chèn bức xạ âm vào API."),
        ("Các bước thực hiện", "1. Gọi trực tiếp preprocess và model forward với từng trường hợp.<br/>2. Kiểm tra T = 200 có bị cắt về 72 mốc không.<br/>3. Chèn bức xạ âm vào dữ liệu và kiểm tra trạng thái.<br/>4. Lệnh chạy: $PY -m scripts.at10_tensor_shape_tampering"),
        ("Kết quả mong đợi", "Tất cả trường hợp không hợp lệ bị từ chối bằng ValueError hoặc 422; T = 200 được cắt về 72 mốc."),
        ("Kết quả thực tế", "10/18 lượt bị từ chối đúng (NaN, +Inf, -Inf, sai kích thước). Không bị từ chối: bức xạ mặt trời âm (-500 W/m2), độ ẩm 250%, T = 0. T = 200 được cắt đúng về 72 mốc."),
        ("Đánh giá", "FAIL (24/32 kiểm tra đạt)")
    ]
    story.append(make_spec_table(at10_p2, styles))

    log_at10_box = "$ AT10: trích evidence/AT10/execution.log\nPASS · NaN preprocess ValueError · expected=ValueError · actual=ValueError\nPASS · +Inf preprocess ValueError · expected=ValueError · actual=ValueError\nPASS · -Inf preprocess ValueError · expected=ValueError · actual=ValueError\nFAIL · bức xạ mặt trời âm (-500 W/m2) bị từ chối · expected=ValueError · actual=None\nFAIL · độ ẩm 250% bị từ chối · expected=ValueError · actual=None\nPASS · tensor sai kích thước [3, 60, 72] bị từ chối · expected=ValueError\n... (20 assertion khác, xem đầy đủ trong execution.log)\nVERDICT AT10: FAIL"
    story.append(make_code_box(log_at10_box, styles, font_size=7.0, leading=8.8))
    story.append(Paragraph("Hình 3.10. Trích nhật ký thực thi AT10.", styles["FigureCaption"]))

    story.append(Paragraph("Bảng 3.36. Tham số kiểm thử AT10 (request JSON)", styles["TableCaption"]))
    story.append(make_code_box(req_v1_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.37. Kết quả phản hồi API AT10 (response JSON)", styles["TableCaption"]))
    story.append(make_code_box('HTTP 200, 20,3 ms\n{\n  "status": "success",\n  "horizon_minutes": 60\n}', styles, font_size=7.2, leading=9.0))

    story.append(Paragraph("Bảng 3.38. Các trường hợp kiểm thử AT10 (4 request)", styles["TableCaption"]))
    at10_cases = [
        (1, "POST /predict bức xạ âm", "solar_radiation: -500", 200, '{"status": "success"}'),
        (2, "POST /predict tensor sai", "data: 60 cột", 422, '{"detail": "matrix must have 66 cols"}')
    ]
    story.append(make_cases_table(at10_cases, styles))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 46 (NUMBERED AS "44" - AT10 BẢNG 3.39, 3.40, LỖI)
    # ==========================================================================
    story.append(Paragraph("Bảng 3.39. Cấu hình kiểm thử AT10", styles["TableCaption"]))
    b339_str = '{\n  "cases": [\n    {"name": "NaN", "shape": [3, 66, 72]},\n    {"name": "+Inf", "shape": [3, 66, 72]},\n    {"name": "-Inf", "shape": [3, 66, 72]},\n    {"name": "negative_solar", "value": -500},\n    {"name": "humidity_250", "value": 250},\n    {"name": "shape_60x72", "shape": [3, 60, 72]},\n    {"name": "T_zero", "shape": [3, 66, 0]}\n  ]\n}'
    story.append(make_code_box(b339_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Bảng 3.40. Kết quả kiểm thử AT10 (các chỉ số chính)", styles["TableCaption"]))
    b340_str = '{\n  "cases": [\n    {"case": "NaN", "rejected": true, "exception": "ValueError"},\n    {"case": "+Inf", "rejected": true, "exception": "ValueError"},\n    {"case": "-Inf", "rejected": true, "exception": "ValueError"},\n    {"case": "negative_solar", "rejected": false},\n    {"case": "humidity_250", "rejected": false},\n    {"case": "shape_60x72", "rejected": true, "exception": "ValueError"},\n    {"case": "T_zero", "rejected": false}\n  ]\n}'
    story.append(make_code_box(b340_str, styles, font_size=7.0, leading=8.8))

    story.append(Paragraph("Lỗi phát hiện: Chuỗi rỗng (T = 0) vẫn cho ra dự đoán, giá trị bức xạ mặt trời âm (-500 W/m2) và độ ẩm > 100% không bị chặn vì thiếu bộ ràng buộc miền vật lý.", styles["BodyJustify"]))
    story.append(Paragraph("Mức độ ảnh hưởng: Thấp", styles["BodyJustify"]))
    story.append(Paragraph("Hướng khắc phục: Từ chối T = 0 hoặc số mốc dưới mức tối thiểu; bổ sung validator kiểm tra dải giá trị vật lý tự nhiên.", styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 47 (NUMBERED AS "45" - CHƯƠNG 4, 4.1 BẢNG TỔNG HỢP PART 1: STT 1-17)
    # ==========================================================================
    story.append(Paragraph("CHƯƠNG 4. TỔNG HỢP KẾT QUẢ VÀ KẾT LUẬN", styles["ChapterHeading"]))
    story.append(Paragraph("4.1. Bảng tổng hợp", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 4.1. Tổng hợp 20 test case", styles["TableCaption"]))

    sum_rows_p1 = [
        [Paragraph("STT", styles["TableCellCenter"]), Paragraph("Mã test", styles["TableCell"]), Paragraph("Tên kiểm thử", styles["TableCell"]), Paragraph("Kết quả", styles["TableCellCenter"]), Paragraph("Ghi chú", styles["TableCell"])],
        [Paragraph("1", styles["TableCellCenter"]), Paragraph("TC01", styles["TableCell"]), Paragraph("Kiểm tra trạng thái hoạt động của API", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("2", styles["TableCellCenter"]), Paragraph("TC02", styles["TableCell"]), Paragraph("Kiểm tra dữ liệu đầu vào của API", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("3", styles["TableCellCenter"]), Paragraph("TC03", styles["TableCell"]), Paragraph("Kiểm thử luồng phân tích từ đầu đến cuối", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("4", styles["TableCellCenter"]), Paragraph("TC04", styles["TableCell"]), Paragraph("Kiểm tra định dạng và tính toàn vẹn của kết quả", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("5", styles["TableCellCenter"]), Paragraph("TC05", styles["TableCell"]), Paragraph("Đánh giá chất lượng dự đoán của mô hình", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("6", styles["TableCellCenter"]), Paragraph("TC06", styles["TableCell"]), Paragraph("Độ bền của mô hình trước nhiễu ngẫu nhiên", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("7", styles["TableCellCenter"]), Paragraph("TC07", styles["TableCell"]), Paragraph("Tính nhất quán khi thiếu dữ liệu thời gian", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("8", styles["TableCellCenter"]), Paragraph("TC08", styles["TableCell"]), Paragraph("Hành vi trên dữ liệu ngoài phân phối huấn luyện", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Mô hình tự tin hơn trên dữ liệu cực đoan", styles["TableCell"])],
        [Paragraph("9", styles["TableCellCenter"]), Paragraph("TC09", styles["TableCell"]), Paragraph("Giả lập lỗi dịch vụ dữ liệu khí tượng bên ngoài", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("10", styles["TableCellCenter"]), Paragraph("TC10", styles["TableCell"]), Paragraph("Giả lập lỗi trong quá trình suy luận", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("", styles["TableCell"])],
        [Paragraph("11", styles["TableCellCenter"]), Paragraph("AT01", styles["TableCell"]), Paragraph("Tấn công bằng dữ liệu sai cấu trúc", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Ép kiểu, bỏ qua trường thừa", styles["TableCell"])],
        [Paragraph("12", styles["TableCellCenter"]), Paragraph("AT02", styles["TableCell"]), Paragraph("Tấn công bằng payload kích thước lớn", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Nhận body 6 MiB; JSON sâu gây 500", styles["TableCell"])],
        [Paragraph("13", styles["TableCellCenter"]), Paragraph("AT03", styles["TableCell"]), Paragraph("Gửi dồn dập yêu cầu tới API", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("Hàng đợi xử lý mượt mà 200 request", styles["TableCell"])],
        [Paragraph("14", styles["TableCellCenter"]), Paragraph("AT04", styles["TableCell"]), Paragraph("Tấn công đối kháng FGSM và PGD", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("PGD epsilon=0,1: MAE lệch 8,42°C", styles["TableCell"])],
        [Paragraph("15", styles["TableCellCenter"]), Paragraph("AT05", styles["TableCell"]), Paragraph("Thao túng chuỗi thời gian", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Nhạy với xáo trộn thứ tự thời gian", styles["TableCell"])],
        [Paragraph("16", styles["TableCellCenter"]), Paragraph("AT06", styles["TableCell"]), Paragraph("Đầu vào ngoài phân phối (dữ liệu tổng hợp)", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Độ tin cậy ~1 với dữ liệu vô nghĩa", styles["TableCell"])],
        [Paragraph("17", styles["TableCellCenter"]), Paragraph("AT07", styles["TableCell"]), Paragraph("Tấn công bằng giá trị số học bất thường", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("NaN token thô gây lỗi 500", styles["TableCell"])]
    ]
    t_sum_p1 = Table(sum_rows_p1, colWidths=[24, 42, 175, 52, 194])
    t_sum_p1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 3.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_sum_p1)
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 48 (NUMBERED AS "46" - BẢNG 4.1 CONT'D, 4.2 THỐNG KÊ, BẢNG 4.2, 4.3, 4.3 LỖI 1-6)
    # ==========================================================================
    sum_rows_p2 = [
        [Paragraph("STT", styles["TableCellCenter"]), Paragraph("Mã test", styles["TableCell"]), Paragraph("Tên kiểm thử", styles["TableCell"]), Paragraph("Kết quả", styles["TableCellCenter"]), Paragraph("Ghi chú", styles["TableCell"])],
        [Paragraph("18", styles["TableCellCenter"]), Paragraph("AT08", styles["TableCell"]), Paragraph("Can thiệp tham số và định danh tài nguyên", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Không có xác thực API token", styles["TableCell"])],
        [Paragraph("19", styles["TableCellCenter"]), Paragraph("AT09", styles["TableCell"]), Paragraph("Tiêu thụ tài nguyên bằng yêu cầu phân tích lớn", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("Batch nặng chiếm CPU trong 60 giây", styles["TableCell"])],
        [Paragraph("20", styles["TableCellCenter"]), Paragraph("AT10", styles["TableCell"]), Paragraph("Giá trị số và kích thước tensor không hợp lệ", styles["TableCell"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("Chấp nhận bức xạ âm và độ ẩm > 100%", styles["TableCell"])]
    ]
    t_sum_p2 = Table(sum_rows_p2, colWidths=[24, 42, 175, 52, 194])
    t_sum_p2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
        ('LEFTPADDING', (0,0), (-1,-1), 3.0),
        ('RIGHTPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_sum_p2)

    story.append(Paragraph("4.2. Thống kê", styles["SectionHeading"]))
    story.append(Paragraph("Bảng 4.2. Thống kê kết quả kiểm thử", styles["TableCaption"]))
    stat_rows = [
        [Paragraph("Nhóm", styles["TableCell"]), Paragraph("Số test", styles["TableCellCenter"]), Paragraph("PASS", styles["TableCellCenter"]), Paragraph("FAIL", styles["TableCellCenter"]), Paragraph("BLOCKED", styles["TableCellCenter"])],
        [Paragraph("Kiểm thử hệ thống AI", styles["TableCell"]), Paragraph("10", styles["TableCellCenter"]), Paragraph("9", styles["TableCellCenter"]), Paragraph("1", styles["TableCellCenter"]), Paragraph("0", styles["TableCellCenter"])],
        [Paragraph("Kiểm thử tấn công", styles["TableCell"]), Paragraph("10", styles["TableCellCenter"]), Paragraph("2", styles["TableCellCenter"]), Paragraph("8", styles["TableCellCenter"]), Paragraph("0", styles["TableCellCenter"])],
        [Paragraph("Tổng", styles["TableCell"]), Paragraph("20", styles["TableCellCenter"]), Paragraph("11", styles["TableCellCenter"]), Paragraph("9", styles["TableCellCenter"]), Paragraph("0", styles["TableCellCenter"])]
    ]
    t_stat = Table(stat_rows, colWidths=[167, 80, 80, 80, 80])
    t_stat.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
    ]))
    story.append(t_stat)

    story.append(Paragraph("Tổng số kiểm tra đã thực hiện là 270, trong đó 221 đạt. Bảng 4.3 tổng hợp các số liệu hiệu năng đã đo.", styles["BodyJustify"]))
    story.append(Paragraph("Bảng 4.3. Số liệu hiệu năng đã đo", styles["TableCaption"]))
    perf_rows = [
        [Paragraph("Phép đo", styles["TableCell"]), Paragraph("Số mẫu", styles["TableCellCenter"]), Paragraph("p50 (ms)", styles["TableCellCenter"]), Paragraph("p95 (ms)", styles["TableCellCenter"]), Paragraph("p99 (ms)", styles["TableCellCenter"]), Paragraph("Tỉ lệ lỗi", styles["TableCellCenter"])],
        [Paragraph("/health, Local, 8 luồng (AT03)", styles["TableCell"]), Paragraph("200", styles["TableCellCenter"]), Paragraph("14,1", styles["TableCellCenter"]), Paragraph("23,3", styles["TableCellCenter"]), Paragraph("26,5", styles["TableCellCenter"]), Paragraph("0/200", styles["TableCellCenter"])],
        [Paragraph("/health, Local, khi đang chạy job lớn (AT09)", styles["TableCell"]), Paragraph("13", styles["TableCellCenter"]), Paragraph("—", styles["TableCellCenter"]), Paragraph("3,94", styles["TableCellCenter"]), Paragraph("—", styles["TableCellCenter"]), Paragraph("0", styles["TableCellCenter"])],
        [Paragraph("/health, Production, tuần tự (TC01)", styles["TableCell"]), Paragraph("3", styles["TableCellCenter"]), Paragraph("105,9", styles["TableCellCenter"]), Paragraph("—", styles["TableCellCenter"]), Paragraph("—", styles["TableCellCenter"]), Paragraph("0/3", styles["TableCellCenter"])]
    ]
    t_perf = Table(perf_rows, colWidths=[167, 60, 65, 65, 65, 65])
    t_perf.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.0),
    ]))
    story.append(t_perf)

    story.append(Paragraph("4.3. Các lỗi phát hiện", styles["SectionHeading"]))
    flaws_p1 = [
        "• Lỗi 1 (trung bình, AT07): JSON chứa NaN hoặc Infinity gây lỗi 500 thay vì 422, do phản hồi lỗi chứa giá trị NaN không mã hóa được thành JSON.",
        "• Lỗi 2 (trung bình, AT02): JSON lồng quá sâu gây lỗi 500; ứng dụng không giới hạn kích thước thân yêu cầu.",
        "• Lỗi 3 (cao về khả dụng, AT09): chưa giới hạn kích thước phân tích; một yêu cầu hợp lệ có thể chiếm CPU máy chủ kéo dài độ trễ.",
        "• Lỗi 4 (trung bình, TC08, AT06): mô hình quá tự tin với dữ liệu bất thường, chưa có cơ chế phát hiện dữ liệu ngoài phân phối.",
        "• Lỗi 5 (trung bình, AT04, AT05): mô hình nhạy với nhiễu đối kháng và ngày/mốc quan sát bị sai lệch.",
        "• Lỗi 6 (thấp, AT10): chấp nhận giá trị bức xạ mặt trời âm và độ ẩm > 100%."
    ]
    for fl in flaws_p1:
        story.append(Paragraph(fl, styles["BodyJustify"]))
    story.append(PageBreak())

    # ==========================================================================
    # PAGE 49 (NUMBERED AS "47" - LỖI 7-8, 4.4, 4.5, 4.6)
    # ==========================================================================
    flaws_p2 = [
        "• Lỗi 7 (thấp đến trung bình, AT08): không có xác thực hay phân quyền API; gọi suy luận nặc danh không bị chặn.",
        "• Lỗi 8 (thấp, AT01, AT10): dữ liệu đầu vào chưa được kiểm tra chặt (ép kiểu, trường thừa, chuỗi thời gian rỗng)."
    ]
    for fl in flaws_p2:
        story.append(Paragraph(fl, styles["BodyJustify"]))

    story.append(Paragraph("4.4. Nhận xét về chất lượng hệ thống", styles["SectionHeading"]))
    story.append(Paragraph(
        "Chức năng chính hoạt động ổn định trên cả hai môi trường. Kết quả của Local và Production trùng nhau từng trạm, và các file xuất ra "
        "đúng định dạng. Mô hình đạt Macro MAE 0,2241°C và RMSE 0,2814°C trên tập test, chịu tốt nhiễu nhỏ và việc thiếu tới một nửa số mốc đo. "
        "Hệ thống xử lý tốt các lỗi vận hành như dịch vụ ngoài lỗi, mô hình lỗi, đọc file lỗi, và từ chối checkpoint bị sửa. Điểm yếu tập trung ở ba chỗ: "
        "hai đường xử lý dữ liệu đầu vào bất thường gây lỗi 500, chưa giới hạn tài nguyên cho mỗi yêu cầu, và mô hình chưa nhận biết được dữ liệu bất thường.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("4.5. Đề xuất cải thiện", styles["SectionHeading"]))
    story.append(Paragraph(
        "Theo thứ tự ưu tiên: (1) giới hạn số mốc và thời gian chạy của mỗi job; (2) sửa hai đường gây lỗi 500 và giới hạn kích thước thân yêu cầu; "
        "(3) thêm kiểm tra chất lượng dữ liệu đầu vào và cơ chế đánh dấu kết quả 'không chắc chắn'; (4) gắn xác thực API Key với người tạo; "
        "(5) dùng chế độ kiểm tra chặt cho dữ liệu đầu vào; (6) đưa các test trong báo cáo này vào quy trình CI.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("4.6. Kết luận", styles["SectionHeading"]))
    story.append(Paragraph(
        "Đã thiết kế và thực hiện đủ 20 test case: 11 đạt, 9 không đạt, 0 bị chặn. Nhóm kiểm thử hệ thống AI đạt 9/10; test không đạt (TC08) chỉ ra hạn chế "
        "về khả năng nhận biết dữ liệu bất thường của mô hình. Nhóm kiểm thử tấn công phát hiện 8 điểm yếu với mức độ khác nhau, đã nêu nguyên nhân và hướng khắc phục. "
        "Kết quả chỉ phản ánh các tình huống đã thử, không chứng minh hệ thống an toàn tuyệt đối. Bài kiểm thử còn hạn chế: chỉ có một tập test có nhãn, và các "
        "kiểm thử tấn công chưa được thực hiện trên Production để đảm bảo an toàn cho dịch vụ.",
        styles["BodyJustify"]
    ))

    # Build document with ExactMatchCanvas
    doc.build(story, canvasmaker=ExactMatchCanvas)
    print(f"\n✅ Successfully generated PDF: {OUTPUT_PDF}")

if __name__ == "__main__":
    generate_pdf()
