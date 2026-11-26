# The `table-row` attribution predicts nothing in Google, and the solo constant is not one number

**26 Nov 2026, relay slot 14:18.** No engine change. Two refutations, measured on the 207 committed
Google results and cross-checked against the `.docx` files themselves.

## Why this was worth a run

`benchmarks/DISP-TABLE.csv` labels 75 of 213 documents `attribution=table-row`, and its column
`google_per_row_growth_pt` is **empty for every row**. The label has been carried since the table was
built and nothing has ever tested it against a Google render. If per-row growth were real it would be
the single biggest lever in the corpus — 75 documents, and 50 of the 113 `18_displacement` failers sit
in that label. The `DOCGRID` finding of the 10:54 slot also left one question open: is the residual a
single page-level constant? Both questions are answerable from committed data, with no Drive calls.

## What was measured

For each of the 207 documents with a Google result, `med_dy` / `worst_dy` / `bad_pages` from
`benchmarks/gverify/*.json` were joined to `docx_table_rows`, `attribution` and `src_pages` from
`DISP-TABLE.csv`.

**1. Row count does not predict displacement.**

| fit | n | result | r² |
|:--|--:|:--|--:|
| `med_dy = a + b*rows` (table-row docs) | 72 | `0.18 − 0.108*rows` | **0.00** |
| `worst_dy = a + b*rows` (table-row docs) | 72 | `16.22 + 0.518*rows` | **0.01** |
| `worst_dy = a + b*pages` (all 113 failers) | 113 | `48.19 + 0.196*pages` | **0.00** |

The `med_dy` slope is **negative**. Nine rows or nineteen, the median vertical displacement is the
same. The `google_per_row_growth_pt` column is empty because there is no per-row growth to put in it.

**2. `18_displacement`'s 113 failers are two different defects, not one.**

| family | rule | n | worst_dy median |
|:--|:--|--:|--:|
| systematic | `abs(med_dy) >= 1.5` | **82** | 11.1 pt |
| outlier | `abs(med_dy) < 1.5` | **31** | 5.0 pt |

The 31 outlier documents are *not* shifted; a few runs are far out — the check's third clause ("no
single upright run more than twice its own tolerance out"), not its first. Working them as a shift
would be working the wrong clause. The 82 systematic documents have a median `med_dy` of 1.9 pt and a
sign split of **46 positive / 36 negative**.

**3. The page-level constant is not one number.** The 23 documents that fail `18_displacement` and
nothing else carry `med_dy` = −10.2, −7.2, −6.3, −6.0, −2.8, −2.3, −1.6, −0.5, −0.2, 1.1, 1.1, 1.4,
1.7, 1.7, 1.8, 2.1, 2.2, 2.6, 2.8, 3.0, 3.8, 8.0, 8.2 — **sd 4.37, range 18.4 pt, both signs**. A
term that is one number corpus-wide would cluster; this does not cluster.

## The independent check on the join itself

The row counts above come from `DISP-TABLE.csv`, and a wrong column would fake a zero correlation. So
the count was re-derived from the `.docx` files — `<w:tr>` occurrences in `word/document.xml` for each
of the 76 documents converted on this pod — and compared with the table's `docx_table_rows`:
**76 agree, 0 disagree.** The column is right; the zero correlation is real.

## What is now true, and what it forbids

1. **Do not build on `attribution=table-row`.** It is not a cause, and a fix aimed at row height,
   `trHeight` or cell margins cannot be justified by it. The construct it names is refuted in the
   renderer the user opens. (It may still be true in LibreOffice — `lo_per_row_growth_pt` is 0.15–0.33
   and is a real measurement of the proxy. That is precisely why the proxy misleads.)
2. **Do not look for one page-origin constant.** The 23 solo documents span 18.4 pt in both
   directions. The next run should stop pairing page origins looking for a single number; if it pairs
   them at all it must do so per document and expect a different answer each time.
3. **Split the class before working it.** 82 systematic and 31 outlier are different clauses of the
   same check. A run that measures a shift on an outlier document will see nothing move and correctly
   but uselessly abandon the hypothesis.
4. The largest surviving family is the **82 systematic** documents; `18_displacement` is worth 51.9
   CLEAN documents, so this split is where that value has to be earned — one document at a time, on
   evidence, not on a label.

## What does grow: the tail, with document length

Same 113 failers, against `runs_matched` (the number of runs the check paired, i.e. how much text the
document holds):

| fit | n | result | r² |
|:--|--:|:--|--:|
| `worst_dy = a + b*runs_matched` | 113 | `13.55 + 0.287*runs` | **0.31** |
| `med_dy = a + b*runs_matched` | 113 | `−1.59 − 0.027*runs` | 0.05 |

By quartile of `runs_matched`: 7–49 runs → worst_dy median 6.9 pt; 50–74 → 8.6; 74–113 → 8.1;
**114–1496 → 28.8 pt**, while `med_dy` stays between −0.5 and +2.2 in every quartile.

So the displacement is **in the tail and it accumulates with document length**, while the median line
does not move at all. That is the signature of the check's third clause (a few runs far out), not of a
layout shift — and it is the opposite of what every "correct the page constant" attempt has assumed.
A fix that shifts every line will move the median, which is already right, and leave `worst_dy` where
it is. The lever is the runs at the tail: the ones the check pairs last and furthest.

## Falsifier for the next run

If a per-row construct is still believed in, it must first show a **positive** `med_dy` slope against
row count on a Google export of at least ten documents. This run's fit says that slope is −0.108 ± a
standard error large enough for r² = 0.00; a real accumulator would give r² well above 0.3.

Reproduce with `/scratch/work/an18.py` (reads `benchmarks/gverify/*.json` + `benchmarks/DISP-TABLE.csv`;
writes nothing).

## The tail has a size, and the size sorts the class

`worst_dy` is in points, and a page is about 792 pt. Splitting the 113 failers by the size of their
worst run:

| family | rule | n | median runs_matched | median med_dy |
|:--|:--|--:|--:|--:|
| page-scale | `worst_dy > 100` | **17** | 121 | −7.4 pt |
| block-scale | `9 < worst_dy <= 100` | **38** | — | — |
| line-scale | `worst_dy <= 9` | **58** | 71 | — |

The page-scale 17 are long multipage documents and **not one of them fails `00_page_count`**: the page
count is right, but a run on a later page is a tenth to eight-tenths of a page away from where the
source puts it. That is a page-break landing in the wrong place inside a correct page count, and it is
measured in pages, not in the points every existing displacement attempt has been chasing. The worst
of them: `very-long-single-column-table` 656.7 pt, `table-across-page-break-repeated-header` 401.3,
`324_loan_amortisation_schedule` 357.8, `bank-statement-5-pages` 355.4.

The line-scale 58 are the only ones a line-box construct can reach at all, and they are the ones whose
median run is *not* moving. Work order this implies: the 58 line-scale documents are where a line
construct is testable; the 17 page-scale documents need a page-break construct and no line-box change
will touch them.

## The line-scale family: a small, weakly size-proportional charge

Third measurement, same run. For the 27 line-scale documents (`worst_dy <= 9`) that also have a
`.docx` on this pod, the median font size was read from `word/document.xml` (`w:sz`, half-points) and
fitted against `med_dy`:

    med_dy = -5.17 + 0.765 * size_pt     n = 27, r2 = 0.20

The slope is positive and of the order the hairline theory predicts (a charge proportional to size),
but it explains a fifth of the variance, and the whole family sits between -3.1 and +4.2 pt with a
median near 1.2 pt — inside or near `clamp(0.35*size, 1.5, 4.5)`. So this family fails on its tail
runs, not on its median, exactly like the 31 "outlier" documents above, and a size-proportional
correction is **not** established by this fit: r² = 0.20 is not enough to justify a construct. What
would settle it: the same fit on at least 60 line-scale documents with a size range that does not
cluster at 7–9 pt (this pod had 6.8–11.0 pt, mostly 8).
