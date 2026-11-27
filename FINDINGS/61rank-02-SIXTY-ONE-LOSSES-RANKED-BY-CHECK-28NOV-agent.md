# The 61 genuine losses ranked by check: `18_displacement` alone would clean 13 of them

**28 Nov 2026, fixer slot 04:00 IST, agent `61rank-02`.** Read-only, from the committed tables.
Engine `a05b20eb05fe0fc8`.

## How the 61 were isolated

`regress.py`'s own rule, recomputed: of the 212 documents present in both `benchmarks/RANKING.csv` and
`benchmarks/RANKING-BASELINE.csv`, **84** have a current `share5` above their 15 Nov baseline
(`Prakashan_Print_Fidelity_Handbook` is in the current table only and is outside the set).

Excluded from the 84, and why each exclusion is not damage the charter recognises:

| exclusion | documents | note |
|:--|--:|:--|
| Google-clean on `a05b20eb` (`failed == []`) | 10 | the charter's own definition of done |
| impossible baseline (`share5 == 0.00` with `max_pt > 2.4`) | 4 | 2.88-3.36 pt of ink beyond a 2.4 pt radius |
| already at the 99 % bar (current `share5 <= 1.0`) | 13 | refused by a gate that never reads the bar |

27 raw, **4 double-counted** (`29_dot_leaders_txtpos` and `362_price_list_dense` are clean *and* at the
bar; `323_credit_card_statement` and `403_crossword_puzzle` are impossible *and* at the bar), so the
union is **23** and the remainder is **61**. No discrepancy.

## The ranking

All 61 have a `gverify` result and none has an empty `failed` list. 23 distinct check ids; **17 of the
61 fail exactly one check**.

| # | check id | fails of 61 | fails **only** it |
|--:|:--|--:|--:|
| 1 | `18_displacement` | **47** | **13** |
| 2 | `60_text_column_right_edge` | 22 | 3 |
| 3 | `26_text_overlap` | 7 | 1 |
| 4 | `59_shape_anchor` | 21 | 0 |
| 5 | `04_chars_missing` | 16 | 0 |
| 6 | `47_margins` | 9 | 0 |
| 7 | `13_text_colours` | 8 | 0 |
| 8 | `27_text_off_page` | 7 | 0 |

The only-counts reconcile: 13 + 3 + 1 = 17 = the single-check documents.

The 13 that fail **only** `18_displacement`: `10_stamp_as_image`, `306_clinical_protocol_synopsis`,
`30_mixed_font_sizes_one_baseline_txtpos`, `35_four_typefaces_one_page`,
`71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`,
`74_balance_sheet_indented_subitems`, `balance-sheet-two-columns-of-figures`,
`bus-timetable-station-left-times-right`, `eway-bill`, `price-list-2col-dense-right-aligned`,
`table-with-no-header-row`, `two-tables-stacked-with-no-gap`.

## What it means

`18_displacement` is worth **more than four times** any other check among the genuine losses, and it is
an engine construct rather than a Google limit: `FINDINGS/18-displacement-TWO-CONSTRUCTS-27NOV.md`
splits it into A (`LINE_BASE = 0.8` at `DocxWriter.java:220` against Google's ~0.31 em), B (a row laid
taller than its declared `w:trHeight`, which is `ROW_RUNG_UNDER_TW`) and C (`afterTablePt` / `edgeGap`
block placement). It is vertical-only (`med_dx` within 0.8 pt).

**Sub-construct B is closed as a revert** - measured this run in Google, `ROW_RUNG_UNDER_TW = 0` takes
`mobile-bill` and `electricity-bill` from 47/47 to 46/47
(`FINDINGS/THE-RUNG-IS-GOOGLE-PROVED-AND-THE-LIBREOFFICE-BASELINE-IS-BACKWARDS-28NOV-fixer.md`). So
these 13 are **A and C territory**, and that is where the next run should look first.

`60_text_column_right_edge` is not something Google refuses - Google honours a right tab stop to
0.11 pt (`FINDINGS/60-RIGHT-TAB-HONOURED-INSTRUMENT-BLIND-27NOV-fixer.md`) and 2 of its 5 solo charges
are the reader re-grouping a line (`FINDINGS/60-COLUMN-RIGHT-EDGE-CENSUS-27NOV-agent.md`). Worth 3
documents, and only after `page_lines()` is fixed. `26_text_overlap`, `59_shape_anchor`,
`04_chars_missing`, `47_margins`, `13_text_colours` and `27_text_off_page` are not characterised in
`FINDINGS/` as construct-versus-instrument; not stated rather than guessed.
