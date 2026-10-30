"""
Unified Segmentation Models Wrapper for WebApp CADx:
Supports:
1. Attention U-Net (Baseline)
2. Boundary-Aware Attention U-Net
3. ResNeXt-UNet++ (nnU-Net Style)
4. SegFormer (Vision Transformer)
"""
import os
import time
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Dict
import torch
import torch.nn.functional as F

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
INPUT_SIZE = 256  # Chuẩn kích thước mô hình mới

class SegmentationModelWrapper:
    def __init__(self, model_key: str, model_name_display: str, weights_filename: str, arch_type: str, encoder_name: str, decoder_attention: Optional[str] = "scse"):
        self.model_key = model_key
        self.name = model_name_display
        self.weights_filename = weights_filename
        self.arch_type = arch_type
        self.encoder_name = encoder_name
        self.decoder_attention = decoder_attention
        
        # Đường dẫn weights
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.weights_path = os.path.join(cur_dir, "..", "weights", weights_filename)
        # Fallback to root weights if not found
        if not os.path.exists(self.weights_path):
            self.weights_path = os.path.join(cur_dir, "..", "..", "weights", weights_filename)
            
        self.model = None
        self.is_loaded = False
        self.load_error = None

    def load(self) -> bool:
        if not os.path.exists(self.weights_path):
            self.load_error = f"Không tìm thấy file: {self.weights_filename}"
            return False
        try:
            import segmentation_models_pytorch as smp
            if self.arch_type == "unet":
                self.model = smp.Unet(
                    encoder_name=self.encoder_name,
                    encoder_weights=None,
                    in_channels=3,
                    classes=4,
                    decoder_attention_type=self.decoder_attention,
                    activation=None
                )
            elif self.arch_type == "unetplusplus":
                self.model = smp.UnetPlusPlus(
                    encoder_name=self.encoder_name,
                    encoder_weights=None,
                    in_channels=3,
                    classes=4,
                    decoder_attention_type=self.decoder_attention,
                    activation=None
                )
            elif self.arch_type == "segformer":
                self.model = smp.Segformer(
                    encoder_name=self.encoder_name,
                    encoder_weights=None,
                    in_channels=3,
                    classes=4,
                    activation=None
                )
            else:
                raise ValueError(f"Kiến trúc không hỗ trợ: {self.arch_type}")

            state = torch.load(self.weights_path, map_location="cpu", weights_only=False)
            self.model.load_state_dict(state)
            self.model.eval()
            self.is_loaded = True
            return True
        except Exception as e:
            self.load_error = str(e)
            return False

    def _preprocess(self, image: Image.Image) -> torch.Tensor:
        img = image.convert("RGB").resize((INPUT_SIZE, INPUT_SIZE), Image.LANCZOS)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = (arr - MEAN) / STD
        tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0).float()
        return tensor

    def predict(self, image: Image.Image) -> Tuple[Optional[np.ndarray], float, str]:
        if not self.is_loaded:
            if not self.load():
                return None, 0.0, self.load_error or "Model chưa tải thành công."

        try:
            tensor = self._preprocess(image)
            t0 = time.time()
            with torch.no_grad():
                logits = self.model(tensor)
                probs  = torch.softmax(logits, dim=1)
                pred   = torch.argmax(probs, dim=1)
            elapsed_ms = (time.time() - t0) * 1000
            
            # Resize mask về lại kích thước ảnh gốc
            mask_256 = pred.squeeze(0).numpy().astype(np.uint8)
            import cv2
            orig_w, orig_h = image.size
            if (orig_w, orig_h) != (INPUT_SIZE, INPUT_SIZE):
                mask_full = cv2.resize(mask_256, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            else:
                mask_full = mask_256

            return mask_full, elapsed_ms, ""
        except Exception as e:
            return None, 0.0, str(e)

    def compute_gradcam(self, image: Image.Image, target_class: int = 1) -> Optional[np.ndarray]:
        """Tính Grad-CAM heatmap."""
        if not self.is_loaded:
            self.load()
        if not self.is_loaded or self.model is None:
            return None

        try:
            tensor = self._preprocess(image)
            tensor.requires_grad = True
            
            activations = None
            gradients = None
            
            # Tìm conv layer cuối
            target_layer = None
            for name, module in self.model.named_modules():
                if isinstance(module, torch.nn.Conv2d):
                    target_layer = module

            if target_layer is None:
                return None

            def f_hook(m, i, o):
                nonlocal activations
                activations = o.detach()
            def b_hook(m, gi, go):
                nonlocal gradients
                gradients = go[0].detach()

            h1 = target_layer.register_forward_hook(f_hook)
            h2 = target_layer.register_full_backward_hook(b_hook)

            with torch.enable_grad():
                out = self.model(tensor)
                score = torch.sum(out[0, target_class])
                score.backward()

            h1.remove()
            h2.remove()

            if gradients is None or activations is None:
                return None

            weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
            cam = torch.sum(weights * activations, dim=1, keepdim=True)
            cam = F.relu(cam)
            orig_w, orig_h = image.size
            cam = F.interpolate(cam, size=(orig_h, orig_w), mode='bilinear', align_corners=False)
            cam_np = cam.squeeze().cpu().numpy()
            
            c_min, c_max = np.min(cam_np), np.max(cam_np)
            if c_max > c_min:
                cam_norm = (cam_np - c_min) / (c_max - c_min)
            else:
                cam_norm = np.zeros_like(cam_np)
            return cam_norm
        except Exception:
            return None


# ── ĐĂNG KÝ CÁC MÔ HÌNH HỌC SÂU ──
attention_unet_model = SegmentationModelWrapper(
    model_key="unet",
    model_name_display="Attention U-Net (Baseline)",
    weights_filename="best_attention_unet.pt",
    arch_type="unet",
    encoder_name="efficientnet-b0",
    decoder_attention="scse"
)

boundary_unet_model = SegmentationModelWrapper(
    model_key="boundary_unet",
    model_name_display="Boundary-Aware Attention U-Net",
    weights_filename="best_boundary_unet.pt",
    arch_type="unet",
    encoder_name="efficientnet-b0",
    decoder_attention="scse"
)

resunet_plusplus_model = SegmentationModelWrapper(
    model_key="resunet_plusplus",
    model_name_display="ResNeXt-UNet++ (nnU-Net Style)",
    weights_filename="best_resunet_plusplus.pt",
    arch_type="unetplusplus",
    encoder_name="se_resnext50_32x4d",
    decoder_attention="scse"
)

segformer_model = SegmentationModelWrapper(
    model_key="segformer",
    model_name_display="SegFormer (Vision Transformer SOTA)",
    weights_filename="best_segformer_transformer.pt",
    arch_type="segformer",
    encoder_name="mit_b2"
)

# Alias backward compatibility
unet_model = attention_unet_model
