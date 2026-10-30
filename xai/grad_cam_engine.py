"""
grad_cam_engine.py
Mô-đun Trí tuệ Nhân tạo có khả năng giải thích (Explainable AI - XAI):
Triển khai Grad-CAM (Gradient-weighted Class Activation Mapping) cho các kiến trúc mạng phân đoạn u não.
Trích xuất bản đồ kích hoạt nhiệt (Heatmap) giúp bác sĩ đối chứng vùng đặc trưng mô hình tập trung chú ý
(vùng nhân hoại tử, bắt thuốc cản quang hay viền thâm nhiễm).
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F

class GradCAMEngine:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        """
        model: Mô hình PyTorch (U-Net, SegFormer, etc.)
        target_layer: Lớp Conv mục tiêu cần trích xuất bản đồ đặc trưng (ví dụ: bottleneck hoặc layer cuối của encoder)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.hook_handles = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        h1 = self.target_layer.register_forward_hook(forward_hook)
        h2 = self.target_layer.register_full_backward_hook(backward_hook)
        self.hook_handles.extend([h1, h2])

    def generate_heatmap(self, input_tensor: torch.Tensor, target_class: int = 1) -> np.ndarray:
        """
        input_tensor: (1, C, H, W) - Tensor ảnh MRI đầu vào
        target_class: Lớp bệnh học mục tiêu (1=Glioma, 2=Meningioma, 3=Pituitary)
        Trả về: np.ndarray (H, W) bản đồ nhiệt [0, 1]
        """
        self.model.eval()
        self.model.zero_grad()

        # Cho phép tính gradient với input_tensor và model parameters
        with torch.enable_grad():
            output = self.model(input_tensor) # (1, num_classes, H, W)
            # Điểm số kích hoạt cho target_class trên toàn bộ vùng u
            score = torch.sum(output[0, target_class, :, :])
            score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Không thu thập được gradient hoặc activation từ target_layer!")

        # Global average pooling của gradients để tìm trọng số alpha_k
        # gradients: (1, C_feat, H_feat, W_feat)
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True) # (1, C_feat, 1, 1)

        # Tổ hợp tuyến tính của activation maps với alpha_k
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True) # (1, 1, H_feat, W_feat)

        # Áp dụng ReLU để chỉ giữ lại các đặc trưng có đóng góp tích cực
        cam = F.relu(cam)

        # Nội suy Bilinear phóng to lên kích thước ảnh gốc
        cam = F.interpolate(cam, size=(input_tensor.shape[2], input_tensor.shape[3]), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()

        # Chuẩn hóa về [0, 1]
        cam_min, cam_max = np.min(cam), np.max(cam)
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        return cam

    @staticmethod
    def overlay_heatmap(img_bgr: np.ndarray, heatmap: np.ndarray, alpha=0.5, colormap=cv2.COLORMAP_JET) -> np.ndarray:
        """
        Chồng bản đồ nhiệt màu lên ảnh MRI gốc:
        img_bgr: (H, W, 3), uint8
        heatmap: (H, W), float [0, 1]
        """
        heatmap_uint8 = np.uint8(255 * heatmap)
        colored_cam = cv2.applyColorMap(heatmap_uint8, colormap)
        
        # Nếu ảnh gốc là kích thước khác, resize colored_cam
        if colored_cam.shape[:2] != img_bgr.shape[:2]:
            colored_cam = cv2.resize(colored_cam, (img_bgr.shape[1], img_bgr.shape[0]))

        overlay = cv2.addWeighted(img_bgr, 1 - alpha, colored_cam, alpha, 0)
        return overlay

    def remove_hooks(self):
        for h in self.hook_handles:
            h.remove()
        self.hook_handles.clear()
