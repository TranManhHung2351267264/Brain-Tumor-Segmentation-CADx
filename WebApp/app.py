"""
NeuroScan CADx — Hệ thống Hỗ trợ Chẩn đoán và Phân đoạn U não Từ Ảnh Chụp Cộng Hưởng Từ (MRI)
"""
import os
import sys
import io
import time
import json
import base64
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

# Thêm thư mục gốc vào đường dẫn hệ thống
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(ROOT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from models.yolo_model import yolov8_model, yolo11_model
from models.unet_model import (
    unet_model, attention_unet_model, boundary_unet_model,
    resunet_plusplus_model, segformer_model
)
from pipeline.mri_preprocessor import MRIPipeline
from cadx.clinical_reporter import TumorMorphologyAnalyzer, MedicalPDFReportGenerator
from utils.visualization import (
    CLASS_COLORS, CLASS_COLORS_HEX, CLASS_NAMES_VI, CLASS_NAMES_EN,
    CLASS_DESCRIPTIONS, create_mask_overlay, draw_yolo_results,
    compute_class_stats,
)
from utils.image_utils import load_image_from_upload, image_to_bytes

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="NeuroScan CADx - Hệ Thống Chẩn Đoán U Não",
    page_icon="O",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Nạp tệp định kiểu CSS y tế
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Khởi tạo trạng thái phiên làm việc
def init_session():
    defaults = {
        "current_page": "analysis",
        "uploaded_image": None,
        "image_metadata": {},
        "analysis_results": None,
        "session_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


@st.cache_resource(show_spinner=False)
def get_system_models():
    """Khởi tạo và kiểm tra nạp trọng số 6 mô hình học sâu."""
    status = {}
    status["yolov8"] = yolov8_model.load()
    status["yolo11"] = yolo11_model.load()
    status["unet"] = attention_unet_model.load()
    status["boundary_unet"] = boundary_unet_model.load()
    status["resunet_plusplus"] = resunet_plusplus_model.load()
    status["segformer"] = segformer_model.load()
    return status


def parse_sample_filename(fname: str) -> Dict[str, str]:
    """Phân tích tên file mẫu để trích xuất loại u và hướng cắt chụp."""
    lower = fname.lower()
    
    # Loại u
    tumor_type = "Không xác định"
    tumor_code = "unk"
    if "notumor" in lower or "_no_" in lower:
        tumor_type = "Não lành (Không có u - No Tumor)"
        tumor_code = "no"
    elif "_gl_" in lower or "glioma" in lower:
        tumor_type = "U tế bào thần kinh đệm (Glioma)"
        tumor_code = "gl"
    elif "_me_" in lower or "meningioma" in lower:
        tumor_type = "U màng não (Meningioma)"
        tumor_code = "me"
    elif "_pi_" in lower or "pituitary" in lower:
        tumor_type = "U tuyến yên (Pituitary)"
        tumor_code = "pi"
        
    # Mặt cắt
    plane = "Cắt ngang (Axial)"
    if "_ax_" in lower:
        plane = "Cắt ngang (Axial)"
    elif "_co_" in lower:
        plane = "Cắt trán (Coronal)"
    elif "_sa_" in lower:
        plane = "Cắt đứng dọc (Sagittal)"
        
    return {
        "tumor_type": tumor_type,
        "tumor_code": tumor_code,
        "plane": plane,
        "filename": fname,
    }


def load_sample_dataset() -> List[Dict]:
    """Tải danh sách các mẫu ảnh kiểm nghiệm có sẵn."""
    samples_dir = Path(ROOT_DIR) / "sample_images"
    if not samples_dir.exists():
        return []
    
    files = sorted(list(samples_dir.glob("*.jpg")) + list(samples_dir.glob("*.png")))
    dataset = []
    for f in files:
        meta = parse_sample_filename(f.name)
        meta["path"] = str(f)
        dataset.append(meta)
    return dataset


# ==============================================================================
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="clinical-brand">
            <span class="brand-badge">Hệ Thống Hỗ Trợ Chẩn Đoán CADx</span>
            <div class="brand-title">NEUROSCAN AI</div>
            <div class="brand-subtitle">Phân đoạn & phân tích định lượng u não tự động trên ảnh MRI</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Danh mục chức năng</div>', unsafe_allow_html=True)
        nav_options = {
            "analysis": "Phân tích & Chẩn đoán",
            "benchmark": "Đối chuẩn mô hình (Benchmark)",
            "history": "Nhật ký ca khám (History)",
            "docs": "Tài liệu kỹ thuật & Giải thuật",
        }
        for page_id, page_title in nav_options.items():
            is_active = (st.session_state.current_page == page_id)
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_title, key=f"nav_{page_id}", use_container_width=True, type=btn_type):
                st.session_state.current_page = page_id
                st.rerun()

        st.divider()

        st.markdown('<div class="section-label">Trạng thái các mô hình suy luận</div>', unsafe_allow_html=True)
        model_status = get_system_models()
        
        status_items = [
            ("YOLOv8s-seg", model_status["yolov8"]),
            ("YOLO11s-seg", model_status["yolo11"]),
            ("Attention U-Net", model_status["unet"]),
        ]
        
        status_html = ""
        for name, is_ready in status_items:
            css_cls = "status-ready" if is_ready else "status-unavailable"
            txt = f"[OK] {name}" if is_ready else f"[!] {name}"
            status_html += f'<div class="status-pill {css_cls}">{txt}</div>'
        st.markdown(status_html, unsafe_allow_html=True)

        st.divider()

        st.markdown('<div class="section-label">Cấu hình suy luận (Inference Configuration)</div>', unsafe_allow_html=True)
        
        selected_models = []
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.checkbox("YOLOv8s-seg", value=True, disabled=not model_status.get("yolov8", False)):
                selected_models.append("yolov8")
            if st.checkbox("Attention U-Net", value=True, disabled=not model_status.get("unet", False)):
                selected_models.append("unet")
            if st.checkbox("ResNeXt-UNet++", value=False, disabled=not model_status.get("resunet_plusplus", False)):
                selected_models.append("resunet_plusplus")
        with col_m2:
            if st.checkbox("YOLO11s-seg", value=True, disabled=not model_status.get("yolo11", False)):
                selected_models.append("yolo11")
            if st.checkbox("Boundary U-Net", value=True, disabled=not model_status.get("boundary_unet", False)):
                selected_models.append("boundary_unet")
            if st.checkbox("SegFormer (ViT)", value=True, disabled=not model_status.get("segformer", False)):
                selected_models.append("segformer")

        st.markdown('<div class="section-label">Tiền xử lý y tế & Giải thích (Medical Preprocessing & XAI)</div>', unsafe_allow_html=True)
        enable_skull_strip = st.checkbox("Bóc tách Hộp sọ (Skull Stripping)", value=False, help="Loại bỏ màng não, xương sọ và nền đen nhiễu")
        enable_clahe = st.checkbox("Tăng tương phản mô mềm (CLAHE)", value=False, help="Cân bằng thích ứng làm rõ viền thâm nhiễm")
        enable_gradcam = st.checkbox("Bản đồ nhiệt Grad-CAM (XAI)", value=True, help="Hiển thị vùng kích hoạt đặc trưng của mạng neural")

        conf_threshold = st.slider(
            "Ngưỡng tin cậy (Confidence Threshold)",
            min_value=0.10,
            max_value=0.90,
            value=0.25,
            step=0.05,
            format="%.2f",
            help="Áp dụng cho các mô hình YOLO nhằm lọc các đối tượng có độ tin cậy thấp",
        )

        mask_opacity = st.slider(
            "Độ chắn sáng mặt nạ (Mask Opacity)",
            min_value=0.20,
            max_value=0.85,
            value=0.45,
            step=0.05,
            format="%.2f",
            help="Điều chỉnh độ đậm nhạt của lớp màu phân đoạn đè lên ảnh gốc",
        )

        st.divider()

        st.markdown("""
        <div style="font-size:0.72rem; color:#64748B; line-height:1.6;">
            <strong>Bộ dữ liệu:</strong> BRISC 2025 (4,794 ca chụp)<br>
            <strong>Độ phân giải chuẩn:</strong> 640x640 / 512x512<br>
            <strong>Môi trường phần cứng:</strong> CPU Optimization Mode<br>
            <strong>Chuẩn đánh giá:</strong> mAP50, Dice & IoU
        </div>
        """, unsafe_allow_html=True)

    return selected_models, conf_threshold, mask_opacity, enable_skull_strip, enable_clahe, enable_gradcam


# ==============================================================================
# TRANG 1: PHÂN TÍCH VÀ CHẨN ĐOÁN (ANALYSIS)
# ==============================================================================
def render_analysis_page(selected_models: List[str], conf_threshold: float, mask_opacity: float, enable_skull_strip: bool = False, enable_clahe: bool = False, enable_gradcam: bool = True):
    st.markdown("""
    <div class="clinical-hero">
        <div class="hero-meta">
            <span class="brand-badge">PHÂN ĐOẠN ĐỊNH LƯỢNG LÂM SÀNG</span>
        </div>
        <div class="hero-title">Phân Tích & Phân Đoạn U Não Tự Động</div>
        <div class="hero-desc">
            Ứng dụng kiến trúc Deep Learning đối chuẩn đa mô hình để phát hiện, phân loại và tính toán diện tích mô bệnh học (Glioma, Meningioma, Pituitary).
        </div>
        <div class="specs-strip">
            <span class="spec-chip active-blue">YOLOv8s-seg: mAP50 90.56%</span>
            <span class="spec-chip active-amber">YOLO11s-seg: mAP50 90.64%</span>
            <span class="spec-chip active-teal">Attention U-Net: Dice 92.92%</span>
            <span class="spec-chip">Thời gian đáp ứng CPU: ~1.2s - 1.9s</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Khu vực nạp dữ liệu
    st.markdown('<div class="section-label">1. Nạp dữ liệu ảnh chụp MRI</div>', unsafe_allow_html=True)
    tab_upload, tab_samples = st.tabs(["Tải tệp ảnh chụp mới", "Kho dữ liệu mẫu kiểm chuẩn (15 mẫu ca bệnh)"])

    chosen_image: Optional[Image.Image] = None
    chosen_meta: Dict = {}

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Chọn tệp ảnh MRI (định dạng JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            help="Khuyến nghị ảnh cắt lớp đầu có độ phân giải tối thiểu 512x512",
        )
        if uploaded_file is not None:
            chosen_image = load_image_from_upload(uploaded_file)
            chosen_meta = {
                "name": uploaded_file.name,
                "source": "Người dùng tải lên",
                "tumor_hint": "Chưa xác định",
                "plane": "Tự động phát hiện",
            }
            st.session_state.uploaded_image = chosen_image
            st.session_state.image_metadata = chosen_meta

    with tab_samples:
        samples = load_sample_dataset()
        if samples:
            # Nhóm theo loại u để hiển thị chuyên nghiệp
            categories = {
                "gl": "Nhóm bệnh: U tế bào thần kinh đệm (Glioma)",
                "me": "Nhóm bệnh: U màng não (Meningioma)",
                "pi": "Nhóm bệnh: U tuyến yên (Pituitary)",
            }
            
            for code, group_title in categories.items():
                group_samples = [s for s in samples if s["tumor_code"] == code]
                if not group_samples:
                    continue
                st.markdown(f"**{group_title}**")
                cols = st.columns(len(group_samples))
                for idx, s in enumerate(group_samples):
                    with cols[idx]:
                        try:
                            thumb = Image.open(s["path"]).resize((110, 110), Image.BILINEAR)
                            st.image(thumb, use_container_width=True)
                            st.caption(f"{s['plane']}")
                            if st.button("Chọn mẫu này", key=f"btn_sample_{s['filename']}", use_container_width=True):
                                chosen_image = Image.open(s["path"]).convert("RGB")
                                chosen_meta = {
                                    "name": s["filename"],
                                    "source": "Kho dữ liệu chuẩn BRISC 2025",
                                    "tumor_hint": s["tumor_type"],
                                    "plane": s["plane"],
                                }
                                st.session_state.uploaded_image = chosen_image
                                st.session_state.image_metadata = chosen_meta
                                st.rerun()
                        except Exception:
                            pass
                st.write("")

    # Nếu đã có ảnh trong phiên làm việc
    if chosen_image is None and st.session_state.uploaded_image is not None:
        chosen_image = st.session_state.uploaded_image
        chosen_meta = st.session_state.image_metadata

    if chosen_image is None:
        st.markdown("""
        <div class="clinical-empty">
            <div class="clinical-empty-title">Chưa có dữ liệu ảnh MRI</div>
            <div class="clinical-empty-desc">
                Vui lòng tải lên tệp ảnh quét hoặc chọn một ảnh từ kho dữ liệu mẫu kiểm chuẩn ở trên để kích hoạt quy trình phân tích.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Xem trước ảnh gốc và thông số
    st.markdown("---")
    st.markdown('<div class="section-label">2. Đối chiếu dữ liệu ảnh đầu vào</div>', unsafe_allow_html=True)
    
    col_preview, col_tech = st.columns([1, 1])
    W, H = chosen_image.size

    with col_preview:
        st.image(chosen_image, caption=f"Ảnh đầu vào: {chosen_meta.get('name', 'mri_scan')}", use_container_width=True)

    with col_tech:
        st.markdown(f"""
        <div class="clinical-card">
            <div class="section-label">Thông số kỹ thuật ảnh</div>
            <table class="clinical-table">
                <tr>
                    <td style="color:#94A3B8;">Tên tệp lưu trữ</td>
                    <td style="font-family:monospace; word-break:break-all;">{chosen_meta.get('name', 'Unknown')}</td>
                </tr>
                <tr>
                    <td style="color:#94A3B8;">Nguồn gốc</td>
                    <td>{chosen_meta.get('source', 'Tự tải lên')}</td>
                </tr>
                <tr>
                    <td style="color:#94A3B8;">Chẩn đoán tham chiếu</td>
                    <td style="font-weight:600; color:#38BDF8;">{chosen_meta.get('tumor_hint', 'Chưa đối chiếu')}</td>
                </tr>
                <tr>
                    <td style="color:#94A3B8;">Mặt phẳng giải phẫu</td>
                    <td>{chosen_meta.get('plane', 'Chưa rõ')}</td>
                </tr>
                <tr>
                    <td style="color:#94A3B8;">Kích thước ảnh</td>
                    <td style="font-family:monospace;">{W} x {H} pixels</td>
                </tr>
                <tr>
                    <td style="color:#94A3B8;">Tổng số lượng pixel</td>
                    <td style="font-family:monospace;">{W * H:,} px</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        if not selected_models:
            st.warning("Cảnh báo: Hiện chưa có mô hình nào được chọn trong cấu hình bên trái.")

    # Nút thực hiện phân tích
    st.markdown("---")
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        execute_analysis = st.button(
            "Tiến hành phân tích hình ảnh",
            type="primary",
            use_container_width=True,
            disabled=len(selected_models) == 0,
        )

    if execute_analysis:
        # Áp dụng tiền xử lý y tế nếu được kích hoạt
        if enable_skull_strip or enable_clahe:
            import cv2
            np_ch = np.array(chosen_image)
            bgr_ch = cv2.cvtColor(np_ch, cv2.COLOR_RGB2BGR)
            mri_pipe = MRIPipeline()
            processed_bgr, _ = mri_pipe.process(bgr_ch, apply_skull_strip=enable_skull_strip, apply_clahe=enable_clahe)
            chosen_image = Image.fromarray(cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB))

        results = {}
        t_start_all = time.time()
        
        progress = st.progress(0, text="Khởi tạo pipeline suy luận...")
        step = 1.0 / len(selected_models)
        
        for idx, m_key in enumerate(selected_models):
            if m_key == "yolov8":
                progress.progress(int((idx) * step * 100), text="Đang phân tích với YOLOv8s-seg...")
                raw_res, t_ms, err = yolov8_model.predict(chosen_image, conf=conf_threshold)
                if err:
                    results["yolov8"] = {"error": err}
                else:
                    ann_img, detections = draw_yolo_results(chosen_image, raw_res, conf_threshold)
                    results["yolov8"] = {
                        "name": "YOLOv8s-seg",
                        "type": "yolo",
                        "annotated": ann_img,
                        "detections": detections,
                        "time_ms": t_ms,
                    }

            elif m_key == "yolo11":
                progress.progress(int((idx) * step * 100), text="Đang phân tích với YOLO11s-seg...")
                raw_res, t_ms, err = yolo11_model.predict(chosen_image, conf=conf_threshold)
                if err:
                    results["yolo11"] = {"error": err}
                else:
                    ann_img, detections = draw_yolo_results(chosen_image, raw_res, conf_threshold)
                    results["yolo11"] = {
                        "name": "YOLO11s-seg",
                        "type": "yolo",
                        "annotated": ann_img,
                        "detections": detections,
                        "time_ms": t_ms,
                    }

            elif m_key == "unet":
                progress.progress(int((idx) * step * 100), text="Đang phân tích với Attention U-Net...")
                mask_arr, t_ms, err = attention_unet_model.predict(chosen_image)
                if err:
                    results["unet"] = {"error": err}
                else:
                    overlay_img = create_mask_overlay(chosen_image, mask_arr, alpha=mask_opacity)
                    stats = compute_class_stats(mask_arr)
                    cam = attention_unet_model.compute_gradcam(chosen_image) if enable_gradcam else None
                    results["unet"] = {
                        "name": "Attention U-Net (Baseline)",
                        "type": "unet",
                        "annotated": overlay_img,
                        "mask": mask_arr,
                        "stats": stats,
                        "gradcam": cam,
                        "time_ms": t_ms,
                    }

            elif m_key == "boundary_unet":
                progress.progress(int((idx) * step * 100), text="Đang phân tích với Boundary-Aware U-Net...")
                mask_arr, t_ms, err = boundary_unet_model.predict(chosen_image)
                if err:
                    results["boundary_unet"] = {"error": err}
                else:
                    overlay_img = create_mask_overlay(chosen_image, mask_arr, alpha=mask_opacity)
                    stats = compute_class_stats(mask_arr)
                    cam = boundary_unet_model.compute_gradcam(chosen_image) if enable_gradcam else None
                    results["boundary_unet"] = {
                        "name": "Boundary-Aware Attention U-Net",
                        "type": "unet",
                        "annotated": overlay_img,
                        "mask": mask_arr,
                        "stats": stats,
                        "gradcam": cam,
                        "time_ms": t_ms,
                    }

            elif m_key == "resunet_plusplus":
                progress.progress(int((idx) * step * 100), text="Đang phân tích với ResNeXt-UNet++...")
                mask_arr, t_ms, err = resunet_plusplus_model.predict(chosen_image)
                if err:
                    results["resunet_plusplus"] = {"error": err}
                else:
                    overlay_img = create_mask_overlay(chosen_image, mask_arr, alpha=mask_opacity)
                    stats = compute_class_stats(mask_arr)
                    cam = resunet_plusplus_model.compute_gradcam(chosen_image) if enable_gradcam else None
                    results["resunet_plusplus"] = {
                        "name": "ResNeXt-UNet++ (nnU-Net Style)",
                        "type": "unet",
                        "annotated": overlay_img,
                        "mask": mask_arr,
                        "stats": stats,
                        "gradcam": cam,
                        "time_ms": t_ms,
                    }

            elif m_key == "segformer":
                progress.progress(int((idx) * step * 100), text="Đang phân tích với SegFormer (Vision Transformer)...")
                mask_arr, t_ms, err = segformer_model.predict(chosen_image)
                if err:
                    results["segformer"] = {"error": err}
                else:
                    overlay_img = create_mask_overlay(chosen_image, mask_arr, alpha=mask_opacity)
                    stats = compute_class_stats(mask_arr)
                    cam = segformer_model.compute_gradcam(chosen_image) if enable_gradcam else None
                    results["segformer"] = {
                        "name": "SegFormer (Vision Transformer SOTA)",
                        "type": "unet",
                        "annotated": overlay_img,
                        "mask": mask_arr,
                        "stats": stats,
                        "gradcam": cam,
                        "time_ms": t_ms,
                    }

        total_elapsed = (time.time() - t_start_all) * 1000
        progress.progress(100, text="Hoàn tất phân tích dữ liệu.")
        time.sleep(0.3)
        progress.empty()

        st.session_state.analysis_results = {
            "models_output": results,
            "total_time_ms": total_elapsed,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S ngày %d/%m/%Y"),
            "image_name": chosen_meta.get("name", "MRI_Case"),
        }

        # Lưu nhật ký
        st.session_state.session_history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": chosen_meta.get("name", "MRI_Case"),
            "models": list(results.keys()),
            "time_ms": total_elapsed,
        })

    # Hiển thị kết quả đã phân tích
    if st.session_state.analysis_results is not None:
        render_results_section(chosen_image, st.session_state.analysis_results, mask_opacity)


def render_results_section(original_image: Image.Image, pack: Dict, mask_opacity: float):
    st.markdown("---")
    st.markdown('<div class="section-label">3. Kết quả chẩn đoán và phân đoạn định lượng</div>', unsafe_allow_html=True)
    
    outputs = pack["models_output"]
    total_time = pack["total_time_ms"]
    
    # Tính số lượng tổn thương ghi nhận
    total_lesions = 0
    for res in outputs.values():
        if "error" not in res:
            if res["type"] == "yolo":
                total_lesions += len(res.get("detections", []))
            elif res["type"] == "unet":
                total_lesions += sum(1 for s in res.get("stats", {}).values() if s["area_px2"] > 0)

    # Thống kê nhanh cấp cao
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-cell">
            <div class="metric-cell-label">Mô hình hoàn tất</div>
            <div class="metric-cell-value">{len(outputs)}</div>
            <div class="metric-cell-hint">Kiến trúc đã thực thi</div>
        </div>
        <div class="metric-cell {'green' if total_lesions > 0 else 'gray'}">
            <div class="metric-cell-label">Vùng tổn thương</div>
            <div class="metric-cell-value">{total_lesions}</div>
            <div class="metric-cell-hint">Ghi nhận từ các mô hình</div>
        </div>
        <div class="metric-cell amber">
            <div class="metric-cell-label">Thời gian tổng</div>
            <div class="metric-cell-value">{total_time:.0f} ms</div>
            <div class="metric-cell-hint">Xử lý trên luồng CPU</div>
        </div>
        <div class="metric-cell">
            <div class="metric-cell-label">Thời điểm hoàn thành</div>
            <div class="metric-cell-value" style="font-size:0.95rem; line-height:1.6;">{pack['timestamp']}</div>
            <div class="metric-cell-hint">Đã đồng bộ vào lịch sử</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị chi tiết từng mô hình
    for m_key, res in outputs.items():
        if "error" in res:
            st.error(f"Lỗi suy luận ở mô hình {m_key}: {res['error']}")
            continue

        model_name = res["name"]
        t_ms = res["time_ms"]
        
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:6px; margin:24px 0 14px 0;">
            <div style="font-weight:700; font-size:1.05rem; color:#F8FAFC;">Kết quả từ mô hình: {model_name}</div>
            <div style="font-family:monospace; font-size:0.8rem; color:#94A3B8;">Thời gian: {t_ms:.1f} ms</div>
        </div>
        """, unsafe_allow_html=True)

        col_img, col_metrics = st.columns([1, 1])

        with col_img:
            ann_img = res.get("annotated")
            if ann_img is not None:
                st.image(ann_img, caption=f"Bản đồ phân đoạn - {model_name}", use_container_width=True)
                
                # Nút lưu ảnh
                img_data = image_to_bytes(ann_img, "PNG")
                st.download_button(
                    label="Tải ảnh phân đoạn này (PNG)",
                    data=img_data,
                    file_name=f"neuroscan_{m_key}_{int(time.time())}.png",
                    mime="image/png",
                    key=f"dl_btn_{m_key}",
                )

        with col_metrics:
            st.markdown('<div class="section-label">Định lượng tổn thương mô học</div>', unsafe_allow_html=True)

            if res["type"] == "yolo":
                dets = res.get("detections", [])
                if dets:
                    for d in dets:
                        color = CLASS_COLORS_HEX.get(d["class_id"], "#38BDF8")
                        st.markdown(f"""
                        <div class="finding-item">
                            <div style="display:flex; align-items:center;">
                                <div class="finding-indicator" style="background:{color}; box-shadow:0 0 6px {color};"></div>
                                <div>
                                    <div class="finding-title">{d['class_vi']}</div>
                                    <div class="finding-sub">{d['class_name']} &bull; Độ tin cậy: {d['confidence']:.1%}</div>
                                </div>
                            </div>
                            <div class="finding-metric">
                                <div class="finding-value">{d['area_pct']:.2f}%</div>
                                <div class="finding-area">{d['area_px2']:,.0f} px</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    df_det = pd.DataFrame([{
                        "Phân loại bệnh học": d["class_vi"],
                        "Độ tin cậy": f"{d['confidence']:.2%}",
                        "Tỉ lệ diện tích": f"{d['area_pct']:.2f}%",
                        "Số lượng pixel": f"{d['area_px2']:,.0f} px",
                    } for d in dets])
                    st.dataframe(df_det, use_container_width=True, hide_index=True)
                else:
                    st.markdown("""
                    <div class="clinical-empty" style="padding:20px;">
                        <div class="clinical-empty-title">Không phát hiện khối u</div>
                        <div class="clinical-empty-desc">Không có vùng tổn thương nào vượt qua ngưỡng tin cậy thiết lập.</div>
                    </div>
                    """, unsafe_allow_html=True)

            elif res["type"] == "unet":
                stats = res.get("stats", {})
                has_tumor = any(s["area_px2"] > 0 for s in stats.values())
                if has_tumor:
                    for cid, s in stats.items():
                        if s["area_px2"] > 0:
                            color = CLASS_COLORS_HEX.get(cid, "#38BDF8")
                            st.markdown(f"""
                            <div class="finding-item">
                                <div style="display:flex; align-items:center;">
                                    <div class="finding-indicator" style="background:{color}; box-shadow:0 0 6px {color};"></div>
                                    <div>
                                        <div class="finding-title">{s['class_vi']}</div>
                                        <div class="finding-sub">{s['class_name']} &bull; Phân đoạn mức pixel</div>
                                    </div>
                                </div>
                                <div class="finding-metric">
                                    <div class="finding-value">{s['area_pct']:.2f}%</div>
                                    <div class="finding-area">{s['area_px2']:,.0f} px</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Bảng phân tích chi tiết diện tích
                    rows_table = []
                    total_pixels = original_image.size[0] * original_image.size[1]
                    bg_pixels = total_pixels - sum(s["area_px2"] for s in stats.values())
                    rows_table.append({
                        "Cấu trúc mô học": "Mô não lành & Nền",
                        "Số lượng pixel": f"{bg_pixels:,} px",
                        "Tỉ lệ trên lát cắt": f"{(bg_pixels/total_pixels)*100:.2f}%"
                    })
                    for cid, s in stats.items():
                        if s["area_px2"] > 0:
                            rows_table.append({
                                "Cấu trúc mô học": s["class_vi"],
                                "Số lượng pixel": f"{s['area_px2']:,} px",
                                "Tỉ lệ trên lát cắt": f"{s['area_pct']:.2f}%"
                            })
                    st.dataframe(pd.DataFrame(rows_table), use_container_width=True, hide_index=True)
                else:
                    st.markdown("""
                    <div class="clinical-empty" style="padding:20px;">
                        <div class="clinical-empty-title">Không ghi nhận tổn thương</div>
                        <div class="clinical-empty-desc">Attention U-Net phân loại toàn bộ lát cắt là mô lành/nền.</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Chú giải mã màu chuẩn
    st.markdown("---")
    st.markdown('<div class="section-label">Chú giải mã màu phân loại mô học</div>', unsafe_allow_html=True)
    c_leg1, c_leg2, c_leg3 = st.columns(3)
    with c_leg1:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:12px; height:12px; border-radius:2px; background:{CLASS_COLORS_HEX[1]};"></div>
            <div>
                <strong>U Tế bào Thần kinh đệm (Glioma)</strong><br>
                <span style="font-size:0.75rem; color:#94A3B8;">Mô u xâm lấn, ranh giới khó xác định</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_leg2:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:12px; height:12px; border-radius:2px; background:{CLASS_COLORS_HEX[2]};"></div>
            <div>
                <strong>U Màng não (Meningioma)</strong><br>
                <span style="font-size:0.75rem; color:#94A3B8;">Khối u ngoài trục, ranh giới rõ ràng</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_leg3:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:12px; height:12px; border-radius:2px; background:{CLASS_COLORS_HEX[3]};"></div>
            <div>
                <strong>U Tuyến yên (Pituitary)</strong><br>
                <span style="font-size:0.75rem; color:#94A3B8;">Khu trú hố yên, ảnh hưởng trục nội tiết</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Xuất dữ liệu báo cáo
    st.markdown("---")
    st.markdown('<div class="section-label">4. Xuất hồ sơ kết quả chẩn đoán</div>', unsafe_allow_html=True)
    col_exp1, col_exp2 = st.columns(2)

    # Xuất file CSV
    with col_exp1:
        csv_rows = []
        for m_key, res in outputs.items():
            if "error" in res:
                continue
            if res["type"] == "yolo":
                for d in res.get("detections", []):
                    csv_rows.append({
                        "Thời gian": pack["timestamp"],
                        "Tên tệp": pack["image_name"],
                        "Mô hình": res["name"],
                        "Phân loại": d["class_vi"],
                        "Độ tin cậy": f"{d['confidence']:.4f}",
                        "Diện tích (px)": d["area_px2"],
                        "Tỉ lệ (%)": f"{d['area_pct']:.4f}",
                    })
            elif res["type"] == "unet":
                for cid, s in res.get("stats", {}).items():
                    if s["area_px2"] > 0:
                        csv_rows.append({
                            "Thời gian": pack["timestamp"],
                            "Tên tệp": pack["image_name"],
                            "Mô hình": res["name"],
                            "Phân loại": s["class_vi"],
                            "Độ tin cậy": "Mặt nạ phân đoạn pixel",
                            "Diện tích (px)": s["area_px2"],
                            "Tỉ lệ (%)": f"{s['area_pct']:.4f}",
                        })
        if csv_rows:
            df_export = pd.DataFrame(csv_rows)
            csv_content = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="Xuất dữ liệu định lượng (.CSV)",
                data=csv_content,
                file_name=f"neuroscan_report_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # Xuất file JSON
    with col_exp2:
        json_report = {
            "metadata": {
                "system": "NeuroScan CADx v1.0",
                "timestamp": pack["timestamp"],
                "source_file": pack["image_name"],
            },
            "models_evaluated": list(outputs.keys()),
            "findings": csv_rows,
        }
        json_bytes = json.dumps(json_report, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            label="Xuất hồ sơ ca khám dạng cấu trúc (.JSON)",
            data=json_bytes,
            file_name=f"neuroscan_case_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True,
        )


# ==============================================================================
# TRANG 2: ĐỐI CHUẨN MÔ HÌNH (BENCHMARK)
# ==============================================================================
def render_benchmark_page():
    st.markdown("""
    <div class="clinical-hero">
        <div class="hero-meta">
            <span class="brand-badge">ĐỐI CHUẨN HIỆU NĂNG HỆ THỐNG</span>
        </div>
        <div class="hero-title">Đánh Giá & Đối Chuẩn 3 Kiến Trúc Mô Hình</div>
        <div class="hero-desc">
            Tổng hợp kết quả kiểm nghiệm trên tập dữ liệu độc lập (Validation Set gồm 693 ca chụp) theo các tiêu chuẩn quốc tế: mAP50, Dice Similarity Coefficient (DSC) và Intersection over Union (IoU).
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Bảng tổng hợp chỉ số kỹ thuật và độ chính xác</div>', unsafe_allow_html=True)
    table_overview = """
    <table class="clinical-table">
        <thead>
            <tr>
                <th>Kiến trúc Mô hình</th>
                <th>Số tham số</th>
                <th>Trường phái Thuật toán</th>
                <th>Hàm mất mát (Loss)</th>
                <th>Dice Score (DSC)</th>
                <th>IoU (%)</th>
                <th>Sai lệch viền HD95 (mm)</th>
                <th>Khoảng cách ASSD (mm)</th>
                <th>Tốc độ (FPS)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="font-weight:700; color:#38BDF8;">YOLOv8s-seg</td>
                <td style="font-family:monospace;">11.8 M</td>
                <td>One-stage Instance Seg</td>
                <td style="font-size:0.75rem;">CIoU + Proto-net BCE</td>
                <td style="font-family:monospace;">0.8840</td>
                <td style="font-family:monospace;">81.20%</td>
                <td style="font-family:monospace; color:#EF4444;">8.42 mm</td>
                <td style="font-family:monospace;">6.15 mm</td>
                <td style="font-family:monospace; color:#34D399; font-weight:700;">42.5 FPS</td>
            </tr>
            <tr>
                <td style="font-weight:700; color:#F59E0B;">YOLO11s-seg</td>
                <td style="font-family:monospace;">9.8 M</td>
                <td>One-stage Instance Seg</td>
                <td style="font-size:0.75rem;">Enhanced C3k2 + Proto BCE</td>
                <td style="font-family:monospace;">0.9020</td>
                <td style="font-family:monospace;">83.70%</td>
                <td style="font-family:monospace; color:#EF4444;">7.15 mm</td>
                <td style="font-family:monospace;">5.42 mm</td>
                <td style="font-family:monospace; color:#34D399; font-weight:700;">38.2 FPS</td>
            </tr>
            <tr>
                <td style="font-weight:700; color:#94A3B8;">Attention U-Net (Baseline)</td>
                <td style="font-family:monospace;">6.4 M</td>
                <td>CNN + scSE Attention</td>
                <td style="font-size:0.75rem;">50% Dice + 50% CE</td>
                <td style="font-family:monospace;">0.8207</td>
                <td style="font-family:monospace;">73.61%</td>
                <td style="font-family:monospace; color:#EF4444;">9.45 mm (Over-smooth)</td>
                <td style="font-family:monospace;">7.16 mm</td>
                <td style="font-family:monospace; color:#34D399; font-weight:700;">246.8 FPS</td>
            </tr>
            <tr>
                <td style="font-weight:700; color:#10B981;">Boundary-Aware U-Net</td>
                <td style="font-family:monospace;">6.4 M</td>
                <td>CNN + Distance Transform</td>
                <td style="font-size:0.75rem; color:#10B981; font-weight:600;">Dice + Focal + Boundary</td>
                <td style="font-family:monospace; font-weight:600; color:#10B981;">0.8241</td>
                <td style="font-family:monospace;">73.77%</td>
                <td style="font-family:monospace; color:#10B981; font-weight:700;">6.99 mm (Giảm 26%)</td>
                <td style="font-family:monospace; color:#10B981; font-weight:700;">4.65 mm (Giảm 35%)</td>
                <td style="font-family:monospace; color:#34D399; font-weight:700;">249.1 FPS</td>
            </tr>
            <tr>
                <td style="font-weight:700; color:#A855F7;">ResNeXt-UNet++</td>
                <td style="font-family:monospace;">53.3 M</td>
                <td>Nested Dense Skip CNN (nnU-Net)</td>
                <td style="font-size:0.75rem;">Dice + CE (Dense Skip)</td>
                <td style="font-family:monospace; font-weight:600;">0.8277</td>
                <td style="font-family:monospace; color:#A855F7; font-weight:700;">74.60% (Cao nhất)</td>
                <td style="font-family:monospace;">9.03 mm</td>
                <td style="font-family:monospace;">6.83 mm</td>
                <td style="font-family:monospace;">36.3 FPS</td>
            </tr>
            <tr>
                <td style="font-weight:700; color:#38BDF8;">SegFormer (Vision Transformer)</td>
                <td style="font-family:monospace;">24.8 M</td>
                <td>Self-Attention mit-b2 + MLP</td>
                <td style="font-size:0.75rem;">Dice + CE (Transformer)</td>
                <td style="font-family:monospace; color:#38BDF8; font-weight:700;">0.8300 (Cao nhất)</td>
                <td style="font-family:monospace; font-weight:600;">74.50%</td>
                <td style="font-family:monospace; color:#38BDF8; font-weight:600;">7.63 mm</td>
                <td style="font-family:monospace; color:#38BDF8; font-weight:600;">5.58 mm</td>
                <td style="font-family:monospace; color:#34D399; font-weight:700;">163.6 FPS</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(table_overview, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-label">Độ chính xác phân giải theo từng nhóm bệnh học</div>', unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    try:
        import plotly.graph_objects as go

        with col_chart1:
            classes = ["Glioma", "Meningioma", "Pituitary"]
            fig_yolo = go.Figure()
            fig_yolo.add_trace(go.Bar(
                name="YOLOv8s-seg",
                x=classes,
                y=[81.8, 98.7, 91.2],
                marker_color="#38BDF8",
                text=["81.8%", "98.7%", "91.2%"],
                textposition="auto",
            ))
            fig_yolo.add_trace(go.Bar(
                name="YOLO11s-seg",
                x=classes,
                y=[83.0, 98.4, 90.5],
                marker_color="#F59E0B",
                text=["83.0%", "98.4%", "90.5%"],
                textposition="auto",
            ))
            fig_yolo.update_layout(
                title="mAP50 Mask theo loại u (YOLO)",
                plot_bgcolor="#0F172A",
                paper_bgcolor="#0F172A",
                font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
                barmode="group",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=320,
                margin=dict(l=20, r=20, t=50, b=20),
            )
            fig_yolo.update_yaxes(range=[70, 105], ticksuffix="%")
            st.plotly_chart(fig_yolo, use_container_width=True)

        with col_chart2:
            fig_unet = go.Figure()
            fig_unet.add_trace(go.Bar(
                name="Dice Score (DSC)",
                x=classes,
                y=[91.07, 95.41, 92.28],
                marker_color="#10B981",
                text=["91.07%", "95.41%", "92.28%"],
                textposition="auto",
            ))
            fig_unet.add_trace(go.Bar(
                name="IoU Score",
                x=classes,
                y=[83.63, 91.26, 85.10],
                marker_color="#6EE7B7",
                text=["83.63%", "91.26%", "85.10%"],
                textposition="auto",
            ))
            fig_unet.update_layout(
                title="Chỉ số Dice & IoU theo loại u (Attention U-Net)",
                plot_bgcolor="#0F172A",
                paper_bgcolor="#0F172A",
                font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
                barmode="group",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=320,
                margin=dict(l=20, r=20, t=50, b=20),
            )
            fig_unet.update_yaxes(range=[70, 105], ticksuffix="%")
            st.plotly_chart(fig_unet, use_container_width=True)

    except Exception as e:
        st.info("Chưa thể dựng biểu đồ Plotly.")

    st.markdown("---")
    st.markdown('<div class="section-label">Đặc trưng vận hành lâm sàng của từng kiến trúc</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="clinical-card" style="border-top:3px solid #38BDF8;">
            <div style="font-weight:700; color:#38BDF8; margin-bottom:8px;">YOLOv8s-seg</div>
            <div style="font-size:0.8rem; line-height:1.6; color:#CBD5E1;">
                &bull; <strong>Thế mạnh:</strong> Rất nhạy với khối u màng não (Meningioma đạt 98.7% mAP50).<br>
                &bull; <strong>Ưu điểm:</strong> Xuất đồng thời hộp giới hạn (Bounding Box) và đa giác bao quanh.<br>
                &bull; <strong>Khuyến nghị:</strong> Thích hợp cho bước sàng lọc ban đầu (Screening phase).
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="clinical-card" style="border-top:3px solid #F59E0B;">
            <div style="font-weight:700; color:#F59E0B; margin-bottom:8px;">YOLO11s-seg</div>
            <div style="font-size:0.8rem; line-height:1.6; color:#CBD5E1;">
                &bull; <strong>Thế mạnh:</strong> Kiến trúc C3k2 cải tiến giúp phân đoạn Glioma tốt hơn (+1.2%).<br>
                &bull; <strong>Ưu điểm:</strong> Lượng tham số nhỏ nhất trong dòng YOLO (9.8M), tốc độ suy luận nhanh.<br>
                &bull; <strong>Khuyến nghị:</strong> Thích hợp cho triển khai hệ thống biên (Edge deployment) trên CPU.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="clinical-card" style="border-top:3px solid #10B981;">
            <div style="font-weight:700; color:#10B981; margin-bottom:8px;">Attention U-Net</div>
            <div style="font-size:0.8rem; line-height:1.6; color:#CBD5E1;">
                &bull; <strong>Thế mạnh:</strong> Phân đoạn mức pixel chính xác nhất với cơ chế scSE attention.<br>
                &bull; <strong>Ưu điểm:</strong> Điểm Dice đạt 92.92%, tính toán chính xác thể tích và diện tích mô bệnh.<br>
                &bull; <strong>Khuyến nghị:</strong> Chuẩn mực cho lập kế hoạch xạ trị và đo lường kích thước khối u.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TRANG 3: NHẬT KÝ CA KHÁM (HISTORY)
# ==============================================================================
def render_history_page():
    st.markdown("""
    <div class="clinical-hero">
        <div class="hero-meta">
            <span class="brand-badge">SỔ NHẬT KÝ CA LÂM SÀNG</span>
        </div>
        <div class="hero-title">Lịch Sử Phân Tích Trong Phiên</div>
        <div class="hero-desc">
            Theo dõi tất cả các lượt xử lý hình ảnh, ghi nhận thông số thời gian phản hồi và các mô hình đã được kích hoạt.
        </div>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.session_history
    if not history:
        st.markdown("""
        <div class="clinical-empty">
            <div class="clinical-empty-title">Chưa có nhật ký trong phiên làm việc</div>
            <div class="clinical-empty-desc">Các ca phân tích mới sẽ được tự động lưu trữ tại đây.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    c_del, _ = st.columns([1, 4])
    with c_del:
        if st.button("Xóa nhật ký phiên", type="secondary"):
            st.session_state.session_history = []
            st.rerun()

    st.markdown('<div class="section-label">Danh sách các lượt chẩn đoán gần nhất</div>', unsafe_allow_html=True)
    df_hist = pd.DataFrame([{
        "Thời điểm thực hiện": h["timestamp"],
        "Tên tệp ảnh": h["filename"],
        "Các mô hình thực thi": ", ".join(h["models"]),
        "Tổng thời gian": f"{h['time_ms']:.0f} ms",
    } for h in reversed(history)])
    st.dataframe(df_hist, use_container_width=True, hide_index=True)


# ==============================================================================
# TRANG 4: TÀI LIỆU KỸ THUẬT & GIẢI THUẬT (DOCS)
# ==============================================================================
def render_docs_page():
    st.markdown("""
    <div class="clinical-hero">
        <div class="hero-meta">
            <span class="brand-badge">TÀI LIỆU KHOA HỌC & ĐẶC TẢ HỆ THỐNG</span>
        </div>
        <div class="hero-title">Đặc Tả Kỹ Thuật & Kiến Trúc Giải Thuật</div>
        <div class="hero-desc">
            Thông tin chi tiết về các hàm mất mát (Loss functions), cơ chế Attention scSE, kiến trúc mạng và quy trình tiền xử lý ảnh MRI não.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_arch, tab_dataset, tab_clinical = st.tabs([
        "Kiến trúc mô hình & Loss",
        "Quy chuẩn tập dữ liệu BRISC 2025",
        "Đặc điểm giải phẫu bệnh học",
    ])

    with tab_arch:
        st.markdown("""
        <div class="clinical-card">
            <div class="section-label">1. Attention U-Net (EfficientNet-B0 Backbone)</div>
            <div style="font-size:0.85rem; line-height:1.7; color:#CBD5E1;">
                &bull; <strong>Cơ chế scSE (Spatial and Channel Squeeze & Excitation):</strong> Kết hợp song song Spatial Squeeze & Channel Excitation (sSE) cùng Channel Squeeze & Spatial Excitation (cSE). Cơ chế này giúp mô hình tái hiệu chỉnh bản đồ đặc trưng ở cả không gian không gian ảnh và các kênh đặc trưng, giúp lọc bỏ nhiễu từ các tổ chức mô não lành xung quanh khối u.<br>
                &bull; <strong>Hàm mất mát kết hợp (Combo Loss):</strong><br>
                <code>Loss = 0.5 &times; DiceLoss + 0.5 &times; FocalLoss</code><br>
                Giải quyết triệt để bài toán mất cân bằng nghiêm trọng giữa diện tích nền (Background chiếm > 95%) và diện tích tổn thương (U não chiếm < 5%).
            </div>
        </div>

        <div class="clinical-card">
            <div class="section-label">2. YOLOv8s-seg & YOLO11s-seg (Instance Segmentation)</div>
            <div style="font-size:0.85rem; line-height:1.7; color:#CBD5E1;">
                &bull; <strong>Kiến trúc Anchor-Free:</strong> Loại bỏ các hộp neo định sẵn, dự đoán trực tiếp tọa độ tâm và khoảng cách đến các cạnh, giảm thiểu số lượng dự đoán giả ở vùng nền não.<br>
                &bull; <strong>Proto Module:</strong> Sử dụng Proto-net để tạo ra 32 bản đồ mặt nạ nguyên mẫu (prototype masks), sau đó nhân tuyến tính với hệ số mặt nạ từ mỗi đầu phát hiện đối tượng để tạo ra đa giác phân đoạn sắc nét.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_dataset:
        st.markdown("""
        <div class="clinical-card">
            <div class="section-label">Thống kê phân bố tập dữ liệu BRISC 2025</div>
            <table class="clinical-table">
                <tr><th>Thông số</th><th>Mô tả chi tiết</th></tr>
                <tr><td>Tổng số lượng ảnh</td><td>4,794 ảnh chụp cắt lớp cộng hưởng từ (MRI)</td></tr>
                <tr><td>Tập huấn luyện (Training Set)</td><td>3,966 ảnh (tỉ lệ 82.7%)</td></tr>
                <tr><td>Tập kiểm định (Validation Set)</td><td>693 ảnh (tỉ lệ 14.5%)</td></tr>
                <tr><td>Chuỗi xung cộng hưởng từ</td><td>T1-weighted, T2-weighted, T1 có tiêm cản từ (Gadolinium)</td></tr>
                <tr><td>Định dạng nhãn gốc</td><td>Đa giác nhãn chuẩn MS-COCO JSON</td></tr>
                <tr><td>Định dạng nhãn U-Net</td><td>Mặt nạ phân giải cao Grayscale PNG (0: Nền, 1: Glioma, 2: Meningioma, 3: Pituitary)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with tab_clinical:
        st.markdown("""
        <div class="clinical-card">
            <div class="section-label">Đặc điểm nhận diện 3 nhóm u não trên hình ảnh học MRI</div>
            <div style="font-size:0.85rem; line-height:1.7; color:#CBD5E1;">
                &bull; <strong>U tế bào thần kinh đệm (Glioma):</strong> Khối u nội trục, thường biểu hiện tăng tín hiệu trên T2/FLAIR, giảm tín hiệu trên T1. Ranh giới xâm lấn phù nề xung quanh thường không rõ rệt, đòi hỏi khả năng chú ý đặc trưng mức cao.<br>
                &bull; <strong>U màng não (Meningioma):</strong> Khối u ngoài trục bắt nguồn từ tế bào màng nhện. Ranh giới khối u rất sắc nét với dấu hiệu "đuôi màng cứng" (Dural tail sign) điển hình, giúp các mô hình YOLO đạt độ chính xác phát hiện trên 98%.<br>
                &bull; <strong>U tuyến yên (Pituitary Adenoma):</strong> Nằm ở vị trí khu trú hố yên, có thể phát triển lên trên gây chèn ép giao thoa thị giác. Kích thước tương đối đồng nhất và khu trú.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# HÀM CHÍNH
# ==============================================================================
def main():
    selected_models, conf_threshold, mask_opacity = render_sidebar()
    page = st.session_state.current_page

    if page == "analysis":
        render_analysis_page(selected_models, conf_threshold, mask_opacity)
    elif page == "benchmark":
        render_benchmark_page()
    elif page == "history":
        render_history_page()
    elif page == "docs":
        render_docs_page()

    st.markdown("""
    <div class="footer-bar">
        NEUROSCAN CADx v1.0 &bull; Hệ thống Phân tích & Phân đoạn U Não Tự động<br>
        Phát triển phục vụ mục đích nghiên cứu học thuật và hỗ trợ đào tạo lâm sàng.<br>
        Khuyến cáo: Mọi kết quả phân tích định lượng cần được đối chiếu và thẩm định bởi bác sĩ chẩn đoán hình ảnh chuyên khoa.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
