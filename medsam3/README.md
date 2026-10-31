# Hướng Dẫn Fine-Tuning MedSAM3 (LoRA) Cho Phân Đoạn U Não MRI

## 1. Tổng quan
Thư mục này chứa toàn bộ đường ống (pipeline) triển khai Fine-tuning mô hình nền tảng y tế thế hệ mới **MedSAM3** (`lal-Joey/MedSAM3_v1b` - *Segment Anything with Medical Concepts*, arXiv:2511.19046) bằng phương pháp **LoRA (Low-Rank Adaptation)** trên bộ dữ liệu U não BRISC 2025 (4.794 ảnh).

Khác biệt với SAM truyền thống (cần click chuột hoặc vẽ hộp bao), MedSAM3 cho phép bác sĩ phân đoạn trực tiếp bằng câu lệnh văn bản lâm sàng (**Concept-Guided Promptable Segmentation**):
* `"brain glioma tumor"` -> Tự động tìm và khoanh u thần kinh đệm.
* `"brain meningioma tumor"` -> Tự động khoanh u màng não.
* `"brain pituitary adenoma"` -> Tự động khoanh u tuyến yên.

---

## 2. Cấu trúc thư mục
```text
medsam3/
├── configs/
│   └── lora_brain_tumor.yaml      # Cấu hình LoRA (rank=8, alpha=16.0, Vision + DETR + Mask Decoder)
├── dataset_metadata/
│   ├── train_samples.json         # Siêu dữ liệu tập Train (3,966 mẫu)
│   ├── val_samples.json           # Siêu dữ liệu tập Validation (693 mẫu)
│   └── dataset_summary.json       # Thống kê tổng hợp phân bố 3 nhóm u
├── data_converter.py              # Script tự động trích xuất metadata và prompt văn bản
├── train_lora_tumor.py            # Script PyTorch huấn luyện LoRA (hỗ trợ GPU / Kaggle)
└── infer_medsam3.py               # Script suy luận từ ảnh MRI + Text Prompt ra kết quả RECIST 1.1
```

---

## 3. Các bước chạy Fine-Tuning trên Kaggle GPU (Tesla T4 16GB)

### Bước 1: Mở Notebook trên Kaggle
Mở sổ tay [notebooks/Kaggle_FineTune_MedSAM3_Tumor.ipynb](../notebooks/Kaggle_FineTune_MedSAM3_Tumor.ipynb) và tải lên Kaggle Notebooks (bật Settings -> Accelerator -> **GPU T4 x2** hoặc **GPU P100**).

### Bước 2: Cài đặt thư viện & nạp trọng số LoRA
```bash
git clone https://github.com/Joey-S-Liu/MedSAM3.git
cd MedSAM3 && pip install -q -e .
pip install -q peft transformers
```

### Bước 3: Chạy lệnh huấn luyện
```bash
python medsam3/train_lora_tumor.py --config medsam3/configs/lora_brain_tumor.yaml
```

Mô hình sẽ tự động lưu checkpoint có điểm Dice cao nhất tại:
`weights/medsam3_lora_tumor/best_medsam3_tumor_lora.pt`

---

## 4. Kiểm thử suy luận (Inference)
Chạy lệnh suy luận mẫu trên ca bệnh U Glioma:
```bash
python medsam3/infer_medsam3.py --image test_images/case4_glioma.jpg --prompt "brain glioma tumor"
```
Kết quả sẽ xuất ra ảnh đa giác u kèm các thông số chuẩn y tế RECIST 1.1 ($D_{\max}$, $D_{\min}$, diện tích $mm^2$).
