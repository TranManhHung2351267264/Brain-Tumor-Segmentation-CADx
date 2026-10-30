"""
Script: convert_coco_to_unet_masks.py
Mục đích: Chuyển đổi nhãn đa giác (polygon) trong file COCO JSON
          sang ảnh mặt nạ nhị phân (Binary Mask PNG) chuẩn cho bài toán U-Net Segmentation.

Cấu trúc đầu ra (UNet/):
    UNet/
    ├── images/
    │   ├── train/   <- Ảnh MRI gốc (copy từ Tumor.v1i.coco)
    │   └── val/
    ├── masks/
    │   ├── train/   <- Ảnh mask PNG (giá trị pixel: 0=Nền, 1=Glioma, 2=Meningioma, 3=Pituitary)
    │   └── val/
    └── class_info.txt

QUAN TRỌNG:
- Dữ liệu nguồn gốc (Tumor.v1i.coco) KHÔNG bị chỉnh sửa.
- Dữ liệu YOLO (YOLO/) KHÔNG bị chỉnh sửa.
- Toàn bộ output đều lưu riêng biệt vào thư mục UNet/.
"""

import os
import sys
import json
import shutil
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')

# ===================== CẤU HÌNH =====================
SOURCE_COCO = Path(r"d:\Học Sâu và Ứng dụng\Tumor\Tumor.v1i.coco")
DEST_UNET   = Path(r"d:\Học Sâu và Ứng dụng\Tumor\UNet")

# Class mapping: lấy từ tên file (giống như trong convert_coco_to_yolo_seg.py)
# Pixel value trong Mask PNG: 0 = Nền (Background), 1 = Glioma, 2 = Meningioma, 3 = Pituitary
CLASS_MAP = {
    "gl": 1,  # Glioma
    "me": 2,  # Meningioma
    "pi": 3,  # Pituitary
}
CLASS_NAMES = {1: "Glioma", 2: "Meningioma", 3: "Pituitary"}

SPLIT_MAP = {"train": "train", "valid": "val"}
# ====================================================

def extract_subtype(filename: str) -> str | None:
    """Trích xuất mã loại u não từ tên file."""
    base = filename.split(".rf.")[0]
    parts = base.split("_")
    if len(parts) >= 4 and parts[3] in CLASS_MAP:
        return parts[3]
    return None  # Không xác định được (ảnh Kaggle Y-series)


def create_mask_png(coco_annos: list, img_w: int, img_h: int, class_pixel: int) -> Image.Image:
    """
    Tạo ảnh mask đơn kênh (grayscale) từ danh sách annotations.
    - Nền (background): pixel = 0
    - Vùng khối u:       pixel = class_pixel (1, 2 hoặc 3)
    """
    mask = Image.new("L", (img_w, img_h), 0)  # "L" = grayscale, mặc định = 0 (nền)
    draw = ImageDraw.Draw(mask)

    for ann in coco_annos:
        seg = ann.get("segmentation", [])
        if not seg:
            # Fallback sang bbox nếu không có polygon
            bx, by, bw, bh = ann.get("bbox", [0, 0, 0, 0])
            bbox_poly = [bx, by, bx + bw, by, bx + bw, by + bh, bx, by + bh]
            seg = [bbox_poly]

        for poly in seg:
            if len(poly) < 6:
                continue
            # Chuyển list phẳng [x1, y1, x2, y2, ...] sang list tuple [(x1, y1), ...]
            coords = [(poly[i], poly[i + 1]) for i in range(0, len(poly), 2)]
            # Tô màu vùng đa giác với giá trị pixel = class_pixel
            draw.polygon(coords, fill=class_pixel)

    return mask


def process_split(split_src: str, split_dst: str, stats: dict):
    """Xử lý một split (train / valid)."""
    coco_file = SOURCE_COCO / split_src / "_annotations.coco.json"
    img_src_dir = SOURCE_COCO / split_src
    img_dst_dir = DEST_UNET / "images" / split_dst
    msk_dst_dir = DEST_UNET / "masks"  / split_dst

    print(f"\n{'='*55}")
    print(f"  Xử lý split: {split_src} --> {split_dst}")
    print(f"{'='*55}")

    with open(coco_file, "r", encoding="utf-8") as f:
        coco = json.load(f)

    # Map image_id -> list annotations
    img_to_annos = {}
    for ann in coco["annotations"]:
        img_to_annos.setdefault(ann["image_id"], []).append(ann)

    skipped, processed = 0, 0

    for img_info in coco["images"]:
        fn     = img_info["file_name"]
        img_id = img_info["id"]
        img_w  = img_info.get("width",  640)
        img_h  = img_info.get("height", 640)

        # --- Bước 1: Xác định loại u não từ tên file ---
        subtype = extract_subtype(fn)
        if subtype is None:
            # Bỏ qua ảnh Kaggle Y-series (không rõ loại u)
            skipped += 1
            continue

        class_pixel = CLASS_MAP[subtype]

        # --- Bước 2: Copy ảnh gốc vào UNet/images/ ---
        src_img = img_src_dir / fn
        dst_img = img_dst_dir / fn
        shutil.copy2(src_img, dst_img)

        # --- Bước 3: Tạo file Mask PNG vào UNet/masks/ ---
        annos = img_to_annos.get(img_id, [])
        mask_img = create_mask_png(annos, img_w, img_h, class_pixel)

        # Lưu mask với tên file giống ảnh gốc (thay đuôi .jpg -> .png)
        mask_filename = Path(fn).stem + ".png"
        dst_mask = msk_dst_dir / mask_filename
        mask_img.save(dst_mask)

        processed += 1
        stats[split_dst][CLASS_NAMES[class_pixel]] += 1

    stats[split_dst]["total_processed"] = processed
    stats[split_dst]["total_skipped"]   = skipped
    print(f"  Processed: {processed} | Skipped (no-label): {skipped}")


def main():
    # --- Tạo cấu trúc thư mục UNet ---
    for split in ["train", "val"]:
        (DEST_UNET / "images" / split).mkdir(parents=True, exist_ok=True)
        (DEST_UNET / "masks"  / split).mkdir(parents=True, exist_ok=True)

    stats = {
        "train": {"Glioma": 0, "Meningioma": 0, "Pituitary": 0},
        "val":   {"Glioma": 0, "Meningioma": 0, "Pituitary": 0},
    }

    for split_src, split_dst in SPLIT_MAP.items():
        process_split(split_src, split_dst, stats)

    # --- Ghi file thông tin lớp ---
    class_info = (
        "# UNet Mask Label Encoding\n"
        "# Pixel Value | Class Name   | Hex Color (visualization)\n"
        "# -----------   ----------     -------------------------\n"
        "#     0        | Background   | #000000 (Black)\n"
        "#     1        | Glioma       | #FF0000 (Red)\n"
        "#     2        | Meningioma   | #00FF00 (Green)\n"
        "#     3        | Pituitary    | #FFA500 (Orange)\n"
    )
    (DEST_UNET / "class_info.txt").write_text(class_info, encoding="utf-8")

    # --- In kết quả ---
    print("\n" + "="*55)
    print("  CHUYỂN ĐỔI HOÀN TẤT!")
    print("="*55)
    print(f"  Lưu tại: {DEST_UNET}")
    print()
    for split, st in stats.items():
        print(f"  [{split}]")
        print(f"    Total processed : {st['total_processed']}")
        print(f"    Total skipped   : {st['total_skipped']}")
        print(f"    Glioma          : {st['Glioma']}")
        print(f"    Meningioma      : {st['Meningioma']}")
        print(f"    Pituitary       : {st['Pituitary']}")
        print()
    print("  LUU Y:")
    print("  - Tumor.v1i.coco/  (goc) : NGUYEN VEN, KHONG bi sua doi")
    print("  - YOLO/            (YOLO): NGUYEN VEN, KHONG bi sua doi")
    print("  - UNet/            (moi) : Da tao rieng biet, doc lap")
    print("="*55)


if __name__ == "__main__":
    main()
