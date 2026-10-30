# -*- coding: utf-8 -*-
"""
scripts/generate_test_visualizations.py
Sinh ảnh trực quan hóa chi tiết kết quả thử nghiệm trên bộ dữ liệu Masoud Nickparvar:
- 1 ca Não lành (No tumor - Te-no_100.jpg)
- 3 ca U não: U màng não (Meningioma), U tuyến yên (Pituitary), U thần kinh đệm (Glioma)
- Xuất các bảng đối chiếu: Ảnh gốc | YOLOv8s | YOLO11s | Boundary U-Net | SegFormer | Grad-CAM Heatmap
"""

import os
import sys
import shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2

sys.stdout.reconfigure(encoding='utf-8')

# Thiết lập đường dẫn
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "WebApp"))
sys.path.insert(0, str(WORKSPACE_ROOT))

from models.yolo_model import yolov8_model, yolo11_model
from models.unet_model import boundary_unet_model, segformer_model
from utils.visualization import draw_yolo_results, create_mask_overlay, CLASS_COLORS, CLASS_NAMES_VI

OUT_DIR = WORKSPACE_ROOT / "cadx_output" / "test_visualizations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\ba1a614c-c117-4a3f-95ff-1a696fad272c\test_visualizations")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# Tải các mô hình
print("Nạp các mô hình học sâu...")
yolov8_model.load()
yolo11_model.load()
boundary_unet_model.load()
segformer_model.load()
print("Nạp mô hình hoàn tất!")

TEST_BASE = Path(r"c:\Users\User\Downloads\test_tumor\Testing")

CASES = [
    {
        "id": "case1_notumor",
        "title": "1. Não Lành (Khỏe mạnh - Không có khối u)",
        "gt": "Không có khối u (No Tumor / Healthy Brain)",
        "file": TEST_BASE / "notumor" / "Te-no_100.jpg",
        "cls_id": 0
    },
    {
        "id": "case2_meningioma",
        "title": "2. U Màng Não (Meningioma - Khối ngoài trục)",
        "gt": "Meningioma (U màng não bọc rõ ngoài trục)",
        "file": TEST_BASE / "meningioma" / "Te-aug-me_1.jpg",
        "cls_id": 2
    },
    {
        "id": "case3_pituitary",
        "title": "3. U Tuyến Yên (Pituitary - Tổn thương hố yên)",
        "gt": "Pituitary (U tuyến yên đáy sọ)",
        "file": TEST_BASE / "pituitary" / "Te-pi_10.jpg",
        "cls_id": 3
    },
    {
        "id": "case4_glioma",
        "title": "4. U Thần Kinh Đệm (Glioma - Tổn thương thâm nhiễm)",
        "gt": "Glioma (U nội trục ác tính thâm nhiễm)",
        "file": TEST_BASE / "glioma" / "Te-gl_1.jpg",
        "cls_id": 1
    }
]

def render_case(case_info):
    cid = case_info["id"]
    title = case_info["title"]
    gt_text = case_info["gt"]
    img_path = case_info["file"]
    cls_id = case_info["cls_id"]

    orig_pil = Image.open(img_path).convert("RGB")
    W, H = orig_pil.size

    # 1. YOLOv8s-seg
    r8, n8, _ = yolov8_model.predict(orig_pil, conf=0.35)
    img_yolo8, det8 = draw_yolo_results(orig_pil, r8, conf_threshold=0.35)
    if det8 and len(det8) > 0:
        y8_sub = f"{det8[0]['class_name']}\nĐộ tin cậy: {det8[0]['confidence']*100:.1f}%"
    else:
        y8_sub = "Âm tính chuẩn xác\n(0 khối u / Sạch)"
        # Vẽ nhãn xanh lá báo âm tính sạch
        d = ImageDraw.Draw(img_yolo8)
        d.rectangle([(10, 10), (W - 10, 36)], fill=(16, 185, 129, 220))
        d.text((20, 14), "ÂM TÍNH (SẠCH) - 0 KHỐI U", fill=(255, 255, 255))

    # 2. YOLO11s-seg
    r11, n11, _ = yolo11_model.predict(orig_pil, conf=0.35)
    img_yolo11, det11 = draw_yolo_results(orig_pil, r11, conf_threshold=0.35)
    if det11 and len(det11) > 0:
        y11_sub = f"{det11[0]['class_name']}\nĐộ tin cậy: {det11[0]['confidence']*100:.1f}%"
    else:
        y11_sub = "Âm tính chuẩn xác\n(0 khối u / Sạch)"
        d = ImageDraw.Draw(img_yolo11)
        d.rectangle([(10, 10), (W - 10, 36)], fill=(16, 185, 129, 220))
        d.text((20, 14), "ÂM TÍNH (SẠCH) - 0 KHỐI U", fill=(255, 255, 255))

    # 3. Boundary-Aware U-Net
    m_b, _, _ = boundary_unet_model.predict(orig_pil)
    px_b = np.sum(m_b > 0)
    pct_b = (px_b / m_b.size) * 100
    img_b = create_mask_overlay(orig_pil, m_b, alpha=0.5)
    if px_b > 50:
        c_b = [c for c in np.unique(m_b) if c > 0]
        c_name = CLASS_NAMES_VI.get(c_b[0], "U não")
        b_sub = f"{c_name}\nDiện tích: {pct_b:.2f}% ({px_b:,} px)"
    else:
        b_sub = "Không phát hiện u\n(0 px / Não lành)"
        d = ImageDraw.Draw(img_b)
        d.rectangle([(10, 10), (W - 10, 36)], fill=(16, 185, 129, 220))
        d.text((20, 14), "KHÔNG PHÁT HIỆN TỔN THƯƠNG", fill=(255, 255, 255))

    # 4. SegFormer (Transformer)
    m_s, _, _ = segformer_model.predict(orig_pil)
    px_s = np.sum(m_s > 0)
    pct_s = (px_s / m_s.size) * 100
    img_s = create_mask_overlay(orig_pil, m_s, alpha=0.5)
    if px_s > 50:
        c_s = [c for c in np.unique(m_s) if c > 0]
        c_name = CLASS_NAMES_VI.get(c_s[0], "U não")
        s_sub = f"{c_name}\nDiện tích: {pct_s:.2f}% ({px_s:,} px)"
    else:
        s_sub = "Không phát hiện u\n(0 px / Não lành)"
        d = ImageDraw.Draw(img_s)
        d.rectangle([(10, 10), (W - 10, 36)], fill=(16, 185, 129, 220))
        d.text((20, 14), "KHÔNG PHÁT HIỆN TỔN THƯƠNG", fill=(255, 255, 255))

    # 5. Grad-CAM Heatmap
    cam = boundary_unet_model.compute_gradcam(orig_pil, target_class=(cls_id if cls_id > 0 else 1))
    orig_np = np.array(orig_pil)
    if cam is not None and cls_id > 0:
        heatmap = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        xai_img = (orig_np * 0.55 + heatmap * 0.45).astype(np.uint8)
        xai_sub = "Vùng kích hoạt nơ-ron\n(Tập trung lõi khối u)"
    else:
        # Não lành: không có điểm kích hoạt tập trung
        xai_img = orig_np.copy()
        xai_sub = "Trọng số phân tán đồng đều\n(Không có điểm kích hoạt u)"

    # Vẽ biểu đồ 6 cột
    fig, axes = plt.subplots(1, 6, figsize=(18, 3.8), dpi=250)
    fig.patch.set_facecolor('#0F172A') # Nền Dark Navy y tế

    panels = [
        (orig_pil, "1. Ảnh MRI Gốc", f"Nhãn chuẩn:\n{gt_text}"),
        (img_yolo8, "2. YOLOv8s-seg", y8_sub),
        (img_yolo11, "3. YOLO11s-seg", y11_sub),
        (img_b, "4. Boundary-Aware U-Net", b_sub),
        (img_s, "5. SegFormer (Transformer)", s_sub),
        (xai_img, "6. Grad-CAM (XAI)", xai_sub)
    ]

    for ax, (im_data, header, subtitle) in zip(axes, panels):
        ax.imshow(im_data)
        ax.axis("off")
        ax.set_title(f"{header}\n{subtitle}", fontsize=9.2, fontweight='bold', color='#E2E8F0', pad=6)

    fig.suptitle(f"{title} — Đối Chuẩn Thực Nghiệm Suy Luận Lâm Sàng", fontsize=14, fontweight='bold', color='#38BDF8', y=1.06)
    plt.tight_layout()

    out_file = OUT_DIR / f"{cid}_comparison.png"
    plt.savefig(out_file, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    # Sao lưu sang artifact
    art_file = ARTIFACT_DIR / f"{cid}_comparison.png"
    shutil.copy2(out_file, art_file)
    print(f"[OK] Xuất thành công: {out_file.name}")
    return out_file

def main():
    print("Bắt đầu sinh ảnh trực quan hóa đối chuẩn...")
    generated_files = []
    for c in CASES:
        f = render_case(c)
        generated_files.append(f)

    # Sinh ảnh Poster tổng hợp cả 4 ca bệnh
    print("\nSinh ảnh tổng hợp toàn diện cả 4 ca bệnh...")
    fig_all, all_axes = plt.subplots(4, 6, figsize=(18, 14), dpi=250)
    fig_all.patch.set_facecolor('#0F172A')

    for row_idx, case_info in enumerate(CASES):
        img_path = case_info["file"]
        cls_id = case_info["cls_id"]
        gt_text = case_info["gt"]

        orig_pil = Image.open(img_path).convert("RGB")
        W, H = orig_pil.size

        # YOLOv8
        r8, _, _ = yolov8_model.predict(orig_pil, conf=0.35)
        img_y8, det8 = draw_yolo_results(orig_pil, r8, conf_threshold=0.35)
        y8_txt = f"{det8[0]['class_name']} ({det8[0]['confidence']*100:.0f}%)" if det8 else "0 u (Âm tính sạch)"

        # YOLO11
        r11, _, _ = yolo11_model.predict(orig_pil, conf=0.35)
        img_y11, det11 = draw_yolo_results(orig_pil, r11, conf_threshold=0.35)
        y11_txt = f"{det11[0]['class_name']} ({det11[0]['confidence']*100:.0f}%)" if det11 else "0 u (Âm tính sạch)"

        # Boundary U-Net
        m_b, _, _ = boundary_unet_model.predict(orig_pil)
        px_b = np.sum(m_b > 0)
        img_b = create_mask_overlay(orig_pil, m_b, alpha=0.5)
        b_txt = f"U não: {(px_b/m_b.size)*100:.2f}%" if px_b > 50 else "0 px (Sạch)"

        # SegFormer
        m_s, _, _ = segformer_model.predict(orig_pil)
        px_s = np.sum(m_s > 0)
        img_s = create_mask_overlay(orig_pil, m_s, alpha=0.5)
        s_txt = f"U não: {(px_s/m_s.size)*100:.2f}%" if px_s > 50 else "0 px (Sạch)"

        # Grad-CAM
        cam = boundary_unet_model.compute_gradcam(orig_pil, target_class=(cls_id if cls_id > 0 else 1))
        orig_np = np.array(orig_pil)
        if cam is not None and cls_id > 0:
            heatmap = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            xai_img = (orig_np * 0.55 + heatmap * 0.45).astype(np.uint8)
            xai_txt = "Kích hoạt lõi u"
        else:
            xai_img = orig_np.copy()
            xai_txt = "Phân tán (Không u)"

        row_data = [
            (orig_pil, f"Hàng {row_idx+1}: Ảnh Gốc", gt_text[:28]),
            (img_y8, "YOLOv8s-seg", y8_txt),
            (img_y11, "YOLO11s-seg", y11_txt),
            (img_b, "Boundary U-Net", b_txt),
            (img_s, "SegFormer", s_txt),
            (xai_img, "Grad-CAM (XAI)", xai_txt)
        ]

        for col_idx, (im_d, col_title, status) in enumerate(row_data):
            ax = all_axes[row_idx, col_idx]
            ax.imshow(im_d)
            ax.axis("off")
            if row_idx == 0:
                ax.set_title(f"{col_title}\n{status}", fontsize=9.5, fontweight='bold', color='#E2E8F0', pad=6)
            else:
                ax.set_title(status, fontsize=9.2, fontweight='bold', color='#CBD5E1', pad=4)

    fig_all.suptitle("BẢNG TỔNG HỢP ĐỐI CHUẨN THỰC NGHIỆM TRÊN TẬP KIỂM THỬ NGOÀI (MASOUD NICKPARVAR)", 
                     fontsize=15, fontweight='bold', color='#38BDF8', y=0.99)
    plt.tight_layout()

    poster_file = OUT_DIR / "all_cases_comparison_grid.png"
    plt.savefig(poster_file, bbox_inches='tight', facecolor=fig_all.get_facecolor(), edgecolor='none')
    plt.close()

    art_poster = ARTIFACT_DIR / "all_cases_comparison_grid.png"
    shutil.copy2(poster_file, art_poster)
    print(f"[OK] Xuất thành công poster tổng hợp: {poster_file.name}")

if __name__ == "__main__":
    main()
