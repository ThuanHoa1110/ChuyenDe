"""
PDF Generator for Báo Cáo Bài Thực Hành 3.
Môn: Chuyên đề Trí tuệ Nhân tạo và Khoa học Dữ liệu (Lớp 65TTNT - ĐH Thủy Lợi)
Sinh viên: Nguyễn Thuận Hóa - MSV: 2351260652

Yêu cầu đúng nguyên văn trên bảng của Thầy:
1. Triển khai CI/CD cho bài toán AI.
2. Build docker image cho model AI -> public image lên docker hub.
==> Tổng thể submit PDF step by step (Chỉ tập trung chính xác các Link nghiệm thu).
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
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
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 36, A4[0] - 40, 36)

        footer_left = "Khoa CNTT - Đại học Thủy Lợi • Chuyên đề TTNT & KHDL (65TTNT)"
        footer_right = f"Trang {self._pageNumber} / {total_pages}"
        self.drawString(40, 24, footer_left)
        self.drawRightString(A4[0] - 40, 24, footer_right)

        self.restoreState()


def register_fonts():
    font_paths = {
        "Arial": r"C:\Windows\Fonts\arial.ttf",
        "Arial-Bold": r"C:\Windows\Fonts\arialbd.ttf",
        "Arial-Italic": r"C:\Windows\Fonts\ariali.ttf",
        "Arial-BoldItalic": r"C:\Windows\Fonts\arialbi.ttf",
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
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Arial-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=10
    )
    student_style = ParagraphStyle(
        'StudentInfo',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    req_title_style = ParagraphStyle(
        'ReqTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0F172A")
    )
    label_style = ParagraphStyle(
        'ItemLabel',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )
    link_style = ParagraphStyle(
        'ItemLink',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1D4ED8")
    )
    note_style = ParagraphStyle(
        'ItemNote',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569")
    )

    story = []

    # Header Box
    header_html = """
    <b>TRƯỜNG ĐẠI HỌC THỦY LỢI — KHOA CÔNG NGHỆ THÔNG TIN</b><br/>
    <b>BỘ MÔN: KHOA HỌC MÁY TÍNH & TRÍ TUỆ NHÂN TẠO</b>
    """
    story.append(Paragraph(header_html, student_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=10))

    story.append(Paragraph("BÁO CÁO NỘP BÀI THỰC HÀNH 3", title_style))
    story.append(Paragraph("HỌC PHẦN: CHUYÊN ĐỀ TRÍ TUỆ NHÂN TẠO VÀ KHOA HỌC DỮ LIỆU (LỚP 65TTNT)", subtitle_style))

    # Student Info Table
    info_data = [
        [
            Paragraph("<b>Họ và tên sinh viên:</b> Nguyễn Thuận Hóa", student_style),
            Paragraph("<b>Mã số sinh viên:</b> 2351260652", student_style)
        ],
        [
            Paragraph("<b>Lớp chuyên ngành:</b> 65TTNT", student_style),
            Paragraph("<b>Hình thức nghiệm thu:</b> File PDF Step by Step theo yêu cầu trên bảng", student_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[270, 245])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 14))

    # STEP 1
    story.append(Paragraph("Bước 1: Triển khai CI/CD cho bài toán AI", req_title_style))
    story.append(Spacer(1, 4))
    sec1_data = [
        [
            Paragraph("<b>Kết quả chạy CI/CD mới nhất (Pass 100%):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/actions/runs/43051873129</u></font>", link_style)
        ],
        [
            Paragraph("<b>Trang tổng GitHub Actions Workflows:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/actions/workflows/ci.yml</u></font>", link_style)
        ],
        [
            Paragraph("<b>File CI Workflow chính (.github/workflows/ci.yml):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/.github/workflows/ci.yml</u></font>", link_style)
        ],
        [
            Paragraph("<b>File Release CD Workflow (.github/workflows/release.yml):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/.github/workflows/release.yml</u></font>", link_style)
        ],
        [
            Paragraph("<b>Bộ kiểm thử tự động (54 tests Pytest pass 100%):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/tree/main/tests</u></font>", link_style)
        ],
        [
            Paragraph("<b>Tài liệu hướng dẫn Step-by-Step chi tiết:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/docs/ci_cd_docker_step_by_step.md</u></font>", link_style)
        ]
    ]
    t1 = Table(sec1_data, colWidths=[200, 315])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 14))

    # STEP 2
    story.append(Paragraph("Bước 2: Build Docker image cho model AI &rarr; Public image lên Docker Hub", req_title_style))
    story.append(Spacer(1, 4))
    sec2_data = [
        [
            Paragraph("<b>Link Docker Hub Public Repository:</b>", label_style),
            Paragraph("<font color='#1D4ED8' size='10'><b><u>https://hub.docker.com/r/nguyenthuanhoa/hanoi-temperature</u></b></font>", link_style)
        ],
        [
            Paragraph("<b>Image Tag mục tiêu:</b>", label_style),
            Paragraph("<b>nguyenthuanhoa/hanoi-temperature:v1.0.0</b>", note_style)
        ],
        [
            Paragraph("<b>Lệnh kéo Docker Image:</b>", label_style),
            Paragraph("<code>docker pull nguyenthuanhoa/hanoi-temperature:v1.0.0</code>", note_style)
        ],
        [
            Paragraph("<b>Lệnh khởi chạy Container:</b>", label_style),
            Paragraph("<code>docker run -d -p 8000:8000 nguyenthuanhoa/hanoi-temperature:v1.0.0</code>", note_style)
        ],
        [
            Paragraph("<b>Workflow Build &amp; Push Docker Hub tự động:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/actions/workflows/release.yml</u></font>", link_style)
        ],
        [
            Paragraph("<b>File cấu hình Dockerfile:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/Dockerfile</u></font>", link_style)
        ]
    ]
    t2 = Table(sec2_data, colWidths=[200, 315])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86EFAC")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)
    story.append(Spacer(1, 14))

    # Note footer
    confirm_p = Paragraph(
        "<b>XÁC NHẬN:</b> Báo cáo tổng hợp đầy đủ và chính xác tất cả các liên kết nộp bài theo đúng 2 bước yêu cầu trên bảng của Giảng viên.",
        ParagraphStyle('Confirm', parent=styles['Normal'], fontName='Arial-Bold', fontSize=9, textColor=colors.HexColor("#0F766E"))
    )
    t_confirm = Table([[confirm_p]], colWidths=[515])
    t_confirm.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDFA")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#99F6E4")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_confirm)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
