# The gate's ratchet floor is a table row measured on an engine the tree no longer contains

**Measured 27 Nov 2026, 02:10 IST, on a clean HEAD (`248924f2`), engine docx `a4de7df896875a39`.**

## The symptom

On an **unmodified clone of HEAD**, with the corpus fully built and `measure_gate.py` reporting
`READY - every document measured`, the commit gate refuses:

```
$ python3 tools/p2w-bench/regress.py --check
  engine fingerprint : a4d8fca469bba636
  scope of the change: docx   (scope.py: scope: docx)
  docx: 3 REGRESSION(S)
    39_small_caps_letter_spacing                 0.72 -> 0.80   share@5 up 0.72 -> 0.80 vs the 15 Nov baseline
    newsletter-3col-header-footer                3.45 -> 86.30   share@5 up 3.45 -> 86.30 vs the 15 Nov baseline
    350_question_paper                           0.11 -> 0.12   share@5 up 0.11 -> 0.12 vs the 15 Nov baseline
  google-safe : no construct Google ignores has spread
  REFUSED. This commit would land a regression or an unmeasured engine.
```

The gate does not refuse because a run made a bad change. It refuses because **the committed table is
not a measurement of the committed engine**. No fixer run can land anything until this is resolved, and
every run since 26 Nov 22:20 has ended with an unlandable patch for this reason.

## The proof, from two committed tables and their stamps

`benchmarks/RANKING.csv` and `tools/p2w-bench/txt/ENGINE-STAMP.json` are committed together as a pair.
Read the pair at the two commits that matter:

| commit | what it says it measured | `newsletter-3col-header-footer` share1/2/3/5/10 | stamp `docx` |
|---|---|---|---|
| `4c027304` "RANKING.csv rebuilt on the reverted engine" | the reverted engine | 4.97 / 1.58 / 0.66 / **0.20** / 0.00 | `771234e164611275` |
| `344aff13` "docx table measured on aa496ebe" | `aa496ebe` (the page-top `w:pgMar` change) | 90.88 / 87.62 / 86.76 / **86.30** / 86.10 | `a4de7df896875a39` |
| **HEAD, today** | — | **86.30** (the row above) | `a4de7df896875a39` |

The stamp at `344aff13` reads `a4de7df896875a39`. That is **exactly the docx fingerprint of the current
tree** — so `regress.py` finds no `ENGINE CHANGED` line and passes the provenance check, while the row
it then judges is the `aa496ebe` number.

The two engines cannot share a fingerprint: `engine_fingerprint('docx')` hashes `DocxWriter.java`, and
`DocxWriter.java` differs between `aa496ebe` and `9f0a8207`. So the pair committed at `344aff13` is
inconsistent — the 86.30 row was measured on `aa496ebe`, and the stamp beside it describes `9f0a8207`.

Confirmed independently, twice:

- `git diff 9f0a8207 HEAD -- .../engine/DocxWriter.java` is **empty**. `ee5a00d6` ("restore DocxWriter
  to 9f0a8207") put back the pre-`aa496ebe` file, so the tree today is `9f0a8207`'s engine.
- `4c027304` measured the reverted engine and got **0.20** on that document, not 86.30.
- `978e9cef` (a later run) reported "corpus re-measured on the tree 212/212, **0 regressions vs
  baseline**, 153 clean (was 120)" — the same conclusion, reached by re-measuring. It did not commit a
  corrected `RANKING.csv`, so the stale row survived it.

## What this means, and what it is not

It is **not** an engine regression. The engine in the tree is the engine that measured 0.20 on that
document. The 86.30 is a property of `aa496ebe`, which is not in the tree.

It is **not** fixable by an engine change. No patch to `DocxWriter.java` can make a stale row stop
being stale; any patch moves the fingerprint and the gate then refuses for a second, honest reason
("ENGINE CHANGED").

It **is** a table that must be re-measured on the tree and re-stamped as one act.

## The obstacle to re-measuring it here

The pixel metric in `RANKING.csv` (`share1/2/3/5/10`) is produced by a harness that is **not in this
repository**: `pixbatch.py` imports `sys.path.insert(0, "/scratch/work/vv2/tools/p2w-bench")`, and no
script under `tools/` computes `share5` (checked: `grep -rln share5 tools/ --include=*.py` returns
nothing outside `tools/p2w-bench/`, and every hit there *reads* the CSV). On this pod
`/scratch/work/vv2` does not exist. So a run cannot re-measure the pixel table at all — which is the
mechanical reason the corrected table from `978e9cef` was never committed, and why this has now
blocked four consecutive slots.

## What would unblock it, in order of cost

1. **Cheapest and correct: re-stamp the pair honestly and re-measure the three rows.** Either land the
   `vv2` harness in the repo, or record that the floor for a row must be the *baseline* row, not the
   last-measured row, when the committed value came from an engine that is not in the tree. The second
   is a `regress.py` change and needs no harness.
2. **`git revert 344aff13`** would restore the `4c027304` table (newsletter 0.20) and its stamp in one
   commit. It is a measurement of a reverted engine, and the tree is that engine. It is reversible and
   it is the smallest true statement available. Not done here: the commit also carries the `aa496ebe`
   finding text, and reverting evidence is the one thing this project does not do. The row and the
   stamp are the part that is wrong.
3. Nothing else. A new engine patch on top of a stale floor cannot land, by construction.

## The measurement I could not make, stated as a measurement

I did not re-measure `newsletter-3col-header-footer` on this tree. `screen.py --docs
"newsletter-3col-header-footer"` answers `no OPEN documents for ...` (it resolves documents through the
class store, and this document is not OPEN in it), and no in-repo script computes `share5`. What is
proven above is documentary, from two committed tables and two committed stamps plus an empty `git
diff` — not a render. A render on this tree is the one measurement that would close it, and the tool to
take it is not in the repository.
