# P2W Fixer - Run Report

**27 Nov 2026 · slot 22:00 → running IST · 1h 08m**

> No change was kept this run. The numbers below say what was tried.

## The finding, first

Nine consecutive fixer reports recorded this and read it as bookkeeping:

    ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8
    docx: no document worse than baseline
    REFUSED.

The 20:09 run wrote it out in words: *"What refuses is that RANKING.csv has not been re-measured on this
engine."* This run did that re-measurement — the full corpus, six budgeted `gate.py` slices, about 26
minutes — and the second line changed:

    docx: 96 REGRESSION(S)
    txt : no document worse than baseline
    REFUSED.

**"no document worse than baseline" was never a measurement of the current engine.** It was the stale
table compared against the baseline it was derived from. The gate has been refusing correctly for 63
engine commits, and what it was refusing is real.

## What was measured, and against what

| | |
|:--|:--|
| Engine measured | `a05b20eb05fe0fc8` — clean HEAD tree, nothing of mine in it |
| Corpus converted | **214** documents, 0 failed (4 slices: 53, 53, 53, 20) |
| Corpus re-measured | **212** documents, 6 `gate.py --budget` slices, complete |
| `regress.py --check` | `docx: 96 REGRESSION(S)` · `txt : no document worse than baseline` |
| Independent recompute on `share5` | **84 worse · 47 better · 81 unchanged** of 212 |
| Median delta, all documents | **0.00** |

The tool counts 96 because it also refuses on `median_pt`; my 84 is the `share@5` subset. Both are in
`FINDINGS/GATE-BLOCKED-BY-84-REAL-REGRESSIONS-NOT-A-STALE-TABLE-27NOV.md`; the raw table is committed
beside it as `FINDINGS/RANKING-a05b20eb05fe0fc8-FULL-CORPUS-27NOV.csv`.

## It is one construct: table row placement

| document | 15 Nov | now | delta |
|:--|--:|--:|--:|
| `table-with-no-header-row` | 0.61 | 47.48 | **+46.87** |
| `boq-tender-bill-of-quantities` | 7.10 | 41.95 | +34.85 |
| `very-long-single-column-table` | 6.87 | 41.14 | +34.27 |
| `balance-sheet-and-profit-loss` | 6.20 | 36.69 | +30.49 |
| `price-list-2col-dense-right-aligned` | 2.69 | 27.89 | +25.20 |
| `table-across-page-break-repeated-header` | 9.41 | 33.52 | +24.11 |
| `electricity-bill` | 16.24 | 36.78 | +20.54 |

The improvements in the same window are the mirror image and a different construct: `415_inline_images`
89.04 → 0.00, `411_nested_xobject_transforms` 31.05 → 0.00, `itr-computation-with-slab-table`
68.82 → 38.49. Image and xobject handling got fixed; **tables went backwards**, and 63 engine commits
landed in between without a single corpus measurement.

## What I refused to do

I did **not** run `regress.py --stamp`, and I did **not** commit the new `RANKING.csv` as the comparison
table. `--stamp` would name `a05b20eb` the measured engine and its only effect on these 84 documents is to
stop the gate naming them — it would ratify a 40-point loss on `table-with-no-header-row` as the new
floor. Non-negotiable 3 is "no document gets worse"; a stamp that hides 84 is how a corpus rots for 63
commits while every run reads "no document worse than baseline".

This is also why `report.py` still prints **Regressions: none** — it reads the committed table, which is
the stale one. The tool's blindness and the gate's refusal are the same fact seen from two sides, and that
is the self-check disagreement below.

## Attempts

| At | Class | Outcome | Moved | What it measured |
|:--|:--|:--|--:|:--|
| 22:48 | `63_table_rows` | **lead** | 0 | Gate state, not a fix: 96 real regressions vs the 15 Nov baseline on `a05b20eb`; 84 on `share@5`; all table row placement. Stamping refused as a ratification. |

## The class, and why this one

The class is not a document class this run, and I am saying so rather than picking one that looks
tractable. The work was the commit gate's own state, because **every** class is unlandable while the gate
refuses every commit — a +1 document on `18_displacement` (measured live in Google by the 20:09 run at
41/42 → 42/42) is worth nothing while `regress.py --check` says REFUSED. `classpick.py --leverage` prices
`18_displacement` at 53.9 clean documents and that number is now known to be wrong: the 20:09 run measured
it at +1. The honest order is: restore the table construct, then stamp, then land the cell-before patch.

Recorded against `63_table_rows` because that is the construct that regressed, with `--moved 0` and a
reason that says it is a gate-state measurement on the `share@5` axis and not a Google check.

## Subagents

Two, deployed in the first ten minutes, both on the gate rather than on a grep.

1. **Gate instrumentation audit** — corrected two premises I would otherwise have inherited. The
   documented remedy for `ENGINE CHANGED` is `benchmarks/gate.py --budget 250` repeated until complete,
   then `regress.py --stamp`, with engine + `RANKING.csv` + `STATE.json` committed together. And
   `google-safe : SKIPPED - no .docx output directory` is a **false message**: `google_safe.py` returns
   exit 3 for two different states (no corpus dir, and *mark population ≠ docx count*), `regress.py:636`
   prints one hard-coded sentence for both, and exit 3 is treated as a skip rather than a refusal — so a
   PASS can be issued with `CHECKS THAT DID NOT RUN: google-safe`. The mark records **213** documents and
   the corpus is **214**, so google-safe can never pass without re-basing the mark. Its proposed fix is
   `google_safe.py:299` `return 3` → `return 1`, which turns the silent skip into a refusal.
2. **Page-offset root cause** — nine ranked candidates for the ±4-6 pt whole-page offset on `22` and
   `71`, each with a falsifier, and two corrections that matter: the "footer" is an ordinary flowed `w:p`
   (there is no footer part at all), so a footer that moves proves the shift is in the **flow**, not the
   page frame; and the project's own probe table gives a **range** (−5.84 min −6.74 max −3.69), not a
   rigid shift, so "the two documents need opposite corrections" is not yet established — the sign
   convention is inconsistent between two FINDINGS files. First test named: `R1`, the first line's
   `w:before` charged at `LINE_BASE × hairline` (0.8 × 0.069 em) where the renderer puts it at 0.312 em;
   predicted first `w:sz` ≈ 312 on `22` and ≈ 454 on `71`, and `dy/size` slope 0.257.

## The gate's own state, and one thing I did not fix

    $ python3 tools/p2w-bench/regress.py --check
    engine fingerprint : 72ff003db5871587
    scope of the change: docx, txt   (scope.py: both)
    ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8
    docx: 96 REGRESSION(S)
    txt : no document worse than baseline
    google-safe : SKIPPED - no .docx output directory
    REFUSED.

The `ENGINE CHANGED` line still names the old table because I reverted `RANKING.csv` on purpose. The
`google-safe` skip is the audit's defect and is left unfixed: making it a refusal would block every commit
on a mark that records 213 of 214 documents, and re-basing that mark records today's carriers as the new
ceiling — which is the same ratification I just refused for `RANKING.csv`. It needs to be fixed together
with the table construct, not before it.

## Progress

| | |
|:--|:--|
| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1 (one refused record attempt); kept change: 1 commit in this window with no kept record - correct, the commit is a FINDINGS, not a kept change |
| Document-moves this run | **0** — 1 attempt, 0 kept |
| Documents improved, round total | **61** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none in the committed table** — which is the stale one; measured on `a05b20eb` it is **96**, see the finding |
| Fixed - Google, every applicable check | **46** of the **206** re-measured on this engine |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw |
| Classes solved | 0 of 40 clear |

## Next run

**Do not start with `regress.py --stamp`. It is the wrong move and it is the move nine runs wanted to
make.** Order:

1. **Bisect the table regression.** 63 engine commits between `d28ca7516c3f9165` and
   `a05b20eb05fe0fc8` landed unmeasured. `git log --oneline -- tools/p2w-bench/engine` gives the range.
   Bisect on `table-with-no-header-row` (0.61 → 47.48): a 48-point move on a bare table is the cleanest
   signal on the board, and the corpus and render cache are warm, so scoring one document is seconds.
   Expect the culprit to be in the table row-height or cell-margin path — `trHeight hRule="exact"`,
   `tblCellMar`, or the `cellBoxTw`/`rowHeightTw` interaction the 20:09 run instrumented.
2. **Then** re-measure and `--stamp`. A stamp is honest when the engine is no worse than the baseline.
3. Do **not** re-run the `18_displacement` cell-before patch as landable on this engine: its two measured
   documents, `74_balance_sheet_indented_subitems` (0.03 → 4.80) and
   `price-list-2col-dense-right-aligned` (2.69 → 27.89), are both in the 84.
4. Fix `google_safe.py:299` (`return 3` → `return 1`) together with the table restoration, and re-base
   `GOOGLE-SAFE-MARK.json` from 213 to the real corpus count in the same commit.


## One obstacle worth recording

`bash tools/install-gate.sh` times out at the platform's 300 s ceiling on a cold pod, because
`pod-prep.sh` converts the whole corpus inside it. Running `pod-prep.sh` directly in repeated 285 s calls
is the same work with progress saved — 53, 53, 53, 20 documents. `install-gate.sh` should call
`pod-prep.sh` with a slice budget rather than the whole conversion, or every future run pays five minutes
of timeout before it starts.

## The txt

| | |
|:--|:--|
| Measured | **3.1 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Timing

| | |
|:--|:--|
| Slot window | 22:00 → running · 1h 08m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 152 |
| Longest silence | **14.6 min** — from 22:00:01, after `pending.py: reading the pending gate` |
| Silences over 2 min | 8 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `#` |
| fix - diagnose and change the engine | **4 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **47 min** | `###############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **10 min** | `###` |

The unattributed row is 5 distinct beat(s) that matched no phase. They said:

- `corpus slice 2/4 for the gate`
- `corpus slice 3/4 for the gate`
- `corpus slice 4/4 for the gate`
