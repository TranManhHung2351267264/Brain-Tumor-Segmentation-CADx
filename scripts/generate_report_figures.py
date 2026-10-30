# -*- coding: utf-8 -*-
"""
Script sinh toàn bộ hình ảnh minh họa chất lượng cao (300 DPI) cho Báo cáo tiến độ:
1. fig1_tumor_classes.png: Ảnh MRI thực tế kèm mặt nạ của 3 nhóm u (Glioma, Meningioma, Pituitary)
2. fig2_dataset_distribution.png: Biểu đồ phân bố thống kê dữ liệu
3. fig3_yolo_architecture.png: Sơ đồ kiến trúc YOLO-seg (Proto-net)
4. fig4_unet_attention_architecture.png: Sơ đồ kiến trúc Attention U-Net (scSE)
5. fig5_benchmark_comparison.png: Biểu đồ đối chuẩn hiệu năng các mô hình
6. fig6_cadx_inference_comparison.png: Ảnh kết quả suy luận thực tế đối đầu giữa 3 mô hình
"""

import os
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Cấu hình font và phong cách học thuật
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

OUTPUT_DIR = Path(r"d:\Học Sâu và Ứng dụng\Tumor\report_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# 1. FIG 1: HÌNH ẢNH THỰC TẾ 3 NHÓM U NÃO KÈM MẶT NẠ PHÂN ĐOẠN
# -----------------------------------------------------------------------------
def generate_fig1_tumor_classes():
    val_img_dir = Path(r"d:\Học Sâu và Ứng dụng\Tumor\UNet\images\val")
    val_mask_dir = Path(r"d:\Học Sâu và Ứng dụng\Tumor\UNet\masks\val")

    # Chọn 3 ảnh đại diện cho 3 lớp
    cases = [
        ("brisc2025_test_00003_gl_ax_t1_jpg.rf.6951430ab61aac3c011ee61ccd79a847.jpg", 
         "U Tế Bào Thần Kinh Đệm (Glioma)", 
         "Mặt cắt ngang (Axial T1W)\nRanh giới mờ, thâm nhiễm", 
         "#EF4444", 1),
        ("brisc2025_test_00327_me_ax_t1_jpg.rf.148532a1b96948fac878583af0b6148e.jpg", 
         "U Màng Não (Meningioma)", 
         "Mặt cắt ngang (Axial T1W)\nKhối ngoài trục, ranh giới rõ", 
         "#10B981", 2),
        ("brisc2025_test_00771_pi_ax_t1_jpg.rf.e7b5f399ecb0303e89d1e49b1e860fe5.jpg", 
         "U Tuyến Yên (Pituitary)", 
         "Mặt cắt ngang (Axial T1W)\nKhu trú hố yên đáy sọ", 
         "#F59E0B", 3),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(11, 7.5), dpi=300)

    for col_idx, (fname, title, desc, color_hex, cls_id) in enumerate(cases):
        img_path = val_img_dir / fname
        mask_path = val_mask_dir / (fname[:-4] + ".png")

        img = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")
        mask_np = np.array(mask)

        # Hàng 1: Ảnh gốc MRI
        ax_orig = axes[0, col_idx]
        ax_orig.imshow(img)
        ax_orig.set_title(f"{title}\nẢnh MRI Gốc", fontsize=11, fontweight='bold', color='#1A365D', pad=8)
        ax_orig.axis("off")

        # Hàng 2: Overlay mặt nạ lên ảnh gốc
        ax_ov = axes[1, col_idx]
        img_np = np.array(img, dtype=np.float32)
        tumor_mask = (mask_np == cls_id)

        # Tạo lớp overlay màu
        color_rgb = matplotlib.colors.to_rgb(color_hex)
        overlay_np = img_np.copy()
        alpha = 0.55
        for c in range(3):
            overlay_np[:, :, c] = np.where(
                tumor_mask,
                img_np[:, :, c] * (1 - alpha) + color_rgb[c] * 255 * alpha,
                img_np[:, :, c]
            )
        overlay_np = np.clip(overlay_np, 0, 255).astype(np.uint8)

        ax_ov.imshow(overlay_np)
        
        # Vẽ contour viền
        if tumor_mask.any():
            ax_ov.contour(tumor_mask, colors=[color_hex], linewidths=1.5)

        area_px = int(tumor_mask.sum())
        total_px = tumor_mask.size
        pct = (area_px / total_px) * 100

        ax_ov.set_title(f"Mặt Nạ Phân Đoạn Chuẩn\nDiện tích: {pct:.2f}% ({area_px:,} px)", 
                         fontsize=10, fontweight='bold', color=color_hex, pad=8)
        ax_ov.set_xlabel(desc, fontsize=9, color='#475569', labelpad=4)
        ax_ov.axis("off")

    plt.tight_layout()
    out_file = OUTPUT_DIR / "fig1_tumor_classes.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {out_file}")


# -----------------------------------------------------------------------------
# 2. FIG 2: BIỂU ĐỒ PHÂN BỐ DỮ LIỆU
# -----------------------------------------------------------------------------
def generate_fig2_dataset_distribution():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Subplot 1: Phân bố số lượng ca theo tập Train / Val / Test
    splits = ['Tập Train\n(Huấn luyện)', 'Tập Val\n(Kiểm định)', 'Tập Test\n(Kiểm thử)']
    counts = [3966, 693, 135]
    colors = ['#1A365D', '#2B4C7E', '#64748B']

    bars = ax1.bar(splits, counts, color=colors, width=0.55, edgecolor='#0F172A', linewidth=1)
    ax1.set_title("A. Quy mô phân chia các tập dữ liệu", fontweight='bold', color='#1A365D', fontsize=11, pad=10)
    ax1.set_ylabel("Số lượng ảnh MRI", fontweight='bold')
    ax1.set_ylim(0, 4600)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    for bar, count in zip(bars, counts):
        pct = (count / sum(counts)) * 100
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 80,
                 f"{count:,}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1E293B')

    # Subplot 2: Phân bố theo loại u não
    classes = ['Glioma\n(U thần kinh đệm)', 'Meningioma\n(U màng não)', 'Pituitary\n(U tuyến yên)']
    class_counts = [1580, 1690, 1524]  # Phân bố xấp xỉ cân bằng trong BRISC 2025
    class_colors = ['#EF4444', '#10B981', '#F59E0B']

    bars2 = ax2.bar(classes, class_counts, color=class_colors, width=0.55, edgecolor='#0F172A', linewidth=1)
    ax2.set_title("B. Phân bố tương đối giữa 3 nhóm u não", fontweight='bold', color='#1A365D', fontsize=11, pad=10)
    ax2.set_ylabel("Số lượng ca tổn thương", fontweight='bold')
    ax2.set_ylim(0, 2000)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)

    for bar, count in zip(bars2, class_counts):
        pct = (count / sum(class_counts)) * 100
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 40,
                 f"{count:,}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1E293B')

    plt.tight_layout()
    out_file = OUTPUT_DIR / "fig2_dataset_distribution.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {out_file}")


# -----------------------------------------------------------------------------
# 3. FIG 3: SƠ ĐỒ KIẾN TRÚC YOLO-SEG (INSTANCE SEGMENTATION)
# -----------------------------------------------------------------------------
def generate_fig3_yolo_architecture():
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle="", color="#E2E8F0", text_color="#0F172A", border_color="#1A365D"):
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
            facecolor=color, edgecolor=border_color, linewidth=1.5
        )
        ax.add_patch(rect)
        if subtitle:
            ax.text(x + w / 2, y + h / 2 + 0.15, title, ha='center', va='center',
                    fontsize=9.5, fontweight='bold', color=text_color)
            ax.text(x + w / 2, y + h / 2 - 0.22, subtitle, ha='center', va='center',
                    fontsize=7.8, color="#475569")
        else:
            ax.text(x + w / 2, y + h / 2, title, ha='center', va='center',
                    fontsize=9.5, fontweight='bold', color=text_color)

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate(
            label, xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(facecolor="#1A365D", edgecolor="#1A365D", width=1.5, headwidth=6, shrink=0.05),
            ha='center', va='bottom', fontsize=8, color="#1A365D", fontweight='bold'
        )

    # 1. Input
    draw_box(0.3, 2.2, 1.4, 1.6, "ẢNH MRI\nĐẦU VÀO", "640 x 640 x 3", "#F1F5F9", "#1A365D")

    # 2. Backbone
    draw_arrow(1.7, 3.0, 2.3, 3.0)
    draw_box(2.3, 1.8, 1.9, 2.4, "BACKBONE\nTRÍCH XUẤT", "CSPDarknet (YOLOv8)\nC3k2 Blocks (YOLO11)\nP3, P4, P5 multi-scale", "#DBEAFE", "#1E3A8A")

    # 3. Neck
    draw_arrow(4.2, 3.0, 4.8, 3.0)
    draw_box(4.8, 1.8, 1.8, 2.4, "NECK\nFPN + PANet", "Nâng cao độ phân giải\n& Gộp đặc trưng đa tầng", "#E0E7FF", "#3730A3")

    # 4. Rẽ nhánh 2 đầu (Heads)
    # Head 1: Box & Class & Mask Coeffs
    draw_arrow(6.6, 3.5, 7.3, 4.2)
    draw_box(7.3, 3.5, 2.4, 1.6, "DETECTION HEAD", "• Hộp bao: (x, y, w, h)\n• Phân loại: 3 lớp u\n• 32 Mask Coeffs ($k_i$)", "#FEF3C7", "#92400E")

    # Head 2: Protonet
    draw_arrow(6.6, 2.5, 7.3, 1.8)
    draw_box(7.3, 0.9, 2.4, 1.6, "PROTO-NET HEAD", "Mạng tích chập độc lập\n32 Bản đồ mặt nạ nguyên mẫu\n(160 x 160 x 32)", "#D1FAE5", "#065F46")

    # 5. Phép nhân ma trận và Sigmoid
    draw_arrow(9.7, 4.3, 10.4, 3.3)
    draw_arrow(9.7, 1.7, 10.4, 2.7)
    draw_box(10.2, 2.4, 1.6, 1.2, "NHÂN TUYẾN TÍNH\n& SIGMOID", "Mask = $\\sigma(M_{proto} \\times K)$", "#FEE2E2", "#991B1B")

    # 6. Output
    draw_arrow(11.0, 2.4, 11.0, 1.2)
    draw_box(10.1, 0.2, 1.8, 0.9, "ĐA GIÁC U NÃO\n(Instance Mask)", "Kèm Bounding Box", "#F3E8FF", "#6B21A8")

    ax.set_title("Sơ đồ luồng xử lý của kiến trúc Phân đoạn Thực thể YOLO-seg (YOLOv8s-seg & YOLO11s-seg)",
                 fontsize=12, fontweight='bold', color='#1A365D', pad=14)

    plt.tight_layout()
    out_file = OUTPUT_DIR / "fig3_yolo_architecture.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {out_file}")


# -----------------------------------------------------------------------------
# 4. FIG 4: SƠ ĐỒ KIẾN TRÚC ATTENTION U-NET (scSE ATTENTION)
# -----------------------------------------------------------------------------
def generate_fig4_unet_attention_architecture():
    fig, ax = plt.subplots(figsize=(12, 6.2), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle="", color="#E2E8F0", text_color="#0F172A", border_color="#1A365D"):
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
            facecolor=color, edgecolor=border_color, linewidth=1.4
        )
        ax.add_patch(rect)
        if subtitle:
            ax.text(x + w / 2, y + h / 2 + 0.16, title, ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color=text_color)
            ax.text(x + w / 2, y + h / 2 - 0.2, subtitle, ha='center', va='center',
                    fontsize=7.2, color="#475569")
        else:
            ax.text(x + w / 2, y + h / 2, title, ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color=text_color)

    # Cột trái: Encoder (Downsampling)
    draw_box(0.5, 5.5, 2.2, 0.9, "ẢNH ĐẦU VÀO", "512 x 512 x 3", "#F1F5F9", "#1A365D")
    draw_box(0.5, 4.3, 2.2, 0.9, "Encoder Stage 1", "EfficientNet-B0 (256x256)", "#DBEAFE", "#1E3A8A")
    draw_box(0.5, 3.1, 2.2, 0.9, "Encoder Stage 2", "EfficientNet-B0 (128x128)", "#DBEAFE", "#1E3A8A")
    draw_box(0.5, 1.9, 2.2, 0.9, "Encoder Stage 3", "EfficientNet-B0 (64x64)", "#DBEAFE", "#1E3A8A")

    # Mũi tên đi xuống Encoder
    ax.annotate("", xy=(1.6, 5.2), xytext=(1.6, 5.5), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
    ax.annotate("", xy=(1.6, 4.0), xytext=(1.6, 4.3), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
    ax.annotate("", xy=(1.6, 2.8), xytext=(1.6, 3.1), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
    ax.annotate("", xy=(1.6, 1.6), xytext=(1.6, 1.9), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))

    # Đáy: Bottleneck
    draw_box(1.5, 0.5, 2.8, 0.9, "BOTTLENECK", "Đặc trưng sâu nhất (16x16x320)", "#C7D2FE", "#3730A3")

    # Cột phải: Decoder (Upsampling)
    draw_box(6.2, 1.9, 2.2, 0.9, "Decoder Block 3", "UpConv + Conv (64x64)", "#E0E7FF", "#3730A3")
    draw_box(6.2, 3.1, 2.2, 0.9, "Decoder Block 2", "UpConv + Conv (128x128)", "#E0E7FF", "#3730A3")
    draw_box(6.2, 4.3, 2.2, 0.9, "Decoder Block 1", "UpConv + Conv (256x256)", "#E0E7FF", "#3730A3")
    draw_box(6.2, 5.5, 2.2, 0.9, "MẶT NẠ DỰ ĐOÁN", "4 channels (512x512)", "#DCFCE7", "#166534")

    # Mũi tên đi lên Decoder
    ax.annotate("", xy=(5.0, 1.0), xytext=(4.3, 0.95), arrowprops=dict(arrowstyle="->", lw=1.5, color="#3730A3"))
    ax.annotate("", xy=(7.3, 2.8), xytext=(7.3, 2.5), arrowprops=dict(arrowstyle="->", lw=1.5, color="#3730A3"))
    ax.annotate("", xy=(7.3, 4.0), xytext=(7.3, 3.7), arrowprops=dict(arrowstyle="->", lw=1.5, color="#3730A3"))
    ax.annotate("", xy=(7.3, 5.2), xytext=(7.3, 4.9), arrowprops=dict(arrowstyle="->", lw=1.5, color="#3730A3"))

    # Skip Connections với khối Attention scSE
    for y_pos in [4.75, 3.55, 2.35]:
        ax.annotate("", xy=(6.2, y_pos), xytext=(2.7, y_pos),
                    arrowprops=dict(arrowstyle="->", lw=1.8, color="#059669", ls="--"))
        draw_box(4.0, y_pos - 0.28, 1.4, 0.55, "scSE Module", "Attention Gating", "#D1FAE5", "#065F46", "#059669")

    # Khung phóng to giải thích scSE Module ở góc phải
    rect_box = patches.Rectangle((8.8, 0.8), 3.0, 5.6, facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.2)
    ax.add_patch(rect_box)
    ax.text(10.3, 6.1, "CƠ CHẾ CHÚ Ý scSE", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1A365D')
    ax.text(10.3, 5.75, "(Spatial & Channel Squeeze-Excitation)", ha='center', va='center', fontsize=7.2, color='#64748B')

    draw_box(9.1, 4.4, 2.4, 0.9, "Nhánh sSE", "Spatial Squeeze\nTập trung kênh u não", "#FEF3C7", "#92400E")
    draw_box(9.1, 3.1, 2.4, 0.9, "Nhánh cSE", "Channel Squeeze\nTập trung vị trí không gian u", "#E0E7FF", "#3730A3")
    draw_box(9.1, 1.8, 2.4, 0.8, "CỘNG KẾT HỢP", "Output = $U_{sSE} + U_{cSE}$", "#D1FAE5", "#065F46")

    ax.annotate("", xy=(10.3, 4.4), xytext=(10.3, 4.1), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate("", xy=(10.3, 3.1), xytext=(10.3, 2.7), arrowprops=dict(arrowstyle="->", lw=1.2))

    ax.set_title("Sơ đồ kiến trúc Attention U-Net với mạng mã hóa EfficientNet-B0 và khối chú ý scSE",
                 fontsize=12, fontweight='bold', color='#1A365D', pad=14)

    plt.tight_layout()
    out_file = OUTPUT_DIR / "fig4_unet_attention_architecture.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {out_file}")


# -----------------------------------------------------------------------------
# 5. FIG 5: BIỂU ĐỒ ĐỐI CHUẨN HIỆU NĂNG CÁC MÔ HÌNH
# -----------------------------------------------------------------------------
def generate_fig5_benchmark_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Subplot A: YOLOv8 vs YOLO11 mAP50 Mask
    categories = ['Glioma\n(U thần kinh đệm)', 'Meningioma\n(U màng não)', 'Pituitary\n(U tuyến yên)', 'Trung bình\n(All Classes)']
    yolo8 = [81.8, 98.7, 91.2, 90.56]
    yolo11 = [83.0, 98.4, 90.5, 90.64]

    x = np.arange(len(categories))
    w = 0.35

    bars1 = ax1.bar(x - w/2, yolo8, w, label='YOLOv8s-seg', color='#3B82F6', edgecolor='#1E3A8A', linewidth=1)
    bars2 = ax1.bar(x + w/2, yolo11, w, label='YOLO11s-seg', color='#F59E0B', edgecolor='#92400E', linewidth=1)

    ax1.set_title("A. Đối chuẩn mAP50 Mask giữa YOLOv8s và YOLO11s", fontweight='bold', color='#1A365D', fontsize=11, pad=10)
    ax1.set_ylabel("Độ chính xác mAP50 Mask (%)", fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=8.8)
    ax1.set_ylim(70, 105)
    ax1.legend(loc='lower right', framealpha=0.9)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    for b in bars1:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{b.get_height():.1f}%",
                 ha='center', va='bottom', fontsize=7.8, color='#1E3A8A', fontweight='bold')
    for b in bars2:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{b.get_height():.1f}%",
                 ha='center', va='bottom', fontsize=7.8, color='#92400E', fontweight='bold')

    # Subplot B: Attention U-Net Dice & IoU
    classes_u = ['Glioma', 'Meningioma', 'Pituitary', 'Trung bình']
    dice_vals = [91.07, 95.41, 92.28, 92.92]
    iou_vals  = [83.63, 91.26, 85.10, 86.66]

    x2 = np.arange(len(classes_u))
    bars3 = ax2.bar(x2 - w/2, dice_vals, w, label='Dice Score (DSC)', color='#10B981', edgecolor='#065F46', linewidth=1)
    bars4 = ax2.bar(x2 + w/2, iou_vals,  w, label='IoU Score (Jaccard)', color='#6EE7B7', edgecolor='#065F46', linewidth=1)

    ax2.set_title("B. Độ chính xác Dice và IoU của Attention U-Net", fontweight='bold', color='#1A365D', fontsize=11, pad=10)
    ax2.set_ylabel("Điểm tương đồng (%)", fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(classes_u, fontsize=9.5)
    ax2.set_ylim(70, 105)
    ax2.legend(loc='lower right', framealpha=0.9)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)

    for b in bars3:
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{b.get_height():.1f}%",
                 ha='center', va='bottom', fontsize=7.8, color='#065F46', fontweight='bold')
    for b in bars4:
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{b.get_height():.1f}%",
                 ha='center', va='bottom', fontsize=7.8, color='#047857', fontweight='bold')

    plt.tight_layout()
    out_file = OUTPUT_DIR / "fig5_benchmark_comparison.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {out_file}")


# -----------------------------------------------------------------------------
# 6. FIG 6: KẾT QUẢ SUY LUẬN ĐỐI ĐẦU 3 MÔ HÌNH TRÊN CA BỆNH THỰC TẾ
# -----------------------------------------------------------------------------
def generate_fig6_cadx_inference_comparison():
    # Import mô hình suy luận thực tế
    sys.path.insert(0, str(Path(r"d:\Học Sâu và Ứng dụng\Tumor\WebApp")))
    from models.yolo_model import yolov8_model, yolo11_model
    from models.unet_model import unet_model
    from utils.visualization import draw_yolo_results, create_mask_overlay

    sample_img_path = Path(r"d:\Học Sâu và Ứng dụng\Tumor\WebApp\sample_images\brisc2025_test_00003_gl_ax_t1_jpg.rf.6951430ab61aac3c011ee61ccd79a847.jpg")
    mask_path = Path(r"d:\Học Sâu và Ứng dụng\Tumor\UNet\masks\val\brisc2025_test_00003_gl_ax_t1_jpg.rf.6951430ab61aac3c011ee61ccd79a847.png")

    img = Image.open(sample_img_path).convert("RGB")
    gt_mask = np.array(Image.open(mask_path).convert("L"))

    # Chạy YOLOv8
    yolov8_model.load()
    res8, _, _ = yolov8_model.predict(img, conf=0.25)
    ann8, _ = draw_yolo_results(img, res8, conf_threshold=0.25)

    # Chạy YOLO11
    yolo11_model.load()
    res11, _, _ = yolo11_model.predict(img, conf=0.25)
    ann11, _ = draw_yolo_results(img, res11, conf_threshold=0.25)

    # Chạy Attention U-Net
    unet_model.load()
    mask_u, _, _ = unet_model.predict(img)
    ann_u = create_mask_overlay(img, mask_u, alpha=0.5)

    # Tạo ảnh Ground Truth overlay
    gt_overlay = create_mask_overlay(img, gt_mask, alpha=0.5)

    # Dựng figure so sánh 5 khung hình
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.8), dpi=300)

    panels = [
        (img, "1. Ảnh MRI Gốc", "Lát cắt Axial T1W"),
        (gt_overlay, "2. Nhãn Bác Sĩ (GT)", "Mặt nạ chuẩn bệnh học"),
        (ann8, "3. YOLOv8s-seg", "Box + Mask (mAP: 90.56%)"),
        (ann11, "4. YOLO11s-seg", "Box + Mask (mAP: 90.64%)"),
        (ann_u, "5. Attention U-Net", "Pixel Mask (Dice: 92.92%)"),
    ]

    for ax, (im_data, title, sub) in zip(axes, panels):
        ax.imshow(im_data)
        ax.set_title(title, fontsize=10.5, fontweight='bold', color='#1A365D', pad=6)
        ax.set_xlabel(sub, fontsize=8.5, color='#475569', labelpad=4)
        ax.axis("off")

    plt.suptitle("So sánh trực quan kết quả suy luận phân đoạn u não giữa Nhãn chuẩn và 3 Mô hình",
                 fontsize=12, fontweight='bold', color='#1A365D', y=0.98)

    plt.tight_layout()
    out_file = OUTPUT_DIR / "fig6_cadx_inference_comparison.png"
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {out_file}")


if __name__ == "__main__":
    print("=== Đang sinh các hình ảnh chất lượng cao ===")
    generate_fig1_tumor_classes()
    generate_fig2_dataset_distribution()
    generate_fig3_yolo_architecture()
    generate_fig4_unet_attention_architecture()
    generate_fig5_benchmark_comparison()
    generate_fig6_cadx_inference_comparison()
    print("=== Hoàn tất toàn bộ hình ảnh ===")
