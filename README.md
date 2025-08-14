# PDF Key-Value Extractor

Extract key-value pairs from PDFs using EasyOCR and Streamlit.

## Warning

This app uses OCR (Object Character Recognition) to extract text from PDFs. It is not perfect and may not work for all PDFs.
It also uses Pytorch and EasyOCR, which will run SIGNIFICANTLY faster on a GPU, running it on CPU alone will be slow.

## Local Setup

### Prerequisites
- Python 3.8+
- `poppler-utils` (for PDF conversion)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Application
```bash
streamlit run app_easyocr_simplified.py --server.address=0.0.0.0
```

Access at: http://localhost:8501

## Docker Setup

### Build & Run
```bash
docker-compose up --build
```

### Access
http://localhost:8501

### Stop
```bash
docker-compose down
```