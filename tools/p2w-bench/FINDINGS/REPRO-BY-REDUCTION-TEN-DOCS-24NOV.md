# Minimal repros by REDUCTION, from real KavoPDF corpus documents

Tool: `tools/p2w-bench/reduce-repro.py` (new, added by this run). Nothing in
`app/src/main/java/com/kavopdf/app/engine/` was read-modify-written; `git status` on that
directory is empty. Nothing in the repository was deleted.

## 0. The one-sentence warning that applies to every number below

**There is no Google Docs in this sandbox.** Every reduced file below is a real document that
still *carries* the construct its original carried. **None of them is shown to still fail in
Google Docs**, and a reduction may have removed the real cause. Everything in section 4 is
what was actually measured; everything not in section 4 is unverified.

## 1. What the corpus offers: documents failing exactly ONE check

`benchmarks/gverify/*.json`, 213 files: 22 are `page_count_refused` and were never scored; 24
fail exactly one check. Those 24 are the reduction candidates (the single failure is
unambiguous). **All 24 are one-page PDFs** - measured with PyMuPDF - so page-level reduction is
available on none of them; it is exercised separately on `412_page_labels_roman` (5 pages),
which fails two checks and is therefore a machinery demo, not a repro candidate.

| document | single failing check | PDF pages |
|---|---|---|
| 16_right_aligned_amounts_txtpos | 18_displacement | 1 |
| 31_times_body_arial_headings | 18_displacement | 1 |
| 36_embedded_subset_font | 18_displacement | 1 |
| 68_journal_wide_table_spanning | 18_displacement | 1 |
| 71_invoice_space_aligned_no_rules | 18_displacement | 1 |
| 72_bank_statement_no_rules_right_amounts | 18_displacement | 1 |
| 74_balance_sheet_indented_subitems | 18_displacement | 1 |
| balance-sheet-two-columns-of-figures | 18_displacement | 1 |
| bus-timetable-station-left-times-right | 18_displacement | 1 |
| insurance-policy-schedule | 18_displacement | 1 |
| mobile-bill | 18_displacement | 1 |
| table-with-no-header-row | 18_displacement | 1 |
| two-tables-stacked-with-no-gap | 18_displacement | 1 |
| 302_radiology_report | 60_text_column_right_edge | 1 |
| 313_power_of_attorney | 60_text_column_right_edge | 1 |
| 316_contract_with_schedules | 60_text_column_right_edge | 1 |
| 321_auditors_report | 60_text_column_right_edge | 1 |
| 79_inr_indian_digit_grouping_table | 60_text_column_right_edge | 1 |
| 391_survey_questionnaire_grid | 17_matched_runs | 1 |
| 392_statistical_console_output | 47_margins | 1 |
| 407_id_card_front_back | 32_stroke_lines | 1 |
| 49_coloured_background_block_paragraph | 32_stroke_lines | 1 |
| 48_form_coloured_border_coloured_values | 59_shape_anchor | 1 |
| 52_one_cm_margin_wide_body | 59_shape_anchor | 1 |

## 2. What was reduced, and by how much

Ten documents were converted with the repo's own engine (`tools/engine-verify/ConvertAll`, engine
sources at HEAD, JDK 17 from `jdk-fetch.sh`), then reduced. Nine are single-failure candidates;
`412_page_labels_roman` is the page-reduction demo.

Guard = **carrier**: at least one child carrying the construct survives byte-identical (the
element the construct is written in is protected; other instances may go). `--rows --runs` were
on, so table rows and individual runs were also removable.

| document | check preserved | bytes | document.xml bytes | paragraphs | tables | rows | pages |
|---|---|---|---|---|---|---|---|
| table-with-no-header-row | 18_displacement | 7224 -> 4111 (**-43.1%**) | 105147 -> 1477 (-98.6%) | 6 -> 1 | 1 -> 0 | 26 -> 0 | 1 -> 1 |
| 72_bank_statement_no_rules_right_amounts | 18_displacement | 6507 -> 4052 (**-37.7%**) | 47062 -> 1202 (-97.4%) | 9 -> 1 | 1 -> 0 | 18 -> 0 | 1 -> 1 |
| 16_right_aligned_amounts_txtpos | 18_displacement | 6682 -> 4031 (**-39.7%**) | 51620 -> 1188 (-97.7%) | 9 -> 1 | 1 -> 0 | 13 -> 0 | 1 -> 1 |
| mobile-bill | 18_displacement | 11446 -> 4074 (**-64.4%**) | 108411 -> 1452 (-98.7%) | 11 -> 1 | 3 -> 0 | 24 -> 0 | 1 -> 1 |
| 407_id_card_front_back | 32_stroke_lines | 15226 -> 13010 (**-14.6%**) | 59924 -> 2817 (-95.3%) | 16 -> 1 | 0 -> 0 | 0 -> 0 | 1 -> 1 |
| 391_survey_questionnaire_grid | 17_matched_runs | 7463 -> 4386 (**-41.2%**) | 94463 -> 2288 (-97.6%) | 13 -> 1 | 0 -> 0 | 0 -> 0 | 1 -> 1 |
| 302_radiology_report | 60_text_column_right_edge | 6054 -> 4028 (**-33.5%**) | 19693 -> 1192 (-93.9%) | 22 -> 1 | 1 -> 0 | 4 -> 0 | 1 -> 1 |
| 321_auditors_report | 60_text_column_right_edge | 5306 -> 4055 (**-23.6%**) | 15967 -> 1241 (-92.2%) | 34 -> 1 | 0 -> 0 | 0 -> 0 | 1 -> 1 |
| 392_statistical_console_output | 47_margins | 4896 -> 4039 (**-17.5%**) | 10129 -> 1205 (-88.1%) | 21 -> 1 | 0 -> 0 | 0 -> 0 | 1 -> 1 |
| 412_page_labels_roman | 18_displacement | 4358 -> 3993 (**-8.4%**) | 7920 -> 1149 (-85.5%) | 19 -> 1 | 0 -> 0 | 0 -> 0 | 5 -> 1 |

Mean cut of `word/document.xml` across the ten: **94.5%**. Mean cut of the whole file: **32.4%**.

**Why the two percentages disagree, and it is not a rounding artefact.** The whole-file cut is
limited by parts the reduction never touches: `styles.xml`, `numbering.xml`, `theme1.xml`,
`settings.xml`, `fontTable.xml` and `word/media/*`. `72_bank_statement_no_rules_right_amounts`
ends at 4 052 bytes with a 1 202-byte `document.xml`; the other 2 850 bytes are that fixed
overhead, which is also *the reason a reduced real file is worth having* - the styles, fonts and
section properties that a synthetic file would have to invent are still the original's.
`407_id_card_front_back` is the extreme case: 12 351 of its 13 010 bytes are media parts, and the
construct itself is 2 817 bytes of `document.xml`.

### 2b. The strict reading, for comparison

The brief asks that the `scan()` construct count be unchanged at every step. That is the
`--strict` guard, and it was run on all ten documents:

| document | check | document.xml bytes | paragraphs | scan() before -> after |
|---|---|---|---|---|
| table-with-no-header-row | 18_displacement | 105147 -> 104332 (-0.8%) | 6 -> 6 | `w:before-page-top=214 w:drawing=2 wp:anchor=2` -> `w:before-page-top=214 w:drawing=2 wp:anchor=2` |
| 72_bank_statement_no_rules_right_amounts | 18_displacement | 47062 -> 45528 (-3.3%) | 9 -> 9 | `w:before-page-top=99 w:drawing=2 wp:anchor=2` -> `w:before-page-top=99 w:drawing=2 wp:anchor=2` |
| 16_right_aligned_amounts_txtpos | 18_displacement | 51620 -> 50513 (-2.1%) | 9 -> 9 | `w:before-page-top=74 w:drawing=17 wp:anchor=17` -> `w:before-page-top=74 w:drawing=17 wp:anchor=17` |
| mobile-bill | 18_displacement | 108411 -> 107211 (-1.1%) | 11 -> 11 | `w:before-page-top=112 w:drawing=15 wp:anchor=15` -> `w:before-page-top=112 w:drawing=15 wp:anchor=15` |
| 407_id_card_front_back | 32_stroke_lines | 59924 -> 53761 (-10.3%) | 16 -> 2 | `w:before-page-top=16 w:drawing=41 wp:anchor=41` -> `w:before-page-top=2 w:drawing=41 wp:anchor=41` |
| 391_survey_questionnaire_grid | 17_matched_runs | 94463 -> 88190 (-6.6%) | 13 -> 1 | `w:before-page-top=13 w:drawing=81 wp:anchor=81` -> `w:before-page-top=1 w:drawing=81 wp:anchor=81` |
| 302_radiology_report **(no countable construct - ran as carrier)** | 60_text_column_right_edge | 19693 -> 1192 (-93.9%) | 22 -> 1 | `w:before-page-top=38 w:drawing=2 wp:anchor=2` -> `w:before-page-top=1` |
| 321_auditors_report **(no countable construct - ran as carrier)** | 60_text_column_right_edge | 15967 -> 1241 (-92.2%) | 34 -> 1 | `w:before-page-top=34 w:spacing-letter=10` -> `w:before-page-top=1 w:spacing-letter=1` |
| 392_statistical_console_output **(no countable construct - ran as carrier)** | 47_margins | 10129 -> 1205 (-88.1%) | 21 -> 1 | `w:before-page-top=21` -> `w:before-page-top=1` |
| 412_page_labels_roman | 18_displacement | 7920 -> 5233 (-33.9%) | 19 -> 19 | `w:before-page-top=19` -> `w:before-page-top=19` |

Three rows are marked **no countable construct**: `60_text_column_right_edge` and `47_margins` have no measured construct mapping, so `--strict` had no count to hold and the run fell back to the carrier guard. Those three are the same reduction in both tables and must not be read as strict results; the strict mean below excludes them (7 of 10 documents).

Mean `document.xml` cut under the strict guard, over the 7 documents it could actually enforce: **8.3%**, against **94.5%** under the carrier guard over the same ten.

Two things this measures, and neither was obvious before running it:

1. **`scan()` counts are too coarse to guard a reduction.** For the 13 `18_displacement`
   documents the mapped construct is `w:before-page-top`, and `scan()` counts *every* paragraph
   that asks for space before it - 214 instances in a 6-paragraph document, because table-cell
   paragraphs count too. The measured defect is narrower (google_safe.py's own note: Google
   renders 0.33 of the 55.15 pt asked **at the top of a page**). Holding the count identical holds
   almost the whole document: 0.8%-6.6% of `document.xml` removed, and on `mobile-bill` and
   `table-with-no-header-row` **zero** structural elements removed.
2. **A count guard does not protect content.** `412_page_labels_roman` under `--strict` cut 33.9%
   of `document.xml` while keeping all 19 paragraphs and all 5 pages - it deleted *runs* whose
   text carried no construct. The count was preserved exactly while text disappeared. A number
   that stays still is not evidence that the document is the same document.

## 3. What the reduced documents actually are

| document | carrier the tool preserved | what is left |
|---|---|---|
| table-with-no-header-row | w:before-page-top at a page top (google_safe.py: Google renders 0.33 of the 55.1 | 1 paragraph (`VASUDHA TRADERS ...`), `w:spacing w:before="1040"` = 52.0 pt, at page top |
| 72_bank_statement_no_rules_right_amounts | w:before-page-top at a page top (google_safe.py: Google renders 0.33 of the 55.1 | 1 paragraph (`NAGAR URBAN CO-OPERATIVE BANK LTD`), `w:before="1230"` = 61.5 pt, at page top |
| 16_right_aligned_amounts_txtpos | w:before-page-top at a page top (google_safe.py: Google renders 0.33 of the 55.1 | 1 paragraph (`SRI LAKSHMI FABRICS`), `w:before="1190"` = 59.5 pt, at page top |
| mobile-bill | w:before-page-top at a page top (google_safe.py: Google renders 0.33 of the 55.1 | 1 paragraph (`VISTARA TELECOM TAX INVOICE`), `w:before="1040"` = 52.0 pt, at page top |
| 407_id_card_front_back | w:drawing, wp:anchor (diagnose.CAUSE: measured to break 32_stroke_lines) | 1 paragraph carrying exactly ONE `<w:drawing>` (an anchored `wps` rule), 41 -> 1 |
| 391_survey_questionnaire_grid | wp:anchor, w:drawing, w:spacing-letter (diagnose.CAUSE: measured to break 17_mat | 1 paragraph carrying exactly ONE `<w:drawing>`, 81 -> 1 |
| 302_radiology_report | no measured construct maps to 60_text_column_right_edge | 1 paragraph (`Consultant Radiologist - Reg. KMC/28411/2001`) - the source line with the furthest-right edge |
| 321_auditors_report | no measured construct maps to 60_text_column_right_edge | 1 paragraph (`4. We draw attention to Note 27 ...`) - the source line with the furthest-right edge |
| 392_statistical_console_output | no measured construct maps to 47_margins | 1 paragraph (`R console output - linear model of handling cost`) - the source line with the furthest-left edge |
| 412_page_labels_roman | w:before-page-top at a page top (google_safe.py: Google renders 0.33 of the 55.1 | 1 paragraph, `w:before="1227"` = 61.35 pt, at page top; 5 pages -> 1 |

The four `18_displacement` reductions converge on the same shape independently: **one paragraph,
no table, no drawing, at page top, asking 52-61.5 pt of space before it.** That is within a few
points of the 55.15 pt in `google_safe.py`'s note, and it is arrived at by deleting from a real
file rather than by writing that value down. Whether it is the right shape is not established by
this - see section 5.

## 4. What was verified, and how

Run for every reduced file (all True unless stated; raw data in `reduction-records.json`):

| check | how | result |
|---|---|---|
| valid zip | `zipfile.ZipFile.testzip()` | 10/10 pass |
| `word/document.xml` parses | `lxml.etree.fromstring` | 10/10 pass |
| opens as a Word document | `python-docx` `Document()` | 10/10 pass |
| every other part byte-identical | byte-compare of every zip entry except `word/document.xml`, and the entry list is identical | 10/10 pass |
| the reduction is deletions only | written `document.xml` is a *subsequence* of the original's bytes | 10/10 pass |
| the carrier element survives | the exact `<w:spacing>`/`<w:drawing>` bytes, looked for in the file on disk | 10/10 pass |
| `scan()` counts, every step | `google_safe.scan()` / its regexes re-run on each candidate | recorded per step (section 2 / records) |
| still converts in LibreOffice | `soffice --convert-to pdf` | 10/10 pass, 1 page each (5 -> 1 on the page demo) |
| carrier text still lands where it did | PyMuPDF line position, original render vs reduced render | 5 exact, drift (0.0, 0.0) - `16_right_aligned_amounts_txtpos`, `72_bank_statement...`, `mobile-bill`, `table-with-no-header-row`, `392_statistical_console_output`; 2 moved up by exactly the content deleted above them (`302_radiology_report` -694.3 pt, `321_auditors_report` -309.0 pt, x unchanged in both); 3 have no carrier text left in the reduced render (`391`, `407`: drawing-only carrier; `412`: text not located in either render) |

The `scan()` counts, before -> after, per document, are in the section 2 table (strict) and in
`reduction-records.json` (`scan_before`, `scan_after`, and the same pair at every one of the 9-93
intermediate steps, under `steps[]`).

**Not verified, and this is the important list:**

* that any reduced file still **fails its check in Google Docs**. No Google renderer was
  available; `gverify.py` needs Drive API calls that a script cannot make here.
* that the construct identified as the *carrier* is the actual cause. For `18_displacement` and
  `32_stroke_lines` the carrier comes from `diagnose.CAUSE` / `google_safe.py`'s recorded laws.
  For `60_text_column_right_edge`, `47_margins` and `391`'s `17_matched_runs` **no measured
  construct maps to the check**, and the carrier was located by geometry - the source PDF's
  furthest-right (or furthest-left) text line, matched back to a docx paragraph. That is an
  inference. If it is wrong, the reduction deleted the cause and every structural check above
  still passes.
* that the reduction is *minimal*. The loop is greedy (biggest element first, restart on every
  accepted step) and stops at the first local minimum. It also cannot touch parts outside
  `word/document.xml`, so unreferenced `word/media/*` stays: `407_id_card_front_back` is still
  13 010 bytes for a 2 817-byte body.
* that LibreOffice's clean render means anything about Google. `google_safe.py`'s own docstring
  is explicit that LibreOffice honours exactly the constructs Google drops; a reduced file that
  renders perfectly locally is not evidence about the phone.

## 5. Reduction or synthesis - judgement

**Neither route produces a repro without a Google run.** A minimal synthetic `.docx` and a
reduced real `.docx` are both *candidates*; only Google can promote one. What differs is what
each gets wrong when it is wrong.

**Where reduction is the better route.** For a check whose cause is a construct the project has
already measured - `18_displacement` (52-61.5 pt of `w:before` at a page top), `32_stroke_lines`
(a rule carried as a floating `<w:drawing>`), `59_shape_anchor` (an anchored object) - reduction is strictly more
informative than synthesis, for three measured reasons:

1. It converges on a shape a synthesist would have to *guess*: the five `18_displacement`
   documents reduced here (four single-failure candidates plus the page demo), reduced
   independently, all ended as one page-top paragraph with 52-61.5 pt of
   space before it. That agreement is evidence the shape is not an artefact of one document.
2. It keeps the ingredients nobody named - real `styles.xml`, the engine's `docGrid`/`pgMar`
   (top=0, left=0 on these documents), the exact run properties - because it never rewrites a
   part, it only deletes spans. A synthetic file re-invents those, and a failure that depends on
   one of them cannot reproduce from a re-invention.
3. It is a *bisect over real content*, which synthesis is not. If a reduced file stops failing in
   Google, the removed content was the cause, and the last accepted step names it. A synthetic
   file that fails to reproduce tells you only that your theory was incomplete.

**Where synthesis is the better route.** For the checks with no measured construct mapping -
`60_text_column_right_edge` (5 single-failure documents), `47_margins`, `17_matched_runs` on
`391` - reduction has to *locate* the carrier by geometry before it can preserve it, and that
location is an inference the tool cannot test. On those documents the reduction is only as
faithful as the guess, and the failure is more likely a global property (font substitution
widening lines, a margin the renderer rounds) than a construct sitting in one paragraph. Synthesis
is not better because it is smarter; it is better because there it is honest about being a guess,
whereas reduction there *looks* like a measurement and is not one.

**What I would do next, in order.** (a) Take the `18_displacement` reductions to Google -
one page, one paragraph, no table - and see whether the 52-61.5 pt gap is still dropped. That is
the cheapest real answer available and it tests the project's own 55.15 pt law at the same time.
(b) Take `407_id_card_front_back` (one drawing, no text) to Google for `32_stroke_lines`; that
check has never passed on a floating drawing in 192 scored documents, so the prediction is
specific and falsifiable. (c) Do **not** trust the three geometry-carrier reductions until a
carrier is measured rather than inferred; if one of them fails to reproduce, that is a finding
about the carrier, not about reduction.

## 6. Reproducing this

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/app
bash tools/p2w-bench/jdk-fetch.sh --path        # JDK 17
bash tools/p2w-bench/corpus-fetch.sh            # 213 PDFs
bash tools/p2w-bench/build-engine.sh            # ConvertAll
# convert the documents you want (ConvertAll takes a directory of PDFs):
java -cp 'out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar' \
     ConvertAll /scratch/work/shard /scratch/work/p2w/out

python3 tools/p2w-bench/reduce-repro.py --candidates
python3 tools/p2w-bench/reduce-repro.py 72_bank_statement_no_rules_right_amounts --rows --runs --lo
python3 tools/p2w-bench/reduce-repro.py 412_page_labels_roman --check 18_displacement \
        --allow-multi --rows --runs --lo          # page-level reduction, 5 pages -> 1
python3 tools/p2w-bench/reduce-repro.py 407_id_card_front_back --strict   # count guard
```

Reduced files: `reduced/` (carrier guard) and `reduced/*.strict-guard.docx`. Per-step records,
including the `scan()` count at every step: `reduction-records.json`.

