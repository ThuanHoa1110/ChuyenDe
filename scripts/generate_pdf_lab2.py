"""
Báo Cáo Bài Thực Hành 2 - Chuyên đề TTNT & KHDL (65TTNT - ĐH Thủy Lợi)
Sinh viên: Nguyễn Thuận Hóa - MSV: 2351260652
Đúng 100% 3 yêu cầu trên bảng, tập trung toàn bộ vào các Link nghiệm thu thực tế.
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
OUTPUT_PDF = os.path.join(BASE_DIR, "docs", "Bao_Cao_Bai_Thuc_Hanh_2.pdf")


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

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 32, A4[0] - 40, 32)

        footer_left = "Trường ĐH Thủy Lợi • Khoa CNTT • Báo Cáo Thực Hành 2 — Nguyễn Thuận Hóa (2351260652)"
        footer_right = f"Trang {self._pageNumber} / {total_pages}"
        self.drawString(40, 20, footer_left)
        self.drawRightString(A4[0] - 40, 20, footer_right)

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
        topMargin=35,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Arial-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=8
    )
    student_style = ParagraphStyle(
        'StudentInfo',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )
    req_title_style = ParagraphStyle(
        'ReqTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F172A")
    )
    label_style = ParagraphStyle(
        'ItemLabel',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    link_style = ParagraphStyle(
        'ItemLink',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1D4ED8")
    )

    story = []

    # Header Box
    story.append(Paragraph("<b>TRƯỜNG ĐẠI HỌC THỦY LỢI — KHOA CÔNG NGHỆ THÔNG TIN</b>", student_style))
    story.append(Paragraph("<b>BỘ MÔN: KHOA HỌC MÁY TÍNH & TRÍ TUỆ NHÂN TẠO</b>", student_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=8))

    story.append(Paragraph("BÁO CÁO NỘP BÀI THỰC HÀNH 2", title_style))
    story.append(Paragraph("HỌC PHẦN: CHUYÊN ĐỀ TRÍ TUỆ NHÂN TẠO VÀ KHOA HỌC DỮ LIỆU (LỚP 65TTNT)", subtitle_style))

    # Student Info Table
    info_data = [
        [
            Paragraph("<b>Họ và tên:</b> Nguyễn Thuận Hóa", student_style),
            Paragraph("<b>Mã số sinh viên:</b> 2351260652", student_style),
            Paragraph("<b>Lớp:</b> 65TTNT", student_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[185, 175, 155])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))

    # YÊU CẦU 1
    story.append(Paragraph("1. Code thay encoder (hoặc backbone) bằng Dino-v3 &rarr; Submit GitHub kèm Readme chỉ chỗ đã update", req_title_style))
    story.append(Spacer(1, 3))
    sec1_data = [
        [
            Paragraph("<b>GitHub Repository:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe</u></font>", link_style)
        ],
        [
            Paragraph("<b>README chỉ rõ vị trí đã update DINO-v3:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe#chỉ-rõ-vị-trí-đã-update-backbone-dino-v3-trước--sau</u></font>", link_style)
        ],
        [
            Paragraph("<b>Commit Diff chỉ rõ vị trí code update:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/compare/7601190...e6120a1</u></font>", link_style)
        ],
        [
            Paragraph("<b>File mã nguồn mô hình DINO-v3:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/src/weather/models/dinov3_forecaster.py</u></font>", link_style)
        ]
    ]
    t1 = Table(sec1_data, colWidths=[190, 325])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    # YÊU CẦU 2
    story.append(Paragraph("2. Thu thập data private theo đúng luồng hôm trước &rarr; Submit link Kaggle Public", req_title_style))
    story.append(Spacer(1, 3))
    sec2_data = [
        [
            Paragraph("<b>Link Kaggle Public Dataset:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://www.kaggle.com/datasets/hanguynthun/hanoi-weather-multi-station-benchmark</u></font>", link_style)
        ],
        [
            Paragraph("<b>Link Kaggle Visualize Dữ liệu (EDA Code):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://www.kaggle.com/code/hanguynthun/visualize-datasets-time-series</u></font>", link_style)
        ],
        [
            Paragraph("<b>Quy mô dữ liệu (10 năm, 6 trạm Hà Nội):</b>", label_style),
            Paragraph("6,312,384 dòng (Tần số 5 phút, 0% NaN, khóa chính duy nhất)", student_style)
        ],
        [
            Paragraph("<b>File Notebook Visualize trong Repo:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/notebooks/kaggle_eda_visualization.ipynb</u></font>", link_style)
        ]
    ]
    t2 = Table(sec2_data, colWidths=[190, 325])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86EFAC")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    # YÊU CẦU 3
    story.append(Paragraph("3. Code design như buổi 1 kèm model AI đã xuất &rarr; Link deploy hệ thống", req_title_style))
    story.append(Spacer(1, 3))
    sec3_data = [
        [
            Paragraph("<b>Link Deploy Hệ thống (Web Online 24/7):</b>", label_style),
            Paragraph("<font color='#1D4ED8' size='9.5'><b><u>https://thuanhoa1110.github.io/ChuyenDe/</u></b></font>", link_style)
        ],
        [
            Paragraph("<b>Link Deploy Dự phòng (Vercel Edge):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://chuyende.vercel.app</u></font>", link_style)
        ],
        [
            Paragraph("<b>Mã nguồn Giao diện Web (Design Buổi 1):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/index.html</u></font>", link_style)
        ],
        [
            Paragraph("<b>Model AI đã xuất (PyTorch Checkpoint .pt):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/checkpoints/dinov3_forecaster_best.pt</u></font>", link_style)
        ]
    ]
    t3 = Table(sec3_data, colWidths=[190, 325])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FDE047")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t3)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
