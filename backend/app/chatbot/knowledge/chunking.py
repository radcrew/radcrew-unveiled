"""Split knowledge documents into embeddable chunks.

``all-MiniLM-L6-v2`` truncates input past 256 word pieces and says nothing about
it, so embedding a document whole makes everything after roughly the first
thousand characters invisible to semantic retrieval. The static site copy is
well inside that limit (the largest is ~198 tokens), but GitHub Markdown is not.

Chunks stay under a character budget standing in for that token limit, split on
Markdown headings first and paragraphs second so a chunk is a coherent passage
rather than a fixed-width slice. Each chunk carries the document title into the
embedded text, because a paragraph scored on its own loses the subject it is
about.

A document that already fits yields exactly one chunk whose embedded text is
identical to what ``index_documents`` produced before, so short documents score
exactly as they did.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.chatbot.knowledge.models import KnowledgeDocument

# ~250 tokens at the usual 4 characters per token, against a 256 word-piece
# limit. Every static site document fits in one chunk at this size.
MAX_CHUNK_CHARS = 1000
# Carried from the end of the previous chunk so a passage split mid-thought is
# still retrievable from either side of the seam.
OVERLAP_CHARS = 150

_HEADING_RE = re.compile(r"^#{1,6} ", re.MULTILINE)
_PARAGRAPH_RE = re.compile(r"\n\s*\n")


@dataclass(frozen=True)
class Chunk:
    document_id: str
    chunk_index: int
    title: str
    body: str

    @property
    def embed_text(self) -> str:
        """What actually gets embedded: the title gives an isolated chunk its subject."""
        return f"{self.title}\n{self.body}"


def chunk_document(document: KnowledgeDocument) -> list[Chunk]:
    """Split one document into chunks, in reading order.

    Blank documents yield nothing rather than an empty chunk: an embedding of
    "" is a meaningless vector that still matches queries.
    """
    text = document.text.strip()
    if not text:
        return []

    budget = max(MAX_CHUNK_CHARS - len(document.title) - 1, OVERLAP_CHARS * 2)
    if len(text) <= budget:
        bodies = [document.text]
    else:
        bodies = _pack(_pieces(text, budget), budget)

    return [
        Chunk(document_id=document.id, chunk_index=index, title=document.title, body=body)
        for index, body in enumerate(bodies)
    ]


def chunk_documents(documents: list[KnowledgeDocument]) -> list[Chunk]:
    return [chunk for document in documents for chunk in chunk_document(document)]


def _split_sections(text: str) -> list[str]:
    """Split before each Markdown heading, keeping the heading with its body."""
    starts = [match.start() for match in _HEADING_RE.finditer(text)]
    if not starts:
        return [text]

    # Text before the first heading is its own section.
    bounds = ([0] if starts[0] > 0 else []) + starts
    sections = [text[start:end].strip() for start, end in zip(bounds, bounds[1:] + [len(text)])]
    return [section for section in sections if section]


def _pieces(text: str, budget: int) -> list[str]:
    """The smallest units worth keeping whole, largest first.

    A section that fits stays intact so a heading keeps its body. Only a section
    over budget is broken down into paragraphs, and only a paragraph over budget
    is broken on words.
    """
    pieces: list[str] = []
    for section in _split_sections(text):
        if len(section) <= budget:
            pieces.append(section)
            continue
        for paragraph in _paragraphs(section):
            pieces.extend(_fit(paragraph, budget))
    return pieces


def _pack(pieces: list[str], budget: int) -> list[str]:
    """Greedily fill chunks with whole pieces, overlapping at each seam.

    Packing runs across sections, not within them. Per-section packing looks
    equivalent but fragments a document of many short sections into one tiny
    chunk each, which costs an embedding per heading and gives retrieval
    passages too small to carry meaning.
    """
    chunks: list[str] = []
    current = ""

    for piece in pieces:
        if not current:
            current = piece
        elif len(current) + 2 + len(piece) <= budget:
            current = f"{current}\n\n{piece}"
        else:
            chunks.append(current)
            current = _seam(current, piece, budget)

    if current:
        chunks.append(current)
    return chunks


def _paragraphs(section: str) -> list[str]:
    return [p.strip() for p in _PARAGRAPH_RE.split(section) if p.strip()]


def _fit(paragraph: str, budget: int) -> list[str]:
    """Break a paragraph that is itself over budget, on word boundaries."""
    if len(paragraph) <= budget:
        return [paragraph]

    pieces: list[str] = []
    current = ""
    for word in paragraph.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= budget:
            current = f"{current} {word}"
        else:
            pieces.append(current)
            current = word
    if current:
        pieces.append(current)
    return pieces


def _seam(previous: str, piece: str, budget: int) -> str:
    """Start a chunk with the tail of the previous one, trimmed to a word boundary."""
    tail = previous[-OVERLAP_CHARS:]
    tail = tail.partition(" ")[2] if " " in tail else ""
    if not tail or len(tail) + 2 + len(piece) > budget:
        return piece
    return f"{tail}\n\n{piece}"
