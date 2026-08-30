# -*- coding: utf-8 -*-
"""Multi-pattern chapter-title scanner for OCR/merged corpora.

Reads a text file and reports title-like lines across several common formats,
so you can see which pattern each book actually uses before writing its
chapter map. Line numbers = file's own \n count (grep/sed view).

Usage:
  python structure-scan.py <file> [start_line] [end_line]
  # start_line/end_line optional: scan only a book's line span inside a merged file.

Notes:
  - OCR corpora: titles may be cross-line, split ("FOUR TEEN"), or absent
    (titles only in ToC). A book with 0 hits usually has a nonstandard format —
    probe its ToC region instead of widening patterns blindly.
  - Foot/citation lines in academic books (e.g. "2 Among mainstream economists...")
    will false-positive; verify hits against the author's ToC.
"""
import re
import sys
from pathlib import Path

TITLE_PATS = [
    ("CH N: TITLE",  re.compile(r"^\s*CHAPTER\s+(\d+|[IVXLC]+)\s*[:.]\s*([A-Z].{3,60})$")),
    ("CH N TITLE",   re.compile(r"^\s*CHAPTER\s+(\d+|[IVXLC]+)\s+([A-Z].{3,60})$")),
    ("CH N -",       re.compile(r"^\s*Chapter\s+(\d+)\s*-\s*(.{3,60})$")),
    ("CH N",         re.compile(r"^\s*Chapter\s+(\d+)\s*$")),
    ("CH ONE",       re.compile(r"^\s*CHAPTER\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\s*[:.]?\s*(.*)$")),
    ("Part",         re.compile(r"^\s*PART\s+([IVXLC\d]+)\s*[:.]?\s*(.*)$")),
    ("N. TITLE",     re.compile(r"^\s*(\d{1,2})\.\s+([A-Z][A-Z0-9 ,'\-—]{5,60})$")),
    ("NUM TITLE",    re.compile(r"^\s*(\d{1,2})\s+([A-Z][A-Za-z ,'’\-—]{8,60})$")),
]


def scan(lines, start, end):
    hits = []
    for ln in range(start, end + 1):
        text = lines[ln - 1].strip()
        if not text or len(text) > 80:
            continue
        for pname, pat in TITLE_PATS:
            m = pat.match(text)
            if m:
                g2 = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
                hits.append((ln, pname, m.group(1), g2.strip()[:55]))
                break
    return hits


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = Path(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end = int(sys.argv[3]) if len(sys.argv) > 3 else None
    # binary read: keep the file's own \n count (do NOT use read_text's
    # universal-newlines translation, which doubles line numbers on \r\r\n files)
    text = path.read_bytes().decode("utf-8", errors="replace")
    lines = text.split("\n")
    if end is None:
        end = len(lines)
    hits = scan(lines, start, end)
    print(f"{path.name}: {len(hits)} title hits in L{start}-L{end} (of {len(lines)} lines)")
    for ln, pname, num, title in hits:
        print(f"  L{ln:>6} [{pname:<11}] {num:<4} {title}")


if __name__ == "__main__":
    sys.exit(main())
