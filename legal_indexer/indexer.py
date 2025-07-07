import re
from collections import defaultdict
from typing import Dict, List
from legal_indexer.config import STATUTORY_PATTERNS, CASE_LAW_PATTERNS, GENERAL_PATTERNS, PHRASE_PATTERNS

class LegalIndexer:
    def __init__(self, legal_terms: Dict[str, List[str]], page_offset: int = 0, terms_only: bool = False):
        self.legal_terms = legal_terms
        self.index = defaultdict(lambda: defaultdict(list))
        self.cross_references = defaultdict(set)
        self.page_offset = page_offset
        self.terms_only = terms_only
        self.current_headings = [None] * 5

    def set_current_headings(self, headings: List[str]):
        self.current_headings = headings

    def _add_to_index(self, term: str, category: str, page_num: int, match: re.Match, text: str):
        """Add a term to the index with context."""
        context_window = 100
        start = max(0, match.start() - context_window)
        end = min(len(text), match.end() + context_window)
        snippet = text[start:end].strip().replace('\n', ' ')
        
        entry = (page_num, snippet, self.current_headings.copy())
        
        # Avoid duplicate entries for the same page and context
        if entry not in self.index[term][category]:
            self.index[term][category].append(entry)
        if entry not in self.index[term]['all_references']:
            self.index[term]['all_references'].append(entry)

    def identify_legal_concepts(self, text: str, page_num: int):
        """Identify and index legal concepts with improved accuracy."""
        page_num -= self.page_offset

        if not self.terms_only:
            # Process statutory patterns
            for category, patterns in STATUTORY_PATTERns.items():
                for pattern in patterns:
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        term = match.group().strip()
                        if not term.isnumeric():
                            self._add_to_index(term, category, page_num, match, text)

            # Process case law patterns
            for category, patterns in CASE_LAW_PATTERNS.items():
                for pattern in patterns:
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        term = match.group().strip()
                        if not term.isnumeric():
                            self._add_to_index(term, category, page_num, match, text)

        # Process general patterns
        for category, pattern in GENERAL_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                term = match.group().strip()
                if not term.isnumeric():
                    self._add_to_index(term, category, page_num, match, text)

        # Index predefined legal terms
        text_lower = text.lower()
        for category, terms in self.legal_terms.items():
            for term in terms:
                pattern = rf'\b{re.escape(term.lower())}\b'
                for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                    formatted_term = term.title()
                    self._add_to_index(formatted_term, category, page_num, match, text)

    def extract_key_phrases(self, text: str, page_num: int):
        """Extract important legal phrases."""
        page_num -= self.page_offset
        for pattern in PHRASE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                phrase = match.group().title()
                if not phrase.isnumeric():
                    self._add_to_index(phrase, 'key_phrases', page_num, match, text)

    def build_cross_references(self):
        """Build cross-references between related terms."""
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

