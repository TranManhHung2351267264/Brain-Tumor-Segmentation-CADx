"""
Script chuẩn hóa và chuyển đổi dữ liệu U não (BRISC 2025)
sang định dạng nạp dữ liệu MedSAM3 (Concept-Guided Promptable Segmentation).
"""

import os
import sys
import json
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CLASS_MAP = {
    "gl": {"id": 1, "name": "Glioma", "concept": "brain glioma tumor", "concept_id": 0},
    "me": {"id": 2, "name": "Meningioma", "concept": "brain meningioma tumor", "concept_id": 1},
    "pi": {"id": 3, "name": "Pituitary", "concept": "brain pituitary adenoma", "concept_id": 2}
}

def create_medsam3_dataset_metadata(base_dir=r"D:\Học Sâu và Ứng dụng\Tumor"):
    base_path = Path(base_dir)
    unet_dir = base_path / "UNet"
    out_dir = base_path / "medsam3" / "dataset_metadata"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {}
    for split in ["train", "val"]:
        img_dir = unet_dir / "images" / split
        mask_dir = unet_dir / "masks" / split

        if not img_dir.exists() or not mask_dir.exists():
            print(f"Bỏ qua tập {split}: không tìm thấy thư mục ảnh/mask")
            continue

        samples = []
        class_counts = {"Glioma": 0, "Meningioma": 0, "Pituitary": 0}

        img_files = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))
        for img_path in img_files:
            stem = img_path.stem
            # Mask corresponding file
            mask_path = mask_dir / f"{stem}.png"
            if not mask_path.exists():
                mask_path = mask_dir / f"{stem}.jpg"
            if not mask_path.exists():
                continue

            # Parse subtype: e.g. brisc2025_train_00001_gl_ax_t1
            parts = stem.split("_")
            subtype = None
            for p in parts:
                if p in CLASS_MAP:
                    subtype = p
                    break

            if not subtype:
                # Default generic
                class_info = {"id": 1, "name": "Brain Tumor", "concept": "brain tumor", "concept_id": 0}
            else:
                class_info = CLASS_MAP[subtype]

            class_counts[class_info["name"]] = class_counts.get(class_info["name"], 0) + 1

            sample_entry = {
                "id": stem,
                "image_path": str(img_path.resolve()).replace("\\", "/"),
                "mask_path": str(mask_path.resolve()).replace("\\", "/"),
                "class_id": class_info["id"],
                "class_name": class_info["name"],
                "text_concept": class_info["concept"],
                "concept_id": class_info["concept_id"]
            }
            samples.append(sample_entry)

        out_json = out_dir / f"{split}_samples.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)

        summary[split] = {
            "total_samples": len(samples),
            "class_counts": class_counts,
            "json_path": str(out_json.resolve()).replace("\\", "/")
        }
        print(f"Đã tạo siêu dữ liệu MedSAM3 [{split}]: {len(samples)} mẫu -> {out_json}")
        for cname, count in class_counts.items():
            print(f"  - {cname}: {count} mẫu")

    summary_file = out_dir / "dataset_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nTổng kết đã lưu tại: {summary_file}")
    return summary

if __name__ == "__main__":
    create_medsam3_dataset_metadata()
