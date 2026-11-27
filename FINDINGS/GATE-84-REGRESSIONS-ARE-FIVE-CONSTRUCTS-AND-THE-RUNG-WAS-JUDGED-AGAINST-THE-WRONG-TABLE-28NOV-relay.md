# The gate is blocked by 84 documents, not by the rung — and the rung verdict was measured against the wrong table

**28 Nov 2026, relay slot 02:24.** Fixer run. Class: `63_table_rows` (gate first), then txt.

This run did not land an engine change, because **the commit gate refuses every engine change**: 84 docx
documents are worse than `benchmarks/RANKING-BASELINE.csv` (the 15 Nov state, engine `ead0d0e`). The
rung is only 28 of them. Two things below are corrections to the record; both are re-derivable from
committed CSVs in minutes.

---

## 1. The gate's actual state, which the last two reports describe as "unblocked"

    python3 tools/p2w-bench/regress.py --check
      engine fingerprint : 72ff003db5871587
      docx: 84 REGRESSION(S)
      txt : no document worse than baseline
      REFUSED.

The 00:58 run's "gate unblocked" cleared the **fingerprint** refusal (the table now names the engine it
was measured on). It did not clear the **regression** refusal, which is a different message from the same
tool. Nothing has changed in the engine since; the 84 are live now and were live then.

## 2. `ROW_RUNG_UNDER_TW = 0` is a net improvement on the gate's own metric

Both the 00:18 run and the 27 Nov 23:17 run judged the rung by comparing the rung=0 tree against
`benchmarks/RANKING.csv` — **which is the rung=10 tree's own output**. That comparison can only say
"rung=0 is worse than rung=10". It cannot answer the gate's question, which is "is this document worse
than 15 Nov".

Against `RANKING-BASELINE.csv`, over the 212 documents both tables carry:

| tree | worse than 15 Nov | better than 15 Nov | unchanged |
|:--|--:|--:|--:|
| current (`a05b20eb`, rung=10) | **84** | 47 | 81 |
| `ROW_RUNG_UNDER_TW = 0` (`b6485949`) | **57** | 64 | 91 |

So the rung costs 28 documents against the baseline and buys back 1:

* **fixed by rung=0 (28):** `table-with-no-header-row` 0.61 → 47.48 → 0.61, `boq-tender-bill-of-quantities`,
  `very-long-single-column-table`, `balance-sheet-and-profit-loss`, `electricity-bill`, `form16-part-b`,
  `gst-invoice-multipage-item-table`, `eway-bill`, `bank-statement-5-pages`, `375_attendance_register`,
  `372_timesheet_grid`, `404_sudoku_grid`, `306_clinical_protocol_synopsis`, `311_fir_police_form`,
  `332_bom_on_drawing`, `344_customs_declaration`, `23_timetable_grid_txtpos`, `insurance-policy-schedule`,
  `invoice-line-items-qty-rate-amount`, `marksheet-university-consolidated`, `mobile-bill`,
  `mutual-fund-statement`, `property-tax-receipt`, `purchase-order`, `salary-slip-factory-wages`,
  `table-across-page-break-repeated-header`, `table-with-rotated-header`,
  `two-tables-stacked-with-no-gap`.
* **introduced by rung=0 (1):** `marksheet-subject-left-marks-right` 4.55 baseline, **2.15** on the
  current tree, **5.21** at rung=0. The rung genuinely helps this document; this is the one row a
  per-row rung has to keep.

**Integrity of the rung=0 table, checked without trusting the run that made it.** The table is stamped
`b648594972a7682b`. Taking the current tree, changing only `DocxWriter.java:54` to `= 0` and hashing the
engine sources the way `regress.py:engine_fingerprint(fmt='docx')` does reproduces `b648594972a7682b`
exactly. So the CSV is a measurement of "this tree, rung only", not of some other state.

**It is still not committable.** 57 regressions is a refusal. The rung is not the gate's cause, only the
largest single contributor to it.

## 3. The 84 are at least five constructs, and the largest coherent one is stamps

With the rung removed, 57 remain. Clustered by document name and by the delta against baseline:

| cluster | documents | worst delta |
|:--|--:|:--|
| **stamps** (rotated / positioned / image) | **10** | `03_stamp_vertical_90deg` 16.98 → 34.38 (+17.40) |
| right-aligned amounts / dense price lists | 6 | `price-list-2col-dense-right-aligned` 2.69 → 27.89 (+25.20) |
| fonts (typefaces, sans body, subset, devanagari) | 5 | `35_four_typefaces_one_page` 2.19 → 9.10 (+6.91) |
| `txtpos` text-positioning | 5 | `16_right_aligned_amounts_txtpos` 0.00 → 3.83 |
| tables / margins / page shape | the rest | `bus-timetable-station-left-times-right` 0.27 → 11.40 |

The rows overlap on purpose (`16_right_aligned_amounts_txtpos` is both an amount column and a `txtpos`
document), so the column does not sum to 57; the clusters are named by construct, not partitioned.

The stamp cluster is ten documents, all of them carrying `stamp` in the name, and it is the only cluster
where one construct plausibly owns the whole group. It is the next prize; it is not a one-line change and
this run did not have the slot to diagnose it.

## 4. The txt half is 3 documents from the charter's bar, and two of them are one construct

    txt: 214 scored | 208 clean (97.2%) | 6 failing

213 scored documents at 99% is **211 clean**. The txt gate compares against its own baseline and passes,
so a `.txt`-scoped change is committable today even while the docx gate refuses.

The six, and what they fail:

| document | fails |
|:--|:--|
| `041122-Account_Opening_Form` | t06_encoding, t09_page_furniture, t12_word_invention |
| `Account_Opening_Form_Fillable_filled` | t06_encoding, t09_page_furniture, t12_word_invention |
| `Prakashan_Print_Fidelity_Handbook` | t01_word_accuracy, t03_symbols, t07_symbol_counts, t12_word_invention |
| `600_reviewed_invoice_with_annotations` | t12_word_invention |
| `601_fillable_admission_form` | t01_word_accuracy |
| `305_vaccination_certificate` | t08_line_order |

**The two `Account_Opening_Form` documents are the same defect** — near-identical counts (127 / 125 / 14
against 127 / 125 / 14). Measured on `041122-Account_Opening_Form`:

* source PDF text extraction: 48,837 characters, **0** U+FFFD; `.txt`: 270,545 characters, **127** U+FFFD.
* the invented characters are exactly `U+FFFD` x127; the missing ones are `Ĥ` x89, `Ħ` x23, `ģ` x13 (125).
* first occurrence: `Please \ufffdll up in BLOCK letters` — a **ligature glyph** the engine cannot name,
  written as "cannot represent this". The PDF's own extraction names these glyphs, so this is the
  engine's glyph→Unicode mapping, not a decode fault in the writer.
* `t09_page_furniture` reports owed 29 / **present 125**: the `.txt` repeats its running heads far more
  often than the page drew them, which is the same 5.5x over-generation the character count shows.

So this is one construct with three symptoms — the shape the brief warns about — and clearing it would
take the txt from 208 to 210. One more document reaches 211 and the charter's 99% on the `.txt`.

## What this run did not settle

* **Whether a per-row rung can keep `marksheet-subject-left-marks-right`.** The quantity the falsifier
  named — the difference between the source pitch and the room a row's own text needs — is not computed
  anywhere yet. `footRoom` already measures the room; it does not measure the pitch mismatch that the
  10 tw constant is standing in for.
* **The Google side of the rung trade.** `mobile-bill` and `electricity-bill` were the documents
  `8fb4f503` was tuned on. Nothing here was exported through Drive.

## Pod facts worth not paying again

* **`/scratch/work` was warm on this pod**: JDK at `/scratch/work/.p2w-jdk/jdk`, jars in
  `tools/engine-verify/libs`, corpus 214 PDFs, engine compiled. `pod-prep.sh` skipped steps 1-7.
* `install-gate.sh` calls `pod-prep.sh`, whose corpus slice is 240 s, so **the install call alone exceeds
  one sandbox call** on a cold pod. Run `pod-prep.sh` on its own until it prints `DONE`; it is
  idempotent and prints "skipped (warm)" per step.
* The corpus was 18 documents short of complete and finished in 92 s on this pod.
* `verify_txt.py <pdf> <txt>` runs one document in about a second and needs **no JDK** — the `.txt`
  outputs are already in `/scratch/work/p2w/out/`. The whole txt half of the goal is diagnosable from a
  cold pod.
