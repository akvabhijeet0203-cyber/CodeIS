

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from utils.logger import get_logger
from utils.text_utils import is_clause_header, extract_clause_number, token_count_approx
from config import CHUNK_MAX_TOKENS, CHUNK_OVERLAP

log = get_logger(__name__)


@dataclass
class Chunk:
    chunk_id: str         
    text: str               
    source_file: str       
    part_name: str    
    clause_number: str      
    page_numbers: List[int] = field(default_factory=list)
    token_count: int = 0

    def to_metadata(self) -> dict:
        return {
            "chunk_id":      self.chunk_id,
            "source_file":   self.source_file,
            "part_name":     self.part_name,
            "clause_number": self.clause_number,
            "page_numbers":  str(self.page_numbers),
            "token_count":   self.token_count,
        }


class ClauseBoundaryChunker:
    """
    Splits a ParsedDocument into Chunk objects by:
    1. Scanning lines for clause header patterns.
    2. Grouping text under each clause header.
    3. If a clause section exceeds CHUNK_MAX_TOKENS, sub-chunking with overlap.
    """

    def __init__(
        self,
        max_tokens:   int = CHUNK_MAX_TOKENS,
        overlap:      int = CHUNK_OVERLAP,
    ):
        self.max_tokens = max_tokens
        self.overlap    = overlap

    #  Public API 

    def chunk_document(self, document) -> List[Chunk]:
        """Main entry point. Takes a ParsedDocument, returns list of Chunks."""
        log.info(f"Chunking: {document.part_name}")
        chunks: List[Chunk] = []

        # Build a flat list of (page_number, line) pairs
        page_lines: List[tuple[int, str]] = []
        for page in document.pages:
            for line in page.raw_text.split("\n"):
                page_lines.append((page.page_number, line))

        # Split into sections at clause boundaries
        sections = self._split_into_sections(page_lines)
        log.debug(f"  Found {len(sections)} clause sections")

        for section_idx, (clause_id, lines_with_pages) in enumerate(sections):
            text  = "\n".join(line for _, line in lines_with_pages).strip()
            pages = sorted(set(pn for pn, _ in lines_with_pages))

            if not text:
                continue

            tokens = token_count_approx(text)

            if tokens <= self.max_tokens:
                # Fits in one chunk
                chunk = self._make_chunk(
                    text=text,
                    clause_number=clause_id,
                    pages=pages,
                    document=document,
                    sub_idx=0,
                )
                chunks.append(chunk)
            else:
                # Sub-chunk with overlap
                sub_chunks = self._sub_chunk(text, clause_id, pages, document)
                chunks.extend(sub_chunks)

        log.success(f"  Generated {len(chunks)} chunks from {document.part_name}")
        return chunks

    #  Internal helpers 

    def _split_into_sections(
        self, page_lines: List[tuple[int, str]]
    ) -> List[tuple[str, List[tuple[int, str]]]]:
        """
        Group page_lines into (clause_label, [(page, line), ...]) tuples.
        Each new clause header starts a new section.
        """
        sections: List[tuple[str, List]] = []
        current_clause = "preamble"
        current_lines: List[tuple[int, str]] = []

        for page_num, line in page_lines:
            if is_clause_header(line):
                # Save previous section
                if current_lines:
                    sections.append((current_clause, current_lines))
                # Start new section
                clause_num = extract_clause_number(line) or line.strip()[:40]
                current_clause = clause_num
                current_lines  = [(page_num, line)]
            else:
                current_lines.append((page_num, line))

        # Don't forget last section
        if current_lines:
            sections.append((current_clause, current_lines))

        return sections

    def _sub_chunk(
        self,
        text: str,
        clause_number: str,
        pages: List[int],
        document,
    ) -> List[Chunk]:
        """
        Split oversized clause text into overlapping word-level chunks.
        """
        words = text.split()
        step  = self.max_tokens - self.overlap
        if step <= 0:
            step = self.max_tokens

        chunks = []
        start  = 0
        sub_idx = 0

        while start < len(words):
            end     = min(start + self.max_tokens, len(words))
            snippet = " ".join(words[start:end])
            chunk   = self._make_chunk(
                text=snippet,
                clause_number=clause_number,
                pages=pages,
                document=document,
                sub_idx=sub_idx,
            )
            chunks.append(chunk)
            if end == len(words):
                break
            start  += step
            sub_idx += 1

        return chunks

    def _make_chunk(
        self,
        text: str,
        clause_number: str,
        pages: List[int],
        document,
        sub_idx: int,
    ) -> Chunk:
        import hashlib
        part_tag    = document.part_name.replace(" ", "_").replace("-", "").lower()
        clause_tag  = re.sub(r"[^a-z0-9]", "", clause_number.lower())
        unique_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        chunk_id    = f"{part_tag}_cl{clause_tag}_{sub_idx:03d}_{unique_hash}"

        return Chunk(
            chunk_id      = chunk_id,
            text          = text,
            source_file   = document.file_path,
            part_name     = document.part_name,
            clause_number = clause_number,
            page_numbers  = pages,
            token_count   = token_count_approx(text),
        )


#  Convenience function 

def chunk_all_documents(documents: list) -> List[Chunk]:
    chunker = ClauseBoundaryChunker()
    all_chunks: List[Chunk] = []
    for doc in documents:
        all_chunks.extend(chunker.chunk_document(doc))
    log.info(f"Total chunks across all documents: {len(all_chunks)}")
    return all_chunks
