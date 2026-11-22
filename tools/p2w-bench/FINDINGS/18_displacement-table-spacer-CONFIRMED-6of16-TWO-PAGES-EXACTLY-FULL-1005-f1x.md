# 18_displacement — the table spacer is CONFIRMED as the cause, worth 6 of the 16 solo documents, and blocked by two pages that are exactly full

**22 Nov 2026 · fixer slot 08:56 → · engine `kavopdf/app` at HEAD, built in-sandbox · every Google
number below is a live round trip (ConvertOne → Drive create-as-Google-Doc in `KavoPDF-Verify` →
export PDF → `verify_google.py`) · all 24 probe Docs deleted after scoring, folder empty**

## Why this was measured, and what it corrects

`FINDINGS/18_displacement-single-page-row-pitch-EMITTED-PITCH-IS-EXACT-082000-f1x.md` ranked nine
candidate causes and named C2 — the gap above a table, written as `w:line` on a 1 pt mark — as "the
single most valuable next measurement", because Google reads `w:line` as a *multiple* of the mark's
line height and not as a length, and the probe that would settle it had never been run on a real
document.

The 08:16 run appeared to test it and reported it refuted: *"screened all sixteen through Google …
1 of 16 moved by 0.85 pt"*. **That measurement was not a Google measurement.** `screen.py` renders
with `p2w.docx` / `p2w.run`, which call `benchmarks/p2w.py`'s `soffice_pdf` — LibreOffice. LibreOffice
honours `w:line` with `lineRule="exact"` as a length, so it places the table correctly in both states
and the screen could not see the change in either direction. The same report used `RANKING.csv`'s
`max_pt` (8.64 for `68_journal`) to argue the defect could not be 130 pt — but `max_pt` is `p2w.py`'s
ink EDT over the **soffice** render, and on that render all 16 pass 42/42. Both halves of the
refutation were measured in the renderer the defect does not exist in.

## The measurement — four documents, before, in Google

Converted with `ConvertOne`, uploaded, exported, scored, and then read per run with the new
`tools/p2w-bench/dy.py` (it intercepts `verify_google.extra_checks` to receive `pairs`, so it cannot
disagree with the instrument it explains).

| document | spacer written | median dy | min | max | n_out/n | score |
|:--|--:|--:|--:|--:|--:|:--|
| 68_journal_wide_table_spanning | 144.0 (capped) | **−114.28** | −115.03 | +1.31 | 61/74 | 41/42 |
| 73_marksheet_subject_marks_grade | 16.7 | **−12.85** | −145.35 | +6.40 | 60/64 | 41/42 |
| 41_coloured_headings_white_bg | 3.5, 3.45, 3.45 | **−4.13** | −6.84 | +0.88 | 21/36 | 41/42 |
| 71_invoice_space_aligned_no_rules | **none** | **+1.06** | +0.12 | +6.69 | 29/72 | 41/42 |

All four reproduce `RANKING.csv` exactly (41/42, `18_displacement` alone), so the instrument and the
published table agree.

The signature on `68_journal` is the decisive one: runs **above** the spacer sit at **+0.09** and
every run **below** it at **−114 to −115**. One construct, one gap, everything under it moves.
`loss / written` = 0.79, 0.77, 0.40 (partial population), 0 — i.e. **Google charges a
`w:line="G" lineRule="exact"` spacer on a 1 pt mark at ~22 % of G**, the same 0.22 the isolated TOPB
probe in `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md` measured (1103 twips asked
→ 12.22 pt rendered). Three real documents and one controlled probe agree, and the agreement is a
dose-response, not a single point.

## The change that was built

`DocxWriter.java:5872-5875` — the spacer `<w:p>` moved its gap from `w:line` to `w:before` (the one
vertical length Google honours exactly) and cut the line box to a hairline:

    <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="2880" w:after="0"
               w:line="1" w:lineRule="exact"/><w:rPr><w:sz w:val="2"/></w:rPr>

`ctx.flowTw` already added `spacerTw`, so the engine's page height and every page break were
unchanged. Second change: the 2880-twip cap on the spacer (`5852`, `5866`) raised to 4320, because
`68_journal` draws a real gap of 148.07 pt = 2961 twips and the cap truncated it by 4.05 pt. That cap
is reached by exactly one document in the 16 — the next largest spacer is 18.30 pt — so the raise is
a one-document change.

## What it did — all 16, measured in Google

| outcome | count | documents |
|:--|--:|:--|
| **42/42 CLEAN** | **6** | `16_right_aligned_amounts_txtpos`, `22_invoice_four_columns_txtpos`, `29_dot_leaders_txtpos`, `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`, `73_marksheet_subject_marks_grade` |
| still 41/42, 18 alone | 8 | `31_times_body_arial_headings`, `362_price_list_dense`, `71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`, `balance-sheet-two-columns-of-figures`, `bus-timetable-station-left-times-right`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap` |
| **WORSE — 41/42 → 38/42** | 2 | `insurance-policy-schedule`, `mobile-bill` |

`68_journal`'s median dy went **−114.28 → −3.08** with the spacer alone (then +0.97 and clean once the
cap let the real 148.0 pt through); its 130 pt loss is gone. That is the construct working.

The 8 that stayed open are no longer large errors — their residuals after the fix are tight:

| document | median dy | slope | rms resid |
|:--|--:|--:|--:|
| bus-timetable-station-left-times-right | +1.84 | +0.00611 | 0.27 |
| 72_bank_statement_no_rules_right_amounts | +1.18 | +0.00932 | 0.63 |
| 362_price_list_dense | −2.76 | −0.01474 | 0.52 |
| 31_times_body_arial_headings | +2.62 | +0.00291 | 0.40 |

They fail on the count budget (`n_out > max(2, 5 %)`) at tolerances of 2.87–4.5 pt, not on a gross
displacement. `71_invoice` and `31_times` have **no spacer at all** and cannot be reached by this
construct; `362_price_list` and the rest have a small residual of their own.

## Why it was not landed — the measured blocker

`insurance-policy-schedule` and `mobile-bill` went to **2 pages with content lost** (34 source blocks
→ 32 on page 1, page 2 empty; `01_page_count`, `32_stroke_lines`, `55_orientation_mix` newly failing).
Both are the documents with **three** spacers each (14.4/6.4/6.0 and 12.4/6.4/6.2), and both are
pages that are already full.

The mechanism, measured directly rather than inferred — source row pitch against the render's own:

| document | source pitch | Google render pitch | excess |
|:--|--:|--:|--:|
| mobile-bill | **18.40 pt** | **19.10 pt** | +0.70 pt/row |
| insurance-policy-schedule | **18.40 pt** | **19.10 pt** | +0.70 pt/row |

The engine writes these rows `w:trHeight … hRule="atLeast"` at 18.0/19.0 (the `floor(18.4k)` pattern,
emitted pitch exact to the source — see the 08:20 finding §2). `atLeast` lets Google grow each row to
the cell's natural height, and Google's natural height is **19.10** — so every row is 0.70 pt taller
than the page drew. Over 21–22 rows that is **+14.7 to +15.4 pt** of unaccounted height.

Before this change Google *under-spent* the spacer by ~19.5 pt on these documents, and that slack
absorbed the row excess. Charging the spacer at its true value removes the slack, the row excess is
exposed, the page overflows, and Google drops content. So the spacer fix is correct and **cannot be
landed alone**: it needs the row height to be true in the same attempt.

## What the next run should do, with the numbers

1. **Land both constructs together.** The spacer as `w:before` + hairline (exactly as above) **and**
   the row height corrected so Google's `atLeast` growth cannot exceed the source pitch. The measured
   excess is +0.70 pt/row at a source pitch of 18.40, i.e. a factor of **0.9634**; the C1 proposal in
   the 08:20 finding used 0.9785 from a different, unreproduced premise — **use 0.9634, measured
   here.** On `mobile-bill` that reclaims 14.7 pt against a ~10 pt overflow.
2. **Do not switch `atLeast` to `exact`.** The cell content Google computes (19.10) exceeds the
   declared height (18.0), so `exact` would clip 1.1 pt of descender. Shrink the emitted height
   instead.
3. **Then measure the blast radius before committing.** The spacer change touches every corpus
   document that has a table spacer, and this slot measured only the 16 that fail `18_displacement`.
   A document that is clean today and carries a spacer could move. Count them first —
   `ConvertAll` the corpus and grep for `<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>` — and render
   the clean ones that have one.
4. **Do not trust a `screen.py` verdict on this class.** `screen.py` measures in soffice, which
   honours `w:line` as a length and therefore cannot see either state of this construct. Every number
   in this finding cost three Drive calls and is worth it.

## What is settled by this slot

- The table spacer is the cause of `18_displacement` on the documents that have one. Dose-response
  measured on four documents and confirmed against one isolated probe.
- Google charges `w:line … lineRule="exact"` at ~0.22× the written twips on a 1 pt mark.
- Google renders `w:trHeight … hRule="atLeast"` rows 0.70 pt taller than an 18.40 pt source pitch,
  because the cell's natural height is 19.10.
- `68_journal`'s 2880-twip cap is 4.05 pt short of the gap the page really draws (2961 twips).
- `screen.py` is a LibreOffice instrument and cannot judge a construct whose whole effect is a
  Google-only reinterpretation.
