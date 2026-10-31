# Nghiên Cứu và Đánh Giá Toàn Diện Các Kiến Trúc Học Sâu Phân Đoạn Đa Mô Hình Khối U Não Trên Ảnh Cộng Hưởng Từ Kết Hợp Tối Ưu Hóa Ranh Giới Lâm Sàng

* **Tác giả:** Trần Mạnh Hùng
* **Giảng viên hướng dẫn:** ThS. Hoàng Văn Quý
* **Đơn vị:** Phân hiệu Trường Đại học Thủy Lợi, TP. Hồ Chí Minh

---

## Cấu trúc thư mục dự án chuẩn hóa (Project Structure)

```
Tumor/
├── docs/                       # Thư mục tài liệu báo cáo khoa học và slide
│   ├── Bao_Cao_Khoa_Hoc_Springer_Nature.docx      # Báo cáo khoa học hoàn chỉnh (Word chuẩn Springer)
│   ├── Bao_Cao_Khoa_Hoc_Springer_Nature.pdf       # Báo cáo khoa học xuất định dạng PDF
│   └── Bao_Cao_Khoa_Hoc_Springer_Nature.pptx      # Slide thuyết trình PowerPoint 16:9 (16 Slides)
│
├── WebApp/                     # Hệ thống phần mềm chẩn đoán hình ảnh NeuroScan CADx (Streamlit)
│   ├── app.py                  # Mã nguồn ứng dụng web chính
│   ├── models/                 # Kiến trúc nạp 6 mô hình học sâu
│   ├── utils/                  # Tiện ích tiền xử lý, tính RECIST 1.1 và vẽ đồ họa
│   └── start_app.bat           # File khởi chạy nhanh ứng dụng
│
├── weights/                    # Trọng số tối ưu đã huấn luyện của 6 mô hình học sâu
│   ├── best_yolov8s.pt         # Trọng số YOLOv8s-seg
│   ├── best_yolo11s.pt         # Trọng số YOLO11s-seg
│   ├── best_attention_unet.pt  # Trọng số Attention U-Net
│   ├── best_boundary_unet.pt   # Trọng số Boundary-Aware Attention U-Net
│   ├── best_resunet_plusplus.pt# Trọng số ResNeXt50-UNet++
│   └── best_segformer_transformer.pt # Trọng số SegFormer MiT-B2
│
├── pipeline/                   # Đường ống tiền xử lý y khoa tự động và hàm mất mát
│   ├── mri_preprocessor.py     # Bóc tách hộp sọ (Skull Stripping) & CLAHE
│   └── boundary_loss.py        # Hàm mất mát biên độ dựa trên bản đồ khoảng cách dấu (SDF)
│
├── metrics/                    # Module đánh giá lâm sàng
│   └── clinical_evaluator.py   # Tính toán Hausdorff HD95, ASSD, Dice, IoU và RECIST 1.1
│
├── xai/                        # Trí tuệ nhân tạo giải thích được (Explainable AI)
│   └── grad_cam_engine.py      # Trích xuất bản đồ nhiệt Grad-CAM từ tầng tích chập cuối
│
├── cadx/                       # Module xuất bệnh án y khoa
│   └── clinical_reporter.py    # Tự động xuất phiếu kết quả chẩn đoán định dạng PDF ReportLab
│
├── report_figures/             # 6 hình ảnh khoa học chất lượng cao phục vụ báo cáo và slide
├── benchmarks/                 # Bảng số liệu đối chuẩn CSV chi tiết
├── notebooks/                  # Sổ tay Jupyter Notebooks huấn luyện trên Kaggle GPU
├── cadx_output/                # Mẫu phiếu kết quả PDF và lưới ảnh kiểm thử ngoại kiểm
├── scripts/                    # Các kịch bản tự động hóa chính
└── Tumor.v1i.coco/             # Bộ dữ liệu sọ não BRISC 2025 gốc
```

python -m streamlit run WebApp/app.py