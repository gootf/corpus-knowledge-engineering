# Post-compile audit: publishability + coverage completeness

Two-part audit to run when asked "is this skill publishable / does it leak local info" or "did the skill fully absorb the corpus" — BEFORE touching anything.

## Audit A — privacy/publishability scan (run BEFORE publishing a skill anywhere: repo/PR/docs)

1. **Grep patterns** (add `(?i)` prefix — default search is case-sensitive and silently misses hits):
   - Local paths: `[A-Za-z]:[\\/]`, `/c/Users`, `/home/`, `C:\Users`, `E:|F:|D:|C:` + `[\\/]`
   - User dirs / secrets markers: `AppData`, `.ssh`, `token`, `password`, `api[_-]?key`, `secret`, `credential`, `BEGIN [A-Z ]*PRIVATE KEY`, `sk-[a-zA-Z0-9]`
   - Internal addresses: `localhost`, `127\.0\.0\.1`
   - Workflow artifacts: `PROJECT-LOG`, `PROJECT-CONTEXT`, `AGENTS`, `tasks/`, `.hermes`, `HANDOFF`, `tmp/`, `workspace`
2. **Hidden files**: `ls -la` the skill dir — confirm no `.git`, dotfiles, or stray binaries.
3. **False-positive rule**: content terms legitimately match credential regexes (a "secrets" concept hits `secret`). Verify each hit's context and report the matching LINE, not the regex. Don't report zero-context regex hits.
4. **Verify before asserting**: recount claims/statistics yourself before reporting a count mismatch.
5. **Report shape**: security findings as a table (check item | result); functional defects (broken links, stale notes, count mismatches) listed separately — they are not security issues.

## Audit B — coverage completeness (did the skill fully absorb the corpus?)

Constraint: corpus files are huge — NEVER read them. Verify with metadata + targeted greps only.

1. **Purpose-relative verdict first.** Read SKILL.md + any sibling skills/README.md: what is it FOR? A judgment protocol is not a knowledge base — its coverage standard is the sources it CLAIMS, not the whole corpus. A large corpus → small skill set is designed compression, not truncation.
2. **Source localization**: locate each claimed source in the corpus by filename grep (Merged files: match the first book title before the `+` separator).
3. **Presence verification**: for key claim terms, `grep -o -i "<term>" <file> | wc -l` — non-zero proves the claim's basis exists in source text.
4. **Claim-count cross-check**: umbrella claims.yaml total MUST equal the sum of component skills' claims. Check ID prefixes and depends_on resolution (no dangling references).
5. **Decision-log archaeology**: partial retention is DESIGN when the merge-decision-log documents it — family merge, no-new-primitive → evidence, out-of-domain (journals → archive, current-affairs → reject). Intentional compression ≠ truncation.
6. **Timestamp staleness check**: summary logs lag artifacts. Prefer artifacts + decision logs over summary logs for current state; FLAG contradictions between records.
7. **Honest gap list** (report separately from intentional retention):
   - Dimension upgrades recorded in decision logs may NOT be sunk into the compiled skill.
   - `Scope & Limits` / Gaps declarations go stale vs the evidence layer.
   - A detail layer (e.g. chapters/) may live only in the component-skill tree, not the umbrella — decide publish scope explicitly (whole-tree vs single-directory).

## Verdict shape (conclusion first)

1. Security verdict table (A).
2. Coverage verdict with the purpose-based standard (B).
3. Intentional-retention reasons citing decision-log entries.
4. Numbered genuine gaps.
5. Offer to fix (sink dimensions into skill docs, sync Gaps declarations, pack chapters/) — then wait for user pick.
