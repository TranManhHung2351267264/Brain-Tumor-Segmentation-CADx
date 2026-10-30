import os
import json
import shutil
from pathlib import Path
from tqdm import tqdm

def convert():
    source_dir = Path(r"d:\Học Sâu và Ứng dụng\Tumor\Tumor.v1i.coco")
    dest_dir = Path(r"d:\Học Sâu và Ứng dụng\Tumor\tumor_yolo_seg")
    
    # Class mapping based on filename metadata
    # 0: Glioma (gl), 1: Meningioma (me), 2: Pituitary (pi)
    class_map = {
        "gl": 0,
        "me": 1,
        "pi": 2
    }
    class_names = ["Glioma", "Meningioma", "Pituitary"]
    
    # Create target directories
    for split_target in ["train", "val"]:
        (dest_dir / "images" / split_target).mkdir(parents=True, exist_ok=True)
        (dest_dir / "labels" / split_target).mkdir(parents=True, exist_ok=True)
        
    stats = {
        "train": {"total": 0, "Glioma": 0, "Meningioma": 0, "Pituitary": 0, "skipped": 0},
        "val": {"total": 0, "Glioma": 0, "Meningioma": 0, "Pituitary": 0, "skipped": 0}
    }
    
    split_mapping = {
        "train": "train",
        "valid": "val"
    }
    
    for split_src, split_dst in split_mapping.items():
        coco_file = source_dir / split_src / "_annotations.coco.json"
        print(f"\nProcessing {split_src} -> {split_dst}...")
        
        with open(coco_file, "r", encoding="utf-8") as f:
            coco_data = json.load(f)
            
        # Map image_id to annotations
        img_annos = {}
        for ann in coco_data["annotations"]:
            img_id = ann["image_id"]
            if img_id not in img_annos:
                img_annos[img_id] = []
            img_annos[img_id].append(ann)
            
        for img_info in coco_data["images"]:
            file_name = img_info["file_name"]
            img_id = img_info["id"]
            img_w = float(img_info.get("width", 640))
            img_h = float(img_info.get("height", 640))
            
            # Identify tumor subtype from filename
            # Example: brisc2025_train_04496_pi_sa_t1_jpg.rf.3ae366e03ae5e2cd5763aef5502490af.jpg
            base = file_name.split(".rf.")[0]
            parts = base.split("_")
            
            subtype = None
            if len(parts) >= 4 and parts[3] in class_map:
                subtype = parts[3]
            elif "kaggle" in file_name or file_name.startswith("Y"):
                # Skip Kaggle images because subtype is unknown
                stats[split_dst]["skipped"] += 1
                continue
            else:
                stats[split_dst]["skipped"] += 1
                continue
                
            cls_id = class_map[subtype]
            cls_name = class_names[cls_id]
            stats[split_dst][cls_name] += 1
            stats[split_dst]["total"] += 1
            
            # Destination image path
            src_img_path = source_dir / split_src / file_name
            dst_img_path = dest_dir / "images" / split_dst / file_name
            
            # Copy image
            shutil.copy2(src_img_path, dst_img_path)
            
            # Prepare label file
            label_filename = Path(file_name).stem + ".txt"
            dst_label_path = dest_dir / "labels" / split_dst / label_filename
            
            annos = img_annos.get(img_id, [])
            label_lines = []
            
            for ann in annos:
                seg = ann.get("segmentation", [])
                if not seg:
                    # Fallback to bbox if no segmentation: bbox [x, y, w, h]
                    bx, by, bw, bh = ann.get("bbox", [0, 0, 0, 0])
                    # Polygon for bbox: 4 points
                    poly = [bx, by, bx + bw, by, bx + bw, by + bh, bx, by + bh]
                    seg = [poly]
                    
                for poly in seg:
                    if len(poly) < 6: # need at least 3 points (x, y)
                        continue
                    # Normalize coordinates
                    norm_coords = []
                    for i in range(0, len(poly), 2):
                        nx = min(max(poly[i] / img_w, 0.0), 1.0)
                        ny = min(max(poly[i+1] / img_h, 0.0), 1.0)
                        norm_coords.append(f"{nx:.6f}")
                        norm_coords.append(f"{ny:.6f}")
                    label_lines.append(f"{cls_id} " + " ".join(norm_coords))
                    
            with open(dst_label_path, "w", encoding="utf-8") as f:
                f.write("\n".join(label_lines) + "\n")
                
    # Create data.yaml
    yaml_content = f"""# YOLOv8 Brain Tumor Segmentation Dataset (3-classes)
path: tumor_yolo_seg
train: images/train
val: images/val

names:
  0: Glioma
  1: Meningioma
  2: Pituitary
"""
    yaml_path = dest_dir / "data.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
        
    print("\n" + "="*50)
    print("CONVERSION COMPLETE!")
    print(f"Data saved to: {dest_dir}")
    print(f"data.yaml created at: {yaml_path}")
    print("Statistics:")
    print("  Train set:", stats["train"])
    print("  Validation set:", stats["val"])
    print("="*50)

if __name__ == "__main__":
    convert()
