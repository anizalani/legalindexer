FROM python:3.12-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the legal indexer script
COPY legal_index.py .

# Create directories for input/output
RUN mkdir -p /input /output

# Set default environment variables
ENV INPUT_PDF="/input/document.pdf"
ENV OUTPUT_FILE="/output/legal_index.txt"
ENV OUTPUT_FORMAT="text"
ENV INCLUDE_SUBCATEGORIES="true"
ENV SHOW_STATS="true"
ENV CUSTOM_TERMS_FILE=""

# Create entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]