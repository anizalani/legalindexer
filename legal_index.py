#!/usr/bin/env python3
"""
Legal Document Index Generator (Enhanced)
Extracts and indexes legal concepts, terms, and rules from PDF documents.
Combines comprehensive term recognition with efficient processing.
"""

import re
import fitz  # PyMuPDF
import PyPDF2
from collections import defaultdict, OrderedDict
import argparse
import json
from typing import Dict, List, Set, Tuple
import sys
import os

# Enhanced Legal Patterns
LEGAL_PATTERNS = {
    'ny_statutes': r'(?:N\.Y\.|New York)\s*[A-Za-z\s]*\s*(?:Law|Code)\s*(?:\u00a7|Section|§)\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
    'cplr_rules': r'CPLR\s*(?:\u00a7|§)?\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
    'cpl_rules': r'CPL\s*(?:\u00a7|§)?\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
    'generic_rules': r'Rule\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
    'cases': r'[A-Z][a-zA-Z\s&\.\-]{2,30}\s+v\.?\s+[A-Z][a-zA-Z\s&\.\-]{2,30}',
    'sections': r'(?:\u00a7|§)\s*[\d\-\.]+(?:\([a-z0-9\-]+\))*',
    'subdivisions': r'\((?:[a-z]{1,3}|\d{1,3})\)',
    'federal_cases': r'\d{1,3}\s+[A-Z][a-zA-Z\s\.]+\s+\d{1,4}(?:\s+\([A-Za-z\.\s\d]+\))?',
    'court_decisions': r'(?:App\.?\s*Div\.?|Ct\.?\s*App\.?|S\.?\s*Ct\.?)',
}

# Enhanced Phrase Patterns
PHRASE_PATTERNS = [
    # Procedural concepts
    r'\b(?:burden of proof|standard of review|statute of limitations|res judicata|collateral estoppel)\b',
    r'\b(?:due process|equal protection|probable cause|reasonable suspicion)\b',
    r'\b(?:good faith|bad faith|arm\'s length|bona fide)\b',
    r'\b(?:summary judgment|directed verdict|judgment as a matter of law|dismissal)\b',
    r'\b(?:motion to dismiss|motion for summary judgment|motion in limine)\b',
    
    # Evidence and proof
    r'\b(?:preponderance of evidence|clear and convincing|beyond reasonable doubt)\b',
    r'\b(?:hearsay|best evidence rule|authentication|chain of custody)\b',
    r'\b(?:expert testimony|lay opinion|judicial notice)\b',
    
    # Duty and liability concepts
    r'\b(?:fiduciary duty|duty of care|duty of loyalty|breach of duty)\b',
    r'\b(?:proximate cause|but for causation|substantial factor|foreseeability)\b',
    r'\b(?:strict liability|negligence per se|res ipsa loquitur)\b',
    
    # Contract law
    r'\b(?:meeting of minds|offer and acceptance|consideration|mutual assent)\b',
    r'\b(?:material breach|anticipatory breach|substantial performance)\b',
    r'\b(?:unconscionable|void|voidable|unenforceable)\b',
    
    # Family/matrimonial
    r'\b(?:best interests of child|equitable distribution|maintenance|child support)\b',
    r'\b(?:legal custody|physical custody|visitation|parenting time)\b',
    
    # Professional responsibility
    r'\b(?:attorney-client privilege|work product|conflict of interest)\b',
    r'\b(?:competent representation|zealous advocacy|candor to tribunal)\b'
]

# Comprehensive legal terms dictionary
DEFAULT_LEGAL_TERMS = {
    'courts_jurisdiction': [
        'appellate court', 'trial court', 'supreme court', 'family court',
        'surrogate court', 'criminal court', 'civil court', 'district court',
        'court of appeals', 'jurisdiction', 'venue', 'forum non conveniens',
        'personal jurisdiction', 'subject matter jurisdiction', 'in rem', 'quasi in rem'
    ],
    
    'administrative_law': [
        'rulemaking', 'adjudication', 'judicial review', 'administrative agency',
        'due process', 'public disclosure', 'freedom of information',
        'administrative procedure act', 'chevron deference', 'arbitrary and capricious'
    ],
    
    'business_entities': [
        'corporation', 'limited liability company', 'llc', 'partnership',
        'limited partnership', 'general partnership', 'professional service corporation',
        'registered limited liability partnership', 'articles of incorporation',
        'bylaws', 'board of directors', 'shareholders', 'members', 'managers',
        'piercing corporate veil', 'ultra vires', 'derivative suit'
    ],
    
    'civil_procedure': [
        'personal jurisdiction', 'service of process', 'statute of limitations',
        'pleadings', 'motion', 'discovery', 'deposition', 'interrogatories',
        'summary judgment', 'trial', 'appeal', 'venue', 'affidavit',
        'affirmation', 'provisional remedies', 'attachment', 'preliminary injunction',
        'temporary restraining order', 'mandamus', 'certiorari', 'prohibition'
    ],
    
    'contracts': [
        'consideration', 'statute of frauds', 'parol evidence rule',
        'unconscionability', 'mutual mistake', 'unilateral mistake',
        'third-party beneficiary', 'constructive trust', 'employment contract',
        'breach of contract', 'damages', 'specific performance', 'rescission',
        'reformation', 'quantum meruit', 'unjust enrichment'
    ],
    
    'criminal_law': [
        'felony', 'misdemeanor', 'violation', 'mens rea', 'actus reus',
        'intent', 'negligence', 'recklessness', 'strict liability',
        'affirmative defense', 'self-defense', 'duress', 'entrapment',
        'insanity defense', 'juvenile offender', 'youthful offender',
        'arraignment', 'indictment', 'information', 'plea bargain'
    ],
    
    'evidence': [
        'relevance', 'hearsay', 'privilege', 'attorney-client privilege',
        'physician-patient privilege', 'spousal privilege', 'work product',
        'judicial notice', 'authentication', 'best evidence rule',
        'expert witness', 'lay witness', 'impeachment', 'rehabilitation',
        'character evidence', 'habit evidence', 'prior bad acts'
    ],
    
    'family_law': [
        'marriage', 'divorce', 'separation', 'annulment', 'custody',
        'child support', 'spousal support', 'maintenance', 'alimony',
        'equitable distribution', 'marital property', 'separate property',
        'adoption', 'parentage', 'paternity', 'visitation', 'parenting time',
        'domestic violence', 'family offense', 'order of protection'
    ],
    
    'professional_responsibility': [
        'attorney-client relationship', 'confidentiality', 'conflict of interest',
        'retainer agreement', 'legal fees', 'client funds', 'trust account',
        'solicitation', 'advertising', 'pro bono', 'disciplinary proceedings',
        'competent representation', 'zealous advocacy', 'candor to tribunal',
        'client perjury', 'withdrawal from representation'
    ],
    
    'real_property': [
        'landlord', 'tenant', 'lease', 'mortgage', 'deed', 'title',
        'easement', 'covenant', 'zoning', 'eminent domain',
        'adverse possession', 'recording', 'chain of title', 'encumbrance',
        'fee simple', 'life estate', 'remainder', 'reversion', 'servitude'
    ],
    
    'torts': [
        'negligence', 'duty of care', 'breach of duty', 'causation',
        'proximate cause', 'damages', 'strict liability', 'product liability',
        'defamation', 'libel', 'slander', 'privacy', 'intentional tort',
        'assault', 'battery', 'false imprisonment', 'no-fault insurance',
        'emotional distress', 'invasion of privacy', 'nuisance'
    ],
    
    'estates_trusts': [
        'will', 'testament', 'intestate', 'probate', 'executor',
        'administrator', 'beneficiary', 'heir', 'devise', 'bequest',
        'trust', 'trustee', 'settlor', 'power of attorney',
        'health care proxy', 'living will', 'estate planning',
        'elective share', 'pretermitted heir', 'per stirpes', 'per capita'
    ]
}


class LegalIndexGenerator:
    def __init__(self, legal_terms: Dict[str, List[str]] = None):
        self.legal_terms = legal_terms or DEFAULT_LEGAL_TERMS
        self.index = defaultdict(lambda: defaultdict(set))
        self.page_content = {}
        self.cross_references = defaultdict(set)
        
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
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
            return self._extract_with_pypdf2(pdf_path)

    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[int, str]:
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

    def identify_legal_concepts(self, text: str, page_num: int):
        """Identify and index legal concepts with improved accuracy."""
        text_lower = text.lower()
        
        # Index predefined legal terms with word boundary matching
        for category, terms in self.legal_terms.items():
            for term in terms:
                # Use word boundaries to avoid partial matches
                pattern = rf'\b{re.escape(term.lower())}\b'
                if re.search(pattern, text_lower):
                    formatted_term = term.title()
                    self.index[formatted_term][category].add(page_num)
                    self.index[formatted_term]['all_references'].add(page_num)

        # Index legal patterns with better specificity
        for pattern_name, pattern in LEGAL_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group().strip()
                if len(matched_text) > 2:
                    self.index[matched_text][pattern_name].add(page_num)
                    self.index[matched_text]['all_references'].add(page_num)

        # Index meaningful capitalized terms (improved filtering)
        cap_terms = re.findall(r'\b[A-Z][A-Z\s]{2,30}\b', text)
        excluded_terms = {'PAGE', 'CHAPTER', 'TABLE OF CONTENTS', 'INDEX', 'APPENDIX', 'SECTION'}
        for term in cap_terms:
            clean_term = term.strip()
            if (len(clean_term.split()) <= 5 and 
                clean_term not in excluded_terms and
                not re.match(r'^[A-Z]+$', clean_term)):  # Skip all-caps abbreviations
                self.index[clean_term.title()]['proper_nouns'].add(page_num)
                self.index[clean_term.title()]['all_references'].add(page_num)

    def extract_key_phrases(self, text: str, page_num: int):
        """Extract important legal phrases."""
        for pattern in PHRASE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.group().title()
                self.index[phrase]['key_phrases'].add(page_num)
                self.index[phrase]['all_references'].add(page_num)

    def build_cross_references(self):
        """Build cross-references between related terms."""
        # Example: link different forms of the same concept
        synonyms = {
            'Corporation': ['Business Corporation', 'Corp'],
            'Limited Liability Company': ['LLC', 'Limited Liability Co'],
            'Summary Judgment': ['Summary Judgement'],
            'Statute Of Limitations': ['Limitations Period', 'Time Limitation']
        }
        
        for main_term, alternatives in synonyms.items():
            if main_term in self.index:
                for alt in alternatives:
                    if alt in self.index:
                        self.cross_references[main_term].add(alt)

    def process_document(self, pdf_path: str):
        """Main processing function with progress indication."""
        print(f"Processing document: {pdf_path}")
        
        self.page_content = self.extract_text_from_pdf(pdf_path)
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
                self.identify_legal_concepts(text, page_num)
                self.extract_key_phrases(text, page_num)
        
        self.build_cross_references()
        print(f"Identified {len(self.index)} unique legal concepts and terms")

    def generate_index(self, include_subcategories: bool = True) -> str:
        """Generate formatted index with optional subcategory detail."""
        output = "COMPREHENSIVE LEGAL INDEX\n"
        output += "=" * 50 + "\n\n"
        
        sorted_terms = sorted(self.index.keys())
        
        for term in sorted_terms:
            subcategories = self.index[term]
            all_pages = sorted(subcategories.get('all_references', set()))
            
            if not all_pages:
                continue
                
            output += f"{term}\n"
            
            if include_subcategories and len(subcategories) > 1:
                # Show specific subcategories
                for subcat, pages in sorted(subcategories.items()):
                    if subcat != 'all_references' and pages:
                        sub_pages = sorted(list(pages))
                        output += f"  {subcat.replace('_', ' ').title()}: {', '.join(map(str, sub_pages))}\n"
            
            # Always show all references
            output += f"  All references: {', '.join(map(str, all_pages))}\n"
            
            # Add cross-references if they exist
            if term in self.cross_references:
                cross_refs = sorted(self.cross_references[term])
                output += f"  See also: {', '.join(cross_refs)}\n"
            
            output += "\n"
        
        return output

    def save_output(self, path: str, json_format: bool = False, include_subcategories: bool = True):
        """Save index output in text or JSON format."""
        try:
            if json_format:
                # Convert sets to sorted lists for JSON serialization
                json_data = {}
                for term, subcats in self.index.items():
                    json_data[term] = {}
                    for subcat, pages in subcats.items():
                        json_data[term][subcat] = sorted(list(pages))
                
                # Add cross-references to JSON
                if self.cross_references:
                    json_data['_cross_references'] = {
                        k: sorted(list(v)) for k, v in self.cross_references.items()
                    }
                
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            else:
                index_text = self.generate_index(include_subcategories)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(index_text)
            
            print(f"Index saved to: {path}")
            
        except Exception as e:
            print(f"Error saving output: {e}")

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the indexed content."""
        stats = {
            'total_terms': len(self.index),
            'total_pages': len(self.page_content),
            'pages_with_content': sum(1 for text in self.page_content.values() if text.strip()),
        }
        
        # Count terms by category
        category_counts = defaultdict(int)
        for term_data in self.index.values():
            for category in term_data.keys():
                if category != 'all_references':
                    category_counts[category] += 1
        
        stats['terms_by_category'] = dict(category_counts)
        return stats


def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive legal index from PDF documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python legal_index.py document.pdf
  python legal_index.py document.pdf -o my_index.txt
  python legal_index.py document.pdf -j -o index.json
  python legal_index.py document.pdf --no-subcategories
        """
    )
    
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('-o', '--output', default='legal_index.txt',
                       help='Output file path (default: legal_index.txt)')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Save output as JSON format')
    parser.add_argument('--no-subcategories', action='store_true',
                       help='Exclude subcategory details in text output')
    parser.add_argument('--stats', action='store_true',
                       help='Print statistics about the indexing')
    
    args = parser.parse_args()
    
    try:
        # Create and run the generator
        generator = LegalIndexGenerator()
        generator.process_document(args.input_pdf)
        
        # Save output
        generator.save_output(
            args.output, 
            json_format=args.json, 
            include_subcategories=not args.no_subcategories
        )
        
        # Print statistics if requested
        if args.stats:
            stats = generator.get_statistics()
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
