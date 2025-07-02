
import json
from collections import defaultdict
from typing import Dict
import csv
import fitz  # PyMuPDF
from docx import Document
from lxml import etree

class Exporter:
    def __init__(self, index: Dict, cross_references: Dict):
        self.index = index
        self.cross_references = cross_references
        self.case_law_references = {k: v for k, v in index.items() if 'case_law_references' in v}
        self.statutory_references = {k: v for k, v in index.items() if 'statutory_references' in v}
        self.subject_matter_index = {k: v for k, v in index.items() if 'case_law_references' not in v and 'statutory_references' not in v}

    def _format_entry(self, term, pages):
        return f"{term}: {', '.join(map(str, sorted(list(pages))))}"

    def to_text(self, include_subcategories: bool = True) -> str:
        """Generate formatted index with the new structure."""
        output = "COMPREHENSIVE LEGAL INDEX\n"
        output += "=" * 50 + "\n\n"

        # Case Law References
        output += "CASE LAW REFERENCES\n"
        output += "-" * 50 + "\n"
        for term, data in sorted(self.case_law_references.items()):
            output += self._format_entry(term, data['all_references']) + "\n"
        output += "\n"

        # Statutory References
        output += "STATUTORY REFERENCES\n"
        output += "-" * 50 + "\n"
        for term, data in sorted(self.statutory_references.items()):
            output += self._format_entry(term, data['all_references']) + "\n"
        output += "\n"

        # Index by Subject
        output += "INDEX BY SUBJECT\n"
        output += "-" * 50 + "\n"
        # Group terms by category
        subject_index = defaultdict(list)
        for term, data in sorted(self.subject_matter_index.items()):
            for category in data:
                if category != 'all_references':
                    subject_index[category].append((term, data['all_references']))
        
        for category, terms in sorted(subject_index.items()):
            output += f"\n-- {category.replace('_', ' ').title()} --\n"
            for term, pages in sorted(terms):
                output += self._format_entry(term, pages) + "\n"
        output += "\n"

        # Alphabetical Index
        output += "ALPHABETICAL INDEX\n"
        output += "-" * 50 + "\n"
        for term, data in sorted(self.index.items()):
            output += self._format_entry(term, data['all_references']) + "\n"
        
        return output

    def to_json(self) -> str:
        """Convert index to JSON format with the new structure."""
        json_data = {
            'case_law_references': {k: sorted(list(v['all_references'])) for k, v in self.case_law_references.items()},
            'statutory_references': {k: sorted(list(v['all_references'])) for k, v in self.statutory_references.items()},
            'subject_matter_index': {k: {cat: sorted(list(pages)) for cat, pages in v.items()} for k, v in self.subject_matter_index.items()},
            '_cross_references': {k: sorted(list(v)) for k, v in self.cross_references.items()}
        }
        return json.dumps(json_data, indent=2, ensure_ascii=False)

    def to_pdf(self, path: str):
        """Generate a PDF version of the index."""
        doc = fitz.open()
        page = doc.new_page(width=595, height=842) # A4 size
        
        text = self.to_text()
        
        # Use a textbox for better layout control
        rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontname="helv", fontsize=10)
        
        doc.save(path)
        doc.close()

    def to_docx(self, path: str):
        """Generate a .docx version of the index."""
        doc = Document()
        doc.add_heading('Comprehensive Legal Index', 0)
        
        # Case Law References
        doc.add_heading('Case Law References', level=1)
        for term, data in sorted(self.case_law_references.items()):
            doc.add_paragraph(self._format_entry(term, data['all_references']))

        # Statutory References
        doc.add_heading('Statutory References', level=1)
        for term, data in sorted(self.statutory_references.items()):
            doc.add_paragraph(self._format_entry(term, data['all_references']))

        # Index by Subject
        doc.add_heading('Index by Subject', level=1)
        subject_index = defaultdict(list)
        for term, data in sorted(self.subject_matter_index.items()):
            for category in data:
                if category != 'all_references':
                    subject_index[category].append((term, data['all_references']))
        
        for category, terms in sorted(subject_index.items()):
            doc.add_heading(category.replace('_', ' ').title(), level=2)
            for term, pages in sorted(terms):
                doc.add_paragraph(self._format_entry(term, pages))

        # Alphabetical Index
        doc.add_heading('Alphabetical Index', level=1)
        for term, data in sorted(self.index.items()):
            doc.add_paragraph(self._format_entry(term, data['all_references']))
        
        doc.save(path)

    def to_csv(self, path: str):
        """Generate a CSV version of the index."""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Term', 'Category', 'Pages'])
            
            for term, data in sorted(self.index.items()):
                for cat, pages in data.items():
                    if pages:
                        writer.writerow([term, cat, ', '.join(map(str, sorted(list(pages))))])

    def to_xml(self, path: str):
        """Generate an XML version of the index."""
        root = etree.Element('LegalIndex')
        
        # Case Law
        case_law_root = etree.SubElement(root, 'CaseLawReferences')
        for term, data in sorted(self.case_law_references.items()):
            etree.SubElement(case_law_root, 'Reference', name=term).text = ', '.join(map(str, sorted(list(data['all_references']))))

        # Statutory
        statutory_root = etree.SubElement(root, 'StatutoryReferences')
        for term, data in sorted(self.statutory_references.items()):
            etree.SubElement(statutory_root, 'Reference', name=term).text = ', '.join(map(str, sorted(list(data['all_references']))))

        # Subject Matter
        subject_root = etree.SubElement(root, 'SubjectMatterIndex')
        for term, data in sorted(self.subject_matter_index.items()):
            term_element = etree.SubElement(subject_root, 'Term', name=term)
            for cat, pages in data.items():
                cat_element = etree.SubElement(term_element, 'Category', name=cat)
                cat_element.text = ', '.join(map(str, sorted(list(pages))))

        with open(path, 'wb') as f:
            f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

    def to_markdown(self, path: str):
        """Generate a Markdown version of the index."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Comprehensive Legal Index\n\n")

            f.write("## Case Law References\n")
            for term, data in sorted(self.case_law_references.items()):
                f.write(f"- {self._format_entry(term, data['all_references'])}\n")
            f.write("\n")

            f.write("## Statutory References\n")
            for term, data in sorted(self.statutory_references.items()):
                f.write(f"- {self._format_entry(term, data['all_references'])}\n")
            f.write("\n")

            f.write("## Index by Subject\n")
            subject_index = defaultdict(list)
            for term, data in sorted(self.subject_matter_index.items()):
                for category in data:
                    if category != 'all_references':
                        subject_index[category].append((term, data['all_references']))
            
            for category, terms in sorted(subject_index.items()):
                f.write(f"### {category.replace('_', ' ').title()}\n")
                for term, pages in sorted(terms):
                    f.write(f"- {self._format_entry(term, pages)}\n")
                f.write("\n")

            f.write("## Alphabetical Index\n")
            for term, data in sorted(self.index.items()):
                f.write(f"- {self._format_entry(term, data['all_references'])}\n")

def save_output(path: str, index: Dict, cross_references: Dict, format: str, include_subcategories: bool = True):
    """Save index output in the specified format."""
    exporter = Exporter(index, cross_references)
    
    try:
        if format == 'text':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(exporter.to_text(include_subcategories))
        elif format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(exporter.to_json())
        elif format == 'pdf':
            exporter.to_pdf(path)
        elif format == 'docx':
            exporter.to_docx(path)
        elif format == 'csv':
            exporter.to_csv(path)
        elif format == 'xml':
            exporter.to_xml(path)
        elif format == 'md':
            exporter.to_markdown(path)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        print(f"Index saved to: {path}")
        
    except Exception as e:
        print(f"Error saving output: {e}")

def get_statistics(index: Dict, page_content: Dict) -> Dict:
    """Get statistics about the indexed content."""
    stats = {
        'total_terms': len(index),
        'total_pages': len(page_content),
        'pages_with_content': sum(1 for text in page_content.values() if text.strip()),
    }
    
    category_counts = defaultdict(int)
    for term_data in index.values():
        for category in term_data.keys():
            if category != 'all_references':
                category_counts[category] += 1
    
    stats['terms_by_category'] = dict(category_counts)
    return stats
