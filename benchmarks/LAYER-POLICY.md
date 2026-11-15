# Layer policy — what is authoritative, what is advisory

Three layers measure the pipeline. They are not equal, and no consumer should
have to guess which one to trust.

## Layer 1 — ground truth (blocking)

`p2w.py --validate`

Sets displacement by construction on synthetic pages and reads it back:

    1/2/5/10/20/40 pt horizontal   1/5/10 pt vertical
    diagonal (3,4) pt must read 5.00 — proves Euclidean, not Manhattan
    identical pages must read 0.000
    ink removed must be flagged, not scored
    1 px jitter must read 0.000 — the raster floor

Tolerance is 1 px at 150 dpi = 0.48 pt, the raster's own resolution.

**If this fails, nothing else runs.** A number produced by an instrument that
cannot read a known value is not a measurement. `gate.py` exits 3 and measures
nothing.

## Layer 2 — global measurement (authoritative for size)

`p2w.py --budget N`

Two axes per document:

    POSITION   a tolerance sweep (share@1,2,3,5,10 px, median, p90, max).
               The SHAPE of the sweep classifies the defect:
                 flat    -> ink absent     (content-loss)
                 falling -> ink displaced  (displacement)
                 ~0      -> page right     (clean)
    CONTENT    character-multiset recall against the source text.

**This is the authority for "how far off is this document".** Its numbers are
the ones to quote. Reproduced to the digit across full environment wipes.

Rank by `share@5px`, never by `share@1px` — the latter is inflated by text
antialiasing and would order documents by how much text they contain.

## Layer 3 — named semantic checks (advisory)

`verify_google.py` (47 docx checks) and `verify_txt.py` (12 txt checks).

These name a defect; they do not size it. They cover things a raster cannot
carry — UTF-8 validity, page separators, symbol counts, line order, page
furniture — which is why they are kept.

**They are advisory, and a check that cannot fail is a bug in the check, not a
pass.** Before a check's result is quoted, it must be shown capable of failing;
otherwise it is retired or repaired.

**Measured status of the falsifiability, and a retraction.**

The .txt checks: 12 of 12 proven able to fail (`TXT-FALSIFIABILITY.md`,
`T09-FURNITURE-FIX.md`). Getting there required fixing two checks -- t09 could
only see MISSING furniture, and t06/t10 had never been given the input they test.

The docx checks: 47 of 47 proven able to fail (`FALSIFY-47-RESULT.md`). 41
mutations, each aimed at specific checks of a real corpus document; 41 fired
their target, 0 missed, 0 errored, and every one of the 47 fired at least once.

**This page used to say "the falsifiability gate already showed that 66 % of
verify_google's passes could not have failed." That was wrong and it is
withdrawn.** The figure came from a run against an earlier verifier; the harness
had since broken (`set_universe()` was removed from verify_google.py), so nobody
could reproduce it, and when it was repaired the measurement said the opposite.
It is recorded rather than quietly deleted because a number that is repeated
after it stops being reproducible is the exact failure this whole layer exists
to prevent.

So the 47 checks are advisory for one reason only, and it never needed a
percentage: **a named check tells you a defect exists, it does not tell you how
large it is.** `01_page_count` cannot say a document is 3 % wrong; `share@5px`
can. Falsifiable is the floor -- it says the check responds when its input
breaks. It does not say the check responds to the right things, which needs
documents known to be correct, not mutations known to be wrong.

## The ratchet

`gate.py` compares the new RANKING.csv against the committed baseline. Any
document whose `share@5px` got worse is a REGRESSION, whatever else improved.
Regressions are reported, never silently accepted.

A change that improves one document and worsens another has not been verified.

## What gate.py refuses to do

* Measure with a failing ground-truth gate.
* Drop a document it could not measure — that document becomes a `MEASURE-ERROR`
  row in RANKING.csv.
* Report a layer it did not run — a skipped layer is `not-run` with a reason,
  never a pass.

## Entry point

    python3 benchmarks/gate.py --budget 250     # run all layers, write STATE.json
    python3 benchmarks/gate.py --ratchet-only   # compare to baseline only

STATE.json carries one `verdict` line:

    BLOCKED: instrument failed ground-truth validation
    REGRESSION: N document(s) worse than baseline
    OK, but no baseline to ratchet against
    OK: no regressions against baseline
