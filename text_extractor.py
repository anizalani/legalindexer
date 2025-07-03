from legal_indexer.extractor import extract_text_from_pdf
import json
import sys

if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
    print(json.dumps(extract_text_from_pdf(pdf_path)))
