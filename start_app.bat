@echo off
title NeuroScan CADx - Brain Tumor Segmentation
echo ======================================================================
echo  HE THONG HO TRO CHAN DOAN VA DINH LUONG KHOI U NAO MRI (CADx)
echo ======================================================================
echo.
echo [1/2] Dang kiem tra moi truong va thu vien...
python -c "import streamlit, torch, ultralytics; print('-> Moi truong PyTorch & Streamlit san sang!')" 2>nul
if %errorlevel% neq 0 (
    echo [CANH BAO] Co the chua cai dat du thu vien. Dang tu dong cai dat requirements.txt...
    pip install -r requirements.txt
)

echo.
echo [2/2] Dang khoi chay giao dien WebApp tai cong 8501...
echo Trinh duyet se tu dong mo tai: http://localhost:8501
echo (Nhan Ctrl+C de dung ung dung)
echo ----------------------------------------------------------------------
echo.

python -m streamlit run WebApp/app.py --server.port 8501 --server.address localhost

pause
