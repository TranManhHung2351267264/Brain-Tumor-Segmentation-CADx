@echo off
echo ============================================
echo  NeuroScan AI - Brain Tumor Segmentation
echo ============================================
echo.
echo Dang khoi dong ung dung...
echo.
cd /d "%~dp0"
python -m streamlit run app.py --server.port 8501 --server.address localhost
pause
