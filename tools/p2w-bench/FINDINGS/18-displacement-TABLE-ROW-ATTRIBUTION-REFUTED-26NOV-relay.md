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
