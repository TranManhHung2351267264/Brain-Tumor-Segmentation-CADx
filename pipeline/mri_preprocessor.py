"""
mri_preprocessor.py
Module tiền xử lý ảnh cộng hưởng từ (MRI) chuyên sâu cho bài toán phân đoạn u não:
1. Bóc tách hộp sọ (Skull Stripping / Brain Mask Extraction)
2. Cân bằng tương phản thích ứng (Adaptive CLAHE Contrast Enhancement)
3. Chuẩn hóa cường độ tín hiệu (Z-score / Min-Max Intensity Normalization)
4. Trích xuất bản đồ biên (Edge Distance Map) phục vụ Boundary Loss
"""

import cv2
import numpy as np
from PIL import Image

class MRISkullStripper:
    """
    Thuật toán bóc tách hộp sọ (Skull Stripping) không cần trọng số nặng:
    Sử dụng kết hợp Otsu thresholding, phép toán hình thái học (Morphological Closing/Opening)
    và lọc thành phần liên thông lớn nhất (Largest Connected Component) để giữ lại nhu mô não,
    loại bỏ hoàn toàn tín hiệu xương sọ, da đầu và nền đen nhiễu.
    """
    def __init__(self, kernel_size=5, num_erosions=2, num_dilations=2):
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        self.num_erosions = num_erosions
        self.num_dilations = num_dilations

    def get_brain_mask(self, gray_img: np.ndarray) -> np.ndarray:
        """
        Trích xuất mặt nạ nhu mô não (Binary Mask).
        gray_img: np.ndarray (H, W), uint8 [0, 255]
        """
        # 1. Làm mờ nhẹ Gaussian để giảm nhiễu hạt Rician của máy MRI
        blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)

        # 2. Phân ngưỡng tự động Otsu để tách foreground (đầu + sọ) khỏi nền đen
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 3. Tìm thành phần liên thông lớn nhất (toàn bộ hộp sọ và não)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        if num_labels > 1:
            # Bỏ qua label 0 (background), tìm label có diện tích lớn nhất
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            skull_mask = (labels == largest_label).astype(np.uint8) * 255
        else:
            skull_mask = binary

        # 4. Phép ăn mòn (Erosion) để tách rời mô não khỏi viền xương sọ mỏng
        eroded = cv2.erode(skull_mask, self.kernel, iterations=self.num_erosions)

        # 5. Lọc lại thành phần liên thông lớn nhất của nhu mô não bên trong
        num_labels_inner, labels_inner, stats_inner, _ = cv2.connectedComponentsWithStats(eroded, connectivity=8)
        if num_labels_inner > 1:
            largest_inner = 1 + np.argmax(stats_inner[1:, cv2.CC_STAT_AREA])
            brain_core = (labels_inner == largest_inner).astype(np.uint8) * 255
        else:
            brain_core = eroded

        # 6. Giãn nở (Dilation) để bù lại thể tích vỏ não và u ngoại vi sát màng não
        brain_mask = cv2.dilate(brain_core, self.kernel, iterations=self.num_dilations + 1)
        
        # 7. Lấp đầy lỗ rỗng (Fill holes) bên trong não
        contours, _ = cv2.findContours(brain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled_mask = np.zeros_like(brain_mask)
        cv2.drawContours(filled_mask, contours, -1, 255, thickness=cv2.FILLED)

        return filled_mask

    def strip(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Bóc tách hộp sọ từ ảnh màu BGR / RGB.
        """
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if len(img_bgr.shape) == 3 else img_bgr
        mask = self.get_brain_mask(gray)
        # Áp mặt nạ lên từng kênh
        stripped = cv2.bitwise_and(img_bgr, img_bgr, mask=mask)
        return stripped, mask


class MRIContrastEnhancer:
    """
    Tăng cường độ tương phản mô mềm (Contrast Enhancement) cho ảnh MRI sọ não:
    Sử dụng Contrast Limited Adaptive Histogram Equalization (CLAHE) trên kênh độ sáng L (trong không gian Lab).
    Giúp làm nổi bật viền thâm nhiễm mờ giữa mô u và chất xám / chất trắng bình thường.
    """
    def __init__(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def enhance(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Tăng tương phản mà không làm bão hòa (cháy) vùng bắt thuốc cản quang.
        """
        if len(img_bgr.shape) == 3:
            lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_enhanced = self.clahe.apply(l)
            lab_enhanced = cv2.merge([l_enhanced, a, b])
            return cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        else:
            return self.clahe.apply(img_bgr)


class MRIIntensityNormalizer:
    """
    Chuẩn hóa cường độ tín hiệu MRI:
    - Min-Max Scaling về [0, 1]
    - Z-Score Normalization (loại bỏ giá trị ngoại lai 1% và 99% percentile)
    """
    @staticmethod
    def zscore_normalize(img: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
        """
        Chuẩn hóa z-score chỉ trên vùng nhu mô não (bỏ qua nền đen 0).
        """
        float_img = img.astype(np.float32)
        if mask is not None:
            valid_pixels = float_img[mask > 0]
        else:
            valid_pixels = float_img[float_img > 0]

        if len(valid_pixels) == 0:
            return float_img

        # Cắt ngưỡng ngoại lai 1% và 99% percentile
        p1, p99 = np.percentile(valid_pixels, (1, 99))
        clipped = np.clip(float_img, p1, p99)

        mean = np.mean(clipped[clipped > 0]) if np.any(clipped > 0) else 0.0
        std = np.std(clipped[clipped > 0]) if np.any(clipped > 0) else 1.0
        if std == 0:
            std = 1.0

        normalized = (clipped - mean) / std
        return normalized


class MRIPipeline:
    """
    Toàn bộ quy trình tiền xử lý ảnh MRI đầu cuối (End-to-End MRI Preprocessing Pipeline):
    1. Skull Stripping
    2. CLAHE Contrast Enhancement
    3. Min-Max Normalization
    """
    def __init__(self):
        self.stripper = MRISkullStripper()
        self.enhancer = MRIContrastEnhancer()
        self.normalizer = MRIIntensityNormalizer()

    def process(self, img_bgr: np.ndarray, apply_skull_strip: bool = True, apply_clahe: bool = True):
        processed = img_bgr.copy()
        mask = None
        if apply_skull_strip:
            processed, mask = self.stripper.strip(processed)
        if apply_clahe:
            processed = self.enhancer.enhance(processed)
        return processed, mask
