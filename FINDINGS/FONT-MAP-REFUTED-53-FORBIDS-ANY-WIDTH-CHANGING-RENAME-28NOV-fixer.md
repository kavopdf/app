# The DejaVu face map is refuted: check 53 forbids every rename that would fix 60

**28 Nov 2026 · fixer · engine HEAD a05b20eb05fe0fc8 · 12 documents measured through Google Drive**

## What the previous run handed over

A lead, recorded as `lead` with 0 moved:

> "Source PDFs use DejaVu at 10 pt; the engine declares DejaVu at 10 pt; Google Docs does not carry
> DejaVu and draws something about fifteen per cent narrower... Verdana fixed the edge, kept every
> other check passing, and took the document to 42 of 42 in Google; a second document, with two
> declared families rather than one, went to 42 of 42 the same way."

Two documents, and the claim was `42 of 42`.

## What this run measured

The change: `DocxWriter.faceName` now routes every DejaVu family through a new
`dejaVuFace(String)` helper - normalise the name (drop spaces/hyphens/underscores, lower case),
`DejaVu*Mono*` -> `Courier New`, every other DejaVu -> `Verdana`. That covers all six spellings the
corpus uses (`DejaVuSans`, `DejaVuSans-Bold`, `DejaVu-Sans`, `DejaVu-Sans-Bold`, `DejaVu-Sans-Mono`,
`DejaVu Sans Book`, `DejaVu Sans Mono Book`), which a `BASE14` entry does not: measured on
`33_sans_nondefault_body`, three map entries left **32 runs in `DejaVu Sans Book`** while 3 became
Verdana.

Twelve documents through the real Drive round trip (Google Doc -> PDF export -> `verify_google.py`
with `--docx`), five targets and seven controls:

| document | was | after | what changed |
|:--|:--|:--|:--|
| 313_power_of_attorney | 41/42, `60` FAIL | 41/42, **`60` PASS, `53` FAIL** | serif: `53: dejavuserif kept 0% of 1638 chars` |
| 302_radiology_report | 41/42, `60` FAIL | 41/42, **`60` PASS, `53` FAIL** | same trade |
| 316_contract_with_schedules | 41/42 | 46/47, `60` PASS, `53` FAIL | same trade |
| 370_offer_letter | 41/42 | 46/47, `60` PASS, `53` FAIL | same trade |
| 321_auditors_report | 41/42 | 41/42, `60` PASS, `53` FAIL | same trade |
| **304_package_insert_small_print** (control, was clean) | 42/42 | **41/42** `53` FAIL | regressed |
| **315_gazette_notification** (control, was clean) | 42/42 | **41/42** `53` FAIL | regressed |
| **362_price_list_dense** (control, was clean) | 42/42 | **41/42** `53` FAIL | regressed |
| **33_sans_nondefault_body** (control, was clean) | 42/42 | **39/42** `46`,`53`,`59` | regressed |
| **340_bill_of_lading** (control, was clean) | 42/42 | **39/42** `18`,`53`,`59` | regressed |
| 301_lab_report_panel | 45/47 | 45/47, `53` FAIL | trade, no gain |
| 334_patent_document | - | bridge unreachable, **not measured** | hole, not a pass |

## The finding

**The width half of the lead is right and is now confirmed on five documents, not two.** `60_text_column_right_edge`
passes on every document it was failing on. The previous run's `42 of 42` was not wrong about the
edge; it was measured on an instrument that did not include `53`.

**`53_embedded_faces` is the wall, and it is the wall by design.** It asks, for every family the source
PDF draws with, whether the `.docx` still puts that text in that family. `SAME_FACE` - the only place a
rename can be forgiven - states its own two rules:

> 1. IT MUST BE A RENAME THE ENGINE PERFORMS.
> 2. THE TWO FACES MUST BE METRIC-IDENTICAL, not merely "a reasonable substitute". A forgiveness that
>    spans two widths turns the check blind by construction... A serif as a sans, a sans as a serif,
>    anything as DejaVu. Those stay losses.

`dejavuserif -> verdana` breaks rule 2 twice over: it is a serif arriving as a sans, and it is 1.5 %
narrow besides. So for **every** document drawn in DejaVu Serif - and 313, the document the previous
run proved its lead on, is one - `60` and `53` cannot both pass. Google Docs has no DejaVu, and the
only faces Google has that are wide enough for DejaVu Sans are not DejaVu Sans.

**And the sans half regresses controls.** `33_sans_nondefault_body` (Verdana only after the fix, no mono)
lost `46_text_crossing_rule` and `59_shape_anchor`: Verdana at 1.008-1.037 x DejaVu is inside `60`'s
one-word slack but wide enough to push a line across a rule and move a shape. `340_bill_of_lading`
lost `18_displacement` as well.

**Net: zero documents became clean, and five that were clean stopped being clean.** The change is
refused by non-negotiable 3.

## Why the ratio evidence does not rescue it

The measured target is solid: over 5509 spans in 214 documents, drawn width / DejaVu advance width =
**1.0000** (median; 74 of 78 family+size buckets within +-0.001). Against that, measured from font
programs: Arial 0.899, Georgia 0.890, Times New Roman 0.817, Calibri 0.805, Cambria 0.774, Courier New
0.997 (for the mono face), Verdana ~1.008-1.037. So Verdana is the only proportional face on Google's
list within a few per cent, and the table is right. It does not matter: the check that refuses the
change is not a width check.

## What this closes, and what it opens

- **Closes:** the "declare a Google face for DejaVu" family of fixes, for good. No entry in `SAME_FACE`
  can be added for `dejavusans`, `dejavuserif` or `dejavusansmono` without breaking that table's own
  rule 2, and `prove_checks.py` asserts rule 1 against `DocxWriter.java`. `60` on a DejaVu document is
  a renderer limitation, not an engine defect, and should be recorded as such rather than chased again.
- **Opens:** `DejaVuSansMono -> Courier New` alone is 0.6020 em against 0.6000 em, 0.33 %, which IS
  metric-identical under rule 2. It was not measured alone here, because the mono family never carries
  the widest line in a document and so cannot move `60` by itself. It is a lead, not a fix.
- **Also opens (bigger):** the Drive measurement path is unblocked - see
  `tools/p2w-bench/VERIFY-GOOGLE.md`, "the path that works". Every future `.docx` attempt can be
  measured in Google inside its own slot, which is what blocked the last three runs.

## The probe branch

`probe/fontmap-28nov`, folder `tools/p2w-bench/PROBE-28NOV/` - the twelve `.docx` this run measured,
published only because `GOOGLEDRIVE_UPLOAD_FROM_URL` needs a public URL. The source PDFs are the repo's
own public corpus release assets, so nothing private was published. Nothing was deleted.

---

## The split the last two runs never made: 27 of the 59 are not font-limited

Both runs treated `60_text_column_right_edge` as a DejaVu problem. It is not. For each of the 59
documents that fail 60, this run read the source PDF and asked which family draws the page's **widest
line** - the line the check takes the column's right edge from:

| widest line drawn in | documents | can a face change fix it? |
|:--|--:|:--|
| a DejaVu family | **32** | no - Google has no DejaVu, and 53 forbids the substitute (this file) |
| Liberation Sans / Serif / Noto Naskh Arabic | **27** | **yes - the engine already maps these to metric-identical faces** |

The 27, which are the ones worth the next run's slot:

    14_stamp_chars_positioned_td, 25_signature_block_underscores_txtpos,
    28_value_overflows_cell_txtpos, 38_faux_bold_italic_synthesised,
    56_table_indented_from_margin, 65_two_col_full_width_figure_caption,
    77_arabic_rtl_document, 79_inr_indian_digit_grouping_table,
    academic-paper-ieee-2col-abstract, balance-sheet-and-profit-loss,
    boq-tender-bill-of-quantities, delivery-challan, form16-part-b, gst-invoice-3line-items,
    gst-invoice-horizontal-rules-only, landscape-page-inside-portrait-document,
    magazine-2col-pullquote-spanning, marksheet-subject-left-marks-right,
    marksheet-university-consolidated, mutual-fund-statement,
    one-page-rotated-180-degrees, policy-2col-spanning-section-heading, purchase-order,
    question-paper-marks-right-margin, table-across-page-break-repeated-header,
    text-held-twice-shadow-text, very-long-single-column-table

Liberation Sans is Arial's metric drop-in and Liberation Serif is Times New Roman's, so on these
documents the `.docx` already names a face whose widths match the page. The edge that is short is
therefore **not** a substitution artefact - it is something the engine controls: the column's right
edge, a paragraph indent, justification, or a table cell width. That is a different class from the
DejaVu one, it was invisible while the two were counted together, and 27 documents is 8.9 clean
documents of leverage on the classpick table.

## The 19 documents whose only failure is 18_displacement

Not the face, and not this file's class, but measured here because the store had it and it costs
nothing. All 19 fail on exactly ONE page. Split by the median dy of the matched runs:

| shape | documents | median dy | reading |
|:--|--:|:--|:--|
| constant small offset, \|med\| <= 3 pt | 13 | -7.7 .. +2.9 | the whole page sits a fixed distance off; not a drift |
| accumulating drift, med >= 4 pt | 6 | +2.4 .. +8.0 | the row pitch is wrong and the error grows down the page |

    13 constant: 10_stamp_as_image(-1.8), 303_discharge_summary(0.9), 306_clinical_protocol_synopsis(-0.4),
       30_mixed_font_sizes_one_baseline_txtpos(2.3), 35_four_typefaces_one_page(-2.8),
       403_crossword_puzzle(-7.7), 70_magazine_drop_cap_photo_caption(2.9),
       72_bank_statement_no_rules_right_amounts(-1.0), 74_balance_sheet_indented_subitems(1.5),
       balance-sheet-two-columns-of-figures(-0.5), eway-bill(-2.7), table-with-no-header-row(0.7),
       two-tables-stacked-with-no-gap(-1.2)
    6 drift:    320_balance_sheet_statutory(7.2), 341_shipping_manifest(2.4/worst 21.4),
       71_invoice_space_aligned_no_rules(2.9/worst 26.3), bus-timetable-station-left-times-right(4.2),
       price-list-2col-dense-right-aligned(5.8), table-inside-two-column-page(8.0/worst 69.2)

Several of the 13 have a worst dy BELOW the 4.5 pt cap (303 and 70 at 3.1, two-tables at 2.9, 35 at
3.3) and still fail - so they fail on the TAIL clause (one run more than 2x its own tolerance, which at
6.5 pt is 4.55 pt) or on the per-page budget, not on the median. The 6 drift documents are the row-pitch
question `FINDINGS/TABLE-ROW-PITCH-IS-FLOORED-BY-GOOGLE-8-VARIANTS-28NOV-fixer.md` already opened; the
13 constant-offset ones are a different, smaller, and never-separated shape.

---

## What the 27 actually do: they OVER-run, by 77 to 161 pt, in one column each

`60` reports pass/fail and no numbers, so a fixer could not tell a shortfall from an over-run. This run
added `tools/p2w-bench/edgeprobe.py`, which prints the numbers `60` compares - per column, the source's
right edge, Google's, the difference, and the window `60` allows - using `60`'s own estimator and
tolerance. **Cross-checked against an independent number:** on `313_power_of_attorney` it prints
`src_edge=538.63 gd_edge=477.66 d=-60.97 allow=-48.00`, which is the previous run's own recorded
`edge 477.66 vs src 538.63, tolerance 48` to the digit. So the probe is the check, not a lookalike.

Five of the 27 measured through Google at engine HEAD:

| document | verdict from the probe | the one column that fails |
|:--|:--|:--|
| delivery-challan | 9 of 10 columns PASS | left 422.76: src 473.53, gd **550.74**, **+77.21** (allow +27.61) |
| purchase-order | 7 of 8 columns PASS | left 428.30: src 449.71, gd **553.07**, **+103.36** (allow +23.51) |
| gst-invoice-3line-items | 10 of 11 columns PASS | left 62.92: src 174.79, gd **335.97**, **+161.18** (allow +25.99) |
| marksheet-subject-left-marks-right | every column PASSES | - |
| very-long-single-column-table | every column PASSES | - |

**That inverts the story both previous runs told.** `60` on these documents is not "the line stops short
because the face is narrow". It is **one column running 77-161 pt past the source's edge** while every
other column on the page lands within a couple of points. A column whose text is 1.6x to 2.4x the width
the page drew is a lost table cell width, a lost wrap, or text that should have been split and was not -
a geometry fault in `PdfToWord`, not a font fault and not a small tolerance miss.

The two that pass every column and still fail `60` fail the check's SAFETY NET, not its columns:
`far >= 2` lines past `s_max + 3 * RIGHT_OVERRUN` - ink outside every column, which `edgeprobe.py` does
not yet print. That is the next instrument gap and it is one function.

**So the next run's target is not "stretch the line".** It is: on each of the 27, find the column the
probe names, and ask why that column's render is 77-161 pt wider than the page's. `gst-invoice-3line-items`
at +161.18 pt on a 112 pt source column is the cheapest single document to open, because a 2.4x
widening is not a tolerance question - it is a table column that arrived at the wrong width, and it
should be visible in the `.docx`'s `w:tcW` without any renderer at all.
