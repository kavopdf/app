# `ROW_RUNG_UNDER_TW = 0` is refuted as a corpus fix: 4 documents better, 63 worse

**28 Nov 2026, relay slot 00:18.** Fixer run. Class attempted: `63_table_rows`.

The 27 Nov 23:17 run proved `ROW_RUNG_UNDER_TW` (`DocxWriter.java:54`) is the cause of the four named
table documents and wrote "the next run must measure the full corpus". This run measured it. **The
full-corpus measurement refutes the change as a fix**, by the falsifier that run itself wrote:

> "If any document is worse than its `RANKING.csv` row, the rung was not the only cause and this file
> is wrong - that is the falsifier."

63 documents are worse. The change was reverted; nothing was committed to the engine.

---

## What was measured

Engine `b648594972a7682b` (the tree with `ROW_RUNG_UNDER_TW = 0` and nothing else changed), corpus
converted 214 of 214 (`corpus-slice.py`, 0 failed), then measured document by document
(`gate.py`, 213 scored), then compared row by row against the committed table at HEAD.

| | documents |
|:--|--:|
| better than the committed table (share@5 down) | **4** |
| worse than the committed table (share@5 up) | **63** |
| unchanged | 146 |

The four the 27 Nov run predicted, reproduced on this pod, this JDK, this build, one document per JVM,
converted fresh for this run:

| document | published row | rung = 10 | rung = 0 (this run) |
|:--|--:|--:|--:|
| `table-with-no-header-row` | 0.61 | 47.48 | **0.61** (share1 18.47, median 0.96, max 11.52) |
| `boq-tender-bill-of-quantities` | 0.62 | - | **0.62** (11.46 / 0.96 / 12.96) |
| `mobile-bill` | 1.55 | - | **1.55** (43.87 / 1.44 / 16.80) |
| `electricity-bill` | 1.33 | - | **1.33** (46.85 / 0.96 / 14.40) |

Every value digit for digit. **The prediction about those four documents is confirmed.** It is the
generalisation to the corpus that is false.

The worst of the 63, and the first one verified independently:

| document | committed | rung = 0 |
|:--|--:|--:|
| `price-list-2col-dense-right-aligned` | 2.69 | **27.89** |
| `75_merged_header_cell_three_columns` | 7.62 | 26.77 |
| `03_stamp_vertical_90deg` | 16.98 | 34.38 |
| `360_restaurant_menu` | 34.43 | 50.18 |
| `bus-timetable-station-left-times-right` | 0.27 | 11.40 |
| `price-list-right-aligned-amounts` | 1.79 | 12.37 |
| `73_marksheet_subject_marks_grade` | 0.00 | 7.95 |
| `79_inr_indian_digit_grouping_table` | 0.74 | 7.77 |
| `35_four_typefaces_one_page` | 2.19 | 9.10 |
| `06_rect_paid_stamp_red_transparent` | 0.00 | 6.90 |

**Independent check, not the tool being blamed:** `price-list-2col-dense-right-aligned` was converted
again on its own (`ConvertAll` on a one-file shard) and scored with `p2w.measure_doc`, and returned
share1 63.97 / share5 **27.89** / median 2.40 / max 8.64 - the same 27.89 the table carries. The
regression is in the render, not in the table.

The measured table this run produced is kept beside this file as
`RANKING-rung0-FULL-CORPUS-28NOV.csv` (213 rows) so the next run can re-derive the 63 without paying
the hour it cost here.

## Why the "one constant" reading is wrong

The rung is a **per-row** subtraction of 10 twips from `w:trHeight`, gated on `footRoom`
(`DocxWriter.java:6591-6601`). Its effect on a document is therefore a function of that document's own
table: how many rows, what pitch, and how much room each row's text leaves below its baseline.

* On a **long ruled table** where the source pitch is exactly the page pitch, the accumulated ramp is
  pure error: 26 rows x 0.5 pt = 13 pt at the foot. Removing it restores the document
  (`table-with-no-header-row` 47.48 -> 0.61).
* On a **dense two-column price list** the rows are shorter than the pitch, `footRoom` passes on most
  rows, and the declared 10-tw shortfall is what keeps each row's ink inside its own band. Remove it
  and every row is laid 0.5 pt low and accumulates; the ink crosses the row rules
  (`price-list-2col-dense-right-aligned` 2.69 -> 27.89).

So the rung is not a defect constant to delete. It is a **global approximation of a per-row quantity**
- the difference between the source pitch and the room a row's own text needs - and the correct fix is
to compute that quantity per row, not to move the constant. That is a different and larger change than
a one-line edit, and it is the shape the next run should build.

## The two other candidates, ruled out by this run's numbers

* **The spacer fraction is not the whole story either.** `SPACER_SPEND_FRAC` was left at 0.70 in every
  measurement here. The 63 regressions appear with it untouched, so they are the rung's, not the
  fraction's - and the 4 wins appear with it untouched too, so the fraction does not carry the
  published values on those four either.
* **The committed table at HEAD is not stale.** Every one of the 63 is a document whose HEAD row the
  rung=0 engine fails to match, and one of them was re-derived independently. The comparison is
  therefore against a real target, not against a table measured on another engine.

## What this run did not settle

* **Which of the 63 also carry other open classes**, and so whether a per-row rung could ever make
  them CLEAN rather than merely better. That is the question before any build: `classpick.py
  --leverage` plus the docx class table.
* **The Google side.** Nothing here was exported through Drive. The rung bought `mobile-bill` and
  `electricity-bill` one `18_displacement` check each per the `8fb4f503` message; rung=0 restores their
  published `share5` but that check was not re-run, so the trade on Google is still unmeasured.

## Pod facts worth not paying again

* The pod was **warm** this run: JDK at `/scratch/work/.p2w-jdk/jdk`, jars in
  `tools/engine-verify/libs`, corpus 214 PDFs, engine compiled. `pod-prep.sh` skipped 1-7 and went
  straight to the corpus slice.
* `install-gate.sh` runs `pod-prep.sh`, which converts the corpus in a 240 s slice - so on a cold pod
  the install call alone exceeds one 290 s sandbox call. Run `pod-prep.sh` on its own, repeatedly,
  until it says DONE.
* A full corpus pass costs **5 slices of conversion (~15 min)** and **7 slices of measurement
  (~28 min)** at 213 documents. Budget the whole slot for one full-corpus answer.
* `gate.py --budget N` spends the whole N seconds even when nothing is left to measure, and then the
  later layers run past the 290 s call limit and the call is killed before it writes STATE. Pass a
  **small budget (60)** when the measurement is already complete; that is what published the table.
