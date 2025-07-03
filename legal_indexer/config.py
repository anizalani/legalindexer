
# Enhanced Legal Patterns
STATUTORY_PATTERNS = {
    'statutory_references': [
        r'(?:N\.Y\.|New York)\s*[A-Za-z\s]*\s*(?:Law|Code)\s*(?:\u00a7|Section|§)\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
        r'CPLR\s*(?:\u00a7|§)?\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
        r'CPL\s*(?:\u00a7|§)?\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
        r'Rule\s*[\d\-\.]+(?:\([a-z0-9\-]+\))?',
        r'(?:\u00a7|§)\s*[\d\-\.]+(?:\([a-z0-9\-]+\))*',
    ]
}

CASE_LAW_PATTERNS = {
    'case_law_references': [
        r'[A-Z][a-zA-Z\s&\.\-]{2,30}\s+v\.?\s+[A-Z][a-zA-Z\s&\.\-]{2,30}',
        r'\d{1,3}\s+[A-Z][a-zA-Z\s\.]+\s+\d{1,4}(?:\s+\([A-Za-z\.\s\d]+\))?',
        r'(?:App\.?\s*Div\.?|Ct\.?\s*App\.?|S\.?\s*Ct\.?)',
    ]
}

# General patterns (less specific)
GENERAL_PATTERNS = {
    'subdivisions': r'\((?:[a-z]{1,3}|\d{1,3})\)',
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


