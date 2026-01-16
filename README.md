# Scientific Paper Analyzer (MVP)

An interactive NLP-based application to analyze scientific papers (PDF).

## 🚀 Features
- PDF text extraction
- Automatic section detection (Abstract, Introduction, etc.)
- Keyword extraction (TF-IDF)
- Automatic summarization (TextRank)
- Metadata extraction (title, year, emails)
- Interactive Streamlit interface
- Exportable JSON report

## 🛠 Tech Stack
- Python
- Streamlit
- Scikit-learn
- Sumy (TextRank)
- PDF parsing libraries

## ▶️ How to run
```bash
pip install -r requirements.txt
streamlit run app/app.py

## 🎯 Purpose
This project was built as a hands-on NLP application to explore
scientific document understanding, text mining, and data-driven analysis.

## 📂 Project Structure
app/        # Streamlit application
src/        # NLP and processing modules
data/       # Sample scientific papers
outputs/    # Generated JSON reports


