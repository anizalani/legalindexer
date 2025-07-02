
import unittest
from unittest.mock import patch, MagicMock
from legal_indexer.extractor import extract_text_from_pdf

class TestExtractor(unittest.TestCase):

    @patch('fitz.open')
    def test_extract_text_from_pdf_success(self, mock_fitz_open):
        # Mock the PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 2
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "This is page 1."
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "This is page 2."
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_fitz_open.return_value = mock_doc

        # Call the function
        pages = extract_text_from_pdf("dummy.pdf")

        # Assert the results
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[1], "This is page 1.")
        self.assertEqual(pages[2], "This is page 2.")

    @patch('fitz.open', side_effect=Exception("PyMuPDF error"))
    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_pdf_fallback(self, mock_pdf_reader, mock_fitz_open):
        # Mock the PDF reader
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock(), MagicMock()]
        mock_reader.pages[0].extract_text.return_value = "Fallback page 1."
        mock_reader.pages[1].extract_text.return_value = "Fallback page 2."
        mock_pdf_reader.return_value = mock_reader

        # Call the function
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'')):
            pages = extract_text_from_pdf("dummy.pdf")

        # Assert the results
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[1], "Fallback page 1.")
        self.assertEqual(pages[2], "Fallback page 2.")

if __name__ == '__main__':
    unittest.main()
