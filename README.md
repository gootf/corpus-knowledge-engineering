# Corpus → Knowledge Engineering

**English** | [简体中文](README.zh-CN.md)

![License](https://img.shields.io/github/license/gootf/corpus-knowledge-engineering)
![Release](https://img.shields.io/github/v/release/gootf/corpus-knowledge-engineering)
![Stars](https://img.shields.io/github/stars/gootf/corpus-knowledge-engineering)

**Turn a pile of books into a small set of auditable agent skills — and prove where every claim came from.**

Hand a raw corpus (hundreds of books, merged TXT files, EPUB/PDF, OCR scans) to an AI and ask for a knowledge base, and you usually get one of two things: a directory-shaped summary with no checkable relationship to the source text, or a beautifully confident synthesis built on hallucinated page numbers. Neither is usable as a knowledge asset.

This repository ships a pipeline that treats the corpus as material to be **engineered, not summarized**: deterministic normalization → per-book segmentation → chapter maps recovered from the author's own ToC → claims with full provenance coordinates → book skills routed into a knowledge system that knows what it does *not* contain.

## What goes wrong without it

| The failure | Without it | With it |
|---|---|---|
| **Provenance that cannot be verified** — claims cite "page 27" with no way to find it | Beautiful citations, fabricated basis | Coordinates: `source → chapter → section → printed page → OCR page → line range`; both page numbers kept (they differ per book) |
| **Every book feels like a new discovery** — 300 books → 300 "skills", each a summary nobody audits | A book-summary library that grows forever | Decision-value routing: SKILL / EVIDENCE / TOOL / REJECT / STOP, with a Merge Test and a registry drift policy (measured ≈10:1 compression) |
| **The extractor's chapter detection is noise** — ToC entries, footnotes, and repeated page headers match before real titles do | Chapter maps that misalign every downstream claim | Five-route structure recovery from the author's own ToC + page markers; LLM only fills gaps |
| **Merged files treated as one book** — `Merged-A+B+C.txt` is three books glued together, each with its own ToC and page numbering | A converter "summarizes" three works as one; cross-book claims get attributed to the wrong author | Deterministic segmentation by per-book markers before anything else (L2) |
| **Incomplete files completed by the LLM** — front matter + ToC + bibliography, no body | The model invents the missing chapters; provenance is poisoned forever | Completeness Gate rejects before generation (S1–S4 signals) |
| **Dirty OCR misjudged by filename** — files named "scan" that are actually clean (and vice versa) | ~20 usable files rejected per 300-item corpus | Quantitative noise metrics, not naming heuristics |

## The core idea

A corpus of N books becomes **far fewer than N knowledge units**. The pipeline's job is to decide, per material, which of these it is:

```
SKILL    — a new decision primitive (a judgment-rule family) → compile with provenance
EVIDENCE — supports existing primitives → register, indexed by primitive_id
TOOL     — formally invocable rules (logic checks, calculators) → separate tool layer
REJECT   — incomplete, unverifiable, or redundant → logged, never silently dropped
```

```
Book A ──┐
Book B ──┼──→  Merge Test: new decision primitive?  ──→  1 family skill
Book C ──┘          (same author, same question)             (not 3 summaries)
```

Compression is the success metric: **hundreds of items → a small set of operational skills** is a traced result (merge/evidence/archive/reject destinations for every item), not a shortfall.

## Who this is for

| You are | Your situation | What this gives you |
|---|---|---|
| **Knowledge engineer** | Building a knowledge base / skill library from books, docs, or OCR corpora | A proven L0→L5 pipeline with deterministic structure recovery and a freeze-baseline discipline |
| **AI agent builder** | Wanting books compiled into skills your agent actually loads | Compilation templates (two types), install/verification steps, and the draft-vs-final naming trap documented |
| **Researcher / analyst** | Synthesizing many sources while keeping attribution honest | Three-layer claim typing (source / agent / cross-source), both page numbers in every coordinate, editorial-intro separation |

## Why this pipeline

1. **Deterministic first, LLM second.** The author's own ToC and page markers beat any extractor's auto-detection (measured: naive grep 4/9 chapters vs page-anchor 9/9). The LLM fills gaps, never invents structure.
2. **Anti-explosion is engineered, not hoped for.** Merge Test + novelty scoring (0–3) + registry drift rate (<5% → <1%) + Stop Condition: every material may legally become nothing. Without these, scaling always inflates into a summary library.
3. **Rejection is a first-class outcome.** Incomplete → REJECT before generation; dirty → quantitative metrics; user-prioritized materials do not override gates. The system knows when *not* to compile.
4. **The SOP is a state machine, and it is tested.** Six terminal states (FREEZE / SKILL / EVIDENCE / TOOL / REJECT / STOP), DFA-style determinism, replayable historical samples; the v3 form replaces semantic guards with a 13-component feature vector (LLM as sensor, computation as controller).
5. **Ship-ready scripts.** Six dependency-light utilities (`scripts/`): structure scanning, page-anchor chapter maps, EPUB→text (stdlib only), PDF→text, chunked PDF extraction, and window→claims decomposition helpers — plus a chapter-map template.

## Quick start

```bash
git clone https://github.com/gootf/corpus-knowledge-engineering.git

# copy the skill into your agent's skills directory
# (SKILL.md + references/ + scripts/ + templates/ is a self-contained skill)

# scan a book's chapter-title formats before writing its chapter map:
python scripts/structure-scan.py path/to/book.txt

# extract EPUB without any dependencies:
python scripts/epub-to-text.py book.epub book.txt
```

Then follow SKILL.md: L0 raw (immutable) → L1 normalize → L2 segment → L3 chapter-map → L4 compile → L5 route. The full working method — format states, pitfalls, evaluation gates, publication standards — lives in the skill's `references/`.

## Honest boundaries

- **Not an auto-summarizer.** The pipeline is deterministic + agent-guided; curation decisions (duplicates, merges, rejects) require a human gate.
- **Not a RAG indexer.** It produces skills with provenance, not retrieval over the raw corpus — the corpus stays the source of truth, the skills are the compiled view.
- **No magic numbers for your corpus.** Compression ratios and cost models were measured on one large corpus; treat them as calibration priors, not guarantees.
- **Chapters with extensive verbatim excerpts are excluded from any public release** (copyright); short quotes and derivative summaries stay.

## Structure

| Path | Purpose |
|---|---|
| `SKILL.md` | The pipeline manual — stages, principles, pitfalls, gates, publication standards |
| `references/` | Protocol details: vector-machine SOP, window→claims decomposition, evaluation gates, release standards |
| `scripts/` | Six utilities (structure scan, chapter maps, EPUB/PDF extraction, claims helpers) |
| `templates/chapter-map.yaml` | Deterministic chapter-map skeleton |

## License

MIT — see [LICENSE](LICENSE).

## Related

The methodology is used as the ingestion reference in [EACKS](https://github.com/gootf/eacks) (S0 ingestion / S1 decomposition / S5 integration).
