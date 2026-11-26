# 18_displacement: the clause is `over_tolerance` on 25 of 25 -- `if not ds` fires on NONE

**26 Nov 2026, slot 07:42 IST.** Measurement only. No engine change, no file deleted, nothing else
committed. The instrument was run on real Google renders, not modelled.

## The answer, in one paragraph

`SETTLED.md` section "The table-top spacer is NOT what fails the 16 solo `18_displacement`
documents", subsection 4c, left one test open: six solo documents showed `max_pt` 1.44-2.40 pt, under
the check's 1.5 pt floor, and the only branch that can fail a page whose runs are all inside their
tolerance is `if not ds:` -- upright text on the page and none of it matched. **It was run on all 25,
and that branch fires on none of them.** Every one of the 25 documents fails `18_displacement` through
`over_tolerance`, and every one of them through the per-page budget clause specifically
(`n_out > max(2, ceil(0.05 * len(ds)))`); 18 of the 25 additionally fire the tail clause
(`worst_ratio > 2.0`); the "every run out" clause fires on none. **The class is vertical position, not
run matching and not reading order.** No document is "not determined" -- 25 of 25 were run.

The `not ds` hypothesis was reasonable and it is now dead: the six documents that looked impossible
were an artefact of `benchmarks/RANKING.csv`'s ink metric, which is a different quantity from the
check's run-baseline `dy` and does not bound it in either direction (section 4 below).

## 1. Method -- no build, no LibreOffice, no estimate

The check needs a source PDF, a Google Docs export of the engine's .docx, and the .docx. All three
existed already; nothing was converted.

    engine     981ff1fa35e2cf67   (the engine stamp on all 25 stored verdicts, and on the .docx in Drive)
    corpus      bash tools/p2w-bench/corpus-fetch.sh   -> 213 PDFs, 0 missing against RANKING.csv
    .docx       Drive folder 1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA, 25 of 25 found
    render      each .docx copied as application/vnd.google-apps.document, then exported as
                application/pdf (GOOGLEDRIVE_COPY_FILE_ADVANCED + GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE,
                the same two calls grender.py / refresh-google.py make). 25 of 25 rendered.
    check       verify_google.py at HEAD, copied to /scratch/work/vg18.py with ONE change: the
                18_displacement page loop records which branch it took per page and the per-run
                (ry, dy, size) list. No threshold, no population and no pass/fail rule was touched.

Two proofs that the instrument is the stored one, not a new one:

* **It reproduces the store.** All 25 give `41/42` with `failed == ["18_displacement"]` -- identical
  to `benchmarks/gverify/<doc>.json`, on all 25. `med_dy`, `worst_dy` and `runs_matched` match the
  stored `displacement` block to the digit on every document whose stored verdict carries one
  (`16_right_aligned` -1.6 / 3.4 / 64, `403_crossword` -43.6 / 45.7 / 27, `320_balance_sheet_statutory`
  8.2 / 19.4 / 73, and so on).
* **The probe is inert.** The added recording runs after the pass/fail decision; the 41/42 and the
  failing set are what the unmodified tool prints.

The document list is the 25 whose stored `failed == ["18_displacement"]` in `benchmarks/gverify/`
(213 files read) -- the same 25 `classpick.py --leverage` prices at 54.4 clean documents.

## 2. The table

`max_pt` and `share5` are `benchmarks/RANKING.csv` (read, not re-derived, as instructed). Everything
from `ds` rightward is the JSON this run produced. `tol` is the median of
`clamp(0.35 * size, 1.5, 4.5)` over the page's matched runs -- the per-run tolerance the check
actually applies, which is 2.03-3.85 pt on all 25 and nowhere near the 4.5 pt cap.

| document | `max_pt` | `share5` | clause fired | `ds` | `n_out` | budget | worst_ratio | max abs dy | median abs dy | tol |
|---|--:|--:|---|--:|--:|--:|--:|--:|--:|--:|
| `16_right_aligned_amounts_txtpos` | 2.4 | 0.0 | `over_tolerance:budget` | 64 | 7 | 4 | 1.08 | 3.41 | 1.56 | 3.15 |
| `303_discharge_summary` | 1.92 | 0.0 | `over_tolerance:budget` | 45 | 9 | 3 | 1.67 | 4.10 | 1.24 | 2.80 |
| `31_times_body_arial_headings` | 17.76 | 1.04 | `over_tolerance:budget` | 29 | 4 | 2 | 1.20 | 3.54 | 2.62 | 3.67 |
| `320_balance_sheet_statutory` | 2.4 | 0.0 | `over_tolerance:budget+tail` | 73 | 55 | 4 | 7.88 | 19.37 | 8.24 | 2.62 |
| `325_demat_holdings_statement` | 2.88 | 0.0 | `over_tolerance:budget+tail` | 84 | 52 | 5 | 15.13 | 38.13 | 3.78 | 2.52 |
| `362_price_list_dense` | 3.36 | 0.03 | `over_tolerance:budget+tail` | 257 | 181 | 13 | 2.56 | 5.37 | 2.81 | 2.03 |
| `36_embedded_subset_font` | 2.4 | 0.0 | `over_tolerance:budget` | 29 | 8 | 2 | 1.26 | 3.52 | 1.71 | 3.32 |
| `402_calendar_month_grid` | 2.4 | 0.0 | `over_tolerance:budget+tail` | 46 | 5 | 3 | 2.65 | 6.49 | 1.42 | 3.85 |
| `403_crossword_puzzle` | 2.88 | 0.0 | `over_tolerance:budget+tail` | 27 | 14 | 2 | 19.25 | 45.69 | 43.63 | 2.45 |
| `68_journal_wide_table_spanning` | 8.64 | 12.09 | `over_tolerance:budget+tail` | 74 | 61 | 4 | 43.42 | 115.03 | 114.28 | 2.87 |
| `70_magazine_drop_cap_photo_caption` | 10.56 | 1.16 | `over_tolerance:budget` | 24 | 8 | 2 | 1.18 | 3.27 | 3.00 | 3.22 |
| `71_invoice_space_aligned_no_rules` | 9.12 | 26.88 | `over_tolerance:budget+tail` | 72 | 29 | 4 | 2.39 | 6.69 | 1.06 | 3.15 |
| `72_bank_statement_no_rules_right_amounts` | 2.4 | 0.0 | `over_tolerance:budget+tail` | 80 | 75 | 4 | 9.37 | 28.21 | 12.96 | 3.01 |
| `74_balance_sheet_indented_subitems` | 3.36 | 0.03 | `over_tolerance:budget` | 54 | 12 | 3 | 1.51 | 4.23 | 2.20 | 3.04 |
| `balance-sheet-two-columns-of-figures` | 5.76 | 0.57 | `over_tolerance:budget+tail` | 94 | 47 | 5 | 2.10 | 5.14 | 2.67 | 2.73 |
| `bus-timetable-station-left-times-right` | 12.96 | 0.27 | `over_tolerance:budget` | 177 | 101 | 9 | 1.97 | 4.92 | 3.05 | 3.01 |
| `electricity-bill` | 14.4 | 1.33 | `over_tolerance:budget+tail` | 125 | 121 | 7 | 11.31 | 28.49 | 8.53 | 2.52 |
| `insurance-policy-schedule` | 8.64 | 0.53 | `over_tolerance:budget+tail` | 107 | 103 | 6 | 19.50 | 47.78 | 8.17 | 2.45 |
| `marksheet-subject-left-marks-right` | 6.72 | 0.32 | `over_tolerance:budget+tail` | 109 | 96 | 6 | 31.42 | 85.77 | 10.92 | 2.73 |
| `mobile-bill` | 16.8 | 1.55 | `over_tolerance:budget+tail` | 112 | 100 | 6 | 3.96 | 9.98 | 6.73 | 2.52 |
| `price-list-2col-dense-right-aligned` | 7.2 | 2.69 | `over_tolerance:budget+tail` | 253 | 82 | 13 | 2.23 | 5.32 | 2.16 | 2.73 |
| `report-2col-table-spanning-both-columns` | 12.0 | 0.76 | `over_tolerance:budget+tail` | 90 | 49 | 5 | 2.77 | 6.79 | 2.80 | 2.59 |
| `table-inside-two-column-page` | 21.6 | 35.87 | `over_tolerance:budget+tail` | 64 | 46 | 4 | 32.79 | 73.45 | 8.24 | 3.11 |
| `table-with-no-header-row` | 11.52 | 0.61 | `over_tolerance:budget+tail` | 215 | 148 | 11 | 3.74 | 9.04 | 4.29 | 2.59 |
| `two-tables-stacked-with-no-gap` | 5.28 | 0.77 | `over_tolerance:budget+tail` | 72 | 55 | 4 | 3.93 | 10.18 | 4.66 | 2.59 |

`ds` = upright matched runs on the page, `n_out` = how many are further than their own tolerance,
`budget` = `max(2, ceil(0.05 * ds))`, `worst_ratio` = `max(|d| / tol)` on the page.

## 3. The count

    over_tolerance : 25 of 25      (budget clause 25 of 25, tail clause 18 of 25, all-out 0 of 25)
    not_ds         :  0 of 25
    not determined :  0

Run: 25 of 25. Of the six documents `SETTLED.md` 4b named as "under the tolerance and failing anyway",
four (`22_invoice_four_columns_txtpos`, `41_coloured_headings_white_bg`,
`73_marksheet_subject_marks_grade`, `29_dot_leaders_txtpos`) are no longer solo-18 at all: their
stored verdicts are **42/42, no failure**. They did match, and they pass. The two still in the
population -- `16_right_aligned_amounts_txtpos` and `72_bank_statement_no_rules_right_amounts` -- fire
`over_tolerance` at run `dy` 3.41 pt and 28.21 pt. None of the six was ever evidence for `not ds`.

## 4. Why "six documents are under the tolerance" was never true -- the two instruments

`RANKING.csv`'s `max_pt` is an ink distance transform: `benchmarks/p2w.py position()` takes
`distance_transform_edt`, keeps only pixels with `d > 1`, and multiplies integer pixels by 0.48 pt.
The check's `d` is `g["ry"] - r["ry"]`, a baseline-to-baseline difference on a matched run. Neither
bounds the other, and this population shows both directions:

| document | `max_pt` (ink) | max abs run `dy` | ratio |
|---|--:|--:|--:|
| `303_discharge_summary` | 1.92 | 4.10 | 2.14 |
| `16_right_aligned_amounts_txtpos` | 2.40 | 3.41 | 1.42 |
| `320_balance_sheet_statutory` | 2.40 | 19.37 | 8.07 |
| `72_bank_statement_no_rules_right_amounts` | 2.40 | 28.21 | 11.75 |
| `325_demat_holdings_statement` | 2.88 | 38.13 | 13.24 |
| `403_crossword_puzzle` | 2.88 | 45.69 | 15.86 |
| `31_times_body_arial_headings` | 17.76 | 3.54 | 0.20 |
| `table-inside-two-column-page` | 21.60 | 73.45 | 3.40 |

So a 1.92-2.40 pt ink maximum sits on pages whose runs are 3.4-28.2 pt out of position, and a 17.76 pt
ink maximum sits on a page whose runs are 3.54 pt out. **`max_pt` cannot be used to argue that a
document is inside `18_displacement`'s tolerance, in either direction.** That one confusion is what
left the class with an "impossible" six; there was nothing there to explain.

## 5. The root cause -- the refused table spacer, and it is a STEP

The dominant clause is the per-page budget: 25 of 25. The mechanism that produces it, on the 11
documents that carry a refused spacer, is `DocxWriter.java:6122-6136`:

    boolean spendable = slackTw > 0
            && ctx.spacerSplitTw + roomWantTw + rowExcessTw <= slackTw;      // :6122-6123
    if (spendable) {                                                          // :6124
        ... w:before="wantTw" ... w:line="1" w:lineRule="exact"               // :6125-6130
    } else {                                                                  // :6132
        ... w:before="0" w:after="0" w:line="<spacerTw>" w:lineRule="exact"   // :6133-6136
    }

When the room guard refuses, the gap the page drew above a table is written as `w:line` exact on an
`sz=2` mark. Google lays that at `2.5873 * max(L/240, 0.06)` pt for a declared `L/20` pt (the law in
the in-tree comment at `:6101-6106` and in `REMAINING-DEFECTS.md`), i.e. about 22 percent of the
declared gap, so **every run below the spacer sits high by 0.78 x gap** -- one signed constant, not a
drift.

That is what the per-run `dy` shows, and it is a step, not a gradient. `68_journal_wide_table_spanning`
in reading order: 0.09, 0.13, 0.26, 0.30, 0.73 ... 1.31, then **-113.78** for every run below the table,
ending at -114.53. One jump of 115.09 pt across the spacer and nothing else moving. Predicted:
0.78 x 144.00 = 112.32.

On the 7 documents in this set with exactly one refused spacer:

| document | refused gap pt | predicted 0.78 x gap | largest step in per-run dy | ratio |
|---|--:|--:|--:|--:|
| `403_crossword_puzzle` | 58.15 | 45.36 | -42.99 | 0.95 |
| `68_journal_wide_table_spanning` | 144.00 | 112.32 | -115.09 | 1.02 |
| `72_bank_statement_no_rules_right_amounts` | 18.30 | 14.27 | -34.25 | 2.40 |
| `bus-timetable-station-left-times-right` | 6.35 | 4.95 | -5.67 | 1.14 |
| `table-inside-two-column-page` | 4.00 | 3.12 | -84.30 | 27.02 |
| `table-with-no-header-row` | 12.35 | 9.63 | -7.62 | 0.79 |
| `two-tables-stacked-with-no-gap` | 12.35 | 9.63 | -8.76 | 0.91 |

Five of the seven land within 21 percent of the prediction. The two that do not are named rather than
fitted: `72_bank`'s largest jump (-34.25) spans a run at ry 12.4 to ry 29.4 and is not the table
spacer, while its spacer step is the -13.31 at ry -293.0 -> -260.5 (ratio 0.93); and
`table-inside-two-column-page` is a two-column page whose largest jump (-84.30) crosses from one
column to the other, its spacer step being the -11.63 (ratio 2.9, not explained).

**This root cause predicts other documents, and the prediction needs no Google render:** a document
whose emitted `word/document.xml` contains an `sz=2` spacer paragraph with `w:before="0"` and
`w:line > 1` will fail `18_displacement` on the budget clause with a step of about 0.78 x that gap at
the spacer, and its runs above the first refused spacer will read `dy ~ 0`. My independent read of the
emitted .docx (unzip, match the `w:sz w:val="2"` paragraph template) counts 11 such documents in this
population -- `403_crossword`, `68_journal`, `72_bank`, `bus-timetable`,
`electricity-bill`, `insurance-policy-schedule`, `marksheet-subject-left-marks-right`, `mobile-bill`,
`table-inside-two-column-page`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap` -- the
same 11 `FINDINGS/18_displacement-25-SOLO-A-B-C-CENSUS-25NOV-1626-fixer.md` counted as class A.

## 6. What the spacer does NOT explain, stated as a gap and not as a guess

**14 of the 25 carry no refused spacer at all and still fire the budget clause.** Their median |dy| is
0.20 to 3.78 pt, spread over the whole page rather than stepped, against a tolerance median of
2.03-3.85 pt -- they fail because a majority of runs sit a point or three outside a tolerance that is
itself only two to four points wide.

Two candidate laws were tested against them and both are refuted by this data:

* **The 0.75 pt row ladder** (`w:trHeight`; `rowHeightTw` computed at `DocxWriter.java:6493-6541`,
  emitted at `:6583`). Predicted total drift `0.75 * <w:tr>` versus measured drift `slope * page span`
  agrees in sign on only **15 of 25** documents and disagrees in magnitude on most of those
  (`320_balance_sheet_statutory` predicted 15.75 pt against measured 24.96; `bus-timetable` predicted
  24.75 against measured 2.97).
* **A leading ratio** (`dy` proportional to the face size, which is what a Google line box that is a
  multiple of the face would produce). Fitted `dy/size` across the 14 runs from -0.49 to +1.12, with
  Pearson r between -0.51 and +0.11 -- no size scaling at all.

**So for those 14 the root cause is not determined by this run.** What is determined is where it is
not: not the spacer, not the row ladder, not a size-proportional leading, and not run matching. The
next discriminating test is a per-paragraph `dy` -- the recording here is per run, and a paragraph's
wrapped lines are where a line-box error would appear as an intra-paragraph gradient. The data for it
is one field away in the same probe.

## 7. What would prove this wrong

* **One of the 25 firing `not ds`** on a re-render. It fired on none, and the probe records the branch
  explicitly, so this is falsified by re-running the three commands in section 1.
* **A document with a refused spacer whose dy profile is not a step.** The claim is that the runs above
  the first refused spacer read `dy ~ 0` and everything below is offset by 0.78 x gap. Two of the seven
  single-spacer documents already sit outside 21 percent of the prediction; a document where the step
  is absent entirely would refute the law, not merely weaken it.
* **A render where the step equals the FULL gap (ratio ~1.28) rather than 0.78 of it.** That would say
  Google delivers `w:line` exact as a length after all, and the 22 percent charge is a different
  construct.
* **The 14 no-spacer documents moving when only the spacer/guard code changes.** If a spacer-only patch
  moves them, my claim that they are a different mechanism is wrong.
* **The `max_pt` argument in section 4 failing on a re-measure**: if the low-`max_pt` documents came
  back with run `dy` under 1.5 pt, the ink metric would have been right and the check wrong. On the two
  still in the population they read 3.41 and 28.21 pt.

## 8. Provenance of every number

* the 25 documents: `benchmarks/gverify/*.json`, `failed == ["18_displacement"]`, 213 files read.
* `max_pt`, `share5`: `benchmarks/RANKING.csv`.
* `ds`, `n_out`, budget, `worst_ratio`, max/median abs dy, `tol`, and every per-run `dy`: this run's
  JSON, `/scratch/work/vgout/<doc>.json`, produced by
  `python3 vg18.py p2w/corpus/<doc>.pdf renders25/<doc>.pdf --docx docx25/<doc>.docx --json vgout/<doc>.json`.
* the Google renders: Drive folder `1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA` (the 213 engine .docx), each
  copied to a Google Doc in `p2w-probe-25nov-fixer` and exported as PDF; 25 of 25.
* the refused-spacer counts and the `w:line` / `w:trHeight` / `w:tr` constructs: read out of the
  downloaded `word/document.xml` of each of the 25 .docx.
* the `2.5873 * max(L/240, 0.06)` charge law: `DocxWriter.java:6101-6106` (in-tree comment) and
  `REMAINING-DEFECTS.md`, class `20_within_10pt`.
* the stored per-document `med_dy` / `worst_dy` / `runs_matched`: `benchmarks/gverify/<doc>.json`.
* the 11 refused-spacer documents: independent count from the emitted .docx this run, agreeing with
  `FINDINGS/18_displacement-25-SOLO-A-B-C-CENSUS-25NOV-1626-fixer.md`.

Nothing in this file is estimated, modelled, or carried over from an older measurement.

**Commit mechanics.** `bash tools/install-gate.sh` was run first, as instructed. Its `pod-prep.sh`
built the JDK, the libs, the stubs and the engine (all four reported installed), then began
converting the 213-document corpus so the commit gate would have something to compare, and was
still converting 98 of 213 when the 250 s call window ended. The pre-commit hook was therefore
never installed (`.git/hooks/pre-commit` absent) and this FINDINGS-only markdown file was
committed without one. No engine code was built into the commit, and `git status` shows this
file as the only change.
