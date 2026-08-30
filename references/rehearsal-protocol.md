# Production Rehearsal — protocol and run data

Worked rehearsal of the production protocol on representative materials, done before full corpus scale-out. Shows the format-difficulty spread and the routing decisions.

## Run table (material shapes, anonymized)

| Sample | Material shape | Line endings | Page markers | Structure difficulty | Score | Verdict |
|---|---|---|---|---|---|---|
| book001 | single book / treatise | LF (clean) | none | none (ToC = map) | 9 | Skill candidate |
| book002 | Merged / essay type | CRLF | none | **ToC-only body titles** (headings lost in body) → semantic anchor | 10 | Skill candidate (highest) |
| book003 | Merged / theory | CRLF | `--- Page N ---` (no offset) | `N UPPERCASE TITLE` body format; editor intro vs body | 10 | Skill candidate (new primitive) |

## Rehearsal findings (scale-out must-read)

1. **Line-ending triad is complete**: LF / CRLF / `\r\r\n` (extractor output). Always detect binary before read; normalize to LF.
2. **ToC-only-title failure class**: ToC has full `Chapter N: Title` list but body has no headings → **semantic anchor** = grep the key concept-definition sentences (a concept triplet, a named fallacy, a definition sentence — locate them, anchor chapters by them).
3. **Same-author overlap is the skill-count control point**: multiple books by one author → family merge (skill-merging-rules: new decision primitive?).
4. **Editorial intro vs body**: scholar's editions carry long editor introductions; concept-history claims (e.g. "X introduced concept Y") often live in the intro, not the author's body — label evidence accordingly.
5. **Cost model**: clean single book ≈ low; merged/essay type ≈ 2–3× (structure-recovery cost dominates). Varies by model provider.

## Decision Value Score (Q3) — as applied

| Dimension | Points | Basis |
|---|---|---|
| +3 decision rules | 3 | explicit judgment rules in the material |
| +2 knowledge routing | 2 | who holds the relevant knowledge signals |
| +2 uncertainty handling | 2 | case probability; unknown unknowns |
| +2 strategic action | 2 | opportunity search; robustness → resource allocation |
| +1 historical context | 1 | crisis context etc. |

Bands: ≤3 archive / 4–6 KB only / ≥7 skill candidate. Compile gate: ≥8 AND new decision primitive AND not duplicate.

## Skill Merge Test application

- A book with a distinct judgment-rule family → PASS (new primitive: opportunity discovery/alertness/weak signals — distinct from uncertainty-classification, authority-assignment, diagnosis-first, knowledge-distribution, demand-side-discovery)
- Same-author later books → likely family merge (no new primitive expected)
- A popular-economics primer → likely evidence/reference (consequence intuition already covered elsewhere)

## Landscape projection

A ~300-item corpus projects to a small set of decision primitives / skills + a large evidence layer (tracked in a skill-landscape doc). Expect compression: materials → skills is NOT 1:1, and high-value materials often merge rather than generate.
