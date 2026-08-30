# SOP v3 Vector Machine — design and replay verification

The v2 automaton guards were LLM semantic judgments ("novelty ≤ 2?"). v3 replaces guards with **vector computation**: each material becomes a 13-component feature vector; a threshold decision tree computes the state transition. LLM is demoted from controller to sensor — it generates only 3 components.

## Feature vector (13 components)

Computable without LLM:

- `f_type` (txt/epub/pdf/merged — format pipeline dispatch)
- `f_words` (**CJK-adjusted**: `len(text.split()) + int(cjk_chars / 1.5)` — Chinese has no spaces, plain split() ≈ 1 "word" per paragraph and Chinese books misjudge as incomplete)
- `f_garbage` (special-chars/total — **only after textify**, never on binary)
- `f_page_ratio` (page markers vs expected)
- `f_chapter_hits` (regex on **body region only** — exclude first ~10% of file where ToC lives)
- `f_toc` (0/1, first 3000 chars)
- `f_biblio` (0/1, bibliography in last 3000 chars)
- `f_boundaries` (boundary-marker count for merged — corpus's own convention, e.g. 【】)
- `f_family_hit` (keyword match — **normalize filename first** (`_`/`-` → space) or `book_title.txt` never hits "book title"; **merged filenames: match the segment before the first `+`** (first book title), fallback: match first 2000 chars of extracted text)
- `f_festschrift` (journal/reader/essays-in-honor/in-memoriam markers — fast path)

LLM-generated (3): `f_novelty` (Merge Test 0–3), `f_score` (Decision Value Score 0–10), `f_runtime_gain` (0/1 strategic guard).

## Threshold decision tree (controller, final form)

```yaml
garbage > 0.3                        → REJECT (post-textify only)
chapter_hits == 0 AND toc == 1 AND biblio == 1 → REJECT (incomplete)
words < expected×0.2 AND toc == 1    → REJECT (incomplete)
words < expected×0.5 AND toc == 0 AND no family → REVIEW (LLM confirms: toolbook vs fragment)
festschrift == 1                     → ARCHIVE/EVIDENCE
family hit                           → MERGE candidate (LLM confirms novelty ≤ 2 + merge_target)
else                                 → REVIEW (unknown type — LLM)
```

## Replay = regression test

Historical judgments are the regression set. On every SOP change: replay all samples; vector ≠ history → **flag for human recheck, never auto-overwrite** (either side may be wrong; the human decides). Run the replay after every rule change — the distribution shift IS the quantitative regression report.

### The binary-read-as-text catch (why replay pays)

Historical verdict: "REJECT — garbage 64.8%". Vector machine predicted MERGE (family hit). Recheck found: the epub BINARY had been read as txt; unpacked text = 164K words at 0.68% garbage — a perfectly normal book. Corrected verdict: merge. Rules extracted:

- **Textify before featurize**: epub/pdf must be unpacked (zipfile / PyMuPDF) before any garbage/structural metrics.
- Any historical REJECT on an epub/pdf-derived verdict deserves a recheck pass when the vector machine replays.

## PDF extraction (the 53-error saga)

1. `python -c "multi-line script"` **cannot contain for-loops** — `for i in ...: a; b` is a SyntaxError (semicolons can't follow a colon in `-c` strings). Symptom: rc=1, `SyntaxError: invalid` pointing at the for-line. Always write a standalone script file for anything with loops.
2. Whole-doc PyMuPDF extraction of 100+ page PDFs times out / dies silently → small-word REJECTs (false "incomplete").
3. Fix (proven): standalone `scripts/pdf-extract-chunked.py` (chunked 20-page extraction + one retry + timeout), invoked as `subprocess.run([sys.executable, script_path, str(pdf)])`. → extraction errors eliminated.

## Implementation notes

- A featurize module (featurize + classify in one file; classify takes expected_words param, default 200K) plus a replay driver = batch runner writing JSONL + distribution stats.
- epub branch: zipfile → strip HTML tags → unescape → concat (stdlib only, mirrors `scripts/epub-to-text.py`).
- pdf branch: subprocess to the standalone chunked extractor (PyMuPDF often lives on a different python than the venv).
- Text extraction failure → garbage = 1.0 (treated as dirty; conservative).

## Cost model

Vector pre-classification + 3 LLM components ≈ <1 min/book (vs 2.5–3 min manual). The LLM's per-item work shrinks to confirming 3 numbers + edge cases; batch mode becomes "review the pre-classified queue".
