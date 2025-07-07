
#!/usr/bin/env python3
"""
Legal Document Index Generator (Enhanced)
Extracts and indexes legal concepts, terms, and rules from PDF documents.
Combines comprehensive term recognition with efficient processing.
"""

import argparse
import sys
import json
import os
from legal_indexer.extractor import extract_text_from_pdf
from legal_indexer.indexer import LegalIndexer
from legal_indexer.utils import save_output, get_statistics, get_table_of_contents

class LegalIndexGenerator:
    def __init__(self, legal_terms: dict, page_offset: int = 0, terms_only: bool = False):
        self.indexer = LegalIndexer(legal_terms=legal_terms, page_offset=page_offset, terms_only=terms_only)
        self.page_content = {}
        self.toc = {}

    def process_document(self, pdf_path: str):
        """Main processing function with progress indication."""
        print(f"Processing document: {pdf_path}")
        
        self.toc = get_table_of_contents(pdf_path, self.indexer.page_offset)
        self.page_content = extract_text_from_pdf(pdf_path)
        total_pages = len(self.page_content)
        
        if total_pages == 0:
            print("Error: No pages extracted from PDF")
            return
            
        print(f"Extracted text from {total_pages} pages")
        
        # Process pages with progress indication
        current_headings = [None] * 5
        for i, (page_num, text) in enumerate(self.page_content.items(), 1):
            if i % 10 == 0 or i == total_pages:
                print(f"Processing page {i}/{total_pages}...")
            
            # This is a simplified heading update. A more robust solution would analyze font changes.
            for l1, l2_dict in self.toc.items():
                for l2, l3_dict in l2_dict.items():
                    for l3, l4_val in l3_dict.items():
                        if isinstance(l4_val, dict):
                            if list(l4_val.values())[0] == page_num:
                                current_headings = [l1, l2, l3, None, None]
                        elif l4_val == page_num:
                            current_headings = [l1, l2, l3, None, None]


            self.indexer.set_current_headings(current_headings)

            if text.strip():
                self.indexer.identify_legal_concepts(text, page_num)
                self.indexer.extract_key_phrases(text, page_num)
        
        self.indexer.build_cross_references()
        print(f"Identified {len(self.indexer.index)} unique legal concepts and terms")

def load_legal_terms(custom_terms_file: str = None) -> dict:
    """Load legal terms from a JSON file."""
    if custom_terms_file and os.path.exists(custom_terms_file):
        terms_file = custom_terms_file
    else:
        # Default path relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        terms_file = os.path.join(script_dir, 'legal_terms.json')

    try:
        with open(terms_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading legal terms from {terms_file}: {e}")
        sys.exit(1)

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
  python -m legal_indexer.main document.pdf --terms-only
  python -m legal_indexer.main document.pdf --custom-terms my_terms.json
  python -m legal_indexer.main document.pdf --columns 2
  python -m legal_indexer.main document.pdf --suppress-categories subdivisions
  python -m legal_indexer.main document.pdf --context-style headings
        """
    )
    
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('-o', '--output', default='legal_index.txt',
                       help='Output file path (default: legal_index.txt)')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'pdf', 'docx', 'csv', 'xml', 'md'],
                       help='Output format (default: auto-detect from output file extension)')
    parser.add_argument('--no-subcategories', action='store_true',
                       help='Exclude subcategory details in text output')
    parser.add_argument('--terms-only', action='store_true',
                        help='Only index defined terms, excluding case and statutory references')
    parser.add_argument('--stats', action='store_true',
                       help='Print statistics about the indexing')
    parser.add_argument('--page-offset', type=int, default=0,
                       help='Offset for page numbers (e.g., -4 if content starts on page 5)')
    parser.add_argument('--custom-terms', help='Path to a custom legal terms JSON file')
    parser.add_argument('--columns', type=int, default=1, help='Number of columns for DOCX output')
    parser.add_argument('--suppress-categories', nargs='+', help='List of categories to suppress from the output')
    parser.add_argument('--context-style', choices=['none', 'snippet', 'headings'], default='none', help='Style of context to display for each term.')
    
    args = parser.parse_args()
    
    try:
        # Load legal terms
        legal_terms = load_legal_terms(args.custom_terms)

        # Determine output format
        output_format = args.format
        if not output_format:
            ext = args.output.split('.')[-1].lower()
            if ext in ['json', 'pdf', 'docx', 'csv', 'xml', 'md']:
                output_format = ext
            else:
                output_format = 'text'

        # Create and run the generator
        generator = LegalIndexGenerator(
            legal_terms=legal_terms,
            page_offset=args.page_offset, 
            terms_only=args.terms_only
        )
        generator.process_document(args.input_pdf)
        
        # Save output
        save_output(
            args.output, 
            generator.indexer.index,
            generator.indexer.cross_references,
            generator.toc,
            format=output_format, 
            include_subcategories=not args.no_subcategories,
            terms_only=args.terms_only,
            columns=args.columns,
            suppress_categories=args.suppress_categories,
            context_style=args.context_style
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
