# The 10 documents that fail only 18_displacement, and the hairline line-box charge is NOT why

**26 Nov 2026, fixer slot 10:54.** Ledger: `benchmarks/gverify/*.json` at HEAD `a4d8fca469bba636`.
Measured against the emitted `.docx` and the stored Google verdicts; nothing committed but this file
and the Google-loop finding.

## The target list, which is the cheapest in the corpus

136 documents carry a Google verdict: **35 clean, 24 fail exactly one check**. Of those 24, **10 fail
only `18_displacement`** - one construct each stands between them and CLEAN, and they are worth more
than any other group that size. All ten are single-page (`w:br w:type="page"` count is 0 in every one),
so construct A - the page-top `w:before` Google drops - cannot be their cause.

| document | med_dy | worst_dy | exact lines | below hairline | hRule=atLeast rows |
|:--|--:|--:|--:|--:|--:|
| 16_right_aligned_amounts_txtpos | -1.6 | 3.4 | 59 | 2 | 13 |
| 303_discharge_summary | -0.2 | 4.1 | 43 | 1 | 5 |
| 31_times_body_arial_headings | 2.6 | 3.5 | 24 | 20 | 0 |
| 320_balance_sheet_statutory | 8.2 | 19.4 | 73 | 1 | 21 |
| 325_demat_holdings_statement | 3.8 | 38.1 | 81 | 1 | 12 |
| 362_price_list_dense | -2.8 | 5.4 | 259 | 1 | 29 |
| 36_embedded_subset_font | 1.7 | 3.5 | 28 | 5 | 7 |
| 402_calendar_month_grid | 1.4 | 6.5 | 41 | 11 | 6 |
| 403_crossword_puzzle | -10.2 | 12.2 | 28 | 0 | 7 |
| 72_bank_statement_no_rules_right_amounts | 1.1 | 4.8 | 80 | 2 | 18 |

**Eight of the ten have a median displacement inside +/- 3 pt** - the page is where the original drew
it - and they still fail, because `18_displacement` convicts on the count of runs beyond
`clamp(0.35*size, 1.5, 4.5)` pt, not on the median. The failure on those eight is a handful of
*specific* runs (`worst_dy` 3.4-6.5), not a page-wide offset. Only 320, 325 and 403 carry a real
magnitude (19.4, 38.1, 12.2 pt worst).

## What I believed, and the measurement that refutes it

The engine writes a flow line as `w:line = 1.38 * size` with `lineRule="exact"` - a hairline - and
carries the rest of the pitch in `w:before`. The design comment at `DocxWriter.java:75-106` says that
box is the one value both Word (`line/20`) and Google (`max((line/240)*r*size, 0.069*size)`) charge
the same, *provided the box stays at or above the floor*. A residual box below the floor would make
Google charge `0.069 * size` where Word charges `line/20`, and the difference is one sign and
accumulates down the page - a good candidate for the marginal failures.

I censused every `lineRule="exact"` paragraph in all ten emitted `.docx`: the count of boxes below
`1.38 * size`, and the summed per-line difference `max(0, google_charge - word_charge)` over the whole
document.

**It is refuted.** The summed difference is 0.00-1.82 pt on all ten, and it does not order the
documents:

| document | sum of per-line deficit, pt | \|med_dy\| |
|:--|--:|--:|
| 403_crossword_puzzle | **0.00** | **10.2** |
| 320_balance_sheet_statutory | 0.11 | 8.2 |
| 325_demat_holdings_statement | 0.25 | 3.8 |
| 402_calendar_month_grid | **1.82** | **1.4** |
| 31_times_body_arial_headings | 1.52 | 2.6 |

403 has no sub-hairline box at all and the largest median displacement; 402 has the largest deficit and
almost no displacement. **The hairline charge is not the mechanism of these ten.** Do not spend a run
on raising the residual box to `1.38*size`.

## What is now true, and what to test next

1. The ten are the right target, and they are cheap. Nothing in the ledger is closer to CLEAN.
2. Their displacement is not a uniform page offset on eight of them. It is a few runs. The next run
   should read **which runs** - `gverify.py --collect` keeps the export, and the per-run dy is
   computable from it against the source PDF - rather than looking for a page-wide constant.
3. `hRule="atLeast"` rows are present on nine of the ten (0-29 rows each). 31_times has none and 403
   has seven, so the row floor is not sufficient either, but 320/325 - the only two with a real
   magnitude - carry 21 and 12 of them. That is where the next measurement should start.
