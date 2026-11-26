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

## The residual on 31_times is ONE page-level constant of 2.65 pt, not 29 constructs

Measured directly, per run, source PDF against the Google export of the same document
(`/scratch/downloads/composio/probe-31.pdf`, 29 runs paired by text on page 0):

    n = 29   mean dy = +2.649 pt   sd = 0.712   min 1.39   max 3.59

and it does not scale with the type:

    size  8.0 -> +2.50    9.0 -> +3.42   10.0 -> +3.10
    size 10.5 -> +2.63   11.0 -> +1.98   12.0 -> +2.15

A per-line construct would grow down the page and would scale with the em. This does neither: every
run on the page is low by about the same 2.6 pt, whatever its size. **It is one constant at the top of
the page, not a defect in any line.**

It also means the document is closer to CLEAN than the verdict reads. `18_displacement`'s tolerance is
`clamp(0.35*size, 1.5, 4.5)` pt - 3.5 pt at 10 pt - and three runs read 3.55-3.59. **31_times fails by
0.09 pt**, on a page whose whole flow is 2.65 pt low.

### The test the next run should make

Find the constant. Three candidates, in the order I would test them:

1. **the page's own top edge** - compare `page.rect` of the source PDF and of the Google export. A
   cropbox/mediabox origin difference of 2.6 pt would shift every run on the page and nothing else,
   and it would be identical across documents.
2. **the first paragraph's box** - `w:before="1230"` (61.5 pt) plus a `w:line="13"` exact box on a
   12 pt heading. Google charges that box `0.069 * 12 = 0.828` pt where the engine's model charges
   0.65 pt; that is 0.18 pt, so it is not the whole 2.65, but it is the only page-top term.
3. **`LINE_BASE`** - the engine places a baseline at `before + LINE_BASE * box`. If Google's baseline
   fraction for the substituted face is not `LINE_BASE`, the error is `(LINE_BASE - google) * box`,
   which WOULD scale with size. The measurement above says it does not scale, so this is the least
   likely of the three and should be tested last.

Whichever it is, it is worth more than one document: a constant that shifts every run on a page is
charged by `18_displacement` and `43_within_10pt_x` on every document that has it, and 8 of the ten
solo documents are inside +/-3 pt at the median, which is the same signature.
