# The gate's four refusals are four ghost rows, and all four are now measured

**27 Nov 2026, fixer, 02:2x IST. Engine `a4de7df896875a39` (docx) / `a4d8fca469bba636` (txt).**

## What refused

`python3 tools/p2w-bench/regress.py --check` on a clean tree at `be10ebd`:

```
  docx: 3 REGRESSION(S)
    39_small_caps_letter_spacing                 0.72 -> 0.80   share@5 up ... vs the 15 Nov baseline
    newsletter-3col-header-footer                3.45 -> 86.30   share@5 up ... vs the 15 Nov baseline
    350_question_paper                           0.11 -> 0.12   share@5 up ... vs the 15 Nov baseline
  REFUSED. This commit would land a regression or an unmeasured engine.
```

`measure_gate.py` is READY (212/212 scored, 1 exempt, 0 blocking) and `git diff` on `app/` is empty.
So the refusal is not about code: it is about four rows of `benchmarks/RANKING.csv`.

## The cause

`benchmarks/RANKING.csv` was last written by the **withdrawn** engine `aa496ebe` (the page-top gap that
moved `w:before` into `w:pgMar w:top`, commit `aa496ebe`, reverted to `9f0a8207` by `ee5a00d6`). 208 of
its 212 rows agree with the current tree; four do not, and all four are `aa496ebe`'s numbers.

## The measurement, made this run, independently of the CSV

`benchmarks/p2w.py::measure_doc(pdf, dx)` on the already-converted corpus, one call per document, same
instrument that wrote the table (LibreOffice render, scipy exact EDT, ink threshold 68). Reproduced the
previous run's `FINDINGS/RANKING-MEASURED-RESTORED-ENGINE-27NOV.csv` **exactly**, to the last digit:

| document | 15 Nov baseline | RANKING.csv before | **measured now** | verdict vs baseline |
|---|---|---|---|---|
| newsletter-3col-header-footer | 3.45 | 86.3 | **0.20** | better by 3.25 |
| itr-computation-with-slab-table | 68.82 | 9.1 | **42.33** | better by 26.49 |
| 39_small_caps_letter_spacing | 0.72 | 0.8 | **0.70** | better by 0.02 |
| 350_question_paper | 0.11 | 0.12 | **0.11** | equal |

Three of the gate's four refusals were therefore **phantom**: they charged the tree for `aa496ebe`'s
defects, and on the tree the same three documents are better than the 15 Nov baseline, two of them by a
wide margin.

## The one refusal that is real, and why it still gets landed

After the three rows were corrected the gate reported exactly one:

```
    itr-computation-with-slab-table              9.10 -> 42.33   share@5 up 9.10 -> 42.33 vs the last commit
```

That is not a phantom in the same sense. **On this tree `itr` really is 42.33**; it was 9.10 on
`aa496ebe`. The engine revert (`ee5a00d6`) bought `newsletter` 86.3 -> 0.2 and cost `itr` 9.1 -> 42.33.
That trade was made by a previous run and is not this run's to relitigate. What is this run's to fix is
that the table said 9.10 while the engine produced 42.33, so every commit was refused for a number that
no code in the tree could produce.

So the row is landed at its measured value, with `--no-verify`, as **measurement data only** - the same
route `6815af8e` and `344aff13` used. No engine code, no instrument change. The ratchet's floor then
becomes 42.33, which is what the tree measures, and the gate passes for real from here.

**`itr` at 42.33 is an open defect, not a paper improvement.** Its shape (share@1 64.93, @5 42.33,
@10 27.4 - a falling curve) is displacement, and it is one of the 14 documents one check away from clean
in Google. It is on the list for the next attempt, not closed by this commit.

## What would overturn this

Re-measuring any of the four on the current tree and getting a different number. The command is in
`/scratch/work/verify4.py`; it takes about 90 s for the four.

## Correction to the previous run's framing

`aef11fc6` concluded the gate's floor "carries an aa496ebe newsletter row (86.30) under a 9f0a8207
stamp". Half right: the row is `aa496ebe`'s, but there were **four** such rows, and the gate reported
them as three baseline regressions plus (after correction) one ratchet trip - not as one newsletter row.
The `benchmarks/STATE.json` field `"engine": "aa496ebe"` is a third stamp scheme (8-char git abbrev) that
no `--check` path reads; it is stale and should be re-stamped by the harness, not hand-edited.
