
import fitz  # PyMuPDF
import PyPDF2
import os
from typing import Dict

def extract_text_from_pdf(pdf_path: str) -> Dict[int, str]:
    """Extract text from PDF using PyMuPDF with fallback to PyPDF2."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    try:
        doc = fitz.open(pdf_path)
        pages = {}
        for i in range(doc.page_count):
            try:
                text = doc[i].get_text()
                pages[i + 1] = text
            except Exception as e:
                print(f"Warning: Error extracting page {i + 1}: {e}")
                pages[i + 1] = ""
        doc.close()
        return pages
    except Exception as e:
        print(f"PyMuPDF error: {e}. Falling back to PyPDF2.")
        return _extract_with_pypdf2(pdf_path)

def _extract_with_pypdf2(pdf_path: str) -> Dict[int, str]:
    """Fallback extraction using PyPDF2."""
    pages = {}
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                try:
                    pages[i + 1] = page.extract_text() or ""
                except Exception as e:
                    print(f"Warning: Error extracting page {i + 1}: {e}")
                    pages[i + 1] = ""
    except Exception as e:
        print(f"Error reading PDF with PyPDF2: {e}")
        return {}
    return pages
