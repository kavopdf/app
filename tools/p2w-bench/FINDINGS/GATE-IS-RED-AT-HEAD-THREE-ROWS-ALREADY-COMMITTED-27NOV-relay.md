# The gate is red for ONE reason: the itr gain and the newsletter break are the same clause

Measured 27 Nov 2026 on a fresh clone of `main` at `c1f4ed6`, engine `a4d8fca469bba636`, corpus built
213/213 by `corpus-slice.py` (191 + 233 + 125 s, 0 failed), then **203 of 212 documents re-measured**
by `benchmarks/p2w.py` on that engine. The full measured table is
`FINDINGS/RANKING-MEASURED-RESTORED-ENGINE-27NOV.csv`.

## What was believed, and what the measurement says

`regress.py --check` at HEAD, with nothing in `app/` touched, refuses on three rows:

    39_small_caps_letter_spacing    0.72 -> 0.80
    newsletter-3col-header-footer   3.45 -> 86.30
    350_question_paper              0.11 -> 0.12

The committed `benchmarks/RANKING.csv` holds the numbers of the **withdrawn** engine `aa496ebe`
(commit `344aff1` recorded the table but deliberately did not commit it; it landed later anyway).
Re-measuring on the restored engine, all three come back at or better than the 15 Nov baseline:

| document | baseline 15 Nov | committed RANKING.csv | **measured, restored engine** |
|:--|--:|--:|--:|
| `newsletter-3col-header-footer` | 3.45 | 86.30 | **0.20** (signature `clean`) |
| `39_small_caps_letter_spacing` | 0.72 | 0.80 | **0.70** |
| `350_question_paper` | 0.11 | 0.12 | **0.11** |

So the three-baseline regressions are **stale data, not engine behaviour**. Writing all 203 measured
rows into `RANKING.csv` and re-running the gate leaves exactly one refusal, and it is a different one:

    docx: 1 REGRESSION(S)
      itr-computation-with-slab-table   9.10 -> 42.33   share@5 up 9.10 -> 42.33 vs the last commit

`itr-computation-with-slab-table`: baseline 68.82, withdrawn engine **9.10**, restored engine **42.33**.
The restore bought back newsletter (86.30 -> 0.20) and gave back 33.23 share5 on itr. The ratchet
compares against the last commit, so it refuses the restore.

## The decision this leaves, stated as a number

| clause | newsletter share5 | itr share5 |
|:--|--:|--:|
| withdrawn (`aa496ebe`) | 86.30 | 9.10 |
| restored (`9f0a8207`, HEAD) | 0.20 | 42.33 |

One clause, 86.10 points one way and 33.23 the other. Both documents are **better than the 15 Nov
baseline** under the restored engine (newsletter 0.20 vs 3.45; itr 42.33 vs 68.82) — the refusal is
against the previous *commit*, not against the baseline.

The previous run's agent bisected this and proposed gating the clause on page count
(`pageTopTw = 0` when `pages == 1`), with six deciding documents: newsletter, 600, 601 and 401 must
not move; itr-computation and bank-statement-5-pages must keep their gain. Its report
(`AA496EBE-BISECT.md`) is **not** in the tree — it exists only in prose inside `LAST-MESSAGE.md`.
The withdrawn clause itself **is** recoverable: `tools/p2w-bench/PATCHES/aa496ebe-pagetop-not-identity.patch`,
229 lines, re-landable. It carries no page-count gate today, which is why re-landing it as-is reproduces
86.30 on newsletter. `git cat-file -t aa496ebe` fails in a depth-50 clone, so the patch is the only copy
of the change — read it, do not fetch for it.

## Also recorded here, because it costs every run

A fresh pod has no corpus, no JDK and no compiled engine, and `install-gate.sh` (which calls
`pod-prep.sh`) exceeds the 300 s call limit on the corpus conversion alone. This run spent 9 minutes
on three `corpus-slice.py` calls before it could measure anything. That is 10 % of a 90-minute slot,
every slot, on a pod that keeps nothing between runs.
