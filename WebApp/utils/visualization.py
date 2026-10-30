"""
Trực quan hóa kết quả phân đoạn — Visualization utilities
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import colorsys
from typing import Optional, List, Tuple, Dict

# ── Bảng màu chuẩn ─────────────────────────────────────────────────────────
CLASS_COLORS = {
    0: (0,   0,   0),    # Background — đen
    1: (255,  50,  50),  # Glioma     — đỏ
    2: (50,  200,  80),  # Meningioma — xanh lá
    3: (255, 165,   0),  # Pituitary  — cam
}

CLASS_NAMES_VI = {
    0: "Nền (Background)",
    1: "U Glioma",
    2: "U Màng Não (Meningioma)",
    3: "U Tuyến Yên (Pituitary)",
}

CLASS_NAMES_EN = {
    0: "Background",
    1: "Glioma",
    2: "Meningioma",
    3: "Pituitary",
}

CLASS_COLORS_HEX = {
    0: "#000000",
    1: "#FF3232",
    2: "#32C850",
    3: "#FFA500",
}

# Mô tả lâm sàng ngắn gọn
CLASS_DESCRIPTIONS = {
    1: "U não nguyên phát, phát sinh từ tế bào thần kinh đệm. Có thể ác tính.",
    2: "U màng não, thường lành tính, phát sinh từ màng bao quanh não.",
    3: "U tuyến yên, thường lành tính, ảnh hưởng đến nội tiết tố.",
}


def create_mask_overlay(
    original: Image.Image,
    class_mask: np.ndarray,  # HxW, giá trị 0-3
    alpha: float = 0.45,
    ignore_background: bool = True,
) -> Image.Image:
    """
    Tạo ảnh overlay với mask màu sắc theo lớp.
    Returns: PIL Image RGB có mask đè lên ảnh gốc.
    """
    h, w = class_mask.shape
    orig_rgb = original.convert("RGB").resize((w, h), Image.LANCZOS)
    orig_arr = np.array(orig_rgb, dtype=np.float32)

    color_mask = np.zeros((h, w, 3), dtype=np.float32)
    has_tumor = False

    for cls_id, color in CLASS_COLORS.items():
        if ignore_background and cls_id == 0:
            continue
        region = class_mask == cls_id
        if region.any():
            color_mask[region] = color
            if cls_id != 0:
                has_tumor = True

    # Alpha blend chỉ tại vùng có mask tumor
    tumor_mask_bool = (color_mask.sum(axis=2) > 0)
    result = orig_arr.copy()
    result[tumor_mask_bool] = (
        orig_arr[tumor_mask_bool] * (1 - alpha) +
        color_mask[tumor_mask_bool] * alpha
    )
    result = np.clip(result, 0, 255).astype(np.uint8)

    # Viền sắc nét quanh vùng tumor
    result_img = Image.fromarray(result)
    if has_tumor:
        result_img = _add_contour(result_img, class_mask)

    return result_img


def _add_contour(img: Image.Image, class_mask: np.ndarray) -> Image.Image:
    """Vẽ đường viền mảnh quanh các vùng phân đoạn."""
    from PIL import ImageFilter
    draw = ImageDraw.Draw(img)
    for cls_id in [1, 2, 3]:
        binary = (class_mask == cls_id).astype(np.uint8) * 255
        if binary.max() == 0:
            continue
        pil_bin = Image.fromarray(binary, mode="L")
        # Đường biên = hiệu của dilation và erosion
        dilated = pil_bin.filter(ImageFilter.MaxFilter(3))
        eroded  = pil_bin.filter(ImageFilter.MinFilter(3))
        contour = np.array(dilated, dtype=np.int16) - np.array(eroded, dtype=np.int16)
        contour_px = np.argwhere(contour > 0)
        color = CLASS_COLORS.get(cls_id, (255, 255, 255))
        for (py, px) in contour_px:
            draw.point((px, py), fill=color)
    return img


def draw_yolo_results(
    original: Image.Image,
    results,
    conf_threshold: float = 0.25,
) -> Tuple[Image.Image, List[Dict]]:
    """
    Vẽ kết quả YOLO (bounding box + polygon mask) lên ảnh.
    Returns: (annotated_image, list_of_detections)
    """
    img = original.convert("RGB").copy()
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    detections = []

    if results is None or len(results) == 0:
        return img, detections

    result = results[0]

    # Polygon masks
    if result.masks is not None and result.boxes is not None:
        masks_xy = result.masks.xy      # list of polygon arrays
        boxes    = result.boxes
        for i, (poly, box) in enumerate(zip(masks_xy, boxes)):
            conf  = float(box.conf[0])
            cls_id_yolo = int(box.cls[0])   # YOLO: 0=Glioma,1=Mening,2=Pit
            cls_id_app  = cls_id_yolo + 1   # App mapping 1-3

            if conf < conf_threshold:
                continue

            color = CLASS_COLORS.get(cls_id_app, (255, 255, 255))
            color_a = color + (120,)  # RGBA với alpha

            # Vẽ polygon fill
            if len(poly) >= 3:
                pts = [(float(x), float(y)) for x, y in poly]
                draw.polygon(pts, fill=color_a, outline=color + (255,))

            # Bounding box
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            draw.rectangle([x1, y1, x2, y2], outline=color + (220,), width=2)

            # Label
            label = f"{CLASS_NAMES_EN[cls_id_app]} {conf:.0%}"
            _draw_label(draw, label, x1, y1, color)

            # Tính diện tích pixel từ polygon
            area_px = _polygon_area(poly)
            area_pct = (area_px / (W * H)) * 100

            detections.append({
                "class_id":   cls_id_app,
                "class_name": CLASS_NAMES_EN[cls_id_app],
                "class_vi":   CLASS_NAMES_VI[cls_id_app],
                "confidence": conf,
                "area_px2":   area_px,
                "area_pct":   area_pct,
                "bbox":       [x1, y1, x2, y2],
            })

    return img, detections


def _polygon_area(pts: np.ndarray) -> float:
    """Shoelace formula for polygon area."""
    if len(pts) < 3:
        return 0.0
    x = pts[:, 0]
    y = pts[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def _draw_label(draw: ImageDraw.ImageDraw, text: str, x: float, y: float, color: Tuple):
    """Vẽ nhãn chữ trắng nền màu trên bounding box."""
    # Simplified: dùng font mặc định
    padding = 3
    tw, th = 120, 16  # estimate
    box_y0 = max(0, y - th - padding * 2)
    box_y1 = y
    draw.rectangle([x, box_y0, x + tw + padding * 2, box_y1],
                   fill=color + (220,))
    draw.text((x + padding, box_y0 + padding), text, fill=(255, 255, 255))


def compute_class_stats(class_mask: np.ndarray) -> Dict:
    """Tính thống kê diện tích từng lớp trong mask."""
    total_px = class_mask.size
    stats = {}
    for cls_id in [1, 2, 3]:
        region = (class_mask == cls_id)
        px_count = int(region.sum())
        pct = (px_count / total_px) * 100
        stats[cls_id] = {
            "class_id":   cls_id,
            "class_name": CLASS_NAMES_EN[cls_id],
            "class_vi":   CLASS_NAMES_VI[cls_id],
            "area_px2":   px_count,
            "area_pct":   pct,
        }
    return stats
