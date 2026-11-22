
# P2W Fixer - Run Report

**23 Nov 2026 · slot 01:14 → 01:34 IST · 19 min**

> **3 documents** went from 41/42 to **42/42 in Google**: `73_marksheet_subject_marks_grade`,
> `41_coloured_headings_white_bg`, `29_dot_leaders_txtpos`. Both cost documents are byte-identical.
> The LibreOffice table shows no movement because the construct is one LibreOffice honours either way.

## Progress

| | |
|:--|:--|
| Document-moves this run | **3** — 3 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **26**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:30 | **reverted** | 0/None | guarded spacer split (non-ruled carrier, gap<=20pt) reproduces 1 of the 4 wins the 23:10 run reported (29_dot_leaders 42/42) and costs 16_right_aligned_amounts 41/42 -> 40/42 via a new 23_line_pitch; |
| 01:33 | **lead** | 0/None | spacer split ALONE (guard: non-ruled carrier, gap<=20pt; dither disabled) takes 5 of 8 measured documents to 42/42 in Google with no document worse: 29_dot_leaders, 41_coloured, 73_marksheet, 22_invoi |


## What this slot did

`HANDOFF.md` told every run to apply the dither patch. That instruction is refuted by
`FINDINGS/18_displacement-DITHER-REFUTED-AND-THE-GUARD-THAT-REPLACES-IT-0030-fixer.md` (18:42
yesterday) — Google stores `w:trHeight` and does not lay it — and it had been overwritten, not
merely left: commit `477526b` (19:05) committed a whole-file stale `HANDOFF.json` over the corrected
one, and `handoff.py` `save()` has no re-read and no merge. `HANDOFF.json` `next` is corrected, and
the defect is a row in `BLOCKERS.md`.

The work is the guard that finding specified. The table gap was written as `w:line`, which Google
delivers at about a fifth of its value, so the table sat too high; splitting it into `w:before`
plus a 20 tw hairline keeps the sum identical for LibreOffice and hands the gap to Google. Spent
unguarded it overflowed two exactly-full pages. The guard reads the page's own lowest ink before a
byte is written and spends the gap only where that leaves room for it plus 0.75 pt per table row.

`73_marksheet` was measured on both engines in this slot: 41/42 unpatched, 42/42 patched, and 42/42
again on a second upload. `mobile-bill` 46/47 on one page, unchanged, and its `document.xml` is
identical before and after — the two cost documents cannot regress, which is checkable without a
round trip.

Two readings did not survive: `22_invoice` and `16_right_aligned` spend their gaps and still fail,
and the 01:14 relay slot read both at 42/42 where this build reads 41/42 on the same construct. The
number this slot can defend is three, and the finding says so.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 01:14 → 01:34 · 19 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 28 |
| Longest silence | **9.0 min** — from 01:14:31, after `report.py: building the report` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **9 min** | `###########` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `##########` |
| record - attempt, handoff, class rows | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

The spacer SCOPE GUARD is LANDED (FINDINGS/18_displacement-SPACER-SCOPE-GUARD-LANDS-3-GOOGLE-0051-fixer.md): the table gap is split (w:before = gap-20tw, w:line = 20tw) only where the page's own lowest ink leaves room for it plus 0.75 pt per table row on the page. 73_marksheet, 41_coloured_headings and 29_dot_leaders are 42/42 in Google; mobile-bill and insurance-policy-schedule are byte-identical at document.xml level and mobile-bill re-verified 46/47 one page. Corpus 212/212 re-measured on this engine, 0 worse, 0 better in the LibreOffice proxy (by design). Do NOT apply the dither patch - refuted twice. Two readings to settle before more of this class: (1) 22_invoice and 16_right_aligned spend their gaps and STILL fail 18_displacement with a constant -2.5 pt step and slope ~0 - that is a second term, and FINDINGS/18_displacement-GUARDED-SPACER-SPLIT-1-WIN-1-COST-0219-relay.md read them 42/42 where this build reads 41/42, so re-measure before trusting either; (2) 72_bank_statement is refused by the guard 58 twips short (18 rows -> 270tw row term, gap 346tw, room 558tw) - measure Google's real per-row excess on a ruled table and replace the inherited 15 tw/row, worth +1. Any Google reading at the 41/42-42/42 margin must be taken twice: the same construct read differently two hours apart.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

