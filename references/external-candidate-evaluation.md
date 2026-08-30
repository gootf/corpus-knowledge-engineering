# External Candidate Evaluation — filling protocol/pipeline gaps

Complete workflow for evaluating "use an external repo/tool to fill a protocol or pipeline gap", plus integration-test techniques. Use when a protocol/pipeline has a missing block that an external skill/repo/tool might fill, or when an external AI's recommendation list needs independent verification.

## Trigger

- A protocol/pipeline has a missing block, and you need to find an external skill/repo/tool to fill it
- You received a recommendation list from an external AI and must verify it independently

## Workflow

1. **Verify independently, never mirror external recommendations:**
   - External AIs often get URLs/repo names wrong (measured: an owner-name typo → 404; a tool named without its real repo).
   - Ratings are often overstated (a tool rated ★★★★★ as a drop-in base was actually a different technology stack with impedance mismatch vs the text-knowledge context — downgraded to methodology reference).
   - Independent rating dimensions: **task-structure isomorphism / context fit / license / activity / integration cost**. State the counter-argument explicitly ("strongest task isomorphism, weakest context fit" style) and record which claims were accepted vs corrected.
2. **GitHub verification (avoid API rate limit)**: unauthenticated API is 60 req/h. Use HTML pages instead:
   `curl -s https://github.com/<owner>/<repo>` → regex-extract `og:description` (description) and `aria-label="(\d+[,.]?\d*) users starred"` (stars); 404 pages contain "Page not found". README via `raw.githubusercontent.com/<owner>/<repo>/<main|master>/README.md`.
3. **Download**: codeload tarball is lighter than git clone (no `.git`):
   ```bash
   for br in main master; do
     curl -sL -o x.tgz -w '%{http_code}' "https://codeload.github.com/${owner}/${name}/tar.gz/refs/heads/${br}" \
       && tar xzf x.tgz && mv "${name}-${br}" "${name}" && break
   done
   ```
   Branch name == extracted dir name (`name-main/` needs renaming); large repos time out — download one at a time, `--max-time 90`.
4. **Local code review (not just README)**: look at core module structure, import graph, dependency list; grep to verify claimed features actually exist (a claimed contradiction-detection lived in an agent module but at page granularity ≠ the protocol's relation granularity).
5. **Integration test** (judging "usable / not directly usable"): see techniques below.
6. **Register the evaluation history**: a living candidate register — one row per evaluated candidate (date / repo / stars / license / conclusion) with labels ✅adopt / ◐backup / ✖reject / ?pending, a "current best combination" table, a backlog of not-yet-evaluated candidates, and a dated update log. New searches append rows; never rewrite history.

## Integration-test techniques (verified)

- **PyPI packages pin old dependencies** → skip PyPI, use GitHub source + manually supply dependencies. Measured: an ontology-merging package pinned pandas==1.3.5/pandas-profiling/great_expectations (2021-era, uninstallable on py312); its source ran fine on pandas 3.x / networkx 3.x.
- **Circular-import workaround** (caused by top-level re-exports in `__init__.py`): pre-register empty packages to block `__init__` execution, then load submodules normally:
  ```python
  import types, sys
  pkg = types.ModuleType('pkgname.subpkg')
  pkg.__path__ = [os.path.join(root, 'pkgname', 'subpkg')]
  sys.modules['pkgname.subpkg'] = pkg   # must happen before any import
  from pkgname.data.data_manager import DataManager  # submodule loads normally
  ```
  Precondition: modules on the cycle must not depend on each other (check the import graph first).
- **Corrupted/contaminated system Python** → `pip install --target <dir>` clean dependency dir + script `sys.path.insert(0, <dir>)`, without touching the user environment. Note `--target` flattens multi-top-level packages (`from pipeline import Pipeline` instead of `from pkg.pipeline import Pipeline`); if the flattened `__init__` still imports under the original name, the packaging is inconsistent — go back to the source approach.
- **Heavy report/analysis dependencies can be bypassed**: the core algorithm module often doesn't depend on the report layer (a package whose top-level imports a profiling library — the core manager class only depends on lightweight modules). Drive the core module directly, skip the heavy entry points.
- **⚠ Opposite-direction trap**: a tool's default goal may be the OPPOSITE of the protocol's default (measured: an ontology-merger defaults to MERGING for dedup-maximization; the protocol defaults to differentiation). Tool output must pass through the protocol's conservative gate — never adopted directly. This is the core adaptation work; mark it during evaluation.

## Conclusion shape per gap

External projects supply execution mechanisms and engineering paradigms; the protocol/guard layer (taxonomies, type systems, hard gates) is always self-built — say so explicitly rather than presenting "found a repo" as "gap filled".
