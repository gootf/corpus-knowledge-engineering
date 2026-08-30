# Window → Claims Decomposition (post-segmentation, subagent fan-out)

After segmentation, each source is cut into ~8k-char windows `state/s1_windows/<SRC>-cNNNNwNN[sN].txt` (optional `sN` sub-slice suffix when one oversized chunk was split further — e.g. `SRC-0001-c0009w02s2` / `-w03s1` / `-w03s2` alongside unsuffixed `-w04`; flag names carry the FULL id incl. suffix). Parallel subagent batches each get a slice of windows and do, per window: **read → append claims → write done-flag**, strictly in order (clean checkpoints if interrupted).

Outputs per batch (part file `W<k>`):

```
state/claims_parts/<SRC>.W<k>.jsonl      # claim records, append-only
state/s1_done/<SRC>-cNNNNwNN.flag        # {"units_done": n, "chunks": 1, "notes": "window"}
```

Claim record schema (one JSON object per line):

```json
{"claim_id":"C-SRC-0001-c0001-001","unit_id":"SRC-0001","chunk_id":"c0001",
 "parent_src_id":"SRC-0001","quote":"<verbatim>","offset_hint":3200,
 "spo":{"s":"","p":"","o":""},"claim_type":"descriptive|causal|mechanistic|predictive|definitional|taxonomic|interpretive|methodological|normative",
 "origin":"source_asserted","condition":"","boundary":"","granularity":"fine","inference_basis":""}
```

## BEFORE writing: infer conventions from sibling artifacts (mandatory)

Task prompts underspecify; the real contract lives in files already written by earlier batches. Inspect first, then write:

- `ls state/claims_parts/` — sibling part files may exist while you run yours. `head` one to confirm field usage: `offset_hint` = char offset into the *cleaned* window text (−1 when unknown), `condition`/`boundary` carry free-text qualifiers/referent notes.
- `cat state/s1_done/*.flag` for an existing unit → flag naming = **full window id** (`SRC-0001-c0001w02.flag`, not unit-level), and `units_done` = **that window's claim count** (NOT a running batch index — earlier note was wrong). An empty (0-byte) window gets `{"units_done": 0, "chunks": 1, "notes": "window"}` and zero claim lines.
- **Flag template `<n>` is prompt-ambiguous — TWO live conventions coexist.** Sibling batches measure `units_done` = that window's claim count, but a same-day prompt can ship a literal template `{"units_done": <n>, ...}` with no definition of n, and its agent fills `1` per window (one unit = one window done). Both variants can sit in `state/s1_done/`. Before your FIRST flag, grep the same source's existing flags and MATCH their semantics; if you must pick blind, say in your closing summary which convention you used so the parent can normalize at merge.
- **Claim numbering restarts per CHUNK, not per window or per part file — and the scan is across ALL part files.** All windows of a chunk share one NNN sequence even across separate agents/files. Before appending, scan every `<SRC>.*.jsonl` in `claims_parts/` (not just your own part file) for the chunk's max NNN and continue from there:

```python
start_n = 1 + max(int(m.group(1))
                  for fn in os.listdir(parts_dir) if fn.startswith(src + ".") and fn.endswith(".jsonl")
                  for ln in open(os.path.join(parts_dir, fn), encoding="utf-8") if ln.strip()
                  for m in [re.search(r'"claim_id": "C-SRC-0001-c0003-(\d+)"', ln)] if m)
```

  ⚠ **Task prompts can give stale start numbers** (measured: prompt said "c0004 starts at 001" while W4.jsonl already held c0004-001…016 from earlier windows). The files win; continue past their max and FLAG the deviation in your summary for parent arbitration. Corollary: some earlier batches violated global uniqueness anyway (duplicates across part files) — never add NEW collisions, and report pre-existing ones rather than silently fixing other agents' files.
- **The numbering rule itself is a per-batch prompt parameter — two variants observed.** Restart-per-chunk vs CONTINUOUS-within-batch (no reset at the chunk boundary). Obey the CURRENT prompt's explicit rule when it gives one, but the sibling scan stays mandatory EITHER way — parallel live batches may be writing YOUR chunks concurrently, and "collisions fixed at merge" only works if you report exactly what you created. Never mix conventions within one part file; likewise keep ONE offset_hint convention per source family (cleaned-char offset is established — raw line numbers and rough line×~70-char ESTIMATES have both crept in, in separate batches). Estimates are the right order of magnitude (thousands), so NOT caught by a line-number heuristic (<20), but still not find()-exact. If quotes re-locate, repair cheaply in the closeout pass: `r["offset_hint"] = norm.find(clean(r["quote"]))`.
  - **Why it keeps recurring:** delegated subagents never load this skill — the prompt alone governs. Prose warnings in references don't reach them; the fix must be MECHANICAL. Parent dispatch prompts should embed the convention inline ("offset_hint = index from clean(window_text).find(quote), NEVER the line prefix a file viewer prints").
  - **Detection heuristic (closeout):** offset_hint values that (a) exactly match the small integers a file viewer displays as line prefixes AND (b) sit orders of magnitude below sibling parts' hints (~8k-char windows ⇒ char offsets in the thousands; line numbers stay small) ⇒ they're line numbers.
  - **Remediation:** quotes locate uniquely, so the fix is deterministic — for each affected record in YOUR OWN part file: `r["offset_hint"] = norm.find(clean(r["quote"]))` (−1 ⇒ leave and flag). Run before the closeout pass so counts/flags stay honest; never rewrite OTHER batches' part files — report the convention break for parent arbitration.
- Append mode only, never overwrite — parallel batches own other part files.

## Verbatim quote matching (the load-bearing technique)

Window text has hard line-wraps mid-sentence AND page markers embedded INSIDE sentences (page breaks land wherever they land — `[PAGE n/m]` in the corpus family this was built for; adapt the regex to your corpus's format). A sentence quoted from rendered text will NOT raw-match the file. Normalize both sides before `find()`:

```python
def clean(t): return re.sub(r"\s+", " ", re.sub(r"\[PAGE \d+/\d+\]", " ", t))
norm = clean(open(win_path, encoding="utf-8").read())
q    = clean(candidate_quote)
off  = norm.find(q)          # miss → do not guess; investigate
```

- Source typography is curly: U+2019 ’ / U+2018 ‘ / U+2014 —. Quotes must reproduce them exactly; safest to build candidate strings with `\u2019`-style escapes rather than retyping.
- Partial / mid-sentence quotes are accepted convention (existing files contain them). When a sentence runs past the window edge, quote through the last complete clause verbatim and note `"boundary": "sentence truncated at window edge"`. When a pronoun's referent sits outside the quote ('this', 'the event'), pin it in `boundary`.
- On a `find()` miss, print the region around a distinctive fragment to SEE the artifact (a page marker mid-sentence, hyphenation) instead of hand-editing the quote blind. Measured catch: one quote spanning a page break failed until markers were stripped from the match text.
- `offset_hint` = the index returned from cleaned-text `find()` — consistent within the file family, good enough for later re-location.

### Slice, don't type (anchor-based extraction — preferred over retyping quotes)

Typing candidate quotes invites typos and curly-char misses. Instead: pick a **unique ASCII-only anchor** substring inside the cleaned window, locate it, then expand outward to sentence boundaries (terminators `. ! ?` followed by a space):

```python
def slice_sentence(norm, anchor):
    i = norm.find(anchor); assert i >= 0 and norm.find(anchor, i + 1) == -1
    left = max(norm.rfind(". ", 0, i), norm.rfind("! ", 0, i), norm.rfind("? ", 0, i)) + 1
    ends = [e for e in (norm.find(x, i) for x in (". ", "! ", "? ")) if e != -1]
    return norm[left:min(ends) + 1].strip(), left
```

The quote is sliced FROM the text, so verbatim + curly typography are guaranteed by construction. Per-item guards for the cases where naive expansion misfires:

- `end_at`: sentences ending `…river.’` / `…statics’.` — the ’ between `.` and the space breaks the right scan, so it overshoots into later sentences. Cut explicitly after this exact substring.
- `trim_to`: leading junk gets swept in when the preceding sentence has no clean `. ` terminator nearby (section headers sitting between sentences; `i.e. ` acting as a fake left boundary). Drop everything before this substring inside the slice.
- `extend_to`: when one claim legitimately spans TWO sentences ("…an important difference. Plato believed that…"), grow past the found end through this substring found at/after the offset.
- Long quoted-fragment blocks contain NO `. ` for whole paragraphs → left-expansion swallows ~500 chars of quotations. Always PRINT all built records and eyeball them before commit; asserts catch structure, not semantics.
- Footnote digits sit INSIDE sentences and right after terminal periods — keep verbatim, note in `boundary`.
- Line-wrap hyphenation (`instru-\nment` → cleaned `instru- ment`): KEEP the artifact verbatim and record the reading in `boundary` ("reads 'instrument'"). De-hyphenating breaks downstream plain-clean() re-location.
- **Hand-typed quotes under strict pacing drift toward silent normalization.** Parent pacing ("IMMEDIATELY APPEND after reading, ≤2 planning sentences") pushes batches to type quotes by eye — joining wraps with spaces AND de-hyphenating soft wraps, directly against the keep-verbatim rule — then skip any find() verification entirely (closeout checks only JSON validity + id continuity). Net effect: records whose quotes silently FAIL plain `clean().find()` re-location at every de-hyphenated join. When pacing or consent-gating blocks the slice_sentence helpers, run the closeout locate-check anyway with a fallback normalizer instead of skipping it:

```python
def clean2(t): return re.sub(r"-\s+", "", clean(t))   # try clean() first, then clean2()
```

Either restore the artifact-verbatim form in affected quotes, or tag them `boundary: "soft-wrap hyphen de-hyphenated"` so downstream matchers know clean2 applies.

- **Hand-reconstructed multi-wrap quotes need ONE uniform join policy**: joining plain wraps with spaces while pasting a hyphenated wrap verbatim leaves a RAW newline character inside the JSON `quote` field — valid JSONL, but every downstream clean()-based re-location misses it. Prefer wrap-free contiguous clauses (carry the full assertion in spo fields) over stitching 3+ wraps by hand; if a bad record slips through, repair BEFORE the flag with a targeted read-modify-rewrite of just that record (read all lines → json.loads each → fix field → dump back), never a full-file retype.

### Unattended (subagent) execution pattern

In delegated runs the code-execution tool may be consent-gated (blocked without a live user to approve). Working fallback: `write_file` ONE helpers module (`agent_helpers.py`: clean / load_window / slice_sentence / make_rec / next_n / append_records / spec) plus a thin driver per window (`w<N>.py`, items = `(anchor, spo, claim_type[, boundary[, trim_to[, end_at[, extend_to]]]])`). Running with no argv prints every built record for eyeballing; passing `commit` appends + writes the flag only after all asserts pass (append-before-flag keeps checkpoint semantics). Execute via terminal `python wN.py [commit]`. Copy-ready helpers: `scripts/window-claims-helpers.py`.

## Turn-integrity & schema-discipline pitfalls

- **Never end a turn between append and flag.** A subagent turn that stops right after the append leaves the window unflagged — the parent sees no progress and must nudge before work resumes. Complete read → append → flag for each window inside ONE turn before opening the next file; if a turn does break there, the resume action is ONLY the missing flag, not a re-read or re-append.
- **Sibling scan even when the prompt says "create on first append."** A part-file name like W13 implies W1–W12 may exist from parallel batches on the SAME source. One `ls state/claims_parts/<SRC>.*` before the first append costs nothing; starting at 001 blind relies entirely on the "collisions fixed at merge" clause.
- **claim_type is a closed enum** (`descriptive|causal|mechanistic|predictive|definitional|taxonomic|interpretive|methodological|normative`). Inventing a new type for narrative/dating sentences poisons downstream filters — map them to `descriptive`. Truncation-forced inference goes in `origin: source_inferred` + `inference_basis`, never a new type.
- **Window text containing a literal `[truncated]` marker** (pre-truncated slices): quote through the last complete clause BEFORE the marker and record it in `boundary`; copying the `[truncated]` token into `quote` breaks any later re-location against an intact copy of the text.
- **A file viewer's display truncation ≠ missing content**: window files stored as a few GIANT lines get their display output cut mid-sentence with `... [truncated]` — the file itself is intact. Don't treat past-the-cut text as absent and don't quote blind up to the visible edge; fetch what you need with python first:

```python
t = open(win_path, encoding="utf-8").read(); print(t[-1200:])   # or t[i:j] around an anchor
```

  Triage rule: if `[truncated]` appears in viewer OUTPUT, check raw bytes (`len(t)`, search for the token) before applying the in-text-marker boundary rule above — one means "tool display cut", the other means "upstream slice really ends there"; they need opposite handling.
- **Direct code-execution appends are fine when not consent-gated**: building records as Python dicts + `json.dumps(rec, ensure_ascii=False)` + append mode is the simple path for delegated batches where code execution runs un-gated. The write_file-helpers+driver pattern stays the fallback ONLY for consent-blocked environments. **Batch-script atomicity:** a hand-built Python list-literal typo (missing comma between two dict literals) kills the script with SyntaxError BEFORE `open(..., "a")` ever runs — zero partial writes, so fix-and-rerun of the FULL batch is safe; confirm with the json.loads-per-line closeout instead of assuming. Keep records as a list built before any file I/O to preserve this property.

## Per-window loop + closeout verification

Per window: read file → build 4–9 claims (quotes verbatim, spo.s/p/o English terms, type from the taxonomy) → verify all `find()` ≥ 0 → append lines → write flag. Then one closeout pass over the whole part file:

```python
recs = [json.loads(l) for l in open(part_file, encoding="utf-8") if l.strip()]
assert len({r["claim_id"] for r in recs}) == len(recs)          # unique ids
for r in recs:                                                   # every quote locates in SOME window,
    hits = [w for w in my_windows if r["quote"] in clean(open(w).read())]
    # and per-window counts sum to the total you intended
```

Closeout additions: (1) scope the cross-file uniqueness check to YOUR part file and REPORT pre-existing duplicates elsewhere instead of asserting; (2) assert per-chunk numbering CONTINUITY, not just uniqueness (gapless); (3) attribute each quote to its own window via membership in the cleaned text — catches accidental cross-window slices; (4) finish with a flags-present check (N/N). Boundary-note fixes after commit are safe as a read-modify-rewrite of your OWN part file only.

Measured yield: ~8 claims per ~8k-char introduction-quality window; split windows yield proportional to size (~1.4 claims/kchar); a dense chapter sustains the same rate as front matter; empty windows yield 0 claims and a flag-only record. Editorial introductions decompose fine but attribute claims carefully — "Author held X" inside an introduction is the editor reporting the author; use `condition` ("author's view as reported by the editor") to keep attribution honest.
