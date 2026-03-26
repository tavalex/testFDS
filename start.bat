@echo off
echo Installing dependencies...
pip install flask pdfplumber
echo.
echo Starting FDS Manager...
echo Open your browser at: http://localhost:5000
echo.
python app.py
pause
