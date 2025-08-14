# Use NVIDIA CUDA base image for GPU support
# FROM nvidia/cuda:11.8-runtime-ubuntu20.04
FROM python:3.12-slim

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    # software-properties-common \
    # && add-apt-repository ppa:deadsnakes/ppa \
    # && apt-get update && apt-get install -y \
    # python3.12 \
    # python3.12-pip \
    # python3.12-venv \
    # python3.12-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# # Set Python 3.12 as default
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
# RUN update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.12 1

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY app_easyocr_simplified.py .

# Expose Streamlit port
EXPOSE 8501

# Configure Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Run Streamlit app
CMD ["streamlit", "run", "app_easyocr_simplified.py", "--server.port=8501", "--server.address=0.0.0.0"]