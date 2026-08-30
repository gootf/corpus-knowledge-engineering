# Coverage Tests — new-primitive detection before scale-out

> Pattern: before full scale-out, run 2–3 targeted "coverage tests" (Test A/B/C) on
> materials that might either create a NEW decision primitive or extend an existing one.
> Verdicts: Test A = **upgrade, not new**; Test B = **dimension merge, not new**.
> Test C (capability boundary) = **dimension merge** — see `dirty-sample-and-test-c.md`.

## Test A — institutional-constraints material

### Why this material

The "who knows?" essay answers who holds knowledge; institutional-constraints material answers "what INSTITUTIONS allow knowledge to be used?" — rules/commands/incentives shape the decision environment itself. Decision-maker mapping: why do heavy-control processes suppress initiative?

### Extraction route

- Material: a rule-of-law treatise epub → zip → HTML strip → clean text.
- Title format found: **English-word chapter numbers + cross-line title** (`Nine / <Title>`); ToC shows printed pages but body has NO page markers → line-only provenance; page headers repeat the chapter title (anchor).
- Content anchors (claim coordinates): freedom = absence of coercion; coercion definition ("one man's actions are made to serve another man's will"); known-rules constraints.

### Claims registered (concept-level, source-derived)

- liberty = absence of coercion (provisional definition; coercion requires a human agent — physical force ≠ coercion)
- coercion definition (serve another's will; coerced still chooses)
- rule of law = government coercion only for enforcing known rules; rules must be abstract, not ad-hoc commands
- rules vs commands: spontaneous order coordinates via general rules; commands are specific instructions — rules give individuals stable expectations
- known rules make coercion predictable → individuals can plan
- (cross-source) institutions decide whether knowledge gets used (depends_on rules claims + dispersed-knowledge claims)
- (agent-derived) heavy-control processes reduce initiative BECAUSE commands replace rules → local knowledge can't be used
- (cross-source) rules delimit the exercise boundary of derived judgment

### Verdict

| Question | Answer |
|---|---|
| New primitive? | **NO** — institutional constraint is a dimension of the knowledge problem, not a new decision domain |
| Primitive upgrade? | YES — the knowledge-distribution primitive gains an institutional dimension (rules/incentives/permissions) |
| Authority deepening? | YES — rules delimit derived-judgment boundaries |
| Runtime impact? | YES — the memo template gains "rules-led vs command-led" checks |

Compile decision: do NOT build a standalone skill — fold the institutional claims into the existing knowledge-distribution skill as its institutional dimension (re-evaluate only if organizational-design scenarios become high-frequency).

## Test B — capital/time-structure material

### Why this material

Long-horizon decisions (rewrite architecture, platform investment, tech-debt repayment, expand R&D) are NOT strategy-diagnosis questions — they are **time-structure problems**: the action itself changes the future option space. Capital-theory macro (intertemporal capital structure, short-/long-run coupling, sustainable vs unsustainable growth) is the answer.

### Material defect discovered (Completeness Gate trigger)

A seemingly complete book file (clean line endings, plausible word count, full ToC with 12 chapters) contained ONLY title page + introduction + preface + ToC + acknowledgments + bibliography. **All 12 chapters of body text were missing** (file ≈ front third of the book). A naive pipeline would have proceeded and the LLM would have "completed" the missing body → a beautiful skill with fabricated basis → provenance poisoned. This is the systemic risk the Completeness Gate exists for.

### Handling (do not abandon the test on a defective file)

1. Record the defect as a pipeline data point (new material-defect class: incomplete book).
2. Downgrade to **concept-level verdict**: the Preface carries the core concepts (intertemporal capital structure; short/long-run real coupling; sustainable vs unsustainable growth; credit-induced artificial boom).
3. Cross-verify with alternate corpus sources: a heterogeneous-capital treatment in another book; the origin text on the same school.

### Claims registered (front-matter based, flagged partial)

- intertemporal structure of capital (time-consuming, multi-stage)
- real coupling of short- and long-run; consumption/investment move together short-run, must oppose to change the growth rate
- sustainable vs unsustainable growth; credit-induced artificial boom → intertemporal misallocation → eventual liquidation
- intertemporal coordination
- production-structure shape (lengthen/shorten), not just scale
- (cross-source) capital heterogeneity — already covered by another book
- (agent-derived) time-structure decision triad: **now-sacrifice ↔ future-release ↔ path-reversibility** (the test's decision variable)
- (cross-source) intertemporal-misallocation signal: short-term metrics vs unsustainable structure

### Verdict

| Question | Answer |
|---|---|
| Q1: Just resource commitment? | **NO** — commitment is an action attribute; intertemporal capital structure is the decision OBJECT (what to sacrifice now / release later) |
| Q2: New decision variable? | YES — the triad, incl. "is the middle path reversible" (partial/exit costs) |
| New primitive? | **NO** — dimension, novelty=2; merged into diagnosis-first as time-structure dimension; the memo template's irreversible-commitments field upgraded to a 4-check (sacrifice / release / reversibility / artificial-boom detection) |
| Anti-explosion | held — no time/capital/investment skills created |

## Completeness Gate (formalized from Test B)

Input validation BEFORE curation, per material:

```
signals: S1 body-anchor missing (ToC titles absent from body region)
         S2 size-ratio anomaly (words ≪ expected; front+ToC+bib ≈ 1/4-1/3 of book)
         S3 structural termination (file ends in bibliography/index)
         S4 citation integrity ("see Chapter N" with no such chapter)
grades:  complete → proceed
         partial (missing <20%) → proceed with gap marked
         incomplete → REJECT (insufficient source body)
         fragment (no ToC no body) → evidence-eval, not skill compile
policy:  reject ≠ delete (log in merge-decision-log)
         reject BEFORE generate when uncertain (LLM-completion is the failure mode)
         source-derived evidence is the provenance floor
```

Add the gate to the pipeline before curation for full scale-out.

## Mini-pilot selection lessons

- Sample choice = failure-mode coverage, not importance ranking. After the rehearsal books the remaining increments are: institutional material (Test A), capital/time material (Test B), technology judgment (Test C), plus one dirty-OCR and one weak-theory sample. 5–6 samples answer this; 10 is padding.
- The dirty/low-value samples are the only true randomness checks — running them token-style defeats the purpose.

## Phase freeze pattern

`phase-freeze-manifest.yaml`: version + validated (router/classification/merge/explosion-control/runtime) + known_gaps (recorded at freeze time, not silently fixed) + rule_freeze ("attribute failures to compiler vs corpus-type vs routing rule"). Phase-level freeze complements book-level golden manifests: it tells you WHAT was validated before the next phase started.
