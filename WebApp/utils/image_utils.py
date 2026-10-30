"""
Tiện ích xử lý ảnh — Image processing utilities
"""
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def load_image_from_upload(uploaded_file) -> Image.Image:
    """Đọc ảnh từ Streamlit file uploader, trả về PIL Image RGB."""
    img_bytes = uploaded_file.read()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return img


def resize_image(img: Image.Image, target_size: int = 640) -> Image.Image:
    """Giữ nguyên tỉ lệ khung hình, resize để cạnh dài = target_size."""
    w, h = img.size
    if max(w, h) == target_size:
        return img
    scale = target_size / max(w, h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return img.resize((new_w, new_h), Image.LANCZOS)


def pil_to_numpy(img: Image.Image) -> np.ndarray:
    """PIL Image -> numpy array HWC uint8."""
    return np.array(img)


def numpy_to_pil(arr: np.ndarray) -> Image.Image:
    """Numpy array HWC uint8 -> PIL Image."""
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """Chuyển PIL Image -> bytes để download."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def blend_overlay(original: Image.Image, mask_overlay: Image.Image, alpha: float = 0.45) -> Image.Image:
    """Blend ảnh gốc với overlay mask."""
    original_rgba = original.convert("RGBA")
    overlay_rgba = mask_overlay.convert("RGBA")
    # Resize overlay to match original if needed
    if original_rgba.size != overlay_rgba.size:
        overlay_rgba = overlay_rgba.resize(original_rgba.size, Image.NEAREST)
    blended = Image.blend(original_rgba, overlay_rgba, alpha=alpha)
    return blended.convert("RGB")
