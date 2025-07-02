
#!/usr/bin/env python3
"""
Legal Document Index Generator (Enhanced)
Extracts and indexes legal concepts, terms, and rules from PDF documents.
Combines comprehensive term recognition with efficient processing.
"""

import argparse
import sys
from legal_indexer.extractor import extract_text_from_pdf
from legal_indexer.indexer import LegalIndexer
from legal_indexer.utils import save_output, get_statistics

class LegalIndexGenerator:
    def __init__(self, page_offset: int = 0):
        self.indexer = LegalIndexer(page_offset=page_offset)
        self.page_content = {}

    def process_document(self, pdf_path: str):
        """Main processing function with progress indication."""
        print(f"Processing document: {pdf_path}")
        
        self.page_content = extract_text_from_pdf(pdf_path)
        total_pages = len(self.page_content)
        
        if total_pages == 0:
            print("Error: No pages extracted from PDF")
            return
            
        print(f"Extracted text from {total_pages} pages")
        
        # Process pages with progress indication
        for i, (page_num, text) in enumerate(self.page_content.items(), 1):
            if i % 10 == 0 or i == total_pages:
                print(f"Processing page {i}/{total_pages}...")
                
            if text.strip():
                self.indexer.identify_legal_concepts(text, page_num)
                self.indexer.extract_key_phrases(text, page_num)
        
        self.indexer.build_cross_references()
        print(f"Identified {len(self.indexer.index)} unique legal concepts and terms")

def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive legal index from PDF documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m legal_indexer.main document.pdf
  python -m legal_indexer.main document.pdf -o my_index.pdf
  python -m legal_indexer.main document.pdf --format json -o index.json
  python -m legal_indexer.main document.pdf --no-subcategories
        """
    )
    
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('-o', '--output', default='legal_index.txt',
                       help='Output file path (default: legal_index.txt)')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'pdf', 'docx', 'csv', 'xml', 'md'],
                       help='Output format (default: auto-detect from output file extension)')
    parser.add_argument('--no-subcategories', action='store_true',
                       help='Exclude subcategory details in text output')
    parser.add_argument('--stats', action='store_true',
                       help='Print statistics about the indexing')
    parser.add_argument('--page-offset', type=int, default=0,
                       help='Offset for page numbers (e.g., -4 if content starts on page 5)')
    
    args = parser.parse_args()
    
    try:
        # Determine output format
        output_format = args.format
        if not output_format:
            ext = args.output.split('.')[-1].lower()
            if ext in ['json', 'pdf', 'docx', 'csv', 'xml', 'md']:
                output_format = ext
            else:
                output_format = 'text'

        # Create and run the generator
        generator = LegalIndexGenerator(page_offset=args.page_offset)
        generator.process_document(args.input_pdf)
        
        # Save output
        save_output(
            args.output, 
            generator.indexer.index,
            generator.indexer.cross_references,
            format=output_format, 
            include_subcategories=not args.no_subcategories
        )
        
        # Print statistics if requested
        if args.stats:
            stats = get_statistics(generator.indexer.index, generator.page_content)
            print("\nIndexing Statistics:")
            print(f"Total terms indexed: {stats['total_terms']}")
            print(f"Total pages: {stats['total_pages']}")
            print(f"Pages with content: {stats['pages_with_content']}")
            print("\nTerms by category:")
            for category, count in sorted(stats['terms_by_category'].items()):
                print(f"  {category.replace('_', ' ').title()}: {count}")
        
        print("\nIndex generation complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
