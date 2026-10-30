"""
clinical_evaluator.py
Bộ công cụ tính toán các chỉ số đối chuẩn y tế lâm sàng chuyên sâu (Clinical Evaluation Metrics):
1. Dice Similarity Coefficient (DSC)
2. Intersection over Union (IoU / Jaccard Index)
3. 95% Hausdorff Distance (HD95 in pixels / mm) - Thước đo độ sai lệch đường viền chuẩn MICCAI
4. Average Symmetric Surface Distance (ASSD)
5. Độ nhạy (Sensitivity / Recall) và Độ đặc hiệu (Specificity)
"""

import numpy as np
import cv2
from scipy.spatial.distance import directed_hausdorff

class ClinicalMetricsEvaluator:
    """
    Tính toán các chỉ số hình thái học y tế giữa Mặt nạ Dự đoán (Prediction)
    và Nhãn Bác sĩ (Ground Truth).
    Hỗ trợ 4 lớp: 0=Nền, 1=Glioma, 2=Meningioma, 3=Pituitary.
    """
    CLASS_NAMES = {
        1: "Glioma",
        2: "Meningioma",
        3: "Pituitary"
    }

    def __init__(self, pixel_spacing_mm=1.0, eps=1e-6):
        """
        pixel_spacing_mm: Độ phân giải vật lý của voxel/pixel (thường là 0.5 - 1.0 mm trên máy MRI 1.5T/3T)
        """
        self.spacing = pixel_spacing_mm
        self.eps = eps

    def compute_overlap_metrics(self, pred_mask: np.ndarray, gt_mask: np.ndarray):
        """
        pred_mask, gt_mask: mảng nhị phân boolean / uint8 {0, 1}
        """
        pred = (pred_mask > 0).astype(bool)
        gt = (gt_mask > 0).astype(bool)

        tp = np.logical_and(pred, gt).sum()
        fp = np.logical_and(pred, ~gt).sum()
        fn = np.logical_and(~pred, gt).sum()
        tn = np.logical_and(~pred, ~gt).sum()

        intersection = tp
        union = pred.sum() + gt.sum()

        # Dice Score: 2 * |P & G| / (|P| + |G|)
        dice = (2.0 * intersection + self.eps) / (union + self.eps)

        # IoU: |P & G| / |P | G|
        iou = (intersection + self.eps) / (tp + fp + fn + self.eps)

        # Sensitivity / Recall
        sensitivity = (tp + self.eps) / (tp + fn + self.eps)

        # Specificity
        specificity = (tn + self.eps) / (tn + fp + self.eps)

        # Precision
        precision = (tp + self.eps) / (tp + fp + self.eps)

        return {
            "dice": float(dice),
            "iou": float(iou),
            "sensitivity": float(sensitivity),
            "specificity": float(specificity),
            "precision": float(precision)
        }

    def extract_contours_points(self, binary_mask: np.ndarray):
        """
        Trích xuất tập hợp tọa độ các điểm nằm trên đường viền chu vi của mặt nạ.
        """
        contours, _ = cv2.findContours(binary_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return np.empty((0, 2), dtype=np.float32)
        
        all_pts = []
        for c in contours:
            pts = c.squeeze(axis=1) # (N, 2)
            if len(pts.shape) == 2:
                all_pts.append(pts)
            elif len(pts.shape) == 1 and len(pts) == 2:
                all_pts.append(pts.reshape(1, 2))
        
        if not all_pts:
            return np.empty((0, 2), dtype=np.float32)
        return np.vstack(all_pts).astype(np.float32)

    def compute_surface_distances(self, pred_mask: np.ndarray, gt_mask: np.ndarray):
        """
        Tính 95% Hausdorff Distance (HD95) và Average Symmetric Surface Distance (ASSD).
        Đo bằng mm (hoặc pixel nếu spacing=1.0).
        """
        pred_pts = self.extract_contours_points(pred_mask)
        gt_pts = self.extract_contours_points(gt_mask)

        # Nếu cả 2 đều không có u: khoảng cách bằng 0 mm
        if len(pred_pts) == 0 and len(gt_pts) == 0:
            return {"hd95": 0.0, "assd": 0.0}

        # Nếu một bên có u nhưng bên kia dự đoán rỗng: gán giá trị phạt tối đa (đường chéo ảnh)
        h, w = pred_mask.shape
        max_penalty = np.sqrt(h**2 + w**2) * self.spacing
        if len(pred_pts) == 0 or len(gt_pts) == 0:
            return {"hd95": float(max_penalty), "assd": float(max_penalty)}

        # Áp dụng pixel spacing vào tọa độ
        pred_coords = pred_pts * self.spacing
        gt_coords = gt_pts * self.spacing

        # Tính ma trận khoảng cách Euclide giữa các điểm viền
        # d_pred_to_gt[i] là khoảng cách từ điểm pred_pts[i] tới điểm gần nhất trên gt
        from scipy.spatial import cKDTree
        tree_gt = cKDTree(gt_coords)
        dists_pred_to_gt, _ = tree_gt.query(pred_coords)

        tree_pred = cKDTree(pred_coords)
        dists_gt_to_pred, _ = tree_pred.query(gt_coords)

        # HD95: Phân vị thứ 95 của khoảng cách 2 chiều đối xứng (loại bỏ 5% điểm nhiễu ngoại lai)
        all_dists = np.concatenate([dists_pred_to_gt, dists_gt_to_pred])
        hd95 = float(np.percentile(all_dists, 95))

        # ASSD: Khoảng cách bề mặt trung bình đối xứng
        assd = float((np.mean(dists_pred_to_gt) + np.mean(dists_gt_to_pred)) / 2.0)

        return {"hd95": hd95, "assd": assd}

    def evaluate_slice(self, pred_mask_2d: np.ndarray, gt_mask_2d: np.ndarray):
        """
        Đánh giá toàn diện một lát cắt MRI trên cả 3 lớp tổn thương (1, 2, 3)
        pred_mask_2d, gt_mask_2d: (H, W), giá trị [0, 1, 2, 3]
        """
        results = {}
        dice_list = []
        iou_list = []
        hd95_list = []
        assd_list = []

        for c, name in self.CLASS_NAMES.items():
            p_c = (pred_mask_2d == c).astype(np.uint8)
            g_c = (gt_mask_2d == c).astype(np.uint8)

            overlap = self.compute_overlap_metrics(p_c, g_c)
            surface = self.compute_surface_distances(p_c, g_c)

            class_res = {**overlap, **surface}
            results[name] = class_res

            # Chỉ đưa vào trung bình nếu lớp đó có xuất hiện ở GT hoặc Pred
            if g_c.sum() > 0 or p_c.sum() > 0:
                dice_list.append(class_res["dice"])
                iou_list.append(class_res["iou"])
                hd95_list.append(class_res["hd95"])
                assd_list.append(class_res["assd"])

        results["Mean"] = {
            "dice": float(np.mean(dice_list)) if dice_list else 1.0,
            "iou": float(np.mean(iou_list)) if iou_list else 1.0,
            "hd95": float(np.mean(hd95_list)) if hd95_list else 0.0,
            "assd": float(np.mean(assd_list)) if assd_list else 0.0
        }

        return results
