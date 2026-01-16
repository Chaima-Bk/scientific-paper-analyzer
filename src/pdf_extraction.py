from __future__ import annotations

from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract text from a text-based PDF using PyMuPDF.

    Returns:
        A single string containing the concatenated text of all pages.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_parts: list[str] = []

    with fitz.open(pdf_path) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            page_text = page.get_text("text")  # plain text extraction
            if page_text:
                text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()
    return full_text
