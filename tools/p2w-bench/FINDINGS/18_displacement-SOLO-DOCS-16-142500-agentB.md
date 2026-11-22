# SOLO — which documents go CLEAN if one row-pitch declaration law is fixed

Evidence base: `gverify/*.json` (213 files), `CENSUS.csv`, `DEFECT-CLASSES-GOOGLE.md`,
`18_displacement-ROW-PITCH-LAW-135800-relay.md`. No number below is inferred from a filename.

## 0. Shape of the JSON set (counts only)

| status | n |
|---|---:|
| `ok`, scored | 192 |
| `page_count_refused` (no per-check results at all) | 21 |
| clean, all 42 checks | 23 |
| fail exactly one check | 21 |

All 23 clean documents are `42/42`. This matches `DEFECT-CLASSES-GOOGLE.md`: "Google Docs 23 of 192 pass all 42".

Check-set caveat: 126 of the 192 scored documents carry `total: 42`, 64 carry `total: 47`, 2 carry `total: 44`.
"42/42" is therefore only the target for the 42-check documents. A 47-check document reaching clean
reaches 47/47, not 42/42.

## 1. Documents failing EXACTLY ONE check (21)

### 1a. Only failing check is `18_displacement` (16)

| document | score |
|---|---|
| `16_right_aligned_amounts_txtpos` | 41/42 |
| `22_invoice_four_columns_txtpos` | 41/42 |
| `29_dot_leaders_txtpos` | 41/42 |
| `31_times_body_arial_headings` | 41/42 |
| `362_price_list_dense` | 41/42 |
| `41_coloured_headings_white_bg` | 41/42 |
| `68_journal_wide_table_spanning` | 41/42 |
| `71_invoice_space_aligned_no_rules` | 41/42 |
| `72_bank_statement_no_rules_right_amounts` | 41/42 |
| `73_marksheet_subject_marks_grade` | 41/42 |
| `balance-sheet-two-columns-of-figures` | 41/42 |
| `bus-timetable-station-left-times-right` | 41/42 |
| `insurance-policy-schedule` | 46/47 |
| `mobile-bill` | 46/47 |
| `table-with-no-header-row` | 46/47 |
| `two-tables-stacked-with-no-gap` | 46/47 |

12 at 41/42, 4 at 46/47.

### 1b. Only failing check is something else (5)

| document | only failing check | score |
|---|---|---|
| `313_power_of_attorney` | `60_text_column_right_edge` | 41/42 |
| `321_auditors_report` | `60_text_column_right_edge` | 41/42 |
| `392_statistical_console_output` | `47_margins` | 41/42 |
| `407_id_card_front_back` | `32_stroke_lines` | 41/42 |
| `49_coloured_background_block_paragraph` | `32_stroke_lines` | 41/42 |

These five are out of scope for a row-pitch law: their single failure is a different check.

### 1c. Documents failing exactly `18_displacement` + `23_line_pitch`

**None.** Zero documents in the 192 have that exact pair.

`23_line_pitch` fails in only three documents, each carrying at least four failures, so none of them is
one law away from clean:

| document | failing checks | score |
|---|---|---|
| `64_newspaper_uneven_columns_ad_boxes` | `05_chars_extra`, `18_displacement`, `23_line_pitch`, `26_text_overlap`, `59_shape_anchor` | 37/42 |
| `373_leave_application_form` | `05_chars_extra`, `18_displacement`, `23_line_pitch`, `60_text_column_right_edge` | 43/47 |
| `404_sudoku_grid` | `18_displacement`, `23_line_pitch`, `47_margins`, `59_shape_anchor` | 43/47 |

## 2. Page count, `signal`, `worst_page` from `CENSUS.csv`

**`CENSUS.csv` contains no data rows.** It is 194 bytes: one CRLF-terminated header line and nothing else,
20 columns (`document, problem, share5, max_pt, worst_page, pages, src_chars, docx_chars, src_images,
docx_images, src_drawings, docx_tables, docx_cells, src_annots, src_images_any, signal, dx_pt, dy_pt,
explains, moved_gt20`). Therefore for every document in section 1:

- page count: **not stated**
- `signal`: **not stated**
- `worst_page`: **not stated**

The JSON files do not carry page counts for scored documents either — a `pages` key exists only on the 21
`page_count_refused` files. None of the 16 single-`18_displacement` documents is among those 21, so no page
count for them exists anywhere in the supplied inputs.

One page count is documented, in the relay rather than the census: `two-tables-stacked-with-no-gap` is
**1 page, 13 ruled rows**, source rule pitch **18.40 pt**, rules at 86.52, 104.92, 123.32 …

So: cheap-vs-long cannot be assigned from these inputs. Exactly one of the 16 is evidenced as 1 page
(`two-tables-stacked-with-no-gap`); the other 15 are **unclassified**.

For completeness, the only page data in the inputs — the refused files — is: all 21 refused at
`pages: 2, want: 1`, except `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled`,
both `pages: 14, want: 9`.

## 3. Source rule pitch

**pitch not in the census.** `CENSUS.csv` has no pitch column and no rows.

The only pitch value in the supplied evidence is the relay's, for one document: `two-tables-stacked-with-no-gap`,
18.40 pt on every one of its 13 rows. No pitch is stated for any other document.

## 4. If one declaration law lands every ruled row on the nearest reachable 0.5 pt step

Law as given: laid pitch = max(declared `trHeight`, 1.15 × font size); laid pitches are always multiples of
0.5 pt; measured map on the 18.40 pt row is 17.40→18.0, 18.00→19.0, 18.40→19.5, so the reachable ladder is
18.0 / 18.5 / 19.0 / 19.5. Nearest ladder point to a 18.40 pt source is **18.5 pt** (0.1 pt a row), and the
relay states 18.5 is bracketed by the two lower measurements, so a declaration between 17.40 and 18.00
should land it.

**Plausibly 42/42 (12 documents)** — the 41/42 single-`18_displacement` set: `16_right_aligned_amounts_txtpos`,
`22_invoice_four_columns_txtpos`, `29_dot_leaders_txtpos`, `31_times_body_arial_headings`,
`362_price_list_dense`, `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`,
`71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`,
`73_marksheet_subject_marks_grade`, `balance-sheet-two-columns-of-figures`,
`bus-timetable-station-left-times-right`.

Conditional, and I cannot verify it: this holds only if each document's source pitch sits close enough to a
ladder point that the residual stays inside `18_displacement`'s tolerance. Pitch is stated for none of them.
The one calibration point is the relay's: 0.4 pt a row (18.0 against 18.4) failed with 5.2 pt cumulative on
13 rows; 0.1 pt a row (18.5) is 1.3 pt cumulative and is untested.

**Plausibly 47/47, not 42/42 (4 documents)** — `insurance-policy-schedule`, `mobile-bill`,
`table-with-no-header-row`, `two-tables-stacked-with-no-gap`. They are scored on 47 checks, so the law's
ceiling for them is 47/47. `two-tables-stacked-with-no-gap` is the only one with a stated pitch (18.40) and
the only one the law has actually been measured against; HEAD already scores it 46/47 and the relay's
net-of-rule build also scored 41/42 (see the discrepancy note below) — no build reached clean.

**Definitely cannot (5 documents)** — `313_power_of_attorney` and `321_auditors_report`
(`60_text_column_right_edge`), `392_statistical_console_output` (`47_margins`),
`407_id_card_front_back` and `49_coloured_background_block_paragraph` (`32_stroke_lines`). Their single
failing check is not `18_displacement`, so a row-pitch law cannot clean them.

**Definitely cannot, other class (21 documents)** — the `page_count_refused` set, e.g.
`041122-Account_Opening_Form`, `bank-statement-horizontal-rules-only`, `boq-horizontal-rules-only`,
`price-list-2col-dense-right-aligned`. They fail page count before any check runs, so they carry no check
score to clean.

**Pitch far off the ladder** — cannot be asserted for any document. Pitch is stated for one document only,
and 18.40 is 0.1 pt from a reachable point, not far off. For the other 15 the pitch is not stated, so the
question is open rather than negative.

### Discrepancy in the inputs (reported, not resolved)

The relay says `two-tables-stacked-with-no-gap` scores **41/42** at HEAD and that this is "the same as
`benchmarks/gverify/`". The JSON in this archive says **46/47** for the same document. Same single failure
(`18_displacement`), different check set size. Either the relay quoted a 42-check run or the archive's JSON
was produced with the 47-check set; I did not have the runner to tell which.

## 5. Three cheapest documents to prove the law on, in order

Cheapness here is evidenced by one Google round trip on a document that is one check from clean. Page count
is verified for only the first; the ordering after it rests on score completeness and construct shape, not on
page count, because the census is empty.

1. **`two-tables-stacked-with-no-gap`** — 46/47, only `18_displacement`. The only document in the corpus with
   all three things the test needs already measured: 1 page (relay), 13 ruled rows, source pitch 18.40 pt, and
   three declared→laid points bracketing the 18.5 target. The next build either lands 18.5 or it does not, and
   one round trip answers it. Cheapest and highest-information.
2. **`table-with-no-header-row`** — 46/47, only `18_displacement`. Same top score band as (1) with the
   simplest ruled construct (a table with no header row, so no header-repeat or type-floor interaction to
   confound the row height). Page count not stated.
3. **`mobile-bill`** — 46/47, only `18_displacement`. Third of the 46/47 band, so the same one-check step; it
   is a ruled-figure bill, the shape the law was derived on. Tied on all supplied evidence with
   `insurance-policy-schedule` (also 46/47, only `18_displacement`); pick either — nothing in the inputs
   separates them.

Why not the 41/42 twelve first: each is the same one-check step but has to clear the 42-check set from a lower
base, so a failure mode other than row pitch is more likely to surface; and no page count or pitch is stated
for any of them, so none is provably cheap.

## What is missing

- `CENSUS.csv` is empty (header only). Page count, `signal`, `worst_page` and per-document pitch for all 16
  single-`18_displacement` documents are unavailable from it.
- Source pitch is stated for one document only (`two-tables-stacked-with-no-gap`, 18.40 pt).
- `18_displacement`'s tolerance is not stated in any supplied file, so "plausibly clean at 0.1 pt a row"
  cannot be checked against a threshold.
