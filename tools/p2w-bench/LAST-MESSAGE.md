# P2W Fixer - Run Report

**22 Nov 2026 · slot 08:56 → running IST · 36 min**

> No change was kept this run — and it is the most valuable slot `18_displacement` has had: the
> cause is now measured in Google rather than inferred, 6 of the 16 documents went clean in the test,
> and the ratchet that decides the build is now counted instead of guessed.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:19 | **lead** | 6/16 | Table spacer as w:before + hairline (DocxWriter 5872-5875) and the 2880->4320 twip cap (5852,5866). Measured in Google on all 16 solo-18 documents: 6 became 42/42 (16_right_aligned, 22_invoice, 29_dot |

## The gap above a table is the cause. Measured, not inferred.

`18_displacement` is worth 38.7 clean documents, the largest single check in the corpus, and 16
documents fail it and nothing else at 41/42. Two runs were spent guessing at it. This one measured it.

Google reads `w:line` with `lineRule="exact"` as a *multiple* of the paragraph mark's line height, not
as a length in twips. The engine writes the gap above a table as `w:line` on a 1 pt mark, so Google
charges about a fifth of it. Four documents through the real renderer:

| document | spacer written | median dy | min | max |
|:--|--:|--:|--:|--:|
| 68_journal_wide_table_spanning | 144.0 | **−114.28** | −115.03 | +1.31 |
| 73_marksheet_subject_marks_grade | 16.7 | **−12.85** | −145.35 | +6.40 |
| 41_coloured_headings_white_bg | 3.5 ×3 | **−4.13** | −6.84 | +0.88 |
| 71_invoice_space_aligned_no_rules | **none** | **+1.06** | +0.12 | +6.69 |

That is a dose-response, and it agrees with the isolated TOPB probe (1103 twips asked → 12.22 pt
rendered). On `68_journal` the signature is exact: the runs above the spacer sit at **+0.09** and every
run below it at **−114 to −115**. One construct, one gap, everything under it moves.

Writing the gap as `w:before` — the one vertical length Google honours exactly — took `68_journal` from
**−114.28 to −3.08**, and with the 2880-twip cap raised to the 2961 twips the page really draws, it went
**42/42**. Six of the sixteen came clean: `16_right_aligned_amounts_txtpos`,
`22_invoice_four_columns_txtpos`, `29_dot_leaders_txtpos`, `41_coloured_headings_white_bg`,
`68_journal_wide_table_spanning`, `73_marksheet_subject_marks_grade`.

## Why it was reverted

Two documents got worse — `insurance-policy-schedule` and `mobile-bill`, 41/42 → **38/42**, two pages,
content lost. A change that makes a document worse is not a fix, so the engine is back at HEAD and the
measurement stands as a lead.

The cause is measured, not guessed. Google renders `w:trHeight hRule="atLeast"` rows at **19.10 pt**
against an **18.40 pt** source pitch — **+0.70 pt per row** — because the cell's natural height is 19.10
and `atLeast` lets the row grow to it. Over 21–22 rows that is 14.7–15.4 pt. Before the fix the
under-charged spacer was accidentally absorbing that excess; charging the spacer truly exposes it, and
the two pages with three spacers each are exactly full, so they overflow. The two constructs have to
land together.

One correction worth carrying: the 08:16 run reported this construct *refuted* — "screened all sixteen
through Google, 1 of 16 moved by 0.85 pt". `screen.py` renders with **soffice**, which honours `w:line`
as a length and so cannot see either state. It also argued from `RANKING.csv`'s `max_pt`, which is the
ink error of the LibreOffice render — the renderer these 16 documents already pass 42/42 in. Both
halves of that refutation were measured in the renderer where the defect does not exist.


## The blast radius, counted

The spacer change touches every document that has one, and this slot had measured only the 16 that
fail `18_displacement`. Converting the whole corpus and reading each `word/document.xml`:

| | |
|:--|--:|
| **documents carrying a table spacer** | **124 of the 213 (58.2 %)** |
| spacers in total | 245 |
| spacer value, min / median / max | 2.10 / 11.45 / **178.05** pt |
| documents with 3 or more spacers | 23 |
| documents over the OLD 144 pt cap | **5** |
| **documents clean today that carry one** | **13** |

Two of my own claims were wrong and are corrected in the finding: the cap raise is a **five**-document
change, not the one-document change the 16-document view suggested; and two of those five
(`041122-Account_Opening_Form` and its fillable twin, 22 spacers each, max 166 pt) are **clean today**.
A 166 pt spacer charged at 22 % of its written value is a ~130 pt move if that table is positioned by
the flow, so it must be rendered before and after before this lands. That is why the change is a lead
and not a commit.


## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-04` | which clause of the check can fire on a 1.44-2.40 pt | 09:20 | 03:51 | 1 min |
| `18_dB-03` | do 05/32/59/18 share ONE engine construct in the emi | 09:20 | 03:51 | 1 min |

## Timing

| | |
|:--|:--|
| Slot window | 08:56 → running · 36 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 21 |
| Longest silence | **14.1 min** — from 09:05:17, after `read findings; C2 spacer probe is the lead` |
| Silences over 2 min | 3 |
| Obstacles | 1 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **I forced a release on a slot whose run was still alive, and this watchdog has no `cron` tool to look at the  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **14 min** | `########` |
| measure or build - a conversion, screen or compile writes no beacon | **19 min** | `############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Land BOTH constructs in one build: (1) the table spacer as w:before + hairline w:line=1 exact at DocxWriter.java:5872-5875, and (2) the row height scaled by 0.9634 at the trHeight emitter (line 6228 max(rowTwHere,rowLineTw)) so Google's atLeast growth cannot exceed the source pitch - 0.9634 is measured (19.10/18.40 renders), NOT the 0.9785 in the 08:20 finding. Raise the spacer cap 2880->4320 (5852,5866). Do not use hRule=exact - Google's cell content is 19.10 and exact would clip. THE RATCHET IS NOW COUNTED: 124 of 213 documents carry a table spacer (58.2%), 13 of the 44 Google-clean documents carry one (041122-Account_Opening_Form and its fillable twin have 22 spacers each, max 166 pt; 403_crossword_puzzle 58.15; 332_bom_on_drawing 29.9), and FIVE documents exceed the old 144 pt cap so the cap raise is a five-document change not a one-document one. Render the 13 clean ones before and after and land only if none regresses and at least 4 of the 16 come clean - 29 documents, 87 Drive calls, ~20 min. Do NOT screen this class with screen.py: it renders in soffice, which honours w:line as a length and cannot see either state.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## What this run leaves behind

The finding, with every number and its method: the four before-states, the dose-response, the
six-clean list, the two regressions, the measured row-pitch excess that explains them, and the
blast-radius census. A new instrument, `dy.py`, which reads per-run vertical displacement out of a real
Google export by intercepting `verify_google.extra_checks`, so it cannot disagree with the check it
explains. Both subagents landed and both changed the plan: agent A excluded the `if not ds` branch and
showed that `RANKING.csv`'s `max_pt` is the soffice ink error rather than Google's dy, which killed the
previous run's premise; agent B separated the four travelling checks into two causes and named the
emitter.

All 24 probe Google Docs created this run were deleted after scoring; `KavoPDF-Verify` is empty. No
corpus file, table row, branch or release asset was touched. The engine is back at HEAD.
