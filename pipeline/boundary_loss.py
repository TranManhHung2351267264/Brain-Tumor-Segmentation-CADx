"""
boundary_loss.py
Cài đặt hàm mất mát đường biên (Boundary Loss) cho bài toán phân đoạn y tế:
Dựa trên công trình của Kervadec et al. (MIDL / Medical Image Analysis):
"Boundary loss for highly unbalanced segmentation".
Giải quyết triệt để hiện tượng over-smoothing (vo tròn khối u làm mất vết lõm và mầm thâm nhiễm vi mô).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy.ndimage import distance_transform_edt

def compute_signed_distance_map(mask_np: np.ndarray) -> np.ndarray:
    """
    Tính Signed Distance Transform Map (Bản đồ khoảng cách có dấu) cho 1 mặt nạ nhị phân:
    phi(x) = - d(x, viền) nếu x nằm TRONG khối u
    phi(x) = + d(x, viền) nếu x nằm NGOÀI khối u
    mask_np: mảng nhị phân 2D (H, W), giá trị {0, 1}
    Trả về: mảng float32 (H, W) chuẩn hóa về khoảng [-1, 1]
    """
    posmask = mask_np.astype(bool)
    if not posmask.any():
        # Không có u: toàn bộ là khoảng cách dương từ nền
        return np.ones_like(mask_np, dtype=np.float32)
    
    negmask = ~posmask
    dist_inside = distance_transform_edt(posmask)
    dist_outside = distance_transform_edt(negmask)
    
    # phi = dist_outside - dist_inside
    # Để chuẩn hóa: trừ đi 0.5 ở viền
    phi = dist_outside - dist_inside
    # Chuẩn hóa theo bán kính ảnh
    h, w = mask_np.shape
    max_dist = np.sqrt(h**2 + w**2)
    phi = phi / max_dist
    return phi.astype(np.float32)


class BoundaryLoss(nn.Module):
    """
    Boundary Loss tính toán trên tensor xác suất Softmax và Signed Distance Map:
    Loss = sum( P * phi ) / N
    Trong đó:
      - P là xác suất dự đoán (sau Softmax) của từng lớp u não
      - phi là Signed Distance Map tính từ Ground Truth
    """
    def __init__(self, num_classes=4):
        super(BoundaryLoss, self).__init__()
        self.num_classes = num_classes

    def forward(self, probs: torch.Tensor, dist_maps: torch.Tensor) -> torch.Tensor:
        """
        probs: (B, C, H, W) - Xác suất dự đoán (Softmax)
        dist_maps: (B, C, H, W) - Bản đồ khoảng cách tương ứng từng lớp
        """
        # Bỏ qua lớp background (c=0), chỉ phạt trên các lớp tổn thương c=1..3
        probs_tumors = probs[:, 1:, ...]
        dist_tumors = dist_maps[:, 1:, ...]

        # Phép nhân từng phần tử: pixel dự đoán càng xa biên thực tế thì phạt càng nặng
        multipled = probs_tumors * dist_tumors
        loss = torch.mean(multipled)
        return loss


class ActiveContourLoss(nn.Module):
    """
    Hàm mất mát đường viền chủ động (Active Contour / Region-based Level Set Loss):
    Dựa trên mô hình Chan-Vese: ép xác suất dự đoán khớp với độ cong biên và phân tách cường độ:
    L_length = Chu vi đường viền dự đoán (Length penalty)
    L_region = Độ đồng nhất vùng bên trong và bên ngoài
    """
    def __init__(self, weight_length=0.1, weight_region=1.0):
        super(ActiveContourLoss, self).__init__()
        self.weight_length = weight_length
        self.weight_region = weight_region

    def forward(self, y_pred_prob: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
        """
        y_pred_prob: (B, C, H, W) sau Softmax
        y_true: (B, H, W) ground truth nhãn
        """
        # Tính gradient không gian của xác suất dự đoán (độ dài đường biên)
        # Bỏ qua lớp nền
        pred_fg = torch.sum(y_pred_prob[:, 1:, ...], dim=1, keepdim=True) # (B, 1, H, W)
        
        # Đạo hàm theo trục X và Y
        dx = torch.abs(pred_fg[:, :, :, 1:] - pred_fg[:, :, :, :-1])
        dy = torch.abs(pred_fg[:, :, 1:, :] - pred_fg[:, :, :-1, :])
        length_loss = torch.mean(dx) + torch.mean(dy)

        # Region loss: MSE giữa xác suất u và nhãn u nhị phân
        true_fg = (y_true > 0).float().unsqueeze(1)
        region_loss = F.mse_loss(pred_fg, true_fg)

        return self.weight_length * length_loss + self.weight_region * region_loss


class DiceFocalBoundaryLoss(nn.Module):
    """
    Hàm mất mát hỗn hợp 3 thành phần (Combo Loss toàn diện):
    Loss = w_dice * DiceLoss + w_focal * FocalLoss + w_boundary * BoundaryLoss
    - DiceLoss: tối ưu hóa diện tích giao nhau tổng thể
    - FocalLoss: giải quyết mất cân bằng điểm ảnh u nhỏ (< 5% lát cắt)
    - BoundaryLoss: giải quyết hiện tượng over-smoothing, bám sát bờ thâm nhiễm và vết lõm
    """
    def __init__(self, num_classes=4, w_dice=0.4, w_focal=0.4, w_boundary=0.2):
        super(DiceFocalBoundaryLoss, self).__init__()
        self.num_classes = num_classes
        self.w_dice = w_dice
        self.w_focal = w_focal
        self.w_boundary = w_boundary
        self.boundary_fn = BoundaryLoss(num_classes=num_classes)

    def dice_loss(self, probs: torch.Tensor, targets_one_hot: torch.Tensor, eps=1e-6) -> torch.Tensor:
        intersection = torch.sum(probs[:, 1:] * targets_one_hot[:, 1:], dim=(2, 3))
        union = torch.sum(probs[:, 1:] + targets_one_hot[:, 1:], dim=(2, 3))
        dice = (2.0 * intersection + eps) / (union + eps)
        return 1.0 - torch.mean(dice)

    def focal_loss(self, probs: torch.Tensor, targets: torch.Tensor, gamma=2.0) -> torch.Tensor:
        log_probs = torch.log(torch.clamp(probs, min=1e-7, max=1.0))
        ce = F.nll_loss(log_probs, targets, reduction='none')
        # pt = exp(-ce)
        pt = torch.exp(-ce)
        focal = ((1.0 - pt) ** gamma) * ce
        return torch.mean(focal)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor, dist_maps: torch.Tensor = None) -> torch.Tensor:
        probs = F.softmax(logits, dim=1)
        B, C, H, W = logits.shape

        # One-hot encoding cho ground truth
        targets_one_hot = F.one_hot(targets, num_classes=self.num_classes).permute(0, 3, 1, 2).float()

        l_dice = self.dice_loss(probs, targets_one_hot)
        l_focal = self.focal_loss(probs, targets)

        if dist_maps is not None:
            l_bnd = self.boundary_fn(probs, dist_maps)
            total = self.w_dice * l_dice + self.w_focal * l_focal + self.w_boundary * l_bnd
        else:
            total = 0.5 * l_dice + 0.5 * l_focal

        return total
