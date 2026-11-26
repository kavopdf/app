# Fixer report - 2026-11-26 15:24

```
# P2W Fixer - Run Report

**26 Nov 2026 · slot 15:46 → running IST**

> No engine change was kept. One lead was restored after the run before it had closed it on bad data,
> and the obvious mechanism for it was refuted by measurement.

## Progress

| | |
|:--|:--|
| Check-instances passing | **8521** of 9058 (94.1%) on 208 documents |
| Check-instances still failing | **537** |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| **Fixed - Google, every applicable check** | **42** - out of the **207** re-measured on this engine |
| Not scored - page count did not match | **6** of the 213 gverify saw |
| Moved but still open | **28** |
| Classes solved | 0 of 40 clear |
| Document-moves this run | **0** — 1 attempt(s), 0 kept |
| Regressions | **none** |

## What was tried

| At | Outcome | What it measured |
|--:|:--|:--|
| 16:19 | **lead** | `18_displacement`: worst_dy vs `docx_table_rows` is **2.188 pt/row, r² 0.423, n=207** on `benchmarks/gverify/*.json`. The 15:12 run's "0.518 pt/row, r² 0.01" does not reproduce; `DISP-TABLE.csv`'s Google columns are stale (32 disagreements among the 130 worst_dy values compared, max 96.70 pt; 20 of 213 fail flags disagree). |
| 16:17 | **lead** | `p2w.fitreserve` 96 → 300 twips: `word/document.xml` **byte-identical on all 8** largest-displacement multi-row documents (very-long-single-column-table, table-across-page-break-repeated-header, 324_loan_amortisation_schedule, bank-statement-5-pages, gst-invoice-multipage-item-table, form16-part-b, mutual-fund-statement, balance-sheet-and-profit-loss). The fit reserve never fires on them. |

## Why nothing moved

The class is `18_displacement`: 113 documents out of the 207 scored fail it. The run before this one closed the row-count lead
with a slope that does not exist in the committed data. Restoring it was worth the slot, because the
alternative - another blind patch - is what the previous five attempts did.

The mechanism that lead suggests was then tested and did not hold: if a sheet is left with ~25 pt of slack
and row growth eats it, the engine's own fit reserve is the lever. Raising it from 96 to 300 twips changed
not one byte of eight documents that are 70 to 657 pt out in Google. So the pages are not "slightly over"
by the model's accounting - the model and the renderer disagree about page height by an amount that scales
with row count.

The engine charges a ruled row **15 twips (0.75 pt)** of excess (`DocxWriter.java:6151`). The displacement
slope says the rendered excess is about **2.2 pt/row**. That three-fold gap is the next run's first
question, and one probe document decides it.

## The txt

| | |
|:--|:--|
| Measured | **4.5 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Landed | Took |
|:--|:--|:--|--:|
| R-01 | recompute the `18_displacement` families from committed data and find what separates the 17 worst from the 58 smallest | yes - 17 / 38 / 58 reproduced exactly; slope disagreement found | 3 min |

It ran inside the turn, so report.py does not see it; its numbers were re-derived here before being used.
One of its claims did not survive my own check: it counted 34 `worst_dy` disagreements in `DISP-TABLE.csv`,
I count **32**.

## Gates

`regress.py --check` PASS (no document worse, google-safe, table matches this engine a4d8fca469bba636);
`measure_gate.py` READY (212 of 212 scored). The gate was never the obstacle this run.

## Timing

| | |
|:--|:--|
| Slot window | 15:46 → running · 1 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 6 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **1 min** | `######################` |

The window above is not the slot. The claim was recorded at **15:24**; `RUN.json` was reset to 15:46
by the first tool call that wrote a run window, so the duration shown is short. The cold-pod cost was
real: `install-gate.sh` was killed at 300 s, then three `pod-prep.sh` corpus slices ran
(53 + 53 + 17 documents, 224 s + 186 s + 88 s), about 28 minutes in all.

## Next run

**Read `FINDINGS/18-displacement-ROW-COUNT-LEAD-RESTORED-26NOV-relay.md` first.** It replaces the "do not
touch rows" instruction of the 15:12 run, and it names the two things not to repeat:

- Do not fit displacement numbers on `DISP-TABLE.csv`'s `google_*` columns. They are stale. Use
  `benchmarks/gverify/*.json`. Structural columns of the CSV (`docx_table_rows`, `src_pages`,
  `declared_row_pt`) are fine.
- Do not sweep `p2w.fitreserve` on the large-displacement family. Measured inert, byte for byte, on the
  eight worst.

**First attempt: one probe on `324_loan_amortisation_schedule`** (246 table rows, 7 pages, worst_dy 357.8).
Measure in Google the rendered height of one ruled row against its `w:trHeight` declaration. If the
rendered row is ~2 pt taller than declared while the engine charges 0.75 pt, the constant at
`DocxWriter.java:6151` is the defect and the fix is a number, not a construct. If it is 0.75 pt, row growth
is not the mechanism and the 2.19 pt/row slope is a proxy for something else that scales with row count.

**Pod cost, priced:** ~28 minutes cold, in this order - `pod-prep.sh` until it says DONE (it converts the
corpus in 240 s slices and tells you how many are left), then `regress.py --check`, then `measure_gate.py`.
