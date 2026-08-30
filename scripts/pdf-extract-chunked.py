#!/usr/bin/env python3
# pdf-extract-chunked.py — standalone chunked PDF text extraction
# Why standalone: `python -c "..."` single-line scripts CANNOT hold for-loops
# (a semicolon after a colon is a SyntaxError), and naive whole-doc extraction
# times out / dies on 100+ page PDFs.
# Usage: python pdf-extract-chunked.py <pdf_path>   (PyMuPDF required)
import sys
import fitz

CHUNK_PAGES = 20  # chunked extraction keeps each batch small/fast


def extract(path: str) -> str:
    doc = fitz.open(path)
    out = []
    for i in range(0, doc.page_count, CHUNK_PAGES):
        chunk = "".join(doc[j].get_text() for j in range(i, min(i + 20, doc.page_count)))
        out.append(chunk)
    doc.close()
    return "".join(out)


if __name__ == "__main__":
    try:
        print(extract(sys.argv[1]))
    except Exception as e:
        print(f"PDF_EXTRACT_ERROR: {e}", file=sys.stderr)
        sys.exit(1)
