# -*- coding: utf-8 -*-
"""Page-anchor chapter-map builder (corpus-knowledge-engineering).

Deterministic structure recovery: Contents printed pages + verified OCR offset
-> [PAGE N/M] markers -> chapter spans. Never locate titles by full-text grep
alone (page headers / subsection titles / body citations match first).

Usage:
    python page-anchor-chapter-map.py <source.txt> "<title>|<printed_page>|..." [--marker "PAGE"]
Example:
    python page-anchor-chapter-map.py source.txt \
      "Chapter One Title|1" \
      "Chapter Two Title|23" \
      --marker "PAGE"

Notes:
- Offset = OCR page - printed page, verified per book (measured +10/+12 in one
  corpus; any value possible). Front-matter (roman pages) floats — never use as anchor.
- The default --marker pattern matches the corpus family this was built for
  ([PAGE N/M] lines); pass --marker for any other page-signal convention.
- Source file must be LF-normalized (line numbers = grep/sed view).
- Title substring search starts after front matter (tune --body-start per book).
"""
import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="LF-normalized per-book txt")
    ap.add_argument("chapters", nargs="+",
                    help="'title|printed_page' entries (printed page from the book's own Contents)")
    ap.add_argument("--marker", default=r"\[PAGE (\d+)/\d+\]",
                    help="regex for page markers with one capture group (OCR page number)")
    ap.add_argument("--body-start", type=int, default=390,
                    help="first line where the body can begin (after front matter)")
    args = ap.parse_args()

    lines = Path(args.source).read_text(encoding="utf-8").split("\n")
    marker_re = re.compile(args.marker)
    page_marks = [(i + 1, int(m.group(1))) for i, l in enumerate(lines)
                  if (m := marker_re.search(l))]
    if not page_marks:
        print(f"No page markers matched '{args.marker}'", file=sys.stderr)
        return 1

    entries = []
    for spec in args.chapters:
        title, _, page = spec.rpartition("|")
        entries.append((title, int(page)))

    # Verify offset with the first entry, then anchor all chapters.
    first_title, first_page = entries[0]
    first_hit = next(i + 1 for i, l in enumerate(lines)
                     if i + 1 >= args.body_start and first_title.lower() in l.lower())
    anchor = max((pl for pl, pn in page_marks if pl <= first_hit), default=None)
    if anchor is None:
        print("First chapter not anchored", file=sys.stderr)
        return 1
    offset = dict(page_marks)[anchor] - first_page
    print(f"# verified OCR offset: {offset:+d} (OCR = printed {offset:+d})")

    starts = []
    for title, printed in entries:
        target = printed + offset
        pl = next((pl for pl, pn in page_marks if pn == target), None)
        if pl is None:
            print(f"# !! {title}: no marker for printed p{printed} (OCR p{target})", file=sys.stderr)
            continue
        page_text = "\n".join(lines[pl:pl + 8]).lower()
        hit = title.lower() in page_text
        print(f"# {'OK ' if hit else '?? '} {title} (printed p{printed}) -> L{pl} {'title-in-page' if hit else 'TITLE NOT FOUND IN PAGE - inspect'}")
        starts.append((title, printed, pl))

    for i, (title, printed, pl) in enumerate(starts):
        end = starts[i + 1][2] - 1 if i + 1 < len(starts) else len(lines)
        print(f"- {{ id: ch{i+1:02d}, title: \"{title}\", start_page: {printed}, "
              f"start_line: {pl}, end_line: {end} }}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
