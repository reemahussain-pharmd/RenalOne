@echo off
echo.
echo  ====================================================
echo   RenalCare OS - Installing Dependencies
echo  ====================================================
echo.
pip install streamlit plotly pandas numpy scikit-learn reportlab python-dotenv
pip install openai google-generativeai
echo.
echo  Optional (for full RAG):
echo  pip install faiss-cpu sentence-transformers PyPDF2
echo.
echo  Installation complete. Run: streamlit run app.py
pause
