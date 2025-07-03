
FROM python:3.12-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy setup.py and install the package
COPY setup.py .
COPY legal_indexer/ ./legal_indexer
RUN pip install .

# Create directories for input/output
RUN mkdir -p /input /output

# Set default environment variables
ENV INPUT_PDF="/input/document.pdf"
ENV OUTPUT_FILE="/output/legal_index.txt"
ENV INCLUDE_SUBCATEGORIES="true"
ENV SHOW_STATS="true"
ENV CUSTOM_TERMS_FILE=""
ENV PAGE_OFFSET="0"

# Create entrypoint script
ENTRYPOINT ["python3", "-m", "legal_indexer.main"]

