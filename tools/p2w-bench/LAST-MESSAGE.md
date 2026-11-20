# P2W Fixer - Run Report

**20 Nov 2026 · slot 09:58 → 10:43 IST · 45 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 3 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7** of the 192 measured in Google |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **15** files in 6 commit(s) from `027fe14` — ...18_displacement-engine-topoffset-101951-cda8.md, ...placement-page-top-before-DROPPED-105000-f1x.md, 18_displacement-dy-shape-101323-4fa7.md, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE. |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 10:36 | **reverted** | 0/107 | table-spacer gap moved from w:line(exact) into w:before: MEASURED IN GOOGLE, reverted. Mechanism was named by two agents and looked right - the spacer paragraph writes the whole gap as w:line on a 1 p |
| 10:38 | **reverted** | 0/107 | ROOT CAUSE PROVEN, no engine change landed. Controlled probe through Google: w:before on the first paragraph after a w:br w:type=page is DROPPED ENTIRELY by Google Docs (55.15 pt asked, rendered 0.33 |
| 10:41 | **reverted** | 0/107 | Third probe, hand-edited docx (no engine change): replaced the four page-top w:before gaps in bank-statement-5-pages with 1x1 trHeight-exact table rows and zeroed the before. THE DISPLACEMENT ITSELF I |


## What 18\_displacement actually is

The class is 125 documents in Google and 19 in LibreOffice. The dominant shape on those pages is the
whole text block, header included, sitting 48 to 68 pt too high, constant in points and not
proportional to type size.

A controlled probe settled it: one hand-built .docx, five variants of the same 55.15 pt page-top
gap, each on its own page, measured in both renderers.

| gap carried by | LibreOffice | Google |
|:--|--:|--:|
| w:before on the first paragraph after the page break | 56.80 | **0.33** |
| empty paragraph, w:line exact, 1 pt mark | 56.80 | 12.22 |
| 1x1 table row, w:trHeight hRule exact | 56.80 | **55.83** |
| empty paragraph, w:line auto, mark 55.15 pt | 752.80 | 589.08 |

LibreOffice places the gap correctly. Google drops it entirely: 0.33 pt is the paper's top edge.
The engine emits a page's top gap as w:before on the first paragraph after the page break, and on
bank-statement-5-pages that paragraph carries 1103 twips, 55.15 pt, while the measured Google
displacement on pages 1 to 4 is -56.9, -57.1, -57.1 and -57.1 pt. The same number.

The construct Google does honour at a page top, as a length in points, is a single-cell table row
with an exact row height: 55.83 pt of the 55.15 asked.

## Why no fix landed

Applying that construct by hand to bank-statement-5-pages, with no engine code touched, moves the
per-page displacement median from -53.8 to +0.8 and from -54.9 to +0.6, inside the 1.5 to 4.5 pt
tolerance. The displacement is fixed. The document then renders as ten pages in Google instead of
six, with a blank page after every real one, for two separately measured reasons: the baseline
already emits a blank page 1 on its own, and the 55 pt gap is not charged to the page fill budget,
which assumed it was free because in Google it was.

So this is not a construct swap. It is make the gap real, charge it to the page capacity, and fix
the blank page the break paragraph already produces. That is engine work, and it needs a full
corpus ratchet rather than the single-document probe this slot could afford.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-01` | Quantify the dy signature: across the Google renders | 09:59 | 05:12 | 43 min |
| `18_dB-01` | Find the engine code path that decides each line's v | 09:59 | 05:12 | 43 min |

## Timing

| | |
|:--|:--|
| Slot window | 09:58 → 10:43 · 45 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 32 |
| Longest silence | **27.0 min** — from 09:59:51, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **8 min** | `####` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **34 min** | `#################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: the page-top gap is PROVEN to be the cause (Google drops w:before there; a trHeight-exact 1x1 table row is honoured to 0.97 pt). Applying it by hand to bank-statement-5-pages fixes the displacement itself (dy median -53.8 -> +0.8) but the document goes 6 pages -> 10 with a blank after each, because (a) the break paragraph already emits a blank page 1 in Google and (b) the 55 pt gap is not charged to the page fill budget. So it is NOT a construct swap: make the gap real AND charge it to the page capacity, and fix the blank page. Engine work, needs a full corpus ratchet. See FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md, second section.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
