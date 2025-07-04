
#!/bin/bash

# Legal Index Generator Docker Entrypoint
set -e

# Validate required environment variables
if [ -z "$INPUT_PDF" ]; then
    echo "Error: INPUT_PDF environment variable is required"
    exit 1
fi

if [ -z "$OUTPUT_FILE" ]; then
    echo "Error: OUTPUT_FILE environment variable is required"
    exit 1
fi

# Check if input PDF exists
if [ ! -f "$INPUT_PDF" ]; then
    echo "Error: Input PDF file '$INPUT_PDF' does not exist"
    echo "Available files in /input:"
    ls -la /input/ 2>/dev/null || echo "No files found in /input directory"
    exit 1
fi

# Create output directory if it doesn't exist
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
mkdir -p "$OUTPUT_DIR"

# Build command arguments
ARGS=("$INPUT_PDF" "-o" "$OUTPUT_FILE")

# Add format flag if provided
if [ -n "$OUTPUT_FORMAT" ]; then
    ARGS+=("--format" "$OUTPUT_FORMAT")
fi

# Add no-subcategories flag if disabled
if [ "${INCLUDE_SUBCATEGORIES,,}" = "false" ]; then
    ARGS+=("--no-subcategories")
fi

# Add terms-only flag if enabled
if [ "${TERMS_ONLY,,}" = "true" ]; then
    ARGS+=("--terms-only")
fi

# Add stats flag if enabled
if [ "${SHOW_STATS,,}" = "true" ]; then
    ARGS+=("--stats")
fi

# Add page offset if provided
if [ -n "$PAGE_OFFSET" ]; then
    ARGS+=("--page-offset" "$PAGE_OFFSET")
fi

echo "Starting Legal Index Generator..."
echo "Input PDF: $INPUT_PDF"
echo "Output File: $OUTPUT_FILE"
echo "Output Format: $OUTPUT_FORMAT"
echo "Include Subcategories: $INCLUDE_SUBCATEGORIES"
echo "Terms Only: $TERMS_ONLY"
echo "Show Stats: $SHOW_STATS"
echo "Page Offset: $PAGE_OFFSET"

# Load custom terms if provided
if [ -n "$CUSTOM_TERMS_FILE" ] && [ -f "$CUSTOM_TERMS_FILE" ]; then
    echo "Custom terms file: $CUSTOM_TERMS_FILE"
    # Note: You'd need to modify the Python script to accept custom terms file
fi

echo "Running command: legal-indexer ${ARGS[*]}"
echo "----------------------------------------"

# Execute the legal indexer
legal-indexer "${ARGS[@]}"

# Verify output was created
if [ -f "$OUTPUT_FILE" ]; then
    echo "----------------------------------------"
    echo "✅ Legal index generated successfully!"
    echo "📄 Output file: $OUTPUT_FILE"
    echo "📊 File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
    
    # Show file details
    echo "📁 File details:"
    ls -la "$OUTPUT_FILE"
    
    # Show preview if text format
    if [ "${OUTPUT_FORMAT,,}" != "json" ]; then
        echo ""
        echo "📋 Index preview (first 5 lines):"
        echo "----------------------------------------"
        head -n 5 "$OUTPUT_FILE"
        echo "----------------------------------------"
    fi
else
    echo "❌ Error: Output file was not created"
    exit 1
fi

echo "Legal indexing complete!"
