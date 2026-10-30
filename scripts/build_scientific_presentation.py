# -*- coding: utf-8 -*-
"""
Script tao file PowerPoint (.pptx) bao cao khoa hoc chuyen nghiep:
De tai: Nghien Cuu va Danh Gia Toan Dien Cac Kien Truc Hoc Sau Phan Doan Da Mo Hinh Khoi U Nao Tren Anh Cong Huong Tu Ket Hop Toi Uu Hoa Ranh Gioi Lam Sang
Tac gia: Tran Manh Hung, Hoang Van Quy
Don vi: Phan hieu truong dai hoc Thuy Loi, thanh pho Ho Chi Minh, Viet Nam
"""

import os
import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Bang mau khoa hoc - y te (Scientific Medical AI Palette)
    C_PRIMARY       = RGBColor(15, 23, 42)      # #0F172A (Deep Slate / Dark Navy)
    C_SECONDARY     = RGBColor(30, 58, 138)     # #1E3A8A (Medical Navy)
    C_ACCENT        = RGBColor(2, 132, 199)     # #0284C7 (Medical Sky/Cyan)
    C_ACCENT_DARK   = RGBColor(3, 105, 161)     # #0369A1
    C_EMERALD       = RGBColor(16, 185, 129)    # #10B981 (Success / Best metric)
    C_AMBER         = RGBColor(217, 119, 6)     # #D97706 (Warning / Attention)
    C_BG_CARD       = RGBColor(248, 250, 252)   # #F8FAFC (Slate 50)
    C_BG_CARD_ALT   = RGBColor(241, 245, 249)   # #F1F5F9 (Slate 100)
    C_TEXT_DARK     = RGBColor(15, 23, 42)      # #0F172A
    C_TEXT_MUTED    = RGBColor(100, 116, 139)   # #64748B
    C_BORDER        = RGBColor(226, 232, 240)   # #E2E8F0 (Slate 200)
    C_BORDER_DARK   = RGBColor(203, 213, 225)   # #CBD5E1
    C_WHITE         = RGBColor(255, 255, 255)
    
    base_dir = Path(__file__).resolve().parent.parent
    fig_dir = base_dir / "report_figures"
    cadx_viz_dir = base_dir / "cadx_output" / "test_visualizations"

    TOTAL_SLIDES = 16

    def add_run_txt(p, text, bold=False, italic=False, size_pt=10.5, color_rgb=C_TEXT_DARK, font_name="Arial"):
        r = p.add_run()
        r.text = text
        r.font.name = font_name
        r.font.bold = bold
        r.font.italic = italic
        r.font.size = Pt(size_pt)
        if color_rgb:
            r.font.color.rgb = color_rgb
        return r

    def add_slide_header(slide, title_text, category_text, slide_num):
        # Header text box
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.733), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_cat = tf.paragraphs[0]
        p_cat.space_after = Pt(2)
        add_run_txt(p_cat, category_text.upper(), bold=True, size_pt=9.5, color_rgb=C_ACCENT)

        p_title = tf.add_paragraph()
        add_run_txt(p_title, title_text, bold=True, size_pt=18.5, color_rgb=C_PRIMARY)

        # Header underline
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.color.rgb = C_BORDER

        # Footer
        footer_tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        ftf = footer_tb.text_frame
        ftf.word_wrap = True
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        add_run_txt(fp, "Phân đoạn Đa Mô hình Khối U Não MRI | Đại học Thủy Lợi", bold=False, size_pt=8.5, color_rgb=C_TEXT_MUTED)
        
        # Slide number on right
        num_tb = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.533), Inches(0.3))
        ntf = num_tb.text_frame
        ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        add_run_txt(np, f"{slide_num} / {TOTAL_SLIDES}", bold=True, size_pt=8.5, color_rgb=C_ACCENT)

    def add_card(slide, left, top, width, height, bg_color=C_BG_CARD, border_color=C_BORDER, radius_factor=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # =========================================================================
    # SLIDE 1: TIÊU ĐỀ BÁO CÁO (TITLE SLIDE)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_PRIMARY
    bg1.line.fill.background()

    # Subtle inner card with decorative borders
    inner1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    inner1.fill.solid()
    inner1.fill.fore_color.rgb = RGBColor(20, 31, 54)
    inner1.line.color.rgb = RGBColor(45, 68, 107)
    inner1.line.width = Pt(1.5)

    tb1 = slide1.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(10.733), Inches(5.1))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER
    p0.space_after = Pt(12)
    add_run_txt(p0, "BÁO CÁO CÔNG TRÌNH NGHIÊN CỨU KHOA HỌC", bold=True, size_pt=12.5, color_rgb=C_ACCENT)

    p_title = tf1.add_paragraph()
    p_title.alignment = PP_ALIGN.CENTER
    p_title.space_after = Pt(22)
    add_run_txt(p_title, "NGHIÊN CỨU VÀ ĐÁNH GIÁ TOÀN DIỆN CÁC KIẾN TRÚC HỌC SÂU\nPHÂN ĐOẠN ĐA MÔ HÌNH KHỐI U NÃO TRÊN ẢNH CỘNG HƯỞNG TỪ\nKẾT HỢP TỐI ƯU HÓA RANH GIỚI LÂM SÀNG", bold=True, size_pt=20.5, color_rgb=C_WHITE)

    p_div = tf1.add_paragraph()
    p_div.alignment = PP_ALIGN.CENTER
    p_div.space_after = Pt(20)
    add_run_txt(p_div, "—" * 38, bold=False, size_pt=9, color_rgb=RGBColor(71, 85, 105))

    p_auth = tf1.add_paragraph()
    p_auth.alignment = PP_ALIGN.CENTER
    p_auth.space_after = Pt(6)
    add_run_txt(p_auth, "Tác giả nghiên cứu: ", bold=False, size_pt=13, color_rgb=RGBColor(203, 213, 225))
    add_run_txt(p_auth, "Trần Mạnh Hùng  •  Hoàng Văn Quý\n", bold=True, size_pt=14, color_rgb=C_WHITE)

    p_aff = tf1.add_paragraph()
    p_aff.alignment = PP_ALIGN.CENTER
    p_aff.space_after = Pt(8)
    add_run_txt(p_aff, "Đơn vị: ", bold=False, size_pt=12, color_rgb=RGBColor(148, 163, 184))
    add_run_txt(p_aff, "Phân hiệu Trường Đại học Thủy Lợi, TP. Hồ Chí Minh, Việt Nam\n", bold=True, size_pt=12.5, color_rgb=RGBColor(226, 232, 240))
    add_run_txt(p_aff, "Chuyên ngành: Trí tuệ Nhân tạo & Xử lý Ảnh Y tế | Tháng 10 / 2026", italic=True, size_pt=11, color_rgb=RGBColor(148, 163, 184))

    # =========================================================================
    # SLIDE 2: ĐẶT VẤN ĐỀ & THÁCH THỨC LÂM SÀNG
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide2, "Thực Trạng Lâm Sàng & Thách Thức Trong Phân Đoạn U Não MRI", "1. Giới thiệu & Đặt vấn đề", 2)

    w_card = Inches(5.72)
    h_card = Inches(5.35)

    # Card 1: Bối cảnh lâm sàng
    add_card(slide2, Inches(0.8), Inches(1.55), w_card, h_card)
    tb2_1 = slide2.shapes.add_textbox(Inches(1.05), Inches(1.75), w_card - Inches(0.5), h_card - Inches(0.4))
    tf2_1 = tb2_1.text_frame
    tf2_1.word_wrap = True

    p = tf2_1.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "BỐI CẢNH & Ý NGHĨA LÂM SÀNG SỐNG CÒN\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Vai trò của phân đoạn chính xác trên ảnh MRI thần kinh:\n", bold=True, size_pt=10.5, color_rgb=C_ACCENT)

    items_c1 = [
        ("Tiêu chuẩn vàng nhưng áp lực thủ công cao: ", "Chụp cộng hưởng từ (MRI) là phương tiện chẩn đoán tối ưu nhờ độ phân giải mô mềm cao. Tuy nhiên, việc khoanh vùng thủ công từng lát cắt (80 - 120 lát/ca) tiêu tốn nhiều thời gian và gây mệt mỏi thị giác cho chuyên gia."),
        ("Độ biến thiên quan sát lớn (15% - 25%): ", "Sự bất đồng thuận giữa các bác sĩ chẩn đoán hình ảnh dao động tới 25%, phụ thuộc lớn vào kinh nghiệm chủ quan và sự phức tạp của lát cắt."),
        ("Hậu quả nghiêm trọng của sai lệch bờ viền: ", "Chỉ cần sai số vài milimet ranh giới tổn thương có thể dẫn đến việc cắt phạm vào bó sợi thần kinh chức năng (vận động, ngôn ngữ), hoặc ngược lại, bỏ sót tế bào ung thư vi thâm nhiễm dẫn tới tái phát nhanh.")
    ]
    for title, text in items_c1:
        p_item = tf2_1.add_paragraph()
        p_item.space_after = Pt(8)
        add_run_txt(p_item, "• " + title, bold=True, size_pt=10, color_rgb=C_TEXT_DARK)
        add_run_txt(p_item, text, size_pt=10, color_rgb=C_TEXT_DARK)

    # Card 2: Rào cản kỹ thuật
    add_card(slide2, Inches(6.81), Inches(1.55), w_card, h_card)
    tb2_2 = slide2.shapes.add_textbox(Inches(7.06), Inches(1.75), w_card - Inches(0.5), h_card - Inches(0.4))
    tf2_2 = tb2_2.text_frame
    tf2_2.word_wrap = True

    p = tf2_2.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "BA RÀO CẢN KỸ THUẬT CHO THỊ GIÁC MÁY TÍNH\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Các thách thức cốt lõi đối với giải thuật học sâu:\n", bold=True, size_pt=10.5, color_rgb=C_AMBER)

    items_c2 = [
        ("Mất cân bằng diện tích cục bộ nghiêm trọng: ", "Khối u não chỉ chiếm từ 1.2% đến 6.8% tổng diện tích lát cắt (<5%), hơn 93% diện tích còn lại là mô não lành và nền xương sọ. Mạng dễ bị thiên lệch dự đoán nền."),
        ("Dị thấu giải phẫu mô bệnh học giữa các nhóm u: ", "U màng não (ngoại trục, bao xơ rõ) vs. U tuyến yên (đáy sọ hố yên) vs. U thần kinh đệm (nội trục ác tính, thâm nhiễm mờ nhạt, phù nề rộng). Không thể dùng một mô hình đơn nhất cho mọi ca."),
        ("Hạn chế của hàm mất mát diện tích truyền thống: ", "Dice Loss và Cross-Entropy chỉ tối ưu tích phân diện tích trùng khớp, có xu hướng 'làm tròn' các góc khía vi thể (Over-smoothing), khiến sai số khoảng cách bề mặt (Hausdorff Distance) vẫn rất cao.")
    ]
    for title, text in items_c2:
        p_item = tf2_2.add_paragraph()
        p_item.space_after = Pt(8)
        add_run_txt(p_item, "• " + title, bold=True, size_pt=10, color_rgb=C_TEXT_DARK)
        add_run_txt(p_item, text, size_pt=10, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 3: MỤC TIÊU NGHIÊN CỨU & 6 ĐÓNG GÓP HỌC THUẬT
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide3, "Mục Tiêu Nghiên Cứu & 6 Đóng Góp Học Thuật Trọng Tâm", "1. Giới thiệu & Đặt vấn đề", 3)

    w_col3 = Inches(3.72)
    h_col3 = Inches(5.35)

    # Cột 1: Đối chuẩn & Kiến trúc
    add_card(slide3, Inches(0.8), Inches(1.55), w_col3, h_col3)
    tb3_1 = slide3.shapes.add_textbox(Inches(0.95), Inches(1.75), w_col3 - Inches(0.3), h_col3 - Inches(0.4))
    tf3_1 = tb3_1.text_frame
    tf3_1.word_wrap = True
    p = tf3_1.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "ĐỐI CHUẨN KIẾN TRÚC\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Trường phái đa mô hình:\n", bold=True, size_pt=9.5, color_rgb=C_ACCENT)
    
    col1_items = [
        ("1. Đối chuẩn toàn diện 6 mô hình: ", "Khảo sát có hệ thống cả Phân đoạn thực thể (YOLOv8s-seg, YOLO11s-seg) và Phân đoạn ngữ nghĩa (Attention U-Net, ResNeXt50-UNet++, SegFormer MiT-B2) trên tập dữ liệu BRISC 2025."),
        ("2. Tối ưu hóa hàm Boundary Loss: ", "Tích hợp bản đồ khoảng cách dấu (Signed Distance Maps - SDF), giải quyết hiện tượng Over-smoothing, kéo giảm 26.0% sai số HD95 và 35.1% sai số ASSD.")
    ]
    for t, txt in col1_items:
        p_i = tf3_1.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Cột 2: Tiền xử lý & Minh bạch XAI
    add_card(slide3, Inches(4.8), Inches(1.55), w_col3, h_col3)
    tb3_2 = slide3.shapes.add_textbox(Inches(4.95), Inches(1.75), w_col3 - Inches(0.3), h_col3 - Inches(0.4))
    tf3_2 = tb3_2.text_frame
    tf3_2.word_wrap = True
    p = tf3_2.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "TIỀN XỬ LÝ & XAI\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Chuẩn y tế & Giải thích được:\n", bold=True, size_pt=9.5, color_rgb=C_ACCENT)

    col2_items = [
        ("3. Pipeline tiền xử lý tự động: ", "Tích hợp thuật toán bóc tách hộp sọ Skull Stripping (Otsu + Morphology + LCC) và cân bằng tương phản thích ứng CLAHE, triệt tiêu báo động giả."),
        ("4. Minh bạch hóa quyết định (XAI): ", "Ứng dụng kỹ thuật Grad-CAM phân tích vùng kích hoạt trọng số nơ-ron, chứng minh mô hình tập trung vào mỏm viền u ác tính (Enhancing Rim) phù hợp bệnh học.")
    ]
    for t, txt in col2_items:
        p_i = tf3_2.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Cột 3: Ngoại kiểm & CADx Thực tế
    add_card(slide3, Inches(8.8), Inches(1.55), w_col3, h_col3)
    tb3_3 = slide3.shapes.add_textbox(Inches(8.95), Inches(1.75), w_col3 - Inches(0.3), h_col3 - Inches(0.4))
    tf3_3 = tb3_3.text_frame
    tf3_3.word_wrap = True
    p = tf3_3.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "NGOẠI KIỂM & CADX\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Ứng dụng lâm sàng thực tiễn:\n", bold=True, size_pt=9.5, color_rgb=C_EMERALD)

    col3_items = [
        ("5. Kiểm định ngoại kiểm độc lập: ", "Thực nghiệm kiểm chứng độ đặc hiệu trên ảnh não lành (0% dương tính giả) và kiểm tra tính khái quát trên tập dữ liệu ngoài Masoud Nickparvar."),
        ("6. Đóng gói hệ thống CADx hoàn chỉnh: ", "Xây dựng ứng dụng NeuroScan CADx vận hành mượt trên CPU, trích xuất hình thái học RECIST 1.1 và tự động sinh phiếu kết quả y khoa định dạng PDF.")
    ]
    for t, txt in col3_items:
        p_i = tf3_3.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 4: DỮ LIỆU NGHIÊN CỨU & TIỀN XỬ LÝ Y KHOA
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide4, "Bộ Dữ Liệu BRISC 2025 & Đường Ống Tiền Xử Lý Tự Động", "2. Dữ liệu & Tiền xử lý", 4)

    # Bên trái: 2 Cards thông tin
    w_left4 = Inches(5.2)
    add_card(slide4, Inches(0.8), Inches(1.55), w_left4, Inches(2.6))
    tb4_1 = slide4.shapes.add_textbox(Inches(0.95), Inches(1.65), w_left4 - Inches(0.3), Inches(2.4))
    tf4_1 = tb4_1.text_frame
    tf4_1.word_wrap = True
    p = tf4_1.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "BỘ DỮ LIỆU CHUẨN BRISC 2025\n", bold=True, size_pt=11.5, color_rgb=C_SECONDARY)
    p_info = tf4_1.add_paragraph()
    p_info.space_after = Pt(4)
    add_run_txt(p_info, "• Tổng số mẫu: ", bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_info, "4,794 lát cắt MRI sọ não chuẩn hóa nhãn đa giác.\n", size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_info, "• Phân chia độc lập: ", bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_info, "Train (82.7% - 3,966 ảnh) | Test kiểm thử (14.5% - 693 ảnh) | Bổ sung (2.8% - 135 ảnh).\n", size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_info, "• Ba nhóm bệnh lý: ", bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_info, "U màng não (1,690 - 35.3%) | U thần kinh đệm (1,580 - 33.0%) | U tuyến yên (1,524 - 31.8%).", size_pt=9.5, color_rgb=C_TEXT_DARK)

    add_card(slide4, Inches(0.8), Inches(4.3), w_left4, Inches(2.6))
    tb4_2 = slide4.shapes.add_textbox(Inches(0.95), Inches(4.4), w_left4 - Inches(0.3), Inches(2.4))
    tf4_2 = tb4_2.text_frame
    tf4_2.word_wrap = True
    p = tf4_2.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "ĐƯỜNG ỐNG TIỀN XỬ LÝ 2 GIAI ĐOẠN\n", bold=True, size_pt=11.5, color_rgb=C_SECONDARY)
    p_pipe = tf4_2.add_paragraph()
    p_pipe.space_after = Pt(4)
    add_run_txt(p_pipe, "1. Bóc tách hộp sọ (Skull Stripping): ", bold=True, size_pt=9.5, color_rgb=C_ACCENT)
    add_run_txt(p_pipe, "Phân ngưỡng Otsu kết hợp Opening/Closing và thuật toán LCC loại bỏ toàn bộ xương sọ và màng cứng sáng, ngăn chặn báo động dương tính giả.\n", size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_pipe, "2. Cân bằng tương phản thích ứng (CLAHE): ", bold=True, size_pt=9.5, color_rgb=C_ACCENT)
    add_run_txt(p_pipe, "Clip Limit = 2.0, lưới 8x8 làm nổi bật viền tổn thương mà không khuếch đại nhiễu.", size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Bên phải: Hình ảnh Fig 1 & Fig 2
    fig1_path = fig_dir / "fig1_tumor_classes.png"
    fig2_path = fig_dir / "fig2_dataset_distribution.png"
    if fig1_path.exists():
        slide4.shapes.add_picture(str(fig1_path), Inches(6.2), Inches(1.55), width=Inches(6.33), height=Inches(2.55))
    if fig2_path.exists():
        slide4.shapes.add_picture(str(fig2_path), Inches(6.2), Inches(4.3), width=Inches(6.33), height=Inches(2.55))

    # =========================================================================
    # SLIDE 5: CHIẾN LƯỢC KIẾN TRÚC ĐA TRƯỜNG PHÁI
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide5, "Chiến Lược Kết Hợp Phân Đoạn Thực Thể & Phân Đoạn Ngữ Nghĩa", "3. Phương pháp & Kiến trúc", 5)

    w_card5 = Inches(5.72)
    h_card5 = Inches(4.2)

    # Trường phái 1: Instance Segmentation
    add_card(slide5, Inches(0.8), Inches(1.55), w_card5, h_card5)
    tb5_1 = slide5.shapes.add_textbox(Inches(1.05), Inches(1.75), w_card5 - Inches(0.5), h_card5 - Inches(0.4))
    tf5_1 = tb5_1.text_frame
    tf5_1.word_wrap = True
    p = tf5_1.paragraphs[0]
    p.space_after = Pt(6)
    add_run_txt(p, "PHÂN ĐOẠN THỰC THỂ (INSTANCE SEGMENTATION)\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "YOLOv8s-seg & YOLO11s-seg | Mục tiêu: Sàng lọc nhanh\n", bold=True, size_pt=10, color_rgb=C_ACCENT)

    items_inst = [
        ("Cơ chế vận hành: ", "Tích hợp trực tiếp nhánh phát hiện hộp bao (Bounding Box) và nhánh tổng hợp mặt nạ nguyên mẫu (Proto-net)."),
        ("Tốc độ xử lý siêu tốc: ", "Đạt từ 36.3 đến 38.1 FPS trên CPU (10 - 25 ms/lát cắt), phản hồi tức thì cho bác sĩ phòng cấp cứu."),
        ("Đặc tính ranh giới: ", "Đa giác viền được xấp xỉ nhanh từ hệ số mặt nạ, phù hợp cho việc định vị sơ bộ và phát hiện sự hiện diện của khối u."),
        ("Ứng dụng lâm sàng: ", "Chặng 1 quét nhanh toàn bộ 100+ lát cắt MRI để khoanh vùng nghi ngờ (ROI).")
    ]
    for t, txt in items_inst:
        p_i = tf5_1.add_paragraph()
        p_i.space_after = Pt(6)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Trường phái 2: Semantic Segmentation
    add_card(slide5, Inches(6.81), Inches(1.55), w_card5, h_card5)
    tb5_2 = slide5.shapes.add_textbox(Inches(7.06), Inches(1.75), w_card5 - Inches(0.5), h_card5 - Inches(0.4))
    tf5_2 = tb5_2.text_frame
    tf5_2.word_wrap = True
    p = tf5_2.paragraphs[0]
    p.space_after = Pt(6)
    add_run_txt(p, "PHÂN ĐOẠN NGỮ NGHĨA (SEMANTIC SEGMENTATION)\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Attention U-Net, ResNeXt50, SegFormer | Mục tiêu: Đo đạc tế vi\n", bold=True, size_pt=10, color_rgb=C_EMERALD)

    items_sem = [
        ("Cơ chế vận hành: ", "Phân loại từng điểm ảnh (Pixel-wise classification) với kiến trúc Encoder-Decoder và cơ chế chú ý/Transformer toàn cục."),
        ("Độ chính xác bờ viền cực cao: ", "Bóc tách chính xác các vi thâm nhiễm và góc khía phức tạp của khối u, giảm thiểu sai số khoảng cách HD95."),
        ("Tối ưu hóa hình thái học: ", "Cung cấp đường viền độ phân giải gốc để tính toán chuẩn xác các chỉ số RECIST 1.1 và thể tích u (cm³)."),
        ("Ứng dụng lâm sàng: ", "Chặng 2 can thiệp sâu, hỗ trợ lập kế hoạch xạ trị lập thể và phẫu thuật bảo tồn.")
    ]
    for t, txt in items_sem:
        p_i = tf5_2.add_paragraph()
        p_i.space_after = Pt(6)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Bottom Banner: Quy trình Cascaded 2-Stage
    add_card(slide5, Inches(0.8), Inches(5.9), Inches(11.733), Inches(1.0), bg_color=C_BG_CARD_ALT)
    tb5_bot = slide5.shapes.add_textbox(Inches(1.0), Inches(5.95), Inches(11.333), Inches(0.9))
    tf5_bot = tb5_bot.text_frame
    tf5_bot.word_wrap = True
    p = tf5_bot.paragraphs[0]
    add_run_txt(p, "QUY TRÌNH HỢP TÁC LIÊN HOÀN HAI CHẶNG (CASCADED TWO-STAGE PIPELINE):\n", bold=True, size_pt=10.5, color_rgb=C_SECONDARY)
    p_sub = tf5_bot.add_paragraph()
    add_run_txt(p_sub, "MRI Gốc  —>  [Chặng 1: YOLO-seg quét siêu tốc 15ms phát hiện ROI]  —>  Tự động cắt vùng nghi ngờ  —>  [Chặng 2: Boundary U-Net / SegFormer gọt viền tế vi & đo RECIST 1.1]  —>  Bệnh án PDF hoàn chỉnh", bold=False, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 6: KIẾN TRÚC YOLO-SEG
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide6, "Kiến Trúc Phân Đoạn Thực Thể Không Dùng Hộp Neo (Anchor-Free)", "3. Phương pháp & Kiến trúc", 6)

    w_left6 = Inches(5.2)
    add_card(slide6, Inches(0.8), Inches(1.55), w_left6, Inches(5.35))
    tb6 = slide6.shapes.add_textbox(Inches(1.05), Inches(1.75), w_left6 - Inches(0.5), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    p = tf6.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "CƠ CHẾ ĐỘT PHÁ CỦA YOLO-SEG\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "YOLOv8s-seg & YOLO11s-seg (Anchor-free & Proto-net):\n", bold=True, size_pt=10, color_rgb=C_ACCENT)

    items_yolo = [
        ("Mạng trích xuất đặc trưng C2f / C3k2: ", "Tích hợp các khối tích chập thắt cổ chai phân tách (Cross-Stage Partial), kết hợp SPPF nắm bắt ngữ cảnh ở nhiều quy mô không gian."),
        ("Cơ chế loại bỏ hộp neo (Anchor-free): ", "Dự đoán trực tiếp khoảng cách từ tâm đối tượng đến 4 cạnh biên hộp bao, loại bỏ việc tinh chỉnh anchor priors vốn rất nhạy cảm với hình dạng u não."),
        ("Nhánh Proto-net sinh mặt nạ nguyên mẫu: ", "Trích xuất từ tầng P3 của FPN để sinh 32 bản đồ mặt nạ nguyên mẫu (Prototype Masks) kích thước 160x160 với chi tiết biên sắc nét."),
        ("Đầu phát hiện tính hệ số mặt nạ: ", "Đầu phát hiện tính toán 32 hệ số mặt nạ (Mask Coefficients). Phép nhân ma trận giữa hệ số và Proto-net tạo ra đa giác viền u trong 1 bước duy nhất.")
    ]
    for t, txt in items_yolo:
        p_i = tf6.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Bên phải: Hình 3
    fig3_path = fig_dir / "fig3_yolo_architecture.png"
    if fig3_path.exists():
        slide6.shapes.add_picture(str(fig3_path), Inches(6.2), Inches(1.55), width=Inches(6.33), height=Inches(5.35))

    # =========================================================================
    # SLIDE 7: KIẾN TRÚC ATTENTION U-NET & VISION TRANSFORMER
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide7, "Kiến Trúc Attention U-Net & Vision Transformer Phân Cấp", "3. Phương pháp & Kiến trúc", 7)

    w_left7 = Inches(5.2)
    add_card(slide7, Inches(0.8), Inches(1.55), w_left7, Inches(5.35))
    tb7 = slide7.shapes.add_textbox(Inches(1.05), Inches(1.75), w_left7 - Inches(0.5), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    p = tf7.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "CÁC KIẾN TRÚC CHUYÊN SÂU\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Bảo toàn chi tiết giải phẫu vi mô:\n", bold=True, size_pt=10, color_rgb=C_ACCENT)

    items_unet = [
        ("Attention U-Net (EfficientNet-B0 + scSE): ", "Bộ mã hóa 6.4M tham số chống quá khớp trên ảnh y tế. Skip Connections tích hợp khối chú ý kép scSE: nhánh không gian sSE ép mạng chú ý tọa độ u, nhánh kênh cSE chọn lọc kênh đặc trưng bệnh lý."),
        ("ResNeXt50-UNet++: ", "Kết hợp mạng tích chập nhóm ResNeXt50 (32x4d) và các nút giải mã dày đặc lồng ghép (Dense Skip Pathways), bù đắp thông tin bị mất qua các tầng pooling, tối ưu hóa diện tích IoU đạt 74.60%."),
        ("SegFormer (MiT-B2 Transformer): ", "Đại diện trường phái Vision Transformer. Multi-Head Efficient Self-Attention mô hình hóa tương quan ngữ cảnh toàn cục giữa hai bán cầu não, khắc phục giới hạn Receptive Field của CNN.")
    ]
    for t, txt in items_unet:
        p_i = tf7.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Bên phải: Hình 4
    fig4_path = fig_dir / "fig4_unet_attention_architecture.png"
    if fig4_path.exists():
        slide7.shapes.add_picture(str(fig4_path), Inches(6.2), Inches(1.55), width=Inches(6.33), height=Inches(5.35))

    # =========================================================================
    # SLIDE 8: ĐỘT PHÁ HÀM MẤT MÁT BOUNDARY LOSS
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide8, "Hàm Mất Mát Biên Độ Dựa Trên Bản Đồ Khoảng Cách Dấu (SDF)", "3. Phương pháp & Kiến trúc", 8)

    w_c8 = Inches(5.72)
    h_c8 = Inches(5.35)

    # Trái: Giới hạn Dice & Cơ chế SDF
    add_card(slide8, Inches(0.8), Inches(1.55), w_c8, h_c8)
    tb8_1 = slide8.shapes.add_textbox(Inches(1.05), Inches(1.75), w_c8 - Inches(0.5), h_c8 - Inches(0.4))
    tf8_1 = tb8_1.text_frame
    tf8_1.word_wrap = True
    p = tf8_1.paragraphs[0]
    p.space_after = Pt(6)
    add_run_txt(p, "GIỚI HẠN CỦA DICE LOSS & GIẢI PHÁP SDF\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)

    items_b1 = [
        ("Hiện tượng làm tròn bờ viền (Over-smoothing): ", "Dice Loss tính độ trùng diện tích: L_Dice = 1 - (2|P ∩ G| + ε) / (|P| + |G| + ε). Khi khối u lớn, sai lệch vài pixel ở biên chỉ chiếm tỉ trọng cực nhỏ trong tổng diện tích, khiến mô hình bỏ qua sai số hình học bờ viền."),
        ("Bản đồ khoảng cách dấu (Signed Distance Maps - SDF): ", "Xây dựng ma trận khoảng cách phi_G(q) đo khoảng cách Euclid thực từ mỗi pixel q tới đường biên nhãn chuẩn G: âm nếu nằm trong u, dương nếu nằm ngoài u, bằng 0 ngay tại đường biên."),
        ("Công thức Boundary Loss: ", "L_Boundary = ∫_Ω phi_G(q) · s_θ(q) dq. Mô hình trực tiếp phạt lũy tiến các pixel dự đoán sai lệch càng xa bờ viền.")
    ]
    for t, txt in items_b1:
        p_i = tf8_1.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Phải: Hàm mất mát hỗn hợp & Kết quả cải thiện
    add_card(slide8, Inches(6.81), Inches(1.55), w_c8, h_c8)
    tb8_2 = slide8.shapes.add_textbox(Inches(7.06), Inches(1.75), w_c8 - Inches(0.5), h_c8 - Inches(0.4))
    tf8_2 = tb8_2.text_frame
    tf8_2.word_wrap = True
    p = tf8_2.paragraphs[0]
    p.space_after = Pt(6)
    add_run_txt(p, "HÀM MẤT MÁT HỖN HỢP & HIỆU QUẢ VƯỢT TRỘI\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)

    items_b2 = [
        ("Thiết lập hàm mất mát hỗn hợp tối ưu: ", "L_total = α · L_Dice + β · L_Focal + γ · L_Boundary với α = 0.4, β = 0.4, γ = 0.2. Trong đó Focal Loss (γ_focal = 2.0) giúp triệt tiêu gradient của pixel nền dễ học."),
        ("Giảm mạnh 26.0% sai số khoảng cách HD95: ", "Khoảng cách Hausdorff phân vị 95 giảm từ 9.45 mm xuống 6.99 mm (giảm 2.46 mm), chứng minh bờ viền khối u được khôi phục sắc nét."),
        ("Giảm 35.1% khoảng cách bề mặt đối xứng (ASSD): ", "Chỉ số ASSD giảm từ 7.16 mm xuống 4.65 mm."),
        ("Bản chất hình học: ", "Mặc dù chỉ số Dice chỉ tăng nhẹ (từ 82.07% lên 82.41%), nhưng cấu trúc ranh giới hình học được bảo tồn an toàn tuyệt đối cho phẫu thuật.")
    ]
    for t, txt in items_b2:
        p_i = tf8_2.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 9: BẢNG ĐỐI CHUẨN HIỆU NĂNG TOÀN DIỆN 6 MÔ HÌNH
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide9, "Bảng Đối Chuẩn Hiệu Năng Toàn Diện Trên Tập Kiểm Thử BRISC 2025", "4. Kết quả thực nghiệm", 9)

    # Tạo bảng đối chuẩn
    rows, cols = 7, 7
    left_tbl, top_tbl, width_tbl, height_tbl = Inches(0.8), Inches(1.55), Inches(11.733), Inches(2.7)
    table_shape = slide9.shapes.add_table(rows, cols, left_tbl, top_tbl, width_tbl, height_tbl)
    tbl = table_shape.table

    tbl.columns[0].width = Inches(2.8)
    tbl.columns[1].width = Inches(2.2)
    tbl.columns[2].width = Inches(1.3)
    tbl.columns[3].width = Inches(1.3)
    tbl.columns[4].width = Inches(1.4)
    tbl.columns[5].width = Inches(1.4)
    tbl.columns[6].width = Inches(1.333)

    headers = ["Mô hình Học sâu", "Kiểu Kiến trúc", "Dice (%)", "IoU (%)", "HD95 (mm)", "ASSD (mm)", "FPS / Tham số"]
    data = [
        ["YOLOv8s-seg", "Instance (Anchor-free)", "80.52%", "71.95%", "9.03", "6.84", "36.3 fps (11.8M)"],
        ["YOLO11s-seg", "Instance (Anchor-free)", "81.24%", "72.80%", "8.76", "6.51", "38.1 fps (9.4M)"],
        ["Attention U-Net", "Semantic (Combo Loss)", "82.07%", "73.61%", "9.45", "7.16", "4.2 fps (6.4M)"],
        ["Boundary-Aware U-Net", "Semantic (Boundary Loss)", "82.41%", "73.77%", "6.99 (-26%)", "4.65 (-35%)", "4.2 fps (6.4M)"],
        ["ResNeXt50-UNet++", "Semantic (Dense Nested)", "82.85%", "74.60% (Max)", "7.82", "5.12", "1.8 fps (28.5M)"],
        ["SegFormer (MiT-B2)", "Semantic (Transformer)", "83.00% (Max)", "74.28%", "7.45", "4.88", "2.5 fps (24.7M)"]
    ]

    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PRIMARY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        add_run_txt(p, h_text, bold=True, size_pt=9.5, color_rgb=C_WHITE)

    for row_idx, row_data in enumerate(data):
        for col_idx, val in enumerate(row_data):
            cell = tbl.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_BG_CARD if row_idx % 2 == 0 else C_WHITE
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if col_idx < 2 else PP_ALIGN.CENTER
            is_bold = "(Max)" in val or "(-26%)" in val
            color = C_EMERALD if is_bold else C_TEXT_DARK
            add_run_txt(p, val, bold=is_bold, size_pt=9, color_rgb=color)

    # Bên dưới: Hình 5 biểu đồ đối chuẩn
    fig5_path = fig_dir / "fig5_benchmark_comparison.png"
    if fig5_path.exists():
        slide9.shapes.add_picture(str(fig5_path), Inches(0.8), Inches(4.35), width=Inches(11.733), height=Inches(2.55))

    # =========================================================================
    # SLIDE 10: BÓC TÁCH HIỆU NĂNG THEO TỪNG NHÓM BỆNH LÝ
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide10, "Bóc Tách Hiệu Năng Phân Đoạn Theo Từng Nhóm Mô Bệnh Học", "4. Kết quả thực nghiệm", 10)

    w_c10 = Inches(3.72)
    h_c10 = Inches(5.35)

    # U màng não
    add_card(slide10, Inches(0.8), Inches(1.55), w_c10, h_c10)
    tb10_1 = slide10.shapes.add_textbox(Inches(0.95), Inches(1.75), w_c10 - Inches(0.3), h_c10 - Inches(0.4))
    tf10_1 = tb10_1.text_frame
    tf10_1.word_wrap = True
    p = tf10_1.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "U MÀNG NÃO (MENINGIOMA)\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Hiệu năng dẫn đầu (Dice 90.6% - 92.9%)\n", bold=True, size_pt=9.5, color_rgb=C_EMERALD)
    
    men_items = [
        ("Đặc tính giải phẫu: ", "Khối u ngoài trục não, phát triển từ màng nhện, có bao xơ phân tách rõ ràng với nhu mô não xung quanh."),
        ("Độ ổn định mô hình: ", "Tất cả 6 mô hình đều đạt Dice > 90%. ResNeXt50-UNet++ dẫn đầu đạt Dice 92.92% và IoU 86.78%."),
        ("Khoảng cách biên độ: ", "Sai số khoảng cách HD95 thấp nhất trong 3 nhóm bệnh lý (chỉ 5.12 - 6.20 mm)."),
        ("Ý nghĩa: ", "Các mô hình dễ dàng phát hiện và bóc tách do độ tương phản bao xơ rất sắc nét.")
    ]
    for t, txt in men_items:
        p_i = tf10_1.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # U tuyến yên
    add_card(slide10, Inches(4.8), Inches(1.55), w_c10, h_c10)
    tb10_2 = slide10.shapes.add_textbox(Inches(4.95), Inches(1.75), w_c10 - Inches(0.3), h_c10 - Inches(0.4))
    tf10_2 = tb10_2.text_frame
    tf10_2.word_wrap = True
    p = tf10_2.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "U TUYẾN YÊN (PITUITARY)\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Độ khu trú cao (Dice 88.1% - 90.6%)\n", bold=True, size_pt=9.5, color_rgb=C_ACCENT)

    pit_items = [
        ("Đặc tính giải phẫu: ", "Khu trú đặc thù ở đáy sọ tại hố yên (Sella Turcica), cấu trúc xương bảo vệ cố định tọa độ."),
        ("Độ đồng thuận chẩn đoán: ", "SegFormer đạt Dice 90.64%, YOLO11s đạt 89.45%."),
        ("Thách thức nhỏ: ", "Khi u phát triển lớn chèn ép giao thoa thị giác lên phía trên, ranh giới phần đỉnh có thể mờ nhạt."),
        ("Ý nghĩa: ", "Mô hình học được tọa độ không gian đáy sọ nhờ cơ chế chú ý sSE và Self-Attention.")
    ]
    for t, txt in pit_items:
        p_i = tf10_2.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # U thần kinh đệm
    add_card(slide10, Inches(8.8), Inches(1.55), w_c10, h_c10)
    tb10_3 = slide10.shapes.add_textbox(Inches(8.95), Inches(1.75), w_c10 - Inches(0.3), h_c10 - Inches(0.4))
    tf10_3 = tb10_3.text_frame
    tf10_3.word_wrap = True
    p = tf10_3.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "U THẦN KINH ĐỆM (GLIOMA)\n", bold=True, size_pt=12, color_rgb=C_SECONDARY)
    add_run_txt(p, "Thách thức lớn nhất (Dice 81.5% - 86.6%)\n", bold=True, size_pt=9.5, color_rgb=C_AMBER)

    gli_items = [
        ("Đặc tính giải phẫu: ", "Tổn thương nội trục ác tính, tế bào ung thư thâm nhiễm lan tỏa vào chất trắng não, phù nề rộng quanh u."),
        ("Ưu thế của Transformer: ", "SegFormer vượt trội (Dice 86.66%) nhờ cơ chế Multi-Head Attention nắm bắt tương quan ngữ cảnh toàn cục hai bán cầu."),
        ("Ưu thế Boundary U-Net: ", "Kéo giảm sai số HD95 từ 11.20 mm xuống 8.45 mm tại vùng ranh giới vi thâm nhiễm."),
        ("Ý nghĩa lâm sàng: ", "Cần kết hợp SegFormer (bao quát vùng phù) và Boundary U-Net (bám lõi u).")
    ]
    for t, txt in gli_items:
        p_i = tf10_3.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 11: KIỂM ĐỊNH NGOẠI KIỂM MASOUD NICKPARVAR
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide11, "Kiểm Định Độc Lập Ngoại Kiểm Trên Bộ Dữ Liệu Masoud Nickparvar", "4. Kết quả thực nghiệm", 11)

    # Trái: Lưới ảnh Fig grid
    grid_path = cadx_viz_dir / "all_cases_comparison_grid.png"
    if grid_path.exists():
        slide11.shapes.add_picture(str(grid_path), Inches(0.8), Inches(1.55), width=Inches(6.8), height=Inches(5.35))

    # Phải: Phân tích 2 Card
    w_r11 = Inches(4.733)
    add_card(slide11, Inches(7.8), Inches(1.55), w_r11, Inches(2.6))
    tb11_1 = slide11.shapes.add_textbox(Inches(7.95), Inches(1.65), w_r11 - Inches(0.3), Inches(2.4))
    tf11_1 = tb11_1.text_frame
    tf11_1.word_wrap = True
    p = tf11_1.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "KIỂM CHỨNG TRÊN NHÓM NÃO LÀNH (NO TUMOR)\n", bold=True, size_pt=11.5, color_rgb=C_SECONDARY)
    p_txt1 = tf11_1.add_paragraph()
    p_txt1.space_after = Pt(4)
    add_run_txt(p_txt1, "• Độ đặc hiệu tuyệt đối 100%: ", bold=True, size_pt=9.5, color_rgb=C_EMERALD)
    add_run_txt(p_txt1, "Cả 6 mô hình đều dự đoán 0 pixel u, không báo động dương tính giả khi quét qua chất trắng, chất xám và não thất thông thường.\n", size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_txt1, "• Hiệu quả của Skull Stripping: ", bold=True, size_pt=9.5, color_rgb=C_ACCENT)
    add_run_txt(p_txt1, "Việc bóc tách xương sọ triệt để giúp loại bỏ hoàn toàn các viền màng não sáng dễ gây nhầm lẫn.", size_pt=9.5, color_rgb=C_TEXT_DARK)

    add_card(slide11, Inches(7.8), Inches(4.3), w_r11, Inches(2.6))
    tb11_2 = slide11.shapes.add_textbox(Inches(7.95), Inches(4.4), w_r11 - Inches(0.3), Inches(2.4))
    tf11_2 = tb11_2.text_frame
    tf11_2.word_wrap = True
    p = tf11_2.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "KIỂM CHỨNG TRÊN 3 NHÓM U NGOẠI KIỂM\n", bold=True, size_pt=11.5, color_rgb=C_SECONDARY)
    p_txt2 = tf11_2.add_paragraph()
    p_txt2.space_after = Pt(4)
    add_run_txt(p_txt2, "• Đồng thuận tuyệt đối trên U màng não & Tuyến yên: ", bold=True, size_pt=9.5, color_rgb=C_ACCENT)
    add_run_txt(p_txt2, "Cả 6 mô hình định vị chính xác vị trí và hình thái học của khối u dù thiết bị chụp và độ tương phản khác biệt hoàn toàn với tập BRISC.\n", size_pt=9.5, color_rgb=C_TEXT_DARK)
    add_run_txt(p_txt2, "• Phân tách thâm nhiễm trên U Glioma: ", bold=True, size_pt=9.5, color_rgb=C_ACCENT)
    add_run_txt(p_txt2, "YOLO11s tin cậy 87%, SegFormer bao quát vùng phù (7.44%), Boundary U-Net bám lõi u (3.06%).", size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 12: MINH BẠCH HÓA GRAD-CAM XAI
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide12, "Minh Bạch Hóa Trọng Số Ra Quyết Định Với Grad-CAM (XAI)", "4. Kết quả thực nghiệm", 12)

    w_c12 = Inches(5.72)
    h_c12 = Inches(5.35)

    add_card(slide12, Inches(0.8), Inches(1.55), w_c12, h_c12)
    tb12_1 = slide12.shapes.add_textbox(Inches(1.05), Inches(1.75), w_c12 - Inches(0.5), h_c12 - Inches(0.4))
    tf12_1 = tb12_1.text_frame
    tf12_1.word_wrap = True
    p = tf12_1.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "CƠ CHẾ KÍCH HOẠT GRAD-CAM\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Minh bạch hóa vùng nơ-ron tập trung quyết định:\n", bold=True, size_pt=10, color_rgb=C_ACCENT)

    items_xai1 = [
        ("Nguyên lý Grad-CAM trên nhánh Decoder: ", "Tính toán đạo hàm riêng của điểm số lớp u so với bản đồ đặc trưng tầng tích chập cuối cùng: alpha_k^c = (1/Z) ∑_i ∑_j (∂y^c / ∂A_{i,j}^k)."),
        ("Tạo bản đồ nhiệt trực quan: ", "Kết hợp hàm chỉnh lưu ReLU để giữ lại các trọng số kích hoạt dương: L_Grad-CAM = ReLU(∑_k alpha_k^c · A^k)."),
        ("Nội suy song tuyến tính: ", "Phóng đại về kích thước ảnh gốc và phủ màu bán trong suốt, cho phép bác sĩ lâm sàng đối chiếu trực tiếp với phim chụp MRI.")
    ]
    for t, txt in items_xai1:
        p_i = tf12_1.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    add_card(slide12, Inches(6.81), Inches(1.55), w_c12, h_c12)
    tb12_2 = slide12.shapes.add_textbox(Inches(7.06), Inches(1.75), w_c12 - Inches(0.5), h_c12 - Inches(0.4))
    tf12_2 = tb12_2.text_frame
    tf12_2.word_wrap = True
    p = tf12_2.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "GIẢI THÍCH SINH HỌC THẦN KINH LÂM SÀNG\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Tại sao nhiệt chỉ bôi tập trung vào hai mỏm viền u Glioma?\n", bold=True, size_pt=10, color_rgb=C_AMBER)

    items_xai2 = [
        ("Hiện tượng kích hoạt không đều: ", "Bản đồ nhiệt Grad-CAM không phân bổ phẳng trên toàn bộ diện tích khối u Glioma ác tính mà tập trung cao độ vào hai mỏm viền ngấm thuốc cản từ ở cực trên tổn thương."),
        ("Bản chất mô bệnh học thần kinh: ", "Vùng lõi trung tâm là mô hoại tử (Central Necrosis) trơ về mặt tín hiệu và chuyển hóa. Ngược lại, vùng bờ viền (Enhancing Rim) là nơi tế bào ung thư tăng sinh mạch và xâm lấn mô lành mạnh mẽ nhất."),
        ("Hiện tượng bão hòa Gradient: ", "Mạng nơ-ron học cách dồn toàn bộ trọng số vào ranh giới sống còn này để phân biệt mô lành và u ác tính. Điều này khẳng định mô hình học đúng đặc trưng bệnh học thực sự, không học tương quan giả.")
    ]
    for t, txt in items_xai2:
        p_i = tf12_2.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 13: ĐỊNH LƯỢNG HÌNH THÁI HỌC RECIST 1.1
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide13, "Module Đo Đạc Hình Thái Học Chuẩn Quốc Tế RECIST 1.1", "5. Ứng dụng lâm sàng & CADx", 13)

    w_c13 = Inches(11.733)
    add_card(slide13, Inches(0.8), Inches(1.55), w_c13, Inches(5.35))
    tb13 = slide13.shapes.add_textbox(Inches(1.05), Inches(1.75), w_c13 - Inches(0.5), Inches(5.0))
    tf13 = tb13.text_frame
    tf13.word_wrap = True

    p = tf13.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "CÁC CHỈ SỐ HÌNH THÁI HỌC VẬT LÝ PHỤC VỤ ĐÁNH GIÁ ĐÁP ỨNG ĐIỀU TRỊ UNG THƯ\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Tự động trích xuất từ đa giác mặt nạ dựa trên Pixel Spacing (mm) và Slice Thickness (mm):\n", bold=True, size_pt=10, color_rgb=C_ACCENT)

    recist_params = [
        ("Đường kính lớn nhất RECIST (Maximum Diameter - D_max): ", "Đo khoảng cách Euclid lớn nhất giữa hai điểm bất kỳ trên đường viền đa giác bao quanh khối u (đơn vị: mm). Đây là tiêu chuẩn vàng đánh giá mức độ co nhỏ hoặc tiến triển u theo RECIST 1.1."),
        ("Đường kính vuông góc nhỏ nhất (Perpendicular Minor Diameter - D_min): ", "Đo trục ngắn vuông góc với trục lớn nhất (đơn vị: mm), hỗ trợ tính toán tích diện tích tích hai chiều theo tiêu chuẩn WHO."),
        ("Diện tích mặt cắt tổn thương (Area): ", "Tính tổng số lượng pixel u nhân với diện tích vật lý của một pixel: Area = N_pixels · (Pixel_Spacing_x · Pixel_Spacing_y) (đơn vị: mm²)."),
        ("Chu vi bờ viền tổn thương (Perimeter): ", "Chiều dài đường viền bao ngoài khép kín của khối u (đơn vị: mm), phản ánh mức độ gồ ghề và tính chất phân nhánh của u thần kinh đệm."),
        ("Tỉ lệ chiếm thể tích nhu mô não (Brain Occupancy Ratio): ", "Tỉ lệ phần trăm diện tích khối u so với diện tích toàn bộ nhu mô não đã bóc tách xương sọ (đơn vị: %), cung cấp thước đo trực quan về mức độ chèn ép nội sọ."),
        ("Thể tích khối u ước tính (Estimated Volume): ", "Tích phân diện tích mặt cắt theo độ dày lát cắt MRI: V = Area · Slice_Thickness (đơn vị: cm³), đóng vai trò quan trọng trong lập kế hoạch xạ trị gia tốc.")
    ]
    for t, txt in recist_params:
        p_i = tf13.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 14: HỆ THỐNG PHẦN MỀM CADX & XUẤT BỆNH ÁN PDF
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide14, "Hệ Thống Hỗ Trợ Chẩn Đoán CADx & Xuất Bệnh Án PDF Tự Động", "5. Ứng dụng lâm sàng & CADx", 14)

    # Top: 3 Cards tính năng
    w_top14 = Inches(3.72)
    h_top14 = Inches(2.2)

    add_card(slide14, Inches(0.8), Inches(1.55), w_top14, h_top14)
    tb14_1 = slide14.shapes.add_textbox(Inches(0.95), Inches(1.65), w_top14 - Inches(0.3), h_top14 - Inches(0.2))
    tf14_1 = tb14_1.text_frame
    tf14_1.word_wrap = True
    p = tf14_1.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "TỐI ƯU HÓA TRÊN CPU\n", bold=True, size_pt=11, color_rgb=C_SECONDARY)
    p_t1 = tf14_1.add_paragraph()
    add_run_txt(p_t1, "• Vận hành mượt mà trên chip Intel Core i5/i7 thông thường.\n• Tốc độ YOLO 15ms, U-Net ~240ms, không bắt buộc trang bị GPU đắt tiền trong phòng khám cơ sở.", size_pt=9, color_rgb=C_TEXT_DARK)

    add_card(slide14, Inches(4.8), Inches(1.55), w_top14, h_top14)
    tb14_2 = slide14.shapes.add_textbox(Inches(4.95), Inches(1.65), w_top14 - Inches(0.3), h_top14 - Inches(0.2))
    tf14_2 = tb14_2.text_frame
    tf14_2.word_wrap = True
    p = tf14_2.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "HỘI CHẨN ĐA MÔ HÌNH\n", bold=True, size_pt=11, color_rgb=C_SECONDARY)
    p_t2 = tf14_2.add_paragraph()
    add_run_txt(p_t2, "• Chế độ Second-Opinion: Cho phép chạy độc lập từng mô hình hoặc đối chuẩn song song cả 6 mô hình trên cùng 1 màn hình để bác sĩ có góc nhìn đa chiều.", size_pt=9, color_rgb=C_TEXT_DARK)

    add_card(slide14, Inches(8.8), Inches(1.55), w_top14, h_top14)
    tb14_3 = slide14.shapes.add_textbox(Inches(8.95), Inches(1.65), w_top14 - Inches(0.3), h_top14 - Inches(0.2))
    tf14_3 = tb14_3.text_frame
    tf14_3.word_wrap = True
    p = tf14_3.paragraphs[0]
    p.space_after = Pt(4)
    add_run_txt(p, "XUẤT BÁO CÁO PDF Y KHOA\n", bold=True, size_pt=11, color_rgb=C_SECONDARY)
    p_t3 = tf14_3.add_paragraph()
    add_run_txt(p_t3, "• Tích hợp ReportLab tự động tổng hợp: Thông tin hành chính, ảnh gốc, mặt nạ phân đoạn, bản đồ nhiệt XAI và bảng đo RECIST 1.1 sẵn sàng in ấn EMR.", size_pt=9, color_rgb=C_TEXT_DARK)

    # Bottom: Hình 6 giao diện webapp
    fig6_path = fig_dir / "fig6_cadx_inference_comparison.png"
    if fig6_path.exists():
        slide14.shapes.add_picture(str(fig6_path), Inches(0.8), Inches(3.9), width=Inches(11.733), height=Inches(3.0))

    # =========================================================================
    # SLIDE 15: THẢO LUẬN, HẠN CHẾ & HƯỚNG PHÁT TRIỂN
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide15, "Thảo Luận Học Thuật, Hạn Chế Đề Tài & Hướng Phát Triển", "6. Tổng kết & Định hướng", 15)

    w_c15 = Inches(5.72)
    h_c15 = Inches(5.35)

    # Trái: Thảo luận & Hạn chế
    add_card(slide15, Inches(0.8), Inches(1.55), w_c15, h_c15)
    tb15_1 = slide15.shapes.add_textbox(Inches(1.05), Inches(1.75), w_c15 - Inches(0.5), h_c15 - Inches(0.4))
    tf15_1 = tb15_1.text_frame
    tf15_1.word_wrap = True
    p = tf15_1.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "THẢO LUẬN HỌC THUẬT & HẠN CHẾ\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Bài học rút ra từ quá trình thực nghiệm:\n", bold=True, size_pt=10, color_rgb=C_AMBER)

    items_disc = [
        ("Sự đánh đổi giữa mất mát diện tích và biên độ: ", "Chỉ số Dice cao không đồng nghĩa với việc an toàn cho phẫu thuật. Việc Boundary Loss tái cấu trúc không gian gradient ưu tiên bảo vệ ranh giới sống còn có ý nghĩa thiết thực hơn việc cố tăng thêm 0.5% điểm Dice."),
        ("Sự phù hợp của từng trường phái: ", "Không có một mô hình duy nhất tối ưu cho mọi tình huống: YOLO vượt trội về sàng lọc ban đầu, SegFormer bao quát thâm nhiễm lan tỏa, Boundary U-Net bóc tách bờ viền vi mô."),
        ("Hạn chế hiện tại của đề tài: ", "Nghiên cứu tập trung xử lý trên các lát cắt MRI 2D độc lập. Việc chưa khai thác trực tiếp tương quan 3 chiều liên tục giữa các lát cắt kế cận có thể hạn chế độ mượt mà của bề mặt u ở lát cắt biên mỏng.")
    ]
    for t, txt in items_disc:
        p_i = tf15_1.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # Phải: Hướng phát triển
    add_card(slide15, Inches(6.81), Inches(1.55), w_c15, h_c15)
    tb15_2 = slide15.shapes.add_textbox(Inches(7.06), Inches(1.75), w_c15 - Inches(0.5), h_c15 - Inches(0.4))
    tf15_2 = tb15_2.text_frame
    tf15_2.word_wrap = True
    p = tf15_2.paragraphs[0]
    p.space_after = Pt(8)
    add_run_txt(p, "KẾ HOẠCH BƯỚC TIẾP THEO\n", bold=True, size_pt=12.5, color_rgb=C_SECONDARY)
    add_run_txt(p, "Mở rộng nghiên cứu trong tương lai:\n", bold=True, size_pt=10, color_rgb=C_EMERALD)

    items_future = [
        ("1. Mở rộng sang kiến trúc 3D Thể tích (3D Volumetric): ", "Triển khai kiến trúc 3D nnU-Net và 3D Swin-UNETR để phân đoạn trực tiếp trên khối voxel 3D liên tục, tái tạo chính xác mô hình giải phẫu 3D phục vụ phẫu thuật bằng robot."),
        ("2. Tích hợp dữ liệu MRI đa chuỗi xung (Multimodal MRI): ", "Khai thác đồng thời 4 chuỗi xung: T1W (giải phẫu), T1c (ngấm thuốc viền u), T2W và FLAIR (vùng phù nề quanh u) để bóc tách đa thành phần khối u (Whole Tumor, Tumor Core, Enhancing Tumor) theo chuẩn BraTS."),
        ("3. Tích hợp Mô hình Ngôn ngữ Lớn Y khoa (Medical LLM): ", "Ứng dụng mô hình LLM chuyên biệt để tự động chuyển đổi bảng số liệu RECIST 1.1 thành văn bản kết luận chẩn đoán hoàn chỉnh bằng ngôn ngữ tự nhiên.")
    ]
    for t, txt in items_future:
        p_i = tf15_2.add_paragraph()
        p_i.space_after = Pt(8)
        add_run_txt(p_i, "• " + t, bold=True, size_pt=9.5, color_rgb=C_TEXT_DARK)
        add_run_txt(p_i, txt, size_pt=9.5, color_rgb=C_TEXT_DARK)

    # =========================================================================
    # SLIDE 16: KẾT LUẬN & LỜI CẢM ƠN
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    bg16 = slide16.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg16.fill.solid()
    bg16.fill.fore_color.rgb = C_PRIMARY
    bg16.line.fill.background()

    inner16 = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    inner16.fill.solid()
    inner16.fill.fore_color.rgb = RGBColor(20, 31, 54)
    inner16.line.color.rgb = RGBColor(45, 68, 107)
    inner16.line.width = Pt(1.5)

    tb16 = slide16.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(10.733), Inches(5.1))
    tf16 = tb16.text_frame
    tf16.word_wrap = True

    p0 = tf16.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER
    p0.space_after = Pt(10)
    add_run_txt(p0, "TỔNG KẾT CÔNG TRÌNH NGHIÊN CỨU", bold=True, size_pt=12.5, color_rgb=C_ACCENT)

    p_title = tf16.add_paragraph()
    p_title.alignment = PP_ALIGN.CENTER
    p_title.space_after = Pt(18)
    add_run_txt(p_title, "KẾT LUẬN & GIẢI PHÁP CHUYỂN GIAO LÂM SÀNG", bold=True, size_pt=21, color_rgb=C_WHITE)

    # 3 Summary points
    sum_items = [
        "1. Hoàn thành xuất sắc việc đối chuẩn có hệ thống 6 kiến trúc học sâu đa trường phái trên tập BRISC 2025 và ngoại kiểm độc lập trên tập Masoud Nickparvar.",
        "2. Đột phá ứng dụng hàm mất mát Boundary Loss kéo giảm 26.0% sai số khoảng cách HD95 và 35.1% sai số ASSD, giải quyết triệt để vấn đề Over-smoothing.",
        "3. Đóng gói hoàn thiện hệ thống NeuroScan CADx tương tác mượt mà trên CPU, tích hợp Grad-CAM giải thích sinh học, trích xuất RECIST 1.1 và xuất PDF tự động."
    ]
    for s in sum_items:
        p_s = tf16.add_paragraph()
        p_s.space_after = Pt(8)
        add_run_txt(p_s, s, bold=False, size_pt=11, color_rgb=RGBColor(226, 232, 240))

    p_div = tf16.add_paragraph()
    p_div.alignment = PP_ALIGN.CENTER
    p_div.space_after = Pt(16)
    add_run_txt(p_div, "—" * 38, bold=False, size_pt=9, color_rgb=RGBColor(71, 85, 105))

    p_thanks = tf16.add_paragraph()
    p_thanks.alignment = PP_ALIGN.CENTER
    p_thanks.space_after = Pt(8)
    add_run_txt(p_thanks, "XIN TRÂN TRỌNG CẢM ƠN QUÝ THẦY CÔ VÀ HỘI ĐỒNG!\n", bold=True, size_pt=16, color_rgb=C_WHITE)
    add_run_txt(p_thanks, "Kính mong nhận được sự đóng góp ý kiến để hoàn thiện đề tài.\n", italic=True, size_pt=11.5, color_rgb=RGBColor(148, 163, 184))
    add_run_txt(p_thanks, "Hỏi & Đáp (Q&A)", bold=True, size_pt=12, color_rgb=C_ACCENT)

    output_pptx = base_dir / "Bao_Cao_Khoa_Hoc_Springer_Nature.pptx"
    prs.save(str(output_pptx))
    print(f"Presentation saved successfully to: {output_pptx}")

if __name__ == '__main__':
    create_deck()
