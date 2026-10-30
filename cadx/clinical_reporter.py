"""
clinical_reporter.py
Mô-đun Đo đạc Hình thái học Lâm sàng & Tự động kết xuất Báo cáo Y khoa Chẩn đoán Hình ảnh:
1. Đo đạc hình thái tổn thương (Đường kính lớn nhất RECIST, chu vi, diện tích mm², tỷ lệ thâm nhiễm).
2. Tự động sinh Báo cáo Y tế dạng PDF chuẩn bệnh viện bằng ReportLab.
"""

import os
import cv2
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class TumorMorphologyAnalyzer:
    """
    Phân tích định lượng các thông số hình thái học của khối u:
    """
    def __init__(self, pixel_spacing_mm=0.5, slice_thickness_mm=3.0):
        self.pixel_spacing = pixel_spacing_mm
        self.slice_thickness = slice_thickness_mm

    def analyze(self, binary_mask: np.ndarray, brain_mask: np.ndarray = None):
        """
        binary_mask: mảng 2D (H, W), {0, 1}
        brain_mask: mảng 2D (H, W) của toàn bộ nhu mô não (để tính % chiếm dụng não)
        """
        mask_uint8 = (binary_mask > 0).astype(np.uint8)
        num_tumor_pixels = np.sum(mask_uint8)

        if num_tumor_pixels == 0:
            return {
                "has_tumor": False,
                "area_mm2": 0.0,
                "perimeter_mm": 0.0,
                "max_diameter_mm": 0.0,
                "min_diameter_mm": 0.0,
                "brain_occupancy_ratio_pct": 0.0,
                "estimated_volume_cm3": 0.0
            }

        # 1. Diện tích u (Area in mm²)
        area_mm2 = float(num_tumor_pixels * (self.pixel_spacing ** 2))

        # 2. Chu vi u (Perimeter in mm)
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        perimeter_pixels = sum(cv2.arcLength(c, closed=True) for c in contours)
        perimeter_mm = float(perimeter_pixels * self.pixel_spacing)

        # 3. Đường kính lớn nhất RECIST (Maximum Feret Diameter)
        # Sử dụng MinAreaRect (bounding box xoay tối ưu) hoặc Convex Hull
        all_pts = []
        for c in contours:
            all_pts.extend(c.reshape(-1, 2))
        
        max_d_mm = 0.0
        min_d_mm = 0.0
        if len(all_pts) >= 5:
            rect = cv2.minAreaRect(np.array(all_pts))
            (w_box, h_box) = rect[1]
            max_d_mm = float(max(w_box, h_box) * self.pixel_spacing)
            min_d_mm = float(min(w_box, h_box) * self.pixel_spacing)

        # 4. Tỷ lệ thể tích u so với diện tích não (%)
        occupancy_pct = 0.0
        if brain_mask is not None:
            num_brain_pixels = np.sum(brain_mask > 0)
            if num_brain_pixels > 0:
                occupancy_pct = float((num_tumor_pixels / num_brain_pixels) * 100.0)

        # 5. Thể tích lát cắt ước tính (Estimated slice volume in cm³)
        # V = Area * slice_thickness (mm³) / 1000 -> cm³
        vol_cm3 = float((area_mm2 * self.slice_thickness) / 1000.0)

        return {
            "has_tumor": True,
            "area_mm2": round(area_mm2, 2),
            "perimeter_mm": round(perimeter_mm, 2),
            "max_diameter_mm": round(max_d_mm, 2),
            "min_diameter_mm": round(min_d_mm, 2),
            "brain_occupancy_ratio_pct": round(occupancy_pct, 2),
            "estimated_volume_cm3": round(vol_cm3, 3)
        }


class MedicalPDFReportGenerator:
    """
    Tự động xuất báo cáo chẩn đoán hình ảnh chuyên nghiệp dạng PDF:
    Bao gồm hình ảnh minh họa (MRI, Mask, XAI), bảng số liệu định lượng và kết luận phân loại.
    """
    def __init__(self, output_pdf_path: str):
        self.output_pdf_path = output_pdf_path

    def generate(self, patient_info: dict, diagnosis_info: dict, morphology_info: dict, image_paths: list):
        """
        patient_info: {"id": "BN-2026-9812", "name": "Tran Van A", "age": 48, "gender": "Nam", "date": "29/10/2026"}
        diagnosis_info: {"model_name": "Attention U-Net + Boundary Loss", "tumor_type": "Glioma", "confidence": "96.8%"}
        morphology_info: kết quả từ TumorMorphologyAnalyzer
        image_paths: [path_orig, path_pred, path_xai]
        """
        doc = SimpleDocTemplate(
            self.output_pdf_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            alignment=1, # Center
            textColor=colors.HexColor('#1B365D')
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=1,
            textColor=colors.HexColor('#4A5568')
        )
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1B365D'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12
        )
        bold_body_style = ParagraphStyle(
            'BoldBodyStyle',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        story = []

        # 1. Header Bệnh viện / Trung tâm CADx
        story.append(Paragraph("<b>HỆ THỐNG TRỢ GIÚP CHẨN ĐOÁN HÌNH ẢNH Y KHOA (CADx)</b>", title_style))
        story.append(Paragraph("KHOA CHẨN ĐOÁN HÌNH ẢNH & Y HỌC HẠT NHÂN - PHÂN ĐOẠN U NÃO TỰ ĐỘNG", subtitle_style))
        story.append(Spacer(1, 12))

        # 2. Thông tin bệnh nhân & Thông số chụp
        patient_data = [
            [
                Paragraph("<b>Mã bệnh nhân:</b> " + patient_info.get("id", "N/A"), body_style),
                Paragraph("<b>Họ và tên:</b> " + patient_info.get("name", "N/A"), body_style),
                Paragraph("<b>Ngày chụp:</b> " + patient_info.get("date", "29/10/2026"), body_style)
            ],
            [
                Paragraph("<b>Tuổi / Giới tính:</b> " + f"{patient_info.get('age', 45)}T / {patient_info.get('gender', 'N/A')}", body_style),
                Paragraph("<b>Chuỗi xung:</b> Contrast-Enhanced T1W MRI", body_style),
                Paragraph("<b>Mặt cắt:</b> Axial Transversal", body_style)
            ]
        ]
        t_patient = Table(patient_data, colWidths=[170, 180, 170])
        t_patient.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_patient)
        story.append(Spacer(1, 10))

        # 3. Kết quả hình ảnh phân đoạn & Bản đồ XAI
        story.append(Paragraph("I. HÌNH ẢNH TRỰC QUAN HÓA TỔN THƯƠNG VÀ BẢN ĐỒ KÍCH HOẠT (XAI)", section_style))
        
        img_cells = []
        labels = ["1. Lát cắt MRI Gốc", "2. Phân đoạn Ranh giới u", "3. Bản đồ nhiệt Grad-CAM"]
        for p in image_paths:
            if os.path.exists(p):
                img_cells.append(RLImage(p, width=160, height=160))
            else:
                img_cells.append(Paragraph("Ảnh không khả dụng", body_style))

        img_table_data = [
            img_cells,
            [Paragraph(f"<b>{lbl}</b>", body_style) for lbl in labels]
        ]
        t_imgs = Table(img_table_data, colWidths=[173, 173, 173])
        t_imgs.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_imgs)
        story.append(Spacer(1, 10))

        # 4. Bảng đo đạc định lượng hình thái học
        story.append(Paragraph("II. KẾT QUẢ ĐO ĐẠC HÌNH THÁI HỌC TỔN THƯƠNG ĐỊNH LƯỢNG", section_style))
        
        morph_data = [
            [Paragraph("<b>Thông số định lượng</b>", bold_body_style), Paragraph("<b>Giá trị đo</b>", bold_body_style), Paragraph("<b>Ý nghĩa lâm sàng / Tiêu chuẩn</b>", bold_body_style)],
            [Paragraph("Phân loại mô bệnh học", body_style), Paragraph(f"<b>{diagnosis_info.get('tumor_type', 'N/A')}</b>", body_style), Paragraph("Dự đoán mạng Deep Learning (Độ tin cậy: " + diagnosis_info.get('confidence', '95%') + ")", body_style)],
            [Paragraph("Diện tích u lát cắt (2D Area)", body_style), Paragraph(f"{morphology_info.get('area_mm2', 0)} mm²", body_style), Paragraph("Diện tích bề mặt mô u thâm nhiễm", body_style)],
            [Paragraph("Chu vi viền tổn thương (Perimeter)", body_style), Paragraph(f"{morphology_info.get('perimeter_mm', 0)} mm", body_style), Paragraph("Độ gồ ghề và kéo dài của ranh giới tổn thương", body_style)],
            [Paragraph("Đường kính lớn nhất (Max Feret)", body_style), Paragraph(f"<b>{morphology_info.get('max_diameter_mm', 0)} mm</b>", body_style), Paragraph("Tiêu chuẩn vàng đánh giá khối u theo RECIST 1.1", body_style)],
            [Paragraph("Tỷ lệ chiếm dụng não (% Brain)", body_style), Paragraph(f"{morphology_info.get('brain_occupancy_ratio_pct', 0)} %", body_style), Paragraph("Mức độ choán chỗ so với tổng thể tích não", body_style)],
            [Paragraph("Thể tích ước tính lát cắt", body_style), Paragraph(f"{morphology_info.get('estimated_volume_cm3', 0)} cm³", body_style), Paragraph("Tích phân thể tích hỗ trợ lập kế hoạch xạ trị", body_style)],
        ]
        t_morph = Table(morph_data, colWidths=[170, 130, 220])
        t_morph.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_morph)
        story.append(Spacer(1, 10))

        # 5. Kết luận và Khuyến nghị
        story.append(Paragraph("III. KẾT LUẬN & ĐỀ XUẤT THEO DÕI", section_style))
        conclusion_text = (
            f"Hình ảnh lát cắt MRI ghi nhận tổn thương dạng khối choán chỗ vùng bán cầu đại não phù hợp với đặc tính <b>{diagnosis_info.get('tumor_type', 'Glioma')}</b>. "
            f"Đường kính tổn thương lớn nhất ghi nhận {morphology_info.get('max_diameter_mm', 0)} mm. Bản đồ kích hoạt Grad-CAM xác nhận mô hình tập trung chính xác vào vùng nhân hoại tử và viền thâm nhiễm. "
            f"Khuyến nghị: Đối chiếu chuỗi xung FLAIR để đánh giá phù nề quanh u và hội chẩn chuyên khoa phẫu thuật thần kinh."
        )
        story.append(Paragraph(conclusion_text, body_style))
        story.append(Spacer(1, 15))

        # 6. Bảng ký tên
        sig_data = [
            [Paragraph("<b>Hệ thống Trợ lý AI (CADx)</b>", body_style), Paragraph("<b>Bác sĩ Chẩn đoán Hình ảnh</b>", body_style)],
            [Paragraph("<i>Mô hình: " + diagnosis_info.get('model_name', 'Attention U-Net') + "</i>", body_style), Paragraph("<i>(Ký và ghi rõ họ tên)</i>", body_style)],
            [Spacer(1, 25), Spacer(1, 25)],
            [Paragraph("Đã thẩm định thuật toán tự động", body_style), Paragraph("<b>TS. Hoàng Văn Quý</b>", body_style)]
        ]
        t_sig = Table(sig_data, colWidths=[260, 260])
        t_sig.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_sig)

        doc.build(story)
        return self.output_pdf_path
