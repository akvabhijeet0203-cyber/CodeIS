
from __future__ import annotations

import fitz                 
import pdfplumber
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

from utils.logger import get_logger
from utils.text_utils import normalise_text, clean_clause_text

log = get_logger(__name__)


@dataclass
class ParsedPage:
    page_number: int
    raw_text: str
    tables: List[List[List[str]]] = field(default_factory=list) 
    has_images: bool = False
    source_file: str = ""


@dataclass
class ParsedDocument:
    file_path: str
    part_name: str         
    pages: List[ParsedPage] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.raw_text for p in self.pages if p.raw_text.strip())


class PDFParser:
    """
    Two-pass PDF parser:
    Pass 1 — PyMuPDF  : fast text extraction with layout ordering
    Pass 2 — pdfplumber: table extraction for pages identified as table-heavy
    """

    TABLE_DENSITY_THRESHOLD = 0.3   

    def __init__(self, file_path: str | Path, part_name: str):
        self.file_path  = Path(file_path)
        self.part_name  = part_name
        self._doc_fitz  = None
        self._doc_plumb = None

    # Public API 

    def parse(self) -> ParsedDocument:
        log.info(f"Parsing: {self.file_path.name}")
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.file_path}")

        result = ParsedDocument(
            file_path=str(self.file_path),
            part_name=self.part_name,
        )

        self._doc_fitz  = fitz.open(str(self.file_path))
        self._doc_plumb = pdfplumber.open(str(self.file_path))

        total = len(self._doc_fitz)
        log.info(f"  Total pages: {total}")

        for page_idx in range(total):
            parsed = self._parse_page(page_idx)
            result.pages.append(parsed)

        self._doc_fitz.close()
        self._doc_plumb.close()

        log.success(f"  Parsed {len(result.pages)} pages from {self.file_path.name}")
        return result

    # Internal helper

    def _parse_page(self, idx: int) -> ParsedPage:
        fitz_page  = self._doc_fitz[idx]
        plumb_page = self._doc_plumb.pages[idx]

        # Text extraction 
        raw = fitz_page.get_text("text", sort=True)   
        raw = clean_clause_text(raw)

        # Detect images 
        has_images = len(fitz_page.get_images()) > 0

        # Table extraction
        tables = []
        try:
            plumb_tables = plumb_page.extract_tables()
            if plumb_tables:
                for tbl in plumb_tables:
                    # Clean None cells
                    cleaned = [
                        [cell if cell is not None else "" for cell in row]
                        for row in tbl
                    ]
                    tables.append(cleaned)
                    # Append table as text block for embedding
                    table_text = self._table_to_text(cleaned)
                    raw = raw + "\n\n" + table_text
        except Exception as e:
            log.warning(f"    Table extraction failed on page {idx+1}: {e}")

        return ParsedPage(
            page_number  = idx + 1,
            raw_text     = normalise_text(raw),
            tables       = tables,
            has_images   = has_images,
            source_file  = self.file_path.name,
        )

    @staticmethod
    def _table_to_text(table: List[List[str]]) -> str:
        """
        Convert a table (list of rows) to a readable text block.
        First row is treated as header.
        """
        if not table:
            return ""
        lines = []
        header = table[0]
        for row in table[1:]:
            pairs = []
            for col_idx, cell in enumerate(row):
                col_name = header[col_idx] if col_idx < len(header) else f"Col{col_idx}"
                if cell.strip():
                    pairs.append(f"{col_name}: {cell.strip()}")
            if pairs:
                lines.append(" | ".join(pairs))
        return "\n".join(lines)


# Convenience function

def parse_all_parts(is875_files: dict) -> List[ParsedDocument]:
    """Parse all three IS 875 parts and return list of ParsedDocuments."""
    part_names = {
        "part1": "IS 875 Part 1 - Dead Loads",
        "part2": "IS 875 Part 2 - Imposed Loads",
        "part3": "IS 875 Part 3 - Wind Loads",
    }
    documents = []
    for key, path in is875_files.items():
        name = part_names.get(key, key)
        parser = PDFParser(path, name)
        try:
            doc = parser.parse()
            documents.append(doc)
        except FileNotFoundError as e:
            log.error(str(e))
    return documents
