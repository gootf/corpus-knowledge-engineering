# Dirty Sample Test + Coverage Test C

Two pre-scale closure protocols: the Dirty Sample Test (Compilation Safety) and the Coverage Test C verdict pattern (new-primitive detection). Complements `coverage-tests.md` (Tests A/B).

## Coverage Test C — technical-capability material

**Verdict: NO new primitive — `capability-boundary` merged as a DIMENSION into `authority-assignment` (novelty=2; anti-explosion hit).**

### Primitive-detection questions (generalize for any candidate source)

- **Q1 — independent decision question?** Partial yes: "What can our organization actually execute?" ≠ "what challenge must be overcome?" (diagnosis = what the problem IS; capability = whether the org CAN execute), ≠ "who owns judgment?" (capability is execution feasibility, not decision rights), ≠ "what do customers need?" (adjacent but distinct).
- **Q2 — independent runtime action?** Partial yes: "spin up an independent exploration unit whose size matches the target market", "never demand quantification-before-entry in disruptive contexts", "value-network blind-spot check". These are NOT producible by re-running existing diagnosis — real action space exists.
- **Q3 — already covered?** customer needs, knowledge, judgment, strategy, uncertainty all have owners. **Organizational capability as constraint = this material's space** (the empty cell).

**Verdict rule (durable):** dimension-merge wins when the decision DOMAIN still belongs to an existing primitive — capability sits where judgment meets execution feasibility → authority domain. Q1/Q2 partially passing is not enough for a new primitive; domain ownership is the tiebreaker.

**Backfill:** runtime-coverage-audit's `technical uncertainty / capability-boundary` field went 0/N → covered by the capability procedure (who funds what / no quantification-before-entry / org-size match / value-network blind spot).

**Title format data point:** `N Title` (digit + space + mixed-case title, no Chapter prefix, not uppercase). No page markers; the Introduction is a high-density anchor region (use it for claim extraction when the rest of the book is partial).

## Dirty Sample Test — Compilation Safety

**Purpose:** before production, verify the compiler does NOT hallucinate on bad input. "Does the system know when NOT to compile?" Same principle as Completeness Gate: reject-before-generate.

### Sample verdicts (3-sample run)

| Sample | Type | Key signals | Verdict | Validates |
|---|---|---|---|---|
| 001 | OCR, complete | garbage 0.5%, `[PAGE N/M]` M/M | **PROCEED** | naming ≠ dirty (quantitative over heuristic) |
| 002 | OCR, structure-uncertain | garbage 0.6%, `--- Page N ---` starting at page 4 (front pages missing), 0 standard chapter hits, CONTENTS present | **PARTIAL** | structure-uncertain → no skill (semantic-anchor recovery first) |
| 003 | Merged, 5 books | boundaries 5/5 (corpus markers, e.g. `【】`), header order note | **PROCEED** (auto-split) | boundary-anchor → source split is rule-able, no manual work |

### Noise metrics (measure, don't guess)

- garbage_ratio: special chars / total chars. <0.01 low, 0.01–0.02 medium, >0.02 high risk. **Measured on 4 named-ocr files: all 0.005–0.008** — "ocr"/"scan" in filenames is a weak signal; per naming you'd reject ~20 usable files in a 300-item corpus.
- page_marker_integrity: markers found vs expected pages; >20% missing → structural risk.
- header_footer_repeat: high-frequency repeated lines in head slice → check pollution.
- chapter_anchor_hits: standard chapter-format hits; 0 → semantic anchor required.

### Compilation Safety decision matrix (formalized)

| Situation | Allowed output |
|---|---|
| Body missing | Reject (insufficient source body) |
| Structure uncertain (0 chapter hits + page gaps) | Partial (recover via semantic anchor, then proceed) |
| Duplicates undecidable | Evidence only |
| Provenance lost | Forbid skill (source-derived is the floor) |
| Named "ocr" but garbage<1% + complete markers | Proceed |

### Special cases

- **archive.org scans**: `--- Page N ---` markers with front pages missing (observed: starts at page 4); needs front-matter completeness check; treat as its own source class at scale.
- **Merged**: corpus boundary markers (e.g. `【】`) + file-header order note → automatic boundary-anchor split + per-book routing.
- Real reject rate estimate for a ~300-item corpus: **<5%**.
