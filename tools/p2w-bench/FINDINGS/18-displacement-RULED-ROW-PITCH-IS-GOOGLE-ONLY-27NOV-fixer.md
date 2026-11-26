# 18_displacement — a ruled table row is 0.75 pt taller in Google than in LibreOffice, and no `trHeight` value can fix it

**Run:** 27 Nov 2026, fixer slot 03:01 IST.
**Class:** `18_displacement` (worth 52.2 clean documents, the largest single lever in the corpus).
**Verdict:** CONFIRMED cause for **4 of the 9** documents on this engine that fail `18_displacement` and
nothing else. **Not** the cause for the other 5. The two renderers cannot be reconciled by tuning the row
height, so this sub-class is a *layout-construct* fix, not a number.

---

## 1. The measurement, end to end

`303_discharge_summary` fails `18_displacement` and nothing else: 46/47, `med_dy = -0.2`, `worst_dy = 4.1`,
45 runs, one bad page.

The nine runs that are out of tolerance are all **positive** dy (render lower than the source), and they
all sit at or below the document's one table:

```
dy=+4.10 size=7.0 tol=2.45 'Resident Medical Officer'
dy=+4.10 size=7.0 tol=2.45 'Dr. Meera Krishnan, Consultant'
dy=+3.79 size=7.0 tol=2.45 'FOLLOW UP'
dy=+3.63 size=8.0 tol=2.80 'WARNING SIGNS: return immediately if breathlessn'
dy=+3.47 size=8.5 tol=2.97 'Review in chest medicine OPD on 25-03-2024 with '
dy=+2.80 size=8.0 tol=2.80 'Tab. Prednisolone'      <- table row 4
dy=+2.80 size=8.0 tol=2.80 '20 mg'                  <- same row
dy=+2.80 size=8.0 tol=2.80 '1-0-0 tapering'         <- same row
dy=+2.80 size=8.0 tol=2.80 '5 days'                 <- same row
```

The last table row is **+2.80 pt** low, and 2.80 = **4 rows x 0.70**. The four cells of that row share one
offset exactly, which is a row that has been laid out too tall, not text that has drifted.

Measured on the three renderers, same `.docx`, row baseline pitch:

| renderer | pitch | rows are |
|---|---|---|
| source PDF | **15.00 pt** | the page drew 5 rows at exactly 15.00 (baselines 283.88, 298.88, 313.88, 328.88, 343.87) |
| LibreOffice | **15.00 pt** | correct |
| Google (export of the .docx) | **15.75 pt** | **+0.75 per row** |

`w:trHeight w:val="300" w:hRule="atLeast"`, `w:tblBorders` all six edges `w:sz="3"` (0.375 pt),
`w:tblCellMar` all zero, cell paragraph `before=209 line=11 exact` (= 11.0 pt of content in a 15.0 pt row).

## 2. Where the 0.75 comes from — seven variants, two renderers, one probe document

A single probe `.docx` holding one table per variant was uploaded once to Drive, exported once, and the
row pitch read off the export with PyMuPDF. LibreOffice rendered the same file locally. Nothing here is
inferred from the engine or from the checker; both columns are measured from rendered PDFs.

| variant | table borders | trHeight | LO pitch | **Google pitch** |
|---|---|---|---|---|
| V1 | top,left,bottom,right,insideH,insideV | 300 atLeast | 15.00 | **15.75** |
| V2 | none | 300 atLeast | 15.00 | **15.00** |
| V3 | top,left,bottom,right,insideH,insideV | 285 atLeast | 14.25 | **15.00** |
| V4 | top,left,bottom,right (outer box only) | 300 atLeast | 15.00 | **15.00** |
| V5 | all six | 300 **exact** | 15.00 | **15.75** |
| V6 | all six | 315 **exact** | 15.80 | **16.50** |
| V8 | left,right,insideH,insideV (no outer top/bottom) | 300 atLeast | 15.00 | **15.75** |
| V9 | left,right + per-cell top on row 0, bottom on every row | 300 atLeast | 15.00 | **15.75** |

*(Every pitch in this table is rows 2-4 of the variant's table. Row 1 is not a row pitch — it is the
distance from the variant's title paragraph to the table's first row, and it moves with the border
above it. `probe-rowpitch.py --measure` skips it for that reason.)*

What the table says:

- **`hRule` is irrelevant.** `exact` behaves exactly like `atLeast` in Google (V5 = V1; V6 = V1 + 0.75).
- **The outer box is irrelevant.** Removing the table's top and bottom (V8) changes nothing.
- **What costs 0.75 pt is a horizontal rule on a row boundary.** V4 is the only ruled variant that renders
  at 15.00, and it is the only one with **no horizontal rule between rows**. Moving that rule out of
  `tblBorders/insideH` and onto the cells' `tcBorders/bottom` (V9) does **not** help — the cost follows the
  rule, not the element it is written in.
- **LibreOffice never charges for the rule.** Every LO column reads 15.00 except where the height itself
  was lowered to 285 (V3, 14.25).

So the law is: **Google lays a ruled row at `trHeight + 0.75 pt`; LibreOffice lays it at `trHeight`.**

## 3. Why this is not a one-number fix

For the row to be right in Google, `trHeight` must be `pitch - 0.75` (V3: 285 -> 15.00 in Google). For the
row to be right in LibreOffice, `trHeight` must be `pitch` (V3: 285 -> 14.25, wrong). There is no value of
`trHeight` for which both renderers produce 15.00, and `hRule` does not change the relationship.

That is the whole reason 98 recorded attempts against this class have not closed it: the attempts were
looking for a number, and for ruled rows the number does not exist. The row height has to stop being
carried by `trHeight` on a ruled row at all — the horizontal rules have to leave the table (drawn as
shapes or as paragraph rules that are not charged), or the row height has to be carried by the content
with the table's rules suppressed.

**This also explains the LibreOffice proxy trap.** Every attempt that lowered `trHeight` to fix Google
made LibreOffice worse by the same 0.75 pt, and `regress.py --check` gates on LibreOffice. A change that
is right in Google is *guaranteed* to look like a regression in the proxy. That is a property of this
sub-class, not of any one patch.

## 4. How far it reaches — and how far it does not

Of the 25 corpus documents that fail `18_displacement` and nothing else, 9 are on the engine in the tree
and have a `.docx` to inspect:

| document | tables with `insideH` | explained by this finding |
|---|---|---|
| 303_discharge_summary | 1/1 | **yes** — pitch +0.75/row measured |
| 320_balance_sheet_statutory | 2/2 | **yes** |
| 325_demat_holdings_statement | 2/2 | **yes** |
| 402_calendar_month_grid | 1/1 | **yes** |
| 16_right_aligned_amounts_txtpos | 0/1 | no |
| 362_price_list_dense | 0/1 | no |
| 36_embedded_subset_font | 0/1 | no |
| 403_crossword_puzzle | 0/1 | no |
| 31_times_body_arial_headings | 0/0 (no table) | no |

**4 of 9.** The other five have no horizontal rule between rows, so their displacement is a different
construct and is still unexplained. Do not treat this finding as the class.

## 5. What was tried this run and measured as inert or irrelevant

- **`capTw` content cap on a single-line cell** (`DocxWriter.java:6859`, `rowParts == 1 ? rowHeightTw :
  min(rowHeightTw, contentTwHere)`). Predicted: lets a single-line cell's paragraph fill its row. Measured:
  **byte-identical `word/document.xml` on all 9 target documents** — `contentTwHere` is never below
  `rowHeightTw` in this corpus, so the cap never binds. Reverted. The patch is inert, not wrong.
- **`patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch`** (unmeasured; moves the
  page-top gap from `w:before` into `w:pgMar w:top`). Applied, compiled, converted, measured through
  Google on `303_discharge_summary`: **46/47 before, 46/47 after, same failing check, same page.** It
  cannot help: all 9 documents in this group are **single-page**, so there is no continuation page for the
  patch to act on. Its own evidence is about pages 2..n. Reverted, and left unmeasured for its real
  population (multi-page documents) — that is still the right next test for it, on
  `bank-statement-5-pages` and `412_page_labels_roman`, not on this group.

## 6. The instrument this run proved, which outlives the finding

The Google after-side is reachable from a fixer slot, end to end, in about 90 seconds a document:

```
cp <docx> /scratch/output/probe.docx
upload(path="/scratch/output/probe.docx", tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
GOOGLEDRIVE_CREATE_FILE(name=..., mimeType="application/vnd.google-apps.document",
                        parents=["1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij"], file_to_upload={...})
GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=..., mimeType="application/pdf")
   -> artifacts[0].workspace_path, no separate download call needed
gverify.py --collect <name> <workspace_path>
```

Four MCP calls, one export, no download step. **The copy into `/scratch/output` is mandatory** — the
platform `upload` refuses a path under `/scratch/work` (FINDINGS/GOOGLE-LOOP-UNBLOCKED-COPY-TO-OUTPUT-FIRST-26NOV-fixer.md).

Five probe documents were created in `KavoPDF-Verify` this run and deleted at the end of it.

## 7. What the next run should do with this

1. **Do not** look for a `trHeight` value for ruled rows. It does not exist (§3).
2. The shippable change for the 4 explained documents: emit the horizontal rules of a ruled table **outside**
   `trHeight` accounting — as zero-height ruled paragraphs between rows, or as line shapes — so that
   `trHeight` is the page's pitch in both renderers. Prove it on `303_discharge_summary` first: the row
   pitch must read **15.00 in both** and the `Tab. Prednisolone` cells must move from +2.80 to 0.00.
3. The five unexplained documents (`16`, `362`, `36`, `403`, `31`) have no ruled rows. Their `med_dy` is
   -1.6, -2.8, +1.7, -10.2 and +2.6 pt, i.e. both signs, so it is not a single global offset. Take `403`
   first: -10.2 pt median with 27 runs is the largest and the cleanest to diagnose.
