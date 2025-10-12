@echo off
echo Starting Workout Recommender App...
echo.
echo Make sure you have:
echo - Trained the model (run: python train.py)
echo - Installed dependencies (run: pip install -r requirement.txt)
echo.
echo Starting Streamlit app...
D:\DOWNLOADS\workout-recommender\.venv\Scripts\python.exe -m streamlit run app.py
pause