# -*- coding: utf-8 -*-
"""EPUB → plain text (zero deps: zipfile + re + html, stdlib only).

Usage:
    python epub-to-text.py <input.epub> <output.txt>

Notes:
    - EPUB is a zip of XHTML/HTML files; this strips tags and concatenates in
      file-name order, with a '--- FILE: <name> ---' separator per source file.
    - Extracted EPUB text has NO page markers -> line-only provenance.
    - Footnotes interleave in the body ([n] markers) — tag citations as
      body-vs-footnote when building claims.
"""
import html
import re
import sys
import zipfile
from pathlib import Path


def html_to_text(h: str) -> list:
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", "\n", h)
    h = html.unescape(h)
    return [l.strip() for l in h.split("\n") if l.strip()]


def main(epub_path: str, out_path: str) -> None:
    epub = Path(epub_path)
    out = Path(out_path)
    with zipfile.ZipFile(epub) as z:
        names = z.namelist()
        htmls = sorted(
            n for n in names
            if n.endswith((".html", ".xhtml", ".htm"))
            and "toc" not in n.lower()
            and "nav" not in n.lower()
        )
        print(f"HTML files: {len(htmls)}")
        total = 0
        with open(out, "w", encoding="utf-8") as f:
            for n in htmls:
                raw = z.read(n).decode("utf-8", errors="replace")
                lines = html_to_text(raw)
                f.write(f"\n--- FILE: {n} ---\n")
                f.write("\n".join(lines))
                f.write("\n")
                total += len(lines)
        print(f"Output: {out} ({total} lines)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
