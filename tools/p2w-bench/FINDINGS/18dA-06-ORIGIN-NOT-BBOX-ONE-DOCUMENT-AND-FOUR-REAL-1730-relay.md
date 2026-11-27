# 18_displacement measured the ink top, not the baseline: one document flipped, and four of five are real

**27 Nov 2026, 17:30 IST, relay run. Engine `d28ca7516c3f9165`.**

## The change

`verify_google.py` published `ry` = the span's reading-space **bbox top** (origin minus the rendered
face's own ascent) and `18_displacement` scored `g["ry"] - r["ry"]`. That difference is the baseline
difference **plus the ascent difference between the source face and the substituted face** - a font
metric, not a layout move. `runs()` now also publishes `roy`, the origin projected into reading space,
and 18 scores and reports that. `ry` is untouched, because the pair matcher and checks 34/42/43 are
keyed on it and must not move.

    ds = [(g["roy"] - r["roy"], r["size"]) for r, g in pairs ...]     # was ry - ry
    dy18 = [g["roy"] - r["roy"] for r, g in pairs ...]                # reported med_dy / worst_dy

## What it was worth: 12 documents measured on live Google renders

Twelve documents were converted this run, uploaded to Drive, converted by Google, exported to PDF and
scored twice - once with `HEAD`'s instrument, once with the patched one. Same PDF both times.

| Document | 18 before | 18 after | Verdict change |
|:--|--:|--:|:--|
| `31_times_body_arial_headings` | FAIL (med +2.6, worst 3.5) | **PASS** (med +0.9, worst 2.1) | **41/42 -> 42/42, CLEAN** |
| `16_right_aligned_amounts_txtpos` | FAIL (med -2.8) | FAIL (med -2.8) | none - real |
| `320_balance_sheet_statutory` | FAIL (med +5.3) | FAIL (med +7.2) | none - real, larger |
| `71_invoice_space_aligned_no_rules` | FAIL (med +1.1, worst 6.7) | FAIL (med +1.1, worst 6.7) | none - real |
| `72_bank_statement_no_rules_right_amounts` | FAIL (med -3.0) | FAIL (med -3.0) | none - real |
| `mobile-bill` | PASS (worst 2.7) | PASS (worst 3.2) | none |
| `312_affidavit_stamp_paper` | PASS (worst 4.2) | PASS (worst 2.3) | margin improved |
| `09_stamp_font_not_embedded` | PASS (3.4) | PASS (3.4) | none |
| `06_rect_paid_stamp_red_transparent` | PASS (1.9) | PASS (1.9) | none |
| `393_spectrum_peak_table` | FAIL (5.2) | FAIL (3.3) | still out, closer |
| `364_event_ticket` | FAIL (6.7) | FAIL (4.1) | still out, closer |
| `07_stamp_over_table` | FAIL (4.3) | FAIL (4.3) | none |

**No new failure on any of the twelve. One document became clean.** `31_times_body_arial_headings` was
charged 2.6 pt for a baseline that sits 0.9 pt from the source's: source `Helvetica-Bold@12` reports an
ascent of 1.07 em, the built `LiberationSans-Bold` 0.80 em.

## The claim it refutes

A prior reading of the same mechanism (and a sub-agent briefed on it this run) predicted that the
ascent term explains **all 25** documents whose only failing check is 18, i.e. 25 documents would become
clean. It explains **one of the five measured**. Four of the five carry a real baseline shift of
-3.1 to +6.3 pt, confirmed below.

**So the other 24 sole-18 documents are an ENGINE defect, not an instrument artefact.** That is the
useful half of this finding: the class does not dissolve on a measurement correction, and the next run
should treat the remaining sole-18 documents as genuine Google vertical displacement.

## Independent confirmation (a second implementation, not the edited file)

A throwaway script that opens both PDFs with PyMuPDF, matches spans by `(page, text)` and subtracts
`span["origin"][1]` directly - no import of `verify_google.py`:

| Document | independent median baseline dy | 18 after (med_dy) |
|:--|--:|--:|
| `16_right_aligned_amounts_txtpos` | -2.63 pt | -2.8 |
| `320_balance_sheet_statutory` | +6.25 pt | +7.2 |
| `71_invoice_space_aligned_no_rules` | +1.12 pt | +1.1 |
| `72_bank_statement_no_rules_right_amounts` | -3.12 pt | -3.0 |
| `31_times_body_arial_headings` | +0.97 pt | +0.9 |

The two implementations agree to within the difference between their pair sets, which is the
confirmation that `roy` is the baseline and that the four remaining failures are the page, not the check.

## Regression risk, stated

A document that passes 18 today on a bbox-top dy could in principle fail on a baseline dy if the
ascent term was masking a real shift. Six documents were chosen for exactly that reason - the
passing-18 documents with the **smallest margin** in `benchmarks/gverify/` (`07_stamp_over_table` 4.3,
`312_affidavit_stamp_paper` 4.2, `364_event_ticket` 4.2, `393_spectrum_peak_table` 3.6,
`09_stamp_font_not_embedded` 3.4, `06_rect_paid_stamp_red_transparent` 3.3 pt) - and **none of them
gained a failure**. The largest movement on a passing document was 312's 4.2 -> 2.3 pt, toward the
source. What would overturn this: a corpus Google pass in which a document that passed 18 on
`HEAD` fails it on this instrument.
