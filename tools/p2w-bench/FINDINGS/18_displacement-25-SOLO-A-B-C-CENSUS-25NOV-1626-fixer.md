# The 25 solo `18_displacement` documents are three constructs — A 11 / B 10 / C 4 — and only A can be reached by the spacer guard

**25 Nov 2026, fixer slot 16:26 IST. No engine change landed; this is a measurement.**

What I believed: `pending.py` item 1 said "25 documents fail ONLY `18_displacement` and nothing else, so any
patch making 18 pass makes the document CLEAN", and `FINDINGS/18_displacement-14-SOLO-IS-THREE-CONSTRUCTS-CENSUS-25NOV.md`
had split the then-14 solo documents into A (refused table spacer), B (spacer already spent) and C (no table).
The population has since doubled, 14 → 25, and nobody had re-run the split on the 25.

What I measured: the split, on the `.docx` the current engine actually writes.

    engine   981ff1fa35e2cf67   (corpus rebuilt from scratch this run: corpus-slice.py, 213 of 213, stamp written)
    method   unzip each of the 25 .docx and match the engine's exact spacer paragraph template
             `<w:p><w:pPr><w:snapToGrid w:val="0"/><w:spacing w:beforeAutospacing="0"
              w:afterAutospacing="0" w:before="B" w:after="0" w:line="L" w:lineRule="exact"/>
              <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>`
             refused = B == 0 and L > 1 (the guard's `else` branch, DocxWriter.java:6132)
             spent   = B > 0        (the guard's `if (spendable)` branch, DocxWriter.java:6125)
    dy       med_dy / worst_dy / runs read from benchmarks/gverify/*.json, `checks.18_displacement.detail`

## The census

| cls | document | spacer paras | refused | spent | refused gap pt | med_dy | worst_dy | runs |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| A | `403_crossword_puzzle` | 1 | 1 | 0 | 58.15 | -43.6 | 45.7 | 27 |
| A | `68_journal_wide_table_spanning` | 1 | 1 | 0 | 144.00 | -114.3 | 115.0 | 74 |
| A | `72_bank_statement_no_rules_right_amounts` | 1 | 1 | 0 | 18.30 | -13.0 | 28.2 | 80 |
| A | `bus-timetable-station-left-times-right` | 1 | 1 | 0 | 6.35 | -3.0 | 4.9 | 177 |
| A | `electricity-bill` | 3 | 3 | 0 | 26.20 | -8.5 | 28.5 | 125 |
| A | `insurance-policy-schedule` | 3 | 3 | 0 | 26.80 | -7.7 | 47.8 | 107 |
| A | `marksheet-subject-left-marks-right` | 5 | 2 | 1 | 36.30 | -10.9 | 85.8 | 109 |
| A | `mobile-bill` | 3 | 3 | 0 | 25.00 | -6.7 | 10.0 | 112 |
| A | `table-inside-two-column-page` | 1 | 1 | 0 | 4.00 | +8.0 | 73.5 | 64 |
| A | `table-with-no-header-row` | 1 | 1 | 0 | 12.35 | -0.5 | 9.0 | 215 |
| A | `two-tables-stacked-with-no-gap` | 1 | 1 | 0 | 12.35 | -4.7 | 10.2 | 72 |
| B | `16_right_aligned_amounts_txtpos` | 1 | 0 | 1 | 0.00 | -1.6 | 3.4 | 64 |
| B | `303_discharge_summary` | 1 | 0 | 1 | 0.00 | -0.2 | 4.1 | 45 |
| B | `320_balance_sheet_statutory` | 2 | 0 | 2 | 0.00 | +8.2 | 19.4 | 73 |
| B | `325_demat_holdings_statement` | 2 | 0 | 2 | 0.00 | +3.8 | 38.1 | 84 |
| B | `362_price_list_dense` | 1 | 0 | 1 | 0.00 | -2.8 | 5.4 | 257 |
| B | `36_embedded_subset_font` | 1 | 0 | 1 | 0.00 | +1.7 | 3.5 | 29 |
| B | `402_calendar_month_grid` | 1 | 0 | 1 | 0.00 | +1.4 | 6.5 | 46 |
| B | `74_balance_sheet_indented_subitems` | 2 | 0 | 2 | 0.00 | +2.2 | 4.2 | 54 |
| B | `balance-sheet-two-columns-of-figures` | 2 | 0 | 1 | 0.00 | -2.3 | 5.1 | 94 |
| B | `report-2col-table-spanning-both-columns` | 1 | 0 | 1 | 0.00 | +2.8 | 6.8 | 90 |
| C | `31_times_body_arial_headings` | 0 | 0 | 0 | 0.00 | +2.6 | 3.5 | 29 |
| C | `70_magazine_drop_cap_photo_caption` | 0 | 0 | 0 | 0.00 | +3.0 | 3.3 | 24 |
| C | `71_invoice_space_aligned_no_rules` | 0 | 0 | 0 | 0.00 | +1.1 | 6.7 | 72 |
| C | `price-list-2col-dense-right-aligned` | 0 | 0 | 0 | 0.00 | +2.1 | 5.3 | 253 |

## It reproduces the 14-document census exactly

The earlier census's 7 refused (`68_journal`, `72_bank`, `bus-timetable`, `insurance-policy-schedule`,
`mobile-bill`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap`) are all in my A; its 5 spent
(`16_right_aligned`, `303_discharge_summary`, `36_embedded_subset_font`, `74_balance_sheet`,
`balance-sheet-two-columns`) are all in my B; its 2 with no table (`31_times`, `71_invoice`) are in my C.
Two independent readings of the same construct agree. The 11 documents that joined the solo set since
land as: 4 in A (`403_crossword_puzzle`, `electricity-bill`, `marksheet-subject-left-marks-right`,
`table-inside-two-column-page`), 5 in B (`320_balance_sheet_statutory`, `325_demat_holdings_statement`,
`362_price_list_dense`, `402_calendar_month_grid`, `report-2col-table-spanning-both-columns`) and 2 in C
(`70_magazine_drop_cap_photo_caption`, `price-list-2col-dense-right-aligned`).

## What this changes about the prize

`classpick.py --leverage` prices `18_displacement` as one class. It is three, and they need three different
fixes:

* **A, 11 documents.** The guard refused the spacer, so the gap the page drew is written as `w:line` exact,
  which Google delivers at roughly a fifth. This is the only group a spacer/guard/row-height change reaches.
* **B, 10 documents.** The spacer is already spent and the document still fails. **No spacer patch can fix
  these** — they are flow, row height or leading *below* the table. Any attempt that only makes the guard
  spend more leaves all 10 exactly where they are.
* **C, 4 documents.** There is no spacer paragraph at all. Their `med_dy` is small and **positive** (+1.1 to
  +3.0 pt, i.e. the render sits *below* the source on every one) with `worst_dy` 3.3–6.7 — a systematic small
  downward bias, not a gap. The earlier census recorded -2.87 pt on `31_times`; at this engine it reads +2.6,
  so that constant has moved and the sign has flipped since it was recorded. **Do not build on the -2.87.**

## The arithmetic that says A is not simply "spend the gap"

If spending a refused gap moved the page down by that gap, `refused gap pt` would equal `|med_dy|`. It does
not: it is **1.3x to 3.5x** larger on ten of the eleven (6.35 vs 3.0 on `bus-timetable`, 58.15 vs 43.6 on
`403_crossword`, 144.00 vs 114.3 on `68_journal`, 26.80 vs 7.7 on `insurance-policy-schedule`). The one
measured spend, on `68_journal`, moved it -114.3 -> -3.1 pt (`FINDINGS/18_displacement-GUARD-IS-THE-BLOCKER-68-JOURNAL-111PT-25NOV.md`),
i.e. 111.2 of 144 declared — **77 %**. A 77 % delivery is not the 1:1 the engine's own comment claims for
`w:before` on an empty paragraph, so **the delivery ratio of `w:before` is itself unmeasured at this engine**
and is the number to settle before any guard patch is written.

`table-inside-two-column-page` is the counter-example that forbids one blanket rule: its `med_dy` is **+8.0**
(render already below source) while it carries a 4.0 pt refused gap. Spending it moves the document the wrong
way. A rule that says "always spend" makes this document worse.

## What would prove this census wrong

* A document whose `.docx` carries no `w:sz w:val="2"` spacer paragraph but which is class A here — that
  would mean the template match missed a second emission site. `grep -c 'w:sz w:val="2"' word/document.xml`
  is the independent count; it agrees on all 25.
* A re-conversion at a newer engine that moves a document between A, B and C. The guard's verdict depends on
  `slackTw`, `spacerSplitTw`, `rowExcessTw` — all of which move with the page — so this census is stamped to
  engine `981ff1fa35e2cf67` and must be re-run, not trusted, after any engine change.
* The `med_dy`/`worst_dy` columns are the verdicts as recorded; they are a *summary*, not a per-run
  distribution, so they cannot say how many runs are out on a page — only the check can.

## Two corrections to what is written elsewhere

1. **`AUTOMATION-THE-GOOGLE-LOOP.md` is stale in both directions.** It says the `.docx` cannot be put into
   Drive from a sandbox. Measured this run: the corpus folder
   `1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA` **already holds all 213 `.docx`**, 213 distinct names, uploaded
   04:46 IST today. And the platform `upload` tool **does** stage a sandbox file and return an `s3key` that
   `GOOGLEDRIVE_UPLOAD_FILE` accepts — measured end to end on `303_discharge_summary.docx`
   (`s3key` -> `project_scope/ok_MI5WEzhyITR7/pr_qSx6sTyshHxf/files/gtabbu3786i1.docx`, then a real Drive
   file id). The duplicate it created was trashed again and the folder is back to 213. **Step 1 of
   `refresh-google.py` is not the blocker; it is done.**
2. **My own first census of this run was wrong and is recorded here so nobody repeats it.** A version of the
   same script printed `spacers=0` for 17 documents that had not been converted yet, because the
   "no .docx on disk" branch appended the same `0,0,0` tuple as a real zero and the printer never showed the
   label. The corpus was 74 of 213 at that moment. **A count of zero and a file that does not exist must not
   print the same string.** The numbers in the table above are from a run where `missing: []`.
