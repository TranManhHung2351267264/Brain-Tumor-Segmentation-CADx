"""
YOLO Inference Wrapper — YOLOv8s-seg & YOLO11s-seg
"""
import os
import time
import numpy as np
from PIL import Image
from typing import Optional, Tuple, List, Dict
import torch


class YOLOModel:
    """Wrapper thống nhất cho YOLOv8s-seg và YOLO11s-seg."""

    def __init__(self, model_name: str, weights_path: str):
        self.model_name   = model_name
        self.weights_path = weights_path
        self.model        = None
        self.is_loaded    = False
        self.load_error   = None

    def load(self) -> bool:
        """Tải model. Trả về True nếu thành công."""
        if not os.path.exists(self.weights_path):
            self.load_error = f"Không tìm thấy file weights: {self.weights_path}"
            return False
        try:
            from ultralytics import YOLO
            self.model    = YOLO(self.weights_path)
            self.is_loaded = True
            return True
        except Exception as e:
            self.load_error = str(e)
            return False

    def predict(
        self,
        image: Image.Image,
        conf: float = 0.25,
        iou:  float = 0.45,
    ) -> Tuple[Optional[object], float, str]:
        """
        Chạy inference.
        Returns: (results, inference_time_ms, error_message)
        """
        if not self.is_loaded:
            return None, 0.0, self.load_error or "Model chưa được tải."

        try:
            # Chuyển PIL → numpy để tránh lỗi đường dẫn tiếng Việt
            img_arr = np.array(image.convert("RGB"))
            t0 = time.time()
            results = self.model.predict(
                source=img_arr,
                conf=conf,
                iou=iou,
                verbose=False,
                device="cpu",
            )
            elapsed_ms = (time.time() - t0) * 1000
            return results, elapsed_ms, ""
        except Exception as e:
            return None, 0.0, str(e)

    @property
    def available(self) -> bool:
        return os.path.exists(self.weights_path)


# ── Singleton instances ──────────────────────────────────────────────────────
_TUMOR_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "YOLO", "weights")
)
_TUMOR_DIR_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "YOLO")
)

YOLOV8S_WEIGHTS  = os.path.join(_TUMOR_DIR, "best_yolov8s.pt")
YOLO11S_WEIGHTS  = os.path.join(_TUMOR_DIR_ROOT, "best_yolo11s.pt")

yolov8_model  = YOLOModel("YOLOv8s-seg",  YOLOV8S_WEIGHTS)
yolo11_model  = YOLOModel("YOLO11s-seg",  YOLO11S_WEIGHTS)
