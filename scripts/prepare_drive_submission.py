"""
Tự động đóng gói và chuẩn bị thư mục nộp bài lên Google Drive theo đúng cấu trúc yêu cầu:
- bao_cao/
- slide/
- data.zip
- link_data.txt (kèm bản sao META.txt)
- source-code.zip
"""

import os
import sys
import shutil
import zipfile
import time

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def zip_folder(source_dir, output_zip_path, exclude_dirs=None, exclude_exts=None, prefix=""):
    exclude_dirs = set(exclude_dirs or [])
    exclude_exts = set(exclude_exts or [])
    
    print(f"Bắt đầu nén: {output_zip_path} ...")
    start_time = time.time()
    count = 0
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.git') and d != '__pycache__']
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_exts or file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)
                archive_name = os.path.join(prefix, rel_path) if prefix else rel_path
                zipf.write(file_path, archive_name)
                count += 1
                if count % 500 == 0:
                    print(f"  Đã nén {count} tệp...")
    elapsed = time.time() - start_time
    size_mb = os.path.getsize(output_zip_path) / (1024 * 1024)
    print(f"Đã hoàn thành {output_zip_path}: {count} tệp, kích thước {size_mb:.2f} MB ({elapsed:.1f}s)")

def main():
    base_dir = r"D:\Học Sâu và Ứng dụng\Tumor"
    dest_dir = os.path.join(base_dir, "nop_bai_drive")
    os.makedirs(dest_dir, exist_ok=True)
    
    # 1. Thư mục bao_cao
    bao_cao_dir = os.path.join(dest_dir, "bao_cao")
    os.makedirs(bao_cao_dir, exist_ok=True)
    shutil.copy2(os.path.join(base_dir, "docs", "Bao_Cao_Khoa_Hoc_Springer_Nature.docx"), bao_cao_dir)
    shutil.copy2(os.path.join(base_dir, "docs", "Bao_Cao_Khoa_Hoc_Springer_Nature.pdf"), bao_cao_dir)
    print("Đã tạo thư mục bao_cao/")
    
    # 2. Thư mục slide
    slide_dir = os.path.join(dest_dir, "slide")
    os.makedirs(slide_dir, exist_ok=True)
    shutil.copy2(os.path.join(base_dir, "docs", "Bao_Cao_Khoa_Hoc_Springer_Nature.pptx"), slide_dir)
    shutil.copy2(os.path.join(base_dir, "docs", "Bao_Cao_Khoa_Hoc_Springer_Nature_Slide.pdf"), slide_dir)
    shutil.copy2(os.path.join(base_dir, "docs", "Kich_Ban_Thuyet_Trinh_Springer_Nature.docx"), slide_dir)
    print("Đã tạo thư mục slide/")
    
    # 3. File link_data.txt & META.txt
    link_data_content = """================================================================================
THÔNG TIN BÁO CÁO KHOA HỌC & ĐỒ ÁN MÔN HỌC
HỆ THỐNG HỖ TRỢ CHẨN ĐOÁN VÀ ĐỊNH LƯỢNG HÌNH THÁI HỌC KHỐI U NÃO TRÊN ẢNH MRI (CADx)
================================================================================

1. THÔNG TIN SINH VIÊN
- Họ và tên: Trần Mạnh Hùng
- Mã sinh viên: 2351267264
- Email: 2351267264@e.tlu.edu.vn

2. LIÊN KẾT MÃ NGUỒN (GITHUB REPOSITORY)
- GitHub Repository: https://github.com/TranManhHung2351267264/Brain-Tumor-Segmentation-CADx
- Mã nguồn đầy đủ với phiên bản quản lý git, tài liệu Springer Nature, slide PPTX và trọng số mô hình (.pt) được quản lý qua Git LFS:
  + YOLOv8s-seg: weights/best_yolov8s.pt
  + YOLO11s-seg: weights/best_yolo11s.pt
  + Attention U-Net: weights/best_attention_unet.pt
  + Boundary-Aware U-Net: weights/best_boundary_unet.pt
  + ResUNet++: weights/best_resunet_plusplus.pt
  + SegFormer (Transformer MiT-B0): weights/best_segformer_transformer.pt

3. LIÊN KẾT DỮ LIỆU HUẤN LUYỆN (DATASET)
- Dữ liệu gốc huấn luyện phân đoạn đa lớp MRI Brain Tumor (Roboflow Universe):
  https://universe.roboflow.com/trn-mnh-hng/tumor-3keel-dzyaf
  (Bao gồm 4.794 ảnh MRI được tiền xử lý và gán nhãn đa giác viền chuẩn theo định dạng COCO & YOLOv8/11)
- Dữ liệu tham chiếu & kiểm chuẩn mở rộng (Kaggle Brain Tumor MRI Dataset):
  https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
  (Bao gồm 7.023 ảnh lát cắt MRI sọ não thuộc 4 phân lớp bệnh lý lâm sàng)

4. LIÊN KẾT THƯ MỤC NỘP BÀI GOOGLE DRIVE
- Thư mục nộp bài Google Drive:
  https://drive.google.com/drive/folders/1s6H1zg-Feky_TOCnj8dICbrlPNGwiJ3Z?usp=sharing

5. HƯỚNG DẪN KHỞI CHẠY ỨNG DỤNG LÂM SÀNG (WEBAPP CADX)
- Bước 1: Mở Terminal/PowerShell tại thư mục mã nguồn
- Bước 2: Cài đặt các gói thư viện phụ thuộc:
    pip install -r requirements.txt
- Bước 3: Khởi chạy giao diện chẩn đoán tương tác Streamlit:
    python -m streamlit run WebApp/app.py
- Bước 4: Mở trình duyệt tại địa chỉ http://localhost:8501 để thực hiện suy luận đơn ảnh, ảnh DICOM, xử lý hàng loạt hoặc đối sánh 6 mô hình.
================================================================================
"""
    with open(os.path.join(dest_dir, "link_data.txt"), "w", encoding="utf-8") as f:
        f.write(link_data_content)
    with open(os.path.join(dest_dir, "META.txt"), "w", encoding="utf-8") as f:
        f.write(link_data_content)
    print("Đã tạo file link_data.txt và META.txt")
    
    # 4. Nén data.zip
    data_zip_path = os.path.join(dest_dir, "data.zip")
    coco_dir = os.path.join(base_dir, "Tumor.v1i.coco")
    if os.path.exists(coco_dir):
        zip_folder(coco_dir, data_zip_path, prefix="data")
    else:
        print("Cảnh báo: Không tìm thấy thư mục Tumor.v1i.coco!")
        
    # 5. Nén source-code.zip
    # Các thư mục mã nguồn cốt lõi cần đưa vào:
    source_zip_path = os.path.join(dest_dir, "source-code.zip")
    include_items = [
        "WebApp", "pipeline", "cadx", "xai", "metrics", "scripts",
        "notebooks", "benchmarks", "report_figures", "cadx_output",
        "weights", "README.md", "requirements.txt", ".gitignore", ".gitattributes"
    ]
    
    print(f"Bắt đầu nén source-code.zip...")
    start_src = time.time()
    with zipfile.ZipFile(source_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for item in include_items:
            item_path = os.path.join(base_dir, item)
            if not os.path.exists(item_path):
                print(f"  Bỏ qua {item} (không tồn tại)")
                continue
            if os.path.isfile(item_path):
                zipf.write(item_path, os.path.join("source-code", item))
            elif os.path.isdir(item_path):
                for root, dirs, files in os.walk(item_path):
                    dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
                    for file in files:
                        if file.endswith('.pyc') or file.endswith('.tmp'):
                            continue
                        f_path = os.path.join(root, file)
                        rel_path = os.path.relpath(f_path, base_dir)
                        zipf.write(f_path, os.path.join("source-code", rel_path))
    elapsed_src = time.time() - start_src
    src_size_mb = os.path.getsize(source_zip_path) / (1024 * 1024)
    print(f"Đã hoàn thành source-code.zip: kích thước {src_size_mb:.2f} MB ({elapsed_src:.1f}s)")
    
    print("\n--- HOÀN TẤT CHUẨN BỊ THƯ MỤC NỘP BÀI DRIVE ---")
    for item in os.listdir(dest_dir):
        p = os.path.join(dest_dir, item)
        if os.path.isdir(p):
            print(f"  [Thư mục] {item}/ ({len(os.listdir(p))} tệp)")
        else:
            print(f"  [Tệp]     {item} ({os.path.getsize(p) / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
