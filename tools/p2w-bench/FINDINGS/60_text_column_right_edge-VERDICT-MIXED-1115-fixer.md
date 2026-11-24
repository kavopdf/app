# `60_text_column_right_edge`: **MIXED** — four documents are Google's font substitution, one is a real column defect, and fifty-one cannot be decided from the ratchet table

**Verdict written 24 Nov 2026, read-only analyst slot. No engine change, no render, no upload.**
Primary data: `RATCHET-GOOGLE.json` — 190 rows, all stamped `2026-11-24T04:36:24+05:30`, engine
`b7699196` on 186 of them (`462353f` 3, `5beb8b9d` 1). Secondary: 276 prior notes in `FINDINGS/`.
**No renderer, no corpus, no source PDFs were available on this pod**, so every value-level number
below is *quoted from a prior note that measured it* and is labelled as such. Nothing here was
re-measured.

---

## 0. Headline verdict

**Form (c) MIXED.** `60_text_column_right_edge` fails on **56 of 190** measurable documents. The class
is not one construct, and the one group that can actually be settled splits 4 to 1 **against** the
"real defect" reading:

| tier | documents | status | basis |
|:--|--:|:--|:--|
| **real column defect** | 1 | `79_inr_indian_digit_grouping_table` | **measured** — fails in LibreOffice *and* Google, and names faces Google has (`Arial`, `Times New Roman`) |
| **instrument / renderer** | 4 | `302_radiology_report`, `313_power_of_attorney`, `316_contract_with_schedules`, `321_auditors_report` | **measured** — pass **42/42 (46/47) in LibreOffice** on the same `.docx`, fail only in Google; the `.docx` declares the source's own face |
| **undecided** | 51 | the remaining groups | pass/fail only — no branch, no values, no cross-render in the ratchet |

**One correction to the question as asked.** The repo question frames the alternative as "is 60 or 18
reading the paper instead of the defect — the `25_invisible_text` precedent". The specific hypothesis
that 60 is comparing against **a drawn rule or the page's own drawn edge** is **not supported by any
note in this tree**. Check 60 reads only the text layer — no note shows it calling `get_drawings()`,
and the one note that reads its code says so explicitly:

> "`60_text_column_right_edge` | Does the render's **text column end where the source's did**? Reads
> only the text layer: lines grouped into columns by left edge, each column's right edge = its
> **widest line**" — `60_text_column_right_edge-SHAPE-ANCHOR-1334-B1.md`

So the `25_invisible_text` precedent transfers as a **method**, not as an identity. The instrument
fault that *is* proven for 60 is a different one of the same family: the check's **reference is a
typographic extent of the paper**, and its tolerance is "one word" measured in *the render's own face*,
so a substituted face both moves the extent and grows the slack. That is a reference-side fault — the
paper's own metrics, not the `.docx`'s geometry — but it is not the drawn-rule variant, and the finding
should not be filed as though it were.

**A count discrepancy to record:** the brief says "~25 documents". The primary data says **56** (54 on
the current engine). I could not find a definition that yields 25, and the prior notes use 56
throughout (`1334-B1` §4: "fails `60`: **56**"; `0830` §1 counts "56 of 190 measurable documents"). The
~25 figure is **not stated** anywhere I can see. I use 56.

---

## 1. The census, and three reasons to distrust a naive count

- **190, not 213.** 23 corpus rows are `page_count_refused` and carry no `failed` list.
  `1334-B1` §4 states the same: "190 `ok` rows; 23 `page_count_refused` rows carry no `failed` list and
  are not counted". They are absent from this file, not passing it.
- **The universe varies by document.** 126 rows are counted out of 42 checks, 62 out of 47, 2 out of
  44. A *failed set* is therefore not strictly comparable across documents — `316_contract_with_schedules`
  is a 47-check document, the other three solo documents are 42-check.
- **The ratchet records no direction.** It stores `failed: [ids]` only. It does **not** record whether
  60 fired on the **over** branch (`rg > rs + RIGHT_OVERRUN + slack`) or the **under** branch
  (`rg < rs - RIGHT_UNDERRUN - slack`). This matters: the two published mechanisms predict opposite
  signs (§4). **The primary data cannot even tell me which way the check fired** — that is the single
  biggest limit of this file and it is why 51 documents stay undecided.

Failure frequency across the corpus (check, documents failing):

| check | docs | | check | docs |
|:--|--:|:-:|:--|--:|
| `18_displacement` | 103 | | `45_char_accuracy` | 37 |
| `04_chars_missing` | 65 | | `13_text_colours` | 32 |
| **`60_text_column_right_edge`** | **56** | | `17_matched_runs` | 30 |
| `25_invisible_text` | 48 | | `44_header_footer` | 25 |
| `59_shape_anchor` | 45 | | `47_margins` | 25 |

60 is the third most common failure in the corpus, which is why it was worth a slot — but frequency is
not evidence of construct.

**Co-failure rates inside the 60 population (n = 56):**

| co-failing check | docs | share | what it would mean if it were the cause |
|:--|--:|--:|:--|
| `18_displacement` | 36 | 64% | ink displaced — a **position** fault, not an extent fault |
| `04_chars_missing` | 24 | 43% | characters lost — a content fault, different construct |
| `59_shape_anchor` | 16 | 29% | a shape's anchor moved — the anchored-text-box population |
| `25_invisible_text` | 14 | 25% | text present but not visible — itself largely instrument (§4) |
| `45_char_accuracy` | 14 | 25% | glyph accuracy |
| `13_text_colours` | 13 | 23% | colour |
| `47_margins` | 10 | 18% | margins — a wrong margin **is** a wrong right edge |
| `43_within_10pt_x` | 7 | 12% | x within 10 pt |
| `27_text_off_page` | 7 | 12% | text off page |

Two structural facts fall out, and they pull in opposite directions:

- **36 of 56** also fail `18_displacement`. If 60 were a pure layout defect you
  would expect it to travel with a position check — and it does, in the majority.
- **But 20 of 56** fail 60 *without* `18_displacement`, and **14**
  fail 60 with **no position-family check at all** (`18`, `43`, `47`, `27`, `26`):
  `14_stamp_chars_positioned_td`, `302_radiology_report`, `312_affidavit_stamp_paper`, `313_power_of_attorney`, `316_contract_with_schedules`, `321_auditors_report`, `335_msds_safety_data_sheet`, `352_certificate_ornate_border`, `371_experience_certificate`, `38_faux_bold_italic_synthesised`, `393_spectrum_peak_table`, `65_two_col_full_width_figure_caption`, `79_inr_indian_digit_grouping_table`, `policy-2col-spanning-section-heading`.

A defect that leaves the ink where the page put it, and yet is charged with the column ending in the
wrong place, is either an extent-statistic artefact or a face-metric effect. It is not displacement.

---

## 2. Every document that fails 60, grouped by the exact set of its other failures

**56 documents, 37 distinct groups.** Group label abbreviates the co-failing check ids; the full set is
in the third column.

| n | group | exact co-failing set | documents |
|--:|:--|:--|:--|
| 8 | 18 | 18_displacement | `363_warranty_card`, `370_offer_letter`, `406_passport_mrz_page`, `boq-tender-bill-of-quantities`, `landscape-page-inside-portrait-document`, `marksheet-university-consolidated`, `question-paper-marks-right-margin`, `table-with-merged-cells` |
| 5 | **60 alone** | — | `302_radiology_report`, `313_power_of_attorney`, `316_contract_with_schedules`, `321_auditors_report`, `79_inr_indian_digit_grouping_table` |
| 4 | 18 + 59 | 18_displacement, 59_shape_anchor | `340_bill_of_lading`, `343_air_waybill`, `56_table_indented_from_margin`, `salary-slip-factory-wages` |
| 3 | 18 + 25 | 18_displacement, 25_invisible_text | `301_lab_report_panel`, `342_packing_list`, `gst-invoice-3line-items` |
| 2 | 04 + 18 + 27 | 04_chars_missing, 18_displacement, 27_text_off_page | `form16-part-b`, `table-across-page-break-repeated-header` |
| 2 | 04 + 18 + 45 | 04_chars_missing, 18_displacement, 45_char_accuracy | `25_signature_block_underscores_txtpos`, `311_fir_police_form` |
| 2 | 47 | 47_margins | `317_rti_response`, `365_recipe_card` |
| 1 | 04 | 04_chars_missing | `38_faux_bold_italic_synthesised` |
| 1 | 04 + 05 + 18 + 27 + 32 + 44 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer | `very-long-single-column-table` |
| 1 | 04 + 10 + 13 + 17 + 32 + 43 + 44 + 45 + 47 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 43_within_10pt_x, 44_header_footer, 45_char_accuracy, 47_margins | `magazine-2col-pullquote-spanning` |
| 1 | 04 + 10 + 13 + 17 + 44 + 45 + 59 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy, 59_shape_anchor | `policy-2col-spanning-section-heading` |
| 1 | 04 + 13 + 17 | 04_chars_missing, 13_text_colours, 17_matched_runs | `312_affidavit_stamp_paper` |
| 1 | 04 + 13 + 17 + 18 + 25 + 26 + 44 + 45 + 59 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 26_text_overlap, 44_header_footer, 45_char_accuracy, 59_shape_anchor | `322_mutual_fund_factsheet` |
| 1 | 04 + 13 + 17 + 18 + 25 + 45 + 66 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 45_char_accuracy, 66_table_cell_width | `323_credit_card_statement` |
| 1 | 04 + 13 + 17 + 43 + 45 + 47 + 59 | 04_chars_missing, 13_text_colours, 17_matched_runs, 43_within_10pt_x, 45_char_accuracy, 47_margins, 59_shape_anchor | `318_court_summons_form` |
| 1 | 04 + 13 + 17 + 44 + 45 + 59 | 04_chars_missing, 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy, 59_shape_anchor | `65_two_col_full_width_figure_caption` |
| 1 | 04 + 13 + 17 + 45 | 04_chars_missing, 13_text_colours, 17_matched_runs, 45_char_accuracy | `352_certificate_ornate_border` |
| 1 | 04 + 13 + 17 + 45 + 59 | 04_chars_missing, 13_text_colours, 17_matched_runs, 45_char_accuracy, 59_shape_anchor | `371_experience_certificate` |
| 1 | 04 + 13 + 18 + 25 + 26 | 04_chars_missing, 13_text_colours, 18_displacement, 25_invisible_text, 26_text_overlap | `delivery-challan` |
| 1 | 04 + 13 + 18 + 25 + 59 | 04_chars_missing, 13_text_colours, 18_displacement, 25_invisible_text, 59_shape_anchor | `344_customs_declaration` |
| 1 | 04 + 13 + 25 + 45 | 04_chars_missing, 13_text_colours, 25_invisible_text, 45_char_accuracy | `14_stamp_chars_positioned_td` |
| 1 | 04 + 17 + 18 + 27 + 44 + 45 + 47 | 04_chars_missing, 17_matched_runs, 18_displacement, 27_text_off_page, 44_header_footer, 45_char_accuracy, 47_margins | `academic-paper-ieee-2col-abstract` |
| 1 | 04 + 18 + 25 | 04_chars_missing, 18_displacement, 25_invisible_text | `381_incident_report_timeline` |
| 1 | 04 + 18 + 25 + 47 + 59 + 66 | 04_chars_missing, 18_displacement, 25_invisible_text, 47_margins, 59_shape_anchor, 66_table_cell_width | `383_api_docs_page` |
| 1 | 04 + 18 + 26 + 44 + 45 | 04_chars_missing, 18_displacement, 26_text_overlap, 44_header_footer, 45_char_accuracy | `gst-invoice-horizontal-rules-only` |
| 1 | 04 + 18 + 27 + 43 + 44 + 62 + 63 | 04_chars_missing, 18_displacement, 27_text_off_page, 43_within_10pt_x, 44_header_footer, 62_table_columns, 63_table_rows | `one-page-rotated-180-degrees` |
| 1 | 04 + 43 + 45 + 47 + 59 | 04_chars_missing, 43_within_10pt_x, 45_char_accuracy, 47_margins, 59_shape_anchor | `28_value_overflows_cell_txtpos` |
| 1 | 13 + 18 + 25 | 13_text_colours, 18_displacement, 25_invisible_text | `text-held-twice-shadow-text` |
| 1 | 17 + 18 + 26 + 43 + 47 + 59 | 17_matched_runs, 18_displacement, 26_text_overlap, 43_within_10pt_x, 47_margins, 59_shape_anchor | `77_arabic_rtl_document` |
| 1 | 18 + 23 + 59 | 18_displacement, 23_line_pitch, 59_shape_anchor | `373_leave_application_form` |
| 1 | 18 + 25 + 26 | 18_displacement, 25_invisible_text, 26_text_overlap | `purchase-order` |
| 1 | 18 + 25 + 27 + 59 + 66 | 18_displacement, 25_invisible_text, 27_text_off_page, 59_shape_anchor, 66_table_cell_width | `mutual-fund-statement` |
| 1 | 18 + 27 | 18_displacement, 27_text_off_page | `balance-sheet-and-profit-loss` |
| 1 | 18 + 43 + 47 | 18_displacement, 43_within_10pt_x, 47_margins | `360_restaurant_menu` |
| 1 | 25 | 25_invisible_text | `335_msds_safety_data_sheet` |
| 1 | 43 + 47 | 43_within_10pt_x, 47_margins | `310_court_judgment` |
| 1 | 59 | 59_shape_anchor | `393_spectrum_peak_table` |

Reading the shape of this table:

- **56 documents across 37 groups** — the class is highly fragmented. The largest single group is
  8, the median group is 1. A single shared code path is not implied by the data.
- **19 of 56** fail five or more checks. For those, 60 is a passenger; fixing it changes no score.
  Only **5** fail 60 alone, and only **7** would go clean if 60 alone were fixed
  (`1334-B1` §4 reaches the same 4 + 2 + 1 = 7 by a different route).

---

## 3. What the co-failing checks say about the construct

**`18_displacement` (8 + 4 + 3 + 2 + … = 36 docs).** `18` charges *ink displaced*:
the same text, at a different place. `60` charges *the column's right edge moved*: an extent. These are
different measurements of the same page, and a document can move ink without changing the widest line,
or change the widest line without moving any ink. So co-failure is **not** evidence of a shared cause —
it is evidence of a shared *document population*. `1334-B1` §1 says the same about 60 and 59: "The
'travel together' is not a shared cause, it is a shared **document population**". That reasoning
applies verbatim to 18.

More important: `18`'s own literature in this tree is heavily instrument-laden — there are 60+ notes
on it, including `18_displacement-CENSUS-AND-TWO-INSTRUMENT-FAULTS-0015-relay.md`,
`18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md`, and
`18-guard-charges-a-rule-an-unruled-table-does-not-draw-2200-fixer.md` ("The row excess is 0.75 pt per
row *because* the renderer adds the row's own rule to it. A table whose six sides are all `w:val="nil"`
has no rule to add. The guard charges it anyway."). **A co-failure with 18 is a co-failure with a check
already known to charge for things that are not there.** It cannot upgrade 60 to "real".

**`59_shape_anchor` (16 of the 56 fail 59 and 60 together; 45 fail 59 corpus-wide).** This is the one group
where a *writer-side* construct plausibly makes 60 real. The anchored text box is emitted **inflated**:

> `float wPt = Math.max(4f, advance) * 1.12f + b.size * 1.5f;` — `DocxWriter.java:2793` (and `:3138`)
>
> "for a line of advance **A** at font size **s**, the emitted box is `box_width = 1.12·A + 1.5·s` …
> **The width we emit IS the width the text gets.**" — `1334-B1` §2

If that holds, a box 12 % + 1.5 em wider than the source line re-breaks the line and pushes its right
edge past the source's — a genuine `.docx` defect. **But `1334-B1` had no renderer**: "nothing here was
verified through Google (no corpus, no JDK, no renderer on this pod)", and it files the overrun as
"**INFERRED, NOT MEASURED (no renderer available on this pod): that a re-wrapped line in a 112 %-wide
box actually lands past the source's column edge in Google Docs**". The arithmetic (median +51.2 pt on
647 wide lines) is measured; the *rendered consequence* is not. **I therefore carry this population as
"suspected real, unverified" — not as established.** It is the most valuable thing in this file to test.

**`25_invisible_text` (14 docs).** Its own note reports 48 corpus documents
failing it and **0 of 48 failing in LibreOffice** (`25_invisible_text-CHECK-READ-THE-SHEET-0710-fixer.md`).
A check that fails half the corpus in Google and none of it in the proxy is a check with a reference
problem. 60 co-failing with 25 is a **correlation between two suspect instruments**, not a second vote
for a real defect.

**`04_chars_missing` (24 docs).** Characters lost — a real content fault, but a
different construct. Where 04 fires, the page has genuinely lost text, and 60's widest line is being
measured on a truncated column. Fixing 04 would move 60 without 60 having been wrong.

**`47_margins` / `43_within_10pt_x` (10 / 7 docs).** These are
the **strongest real candidates outside 79**. `317_rti_response` and `365_recipe_card` fail
**`47_margins` + `60` and nothing else**; `310_court_judgment` fails `43` + `47` + `60`. If the page's
margins are wrong, the text area's right edge *is* wrong, and 60 is correctly reporting it. These two
documents deserve to be checked first among the undecided — they are cheap and they are the cases where
60 and 47 agree on a construct.

**`60` alone (5 docs).** The only group that is decidable, and it is decidable because a prior slot
measured it (§4).

---

## 4. The precedent, quoted — and the test applied to 60

### 4.1 How `25_invisible_text` was shown to read the paper

The check takes the point inside a run's corner and stops at the **first** filled rect containing it:

> "A **Google PDF export opens with a page-sized white rectangle** — Google paints the sheet. On
> `10_stamp_as_image` the heading `SUPPLY ORDER ACKNOWLEDGEMENT` is white type on an orange band. In
> the export the band arrives as an **image** … so `get_drawings()` never sees it. The first fill
> containing the heading's corner is the white sheet, the heading is white, and the check counted the
> heading as invisible."
>
> "**It is not invisible.** Rendered at 110 dpi from the export and read by eye: white on orange, the
> same band, the same place, the same colour as the source."
>
> — `25_invisible_text-CHECK-READ-THE-SHEET-0710-fixer.md`

And the decisive form of the proof — **same bytes, two rules, only the rule changes**:

> "The stamp pair is the same exported PDF scored by both rules, so the difference is the rule and
> nothing else." — *ibid.* (old rule: source 0, render **1**, 41/42 → new rule: source 0, render **0**,
> **42/42**)

That is the precedent's test: **hold the artifact fixed and vary only the rule; if the verdict flips,
the rule was the fault.**

### 4.2 How `18_displacement` was shown to read a constant rather than a layout

> "Two unrelated documents land on the same **−65.6 pt**. A layout defect does not repeat to the tenth
> of a point across a radiology report and an auditor's report; a constant does."
> — `60_text_column_right_edge-IT-FIRES-UNDER-…-2322-fixer.md`

> "All four report the identical pair: **`source=0`, `render=1`**. Not 0 → 40, not 3 → 90. **One** piece
> of text crosses the column's right edge in Google and none does in the source, on four documents of
> four different kinds … A one-unit overshoot repeated across unrelated layouts reads as a constant, not
> a layout failure — the same shape as the `w:line` charge law that produced a flat 0.78 pt on every
> table in `18_displacement`."
> — `60_text_column_right_edge-STALE-ENGINE-REFUTED-ON-ALL-FOUR-2318-fixer.md`

So for `18` the discriminator is **invariance**: a defect that is the same number on unrelated
documents is a constant in the instrument or the renderer, not a property of each document's layout.

### 4.3 The same test, applied to 60

**Test A — hold the `.docx` fixed, vary only the renderer.** This is the `25` test in its strongest
form, and it was run on the four solo documents:

> "| document | LibreOffice | Google (committed) | … `302_radiology_report` | **42/42 PASS** | 41/42,
> fails 60 | `313_power_of_attorney` | **42/42 PASS** | 41/42 … `316_contract_with_schedules` |
> **42/42 PASS** | 46/47 … `321_auditors_report` | **42/42 PASS** | 41/42 … `79_inr…` | 41/42, fails 60
> | 41/42, fails 60 |"
> — `60_text_column_right_edge-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md` §1

Four of four flip on the renderer and **only** on the renderer. `79` does not flip — it fails in both.
**The verdict flips with the renderer for four documents, therefore for those four the fault is not in
the artifact.** That is the precedent's test, and it returns "instrument".

The mechanism, measured on the export:

> "The `.docx` declares `w:ascii="DejaVuSans"` (27 runs) and `w:ascii="DejaVuSerif"` (6 runs) — the
> source's own faces. **LibreOffice has DejaVu and renders it: 33 lines, first line 257.41 pt, the
> source's width to 0.2 pt.** **Google has no DejaVu**, substitutes a face it does have, and the
> substitute is **+4.8 % wider** (270.00 against 257.62), which re-breaks page 0 into **two more
> lines**, which moves the column right edges — by up to **28.6 pt** on one column (source 174.28,
> Google 202.82) — and `60` convicts the movement."
> — `0830` §2

And the check's tolerance is structurally unable to absorb it:

> "`60`'s slack is one word of the column's own text, and a face 4.8 % wider widens the word too, so
> the slack grows with the fault instead of absorbing it. That is why the check cannot pass it."
> — `0830` §2

**Test B — invariance.** `source=0, render=1` on four unrelated documents
(`STALE-ENGINE-…-2318`), and a −65.6 pt delta repeated to the tenth of a point across two of them
(`2322`). Same shape as the `18` constant. Passes the invariance test as a constant.

**Test C — the drawn-rule variant: NOT RUN, NOT SUPPORTED.** No note in 276 shows 60 consulting
drawings, shapes or rules; the code-reading note says "Reads only the text layer". The documents whose
names *suggest* a paper-side reference — `question-paper-marks-right-margin` (right-margin marks),
`25_signature_block_underscores_txtpos` (underscore signature rules), `table-with-merged-cells`,
`landscape-page-inside-portrait-document` — are the place where the drawn-rule variant could still be
true, and **none of them has been measured for it.** This is inference from document names only; I did
not open a single source PDF.

### 4.4 A contradiction the next run must resolve, not paper over

Two live Google measurements of **the same document** (`302_radiology_report`), twelve hours apart,
disagree on the **sign**:

| note | date | direction | measured delta | substituted face |
|:--|:--|:--|:--|:--|
| `…IT-FIRES-UNDER-…-2322` | 23 Nov 18:58 | **UNDER** (`render=1`, over=0) | source 543.7 → render 478.1 = **−65.6 pt** | ArialMT, "10–15 % narrower" |
| `…GOOGLE-HAS-NO-DEJAVU-0830` | 24 Nov 07:57 | **OVER** (widest line past source) | first line 257.62 → **270.00 = +4.8 %** | Calibri / Verdana / ArialMT |

Both are live round trips. Both agree on the **construct** (Google substitutes a face DejaVu-metric
text needs; the `.docx` is right in LibreOffice). They disagree on the **direction**, and therefore on
which branch fired. `1334-B1` independently claims the class is **over**, from an inflated anchored box,
with no renderer at all. **Three accounts, two directions, one construct.** I report the construct as
established and the direction as **unresolved**. Anyone quoting "60 fires under" or "60 fires over" as
a class-wide fact is quoting one of three conflicting notes.

---

## 5. What the data cannot tell me — stated plainly

1. **No values.** `RATCHET-GOOGLE.json` holds `at`, `engine`, `failed`, `passed`, `total` and nothing
   else. There is no source edge, render edge, delta, slack, or branch. Every number in §4 is quoted
   from a prior note, not recomputed here. **Every value-level claim in this file is second-hand and
   labelled as such.**
2. **No branch.** The ratchet cannot distinguish over from under, which is exactly the distinction that
   separates the two published mechanisms.
3. **`RANKING.csv` is not usable for this question.** Its columns are
   `rank, document, signature, problem, share1…share10, median_pt, p90_pt, max_pt, text_recall,
   chars_missing, worst_page, pages, colour_share, coloured_px, tone_share, order_share, font_share` —
   a per-document ink/recall ranking with **no check-level field**. It cannot be joined to 60. (Its 212
   rows do confirm the corpus size.)
4. **`BASELINE.md` must not be quoted.** Its own first line: "`<!-- RETIRED - see
   tools/p2w-bench/RETIRED.md. This file describes the check-id pipeline, which the live pipeline does
   not run. Do not read it as current. -->`" It is `u59`-universe, measured 10–13 Nov, engine
   `2a68de6`, and its rows use check ids that no longer exist (`18_median_dy`, `19_worst_dy`,
   `20_within_10pt`, `04_words_missing`). Its 213 rows are useful only as a document list.
5. **I did not measure anything.** No conversion, no upload, no export, no render, no PDF opened.
6. **The ~25 figure in the brief is not reproducible from the primary data** (56 here). Not stated
   anywhere I could find.

---

## 6. What the fixer should do next

### The single next measurement

**Cross-render all 56 documents in LibreOffice from the same `.docx`, and for each, print from the
Google export the check's own four numbers per column: `rs` (source edge), `rg` (render edge), the
slack, the branch fired — together with the declared face, the face in the export, and the line count
per page.** That is one table, 56 rows, no new code beyond calling the check's existing
`columns()`/`edge()` on both exports.

It is decisive because it turns the undecided 51 into a 2×2:

| | fails 60 in **both** renderers | fails 60 in **Google only** |
|:--|:--|:--|
| **face unchanged, line count unchanged** | **REAL** — a `.docx` geometry defect | instrument (something else in the export) |
| **face substituted and/or line count changed** | **REAL** (the writer named a face LO lacks) | **INSTRUMENT** — the renderer's substitution |

Predicted outcome, from `0830`'s four-of-five and `1334-B1`'s anchored-box arithmetic: the
Google-only / face-substituted cell takes the large majority, and the both-renderers cell takes `79`
plus most of the `18+59` and `47+60` groups. **If that prediction holds, the verdict stands as (c)
MIXED with a large instrument majority.**

### Concrete order of work

1. **Take `79_inr_indian_digit_grouping_table` now.** It is the one measured real defect, it fails in
   both renderers, and `0830` §1 names its column. One document, no ambiguity.
2. **Check `317_rti_response` and `365_recipe_card` next** — they fail `47_margins` + `60` and nothing
   else, so the margin fix and the column fix are the same fix. Cheapest real win in the class.
3. **Test the anchored-box inflation on the 16 `59`-co-failing documents.** `1334-B1`'s proposal B
   (`1.12·A + 1.5·s` → `A + 0.5·s` at `DocxWriter.java:2793` and `:3138`) is the only writer-side
   construct that would make 60 real at scale, and it has never been rendered. Accept only on: 60
   falls, `04_chars_missing` and `17_matched_runs` do not rise (the anti-clip reason at `:3116-3125` is
   real — file 69's "8. The job worker…" became "8." in a 19 pt box), no document regresses.
4. **Do not loosen 60 for the four Google-only documents in isolation.** `0830` §5.4 already warned:
   "**It is not a loosening of `60` for the four documents in isolation — any such change must be
   stated as a rule about extent-versus-substitution and re-measured on the whole class.**" I agree,
   and the rule should be: *60 excludes a column whose edge movement is fully accounted for by a face
   the renderer does not carry* — measurable as "line count changed, face changed, geometry otherwise
   reproduced in the proxy".
5. **Record the branch in the ratchet.** `failed: [ids]` loses the over/under distinction that three
   notes disagree about. A `detail` map of `{id: value}` would have settled §4.4 without a render.

---

## 7. What would refute this verdict

**Refutes the instrument reading (would make it (a) REAL DEFECT):**

- A document that fails 60 in Google **and** fails it in LibreOffice **on the same `.docx`**, with the
  source's own face rendered, the same line count, and the same column edge — i.e. the 2×2's
  top-left cell populated by more than `79`. If that cell is large, the class is real and my majority
  reading is wrong.
- A Google export of one of the four solo documents that carries the declared face (or DejaVu metrics)
  and **still** fails 60. `0830` §4 tried the embedded-face route and it refuted itself — the export
  was "the same render" (35 lines, 270.00 pt, Calibri/Verdana/ArialMT, 81,521 bytes vs 81,526). The
  naming route is what `0830` §2–3 measures. A third route that lands DejaVu metrics in the export and
  still fails 60 would put the fault back in the engine.
- Evidence that 60 reads `get_drawings()` or a page-edge rather than the text layer — that would make
  the drawn-rule variant true, which would *support* instrument but **change the mechanism I have
  stated**, and the finding would need rewriting, not merely confirming.
- A 60 failure whose `rs` equals the source page's **text-area right edge exactly** and whose `rg`
  differs, on a document that passes every position check — that is a column defect with no
  displacement, which the data cannot currently distinguish from an artefact.

**Refutes the MIXED split (would make it (b) INSTRUMENT, cleanly):**

- The 2×2 coming back with **only** the face-substituted column populated — no both-renderers rows
  except `79`, which would then be an outlier to be moved to `04`/`47` rather than counted in 60.

**Refutes the "one real document" claim:**

- `79_inr_indian_digit_grouping_table` passing 60 in LibreOffice on a current engine. It is recorded at
  41/42 in LibreOffice in `0830` §1, but that measurement is one slot old and was not re-run here.

---

## 8. Provenance of every claim in this file

| claim | source | measured or inferred |
|:--|:--|:--|
| 56 of 190 fail 60; the 37-group table; all co-failure counts | `RATCHET-GOOGLE.json`, this run | **measured here** (pass/fail only) |
| 213-row corpus; `RATCHET` covers 190; 23 refused | `BASELINE.md` row count + `1334-B1` §4 | measured (count) / quoted (attribution) |
| 60 reads only the text layer; `RIGHT_OVERRUN` 6.0, `RIGHT_UNDERRUN` 8.0, `SLACK_CAP` 40.0; `verify_google.py:2597-2673` | `1334-B1` §1 | **quoted** — I have no code |
| 4 solo docs pass 42/42 in LibreOffice, fail only in Google | `0830` §1 | **quoted** — live Google round trips in that slot |
| DejaVu declared, Calibri/Verdana/Arial rendered, +4.8 % wider, 33 → 35 lines | `0830` §2 | **quoted** |
| embedded face does not survive Google | `0830` §4 | **quoted** |
| `source=0, render=1` on all four; −65.6 pt constant; Arial 10–15 % narrower | `2322` | **quoted** |
| anchored box `1.12·A + 1.5·s`; median +51.2 pt on 647 wide lines | `1334-B1` §2, §6 | arithmetic measured, **rendered consequence explicitly inferred by its own author** |
| 25 fails 48 docs in Google, 0 in LibreOffice; first-fill vs topmost-fill | `25_invisible_text-CHECK-READ-THE-SHEET-0710-fixer.md` | **quoted** |
| `79` is the one real defect in the solo five | `0830` §1, §5.3 | **quoted** |
| anything about a drawn rule, page edge, or ornament as 60's reference | **no source** | **inference from document names only — flagged, not used** |

---

*Analyst, read-only. No engine change, no patch, no render, no upload. Nothing in this file was
measured against a PDF.*
