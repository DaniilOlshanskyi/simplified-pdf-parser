FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    # libglib2.0-0 \
    # libsm6 \
    # libxext6 \
    # libxrender-dev \
    # libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app_easyocr_simplified.py .
COPY test_pdfs/ ./test_pdfs/

# Create output directory
RUN mkdir -p /app/output

# Run the EasyOCR script
CMD ["python", "app_easyocr_simplified.py"]
