"""
parser.py — Document Text Extractor
Handles PDF and DOCX files, returning clean extracted text.
"""

import fitz  # PyMuPDF
from docx import Document
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF.
    Joins text from every page with a page separator.
    """
    text_pages = []

    with fitz.open(file_path) as doc:
        total_pages = len(doc)
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")  # plain text mode
            if page_text.strip():              # skip blank pages
                text_pages.append(
                    f"--- PAGE {page_num} of {total_pages} ---\n{page_text.strip()}"
                )

    if not text_pages:
        raise ValueError("No extractable text found in PDF. It may be a scanned image-based PDF.")

    return "\n\n".join(text_pages)


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract all text from a DOCX file using python-docx.
    Reads every paragraph in the document.
    """
    doc = Document(file_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]

    if not paragraphs:
        raise ValueError("No text found in DOCX file.")

    return "\n\n".join(paragraphs)


def extract_text(file_path: str) -> dict:
    """
    Main entry point. Detects file type and routes to the correct parser.

    Returns a dict with:
        - text        : extracted raw text
        - file_name   : original filename
        - file_type   : 'pdf' or 'docx'
        - char_count  : total characters extracted
        - word_count  : approximate word count
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = os.path.basename(file_path)
    extension = os.path.splitext(file_name)[1].lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)
        file_type = "pdf"
    elif extension in (".docx", ".doc"):
        text = extract_text_from_docx(file_path)
        file_type = "docx"
    else:
        raise ValueError(
            f"Unsupported file type: '{extension}'. Only PDF and DOCX are supported."
        )

    word_count = len(text.split())
    char_count = len(text)

    return {
        "text": text,
        "file_name": file_name,
        "file_type": file_type,
        "char_count": char_count,
        "word_count": word_count,
    }


# ── Quick standalone test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_file.pdf|.docx>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"\n[PARSING]: {path}\n{'-' * 55}")

    result = extract_text(path)

    print(f"[OK] File Name : {result['file_name']}")
    print(f"[OK] File Type : {result['file_type'].upper()}")
    print(f"[OK] Characters: {result['char_count']:,}")
    print(f"[OK] Words     : {result['word_count']:,}")
    print(f"\n{'-' * 55}")
    print("FIRST 1000 CHARACTERS OF EXTRACTED TEXT:\n")
    print(result["text"][:1000])
    print(f"\n{'-' * 55}")
    print("[OK] Parser test complete!")
