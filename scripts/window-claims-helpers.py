"""Copy-ready helpers for the post-segmentation window -> claims decomposition stage.

Usage pattern (see references/window-claims-decomposition.md):
1. Copy this file into your workspace as agent_helpers.py; adjust BASE below.
2. Per window, write a thin driver w<N>.py defining `items` — one tuple per claim:
       (anchor, spo, claim_type[, boundary[, trim_to[, end_at[, extend_to]]]])
   anchor    unique ASCII-only substring inside the target sentence
   spo       (s, p, o) English terms for the record
   trim_to   drop leading junk before this substring (section headers, block quotes)
   end_at    cut the quote after this exact substring (curly-quote sentence endings)
   extend_to grow past the found sentence end through this substring (2-sentence claims)
3. Dry-run:  python w<N>.py          -> prints every built record for eyeballing
   Commit :  python wN.py commit     -> appends JSONL + writes done-flag after asserts

Guarantees: quotes are SLICED from cleaned window text (verbatim + curly typography
by construction), offset_hint is the cleaned-text index, and next_n() continues each
chunk's numbering from the max found across ALL part files (collision-free).
"""
import json
import os
import re

BASE = r"state"  # adjust: your workspace state dir (claims_parts/, s1_windows/, s1_done/)
PART_DIR = os.path.join(BASE, "claims_parts")
WIN_DIR = os.path.join(BASE, "s1_windows")


def clean(t):
    """Strip [PAGE n/m] markers and collapse whitespace (sibling convention).

    The marker regex matches the corpus family this was built for — adapt
    the pattern to your corpus's own page-marker format.
    """
    return re.sub(r"\s+", " ", re.sub(r"\[PAGE \d+/\d+\]", " ", t))


def load_window(wid):
    with open(os.path.join(WIN_DIR, wid + ".txt"), encoding="utf-8") as f:
        return clean(f.read())


def slice_sentence(norm, anchor):
    """Locate a unique ASCII anchor and expand to enclosing sentence bounds."""
    i = norm.find(anchor)
    assert i >= 0, "anchor not found: %r" % anchor
    assert norm.find(anchor, i + 1) == -1, "anchor not unique: %r" % anchor
    left = max(norm.rfind(". ", 0, i), norm.rfind("! ", 0, i), norm.rfind("? ", 0, i)) + 1
    ends = [e for e in (norm.find(x, i) for x in (". ", "! ", "? ")) if e != -1]
    right = min(ends) + 1 if ends else len(norm)
    return norm[left:right].strip(), left


def make_rec(chunk, n, quote, off, spo, ctype, condition="", boundary=""):
    return {
        "claim_id": "C-SRC-0001-%s-%03d" % (chunk, n),
        "unit_id": "SRC-0001",
        "chunk_id": chunk,
        "parent_src_id": "SRC-0001",
        "quote": quote,
        "offset_hint": off,
        "spo": {"s": spo[0], "p": spo[1], "o": spo[2]},
        "claim_type": ctype,
        "origin": "source_asserted",
        "condition": condition,
        "boundary": boundary,
        "granularity": "fine",
        "inference_basis": "",
    }


def next_n(chunk):
    """Max NNN used for this chunk across ALL part files of this source, +1."""
    src = "SRC-0001"  # adjust if decomposing another source
    pat = re.compile(r'"claim_id": "%s-%s-(\d{3})"' % (src, chunk))
    mx = 0
    for fn in os.listdir(PART_DIR):
        if fn.startswith(src + ".") and fn.endswith(".jsonl"):
            with open(os.path.join(PART_DIR, fn), encoding="utf-8") as f:
                for ln in f:
                    m = pat.search(ln)
                    if m:
                        mx = max(mx, int(m.group(1)))
    return mx + 1


def append_records(recs, flag_wid=None):
    """Append JSONL lines (never overwrite); optionally write the done-flag.
    Flag content {"units_done": <claim count>, ...} — units_done = THIS window's
    claim count (0 for an empty window)."""
    os.makedirs(PART_DIR, exist_ok=True)
    part = os.path.join(PART_DIR, "SRC-0001.W1.jsonl")  # adjust part-file name
    with open(part, "a", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if flag_wid:
        with open(os.path.join(BASE, "s1_done", flag_wid + ".flag"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"units_done": len(recs), "chunks": 1, "notes": "window"}))
    return len(recs)


def spec(wid, chunk, items):
    """Build records for one window from item tuples (see module docstring)."""
    norm = load_window(wid)
    n = next_n(chunk)
    recs = []
    for it in items:
        anchor, spo, ctype = it[0], it[1], it[2]
        boundary = it[3] if len(it) > 3 else ""
        q, off = slice_sentence(norm, anchor)
        if len(it) > 4 and it[4]:                      # trim_to: drop leading junk
            k = q.find(it[4])
            assert k > 0, "trim_to not inside quote: %r" % it[4]
            off += k
            q = q[k:]
        if len(it) > 5 and it[5]:                      # end_at: hard right cut
            k = q.find(it[5])
            assert k >= 0, "end_at not inside quote: %r" % it[5]
            q = q[:k + len(it[5])]
        if len(it) > 6 and it[6]:                      # extend_to: span 2 sentences
            k = norm.find(it[6], off)
            assert k >= 0, "extend_to not found after offset: %r" % it[6]
            q = norm[off:k + len(it[6])].strip()
        recs.append(make_rec(chunk, n, q, off, spo, ctype, boundary=boundary))
        n += 1
    return recs
