# 18_displacement: the row-count lead was refuted on stale data - it is live again

Written 26 Nov 2026, slot 15:24. Engine a4d8fca469bba636.

## The claim this run had to check

The 15:12 run closed with: *"`attribution=table-row` is not a cause in Google ... worst displacement has a
slope of 0.518 pt/row at r² = 0.01. Do not write a row-height, `trHeight` or cell-margin patch on the
strength of that label."*

That sentence told the next run not to touch rows. It does not reproduce.

## What I measured

Two independent sources, both committed, no Drive call.

```
benchmarks/gverify/<doc>.json   ->  displacement.worst_dy, displacement.med_dy, failed[]
benchmarks/DISP-TABLE.csv       ->  docx_table_rows, src_pages, declared_row_pt, ...
```

Join on document name, n = 207 documents that carry a displacement block.

```
worst_dy ~ docx_table_rows,  n=207   slope 2.188 pt/row   r² 0.423
worst_dy ~ docx_table_rows,  n=113 (the documents that fail 18_displacement)
                                     slope 2.092 pt/row   r² 0.377
DISP-TABLE's own google_worst_dy_pt column, n=130
                                     slope 4.088 pt/row   r² 0.455
```

Reproduced by hand in this run (`python3` over the two files, no tool of ours in the loop):

```
worst_dy ~ docx_table_rows: ['2.188', '5.166', '0.423', 207]
```

So table-row count is, after `src_pages`, the strongest single predictor of worst displacement in this
corpus. The 0.518 / 0.01 figure does not appear in any subset I could construct.

## Why the last run's number is not the data's number

`benchmarks/DISP-TABLE.csv` carries a Google column that no longer matches `benchmarks/gverify/`:

```
worst_dy compared      130
disagree > 0.5 pt       32
max disagreement        96.70 pt
google_fail_18 flags compared 213, disagree 20
```

The CSV is a stale measurement; `gverify/` is the source of truth (it is the only source that reproduces
113 of 207 failing `18_displacement`). A slope fitted on the stale column, or on a join that mixes the two,
is a number about an engine that no longer exists. **Rule for the next run: displacement numbers come from
`benchmarks/gverify/*.json`, never from `DISP-TABLE.csv`'s `google_*` columns. `DISP-TABLE.csv` is good for
structural columns only (`docx_table_rows`, `src_pages`, `declared_row_pt`, `spacer_paragraphs`,
`unspent_spacer`), which have no competing source.**

## The mechanism is not the one that was proposed, and `fitreserve` is not the lever

The 15:12 run proposed that the writer leaves ~25 pt of slack per sheet, row growth eats it, and the
renderer breaks before the writer's explicit break.

Tested here on the eight largest-displacement documents that have both many rows and several pages
(`docx_table_rows >= 20`, `src_pages >= 2`), by converting each one twice - `ConvertOne` at the default
`p2w.fitreserve` (96 twips) and at 300 twips, the value the code's own comment says is measured for
`bank-statement-5-pages`:

| document | worst_dy | rows | pages | `document.xml` differs? |
|:--|--:|--:|--:|:--|
| very-long-single-column-table | 656.7 | 99 | 3 | no |
| table-across-page-break-repeated-header | 401.3 | 45 | 3 | no |
| 324_loan_amortisation_schedule | 357.8 | 246 | 7 | no |
| bank-statement-5-pages | 355.4 | 125 | 5 | no |
| gst-invoice-multipage-item-table | 168.3 | 42 | 4 | no |
| form16-part-b | 155.6 | 31 | 2 | no |
| mutual-fund-statement | 121.6 | 31 | 2 | no |
| balance-sheet-and-profit-loss | 70.0 | 47 | 2 | no |

Byte-identical in all eight, page breaks and `w:line` totals unchanged. **The fit reserve never fires on
these documents**, because it is only paid by a page whose flow comes within `pageBudgetTw - 96` - and the
model believes these pages have room to spare. Raising it to 300, or to anything else, cannot move them.

That refutes the "the sheet is nearly full and the reserve is too small" version of the row-growth story,
and it is worth more than the byte comparison suggests: **the model's own accounting says these pages fit
comfortably while Google displaces their content by 100-350 pt.** Any patch that starts from "the page is
slightly over" is aiming at a state the writer never produces here.

## What the next run should do

1. Do **not** re-refute row count. It is a real signal: 2.19 pt of worst displacement per table row,
   r² = 0.42, over 207 documents.
2. Do **not** sweep `p2w.fitreserve` on this family. Measured inert on the eight worst, byte for byte.
3. The open question is now sharper: the per-row excess used by the engine's spacer guard is
   `rowExcessTw = 15 * pageRuledRowCount` (0.75 pt/row, DocxWriter.java:6151, "the quantum the 22 Nov
   sweep measured"). The displacement slope says the *rendered* excess is ~2.2 pt/row - about three times
   that constant. Either the constant is wrong, or something else scales with row count. Distinguish them
   on one document: take `324_loan_amortisation_schedule` (246 rows) and measure, in Google, the rendered
   height of one ruled row against its `w:trHeight` declaration. That is a single probe document and it
   decides between the two.
4. `median_font_size_pt` is in no committed file. The 15:12 regression on it cannot be re-checked by any
   later run; treat it as unverified.

## Cost note

The pod was cold. `install-gate.sh` was killed at 300 s; the prerequisites were already present (a
timed-out earlier pass had built the JDK, jars, AAR, stubs and engine), and the corpus needed three
`pod-prep.sh` slices (53 + 53 + 17 documents, 224 s + 186 s + 88 s) before `regress.py --check` passed.
Total cold-pod cost this run: ~28 minutes of the slot.
