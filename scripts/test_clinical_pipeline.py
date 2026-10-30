"""
test_clinical_pipeline.py
Kiểm thử toàn bộ pipeline lâm sàng trên 1 ca ảnh thực tế từ bộ dữ liệu BRISC 2025:
1. Nạp ảnh MRI và mặt nạ Ground Truth
2. Tiền xử lý: Skull Stripping + CLAHE
3. Phân tích hình thái học lâm sàng (Đường kính RECIST, diện tích mm², chu vi mm, thể tích cm³)
4. Đánh giá chỉ số: Dice, IoU, HD95, ASSD
5. Xuất phiếu kết quả chẩn đoán y khoa PDF
"""

import os, sys
sys.stdout.reconfigure(encoding='utf-8')
proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)
os.chdir(proj_dir)
import cv2
import numpy as np

from pipeline.mri_preprocessor import MRIPipeline
from metrics.clinical_evaluator import ClinicalMetricsEvaluator
from cadx.clinical_reporter import TumorMorphologyAnalyzer, MedicalPDFReportGenerator

# 1. Chọn mẫu ảnh thực tế
train_imgs = os.listdir('UNet/images/train')
sample_name = train_imgs[0]
img_path = os.path.join('UNet', 'images', 'train', sample_name)
mask_path = os.path.join('UNet', 'masks', 'train', sample_name.replace('.jpg', '.png'))

img_bgr = cv2.imread(img_path)
gt_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

print(f'Nạp ảnh: {sample_name}')
print(f'Kích thước ảnh: {img_bgr.shape}, Mặt nạ: {gt_mask.shape}, Các nhãn pixel: {np.unique(gt_mask)}')

# 2. Tiền xử lý ảnh: Skull Stripping + CLAHE
pipeline = MRIPipeline()
processed_bgr, brain_mask = pipeline.process(img_bgr, apply_skull_strip=True, apply_clahe=True)
print(f'Skull Stripping thành công! Diện tích nhu mô não: {np.sum(brain_mask > 0)} pixels')

# 3. Phân tích hình thái học tổn thương
analyzer = TumorMorphologyAnalyzer(pixel_spacing_mm=0.5, slice_thickness_mm=3.0)
morphology = analyzer.analyze(binary_mask=(gt_mask > 0), brain_mask=brain_mask)
print('Kết quả phân tích hình thái học:')
for k, v in morphology.items():
    print(f' - {k}: {v}')

# 4. Đánh giá chỉ số lâm sàng (mô phỏng đối chuẩn)
evaluator = ClinicalMetricsEvaluator(pixel_spacing_mm=0.5)
# Thử nghiệm tính toán chỉ số với chính GT (hoàn hảo)
res = evaluator.evaluate_slice(gt_mask, gt_mask)
mean_dice = res["Mean"]["dice"]
mean_hd95 = res["Mean"]["hd95"]
print(f'Dice Score (GT vs GT): {mean_dice:.4f}')
print(f'HD95 (GT vs GT): {mean_hd95:.2f} mm')

# 5. Lưu ảnh trực quan hóa để chèn vào PDF
os.makedirs('cadx_output', exist_ok=True)
orig_crop_path = 'cadx_output/orig_sample.png'
pred_crop_path = 'cadx_output/pred_sample.png'
xai_crop_path  = 'cadx_output/xai_sample.png'

cv2.imwrite(orig_crop_path, img_bgr)

# Vẽ viền u đỏ lên ảnh
contour_img = img_bgr.copy()
contours, _ = cv2.findContours((gt_mask > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(contour_img, contours, -1, (0, 0, 255), 2)
# Chồng màu bán trong suốt
color_overlay = contour_img.copy()
color_overlay[gt_mask > 0] = [0, 0, 220]
cv2.addWeighted(color_overlay, 0.45, contour_img, 0.55, 0, contour_img)
cv2.imwrite(pred_crop_path, contour_img)

# Tạo ảnh heatmap giả lập
heatmap = cv2.applyColorMap(cv2.GaussianBlur(gt_mask * 80, (25, 25), 0), cv2.COLORMAP_JET)
xai_img = cv2.addWeighted(img_bgr, 0.6, heatmap, 0.4, 0)
cv2.imwrite(xai_crop_path, xai_img)

# 6. Xuất PDF Báo cáo lâm sàng
pdf_gen = MedicalPDFReportGenerator('cadx_output/Phieu_Ket_Qua_Chan_Doan_Mau.pdf')
patient_info = {
    'id': 'BN-2026-BRISC-001',
    'name': 'Nguyễn Văn Minh',
    'age': 52,
    'gender': 'Nam',
    'date': '29/10/2026'
}
diagnosis_info = {
    'model_name': 'SegFormer + Boundary Loss (SOTA)',
    'tumor_type': 'Glioma (U tế bào thần kinh đệm)',
    'confidence': '97.4%'
}
pdf_path = pdf_gen.generate(
    patient_info=patient_info,
    diagnosis_info=diagnosis_info,
    morphology_info=morphology,
    image_paths=[orig_crop_path, pred_crop_path, xai_crop_path]
)

print(f'Xuất báo cáo PDF thành công tại: {pdf_path}')
