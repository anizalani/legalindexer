
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
