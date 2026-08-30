# -*- coding: utf-8 -*-
"""PDF → text extraction (PyMuPDF). Install the dependency first:
    python -m pip install pymupdf
    python scripts/pdf-to-text.py <input.pdf> [output.txt]
Output: one line per text block (blank-line separated), no page markers added.
Caveats: scanned/image-only PDFs yield empty text -> use OCR pipeline instead;
footnotes/headers may interleave (tag or filter per book).
"""
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("usage: pdf-to-text.py <input.pdf> [output.txt]")
        return 1
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".txt")
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF missing:  python -m pip install pymupdf")
        return 2
    doc = fitz.open(str(src))
    blocks = []
    for page in doc:
        t = page.get_text()
        if t.strip():
            blocks.append(t)
    out.write_text("\n\n".join(blocks), encoding="utf-8")
    print(f"{doc.page_count} pages -> {out} ({len(''.join(blocks))} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
