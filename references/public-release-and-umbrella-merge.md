# Public Release & Umbrella Merge

Standards for publishing compiled, corpus-derived skills as PUBLIC artifacts, plus the mechanics of merging multiple skills into one umbrella. Verified end-to-end on a real 6-skill → 1 umbrella release.

## Privacy audit — what corpus-derived skills actually leak

Full scan of all release files using read-only regex scans (Python, since some regex engines mishandle `\p{Han}` and `(?i)` alternation).

### A-class: local path / filename leaks (must fix)

| Location | Content |
|---|---|
| Provenance sections | local material IDs and paths (`pilot/NN/...`, `NNN_author_short.txt`) |
| claims.yaml evidence fields | local OCR filenames + line ranges (`source-149.txt L1996-2011`, `book-01.txt L2458-2485`) |
| Header comments | OCR offset details ("OCR page = printed + 12/+10"), "LF-normalized" |
| Source IDs | numbered material IDs (`04_author_short`, `01_author_short`) |

### B-class: internal pipeline terms & business details (delete / genericize)

- `validation:` blocks with internal case IDs — case descriptions carried REAL business details → deleted entirely, plus "Validated: N cases" lines in SKILL.md
- Benchmark/phase identifiers (`Benchmark N`, `L1 Book Skill Compiler acceptance experiment`, `W3-3`, `L2 synthesis`), "not installed in any skill library", draft version markers, version dates

### C-class: merge-time unification (not privacy)

- `type:` vs `claim_type:` field name inconsistency → unify
- evidence object format `{source_id, chapter, section, page, line}` vs string format → unify to string
- ID collisions: same ID defined in BOTH of two skills → rename one and update ALL references in its protocol file
- Dangling depends_on: referenced IDs that exist in no claims file → drop from depends_on
- Cross-source ID strings: `"author-1945-knowledge-problem"`, `"strategy-kernel"` → resolve to in-library IDs

## Approved change policy (user-confirmed)

1. Evidence coordinates → **author + book title only** (e.g. `"Author, Book Title"`). Line numbers and filenames removed everywhere, including in-body `[source-derived, p13-14/L346-420]` annotations inside support files (kept the `[source-derived]` claim-type marker).
2. Validation records → **deleted** (self-reported validation has no value in a public release).
3. Internal pipeline terms → **deleted**; version markers removed; "draft/not installed" status lines removed.
4. Language → **unified English**; terminology table with tri-state marking approved before translation:
   - standard term: discipline-wide terms
   - author-specific (verbatim): terms that differ in meaning from their near-synonyms (e.g. an "effect" term ≠ its common translation; singular/plural follows the source quote)
   - framework-specific (define at first use): the protocol's own coined terms
5. chapters/ → **excluded from publication** (copyright: whole-chapter compilations with extensive verbatim excerpts of in-copyright books). User decision after explicit explanation of the risk. Glossary/patterns/cheatsheet kept (derivative work).

## External AI feedback arbitration

- A substantive feedback file was mostly adopted (scope and limitations, term distinctions, tri-state marking). REJECTED its reclassification of a core concept (the file conflated knowledge-aggregation impossibility with planning impossibility — the skill's claim is the former). REJECTED pluralizing a quoted term (the source quote is singular).
- A short flattering file: rejected its suggested additions (concepts with no corresponding claims in the library — publication is not content expansion).
- Lesson: when external feedback proposes a RECLASSIFICATION (moving a concept to a different theorist/thesis), verify against the source text before adopting; flattering files need the same scrutiny as critical ones.

## Verification workflow (read-only checks are allowed; modifications are item-by-item)

1. Pre-merge: full residual scan — patterns: local paths/filenames, line-number coordinates (`/L\d{3,}`), CJK chars (`[\u4e00-\u9fff]`), Windows drive paths. False-positive lesson: case-insensitive matching can hit an author NAME that equals a filename root — use context-aware patterns and eyeball hits.
2. Merge completeness: claims union of the sub-files == merged count ± renames; glossary/pattern term counts equal; diff(protocols vs originals) shows ONLY intended edits.
3. depends_on integrity: every referenced ID exists in the merged claims (scripted check) — 0 dangling after cleanup.
4. Final: re-scan the published directory only (source tree keeps chapters/ and stays dirty by design).

## Final structure produced

```
umbrella-skill/
├── SKILL.md            # entry: routing table + judgment chain + terminology + provenance
├── claims.yaml         # merged claims (source-derived / agent-derived / cross-source-derived)
└── references/
    ├── protocols/      # per-protocol files (decision procedures/anti-patterns/translations)
    ├── glossary.md     # terms, source-tagged
    ├── patterns.md     # patterns, source-tagged
    └── cheatsheet.md   # rules, two parts
```
