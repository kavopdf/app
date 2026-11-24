# `04_chars_missing` — writer defect, instrument artefact, or already explained?

**Measured 24 Nov 2026 from `RATCHET-GOOGLE.json` (190 scored documents), `RANKING.csv` and the 276
notes in `FINDINGS/`. No build, no Google round trip, no engine edit. Every number below is
recomputed from those files; every number quoted from a note is labelled as such.**

## Verdict

**(a) REAL WRITER DEFECT — construct-level, not text-level.** The converter does not lose a single
character into the `.docx`: on **63 of the 65** documents that fail `04_chars_missing`, `RANKING.csv`
reports `chars_missing = 0` and `text_recall = 100.0` against the `.docx`, so the source's characters
are all there. What drops them is the construct the writer chose to carry them: text emitted inside an
anchored DrawingML shape (`<wps:txbx><w:txbxContent>`), which Google Docs rasterises on import so the
characters arrive as pixels and never enter the export's text layer. Shared code path
(`DocxWriter.anchorShape()`), proven causally on one document, correlated on 53 more, and fixable by a
construct change the notes already specify.

Two of the 65 are a *different* writer defect each (faux-bold triple draw; a widget `/AP` appearance
stream), and nine have no assigned mechanism. **It is not (b):** the check is not counting characters
the source lacks — the source has them, the `.docx` has them, and a second importer (LibreOffice)
reads every one of them back. **It is not (c):** the t01/t12 instrument notes explain **none** of the
65 through ligature identity, FFFD cmap, control characters or annotation text; every document where
those four mechanisms were actually measured *passes* `04_chars_missing`.

### The caveat that must travel with that verdict

If "writer defect" is defined strictly as *characters absent from the `.docx`*, then only **2 of 65**
qualify (`38_faux_bold_italic_synthesised`, 19 chars; `601_fillable_admission_form`, 2 chars) and the
honest answer for the other 63 is "a writer defect against the target renderer, not against the
file". The three-way choice offered cannot express that distinction, so it is stated here rather than
hidden inside the label. For the stamp and rotated-page documents the shape is not even avoidable —
OOXML has no other construct that carries a rotation angle — so for those the correct label is a
deliberate trade, not a defect. (The census lists 16 documents that carry both the drop and the hide
constructs; the stamps and rotated pages are the bulk of them.)

---

## 1. The failing population

`RATCHET-GOOGLE.json` holds **190** documents (the 213-PDF corpus less the 23 refused on page count),
all stamped `2026-11-24T04:36:24+05:30`; **161** fail at least one check and **29** are clean.
`passed + len(failed) == total` holds on all 190 — no inconsistency in the file.

Documents whose `failed` array contains `04_chars_missing`: **65** (40.4 % of the 161 failing,
34.2 % of 190).

Three properties of that 65 that constrain any attribution:

| property | value | consequence |
|---|---|---|
| engine | `b7699196` 61, `462353f` 3, `5beb8b9d` 1 | a mixed-build set; not one engine's result |
| denominator (`total`) | 42 → 45 docs, 47 → 19, 44 → 1 | the 65 are counted out of three different universes, so failed-check counts are not comparable across them |
| sole failure | **0** documents | no document isolates the check; every attribution is joint by construction |

Failed-check-count distribution inside the 65: 2 → 4 docs, 3 → 8, 4 → 16, 5 → 8, 6 → 11, 7 → 9,
8 → 5, 9 → 2, 10 → 2.

### Grouped by the exact set of co-failing checks

**56 distinct co-failure sets: 6 shared by more than one document, 50 singletons.** The six:

| documents | co-failing set |
|---:|---|
| 3 | `13_text_colours`, `18_displacement`, `25_invisible_text`, `35_rotation`, `59_shape_anchor` |
| 3 | `18_displacement`, `44_header_footer` |
| 3 | `44_header_footer`, `45_char_accuracy` |
| 2 | `18_displacement`, `27_text_off_page`, `60_text_column_right_edge` |
| 2 | `18_displacement`, `45_char_accuracy`, `60_text_column_right_edge` |
| 2 | `44_header_footer` |

The other 50 documents each fail a set no other document fails, so "the co-failing set" is not a
useful grouping key here — the useful structure is frequency:

| co-failing check | documents (of 65) |
|---|---:|
| `45_char_accuracy` | 36 |
| `18_displacement` | 34 |
| `13_text_colours` | 31 |
| `44_header_footer` | 27 |
| `60_text_column_right_edge` | 24 |
| `59_shape_anchor` | 23 |
| `17_matched_runs` | 23 |
| `25_invisible_text` | 16 |
| `35_rotation` | 12 |
| `47_margins` | 10 |

`04` and `45_char_accuracy` co-fail on 36 of 37 documents that fail `45` — two character checks inside
the *same* Google instrument almost never disagree, which is what you expect if they read one
construct. The 29 documents that fail `04` without `45` mean `04` is the more sensitive of the two.

### The brief's "~14 clean documents" is not in this file

`04_chars_missing` is the **sole** failure on **0** documents, so fixing it alone cleans **nothing**
(this reproduces `18_displacement-SOLE-FAILURE-13-DOCS-0120-agentA.md`, which ranks it 8th with a
0.0 % last-blocker share). Only four documents fail exactly two checks, one of them `04`:
`27_two_column_left_short_txtpos` (+`44_header_footer`), `61_two_col_abstract_spanning`
(+`44_header_footer`), `411_nested_xobject_transforms` (+`17_matched_runs`),
`38_faux_bold_italic_synthesised` (+`60_text_column_right_edge`). **The computable ceiling for
`04` is 4, not 14** — and one of the four is a different mechanism. I could not find 14 by any
route through this file and do not know where the figure comes from.

---

## 2. Against the t01/t12 notes: what is already explained, what is new

The t01/t12 corpus names **15** documents across its four mechanisms (ligature identity at Effra CIDs
0x123/0x124/0x126/0x127, FFFD cmap, control characters, annotation text outside the source reader).
**12 of the 15 are in this 190-document set**; three are not (`041122-Account_Opening_Form`,
`Account_Opening_Form_Fillable_filled`, `05_round_company_seal_curved_text` — the first two are absent
from the ratchet entirely, the third has no row).

| t01/t12 document | mechanism (per note) | fails `04`? | `chars_missing` vs `.docx` |
|---|---|:--:|---:|
| `79_inr_indian_digit_grouping_table` | U+0000 control chars | **no** | 0 |
| `391_survey_questionnaire_grid` | U+0000 control chars | **no** | 0 |
| `392_statistical_console_output` | U+0000 control chars | **no** | 0 |
| `406_passport_mrz_page` | U+0000 control chars | **no** | 0 |
| `39_small_caps_letter_spacing` | letter-spaced run re-tokenisation | **no** | 0 |
| `77_arabic_rtl_document` | RTL order/segmentation | **no** | 0 |
| `600_reviewed_invoice_with_annotations` | annotation `/Contents` | **no** | 0 |
| `journal-2col-with-footnotes` | duplicate across columns | **no** | 0 |
| `12_stamp_across_page_break` | page-break duplication | **no** | 0 |
| `38_faux_bold_italic_synthesised` | faux-bold triple draw *(not a t01/t12 mechanism)* | **yes** | **19** |
| `601_fillable_admission_form` | widget `/AP` tick *(not a t01/t12 mechanism)* | **yes** | **2** |
| `311_fir_police_form` | cell welding, `60067Mobile` (t12) | **yes** | 0 |

**Already explained by the t01/t12 notes: 0 of 65.** Every document where ligature identity, FFFD,
control characters or annotation text was actually measured passes `04_chars_missing` — nine for nine.
That is a negative control, and it is the strongest single piece of evidence in this file: the four
instrument mechanisms of t01/t12 are *latent* risks for `04`'s source side (which shares the same
`page.get_text()`/`glyph_truth()` reader) and none of them currently fires.

**Already explained by other notes: 2 of 65**, and both are engine-side, not instrument-side:

- `38_faux_bold_italic_synthesised` — the same line drawn three times, fill/fill/stroke
  (`38-faux-bold-TRIPLE-DRAW-0225-fixer.md`). Its 19 missing characters also reproduce in the
  LibreOffice render, so they are lost before Google sees the file. Sub-mechanism not stated.
- `601_fillable_admission_form` — a tick drawn in a checkbox widget's `/AP /N` appearance stream,
  which `PDFTextStripper` does not process (`601-tick-is-a-widget-appearance-2342.md`). Its 2
  characters likewise reproduce in LibreOffice.

**New: 63 of 65.** Of those, **54** are attributed by the standing census to the anchored-shape
construct (`04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent.md`: `w:txbxContent`
present in 54 of 65 `04` failures and in 54 of 54 documents carrying shape text, 0 of 30 clean), and
**9** have no mechanism assigned by any note:

`25_signature_block_underscores_txtpos`, `381_incident_report_timeline`, `383_api_docs_page`,
`417_rotate180_and_mirrored`, `58_header_rule_footer_rule`, `602_bookmarked_annual_report`,
`form16-part-b`, `table-across-page-break-repeated-header`, `very-long-single-column-table`.

All nine have `chars_missing = 0` and `text_recall = 100.0` — the `.docx` holds every character and
LibreOffice reads them back, so they sit in the same "render-only loss" bucket as the 54; only the
construct is unknown. The TXBX census names the same nine and says so plainly: *"None of the candidate
families in §4 fires on them either, so whatever they are, it is not in that list."*

One document needs a warning: `311_fir_police_form` is in the t12 table for cell welding, and it
**does** fail `04`. It is not the same fault. Welding joins two tokens with no separator; it loses no
character, and `RANKING.csv` confirms `chars_missing = 0`. Its `04` failure belongs to the shape
group (the census lists it as a `w:txbxContent` carrier), not to t12.

---

## 3. Is `04_chars_missing` the same construct as `t01_word_accuracy` / `t12_word_invention`?

**No — a separate construct, sharing a source-side reader.** Five pieces of evidence, strongest first.

1. **They measure different artefacts at different stages.** `t12` quotes its own definition: *"The
   check (`verify_txt.py`, unmodified) counts `txt_words - src_words` as a multiset, after stripping
   surrounding punctuation and folding case… The source side is `page.get_text()`."* That reads the
   **`.docx`/`.txt` the writer produced**. `04_chars_missing` is a Google check: the `.docx` goes to
   Drive, is converted and exported as PDF, and the export's text layer is compared to the source.
   A check that reads the file cannot observe a loss that is not in the file.
2. **63 of 65 have nothing for a `.txt` check to find.** `chars_missing = 0` and
   `text_recall = 100.0` against the `.docx` means `t01`/`t12` would pass these documents while `04`
   fails them. A construct that is invisible to one instrument and fires on 63 documents of the other
   is not the same construct.
3. **The populations barely overlap.** t01 names 10 documents, t12 names 12; `04` fails 65 of 190.
   Three documents appear in both, and for two of those the `04` cause is a mechanism neither t01 nor
   t12 discusses (see §2).
4. **Direction differs.** `t01` is missing words, `t12` is *invented* words, `04` is missing
   characters. The Google-side twin of `t12` is `05_chars_extra` (5 documents here), not `04`.
5. **What they do share is the source side.** Both compare against `page.get_text()`/`glyph_truth()`,
   so the FFFD and ligature defects described in the t01 notes are a *hazard* for `04` — the same
   wrong `Ĥll` would be counted as source text that the render lacks. The negative control in §2
   shows that hazard is not currently firing on any `04` failure in this set.

---

## 4. The evidence that decides (a) over (b)

| # | evidence | value | what it rules out |
|---:|---|---|---|
| 1 | `RANKING.csv` `chars_missing` over the 65 | **0 on 63**, 19 on `38_faux_bold`, 2 on `601_fillable`, **sum 21** | the converter dropping characters into the `.docx`; and (b), since the source's characters are all accounted for |
| 2 | The same 63 pass `04` in LibreOffice with a render count of 0 *(quoted: `gverify-lo` census in the TXBX-REFUTED note; not in this sandbox)* | 63 of 65 | the characters being absent from the artefact — a second importer reads every one |
| 3 | `27_two_column_left_short_txtpos` — the only causal Google measurement in the corpus: 43 characters missing, both missing lines in the document's only 2 text boxes, `w:txbxContent` 4 → 0 took it from **40/42 FAIL to 42/42 PASS** | n = 1, exact | that the missing multiset and the shape-text multiset are different sets, on this document |
| 4 | `w:txbxContent` census: present in 54/65 `04` failures, 54/54 shape-text carriers, **0/30** Google-clean; 14,449 of 84,364 chars (17.1 %) live inside shape text *(quoted from the TXBX note; needs the corpus and a build, not recomputable here)* | 54 of 65 | that the construct is incidental — no clean document carries it |
| 5 | Nine t01/t12-measured documents (control chars, FFFD, ligature, annotation) all **pass** `04` | 9 of 9 | (b) as currently instantiated: none of the known source-side artefacts produces a `04` failure |
| 6 | `04` and `45_char_accuracy` co-fail on 36 of 37 | 36 | that `04` is an isolated threshold artefact — it tracks a second character check in the same instrument |

Why (b) fails as a whole: (b) would require the check to count characters the source does not
contain. The only committed per-document measure of "what the source contains that the artefact
lacks" is `RANKING.csv`, and it is **0** on 63 of 65. The characters are real, they are in the
`.docx`, and they are absent from Google's export — that is a loss in the render, not a phantom in
the check.

Why (c) fails as a whole: (c) would require these to be the known unrecoverable ones. Two are known,
and by notes outside t01/t12. Fifty-four have a named construct, a named emitter
(`DocxWriter.anchorShape()`) and a named fix (put text and the fill behind it in the flow; leave only
genuinely floating geometry as a shape — `RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md`
§6, `04_chars_missing-…-TXBX-IS-RASTERISED-1750-agent.md` §6). Nine have no mechanism at all. That is
not "no new work".

---

## 5. Next measurement — the single cheapest one

**One Google round trip on `66_two_col_footnotes_bottom`, with the export's text layer dumped and
diffed against the source, plus a count of its `w:txbxContent` characters.**

Why this document and not another: its footnote text exists **only** inside `w:txbxContent` — the
census checked every string against the source PDF (all present) and against the rest of
`document.xml` (no second copy in the flow). Its `.docx` is complete (`chars_missing = 0`), LibreOffice
renders it 42/42, and 448 characters sit in the box. So there is exactly one candidate for the missing
set, and one document settles the mechanism that 54 documents are currently only *correlated* with.
It costs one upload, one export, one text extraction — no build, no engine change.

**Result that would refute this verdict:** the export's missing characters include any string that is
**not** inside a `w:txbxContent` run, or the missing count is not 448. Either outcome means characters
are leaving somewhere other than the shape, and (a) as scoped here is wrong.

Cheaper still, and already free: the nine group-(e) documents need the same dump, and the cheapest of
those is `417_rotate180_and_mirrored` (census deficit 8 characters). One such dump showing its missing
characters inside a shape would move it into the construct group and take the undetermined count from
9 to 8; one showing them anywhere else is a second, independent defect.

**What would not settle anything:** any LibreOffice measurement. LibreOffice passes `04` on 63 of 65;
only a Google round trip can move a document between the groups.

---

## 6. Falsifiers, stated as tests

1. **A Google text-layer dump for `66_two_col_footnotes_bottom`** whose missing set is not the 448
   box characters. Refutes (a) for the 54.
2. **A re-census of `w:txbxContent` at HEAD** finding shape text in some of the nine group-(e)
   documents. The 54/11 split is a single-source claim I could not recompute here; if
   `anchorShape()` also writes through an `mc:Fallback` VML `w:pict` path, or a second emitter exists,
   the population changes and (a)'s scope collapses.
3. **A per-character equality over all 54.** If any of the 54 has a missing multiset containing
   characters that are not in a text box, the construct explains only part of the class — and 17.1 %
   shape share leaves large room for that.
4. **A `04` failure on a document with `chars_missing > 0` beyond the two known ones.** That would be
   text loss in the `.docx` and would move that document from (a)-construct to a genuine extraction
   defect.
5. **A Google run at HEAD.** 186 of the 190 verdicts are `b7699196` and 61 of the 65 `04` failures are
   `b7699196`; the census was taken on a different build. A re-measure could change the population
   without any code change.

---

## 7. Method and limits

- **Computed here**, from `RATCHET-GOOGLE.json`: the failing set (65), the engine and `total`
  distributions, `passed + len(failed) == total` on all 190, the 56 co-failure groups and their
  sizes, the co-failure frequency table, the sole-failure count (0), the exactly-two-check set (4),
  the 29 clean documents, and the overlap with the t01/t12 document list.
- **Computed here**, from `RANKING.csv`: `chars_missing` and `text_recall` for all 65 (65/65 coverage,
  no missing rows), sum 21, the 63/19/2 split, and every value in the appendix.
- **Quoted, not recomputed** (each needs the 213-PDF corpus and an engine build, neither available
  here): the per-document presence of `w:txbxContent` (54/65, and the 11 named non-carriers); the
  14,449/84,364 character total; the LibreOffice `04` render counts (63 of 65 at 0); the
  `27_two_column_left_short_txtpos` Google round trip; the two engine-side mechanisms for `38` and
  `601`.
- **Not determinable from this sandbox:** the Google-side missing-character *count* for any document
  (`RATCHET-GOOGLE.json` is pass/fail only — it has no `checks` object, no `measured`, no render
  dump), and therefore any per-document character-level claim. `chars_missing` in `RANKING.csv`
  measures source vs **`.docx`**, not source vs Google — every inference drawn from it is labelled.
- **Inference, flagged as such:** that the 54 census carriers' `04` failures are caused by the shape
  (proven on 1, correlated on 53); that the nine group-(e) documents are render-only losses (inferred
  from `chars_missing = 0` plus the LibreOffice pass, mechanism unknown); that `04` and
  `45_char_accuracy` read one construct (inferred from a 36/37 co-failure rate, not from their
  definitions — no note quotes either definition in full).
- No input file was modified. Nothing was built, converted, or uploaded.

---

## Appendix — all 65 documents

`total` = that document's check count (the universes differ: 42, 44, 47). `cm` = `RANKING.csv`
`chars_missing` (source vs `.docx`). `tag` = `e` for the nine with no assigned mechanism, `t01/t12`
for a document named in the t01/t12 notes.

| # | document | total | engine | cm | text_recall | tag | other failing checks |
|---:|---|---:|---|---:|---:|:--:|---|
| 1 | `01_stamp_rotated_15deg_upright` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 25_invisible_text, 35_rotation, 59_shape_anchor |
| 2 | `02_stamp_rotated_15deg_upleft` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 25_invisible_text, 35_rotation, 59_shape_anchor |
| 3 | `03_stamp_vertical_90deg` | 44 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 35_rotation, 59_shape_anchor, 62_table_columns, 63_table_rows |
| 4 | `04_stamp_180deg_upside_down` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 25_invisible_text, 35_rotation, 59_shape_anchor |
| 5 | `06_rect_paid_stamp_red_transparent` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 35_rotation |
| 6 | `07_stamp_over_table` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 25_invisible_text, 26_text_overlap, 35_rotation, 43_within_10pt_x, 47_margins |
| 7 | `08_two_overlapping_stamps` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 35_rotation, 45_char_accuracy |
| 8 | `09_stamp_font_not_embedded` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 35_rotation, 59_shape_anchor |
| 9 | `11_stamp_with_signature_image` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 35_rotation, 45_char_accuracy |
| 10 | `13_stamp_non_english` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 18_displacement, 35_rotation, 45_char_accuracy, 59_shape_anchor |
| 11 | `14_stamp_chars_positioned_td` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 25_invisible_text, 45_char_accuracy, 60_text_column_right_edge |
| 12 | `15_stamp_on_scanned_page` | 42 | 5beb8b9d | 0 | 100.0 | — | 10_font_sizes, 13_text_colours, 17_matched_runs, 31_pages_lost_their_text, 35_rotation, 44_header_footer, 45_char_accuracy, 59_shape_anchor |
| 13 | `20_numbered_list_separate_column_txtpos` | 42 | b7699196 | 0 | 100.0 | — | 17_matched_runs, 44_header_footer, 45_char_accuracy |
| 14 | `25_signature_block_underscores_txtpos` | 42 | b7699196 | 0 | 100.0 | e | 18_displacement, 45_char_accuracy, 60_text_column_right_edge |
| 15 | `27_two_column_left_short_txtpos` | 42 | b7699196 | 0 | 100.0 | — | 44_header_footer |
| 16 | `28_value_overflows_cell_txtpos` | 42 | b7699196 | 0 | 100.0 | — | 43_within_10pt_x, 45_char_accuracy, 47_margins, 59_shape_anchor, 60_text_column_right_edge |
| 17 | `311_fir_police_form` | 47 | b7699196 | 0 | 100.0 | t01/t12 | 18_displacement, 45_char_accuracy, 60_text_column_right_edge |
| 18 | `312_affidavit_stamp_paper` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 60_text_column_right_edge |
| 19 | `318_court_summons_form` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 43_within_10pt_x, 45_char_accuracy, 47_margins, 59_shape_anchor, 60_text_column_right_edge |
| 20 | `322_mutual_fund_factsheet` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 26_text_overlap, 44_header_footer, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| 21 | `323_credit_card_statement` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 45_char_accuracy, 60_text_column_right_edge, 66_table_cell_width |
| 22 | `330_cad_drawing_sheet` | 47 | b7699196 | 0 | 100.0 | — | 18_displacement, 45_char_accuracy, 47_margins |
| 23 | `331_pid_diagram` | 42 | b7699196 | 0 | 100.0 | — | 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 47_margins, 59_shape_anchor |
| 24 | `344_customs_declaration` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 25_invisible_text, 59_shape_anchor, 60_text_column_right_edge |
| 25 | `352_certificate_ornate_border` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 45_char_accuracy, 60_text_column_right_edge |
| 26 | `364_event_ticket` | 42 | b7699196 | 0 | 100.0 | — | 25_invisible_text, 45_char_accuracy, 59_shape_anchor |
| 27 | `371_experience_certificate` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| 28 | `381_incident_report_timeline` | 47 | b7699196 | 0 | 100.0 | e | 18_displacement, 25_invisible_text, 60_text_column_right_edge |
| 29 | `383_api_docs_page` | 47 | b7699196 | 0 | 100.0 | e | 18_displacement, 25_invisible_text, 47_margins, 59_shape_anchor, 60_text_column_right_edge, 66_table_cell_width |
| 30 | `38_faux_bold_italic_synthesised` | 42 | b7699196 | 19 | 98.01 | t01/t12 | 60_text_column_right_edge |
| 31 | `400_comic_page_speech_bubbles` | 42 | b7699196 | 0 | 100.0 | — | 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor |
| 32 | `411_nested_xobject_transforms` | 42 | b7699196 | 0 | 100.0 | — | 17_matched_runs |
| 33 | `417_rotate180_and_mirrored` | 42 | b7699196 | 0 | 100.0 | e | 17_matched_runs, 18_displacement, 27_text_off_page |
| 34 | `43_red_stamp_over_black_text` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 35_rotation |
| 35 | `46_chart_coloured_labels_body_text` | 42 | b7699196 | 0 | 100.0 | — | 44_header_footer, 45_char_accuracy |
| 36 | `54_two_column_body_full_width_header_footer` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 25_invisible_text, 44_header_footer, 45_char_accuracy |
| 37 | `55_sidebar_box_beside_body` | 42 | b7699196 | 0 | 100.0 | — | 44_header_footer, 45_char_accuracy |
| 38 | `58_header_rule_footer_rule` | 42 | b7699196 | 0 | 100.0 | e | 18_displacement, 27_text_off_page, 44_header_footer |
| 39 | `601_fillable_admission_form` | 42 | b7699196 | 2 | 99.58 | t01/t12 | 18_displacement, 51_field_values, 53_embedded_faces, 59_shape_anchor |
| 40 | `602_bookmarked_annual_report` | 42 | b7699196 | 0 | 100.0 | e | 18_displacement, 27_text_off_page, 52_outline |
| 41 | `61_two_col_abstract_spanning` | 42 | b7699196 | 0 | 100.0 | — | 44_header_footer |
| 42 | `62_two_col_newsletter_pull_quote` | 42 | b7699196 | 0 | 100.0 | — | 25_invisible_text, 44_header_footer, 45_char_accuracy |
| 43 | `65_two_col_full_width_figure_caption` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| 44 | `66_two_col_footnotes_bottom` | 42 | b7699196 | 0 | 100.0 | — | 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy |
| 45 | `67_two_col_with_sidebar` | 42 | b7699196 | 0 | 100.0 | — | 44_header_footer, 45_char_accuracy |
| 46 | `69_two_col_legal_numbered_clauses` | 42 | b7699196 | 0 | 100.0 | — | 10_font_sizes, 13_text_colours, 17_matched_runs, 38_list_markers, 44_header_footer, 45_char_accuracy |
| 47 | `70_magazine_drop_cap_photo_caption` | 42 | b7699196 | 0 | 100.0 | — | 18_displacement, 44_header_footer |
| 48 | `80_gstin_pan_cin_ifsc_table` | 42 | b7699196 | 0 | 100.0 | — | 17_matched_runs, 18_displacement, 44_header_footer, 45_char_accuracy, 59_shape_anchor |
| 49 | `academic-paper-ieee-2col-abstract` | 47 | b7699196 | 0 | 100.0 | — | 17_matched_runs, 18_displacement, 27_text_off_page, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| 50 | `admit-card` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 45_char_accuracy, 59_shape_anchor |
| 51 | `delivery-challan` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement, 25_invisible_text, 26_text_overlap, 60_text_column_right_edge |
| 52 | `form16-part-b` | 47 | b7699196 | 0 | 100.0 | e | 18_displacement, 27_text_off_page, 60_text_column_right_edge |
| 53 | `gst-invoice-horizontal-rules-only` | 42 | b7699196 | 0 | 100.0 | — | 18_displacement, 26_text_overlap, 44_header_footer, 45_char_accuracy, 60_text_column_right_edge |
| 54 | `magazine-2col-pullquote-spanning` | 42 | 462353f | 0 | 100.0 | — | 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 43_within_10pt_x, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| 55 | `newsletter-3col-header-footer` | 42 | b7699196 | 0 | 100.0 | — | 18_displacement, 25_invisible_text, 44_header_footer, 45_char_accuracy, 59_shape_anchor |
| 56 | `newspaper-2col-fullwidth-headline` | 42 | 462353f | 0 | 100.0 | — | 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 45_char_accuracy |
| 57 | `one-page-rotated-180-degrees` | 47 | b7699196 | 0 | 100.0 | — | 18_displacement, 27_text_off_page, 43_within_10pt_x, 44_header_footer, 60_text_column_right_edge, 62_table_columns, 63_table_rows |
| 58 | `policy-2col-spanning-section-heading` | 42 | b7699196 | 0 | 100.0 | — | 10_font_sizes, 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| 59 | `property-tax-receipt` | 47 | b7699196 | 0 | 100.0 | — | 13_text_colours, 18_displacement |
| 60 | `report-2col-table-spanning-both-columns` | 47 | b7699196 | 0 | 100.0 | — | 18_displacement, 44_header_footer |
| 61 | `table-across-page-break-repeated-header` | 47 | b7699196 | 0 | 100.0 | e | 18_displacement, 27_text_off_page, 60_text_column_right_edge |
| 62 | `table-inside-two-column-page` | 47 | b7699196 | 0 | 100.0 | — | 18_displacement, 44_header_footer |
| 63 | `table-of-contents-dot-leaders` | 42 | b7699196 | 0 | 100.0 | — | 44_header_footer, 45_char_accuracy, 47_margins |
| 64 | `table-with-rotated-header` | 47 | b7699196 | 0 | 100.0 | — | 18_displacement, 45_char_accuracy, 47_margins, 59_shape_anchor |
| 65 | `very-long-single-column-table` | 47 | 462353f | 0 | 100.0 | e | 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 60_text_column_right_edge |