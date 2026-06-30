
# utils/text_utils.py — Text cleaning and normalisation helpers

import re
import unicodedata


def normalise_text(text: str) -> str:
    """
    Normalise unicode, collapse whitespace, fix common PDF artefacts.
    """
    # Unicode normalisation
    text = unicodedata.normalize("NFC", text)

    # Fix soft hyphens and ligatures common in PDFs
    text = text.replace("\u00ad", "")      
    text = text.replace("\ufb01", "fi")    
    text = text.replace("\ufb02", "fl")    
    text = text.replace("\u2013", "-")   
    text = text.replace("\u2014", "-")     

    # Remove null bytes
    text = text.replace("\x00", "")

    # Collapse multiple whitespace/newlines but keep paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_clause_text(text: str) -> str:
    """
    Extra cleaning specific to IS code clauses:
    - Remove page headers/footers (e.g. 'IS 875 (Part 3) : 2015')
    - Remove isolated page numbers
    """
    ## Remove IS code header lines like "IS 875 (Part 3) : 2015"
    text = re.sub(r"IS\s*875\s*\(Part\s*\d\)\s*:\s*\d{4}", "", text)

    # Remove standalone page numbers
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Remove lines that are just dashes/underscores (table borders)
    text = re.sub(r"^[-_=]{3,}\s*$", "", text, flags=re.MULTILINE)

    return normalise_text(text)


def is_clause_header(line: str) -> bool:
    """
    Detect lines that start a new IS code clause.
    Examples:
        '6.3 Design Wind Speed'
        'Table 1 — Basic Wind Speed'
        'Annex A (Normative)'
        'Appendix B'
    """
    clause_pattern = re.compile(
        r"""
        ^(
            \d+(\.\d+)*\s+[A-Z]         |  
            Table\s+\d+                  |  
            Fig\.\s*\d+                  |  
            Annex\s+[A-Z]               |  
            Appendix\s+[A-Z]            |  
            FOREWORD                     |
            CONTENTS                     |
            SCOPE
        )
        """,
        re.VERBOSE | re.IGNORECASE,
    )
    return bool(clause_pattern.match(line.strip()))


def extract_clause_number(line: str) -> str | None:
    """
    Extract a clause number from a header line.
    '6.3.1 Wind Directionality Factor' → '6.3.1'
    """
    m = re.match(r"^(\d+(?:\.\d+)*)", line.strip())
    return m.group(1) if m else None


def token_count_approx(text: str) -> int:
    """
    Rough token count: split on whitespace. Good enough for chunking limits.
    (1 token ≈ 0.75 words for English technical text)
    """
    words = len(text.split())
    return int(words / 0.75)
