"""
PDF Generator for Báo Cáo Bài Thực Hành 2.
Môn: Chuyên đề Trí tuệ Nhân tạo và Khoa học Dữ liệu (Lớp 65TTNT - ĐH Thủy Lợi)
Sinh viên: Nguyễn Thuận Hóa - MSV: 2351260652

Yêu cầu đúng nguyên văn trên bảng của Thầy:
1. Code thay encoder (hoặc backbone) bằng Dino-v3 -> submit github kèm Readme chỉ chỗ đã update.
2. Thu thập data private theo đúng luồng hôm trước -> submit link kaggle public.
3. Code design như buổi 1 kèm model AI đã xuất -> Link deploy hệ thống.
==> Tổng thể submit file PDF kèm 3 bài (Chỉ tập trung chính xác các Link nghiệm thu).
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

    # Custom Typography
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

    story.append(Paragraph("BÁO CÁO NỘP BÀI THỰC HÀNH 2", title_style))
    story.append(Paragraph("HỌC PHẦN: CHUYÊN ĐỀ TRÍ TUỆ NHÂN TẠO VÀ KHOA HỌC DỮ LIỆU (LỚP 65TTNT)", subtitle_style))

    # Student Info Table
    info_data = [
        [
            Paragraph("<b>Họ và tên sinh viên:</b> Nguyễn Thuận Hóa", student_style),
            Paragraph("<b>Mã số sinh viên:</b> 2351260652", student_style)
        ],
        [
            Paragraph("<b>Lớp chuyên ngành:</b> 65TTNT", student_style),
            Paragraph("<b>Hình thức nghiệm thu:</b> File PDF nộp link theo yêu cầu trên bảng", student_style)
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

    # Section 1
    story.append(Paragraph("1. Code thay encoder (hoặc backbone) bằng Dino-v3 &rarr; Submit GitHub kèm Readme chỉ chỗ đã update", req_title_style))
    story.append(Spacer(1, 4))
    sec1_data = [
        [
            Paragraph("<b>GitHub Repository chính thức:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe</u></font>", link_style)
        ],
        [
            Paragraph("<b>README chỉ rõ vị trí đã update DINO-v3:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe#chỉ-rõ-vị-trí-đã-update-backbone-dino-v3-trước--sau</u></font>", link_style)
        ],
        [
            Paragraph("<b>Commit Diff thay thế Backbone DINO-v3:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/compare/7601190...e6120a1</u></font>", link_style)
        ],
        [
            Paragraph("<b>File Model DINO-v3 chính thức:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/src/weather/models/dinov3_forecaster.py</u></font>", link_style)
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

    # Section 2
    story.append(Paragraph("2. Thu thập data private theo đúng luồng hôm trước &rarr; Submit link Kaggle Public", req_title_style))
    story.append(Spacer(1, 4))
    sec2_data = [
        [
            Paragraph("<b>Link Kaggle Public Dataset:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://www.kaggle.com/datasets/hanguynthun/hanoi-weather-multi-station-benchmark</u></font>", link_style)
        ],
        [
            Paragraph("<b>Quy mô dữ liệu (10 năm, 6 trạm Hà Nội):</b>", label_style),
            Paragraph("<b>6,312,384 dòng</b> (tần số 5 phút, 0% NaN, khóa chính duy nhất)", note_style)
        ],
        [
            Paragraph("<b>Mã băm toàn vẹn SHA-256:</b>", label_style),
            Paragraph("<code>86c672b12bbba2ec0b784a92c01990c0ef497cb7f3f6c82061e88863f68d90ea</code>", note_style)
        ],
        [
            Paragraph("<b>Thẻ mô tả dữ liệu (DATA_CARD):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/release/public/DATA_CARD.md</u></font>", link_style)
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

    # Section 3
    story.append(Paragraph("3. Code design như buổi 1 kèm model AI đã xuất &rarr; Link deploy hệ thống", req_title_style))
    story.append(Spacer(1, 4))
    sec3_data = [
        [
            Paragraph("<b>Link Deploy Hệ thống (Web Online 24/7):</b>", label_style),
            Paragraph("<font color='#1D4ED8' size='10'><b><u>https://thuanhoa1110.github.io/ChuyenDe/</u></b></font>", link_style)
        ],
        [
            Paragraph("<b>Link Deploy Dự phòng (Vercel Edge):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://chuyende.vercel.app</u></font>", link_style)
        ],
        [
            Paragraph("<b>Mã nguồn Giao diện Web (Buổi 1):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/index.html</u></font>", link_style)
        ],
        [
            Paragraph("<b>Model AI đã xuất (PyTorch Checkpoint .pt):</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://github.com/ThuanHoa1110/ChuyenDe/blob/main/checkpoints/dinov3_forecaster_best.pt</u></font>", link_style)
        ],
        [
            Paragraph("<b>Docker Hub Container Serving:</b>", label_style),
            Paragraph("<font color='#1D4ED8'><u>https://hub.docker.com/r/hanguynthun/hanoi-temperature</u></font>", link_style)
        ]
    ]
    t3 = Table(sec3_data, colWidths=[200, 315])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FDE047")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t3)
    story.append(Spacer(1, 14))

    # Note footer
    confirm_p = Paragraph(
        "<b>XÁC NHẬN:</b> Báo cáo tổng hợp đầy đủ và chính xác tất cả các liên kết nộp bài theo đúng 3 yêu cầu trên bảng của Giảng viên.",
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
